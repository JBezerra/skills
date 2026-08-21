# Confirmed causes of empty results

Every cause below is confirmed in production with evidence. Check new data against this
list before you propose a new cause. A repeat cause is a stronger finding than a novel
one, because it shows a pattern across accounts.

Add a row when you confirm a new cause. Include the evidence, not only the claim.

---

## 1. Invalid field name returns 200 with 0 records

**Bucket:** our defect. The most serious item in this catalog.

The API accepts a contexture tree that names a field the schema does not have. It matches
nothing and returns success. The client receives no error and cannot tell the difference
between a broken query and an empty dataset.

**Confirmed:** Zoom Communications, 2026-08-05. Both users filter `search_spending` on
`Agency.State`, `Agency.Type`, `PO.VendorName`, and `PO.Description`. The `sp-data-lit`
schema has none of them. All 48 calls give an empty result. Neither user recovers.

**Control that proves it:** at 18:12:07 the user sends one filter,
`Agency.State = "Tennessee"`, and gets 0 records. At 18:12:44 the same user sends
`agencyEnriched.agencyState = "Tennessee"` against contracts and gets 35,122 records.

**Aggregate that proves it:** over 7 days, every production call whose tree contains
`Agency.State` or `PO.VendorName` gives an empty result, 100% of the time.

**Valid field names, for reference:**

| Schema | Agency state | Vendor | Free text |
| --- | --- | --- | --- |
| `sp-data-lit` (spending) | `agencyEnriched.agencyState` | `Vendor.Name` | `FieldGroup.POLineItem`, `FieldGroup.All` |
| `contracts` | `agencyEnriched.agencyState` | `companyName` | `FieldGroup.titleAndDescription`, `FieldGroup.titleDescriptionDocuments` |
| `bid-data` | `agencyEnriched.agencyState` | n/a | `FieldGroup.titleAndDescription` |

`vendorName` is not valid on contracts. `FieldGroup.All` is not valid on contracts, and it
is valid on spending.

---

## 2. Agency names must be canonical

**Bucket:** our documentation and steering gap. Seen in 3 accounts in 3 days.

`tagsQuery` fuzzy matching corrects typos. It does not survive a word reorder. The
canonical agency name is the only string that matches.

**Confirmed:** Black Creek Integrated Sys, 2026-08-05. The client filters on
`"Westchester County, New York"` and `"Westchester County"`. The canonical value is
`"County of Westchester, New York"`. 9 consecutive calls give an empty result. The field
names are all correct. Only the value is wrong.

**Evidence pair:** at 21:01:49 the client sends the canonical name with
`contractEndDate: allFutureDates` and gets 0 records. At 21:02:06 the client sends the
same tree with `allPastDates` and gets 24 records.

**Also seen:** NVIDIA, 2026-08-06, `agencyEnriched.nameState = "Cuyahoga County"` gives an
empty result. The next call drops the agency filter and gets 124 records.

`lookup_agency` exists to resolve this. None of the 3 accounts called it.

---

## 3. `exact: true` on a multi-word enum value returns nothing

**Bucket:** our defect.

A `tagsQuery` node with `"exact": true` matches nothing when the value holds a space, even
when the value is the exact string the instructions document.

**Confirmed:** NVIDIA, 2026-08-06. Two pairs of near-identical bid searches.

- 19:00:27, `agencyEnriched.agencyType = "Higher Ed"` with `"exact": true`, 0 records.
  19:01:23, the same tree with `"exact": false`, 4 records.
- 19:26:43, `agencyType`, `country`, and `levelOfGovernment` all with `"exact": true`,
  0 records. 19:26:54, the same tree with no `exact` key, 3 records.

`"Higher Ed"` is the exact value that `search_bids/instructions.md` documents.

**Aggregate that bounds it:** over 7 days, `"exact":true` gives a 3.2% empty rate across
11,465 calls, below the 6.8% baseline. The defect is specific to multi-word enum values,
not to `exact` in general. Do not report it as a general defect.

---

## 4. Sibling `tagsQuery` nodes join with AND

**Bucket:** our documentation gap.

Two `tagsQuery` nodes under one `and` group both have to match, even when each node has
`"join": "any"`. Clients read `"join": "any"` as if it applied across nodes.

