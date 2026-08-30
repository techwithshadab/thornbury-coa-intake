# Questions to send — five notes, one per stakeholder

Drafts of the questions in [`open-questions.md`](open-questions.md), written to be sent. Each note is
short on purpose: a stakeholder who gets eight questions answers none, and the register has twenty-one.
What is left out of a note is not dropped — it is waiting behind something else.

Sign-off is `Shadab` throughout; change it to whatever you actually sign.

---

## Before you send

**Two of these cannot be sent yet.** Purchasing and IT have no named contact — org.md records the roles
and nothing else. Ask Priya for the names first; that request is folded into her note.

**Marisol should not be cold-emailed.** She owns SPEC-7 and the QA tracker, and she was not on the
kick-off call. A note out of nowhere from a consultancy she has not been introduced to, asking her to
adjudicate her own specification, starts the relationship badly. Ask Denis to introduce you — he already
thinks she should be involved — and send the note after.

**Suggested order.** Denis first: he replies fastest, and his answers sharpen the others. Then Priya,
because two of the three remaining notes need names only she can give. Marisol once introduced.
Purchasing and IT last, when you can address them to a person.

**What is blocked on what.** Nothing about the accept/hold rules should be built before Denis answers
Q1 in his note. Nothing about `expiry_date` can be built at all until Purchasing answers. The supplier
master question in IT's note is the only one worth chasing by phone today.

---

## 1 · Denis Achebe — Intake Team Lead

> **Subject:** Four questions from the certificate sample — and one thing in it I'd like your read on

Denis,

Thank you for the note before we started. The detail about the retest date, the method field and the
`moisture` / `water content` disagreement has shaped how we're building this more than anything else we
were given.

We've now read all 36 certificates. Four questions, and one observation I'd rather raise early than sit
on.

**1. How much worse is a wrong release than a wrong hold?**
You said both are bad and they're not the same kind of bad. That's the right frame, and I need to turn
it into a number. If holding a lot unnecessarily costs a day of delay and an awkward call, and releasing
one wrongly is a recall conversation — roughly how many unnecessary holds would you trade to avoid one
wrong release? Ten? A hundred? A rough figure is genuinely useful; it's the setting that decides how
cautious the system is, and I'd rather have your instinct than my guess.

**2. Can I read a supplier's date convention off their other certificates?**
Four certificates have a date like `07/02/2026` that could be July 2nd or February 7th. For Halewood I
can resolve it — their other certificates use `15/03`, `25/10`, `27/12`, so they clearly write
day/month, which makes that one 7 February. For Zeeland Bulk I can't: both of their ambiguous dates have
no other Zeeland certificate to compare against.

Is reading it off their past paperwork something you'd be comfortable with, or does a date that reads
two ways always go to a person? Both are defensible. It's your call, not mine.

**3. Two certificates disagree with themselves about the lot number.**
COA-0018 has `HLW-1185` in the header and `HLW-1191` over the results; COA-0023 has `SRE-6803` and
`SRE-6809`. Exactly the transposition you described. I'm assuming both hold, always. When your team
flags one of these, is it useful if the note suggests which number looks right, or does offering a guess
just get in the way?

**4. Is the certificate the only thing your analysts look at?**
The system sees one document. Your people see the document, the delivery, the supplier's history and
twelve years of knowing who sends clean paperwork. If any of these calls actually need the purchase
order, the previous lot or the goods-in record, I'd rather know now — I'd be building something
structurally unable to make that call.

**The observation.** Exactly half of the 36 — 18 documents — have something in them that isn't routine.
Two report a result outside specification and still say PASS. Three use loss-on-drying for moisture,
which SPEC-7 says can't release a lot. Three are from suppliers not on the approved list you sent us.
Two have no retest date. Two have the lot mismatch above. Four have a date that reads two ways. Two
report heavy metals in ppb against a limit written in ppm.

That is a long way from a handful a month.

I don't want to read too much into it. It could easily be that this batch was picked to be interesting.
But if it's just a normal week, that's worth knowing, and it's a bigger finding than the data entry. Do
you know how these 36 were chosen?

Thanks,
Shadab

---

## 2 · Priya Raghunathan — Director of Supply Operations

> **Subject:** One thing worth settling before we build, and three names I need

