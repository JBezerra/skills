---
name: create-pr
description: Draft a GitHub pull request description (and open the PR) in Tech Lead José Bezerra's house style — Jira link, Summary, Why, Testing Steps, Companion links, with the exact title conventions his team uses for standard, hotfix, warmfix, and revert PRs. Use this skill whenever the user asks to open a PR, create a pull request, write a PR description, "raise a PR", "PR this branch", stack a companion/hotfix/warmfix PR onto master/develop/release-qa, or says "/create-pr". Also trigger when the user has just finished a branch and wants to ship it, or asks you to write up the PR body before pushing.
---

# Create PR

You are writing a GitHub pull request the way Tech Lead José Bezerra writes them: a tight, evidence-linked description that a reviewer can act on without asking questions, plus a title that follows his team's branch-target conventions exactly. The description is not marketing. It states what the PR does, why, how to verify it, and what it depends on — nothing more.

The team runs a stacked release flow (`develop` → `release/qa` → `master`/`main`), so a single change often ships as several PRs. Get the **PR type** right first (below), because it drives both the title and which sections the body needs.

## Workflow

1. **Gather context.** Run these in parallel:
   - `git branch --show-current` — the head branch (carries the Jira key, e.g. `GS-16436/mcp-subdomain-audiences`).
   - `git log <base>..HEAD --oneline` and `git diff <base>...HEAD --stat` — what actually changed. Read the real diff for anything non-trivial; the Summary describes behavior, not file names.
   - `git remote -v` — which repo (`smartprocure/spark` vs `smartprocure/spark-mcp`), which decides companion wording and default base.
   - If a `GS-XXXX` key is present, fetch it with `mcp__Jira__getJiraIssue` to ground the Summary and Testing Steps in the actual ticket intent. Don't invent scope the ticket doesn't have.

2. **Determine the base branch and PR type.** Ask if it's not obvious. The base decides everything:
   - base `develop` (or a feature base) → **Standard PR**
   - base `release/qa` → **Warmfix** (see the Warmfix section)
   - base `master` / `main` → **Hotfix** (see the Hotfix section)
   - the PR reverts a merge → **Revert / incident** (see that section)
   - the PR only exists to promote another PR up the stack, or to mirror a change in the sibling repo → **Companion** (terse body, see below)

3. **Detect companions.** A change usually lands as a chain: `develop` PR ↔ `master`/`main` PR ↔ `release/qa` PR, and spark ↔ spark-mcp often move together. Look for the sibling PR (`gh pr list --search "GS-XXXX"` in this repo and the sibling repo) and link it. One PR in the chain carries the **full** description; the rest are terse and point to it.

4. **Draft the title and body.** Use the title conventions and the section templates below. Match the tone rules. Keep it lean.

5. **Show the full draft and confirm before creating.** Print the title and the rendered Markdown body and wait for explicit go-ahead — opening a PR is outward-facing. If the branch isn't pushed yet, offer to push first.

6. **Create it.** `gh pr create --base <base> --title "..." --body "..."` (write the body to a temp file and use `--body-file` to keep Markdown intact). Return the PR URL. Never add a "Generated with Claude Code" footer or any `Co-Authored-By` trailer.

## Title conventions

Match these exactly — the brackets and backticks are load-bearing, reviewers filter on them.

- **Standard:** `GS-XXXXX: Short imperative title` — e.g. `GS-14619: Federal Onboarding Flow`. Bracketed form `[GS-XXXXX] Title` is also fine; pick one and keep the Jira key first.
- **Hotfix:** `` [HOTFIX][`<branch>`] GS-XXXX: Title `` — branch in backticks (`` `master` ``, `` `main` ``, `` `develop` `` for the companion). e.g. `` [HOTFIX][`master`] GS-16188: OAuth - Support WorkOS Login on Spark ``.
- **Warmfix:** `` [WARMFIX][`release/qa`][GS-XXXX]: Title `` — e.g. `` [WARMFIX][`release/qa`][GS-15676] Add Federal fallback to MCP instructions ``.
- **Revert:** `` [REVERT][`<branch>`] GS-XXXX: What is being undone ``.

If there's no Jira key (infra bump, config fix, conflict resolution), a plain descriptive title is fine: `Bump `@mastra` packages (take 2)`, `Resolve `develop` conflicts`. Backtick package names, branches, and file names in titles too.

## Standard PR body

Use only the sections that carry weight. `# Jira` and `## Summary` are effectively always present; the rest appear when they have something to say. Observed order:

```markdown
# Jira
https://govspend.atlassian.net/browse/GS-XXXXX
<second link if the work spans two tickets>

## Summary
- <present-tense bullet: what this PR does, from the reader's POV>
- <one bullet per meaningful behavior change; backtick params, env vars, files>
- Companion of <#N or full URL to the sibling PR>   ← if there is one

## Why
<Only when the reason isn't self-evident. One or two sentences. Link the evidence
that motivated it — Grafana/Kibana/Axiom logs, a Slack thread, a metrics dashboard.
This is where you justify a removal, a revert, or a non-obvious approach.>

## Testing Steps
<Concrete, reproducible steps. Number them when order matters, bullet them when it
doesn't. Link the exact fixture — a specific bidDetails URL, a saved search, an env.
For multi-service setups, break Setup into subsections:>

### Setting up API
- ...

### Setting up MCP
- ...

## Notes
- <caveats, and anything intentionally out of scope, with the follow-up ticket>
```