**Confirmed:** NVIDIA, 2026-08-06. At 19:27:48 the tree holds one node for stage keywords
(`RFI`, `sources sought`) and one node for technology keywords (`NVIDIA`, `GPU`), both on
`FieldGroup.titleAndDescription`. The result is 0 records. At 19:28:01 the client removes
the stage node and gets 147 records. The same before and after occurs twice more in the
same session.

**Correction, 2026-08-17. Check the call order before you report this.** The same 2 trees
appeared again for NVIDIA on 2026-08-16, and the reading above did not hold. The client
sent the tree without the stage node first, then the tree with it, 535 milliseconds later,
on every one of 69 sweeps. That is a deliberate 2 tier query, not a repair loop. The
client asks for all AI bids, then for the early-stage subset. The AND is what the client
wants.

**The control that separates the 2 readings:** run the `stage` node on its own, then run
it with the other node, at national scope. On 2026-08-17 the `stage` node alone gave
4,200 open bids. The `stage` node with a 4 term technology node gave 53 open bids. The
mechanism works. NVIDIA's 69 empty results came from the agency portfolio, which held
none of those 53 bids.

Report this cause only when the client never sends the tree without the second node.

---

## 5. Free text against a controlled-vocabulary field

**Bucket:** our documentation gap.

Some fields hold a closed list of values in fixed case. `tagsQuery` against them gives an
empty result. `facet` with the exact value works.

**Confirmed:** Black Creek Integrated Sys, 2026-08-05.
`agencyEnriched.departmentName` with `tagsQuery` tags `["Corrections", "Correction"]` gives
0 records. `facet` with `['CORRECTION', 'PROBATION']` gives 192 records.

---

## 6. Narrow date window with no activity

**Bucket:** the correct answer. Do not report this as a problem.

A client that polls for changes sends a date window of a few days. Most windows hold no
new records for a given vendor list. The empty result is correct.

**Confirmed:** NVIDIA, 2026-08-06. The client splits a large partner list into batches of
40 names and runs each batch against `contractEffectiveDate` between 2026-08-02 and
2026-08-06. 12 batches run in 5 seconds. 5 batches give 1 to 7 records. 7 batches give an
empty result.

This cause explains 13 of NVIDIA's 22 empty results. It inflates the digest metric for any
account that polls for changes. State that in the recommendations.

---

## 7. The tool holds a different population than the client assumes

**Bucket:** our documentation gap.

**Confirmed:** NVIDIA, 2026-08-06. Both `search_contacts` calls look for the chief
executive of Aclima, a private company. The `sp-data-oct` schema holds public-sector
contacts only. The empty result is correct. The client had no way to learn the scope
before the call.

---

## 8. `analytics_*` rejects aggregations inside the tree

**Bucket:** our defect, and it produces an error rather than an empty result.

Clients put a `fieldValuesGroupStats` node inside `tree`. The request model expects a
separate `aggregations` list. The call fails with
`ValidationError: aggregations must not be empty`.

**Confirmed:** Zoom Communications and Black Creek, 2026-08-05. 6 of the 7 failed calls
across both accounts carry this error.

---

## 9. Helper tools are not called

**Bucket:** our steering gap. Present in every account investigated so far.

Zoom, Black Creek, and NVIDIA made 0 calls to `lookup_agency` and 0 calls to
`get_tool_instructions`. Production made 729 `lookup_agency` calls in the same 48 hour
window. An account that never calls them is running a script or a weakly steered agent,
and causes 2, 3, and 5 above all follow from that.

Always report the production total next to the account's total, so the comparison has a
denominator.

---

## 10. An unknown agency identifier returns 200 with 0 records

**Bucket:** our documentation gap.

A `facet` node on a valid agency identifier field with a value the index has never held
returns 200 with 0 records. The client cannot separate "GovSpend does not hold this
agency" from "this agency has no matching record".

**Confirmed:** Hand2mind, 2026-08-10. The client filters `search_spending` on
`agencyEnriched.ncesId`, one NCES school district identifier per call. It uses 200
distinct identifiers. A single control call that facets on all 200 at once returns
7,985,607 records and 164 distinct identifiers. The other 36 identifiers hold nothing.

