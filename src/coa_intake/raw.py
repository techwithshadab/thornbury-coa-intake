"""Trust boundary — strict models that validate external input BEFORE any domain logic branches on it.

Two kinds of external input cross this boundary:

  * the certificate text, which arrives from the extraction stub and is untrusted by construction —
    a supplier wrote it, and some of them are wrong (transposed lot numbers, a PASS statement over
    an out-of-limit result);
  * the reviewed reference data (SPEC-7 acceptance table, supplier master, attribute synonyms),
    which is trusted but must still be well-formed, because a malformed limits table silently
    accepting everything is the worst failure this system has.

`extra="forbid"` on every model: an unexpected key is an error, not a silent drop. A field the
reference data grew that this code does not know about must stop the run, not be ignored.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RawExtraction(BaseModel):
    """What the extraction stage hands over. Text only — this system does no OCR (out of scope)."""

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1)
    text: str
    extractor: str = Field(min_length=1, description="which extractor produced this, for provenance")


class RawSpecAttribute(BaseModel):
    """One row of the SPEC-7 §2 acceptance table, as reviewed reference data."""

    model_config = ConfigDict(extra="forbid")

    attribute: str = Field(min_length=1)
    lower: float
    upper: float
    unit: str = Field(min_length=1)
    reportable_method: str = Field(min_length=1)


class RawSpec(BaseModel):
    """The acceptance specification. Carries its revision: a certificate citing a withdrawn
    revision is referred to Quality (SPEC-7 §4), so the revision is load-bearing, not a label."""

    model_config = ConfigDict(extra="forbid")

    document: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    effective: str = Field(min_length=1)
    attributes: list[RawSpecAttribute] = Field(min_length=1)


class RawSupplierMaster(BaseModel):
    """The approved-supplier list. The ERP will not create a lot for a supplier not on it."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    suppliers: list[str] = Field(min_length=1)
