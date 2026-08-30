"""The extraction stage — A STUB WITH A DEFINED INTERFACE.

Thornbury receives PDFs. Making OCR production-grade is real work and is explicitly out of scope
for this build, so this module defines the seam rather than crossing it: everything downstream is
written against `Extractor`, and swapping a text reader for a real PDF/OCR pipeline is a change
here and nowhere else.

`TextFileExtractor` is the one implementation that exists today. It reads the pre-extracted .txt
files the engagement supplied. What productionalising this would take is written up in
docs/reference/extraction-stub.md — do not let this docstring become the only record of it.
"""

from __future__ import annotations

import pathlib
from collections.abc import Iterator
from typing import Protocol

from .raw import RawExtraction


class Extractor(Protocol):
    """The seam. A production implementation reads PDFs; this one reads text files."""

    name: str

    def extract_all(self, documents_root: pathlib.Path) -> Iterator[RawExtraction]:
        """Yield one RawExtraction per document found, in a stable order."""
        ...


class TextFileExtractor:
    """Reads the supplied `.txt` extractions. Deterministic: documents are yielded sorted by
    doc_id, so two runs over the same directory produce the same order."""

    name = "text-file-extractor/0.1.0"

    def extract_all(self, documents_root: pathlib.Path) -> Iterator[RawExtraction]:
        paths = sorted(documents_root.glob("*.txt"), key=lambda p: p.stem)
        if not paths:
            raise RuntimeError(
                f"no .txt documents under {documents_root} — this extractor reads pre-extracted "
                f"text, not PDFs. Point --documents at the extraction directory."
            )
        for path in paths:
            yield RawExtraction(
                doc_id=path.stem,
                text=path.read_text(encoding="utf-8"),
                extractor=self.name,
            )
