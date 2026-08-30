# Decisions (project ADR home — template)

In a real project repo, this is where architecture decision records live: one numbered file per decision, append-only, supersession only. Categorical triggers requiring an ADR *before* implementation (brief §8): new external dependency/service · new data store or schema change beyond blueprint · new API surface · deployment topology change · new cross-cutting pattern (auth, eventing, caching).

Enforced by branch protection + CI lint (no edits to accepted ADRs outside the status field) + CODEOWNERS routing changes here to the solutioner-of-record. The conformance pre-reader diffs this directory.

Kept empty in the template — it's the *home*, pre-created so proof has somewhere to live.
