---
id: ADR-0003
title: treat extraction as a seam and keep OCR out of scope
status: Accepted
date: 2026-08-29
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [scope, extraction]
---

# ADR-0003: treat extraction as a seam and keep OCR out of scope

## Context

Thornbury receives PDFs across roughly forty suppliers with, in the sponsor's words, layouts "all over
the place." Making OCR production-grade is real work, and the engagement brief puts it out of scope for
this build. The documents were supplied as text extractions.

Two ways to honour that scoping. Write against text files directly and note the gap in prose; or define
the interface and ship one implementation behind it.

## Decision

`extraction.Extractor` is a protocol. `TextFileExtractor` is the single implementation and reads the
supplied `.txt` files, sorted by `doc_id` for determinism. Everything downstream is written against the
protocol. What productionalising it takes is written up in `docs/reference/extraction-stub.md` — as a
document with an owner, not a docstring.

## Consequences
- **Good:** the scoping is visible in the code as a named seam, so the next team can see exactly where
  the missing work attaches and that nothing else assumes text files.
- **Good:** it keeps the decision rules independently testable, which is what lets the SPEC-7 logic be
  built and measured before a real extractor exists.
- **Cost:** one indirection over one implementation. Accepted; recorded in `CLAUDE.md` under "complexity
  we accept" with a deletion trigger.
- **Watch:** `RawExtraction` is **known to be incomplete**. A production extractor must carry per-field
  confidence — a low-confidence assay result is a hold reason — and today's exact text reader has none to
  carry. Adding it is a breaking change to the trust boundary and gets a `CHANGELOG` entry and a
  `SCHEMA_VERSION` bump. Do not let the current shape read as settled.

## Options considered
- **Read text files directly, note the gap in the README.** Rejected: the gap then lives only in prose,
  and the coupling to text files spreads quietly through the code that consumes it.
- **Build a real PDF/OCR pipeline now.** Rejected: explicitly out of scope, and it would consume the
  budget that the judgement — the part Thornbury is actually buying — needs.
- **Accept an abstract base class instead of a protocol.** Rejected as ceremony: one implementation, and
  a protocol imposes no inheritance on a future one.
