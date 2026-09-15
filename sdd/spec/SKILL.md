---
name: spec
description: Turn a settled design.md and test-cases.md into spec.md, a sequence of standalone, committable tasks with verifiable acceptance criteria. Runs after sdd:design, before sdd:implement.
argument-hint: "[GS-XXXX]"
disable-model-invocation: true
---

# sdd:spec

Phase 3 of explore → design → spec → implement. Locate the work folder per `${CLAUDE_PLUGIN_ROOT}/work-folder.md`. Input: `$ARGUMENTS`.

Your output is a **contract** for sdd:implement, which runs in a fresh session and reads only `spec.md`. Everything it needs to build and verify each task lives in the task itself. Every line traces back to a decision in `design.md`, a case in `test-cases.md`, or a fact in `context.md`.

## Steps

1. **Gate.** Read `design.md`. Proceed only when it says `Status: settled` and `test-cases.md` exists; otherwise name what's still open or missing and point the user to sdd:design. Then read `test-cases.md`, `context.md`, and the repo's root instruction file for the exact build, lint, and test commands.
2. **Derive requirements.** Write numbered FRs from the approach and decisions. Done when every D is reflected in at least one FR or in Non-goals.
3. **Cut tasks.** Each task is one **reviewable commit**: after it lands, the repo builds, tests pass, and nothing depends on a later task. Order tasks so that holds. A task that's half a feature, with no AC of its own, gets merged or re-cut. List the files each task touches, from `context.md` touch points.
4. **Write AC.** Each criterion is checkable: a behavior with concrete input and output, a named test, or a command that passes. Every task gets a tests criterion covering its TCs where the repo's test setup allows and following the repo's testing rules, and a quality-checks criterion naming the exact commands from step 1. Tasks with UI changes get a browser verification criterion stating what to see.
5. **Coverage check.** Every FR and every TC maps to a task, every task cites the FRs, Ds, and TCs it implements, and every `Touches` path either exists or is marked `(new)`. When a task needs a decision `design.md` lacks, ask it via `AskUserQuestion` and record it there as a new D before writing the task.
6. **Review.** Write `spec.md` with `Status: draft` and show the task list in chat, one line per task. Apply feedback by rewriting the affected sections in place, so the file always reads as the current agreement. Done when the user approves; then set `Status: approved`. Next step: sdd:implement.

## Re-running on an existing spec

Tasks marked `[x]` or `[~]` stay as they are, sha included. Rewrite only `[ ]` tasks, and tell the user which pending tasks changed.

## spec.md template

```markdown
# <KEY>: <title>
Status: draft | approved
Branch: <KEY>/<kebab-slug>

## Overview
The problem and chosen approach in one paragraph. Details: `context.md`, `design.md`, `test-cases.md`.

## Goals
- <measurable outcome>

## Functional requirements
- FR-1: The system must ...

## Non-goals
- <from design.md, plus anything cut while slicing>

## Tasks

### [ ] T-001: <title>
Implements: FR-1, D2
Covers: TC-A1, TC-B2
Touches: `path/to/file.ts`, `path/to/new.ts` (new)

**Description:** What to build, and why it stands alone.

**Acceptance criteria:**
- [ ] <behavior with concrete input and output>
- [ ] Tests: automated coverage for the covered TCs where the repo's test setup allows, in <file>
- [ ] Quality checks: `<exact commands>`
- [ ] [UI only] Browser: <what to verify>
```
