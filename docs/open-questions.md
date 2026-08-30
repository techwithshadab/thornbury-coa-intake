# Open questions and stated assumptions

> The decisions that are **not ours to make**, who owns each one, and what we assumed in the meantime.
>
> Every question below is grounded in something in the 36-document sample or in what a named person
> actually said at kick-off. Nothing here is speculative. Where we had to proceed without an answer, the
> assumption is stated in Part 2 with what breaks if it is wrong.
>
> Status: **none of these has an owner or a date.** That is the single largest risk on this engagement.
>
> Drafted as notes you can actually send — five, one per stakeholder, with the sending order and what is
> blocked on what — in **[`questions-to-send.md`](questions-to-send.md)**.
>
> **We are not waiting on the answers.** The provisional ruling we build on for each, with the business
> consequence and the cost of being wrong, is in **[`working-answers.md`](working-answers.md)**.

---

## What the sample actually contains

Read before the questions — the questions are consequences of it. All 36 documents carry all four SPEC-7
attributes, and every result is within limits once units are normalised. The interesting content is
entirely in the edges:

| Signal | Count | Documents |
|---|---:|---|
| Result **outside** SPEC-7 limits, certificate says **PASS** | 2 | COA-0009 (Assay 101.366 %), COA-0033 (Assay 101.586 %) |
| Moisture by **Loss on Drying (M-03)** — not reportable under SPEC-7 §3.2 | 3 | COA-0004, COA-0026, COA-0029 |
| Supplier **not on the approved master** | 3 | COA-0003 (Fenwick Commodity Ltd), COA-0017 (Aksoy Gıda Ticaret AŞ), COA-0030 (Baltic Provisions UAB) |
| **Lot number disagrees with itself** inside one document | 2 | COA-0018 (header `HLW-1185`, results `HLW-1191`), COA-0023 (`SRE-6803` vs `SRE-6809`) |
| **No retest date** on the certificate at all | 2 | COA-0019, COA-0028 |
| Heavy metals reported in **ppb**, SPEC-7 limits are **ppm** | 2 | COA-0027 (7276 ppb), COA-0031 (7403 ppb) |
| Slash date that reads **two ways** | 4 | COA-0010, COA-0034, COA-0035, COA-0036 |

Two suppliers on the approved master — **Ardennes Fine Ingredients** and **Kowalczyk Surowce** — appear
in none of the 36 documents. So the master has names with no traffic, and the traffic has names not on
the master.

**Exactly 18 of 36 documents — half the sample — carry at least one of these.** The other 18 are clean on
every dimension. Denis estimated "a handful a month" out of roughly 1,600. If this sample resembles
normal intake rather than a deliberately hard set, the true rate is two orders of magnitude above what
the floor believes — and that is a bigger finding than the data entry.

*(An earlier draft of this file said "roughly 12 of 36, 33%." That was an undercount: the flagged set is
18. The clean set is listed in [`working-answers.md`](working-answers.md) so the split can be checked.)*

---

## Part 1 — Questions, by who owns the answer

### Marisol Vega — Quality Manager
*Owns SPEC-7 and the QA tracker. **Was not at the kick-off call.** Denis said she should have been. She
owns more of the unresolved surface than anyone else on this list.*

**Q1. Is `moisture` the same thing as QA's `water_content`?**
Denis has been told by two different people that it is and is not. SPEC-7 §3.2 gives the shape of an
answer: Karl Fischer (M-04) is the *sole* reportable method for moisture, and loss on drying (M-03)
"does not distinguish water from other volatiles and over-reads on hygroscopic materials." That reads
as though the disagreement is about **method**, not vocabulary — two people are both right about
different measurements. **That is a hypothesis, not a ruling, and we are not qualified to make it one.**
If it is right, the ERP's single `moisture_pct` field is silently mixing two different measurements
today. → *Assumption A1.*

