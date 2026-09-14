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

**Current maturity: the slice runs end to end on the supplied corpus.** A deterministic parser
(ADR-0007) reads the certificate; the SPEC-7 rules judge it; every ruling we made on Thornbury's behalf
lives as reviewed data in `reference/policy.json`, not as branches in code. Over the 36 supplied
documents: **21 accept, 15 hold**.

**That split is arithmetic, not a measurement.** There is no labelled set, so nothing here is an
accuracy claim — including the fact that the split matches the hand analysis in `docs/working-answers.md`
document for document, since both routes to that answer are ours. See `STATUS.md` for what is missing
and `docs/handover.md` for what a receiving team would be inheriting.

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
  neither path may be a constant — enforced by `tests/test_no_hardcoded_corpus.py`, which fails if any
  file under `src/` so much as names `engagement/`.
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
  raw.py          the trust boundary — strict models, extra="forbid" (incl. the policy file)
  domain.py       compiled domain objects: Measurement, DateReading, Certificate, Finding, Decision
  policy.py       the compiled provisional rulings from reference/policy.json
  extraction.py   the extraction SEAM — a stub with a defined interface (OCR is out of scope)
  parse.py        deterministic text -> Certificate. No match means ABSENT, never guessed
  reference.py    loads and compiles the reviewed reference data + the policy
  app.py          the one runtime path: decide(certificate, spec, policy, approved) -> Decision
  cli.py          arg parsing, the injected clock, the write; renders Decision -> the contract
tools/
  derive_reference.py   generates reference/*.json from reference/source/
reference/
  source/         vendored controlled documents + PROVENANCE.md
  *.json          spec-7 + supplier-master are DERIVED — run `make reference`, do not hand-edit
  policy.json     HAND-AUTHORED — the provisional rulings, each with a named owner
engagement/       THE SUPPLIED MATERIALS — brief, 36 certificates, SPEC-7, the validator.
                  Not our work; vendored so the repo is one thing to clone. See its README.
tests/            the suite, incl. the invariant tests
docs/
  overview.md         this file
  architecture.md     the runtime path and the data provenance, as diagrams
  open-questions.md   what is NOT ours to decide, by owner, + the assumptions we run on
  working-answers.md  the provisional ruling on each, and what it costs if wrong
  questions-to-send.md  those questions drafted as notes, one per stakeholder
  deployment.md       how this gets to production, in four stages
  handover.md         what a receiving team inherits, scored against the engine checklist
  working-log.md      how AI was used on this build, and what it got wrong
  reference/          how each part works TODAY
decisions/        append-only ADRs
reviews/          gate records
REPO-SURFACE.yaml what this repo is (the router for the repo-fitness bar)
```

## Doc map
- **What we could not decide alone → [`docs/open-questions.md`](open-questions.md)** — 21 questions
  routed to their owner with the evidence behind each, and 10 stated assumptions
- **What we are building on meanwhile → [`docs/working-answers.md`](working-answers.md)** — a
  provisional, reversible ruling per question, with the business consequence of each
- Those questions drafted as sendable notes → [`docs/questions-to-send.md`](questions-to-send.md)
- **How this reaches production → [`docs/deployment.md`](deployment.md)**
- **What a receiving team inherits → [`docs/handover.md`](handover.md)**
- How AI was used, and what it got wrong → [`docs/working-log.md`](working-log.md)
- **The mechanism, with diagrams → [`docs/architecture.md`](architecture.md)**
- Engineering contract & invariants → `CLAUDE.md`
- Repo standards & branch protection → `CONVENTIONS.md`
- How-it-works-today → `docs/reference/`
- Decisions we *did* make → `decisions/` · Current state → `STATUS.md`
