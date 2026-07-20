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

Commit the `.tex` in `latex-resume` so the record of what was sent is frozen. The
`apply-job` folder is not a git repo, so nothing to commit there.

## Phase 5: Report

Tell him:
- What was produced and where.
- **Any gap** between the posting and his actual experience. He needs to know
  where he is stretching before an interview, not after.
- **Any claim the verifier flagged as unsupported**, and what you did about it.
- The page count of the CV and whether anything was cut to fit.

Then stop. He submits. You do not.

## Judgement notes

**Answer length.** Respect a stated limit strictly. With no limit, 150-250 words
beats 400. Recruiters skim.

**Story reuse.** Using the same story for two questions in one application is
usually a mistake. The bank has 21 narrative and 19 STAR entries, so there is
almost always a better fit than a repeat.

**"Why this company".** This is the one question the story bank cannot answer
alone, because it needs something specific about *them*. Pull it from the posting
and the company's own material, and if it still reads generic, ask José what
actually draws him to it. A generic answer here is worse than a short one.

**Tone.** The story banks note: use "I" not "we", include data points, keep each
story self-contained. `latex-resume/AGENTS.md` carries the full writing rules and
the ban on the em dash character. Both apply to everything you write here.
