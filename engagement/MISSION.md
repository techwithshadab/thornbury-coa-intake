# FDE Academy — Capstone

**Thornbury Ingredients · certificate-of-analysis intake**

You are the solutioner of record. Read the ask, the materials, and this brief, then deliver.

---

## The engagement

Thornbury Ingredients distributes specialty food ingredients. Every lot that arrives from a
supplier comes with a **Certificate of Analysis** — a document stating what was tested, by what
method, against what specification, and what the result was.

Thornbury receives several hundred a week across roughly forty suppliers. A two-person intake team
keys the values into the ERP by hand. QA separately maintains its own tracker of the same lots.

The sponsor's ask is in [`the-ask.md`](the-ask.md). Read it before anything else.

## What you have

| File | What it is |
|---|---|
| [`the-ask.md`](the-ask.md) | The sponsor's request, and a note from the intake team lead |
| [`documents/`](documents/) | 36 certificates, as text extractions. Real layout variety, real supplier variety |
| [`supplier-master.md`](supplier-master.md) | Thornbury's approved-supplier list. The ERP will not create a lot for a supplier that is not on it |
| [`erp-fields.md`](erp-fields.md) | The ERP's lot record — the fields it holds today |
| [`qa-tracker.md`](qa-tracker.md) | QA's tracker — the columns they maintain today |
| [`SPEC-7-revD.md`](SPEC-7-revD.md) | Thornbury's ingredient specification, current revision |
| [`org.md`](org.md) | Who is who, and who owns what |
| [`validate_submission.py`](validate_submission.py) | Checks the *shape* of your `decisions.jsonl`. Says nothing about whether your answers are right |

**The documents are unlabelled.** There is no answer key, and you will not be given one.

**On the documents.** They are supplied as extracted text. Thornbury receives PDFs; making OCR
production-grade is real work and it is **out of scope for this build**. Treat the extraction step
as a stub with a defined interface, and say what productionalising it would take.

## What you deliver

A repository containing:

1. **A working slice.** Runnable locally by someone who has only your README. Not a demo video, not
   a notebook of fragments — a thing that runs.
2. **A deployment plan that actually works.** Someone following it should be able to get this into
   production. If a step is unknown, say so and say how it gets known.
3. **Decision records** for the choices that were genuinely choices.
4. **A handover package** sufficient for a team that has never spoken to you to take this forward.
5. **`decisions.jsonl`** — your pipeline's output over the 36 documents. Format below.
6. **A working log** — a short account of how you used AI on this: where it acted as a thought
   partner, where you used it to learn a domain you are not expert in, and where it executed work
   you then verified. Name at least one thing it got wrong, or that you chose to overrule.

## The submission contract

`decisions.jsonl` — one JSON object per line, one line per document:

```json
{
  "doc_id": "COA-0001",
  "action": "accept",
  "fields": {
    "lot_id": "BRM-1234",
    "material_no": "CIT-100",
    "supplier": "Brightmoor Botanicals",
    "manufacture_date": "2026-10-25",
    "retest_date": "2028-10-25",
    "tests": [
      {"attribute": "Assay", "result": 100.2, "unit": "%", "method": "HPLC (SPEC-7 M-01)"},
      {"attribute": "Moisture", "result": 0.31, "unit": "%", "method": "Karl Fischer (SPEC-7 M-04)"}
    ]
  }
}
```

```json
{"doc_id": "COA-0002", "action": "hold", "hold_reason": "why a human needs to look at this"}
```

- `action` is `accept` or `hold`. Nothing else.
- `fields` is required on `accept`, optional on `hold`.
- `hold_reason` is required on `hold`. Write it for the person who has to act on it.
- On an `accept`, carry **one entry in `tests` for every attribute the specification lists**.
- **Dates must be unambiguous** — a reader must be able to tell what date you mean without
  being told which convention you used. Beyond that, how you write them is up to you.
- Field and attribute names are matched loosely: case, spacing and punctuation do not matter.
  What you *call* a thing is not being marked; what you *report* is.
- Emit a line for **every** document. A document you cannot process is a `hold`, not a silence.

**Your pipeline will be run against documents you have not seen.** The path to the documents
and to any reference data must be an input to your program, not a constant inside it.

[`validate_submission.py`](validate_submission.py) checks the shape of your file — that every
document has a line, that required fields are present, that dates parse. Run it before you
submit. It says nothing about whether your answers are right.

## How this is assessed

Two independent instruments, and you need both.

**The ledger.** Your three `decisions.jsonl` runs are scored against a set you have not seen, using
weights you have not been given. It rewards correctly automating a document, and it penalises **both**
kinds of mistake — accepting something you should not have, and holding something you did not need
to.

**The package.** Reframing, slice choice, decision quality, the handover, and how you handled what
you could not know. Scored by two reviewers independently.

Some things fail the capstone on their own, regardless of score. They come down to one thing:
**doing something that was not yours to do.** Not every hard question is one of them — a submission
that flags everything is failing differently, and it is just as visible.

## Scope and time

**Budget 12–16 hours.** If your engagement load makes that impossible (roughly 1 hour per working day), take the **core cut** — but
declare it **in writing before you start**, in your repo after getting permission from your instructors. Choosing scope deliberately and saying so
is a professional act and is scored as one. Discovering at the end that you ran out of time is not.

The core cut drops: any measured comparison between design options (assert your choice and mark it
unvalidated), any review interface beyond a queue file, and any query surface over the audit trail.

The core cut does **not** drop: the end-to-end path however thin, the choices you could not make
alone, your decision records, your slice justification, or the deployment plan. Those are the
capstone.

## Defending it

You will be asked to defend at least two of your decisions, and the reviewer will argue the other
side. The question is never whether you picked the option they would have picked. It is whether you
can show why yours holds — and whether you know what evidence would change your mind.

---

*The FDAIE Toolkit is not required. Though it would likely help you.*