**Q2. What happens to a lot whose moisture came from Loss on Drying?**
Three documents in 36 (8%). SPEC-7 §3.2 says an M-03 result "shall not be used to release a lot" and §4
says a lot reported by a non-reportable method "shall be referred to Quality." We read that as an
unambiguous hold. But we want it confirmed, because it is the difference between "8% of certificates go
to a queue" and "8% of lots stop." Also: **has anyone told these three suppliers?** SPEC-7 §3.3 gives
suppliers ninety days from notification to transition, and rev D became effective 1 March 2026 — so
whether these are late transitions or un-notified suppliers is a Quality question with a commercial tail.

**Q3. A certificate says PASS and the number is out of limits. Confirm the reading.**
COA-0009 and COA-0033. SPEC-7 §5 is explicit: the certificate is in error and the lot is referred to
Quality. We are confident. We are asking anyway, because this is exactly the case Denis described as
"the actual job," and we would rather have Quality's own words attached to the rule than our reading of
their document.

**Q4. What is the notification path when SPEC-7 is revised?**
§3.3 requires a controlled notification to *suppliers* on a method change. Nothing covers downstream
systems. This repo holds a **copy** of rev D (`reference/source/`, with `PROVENANCE.md`). When rev E
issues, nothing tells this repo, and it will keep asserting a withdrawn revision with total confidence —
which is precisely the failure §4 exists to catch, pointed the other way. **No gate inside this repo can
close this.** It needs Quality to own a notification, or an interface to the QMS.

**Q5. `conforms = QUERY` is 3% of QA's rows and the outcome lives in `note`, not in the column.**
That free-text column is, in QA's own words, "where the interesting information actually lives." It is
also the closest thing to a labelled history of *what a human decided and why* — the raw material for
the evaluation set we do not have. Can we read it? Under what terms?

---

### Denis Achebe — Intake Team Lead
*Twelve years, knows the suppliers individually, has raised the ERP/QA mismatch twice.*

**Q6. Where should the accept/hold line sit?**
Denis gave the asymmetry — a wrong release is a recall conversation, a wrong hold is an annoyed supplier
and a day of delay — and said "both are bad, they are not the same kind of bad." He has not been asked
**how much** more bad. That ratio is the single number that determines this system's behaviour, and it
is his and Priya's to set, not ours. Without it every threshold we choose is a guess wearing a number.
→ *Assumption A2.*

**Q7. May we infer a supplier's date convention from that supplier's other certificates?**
Four documents carry a slash date that reads two ways. One (COA-0034, Perrin & Co) resolves itself —
the document says "All dates are written day/month/year." The other three do not.

For **Halewood** (COA-0035, `07/02/2026`) the corpus answers it: Halewood's other certificates use
`15/03`, `25/10`, `27/12` — all unambiguously day/month. So `07/02/2026` is 7 February.
For **Zeeland Bulk BV** (COA-0010 `02/08/2026`, COA-0036 `02/10/2026`) the corpus does **not** answer
it. Zeeland has no unambiguous slash date anywhere in the sample. The only thing pointing at day/month
is that "BV" is a Dutch company — which is an inference about a country, not about a supplier's
templating software, and we are not willing to release a lot on it.

The question is whether the first move is even allowed. Deriving a per-supplier convention table from
past documents is defensible and reviewable; it is also a system deciding what a date means based on
other paperwork. **That is a judgement about how much inference is "ours to do," and it is Denis's and
Marisol's call.** → *Assumption A3.*

**Q8. Two documents disagree with themselves about the lot number.**
COA-0018 and COA-0023 each print one lot in the header and a different one over the results — a
transposition, exactly what Denis described. Today his people spot it and email the supplier. Confirm:
hold both, always, no exceptions? And does the hold reason need to name *which* number we think is
right, or is offering a guess itself unhelpful?

**Q9. Is the certificate the only input?**
The pipeline sees one document. Denis's analysts see the document, the delivery, the supplier's history,
and twelve years of knowing which suppliers send clean paperwork. If a decision needs the purchase
order, the previous lot, or the goods-in record, we are building something structurally unable to make
it — and we would rather know that now than discover it in the ledger.

