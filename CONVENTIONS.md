# Repository conventions

The standards this repo starts inside (brief §5). They are instantiated by solutioning, not adopted mid-flight —
so execution begins on the rails. This file ships with the scaffold; keep it as the repo's standards reference.

## The axioms — what every standard here serves

1. **COMPLIANT PATH = CHEAPEST PATH** — doing the right thing is the easiest thing; guardrails by tooling, not policing.
2. **NO ARTIFACT, NO REVIEW** — a review with no written record didn't happen.
3. **THE RECEIVER ACCEPTS** — handover is accepted by the receiving side, never self-certified.
4. **ROLES, NOT PEOPLE** — accountability attaches to roles, all of them; nobody is unreviewed.
5. **DIAGNOSE BEFORE PRESCRIBING** — surface current practice before mandating tooling.
6. **EVERY ELEMENT SHIPS WITH ITS TOOL** — or an explicitly accepted manual cost.

## Folder layout

| Path | What lives here |
|------|-----------------|
| `README.md` | Type-tagged front page. Fill every required section for the repo type — no TODO placeholders. |
| `docs/` | Blueprint / PRD / architecture / setup / runbook. |
| `decisions/` | Append-only ADRs — numbered `NNNN-title.md`, supersession only. |
| `reviews/` | Gate and conformance records ("no artifact, no review"). |
| `STATUS.md` | Current state — feeds the WBR pre-read and the conformance review. |
| `CHANGELOG.md` | Append-only change / decision / commitment log. |
| `CODEOWNERS` | Review routing (decisions path → solutioner-of-record). |
| `.gitignore` · `.pre-commit-config.yaml` | Hygiene rails — secrets, file size, lint, format. |
| `TOOLKIT.md` | The helpers available in this project (`make` targets + the deliverable tools). |

## Mainline protection (the controls — set them however your host enforces them)

These are **controls, not a host's feature names**: they hold on GitHub, GitLab, Azure DevOps, or a bare /
air-gapped / no-remote git host (where they degrade to discipline + the reader tools + human ratification —
the Dynapar C1 exit-package example; ADR-0022). Set them when the repo gets a remote:

- Protect the mainline (`main`): **no history rewrite (no force-push), no deletion.**
- **Require a reviewed PR before merge; PR author ≠ approver** (separation of duties — nobody signs sole-authored work, brief §8).
- Require the hygiene / CI check (pre-commit + `make check`) to pass before merge.
- Require the `decisions/`-path reviewer (the solutioner-of-record) — routed by `CODEOWNERS`.

**Per-host cheat-sheet — the same four controls, by host feature name.** The engine is host-neutral by
construction (ADR-0022); pick your column:

| Control | GitHub | GitLab | Azure DevOps |
|---|---|---|---|
| No rewrite / no delete of mainline | Branch ruleset (block force-push + deletion) | Protected branch | REQUIRED branch policy + a `Force Push` **Deny** (or branch lock); also Deny "Bypass policies…" for Contributors + the build service |
| Reviewed PR, author ≠ approver | Required PR review + "require review from someone other than the author" | Merge-request approvals (author cannot approve) | "Require a minimum number of reviewers" with **creator-vote-counts off** + block-most-recent-pusher approval |
| Hygiene / CI check passes | Required status check | MR pipeline succeeds | **Build-validation** branch policy on `azure-pipelines.yml` |
| `decisions/`-path reviewer | `CODEOWNERS` + "require review from Code Owners" — read natively, no generator (see `packs/host/github/`) | `CODEOWNERS` | "Automatically included reviewers" policy **generated from `CODEOWNERS`** — ADO has no CODEOWNERS file (see `packs/host/azure-devops/`) |

On a host with no server-side enforcement (bare / air-gapped / no-remote), these degrade to **detective**
controls — `repo-health` reads the canonical files and the pre-commit hooks flag violations — plus human
ratification. The compliant path still holds; only the enforcement altitude drops (ADR-0022, the C1 floor).

## Decision discipline (brief §8)

- **Write an ADR _before_ implementation** for any categorical trigger: a new external dependency/service · a new data store or schema change beyond the blueprint · a new API surface · a deployment topology change · a new cross-cutting pattern (auth, eventing, caching).
- Accepted ADRs are **immutable except the status field** (supersession only — never edit the body).
- Ambiguity or deviation goes to the **change log and the pull path**, not into a workaround.

## Judgment vs. determinism (who decides vs. what writes)

Two different things, kept separate on purpose:

- **Role-holders supply judgment** — does this gate pass? is this ADR right? is the work accepted? A human in a named role decides, and is checked by another role (the receiver accepts; PR author ≠ approver).
- **Small, tested helpers mutate canonical state** — appending an ADR, logging a change-log row, scaffolding a gate/review record (`make new-adr`, `make new-record`, `make log`). A helper that writes the entry can't fat-finger the machine-readable format a later tool (the conformance pre-reader, the WBR assembler) depends on.

Never invert these: a script must not *decide* a gate outcome, and a human should not hand-format a record a tool will parse. This is "every element ships with its tool" (A6) with a sharp edge — the tool guards the format; the human owns the call.
