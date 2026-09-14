# The ask

---

**From:** Priya Raghunathan, Director of Supply Operations, Thornbury Ingredients
**To:** MathCo
**Subject:** CoA data entry — can AI just read these?

Hi,

Following up on our conversation last week.

Every lot we take in arrives with a Certificate of Analysis from the supplier. It's a PDF. Somebody
on my intake team opens it, reads the numbers off it, and types them into the ERP. We're doing
somewhere north of four hundred a week now and it was two hundred eighteen months ago. The team is
drowning and I can't keep adding people to a data-entry job in 2026.

What I want is straightforward: an AI that reads the PDF and fills in the fields. The information is
right there on the document. I've attached a batch of recent ones so you can see what we're dealing
with — the layouts are all over the place because every supplier does their own thing, which I
assume is the hard part.

I'd like to see something working in a few weeks. If it goes well we'd look at the other document
types we're buried in — packing lists, allergen declarations, the whole intake pile.

One thing to know: whatever the system puts in the ERP, we act on. Purchasing releases against
it, production schedules against it. So it needs to be right.

Priya

---

**From:** Denis Achebe, Intake Team Lead
**To:** MathCo
**Subject:** RE: CoA data entry — some context before you start

Priya asked me to send you whatever would be useful. A few things from the floor:

The typing genuinely is most of the job, and I'd be glad to see it go. But the typing isn't the part
that worries me.

What worries me is that QA keeps their own tracker and it doesn't match ours. We enter what we
enter, they enter what they enter, and every few months somebody notices the two disagree on a lot
and there's a scramble to work out which one is right. Nobody has ever sat down and settled it. I've
raised it twice. It's not that anyone disagrees — it's that the two systems were built by different
people at different times and were never reconciled.

Some specifics that come up constantly:

- We have a field called `expiry_date`. The certificates give a retest date. Those are not the
  same thing and I have never been comfortable that we treat them as if they were.
- QA records which *method* was used for each test. Our system has nowhere to put that. Last year we
  had a lot where the number was fine but the method was wrong, and we only caught it because
  someone in QA happened to look.
- We call something `moisture` and QA calls it `water content`. I *think* those are the same. I have
  been told by two different people that they are and are not.

Also — and this is the one that keeps me up — occasionally a certificate is just wrong. The supplier
transposes a lot number, or a value sits outside the specification and the document still says PASS.
Not often. A handful a month, maybe. When one of my people spots it they hold the lot and email the
supplier. That judgment is the actual job, and it's the part I don't know how you'd automate.

If it helps, the rule we work to is: if we release a lot we shouldn't have, that's a recall
conversation with a customer. If we hold a lot we didn't need to, that's an annoyed supplier and a
day of delay. Both are bad. They are not the same kind of bad.

Denis
