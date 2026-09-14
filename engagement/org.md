# Who's who at Thornbury

A sketch of the people this touches. Assembled by MathCo from the kick-off call — not a Thornbury
document, and not exhaustive.

## Supply Operations

**Priya Raghunathan — Director of Supply Operations.** The sponsor. Owns the intake team, the ERP
lot record, and the budget for this. Wants the data-entry load gone and is thinking ahead to the
other document types in the intake pile.

**Denis Achebe — Intake Team Lead.** Runs the two-person intake team day to day. Twelve years at
Thornbury. Knows the suppliers individually and can usually tell you which ones send clean
certificates and which ones don't. Has raised the ERP/QA mismatch internally more than once.

**Intake team — two analysts.** Open the certificate, key the values, flag anything that looks
wrong to Denis.

## Quality

**Marisol Vega — Quality Manager.** Owns SPEC-7 and the QA tracker. Was not on the kick-off call;
Denis suggested she should have been.

**QA analysts — three.** Review incoming lots, maintain the tracker, chase suppliers on anything
marked `QUERY`. They are the people who currently decide what happens to a certificate that doesn't
look right.

## Elsewhere

**Purchasing** consumes `expiry_date` from the ERP for reorder planning. Not yet engaged on this.

**IT** owns the ERP integration surface and the supplier master. They have an existing REST endpoint
for lot creation and two integrations already using it. Any new consumer goes through their change
process; nobody has told us what that involves yet.

---

## Notes from the kick-off

Recorded as stated. Not resolved.

- Priya described the outcome as "the fields get filled in without my team typing them."
- Denis described the outcome as "we stop releasing lots we shouldn't."
- Asked whether the ERP or the QA tracker is authoritative when they disagree, Priya said the ERP
  is the system of record for the business. Denis said QA are the ones who actually check. Marisol
  was not present.
- Asked what happens today when the intake team is unsure about a certificate, Denis said they hold
  it and email the supplier, and that QA gets involved "if it's a real one."
- Volume was given as "north of four hundred a week," up from around two hundred eighteen months
  ago. No one offered a peak figure or a turnaround commitment, and we did not ask.
- Nobody raised document retention. It did not come up.