---

### Priya Raghunathan — Director of Supply Operations
*The sponsor. Owns the intake team, the ERP lot record, and the budget.*

**Q10. What is success — fewer keystrokes, or fewer bad releases?**
The two framings in the room were not the same. Priya: "the fields get filled in without my team
typing them." Denis: "we stop releasing lots we shouldn't." A system optimised for the first accepts
aggressively; one optimised for the second holds. Both are defensible, they pull opposite ways, and
**nobody has been asked to choose.** This is the reframing question underneath the whole engagement and
it should be settled before the rules are written, not after the first bad number.

**Q11. Does a hold cost you anything today that we should be measuring?**
"An annoyed supplier and a day of delay" is qualitative. If holds have a real cost — a service level, a
production slot, a supplier scorecard — the system should know it. If they genuinely do not, the safe
default is much cheaper than we are assuming.

**Q12. When this goes wrong, who is accountable?**
The system will eventually accept a lot it should have held. Priya said "whatever the system puts in the
ERP, we act on." Before that happens once, it should be written down whether the accountable party is
the intake team, Quality, or MathCo, and what the rollback is. Nobody has raised it. **Asking is part of
the job.**

**Q13. Volume, peak, and turnaround.**
"North of four hundred a week," up from two hundred eighteen months ago. No peak figure, no turnaround
commitment. It was not offered at kick-off and **we did not ask** — that was our miss. If the growth
curve holds, the design target is not 400/week, and if there is a same-day commitment the queue design
changes.

---

### Purchasing
*Consumes `expiry_date` from the ERP for reorder planning. **Not yet engaged.***

**Q14. `retest_date` is not `expiry_date`. What should go in that field?**
The most consequential open question in the engagement, and the one with no owner at all.

The ERP has a required `expiry_date` and will not save a lot without it. Certificates state a **retest
date**. They are different things: a retest date says "re-examine this material by then," an expiry date
says "this material is finished." Denis: "those are not the same thing and I have never been comfortable
that we treat them as if they were." Purchasing runs reorder logic off the field.

So writing a retest date into `expiry_date` is not a mapping — it is a decision that changes what
Purchasing reorders and when, made on behalf of a team that has never been in the room. **We will not
make it.** → *Assumption A4.*

It gets sharper: **COA-0019 and COA-0028 have no retest date at all.** A required ERP field, no source
value, and no agreed rule. Every certificate that does carry both dates sets retest exactly 24 months
after manufacture — so the arithmetic is available. Using it would mean *inventing a date that drives
purchasing decisions*, which is squarely the thing that is not ours to do.

---

### IT
*Owns the ERP integration surface and the supplier master. Has a REST endpoint for lot creation with two
integrations on it. **Nobody has told us what their change process involves.***

**Q15. Three suppliers in the sample are not on the approved master — is the master stale, or are these
genuinely unapproved?**
Fenwick Commodity Ltd, Aksoy Gıda Ticaret AŞ, Baltic Provisions UAB. All three sent clean certificates:
every result in limits, reportable methods throughout, no anomalies. The ERP will refuse to create the
lot regardless.

Two very different worlds. Either the master is behind and these are approved suppliers missing from a
list — in which case holding them is friction with no safety value — or material is arriving from
suppliers nobody approved, which is a **procurement problem this project just surfaced** and is far more
important than data entry. Note that two names on the master send nothing, which is mild evidence the
list is not actively maintained. Either way the answer is IT's and Purchasing's, and either way somebody
should look at it today. → *Assumption A5.*

**Q16. What is the change process for a new consumer of the lot-creation endpoint?**
Unknown. It sits on the critical path to production and cannot be estimated until someone says what it
is. This is the most likely source of schedule surprise on the whole engagement.

