# Engineering + governance ritual for a project repo on the engine rails. POLYGLOT core:
# it keeps every governance target (setup, check, size, status, new-adr, new-record, log, gate-check,
# handover-check) and adds the engineering targets (lint, test). `make check` is the whole ritual:
# hygiene + size + lint + test. Wire LINT/TEST/SETUP_STACK to your stack (examples below). If the
# scaffold-template Makefile changes, re-sync the governance targets. (Universal core: one owned command set.)

SHELL := /bin/bash

# --- Wire these to your stack (the ONLY language-specific lines) ----------------------------------------
# Python:  SETUP_STACK := python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
#          LINT := .venv/bin/ruff check . ;  TEST := .venv/bin/pytest -q
# Node:    SETUP_STACK := npm ci ;  LINT := npm run lint ;  TEST := npm test
# Go:      SETUP_STACK := go mod download ;  LINT := golangci-lint run ;  TEST := go test ./...
# Rust:    SETUP_STACK := cargo fetch --locked ;  LINT := cargo clippy -- -D warnings ;  TEST := cargo test
# NOTE ON `LINT`: assign it with the `origin` guard below (or `:=`), NEVER `?=`. GNU make ships a
# BUILT-IN `LINT = lint` feeding the built-in LINT.c suffix rule, and `?=` only assigns when a
# variable is UNDEFINED — a builtin counts as defined. `LINT ?= ...` is therefore a silent no-op:
# LINT stays `lint` and `make check` dies with "lint: No such file or directory", which points at
# nothing useful. SETUP_STACK and TEST are not builtins, so `?=` is correct for them.
SETUP_STACK ?= uv sync --frozen --extra dev
TEST        ?= uv run --frozen pytest
# Keeps `?=` semantics (an env or command-line LINT still wins) while actually taking effect.
# Replace the body with your linter; keep the ifeq wrapper.
ifeq ($(origin LINT),default)
LINT        := uv run --frozen ruff check . && uv run --frozen ruff format --check .
endif
# -------------------------------------------------------------------------------------------------------

PRECOMMIT := pre-commit
.DEFAULT_GOAL := help

help: ## Show the available tools
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install toolchain (frozen/locked) + pre-commit hooks (run once)
	@$(SETUP_STACK)
	@command -v $(PRECOMMIT) >/dev/null 2>&1 && $(PRECOMMIT) install || echo "↪ install pre-commit for hooks"
	@echo "✓ on the rails — run 'make check' anytime"

check: ## The whole ritual: hygiene (gitleaks/format) + size guard + lint + test
	@if command -v $(PRECOMMIT) >/dev/null 2>&1; then \
		$(PRECOMMIT) run --all-files || { echo "✗ hygiene gate failed — fix it, do not skip it"; exit 1; }; \
	else \
		echo "✗ pre-commit is not installed — the hygiene gate (secret scan, size, format) did NOT run."; \
		echo "  Run 'make setup'. A gate that skips itself is worse than no gate: it reports green."; \
		exit 1; \
	fi
	@$(MAKE) --no-print-directory size
	@$(MAKE) --no-print-directory placeholders
	@$(MAKE) --no-print-directory freshness
	@$(MAKE) --no-print-directory lint
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory audit

# The canonical files a scaffolded repo starts with, each shipping placeholder text. Template text
# left in place is worse than a missing file: it reads as filled, so a reader skips it — and no
# linter objects, because a placeholder is valid Markdown. Add paths as your repo grows.
PLACEHOLDER_PATHS ?= README.md CLAUDE.md STATUS.md docs/overview.md REPO-SURFACE.yaml $(wildcard pyproject.toml package.json)

placeholders: ## Report template text still unfilled in the canonical files (STRICT=1 to fail on it)
	@hits=$$(grep -nEH '\[repo name\]|\[Repository Name\]|\[repo_kind\]|\[list\]|\[add as you grow|\[add yours as you hit them\]|\[the single canonical path\]|\[the ones set true\]|One-line description of what this repo does|\[Describe what this repository does|Replace me|^# Pack: |<upcoming milestone|<risk or blocker>|<one-line rationale>' $(PLACEHOLDER_PATHS) 2>/dev/null || true); \
	if [ -z "$$hits" ]; then echo "✓ no template placeholders left"; \
	elif [ -n "$(STRICT)" ]; then echo "✗ template placeholders still unfilled:"; echo "$$hits"; exit 1; \
	else echo "↪ template placeholders still unfilled (warning — 'make placeholders STRICT=1' to fail on these):"; echo "$$hits"; fi
# Warn, don't fail, by default: a freshly scaffolded repo is SUPPOSED to be full of these on day one,
# and a `check` that is red at commit zero teaches people to ignore it. Run it STRICT before you call
# the repo stood up, and again before handover — checklist row 3.1 is exactly this check with teeth.

reference: ## Derive reference/*.json from the controlled sources in reference/source/
	@uv run --frozen python tools/derive_reference.py

freshness: ## Fail if the committed derived reference data is stale (generated_code surface)
	@uv run --frozen python tools/derive_reference.py --check

audit: ## Dependency CVE gate (handles_secrets / external_network surfaces)
	@uv run --frozen pip-audit --skip-editable --progress-spinner off
