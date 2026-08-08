# ASD-STE100 for digest drill-down reports

ASD-STE100 (Simplified Technical English) is the aerospace controlled-language standard.
Here it has one job: make a root-cause report readable in one pass, in a uniform voice,
with no loss of technical content.

Apply it to every sentence you write. Do not apply it to quoted material.

## Never rewrite

Rewriting these is a defect, not a simplification:

- Contexture JSON, in full or trimmed
- Field names: `agencyEnriched.nameState`, `Vendor.Name`, `FieldGroup.titleAndDescription`
- Tool names, dataset names, schema names, APL queries
- Org names, user emails, timestamps, record counts
- Values quoted from customer data, for example `"County of Westchester, New York"`

## Writing rules

1. **One idea per sentence.** Split any sentence that carries two.
2. **Active voice.** "The client sends an invalid field name", not "an invalid field name
   is sent by the client".
3. **Present tense.** No "would", "could", "will". State what happens: "The API returns
   200. The response holds 0 records."
4. **Maximum 25 words per sentence.** Maximum 20 in a TL;DR item.
5. **Maximum six sentences per paragraph.** Most paragraphs are two or three.
6. **Keep the articles.** "The query returns nothing", not "Query returns nothing".
7. **One term per concept, every time.** Never vary a term for style. See the glossary
   below.
8. **No noun cluster longer than three words.** "partner name batch sweep query" becomes
   "the query that sweeps a batch of partner names".
9. **No -ing form as a noun or as the main verb.** "Widening the synonyms did not help"
   becomes "The client widened the synonyms. The result did not change."
10. **No contractions, no idioms, no phrasal verbs, no slang, no metaphors.** This is the
    rule that costs the most effort. See the replacement table.
11. **No hedging.** Delete "it seems", "arguably", "I noticed that", "worth noting".
12. **No rhetorical closers.** Delete any sentence that exists for rhythm.
13. **No em-dashes as sentence punctuation.** Use a period, a comma, or parentheses.
14. **Digits for all numbers**, including one through nine.

## Fixed glossary

Pick these terms and keep them for the whole report. Never substitute a synonym.

| Concept | Approved term | Never write |
| --- | --- | --- |
| A search that matched no records | **empty result** | zero result, no hits, blank, nothing back, came back dry |
| The JSON the client sends | **contexture tree**, or **tree** | query object, payload, request body, search |
| One MCP tool invocation | **call** | request, hit, invocation, shot |
| A named field in a schema | **field name** | key, attribute, property, param |
| A value from a closed list | **enum value** | taxonomy string, controlled value, category |
| The client got data after an empty result | **the client recovers** | dug out, figured it out, self-rescued, got unstuck |
| The client changed the tree and ran it again | **the client repeats the call with X** | tried, attempted, took a stab at, iterated |
| Our fault | **defect** | bug, sharp edge, gotcha, trap, footgun |
| Not our fault, and the answer is right | **correct empty result** | legitimate zero, expected miss, fine |
| A field name that does not exist on the schema | **invalid field name** | wrong field, made-up field, hallucinated field |
| A date filter that covers a short period | **narrow date window** | tight window, tiny range |

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
| a number of, several | the exact count |
| terminate | stop, or end |
| initiate, commence | start |
| ensure that | make sure that |
| additionally, furthermore, moreover | and, or a new sentence |
| currently, presently | now, or delete it |
| potentially, possibly | delete it, or state the condition |
| silently returns nothing | returns 200 with 0 records |
| burned a session, wasted a session | ran <N> calls and received no data |
| brute forced | repeated the call with a different field name <N> times |
| the customer never knew | the client received no error |

## Worked examples

**Before:**
> Zoom's spending searches are 100% dead because of one wrong field name. Both users
> filtered on `Agency.State`, which doesn't exist on the spending schema, and since we
> silently return 200 with zero records instead of erroring, they never knew anything was
> wrong and burned the whole session.

**After:**
> Both users filter the spending searches on the field name `Agency.State`. The
> `sp-data-lit` schema has no such field name. The API returns 200 with 0 records. The
> client receives no error. The 2 users make 48 calls and receive no data.

**Before:**
> They tried six different repair strategies and none of them touched the actual problem,
> so the session ended with them believing we have no spending data for Florida.

**After:**
> The client repeats the call with 6 different corrections. No correction changes the
> invalid field name. All 48 calls give an empty result. The customer can conclude that
> GovSpend holds no spending data for Florida.

**Before:**
> Black Creek dug themselves out after about half an hour, but it cost them the county
> precision they actually wanted.

**After:**
> The client recovers after 29 minutes. The successful call filters by state, not by
> county. The customer loses the county precision of the original question.
