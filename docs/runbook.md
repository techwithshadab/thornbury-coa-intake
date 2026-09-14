# Runbook — how to operate this, cold

**The bar:** a competent engineer who has never seen this repo can run it, diagnose it, and know when
to stop and ask. Nothing here assumes you have spoken to the author.

**Scope:** this is a batch CLI. Nothing is deployed, so there is no on-call, no dashboard and no
incident path. When stage 2 of [`deployment.md`](deployment.md) lands, this file grows a monitoring
section; until then, treating it as if it had one would be a lie.

## Run it

```bash
make setup                                     # once, per clone
make submission                                # the vendored corpus, three runs, validated
make run DOCS=/path/to/certificates OUT=decisions.jsonl   # any other corpus
```

Both paths are **inputs**. There is no default documents directory and there must never be one — this
pipeline is run against documents it has not seen.

## Check it is healthy

```bash
make check          # the whole ritual — must be green before you trust a run
make freshness      # is the derived reference data current?
```

Then read the run's own report: it prints `N decisions written`. **N must equal the number of `.txt`
files in the documents directory.** Fewer lines than documents is a defect, not a partial success —
every document gets a line by contract.

## When something goes wrong

| Symptom | What it means | What to do |
|---|---|---|
| `COA_WORKSPACE_ROOT is unset and no path was given` | Neither `--documents` nor the env var was supplied | Pass `--documents`. There is no default by design |
| `no .txt documents under <path>` | Wrong directory, or PDFs not text | This build does not read PDFs (ADR-0003). Point at the extraction output |
| `reference data missing: .../spec-7.json` | Derived data absent | `make reference` |
| `stale derived reference data` | `reference/source/` changed without regenerating | `make reference`, review the JSON diff, commit both |
| **`went past its review horizon`** | **The staleness gate refusing to run** | Working as designed (ruling R4). Re-vendor SPEC-7 from the QMS into `reference/source/`, `make reference`, move the dates in `policy.json`. **Confirm the revision with Quality first** |
| `WARNING: the vendored SPEC-7 copy passed its annual review date` | Approaching the above | Confirm rev D is still current. Do not just move the date |
| A whole supplier's lots suddenly hold with `unparseable` | That supplier changed their template | Expected failure mode (ADR-0007). Add a labelled pattern in `parse.py` **plus a test**. Do not add a best-effort fallback |
| `make check` red on the hygiene step | A pre-commit hook failed | Read the hook output. Do not `SKIP=` it — the gate failing loudly is the thing that was fixed |

## Changing what it decides

**Most behaviour changes belong in `reference/policy.json`, not in code.** Rule order, routes,
messages, unit conversions, attribute synonyms and supplier date conventions all live there. That is
deliberate: every ruling in it was made provisionally on Thornbury's behalf and has a named owner, so
overturning one must be a reviewed data change rather than an edit to a branch.

After any policy change: `make check`. `tests/test_policy_consistency.py` will catch a convention
below the evidence threshold, a duplicate rule order, a rule with no owner, or a convention for a
supplier the file says must never be inferred.

**Bump `domain.SCHEMA_VERSION`** if the shape of an emitted decision changes, and add a `CHANGELOG`
entry in the same commit.

## When to stop and ask

- The decision looks wrong and `policy.json` says it is right → that is a **ruling** you disagree
  with, not a bug. Take it to the owner named on the rule.
- You are about to make the parser guess at something → read ADR-0007 first.
- You are about to compute a missing retest date → read ruling R14 first. It is deliberate.
- You are about to give the system the ability to release a lot → read ADR-0004. That is a new
  decision needing its own record, not a config change.
