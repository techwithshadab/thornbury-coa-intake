"""The command line — the repo's one entry point.

    coa-intake --documents <dir> --reference <dir> --out decisions.jsonl

Both roots are INPUTS. The pipeline is run against documents it has not seen, so a path baked into
the program is a defect, not a convenience. `paths.py` owns resolution; this module owns argument
parsing, the walk, and the write.

Every document produces exactly one line. A document that cannot be processed is a `hold` with a
reason, never a silence — a missing line reads as "no opinion", and there is no such thing here.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

from . import paths
from .app import decide
from .domain import ACCEPT, Decision
from .extraction import TextFileExtractor
from .parse import parse_certificate
from .reference import load_policy, load_spec, load_supplier_master


def _to_line(decision: Decision) -> dict:
    """Render a Decision into the submission contract. The caller RENDERS the explanation the
    decision carries; it never reassembles the reasoning itself.

    `route` and `explanation` are ours, not the contract's — the submission validator ignores extra
    keys, and a held lot is useless to Thornbury without knowing whose desk it belongs on.
    """
    out: dict = {
        "doc_id": decision.doc_id,
        "action": decision.action,
        "schema_version": decision.schema_version,
        "spec_revision": decision.spec_revision,
    }

    if decision.action != ACCEPT:
        out["hold_reason"] = (
            " ".join(f"{f.message}{f' [{f.evidence}]' if f.evidence else ''}" for f in decision.findings)
            or "held without a stated reason"
        )
        out["route"] = decision.route
        out["findings"] = [
            {"code": f.code, "attribute": f.attribute, "evidence": f.evidence} for f in decision.findings
        ]
        return out

    cert = decision.certificate
    if cert is None:
        raise RuntimeError(f"{decision.doc_id}: an accept must carry a compiled certificate")
    out["fields"] = {
        "lot_id": cert.lot_id,
        "material_no": cert.material_no,
        "supplier": cert.supplier,
        "manufacture_date": cert.manufacture_date.iso if cert.manufacture_date else None,
        "retest_date": cert.retest_date.iso if cert.retest_date else None,
        "tests": [
            {
                "attribute": m.attribute,
                "result": m.value,
                "unit": m.unit,
                "method": m.method,
                **({"reported_as": f"{m.original_value} {m.original_unit}"} if m.was_converted else {}),
            }
            for m in cert.results
        ],
    }
    out["explanation"] = decision.explanation
    return out


def check_spec_freshness(policy, today: dt.date) -> str | None:
    """Ruling R4: nobody owns telling this repo that SPEC-7 was revised, so it assumes its copy goes
    stale on schedule. Past `warn_after` it says so; past `fail_after` it refuses to run.

    The clock is a PARAMETER. Reading it here rather than inside the rules keeps `decide()`
    deterministic, and this the only place in `src/` that a date enters at all.
    """
    if today >= dt.date.fromisoformat(policy.fail_after):
        raise RuntimeError(
            f"the vendored SPEC-7 copy went past its review horizon on {policy.fail_after} and "
            f"today is {today}. Nobody owns notifying this repo of a revision (open question Q4), "
            f"so it refuses to judge lots against a specification it cannot vouch for. Re-vendor "
            f"reference/source/ from the QMS, re-run `make reference`, and move the dates in "
            f"reference/policy.json."
        )
    if today >= dt.date.fromisoformat(policy.warn_after):
        return (
            f"WARNING: the vendored SPEC-7 copy passed its annual review date ({policy.warn_after}). "
            f"Confirm rev {policy.version} is still current before relying on these decisions."
        )
    return None


def run(
    documents_root: pathlib.Path,
    reference_root: pathlib.Path,
    out: pathlib.Path,
    today: dt.date | None = None,
) -> int:
    """Walk every document once, decide, write one line each. Returns the number of lines."""
    spec = load_spec(reference_root)
    policy = load_policy(reference_root)
    if warning := check_spec_freshness(policy, today or dt.date.today()):
        print(warning, file=sys.stderr)
    approved = load_supplier_master(reference_root)
    extractor = TextFileExtractor()

    lines = []
    for extraction in extractor.extract_all(documents_root):
        certificate = parse_certificate(extraction, policy, approved)
        lines.append(_to_line(decide(certificate, spec, policy, approved)))

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")
    return len(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="coa-intake", description=__doc__.split("\n")[0])
    ap.add_argument("--documents", help=f"directory of certificates (or ${paths.WORKSPACE_ENV}/documents)")
    ap.add_argument("--reference", help=f"directory of reference data (or ${paths.WORKSPACE_ENV}/reference)")
    ap.add_argument(
        "--out", default="decisions.jsonl", help="where to write the decisions (default: %(default)s)"
    )
    args = ap.parse_args(argv)

    documents_root = paths.documents_root(args.documents)
    reference_root = paths.reference_root(args.reference)
    n = run(documents_root, reference_root, pathlib.Path(args.out))
    print(f"{n} decisions written to {args.out} from {documents_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
