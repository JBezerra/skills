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

**This is a report the user reads every morning — make it fast to read.**
Aim for a 2-3 minute read, not 5. The value is in the signal, not the
word count: keep every real insight, but say it in the fewest, plainest
words (see "How to write it" below).

Cut connective/hedging phrases that add no information ("worth noting",
"it's worth", "this represents"). Never cut something *substantive* just
because it repeats: if a stale item, a recurring pattern, or an open
question from a prior day is still unresolved, say it again. Persistent
unresolved things are exactly what this skill exists to keep in front of
the user — say it concisely, but say it. Only drop a callback if it's
been explicitly resolved or the user has said to stop flagging it (check
`log.txt`). When in doubt, include it; the user will tell you if
something isn't worth repeating.

### How to write it

Plain and short. Write the way you'd explain it to a friend, not the way
a consultant writes a slide deck.

- **Short sentences, one idea each.** If a sentence stacks three clauses
  with dashes, split it into separate sentences.
- **Everyday words.** No jargon, no abstract metaphors, no invented
  labels. Say "it's hard to get started on it", not "it's an
  activation-energy problem". Say "Today got shorter", not "Today
  decongested". Say "nothing makes you open it", not "no forcing
  function". If a smart friend would have to reread a sentence, rewrite
  it.
- **Prefer commas and periods over em-dashes.** An occasional dash is
  fine; never stack two or three in one sentence.
- **Concrete over clever.** Name the actual task and the actual number of
  days. Describe the behavior, not the psychology theory behind it, even
  when the pattern is real.

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
  Next actions (Step 4) should be personal/Mergi-only on weekends, not
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
log written by past runs of this skill (see Step 8). It is not something
the user reads day to day; it's how one run tells the next one what it
learned. Treat anything in it as working context: open questions a past
run wasn't sure about, judgment calls it made and why, patterns it was
tracking across multiple days, or corrections ("the user clarified X,
don't flag it as stale again"), and any priorities the user gave in a
past interactive run (see Step 3 below). Let it inform Step 4,
especially Insights, Stale items, and Reflection.

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
  two texts directly). Use the diff as the primary input for Step 4.

Also list up to 7 days of snapshots (not just yesterday's) — these feed
the staleness check in Step 4.

---

## Step 3 — Ask about priorities (interactive runs only)

If a human is actually present to respond in this session (not a
headless cron invocation), ask one brief, specific question about
current priorities — grounded in something genuinely ambiguous from the
file or the diff (e.g. "bigger focus this week: Mergi or the Staff Eng
applications?"), not a generic "what are your priorities?" Keep it to
one question.

Append the answer to `~/source/@cron/log.txt` immediately, under its own
heading:

```
## YYYY-MM-DD — priorities (user-provided)
- <what the user said>
```

Use this when ranking Next Actions in Step 4, today and in future runs.

**Skip this step entirely on headless/cron runs** — there's no one to
ask. On those runs, rely on whatever priority notes already exist in
`log.txt` from past interactive runs.

---

## Step 4 — Build the analysis

Every section below is a bullet list, not prose — one line per bullet,
no filler sentences. But favor completeness of insight over brevity: if
there's a genuine pattern, a persistent unresolved item, or something
worth connecting across days, include it even if the section runs long.
If a section has nothing to say, omit the heading — don't write "nothing
to report."

Produce these sections, in this order:

### 1. Progress
What moved from unchecked to checked (`- [ ]` → `- [x]`) since yesterday.
Name the actual task. Group by Work/Mergi/Pessoal if there's enough to
group.

### 2. Insights
**The section where you actually think, not just report.** Given
everything you know about the user (the "how the user actually works"
context above, the last 7 days of analyses, `log.txt`, and today's
diff), what pattern, connection, or concern is worth naming? This is
different from Next Actions (concrete tasks) and Reflection (one
question) — this is your read of what's going on, stated directly, even
if it's not actionable today. Examples of what belongs here: a pattern
repeating across the week that the user hasn't named themselves, a
tension between two stated goals, a connection between something in
Today and something in This Week/Backlog, a read on whether a stale item
looks like early cascade vs. genuinely dropped. Keep it to the 2-3
strongest reads, each a short bullet in plain words — not four long ones.
Skip it if you genuinely have nothing beyond the obvious; don't
manufacture an insight to fill the section.

### 3. Next actions
A ranked list of 3-5 concrete things to do next, ordered by priority.
Not a restatement of everything in Today/Tomorrow — a genuine cut: given
what moved, what's stale, what's new, today's Insights, any priorities
noted in `log.txt` (Step 3), and the day of the week, what should the
user actually act on next? Each bullet is one action, specific enough to
start immediately (not "work on Mergi" but "fix the split-diff syntax
highlight bug"). Weekday-aware: on weekends this list is personal/
Mergi-only, never GovSpend/AIP work.

### 4. New ideas
New `|>` thoughts, new bullets under Tomorrow/This Week/Backlog, or new
freeform notes in `1:1 Notes`. One line each. Only note a connection to
an existing idea if it's genuinely non-obvious — don't force it.

### 5. Stale
Checklist items in Today/Tomorrow unchanged and unchecked across 3+
snapshots (2 is enough if tagged urgent). One line each, name the item
and how many days. Skip GovSpend/AIP items here on Mon if the gap is
just the weekend. Never list `Resoluções Semanal` or its weekly questions
here — it's reflection, not a task (see above). Remember not everything
is logged — phrase these as questions where the item is plausibly
untracked-but-happening, not flat "you didn't do X."

### 6. Reflection
**One question, with a short setup.** Two or three plain sentences of
context, then the single sharpest question. Not a paragraph, not a menu
of questions. Pick the angle from the diff, a recurring pattern, or
something worth savoring rather than fixing (see the "how the user
actually works" context above). Monday gets a little more room since
that's the weekly reset; other days keep it tight, and some days nothing
stands out — that's fine, skip it.

### 7. Cleanup (only if genuinely warranted)
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
`📍.md` directly. This is different from Stale (Step 5): Stale is about
active items you should *do*; Cleanup is about clutter you should *clear*.
Skip the section if the document is already tidy.

---

## Step 5 — Write the analysis file

Write the report to `~/source/@cron/analysis/YYYY-MM-DD-analysis.md`
(today's date). Plain markdown, the section headers above, nothing else
— no preamble, no closing summary restating what's above.

If running interactively inside a sandboxed Claude Code session, prefer
writing via Bash (e.g. `cat > file <<EOF ... EOF`) over the Write tool —
Write has been observed to report success while silently not persisting
files outside the sandbox's allowed paths. Verify with `ls`/`cat` after
writing. This doesn't apply to the actual cron invocation, which runs
unsandboxed.

---

## Step 6 — Save today's snapshot

Copy the current `📍.md` content verbatim to
`~/source/@cron/snapshots/YYYY-MM-DD.md` (today's date) via `cp`. This is
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
code "$HOME/source/@cron/analysis/YYYY-MM-DD-analysis.md"
```

(`code` on this machine is wired to the Cursor CLI, not VS Code — this
opens Cursor.) Do this last, after the file is fully written.

---

## Step 8 — Append to the run log

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
