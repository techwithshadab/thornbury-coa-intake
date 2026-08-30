---
id: ADR-0005
title: route holds to four queues not one
status: Accepted
date: 2026-08-30
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [operations, capacity, explanation]
---

# ADR-0005: route holds to four queues, not one

## Context

ADR-0001 made `hold` a first-class answer. It did not say where a held lot goes, and on the sample that
turns out to matter more than the hold rate itself.

Applying the SPEC-7 rulings to the 36 supplied documents holds 14 of them (39%). Collapsed into a single
"exceptions" pile, that is roughly 156 items a week at current volume landing on a two-person intake team
that today escalates "a handful a month." **That would break the team this project exists to help** — and
it would look like the system over-holding, when in fact the holds are Thornbury's own rules firing.

But the 14 are not one kind of thing. Some are documents a person can key in ninety seconds. Others are
lots that must not move until Quality rules on them. Treating those identically wastes the scarcest
attention in the building.

## Decision

Every hold carries a **route** alongside its reason. Four routes, each with a different owner and a
different urgency:

| Route | Meaning | Sample | Who acts |
|---|---|---:|---|
| `quality` | a SPEC-7 rule is breached — the lot must not move | 5 (14%) | QA analysts |
| `procurement` | supplier is not on the approved master | 3 (8%) | Purchasing / IT |
| `supplier_query` | the document contradicts itself | 2 (6%) | Intake, as today |
| `intake_keying` | we could not read it; nothing is wrong with the lot | 4 (11%) | Intake, manual key |

`intake_keying` is the important one. Those lots are not exceptions in any business sense — they are
certificates the system could not parse confidently. They go back to exactly the process that handles
100% of the volume today, so they represent **no new work**, only work not yet removed.

Read that way, the true new load on Quality is 5/36 (14% of the sample), not 39%.

## Consequences

- **Good — it makes the capacity conversation honest.** "39% held" and "14% referred to Quality, 11%
  keyed as they are today" describe the same system and lead to completely different staffing decisions.
- **Good — it separates two things that would otherwise be confused:** how good the extraction is
  (`intake_keying` rate) and how good the incoming paperwork is (`quality` rate). They have different
  owners and different fixes. Better extraction shrinks the first and does nothing to the second.
- **Good — it gives the feedback loop somewhere to attach.** A lot routed to `intake_keying` and keyed
  without correction is a document the extractor should have handled; that is a training signal a single
  queue would have buried.
- **Cost — the route is a judgement encoded in the rules,** and a wrong route sends a lot to the wrong
  desk. Mitigated by keeping routes coarse and few.
- **Cost — it presumes an organisational shape** (that Purchasing will act on `procurement` holds) that
  nobody has confirmed. If they will not, those lots fall back to intake and the queue is misnamed.
- **Watch — the temptation to add a fifth route** for every new case. Four is already at the limit of what
  a two-person team can hold in their heads.

## Options considered

- **One queue, ordered by severity.** Rejected: it hides the distinction that makes the capacity numbers
  interpretable, and it puts a ninety-second keying job behind a Quality investigation.
- **Route by which rule fired.** Rejected: that is an explanation, not a destination. Six or seven routes
  that each map to the same two people is a taxonomy, not an operating model.
- **Let the reviewer triage.** Rejected: it is exactly the work we were asked to remove, and it makes the
  system's output a pile rather than a decision.
