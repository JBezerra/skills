---
name: apply-job
description: Produce a complete, tailored job application from a posting URL, covering the job description, application questions, a CV built from the latex-resume repo, drafted answers grounded in José's story bank, and a cover letter when one is asked for. Use whenever José pastes a job posting URL and wants to apply, says "apply to this", "tailor my resume for this role", "draft answers for this application", or invokes "/apply-job". Also trigger when he shares a job description and asks what he should say.
---

# Apply Job

You are assembling a real job application that José will submit under his own
name. Two failure modes matter more than anything else here, and every rule below
exists to prevent one of them:

1. **Fabrication.** A metric you invented reads as confident and correct, and he
   will not catch it before it reaches a recruiter. It is a lie on a document he
   signs, and it surfaces in an interview when he cannot back it up.
2. **Submitting something.** You will be inside a live application form. A
   misplaced click sends an unfinished application that cannot be recalled.

## Hard rules

**Never submit anything.** You may read an application form. You may not click
Submit, Apply, Continue-to-submit, or any button that advances the application.
Do not upload files. Do not type into form fields unless José explicitly asks you
to fill the form in a later turn, and even then you stop before submit.

**Never invent a fact.** Every claim in the CV, the answers, and the cover letter
must trace to `roles.json` or the story banks. Rephrasing is fine. A number that
is not in the source files is not. If the posting wants something José does not
have, say so and let him decide how to handle it.

**Stay out of the logistics fields.** Desired pay, date available, address, city,
state, ZIP, country, work authorisation, visa status, notice period, relocation,
referral source. José fills these in himself at submit time. Do not ask him for
them, do not draft them, do not put them in a table for him to review. Your job
is only the parts where his story is the answer: the open-ended questions, the CV,
and a cover letter when one is asked for. List logistics fields in `questions.md`
only as a bare inventory of what the form will ask, with no values and no
follow-up questions.

**Ask before acting.** Confirm the parsed company and role before creating
anything on disk. Confirm the question list before drafting. Show him the
finished artifacts before he sends them anywhere.

## Sources

| What | Where |
|---|---|
| CV source of truth | `~/source/latex-resume/` (obey its `AGENTS.md`) |
| Career facts | `~/source/latex-resume/roles.json` |
| Narrative stories | `~/source/@workflows/apply-job/story-bank.json` |
| STAR stories | `~/source/@workflows/apply-job/star-story-bank.json` |
| Output | `~/source/@workflows/apply-job/applications/<company>/` |

## Output shape

```
applications/anthropic/
  job-description.md
  questions.md
  application.md                            # questions + final answers
  changes.txt                               # CV diff vs the canonical resume
  cover-letter.md                           # only if the application asks
  anthropic-staff-software-engineer.pdf     # copy of the built CV
```

The CV itself is built by the `latex-resume` repo, not here. Its `.tex` stays in
`~/source/latex-resume/applications/<slug>.tex` as the frozen record of what was
sent, per that repo's own rules. Only a **copy** of the built PDF lands in the
application folder.

## Phase 1: Capture the posting

Take the URL from José. If he pasted a job description instead of a URL, skip the
browser and use what he gave you.

Open it with agent-browser: `agent_browser_open`, then `agent_browser_snapshot` or
`agent_browser_read` to get the content. Job boards render client-side, so read
the snapshot rather than assuming the raw HTML holds the text.

Extract: company, role title, team, location, work arrangement, seniority,
requirements, responsibilities, compensation if stated.

**File name**: the company, the role, and the slug you intend to
use (`<company>-<role-kebab>`, e.g. `anthropic-staff-software-engineer`). The slug
names both the `.tex` and the PDF, so getting it right now avoids a rename later.

Once confirmed, create the folder and write `job-description.md`: the full posting
text, with a short front-matter block carrying company, role, location, URL, and
the date captured.

## Phase 1b: Find out what the company actually builds

Do this before any positioning decision. Search the web for the company: what the
product is, who buys it, what the named product areas are, stage and funding,
anything shipped recently. Read their own site and any recent posts. A
`general-purpose` agent is a good fit if it needs more than a couple of fetches.

Then read the posting again for its **product pillars**, the section that lists
the surfaces or teams the hire could land on. That list tells you what the company
thinks it is. The job title does not.

**This step exists because of a real failure.** Stable was tailored as a
generic product role: customer empathy, end-to-end ownership, business context.
The AI work was deliberately demoted because "Product Engineer" did not sound like
an AI title. Stable is an AI mail company. Their posting names "Automation & AI,
LLMs and ML models that route mail, classify documents, extract data, and trigger
workflows" as one of four product pillars, and the role description talks about
training a check-detection model. The whole application had to be redone. The
signal was in the posting the entire time and the title drowned it out.

