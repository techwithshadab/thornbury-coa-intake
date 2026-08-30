# Derived reference data — why `reference/*.json` is generated

## The rule

The acceptance limits, the reportable methods, and the approved-supplier set are **facts that already
exist** in documents Thornbury controls. A hand-kept copy of a fact has nothing comparing it to its
source, so it rots the moment the source moves and never says so. So: `tools/derive_reference.py`
computes them, and **the script is the reviewed thing**. `reference/*.json` is output. Do not hand-edit
it; run `make reference`.

This is the surface teams most often miss, because derived data does not look generated. It looks like
config.

## The three checks, and what each one actually proves

**1. Freshness — `make freshness` (`--check`).** Regenerates from `reference/source/` and compares. It
proves the committed file matches what the generator produces *today*.

**2. Correctness — `tests/test_derivation.py`.** ⚠ **Freshness is not correctness.** `--check` compares
generator output to generator output. If the parse rule is wrong, the committed file is wrong in exactly
the same way, the diff is empty, and the gate goes green. It is a *staleness* detector.

So correctness is established separately, two ways:

- The parse rule is asserted against hand-written expectations — including the **negative cases**: table
  separators, headers, two-column metadata rows, prose, a single limit where a range is required. A
  parser that is too eager invents an acceptance criterion, and an invented limit is how a system accepts
  a lot it should have held. It also refuses inverted limits rather than silently swapping them, and
  refuses to emit a spec with no revision or no criteria — an empty limits table compares every result
  against nothing.
- `test_committed_reference_matches_the_source_by_a_second_route` re-reads the controlled source **by a
  different route than the generator does** — it does not parse the table at all, it asserts each
  committed attribute appears verbatim in the source alongside its own limits. Two implementations
  agreeing is weak evidence when one calls the other, and strong evidence when they were written
  separately.

**3. The gate has been watched to fail — `test_the_freshness_gate_has_been_watched_to_fail`.** It
corrupts the committed artifact and asserts `--check` goes red. A detective control nobody has seen fire
is one you are trusting, not one you have tested.

## The part that is not solved

`reference/source/` holds **copies** of controlled documents. SPEC-7 §3.3 requires a controlled
notification to *suppliers* on a method change; nothing covers downstream systems. Until that has an
owner, a SPEC-7 revision leaves this repo confidently asserting a withdrawn rule — which is exactly the
failure SPEC-7 §4 exists to catch. Recorded in `reference/source/PROVENANCE.md` and `STATUS.md`.
