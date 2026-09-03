"""The SPEC-7 rules, and the parser they depend on.

These are the tests that fail when a ruling in reference/policy.json stops being honoured. They
assert on the *decision*, not on internals, because the decision is what a consumer binds to.

The fixtures are the real layouts from the supplied corpus, trimmed. Synthetic certificates would
test the parser against a shape no supplier actually sends.
"""

from __future__ import annotations

import pathlib

import pytest

from coa_intake.app import decide
from coa_intake.domain import ACCEPT, HOLD, ROUTE_INTAKE_KEYING, ROUTE_QUALITY
from coa_intake.parse import parse_certificate
from coa_intake.raw import RawExtraction
from coa_intake.reference import load_policy, load_spec, load_supplier_master

REFERENCE = pathlib.Path(__file__).resolve().parents[1] / "reference"


@pytest.fixture(scope="module")
def ctx():
    return load_spec(REFERENCE), load_policy(REFERENCE), load_supplier_master(REFERENCE)


def _decide(text: str, ctx, doc_id: str = "COA-TEST"):
    spec, policy, approved = ctx
    extraction = RawExtraction(doc_id=doc_id, text=text, extractor="test")
    return decide(parse_certificate(extraction, policy, approved), spec, policy, approved)


CLEAN = """Aldergrove Mills

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


def test_a_clean_certificate_is_accepted(ctx):
    decision = _decide(CLEAN, ctx)
    assert decision.action == ACCEPT, decision.findings
    assert decision.spec_revision == "D"
    assert {m.attribute for m in decision.certificate.results} == {
        "Assay",
        "Moisture",
        "Heavy Metals",
        "Bulk Density",
    }


# --- SPEC-7 §5: the certificate can be wrong ----------------------------------------------------


def test_out_of_limits_holds_even_when_the_certificate_says_pass(ctx):
    """COA-0009's shape. SPEC-7 §5: non-conforming irrespective of any conformance statement."""
    text = CLEAN.replace("100.356 %", "101.366 %").replace(
        "Assay             99.0-101.0 %", "Assay             99.0-101.0 %  PASS"
    )
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    codes = {f.code for f in decision.findings}
    assert "result_outside_limits" in codes
    assert decision.route == ROUTE_QUALITY


def test_a_stated_pass_over_a_bad_result_is_its_own_finding(ctx):
    """The supplier needs correcting too, so it is reported separately from the breach."""
    text = """Halewood Ingredients
  Item code     : GUA-410
  Batch         : HLW-9520
  Mfg date      : 15/03/2026
  Retest due    : 15/03/2028
  Assay         : 101.366 %   [99.0-101.0]  PASS
                  via HPLC (SPEC-7 M-01)
  Moisture      : 0.296 %   [0.0-0.5]  PASS
                  via Karl Fischer (SPEC-7 M-04)
  Heavy Metals  : 5.695 ppm   [0.0-10.0]  PASS
                  via ICP-MS (SPEC-7 M-11)
  Bulk Density  : 0.523 g/mL   [0.45-0.75]  PASS
                  via USP <616> (SPEC-7 M-21)
"""
    decision = _decide(text, ctx)
    codes = {f.code for f in decision.findings}
    assert "conformance_contradicts_result" in codes
    assert "result_outside_limits" in codes


# --- SPEC-7 §3.1/§3.2: the method is part of whether the number counts ---------------------------


def test_a_non_reportable_method_holds_a_lot_whose_numbers_are_fine(ctx):
    """COA-0004/0026/0029. Every value in limits; moisture by loss on drying. SPEC-7 §3.2 says that
    result cannot release a lot, so a system that only checked numbers would release it."""
    text = CLEAN.replace("Karl Fischer (SPEC-7 M-04)", "Loss on Drying (SPEC-7 M-03)")
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    finding = next(f for f in decision.findings if f.code == "method_not_reportable")
    assert finding.attribute == "Moisture"
    assert decision.route == ROUTE_QUALITY


