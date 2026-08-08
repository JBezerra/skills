# ASD-STE100 for review digests

ASD-STE100 (Simplified Technical English) is the aerospace controlled-language standard. Here it has
one job: make two machine-generated review digests readable at a glance, in a uniform voice, with no
loss of technical content.

Apply it to the **/code-review** and **/pr-review** sections. Do not apply it to the UAT section, to
quoted acceptance criteria, to quoted code, or to quoted app strings.

## Never rewrite

Rewriting these is a defect, not a simplification:

- File paths, `file:line` anchors, commit SHAs, branch names
- Symbol names: functions, variables, types, env vars, collections, fields
- Quoted strings from the app, the database, or the AC
- Code blocks and stored document shapes
- The labels `**blocker:**`, `**suggestion:**`, `**question:**` and the verdict names

## Writing rules

1. **One idea per sentence.** Split any sentence that carries two.
2. **Active voice.** "The handler drops the filter", not "the filter is dropped by the handler".
3. **Present tense.** No "would", "could", "will". A failure scenario is stated as what happens:
   "The user saves the form. The API stores an empty array."
4. **Maximum 20 words per sentence** in findings, 25 in a rationale.
5. **Keep the articles.** "The query runs twice", not "Query runs twice".
6. **One term per concept, every time.** Pick "profile" or "record" and keep it for the whole digest.
   Never vary a term for style.
7. **No noun cluster longer than three words.** "federal profile field reset list" becomes "the list
   of fields that the federal profile resets".
8. **No -ing form as the main verb or as a noun.** "Resetting the profile drops the SLED fields"
   becomes "The reset drops the SLED fields".
9. **No contractions, no idioms, no phrasal verbs, no slang, no rhetorical questions.**
10. **No hedging and no throat-clearing.** Delete "it seems", "arguably", "I noticed that",
    "you might want to". State the finding.
11. **Warnings and consequences come after the fact, in their own sentence**, and start with the
    subject: "The user loses the entered values."
12. **Maximum six sentences per paragraph.** Findings are usually one or two.
13. **No em-dashes as sentence punctuation.** Use a period, a comma, or parentheses.

## Word replacements

| Instead of | Write |
| --- | --- |
| utilize, leverage | use |
| in order to | to |
| prior to | before |
| subsequent to, following | after |
| in the event that | if |
| due to the fact that | because |
| is able to, has the ability to | can |
| perform a check on | check |
| provide support for | support |
| a number of, several | the exact count, or "some" |
| terminate | stop, or end |
| initiate, commence | start |
| ensure that | make sure that, or state the required result |
| additionally, furthermore, moreover | and, or a new sentence |
| currently, presently | now, or delete it |
| potentially, possibly | delete it, or state the condition |

## Finding shape

Each finding becomes one bullet, in this order:

```
- `path/to/file.ts:142` — <what is wrong, one sentence>. <what happens, one or two sentences>
```

For `/pr-review` findings, keep the label first and the same shape after it:

```
- **suggestion:** <what to change, one sentence>. <why, one sentence>
```

## Worked examples

**Before** — /code-review output:
> Because the `resetFederalProfile` helper is currently iterating over the full field list rather
> than filtering to only the SLED-specific keys, calling it would potentially end up clearing user
> data that wasn't intended to be reset, which could result in silent data loss for users who have
> both profiles configured.

**After:**
> - `common/src/profile/reset.ts:38` — `resetFederalProfile` iterates the full field list instead of
>   the SLED keys. The reset clears fields that belong to the federal profile. The user loses that
>   data and sees no error.

**Before** — /pr-review output:
> **suggestion:** It seems like the new `formatFieldLabel` helper is only being utilized in a single
> call site, and given that it doesn't really encompass any complex logic, you might want to consider
> inlining it.

**After:**
> - **suggestion:** Inline `formatFieldLabel` in `FederalProfileForm`. The helper has one call site
>   and no complex logic.
