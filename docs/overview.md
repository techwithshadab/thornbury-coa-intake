# Overview — Thornbury CoA Intake

> Read this first. `CLAUDE.md` is *how* we build; this is *what* we're building and where things live.
> Where a doc conflicts with the code, the code wins.

## What this is
Thornbury Ingredients takes in several hundred ingredient lots a week, each with a supplier Certificate
of Analysis. A two-person team reads each certificate and keys the values into the ERP. This repo reads
the certificate instead and returns one of two answers per document: **accept**, with the fields, or
**hold**, with a reason a person can act on.

The judgement is the product, not the typing. Denis Achebe put the asymmetry plainly: releasing a lot
that should have been held is a recall conversation with a customer; holding a lot that did not need it
is an annoyed supplier and a day of delay. Both are bad, and they are not the same kind of bad. A system
that holds everything has not solved this, and neither has one that accepts everything.

**Current maturity: the frame is built, the judgement is not.** Boundaries, reference data, the contract
and the checks are in place and green. `app.decide()` returns `hold` for every document with an explicit
"rules not implemented" reason. See `STATUS.md` for exactly what is missing.

## The shape
- **Repo kind / surfaces:** `rules-engine`, `criticality: regulated`. True: `has_consumers`,
  `decisioning_or_scoring`, `data_measurement`, `generated_code`, `stores_or_shows_time`.
  `handles_secrets`, `external_network`, `deployed` and `stateful` are false today and named in
  `REPO-SURFACE.yaml` with the change that flips each one.
- **One concern / entry point:** `coa-intake` → `cli.main` → `cli.run` → `app.decide`.
- **Where config/truth lives:** reviewed reference data in `reference/`, derived by
  `tools/derive_reference.py` from `reference/source/`. The one config boundary is `paths.py`.
- **Trust boundary:** `raw.py`. External input — certificate text and reference data alike — is validated
  by strict models before any domain logic branches on it.

## Boundary inventory
- **Inputs:** a directory of certificate documents (`--documents`); a directory of reference data
  (`--reference`). Both are runtime inputs. The pipeline is run against documents it has not seen, so
  neither path may be a constant.
- **Outputs:** `decisions.jsonl` — one line per document, `accept` or `hold`, carrying `schema_version`.
- **Contracts exposed:** the `decisions.jsonl` submission contract. Bump `domain.SCHEMA_VERSION` when it
  changes.
- **Contracts consumed:** SPEC-7 rev D §2 (acceptance limits and reportable methods); the ERP supplier
  master. Both vendored under `reference/source/` with provenance.
- **Files / persisted state:** none beyond the output file. The repo owns no database.
- **Env vars / secrets:** `COA_WORKSPACE_ROOT` (optional; the CLI flags override it). **No secret is used
  today.** When an LLM enters the extraction loop it brings an API key, sourced from a secrets manager or
  injected env — never committed, not even in a tracked `.env`.
- **Network calls:** none today. The same LLM step will add the first, and with it timeouts, retries, and
  a decision about whether certificate text may leave Thornbury's boundary — which is a client decision,
  not ours.

## Layout
```text
src/coa_intake/
  paths.py        the one config boundary — sole owner of env reads, fails loud
  raw.py          the trust boundary — strict models, extra="forbid"
  domain.py       compiled domain objects: Measurement, Certificate, Finding, Decision
  extraction.py   the extraction SEAM — a stub with a defined interface (OCR is out of scope)
  reference.py    loads and compiles the reviewed reference data
  app.py          the one runtime path: decide(certificate, spec) -> Decision
  cli.py          argument parsing and the write; renders Decision -> the submission contract
tools/
  derive_reference.py   generates reference/*.json from reference/source/
reference/
  source/         vendored controlled documents + PROVENANCE.md
  *.json          DERIVED — do not hand-edit; run `make reference`
tests/            the suite, incl. the invariant tests
docs/
  overview.md         this file
  open-questions.md   what is NOT ours to decide, by owner, + the assumptions we run on
  reference/          how each part works TODAY
decisions/        append-only ADRs
reviews/          gate records
REPO-SURFACE.yaml what this repo is (the router for the repo-fitness bar)
```

## Doc map
- **What we could not decide alone → [`docs/open-questions.md`](open-questions.md)** — 21 questions
  routed to their owner with the evidence behind each, 10 stated assumptions, and one we refuse to make
- Those questions drafted as sendable notes → [`docs/questions-to-send.md`](questions-to-send.md)
- Engineering contract & invariants → `CLAUDE.md`
- Repo standards & branch protection → `CONVENTIONS.md`
- How-it-works-today → `docs/reference/`
- Decisions we *did* make → `decisions/` · Current state → `STATUS.md`
