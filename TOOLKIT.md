# Project toolkit — helpers available to this project

The **compliant path is the cheapest path**: these helpers make doing it right the easy thing. This is the
project-facing list; the master registry of all engine tools is `tools/README.md` in the engine repo.

## Local — run in this repo

| Command | Does |
|---------|------|
| `make setup` | venv + pre-commit hooks (run once) |
| `make check` | hygiene gates — gitleaks, ruff, prettier, large-file guard |
| `make status` | print `STATUS.md` |
| `make new-adr title="…"` | scaffold the next numbered ADR — write it **before** you build (categorical triggers) |
| `make new-record gate=… project="…"` | scaffold a review record into `reviews/` (the receiver signs — no artifact, no review) |
| `make log m="…" [type=… owner=… ref=…]` | append a row to the append-only `CHANGELOG.md` (the change log / the pull) |
| `make gate-check` / `make handover-check` | where the exit-package / handover gates live |

## Deliverables — author once, render both forms, freeze for a send

Run via the engine toolkit (the scaffolder wires these in; until then, run from the engine repo pointing at
this project's files):

| Command | Does |
|---------|------|
| `deliverable-renderer/new.py "<Title>" --dir docs/` | scaffold a new deliverable `.md` |
| `deliverable-renderer/render.py <doc>.md` | one Markdown source → house-style HTML + Word `.docx` |
| `deliverable-renderer/freeze.py <file> --label <client>` | immutable, dated snapshot for a client send |
| `deliverable-renderer/send_index.py [root]` | the audit index of frozen client sends |

A deliverable can mark a form **hand-maintained** in its front-matter (`render: html`) so the renderer never
overwrites a hand-styled file — that file is the living document; freeze dated copies for sends (ADR-0005).

> New helpers land here as they're built — this is the project's copy of the toolkit (master: `tools/README.md`).
