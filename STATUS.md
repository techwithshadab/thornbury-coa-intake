---
status: amber                 # green | amber | red
milestone_current: working slice
milestone_position: behind    # on-track | ahead | behind
updated: 2026-08-29
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
- Compile step: certificate text → `Certificate` (`extraction` → `raw` → `domain`). Currently missing;
  `cli.run` hands `decide()` an empty certificate.
- The SPEC-7 rules: limits (§2), reportable method (§3.1), withdrawn revision (§4), stated-conformance
  contradicting the result (§5), supplier not on the master.
- A labelled evaluation set. Without one, no change to extraction or the rules can be *measured*, only
  asserted — and `CLAUDE.md` names this as an invariant that does not yet hold.

## Not built, deliberately — with the reason
- **OCR.** Out of scope per the engagement brief. The seam is `extraction.Extractor`; the one
  implementation reads pre-extracted text. What productionalising it takes is written up in
  `docs/reference/` — not left in a docstring.
- **A review queue / UI.** A held lot currently reaches a person as a line in a file.
- **A query surface over the audit trail.**

## Open questions — NOT ours to answer
These are decisions that belong to Thornbury. Recording them is the work; answering them alone would be
the failure. None is currently owned.

- **`retest_date` is not `expiry_date`.** The ERP requires `expiry_date`, Purchasing runs reorder logic
  off it, and the certificate gives a retest date. Denis Achebe has never been comfortable that these
  are treated as the same thing. Writing a retest date into a field that drives reordering is a decision
  with a consequence, and it is Priya's and Purchasing's to make. **Owner: unassigned. Purchasing is not
  yet engaged.**
- **Is `moisture` the same as QA's `water_content`?** Denis has been told by two people that it is and
  is not. SPEC-7 §3.2 gives the shape of an answer — Karl Fischer is the sole reportable method for
  moisture, and loss on drying over-reads on hygroscopic material — which suggests the disagreement is
  about *method*, not vocabulary. That is a hypothesis, not a ruling. **Owner: Quality (Marisol Vega).**
- **ERP or QA tracker — which is authoritative when they disagree?** Priya said the ERP is the system of
  record; Denis said QA are the ones who actually check; Marisol was not on the call. This system writes
  into one of them and is measured against both. **Owner: unassigned. Marisol has not been engaged and,
  per Denis, should have been.**
- **The ERP has nowhere to put the method.** SPEC-7 §3.1 makes the method part of whether a result counts
  at all. A request to add the field has been open since March, unprioritised. Until then, a lot can be
  accepted here on a correct method and stored there with no record of it. **Owner: IT.**
- **How does this repo learn that SPEC-7 has been revised?** §3.3 requires a controlled notification to
  *suppliers*; nothing covers downstream systems. Until settled, a revision silently leaves this repo
  asserting a withdrawn rule. **Owner: Quality.**
- **Document retention.** Nobody raised it at kick-off and we did not ask.
- **Volume, peak, and turnaround.** "North of four hundred a week" and no peak figure or turnaround
  commitment. Not asked at kick-off.

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
