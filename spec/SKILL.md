---
name: spec
description: Turn a Jira ticket, an RFC, and/or the user's own direction into a reviewed plan (via the prd skill and Claude's Plan Mode), then execute it one self-contained task at a time, pausing for review before every commit. Use this skill whenever the user wants to start working on a ticket, says "let's work on GS-XXXX", "spec this out", "let's plan this feature", "/spec", pastes an RFC or design doc and wants it turned into implementation work, or asks to break a ticket down into tasks. This is the entry point for any nontrivial piece of work, not a research tool and not a coding tool on its own, it produces the plan and then drives the implement-review-commit loop across the whole PRD.
---

# Spec

You are taking a piece of work from "here's a ticket / an RFC / some direction" all the way to a merged set of commits, one reviewed task at a time. The plan is a durable artifact the user can read, correct, and come back to, not just a mental model you hold for one turn. Every phase below exists to prevent the two failure modes that make this kind of work go badly: building on a wrong assumption nobody caught, and racing ahead through commits the user never actually looked at.

## What this skill accepts as input

Any combination of:
- A Jira ticket key or URL (fetch it, don't ask the user to paste its contents)
- An RFC or design doc, linked or pasted
- Freeform direction from the user, "let's do X", constraints, things to avoid
- Nothing but a vague idea, in which case the clarifying-questions phase below carries more of the weight

Treat these as complementary, not exclusive. A ticket plus a verbal correction from the user ("actually skip the migration, do it in the next ticket") means the verbal correction wins, tickets can be stale.

## Phase 1: Gather the source material

Pull in whatever was referenced: fetch the Jira ticket via the Jira MCP tools if a key or URL was given, fetch or read the RFC if one was given (Confluence page, Notion doc, pasted text, whatever form it's in). Read what's actually there before asking the user to repeat it back to you.

If the ticket has a parent, read it too, not just the ticket itself, the parent's own description carries the broader goal the individual ticket is only a slice of. Read its sibling tickets as well, they often clarify scope, terminology, or decisions the ticket itself assumes the reader already knows.

## Phase 2: Read the repo's own instructions

Read the root `AGENTS.md` (or `CLAUDE.md`) if the repo has one. If it points to nested, workspace-specific instruction files (a monorepo convention where `web/AGENTS.md`, `jobs/AGENTS.md`, etc. hold area-specific rules), read the ones relevant to the areas this work is going to touch, not all of them speculatively. These files often encode conventions (import aliases, testing rules, branch naming, build commands) that change what a "correct" plan looks like, skipping this step produces a plan that reads fine and is wrong for this codebase.

## Phase 3: Ask clarifying questions

This is the phase where guessing is most tempting and most costly. Before drafting anything, work out what's actually ambiguous: scope boundaries, which of several reasonable approaches to take, whether an edge case is in or out, anything the ticket or RFC states as a goal without stating as a constraint. Ask. Use `AskUserQuestion` when there's a concrete set of options, ask in plain text when it's more open-ended.

**Never fill a gap with a silent assumption.** If, after asking, something is still unresolved and you have to proceed anyway, say exactly what you're assuming and why, out loud, before it goes into the plan. The user should never discover an assumption by reading it in the plan, they should see it stated as an assumption first and have the chance to correct it before it's load-bearing.

## Phase 4: Explore the codebase in Plan Mode

Use `EnterPlanMode`. Explore the way Plan Mode normally expects: find the relevant files, read the existing patterns for similar work, understand what you're extending rather than guessing at it. This is where you confirm the plan is technically grounded, not just a paraphrase of the ticket.

## Phase 5: Draft the plan with the prd skill

Invoke the `prd` skill to structure everything gathered so far, the ticket/RFC content, the user's direction, the answers from Phase 3, and what you learned in Phase 4, into a PRD with tasks and acceptance criteria. Feed it real, already-clarified context rather than letting its own self-clarification step guess blind, the point of Phases 1 through 4 is to make sure `prd` never has to invent an answer you could have just asked the user for.

Push on task boundaries: each task should be something that could be implemented, reviewed, and committed on its own, without leaving the repo in a broken state and without depending on a task that hasn't landed yet. Order them so that's true. A task that's "half of a feature" with no independent AC is a sign the breakdown needs another pass.

The `prd` skill saves its output to a file, treat that file as the plan's source of truth for the rest of this workflow. Everything from here on, feedback, revisions, task-by-task progress, gets reflected back into that file, not just held in conversation.

## Phase 6: Present the plan for approval

Use `ExitPlanMode` to hand the plan to the user. Do not proceed to implementation until it's approved.

**When the user gives feedback on the plan**, incorporate all of it, then update both your in-session understanding and the saved plan file, the file must never drift out of sync with what was actually agreed. If the feedback changes task boundaries or AC, rewrite those sections rather than appending a note about the change. Re-present with `ExitPlanMode` again if the changes are substantial enough that the user should see the revised version before work starts.

## Phase 7: Execute, one task at a time

Once the plan is approved, the default loop for each task is:

1. **Announce the task.** A short preamble naming which task you're starting and its acceptance criteria, before touching any code, so the user always knows what's coming.
2. **Implement it fully, but do not commit.** Write the code, run whatever local checks the repo's conventions call for (build, lint, tests), get it to a state you'd consider done against the task's AC. Stop there. Do not create a git commit and do not move on to the next task.
3. **Hand it back for review.** Tell the user the task is implemented and ready to look at. Wait.
4. **On approval, commit.** Once the user is satisfied, commit exactly what's in the working tree at that point, scoped to this task, following whatever commit conventions the repo documents (message style, sign-off lines, hook usage). Then loop back to step 1 for the next task.

**Do not skip ahead through multiple tasks' implement-and-commit cycles unless the user explicitly says to.** The pause after every implementation is the whole point, it's cheap for the user to say "keep going through the rest" if that's genuinely what they want, but the default must never assume it.

### The user may edit the code before approving

Between step 2 and step 4, the user might read what you wrote and refactor part of it themselves, rename something, restructure a function, whatever. Before you touch that task's files again for any reason (addressing a review comment, fixing something the user flagged, starting the next task), check what's actually in the working tree. **Never regenerate or reapply your own version on top of changes the user already made.** Their edit is the new baseline, not a diff to be reconciled away. If you need to build on top of it, build on what's there now, if something about their change seems to conflict with the task's AC, ask, don't silently revert it back to your original.

## What NOT to do

- Don't start implementing before the plan is explicitly approved via `ExitPlanMode`.
- Don't let `prd` self-clarify its way past a gap you could have asked the user about directly, ask first, feed it the answer.
- Don't commit a task's work without the user reviewing it first, and don't bundle multiple tasks into one commit.
- Don't silently assume anything the ticket, RFC, or user left ambiguous, state the assumption out loud if you have to make one.
- Don't let the saved plan file go stale, once the user gives feedback or a task lands, the file reflects it.
- Don't overwrite a manual edit the user made to your generated code. Read the current state before acting on a task you've already touched once.
