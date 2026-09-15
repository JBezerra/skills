---
name: implement
description: Commit the task under review, then implement the next task from spec.md and stop for review. Runs after sdd:spec; each invocation advances one task.
argument-hint: "[commit | T-00N] [GS-XXXX]"
disable-model-invocation: true
---

# sdd:implement

Phase 4 of explore → design → spec → implement. Locate the work folder per `${CLAUDE_PLUGIN_ROOT}/work-folder.md`, which also defines the task status markers. Input: `$ARGUMENTS`.

Each invocation advances **one task**. Invoking it while a task is `[~]` is the user's approval of that task: commit it, then start the next. `commit` commits and stops; `T-00N` starts that task instead of the next `[ ]`.

The working tree is the **baseline**. Between invocations the user may edit, rename, or restructure what you wrote; their version is what gets committed and what you build on. When a user edit seems to conflict with a task's AC, ask.

## Steps

1. **Load.** Read `spec.md`. Proceed only when it says `Status: approved`; otherwise point the user to sdd:spec. Run `git status` and find the `[~]` task, if any.
2. **Branch.** Compare the current branch to the spec's `Branch:` line. On a mismatch with a clean tree, check out the base branch from the repo's conventions, pull, and create the branch (or check it out if it exists). On a mismatch with a dirty tree, stop and ask.
3. **Close the task under review.** Only when a task is `[~]`:
   - Dirty tree: read the full diff. When it differs from what you handed back, or you can't tell because this is a new session, rerun the task's quality checks and stop on failure. Stage the task's changes by path; ask before including changes unrelated to the task. Write the message with the `caveman-commit` skill, adjusted to the repo's commit conventions (the repo wins). Commit, then mark the task `[x] (<short sha>)`.
   - Clean tree: find the user's own commit for the task in `git log`, mark it `[x] (<sha>)`, and ask if there isn't one.
   - After `commit`, or when no `[ ]` task remains, report and stop. Once every task is `[x]`, suggest `create-pr`.
4. **Start the next task.** A dirty tree with no `[~]` task: stop and ask what it is. Otherwise take the first `[ ]` task (or the one named; warn when earlier tasks are still open). Announce its title and AC in chat, then read the files it touches as they are now. Implement exactly the task. When it needs something outside its scope, or an AC turns out wrong, stop and agree the change with the user, then update `spec.md` in place.
5. **Verify.** Run the task's tests and quality-check commands until they pass. Verify UI criteria in the browser when a browser tool is available; otherwise leave them unticked and say so. Tick each AC that holds.
6. **Hand back.** Mark the task `[~]` and report: files changed, AC status, any deviation from the spec. Stop. The user reviews, edits if they want, and invokes sdd:implement again to approve.
