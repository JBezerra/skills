---
name: design
description: Settle how to build the work by grilling the user on every open decision, recorded in design.md. Runs after sdd:explore, before sdd:spec.
argument-hint: "[GS-XXXX] [direction]"
disable-model-invocation: true
---

# sdd:design

Phase 2 of explore → design → spec → implement. Locate the work folder per `${CLAUDE_PLUGIN_ROOT}/work-folder.md`. Input: `$ARGUMENTS`.

Your output is **decisions**: which approach, what's in and out, how each fork from exploration resolves, each with its alternatives and the reason. Decisions are the user's; you bring options, trade-offs, and a recommendation, then the user picks. `design.md` works at module level ("add a field to X, validate in Y"); tasks, ordering, and AC belong to sdd:spec.

## Steps

1. **Load.** Read `context.md`. If it's missing, invoke sdd:explore first and continue once it's written. If `Explored at <sha>` is behind HEAD and `git diff --stat <sha>..HEAD` touches the files it cites, tell the user and offer a sdd:explore re-run before designing. If `design.md` exists, resume from it: settled decisions stay, its Open list is the starting frontier.
2. **Build the design tree.** Roots: every open question Q1..Qn, plus decisions exploration couldn't list because they only exist once an approach is picked. Before the first round, check for commonly missed branches: data migration/backfill, rollout (flag, entitlement), backward compat for existing callers and data, test strategy, observability.
3. **Approach first.** When there's more than one viable way to build it, present 2–3 approaches with trade-offs and a recommendation, and settle that before anything else, since it reshapes the rest of the tree.
4. **Grill in rounds.** The frontier is every decision whose prerequisites are settled. Ask the whole frontier each round via `AskUserQuestion` (back-to-back calls when it exceeds 4): recommended option first, suffixed `(Recommended)`; each option's description says what choosing it means and what it costs. Open-ended questions go in plain text. After each round, write the answers into `design.md` and recompute the frontier.
5. **Facts on demand.** When a decision needs a fact, look it up with targeted reads, or one subagent when it's broader, and append the fact with its `file:line` to the matching section of `context.md`. Keep asking the rest of the frontier meanwhile; only questions downstream of the lookup wait.
6. **Assumptions out loud.** Anything you'd proceed on without a user answer gets stated in chat as an assumption and recorded as Ax, pending until the user accepts it.
7. **Settle.** Done when every Q has a D (out-of-scope is a valid D), Open is empty, every Ax is accepted, and the user confirms shared understanding. Then set `Status: settled` and report: approach in two lines, decision count, anything notable deferred to non-goals. Next step: sdd:spec.

## Revisiting a decision

When the user changes a settled D, rewrite it in place, reopen every decision whose `Depends on` names it, and set `Status: open`. If `spec.md` exists, tell the user it's now stale and needs a sdd:spec re-run.

## design.md template

```markdown
# <KEY>: design
Status: open | settled
Based on context.md explored at <short sha>

## Approach
The chosen approach in 3–5 sentences: what changes where, at module level.

## Alternatives considered
- <approach>: why not

## Decisions
### D1: <decision> (settles Q1)
- Chosen: ...
- Alternatives: <option>, why not
- Why: ...
- Depends on: D<n>

## Assumptions
- A1: <assumption> (accepted | pending)

## Non-goals
- ...

## Open
- <decisions still on the frontier; empty when settled>
```
