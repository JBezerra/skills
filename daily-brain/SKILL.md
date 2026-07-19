---
name: daily-brain
description: >
  Analyzes the day-over-day diff of the user's personal brain-dump file
  (~/source/@cron/daily-brain/📍.md) — a mix of work tasks, ideas, and personal/life
  notes organized as a rolling Kanban. Produces a blended daily analysis
  covering where the day diverged from the plan, pattern-level insights,
  a priority order for today, stale items that keep rolling over
  unresolved, and light coaching-style reflection questions. Trigger whenever the user says "/daily-brain", "run my daily
  brain analysis", "diff my notes file", or similar. Also the target of a
  daily 7am cron job — when invoked non-interactively (no user turn to
  respond to), just perform the full run and finish; there is no one to
  ask follow-up questions.
---

# Daily Brain Analysis

Analyze `~/source/@cron/daily-brain/📍.md` against yesterday's snapshot, and produce a
short daily report that blends accountability tracking, idea surfacing,
and reflective coaching — the way a good 1:1 partner would look at this
file with the user.

**This is a report the user reads every morning. It should take one
minute to read.** The whole report is ~25 lines. If it's longer, you're
restating the user's own file back to him instead of telling him
something he doesn't know.

**Never tell the user what he already knows.** He wrote `📍.md`. He
checked those boxes. Listing his tasks back to him is worth nothing. Every
line must add something he couldn't get by rereading his own file: a
pattern across days, a contradiction, a consequence, a ranking, a
question.

### The two rules that matter most

**1. Say each thing exactly once.** A fact, item, or pattern appears in
ONE section of the report and nowhere else. If the quinzenal is the
subject of an Insight, it does not also appear in Priority order,
Cleanup, or Reflection. Pick the section where it lands hardest and leave
it there. Before writing the file, reread it and delete every second
mention. Recent reports said the same thing three times in three
sections — that is the single worst failure mode of this skill.

This is about repetition *within one report*. Repeating across *days* is
different and still correct: if a stale item or unresolved pattern is
still live today, say it again today. Only drop a cross-day callback if
it's been resolved or the user said to stop flagging it (see Standing
corrections below).

**2. One sentence per bullet.** Not three. Not a sentence plus an
explanation plus a justification. If a bullet needs a second sentence to
survive, it gets one, and that's the ceiling. Reflection is the only
exception (2-3 sentences plus the question).

### How to write it

Plain and short. Write the way you'd explain it to a friend, not the way
a consultant writes a slide deck.

- **Everyday words.** No jargon, no abstract metaphors, no invented
  labels. Say "it's hard to get started on it", not "it's an
  activation-energy problem". Say "Today got shorter", not "Today
  decongested". Say "nothing makes you open it", not "no forcing
  function". If a smart friend would have to reread a sentence, rewrite
  it.
