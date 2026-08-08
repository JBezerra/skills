---
name: uat-pr
description: >
  UAT a pull request against the running local app with agent-browser: build a real
  understanding of the feature from code + ticket + PR, write a scenario plan to
  ~/source/@specs, get it approved, execute it in the browser, verify every save in
  MongoDB, and report blockers and checklist gaps. Use whenever asked to UAT, manually
  test, or "try out" a PR or branch in the browser ("UAT this PR", "manually test
  GS-XXXXX", "test this branch in the app", "/uat-pr"). Not for unit tests, not for
  static code review, and not for MCP-tool testing (use gs:qa-mcp for that).
---

# uat-pr

Manual acceptance testing of a PR, driven through the real running app. You are the QA engineer, not the author: you find what is broken, you do not fix it.

## Golden rules

1. **Understand before you plan.** Jira ACs and PR test cases are *inputs*, not the checklist. The checklist is yours, derived from what the code actually does and what would make the feature wrong. Transcribing someone else's ACs and executing them is not a UAT.
2. **Test the app, not the code.** Every claim comes from an observation in the browser or in the database. Reading the diff tells you what to look for, never what happened.
3. **Verify persistence at the data layer.** After every save, read the document back from MongoDB via the mongodb MCP and record the actual stored shape. The UI showing a success toast is not evidence.
4. **Prove findings.** Before calling something a finding, produce the concrete observation: the badge text, the stored document, the message string, the empty container. No inference-only findings.
5. **Don't fix anything.** Not a typo, not a one-liner. This is UAT.
6. **Parallelize everything except the browser.** Context gathering, DB reads, and independent shell commands go out in one block. Browser interaction is one session with shared page state, so UI steps stay sequential and ordered.

## Phase 0 — target and preflight

Resolve the target: a PR URL or number if given, otherwise infer from the current branch (`gh pr view --json number,title,body,headRefName,url`).

Preflight in a single batched block, and **stop with a clear message if anything fails**:

- App is up (`curl -s -o /dev/null -w '%{http_code}' http://localhost:3000` works from the shell for a reachability check even though the sandbox blocks real API calls; if it doesn't, open the app in agent-browser instead).
- MongoDB MCP reachable (`connectionId: "preconfigured"`, list collections on the working DB).
- `git rev-parse --abbrev-ref HEAD` matches the PR's head ref, and the branch isn't behind its remote.

Never check out branches, never start or stop the user's services, never run migrations. If the environment isn't ready, say exactly what's missing and stop.

## Phase 1 — understand the feature

Fire the independent lookups in one block: Jira ticket, PR body, diff stat. Then read the touched source files in full, in parallel.

- **Jira** (`mcp__Jira__getJiraIssue`, `responseContentFormat: markdown`) when the branch or PR carries a `GS-XXXXX` key. Extract every stated AC verbatim; wording like "matches X **or** Y" is where builds deviate.
- **PR description**, which often carries test cases the ticket doesn't.
- **The diff**: `git diff --stat origin/develop...HEAD` (substitute the repo's base branch), then read the components it touches in full. You need the real labels, aria-labels, empty-state strings, validation messages, and the shape of what gets persisted, so you can assert on exact values rather than vibes.
- **Where the data lands**: collection, field, API payload shape. Every save gets verified there.

Do this in the main context. Do not delegate it to subagents: the nuance you extract here is what makes the plan good, and a summarized handoff is exactly what loses it.

You are done with Phase 1 when you can answer, without looking anything up: what does this feature do, what does the user get out of it, and what would make it wrong?

## Phase 2 — write the plan, then stop

Write the plan to `~/source/@specs/<repo-name>/GS-XXXXX-uat-<slug>.md`. No ticket key → `pr-<number>-uat-<slug>.md`. One file per UAT run; results get appended to it in Phase 4.

The plan opens with **"What this feature does / what would make it wrong"** in your own words, then a checklist with two clearly separated groups:

- **Stated** — ACs from the ticket and test cases from the PR, quoted.
- **Derived** — the checks *you* concluded matter that no source stated. If this group is empty, you have not finished Phase 1.

Then the scenarios. Always cover:

- **Happy path** end to end, through the final save.
- **Every checklist item** individually, including ones the diff doesn't appear to touch.
- **Empty and zero states**: no results, nothing selected, no upstream input, an entity with no data behind it.
- **Reverse flows**: back navigation, removing a prerequisite, re-entering, cancelling mid-way.
- **Races**: two rapid interactions before the first commits.
- **Data outside the default shape**: values missing from lookup tables, non-default locales or regions, records lacking optional fields.

And derive the categories specific to *this* feature. The generic list above is a floor, not the plan. Feature-shaped angles worth considering (only when they apply): what a displayed count is actually counting versus what its label claims; the same value reachable through two different parents, where keys and dedup break; whether an omitted field on save means "unchanged" or "deleted".

For each scenario write the steps, the expected result, and **where it gets verified** (UI string, stored document, or both).

**Then stop.** Show the plan and wait for the go-ahead before touching the browser.

## Phase 3 — execute

Read `references/browser-tactics.md` before the first browser call. Those are hard-won, and ignoring them produces false positives.

Login: `agent_browser_auth_list`, then `agent_browser_auth_login` with the saved profile. If no profile matches, stop and say which one is missing. Never type credentials, never ask the user for a password, never try the login form manually.

Fixtures: seeding edge cases by writing directly to MongoDB is allowed, but **snapshot the original document into the plan file first**, reload the page to pick up the change, and **restore it before the run ends**. The report states explicitly whether restore succeeded.

While testing:

- Batch the independent calls. A DB read-back plus a source lookup plus a screenshot go in one block, not three turns.
- After every save, read the document back and paste the actual stored shape into the plan file.
- Hit a blocker? Record it with its exact reproduction, then route around it and execute every remaining scenario that doesn't depend on it. Do not end the run early. Track which scenarios became unreachable.
- When a finding needs data you don't have locally (prod-shaped volume, a real integration), say so explicitly instead of asserting it.

## Phase 4 — report

Append the results to the plan file and print the same report in chat:

1. **Test plan executed** — environment, dataset used, one line listing the flows exercised, and whether the fixture restore succeeded.
2. **Blockers** — anything that loses data, breaks the save, or makes the feature unusable. Each with the exact reproduction and observed versus expected.
3. **Checklist results** — a table of every item from Phase 2, stated and derived together, marked ✓ / ✗ / unreachable. For each ✗, what the app actually did. For each unreachable, which blocker prevented it.
4. **Other confirmed issues** — real but non-blocking, each with its reproduction.
5. **Not reproducible locally** — visible in the code but needing prod-shaped data; state what data would surface it.

Describe the problem: what happens, why it's wrong, what the user loses. Not the fix. One issue per bullet, no code-fix suggestions unless asked.

## Local environment (spark)

Defaults for the spark monorepo. Substitute for other projects.

- Web app on `http://localhost:3000`, API and Mongo and Elasticsearch running locally.
- MongoDB MCP: `connectionId: "preconfigured"`, database `JOSE_LOCAL`. The user's `_id` is in the global CLAUDE.md.
- **`curl` to localhost API endpoints is blocked by the sandbox.** Drive everything through agent-browser: navigation, forms, saves, and even inspecting network responses (`agent_browser_network_requests`). There is no shell fallback.
- Base branch for diffs is `develop`.
- Jira project key `GS`; branch patterns `GS-XXXXX/description` or `username/GS-XXXXX-description`.
