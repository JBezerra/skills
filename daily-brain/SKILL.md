---
name: daily-brain
description: >
  Analyzes the day-over-day diff of the user's personal brain-dump file
  (~/source/@cron/📍.md) — a mix of work tasks, ideas, and personal/life
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

Analyze `~/source/@cron/📍.md` against yesterday's snapshot, and produce a
short daily report that blends accountability tracking, idea surfacing,
and reflective coaching — the way a good 1:1 partner would look at this
file with the user.

**This is a report the user actually reads every morning, not a
transcript of your reasoning.** Default to too short rather than too
long. Cut connective/hedging phrases entirely — "worth noting", "it's
worth", "this represents", "what stands out is" — just state the fact.
One line per bullet. No paragraphs unless a single idea genuinely needs
2 sentences, and even then, 2 is the ceiling. If a section would just
restate something from yesterday's analysis with no new information,
drop it — don't re-explain context the user already read once.

The file is the user's external brain: work tasks (GovSpend/AIP), a side
project (Mergi), and personal/family notes, organized into a `Done` log,
a `Kanban` (Today / Tomorrow / This Week / Backlog), and a `Resoluções
Semanal` weekly reflection block. Treat all of it as fine to read and
reason about locally — no need to redact or split out personal content.

---

## Context: how the user actually works

This comes from a quarterly self-review the user did (Jan-Jun), separate
from `📍.md` itself. It's the psychological lens behind the Kanban — use
it to make Stale items and Reflection sharper, not as new sections to
report on literally.

- **Two root systems.** Pomodoro (interrupting work-pressure buildup
  every ~90 min, before it peaks into stress-driven impulses) is the
  system that anchors *normal* days. The quinzenal review is the system
  that anchors *atypical* weeks (travel, chaos) — it's the one system
  that has never failed him in 3+ months. When work bleeds into
  everything else, the root cause is usually one of these two slipping,
  not a lack of willpower anywhere else.

- **Cascade of abandonment.** A legitimate pause (one rest day) turns
  into a justified absence (next day) turns into inertia (day after) —
  3 days and a system is dead. The fix that has worked for him is
  committing to specific times *before* the week starts (Sunday
  planning: which days for Jiu-Jitsu, what to advance on Mergi, what to
  write about — already mirrored in the `Resoluções Semanal` block).
  When flagging a stale item, consider whether it looks like day 1 of
  this cascade — worth a gentler nudge — versus something that's been
  dead for a week.

- **Sleep is the deepest root cause.** Wake time affects the whole
  morning routine (meditation, reading, cardio); no fixed bedtime means
  wake time is at the mercy of the night before. He deliberately does
  **not** want this turned into a hard resolution/metric — it's a
  supporting condition, not a goal to chase. Don't propose adding it as
  a tracked item; just weigh it in when other mornings-based items
  (reading, meditation, cardio) look inconsistent.

- **Weight goal:** currently working toward 80kg via daily-ish HIIT
  cardio (treadmill sprints) plus Jiu-Jitsu 3-4x/week, tracked with a Mi
  Band. If cardio/weigh-in mentions show up in the diff, that's worth
  surfacing in Progress; if they're absent for several days where they'd
  normally appear, that's a legitimate stale/reflection candidate.

- **Career:** actively applying to Staff Engineer roles externally
  (alongside the day job) as a deliberate, planned move — not something
  to read as disengagement from GovSpend/AIP work. Track application
  activity and follow-ups the same way other Work items are tracked.

- **Reactivity is the core psychological theme**, not just a
  productivity gap. He's explicitly working against being destabilized
  by other people and against ruminating/adding imagined suffering to
  raw events. He is harsh with himself by default — reviews skew toward
  what went wrong, rarely pausing to register what went well as
  something enjoyed rather than just completed. In Reflection, it's
  worth occasionally asking him to savor something that actually went
  well, not only interrogating gaps.

---

## Step 1 — Determine today's date and day of week

Run `date +%Y-%m-%d` and `date +%A` via Bash first, before reading
anything else. Don't infer the date from ambient context — get it
explicitly, since this skill also runs headlessly via cron where that
matters.

The user does not work weekends. This changes both what to say and how
hard to push:

- **Saturday/Sunday:** Don't flag GovSpend/AIP work tasks in Today/
  Tomorrow as stale or overdue just because they weren't touched — that's
  expected, not a gap. Personal/Mergi/health items still count normally.
  Next actions (Step 3) should be personal/Mergi-only on weekends, not
  "catch up on work."
- **Monday:** The most recent Done-log entries span the weekend gap —
  don't treat Friday→Monday as a stale streak. This is also when
  `Resoluções Semanal` is meant to be reviewed, so lean into Reflection
  more than other days.
- **Tue-Fri:** Normal rules apply.

---

## Step 2 — Read the current file, prior context, and find yesterday's snapshot

Read `~/source/@cron/📍.md`.

