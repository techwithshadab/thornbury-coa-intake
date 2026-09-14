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
| ~~F1~~ | ~~Declared boundaries enforced~~ | **CLOSED 2026-09-14.** `import-linter` in `make check` as `make boundaries`. Two contracts: a four-layer ordering, and a forbidden contract stopping `domain` from importing `raw`/`policy`/`parse`. **Watched to fail** — injecting `domain → raw` breaks both. |
| ~~F2~~ | ~~Exact runtime pin + EOL policy~~ | **CLOSED 2026-09-14.** Policy written into `pyproject.toml` beside the pin it governs: 3.11 EOL 2027-10, 3.12 EOL 2028-10, move the floor *before* EOL not after, next review 2027-04. |
| F3 | Owned command in **required** CI | **Half closed 2026-09-14.** The remote exists, CI runs `make check` and is green, and it now also gates that the committed submission reproduces. Still **not a required status check** — branch protection is unset, so a red run does not block a merge. |
| F4 | Dependency **license** gate | **Open — deliberately, as an accepted cost.** The CVE half is present and was *watched to work* (caught `pytest==8.3.4` / PYSEC-2026-1845 on its first run). The license half is not, and we are choosing not to add it: the runtime surface is **one** dependency, `pydantic` (MIT). A deny-list over a single permissive library adds a pinned tool and a gate that cannot fire, and a gate that never fires is weight without signal. **Revisit the moment a second runtime dependency is added** — that is the trigger, not a date. |
| ~~F5~~ | ~~Pins do not fossilize~~ | **CLOSED 2026-09-14.** `.github/dependabot.yml` — monthly for uv, github-actions and pre-commit. Notes that a `ruff` bump must move `pyproject.toml` and the pre-commit `rev:` in the same commit, or the two fight and `make check` can never pass. |
| F6 | Supply-chain hygiene | **Partly open — deliberately.** Actions are SHA-pinned with `contents: read`, and `uv.lock` is a hash-pinned, fully-resolved manifest that already answers what an SBOM is usually asked. Generating a CycloneDX artifact per build is not worth another pinned tool at one runtime dependency and no deployment. **Becomes worth doing at deployment stage 2**, when something is actually shipped and an SBOM has a consumer. |
| ~~F7~~ | ~~Hermetic, order-independent tests~~ | **CLOSED 2026-09-14.** `pytest-randomly` pinned; every run randomises order, so a test that only passes because another ran first fails loudly. 146 tests green. Network-disabled still unproven, but the suite makes no network calls. |
| ~~F8~~ | ~~Dead-code + dependency hygiene~~ | **CLOSED 2026-09-14.** `deptry` pinned and in `make check` as `make deps`. The six DEP002 ignores are tools the Makefile *executes* rather than imports, listed explicitly with reasoning; `pydantic` is correctly detected as used, so the check is live. |
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

> **Re-scored again 2026-09-14, twice.** Closed today: **F1** (import boundaries, watched to fail),
> **F2** (EOL policy), **F5** (dependabot), **F7** (randomised test order), **F8** (dependency
> hygiene). F10 closed 2026-08-30. **F3 half closed** — CI runs, is green, and now gates that the
> committed submission reproduces; branch protection is the remainder and it is not ours to set.
>
> **F4 and F6 are open by decision, not by omission**, with the trigger that would reopen each
> written in their rows. The rubric allows an explicitly accepted cost; these are two.
>
> **F9, F11 and F12 remain genuinely open.** F11 — no evaluation set — is still the one that matters:
> every number this repo states about its own behaviour is arithmetic over 36 documents, and no gate
> added today changes that.

## Conditions
1. F3 and F11 before any quality claim is made about this system.
2. ~~F1, F7, F8 before the decision rules land~~ — F7 and F8 closed; F1 (import-boundary check) open.
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
