#!/usr/bin/env python3
"""Engine git rails — layer 4: the agent guard.

Layers 1-3 fire at commit and push. The commands that destroy the most work
never reach either, because git provides no hook for them and never will:

    git reset --hard    git checkout .    git clean -fd    git stash drop

A PreToolUse hook sees the command string BEFORE it runs. It is the only
interception point that exists for that class. It also catches --no-verify,
which walks past layers 1-3 entirely.

THREE VERDICTS, not two:

  deny              force-push to a protected branch, --no-verify, remote
                    branch deletion. No legitimate agent use.

  require-snapshot  the destroyers, and ONLY when there is actually something
                    to lose. Denied once with an instruction to run `git panic`
                    and retry; allowed on the retry. The command still works —
                    it just stops being able to lose anything. This is the
                    point of the layer.

  allow             everything else, untouched.

AUDIENCE: stderr from a PreToolUse hook goes to the MODEL, not the human. Every
message here is therefore an instruction to an agent — imperative, naming the
exact command to run next. That is the opposite of the layers 1-3 voice, which
teaches a person. Do not blur the two.

SCOPE, honestly: this covers commands an agent runs inside Claude Code. A human
in their own terminal is covered by layers 1-3 only. An agent that writes a
shell script and executes that goes around it. It is a strong speed bump on the
common case, not a sandbox.

Exit 2 + stderr = deny. Exit 0 = allow.
"""

import json
import re
import subprocess
import sys
import time

# A snapshot counts as "for this action" if it was taken within this window.
SNAPSHOT_WINDOW_SECONDS = 300

PROTECTED_FALLBACK = ["main", "master", "release/*"]


def git(*args, cwd=None):
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True,
                             timeout=5, cwd=cwd)
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def protected_globs():
    cfg = git("config", "--get", "rails.protected")
    return cfg.split() if cfg else PROTECTED_FALLBACK


def is_protected(branch):
    if not branch:
        return True  # cannot tell which branch — assume the risky answer
    import fnmatch
    return any(fnmatch.fnmatch(branch, p) for p in protected_globs())


def current_branch():
    return git("symbolic-ref", "--quiet", "--short", "HEAD")


def has_uncommitted_work():
    """True if a destroyer would actually destroy something.

    The whole friction budget of this layer rests here: on a clean tree,
    `git reset --hard` removes nothing, so demanding a snapshot first would be
    pure noise and would train the agent to treat the guard as an obstacle.
    """
    return bool(git("status", "--porcelain"))


def fresh_snapshot():
    """True if `git panic` ran recently enough to cover this action."""
    refs = git("for-each-ref", "--format=%(committerdate:unix)", "refs/rails/panic")
    if not refs:
        return False
    try:
        newest = max(int(line) for line in refs.splitlines() if line.strip())
    except ValueError:
        return False
    return (time.time() - newest) < SNAPSHOT_WINDOW_SECONDS


def push_target_branch(command):
    """Best-effort: which branch is this push aimed at.

    `git push --force origin my-branch` -> my-branch
    `git push --force`                  -> the current branch
    Anything unparseable falls through to the current branch, and is_protected()
    treats an unknown branch as protected.
    """
    tokens = [t for t in command.split() if not t.startswith("-")]
    if "push" in tokens:
        after = tokens[tokens.index("push") + 1:]
        if len(after) >= 2:
            return after[1].split(":")[-1]
    return current_branch()


# --- rule set ---------------------------------------------------------------

FORCE_PUSH = re.compile(r"\bgit\b[^|;&]*\bpush\b[^|;&]*(--force\b|--force-with-lease|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\s)")
NO_VERIFY = re.compile(r"\bgit\b[^|;&]*\b(push|commit)\b[^|;&]*--no-verify")
DELETE_REMOTE = re.compile(r"\bgit\b[^|;&]*\bpush\b[^|;&]*(\s--delete\b|\s:\S)")

DESTROYERS = [
    (re.compile(r"\bgit\b[^|;&]*\breset\b[^|;&]*--hard"), "git reset --hard"),
    (re.compile(r"\bgit\b[^|;&]*\bcheckout\b[^|;&]*(\s--\s+\.|\s\.\s*$)"), "git checkout ."),
    (re.compile(r"\bgit\b[^|;&]*\brestore\b(?![^|;&]*--staged)[^|;&]*(\s--\s+\.|\s\.\s*$|--worktree)"), "git restore ."),
    (re.compile(r"\bgit\b[^|;&]*\bclean\b[^|;&]*\s-[a-zA-Z]*f"), "git clean -f"),
    (re.compile(r"\bgit\b[^|;&]*\bstash\b[^|;&]*\b(drop|clear)\b"), "git stash drop/clear"),
]


def deny(message):
    sys.stderr.write(message.strip() + "\n")
    return 2


def evaluate(command):
    # --- deny ---------------------------------------------------------------
    if NO_VERIFY.search(command):
        return deny("""
BLOCKED: --no-verify bypasses this repo's git rails (secret scan, size ceiling,
force-push and history protection).

Do not retry with --no-verify. Fix whatever the hook reported instead. If a hook
is genuinely wrong, edit it in .githooks/ so the fix is reviewable, or hand the
command to the user to run themselves.
""")

    if DELETE_REMOTE.search(command):
        return deny("""
BLOCKED: deleting a remote branch.

Branch deletion is not reversible from here and may cut other people's work
adrift. Ask the user to do it in the host UI, where it is logged and undoable.
""")

    if FORCE_PUSH.search(command):
        branch = push_target_branch(command)
        if is_protected(branch):
            return deny(f"""
BLOCKED: force-push to protected branch '{branch}'.

A non-fast-forward push deletes commits that exist only on the remote — someone
else's work. This is never the right fix for a rejected push.

Do this instead:
    git panic
    git pull --rebase origin {branch}
    git push

If the rebase conflicts, resolve it, or `git rebase --abort` and report back.
Do not retry with --force.
""")

    # --- require-snapshot ---------------------------------------------------
    for pattern, name in DESTROYERS:
        if pattern.search(command):
            if not has_uncommitted_work():
                return 0  # nothing to lose — no reason to add friction
            if fresh_snapshot():
                return 0  # already recoverable — proceed
            return deny(f"""
BLOCKED ONCE: `{name}` would permanently destroy uncommitted work in this repo.

Git keeps no copy of uncommitted changes, so this is not recoverable afterwards
by any means — not reflog, not fsck.

Run this first, then retry the exact same command and it will be allowed:
    git panic

`git panic` snapshots tracked, staged and untracked state to refs/rails/ and
leaves the working tree byte-identical. It changes nothing and takes a moment.
""")

    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0
    try:
        return evaluate(command)
    except Exception:
        # A guard that crashes must not become a guard that blocks all work.
        return 0


if __name__ == "__main__":
    sys.exit(main())
