# Handover package

> For a team that has never spoken to us. Read this first, then `docs/overview.md`.
>
> Scored against the engine's `Handover_Readiness_Checklist.md` — the checklist's own rule is
> **evidence, not assertion**: an item is done when you can point at the artifact, not when someone
> remembers doing it. Every "done" below names the artifact. The gaps are listed as plainly as the
> completions, because a handover package that reports itself green is the one nobody trusts.

**Honest summary: this repo can be inherited and it now builds green somewhere that is not this
laptop. It has still never been reviewed by a second human.** That is the remaining handover risk,
and it is not fixed by writing more documentation.

---

## 1. The ninety-second version

Thornbury Ingredients receives ~400 supplier Certificates of Analysis a week. Two people read them
and key the values into the ERP. This repo reads the certificate instead and returns one of two
answers per document: **accept**, with the fields, or **hold**, with a reason and a queue.

The judgement is the product. A certificate can be wrong — a transposed lot number, a result outside
specification with PASS printed over it — and catching that is the part that matters. Releasing a lot
that should have been held is a recall conversation; holding one unnecessarily is a day of delay.

**On the 36 supplied documents: 21 accept, 15 hold.** That is arithmetic over a small sample, not a
measurement, and there is no labelled set to make it one.

---

## 2. What you are inheriting

| | |
|---|---|
| **Runs** | `make run DOCS=<dir> OUT=<file>` — a batch CLI. Nothing is deployed. |
| **Prerequisites** | `git`, `make`, `uv`. The interpreter is uv-managed and pinned, so the machine's own Python is not a variable. |
| **The gate** | `make check` — hygiene, size, placeholders, derived-data freshness, lint, 84 tests, CVE audit. Green with no skips. |
| **Proven** | A clean clone reproduces `submissions/decisions.jsonl` byte-for-byte. Output passes the engagement's `validate_submission.py`. |
| **Language** | Python 3.12.5, ~900 lines of source. No framework, no service, no database. |

### The five files that matter

1. **`reference/policy.json`** — every decision we made on Thornbury's behalf, as reviewed data with
   a named owner per rule. **Start here.** If something is deciding wrongly, it is far more likely to
   be a ruling you disagree with than a bug.
2. **`src/coa_intake/app.py`** — the rules. Walks the spec and the policy; writes no rule of its own.
3. **`src/coa_intake/parse.py`** — deterministic text → `Certificate`. No match means *absent*.
4. **`docs/working-answers.md`** — why each ruling is what it is, and what it costs if wrong.
5. **`docs/open-questions.md`** — the 21 things that are not ours to decide, by owner.

