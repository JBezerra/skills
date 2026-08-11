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

## Useful production baselines

Recheck these when you cite them; they drift.

| Measure | Value | Window |
| --- | --- | --- |
| Empty rate, all calls | 6% to 8% | 7 days, 2026-08 |
| Empty rate with `"exact":true` | 3.2% | 7 days, 2026-08 |
| Empty rate, `pageSize` 51 to 100 | 19.5% | 7 days, 2026-08 |
| `lookup_agency` calls | 729 | 48 hours, 2026-08-06 |
| Server-side page cap | 50 records returned | any `pageSize` above 50 |
