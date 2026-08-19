---
name: full-review
description: >
  Run three independent reviews of one pull request in parallel — Anthropic's /code-review at
  high effort, the personal /pr-review TL review, and browser-driven /uat-pr — and merge them
  into one digest that ranks every finding by what it costs to ship, written in ASD-STE100
  Simplified Technical English and delivered as a self-contained HTML docket under
  ~/source/@specs/. Checks out the PR branch, pulls the latest, and preflights the API
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

Wait for every spawned agent. A stalled agent can still resume and deliver, and a killed agent can
report later. Do not finalise the digest while a reviewer is still in flight. If you already gave the
user a digest and a late report then arrives, rewrite the whole digest and state plainly that it
replaces the earlier one.

Write **one document**, not three. Group the findings by what they cost the user to ship, never by
which reviewer spoke. The reader wants a merge decision, and the reviewer that found a defect is a
confidence signal, not an organising principle.

**The deliverable is an HTML file, not a chat message.** A digest of this size is unreadable in a
terminal. Render it from `references/digest-template.html` as described in Phase 5, and keep the chat
reply to the verdict, the bucket counts, and the file path.

**Voice: ASD-STE100 Simplified Technical English for the whole digest**, including the UAT material.
Read `references/ste.md` before you write. The protected list in that file is absolute: never rewrite
a file path, a `file:line` anchor, a symbol name, a quoted app string, a quoted AC line, or a stored
document shape.

### Severity is yours to assign

The reviewers' own labels are input, never the verdict. `/pr-review` names blockers. `/uat-pr` can
report none. They disagree often, and the disagreement is the thing you resolve.

Judge every finding on user harm. Ask one question: does a real customer hit this, and does the
customer lose data or become stuck with no way out through the UI?

- **A stuck or invisible state that the UI cannot undo is a must-fix.** A value the user cannot
  deselect qualifies. A committed value with no visible row qualifies.
- **Work that the user can redo is not a must-fix**, even when the app destroys it with no warning.
  Put it at the top of the follow-up bucket and say in one line that it is a close call.
- **A static prediction that nobody reproduced stays below the line.** Name the precondition that UAT
  never met.
- **Evidence from a stored document outranks a code reading.** When UAT found the defect on disk, say
  so and quote the shape.

### Merge duplicates, and tag who found each one

One defect is one finding. Fold every reviewer that hit it into a single `Found by` line. Independent
agreement between reviewers is the confidence signal, so the digest carries **no separate Agreement
section**.

- When one reviewer predicted a defect and another proved it in the running app, say both.
- When a static prediction went unconfirmed because UAT never met its precondition, say that too.
- Group findings that share one root cause under the same bucket and state the shared cause once.

### Structure

The template holds this structure already, with one worked example of every block. Read it before you
write. The outline is:

`````
# PR #<N> — <ticket key> <short feature name>
`<branch>` @ `<short sha>` · base `<base>`

## My call: <do not merge yet | merge after follow-ups | merge>
<One or two sentences of what drives the call. Then a short paragraph of what is sound, so the
author reads that the feature works before reading what does not.>

# WHAT UAT EXERCISED (<n> checks)   <- leads the document; the checklist itself is collapsed
# MUST FIX BEFORE MERGE (<n>)
# SHOULD FIX, CAN BE A FOLLOW-UP (<n>)
# COSMETIC AND PAPER CUTS (<n>)
# NOT BUILT AT ALL (<n>)
# NOT TESTED, SO UNKNOWN (<n>)
# OPEN QUESTIONS FOR THE AUTHOR (<n>)

## Housekeeping
`````

**The coverage section leads.** The reader sees what a browser drove before reading what is broken,
which is what makes the severity calls legible. Its own checklist stays collapsed inside it.

Number the findings continuously across the four finding buckets, from 1 to N. Omit a bucket that
holds nothing. Keep the count in every heading.

### Finding shape, by bucket

**MUST FIX** carries the full shape and a reproduction. Write the steps as **bullets, never numbers**,
and keep each step to one action the reader performs:

`````
### <n>. <One plain sentence that names the symptom. No file path, no symbol name.>

**What happens.** <The user's experience, in short sentences. Present tense.>

**Why.** <The mechanism, in two or three sentences.>

**Where.** <Anchors and symbol names.>

**Found by.** <reviewers>

**Proof from UAT.** <Only when UAT saw it. Quote the stored shape or the observed string.>

**Check it yourself.**
- <A click-path the user follows in under a minute. Bullets, not numbers.>
`````

**SHOULD FIX** uses the same shape and keeps **Check it yourself**. Every finding the reader can act
on earns a reproduction, so the reader never takes the severity call on trust.

**A finding that nobody reproduced still earns the panel.** Never invent a click-path. Write what the
check actually needs, and say in a closing note why nobody ran it:

- The precondition that UAT never met (`UAT never ticked a state in the filter popover, so step 3 is
  the precondition nobody exercised`).
- The dataset the local environment cannot build, and the code path or the response field to read
  instead.
- The panel opens with the honest sentence when no click-path exists: `This one has no click-path.`

**COSMETIC AND PAPER CUTS** collapses to one bullet each: a bold plain-language label, one or two
sentences, the anchors, then the reviewers in italic parentheses.

**NOT BUILT AT ALL** uses the full shape with no reproduction. Quote the AC line that asks for the
missing work.

