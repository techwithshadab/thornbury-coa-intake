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


def test_every_date_convention_meets_its_own_evidence_threshold():
    """ADR-0006 rung 3 requires >= min_unambiguous_samples agreeing certificates. The threshold is
    stated in the file and read by nothing, so it is asserted here."""
    threshold = RAW.supplier_date_conventions.min_unambiguous_samples
    for convention in RAW.supplier_date_conventions.conventions:
        assert len(convention.evidence) >= threshold, (
            f"{convention.supplier} claims a {convention.order} convention on "
            f"{len(convention.evidence)} certificate(s); the policy requires {threshold}."
        )


def test_no_supplier_is_both_inferred_and_explicitly_not_inferred():
    """Zeeland Bulk BV is listed as never-infer. A convention for it would silently override that."""
    inferred = {c.supplier.casefold() for c in RAW.supplier_date_conventions.conventions}
    refused = {n.supplier.casefold() for n in RAW.supplier_date_conventions.explicitly_not_inferred}
    assert not (inferred & refused), f"contradiction in policy: {inferred & refused}"


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
