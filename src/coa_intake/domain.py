"""Compiled domain objects — what the runtime consumes.

The compile step validates raw input once, at load, and emits these typed objects. Runtime walks
domain objects, never loose dicts. Three laws are visible in the types themselves:

  * **Provenance.** A measured value is never a bare number. `Measurement` carries value, unit, the
    source it was read from, the method that produced it, and — where a unit was converted — what it
    said before, because SPEC-7 §2 requires the conversion to be *recorded*, not just performed.
  * **Missing is not zero.** An attribute the certificate did not report is absent from `results`,
    not present as 0.0. Absence is a decision input in its own right — SPEC-7 §2 requires every
    attribute, so a missing one is a reason to hold, never a zero to compare against a limit.
  * **Conformance is per result.** Certificates state PASS against individual attributes, not against
    the document, and SPEC-7 §5 turns on a per-result contradiction. So the claim lives on the
    Measurement it is a claim about.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Bumped when the shape of an emitted decision changes. Any output that crosses a boundary or is
# persisted carries this, so a consumer can tell which contract produced the line it is reading.
SCHEMA_VERSION = "1.1.0"

ACCEPT = "accept"
HOLD = "hold"

# Where a held lot goes (ADR-0005). Four, deliberately: a lot held because a date was unreadable
# must not consume the attention of the people who rule on quality failures.
ROUTE_QUALITY = "quality"
ROUTE_PROCUREMENT = "procurement"
ROUTE_SUPPLIER_QUERY = "supplier_query"
ROUTE_INTAKE_KEYING = "intake_keying"


@dataclass(frozen=True)
class Measurement:
    """A measured value with provenance — never a bare number."""

    attribute: str  # canonical SPEC-7 attribute name, after synonym mapping
    value: float  # in `unit`, already canonical
    unit: str  # canonical unit: converted on write, never at comparison time
    source: str  # doc_id + locator: which document, and where in it
    # SPEC-7 §2 numbers the reportable method per attribute; the code is the identity, the name is
    # how the supplier wrote it. Both are recorded: the code decides, the name is evidence.
    method_code: str | None = None  # "M-01" — None if the certificate cited no SPEC-7 code
    method_name: str | None = None  # "HPLC" — None if it named nothing
    stated_conformance: bool | None = None  # what the supplier claimed FOR THIS RESULT, if anything
    # SPEC-7 §2: "the conversion shall be recorded". These hold what the certificate actually said.
    original_value: float | None = None
    original_unit: str | None = None

    @property
    def was_converted(self) -> bool:
        return self.original_unit is not None and self.original_unit != self.unit


@dataclass(frozen=True)
class DateReading:
    """A date, and how confident we are about what it says.

    `resolution` records which rung of the ADR-0008 ladder answered: `explicit` (ISO or a written
    month), `stated` (the document declared its own convention), or `ambiguous` (nothing resolved
    it — hold). There is no `inferred`: ADR-0008 removed the rung that read a date from a supplier's
    other certificates, so nothing in this system resolves a date from anything but the document in
    front of it.
    """

    raw: str
    iso: str | None = None
    resolution: str = "ambiguous"

    @property
    def is_resolved(self) -> bool:
        return self.iso is not None


@dataclass(frozen=True)
class SpecAttribute:
    """One acceptance criterion, canonicalized: limits are already in the canonical unit."""

    attribute: str
    lower: float
    upper: float
    unit: str
    reportable_method: str  # as SPEC-7 §2 prints it, e.g. "HPLC (SPEC-7 M-01)"

    @property
    def method_code(self) -> str:
        """The SPEC-7 code — the part that identifies the method rather than describes it."""
        m = re.search(r"M-\d+", self.reportable_method)
        if not m:
            raise ValueError(
                f"{self.attribute}: reportable method {self.reportable_method!r} cites no SPEC-7 "
                f"code, so there is nothing to compare a certificate against."
            )
        return m.group(0).upper()

    @property
    def method_name(self) -> str:
        """The name SPEC-7 gives the method, e.g. 'HPLC'."""
        return re.split(r"[(\[]", self.reportable_method)[0].strip()


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
    manufacture_date: DateReading | None = None
    retest_date: DateReading | None = None  # NOT expiry_date — see docs/working-answers.md R14
    results: tuple[Measurement, ...] = ()
    cited_spec_revision: str | None = None
    lot_id_conflicts: tuple[str, ...] = ()  # every distinct lot number the document printed, if >1


@dataclass(frozen=True)
class Finding:
    """One structured reason, for callers to RENDER. Callers never reconstruct the reasoning from
    the output — two callers reassembling it would explain the same decision differently."""

    code: str  # stable machine code, matching a rule id in reference/policy.json
    message: str  # written for the person who has to act on it
    route: str | None = None
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
    action: str  # ACCEPT | HOLD
    certificate: Certificate | None = None
    findings: tuple[Finding, ...] = ()
    schema_version: str = SCHEMA_VERSION
    spec_revision: str | None = None  # which revision this was judged under — see policy R4
    explanation: list[str] = field(default_factory=list)

    @property
    def route(self) -> str | None:
        """Where a held lot goes. The most severe route among the findings wins; the ordering is the
        rule order in policy.json, so the first finding is already the most severe."""
        for finding in self.findings:
            if finding.route:
                return finding.route
        return None


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