- **No rhetorical flourish.** Drop the writerly closers ("Same outcome,
  opposite mechanism", "just through different doors"). They read as
  clever, not useful. State the thing and stop.
- **Cut hedging and connective filler**: "worth noting", "it's worth",
  "this represents", "that said".
- **Prefer commas and periods over em-dashes.** An occasional dash is
  fine; never stack two or three in one sentence.
- **Concrete over clever.** Name the actual task and the actual number of
  days. Describe the behavior, not the psychology theory behind it, even
  when the pattern is real.

### Standing corrections

Things the user has told this skill to stop doing. These are permanent.

- **The all-caps LinkedIn note at the top of `📍.md` stays.** Never flag
  it in Cleanup, never ask about the missing header, never mention it at
  all.

The file is the user's external brain: work tasks (GovSpend/AIP), a side
project (Mergi), and personal/family notes, organized into a `Done` log,
a `Kanban` (Today / Tomorrow / This Week / Backlog), and a `Resoluções
Semanal` weekly reflection block. Treat all of it as fine to read and
reason about locally — no need to redact or split out personal content.

**`Resoluções Semanal` is food for thought, not a to-do list.** These are
reflection prompts the user keeps for himself, not tasks to finish. It is
completely fine for it to sit blank. Never flag it as stale, overdue, or
"unanswered", never count it as an unfinished item, and never push the
user to fill it in. At most, one of its themes can *inspire* a Reflection
question — but its blankness is never itself the problem.

**Not everything the user does is logged here** — especially personal,
non-work activity (Jiu-Jitsu, reading, time with Thata/Rose) often
happens without a corresponding entry. Treat absence from the file as
weak evidence, not proof something didn't happen. Phrase staleness and
gaps as questions/observations ("no Jiu-Jitsu logged in 5 days — still
happening, just untracked, or actually paused?") rather than flat
assertions that something didn't occur.

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
  Priority order (Step 4) should be personal/Mergi-only on weekends, not
  "catch up on work."
- **Monday:** The most recent Done-log entries span the weekend gap —
  don't treat Friday→Monday as a stale streak. This is also when
  `Resoluções Semanal` is meant to be reviewed, so lean into Reflection
  more than other days.
- **Tue-Fri:** Normal rules apply.

---

## Step 2 — Read the current file, prior context, and find yesterday's snapshot

Read `~/source/@cron/daily-brain/📍.md`.

Read `~/source/@cron/daily-brain/log.txt` if it exists — this is a running, agent-facing
log written by past runs of this skill (see Step 8). It is not something
the user reads day to day; it's how one run tells the next one what it
learned. Treat anything in it as working context: open questions a past
run wasn't sure about, judgment calls it made and why, patterns it was
tracking across multiple days, or corrections ("the user clarified X,
don't flag it as stale again"), and any priorities the user gave in a
past interactive run (see Step 3 below). Let it inform Step 4,
especially Insights, Stale items, and Reflection.

List `~/source/@cron/daily-brain/analysis/` and read the last 7 days of analysis files
(`YYYY-MM-DD-analysis.md`) that exist there, oldest to newest. This is
the user-facing output of past runs — use it, alongside `log.txt`, as
context for today's run: don't repeat a reflection question that was
already asked and answered, notice when something flagged as stale
earlier in the week finally moved (call that out explicitly, it's a real
win), and let multi-day threads (e.g. a stretch of low Mergi activity, a
recurring stress pattern) build across the week instead of resetting
each day. If fewer than 7 exist, use whatever is there — don't treat a
short history as an error.

List `~/source/@cron/daily-brain/snapshots/`. Snapshots are named `YYYY-MM-DD.md`. Find
the most recent snapshot strictly before today's date.

- **If no prior snapshot exists** (first run ever): skip the diff step,
  and instead produce an orientation-style analysis — summarize the
  current state of Today/Tomorrow/This Week/Backlog, and note anything
  that looks stuck or contradictory. Say explicitly in the output that
  this is the first run so there's no diff yet.

- **If a snapshot exists**: diff the current file content against it
  (a simple text diff is enough — `diff -u` via Bash, or reason over the
  two texts directly). Use the diff as the primary input for Step 4.

Also list up to 7 days of snapshots (not just yesterday's) — these feed
the staleness check in Step 4.

---

## Step 2.5 — Fetch Readwise digest data

Call two Readwise MCP tools before building the analysis:

1. `reader_list_documents` with `location="new"`, `limit=5`, `response_fields=["title","author","reading_time","site_name"]` — note the total count returned and pick the first document as the suggested read.
2. `readwise_search_highlights` with `vector_search_term="Marcus Aurelius Meditations stoic discipline"` — from the results, pick ONE highlight that connects to something in today's diff or themes. Don't just return the first result; pick the one that lands.

Store both results; you'll use them in sections 7 and 8 of the analysis.

If either MCP call fails, skip that section silently — don't surface the error in the report.

---

## Step 3 — Ask about priorities (interactive runs only)

If a human is actually present to respond in this session (not a
headless cron invocation), ask one brief, specific question about
current priorities — grounded in something genuinely ambiguous from the
file or the diff (e.g. "bigger focus this week: Mergi or the Staff Eng
applications?"), not a generic "what are your priorities?" Keep it to
one question.

Append the answer to `~/source/@cron/daily-brain/log.txt` immediately, under its own
heading:

```
## YYYY-MM-DD — priorities (user-provided)
- <what the user said>
```

Use this when building Priority order in Step 4, today and in future runs.

**Skip this step entirely on headless/cron runs** — there's no one to
ask. On those runs, rely on whatever priority notes already exist in
`log.txt` from past interactive runs.

---

## Step 4 — Build the analysis

Every section is a bullet list, not prose. One sentence per bullet (see
"The two rules that matter most" above). If a section has nothing to say,
omit the heading — don't write "nothing to report." Omitting sections is
normal and good; a 12-line report on a quiet day is a success, not a
failure.

Assign each fact to exactly one section before you write. If two sections
both want the quinzenal, pick one.

Produce these sections, in this order:

### 1. Progress
**Divergence only.** Compare what the file said the user planned (times,
training days, the week's stated intentions from Monday's planning) against
what actually got checked off. Report only where they differ, in 2-4 short
lines: what slipped, what moved instead, what got struck through. Close
with one line if the rest matched ("Everything else went as planned").

Do NOT list completed tasks. He checked those boxes himself. If nothing
diverged, omit the section entirely.

Example of the whole section, at the right length:

```
Planned Jiu-Jitsu 19h15 + cardio at 6h.
Got: cardio at 18h, wake-at-6h struck through.
Everything else went as planned.
```

### 2. Insights
**The section that carries the report.** Everything else is scaffolding
around this. Given the "how the user actually works" context above, the
last 7 days of analyses, `log.txt`, and today's diff, what do you see that
he doesn't?

This is analysis from someone watching his patterns, not a summary. What
belongs here: a pattern repeating across the week he hasn't named himself,
a tension between two stated goals, a consequence he hasn't connected, a
read on whether a stale item is day 1 of the cascade or genuinely dead.

What does NOT belong here: anything he could see by rereading his own file.
"Mergi got narrowed" is not an insight, it's a diff. "Mergi got narrowed
the same week you picked AI-Native, and it's the only thing on the board
marked in progress" is an insight.

2-3 bullets, the strongest ones only. One sentence each, two if it truly
needs it. Skip the section if you have nothing beyond the obvious — a
manufactured insight is worse than no section.

### 3. Priority order
**Rank what's already on his board. Don't invent tasks and don't restate
them with explanations.** He knows what the tasks are. What he doesn't
know is which one to open first.

A numbered list of what's in Today, ordered. Name the item in a few words,
then a clause on why it's in that slot (time-boxed, blocks something else,
about to go stale, cheap to close). One line each, 3-5 lines total. Cut
anything from Today that shouldn't get attention today, and say so in one
line if the cut is interesting.

Weekday-aware: on weekends this is personal/Mergi-only, never GovSpend/AIP.

Example of the right shape and length:

```
1. Jiu-Jitsu 18h15 — fixed time, everything else bends around it.
2. GS-14620 — only concrete work item in Today.
3. Mergi AI-First Roadmap — day 2 keeps it alive.
4. Levar carro em oficina — closes Tuesday's quote.

Skipping the MCP-thoughts block: it's a thinking task and will eat the
morning.
```

### 4. Stale
Checklist items in Today/Tomorrow unchanged and unchecked across 3+
snapshots (2 is enough if tagged urgent). One line each, name the item
and how many days. Skip GovSpend/AIP items here on Mon if the gap is
just the weekend. Never list `Resoluções Semanal` or its weekly questions
here — it's reflection, not a task (see above). Remember not everything
is logged — phrase these as questions where the item is plausibly
untracked-but-happening, not flat "you didn't do X."

### 5. Cleanup (only if genuinely warranted)
Look across the *whole document*, not just the Done log, for things that
should be tidied up. One-line suggestions for:

- Backlog / This Week items that look already done or no longer relevant.
- Items that have sat in the same place, untouched, for a long time —
  dead weight that's cluttering the board rather than waiting on action.
- Very old notes, finished projects, or stale `1:1 Notes` that could be
  archived or deleted.
- `Done` week blocks old enough to archive.

Phrase every suggestion as a question the user can act on ("remove X?",
"move X to Backlog?", "archive last week's Done block?") — never edit
`📍.md` directly. This is different from Stale: Stale is about active
items he should *do*; Cleanup is about clutter he should *clear*. Skip the
section if the document is already tidy, and never list something here
that a stale item or an insight already covered.

### 6. Reflection
**One question, with a short setup.** Two or three plain sentences of
context, then the single sharpest question. Not a paragraph, not a menu
of questions. Pick the angle from the diff, a recurring pattern, or
something worth savoring rather than fixing (see the "how the user
actually works" context above).

The setup must be new context, not a recap of an Insight. If the sharpest
question is about something already covered above, either ask it there and
drop this section, or find a different angle. Monday gets a little more
room since that's the weekly reset; other days keep it tight, and some
days nothing stands out — that's fine, skip it.

### 7. Leitura
Two lines, no more. First line: how many articles are waiting in the inbox. Second line: "Próximo: [título] — [autor] ([reading_time])" using the first document from Step 2.5. Skip the section if the MCP call failed.

### 8. Lembrete Estoico
One Marcus Aurelius highlight as a blockquote, no commentary, no attribution line (it's always Marco Aurélio). Pick from Step 2.5. Skip if the call failed.

---

## Step 5 — Cut it down, then write the analysis file

Draft the report, then edit it before writing. Every past run of this
skill has been too long and too repetitive, so treat this pass as
mandatory, not optional polish.

Go through the draft and:

1. **Delete every second mention.** For each item or pattern, find all the
   places it appears. Keep the strongest one, cut the rest. No exceptions.
2. **Cut every bullet to one sentence.** If it's three sentences, two of
   them are justification the user didn't ask for.
3. **Delete any line that only restates `📍.md`.** If he'd learn the same
   thing by rereading his own file, it goes.
4. **Delete the clever closers.** Any sentence that exists for rhythm
   rather than information.
5. **Count the lines.** Over ~25 and you haven't cut enough. Go again.

Then write the report to
`~/source/@cron/daily-brain/analysis/YYYY-MM-DD-analysis.md` (today's date).
Plain markdown, the section headers above, nothing else — no preamble, no
closing summary restating what's above.

If running interactively inside a sandboxed Claude Code session, prefer
writing via Bash (e.g. `cat > file <<EOF ... EOF`) over the Write tool —
Write has been observed to report success while silently not persisting
files outside the sandbox's allowed paths. Verify with `ls`/`cat` after
writing. This doesn't apply to the actual cron invocation, which runs
unsandboxed.

---

## Step 6 — Save today's snapshot

Copy the current `📍.md` content verbatim to
`~/source/@cron/daily-brain/snapshots/YYYY-MM-DD.md` (today's date) via `cp`. This is
what tomorrow's run will diff against. Always do this last, after the
analysis is written, so a failure mid-analysis doesn't leave a snapshot
without a matching report. Same sandbox caveat as Step 5 applies if
running interactively.

---

## Step 7 — Notify and open the analysis

Send a macOS notification so the user knows the analysis is ready without
having to check manually:

```bash
osascript -e 'display notification "Daily brain analysis ready" with title "Daily Brain" subtitle "'"$(date +%Y-%m-%d)"'"'
```

Then open today's analysis file in the editor:

```bash
code "$HOME/source/@cron/daily-brain/analysis/YYYY-MM-DD-analysis.md"
```

(`code` on this machine is wired to the Cursor CLI, not VS Code — this
opens Cursor.) Do this last, after the file is fully written.

---

## Step 8 — Append to the run log

Append an entry to `~/source/@cron/daily-brain/log.txt` (create it if missing) — this
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

- **Run more than once same day**: if `~/source/@cron/daily-brain/snapshots/YYYY-MM-DD.md`
  for today already exists, still overwrite it with the latest content at
  Step 6 (idempotent), but diff against the same "yesterday" baseline as
  before, not against today's own earlier snapshot.
- **Non-interactive/cron invocation**: there is no user to ask
  clarifying questions. Make reasonable judgment calls and note any
  assumptions briefly in the output rather than stopping to ask.
- **Empty or missing snapshots directory**: treat as first run (see
  Step 2).
- **Weekend runs**: the cron job itself only fires on weekdays (see the
  launchd schedule), but if the user triggers this manually on a
  Saturday/Sunday, apply the weekend rules from Step 1 anyway.
