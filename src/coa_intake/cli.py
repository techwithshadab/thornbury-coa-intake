"""The command line — the repo's one entry point.

    coa-intake --documents <dir> --reference <dir> --out decisions.jsonl

Both roots are INPUTS. The pipeline is run against documents it has not seen, so a path baked into
the program is a defect, not a convenience. `paths.py` owns resolution; this module owns argument
parsing and the write.

Every document produces exactly one line. A document that cannot be processed is a `hold` with a
reason, never a silence — a missing line reads as "no opinion", and there is no such thing here.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import paths
from .app import decide
from .domain import Certificate, Decision
from .extraction import TextFileExtractor
from .reference import load_spec


def _to_line(decision: Decision) -> dict:
    """Render a Decision into the submission contract. The caller RENDERS the explanation the
    decision carries; it never reassembles the reasoning itself."""
    out: dict = {
        "doc_id": decision.doc_id,
        "action": decision.action,
        "schema_version": decision.schema_version,
    }
    if decision.action == "hold":
        out["hold_reason"] = " ".join(f.message for f in decision.findings) or "held without a stated reason"
        return out

    cert = decision.certificate
    if cert is None:
        raise RuntimeError(f"{decision.doc_id}: an accept must carry a compiled certificate")
    out["fields"] = {
        "lot_id": cert.lot_id,
        "material_no": cert.material_no,
        "supplier": cert.supplier,
        "manufacture_date": cert.manufacture_date,
        "retest_date": cert.retest_date,
        "tests": [
            {
                "attribute": m.attribute,
                "result": m.value,
                "unit": m.unit,
                "method": m.method,
            }
            for m in cert.results
        ],
    }
    return out


def run(documents_root: pathlib.Path, reference_root: pathlib.Path, out: pathlib.Path) -> int:
    """Walk every document once, decide, write one line each. Returns the number of lines."""
    spec = load_spec(reference_root)
    extractor = TextFileExtractor()
    lines = []
    for extraction in extractor.extract_all(documents_root):
        # The compile step from raw text to a Certificate is not built — see app.py. Until it is,
        # every document arrives at decide() as an empty certificate and comes back a hold.
        certificate = Certificate(doc_id=extraction.doc_id)
        lines.append(_to_line(decide(certificate, spec)))

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
