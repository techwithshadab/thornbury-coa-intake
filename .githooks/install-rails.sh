#!/usr/bin/env bash
# Engine git rails — installer.
#
#   .githooks/install-rails.sh            install (idempotent — safe to re-run)
#   .githooks/install-rails.sh --check    verify only; non-zero if not installed
#
# Everything it writes is repo-LOCAL. It never touches the user's global git
# config, so it cannot disturb work in any other repo, and uninstalling is just
# deleting the repo.
#
# Run automatically by the scaffolder when a repo is created. Must be re-run
# once after a fresh clone, because core.hooksPath and config live in
# .git/config, which git deliberately does not transmit — a repo cannot be
# allowed to execute code on someone's machine just because they cloned it.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

MODE="${1:-install}"
CHECK=0; [ "$MODE" = "--check" ] && CHECK=1

_G=$'\033[32m'; _R=$'\033[31m'; _Y=$'\033[33m'; _B=$'\033[1m'; _0=$'\033[0m'
[ -t 1 ] || { _G=''; _R=''; _Y=''; _B=''; _0=''; }

FAILED=0
ok()   { printf '  %s %s\n' "${_G}ok${_0}" "$1"; }
miss() { printf '  %s %s\n' "${_R}--${_0}" "$1"; FAILED=1; }

GITVER="$(git --version | sed 's/[^0-9.]*//; s/ .*//')"
ver_ge() {  # ver_ge 2.37 -> true if installed git >= 2.37
    printf '%s\n%s\n' "$1" "$GITVER" | sort -V -C
}

# --- repo -------------------------------------------------------------------
if [ ! -d .git ]; then
    if [ "$CHECK" -eq 1 ]; then echo "not a git repository" >&2; exit 1; fi
    git init -b main >/dev/null 2>&1 || git init >/dev/null
    printf '%s\n' "${_B}initialised a git repository${_0}"
fi

want() {  # want <key> <value> [min-git-version]
    local key="$1" val="$2" min="${3:-}"
    if [ -n "$min" ] && ! ver_ge "$min"; then
        printf '  %s %s (needs git >= %s, you have %s)\n' "${_Y}skip${_0}" "$key" "$min" "$GITVER"
        return 0
    fi
    if [ "$(git config --local --get "$key" 2>/dev/null)" = "$val" ]; then
        ok "$key = $val"
    elif [ "$CHECK" -eq 1 ]; then
        miss "$key should be $val"
    else
        git config --local "$key" "$val" && ok "$key = $val"
    fi
}

printf '\n%s\n' "${_B}git rails — layer 1: safe defaults${_0}"

# Hooks live in the tracked .githooks/ dir, so they are reviewable and versioned
# rather than hidden in .git/hooks where nobody ever looks at them.
want core.hooksPath .githooks 2.9

# `git pull` on a diverged branch is where most confusion starts: the default
# silently creates a merge commit. ff-only refuses and says so, and `git sync`
# then explains the choice. Aborting is recoverable; a surprise merge is not obvious.
want pull.ff only

# Pushing a new branch without "fatal: no upstream branch" — a pure papercut
# that teaches nothing and wastes everyone's first ten minutes.
want push.autoSetupRemote true 2.37
want push.default simple

# Deleted remote branches stop lingering as ghosts in tab-completion.
want fetch.prune true

# zdiff3 shows the ORIGINAL text alongside both sides of a conflict. Resolving
# a conflict without it is guesswork.
if ver_ge 2.35; then want merge.conflictStyle zdiff3 2.35; else want merge.conflictStyle diff3; fi

# Remember how a conflict was resolved, so the same one is not solved twice.
want rerere.enabled true

# Show the diff in the commit-message editor — the cheapest possible nudge
# toward a message that describes what actually changed.
want commit.verbose true 2.9

want branch.sort -committerdate 2.19
want diff.colorMoved zebra 2.15

