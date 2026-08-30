---
id: ADR-0002
title: derive the SPEC-7 reference data instead of hand-keeping it
status: Accepted
date: 2026-08-29
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [generated-data, reference-data]
---

# ADR-0002: derive the SPEC-7 reference data instead of hand-keeping it

## Context

The system needs the acceptance limits, the reportable method per attribute, and the approved-supplier
set. All three already exist in documents Thornbury controls: SPEC-7 rev D §2, and the ERP supplier
master.

The obvious move is to type them into a JSON file. That file then looks like config, is reviewed like
config, and has nothing comparing it to its source — so when Quality issues rev E, the file is wrong and
nothing says so. SPEC-7 §4 exists precisely because certificates citing withdrawn revisions are a real
hazard; a downstream system silently asserting a withdrawn revision is the same hazard with more reach.

## Decision

The controlled sources are vendored under `reference/source/` with a `PROVENANCE.md` recording revision
and vendoring date. `tools/derive_reference.py` computes `reference/*.json` from them. **The script is
the reviewed thing; the JSON is output.** `make freshness` gates staleness in `make check` and in CI.

Correctness is established *separately from freshness*, because `--check` compares generator output to
generator output and cannot see a backwards derivation. `tests/test_derivation.py` asserts the parse rule
against hand-written expectations including negative cases, re-verifies the committed file by reading the
source by a different route than the generator uses, and contains a mutation test that corrupts the
artifact and asserts the freshness gate goes red.

## Consequences
- **Good:** a SPEC-7 revision is a reference-data change, not a code change, and the diff shows exactly
  which limits moved.
- **Good:** the failure mode this guards against — an accepted lot measured against withdrawn limits — is
  the expensive one.
- **Cost:** the silent-error risk moves from the data into the generator, which is harder to review, not
  easier. That is why bullet three above is not optional: a repo that generates everything and tests none
  of it has made things worse.
- **Cost:** `reference/source/` is a *copy* of a controlled document and will drift.
- **Watch:** nobody owns telling this repo that SPEC-7 changed. Until that has an owner, the vendored
  copy is the weakest link in the chain, and no amount of gating inside this repo fixes it.

## Options considered
- **Hand-keep the JSON.** Rejected: nothing compares it to its source.
- **Read SPEC-7's markdown at runtime.** Rejected: it makes every run depend on parsing a prose document,
  moves a load-bearing failure from build time to run time, and gives no reviewable diff when limits move.
- **Fetch from the QMS at runtime.** Rejected today — no such interface has been offered, and it would
  make the acceptance criteria a network dependency. Revisit if Quality can provide a feed; that would
  also fix the drift problem above.
