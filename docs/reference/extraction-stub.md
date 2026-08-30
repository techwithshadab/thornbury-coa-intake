# The extraction stage — what it is today, and what productionalising it takes

## Today

`extraction.TextFileExtractor` reads pre-extracted `.txt` files from the documents directory, sorted by
`doc_id` so two runs produce the same order. That is the whole implementation. It exists behind the
`extraction.Extractor` protocol, so everything downstream is written against the seam and not against
text files.

Thornbury receives **PDFs**. Making OCR production-grade is real work and is explicitly out of scope for
this build. The seam is what makes that a scoping decision rather than a hole: swapping in a real
document pipeline is a change in this module and nowhere else.

## What productionalising it would take

**1. Getting to text at all.** Thornbury's certificates arrive as PDFs from ~40 suppliers. Some will be
digital-native with a real text layer; some will be scans. Those are different problems. A text-layer
extractor is close to free and close to exact; a scan needs OCR, and OCR on a table of numbers is where
the errors that matter live — a transposed digit in an assay result is a wrong number that looks right.
First job is to find out the split, which nobody has been asked.

**2. Layout, not just characters.** The 36 sample documents already show the variety Priya described:
different column orders, different labels for the same attribute, results and limits in the same cell,
methods sometimes in a column and sometimes in a footnote. Reading characters correctly and reading
*which attribute a number belongs to* correctly are separate failures, and the second is the dangerous
one because it produces a plausible number in the wrong field.

**3. Confidence that reaches the decision.** A production extractor must hand over per-field confidence,
not just values, and `RawExtraction` will need to carry it. A low-confidence assay result is a hold
reason. Today's text reader is exact by construction, so there is nothing to carry — which means this
interface is *known to be incomplete* and will change. That is a breaking change to `raw.py` and gets a
`CHANGELOG` entry and a `SCHEMA_VERSION` bump.

**4. A labelled set, before any of it.** No extractor change can be *measured* without one — only
asserted. See `STATUS.md`.

**5. The boundary question.** If extraction uses a hosted model, certificate text leaves Thornbury's
network. Nobody has been asked whether that is allowed. It is a client decision and it blocks go-live.

## What this does NOT need to be

Not perfect. The system has an explicit second answer: `hold`. An extractor that knows when it could not
read something, and says so, is worth more than one that is slightly more accurate and silent about the
difference.
