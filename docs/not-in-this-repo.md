# What's NOT in this repo

<!--
  A HANDOVER HOME (exit-package gate row 5.2). Ships empty; fill it as you build.

  WHY THIS EXISTS. A repo silently implies "this is the system." It never is. The
  receiver's worst day is discovering — in production, months later — that a step they
  assumed was here lives in someone's notebook, a scheduled job in another tenant, or a
  spreadsheet a business analyst maintains by hand.

  This file is the honest boundary. Everything the system DEPENDS ON but does not
  CONTAIN goes here. Writing "nothing — the repo is the whole system" is a valid entry
  ONLY if you have actually checked; it is the claim most often wrong.
-->

**Engagement:** `<slug>`  ·  **Maintained by:** the solutioner-of-record  ·  **Updated:** YYYY-MM-DD

## Lives elsewhere

| What | Where it actually lives | Who owns it | Why it isn't here |
|---|---|---|---|
| `<pipeline, model artifact, dashboard, scheduled job, mapping file>` | `<system / repo / tenant>` | `<role or team>` | `<the reason — client-owned, licensing, pre-existing, out of scope>` |

## Manual steps

<!-- Anything a HUMAN does that the system assumes has happened. Each one is a silent
     dependency and a handover risk. Name the human step and the role that performs it. -->

| The step | Who does it | How often | What breaks if skipped |
|---|---|---|---|

## Deliberately out of scope

<!-- Work discussed and consciously NOT done, with the decision that settled it. This
     stops the receiver from re-litigating a closed call, and stops it being read as an
     oversight. Cite the ADR or gate record. -->

| Not done | Decided in | Rationale |
|---|---|---|
| `<the thing>` | `<ADR-NNNN / reviews/…>` | `<why>` |
