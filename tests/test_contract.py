"""The submission contract, and the invariants that hold it up.

These are the tests that fail when a law in CLAUDE.md is broken. They are deliberately about the
BOUNDARY — what crosses out of this system — rather than about internals, because the boundary is
what a consumer binds to and what the ledger reads.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from pydantic import ValidationError

from coa_intake import paths
from coa_intake.app import decide
from coa_intake.cli import _to_line, run
from coa_intake.domain import SCHEMA_VERSION, Certificate, Measurement, Spec, SpecAttribute
from coa_intake.raw import RawExtraction, RawSpec

SPEC = Spec(
    document="SPEC-7",
    revision="D",
    effective="1 March 2026",
    attributes=(SpecAttribute("Assay", 99.0, 101.0, "%", "HPLC (SPEC-7 M-01)"),),
)


# --- Trust boundary -------------------------------------------------------------------------


def test_unknown_fields_are_an_error_not_a_silent_drop():
    """A reference file that grows a key this code does not understand must stop the run."""
    with pytest.raises(ValidationError):
        RawSpec.model_validate(
            {
                "document": "SPEC-7",
                "revision": "D",
                "effective": "1 March 2026",
                "attributes": [
                    {
                        "attribute": "Assay",
                        "lower": 99.0,
                        "upper": 101.0,
                        "unit": "%",
                        "reportable_method": "HPLC",
                    }
                ],
                "criticality_override": "accept-everything",
            }
        )


def test_extraction_must_name_its_extractor():
    """Provenance starts at the edge: text with no extractor named cannot be traced."""
    with pytest.raises(ValidationError):
        RawExtraction(doc_id="COA-0001", text="...", extractor="")


# --- Provenance and missing-is-not-zero -----------------------------------------------------


def test_a_measurement_cannot_be_a_bare_number():
    """Constructing a Measurement without a unit and a source is impossible by type."""
    with pytest.raises(TypeError):
        Measurement(attribute="Assay", value=99.8)  # type: ignore[call-arg]


def test_an_unreported_attribute_is_absent_not_zero():
    """The certificate said nothing about Moisture. `results` must not contain a 0.0 for it —
    0.0 is inside the SPEC-7 moisture limits, so a defaulted zero reads as a pass."""
    cert = Certificate(
        doc_id="COA-0001",
        results=(Measurement("Assay", 99.8, "%", "COA-0001:results-table"),),
    )
    assert [m.attribute for m in cert.results] == ["Assay"]
    assert all(m.attribute != "Moisture" for m in cert.results)


# --- The one runtime path -------------------------------------------------------------------


def test_decide_is_deterministic():
    cert = Certificate(doc_id="COA-0001")
    assert decide(cert, SPEC) == decide(cert, SPEC)


def test_every_decision_carries_a_schema_version():
    """Output that crosses a boundary says which contract produced it."""
    assert _to_line(decide(Certificate(doc_id="COA-0001"), SPEC))["schema_version"] == SCHEMA_VERSION


def test_a_hold_always_states_a_reason():
    """A hold with no reason is a silence with extra steps — someone has to act on it."""
    line = _to_line(decide(Certificate(doc_id="COA-0001"), SPEC))
    assert line["action"] == "hold"
    assert line["hold_reason"].strip()


def test_an_accept_without_a_certificate_fails_loud():
    """Fail loud, never silent: an accept that carries no fields is a defect, not an empty object."""
    from coa_intake.domain import Decision

    with pytest.raises(RuntimeError):
        _to_line(Decision(doc_id="COA-0001", action="accept", certificate=None))


# --- Config boundary ------------------------------------------------------------------------


def test_missing_config_fails_closed(monkeypatch):
    monkeypatch.delenv(paths.WORKSPACE_ENV, raising=False)
    with pytest.raises(RuntimeError):
        paths.documents_root(None)


def test_an_explicit_path_does_not_need_the_env(tmp_path, monkeypatch):
    """The documents path is an INPUT. The pipeline runs against unseen documents."""
    monkeypatch.delenv(paths.WORKSPACE_ENV, raising=False)
    (tmp_path / "docs").mkdir()
    assert paths.documents_root(str(tmp_path / "docs")) == (tmp_path / "docs").resolve()


# --- End to end -----------------------------------------------------------------------------


def test_every_document_produces_exactly_one_line(tmp_path):
    """A document that cannot be processed is a hold, not a silence."""
    docs = tmp_path / "documents"
    docs.mkdir()
    for doc_id in ("COA-0002", "COA-0001", "COA-0003"):
        (docs / f"{doc_id}.txt").write_text("ANALYTICAL REPORT\n", encoding="utf-8")

    out = tmp_path / "decisions.jsonl"
    reference = pathlib.Path(__file__).resolve().parents[1] / "reference"
    assert run(docs, reference, out) == 3

    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert [line["doc_id"] for line in lines] == ["COA-0001", "COA-0002", "COA-0003"], "order must be stable"
    assert all(line["action"] in ("accept", "hold") for line in lines)


def test_an_empty_documents_directory_fails_loud(tmp_path):
    """Zero documents is not zero work — it means the path is wrong."""
    docs = tmp_path / "documents"
    docs.mkdir()
    reference = pathlib.Path(__file__).resolve().parents[1] / "reference"
    with pytest.raises(RuntimeError, match="no .txt documents"):
        run(docs, reference, tmp_path / "out.jsonl")
