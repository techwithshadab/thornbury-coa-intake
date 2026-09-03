---
id: ADR-0006
title: resolve dates by a four-step ladder and hold at the bottom
status: Superseded by ADR-0008
date: 2026-08-30
category: architecture
deciders: [solutioner-of-record, tech-lead]
supersedes: none
tags: [dates, inference, provenance]
---

# ADR-0006: resolve dates by a four-step ladder, and hold at the bottom

## Context

Four of the 36 certificates carry a slash date whose two components are both ≤ 12, so it reads two ways:
COA-0010 (`02/08/2026`), COA-0034 (`01/10/2026`), COA-0035 (`07/02/2026`), COA-0036 (`02/10/2026`).

The dates matter. `retest_date` drives Purchasing's reorder logic through the ERP's `expiry_date` field
(see R14). A date read six months wrong is a reorder placed six months wrong.

The engagement's own validator refuses ambiguous dates on purpose, with the reasoning stated in its
source: a date that reads two ways "has not been normalised; it has been passed on." Holding all four is
therefore defensible and cheap. But two of the four are resolvable without guessing, and holding a lot we
could have read is a cost the ledger charges us for.

## Decision

Dates resolve by a ladder. Stop at the first step that answers; if none does, hold.

1. **Unambiguous by construction.** ISO 8601 (`2026-01-27`), a written month (`28 Feb 2026`), or a slash
   date with a component > 12 (`15/03/2026`, `03/19/2026`). No inference.
2. **The document states its own convention.** COA-0034 prints "Issued from our Rotterdam facility. All
   dates are written day/month/year," making `01/10/2026` the 1st of October. Reading a document's own
   instructions is not inference — it is reading the document.
3. **Supplier convention**, and only where that supplier has **≥ 3 unambiguous slash dates in the reviewed
   corpus and all of them agree.** Halewood qualifies: `15/03`, `25/10`, `27/12` are all day/month, so
   COA-0035's `07/02/2026` is 7 February. The resolved date is stamped in the decision's provenance as an
   **inference**, naming the certificates it was drawn from, so a reviewer sees a claim and not a reading.
4. **Otherwise, hold**, routed to `intake_keying` (ADR-0005).

Zeeland Bulk BV reaches step 4: it has no unambiguous slash date anywhere in the corpus. COA-0010 and
COA-0036 hold.

## Consequences

- **Good — it recovers two documents (5.5%) without guessing at either.** Step 2 is not inference at all,
  and step 3 is an inference that is recorded, sourced and checkable.
- **Good — it fails in the safe direction.** The bottom rung is `hold`, and the held lot goes back to the
  process that handles everything today.
- **Good — it refuses the tempting wrong answer.** The obvious move on Zeeland is "BV is Dutch, Dutch
  companies write day/month." That is a guess about a country being used to decide what is in a warehouse.
  The ladder has no rung for it.
- **Cost — step 3 is a real inference and can be wrong.** If a supplier changes templating software
  mid-year, past certificates stop predicting present ones, and nothing in the corpus would say so.
- **Cost — the threshold of 3 is weakly grounded, and this is the weakest point in the decision.** It was
  chosen partly because Halewood has exactly 3, which is close to circular. It is currently load-bearing
  for exactly one document. It should be re-derived against a larger corpus before anyone trusts it, and
  until then the honest description is "a rule calibrated on the case it admits."
- **Watch — step 3 is the rung to delete first** if Denis is uncomfortable. Removing it costs 1 document
  in 36 and nothing else; the other three rungs stand on their own.

## Options considered

- **Hold all four ambiguous dates.** The conservative option, and genuinely defensible — it is what the
  supplied validator's reasoning implies. Rejected because step 2 requires no inference whatsoever, and
  holding a document that tells you how to read it is a failure to read it.
- **Infer from the supplier's country.** Rejected: an inference about a jurisdiction standing in for a
  fact about a document template. It would have "resolved" both Zeeland dates, which is exactly the
  confidence this system should not have.
- **Infer from plausibility** (e.g. prefer a manufacture date that is not in the future). Rejected: it
  reads sensible and is unsound. Eight certificates in the sample carry manufacture dates later than the
  date this analysis was run, so "the future is implausible" would have made confident wrong calls.
- **Ask the supplier.** Correct, and far too slow for 400 a week. It is what the `intake_keying` route
  produces for the cases that reach step 4.
