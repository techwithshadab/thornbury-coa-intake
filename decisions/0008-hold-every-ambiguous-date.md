---
id: ADR-0008
title: hold every ambiguous date
status: Accepted
date: 2026-09-03
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: ADR-0006
tags: [dates, inference, consistency]
---

# ADR-0008: hold every ambiguous date

**Supersedes [ADR-0006](0006-resolve-dates-by-a-four-step-ladder-and-hold-at-the-bottom.md).**

## Context

ADR-0006 built a four-rung ladder. Rungs 1 and 2 read the document: an unambiguous date, or a date
made unambiguous by a convention the document states about *itself*. Rung 3 went further — it
resolved an ambiguous date from **≥3 agreeing certificates by the same supplier**, stamping the
result as an inference with its evidence.

ADR-0006 recorded rung 3 as its own weakest point, for a reason that did not improve on inspection:
the only supplier it admitted (Halewood Ingredients) has exactly 3 unambiguous slash dates in the
corpus, so the threshold had been calibrated on the single case it let through. It was load-bearing
for one document out of 36.

The argument that settles it is **consistency, not the threshold**. The same ladder already refuses
to resolve Zeeland Bulk BV's dates, on the grounds that "BV is a Dutch company form" is a claim about
a jurisdiction standing in for a fact about a document template. Rung 3 is the same kind of move —
a claim about a supplier's *other paperwork* standing in for a fact about *this* document — with
marginally better evidence. The only thing separating the two was a number we picked.

A system that refuses one inference and accepts a structurally identical one has not drawn a
principle; it has drawn a threshold and called it a principle.

## Decision

**Rung 3 is removed. A date resolves only from the document in front of us, or the lot holds.**

1. **Unambiguous by construction** — ISO 8601, a written month, or a slash date with a component > 12.
2. **The document states its own convention** in prose (COA-0034: "All dates are written
   day/month/year"). Reading a document's own instructions is not inference.
3. **Otherwise → hold**, routed to `intake_keying` (ADR-0005).

The corpus analysis that fed rung 3 is **kept in `reference/policy.json` as
`evidence_considered_but_not_acted_on`** — Halewood writes day/month, Brightmoor writes month/day,
Zeeland gives no signal at all. It is real work and the next team should not have to redo it. It is
labelled as not-acted-on and no code reads it.

## Consequences

- **Good — the rule is now statable in one sentence** that survives challenge: *this system resolves
  a date only from the document it is reading.* ADR-0006's version needed a threshold, a rationale
  for the threshold, and an admission that the rationale was weak.
- **Good — it removes the finding we would have conceded first.** The engagement asks us to defend
  two decisions with a reviewer arguing the other side. Rung 3 was the one that would not have held.
- **Cost — one more document holds.** COA-0035 joins COA-0010 and COA-0036 in `intake_keying`.
  Accept/hold moves 22/14 → **21/15**, and the ledger penalises unnecessary holds. We are paying
  roughly 3% of the corpus for a rule we can defend.
- **Cost — a real signal is being ignored.** Halewood almost certainly does write day/month. We are
  choosing not to act on something that is probably true, which is only the right call because the
  cost of being wrong is a date that drives Purchasing's reorder logic.
- **Watch — this will be proposed again**, and reasonably, once there is a labelled set and a larger
  corpus. With a threshold derived from data rather than from the case it admits, and measured
  against real outcomes, rung 3 becomes defensible. It is not defensible *now*, on 36 documents.

## Options considered

- **Keep rung 3 at threshold 3.** Rejected on consistency, not on the threshold: it cannot coexist
  with our refusal to infer Zeeland's convention without an argument neither of us could make.
- **Raise the threshold to 5.** Rejected as the worst of both: identical output to removal on this
  corpus (no supplier qualifies), while shipping a mechanism that does nothing and still has to be
  explained. Inert policy is a maintenance cost with no benefit.
- **Ask Denis first and build to his answer.** Correct, and still the plan — this is his call (Q7),
  and the note in `docs/questions-to-send.md` asks it. But the question is unanswered and unsent, and
  the safe default while it is open is the one that guesses less.