**Control that proves the field name is valid:** `agencyEnriched.ncesId = "0622710"` gives
577,326 records (Los Angeles Unified School District). `"0623340"` gives 45,119 records
(Madera Unified School District).

`agencyEnriched.ncesId` is real and works, and no `instructions.md` documents it. The
documented agency identifiers are `agencyEnriched.agencyId` and
`agencyEnriched.computedId`. `lookup_agency` accepts a name or an `agency_id`, not an NCES
identifier.

**Field cardinality, for reference:** the spending index holds 7,988 distinct
`agencyEnriched.ncesId` values, and 518 of them are California districts.

---

## 11. The existence probe inflates the empty-result metric

**Bucket:** the correct answer. Do not report this as a problem.

A tree with `pageSize` 1 and a single `include` field is a probe, not a search. A client
sweeps a list of agencies and asks one narrow yes-or-no question per agency. Most answers
are "no", and each "no" counts as an empty result in the digest.

**Confirmed:** Hand2mind, 2026-08-10. 273 of 275 empty results come from 2 probe shapes.
The account reaches 88.71% empty and works exactly as designed. The client escalates to a
real search with `pageSize` 15, 20, or 50 for every agency the probe finds.

**Aggregate that bounds the narrow question:** the client's 38-phrase keyword filter
matches 32,479 line items across the whole spending index. With the client's
`LastModified` filter it matches 658. Divided across 200 districts, almost every district
holds 0.

---

## 12. `"join": "all"` on a tokenized agency name

**Bucket:** our documentation gap. The largest single cause found so far.

A client splits an agency name into separate word tokens and puts them in one `tagsQuery`
node with `"join": "all"`. Every token must match. Abbreviations (`Indep`, `Unif`, `Sch`,
`Dist`) never match, because the index holds the full words. No `instructions.md` for a
search tool shows `"join": "all"`; every example uses `"join": "any"`. `contact/tool.py`
does document it, which is where clients likely learn it.

**Confirmed:** Zayo Group, 2026-08-12. 282 `search_contracts` calls in 1 shape, 223 empty.

**Control that proves it:** at 01:08:56 the agency node holds `["Aurora", "Academy"]` with
`"join": "all"` and gives 0 records. At 01:08:58 the same tree with `["Aurora"]` gives 2
records. The keyword node and the date node are byte-identical in both trees.

**The token count controls the outcome.** Across 246 calls that share one keyword node and
one date node:

| Tokens | Calls | Empty % |
| --- | --- | --- |
| 1 | 72 | 51.4% |
| 2 | 79 | 83.5% |
| 3 | 65 | 95.4% |
| 4 or more | 30 | 100% |

**Aggregate that proves it is not one account:** over 7 days, contracts calls holding
`agencyEnriched.name` and `"join": "all"` give 71.8% empty across 365 calls and 26 orgs,
against a 9.4% baseline. Excluding Zayo Group, 48.2% across 85 calls and 25 orgs.

---

## 13. `agencyEnriched.nameState` is documented incorrectly for contracts

**Bucket:** our defect (documentation). A live repo bug, not a customer error.

`search_contracts/instructions.md:57` reads `agencyEnriched.nameState` — state name, e.g.
`"Texas"`. `search_bids/instructions.md:64` and
`search_meeting_intelligence/instructions.md:38` read the same field name as agency name +
state, e.g. `"City of Dallas, Texas"`. The bids and meetings entries are correct.

**Confirmed:** Zayo Group, 2026-08-11. At 16:31:33 the client filters `nameState` on
`["Pittsburg Independent School District", "Texas"]` with `"join": "all"` and gives 0
records. At 16:31:40 the client removes the keyword node and the result does not change.
The agency node alone is unsatisfiable.

Check this file whenever a client mixes an agency name and a state in one node.

---

## 14. The server denies `get_tool_instructions` on an MCP entitlement

**Bucket:** our defect (entitlement). Explains a weakly steered client directly.

`get_tool_instructions` can be refused for an org that holds a working MCP entitlement.
The `core` dataset records `event = entitlement.denied` with
`failure_mode = no_mcp_entitlement`.

