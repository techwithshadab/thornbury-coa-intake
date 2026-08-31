---
record_type: gate-record
gate: conformance
instance_overlay: none
project: Thornbury CoA Intake
date: 2026-08-29
outcome: conditional   # pass | conditional | fail
artifacts_reviewed: [REPO-SURFACE.yaml, CLAUDE.md, docs/overview.md, Makefile, pyproject.toml, uv.lock, .github/workflows/check.yml, src/, tests/, tools/, reference/]
reviewers: []
followups: [import-boundary-check, EOL-policy-note, license-deny-list, SBOM, dependency-update-bot, random-order-tests, dead-code-and-dep-hygiene, runnable-docs-test, committed-contract-artifact, CI-required-check, eval-set]
---

# Gate record — conformance — Thornbury CoA Intake

**What was reviewed:** the repo as stood up, against the `repo-fitness` bar.
**Against which bar:** `references/RUBRIC.md` — the universal core, plus the conditional packs for the
surfaces declared in `REPO-SURFACE.yaml`.
**Outcome:** **conditional** — the shape is sound and every gate that exists is green and demonstrated,
but eleven core/pack lines are partial. Partial credit is a finding, not a pass.

**Self-assessed by the producer. Not accepted.** Under the engine's *receiver accepts* axiom this record
is not closed until a reviewer who did not build it signs the sign-off table below. Nothing here should
be read as an attestation.

## Bar A — universal core

### Passing (demonstrable, not aspirational)
| Line | Evidence |
|---|---|
| One canonical path, no quiet fallbacks | `cli.main → cli.run → app.decide`; "Active compatibility paths: **none at present**" ledger in `CLAUDE.md` |
| A trust boundary | `raw.py`, `extra="forbid"`; `test_unknown_fields_are_an_error_not_a_silent_drop` |
| Config through one typed boundary | `paths.py` sole env reader; `tests/test_path_ownership.py`; `test_missing_config_fails_closed` |
| Boundary-contract inventory | `docs/overview.md` "Boundary inventory"; mirrored in `REPO-SURFACE.yaml` notes |
| Hash-pinned lockfile, installed frozen | `uv.lock` (398 hashes), `uv sync --frozen`; `make setup` uses it |
| Gate tools pinned exactly, and once | `ruff==0.16.1` in `pyproject.toml` **equals** `rev: v0.16.1` in `.pre-commit-config.yaml` |
| No tracked secrets/artifacts; large-file policy | `gitleaks` + `detect-private-key` per commit; `make size`; `.gitattributes` |
| Determinism | documents sorted by `doc_id`; no clock/entropy/network in `decide()`; `test_decide_is_deterministic`; clean clone reproduced the 36-line output byte-for-byte |
| Written invariants enforced by tests | `CLAUDE.md` Invariants, each citing the test that fails on violation |
| Fail loud, never silent | `test_an_accept_without_a_certificate_fails_loud`, `test_an_empty_documents_directory_fails_loud` |
| Failure-path coverage | 32 tests, majority negative/boundary |
| Clone-to-green bootstrap | proven in a clean clone elsewhere, not in the working tree |
| Everything needed is TRACKED, proven elsewhere | same clone reproduced the run; `reference/` is not caught by the scaffold's `/data/*` ignore |
| No template text in canonical files | `make placeholders STRICT=1` |
| Security reporting path | `SECURITY.md` |
| Plural ownership | `CODEOWNERS` ≥2 roles per area |
| Dead-simple default, ledgered complexity | `CLAUDE.md` "complexity we accept" / "negative lessons", each naming its guarantee |
| Complexity ceiling | `ruff` `C901`, `max-complexity = 10` |

### Findings (partial — open)
| # | Line | What is missing |
|---|---|---|
| F1 | Declared boundaries **enforced** | The layer directions are written in `docs/overview.md`; only the config boundary is machine-enforced (by grep, in `test_path_ownership`). No import-linter/cycle check holds `cli → app → domain ← raw`. |
| F2 | Exact runtime pin **+ EOL policy** | The pin is exact and now genuinely reproducible (`.python-version` 3.12.5 + `python-preference = "only-managed"`). The EOL note mapping the supported range to upstream dates is not written. |
| F3 | Owned command in **required** CI | `.github/workflows/check.yml` runs `make check` on every PR, but there is no remote and no branch protection, so "required" is unproven. A CI job that does not block merge is a notification. |
| F4 | Dependency **license** gate | The CVE half is present and was *watched to work*: it caught `pytest==8.3.4` / PYSEC-2026-1845 on the first run and the pin was bumped. There is no license deny-list. |
| F5 | Pins do not fossilize | No dependency-update bot configured. |
| F6 | Supply-chain hygiene | Actions are SHA-pinned with `contents: read`; no SBOM is generated or retained. |
| F7 | Hermetic, **order-independent** tests | The suite makes no network calls, but has not been run network-disabled or in randomized order (no `pytest-randomly`). Order-independence is asserted, not demonstrated. |
| F8 | Dead-code + dependency hygiene | No dead-code finder and no `deptry`-equivalent in the ritual. |
| F9 | Runnable docs | README commands are not executed by a test, so a stale example would not break the build. |

