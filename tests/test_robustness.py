"""Robustness against layouts we have not seen.

**This is the test that speaks to the actual assessment condition:** the pipeline is run against
documents from suppliers whose templates are not in the corpus. Thornbury has ~40 suppliers; the
sample shows 11, in 6 layout families.

Every variation below is a plausible way a different supplier could write the *same certificate*.
A hold on any of them is an **unnecessary hold** — it costs Thornbury a manual keying and it is
penalised by the ledger, so parser coverage is a business number, not a tidiness one.

The design guarantee (ADR-0007) is that an unreadable layout yields *silence*, never a wrong number.
That makes every failure here safe — and still worth fixing.
"""

from __future__ import annotations

import pathlib

import pytest

from coa_intake.app import decide
from coa_intake.domain import ACCEPT
from coa_intake.parse import parse_certificate
from coa_intake.raw import RawExtraction
from coa_intake.reference import load_policy, load_spec, load_supplier_master

REFERENCE = pathlib.Path(__file__).resolve().parents[1] / "reference"

BASE = """Aldergrove Mills

Description ....... Malic Acid Fine
Reference ......... MAL-505
Identification .... ALD-2655
Manufactured ...... 2026-01-27
Valid until ....... 2028-01-27

Determination     Requirement           Obtained          Procedure
Assay             99.0-101.0 %          100.356 %         HPLC (SPEC-7 M-01)
Moisture          0.0-0.5 %             0.153 %           Karl Fischer (SPEC-7 M-04)
Heavy Metals      0.0-10.0 ppm          5.356 ppm         ICP-MS (SPEC-7 M-11)
Bulk Density      0.45-0.75 g/mL        0.591 g/mL        USP <616> (SPEC-7 M-21)
"""

_CODES = ["M-01", "M-04", "M-11", "M-21"]


def _rewrite_methods(text: str, fmt: str) -> str:
    for code in _CODES:
        text = text.replace(f"(SPEC-7 {code})", fmt.format(code=code))
    return text


VARIANTS = {
    # --- how a supplier punctuates the method reference -----------------------------------------
    # The highest-value group: SPEC-7 §3.1 makes the method decisive, so before methods were matched
    # on their CODE rather than the prose around them, every one of these held the lot.
    "method in square brackets": _rewrite_methods(BASE, "[SPEC-7 {code}]"),
    "method bare, no delimiter": _rewrite_methods(BASE, "SPEC-7 {code}"),
    "method 'per SPEC-7 M-nn'": _rewrite_methods(BASE, "per SPEC-7 {code}"),
    "method 'SPEC-7: M-nn'": _rewrite_methods(BASE, "SPEC-7: {code}"),
    "method code lowercase": _rewrite_methods(BASE, "(spec-7 {code})").replace("M-", "m-"),
    # --- attribute naming ------------------------------------------------------------------------
    "attribute 'Purity' / 'Water'": BASE.replace("Assay ", "Purity").replace("Moisture", "Water   "),
    "attribute 'Density'": BASE.replace("Bulk Density", "Density     "),
    # --- field labels ----------------------------------------------------------------------------
    "lot labelled 'Lot No'": BASE.replace("Identification ....", "Lot No ............"),
    "lot labelled 'Batch Number'": BASE.replace("Identification ....", "Batch Number ....."),
    "material labelled 'Product Code'": BASE.replace("Reference .........", "Product Code ....."),
    "material labelled 'Article No'": BASE.replace("Reference .........", "Article No ......."),
    "mfg labelled 'Production Date'": BASE.replace("Manufactured ......", "Production Date ..."),
    "retest labelled 'Retest On'": BASE.replace("Valid until .......", "Retest On ........."),
    "retest labelled 'Next Test'": BASE.replace("Valid until .......", "Next Test ........."),
    # --- units and whitespace --------------------------------------------------------------------
    "heavy metals in mg/kg": BASE.replace(
        "0.0-10.0 ppm          5.356 ppm", "0.0-10.0 mg/kg        5.356 mg/kg"
    ),
    "assay in %w/w": BASE.replace("99.0-101.0 %          100.356 %", "99.0-101.0 %w/w       100.356 %w/w"),
    "tab separated": BASE.replace("     ", "\t"),
    "no column header row": BASE.replace(
        "Determination     Requirement           Obtained          Procedure\n", ""
    ),
}


@pytest.fixture(scope="module")
def ctx():
    return load_spec(REFERENCE), load_policy(REFERENCE), load_supplier_master(REFERENCE)


@pytest.mark.parametrize("name", sorted(VARIANTS), ids=lambda n: n)
def test_a_plausible_unseen_layout_is_still_read(name, ctx):
    """Each of these is the same clean certificate written the way another supplier might write it.
    Holding one is not a safety failure — it is lost automation, and the ledger charges for it."""
    spec, policy, approved = ctx
    extraction = RawExtraction(doc_id="COA-VARIANT", text=VARIANTS[name], extractor="test")
    decision = decide(parse_certificate(extraction, policy, approved), spec, policy, approved)
    assert decision.action == ACCEPT, (
        f"layout variation {name!r} produced an unnecessary hold: "
        f"{[f'{f.code}/{f.attribute}' for f in decision.findings]}"
    )


def test_the_baseline_layout_is_accepted(ctx):
    spec, policy, approved = ctx
    extraction = RawExtraction(doc_id="COA-BASE", text=BASE, extractor="test")
    assert decide(parse_certificate(extraction, policy, approved), spec, policy, approved).action == ACCEPT


def test_a_document_naming_one_method_and_citing_another_s_code_holds(ctx):
    """The certificate says Karl Fischer and cites M-01 (HPLC). Right code for nothing, wrong name
    for the code — the document disagrees with itself about the thing that decides whether its own
    number counts. We do not pick a side."""
    spec, policy, approved = ctx
    text = BASE.replace("Karl Fischer (SPEC-7 M-04)", "Karl Fischer (SPEC-7 M-19)").replace(
        "0.0-0.5 %             0.153 %", "0.0-0.5 %             0.153 %"
    )
    text = text.replace("Karl Fischer (SPEC-7 M-19)", "Gravimetric (SPEC-7 M-04)")
    extraction = RawExtraction(doc_id="COA-CONTRADICT", text=text, extractor="test")
    decision = decide(parse_certificate(extraction, policy, approved), spec, policy, approved)
    assert any(f.code == "method_name_contradicts_code" for f in decision.findings), decision.findings
    assert decision.route == "supplier_query"


def test_an_unknown_method_code_is_never_treated_as_reportable(ctx):
    """A code SPEC-7 does not assign to this attribute cannot release the lot, whatever it is named."""
    spec, policy, approved = ctx
    text = BASE.replace("(SPEC-7 M-01)", "(SPEC-7 M-99)")
    extraction = RawExtraction(doc_id="COA-UNKNOWN", text=text, extractor="test")
    decision = decide(parse_certificate(extraction, policy, approved), spec, policy, approved)
    assert any(f.code == "method_not_reportable" for f in decision.findings)
