# Handover — Thornbury certificate-of-analysis intake

**From:** MathCo · **To:** Thornbury Ingredients · **Date:** 14 September 2026

This document is written for Thornbury. It says what you are receiving, what it does and does not
do, what it decided on your behalf while your questions were open, and what we need from you before
it can go further. Where it reports a gap it reports it plainly — a handover that describes itself
as finished is the one nobody should trust.

Your engineering colleagues will want `README.md` and `docs/architecture.md` as well. Everything
here holds regardless of who reads it.

---

## 1. What this does

Your intake team receives around four hundred certificates of analysis a week and keys the values
into the ERP by hand. This system reads the certificate instead and returns one of two answers for
each document:

- **Accept** — the fields, ready for the lot record.
- **Hold** — a reason written for the person who has to act on it, and the desk it belongs on.

**Over the thirty-six certificates you supplied: 21 accepted, 15 held.**

The judgement is the point, not the typing. Denis Achebe's framing shaped the whole design:
releasing a lot that should have been held is a recall conversation with a customer; holding one
unnecessarily is an annoyed supplier and a day of delay. Both are bad, and they are not the same
kind of bad.

**Please do not read 21/15 as an accuracy figure.** It is arithmetic over thirty-six documents. No
evaluation set exists, so nothing here is a measured quality claim — see §5.

## 2. What it deliberately does not do

**It never releases a lot.** Your ERP already creates lots at status `held` and treats release as a
separate action. This system fills in the fields; a person releases, exactly as today. We did not
take that capability. Adding it later should be a decision you make deliberately, not one that
arrives with an upgrade.

**It does not read PDFs.** Certificates reach it as extracted text. Making OCR production-grade was
out of scope for this build; the seam where it attaches is defined, and what productionalising it
involves is written up rather than left to be discovered.

**It does not call your ERP.** It writes a file. Connecting to the lot-creation endpoint is stage 3
of the deployment plan and is blocked on questions your teams still own.

**It does not guess.** Where it cannot read a field it produces nothing and holds the lot — it never
produces a plausible-looking wrong number. That is a deliberate trade: a certificate in a layout we
have not seen is held rather than misread, which costs you a manual keying and protects you from the
failure that matters.

## 3. Decisions we took on your behalf — all reversible

Twenty-one questions arose that were not ours to answer. Waiting on all of them would have meant
building nothing, so each carries a **provisional ruling** recorded with its reasoning, its business
consequence, what it costs if wrong, and **the person at Thornbury who owns the real answer**.

They are held as reviewed data in `reference/policy.json`, not buried in code, so overturning one is
a reviewed configuration change rather than a development task. `docs/working-answers.md` explains
every one.

The ones carrying the most consequence:

| We are currently | Because | Yours to settle |
|---|---|---|
| Holding any lot whose moisture came from loss-on-drying | SPEC-7 §3.2 and §4 — the method is not reportable, so the result cannot release a lot however good the number is | Marisol Vega |
| Holding any lot from a supplier not on the approved master | Your ERP would refuse it anyway. Three of the thirty-six are in this position, with otherwise clean certificates | IT and Purchasing |
| Writing the certificate's **retest** date into the ERP's `expiry_date` | It is what your team does today. They are not the same claim, and Purchasing reorders off the result — changing it silently would be a larger intervention than preserving it | Purchasing |
| Holding rather than calculating a missing retest date | Every certificate carrying both sets retest at manufacture + 24 months, so it *could* be calculated. Inventing a date that drives your reordering is not ours to do | Purchasing |
| Holding any date that reads two ways | A date resolved from a supplier's *other* paperwork is a guess about this document. Three certificates are affected | Denis Achebe |

**Three decisions we declined outright**, because a wrong answer would bind you to something hard to
undo: whether the system may release a lot, where a confidence threshold should sit once one exists,
and what `expiry_date` ought to mean. `docs/working-answers.md` records what we did instead.

## 4. What we need from you

`docs/open-questions.md` carries all twenty-one with the evidence behind each; `docs/questions-to-send.md`
has them drafted as notes, one per person. **None currently has an owner or a date, and that is the
largest risk to this work.** Three block progress rather than merely shadow it:

1. **What should go in `expiry_date`?** Your ERP requires it, no certificate states it, and two of
   the thirty-six carry no retest date at all. *Purchasing has not been engaged.*
2. **When the ERP and the QA tracker disagree, which is authoritative?** This decides what "correct"
   means, so every other answer inherits from it. It has been open for years; this work forces it.
   *Marisol Vega was not at the kick-off and should have been.*
3. **Are Fenwick Commodity Ltd, Aksoy Gıda Ticaret AŞ and Baltic Provisions UAB approved suppliers?**
   They are not on the master you gave us and their certificates are otherwise clean. Either the
   master is out of date, or material is arriving from unapproved sources. **This is worth someone
   looking at today, independently of this project.**

**One finding to put in front of Quality.** Eighteen of the thirty-six certificates — half — contain
something your own specification says a person must look at. Denis's estimate was a handful a month
out of roughly sixteen hundred. Either the set you sent was chosen to be difficult, or the current
process is missing a great deal. We cannot tell from inside the sample, and the two readings point in
very different directions commercially.

## 5. What is not finished

**There is no evaluation set, so there is no accuracy number.** This is the most important gap. Every
figure here is arithmetic over thirty-six documents. A real quality claim needs roughly two hundred
certificates carrying a QA analyst's accept/hold decision and reason — your tracker's `note` column
is the closest existing source. Until that exists, no responsible attestation can be made about how
well this performs, by us or by anyone else.

**Nobody outside the build has reviewed it.** One person wrote it and no second engineer has read a
line. The repository's own gate record in `reviews/` states this rather than glossing it.

**It is not deployed.** `docs/deployment.md` sets out four stages, each shippable, with the blockers
named. Stage 1 — running it by hand and reviewing the output — needs nothing from anyone and can
begin now.

**A question we did not ask at kick-off and should have:** your volume, your peak, and whether there
is a turnaround expectation on a held lot. We have "north of four hundred a week" and nothing else.

## 6. Running it

Full detail in `docs/runbook.md`; the short version:

```bash
make setup        # once
make submission   # runs the supplied corpus, validates it, proves the runs identical
make run DOCS=<your documents directory> OUT=decisions.jsonl
```

Two things worth knowing in operation:

**Held lots go to four desks, not one queue.** A lot held because a date was unreadable returns to
intake to key by hand — the process that handles all your volume today, so it is not new work. A lot
held because it breaches SPEC-7 goes to Quality. Collapsing those into one "exceptions" pile would
put a ninety-second keying job behind a quality investigation, and would overwhelm the team this is
meant to help.

**The system will eventually stop on purpose.** It holds a copy of SPEC-7 rev D. Nobody currently
owns telling it that a revision has issued, so it warns from March 2027 and refuses to run from June
2027 rather than quietly applying withdrawn limits. That is a safeguard rather than a fault — and the
real fix is a notification path someone at Quality owns.

## 7. Acceptance

This package is producer-written and has not been accepted. Nothing in it should be read as an
attestation. MathCo's own readiness scoring is a separate internal record and is not reproduced here.

| Role | Name | Decision | Date |
|---|---|---|---|
| Director of Supply Operations | Priya Raghunathan | pending | |
| Quality Manager | Marisol Vega | pending | |
| Intake Team Lead | Denis Achebe | pending | |

**Before signing, we would rather you pushed on:** the three blocking questions in §4, the absence of
an evaluation set in §5, and the supplier finding — which we think deserves attention regardless of
what happens to this project.
