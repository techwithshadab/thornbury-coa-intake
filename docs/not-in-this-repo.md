# What's NOT in this repo

Kept short on purpose: the full list lives in the **"What's NOT in this repo"** section of
[`../README.md`](../README.md), which is where a new reader actually looks. Two copies of the same
list is how both stop being true.

The short version — none of these exist here, and each is deliberate:

- **The certificates.** Client documents and a runtime input; never committed.
- **OCR / PDF extraction.** Out of scope (ADR-0003). The seam is `extraction.Extractor`.
- **The ERP integration.** No client for the lot-creation endpoint. Blocked on Q14 and Q16, which is
  why stages 1–2 of [`deployment.md`](deployment.md) do not need it.
- **A review queue or UI.** Held lots reach people as file rows.
- **A labelled evaluation set.** Does not exist anywhere yet, and it is the highest-value missing
  artifact in the engagement.
- **Anything for the other document types** (packing lists, allergen declarations). The seam and the
  policy-as-data shape were chosen partly with them in mind, but nothing here has been designed
  against a second document type and it should not be claimed that it has.

**Supersedes / superseded by:** nothing. First repo of this engagement.
