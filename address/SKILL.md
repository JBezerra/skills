---
name: address
description: Fix what a GitHub review comment points out. Fetches the comment, checks out the PR branch (or a worktree), aligns on the solution, implements it, and stops for review before committing.
argument-hint: "<comment URL...> [worktree] [solution]"
disable-model-invocation: true
---

# Address a review comment

Input: `$ARGUMENTS`, one or more GitHub comment URLs, optionally `worktree` and the solution the user wants. Address one comment at a time, each through every step, one commit per comment.

## Steps

1. **Fetch.** Pick the API from the URL fragment:
   - `#discussion_r<id>`, a review comment: `gh api repos/<owner>/<repo>/pulls/comments/<id>` (body, `path`, `line`, `diff_hunk`, `commit_id`). Read the rest of its thread too (replies carry `in_reply_to_id`).
   - `#issuecomment-<id>`, a conversation comment: `gh api repos/<owner>/<repo>/issues/comments/<id>`.
   - `#pullrequestreview-<id>`, a whole review: `gh api repos/<owner>/<repo>/pulls/<n>/reviews/<id>` plus `.../reviews/<id>/comments`, each comment addressed on its own.

   Then the PR: `gh pr view <n> --json headRefName,baseRefName,title,body`. Done when you can state in one sentence what the reviewer wants.
2. **Check out.** By default, the PR's head branch in the current tree: a dirty tree stops here with a question; otherwise fetch, check out, and fast-forward to the remote. With `worktree`: `git worktree add .claude/worktrees/<branch-slug> <headRefName>` (reuse it when it exists), then `EnterWorktree` with its `path`, and run the repo's setup (install, build) before any checks.
3. **Locate.** Find the commented code at the branch tip; when it moved since `commit_id`, relocate it with `diff_hunk`. Read enough around it to judge the comment. When the branch has a Jira key and `/Users/josebezerra/source/@specs/<repo>/<KEY>/design.md` exists, check whether the comment contradicts a decision there and say so.
4. **Align.** When the user gave the solution, restate it in one line and go on. Otherwise explore what the fix touches (targeted reads; one subagent when it's broader, e.g. other callers or the same pattern elsewhere in the PR), then brief the user: what the reviewer is asking, and whether it holds (agree, or disagree with evidence). Offer the options via `AskUserQuestion`, recommended first, each with a `preview` of the change. A comment that doesn't hold is a valid outcome; offer a reply instead of a fix. Wait for the user's pick.
5. **Implement.** The working tree is the **baseline**: build on what's there, including the user's own edits. Implement exactly the agreed fix; when it needs something beyond that, stop and agree it first. Run the repo's tests and quality checks for what changed until they pass.
6. **Hand back.** Report files changed, how the change answers the comment, and check results. Stop. The user reviews and may edit; their version is what gets committed.
7. **Commit on approval.** Read the full diff; when it changed since hand-back, rerun the checks and stop on failure. Stage by path, write the message with the `caveman-commit` skill adjusted to the repo's commit conventions (the repo wins), and commit. Then offer each of these, each waiting on the user's go: push, reply on the thread with what changed (show the draft first), resolve the thread.
