---
id: ADR-0001
title: hold is a first-class answer, not a pipeline failure
status: Accepted
date: 2026-08-29
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [decisioning, abstain]
---

# ADR-0001: hold is a first-class answer, not a pipeline failure

## Context

The sponsor's ask is "an AI that reads the PDF and fills in the fields" — framed as an extraction
problem. The intake team lead's account is different: the typing is the volume, but the judgement is the
job, and a handful of certificates a month are simply wrong (a transposed lot number, a result outside
specification with PASS printed over it).

Thornbury's own rule states the asymmetry: releasing a lot that should have been held is a recall
conversation with a customer; holding a lot that did not need it is an annoyed supplier and a day of
delay. Both are bad. They are not the same kind of bad.

A system modelled as "extract fields, and error when you can't" makes the hold an exception path — a
thing that happened *to* the pipeline. That framing loses the judgement, and the judgement is what
Thornbury is actually buying.

## Decision

`hold` is one of exactly two values of `Decision.action`, alongside `accept`. It is a *conclusion*, not a
failure. It carries structured `Finding`s written for the person who has to act on it, and it is produced
by the same runtime path that produces an accept.

Consequently there is no third state, no confidence score leaking across the boundary as a decision, and
no silent default in either direction. Where the evidence does not settle a lot, the answer is `hold`
with a reason.

## Consequences
- **Good:** the thing the client is buying is in the type system. A reviewer can read `Decision` and see
  that abstaining is a supported outcome rather than an error path someone remembered to handle.
- **Good:** the hold reason is structured data callers render, so two consumers explain the same hold the
  same way.
- **Cost:** holding is cheap to emit, and a system that holds everything is not a solution — the ledger
  penalises over-holding. The calibration of where the line sits is deferred to the eval set (Bar B3) and
  is not settled by this ADR.
- **Watch:** if `hold` ever grows sub-states ("hold-pending-supplier", "hold-QA"), that is a contract
  change, a `SCHEMA_VERSION` bump, and a conversation with QA about who acts on which — not a quiet enum
  addition.

## Options considered
- **Extraction with an error path.** Rejected: it models the judgement as a malfunction.
- **A confidence score, thresholded by the consumer.** Rejected: it pushes the accept/hold decision onto
  whoever reads the file, so two consumers would draw the line differently, and the asymmetry Thornbury
  stated would live nowhere in particular.
- **Three actions (accept / hold / reject).** Rejected for now: rejecting a lot is a decision with
  supplier and commercial consequences that nobody has said is ours. The ERP already has a `rejected`
  status and a human path to it.