Then, when you need them: [`runbook.md`](runbook.md) to operate it, [`glossary.md`](glossary.md) for
the vocabulary (two of this engagement's hardest questions are vocabulary disputes), and
[`deployment.md`](deployment.md) for how it reaches production.

### Where the bodies are buried

- **The parser is deliberately brittle in one direction.** An unrecognised layout yields nothing and
  the lot holds. That is ADR-0007, not a defect. **Do not add a best-effort fallback** — it converts
  the safe failure into the dangerous one and undoes the basis of the whole design.
- **The safe way to widen coverage is `field_labels` in `reference/policy.json`.** Adding a label can
  only let the parser *read* something it previously held on; it cannot make it misread. That is why
  the vocabulary is data. `tests/test_robustness.py` holds 18 plausible layout variations and every
  one must keep passing — a hold there is lost automation, which the ledger charges for.
- **`reference/spec-7.json` and `supplier-master.json` are generated.** Hand-editing them is
  reverted by `make reference` and caught by `make freshness`. `policy.json` is the hand-authored one.
- **Freshness is not correctness.** `make freshness` compares generator output to generator output;
  a backwards derivation would pass it. Correctness lives in `tests/test_derivation.py`.
- **`make placeholders` only catches markers it has been taught**, and has missed unfilled template
  text twice. If you add a template, add its marker to the grep in the `Makefile`.
- **The staleness gate will eventually stop the pipeline on purpose.** From 2027-03-01 it warns; from
  2027-06-01 it refuses to run, because nobody owns telling this repo that SPEC-7 was revised. That is
  ruling R4 working, not a bug. Re-vendor `reference/source/`, run `make reference`, move the dates.

---

## 3. Scored against the checklist

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

## 4. The four things a receiving team should know are missing

Ranked by how much they should worry you.

**1. Nobody has reviewed this.** One author, no second pair of eyes, no PR ever raised. Every ADR is
self-signed; `reviews/2026-08-29-conformance.md` is explicitly marked self-assessed and unaccepted.
The engine's axiom is that the *receiver* accepts, and no receiver has. The remote and CI are now in
place, so the remaining fix is human: **make `check` required with CODEOWNERS review, and have someone
who did not build it read `policy.json` and the ADR-0006/0008 pair first.**

**2. There is no labelled set, so there is no accuracy number.** Everything this repo says about its
own behaviour is arithmetic over 36 documents. The 21/15 split matching the hand analysis exactly is
a consistency check between two routes that are *both ours* — it is not independent evidence.
**Fix: ~200 certificates with a QA analyst's accept/hold and reason. It blocks the B2 go-live gate
and it can start today, in parallel with everything else.**

**3. Twenty-one questions have no owner and no date.** Three of them block work outright: what goes
in `expiry_date` (Purchasing, never engaged), whether the ERP or QA tracker is authoritative
(unassigned; Marisol Vega never engaged), and whether three suppliers in the sample are genuinely
unapproved (IT). Notes are drafted in `docs/questions-to-send.md` and **have not been sent**.

**4. Half the supplied sample carries an anomaly.** 18 of 36, against the intake lead's estimate of
"a handful a month" out of ~1,600. Either the corpus was enriched for teaching, or the current manual
process misses a great deal. We cannot tell from inside the sample, and the answer changes the
business case in opposite directions. **Do not quote rates from this corpus as production estimates.**

---

## 5. Your first week

**Day 1 — make it yours.** Clone, `make setup`, `make check`, `make submission`. The corpus is
vendored at `engagement/`, so there is nothing to locate. If `make check` is not green on your
machine, that is a defect in this repo or its README and it is the most valuable bug you will find
this week — say so rather than working around it. `make submission` regenerates the three submitted
runs and asserts they are byte-identical to each other; `git diff submissions/` should be empty.

**Day 2 — read the rulings, not the code.** `docs/working-answers.md`, then `reference/policy.json`.
Twenty-one decisions were made on the client's behalf. You are inheriting all of them and you should
disagree with some. **ADR-0008 supersedes ADR-0006 and is worth reading as a pair** — it removes a
rule whose threshold had been calibrated on the single case it admitted. That is the shape of
disagreement this repo expects from you. Start there.

**Day 3 — push it to a remote and make `check` a required status check.** This closes checklist 2.5
and turns the existing workflow into an actual gate. Highest ratio of value to effort in the repo.
Exact commands in §8.

**Day 4 — send the notes.** `docs/questions-to-send.md`, in the stated order: Denis first, then Priya
(two of the remaining three notes need names only she can give), Marisol once Denis has introduced
you. Do not cold-email Marisol.

**Day 5 — start the labelled set.** Nothing else you do this week compounds as much.

---

## 6. Who to ask

| About | Person | State |
|---|---|---|
| SPEC-7, methods, what counts as a result | Marisol Vega, Quality Manager | **Never engaged.** Owns the most unresolved surface |
| Certificates, suppliers, what intake actually does | Denis Achebe, Intake Team Lead | Engaged, helpful, gave the best material we have |
| Scope, budget, the ERP lot record | Priya Raghunathan, Director of Supply Operations | Sponsor |
| `expiry_date`, reorder logic | Purchasing | **No named contact.** Ask Priya |
| ERP endpoint, supplier master, change process | IT | **No named contact.** Ask Priya |
| This repo | solutioner of record (`engine.yaml`) | Sole author of every line |

---

## 7. Publishing it

**Done, 2026-09-03** — `github.com/techwithshadab/thornbury-coa-intake`, private. Kept here because the
remaining step is not.

**What publishing immediately bought.** The workflow had never executed, and it **failed on its first
run**. `make check` had been invoking whatever `pre-commit` was on `PATH`; this machine has one via
Homebrew, a clean runner does not, so the hygiene gate reported that it had not run and failed. The
earlier "clean clone" verification had missed it because the clone was on the *same machine* — a clone
in another directory is not a clone elsewhere, which is precisely the trap the repo-fitness rubric
names and which we walked into while quoting it. `pre-commit` is now a pinned dev dependency. **CI was
the first genuinely independent environment this repo ever ran in, and it found a real defect in 12
seconds.**

**Private, not public.** `reference/source/` holds vendored copies of Thornbury's SPEC-7 and supplier
master. They are framed as controlled client documents, and a repo that reads as client QMS material
does not belong in a public namespace regardless of its provenance.

**Still outstanding — branch protection.** In **Settings → Branches → Add rule** for `main`:
- Require a pull request before merging
- Require status checks to pass → select **`check`**
- Require review from Code Owners (`CODEOWNERS` already routes `/decisions/`, `/reference/` and
  `CLAUDE.md`)

The last of those is what makes `CODEOWNERS` more than a text file, and it is what would have caught
the fact that one person has reviewed every line of this repo.

Until those are set, `check` runs but does not block a merge, and `CODEOWNERS` is a text file rather
than a gate. The second of them is what would catch the fact that one person has reviewed every line
here.

---

## 8. Sign-off

Handover is not complete until a receiver signs. Per the checklist's own rule, sign against the
artifact, not against this table.

| Role | Name | Decision | Date |
|---|---|---|---|
| Workstream Tech Lead | TBD | pending | |
| Delivery Lead | TBD | pending | |

**This package is producer-written and unaccepted.** Nothing in it should be read as an attestation.
