# Working answers — the provisional rulings we are building on

> **INTERNAL working document.** Our reasoning about decisions that are Thornbury's to make, written
> in our own voice including where we think we might be wrong. The client-facing version of this is
> §3 of [`handover.md`](handover.md), which states the rulings and their owners without the
> deliberation. Both should exist; only one is addressed to them.

> Companion to [`open-questions.md`](open-questions.md). That file says what we cannot decide alone.
> This one says **what we are doing in the meantime, why, and what it costs if we are wrong.**
>
> Every ruling here is **provisional and reversible**. None is a recommendation to Thornbury; each is a
> default we run on until the owner answers. Where a ruling would bind Thornbury to something we cannot
> undo, we did not make one — those are listed at the end.

## Why this is not a reversal

`open-questions.md` says these decisions are not ours to make. That still holds. What changed is that
waiting is also a decision, and a worse one: five stakeholders, two of them without names, one not yet
introduced, and a build that cannot start until they reply.

The distinction that matters is not *whether* we proceed — it is whether the choice is **visible,
justified and cheap to reverse**. A silent default buried in an `if` branch is the failure the capstone
warns about. A written ruling with a named owner, a stated cost of being wrong, and a one-line reversal
path is ordinary professional practice. Everything below is the second kind.

**Nothing here has been communicated to Thornbury as a decision.** The notes in
[`questions-to-send.md`](questions-to-send.md) tell each owner what we are assuming, so silence has a
visible cost and correcting us is easy.

---

## The business outcome these rulings produce

On the 36 documents as given, applying every ruling below:

| | Count | Share | Where it goes |
|---|---:|---:|---|
| **Auto-accept** — fields extracted, lot created, no keying | **21** | **58%** | ERP, at status `held` (ADR-0004) |
| Hold → **Quality** (SPEC-7 rule breach) | 5 | 14% | COA-0004, 0009, 0026, 0029, 0033 |
| Hold → **procurement** (supplier not on master) | 3 | 8% | COA-0003, 0017, 0030 |
| Hold → **intake, manual key** (unreadable/incomplete) | 5 | 14% | COA-0010, 0019, 0028, 0035, 0036 |
| Hold → **supplier query** (document contradicts itself) | 2 | 6% | COA-0018, 0023 |

**What that means at 400 certificates a week**, if this sample resembles a normal week — and see the
caveat below, because it probably does not:

- **Keying falls from ~400/week to ~56/week — an 86% reduction.** That is Priya's ask, delivered.
- **~56 lots/week newly referred to Quality that are not referred today.** Denis's floor estimate is a
  handful a month. That is roughly a 20× increase in QA referrals — not because the system is
  over-cautious, but because it applies SPEC-7 consistently and people applying it by eye do not.
- **~33 lots/week from suppliers not on the approved master**, which the ERP would refuse anyway.

**The load-bearing caveat.** Half this sample carries an anomaly. That is almost certainly enriched — a
teaching set, not a random week. If the true anomaly rate is a third of what we see, auto-accept lands
nearer **85–90%** and QA referrals nearer 15/week. **Do not quote the 58% as a production estimate.** It
is a floor derived from a pessimistic sample, and it is stated that way in every note we send.

**The finding underneath the numbers.** The hold rate is not a measure of this system's weakness. It is
a measure of how much inbound paperwork already fails Thornbury's own written specification. Whatever
the true rate, the gap between "a handful a month" and what a consistent reading of SPEC-7 produces is
the most commercially significant thing this project has surfaced, and it is a supplier-quality finding,
not a data-entry one.

---

## The rulings

Each is: **the ruling · why (business) · confidence · cost if wrong · who overturns it.**

### The four that shape everything else

