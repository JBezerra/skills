---
name: stress
description: Stress-test the plan in the work folder (spec.md, else design.md) with a fresh subagent hunting for holes, failure modes, missed code, side effects, and coupled fields. Run ad hoc after sdd:design or sdd:spec.
argument-hint: "[design | spec] [GS-XXXX]"
disable-model-invocation: true
---

# sdd:stress

Ad hoc check on the plan, run after sdd:design or sdd:spec. Locate the work folder per `${CLAUDE_PLUGIN_ROOT}/work-folder.md`. Input: `$ARGUMENTS`.

## Steps

1. **Pick the target.** `design` means `design.md` and `test-cases.md`; `spec` means `spec.md`; with neither, take `spec.md` when it exists, else `design.md`. `context.md` always goes along as background.
2. **Dispatch one general-purpose subagent**, a fresh reader with no stake in the plan. Give it the absolute paths of the target files and the repo root (paths, never a summary, so it reads the plan as written) and the brief below.
3. **Spot-check** every high finding: open its cited `file:line` and confirm the code says what the finding claims. Mark each `confirmed` or `unverified`; drop what the code contradicts and say so.
4. **Write `stress.md`** from the template below, replacing any previous run, and report in chat: counts by severity and the high findings in one line each.
5. **Route.** The user decides each finding: one that challenges a decision goes to sdd:design as a revisit; a missing task, touch point, or TC goes to a sdd:spec re-run; the rest get dismissed. The plan files stay as they are until then.

## Subagent brief

> You are stress-testing an implementation plan before any code is written. Read the plan files and `context.md`, then hunt for holes in five passes:
>
> 1. **Pre-mortem.** Assume the work shipped and failed. What went wrong?
> 2. **Trace.** For every code change the plan proposes, follow the call paths up (callers, entry points) and down (callees, persistence) and find where it can fail: missing values, type mismatches, validation, races, error paths, permissions.
> 3. **Missed code.** Search the codebase for pieces related to this work that the plan doesn't cover: parallel implementations, other entry points into the same flow, tests pinning the current behavior.
> 4. **Side effects.** What else changes behavior because of these changes: sync jobs, indexes, caches, exports, notifications, analytics, other features.
> 5. **Coupled fields.** For every field, schema, type, or config value the plan touches, find every other reader and writer and check each one still works.
>
> Done when every proposed change and every touched field is traced to its callers, readers, and writers.
>
> Report each finding with: severity (high, medium, low), pass, the plan item it hits (`Dn`, `T-00n`, `TC-Xn`, or none), evidence as `file:line`, and a concrete scenario of what goes wrong and when. Describe the problem and leave the fix to the plan's authors. Work read-only.

## stress.md template

```markdown
# <KEY>: stress
Target: <spec.md | design.md>, run on <date> at <short sha>

### S1 [high] <the problem in one line>
- Pass: <pre-mortem | trace | missed code | side effects | coupled fields>
- Hits: <D3, T-002, TC-B4, or none>
- Evidence: `path/to/file.ts:42`
- Scenario: <what goes wrong, and when>
- Check: <confirmed | unverified>
```

Order findings most severe first.
