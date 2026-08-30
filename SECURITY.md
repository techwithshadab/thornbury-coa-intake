# Security

## Reporting an issue

Report a suspected vulnerability to the **solutioner of record** (see `engine.yaml`) and the
**tech lead**, by email, and do not open a public issue for it. If neither responds within two working
days, escalate to the **delivery lead**. Acknowledgement target: two working days.

## What this repo holds

- **No credentials.** No secret is used today. When an LLM enters the extraction loop it brings an API
  key: it is sourced from a secrets manager or injected environment at runtime, never committed — not in
  code, not in a tracked `.env`. `gitleaks` runs on every commit via `.pre-commit-config.yaml`.
- **Client documents.** `reference/source/` holds vendored copies of Thornbury's SPEC-7 and supplier
  master, classified `confidential` in `engine.yaml`. Certificates themselves are **not** committed; they
  are a runtime input.
- **An open question, not a control.** Whether certificate text may leave Thornbury's boundary — to a
  hosted model, for instance — has not been asked or answered. It is a client decision and it blocks the
  B4 security-conformance gate. See `STATUS.md`.

## Dependencies

`make audit` runs `pip-audit` over the frozen lockfile and is part of `make check`. Dependencies are
hash-pinned in `uv.lock` and installed frozen; the gate's own tools (`ruff`, `pytest`, `pip-audit`) are
pinned exactly, and `ruff` is kept identical to the `rev:` in `.pre-commit-config.yaml`.
