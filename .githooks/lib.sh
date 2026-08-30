#!/usr/bin/env bash
# Shared helpers for the engine git rails.
#
# Sourced by every hook. Holds the house style for messages, the tunables, and
# the protected-branch test — so a hook file contains only its own rule.
#
# TUNABLES (all per-repo `git config`, set by install-rails.sh, override freely):
#   rails.protected   space-separated branch globs that must never be rewritten
#   rails.maxblobmb   megabyte ceiling for any single committed file
#   rails.enforce     on | warn-only   — warn-only downgrades every hard block
#   rails.branchflow  on | off — whether committing straight to a protected
#                     branch is worth warning about. Separate from rails.protected
#                     on purpose: a solo or docs repo still wants force-push
#                     protection, but committing to main there is the normal way
#                     to work, and a warning on every single commit is how people
#                     learn to ignore warnings.
#
# House style, and the reason this layer exists at all:
#   A block that only says "no" teaches one lesson — how to use --no-verify.
#   Every refusal here has to name the command that gets the person unstuck.
#   `die` therefore takes a recovery line and will not let you omit it.

# shellcheck disable=SC2034

if [ -t 2 ]; then
    _R=$'\033[31m'; _Y=$'\033[33m'; _C=$'\033[36m'; _B=$'\033[1m'; _0=$'\033[0m'
else
    _R=''; _Y=''; _C=''; _B=''; _0=''
fi

rails_cfg() { git config --get "$1" 2>/dev/null || printf '%s' "$2"; }

RAILS_PROTECTED="$(rails_cfg rails.protected 'main master release/*')"
RAILS_MAXBLOBMB="$(rails_cfg rails.maxblobmb 5)"
RAILS_ENFORCE="$(rails_cfg rails.enforce on)"
RAILS_BRANCHFLOW="$(rails_cfg rails.branchflow on)"

# warn — the default posture. Says what happened, says what to do, proceeds.
warn() {
    printf '%s\n' "${_Y}${_B}warn:${_0}${_Y} $1${_0}" >&2
    shift
    for line in "$@"; do printf '      %s\n' "$line" >&2; done
    printf '\n' >&2
}

# die — reserved for damage that is unrecoverable or lands on other people.
# $1 = what happened, $2 = why it matters, rest = the way out.
die() {
    local what="$1" why="$2"; shift 2
    printf '%s\n' "${_R}${_B}blocked:${_0}${_R} ${what}${_0}" >&2
    printf '  %s\n\n' "$why" >&2
    printf '%s\n' "  ${_B}To get unstuck:${_0}" >&2
    for line in "$@"; do printf '    %s\n' "$line" >&2; done
    printf '\n  %s\n' "${_C}Full recovery guide: RECOVERY.md${_0}" >&2
    if [ "$RAILS_ENFORCE" = "warn-only" ]; then
        printf '  %s\n\n' "${_Y}rails.enforce=warn-only — allowing anyway.${_0}" >&2
        return 0
    fi
    exit 1
}

info() { printf '%s\n' "${_C}$1${_0}" >&2; }

# Current branch name, or the literal "HEAD" when detached.
#
# Deliberately NOT `git rev-parse --abbrev-ref HEAD`: on a branch with no commits
# yet that prints "HEAD" to stdout *and* exits non-zero, so the usual
# `|| echo HEAD` fallback fires too and you get "HEAD\nHEAD". symbolic-ref
# reports the real branch name before the first commit and fails cleanly when
# detached, which is what both callers actually want.
current_branch() {
    git symbolic-ref --quiet --short HEAD 2>/dev/null || printf 'HEAD'
}

# True if $1 matches any glob in rails.protected.
is_protected() {
    local branch="$1" pat
    for pat in $RAILS_PROTECTED; do
        # shellcheck disable=SC2254
        case "$branch" in $pat) return 0 ;; esac
    done
    return 1
}

# Human-readable size for a byte count, without depending on numfmt (absent on macOS).
human_size() { awk -v b="$1" 'BEGIN{ printf (b>=1048576) ? "%.1f MB" : "%.0f KB", (b>=1048576)? b/1048576 : b/1024 }'; }