# --- tunables ---------------------------------------------------------------
printf '\n%s\n' "${_B}rails tunables${_0} (override per repo; see .githooks/lib.sh)"
[ -z "$(git config --local --get rails.protected)" ] && [ "$CHECK" -eq 0 ] && git config --local rails.protected 'main master release/*'
[ -z "$(git config --local --get rails.maxblobmb)" ] && [ "$CHECK" -eq 0 ] && git config --local rails.maxblobmb 5
[ -z "$(git config --local --get rails.enforce)"   ] && [ "$CHECK" -eq 0 ] && git config --local rails.enforce on
[ -z "$(git config --local --get rails.branchflow)" ] && [ "$CHECK" -eq 0 ] && git config --local rails.branchflow on
for k in rails.protected rails.maxblobmb rails.enforce rails.branchflow; do
    v="$(git config --local --get "$k")"
    [ -n "$v" ] && ok "$k = $v" || miss "$k unset"
done

# --- layer 2: hooks ---------------------------------------------------------
printf '\n%s\n' "${_B}layer 2: hooks${_0}"
for h in pre-commit commit-msg pre-push post-checkout; do
    if [ ! -f ".githooks/$h" ]; then miss "$h missing"; continue; fi
    if [ ! -x ".githooks/$h" ]; then
        if [ "$CHECK" -eq 1 ]; then miss "$h not executable"; else chmod +x ".githooks/$h" && ok "$h"; fi
    else ok "$h"; fi
done
[ -x .githooks/bin/rails ] || { [ "$CHECK" -eq 1 ] && miss "bin/rails not executable" || chmod +x .githooks/bin/rails; }

# --- layer 3: aliases -------------------------------------------------------
printf '\n%s\n' "${_B}layer 3: safe commands${_0}"
# Relative to .git/config, which is where the include is read from.
INC="../.githooks/aliases.gitconfig"
if git config --local --get-all include.path 2>/dev/null | grep -qxF "$INC"; then
    ok "aliases included"
elif [ "$CHECK" -eq 1 ]; then
    miss "aliases not included"
else
    git config --local --add include.path "$INC" && ok "aliases included"
fi
for a in sync panic undo oops nb where rescues; do
    git config --get "alias.$a" >/dev/null 2>&1 && ok "git $a" || miss "git $a"
done

# --- layer 4: agent guard ---------------------------------------------------
# Nothing to install — Claude Code reads .claude/settings.json from the repo.
# Reported so `--check` covers all four layers.
printf '\n%s\n' "${_B}layer 4: agent guard${_0}"
if [ -f .claude/hooks/git-agent-guard.py ] && [ -f .claude/settings.json ]; then
    if command -v python3 >/dev/null 2>&1; then
        ok "PreToolUse guard present (blocks reset --hard / clean -fd on unsaved work)"
    else
        printf '  %s %s\n' "${_Y}warn${_0}" "guard present but python3 not on PATH — it will no-op"
    fi
else
    miss ".claude/hooks/git-agent-guard.py or .claude/settings.json missing"
fi

# --- result -----------------------------------------------------------------
if [ "$CHECK" -eq 1 ]; then
    if [ "$FAILED" -ne 0 ]; then
        printf '\n%s\n' "${_R}${_B}git rails are NOT fully installed.${_0}  Run: .githooks/install-rails.sh"
        exit 1
    fi
    printf '\n%s\n' "${_G}${_B}git rails installed.${_0}"
    exit 0
fi

cat <<EOF

${_B}Rails installed.${_0} Seven commands worth knowing — each is safer than what it replaces:

  ${_B}git where${_0}    where am I, what is uncommitted, am I ahead or behind
  ${_B}git sync${_0}     instead of 'git pull' — never surprises you mid-rebase
  ${_B}git panic${_0}    snapshot everything, change nothing. Press before anything scary
  ${_B}git undo${_0}     undo the last commit, keep the work
  ${_B}git oops${_0}     "I lost something" — finds it
  ${_B}git nb <name>${_0} new branch from an up-to-date base
  ${_B}git rescues${_0}  list what 'git panic' saved

Stuck on something git did? ${_B}RECOVERY.md${_0} in this repo.

${_Y}After a fresh clone, re-run:${_0} .githooks/install-rails.sh
(git never transmits hook config — that would let any repo run code on your machine.)
EOF