**Confirmed:** PASCO Scientific, 2026-08-11, at 18:13:07 and 18:13:26. The account made
its first search 60 minutes later, and it was the only org in the window that tried to
read the instructions at all.

Always query `['govspend-production-spark-mcp-core'] | where event == 'entitlement.denied'`
during the Step 6 helper-tool check. A denial is a stronger finding than a zero call
count, because the client did the right thing and we refused.

---

## 15. An exact `facet` on a vendor name field under-counts, and does not empty

**Bucket:** our documentation gap. It suppresses records. It is almost never the cause of
an empty result, so do not report it as one without the control in the last paragraph.

`facet` matches the raw stored string. `companyName` and `Vendor.Name` are listed under
**Text search** in `instructions.md`, for use with `tagsQuery`. A client that builds a
partner watchlist puts marketing names in a `facet` node. The index holds legal entity
names. The node matches a small fraction of the vendor's records.

**Confirmed:** NVIDIA, 2026-08-16. The client keeps a 20 name vendor watchlist on
`companyName`.

**Control that measures the loss**, `contractEffectiveDate` over 12 months:

| Node | Records |
| --- | --- |
| The 20 name watchlist, as `facet` | 111 |
| The same vendors, as `tagsQuery` with shorter tags | 1,792 |

**Per-vendor controls, all dates:**

| Node | Records |
| --- | --- |
| `facet` `companyName` = `"Cisco Systems"` | 13 |
| `tagsQuery` `companyName` tag `Cisco` | 360 |
| `facet` `companyName` = `"ePlusTechnology Inc"` | 0 |
| `tagsQuery` `companyName` tag `ePlus` | 697 |

The index holds `Eplus Technology Inc`. The client sends `ePlusTechnology Inc`.

**`tagsQuery` is not a safe substitute.** The tag `Zones` matches `Stripe A Zone Llc` and
`Balboa Fun Zone Inc`, and gives 2,297 contracts. There is no `lookup_vendor` tool. No
tool resolves a canonical vendor name, and `lookup_agency` does not accept one.

**Before you blame this for an empty result, run the control.** Replace the `facet` node
with a `tagsQuery` node and keep every other node. For NVIDIA the empty result stayed
empty: the corrected tree gave 2 records in a window where the client had 325 empty
results. The date window was the binding constraint, not the vendor names. This cause
explains a low record count. It rarely explains a 0.

`facet` on `agencyEnriched.nameState` does work with a canonical value. That is not the
problem here; the vendor field is.

---

## 16. The spending index load lag is longer than the client's poll window

**Bucket:** the correct answer, plus a documentation gap. Do not open a ticket on the
empty results themselves.

A client polls `PO.IssuedDate` over the last 1 to 5 days. The spending index has not
loaded that period yet for most agencies. Every poll gives an empty result.

**Confirmed:** NVIDIA, 2026-08-16. 359 of 360 `search_spending` calls give an empty
result. Every call carries a `PO.IssuedDate` window of 1 to 5 days.

**Aggregate that proves it:** the whole spending index holds 553 line items for
`PO.IssuedDate` 2026-08-12 to 2026-08-16, and 586 for 2026-08-09 to 2026-08-13. Normal
volume is millions per year.

**Control that measures the lag:** the 6 canonical Maricopa County agency names on
`agencyEnriched.nameState` with 2026-06-01 to 2026-08-17 give 31,681 line items. The
newest `PO.IssuedDate` in that set is 2026-07-07. The lag is about 6 weeks for these
agencies, and it is not uniform: `agencyEnriched.agencyState` = `Arizona` with
2026-08-09 to 2026-08-13 gives 60 line items.

No `instructions.md` states the lag. The client cannot separate "GovSpend has not loaded
this week yet" from "these agencies bought nothing".

---

## 17. `facet` on `agencyEnriched.nameState` is case-sensitive and exact

**Bucket:** our defect, in the sense that 1 character of case silently removes an entire
agency. It suppresses records rather than causing an empty result, so apply the same
control rule as cause 15.

`facet` matches the raw stored string, including case, punctuation, and the exact legal
form of the agency name. A client that generates agency names from a city list loses most
of them, and receives no signal that anything is wrong.

