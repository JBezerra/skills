---
name: resolve-conflicts
description: Walk through git merge, rebase, or cherry-pick conflicts one at a time, briefing each one and applying only the resolution the user approves.
argument-hint: "[path | PR URL]"
disable-model-invocation: true
---

# Resolve conflicts

Walk the conflicts **one at a time**. Trivial ones get resolved on the spot. Every other one gets a plain-text brief and a suggested path, then waits for the user's approval before anything in it changes.

## Sides

Call the sides **we have** (the branch being worked on) and **coming** (the incoming change), never ours/theirs, because git flips those during a rebase:

| Operation | we have | coming |
|---|---|---|
| merge, cherry-pick | `ours`, stage `:2:` | `theirs`, stage `:3:` |
| rebase | `theirs`, stage `:3:` (the user's commit being replayed) | `ours`, stage `:2:` (the upstream) |

Establish the operation from `git status` before reading any hunk.

## Steps

1. **Inventory.** When `$ARGUMENTS` is a PR URL and no operation is in progress, check out the PR's head branch, pull it, and merge its base branch (`origin/<base>`) into it to surface the conflicts. Never push. Find the conflicted files (`git diff --name-only --diff-filter=U`), limited to `$ARGUMENTS` when a path is given. Show the operation, what's coming (branch or commit), and the files with their conflict counts.
2. **Per conflict**, in file order:
   1. **Understand.** Read the base (`git show :1:<path>`), both sides, and the commits behind each side's change to that region (`git log --oneline --merge -- <path>` for a merge, the commit being replayed for a rebase or cherry-pick). Know what each side changed relative to the base, and why, before judging.
   2. **Classify.**
      - **Trivial**: imports, formatting, independent additions, one side a superset of the other, or one side a pure rename or move that the other's edit replays onto.
      - **Judgment call**: everything else. Both sides changed the same behavior, one side deletes what the other edits, or the combination builds but changes semantics.
   3. **Trivial: resolve right away**, without asking. Say in one line what was done. Reconcile a file's imports last, once its real resolutions are in, so they match the final code.
   4. **Judgment call: brief in plain text, then stop.** Never use `AskUserQuestion`. The brief has:
      - **Incoming:** what coming changed and why.
      - **Ours:** what we have changed and why (cite the commit when it explains intent, e.g. a security fix).
      - **Suggested path:** the resolved code in a fenced block, plus any follow-up edits outside the hunk that it implies (imports, callers, now-unused code).
      - End with "Approve?" and wait. Present only one judgment call per message.
      - When several hunks in a file are the same clash (e.g. one rename colliding with one new param), brief them together as one decision.
   5. **Apply** exactly the approved resolution, leaving the rest of the file as is. When a file's last conflict is resolved, confirm no markers remain and `git add` it.
   6. **Watch for breaks outside the hunks.** When coming changes a contract (a signature, a required param, a moved export), grep for callers our side added and flag them in the brief, fixing them with that conflict or at wrap-up.
3. **Non-text conflicts** (delete/modify, rename, binary) go through the same brief and approval. Lockfiles and generated files get regenerated (take coming, then rerun `yarn install` or the generator) rather than merged by hand.
4. **Wrap up.** With nothing unmerged:
   - Run the repo's build or typecheck to catch resolutions that merge textually but not semantically.
   - Run the tests for every touched area, including tests our side added that coming's contract changes may break. Update those tests to the new contract without weakening what they prove.
   - Run the formatter and linter on the touched files.
   - Report what changed beyond the conflict hunks. Continuing the operation (`git rebase --continue`, `git merge --continue`, `git cherry-pick --continue`) waits for the user's go. When a rebase stops on the next commit with new conflicts, start again from step 1.