Priya,

Good progress — we have the pipeline running end to end over the 36 certificates you sent, and the
architecture is in place. Before we write the rules that decide what gets accepted, there's one question
I'd like to put to you directly, because I don't think it's been asked.

**1. Is success fewer keystrokes, or fewer bad releases?**
At kick-off you described the outcome as the fields getting filled in without your team typing them.
Denis described it as stopping releases that shouldn't happen. Both are reasonable, and I don't think
anyone noticed they pull in opposite directions: a system built for the first accepts as much as it can,
a system built for the second holds whenever it's unsure.

We can't have both at the maximum. I'd rather you chose the balance now than discover it in the first
month. My working assumption, until you say otherwise, is that you'd rather we held too much than too
little — but that assumption costs you throughput, so it should be a decision, not a default.

**2. Which is authoritative when the ERP and the QA tracker disagree?**
You said the ERP is the system of record for the business; Denis said QA are the ones who actually
check. Marisol wasn't on the call. Denis tells me this has come up repeatedly over the years without
being settled.

This project can't route around it. It writes into one system and will be judged against both. Could we
get the three of you in a room for thirty minutes? It's the single most useful half hour available to
this project, and it would outlast us.

**3. When the system eventually gets one wrong, who is accountable?**
It will happen — no system reading supplier paperwork is perfect, which is why we've built holding in as
a first-class outcome rather than an error. You said whatever the system puts in the ERP, you act on. So
before it happens once, I'd like it written down whether the accountable party is intake, Quality or us,
and what the rollback looks like. Much easier to agree now than during the incident.

**4. Volume and timing.** We have "north of four hundred a week," up from two hundred. We don't have a
peak figure or a turnaround expectation — that's my omission at kick-off. Is there a busiest week we
should design for, and is there a point at which a held lot becomes a problem in itself?