Read `~/source/@cron/log.txt` if it exists — this is a running, agent-facing
log written by past runs of this skill (see Step 7). It is not something
the user reads day to day; it's how one run tells the next one what it
learned. Treat anything in it as working context: open questions a past
run wasn't sure about, judgment calls it made and why, patterns it was
tracking across multiple days, or corrections ("the user clarified X,
don't flag it as stale again"). Let it inform Step 3, especially Stale
items and Reflection.

List `~/source/@cron/analysis/` and read the last 7 days of analysis files
(`YYYY-MM-DD-analysis.md`) that exist there, oldest to newest. This is
the user-facing output of past runs — use it, alongside `log.txt`, as
context for today's run: don't repeat a reflection question that was
already asked and answered, notice when something flagged as stale
earlier in the week finally moved (call that out explicitly, it's a real
win), and let multi-day threads (e.g. a stretch of low Mergi activity, a
recurring stress pattern) build across the week instead of resetting
each day. If fewer than 7 exist, use whatever is there — don't treat a
short history as an error.

List `~/source/@cron/snapshots/`. Snapshots are named `YYYY-MM-DD.md`. Find
the most recent snapshot strictly before today's date.

- **If no prior snapshot exists** (first run ever): skip the diff step,
  and instead produce an orientation-style analysis — summarize the
  current state of Today/Tomorrow/This Week/Backlog, and note anything
  that looks stuck or contradictory. Say explicitly in the output that
  this is the first run so there's no diff yet.

- **If a snapshot exists**: diff the current file content against it
  (a simple text diff is enough — `diff -u` via Bash, or reason over the
  two texts directly). Use the diff as the primary input for Step 3.

Also list up to 7 days of snapshots (not just yesterday's) — these feed
the staleness check in Step 3.

---

## Step 3 — Build the analysis

**Hard budget: the whole report should read in under a minute.** Target
150-250 words total across all sections combined. Every section below is
a bullet list, not prose. One line per bullet. If a section has nothing
new to say, omit the heading entirely — don't write "nothing to report."

Produce these sections, in this order:

### 1. Progress
What moved from unchecked to checked (`- [ ]` → `- [x]`) since yesterday.
Name the actual task. Max 5 bullets — if there are more, group by
Work/Mergi/Pessoal instead of listing all of them.

### 2. Next actions
**The most important section.** A ranked list of 3-5 concrete things to
do next, ordered by priority. Not a restatement of everything in Today/
Tomorrow — a genuine cut: given what moved, what's stale, what's new,
and what day of the week it is, what should the user actually act on
next? Each bullet is one action, specific enough to start immediately
(not "work on Mergi" but "fix the split-diff syntax highlight bug").
Weekday-aware: on weekends this list is personal/Mergi-only, never
GovSpend/AIP work.

### 3. New ideas
New `|>` thoughts, new bullets under Tomorrow/This Week/Backlog, or new
freeform notes in `1:1 Notes`. One line each. Only note a connection to
an existing idea if it's genuinely non-obvious — don't force it.

### 4. Stale
Checklist items in Today/Tomorrow unchanged and unchecked across 3+
snapshots (2 is enough if tagged urgent). One line each, name the item
and how many days. Skip GovSpend/AIP items here on Mon if the gap is
just the weekend.

### 5. Reflection
**One question, not a menu.** Pick the single sharpest angle from
`Resoluções Semanal`, the diff, or something worth savoring rather than
fixing (see the "how the user actually works" context above). Monday
gets more room here since that's the weekly reset; other days, one
short question is enough — sometimes none if nothing stands out.

### 6. Cleanup (only if genuinely warranted)
One-line suggestions when something in Backlog/This Week looks done, or
a `Done` week block needs archiving. Phrase as "remove/move X?" — never
edit `📍.md` directly.

---

## Step 4 — Write the analysis file

Write the report to `~/source/@cron/analysis/YYYY-MM-DD-analysis.md`
(today's date). Plain markdown, the section headers above, nothing else
— no preamble, no closing summary restating what's above.

---

## Step 5 — Save today's snapshot

Copy the current `📍.md` content verbatim to
`~/source/@cron/snapshots/YYYY-MM-DD.md` (today's date). This is what
tomorrow's run will diff against. Always do this last, after the
analysis is written, so a failure mid-analysis doesn't leave a snapshot
without a matching report.

---

## Step 6 — Notify

Send a macOS notification so the user knows the analysis is ready without
having to check manually:

```bash
osascript -e 'display notification "Daily brain analysis ready" with title "Daily Brain" subtitle "'"$(date +%Y-%m-%d)"'"'
```

---

## Step 7 — Append to the run log

Append an entry to `~/source/@cron/log.txt` (create it if missing) — this
is for the *next run of this skill*, not for the user. Keep it short
(a few lines), plain text, prefixed with today's date:

```
## YYYY-MM-DD
- <anything the next run should know: an ambiguous judgment call and why
  you made it, something you noticed spanning multiple days that hasn't
  fully resolved yet, a correction the user gave you mid-run, or a note
  about how you handled an edge case today>
```

Only write something if there's an actual handoff worth making — don't
pad this with a restatement of the day's analysis. If nothing unusual
happened and the run was routine, a one-liner ("routine run, nothing to
flag") is enough. Always append (never overwrite) so the log accumulates
as a history of the skill's own reasoning across runs.

---

## Edge cases

- **Run more than once same day**: if `~/source/@cron/snapshots/YYYY-MM-DD.md`
  for today already exists, still overwrite it with the latest content at
  Step 5 (idempotent), but diff against the same "yesterday" baseline as
  before, not against today's own earlier snapshot.
- **Non-interactive/cron invocation**: there is no user to ask
  clarifying questions. Make reasonable judgment calls and note any
  assumptions briefly in the output rather than stopping to ask.
- **Empty or missing snapshots directory**: treat as first run (see
  Step 2).
- **Weekend runs**: the cron job itself only fires on weekdays (see the
  launchd schedule), but if the user triggers this manually on a
  Saturday/Sunday, apply the weekend rules from Step 1 anyway.
