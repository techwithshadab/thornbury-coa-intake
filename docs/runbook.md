# Runbook — how to operate this, cold

<!--
  A HANDOVER HOME (exit-package gate row 5.2). Ships empty; fill it as you build.

  THE BAR: a competent engineer who has never seen this repo can run it, diagnose it,
  and recover it FROM THIS FILE ALONE, without calling you. That is the receiver-accepts
  test — if a step only works because you know a trick, the trick belongs here.

  Write the commands verbatim. "Restart the service" is not a step; the exact command is.
-->

**Engagement:** `<slug>`  ·  **Owner:** `<role>`  ·  **Updated:** YYYY-MM-DD

## Run it locally

```bash
# exact commands, in order, from a fresh clone
```

## Run it for real

<!-- Where it runs, how a change reaches there, and how you know it worked. -->

## Health — is it actually working?

<!-- The specific check that answers "is it up AND correct", not just "is the process alive".
     Name the signal and the threshold. -->

## When it breaks

| Symptom (what someone reports) | Likely cause | What to do |
|---|---|---|
| `<the observable — an error string, a stuck queue, a wrong number>` | `<cause>` | `<the exact command / the escalation>` |

## Recovery

<!-- How to get back to a known-good state: the rollback command, the restore procedure,
     and what data (if any) is lost by doing it. State the data loss plainly. -->

## Escalation

<!-- Who to contact when the steps above do not resolve it — by ROLE, not by name
     (roles survive membership churn; names do not). -->
