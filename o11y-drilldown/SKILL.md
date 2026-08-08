---
name: o11y-drilldown
description: >
  Reads the latest Spark MCP production digest in ~/source/@cron/o11y-digest/digests/,
  pulls the raw contexture queries for the orgs it flagged on empty searches through
  the Axiom MCP server, works out why those searches returned nothing, and writes a
  root-cause analysis in ASD-STE100 Simplified Technical English to
  ~/source/@specs/spark-mcp/. Answers three questions per org: which queries returned
  nothing, whether the customer recovered afterwards, and which tools they used.
  Trigger whenever the user says "/o11y-drilldown", "analyse today's digest",
  "drill into the digest", "why did <org> get empty results", "investigate the zero
  results", "what did <org> do wrong", or names an org from a digest and asks what
  happened. Also handles a named org directly without a digest ("look at NVIDIA's
  empty searches").
---

# Digest drill-down

The daily digest says *which* orgs get empty results. It never says *why*. This skill
answers the why, with the customer's own contexture trees as evidence, and writes the
answer as a report the team can act on.

**The output is a root-cause analysis, not a summary of the digest.** The user already
read the digest. Every section must tell him something the digest cannot: what the
customer actually sent us, whether the empty result was our fault or the correct answer,
and what to change.

## The three-way split that carries the report

Every empty result lands in exactly one of these buckets. Deciding which one is the
whole job:

1. **Our defect.** The customer sent a reasonable query and we returned 200 with 0
   records instead of an error or a result. Invalid field names, `exact: true` on a
   multi-word enum value, and silent taxonomy mismatches live here. These are the
   findings worth a ticket.
2. **Our documentation or steering gap.** The customer could not have known. Sibling
   `tagsQuery` nodes that AND together, agency names that must be canonical, a tool
   whose data scope is not stated. Real problems, cheaper fixes.
3. **The correct answer.** A narrow date window with no activity in it, a private
   company that is not in a public-sector dataset, a genuinely empty niche. Say so
   plainly and do not dress it up as a problem.

A report that puts everything in bucket 1 is wrong, and a report that puts everything in
bucket 3 is useless. Count them and state the split in the TL;DR.

## Never do these

- **Never claim a root cause from a single query.** One empty result proves nothing. The
  evidence is a *pair*: a query that returned nothing and a near-identical query that
  returned data, or an aggregate over 7 days.
- **Never trust the condensed render when comparing a pair.** It hides fields. Diff the
  raw JSON. This is how the `exact: true` finding was nearly missed.
- **Never report a call count you did not verify against the digest.** If your window
  produces a different total than the digest table, your window is wrong.
- **Never guess a field name is invalid.** Check it against the feature's
  `instructions.md` in the spark-mcp repo first.

---

## Step 1 — Get the date and the latest digest

Run `date +%Y-%m-%d` through Bash. Do not infer today's date.

List `~/source/@cron/o11y-digest/digests/` and read the newest
`o11y-digest-YYYY-MM-DD.md`. Note the file's modification time with `ls -la`; the digest
ran `ago(24h)` from that moment, and that is the window every later query must use.

If the user named an org and no digest covers it, skip to Step 3 with that org and a
36 hour window.

---

## Step 2 — Pick the targets

Read the **Empty searches by org** table. Take every org marked 🔴, and every ⚠️ org the
user asked about. Two orgs is a normal run; more than three makes the report unreadable.

Record the digest's own numbers for each target (calls, zero, zero %). You will check
your Axiom totals against these in Step 4. A mismatch means your window is wrong, not
that the digest is wrong.

---

## Step 3 — Get the shape before the detail

The eight production datasets, unioned, are referred to below as UNION8:

```
union ['govspend-production-spark-mcp-bids'], ['govspend-production-spark-mcp-contacts'],
      ['govspend-production-spark-mcp-contracts'], ['govspend-production-spark-mcp-federal-opps'],
      ['govspend-production-spark-mcp-meetings'], ['govspend-production-spark-mcp-saved-searches'],
      ['govspend-production-spark-mcp-spending'], ['govspend-production-spark-mcp-utilities']
```

Run this first, through `mcp__axiom__queryDataset`, with `startTime` and `endTime` set to
the digest window:

```
<UNION8>
| where org_name == '<org>'
| where event in ('request.completed','request.failed')
| summarize calls=count(), zero=countif(tostring(zero_results)=='true'),
            first=min(_time), last=max(_time)
  by user_email, tool
| sort by calls desc
```

`zero_results` is typed inconsistently across datasets. Always wrap it in `tostring()`.

Check the total against the digest. Then note which tools are 100% empty: a tool at
exactly 100% is almost always bucket 1, and a tool at 20% is almost always bucket 3.

---

## Step 4 — Pull the raw contexture trees

The `query` field holds the customer's contexture tree as a JSON string. It exists on
every feature dataset except `utilities`.

```
<UNION8>
| where org_name == '<org>'
| where event in ('request.completed','request.failed')
| project _time, user_email, tool, zero_results, records, returned_records, error_type, query
| sort by _time asc
```

**This result will be too large to return inline.** The Axiom MCP tool writes it to a
file under `tool-results/` and gives you the path. That is expected, not an error. Two
things to know:

- The tool caps the row count near 100. If Step 3 said the org made more calls than the
  dump contains, split the query by `user_email` and run it again per user.
- Do not read the dump directly. Run the condenser:

```bash
python3 <skill-dir>/scripts/condense_queries.py <path-to-tool-results-file>
```

It prints one header line and one rendered tree per call: timestamp, user, tool, schema,
page size, the `exact` flag on every `tagsQuery` node, and the outcome
(`ZERO`, `ok r=<matched>/<returned>`, or `FAIL <error_type>`). Pipe it to a file in the
scratchpad and read that.

---

## Step 5 — Find the pairs

This is the core technique. Sort the calls by time and look for **two calls, seconds
apart, that differ in one thing, where one returned nothing and the other returned data.**
The customer's own repair loop runs the experiment for you.

For every candidate pair, extract both raw trees and diff them field by field:

```bash
python3 <skill-dir>/scripts/condense_queries.py <dump> --raw <HH:MM:SS> <HH:MM:SS>
```

The difference that matters is often one the condensed view drops: an `exact` flag, a
`join` value, a `filterOnly` flag, a `distance`, a `mode`. Read the full JSON of both.

When no pair exists, prove the cause with an aggregate over 7 days instead:

```
['govspend-production-spark-mcp-<feature>']
| where _time > ago(7d) | where event == 'request.completed'
| extend suspect = query has '<the suspect token>'
| summarize calls=count(), zero=countif(tostring(zero_results)=='true'), orgs=dcount(org_name)
  by suspect
| extend zero_pct=round(100.0*zero/calls,1)
```

A suspect that shows 100% empty across every org that used it is a defect. A suspect
whose rate matches the baseline is a coincidence, and you drop the theory.

---

## Step 6 — Check the three things that are always worth checking

1. **Are the field names real?** Read
   `~/source/spark-mcp/spark_mcp/features/<feature>/instructions.md` and compare. Never
   assert a field is invalid without this check, and never assert it is valid either.
   `instructions.md` also lists the closed enums, which is how you catch taxonomy
   mismatches.
2. **Did they call the helper tools?** Query for `lookup_agency`,
   `get_tool_instructions`, and `get_user_profile` across UNION8 plus
   `['govspend-production-spark-mcp-core']`. An org that never calls them, in a week
   where production made hundreds of `lookup_agency` calls, tells you the client is a
   script or a weakly steered agent. Get the production total for the same window so the
   comparison has a denominator.
3. **Did they recover?** For each empty result, look at the next call from the same user.
   Recovery on the next call is a healthy client. A repair loop that runs six strategies
   and never recovers means the customer left believing we have no data.

Read `references/failure-catalog.md` before writing. It holds the causes already
confirmed in production, with the evidence that confirmed each one. Check the new data
against it first: most drill-downs find a cause that is already in the catalog, and a
repeat cause is a stronger finding than a new one because it shows a pattern.

---

## Step 7 — Write the report

Write to `~/source/@specs/spark-mcp/zero-results-<org-slug>-YYYY-MM-DD.md`. For a
multi-org run use `zero-results-<slug>-<slug>-YYYY-MM-DD.md`.

**Write the whole report in ASD-STE100 Simplified Technical English.** Read
`references/ste.md` before you draft, and apply it while drafting, not as a cleanup pass.
The rules that change this report the most: one idea per sentence, 25 words maximum,
active voice, present tense, one term per concept, and no idioms. Contexture JSON,
field names, org names, user emails, and timestamps are quoted material and stay exactly
as they are.

Sections, in this order:

### Header
The source datasets, the exact window, and the digest table row for each target org.

### TL;DR
Numbered, 3 to 6 items. The first item states the bucket split: how many empty results
are our defect, how many are a documentation gap, and how many are the correct answer.
Each later item states one cause and the number of empty results it explains.

### Tools used
One table: user, tool, calls, empty, empty percent. Add one line below it for the
helper-tool check from Step 6.

### One section per cause
Order the sections by the number of empty results each cause explains, largest first.
Each section holds:

- The count, in the heading: `## Cause 2 — exact: true on a taxonomy value (2 empty)`.
- The evidence pair, as two fenced JSON blocks with a comment line giving the timestamp
  and the outcome. Trim the trees to the nodes that matter and mark the cut with
  `/* ...40 total... */`.
- Two or three sentences that state what happens and what the customer sees.
- One sentence that assigns the bucket.

### Root causes
One table: number, cause, count of empty results, and whether the cause is ours or the
customer's. Use the words "Ours", "Ours (documentation)", or "Theirs, and correct".

### Recommendations
Numbered, 4 to 6 items, ordered by value. Each item is an imperative sentence and then
one sentence of justification. Put the single real defect first and say that it is the
only defect. Never recommend contacting the customer as the first item.

---

## Step 8 — Offer the Slack message

Do not write it unless the user asks. When he does, produce one fenced block per org, in
this shape, which he has already approved twice:

```
Heads up on <Org name>

<One paragraph: when, which users, the headline percent, and the one-sentence root cause,
framed as what the customer now wrongly believes about our coverage.>

<One paragraph per affected tool. Name the tool, the outcome, and the wrong thing in
plain words. Field names appear as plain text, with no backticks.>

<One paragraph: a hypothesis about what they are running, and what is worth checking.>

<One line: a call to action about coordinating with the customer, and a workspace emoji.>

Tagging @<name> for viz
```

Slack rules, which differ from the report rules:

- No Slack markup. No bold, no italics, no bullets, no backticks.
- Two numbers at most in the whole message.
- Lead with what the customer wrongly believes, not with the mechanism.
- Never include the engineering fix. It stays in the report.
- Do not apply STE here. The Slack voice is the user's own, and it is informal.

---

## Edge cases

- **The digest names an org with fewer than 50 calls.** The digest filters to `calls > 50`,
  so this cannot happen from the org table. If the user names a small org anyway, run it
  and say in the header that the sample is small.
- **The org made calls in two separate sessions.** Report them as separate sessions with
  their own timestamps. Two users hitting the same wall independently is a stronger
  finding than one user hitting it twice.
- **Every empty result is bucket 3.** That is a valid outcome. Write the short report,
  say the account is healthy, and recommend that the digest metric exclude the query
  shape that inflated it.
- **The digest percentage and your percentage differ.** Recheck the window before you
  recheck anything else. State the digest number and your number in the header, and say
  which window each covers.
- **Axiom returns no rows.** Confirm the org name string exactly. `org_name` values carry
  punctuation, for example `Zoom Communications, Inc.`. Get the exact value with
  `summarize by org_name` before filtering on it.
