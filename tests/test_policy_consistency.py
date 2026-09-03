"""The policy file has to be internally consistent, because parts of it are enforced by code and
parts are only *stated*.

That split is the risk. `min_unambiguous_samples: 3` and the `explicitly_not_inferred` list read
like rules, and nothing in `app.py` reads either — so without these tests a reviewer could add a
supplier convention backed by one certificate, or add a convention for a supplier the file
explicitly says must never be inferred, and every other gate would stay green.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from coa_intake.raw import RawPolicy

POLICY_PATH = pathlib.Path(__file__).resolve().parents[1] / "reference" / "policy.json"
RAW = RawPolicy.model_validate(json.loads(POLICY_PATH.read_text(encoding="utf-8")))


def test_the_date_ladder_ends_in_a_hold():
    """ADR-0008. The bottom rung must be a hold — a ladder whose last step resolves something is a
    ladder that guesses. This is the property that keeps date handling honest."""
    assert "HOLD" in RAW.date_resolution.ladder[-1].upper()


def test_the_date_ladder_reads_only_the_document_in_front_of_it():
    """No rung may resolve a date from another document. The corpus evidence for per-supplier
    conventions is kept in the policy as ANALYSIS and must not creep back in as a rule."""
    rungs = " ".join(RAW.date_resolution.ladder).lower()
    for forbidden in ("supplier convention", "other certificates", "country", "jurisdiction"):
        assert forbidden not in rungs, f"the ladder has grown a rung that infers from {forbidden!r}"


def test_the_dropped_inference_evidence_is_retained_as_analysis():
    """Kept so the next team does not redo the corpus reading — and labelled as not-acted-on, so
    nobody mistakes it for a rule."""
    assert RAW.date_resolution.evidence_considered_but_not_acted_on
    assert RAW.date_resolution.why_no_supplier_inference.strip()


def test_rule_ids_and_orders_are_unique():
    """Two rules at the same order make the leading finding — and therefore the queue a lot lands
    in — depend on dict ordering rather than on a decision."""
    ids = [r.id for r in RAW.rules]
    orders = [r.order for r in RAW.rules]
    assert len(ids) == len(set(ids)), "duplicate rule id"
    assert len(orders) == len(set(orders)), "two rules share an order; routing would be arbitrary"


def test_unparseable_leads_every_other_rule():
    """If the document did not parse, every other finding on it is drawn from fields we may have
    misread — so it must not be the one that names the queue."""
    unparseable = next(r for r in RAW.rules if r.id == "unparseable")
    assert unparseable.order == min(r.order for r in RAW.rules)


def test_every_rule_names_an_owner_who_can_overturn_it():
    """A provisional ruling with no owner is one nobody can overturn, which makes it permanent by
    accident — the exact failure this file exists to avoid."""
    for rule in RAW.rules:
        assert rule.owner.strip(), f"{rule.id} has no owner"


def test_the_policy_still_declares_itself_provisional():
    """If this ever says 'final', someone at Thornbury has ratified it — and that should be a
    deliberate change with a gate record, not a quiet edit."""
    assert RAW.status == "provisional"


def test_the_staleness_horizon_is_ordered():
    assert RAW.spec_staleness.warn_after < RAW.spec_staleness.fail_after


@pytest.mark.parametrize("conversion", RAW.unit_conversions, ids=lambda c: f"{c.from_unit}->{c.to_unit}")
def test_every_conversion_states_why(conversion):
    """SPEC-7 §2 requires the conversion to be recorded. A factor with no rationale is unreviewable."""
    assert conversion.why.strip()