# `--skip-editable` skips this project itself, which is not on PyPI and has no feed to check against.
# NOT `--strict`: strict escalates any SKIP to a failure, and that one skip is unavoidable — it would
# make the gate permanently red for a reason that is not a vulnerability, which is how gates get
# disabled. pip-audit still exits non-zero on an actual finding, which is the gate's job.

run: ## Run the pipeline:  make run DOCS=<dir> [OUT=decisions.jsonl]
	@test -n "$(DOCS)" || { echo 'usage: make run DOCS=<documents dir> [OUT=decisions.jsonl]'; exit 1; }
	@uv run --frozen coa-intake --documents "$(DOCS)" --reference reference --out "$(or $(OUT),decisions.jsonl)"

lint: ## Static check over the codebase (wire LINT)
	@$(LINT)

test: ## Run the test suite, incl. your invariant test(s) (wire TEST)
	@$(TEST)

size: ## Fail if any tracked file is unusually large (data/binaries don't belong in git)
	@big=$$(git ls-files | while read f; do \
		[ -f "$$f" ] && sz=$$(du -k "$$f" | cut -f1) && [ "$$sz" -gt 5120 ] && echo "$$f ($$sz KB)"; done); \
	if [ -n "$$big" ]; then echo "✗ oversized files tracked:"; echo "$$big"; exit 1; \
	else echo "✓ no oversized files"; fi

status: ## Print the current STATUS.md
	@cat STATUS.md 2>/dev/null || echo "no STATUS.md yet — initialize it from the scaffold"

new-adr: ## Scaffold the next ADR:  make new-adr title="use X for Y"
	@test -n "$(title)" || { echo 'usage: make new-adr title="use X for Y"'; exit 1; }
	@mkdir -p decisions; \
	n=$$(printf "%04d" $$(( $$(ls decisions/[0-9]*-*.md 2>/dev/null | wc -l | tr -d ' ') + 1 ))); \
	slug=$$(echo "$(title)" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-'); \
	f="decisions/$$n-$$slug.md"; \
	printf -- '---\nid: ADR-%s\ntitle: %s\nstatus: Proposed\ndate: %s\ncategory: other\ndeciders: [solutioner-of-record, tech-lead]\nsupersedes: none\ntags: []\n---\n\n# ADR-%s: %s\n\n## Context\n<!-- What forces the decision? Which categorical trigger? -->\n\n## Decision\n<!-- What we chose, active voice. One decision per record. -->\n\n## Consequences\n- **Good:**\n- **Cost:**\n- **Watch:**\n\n## Options considered\n- \n' \
		"$$n" "$(title)" "$$(date +%F)" "$$n" "$(title)" > "$$f"; \
	echo "✓ created $$f (Proposed — write it before you build; the solutioner reviews via CODEOWNERS)"

new-record: ## Scaffold a review record:  make new-record gate=exit-package project="Name"
	@test -n "$(gate)" || { echo 'usage: make new-record gate=<exit-package|milestone|conformance|handover-readiness> [project="..."]'; exit 1; }
	@mkdir -p reviews; \
	d=$$(date +%F); f="reviews/$$d-$(gate).md"; \
	[ -e "$$f" ] && { echo "exists: $$f (rename or add a suffix)"; exit 1; } || true; \
	printf -- '---\nrecord_type: gate-record\ngate: %s\ninstance_overlay: none\nproject: %s\ndate: %s\noutcome: conditional   # pass | conditional | fail\nartifacts_reviewed: []\nreviewers: []\nfollowups: []\n---\n\n# Gate record — %s — %s\n\n**What was reviewed:** \n**Against which bar:** <link the exit-package success criteria; never restate a new bar>\n**Outcome:** <pass | conditional | fail> — <one-line rationale>\n\n## Findings\n\n## Conditions (if conditional)\n\n## Follow-ups\n| Item | Owner (role / name) | Due | Status |\n|---|---|---|---|\n| | | YYYY-MM-DD | open |\n\n## Sign-offs\n| Role | Name / seat | Decision | Date |\n|---|---|---|---|\n| | | accept | |\n' \
		"$(gate)" "$(project)" "$$d" "$(gate)" "$(project)" > "$$f"; \
	echo "✓ created $$f (fill it — the RECEIVER signs, not the producer)"

log: ## Append a change-log row:  make log m="what changed" [type=decision owner="role" ref=ADR-1]
	@test -n "$(m)" || { echo 'usage: make log m="what changed/decided" [type=decision owner="role" ref=...]'; exit 1; }
	@t="$(type)"; t=$${t:-decision}; \
	printf -- '| %s | %s | %s | %s | %s |\n' "$$(date +%F)" "$$t" "$(m)" "$(owner)" "$(ref)" >> CHANGELOG.md; \
	echo "✓ appended to CHANGELOG.md ($$t)"

gate-check: ## Where the exit-package gate lives
	@echo "Exit-package gate → docs/exit-package-gate.md  (receivers PM + TL accept; DL countersigns; file the record in reviews/)"

handover-check: ## Where the handover readiness checklist lives
	@echo "Handover readiness → the 5-role checklist, linked from the exit package §4 M5 — keep its items green as you build"

.PHONY: help setup check placeholders reference freshness audit run lint test size status new-adr new-record log gate-check handover-check
