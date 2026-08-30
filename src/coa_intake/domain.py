"""Compiled domain objects — what the runtime consumes.

The compile step validates raw input once, at load, and emits these typed objects. Runtime walks
domain objects, never loose dicts. Two laws are visible in the types themselves:

  * **Provenance.** A measured value is never a bare number. `Measurement` carries value, unit, and
    the source it was read from, so nobody downstream can mistake an unsourced figure for truth,
    and a reviewer can find the line on the certificate that produced it.
  * **Missing is not zero.** An attribute the certificate did not report is absent from `results`,
    not present as 0.0. Absence is a decision input in its own right — SPEC-7 §2 requires every
    attribute, so a missing one is a reason to hold, never a zero to compare against a limit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Bumped when the shape of an emitted decision changes. Any output that crosses a boundary or is
# persisted carries this, so a consumer can tell which contract produced the line it is reading.
SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class Measurement:
    """A measured value with provenance — never a bare number."""

    attribute: str  # the SPEC-7 attribute this measures, canonicalized
    value: float
    unit: str  # canonical unit: converted on write, never at comparison time
    source: str  # doc_id + locator: which document, and where in it
    method: str | None = None  # the method the certificate stated, or None if it stated none


@dataclass(frozen=True)
class SpecAttribute:
    """One acceptance criterion, canonicalized: limits are already in the canonical unit."""

    attribute: str
    lower: float
    upper: float
    unit: str
    reportable_method: str


@dataclass(frozen=True)
class Spec:
    """The compiled acceptance specification."""

    document: str
    revision: str
    effective: str
    attributes: tuple[SpecAttribute, ...]


@dataclass(frozen=True)
class Certificate:
    """A compiled certificate. Every field is optional because a certificate may simply not carry
    it — and a missing field is a hold reason, not a blank to be filled with a guess."""

    doc_id: str
    lot_id: str | None = None
    material_no: str | None = None
    supplier: str | None = None
    manufacture_date: str | None = None  # ISO 8601, canonicalized on write
    retest_date: str | None = None  # ISO 8601. NOT expiry_date — see docs/reference/
    results: tuple[Measurement, ...] = ()
    stated_conformance: bool | None = None  # what the supplier claimed, which may be wrong
    cited_spec_revision: str | None = None


@dataclass(frozen=True)
class Finding:
    """One structured reason, for callers to RENDER. Callers never reconstruct the reasoning from
    the output — two callers reassembling it would explain the same decision differently."""

    code: str  # stable machine code, e.g. "supplier_not_approved", "result_out_of_limits"
    message: str  # written for the person who has to act on it
    attribute: str | None = None
    evidence: str | None = None  # what on the document supports this


@dataclass(frozen=True)
class Decision:
    """The one result type. `action` is accept or hold — nothing else crosses the boundary.

    `hold` is not a failure mode of the pipeline; it is a first-class answer meaning a human must
    look. Holding when unsure and accepting when sure are both correct outcomes, and the ledger
    penalises getting either wrong.
    """

    doc_id: str
    action: str  # "accept" | "hold"
    certificate: Certificate | None = None
    findings: tuple[Finding, ...] = ()
    schema_version: str = SCHEMA_VERSION
    explanation: list[str] = field(default_factory=list)


def compile_spec(raw) -> Spec:
    """raw.RawSpec -> Spec. The one place validated raw becomes domain truth."""
    return Spec(
        document=raw.document,
        revision=raw.revision,
        effective=raw.effective,
        attributes=tuple(
            SpecAttribute(
                attribute=a.attribute,
                lower=a.lower,
                upper=a.upper,
                unit=a.unit,
                reportable_method=a.reportable_method,
            )
            for a in raw.attributes
        ),
    )