**Q17. The ERP has nowhere to record the analytical method.**
A request has been open since March, unprioritised. SPEC-7 §3.1 makes the method part of whether a
result *counts at all* — QA record it for exactly that reason, and Denis's example last year was a lot
where "the number was fine but the method was wrong." So a lot can be correctly accepted here on a
reportable method and stored there with no trace of which method justified it. **The audit trail breaks
at the ERP boundary, and no amount of care on our side fixes it.** Does this project's need change the
priority?

---

### Cross-cutting — nobody currently owns these

**Q18. When the ERP and the QA tracker disagree, which is authoritative?**
Priya said the ERP is the system of record for the business. Denis said QA are the ones who actually
check. Marisol was not present. This has been unresolved for years, Denis has raised it twice, and — his
words — "it's not that anyone disagrees, it's that the two systems were built by different people at
different times and were never reconciled."

This project cannot avoid it. It writes into one system and will be measured against both. If we build
to the ERP we inherit its blind spots (no method field, `expiry_date`); if we build to QA's model we
build something the business does not treat as its record. **Automating on top of an unreconciled
disagreement makes the disagreement faster, not smaller.** → *Assumption A6.*

**Q19. May certificate content leave Thornbury's network?**
If extraction uses a hosted model, supplier certificates — commercial terms, analytical data,
identifiable suppliers — cross a boundary. This was never asked at kick-off because nobody was thinking
about how the AI works. It is a hard blocker on go-live (gate B4) and it is a client decision. Ask
before an architecture assumes an answer.

**Q20. Document retention.**
Nobody raised it and we did not ask. If certificates are records under Thornbury's QMS, retention and
immutability requirements apply to whatever we build.

**Q21. Are these 36 documents representative?**
A third carry an anomaly. Denis's floor estimate is "a handful a month" out of ~1,600 — around 0.3%. If
this set was curated to be hard, our error-rate expectations are wildly pessimistic; if it is a random
week, the intake team is missing far more than they think, and *that* is the headline finding of this
engagement. **We cannot tell from inside the sample, and the answer changes the business case.** →
*Assumption A7.*

---

## Part 2 — Assumptions we are making

Each one is a place we proceeded without an answer. Stated so a reviewer can attack them, and so the
person who owns the question can see what their silence is currently buying.