def test_a_missing_attribute_is_not_a_passing_one(ctx):
    """Missing is not zero — and 0.0 is *inside* the moisture limits, so a defaulted zero passes."""
    text = "\n".join(ln for ln in CLEAN.splitlines() if "Moisture" not in ln)
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    assert any(f.code == "attribute_missing" and f.attribute == "Moisture" for f in decision.findings)


# --- SPEC-7 §2: canonicalize on write ------------------------------------------------------------


def test_ppb_is_converted_before_comparison_and_the_conversion_is_recorded(ctx):
    """COA-0027/0031. 7276 ppb is 7.276 ppm — inside the limit. Compared raw it would be rejected."""
    text = CLEAN.replace("0.0-10.0 ppm          5.356 ppm", "0.0-10.0 ppb          7276.0 ppb")
    decision = _decide(text, ctx)
    assert decision.action == ACCEPT, decision.findings
    hm = next(m for m in decision.certificate.results if m.attribute == "Heavy Metals")
    assert hm.value == pytest.approx(7.276)
    assert hm.unit == "ppm"
    assert hm.was_converted and hm.original_unit == "ppb"
    assert any("conversion recorded" in line for line in decision.explanation)


# --- the date ladder (ADR-0006) ------------------------------------------------------------------


def test_an_unresolvable_date_holds_and_goes_back_to_intake_not_to_quality(ctx):
    """COA-0010/0036. Nothing is wrong with the lot — we could not read the document."""
    text = CLEAN.replace("2026-01-27", "02/08/2026").replace("2028-01-27", "02/08/2028")
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    assert {f.code for f in decision.findings} == {"date_ambiguous"}
    assert decision.route == ROUTE_INTAKE_KEYING


def test_a_document_stating_its_own_convention_is_read_not_inferred(ctx):
    """COA-0034. Reading a document's own instructions is not inference."""
    text = CLEAN.replace(
        "Aldergrove Mills", "Aldergrove Mills\nAll dates are written day/month/year."
    ).replace("2026-01-27", "01/10/2026")
    decision = _decide(text, ctx)
    assert decision.certificate.manufacture_date.iso == "2026-10-01"
    assert decision.certificate.manufacture_date.resolution == "stated"


def test_a_supplier_convention_is_never_used_to_resolve_a_date(ctx):
    """COA-0035. Halewood does write day/month on its other certificates — and ADR-0008 removed the
    rung that would have used that. Reading a date off a supplier's other paperwork is the same class
    of move as guessing from their country, which we already refuse; the only thing separating them
    was a threshold we chose, calibrated on the single case it admitted."""
    text = CLEAN.replace("Aldergrove Mills", "Halewood Ingredients").replace("2026-01-27", "07/02/2026")
    decision = _decide(text, ctx)
    assert decision.certificate.manufacture_date.resolution == "ambiguous"
    assert decision.action == HOLD
    assert decision.route == ROUTE_INTAKE_KEYING


def test_a_date_is_never_guessed_from_a_company_s_country(ctx):
    """Zeeland Bulk BV is Dutch, which is a fact about a jurisdiction and not about a template."""
    text = CLEAN.replace("Aldergrove Mills", "Zeeland Bulk BV").replace("2026-01-27", "02/08/2026")
    decision = _decide(text, ctx)
    assert decision.certificate.manufacture_date.resolution == "ambiguous"
    assert decision.action == HOLD


# --- master data and document integrity ----------------------------------------------------------


def test_an_unapproved_supplier_goes_to_procurement_not_quality(ctx):
    """COA-0003/0017/0030. A sourcing question, not a quality one — routing says so."""
    text = CLEAN.replace("Aldergrove Mills", "Fenwick Commodity Ltd")
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    assert decision.route == "procurement"


