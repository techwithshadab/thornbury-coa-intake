# Glossary — the ubiquitous language of this engagement

Terms whose meaning is contested, system-specific, or easy to get subtly wrong. Vocabulary is not
decoration here: two of the engagement's hardest open questions are vocabulary disputes wearing a
technical costume.

**Where a term is disputed, this file records the dispute rather than resolving it.** Resolving it is
Thornbury's job — see `open-questions.md`.

## Contested — do not treat these as settled

| Term | What it means here | The dispute |
|---|---|---|
| **retest date** | The date by which material should be **re-examined**. Stated on the certificate. | **Not the same as an expiry date**, though the ERP stores it in `expiry_date` and Purchasing reorders off the result. Denis Achebe has never been comfortable with the conflation. Q14, unowned. |
| **expiry_date** | An ERP field. Required; the ERP will not save a lot without it. | Holds a retest date today. What it *should* hold is Purchasing's decision, not ours. Ruling R14 preserves current practice deliberately rather than fixing it. |
| **moisture** / **water content** | We treat them as the same **attribute**, never merged across **method**. | Denis has been told by two people that they are and are not the same. SPEC-7 §3.2 suggests both are right and the disagreement is really about method. A hypothesis for Marisol Vega, not a ruling. Q1. |
| **conforms** | QA's tracker column: `Y` / `N` / `QUERY`. | `QUERY` (~3% of rows) means the analyst could not tell from the certificate alone. The outcome usually ends up in the free-text `note`, not the column — so the column understates how often judgement was needed. |

## System-specific

| Term | Meaning |
|---|---|
| **accept** | Our decision that a certificate can be processed automatically. **It is not a release.** The lot is still created at the ERP's default `held` and a person releases it (ADR-0004). |
| **hold** | A conclusion, not a failure: a human must look. Carries a reason and a **route**. |
| **route** | Which of four desks a held lot goes to: `quality`, `procurement`, `supplier_query`, `intake_keying` (ADR-0005). |
| **`intake_keying`** | A hold meaning *we could not read the document*. Nothing is wrong with the lot; it returns to the manual process that handles 100% of volume today, so it is **not new work**. |
| **reportable method** | The method SPEC-7 §2 names for an attribute. A result from any other method is **indicative** and cannot release a lot (§3.1) — so the method is part of whether a number counts at all, not metadata about it. |
| **indicative** | SPEC-7's term for a result that may be recorded for information but not used for acceptance. Loss on drying (M-03) for moisture is the case that occurs in the corpus. |
| **withdrawn revision** | A superseded revision of SPEC-7. A certificate citing one is referred to Quality (§4). Rev C was withdrawn on 2026-03-01. |
| **derived reference data** | `reference/spec-7.json`, `supplier-master.json` — computed from `reference/source/` by `tools/derive_reference.py`. Do not hand-edit. |
| **policy** | `reference/policy.json` — the **provisional rulings** we made on Thornbury's behalf. Hand-authored, each with a named owner. |
| **provenance** | On a `Measurement`: attribute, value, canonical unit, source locator, method, and the original value/unit where a conversion happened (SPEC-7 §2 requires the conversion be *recorded*). |
| **inferred** (of a date) | Resolved from a supplier's *other* certificates, not read from this one. Stamped as an inference with its evidence (ADR-0006), so a reviewer sees a claim rather than a reading. |

## Thornbury systems and people

| Term | Meaning |
|---|---|
| **SPEC-7** | Thornbury's ingredient acceptance specification. Revision D, effective 2026-03-01. Owned by Quality. The authority on whether a lot is acceptable. |
| **the ERP** | Aldon 7. System of record for the lot record. Owned by Supply Operations; integration surface owned by IT. Cannot store a manufacture date, an analytical method, or a unit conversion. |
| **the QA tracker** | Quality's own spreadsheet, ~14,000 rows over four years. Records the method, which the ERP cannot. Its `note` column is the closest thing to a labelled history of human decisions. |
| **the supplier master** | The approved-supplier list. The ERP will not create a lot for a supplier not on it. Three suppliers in the sample are not on it (Q15). |
| **lot / batch** | The same thing. The ERP says `lot_id`, the QA tracker says `batch`, certificates say both. |
| **material_no / item code** | Thornbury's item code (`MAL-505`). Three letters, three digits — distinct from a lot number, which carries four. |