**NOT TESTED, SO UNKNOWN** is one bullet each: what nobody exercised, and what would exercise it.

**OPEN QUESTIONS FOR THE AUTHOR** is one bullet each. Keep the AC quote that raises the question.

### The UAT checklist

Every failed and caveated row becomes a numbered finding in the bucket where it belongs. A passing row
is not a finding, so it never appears above the coverage section.

**Then publish the whole checklist, every row, in the coverage section.** It answers a different
question from the findings: not what is broken, but what a browser actually drove. Without it the
reader cannot tell a defect that does not exist from a defect nobody looked for.

Keep it collapsed behind `details.checks` so it costs nothing to skip. Inside it:

- One `li.chk` per row, with `st-pass`, `st-fail` or `st-warn` on the chip, the row id, the check as
  the plan worded it, and what UAT observed with the exact strings.
- Cross-reference the finding number on every row that did not pass (`See finding 3.`).
- Keep the plan's own grouping: rows from the ticket AC, then the rows UAT derived itself.
- Carry the flows it drove, the environment, the fixtures and the plan file path in the `cov-meta`
  list above the collapsed rows. Say when Elasticsearch was remote, because that decides whether the
  matches ran against real data.

### Housekeeping footer

State that nothing went to GitHub and that no fix is applied. State the database or fixture state.

**Verify the fixture restore yourself with a read query.** Do not repeat the UAT agent's claim on
trust. A killed agent leaves test data behind, and the user's local database is the thing that
suffers.

Close by offering the two next steps: start the top fix, or turn the digest into PR comments.

### Rules

- **Drop no findings.** Every finding from every reviewer appears exactly once, in some bucket. The
  grouping is triage of severity, never triage of coverage.
- **Keep every anchor.** Simplification rewrites prose, never a path, a symbol, or a quoted string.
- **Open every finding in plain language.** Never start a finding with a file path or a symbol name.
  The mechanism sits underneath, where the reader can skip it.
- **A reviewer that did not report keeps a visible line**, with the reason (`the web app on :3000 was
  not listening`, `the agent stalled and delivered no report`). Never invent its findings. Never fill
  the gap with your own review.
- Post nothing to GitHub. Apply no fix. The user asks for either after they read the digest.

## Phase 5 — render the HTML document

Copy `references/digest-template.html` to
`~/source/@specs/<repo>/<TICKET-KEY>-pr<N>-review.html`, then fill it in. Never write the page from
scratch: the template carries a palette, a type scale, an accordion, a copy-to-clipboard script and
print styles that all work together.

### What the template gives you

- **A defect-docket layout.** Hairline rules between findings, the finding number in a left gutter,
  severity as a bucket colour. No cards, no rounded corners, no accent rails.
- **Six semantic bucket colours**, each separate from the teal structural accent.
- **Accordions at two levels.** Every top-level group is a `<details class="bucket">`, open by
  default, so the reader can collapse a whole bucket down to its heading. Every numbered finding
  inside is a `<details class="finding">`, and only the must-fix findings carry `open`. `Expand all`
  and `Collapse all` sit under the nav and drive both levels plus the checklist.
- **A print hook.** `beforeprint` opens every closed `<details>` and `afterprint` puts them back,
  because CSS alone cannot reveal a closed one in Chrome. Never replace this with a `display` rule.
- **A copy button on every `Check it yourself` panel.** It emits the steps and nothing else, as `-`
  bullets with `<code>` spans wrapped in backticks, so they paste into Jira, Slack or GitHub. **Never
  add a header line** naming the PR or the finding. The reader pastes these into a thread that already
  has that context, and a prefix is noise there. A `Note:` line still trails the steps when the panel
  carries one.
- **Light mode, pinned** with `data-theme="light"` on the root element. The dark palette is still in
  the file and is one attribute away. Leave the pin in place.
- **Print styles** that force every accordion open and hide the buttons, so a PDF keeps the full text.
- **A coverage section** that leads the document and carries the complete UAT checklist, collapsed,
  with a pass, fail or warn chip on every row.

### Filling it in

- Replace every `{{TOKEN}}`. There are 25 of them, all upper-case, in the head, the masthead, the
  verdict, the nav counts, the coverage section and the closing block.
- Put exactly one variant class on `.verdict`: `v-block` for do-not-merge, `v-followup` for
  merge-after-follow-ups, `v-clear` for merge.
- Repeat the example block inside each bucket once per finding, and renumber continuously.
- Delete a whole `<details class="bucket">` when its bucket is empty, and delete its `<li>` from the
  nav so the counts stay honest. Keep every remaining group `open`.
- Keep the coverage group first, and its nav entry first.
- Delete every optional block you do not use: `.bucket-note`, `.proof`, `.repro-note`,
  `.close-call`, and the `Not confirmed` row.
- Keep the steps in `<ul>`. Never use `<ol>` in a `Check it yourself` panel.

### Before you hand it over

- Confirm every `{{` is gone.
- Confirm the nav counts match the bucket headings, and that the headings match the number of blocks.
- Confirm the coverage section holds every checklist row, and that its pass, fail and warn counts add
  up to the total.
- Confirm no tag is left unclosed, and that the inline script still parses.
- Give the user the path and the `open <path>` command.

### The chat reply

Keep it short. The verdict line, the bucket counts, the path, and the `open` command. Then the two
offers: start the top fix, or turn the digest into PR comments. Do not paste the findings into the
chat as well.
