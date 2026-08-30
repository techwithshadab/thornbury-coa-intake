#!/usr/bin/env python3
"""Derive the reference data from the vendored controlled sources.

    python tools/derive_reference.py                 # write reference/*.json
    python tools/derive_reference.py --check         # exit 1 if what is committed is stale

The acceptance limits, the reportable methods and the approved-supplier set are FACTS THAT ALREADY
EXIST in reference/source/. A hand-kept copy of them has nothing comparing it to its source, so it
rots the moment Quality revises SPEC-7 and never says so. Hence: the script is the reviewed thing,
and the JSON is output.

⚠ `--check` is a STALENESS detector, not a correctness one. It compares generator output to
generator output: if the parse below is wrong, the committed file is wrong in exactly the same way,
the diff is empty, and the gate goes green. Correctness is established separately, by
tests/test_derivation.py, which asserts the parse rule against hand-written expectations INCLUDING
the negative cases — rows that must yield nothing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reference" / "source"
OUT = ROOT / "reference"

# "| Assay | 99.0 – 101.0 | % | HPLC (SPEC-7 M-01) |" — en dash, as the controlled document prints it.
_SPEC_ROW = re.compile(
    r"^\|\s*(?P<attribute>[^|]+?)\s*\|\s*"
    r"(?P<lower>-?\d+(?:\.\d+)?)\s*[–—-]\s*(?P<upper>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"(?P<unit>[^|]+?)\s*\|\s*(?P<method>[^|]+?)\s*\|\s*$"
)
_REVISION = re.compile(r"^\|\s*Revision\s*\|\s*(?P<revision>\S+)\s*\|\s*$", re.MULTILINE)
_EFFECTIVE = re.compile(r"^\|\s*Effective\s*\|\s*(?P<effective>[^|]+?)\s*\|\s*$", re.MULTILINE)
_SUPPLIER = re.compile(r"^-\s+(?P<name>\S.*?)\s*$")


def parse_spec_row(line: str) -> dict | None:
    """One table line -> one acceptance criterion, or None if the line is not one.

    Returning None is the load-bearing half: a header row, a separator, or a malformed row must
    yield NOTHING rather than a criterion with a plausible-looking default. A limits table that
    silently gains a row of zeros accepts everything.
    """
    m = _SPEC_ROW.match(line)
    if not m:
        return None
    lower, upper = float(m.group("lower")), float(m.group("upper"))
    if lower > upper:
        raise ValueError(f"lower limit above upper limit in row: {line.strip()!r}")
    return {
        "attribute": m.group("attribute"),
        "lower": lower,
        "upper": upper,
        "unit": m.group("unit"),
        "reportable_method": m.group("method"),
    }


def derive_spec(text: str) -> dict:
    revision = _REVISION.search(text)
    effective = _EFFECTIVE.search(text)
    if not revision or not effective:
        raise ValueError("SPEC-7 source is missing its Revision or Effective row — refusing to guess")
    attributes = [row for row in (parse_spec_row(line) for line in text.splitlines()) if row]
    if not attributes:
        raise ValueError("no acceptance criteria parsed from SPEC-7 source — refusing to emit an empty spec")
    return {
        "document": "SPEC-7",
        "revision": revision.group("revision"),
        "effective": effective.group("effective"),
        "attributes": attributes,
    }


def derive_suppliers(text: str) -> dict:
    names = [m.group("name") for m in (_SUPPLIER.match(line) for line in text.splitlines()) if m]
    if not names:
        raise ValueError("no suppliers parsed from the supplier master — refusing to emit an empty list")
    return {"source": "supplier-master.md", "suppliers": names}


def build() -> dict[pathlib.Path, dict]:
    return {
        OUT / "spec-7.json": derive_spec((SOURCE / "SPEC-7-revD.md").read_text(encoding="utf-8")),
        OUT / "supplier-master.json": derive_suppliers(
            (SOURCE / "supplier-master.md").read_text(encoding="utf-8")
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if the committed files are stale")
    args = ap.parse_args(argv)

    stale = []
    for path, payload in build().items():
        rendered = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(rendered, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT).as_posix()}")

    if stale:
        print(f"stale derived reference data: {', '.join(stale)} — run `make reference`", file=sys.stderr)
        return 1
    if args.check:
        print("derived reference data is current (this says nothing about whether it is correct)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
