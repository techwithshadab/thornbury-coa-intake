# Working log — how AI was used on this build

> Deliverable 6. An account of where AI was a thought partner, where it taught me a domain I am not
> expert in, and where it executed work I then verified — plus what it got wrong.
>
> **Drafted from the session record; the judgements are mine to confirm.** Where this log says "I
> decided", check that it matches your memory before you sign it. A working log written by the tool
> it is reporting on has an obvious conflict of interest, and the honest response is to say so at the
> top rather than to write around it.

---

## The honest headline

**AI executed most of the artifact production in this repo — the code, the ADRs, the analysis
documents, this file.** I directed it, challenged it, and verified its output. Understating that
would be the real integrity failure, so: the writing is largely AI's, the structure of the work and
the decisions about what to do next are largely mine, and the errors are shared.

The single most useful thing I did was **repeatedly refuse to let it build before sweeping for what
was missing.** That happened three times, and it paid every time. Details below.

---

## Where it was a thought partner

**Reframing the ask.** The sponsor asked for "an AI that reads the PDF and fills in the fields." The
intake team lead's note said something different — that the typing is the volume but the judgement is
the job. AI surfaced that these two framings pull in opposite directions and that nobody had been
asked to choose. That became ADR-0001 (`hold` is a conclusion, not a failure) and question Q10.

**The move I would not have found alone.** ADR-0004 — the system never releases a lot. The ERP
already defaults `status` to `held`, and releasing is a separate action, so the capability was never
needed. That dissolves the sponsor conflict instead of picking a side and caps the worst failure at
*a wrong field on a held lot* rather than a released one. AI found it by reading `erp-fields.md`
closely rather than by being clever, which is the useful lesson.

**The capacity consequence.** 39% held sounds like the system over-holding. Split by route (ADR-0005)
it is 14% genuinely new load on Quality and 11% going back to the process that already handles 100%
of volume. Same system, same numbers, completely different staffing conversation. AI proposed the
split; I pushed on whether four queues was over-engineering and concluded it was not, because
collapsing them is what would break the intake team.

**Where I overruled it.** AI's first surface classification declared `handles_secrets` and
`external_network` **true**, in anticipation of an LLM extractor. Nothing in the build uses a
credential or the network. Declaring surfaces we might one day have fills the assessment with
not-applicable findings and makes the repo look more capable than it is. Set both to `false`, with
the change that flips each one named in the manifest.

---

## Where I used it to learn a domain I am not expert in

I have no background in pharmaceutical or food-ingredient quality management. Three things AI taught
me that I have since checked against SPEC-7 itself:

**Why the analytical method is not metadata.** SPEC-7 §3.1 says a result is only reportable when
produced by the named method. So a moisture value from loss-on-drying is not a slightly-worse
moisture value — it is not a result at all for acceptance purposes. That is why the method check runs
*before* the limits check in `app.py`, and why three certificates with every number in range are
still held.

**Why `moisture` and `water content` can honestly be both the same and different.** Karl Fischer
measures water; loss on drying measures water plus anything else volatile. Two people can both be
right about the same lot. That reframed Q1 from a vocabulary question into a method question — and it
remains a hypothesis for Marisol Vega to rule on, not something I am qualified to settle.

**Why retest and expiry are different claims.** A retest date says "re-examine by then"; an expiry
date says "this is finished." The ERP conflates them and Purchasing reorders off the result. I would
have mapped one to the other without noticing.

In each case AI gave me the reasoning and the section reference, and I read the section. **That is
the only reason I would defend these in a room with Marisol** — not because AI said so.

---

## Where it executed work I then verified

Governance scaffold, the deterministic parser, the SPEC-7 rules, `reference/policy.json`, 62 tests,
seven ADRs, the analysis documents, the deployment plan, the handover package.

**How I verified it, in descending order of how much I trust each:**

1. **Independent prediction, then comparison.** Before any rules were written, the expected outcome
   was worked out by hand from the corpus: 22 accept, 14 hold, with specific documents named. The
   implementation produced exactly that, document for document. **This is the strongest evidence in
   the repo and it is still weak** — both routes to that answer were produced by the same
   collaboration, so it shows consistency, not correctness.
2. **Gates that caught real defects.** The CVE audit found `pytest` PYSEC-2026-1845 on first run. The
   complexity ceiling forced a refactor of `decide()` rather than a suppression. A test caught a rule
   ordering defect. These are the checks working on their author, which is the point of having them.
