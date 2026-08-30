"""Loading the reviewed reference data across the trust boundary.

The reference data is *derived*, not hand-kept: `tools/derive_reference.py` computes it from the
controlled source documents vendored under `reference/source/`, and CI regenerates it to a clean
diff. See docs/reference/derived-reference-data.md for why, and for the thing that check does NOT
prove.
"""

from __future__ import annotations

import json
import pathlib

from .domain import Spec, compile_spec
from .raw import RawSpec, RawSupplierMaster

SPEC_FILE = "spec-7.json"
SUPPLIER_FILE = "supplier-master.json"


def _load_json(path: pathlib.Path) -> dict:
    if not path.is_file():
        raise RuntimeError(
            f"reference data missing: {path}. Run `make reference` to derive it from "
            f"reference/source/, or point --reference at a directory that has it."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_spec(reference_root: pathlib.Path) -> Spec:
    """Validate then compile the acceptance specification. Unknown keys are an error."""
    return compile_spec(RawSpec.model_validate(_load_json(reference_root / SPEC_FILE)))


def load_supplier_master(reference_root: pathlib.Path) -> frozenset[str]:
    """The approved-supplier set, casefolded for matching. Names print in varying case on
    certificates; the ERP holds them as registered."""
    raw = RawSupplierMaster.model_validate(_load_json(reference_root / SUPPLIER_FILE))
    return frozenset(name.casefold() for name in raw.suppliers)