**R12 → Q12. The system never releases a lot. It creates it at the ERP's default `held`.**
The ERP already defaults `status` to `held`, and releasing is a separate action. So the system does not
need the power to release, and we are not taking it. It fills the fields; a person still releases.
· **Why:** this is what dissolves the Priya/Denis conflict. Priya gets the typing gone; Denis keeps the
judgement gate exactly where it is today. It also means the worst failure this system can produce is a
*wrong field on a held lot*, not a released lot — which changes the risk profile of the whole engagement.
· **Confidence: high.** · **Cost if wrong:** if Thornbury wanted auto-release, we have under-delivered
and can add it deliberately later. That is the cheap direction to be wrong in.
· **Overturned by:** Priya, and it should be a separate conversation with its own record. → **ADR-0004**

**R10 → Q10. Success is two numbers, not one.**
Safety: **zero** wrong accepts against the labelled set — non-negotiable, it is the recall. Throughput:
maximise auto-accept subject to that. · **Why:** "fill in the fields" and "stop bad releases" only
conflict if you optimise one. Stated as a constraint plus an objective they compose, and both sponsors
can sign the same sentence. · **Confidence: high** on the framing, **unmeasurable** on the numbers until
a labelled set exists. · **Overturned by:** Priya and Denis together.

**R18 → Q18. ERP vs QA is a scope question, not a precedence question.**
SPEC-7 is authoritative on **whether a lot is acceptable**. The ERP is authoritative on **the lot
record**. The QA tracker is authoritative on **what a person decided and why**. · **Why:** the argument
has run for years because it is framed as "which system wins," and framed that way it has no answer.
None of the three is trying to do the other's job. · **Confidence: medium.** This is a proposal to put
in front of the three of them, not a ruling we can impose — but it is a better starting point than the
question. · **Cost if wrong:** low; it is a framing, and the reconciliation work is unchanged.

**R21 → Q21. Assume the sample is NOT representative.**
Assume it is enriched for difficulty. Quote rates as "in the sample provided," never as production
estimates. Plan review capacity for a range, not a point. · **Why:** the embarrassing failure here is
telling Priya to staff for 56 QA referrals a week and being wrong by 3×. · **Confidence: high** that it
is enriched, **zero** on by how much. · **Overturned by:** Denis saying how the 36 were chosen.

### The SPEC-7 readings — high confidence, low judgement

**R2 → Q2. Moisture by Loss on Drying (M-03) → hold, route to Quality.**
SPEC-7 §3.2: M-03 "shall not be used to release a lot." §4: refer to Quality. · **Why:** this is the
"number was fine but the method was wrong" case Denis lost a lot to last year. · **Confidence: high** —
reading a controlled document, not inventing policy. · 3 documents (8%).

**R3 → Q3. Result outside limits with a PASS statement → hold, route to Quality, name the breach.**
SPEC-7 §5: the certificate is in error regardless of stated conformance. The hold reason quotes the
value, the limit and the supplier's claim, because the supplier needs correcting too. · **Confidence:
high.** · 2 documents (5.5%) — and these are the highest-value catches in the system.

**R9a → Q9 (units). Convert to SPEC-7 units before comparison; record the conversion.**
COA-0027 (7276 ppb) and COA-0031 (7403 ppb) become 7.276 and 7.403 ppm — both comfortably within the
10 ppm limit. · **Why:** SPEC-7 §2 requires exactly this. Comparing 7276 against 10 would reject two
clean lots. · **Confidence: high** — spec-mandated, not a judgement. · Recovers 2 documents.

**R8 → Q8. A document that disagrees with itself about the lot number → hold. Never pick a side.**
Both values go in the hold reason so the reviewer does not re-read the document. · **Why:** guessing
which lot number is right is guessing which physical material is in the warehouse. · **Confidence:
high.** · 2 documents.

**R15 → Q15. Supplier not on the approved master → hold, route to procurement, not Quality.**
· **Why:** the ERP will refuse the lot anyway, so the hold costs nothing incremental. Routing to
procurement rather than QA is deliberate: this is a sourcing question, not a quality one. · **Confidence:
high** on the hold, **low** on whether the master is even current. · 3 documents (8%) — and if that rate
is real, it is an escalation in its own right, independent of this project.

### The contestable ones

**R7 → Q7. A date resolves only from the document in front of us. Otherwise the lot holds.**

