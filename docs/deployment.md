# Deployment plan

> How this reaches production. Four stages, each one shippable and each one proving something the
> next depends on. Where a step is unknown, it says so and says how it becomes known — an unknown
> named is a task; an unknown hidden is a slip.

**The plan is written so the two things that can block us — Thornbury IT's change process (Q16) and
the data-boundary decision (Q19) — are not on the critical path until stage 3.** That is deliberate.
Both have no owner today, and a plan whose first step depends on an unowned decision is a plan that
starts by waiting.

---

## Where we are

Stage 1 is built. `make check` is green with no skips, a clean clone reproduces
`submissions/decisions.jsonl` byte-for-byte, and the output passes the engagement's
`validate_submission.py`. Nothing is deployed anywhere and `REPO-SURFACE.yaml` declares `deployed`
and `stateful` false, honestly.

---

## Stage 1 — Batch, run by hand, output reviewed by a person

**What it is.** An operator runs `make run DOCS=<dir> OUT=<file>` on a workstation. The output is a
file. A person reads it, keys or uploads the accepts, and works the four hold queues.

**Why start here.** It delivers the actual ask — the typing — without touching the ERP, without an
API key, without a network call, and without needing an answer from IT or from whoever owns the
data-boundary question. It is also the only stage that can be built and proven entirely by us.

**Prerequisites:** `git`, `make`, `uv`. Nothing else — the interpreter is a pinned, uv-managed
input, so the machine's own Python is not a variable.

**Steps.**
```bash
git clone <repo> && cd thornbury-coa-intake
.githooks/install-rails.sh          # git never transmits hook config
make setup                          # frozen install from uv.lock
make check                          # must be green before anything else
make run DOCS=/path/to/certificates OUT=decisions.jsonl
```

**How you know it worked.** `make check` green; the run reports 36-of-36 (or N-of-N) decisions; the
counts by route are plausible against the batch. A run that reports fewer lines than documents is a
defect, not a partial success — every document gets a line by contract.

**Rollback.** Nothing to roll back. The output is a file that a person reads before it reaches any
system. This is the property that makes stage 1 safe to start immediately.

**Who runs it.** One named person on the intake team, with the solutioner reachable. **Not a rota
yet** — a second trained operator is the exit criterion for stage 2, not this stage.

**Exit criteria.** Two consecutive weeks where (a) every batch completes, (b) the intake team's
own reading of the accepts agrees with the system's on a sampled 20, and (c) the four hold routes go
to the right desks without renegotiation. That third one is an organisational test, not a technical
one, and it is the one most likely to fail.

---

## Stage 2 — Scheduled batch, on Thornbury infrastructure

**What changes.** The same command, on a schedule, on a machine Thornbury owns. Output lands in a
shared location. Still no ERP call; still a person releasing every lot (ADR-0004).

**Why this before the API.** It converts "it works on the solutioner's laptop" into "it works when
he's on leave" — which is the actual handover risk — and it produces the first operational data
about hold rates and queue volumes. Those numbers are needed to size stage 3 and are currently
guesses.

**This is where `deployed` becomes true in `REPO-SURFACE.yaml`**, and with it the deployed pack's
obligations: graceful failure, bounded waits, health signal, structured logs carrying the commit and
the policy version. None of that exists today and none of it is needed before this stage.

**What to build.**
- A scheduled job (cron, Airflow, whatever Thornbury already runs — **do not introduce a new
  scheduler for this**).
- Run-level telemetry: counts by action and route, parse-failure count, wall time, policy version,
  spec revision. Five numbers, emitted per run. This is the smallest thing that makes the system
  observable and it is the input to every later sizing decision.
- Alerting on one condition only, to begin with: the run did not complete.

**Prerequisites we do not have.** Where does the job run, who owns that host, and what does
Thornbury use for scheduling? **Unknown — becomes known by asking IT alongside Q16.**

**Rollback.** Disable the schedule; fall back to stage 1's manual run. Keep stage 1 working for
exactly this reason — do not delete the manual path when the scheduled one lands.

**Exit criteria.** Four weeks of unattended runs; two operators who have each run a recovery; hold
rates stable enough to quote a range to Priya.

---

## Stage 3 — Write to the ERP

**What changes.** Accepted lots are created through IT's existing lot-creation REST endpoint, at
status `held`. **The system still never releases** (ADR-0004) — a person performs the release action
exactly as today.