So: **never derive positioning from the role title.** "Product Engineer" at an AI
company is a different job from "Product Engineer" anywhere else. Derive it from
what the company sells and what its pillars say.

Two things come out of this phase:

1. A short `## Company` section appended to `job-description.md`: what they build,
   who buys it, the product pillars verbatim, stage, and anything that changes
   how José should be positioned.
2. A positioning call, stated to José before drafting, in the form "lead with X,
   support with Y, because their pillars say Z." He corrects it there, which is far
   cheaper than after a full run.

This phase also feeds "why this company", which the story bank cannot answer alone.

## Phase 2: Capture the questions

Open-ended questions are almost never in the posting. They live in the
application form, usually behind an Apply button on Greenhouse, Lever, Ashby, or
Workday.

Navigate to the form and read it. Take a snapshot and enumerate every field:
label, whether it is required, any stated word or character limit, and the field
type. What you are hunting for is the **free-text questions**. Logistics fields
get listed as a bare inventory and nothing more, per the hard rule above.

Some forms have no open-ended questions at all. BambooHR postings often do not.
When that happens, say so plainly and move on. The CV becomes the whole
deliverable. Do not manufacture questions to have something to answer.

If the form needs a login, or the site blocks the browser, or the questions are
simply not reachable: **say so plainly and ask José to paste them.** Do not
invent a plausible set of questions. A guessed question list produces polished
answers to questions nobody asked.

Write `questions.md`: every question, numbered, with its stated limit and whether
it is required.

**Stop and confirm.** Show him the open-ended questions and ask anything
genuinely ambiguous about the role or how he wants to be positioned. Do not ask
about salary, availability, or address. Those are his to fill at submit time.

## Phase 3: Tailor and draft

Now run the workflow. It tailors the CV and drafts every answer in parallel, then
fact-checks each answer against the source files with a separate adversarial
agent.

Pass `args` as a real object. A JSON-encoded string destructures to `undefined`
on every field, and the agents then work from the literal text "undefined" and
burn a whole run before failing. The script guards against this now, but the
right call site still matters.

```
Workflow({
  scriptPath: "~/source/@workflows/apply-job/tailor.workflow.js",
  args: {
    company, role, slug,
    jdPath:        "<abs path to job-description.md>",
    questionsPath: "<abs path to questions.md>",
    questions: [{ question: "...", limit: "300 words" }],
    needsCoverLetter: <true only if the posting or form asks for one>,
    resumeRepo: "/Users/josebezerra/source/latex-resume",
    storyBank:  "/Users/josebezerra/source/@workflows/apply-job/story-bank.json",
    starBank:   "/Users/josebezerra/source/@workflows/apply-job/star-story-bank.json",
    personalFacts: "<what José answered in Phase 2>"
  }
})
```

Pass absolute paths, and pass `questions` as a real array, not a JSON string.

The workflow returns `needsUserInput`, `ungrounded`, and `gaps`. Do not bury
these. They are the parts that need a human.

## Phase 3b: Humanize

The workflow's first draft always sounds like an LLM wrote it. Do not hand it to
José in that state.

**Run `/humanizer` on every drafted answer.** Invoke the `humanizer` skill. It
catches the tells that make an application read as machine-written, and job
applications are the highest-stakes place for that to happen. Follow its draft,
audit, final loop and paste its final version into `application.md`.

The patterns it catches that show up most in these answers:

- **Manufactured punchlines (§31).** Every paragraph ending on a quotable closer.
  A single one is fine. Three in a row is a tell.
- **Negative parallelism (§9).** "It's not a latency regression, it's a double
  charge." "Moving toward the problem, not arriving with it solved."
- **Aphorism formulas (§32).** "X is that instinct aimed at Y."
- **Rhetorical openers (§33).** "Straight about the gaps:", "Honestly?"

## Phase 4: Build and assemble

The workflow's CV agent already ran `make`. Verify the PDF exists and the page
count did not grow, then copy it in:

```sh
cp ~/source/latex-resume/build/<slug>.pdf \
   ~/source/@workflows/apply-job/applications/<company>/<slug>.pdf
```

Write `application.md`: each question with its final answer, in form order, with
word counts so he can check limits at a glance. Flag any answer still awaiting a
personal fact. Write `cover-letter.md` only if one was requested.

**Write the answers as unwrapped paragraphs.** One paragraph is one long line, no
hard wrap at 80 columns. José copies these straight into a web textarea, and a
hard-wrapped paragraph pastes in with the line breaks baked in and looks broken to
whoever reads it. Wrap the surrounding prose in `application.md` normally. Only the
answer text itself stays unwrapped.

