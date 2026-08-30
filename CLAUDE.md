# How we work — Thornbury CoA Intake

> Engineering contract for this repo. Read `docs/overview.md` first for *what*; this is *how*. Where a doc
> conflicts with the code, the code wins.

## Surfaces
Declared in `REPO-SURFACE.yaml`: `repo_kind: rules-engine`, `criticality: regulated`. True surfaces:
`has_consumers`, `handles_secrets`, `external_network`, `decisioning_or_scoring`, `data_measurement`,
`generated_code`, `stores_or_shows_time`. The universal-core invariants below always apply; each surface
adds its own section.

`deployed` and `stateful` are **false today and expected to become true** — the working slice is a batch
CLI. Their obligations are the go-live backlog in `STATUS.md`, not silently-passed lines.

## Storage model
- Config/truth lives in reviewed files in-repo under `reference/`, **derived** by
  `tools/derive_reference.py` from the controlled sources vendored in `reference/source/`. Environment
  values come through `paths.py`, never hardcoded.
- State is none. The pipeline reads documents and writes one decisions file. It owns no database. When
  the audit trail becomes queryable, `stateful` turns true and this line changes with it.

## Dead-simple default
The smallest single path that meets today's requirement. Extra branches, flags, formats, and "temporary"
shims are guilty until proven necessary; if you must add one, write the requirement, why the simple path
fails, the owner, the deletion trigger, and the guard/test — under "Active compatibility paths" below.

## Invariants (universal core — a test fails if you break one)
- **One canonical path.** `cli.main` → `cli.run` → `app.decide`. One entry per concern; no "accept
  both"/default-on fallback. *(`tests/test_contract.py::test_every_document_produces_exactly_one_line`)*
- **Trust boundary.** External input is validated by `raw.py`'s strict models — `extra="forbid"` — before
  domain logic branches on it. *(`test_unknown_fields_are_an_error_not_a_silent_drop`)*
- **One config boundary.** `paths.py` is the only module in `src/` that reads the environment; required
  config missing → fail-closed. *(`tests/test_path_ownership.py`, `test_missing_config_fails_closed`)*
- **Paths are inputs, never constants.** The pipeline is run against documents it has not seen. A
  documents or reference path baked into the program is a defect.
  *(`test_an_explicit_path_does_not_need_the_env`)*
- **Determinism.** Same input → same output; documents are processed in sorted order; no clock, entropy,
  or network reaches `decide()`. *(`test_decide_is_deterministic`)*
- **Fail loud.** Missing/invalid input → a structured error, never a default or silent skip.
  *(`test_an_accept_without_a_certificate_fails_loud`, `test_an_empty_documents_directory_fails_loud`)*
- **Breaking changes recorded.** A breaking change lands a `CHANGELOG` entry + migration note in the same
  change, and bumps `domain.SCHEMA_VERSION`.

## Invariants — decisioning_or_scoring
- **Externalized policy.** Limits, reportable methods and the approved-supplier set live in `reference/`
  as reviewed, versioned, derived artifacts — never in `if` branches. A SPEC-7 revision must be a
  reference-data change, not a code change.
- **Compile validated raw → domain at a boundary.** `raw.py` validates; `domain.py` compiles once;
  runtime walks domain objects, never loose dicts.
- **Missing is not zero.** An attribute the certificate did not report is *absent* from `results`. It is
  never 0.0 — and note that 0.0 sits inside the SPEC-7 limits for Moisture and Heavy Metals, so a
  defaulted zero reads as a pass. *(`test_an_unreported_attribute_is_absent_not_zero`)*
- **One runtime path.** `decide()` is the entry. Inspection helpers are siblings, never alternates.
- **Explanation is a contract.** `Decision` carries `Finding`s that callers *render*. A caller never
  reassembles the reasoning — two callers doing so would explain the same hold differently, and a hold
  reason is read by a person who has to act on it.
- **No hidden tie-break.** If the evidence does not settle a lot, the answer is `hold` with a reason —
  never a quiet default in either direction.
- **Versioned outputs.** Every emitted line carries `schema_version`.
  *(`test_every_decision_carries_a_schema_version`)*