1. **Unambiguous by construction** — ISO 8601, a written month, or a slash date with a component >12.
2. **The document states its own convention** in prose (COA-0034: "All dates are written
   day/month/year"). Reading a document's own instructions is not inference.
3. **Otherwise → hold**, routed to `intake_keying`.

· **Why:** an earlier version added a rung that resolved an ambiguous date from ≥3 agreeing
certificates by the same supplier, which recovered COA-0035. **Removed (ADR-0008 supersedes
ADR-0006)** on consistency grounds rather than on the threshold: the ladder already refuses to infer
Zeeland Bulk BV's convention because "BV is a Dutch company form" is a claim about a jurisdiction
standing in for a fact about a document. Reading Halewood's convention off their *other paperwork* is
the same kind of move with marginally better evidence, and the only thing separating the two was a
number we chose — one that had been calibrated on the single case it admitted.
· **Confidence: high now, where it was the weakest ruling before.** The rule states in one sentence
and survives challenge.
· **Cost:** COA-0035 holds. Accept/hold moved 22/14 → 21/15 — about 3% of the corpus, paid for a rule
we can defend. And a real signal is being ignored: Halewood almost certainly does write day/month.
· **Overturned by:** Denis (Q7). If he sanctions supplier-convention inference, rung 3 returns — with
a threshold derived from data rather than from the case it admits. → **ADR-0008**

**R6 → Q6. Provisional exchange rate: one wrong release ≈ 50 unnecessary holds. It does not currently
bind.**
· **Why the number:** a recall conversation in food ingredients carries recall cost, customer damage and
regulatory exposure — conservatively five figures plus the relationship. An unnecessary hold costs a
day and an email. 50:1 is a deliberately round, deliberately conservative number in the right order of
magnitude.
· **Why it does not bind — and why the refusal in `open-questions.md` still stands:** every hold this
system currently issues is **rule-mandated**, not confidence-mandated. SPEC-7 draws the line, not us.
The exchange rate only becomes live when extraction confidence enters the loop and the system starts
choosing between "probably fine" and "check it." We have not built that, so we have not made the call we
said we would not make. When we do, it is Denis's and Priya's number, not ours.
· **Confidence: low on the figure, high on it being inert today.**

**R14 → Q14. Write the retest date into `expiry_date` — because that is what happens today. Do not
compute a missing one.**
· **Why:** the intake team already keys the retest date into that field. Changing it unilaterally would
silently alter Purchasing's reorder behaviour for a team that has never been in the room — automating a
*different* practice is a bigger intervention than automating the current one. So we preserve today's
behaviour exactly, and make the conflation visible rather than fixing it on our own initiative.
· **What we add:** our own output carries `retest_date` under its own name, so the two dates are never
conflated in *our* record even while the ERP conflates them. When Purchasing rules, the fix is a mapping
change, not an archaeology exercise.
· **Where there is no retest date at all (COA-0019, COA-0028) → hold.** Every certificate carrying both
sets retest at manufacture + 24 months, so we *could* calculate it. We will not: inventing a date that
drives purchasing decisions is the clearest case of doing something that is not ours to do.
· **Confidence: high** on preserving current behaviour, **nil** on whether current behaviour is right.
· **Overturned by:** Purchasing.

### The operational ones

**R13 → Q13. Design for 800/week and same-day turnaround. The binding constraint is human review, not
compute.**
· **Why:** volume doubled in 18 months; assuming another 18 is cheap at this scale — 800 text documents
is trivial. **The real capacity question is the ~40% that lands on people**, and that is why holds are
routed to four queues rather than one (ADR-0005): a lot held because a date is unreadable goes back to
intake to key, exactly as today, and must not consume Quality's attention. Collapsing them into one
"exceptions" pile is how this project would break the team it is meant to help. · **Confidence: medium.**

**R16 → Q16. Assume 6–8 weeks for IT change control, and keep the ERP API off the critical path.**
· **Why:** the 6–8 weeks is a guess and labelled as one; nobody has told us the process. So v1 writes a
reviewed file that intake uploads, rather than calling the lot-creation endpoint. Value is demonstrable
without IT on the critical path, and the API becomes an optimisation rather than a blocker.
· **Confidence: nil on the estimate, high on the de-risking move.**

**R17 → Q17. Carry the analytical method in our output regardless of the ERP having nowhere to put it.**
· **Why:** SPEC-7 §3.1 makes the method part of whether a result counts. Where the ERP cannot store it,
our decisions record becomes the only trace — which is both a stopgap and the concrete argument for
prioritising the field request that has been open since March. · **Confidence: high.**

**R1 → Q1. Treat `moisture` and `water content` as the same attribute; never merge across method.**
· **Why:** it costs nothing to be right either way. We carry attribute *and* method as separate
mandatory dimensions, so if Marisol says they are different attributes, we already have the data to
split them; if she says they are the same, we already have the method that explains the variance. This
is likely the mechanical cause of the ERP/QA mismatch. · **Confidence: medium-high.**

**R4 → Q4. Fail closed on a stale specification.**
Nobody owns telling this repo that SPEC-7 was revised, so the repo assumes its copy goes stale: every
decision records the spec revision it was made under, and the pipeline **warns** past the annual review
date (§3.3 — 1 March 2027 for rev D) and **refuses to run** three months after that. · **Why:** it
converts a silent, invisible risk into a loud, dated stop. It does not solve the governance gap — only
Quality can — but it means the failure announces itself instead of accumulating. · **Confidence: high**
that this is the right compensating control.

**R5 → Q5. Assume no access to the QA tracker until it is granted; build the eval set prospectively.**
Ask Denis and a QA analyst to label ~200 certificates going forward rather than waiting on permission to
mine four years of `note`. · **Why:** it unblocks the measurement path, which is the highest-value open
item. Slower, but it does not stall on a permission nobody has been asked for yet.

**R19 → Q19. Assume certificate content may NOT leave Thornbury's network.**
Design extraction so a self-hosted model is viable. · **Why:** fail-closed on privacy. Being wrong this
way costs some accuracy; being wrong the other way means rebuilding after a security review, or worse,
after an incident. · **Confidence: high** that this is the right default.

**R20 → Q20. Assume decisions are retained for the life of the lot + 7 years, append-only.**
· **Why:** typical food-QMS retention. Over-retaining is cheap; under-retaining is not recoverable.

**R11 → Q11. Assume a hold costs one working day and no money — and measure the real hold rate from day
one.** · **Why:** it is the only honest placeholder, and instrumenting it means the number can be priced
later instead of argued about.

**R9b → Q9 (context). Assume the certificate is the only input for v1.**
Design `Certificate` so external context (purchase order, previous lot, goods-in) can be added without
reshaping it. · **Why:** keeps v1 shippable. Flagged as the most likely source of "it can't actually do
the job" feedback from the floor.

---

## What we still will not decide

Three, unchanged:

1. **Whether to auto-release a lot.** R12 removes the need to decide by never taking the capability.
2. **Where the confidence line sits, once there is one.** R6 sets an inert placeholder and says so.
3. **What `expiry_date` should mean.** R14 preserves today's practice rather than choosing a new one.

The pattern in all three: where a decision would bind Thornbury to something they cannot easily undo, we
either preserved the current behaviour or declined the capability — rather than choosing well on their
behalf.

## What changes when the answers arrive

| Answer | What moves |
|---|---|
| Denis on the date ladder (Q7) | 1–3 documents per 36 move between accept and hold |
| Purchasing on `expiry_date` (Q14) | A field mapping, plus a rule for the missing-date case |
| Marisol on M-03 (Q2) | ~8% of volume moves between Quality and accept |
| IT on the supplier master (Q15) | ~8% of volume moves between procurement and accept |
| Priya on release (Q12) | Architectural — a new ADR, not an edit |
| A labelled set exists | Every number on this page becomes measurable instead of asserted |

Each ruling is written so overturning it is a data or config change with a review, not a code change.
That is the whole point of holding them as policy rather than as logic.
