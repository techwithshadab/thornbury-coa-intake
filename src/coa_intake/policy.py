"""The compiled policy — the provisional rulings, as domain objects.

`reference/policy.json` holds every decision we made on Thornbury's behalf while their questions are
unanswered. It is hand-authored and reviewed; the SPEC-7 table and supplier master beside it are
generated. Keeping the rulings as reviewed *data* rather than as `if` branches is what makes
overturning one a data change with a review, which is the whole basis on which we felt able to make
them at all.
"""

from __future__ import annotations

from dataclasses import dataclass

from .raw import RawPolicy


@dataclass(frozen=True)
class Rule:
    id: str
    order: int
    action: str
    route: str
    message: str
    owner: str


@dataclass(frozen=True)
class Conversion:
    attribute: str
    from_unit: str
    to_unit: str
    factor: float


@dataclass(frozen=True)
class Policy:
    version: str
    rules: tuple[Rule, ...]  # sorted by `order`; the first matching finding leads
    conversions: tuple[Conversion, ...]
    synonyms: dict[str, str]  # casefolded alias -> canonical SPEC-7 attribute
    labels: dict[str, tuple[str, ...]]  # field name -> the labels that introduce it
    warn_after: str
    fail_after: str
    may_set_released: bool
    creates_lot_at_status: str

    def rule(self, rule_id: str) -> Rule:
        """Fail loud on an unknown rule id — a typo must not silently produce a hold with no reason."""
        for r in self.rules:
            if r.id == rule_id:
                return r
        raise KeyError(
            f"no rule {rule_id!r} in policy {self.version}. Rules are data: add it to "
            f"reference/policy.json rather than hard-coding the behaviour."
        )


def compile_policy(raw: RawPolicy) -> Policy:
    """raw.RawPolicy -> Policy. The one place validated policy becomes domain truth."""
    synonyms: dict[str, str] = {}
    for canonical, aliases in raw.attribute_synonyms.map.items():
        synonyms[canonical.casefold()] = canonical
        for alias in aliases:
            synonyms[alias.casefold()] = canonical

    return Policy(
        version=raw.policy_version,
        rules=tuple(
            sorted(
                (
                    Rule(
                        id=r.id,
                        order=r.order,
                        action=r.action,
                        route=r.route,
                        message=r.message,
                        owner=r.owner,
                    )
                    for r in raw.rules
                ),
                key=lambda r: r.order,
            )
        ),
        conversions=tuple(
            Conversion(c.attribute, c.from_unit, c.to_unit, c.factor) for c in raw.unit_conversions
        ),
        synonyms=synonyms,
        labels={
            "lot_id": tuple(raw.field_labels.lot_id),
            "material_no": tuple(raw.field_labels.material_no),
            "manufacture_date": tuple(raw.field_labels.manufacture_date),
            "retest_date": tuple(raw.field_labels.retest_date),
            "supplier": tuple(raw.field_labels.supplier),
        },
        warn_after=raw.spec_staleness.warn_after,
        fail_after=raw.spec_staleness.fail_after,
        may_set_released=raw.release.may_set_released,
        creates_lot_at_status=raw.release.creates_lot_at_status,
    )
