# ASD-STE100 for review digests

ASD-STE100 (Simplified Technical English) is the aerospace controlled-language standard. Here it has
one job: make two machine-generated review digests readable at a glance, in a uniform voice, with no
loss of technical content.

Apply it to the **whole digest**, including the UAT material. Do not apply it to quoted acceptance
criteria, to quoted code, to quoted app strings, or to a stored document shape.

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

**The plain statement comes first. The mechanism goes underneath.** Never open a finding with a file
path or a symbol name. The reader must be able to skip every anchor and still understand the defect.

A must-fix or a follow-up finding:

```
### 3. A pasted ZIP sticks in the territory. The user cannot remove it.

**What happens.** The user pastes `33101`. The review reports "Matched". No row holds a tick mark.
The entry stays in the territory. The user cannot deselect it from the step.

**Why.** The code saves the 5-digit ZIP. The row keeps the full ZIP with its 4-digit suffix. The two
values never match.

**Where.** `ZipsStep.tsx:299`, `pasteList.ts:135`, `retainedByState`.

**Found by.** code-review, TL review, UAT.
```

A cosmetic finding collapses to one bullet:

```
- **A dead CSS class.** `text-classs` is not a Tailwind utility. It has no visual effect.
  `CustomFilterableFacet.tsx:225`. *(code-review, TL review, UAT)*
```

## Worked examples

**Before** — /code-review output:
> Because the `resetFederalProfile` helper is currently iterating over the full field list rather
> than filtering to only the SLED-specific keys, calling it would potentially end up clearing user
> data that wasn't intended to be reset, which could result in silent data loss for users who have
> both profiles configured.

**After:**
> ### 1. A profile reset clears fields that the user did not expect to lose.
>
> **What happens.** The user resets the SLED profile. The reset also clears the federal profile
> fields. The user loses that data. The app shows no error.
>
> **Why.** `resetFederalProfile` iterates the full field list instead of the SLED keys.
>
> **Where.** `common/src/profile/reset.ts:38`.
>
> **Found by.** code-review.

**Before** — /pr-review output:
> **suggestion:** It seems like the new `formatFieldLabel` helper is only being utilized in a single
> call site, and given that it doesn't really encompass any complex logic, you might want to consider
> inlining it.

**After** (a cosmetic bullet, because no user is harmed):
> - **A helper with one call site.** `formatFieldLabel` holds no complex logic and runs from one
>   place. `FederalProfileForm`. *(TL review)*

Note what the rewrite does to the label. The digest groups by severity, so a `**suggestion:**` label
carries no information the bucket does not already give. Drop the label and keep the content.
