---
status: amber                 # green | amber | red
milestone_current: working slice
milestone_position: on-track  # on-track | ahead | behind
updated: 2026-08-30
next_milestone: decision rules against SPEC-7 — target TBD
---

<!--
  STATUS.md is the repo's current-state snapshot, maintained by hand (automation deferred, brief §15).
  The WBR pre-read AUTO-pulls from the front-matter + "Now"/"Next" sections; the conformance review reads
  milestone position from here. Keep it short — one screen. Stable headers so the tools can parse it.
-->

# STATUS — thornbury-coa-intake (SOW-2026-CAP-01)

_Rules wired against SPEC-7 under `reference/policy.json`. On the 36 supplied documents: 22 accept,
14 hold. No labelled set yet, so that split is arithmetic, not a measurement._

## Now
- **Milestone:** working slice — **on-track**. Deterministic parser (ADR-0007) and the SPEC-7 rules
  are wired, with every ruling held as reviewed data in `reference/policy.json`. `make check` is green
  with no skips, and a clean clone reproduces `submissions/decisions.jsonl` byte-for-byte.
- **The split matches the hand analysis exactly** — 22/14, document for document, predicted in
  `docs/working-answers.md` before the code existed. That is a consistency check between two
  independent routes to the same answer. **It is not evidence the answers are right**: both routes are
  ours, and there is still no labelled set.
- **Focus:** deliverables 2, 4 and 6 (deployment plan, handover package, working log) — all missing.

## Next
The rulings in `docs/working-answers.md` are decided but **not implemented** — they are documented policy,
not code. In order:

- **The deployment plan and the handover package** (deliverables 2 and 4), and the **working log**
  (deliverable 6).
- Withdrawn-revision detection (SPEC-7 §4). The staleness dates are in `policy.json` and nothing reads
  them yet — a certificate citing rev C would currently pass unremarked.
- A labelled evaluation set. Without one, no change to extraction or the rules can be *measured*, only
  asserted — and `CLAUDE.md` names this as an invariant that does not yet hold. **Every projected number
  in `working-answers.md` is arithmetic over 36 documents, not a measurement.**

## Deliverables — where we actually stand
The engagement asks for six things. A pre-build sweep on 2026-08-30 found **three missing entirely**,
which was a bigger gap than anything technical it turned up.

| # | Deliverable | State |
|---|---|---|
| 1 | A working slice | **done for the supplied corpus** — parser + rules green, 22/14 |
| 2 | A deployment plan that actually works | **missing** — fragments only (R16, ERP API off the critical path) |
| 3 | Decision records | **done** — ADR-0001…0007 |
| 4 | A handover package | **partial** — repo docs exist, no assembled package |
| 5 | `decisions.jsonl` | **done** — `submissions/decisions.jsonl`, passes `validate_submission.py` |
| 6 | A working log — how AI was used, incl. what it got wrong | **missing** |

Deliverable 6 has at least two entries waiting: the sample anomaly count stated as 12/36 when it is
18/36, and the two domain-model defects (M2) that came from designing before reading the corpus.

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
