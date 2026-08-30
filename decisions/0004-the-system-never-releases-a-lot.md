---
id: ADR-0004
title: the system never releases a lot
status: Accepted
date: 2026-08-30
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [risk, authority, erp]
---

# ADR-0004: the system never releases a lot

## Context

Two sponsors described the outcome differently at kick-off. Priya Raghunathan: "the fields get filled in
without my team typing them." Denis Achebe: "we stop releasing lots we shouldn't." Nobody noticed the two
framings pull in opposite directions — a system built for the first accepts as much as it can, a system
built for the second holds whenever it is unsure.

Priya also said the sharper thing: "whatever the system puts in the ERP, we act on. Purchasing releases
against it, production schedules against it." Read literally, that makes every field this system writes a
release decision by proxy.

The ERP's own design contains the resolution, and nobody had used it. From `erp-fields.md`: `status`
defaults to `held` on creation, and "setting it to `released` is a separate action."

## Decision

**The system creates lots at the ERP's default `held` status and never sets `released`.** It does not
have, and will not be given, the capability to release. A person releases, exactly as today.

This is not a limitation we plan to remove. Adding auto-release later would be a new decision with its
own record, not the completion of this one.

## Consequences

- **Good — it dissolves the sponsor conflict rather than picking a winner.** Priya gets the data entry
  gone; Denis keeps the judgement gate precisely where it is. Both asks are satisfied by the same build,
  which is not usually available.
- **Good — it changes the risk profile of the whole engagement.** The worst failure this system can
  produce is a *wrong field on a held lot*, caught at the release step by the person who already performs
  it. It is not a released lot. That is the difference between an error and a recall conversation, and it
  is what makes a `regulated` criticality defensible on a first build.
- **Good — accountability stays where it already sits.** Q12 asks who is accountable when the system gets
  one wrong. By not taking the release capability we avoid moving the answer. The question still deserves
  one; this decision means the project is not blocked waiting for it.
- **Cost — the ceiling on automation is lower.** Someone still touches every lot. We are automating the
  keying, not the release. If Thornbury's actual goal was untouched lots, we have under-delivered against
  it and should be told so.
- **Cost — the benefit is smaller than the headline.** "89% less keying" is real; "89% less work" is not.
  The release click remains, and the note to Priya says so.
- **Watch — the pressure to relax this will come from success.** After a few clean months someone will
  propose auto-releasing the certificates that are obviously fine. That is a reasonable proposal, and it
  must arrive as an ADR with a measured basis, not as a config change.

## Options considered

- **Auto-release lots that pass every SPEC-7 check.** Rejected. It is the highest-value and
  highest-consequence capability in the system, we have no labelled data to justify it, and nobody asked
  for it. Taking it unasked would be the clearest instance of doing something that was not ours to do.
- **Release, but only for suppliers with a clean history.** Rejected for now: it needs history we have not
  been given, and it makes the first exception the hardest case to reason about.
- **Make it configurable, defaulting to off.** Rejected as the worst of both. A flag that grants release is
  release capability with a deniability layer, and a "temporary" flag that becomes product behaviour is
  precisely the quiet second path `CLAUDE.md` forbids.
