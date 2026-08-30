"""Correctness of the derivation — the half `--check` cannot prove.

`tools/derive_reference.py --check` compares generator output to generator output. If the parse
rule is wrong, the committed file is wrong identically, the diff is empty, and the gate is green.
So the parse rule is asserted here against hand-written expectations, and — the load-bearing part —
against inputs that must yield NOTHING. A parser that is too eager invents acceptance criteria, and
an invented limits row is how a system accepts a lot it should have held.

Last test in the file is the mutation test: it corrupts the committed artifact and asserts the
freshness gate goes RED. A detective control nobody has watched fire is one you are trusting.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from derive_reference import derive_spec, derive_suppliers, parse_spec_row  # noqa: E402


def test_parses_a_real_acceptance_row():
    row = parse_spec_row("| Assay | 99.0 – 101.0 | % | HPLC (SPEC-7 M-01) |")
    assert row == {
        "attribute": "Assay",
        "lower": 99.0,
        "upper": 101.0,
        "unit": "%",
        "reportable_method": "HPLC (SPEC-7 M-01)",
    }


def test_keeps_the_method_verbatim_including_angle_brackets():
    """USP <616> must survive intact — the method IS the acceptance criterion (SPEC-7 §3.1)."""
    row = parse_spec_row("| Bulk Density | 0.45 – 0.75 | g/mL | USP <616> (SPEC-7 M-21) |")
    assert row["reportable_method"] == "USP <616> (SPEC-7 M-21)"


@pytest.mark.parametrize(
    "line",
    [
        "|---|---|---|---|",  # the table separator
        "| Attribute | Limits | Unit | Reportable method |",  # the header
        "| Revision | D |",  # a two-column metadata row
        "| Review cycle | Annual, or on change of an acceptance method |",
        "Loss on drying (M-03) is retained as an indicative method only.",
        "",
        "| Assay | 99.0 | % | HPLC |",  # one limit, not a range
    ],
    ids=["separator", "header", "metadata", "review-cycle", "prose", "blank", "single-limit"],
)
def test_non_criteria_yield_nothing(line):
    """The negative cases. Anything that is not an acceptance criterion must return None, never a
    row with a plausible default — a fabricated limit is worse than a missing one."""
    assert parse_spec_row(line) is None


def test_inverted_limits_are_refused_not_silently_swapped():
    with pytest.raises(ValueError):
        parse_spec_row("| Assay | 101.0 – 99.0 | % | HPLC (SPEC-7 M-01) |")


def test_spec_without_a_revision_is_refused():
    """SPEC-7 §4 turns on which revision a certificate cites, so a spec with no revision is not a
    spec with an unknown revision — it is a refusal to proceed."""
    with pytest.raises(ValueError, match="Revision"):
        derive_spec("| Assay | 99.0 – 101.0 | % | HPLC (SPEC-7 M-01) |")


def test_empty_source_never_yields_an_empty_spec():
    """An empty limits table would compare every result against nothing and accept everything."""
    with pytest.raises(ValueError):
        derive_spec("| Revision | D |\n| Effective | 1 March 2026 |\n")


def test_suppliers_are_read_from_the_list_not_the_prose():
    text = "The ERP will not create a lot for a supplier not on this list.\n\n- Acme Ltd\n- Beta BV\n"
    assert derive_suppliers(text)["suppliers"] == ["Acme Ltd", "Beta BV"]


def test_empty_supplier_master_is_refused():
    with pytest.raises(ValueError):
        derive_suppliers("no bullets here\n")


def test_committed_reference_matches_the_source_by_a_second_route():
    """Re-verify the committed file by reading the source a DIFFERENT way than the generator does.

    Two implementations agreeing is weak evidence when one calls the other. This one does not parse
    the table at all — it asserts that every attribute named in the committed JSON appears verbatim
    in the source text alongside its own limits, which the regex route could not fake.
    """
    source = (ROOT / "reference" / "source" / "SPEC-7-revD.md").read_text(encoding="utf-8")
    committed = json.loads((ROOT / "reference" / "spec-7.json").read_text(encoding="utf-8"))
    assert committed["attributes"], "committed spec has no attributes"
    for attribute in committed["attributes"]:
        needle = f"{attribute['attribute']} | {attribute['lower']} – {attribute['upper']}"
        assert needle in source, f"{needle!r} is not in the controlled source — the committed spec is wrong"


def test_the_freshness_gate_has_been_watched_to_fail(tmp_path, monkeypatch):
    """Corrupt the committed artifact and assert `--check` goes RED."""
    target = ROOT / "reference" / "spec-7.json"
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original.replace('"upper": 101.0', '"upper": 999.0'), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "derive_reference.py"), "--check"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, "the freshness gate stayed green over a corrupted artifact"
        assert "stale" in result.stderr
    finally:
        target.write_text(original, encoding="utf-8")
