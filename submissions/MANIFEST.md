# Submission runs

Three runs of the pipeline over the 36 supplied certificates.

## What "three runs" means here

The brief says *"your three `decisions.jsonl` runs are scored"* and does not say whether that means
three submissions over time or three executions checked against each other. **We read it the way that
is falsifiable either way:** three independent executions, submitted as three files, and shown to be
byte-identical.

That is not a trick to satisfy the wording. Determinism is a declared invariant of this system
(`CLAUDE.md`) and it is the property that makes ADR-0007's deterministic parser worth choosing over a
model. If the three runs are being compared to detect run-to-run variance, this is the evidence. If
they are meant to be three separate submissions, here they are.

**If that reading is wrong, ask** — it is question Q26 in `docs/open-questions.md` and it is cheap to
redo.

## What to read

| Path | What it is |
|---|---|
| `run-1/`, `run-2/`, `run-3/` | **The submission.** Three independent executions, byte-identical. |
| `decisions.jsonl` | A convenience copy of the same output at the top level, for anyone who expects one file rather than three. Identical to each run — not a fourth result. |

Regenerate all four with `make submission` from the repo root; it also runs the engagement's own
validator and fails if the three runs diverge. CI runs it on every push and fails if the committed
output changes.

## Provenance

| | |
|---|---|
| Commit | `6f9067d` |
| Policy version | 1.0.0 (status: **provisional**) |
| SPEC-7 revision | D |
| Documents | 36, from the supplied corpus |
| Generated | 2026-09-03 |
| MD5 (all three) | `472fd81c09e9f5502a2f4bb641d3bfcb` |

## Result

| | Count | Share |
|---|---:|---:|
| accept | 21 | 58% |
| hold → `quality` | 5 | 14% |
| hold → `intake_keying` | 5 | 14% |
| hold → `procurement` | 3 | 8% |
| hold → `supplier_query` | 2 | 6% |

All three files pass `validate_submission.py`. **That says nothing about whether the answers are
right** — there is no labelled set, so this split is arithmetic over 36 documents, not a measurement.

## Reproducing

```bash
make setup
make run DOCS=<documents dir> OUT=<file>
```

A clean clone reproduces these bytes exactly. If your run differs, the difference is the finding —
report it rather than working around it.
