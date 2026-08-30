"""The one runtime path — the single entry function the system is called through.

`decide()` is the canonical entry. Inspection helpers may be added as SIBLINGS, never as alternate
entry points. It is deterministic: same certificate + same spec in, same decision out. No clock, no
network, no randomness reaches it — anything time-dependent arrives as an argument.

STATUS: the decision rules are NOT built. Every document currently returns an explicit `hold`
carrying the reason that the rules are not implemented. That is deliberate and it is honest: a
pipeline that emitted `accept` on unbuilt logic would be claiming a judgement it has not made, and
under Thornbury's own asymmetry a wrong accept is a recall conversation. Holding everything is not
a working system either — the ledger penalises over-holding just as it penalises over-accepting —
so this is a starting point to build out from, not a shippable posture.
"""

from __future__ import annotations

from .domain import Certificate, Decision, Finding, Spec

NOT_IMPLEMENTED = Finding(
    code="rules_not_implemented",
    message=(
        "The acceptance rules are not built yet. This lot has not been assessed against SPEC-7 "
        "and must be reviewed by hand."
    ),
)


def decide(certificate: Certificate, spec: Spec) -> Decision:
    """The single runtime entry. Deterministic; fails loud on bad input rather than guessing.

    Build the SPEC-7 assessment here. The order the rules have to run in is a real design
    decision and belongs in an ADR before it is written, not after.
    """
    return Decision(
        doc_id=certificate.doc_id,
        action="hold",
        certificate=certificate,
        findings=(NOT_IMPLEMENTED,),
        explanation=[f"assessed against {spec.document} rev {spec.revision}: rules not implemented"],
    )
