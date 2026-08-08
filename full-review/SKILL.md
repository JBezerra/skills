---
name: full-review
description: >
  Run three independent reviews of one pull request in parallel — Anthropic's /code-review at
  high effort, the personal /pr-review TL review, and browser-driven /uat-pr — and merge them
  into a single digest, with the two code-review digests rewritten in ASD-STE100 Simplified
  Technical English. Checks out the PR branch, pulls the latest, and preflights the local API
  (:1337) and web app (:3000) first. Use whenever the user asks for a full review, a complete
  review, "review this PR every way", "run all the reviews", "code review + UAT", or says
  "/full-review". Not for a single review pass — use /pr-review, /uat-pr, or /code-review
  directly for those.
---

# full-review

One PR, three reviewers, one digest. You are the orchestrator: you resolve the target, prepare the
environment, fan out to three subagents, and merge what comes back. You do **not** review the code
yourself, you do **not** fix anything, and you do **not** post anything to GitHub.

The three reviewers are deliberately independent — they must not see each other's output. Their
disagreement is signal.

| Subagent | Skill it invokes | Looks at |
| --- | --- | --- |
| `code-review` | `code-review` (built-in, Anthropic) at `high` | The diff: correctness bugs, reuse, simplification, efficiency |
| `tl-review` | `personal-skills:pr-review` | The diff against the Jira AC, in José's TL voice |
| `uat` | `personal-skills:uat-pr` | The running app in a browser, plus MongoDB |

## Phase 0 — resolve the target

Argument is a PR URL, a bare PR number, or nothing. With nothing, infer from the current branch:

```
gh pr view --json number,title,url,headRefName,baseRefName,headRefOid,body
```

No PR found → say so and stop. `/pr-review` and `/uat-pr` both need a PR; only `/code-review` works
on a bare branch. Offer to run that one alone rather than guessing.

## Phase 1 — check out the branch and sync

Skip the checkout only when `git rev-parse --abbrev-ref HEAD` already equals the PR's `headRefName`.

1. `git status --porcelain` — anything uncommitted → stop and say what is dirty. Never stash, never
   discard, never commit on the user's behalf.
2. `git fetch origin`
3. `git checkout <headRefName>` (only if not already on it)
4. `git pull --ff-only origin <headRefName>` — a non-fast-forward means the local branch diverged;
   stop and report it instead of merging or rebasing.
5. Confirm `git rev-parse HEAD` matches the PR's `headRefOid`. Report the SHA in the digest.

## Phase 2 — preflight the local environment

**`curl` to localhost is blocked by the sandbox and always returns `000`.** Probe the listener
instead:

```
lsof -nP -iTCP:1337 -sTCP:LISTEN
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

To confirm a listening port actually answers, re-run `curl -s -o /dev/null -w '%{http_code}' -m 8
http://localhost:PORT/` with `dangerouslyDisableSandbox: true`. **Any** HTTP status counts as
healthy — the API answers `404` on `/` because every route is prefixed. Only a connection failure
(`000` outside the sandbox) means down.

**API on :1337 down** → wait 40 seconds (`Monitor`, or a background `sleep 40` — foreground `sleep`
is blocked), then probe once more. Still down after the wait → treat it as down and continue to the
next check; the branch was just checked out, so the API is probably still restarting and may come up
before the UAT agent needs it.

**Web on :3000 down** → tell the user plainly that they have to spin it up (`yarn start` in `web/`,
or their usual command), then **run the two static reviews without UAT**. Do not wait, do not start
services yourself. The digest carries a `not run` UAT section stating exactly why.

**API down but web up** → same handling: run the two static reviews, skip UAT, say the API was not
listening on :1337 after the 40-second wait.

## Phase 3 — fan out

Spawn every applicable subagent **in a single message** so they run concurrently, `subagent_type:
"general-purpose"`, `run_in_background: true`. Do not run any review yourself while they work, and do
not touch the browser — the UAT agent owns that session.

Give each one the resolved PR number/URL, the head SHA, and the base branch. Tell each agent
explicitly: **its final message is the only thing the orchestrator sees**, so it must contain the
complete findings, not a pointer to them or a summary of them.

**`code-review` agent**

> Invoke the Skill tool with `skill: "code-review"` and `args: "high <PR number>"`. Do not pass
> `--comment` or `--fix`, and do not edit any file. When the skill reports findings, repeat every
> finding in your final message as a list: severity/category, `file:line`, the one-sentence defect,
> and the concrete failure scenario. Preserve exact symbol names, paths, and line numbers. If it
> finds nothing, say "no findings" and give the effort level it ran at.

**`tl-review` agent**

> Invoke the Skill tool with `skill: "personal-skills:pr-review"` and `args: "<PR URL>"`. Do not post
> anything to GitHub — the report is the deliverable. Return the skill's full output verbatim:
> the Verdict line and its rationale, and every `**blocker:**`, `**suggestion:**`, and
> `**question:**` exactly as written.

**`uat` agent** (only when :3000 answered)

> Invoke the Skill tool with `skill: "personal-skills:uat-pr"` and `args: "<PR URL>"`. Run it end to
> end **without pausing for plan approval** — the orchestrator approves the plan on the user's
> behalf, so go straight from Phase 2 into Phase 3. Everything else in that skill still holds: the
> branch is already checked out and the app is already running, so never check out a branch and never
> start or stop a service. Return the full Phase 4 report: flows exercised, blockers with their
> reproductions, the complete checklist table, other confirmed issues, what was not reproducible
> locally, and whether the fixture restore succeeded. Include the plan file path.

If a subagent dies or comes back empty, say so in its digest section. Never invent its findings, and
never fill the gap with your own review.

## Phase 4 — the digest

Wait for every spawned agent. Then write one report, in this order.

The **UAT section keeps its native voice** — it is an observation log and rewording it loses the
exact strings it observed. The **two code-review sections are rewritten in ASD-STE100 Simplified
Technical English**; read `references/ste.md` before writing them.

`````
# Full review — PR #<N> <title>
<branch> @ <short sha> · base <base> · <date> · reviewers run: <which of the three>

## 1. UAT
<uat-pr Phase 4 report, verbatim: flows exercised, blockers, checklist table, other issues,
not reproducible locally, fixture restore. Plan file: <path>>

## 2. Code review — /code-review high
<findings, ASD-STE100. One finding per bullet: `file:line` — what is wrong — what happens.>

## 3. TL review — /pr-review
<verdict, ASD-STE100. Then blockers, suggestions, questions, each ASD-STE100, each keeping its
**blocker:** / **suggestion:** / **question:** label.>

## Agreement
<Only findings that two or more reviewers hit independently, one line each, naming who found it.
Nothing overlaps → say "no overlap between the three reviewers." Omit this section when only one
reviewer ran.>
`````

Rules for the digest:

- **Merge nothing.** Each section holds only what its own agent returned. A finding that appears
  twice appears twice, and once more under Agreement.
- **Keep every anchor.** ASD-STE100 rewrites prose, never `file:line`, symbol names, quoted strings,
  AC quotes, or stored document shapes.
- **Drop no findings.** Simplification is about language, not about triage.
- **Skipped sections stay visible**, marked `not run`, with the reason (`web app on :3000 was not
  listening`).
- Post nothing to GitHub. Apply no fix. If the user wants either, they ask for it after reading the
  digest.
