# RECOVERY.md — get unstuck in git

Every block message in this repo points here. Find your situation, run the fix.

**The one thing to believe:** git almost never actually deletes a commit. If you
committed it, it is still there for at least 90 days, even when every branch and
every file says otherwise. Most "I lost a day's work" is really "I cannot see my
work," which is a different and much smaller problem.

The exception, and the only one that matters: **changes you never committed.**
Those are not in git at all, so git cannot give them back. That is what
`git panic` exists for.

---

## "I lost work"

```
git oops
```

Reads your history back in plain language and gives the exact command to return
to any earlier point. Start here — it covers most cases.

If the work was never committed, check your snapshots instead:

```
git rescues
git stash apply refs/rails/panic/<id>
```

Still nothing? Commits that belong to no branch survive anyway:

```
git fsck --lost-found
```

---

## "I ran `git reset --hard` and my changes are gone"

**Committed changes** — recoverable, always:

```
git oops                          # find the hash from before the reset
git switch -c recovered <hash>    # safest: puts it on a fresh branch
```

**Uncommitted changes** — only if you snapshotted. `git reset --hard` overwrites
the working tree, and git never had a copy. Check `git rescues`; if it is empty,
the work is genuinely gone.

This is why `git panic` exists and costs one word. Use it before anything that
feels risky.

---

## "git says my push was rejected"

```
! [rejected]  main -> main (non-fast-forward)
```

Someone pushed while you were working. Your history and theirs have split.

```
git panic                        # first, so nothing can go wrong
git pull --rebase origin main    # replay your work on top of theirs
git push
```

If the rebase gets messy at any point:

```
git rebase --abort               # everything back exactly as it was
```

**Do not use `--force`.** It makes the error message disappear by deleting the
other person's commits. The rails block it on protected branches for this reason.

---

## "I am in the middle of a rebase and I do not understand what is happening"

```
git rebase --abort
```

Puts everything back the way it was. It is always safe. Nothing is lost, and you
can try again — or ask someone — from a known state.

---

## "I committed a huge file"

Fix it **before pushing** and it costs a minute. After pushing it needs a history
rewrite that breaks every clone of the repo.

Not yet pushed, and it was the last commit:

```
git rm --cached path/to/big-file
echo 'path/to/big-file' >> .gitignore
git commit --amend --no-edit
```

Several commits back, still not pushed:

```
git rebase -i origin/main        # mark the offending commit 'edit', remove the file, continue
```

Already pushed: stop and get help. The tool is `git filter-repo`, and everyone
with a clone has to re-clone afterwards. Do not attempt it alone on a client repo.

---

## "I committed a secret"

Treat the secret as compromised the moment it was committed, even if you never
pushed and even after you delete it.

1. **Rotate the credential first.** Everything else is cleanup.
2. Remove it from the working tree and add its path to `.gitignore`.
3. If it was never pushed: `git rm --cached <file> && git commit --amend --no-edit`.
4. If it was pushed: tell whoever owns the credential. History rewriting is a
   secondary concern; the key is already out.

---

## "I committed to `main` and should not have"

Nothing is lost. Move the commit onto a branch:

```
git branch my-work               # bookmark the commit
git reset --keep HEAD~1          # main goes back one; your files stay
git switch my-work
```

---

## "I am on a DETACHED HEAD"

You are looking at a commit rather than standing on a branch. Commits made here
belong to nothing and vanish from view when you leave.

Keep what you did here:

```
git switch -c my-work
```

Just looking? Go back to where you were:

```
git switch -
```

---

## "I committed with the wrong name or email"

Last commit only:

```
git config user.email 'you@themathcompany.com'
git commit --amend --reset-author --no-edit
```

Already pushed, or several commits deep: leave it. Rewriting shared history to
fix attribution costs far more than the wrong attribution does. Fix the config so
the next ones are right.

---

## "I have no idea what state I am in"

```
git where
```

Branch, whether it is protected, your identity, how many files are uncommitted,
how far ahead or behind origin, and which remotes exist. One screen.

---

## Commands that can actually destroy work

Everything else in git is recoverable. These four are not, because they operate
on things git has no copy of:

| Command | Destroys |
|---|---|
| `git reset --hard` | uncommitted changes to tracked files |
| `git checkout .` / `git restore .` | uncommitted changes to tracked files |
| `git clean -fd` | untracked files entirely |
| `git stash drop` / `git stash clear` | the stash it names |

No hook can stop these — git provides no hook for them. `git panic` before any of
them, and they stop being able to hurt you.
