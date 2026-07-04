---
name: daily-brain
description: >
  Analyzes the day-over-day diff of the user's personal brain-dump file
  (~/source/@ai/📍.md) — a mix of work tasks, ideas, and personal/life
  notes organized as a rolling Kanban. Produces a blended daily analysis
  covering progress made, new ideas/intentions captured, stale items that
  keep rolling over unresolved, and light coaching-style reflection
  questions. Trigger whenever the user says "/daily-brain", "run my daily
  brain analysis", "diff my notes file", or similar. Also the target of a
  daily 7am cron job — when invoked non-interactively (no user turn to
  respond to), just perform the full run and finish; there is no one to
  ask follow-up questions.
---

# Daily Brain Analysis

Analyze `~/source/@ai/📍.md` against yesterday's snapshot, and produce a
short daily report that blends accountability tracking, idea surfacing,
and reflective coaching — the way a good 1:1 partner would look at this
file with the user.

The file is the user's external brain: work tasks (GovSpend/AIP), a side
project (Mergi), and personal/family notes, organized into a `Done` log,
a `Kanban` (Today / Tomorrow / This Week / Backlog), and a `Resoluções
Semanal` weekly reflection block. Treat all of it as fine to read and
reason about locally — no need to redact or split out personal content.

---

## Step 1 — Read the current file and find yesterday's snapshot

Read `~/source/@ai/📍.md`.

List `~/source/@ai/snapshots/`. Snapshots are named `YYYY-MM-DD.md`. Find
the most recent snapshot strictly before today's date.

- **If no prior snapshot exists** (first run ever): skip the diff step,
  and instead produce an orientation-style analysis — summarize the
  current state of Today/Tomorrow/This Week/Backlog, and note anything
  that looks stuck or contradictory. Say explicitly in the output that
  this is the first run so there's no diff yet.

- **If a snapshot exists**: diff the current file content against it
  (a simple text diff is enough — `diff -u` via Bash, or reason over the
  two texts directly). Use the diff as the primary input for Step 2.

Also list up to 7 days of snapshots (not just yesterday's) — these feed
the staleness check in Step 2.

---

## Step 2 — Build the analysis

Produce a report with these sections, in this order. Skip a section
entirely if there's nothing worth saying in it — don't pad with "nothing
to report here."

### 1. Progress
What moved from unchecked to checked (`- [ ]` → `- [x]`) since yesterday,
across `Done` and the Kanban. Group by Work / Mergi / Pessoal if there's
enough to group. Be concrete — name the actual task, not "some tasks."

### 2. New ideas & intentions
New `|>` thought entries, new bullets under Tomorrow/This Week/Backlog,
or new freeform notes in the `1:1 Notes` section. For each, note if it
connects to something already in the file (an existing idea, a related
task) — the point is catching ideas that echo each other so nothing gets
lost as a one-off thought.

### 3. Stale items
Using up to 7 days of snapshots, find checklist items in Today/Tomorrow
that appear **unchanged and still unchecked** across multiple snapshots
(3+ days is a reasonable bar, but use judgment — a task tagged ASAP that's
stale is worth flagging even at 2 days). List them explicitly. This is
the section most likely to catch things quietly rotting.

### 4. Reflection
Pick 1-2 of the `Resoluções Semanal` questions (Jiu-Jitsu, Mergi
progress, writing, meals) or a career/balance angle from the diff itself,
and ask them back directly as pointed questions — not generic journaling
prompts, but grounded in what actually happened this week. If it's
Monday, lean into this section more since that's when the weekly
resolution block is meant to be reviewed.

### 5. Suggested cleanup (optional, light-touch)
If something in Backlog/This Week looks actually done based on the Done
log or diff, or a Kanban section looks like it needs to roll over (e.g.
`Done` week log ends and a new week should start), suggest it as a
specific, actionable edit — but do not make the edit yourself. Phrase it
as "want me to remove/move X?" This skill never edits `📍.md` directly.

---

## Step 3 — Write the analysis file

Write the report to `~/source/@ai/daily/YYYY-MM-DD-analysis.md` (today's
date). Use plain markdown, the section headers above, tight bullets. This
is a file the user skims in under a minute, not a long essay.

---

## Step 4 — Save today's snapshot

Copy the current `📍.md` content verbatim to
`~/source/@ai/snapshots/YYYY-MM-DD.md` (today's date). This is what
tomorrow's run will diff against. Always do this last, after the
analysis is written, so a failure mid-analysis doesn't leave a snapshot
without a matching report.

---

## Step 5 — Notify

Send a macOS notification so the user knows the analysis is ready without
having to check manually:

```bash
osascript -e 'display notification "Daily brain analysis ready" with title "Daily Brain" subtitle "'"$(date +%Y-%m-%d)"'"'
```

---

## Edge cases

- **Run more than once same day**: if `~/source/@ai/snapshots/YYYY-MM-DD.md`
  for today already exists, still overwrite it with the latest content at
  Step 4 (idempotent), but diff against the same "yesterday" baseline as
  before, not against today's own earlier snapshot.
- **Non-interactive/cron invocation**: there is no user to ask
  clarifying questions. Make reasonable judgment calls and note any
  assumptions briefly in the output rather than stopping to ask.
- **Empty or missing snapshots directory**: treat as first run (see
  Step 1).