**Confirmed:** NVIDIA, 2026-08-16. The client sweeps 17 metropolitan portfolios with 233
distinct agency names. 150 of them, which is 64%, match no record in the index.

**The case control, which is the crispest proof:**

| Value | Records |
| --- | --- |
| `County of DeKalb, Georgia` | 0 |
| `County of Dekalb, Georgia` | 363,804 |
| `County of DuPage, Illinois` | 0 |
| `County of Dupage, Illinois` | 21,345 |

**The 3 groups of dead names:**

1. **The `X County, State` form, 46 names.** The index never uses it. It uses
   `County of X, State`. `Maricopa County, Arizona` gives 0, and
   `County of Maricopa, Arizona` gives 8,605. A client that emits both forms wastes half
   of every county entry.
2. **Generated `Town of` and `Village of` padding, 92 of 94 names.** Only
   `Town of Cary, North Carolina` and `Town of Chapel Hill, North Carolina` are real.
3. **Near-miss spellings and consolidated agencies, 12 names.** These are the expensive
   ones, because the client believes it covers the agency.

| The client sends | The index holds | Records |
| --- | --- | --- |
| `County of Prince George's, Maryland` | `County of Prince Georges, Maryland` | 389,248 |
| `City of San Francisco, California` | `City and County of San Francisco, California` | 10,393 |
| `County of Wyandotte, Kansas` | `Unified Government of Wyandotte County and Kansas City, Kansas` | 9,190 |
| `City of Chapel Hill, North Carolina` | `Town of Chapel Hill, North Carolina` | 3,257 |
| `City of Washington, District of Columbia` | nothing; DC agencies carry individual names | 0 |

**How to run this check on any account.** Extract every distinct value from the `facet`
node with APL, put all of them in 1 `facet` node, and run `analytics_*` with a
`fieldValuesGroupStats` on the same field. The keys that return are the live names. Diff
them against the sent list. Run it a second time with no date filter, so that a real but
quiet agency does not count as dead. For NVIDIA, 6 names were live but had no spending in
12 months.

**Other facet fields to clear at the same time.** For NVIDIA these were all correct:
`agencyEnriched.country` (`USA` is the only value), `agencyEnriched.levelOfGovernment`
(`State`, `Local`), and `agencyEnriched.agencyState` (full state names). Only the name
fields were wrong.

---

## Useful production baselines

Recheck these when you cite them; they drift.

| Measure | Value | Window |
| --- | --- | --- |
| Empty rate, all calls | 6% to 8% | 7 days, 2026-08 |
| Empty rate, contracts dataset | 9.4% | 7 days, 2026-08-12 |
| Empty rate, meetings dataset | 10.1% | 7 days, 2026-08-12 |
| Empty rate with `"exact":true` | 3.2% | 7 days, 2026-08 |
| Empty rate, `pageSize` 51 to 100 | 19.5% | 7 days, 2026-08 |
| Empty rate, bids, phrase tag of 3 words or more | 18.4% | 7 days, 2026-08-12 |
| Empty rate, `facet` on `agencyEnriched.nameState` | 4.8% | 7 days, 2026-08-12 |
| Empty rate, bids dataset | 17.7% | 7 days, 2026-08-17 |
| Empty rate, bids, tree with a `search` node and a `stage` node (2 orgs, and see cause 4) | 96.0% | 7 days, 2026-08-17 |
| Open bids matching the `stage` node alone, nationwide | 4,200 | 2026-08-17 |
| Open bids matching the `stage` node and a technology node, nationwide | 53 | 2026-08-17 |
| `lookup_agency` calls | 729 | 48 hours, 2026-08-06 |
| `lookup_agency` calls | 239 | 24 hours, 2026-08-12 |
| `lookup_agency` calls | 20 | 24 hours, 2026-08-17 |
| `lookup_agency` calls | 4,629 | 7 days, 2026-08-17 |
| Spending line items with `PO.IssuedDate` in the last 5 days | 553 | 2026-08-12 to 2026-08-16 |
| Active contracts with `contractEffectiveDate` in the last 5 days | 1,330 | 2026-08-12 to 2026-08-16 |
| Server-side page cap | 50 records returned | any `pageSize` above 50 |
