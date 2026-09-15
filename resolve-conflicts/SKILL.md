---
name: resolve-conflicts
description: Walk through git merge, rebase, or cherry-pick conflicts one at a time, briefing each one and applying only the resolution the user approves.
argument-hint: "[path]"
disable-model-invocation: true
---

# Resolve conflicts

Walk the conflicts **one at a time**. Each one gets a brief, a suggested path, and the user's approval before anything in it changes.

## Sides

Call the sides **we have** (the branch being worked on) and **coming** (the incoming change), never ours/theirs, because git flips those during a rebase:

| Operation | we have | coming |
|---|---|---|
| merge, cherry-pick | `ours`, stage `:2:` | `theirs`, stage `:3:` |
| rebase | `theirs`, stage `:3:` (the user's commit being replayed) | `ours`, stage `:2:` (the upstream) |

Establish the operation from `git status` before reading any hunk.

## Steps

1. **Inventory.** Find the conflicted files (`git diff --name-only --diff-filter=U`), limited to `$ARGUMENTS` when a path is given. Show the operation, what's coming (branch or commit), and the files with their conflict counts.
2. **Per conflict**, in file order:
   1. **Understand.** Read the base (`git show :1:<path>`), both sides, and the commits behind each side's change to that region (`git log --oneline --merge -- <path>` for a merge, the commit being replayed for a rebase or cherry-pick). Know what each side changed relative to the base, and why, before judging.
   2. **Brief** in 1–2 sentences: what's coming vs what we have.
   3. **Classify.** **Straightforward**: the sides compose without a judgment call (independent additions, one side a superset of the other, one side a pure rename, move, or format the other's edit replays onto). Everything else is a **judgment call**: both sides changed the same behavior, one side deletes what the other edits, or the combination builds but changes semantics.
   4. **Ask** via `AskUserQuestion`, one conflict per call. Straightforward: the suggested resolution first, suffixed `(Recommended)`, then "keep we have" and "take coming". Judgment call: state the choice the user has to make, then one option per viable resolution, recommending one only when the evidence supports it. Every option's `preview` shows the resolved code with a few lines of context.
   5. **Apply** exactly the approved resolution to that conflict, leaving the rest of the file as is. When a file's last conflict is resolved, confirm no markers remain and `git add` it.
3. **Non-text conflicts** (delete/modify, rename, binary) go through the same brief and ask. Lockfiles and generated files get regenerated (take coming, then rerun `yarn install` or the generator) rather than merged by hand.
4. **Wrap up.** With nothing unmerged, run the repo's build or typecheck to catch resolutions that merge textually but not semantically, and report. Continuing the operation (`git rebase --continue`, `git merge --continue`, `git cherry-pick --continue`) waits for the user's go. When a rebase stops on the next commit with new conflicts, start again from step 1.
