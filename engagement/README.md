# The engagement materials

**This directory is not our work.** It is the material MathCo's FDE Academy supplied for the
Thornbury capstone, vendored here so the repository is one thing a reviewer can clone and run rather
than two they have to be told about.

| File | What it is |
|---|---|
| `MISSION.md` | The capstone brief — what is asked for and how it is assessed |
| `the-ask.md` | The sponsor's request, and the note from the intake team lead |
| `documents/` | 36 certificates, as text extractions |
| `SPEC-7-revD.md` | Thornbury's ingredient acceptance specification |
| `supplier-master.md` | The approved-supplier list |
| `erp-fields.md` · `qa-tracker.md` · `org.md` | The ERP lot record, QA's tracker, and who owns what |
| `validate_submission.py` | Supplied shape-checker for `decisions.jsonl` |

## Two things to know before you use it

**The corpus is an input, not a constant.** The pipeline is scored against certificates it has not
seen, so `--documents` is a required argument and there is no default path anywhere in `src/`.
`tests/test_no_hardcoded_corpus.py` enforces that: this directory existing must not become a
dependency. `make submission` passes the path explicitly, which is the Makefile's business, not the
program's.

**`SPEC-7-revD.md` and `supplier-master.md` also exist under `reference/source/`, deliberately.**
That copy models what happens in production — a controlled document vendored from the QMS with a
provenance record — and the derivation runs from it, not from here. Two copies of a controlled
document in one repo is exactly the drift hazard this project keeps warning about, so
`tests/test_no_hardcoded_corpus.py` asserts they are byte-identical and fails if they diverge.