## Conditional packs

**`decisioning_or_scoring`** — externalized policy ✅ · one runtime path ✅ · missing-is-not-zero ✅
(`test_an_unreported_attribute_is_absent_not_zero`) · provenance ✅ · explanation-as-contract ✅ ·
abstain semantics ✅ (ADR-0001) · versioned outputs ✅.
**F10 — RESOLVED 2026-08-30.** The certificate compile step now exists (`parse.py`, ADR-0007):
validated raw → `Certificate` → `decide()`. Externalized policy strengthened too — every ruling moved
into `reference/policy.json` with a named owner, so a domain fact changes without a code change. **F11 — no eval/gold set.** `CLAUDE.md` names it as an invariant that does not yet hold;
every quality claim about this system is currently unfalsifiable. This is the most important open item
and it blocks Bar B2.

**`data_measurement`** — `{attribute, value, unit, source, method}` on `Measurement`, enforced by type
(`test_a_measurement_cannot_be_a_bare_number`) ✅ · schema-on-read ✅. Canonicalize-on-write is stated in
`CLAUDE.md` and structurally supported, but **unexercised** — no unit conversion runs yet, so SPEC-7 §2's
"convert before comparison, and record the conversion" is a declared law with no code behind it.

**`generated_code`** — the strongest area, and the one most repos get wrong. Derived-not-hand-kept ✅
(ADR-0002) · freshness gated ✅ · **generator verified independently of itself** ✅ (negative cases;
`test_committed_reference_matches_the_source_by_a_second_route` reads the source by a different route
than the generator) · **gate watched to fail** ✅ (`test_the_freshness_gate_has_been_watched_to_fail`
corrupts the artifact and asserts red). Not awarded on `--check` alone.
*Residual risk that no gate in this repo can close:* `reference/source/` is a **copy** of a controlled
document and nobody owns telling this repo that SPEC-7 was revised.

**`stores_or_shows_time`** — declared in `CLAUDE.md` (ISO 8601 on write; `retest_date` is not
`expiry_date`). **Unexercised**: no date parsing exists yet, so there is no DST/locale test. Fires
properly once the compile step lands.

**`has_consumers`** — the contract holds (one line per document, `accept`/`hold` only,
`schema_version` on every line, `test_every_document_produces_exactly_one_line`) and the output passes
the engagement's own `validate_submission.py`. **F12 — no committed contract artifact** (a JSON schema)
and no CI check failing a breaking change without a version bump.

> **Re-scored 2026-08-30 after the rules landed.** F10 resolved. Four core lines newly pass that did
> not before: the SPEC-7 §4 withdrawn-revision rule closed a dead field, the staleness gate reads its
> policy dates through an injected clock, `make check` is green with **no skips** (the prettier hook —
> the only gate needing node — was removed with reasoning recorded), and the placeholder gate was
> widened twice after it was found passing over unfilled template text. Test count 32 → 62.
> **F1–F9, F11, F12 remain open and unchanged.**

## Conditions
1. F3 and F11 before any quality claim is made about this system.
2. F1, F7, F8 before the decision rules land — they are cheap now and get expensive later.
3. This record is **not accepted** until signed by a reviewer who did not build the repo.

## Follow-ups
| Item | Owner (role / name) | Due | Status |
|---|---|---|---|
| F11 labelled evaluation set | solutioner-of-record | 2026-09-05 | open |
| F3 push to a remote, make `check` a required status check | tech-lead | 2026-09-05 | open |
| F1 import-boundary check | solutioner-of-record | 2026-09-12 | open |
| F7 randomized-order + network-off run | solutioner-of-record | 2026-09-12 | open |
| F8 dead-code + unused-dependency check | solutioner-of-record | 2026-09-12 | open |
| F2, F4, F5, F6, F9, F12 | tech-lead | 2026-09-19 | open |
| SPEC-7 revision notification path (no gate in this repo can close it) | Quality — Marisol Vega, not yet engaged | — | open |

## Sign-offs
| Role | Name / seat | Decision | Date |
|---|---|---|---|
| tech-lead | TBD | pending | |
| delivery-lead | TBD | pending | |
