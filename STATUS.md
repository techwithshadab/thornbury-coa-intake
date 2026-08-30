---
status: amber                 # green | amber | red
milestone_current: working slice
milestone_position: behind    # on-track | ahead | behind
updated: 2026-08-30
next_milestone: decision rules against SPEC-7 — target TBD
---

<!--
  STATUS.md is the repo's current-state snapshot, maintained by hand (automation deferred, brief §15).
  The WBR pre-read AUTO-pulls from the front-matter + "Now"/"Next" sections; the conformance review reads
  milestone position from here. Keep it short — one screen. Stable headers so the tools can parse it.
-->

# STATUS — thornbury-coa-intake (SOW-2026-CAP-01)

_The frame is built and green; the judgement is not built. Every document currently returns `hold`._

## Now
- **Milestone:** working slice — **behind**. Boundaries, reference data, the submission contract and the
  full check ritual are in place and passing. `app.decide()` is a stub: it returns `hold` with
  "rules not implemented" for every document. That is honest, and it is not a shippable posture — the
  ledger penalises over-holding as well as over-accepting.
- **Focus:** the SPEC-7 assessment in `app.decide()`, and the extraction that feeds it.

## Next
The rulings in `docs/working-answers.md` are decided but **not implemented** — they are documented policy,
not code. In order:

- Externalise the rulings as reviewed policy data (`reference/policy.json`) so overturning one is a data
  change with a review, not a code change. Required by the `decisioning_or_scoring` invariants.
- Compile step: certificate text → `Certificate` (`extraction` → `raw` → `domain`). Currently missing;
  `cli.run` hands `decide()` an empty certificate.
- The SPEC-7 rules: limits (§2), reportable method (§3.1), withdrawn revision (§4), stated-conformance
  contradicting the result (§5), supplier not on the master — plus the hold routing of ADR-0005 and the
  date ladder of ADR-0006.
- A labelled evaluation set. Without one, no change to extraction or the rules can be *measured*, only
  asserted — and `CLAUDE.md` names this as an invariant that does not yet hold. **Every projected number
  in `working-answers.md` is arithmetic over 36 documents, not a measurement.**

## Not built, deliberately — with the reason
- **OCR.** Out of scope per the engagement brief. The seam is `extraction.Extractor`; the one
  implementation reads pre-extracted text. What productionalising it takes is written up in
  `docs/reference/` — not left in a docstring.
- **A review queue / UI.** A held lot currently reaches a person as a line in a file.
- **A query surface over the audit trail.**

## Open questions — NOT ours to answer
The full register — the evidence behind each question, who owns it, and the assumption we run on until
it is answered — is **[`docs/open-questions.md`](docs/open-questions.md)**: 21 questions routed to their
owner and 10 stated assumptions. Kept there rather than restated here; two
half-true copies of the same list is how a register stops being read.

**None of them has an owner or a date. That is the largest risk on this engagement.** The three that
block work rather than merely shadow it:

- **Q14 — `retest_date` is not `expiry_date`** (Purchasing, not engaged). A required ERP field with no
  agreed source, and two documents in the sample carry no retest date at all. Blocks lot creation.
- **Q18 — ERP or QA tracker, which is authoritative?** (unassigned; Marisol Vega not engaged). Decides
  what "correct" means, so every other answer inherits from it. Open for years; this project forces it.
- **Q15 — three suppliers in the sample are not on the approved master** (IT / Purchasing). Either the
  master is stale, or unapproved material is arriving. Both want someone looking today.

Also unowned and material: whether certificate content may leave Thornbury's network (blocks go-live
gate B4); volume, peak and turnaround (never asked at kick-off — our miss); and whether these 36
documents are representative — **half of them (18/36) carry an anomaly**, against Denis's floor estimate
of "a handful a month" out of ~1,600.

**We are not waiting on them.** [`docs/working-answers.md`](docs/working-answers.md) records a
provisional, reversible ruling for each — what we build on, the business reason, what it costs if wrong,
and who overturns it. Three were architectural enough to become ADRs (0004 release stance, 0005 hold
routing, 0006 date ladder). Three we still decline to make; they are listed there too.

## Risks / blockers
- **No evaluation set** — solutioner. Every quality claim about this system is currently unfalsifiable.
  Mitigation: build a labelled set before the rules, not after.
- **`reference/source/` is a vendored copy of a controlled document** — Quality. It will drift, and there
  is no agreed notification path. Mitigation: `PROVENANCE.md` records the revision and date; the real fix
  is a feed, which needs an owner.
- **`criticality: regulated` with no Bar B gate green** — solutioner. See below; this is expected at this
  stage but must not be mistaken for readiness.

## Go-live backlog (Bar B — not started, not pretended)
`deployed` and `stateful` are false today. They become true when this runs as a service. Per surface:
B1 access topology · B2 a measured quality attestation (needs the eval set) · B3 abstain calibration —
the accept/hold threshold against Thornbury's own asymmetry · B4 security conformance (an LLM key, and
whether certificate text may leave the client boundary) · B5 scale at 400+/week with no stated peak ·
B6 data coverage · B7 data classification · B8 observability and a feedback loop back to the data.

## Links
- Blueprint / architecture: [`docs/overview.md`](docs/overview.md)
- Engineering contract: [`CLAUDE.md`](CLAUDE.md)
- Change log: [`./CHANGELOG.md`](./CHANGELOG.md)
- Decisions: [`./decisions/`](./decisions/)