- **Models propose; deterministic code decides.** When an LLM enters the extraction loop, it emits
  candidate facts with provenance. Schemas, validation and the SPEC-7 rules decide what becomes truth.
  The model never writes the decision.
- **Eval set measures change.** A change touching extraction or the rules is measured against a labelled
  set before it lands. **This does not exist yet** — see `STATUS.md`.

## Invariants — data_measurement
- **Provenance on every measured value.** `Measurement` carries `{attribute, value, unit, source, method}`.
  Never a bare number. *(`test_a_measurement_cannot_be_a_bare_number`)*
- **Canonicalize on write.** SPEC-7 §2 requires a result in a different unit to be converted *before*
  comparison, and the conversion recorded. Conversion happens when the `Measurement` is built, never at
  comparison time.
- **The method is part of the result.** SPEC-7 §3.1: a result from a non-reportable method is indicative
  and cannot release a lot. A value without its method is not a result, and `method=None` is a distinct,
  meaningful state — not an absent field.

## Invariants — generated_code (derived data)
- **Derived data is generated, never hand-maintained.** `reference/*.json` is output.
  `tools/derive_reference.py` is the reviewed thing.
- **Freshness is gated** — `make freshness` regenerates to a clean comparison.
- **Freshness is NOT correctness.** `--check` compares generator output to generator output; a backwards
  derivation passes it. Correctness lives in `tests/test_derivation.py`: the parse rule asserted against
  hand-written expectations *including negative cases*, plus a re-verification of the committed file that
  reads the source by a different route than the generator does.
- **The gate has been watched to fail.** `test_the_freshness_gate_has_been_watched_to_fail` corrupts the
  artifact and asserts the check goes red.

## Invariants — stores_or_shows_time
- Dates are canonicalized to ISO 8601 on write. A date that reads two ways has not been normalised, it
  has been passed on.
- `retest_date` is **not** `expiry_date`. The ERP field is named `expiry_date` and Purchasing runs reorder
  logic off it; the certificate states a retest date. Never map one onto the other silently — that
  conflation is an open question for the client, recorded in `STATUS.md`.

## Invariants — has_consumers
- `decisions.jsonl` is a contract. Every document gets exactly one line; a document that cannot be
  processed is a `hold` with a reason, never a silence.
- `action` is `accept` or `hold`. Nothing else crosses the boundary.

## Change → check matrix
| Change | Run |
|---|---|
| Code-only refactor | `make lint test` |
| Logic / boundary / entry-path change | `make check` (+ the eval set, once it exists) |
| Reference data change | `make reference && make freshness test` — and review the JSON delta |
| `reference/source/` change (a SPEC-7 revision) | `make reference`, an ADR, and a `CHANGELOG` entry |
| Submission-contract change | `make check` + bump `SCHEMA_VERSION` + `CHANGELOG` |

## Complexity we accept
- **A vendored copy of SPEC-7 and the supplier master** (`reference/source/`). Guarantee it protects: the
  derivation has a source *in this repo*, so the freshness gate has something to compare against and a
  reviewer can see what the JSON was derived from. Cost: it is a copy of a controlled document and it will
  drift. Deletion trigger: an agreed feed from the QMS. Owner: Quality (Marisol Vega) — not yet engaged.
- **The extraction seam** (`extraction.Extractor`). Guarantee: OCR is explicitly out of scope, and the
  seam is what makes that a scoping decision rather than a hole. Cost: one indirection over one
  implementation.

## Negative lessons we keep
- A defaulted zero is not a missing value. For Moisture and Heavy Metals, 0.0 is *inside* the limits, so
  defaulting reads as a pass. This is the shape of an accept that should have been a hold.
- Freshness gates prove staleness, not correctness. A `--check` that is green over a backwards derivation
  is false confidence, and it is the confident kind.
- No per-item DEBUG inside hot loops. No casual lint/type suppression. Don't hand-enumerate combinatorial
  variants — generate them.

## Active compatibility paths (must be retired)
**None at present.** A line removed here must match a deletion in the same commit.
