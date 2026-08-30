---
id: ADR-0007
title: parse deterministically and hold what we cannot read
status: Accepted
date: 2026-08-30
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [extraction, determinism, llm, tech-stack]
---

# ADR-0007: parse deterministically, and hold what we cannot read

## Context

The sponsor's framing was "an AI that reads the PDF and fills in the fields," so an LLM extractor is the
assumed answer. Before wiring the rules we had to actually choose, because three commitments already made
constrain it and we had not noticed they collide:

- `CLAUDE.md` declares **determinism** a universal invariant: same input, same output, no ambient
  entropy. An LLM breaks that unless pinned and cached, and even then it is a promise from a vendor
  rather than a property of the code.
- **R19** assumes certificate content may **not** leave Thornbury's network until someone says it may.
  Nobody has been asked (Q19).
- The engagement scores **three runs** of `decisions.jsonl`. If those runs are compared to each other,
  run-to-run variance is being measured directly.

Against that: the pipeline will be run on documents we have not seen, and a deterministic parser fails on
a layout it was not written for, where an LLM generalises.

The corpus settles less than it appears to. The 36 documents use six layout families, and every one cites
its method as `(SPEC-7 M-nn)` — a parser handles them comfortably. But six families in 36 documents from
eleven suppliers is weak evidence about the fortieth supplier's template.

## Decision

**A deterministic parser is the only extraction path. A document it cannot read confidently becomes a
`hold` routed to `intake_keying` (ADR-0005) — never a guess.**

No LLM is in the loop for this build. `extraction.Extractor` (ADR-0003) remains the seam where one could
later sit, and if it does it will **propose candidate fields with provenance that the deterministic rules
then check** — it will not decide.

The design consequence that makes this safe: an unseen layout produces *nothing*, not something wrong.
Every field is extracted by an explicit labelled pattern; a field with no match is absent, and absence is
already a first-class state that holds the lot (`missing is not zero`). There is no path where a novel
layout yields a plausible-but-wrong number.

## Consequences

- **Good — the failure mode of the thing we cannot test is silence, not error.** On an unseen layout the
  parser under-reads and the lot goes to a human, which is what happens today for 100% of volume. The bad
  version of this system reads a novel layout confidently and wrongly.
- **Good — it satisfies determinism, R19 and the three-run scoring at once**, and needs no API key, no
  outbound call, and no answer to Q19 before it can ship. It keeps `handles_secrets` and
  `external_network` honestly false.
- **Good — it is auditable.** Every extracted value points at the line it came from. "Why did it read
  99.7?" has an answer a QA analyst can check, which matters at `criticality: regulated`.
- **Cost — the hold rate is higher than an LLM's would be**, and rises on unfamiliar suppliers. That is a
  real cost paid in intake time, and it is the direction we chose to be wrong in.
- **Cost — new layouts need code, not prompting.** A new supplier template is a pattern addition, a test,
  and a release. At roughly forty suppliers with stable templating that is tolerable; at four hundred it
  would not be, and this decision should be revisited then.
- **Watch — the temptation to add a "best effort" fallback** that guesses when no pattern matches. That
  would convert the safe failure into the dangerous one and undo the whole basis of this decision.

## Options considered

- **LLM extraction as the primary path.** Rejected for now on three counts, any one of which would be
  enough today: it breaks a declared invariant, it needs an answer to a client question nobody has
  answered, and it makes the system's reasoning unauditable in a regulated setting. Not rejected on
  quality — it would very likely read more documents correctly.
- **Deterministic first, LLM fallback on the misses.** Genuinely attractive: the fallback only ever
  *reduces* the hold rate, and the rules still check whatever it proposes. Deferred rather than rejected —
  it is the natural next step, and it should arrive once Q19 is answered and an eval set exists to
  measure whether it helps. Building it now would mean adding an unmeasurable component to an unmeasured
  system.
- **Per-supplier template parsers.** Rejected: eleven suppliers in the sample, ~40 in reality, and a
  template file per supplier rots the moment one changes their letterhead. Labelled field patterns cut
  across layouts and degrade more gracefully.