3. **Reading the output.** Checking that COA-0027's ppb→ppm conversion is recorded, that COA-0035's
   inferred date names the certificates it was inferred from, that COA-0034 is read from the
   convention the document states for itself.
4. **Reading all 36 certificates myself.** Slower than everything above and the source of most of the
   corrections below.

---

## What it got wrong

**1. It miscounted the anomaly rate and I published the wrong number.** AI stated "roughly 12 of 36,
33%" — counted by eye. The real figure is **18 of 36, exactly half**. It had been written into the
question register, into `STATUS.md`, and into a note drafted to Denis Achebe, which understated the
finding to the client. It was only caught when the count was re-derived mechanically before building.

*The lesson is not "AI is bad at arithmetic."* It is that a plausible-sounding number stated
confidently propagates into three documents before anyone checks it. Now enumerated in code.

**2. It designed the domain model before reading the data properly.** Two defects, both found by
reading the corpus against code that had already been written:
- `Certificate.stated_conformance` was a single document-level flag. Certificates state PASS **per
  attribute**, and SPEC-7 §5 turns on a per-result contradiction — so the flag was in the wrong place
  to express the rule it existed for.
- `Measurement` had nowhere to record the original value and unit, so SPEC-7 §2's "the conversion
  shall be recorded" could not be satisfied by the model at all.

Both were designed from the *specification* and not from the *documents*. Reading the corpus earlier
would have caught both in minutes.

**3. Its first parser was badly broken, and the failure was loud only by luck of design.** First run
produced 34 holds instead of 14 — a regex for the method name allowed runs of spaces and swallowed
entire table rows. It was obvious because the design makes an unread field *absent* rather than
guessed. A parser built the other way would have produced confident wrong numbers and looked fine.

**4. A patch it applied silently did nothing.** It edited a file by matching an exact string that a
formatter had since reflowed. The edit reported success and changed nothing; the bug persisted
through another test cycle. This is the exact failure mode the repo's own skill documentation warns
about, and it still happened.

**5. It gitignored a required deliverable.** `decisions.jsonl` was added to `.gitignore` on the
reasonable-sounding grounds that it is derived output. It is also deliverable #5. A locally correct
principle applied without checking it against the brief.

**6. Its own quality gate had a blind spot, twice.** `make placeholders` passed while
`REPO-SURFACE.yaml` still read as unfilled template text, and again while the README carried 32
unfilled blocks — including the entire Deployment section, which is a deliverable. Each time the gate
only caught the markers it had been taught. A gate you have not watched fail is one you are trusting.

**7. It chose a threshold that admits the case it wanted.** ADR-0006 resolves ambiguous dates from a
supplier's other certificates when there are **≥3** agreeing examples. The one supplier this admits
has exactly 3. That is close to circular, it is load-bearing for exactly one document, and **it is
written into the ADR as a known weakness** — which is the right response, but I would rather it had
not needed one. This is the decision I expect to be challenged on and the one I would concede first.

---

## What I would do differently

**Read the source documents before designing anything.** Three of the seven errors above trace to
building from the specification and the field maps without having read all 36 certificates. That
reading took under an hour and would have prevented all three.

**Ask "what is missing?" before "build it."** Three times in this engagement, a sweep before
implementation caught things the build would have cemented: the domain-model defects, the fact that
three of six deliverables did not exist, and a tech-stack decision (deterministic parser vs LLM) that
had never actually been made despite three prior commitments constraining it. Every one of those
sweeps was cheap. None was volunteered.

**Treat confident output as a draft, especially numbers.** The corrections above were not caught by
disagreeing with AI's reasoning — the reasoning was usually fine. They were caught by re-deriving a
figure, running the thing, or reading the source.

---

## What AI was not used for

- **Deciding anything that was Thornbury's to decide.** Twenty-one questions are recorded unanswered
  in `docs/open-questions.md`; three are explicitly declined in `docs/working-answers.md`. Where a
  ruling was needed to proceed, it is provisional, owned by a named person, and reversible as a data
  change.
- **Generating the certificates or any client data.** Everything analysed is the supplied corpus.
- **Producing an accuracy number.** There is no labelled set, so there is no measurement, and no
  quality claim appears anywhere in this repo.