**This is the first stage that can do damage**, because it writes into the system the business acts
on. Everything before it produces a file someone reads.

**Blocked on, and these are hard blockers:**
- **Q16 — IT's change process for a new consumer of that endpoint.** Completely unknown: review,
  environments, credentials, lead time. **Becomes known by asking IT.** Until answered, treat the
  stage-3 estimate as unbounded, not as "a few weeks".
- **Q14 — what goes in `expiry_date`.** The ERP will not save a lot without it, and the field's
  meaning is Purchasing's to settle. **Becomes known by asking Purchasing.** Without it, stage 3
  cannot write a single lot.
- **C2 — what `entered_by` should hold** for an automated record. A service account removes the
  human from the audit trail; that needs a decision, not a default.

**What to build.** A thin ERP client behind one interface, with the `expiry_date` mapping read from
`policy.json` rather than written into code, an idempotency key per lot so a re-run cannot double-
create, and a dry-run mode that logs the payload it *would* send. Ship the dry-run first and let
Thornbury diff it against what their team would have keyed. That diff is the cheapest quality
evidence available before an eval set exists.

**Prerequisite that is ours, not theirs:** `handles_secrets` becomes true here (endpoint credentials).
Sourced from a secrets manager, never committed, rotation path documented in `SECURITY.md`.

**Rollback.** The ERP is the system of record, so rollback is not `git revert` — it is a data
question. Before this stage ships, agree with IT how a wrongly-created lot is voided, and test it.
**Do not ship stage 3 without having performed that test once.**

**Exit criteria.** Dry-run diff agreed by Denis; the void procedure exercised; idempotency proven by
deliberately re-running a batch.

---

## Stage 4 — Better extraction, measured

**What changes.** The hold rate falls because the parser reads more layouts — either through more
labelled patterns, or by adding an LLM that *proposes* fields which the deterministic rules still
check (ADR-0007 defers this rather than rejecting it).

**Blocked on:**
- **A labelled evaluation set.** Without it this stage cannot be shown to have helped, only asserted
  to. **This is the single highest-value missing artifact in the engagement** and it does not depend
  on anything else — it can be started today, in parallel with stage 1.
- **Q19 — may certificate content leave Thornbury's network?** Only if the answer is "yes" is a
  hosted model even a candidate. **Becomes known by asking Priya's security contact.** If the answer
  is no, the stage is more patterns, not a model, and that is a perfectly good outcome.

**The order matters and is easy to get wrong.** The eval set comes *before* the extractor change, not
after. Building a better extractor and then measuring it is how you end up unable to say whether it
helped.

---

## What could go wrong, in the order it is likely to

| Risk | Stage | What it looks like | What we do about it |
|---|---|---|---|
| **Hold volume overwhelms the queues** | 1 | 39% of a real week is more escalations than QA has ever handled at once | ADR-0005's four routes exist for this; most holds go back to intake, which handles 100% today. Watch the `quality` route specifically |
| **The sample was not representative** | 1 | Real hold rates far below (or above) 39% | Expected — assumption A7 says so. Stage 2's telemetry replaces the guess with a number |
| **IT's change process is months** | 3 | Stage 3 slips indefinitely | Why stages 1–2 deliver value without it. Ask now (Q16) so the estimate exists before it is needed |
| **A SPEC-7 revision lands unnoticed** | any | Lots judged against withdrawn limits | The staleness gate warns from 2027-03-01 and refuses from 2027-06-01. It is a compensating control, not a fix — the fix needs Quality to own a notification (Q4) |
| **A new supplier layout appears** | any | That supplier's lots all hold | Correct behaviour by design (ADR-0007), visible in stage 2 telemetry as a parse-failure spike. Fix is a pattern plus a test |
| **The one person who knows it leaves** | 1–2 | Nobody can run or change it | The real risk. See [`handover.md`](handover.md); a second operator is stage 2's exit criterion |

---

## What this plan does not cover

- **Anything that requires releasing a lot automatically.** Not in scope at any stage (ADR-0004).
- **OCR / PDF intake.** Out of scope for this build (ADR-0003); the seam is ready for it.
- **A review UI.** Holds reach people as file rows. If the queues prove workable that way, a UI may
  never be worth building — decide with stage 2's data, not now.
- **Anything for the other document types** Priya mentioned (packing lists, allergen declarations).
  The `Extractor` seam and the policy-as-data shape were chosen partly with that in mind, but nothing
  here has been designed against a second document type and it should not be claimed that it has.