Record the draft history under the answer: what each earlier version got wrong and
why the final one is shaped the way it is. When José pushes back on a later
application, that history is what stops the same mistake being made twice.

### changes.txt

Write `changes.txt` in the same folder: a bullet list of what the tailored CV
changed relative to the **canonical** CV, meaning `resume.tex` built from
`roles.json`, not the previous application's variant. Every application diffs
against the same baseline, so two of them can be compared side by side.

One short sentence per change. No paragraphs, no explanation of the reasoning
behind a move unless the reason is not obvious from the change itself. José scans
this, he does not read it.

Cover, in this order: what the summary now leads with, what got reordered and where
it moved, what was **cut** and why, and the page count. Cuts matter most. A dropped
bullet is the thing he is most likely to want back, and the only record that it ever
existed is this file.

The workflow's resume agent already returns `changes`, `dropped`, and `gaps`. That
is the raw material. Compress it, do not re-derive it.

Commit the `.tex` in `latex-resume` so the record of what was sent is frozen. The
`apply-job` folder is not a git repo, so nothing to commit there.

## Phase 5: Report

Tell him:
- What was produced and where.
- **The contents of `changes.txt`**, in the reply itself, not just as a file path.
  This is the CV diff against the canonical resume. He should not have to open a
  file to see what changed on his own CV.
- **Any gap** between the posting and his actual experience. He needs to know
  where he is stretching before an interview, not after.
- **Any claim the verifier flagged as unsupported**, and what you did about it.
- The page count of the CV and whether anything was cut to fit.

Then stop. He submits. You do not.

## Judgement notes

**Answer length.** Respect a stated limit strictly. With no limit, aim for
**100-130 words**. That is shorter than feels right while drafting, and it is the
length José has actually approved. 250 words reads as padding.

A form may state its own preference, and it overrides this. Nango's asks for "1-3
genuine sentences" and warns that "AI-sounding responses disappoint". Draft to
whatever the form asks for.

**Story reuse.** Using the same story for two questions in one application is
usually a mistake. The bank has 21 narrative and 19 STAR entries, so there is
almost always a better fit than a repeat.

**"Why this company".** This is the one question the story bank cannot answer
alone, because it needs something specific about *them*. Pull it from the Phase 1b
research and the posting. If it still reads generic, ask José what actually draws
him to it. A generic answer here is worse than a short one.

If he declines to supply a reason and tells you to write one, do not invent a
feeling and attribute it to him. Derive the connection from `roles.json` instead:
find the pattern in his actual record that matches what the company builds, and
say that. For Stable it was automating operational work while a human keeps the
judgment call, which is genuinely the shape of Omnipresent, AllowMe and Propi.
That is inference from evidence, and he can confirm or reject it in one read.
Flag it once as an inference. Do not raise it again after he has heard it.

**Tone.** The story banks note: use "I" not "we", include data points, keep each
story self-contained. `latex-resume/AGENTS.md` carries the full writing rules and
the ban on the em dash character. Both apply to everything you write here.

**Do not tell his life story.** An open-ended question is not an invitation to
narrate his career. The drafting agent reaches for a long autobiographical
run-up, walking through roles and projects before it gets to the point. Answer the
question that was asked. Reach for his history only where a specific piece of it
is the answer, and then only the piece.

**Do not write it dramatic.** This is the correction José makes most often. The
drafting agent reaches for staccato openers ("Ten years in, I've never shipped
money movement."), sentences engineered to land, and paragraphs that each end on a
beat. It reads as a pitch deck. Plain declarative sentences that state the thing
are what he approves. If a sentence sounds like it wants to be quoted, rewrite it.

**Handle gaps once, at the end, framed forward.** Being honest about missing
experience is right, and the hard rule against fabrication requires it. Where the
drafts go wrong is placement and repetition. Never open on a gap: "I have not
worked on billing or payments in ten years of backend work" is the first thing the
recruiter reads and it reads as an apology for applying. Never state it twice; an
opening admission plus a closing one inside 110 words is self-sabotage. State it
once, at the end, as the reason the role is interesting rather than a reason to
pass. "Billing, fraud detection, ClickHouse and Rust would all be new to me, and
that is a large part of why the role interests me" does the same honest work
without arguing against him.

**Never imply he uses the product.** For "why this company", he is usually not a
customer. Check before writing anything that assumes he is. When the answer needs
a claim about the company, paraphrase the posting's own language back rather than
praising a product he has not used. Their first paragraph is safer ground than
your impression of them.
