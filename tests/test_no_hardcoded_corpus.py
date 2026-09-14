"""The engagement corpus lives in this repo. It must not become a dependency of the program.

`engagement/` was vendored so a reviewer can clone one thing and run it. That convenience creates two
hazards, and both are checked here rather than trusted:

1. **The corpus path could quietly become a default.** The brief is explicit: the pipeline is run
   against documents it has not seen, so "the path to the documents and to any reference data must be
   an input to your program, not a constant inside it." A default that happens to work on the
   supplied corpus is a wrong answer that passes locally.

2. **SPEC-7 now exists twice in one repo** — here, and vendored under `reference/source/` where the
   derivation reads it. Two copies of a controlled document is the drift hazard this project warns
   about repeatedly; the second copy is deliberate (it models the production path) so the answer is
   to check they agree, not to delete one.
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENGAGEMENT = ROOT / "engagement"
VENDORED = ROOT / "reference" / "source"


def _source_files() -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "ls-files", "src", "tools"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [ROOT / p for p in out.stdout.split() if p.endswith(".py")]


@pytest.mark.parametrize("path", _source_files(), ids=lambda p: p.name)
def test_no_source_file_references_the_engagement_corpus(path):
    """`engagement/` may be read by the Makefile, the docs and the tests. Never by the program."""
    body = path.read_text(encoding="utf-8")
    for forbidden in ("engagement/", "engagement\\", "student-materials"):
        assert forbidden not in body, (
            f"{path.name} references {forbidden!r}. The corpus is a runtime input; a path baked into "
            f"the program is a defect the supplied corpus would hide."
        )


@pytest.mark.parametrize("name", ["SPEC-7-revD.md", "supplier-master.md"])
def test_the_vendored_controlled_documents_match_the_engagement_copy(name):
    """Deliberate duplication, checked rather than trusted. If these diverge, the derived reference
    data is being generated from something the engagement did not supply."""
    engagement = (ENGAGEMENT / name).read_bytes()
    vendored = (VENDORED / name).read_bytes()
    assert engagement == vendored, (
        f"{name} differs between engagement/ and reference/source/. The derivation reads the "
        f"vendored copy, so a divergence means spec-7.json no longer reflects what was supplied. "
        f"Re-vendor and run `make reference`."
    )


def test_the_supplied_validator_is_present():
    """The brief asks for the output to be checked with its own validator. Keeping it in the repo is
    what lets a reviewer verify the submission without hunting for the materials."""
    assert (ENGAGEMENT / "validate_submission.py").is_file()


def test_the_corpus_is_complete():
    """36 documents, as supplied. A short corpus would silently change every count in the docs."""
    assert len(list((ENGAGEMENT / "documents").glob("*.txt"))) == 36
