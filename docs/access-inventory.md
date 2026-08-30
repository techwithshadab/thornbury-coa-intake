# Access inventory — what this needs, and who grants it

<!--
  A HANDOVER HOME (exit-package gate row 5.2). Ships empty; fill it as you build.

  WHY THIS EXISTS. The single most common handover failure is not code the receiver
  can't read — it is a credential, a role, or an allowlist entry that only the departing
  team had. Every dependency below is something that can silently expire, be revoked,
  or be scoped to a person who is leaving. Name it while you still have it.

  ⚠️ NEVER PUT A SECRET IN THIS FILE. This is a committed artifact. Record WHERE a
  credential lives (the vault path, the secret name) and WHO grants it — never the value.
  A secret pasted here is a secret in git history forever.
-->

**Engagement:** `<slug>`  ·  **Maintained by:** the delivery lead  ·  **Updated:** YYYY-MM-DD

## What the system needs to run

| What | Kind | Where the credential lives | Granted by (role) | Expires | Breaks what if lost |
|---|---|---|---|---|---|
| `<system / API / data source>` | `<service account, API key, cert, DB role>` | `<vault path or secret name — NOT the value>` | `<role / team>` | `<date or "n/a">` | `<the concrete failure>` |

## What a human needs to work on this

| Access | Kind | Granted by (role) | Needed for |
|---|---|---|---|
| `<repo / environment / dashboard / tracker>` | `<read, write, admin>` | `<role / team>` | `<the task it unblocks>` |

## Owned by the client, not by us

<!-- The accesses that leave with the engagement, or that we never held. The receiver
     must know which doors we cannot open for them. -->

| Access | Whose | What to do when it's needed |
|---|---|---|
