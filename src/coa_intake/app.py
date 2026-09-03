"""The one runtime path — the single entry function the system is called through.

`decide()` is the canonical entry. Inspection helpers may be added as SIBLINGS, never as alternate
entry points. It is deterministic: same certificate + same spec + same policy in, same decision out.
No clock, no network, no randomness reaches it.

**No rule is written here.** Every threshold, message, route and ruling lives in
`reference/policy.json`; this module walks the spec and the policy and reports what it finds. A
domain fact must be changeable without changing this file — that is the `decisioning_or_scoring`
invariant, and it is also what makes the provisional rulings honestly reversible.
"""

from __future__ import annotations

from .domain import ACCEPT, HOLD, Certificate, Decision, Finding, Spec
from .policy import Policy


def _finding(policy: Policy, rule_id: str, *, attribute=None, evidence=None) -> Finding:
    rule = policy.rule(rule_id)
    return Finding(
        code=rule.id, message=rule.message, route=rule.route, attribute=attribute, evidence=evidence
    )


def _check_readable(certificate: Certificate, policy: Policy) -> list[Finding]:
    """The document had to be readable at all (ADR-0007). Absent, not guessed."""
    missing_core = [
        name
        for name, value in (
            ("lot_id", certificate.lot_id),
            ("material_no", certificate.material_no),
            ("supplier", certificate.supplier),
        )
        if not value
    ]
    if not missing_core:
        return []
    return [_finding(policy, "unparseable", evidence=f"could not read: {', '.join(missing_core)}")]


def _check_spec_revision(certificate: Certificate, spec: Spec, policy: Policy) -> list[Finding]:
    """SPEC-7 §4: a certificate citing a withdrawn revision is referred to Quality."""
    cited = certificate.cited_spec_revision
    if cited and cited != spec.revision:
        return [
            _finding(
                policy,
                "spec_revision_withdrawn",
                evidence=f"certificate cites revision {cited}; current revision is {spec.revision}",
            )
        ]
    return []


def _check_identity(
    certificate: Certificate, policy: Policy, approved_suppliers: frozenset[str]
) -> list[Finding]:
    """Who sent it (R15), and whether the document agrees with itself about which lot it is (R8)."""
    findings: list[Finding] = []
    if certificate.supplier and certificate.supplier.casefold() not in approved_suppliers:
        findings.append(
            _finding(policy, "supplier_not_approved", evidence=f"supplier: {certificate.supplier}")
        )
    if certificate.lot_id_conflicts:
        findings.append(
            _finding(
                policy,
                "lot_id_inconsistent",
                evidence=f"lot numbers printed: {', '.join(certificate.lot_id_conflicts)}",
            )
        )
    return findings


def _check_attribute(criterion, measurement, policy: Policy) -> list[Finding]:
    """One SPEC-7 §2 criterion against what the certificate reported for it."""
    if measurement is None:
        # Missing is not zero. An unreported attribute is a reason to hold, never a 0.0 to compare.
        return [_finding(policy, "attribute_missing", attribute=criterion.attribute)]

    findings: list[Finding] = []
    # SPEC-7 §3.1: a result from a non-reportable method is indicative and cannot release a lot.
    # The method is part of whether the number counts at all, so this is checked before limits.
    if measurement.method != criterion.reportable_method:
        findings.append(
            _finding(
                policy,
                "method_not_reportable",
                attribute=criterion.attribute,
                evidence=(
                    f"stated {measurement.method or 'no method'}; "
                    f"SPEC-7 requires {criterion.reportable_method}"
                ),
            )
        )

    if not criterion.lower <= measurement.value <= criterion.upper:
        findings.append(
            _finding(
                policy,
                "result_outside_limits",
                attribute=criterion.attribute,
                evidence=(
                    f"{measurement.value} {measurement.unit} against "
                    f"{criterion.lower}–{criterion.upper} {criterion.unit}"
                ),
            )
        )
        # SPEC-7 §5: a conformance statement over a non-conforming result makes the certificate
        # itself wrong. Worth its own finding — the supplier needs correcting, not just the lot.
        if measurement.stated_conformance is True:
            findings.append(
                _finding(
                    policy,
                    "conformance_contradicts_result",
                    attribute=criterion.attribute,
                    evidence=f"certificate states PASS for {measurement.value} {measurement.unit}",
                )
            )
    return findings


def _check_dates(certificate: Certificate, policy: Policy) -> tuple[list[Finding], list[str]]:
    """The ADR-0006 ladder's verdict, and R14 on a missing retest date."""
    findings: list[Finding] = []
    explanation: list[str] = []
    for name, reading in (
        ("manufacture_date", certificate.manufacture_date),
        ("retest_date", certificate.retest_date),
    ):
        if reading is None:
            if name == "retest_date":
                findings.append(_finding(policy, "retest_date_missing"))
            continue
        if not reading.is_resolved:
            findings.append(
                _finding(policy, "date_ambiguous", evidence=f"{name}: {reading.raw!r} reads two ways")
            )
        elif reading.resolution == "stated":
            explanation.append(
                f"{name}: {reading.raw!r} read as {reading.iso} using the convention the document "
                f"states for itself"
            )
    return findings, explanation


def decide(
    certificate: Certificate, spec: Spec, policy: Policy, approved_suppliers: frozenset[str]
) -> Decision:
    """The single runtime entry. Deterministic; fails loud on bad input rather than guessing."""
    explanation = [f"judged against {spec.document} rev {spec.revision} under policy {policy.version}"]
    findings = _check_readable(certificate, policy)
    findings += _check_identity(certificate, policy, approved_suppliers)
    findings += _check_spec_revision(certificate, spec, policy)

    by_attribute = {m.attribute: m for m in certificate.results}
    for criterion in spec.attributes:
        measurement = by_attribute.get(criterion.attribute)
        findings += _check_attribute(criterion, measurement, policy)
        if measurement is not None and measurement.was_converted:
            explanation.append(
                f"{criterion.attribute}: converted {measurement.original_value} "
                f"{measurement.original_unit} to {measurement.value} {measurement.unit} "
                f"(SPEC-7 §2 — conversion recorded)"
            )

    date_findings, date_explanation = _check_dates(certificate, policy)
    findings += date_findings
    explanation += date_explanation

    findings.sort(key=lambda f: policy.rule(f.code).order)
    action = HOLD if findings else ACCEPT
    if action == ACCEPT:
        explanation.append("every SPEC-7 §2 attribute present, reportable and within limits")

    return Decision(
        doc_id=certificate.doc_id,
        action=action,
        certificate=certificate,
        findings=tuple(findings),
        spec_revision=spec.revision,
        explanation=explanation,
    )