def test_a_document_that_disagrees_with_itself_about_the_lot_holds(ctx):
    """COA-0018/0023. We never choose between them — which is right determines which material."""
    text = CLEAN.replace("ALD-2655", "HLW-1185").replace(
        "Determination", "Results for lot HLW-1191\n\nDetermination"
    )
    decision = _decide(text, ctx)
    assert any(f.code == "lot_id_inconsistent" for f in decision.findings)


def test_a_missing_retest_date_is_never_computed(ctx):
    """COA-0019/0028. Certificates set retest at manufacture + 24 months, so this COULD be
    calculated. It drives Purchasing's reorder logic, so it is not ours to invent."""
    text = "\n".join(ln for ln in CLEAN.splitlines() if "Valid until" not in ln)
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    assert any(f.code == "retest_date_missing" for f in decision.findings)
    assert decision.certificate.retest_date is None


def test_an_unreadable_layout_yields_silence_not_a_guess(ctx):
    """ADR-0007's whole basis: an unseen layout must under-read, never mis-read."""
    decision = _decide("SOMETHING ENTIRELY DIFFERENT\nno fields here at all\n", ctx)
    assert decision.action == HOLD
    assert any(f.code == "unparseable" for f in decision.findings)
    assert decision.route == ROUTE_INTAKE_KEYING


# --- the rules are data, not logic ---------------------------------------------------------------


def test_every_finding_code_is_a_rule_in_the_policy_file(ctx):
    """A finding whose code is not in policy.json would carry no message, owner or route."""
    _, policy, _ = ctx
    for text in (CLEAN, CLEAN.replace("Karl Fischer (SPEC-7 M-04)", "Loss on Drying (SPEC-7 M-03)")):
        for finding in _decide(text, ctx).findings:
            assert policy.rule(finding.code).owner, f"{finding.code} has no owner"


def test_an_unknown_rule_id_fails_loud(ctx):
    _, policy, _ = ctx
    with pytest.raises(KeyError, match="no rule"):
        policy.rule("a_rule_nobody_wrote")


def test_the_policy_declines_to_grant_release(ctx):
    """ADR-0004. The system creates lots at the ERP's default and never releases."""
    _, policy, _ = ctx
    assert policy.may_set_released is False
    assert policy.creates_lot_at_status == "held"


# --- SPEC-7 §4 and the staleness horizon ---------------------------------------------------------


def test_a_certificate_citing_a_withdrawn_revision_is_referred_to_quality(ctx):
    """SPEC-7 §4. No certificate in the supplied corpus cites a revision, so this rule has never
    fired on real data — which is exactly why it needs a test rather than an assumption."""
    text = CLEAN.replace("Aldergrove Mills", "Aldergrove Mills\nCertified against SPEC-7 rev C.")
    decision = _decide(text, ctx)
    assert decision.action == HOLD
    assert any(f.code == "spec_revision_withdrawn" for f in decision.findings)
    assert decision.route == ROUTE_QUALITY


def test_a_method_reference_is_not_mistaken_for_a_revision(ctx):
    """ "SPEC-7 M-01" appears on every certificate. Reading the M as a revision would hold all 36."""
    assert _decide(CLEAN, ctx).certificate.cited_spec_revision is None


def test_the_pipeline_refuses_to_run_on_a_specification_it_cannot_vouch_for(ctx):
    """Ruling R4. Nobody owns telling this repo SPEC-7 was revised, so staleness fails closed."""
    import datetime as dt

    from coa_intake.cli import check_spec_freshness

    _, policy, _ = ctx
    with pytest.raises(RuntimeError, match="review horizon"):
        check_spec_freshness(policy, dt.date(2030, 1, 1))


def test_the_staleness_warning_fires_before_the_refusal(ctx):
    import datetime as dt

    from coa_intake.cli import check_spec_freshness

    _, policy, _ = ctx
    assert check_spec_freshness(policy, dt.date(2026, 8, 30)) is None
    assert "WARNING" in check_spec_freshness(policy, dt.date(2027, 4, 1))
