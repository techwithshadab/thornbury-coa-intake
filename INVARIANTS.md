# Invariants — `decisioning_or_scoring` surface

Copy these into your repo's `CLAUDE.md` under an **"## Invariants — decisioning_or_scoring"** section. They
are the conditional invariants for a repo that derives/ranks/matches/scores/decides. They are *additions* to
the universal core invariants — not replacements. (Language-neutral; the Python skeleton in this pack is one
implementation.)

- **Externalized policy/data.** Facts, thresholds, mappings, prompts, and rules live as named, reviewed,
  versioned, tested artifacts outside incidental control flow — never in `if` branches. A domain fact changes
  without a code change.
- **Compile validated raw → domain at a boundary.** External input is validated by strict models
  (reject unknown fields) and a compile step emits typed domain objects once; runtime walks domain objects,
  never loose dicts.
- **Provenance on derived values.** Every scored/derived value carries `{value, unit, source}` — never a bare
  number, so nobody mistakes a stale or unsourced figure for truth.
- **Canonicalize on write, not on read.** Units/vocabulary are canonical *before* domain objects are built;
  runtime compares canonical values directly.
- **Missing is not zero.** Scoring skips missing terms and renormalizes; absence is encoded explicitly, never
  silently defaulted to zero.
- **One runtime path.** Runtime starts from one compiled object and calls one entry function (`run(...)`).
  Inspection helpers (decode/encode/probe) are siblings, not alternate entry points.
- **Explanation is a contract.** Decisions, gates, skips, and tie-breaks are structured explanation data that
  callers *render*; callers never reconstruct the reasoning (or two callers explain the same result
  differently).
- **No hidden tie-break (ambiguous/abstain).** Stable ordering is for presentation, not a decision. If two
  outputs tie and one should win, a metric must say so; otherwise return an explicit ambiguous/abstain
  result, never a hidden default.
- **Versioned outputs.** Any output that crosses a boundary or is persisted carries a `spec_version` /
  `schema_version`.
- **Models propose; deterministic code decides.** *(If an LLM/ML model is in the loop.)* The model produces
  candidate facts with provenance; schemas, validation, tests, and human review decide what becomes truth —
  the model never constructs the canonical artifact at runtime and gets trusted directly.
- **Eval/gold set measures change.** A model- or scorer-touching change is measured against an evaluation set
  (the delta is the evidence; ties to Bar B2).
