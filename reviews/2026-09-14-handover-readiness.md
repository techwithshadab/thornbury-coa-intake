---
record_type: gate-record
gate: handover-readiness
instance_overlay: none
project: Thornbury CoA Intake
date: 2026-09-14
outcome: conditional   # pass | conditional | fail
artifacts_reviewed: [docs/handover.md, README.md, docs/architecture.md, docs/deployment.md, docs/runbook.md, CODEOWNERS, .github/workflows/check.yml]
reviewers: []
followups: [branch-protection, second-reviewer, evaluation-set]
---

# Gate record — handover readiness — Thornbury CoA Intake

**What was reviewed:** the repository against the engine's `Handover_Readiness_Checklist.md`.
**Outcome:** **conditional.** Most items pass with a named artifact. Two do not, and both need a
person rather than a commit.

**This is an internal delivery instrument, not a client document.** It lives here rather than in
`docs/handover.md` because Thornbury has no stake in how MathCo scores its own handover discipline —
they have a stake in whether the thing works and what is unfinished, which is what the client-facing
handover says. Moving it here also stops a client document from opening with our own checklist.

**Self-assessed by the producer. Not accepted.** The checklist's own rule is *evidence, not
assertion* — an item is done when you can point at the artifact. Every "Complete" below names one.
Under the engine's receiver-accepts axiom this record is not closed until someone who did not build
the repository signs the table at the end.

## Scored against the checklist

### 1. Documentation completeness

| # | Item | Status | Evidence / gap |
|---|---|---|---|
| 1.1 | Charter and success criteria current | **Complete** | `docs/overview.md`; the engagement brief |
| 1.2 | Current-state architecture documented | **Complete** | `docs/architecture.md` — the runtime path and the derived-vs-hand-authored data provenance, both as Mermaid (GitHub renders natively), plus the boundary table. `docs/overview.md` carries the shape |
| 1.3 | Non-obvious decisions captured | **Complete** | ADR-0001…0007, each with context, consequences and options |
| 1.4 | Alternatives not chosen, with reasoning | **Complete** | Every ADR carries an "Options considered" section naming what was rejected and why |
| 1.5 | Confluence pages exist | **N/A / not started** | No Confluence space for this engagement |
| 1.6 | Handover context digest | **Complete** | This document |

### 2. Repository inventory and hygiene

| # | Item | Status | Evidence / gap |
|---|---|---|---|
| 2.1 | Master repo index | **N/A** | Single repo |
| 2.2 | Named per convention | **Complete** | `thornbury-coa-intake` (client-product-component) |
| 2.3 / 2.4 | Empty / superseded repos | **N/A** | First repo of the engagement |
| 2.5 | **No code only on a laptop** | **Complete** (2026-09-03) | Pushed to `github.com/techwithshadab/thornbury-coa-intake` (private). Was the worst finding in this package; it is closed |
| 2.6 | Branches merged or planned | **Complete** | Single `main`; no open branches |

### 3. README and technical documentation

| # | Item | Status | Evidence / gap |
|---|---|---|---|
| 3.1 | README passes the template check | **Complete** | `make placeholders STRICT=1` clean — after the gate was widened twice to catch markers it had been missing |
| 3.2 | **Setup tested by someone other than the author** | **Half done** | The *environment* half is now proven: CI runs `make setup && make check` on a clean Ubuntu runner carrying none of this machine's tools, and it is green. That is what caught the `pre-commit` defect below. The *human* half is still open — no person other than the author has followed the README |
| 3.3 | Deployment notes | **Complete** | `docs/deployment.md` — four stages, blockers named |
| 3.4 | Runbook | **Complete for what exists** | `docs/runbook.md` — run it, check it, the failure table, and when to stop and ask. No monitoring section, because nothing is deployed to monitor |
| 3.5 | "What's NOT in this repo" filled | **Complete** | `README.md` — and shorter since `engagement/` was vendored |

### 4. Size and history

| # | Item | Status | Evidence |
|---|---|---|---|
| 4.1 | No venvs / artifacts / caches committed | **Complete** | `make size`; `git ls-files` clean |
| 4.2 | No large data files | **Complete** | `make size` (5 MB cap) green |
| 4.3 | History scrubbed where needed | **N/A** | No bloat was ever committed |
| 4.4 | Complete `.gitignore` | **Complete** | From the standard template, customised — and corrected once, when it was found to be ignoring a deliverable |

### 5–8. Access, security, quality, ownership

| Item | Status | Evidence / gap |
|---|---|---|
| Secrets not in code | **Complete** | `gitleaks` + `detect-private-key` on every commit; no credential is used at runtime today |
| Dependency vulnerabilities | **Complete** | `make audit` in `make check`; caught a real CVE (`pytest` PYSEC-2026-1845) on first run |
| Access inventory | **Complete** | `docs/access-inventory.md` — nothing is needed today, and every later need is blocked on a question nobody has been asked |
| SECURITY.md reporting path | **Complete** | `SECURITY.md` |
| Tests | **Complete** | 84, incl. invariant, negative, mutation, policy-consistency and layout-robustness tests. `make check` green with no skips |
| CI | **Running, not yet required** | `.github/workflows/check.yml` runs the same `make check` and is **green** (run 33808585169). It is not yet a *required* status check — branch protection is the remaining step (§7). A job that does not block merge is a notification |
| **Quality attestation (accuracy)** | **NOT STARTED** | No labelled set. No number. See below |
| **≥2 owners per area** | **FAILING** | `CODEOWNERS` names roles, but one human has touched every line and no second person has reviewed any of it |

---


## The two that need a person

**Setup tested by someone other than the author (3.2).** The environment half is proven — CI runs
`make setup && make check` on a clean runner carrying none of the build machine's tools, and it is
green. That is what caught the `pre-commit` defect. The human half is untouched: nobody else has
followed the README.

**Plural ownership.** `CODEOWNERS` names roles, but one person has written every line and no pull
request has ever been raised. Branch protection with required CODEOWNERS review is the mechanism;
it is unset.

## Follow-ups
| Item | Owner (role) | Due | Status |
|---|---|---|---|
| Branch protection: require `check` + CODEOWNERS review | tech-lead | — | open |
| A reviewer who did not build it reads `policy.json` and ADR-0006/0008 | tech-lead | — | open |
| Labelled evaluation set (blocks any quality claim, gate B2) | solutioner-of-record | — | open |

## Sign-offs
| Role | Name / seat | Decision | Date |
|---|---|---|---|
| Workstream Tech Lead | TBD | pending | |
| Delivery Lead | TBD | pending | |
