# Access inventory — what this needs, and who grants it

**Today: nothing.** This repo needs no account, credential, network egress or licence to run. That is
worth recording rather than leaving blank — the reason the inventory is empty is a design choice
(ADR-0007: deterministic parsing, no model, no outbound call), not an omission.

`REPO-SURFACE.yaml` declares `handles_secrets` and `external_network` **false**, honestly.

## What a new joiner needs on day one

| Need | Granted by | Notes |
|---|---|---|
| The repo | — | **No remote exists yet.** This is the top handover finding (checklist 2.5); everything lives in one local clone |
| `git`, `make`, `uv` | Self-install | uv provisions the pinned interpreter; no other runtime needed |
| The certificate corpus | Thornbury Supply Operations | A runtime input, not part of the repo |

## What later stages will need — and who has not been asked yet

| Need | Stage | Owner | State |
|---|---|---|---|
| A host and scheduler for the batch | 2 | Thornbury IT | **Not asked.** Bundled with Q16 |
| Credentials for the ERP lot-creation endpoint | 3 | Thornbury IT | **Not asked.** `handles_secrets` flips true here; sourced from a secrets manager, never committed, rotation path in `SECURITY.md` |
| A decision on whether certificate content may leave the network | 4 | Priya + whoever owns security | **Not asked (Q19).** Gates whether a hosted model is even a candidate |
| Read access to the QA tracker's `note` column | any | Marisol Vega | **Not asked (Q5).** Needed for the eval set |
| A CI runner with a scoped token | now | Whoever hosts the remote | Workflow exists at `.github/workflows/check.yml`, pinned to commit SHAs, `contents: read` — and has never run |

**The pattern worth noticing:** every row in the second table is blocked on a question nobody has been
asked. That is the same finding as `open-questions.md`, seen from the access angle.