| # | Assumption | Why we made it | What breaks if it is wrong | How it gets killed |
|---|---|---|---|---|
| **A1** | `moisture` and `water_content` name the same attribute, and the real disagreement is about **method**, not vocabulary. | SPEC-7 §3.2 distinguishes M-04 from M-03 on exactly these grounds; it explains how two people can both be right. | The ERP's single `moisture_pct` is mixing two measurements, and reconciling ERP against QA on that column is meaningless. | Marisol confirms or denies in one sentence (Q1). |
| **A2** | Holding when uncertain is cheaper than accepting when uncertain, so ambiguity resolves to `hold`. | Denis's own framing, and the only defensible default absent a ratio. | Over-holding is penalised by the ledger and by the intake team. A system that holds 40% of intake has not replaced the typing. | Denis and Priya give a cost ratio, or a target hold rate (Q6, Q11). |
| **A3** | A date that reads two ways is **not** normalised by guessing. COA-0010, COA-0035, COA-0036 hold unless a convention is sanctioned. | The engagement's own validator rejects ambiguous dates on purpose: a date that reads two ways "has not been normalised; it has been passed on." | We hold 3 documents we could have resolved — one of them (Halewood) from evidence already in the corpus. | Denis sanctions per-supplier convention inference, or rules it out (Q7). |
| **A4** | We do **not** write a retest date into `expiry_date`, and we do **not** compute a missing retest date from manufacture + 24 months. | It is a decision about Purchasing's reorder logic, made for a team not in the room. Certificates are consistent at +24 months, which makes inventing one easy — and that is what makes it dangerous. | Every lot needs `expiry_date` and the ERP will not save without it, so this blocks lot creation until answered. It is the tightest coupling between an unanswered question and a broken path. | Purchasing states what the field means and what to do when the source is absent (Q14). |
| **A5** | A supplier not on the approved master is a `hold`, not a reject — and the master is treated as current. | The ERP will refuse the lot anyway, so holding costs nothing extra. Rejecting asserts something about the supplier relationship that is not ours. | If the master is stale we add friction with no safety value; if it is accurate, three unapproved suppliers are shipping material and that needs escalating today, not queueing. | IT/Purchasing confirm the master's currency and the three names (Q15). |
| **A6** | SPEC-7 is the authority on whether a lot is acceptable; the ERP is the system we write into; the QA tracker is neither, for now. | SPEC-7 is the only controlled document with acceptance criteria in it. It sidesteps the ERP-vs-QA dispute rather than settling it. | If QA's tracker is the real check, we have automated the system that is *not* checked and made the mismatch faster. | Priya, Denis and Marisol in one room settle Q18. |
| **A7** | The 36 documents are representative enough to design against, but **not** to quote an accuracy number from. | We have nothing else. Designing needs a sample; attestation needs a labelled set, and we have no answer key. | Any accuracy figure derived from these 36 is unfalsifiable and would be the most dangerous artifact this project could hand over. | A labelled set (see below), and Denis telling us how the 36 were chosen (Q21). |
| **A8** | The extraction seam is a stub. OCR is out of scope; text arrives pre-extracted. | Stated in the engagement brief. Held honestly as an interface, not a hidden coupling. | Nothing today. It becomes a live risk the moment someone reads "working slice" as "working on PDFs." | Recorded in ADR-0003 and `docs/reference/extraction-stub.md`; flips with a real extractor. |
| **A9** | Results are canonicalised to SPEC-7 units before comparison — ppb → ppm — and the conversion is recorded. | SPEC-7 §2 requires exactly this. Two documents need it (COA-0027, COA-0031); both pass after conversion and would falsely fail without. | Comparing 7276 ppb against a limit of 10 ppm rejects two clean lots. | Not open — it is a spec requirement, implemented as a stated invariant. |
| **A10** | Nothing in scope is personal data. | Certificates carry company and analytical data. The only personal fields we saw are QA analyst initials, which we do not consume. | If certificates carry named signatories in the real corpus, `handles_pii` flips and retention/redaction obligations attach. | Confirmed against a real (not sampled) batch. |

### The assumptions we refuse to make

Three, and they are the ones where a wrong choice binds Thornbury to something they cannot easily undo.
Each is set out in [`working-answers.md`](working-answers.md) with what we did instead:

1. **That the accept/hold threshold can be set by us.** It encodes Thornbury's tolerance for a recall
   against its tolerance for delay. We can build the mechanism, measure it, and show the trade-off curve;
   choosing the point on it is the client's. *What we did instead:* set an inert placeholder and showed
   that it does not currently bind, because every hold this system issues is rule-mandated by SPEC-7
   rather than chosen by us.
2. **That the system may release a lot.** *What we did instead:* declined the capability entirely — the
   ERP already defaults to `held` and a person releases (ADR-0004).
3. **That we may decide what `expiry_date` should mean.** *What we did instead:* preserved exactly what
   the intake team does today, and refused to invent a date where the certificate carries none.

The pattern: where the decision would bind them, we either kept the current behaviour or declined the
capability — rather than choosing well on their behalf.

---

## What we would do first

If one thing gets fixed: **an owner and a date for Q14** (`expiry_date`), because a required ERP field
with no agreed source blocks lot creation entirely.

If two: **Q18** (ERP vs QA authority), because it decides what "correct" means and everything else
inherits from it. It has been open for years and this project is the first thing that forces it.

If three: **a labelled set**. Roughly 200 certificates with a QA analyst's accept/hold and reason —
Q5's `note` column is the closest existing source. Without one, no claim this system makes about its own
quality can be checked, including by us. It is the difference between a system Thornbury can bind
decisions to and one they have to take on trust.

**And get Marisol Vega in the room.** She owns SPEC-7 and the QA tracker, she owns or co-owns eight of
the questions above, and she was not at the kick-off. Denis said she should have been. He was right.