Other sections that show up when relevant: `## Demo` (a Slack recording link), `## Screenshots` (before/after images), `## Ref` (external docs that justify the change), `## Test plan` (a checklist for infra/build PRs).

## Companion / stacked PR body

When a PR only promotes another PR up the release stack, or mirrors the sibling repo, the body is one line pointing at the PR that holds the real description. Match this phrasing:

- Promoting to `master`/`main`: `Master for #N` / `Main for #N` / `Main of #N`
- Promoting to `release/qa`: `Release QA for #N` / `QA for #N`
- The `develop` half of a hotfix: `Develop for #N`
- Sibling repo: `Companion of <URL>` / `Companion on <URL>`

It's fine to add the `# Jira` + `## Summary` + `## Testing Steps` to whichever copy is most useful to reviewers (often the `develop` one) and keep the others terse. Don't duplicate a long body across every PR in the chain.

---

## Hotfix directives

A hotfix lands on `master`/`main` to reach production ahead of the normal release, and by team policy the **same branch** used on `develop` is reused for the `master` PR. That's deliberate, and it has consequences the description must own:

- **The `master` PR will show unrelated changes** when the branch was cut from / synced with `develop`. Call it out so reviewers don't panic. Use the standing disclaimer, adapted:

  > ## ⚠️ Disclaimer
  > Following our Hotfix Guidelines, the same branch used on `develop` is used on `master` too. That's why this PR carries unrelated changes. I can only clean up the git tree after merging its develop companion, so don't worry about that — we'll get it straight before merging.

- **State the merge order explicitly** when PRs depend on each other: `**Merge after:** #N`, `**Must deploy after this.**`. Reviewers need the sequence.
- **Always pair the two halves.** The `master` PR says `Master for #<develop-PR>`; the `develop` PR carries the full Summary/Testing Steps and says its companion is the master one. Cross-link both directions.
- If the hotfix branch was cut clean from `master` (no develop bleed), skip the disclaimer — say so plainly instead ("Cherry-picks only the WorkOS commits onto a clean `master` base").

## Warmfix directives

A warmfix targets `release/qa` — a fix that needs to ride the current QA build rather than wait for the next `develop` cut. Conventions:

- Title: `` [WARMFIX][`release/qa`][GS-XXXX]: Title ``.
- Body is usually terse and points at the source PR: `Release QA for #N`. The `develop`/`main` PR in the pair holds the full description.
- If the change originated in the sibling repo, note the companion: `Companion on <spark URL>`.

## Revert / incident directives

When a merge shipped something it shouldn't have, the PR is a full revert plus a post-mortem. Structure it so anyone can see the blast radius:

```markdown
## What happened
<one paragraph: which merge/PR caused it, and the concrete impact — e.g. "carried the
entire develop history to production, shipping N unintended PRs before their release">

## What this PR does
<what you're reverting and to which commit, and why a full revert over a surgical one.
State if the intended feature will be re-landed cleanly in a follow-up.>

## PRs that were accidentally shipped to production
- [Title](url) ⚠️
- [Title](url) (tests only)
```

Prefer a clean full revert over a partial one and say why. Mark production-affecting entries with ⚠️ and label test-only ones so reviewers can triage risk fast.

---

## Tone and formatting

- **First person, plain, a little casual.** "I suspect the cache is causing this", "so I'm putting it back", "don't worry about that". You're a teammate leaving notes, not a changelog bot.
- **Backtick everything technical:** branches, env vars, params, file names, package names, function names. `` `WORKOS_RESOURCE_URL` ``, `` `release/qa` ``, `` `@mastra/core` ``.
- **Link the evidence, don't describe it.** A Grafana/Kibana/Axiom link for a logging-motivated change, a Slack thread for a demo, the exact fixture URL for a repro, the sibling PR for a companion. A claim with a link beats a paragraph without one.
- **Summary bullets are present-tense and behavioral** — what the PR does for the reader, not a file-by-file list. "WorkOS JWTs without an encrypted API key are forwarded directly to Spark as Bearer tokens", not "edited auth_provider.py".
- **Explain the why for anything non-obvious** — a removal, a revert, a workaround, an approach that competes with the existing pattern. Skip the Why section when the Summary already makes it obvious.
- **Keep it lean.** Omit empty sections entirely. A three-line PR is correct when the change is three lines. Don't pad.
- **⚠️** is for genuine warnings (unrelated changes, production impact, merge-order hazards), used sparingly.
- **No em-dashes as sentence punctuation** — use commas, periods, or parentheses. **Never** add a `Co-Authored-By` trailer or an AI-generated footer.

## What NOT to do

- Don't open the PR before showing the full draft (title + body) and getting explicit confirmation.
- Don't write a file-by-file changelog in the Summary — describe behavior and intent.
- Don't duplicate a long description across every PR in a stack — one carries it, the rest point to it.
- Don't omit the hotfix disclaimer when the `master` branch carries develop bleed, and don't include it when the branch is clean.
- Don't invent Testing Steps you can't ground in the diff or the ticket — vague steps are worse than none.
- Don't leave companion/merge-order links out. A stacked PR without its chain links is the most common way these get merged in the wrong order.