**5. Three introductions, please.** I need a contact in Purchasing (they consume the expiry date and
there's a decision only they can make), one in IT (the lot-creation endpoint and the supplier master),
and I'd like Denis to introduce me to Marisol Vega, since she owns the specification everything here
depends on.

**One to flag early:** if the system uses a hosted AI service to read the certificates, their contents
leave your network. I don't know your position on that and it will need answering before anything goes
live — worth pointing me at whoever owns it.

Best,
Shadab

---

## 3 · Marisol Vega — Quality Manager

> **Subject:** Introduction, and some questions your specification has already answered
> *(Send only after Denis has introduced you.)*

Marisol,

Denis will have mentioned us — MathCo, working with Priya's team on reading certificates of analysis
automatically so intake aren't keying them by hand. I wanted to reach out directly, because the more we
look at this the more it turns out to be a Quality question wearing a data-entry costume.

SPEC-7 has been the most useful document we've been given. Several things we were treating as
judgement calls turn out to be answered in it plainly. A few it doesn't settle, and those are yours.

**1. Are `moisture` and `water content` the same measurement?**
Denis mentioned he's been told by two different people that they are and they aren't. Reading §3.2, I
wonder whether both are right and the disagreement is really about method — Karl Fischer measures water,
loss on drying measures water plus anything else volatile, so on a hygroscopic material they'd give
different numbers for the same sample and both be correctly labelled.

If that's the case, the ERP's single moisture field is currently holding two different measurements
depending on which method the supplier used, which would explain some of the mismatch between your
tracker and theirs. I'd rather ask than assume — this is well outside my expertise.

**2. Three of the 36 certificates report moisture by loss on drying (M-03).**
COA-0004, COA-0026 and COA-0029. Reading §3.2 and §4, I take those as referred to Quality, not
releasable on the certificate. Can you confirm? And separately: rev D took effect on 1 March, and §3.3
gives suppliers ninety days from notification — do you know whether those three were notified, or
whether we've found suppliers who haven't transitioned?

**3. Two certificates state PASS on a result outside the limits.**
COA-0009 reports assay at 101.366% and COA-0033 at 101.586%, both against a 99.0–101.0 limit, both
marked PASS. §5 reads unambiguously to me: the certificate is in error and the lot is referred to
Quality. I'm asking anyway, because I'd rather hold your words than my reading of your document.

**4. How would this system learn that SPEC-7 had been revised?**
This is the one that worries me. What we're building holds a copy of rev D. §3.3 covers notifying
suppliers of a method change, but nothing covers notifying a downstream system. If rev E issues, our
copy keeps applying withdrawn limits confidently and nothing flags it — which is exactly the failure §4
exists to catch, pointed the other way. Nothing we can build on our side fixes this; it needs a
notification path that someone owns.

**5. A request.** Your tracker's `note` column is, by QA's own description, where the interesting
information actually lives — particularly on the ~3% marked QUERY. That's the closest thing that exists
to a record of what a trained person decided and why, and it's the raw material we'd need to check
whether this system is any good. Would you be open to us reading a slice of it, on whatever terms suit
you?

Happy to come and talk any of this through rather than trade email.

Best regards,
Shadab

---

## 4 · Purchasing

> **Subject:** The expiry date on incoming lots — a decision we don't think is ours
> *(Needs a named contact from Priya first.)*

Hello,

I'm working with Priya Raghunathan's team on automating certificate-of-analysis intake. You haven't been
involved so far, and I think that's a gap — there's a decision in this that lands on you.

**The situation.** The ERP has a required `expiry_date` on every lot, and I understand you run reorder
planning off it. Supplier certificates don't state an expiry date. They state a **retest date** — the
date by which the material should be re-examined, which isn't the same claim as the date it stops being
usable. Today that retest date is keyed into the expiry field. Denis Achebe tells me he's never been
comfortable with it.

Right now that's a manual habit. If we automate it, it becomes a rule applied several hundred times a
week without anyone looking, and it drives what you reorder and when. That's your call to make, not
ours, so I'd rather stop and ask.

**1. What should go in `expiry_date` for an incoming lot?** The certificate's retest date, as today?
Something derived from it? Something else entirely?

**2. What should happen when there's no retest date at all?** Two of the 36 certificates we've seen
don't state one. Every certificate that does state both sets retest exactly 24 months after manufacture,
so we *could* calculate it — but that would mean inventing a date that then drives your purchasing
decisions, and I'm not willing to do that on my own initiative. Should those lots stop and wait for a
person?

**3. Would a distinction between the two dates be useful to you,** if we could get IT to add a field?
If retest and expiry genuinely mean different things for your planning, this is the moment to say so.

This one blocks us — the ERP won't save a lot without the field — so an answer even in rough form would
unblock work.

Thanks,
Shadab

---

## 5 · IT

> **Subject:** Supplier master, the lot-creation endpoint, and the method field
> *(Needs a named contact from Priya first.)*

Hello,

I'm working with Priya Raghunathan's team on automating certificate-of-analysis intake. Three things,
the first of which may want looking at today regardless of our project.

**1. Is the approved-supplier master current?**
Of 36 recent certificates, three are from suppliers not on the list we were given: **Fenwick Commodity
Ltd**, **Aksoy Gıda Ticaret AŞ** and **Baltic Provisions UAB**. All three are otherwise clean — every
result within specification, correct methods throughout.

Two possibilities, and they're very different. Either the master is behind and these are approved
suppliers missing from the list, or material is arriving from suppliers who haven't been approved. I
can't tell from the outside. Worth noting that two names *on* the list — Ardennes Fine Ingredients and
Kowalczyk Surowce — sent nothing in this batch, which mildly suggests the list isn't actively maintained.

Either way, the ERP will refuse to create lots for those three, so someone is presumably handling them
manually today.

**2. What does your change process involve for a new consumer of the lot-creation endpoint?**
I understand there's an existing REST endpoint with two integrations on it. We'd be a third. Nobody has
been able to tell us what your process for that looks like — review, environments, testing, lead time.
It sits on our critical path and we can't put a date on go-live until we know. Even a rough shape would
help.

**3. The analytical method field.**
I gather there's been a request open since March to add somewhere to record which method produced each
result, and that it hasn't been prioritised. From our side it matters more than it might appear: the
specification says a result only counts if it came from an approved method for that attribute, so the
method is part of whether the number is valid at all — not metadata about it.

The practical effect is that we can correctly accept a lot on the right method and store it with no
record of which method justified it. QA record it; the ERP can't. Does this project change the case for
prioritising it?

Happy to talk any of this through.

Thanks,
Shadab
