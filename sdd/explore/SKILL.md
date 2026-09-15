---
name: explore
description: Explore a Jira ticket, RFC, or bug against the codebase and record the facts in the work folder, ending on open questions. Use when starting work on a ticket ("let's work on GS-XXXX"), investigating a bug before fixing it, or when sdd:design finds no context.md.
argument-hint: "<GS-XXXX | Jira URL | RFC> [direction]"
---

# sdd:explore

Phase 1 of explore → design → spec → implement. Locate the work folder per `${CLAUDE_PLUGIN_ROOT}/work-folder.md`.

Your output is **facts**: how the system works today and everything the work touches, each backed by a source. Every fork you hit (two viable approaches, an in/out scope call, an ambiguous requirement) becomes an **open question**, recorded with the evidence on each side and left for sdd:design to settle. Run end to end without asking the user anything, unless a question blocks the sweep itself (e.g. the ticket names a system you cannot find).

Input: `$ARGUMENTS`. User direction overrides the ticket where they conflict, since tickets go stale. Record the conflict under Sources.

## Steps

1. **Sources.** Fetch the ticket through the Jira MCP, then its parent and siblings (the parent's other children). Read any linked or passed RFC, Confluence, or Notion doc. Done when every referenced source is read or listed as unreachable.
2. **Repo rules.** Read the root `AGENTS.md`/`CLAUDE.md`, the nested instruction files for the areas the work touches, and whatever they name as authoritative behavior (e.g. `openspec/specs/`). Done when every touched area's rules are read.
3. **Sweep.** Split the territory into independent areas (data model/schema, API, UI, jobs, tests, prior art for a similar feature, git history of the touched files) and dispatch one Explore subagent per area, in parallel. Ask each for facts with `file:line`, never file contents. Close the gaps yourself with targeted reads. Done when the flow is traced end to end (entry point to persistence/render) and every claim you'll write has a `file:line` or a source link.
4. **Write `context.md`** from the template below. On a re-run, update the file in place and keep facts sdd:design appended.
5. **Report** in chat: what the work actually touches, surprises vs the ticket, open question count, path to `context.md`. Next step: sdd:design, or a direct fix for a bug with zero open questions.

## context.md template

```markdown
# <KEY>: <title>
Explored at <short sha> on <date>

## Sources
- Ticket: <url>, one-line summary
- Parent: <url>, the goal this ticket is a slice of
- Siblings: <key> (<status>), why it matters here
- Docs: <RFC / Confluence / Notion>
- User direction: <verbatim>, plus any conflict with the ticket

## Problem
What's missing or broken, in ticket terms and in code terms.

## How it works today
The relevant flow, entry point → persistence/render, each step with `file:line`.

## Touch points
| Area | File | What's there | Why it matters |

## Patterns to follow
Similar existing features and applicable AGENTS.md conventions, with pointers.

## Constraints
Hard facts that bound any design: schemas that trigger a resync, flags, callers relying on current behavior, tests pinning it.

## Open questions
### Q1: <question>
- Options seen: A (evidence), B (evidence)
- Unknowns: facts that couldn't be established, and why
```
