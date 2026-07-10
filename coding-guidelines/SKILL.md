---
name: coding-guidelines
description: Jose Bezerra's personal coding-style taste, built iteratively from real corrections he makes to Claude-generated code across projects. Consult this before/while writing non-trivial code, for judgment calls a repo's own AGENTS.md/CLAUDE.md doesn't already settle (comment density, data modeling shape, when to extract a helper, testing style, and similar calls). This skill is also where new taste corrections get captured — see "How this skill learns" below. Triggers on "/coding-guidelines", "apply my coding guidelines", "what's my code style", "learn from this fix", or when a stylistic judgment call comes up that no repo doc resolves.
---

# Coding Guidelines

This is José's personal coding taste, accumulated from real steering/corrections
he's made to generated code, not a one-shot guess written up front. It applies
across repos. A repo's own `AGENTS.md`/`CLAUDE.md` always wins on anything it
states explicitly — those are shared, project-specific, and reviewed by a team.
This skill fills the gaps those docs leave open, and should never be used to
contradict them.

## Guidelines

### Comments

Trim comments to the essential point; drop elaboration once the core point
lands. A multi-line JSDoc explaining a behavior *and* its convention *and* an
example is usually two sentences too long — cut it to the one line that states
the non-obvious part. Don't restate context already clear from the code or
nearby types.

### Function structure

Extract non-trivial inline logic — especially a derived/clamped numeric
calculation — into a dedicated, named, exported function with its own unit
tests, rather than leaving it inline in a render loop or callback, even when
the underlying behavior isn't changing. If a computation needs more than a
glance to verify correctness, name it and test it; don't wait to be asked.

Prefer a pure derivation (e.g. `Array.reduce` building a running total) over
a mutable accumulator (`let x = 0; ...; x += ...`) in a loop or `.map()`,
even at the cost of a little more code.

Push null/absence tolerance into a helper rather than guarding at the call
site. Give the helper nullable optional params and optional-chain internally,
returning the base value when inputs are missing, so callers invoke it
unconditionally on a single path — instead of a call-site ternary that
re-states the fallback (`org && ai ? enrich(x, org, ai) : x`). The "what to do
when inputs are missing" logic then lives in one place, not split between the
helper and every caller.

### Naming

Variable names should be short but descriptive — name a value for what it
actually is, and reach for the shortest name that still says that. This rules
out single-letter placeholders (`u`, `v`, `x`) whose meaning you have to infer
from context, and equally rules out padding a name with noise once it's
already clear. The bar applies everywhere, including loop and comprehension
variables and even when the descriptive name makes a one-liner longer: prefer
`[resource_url.strip() for resource_url in raw.split(",")]` over
`[u.strip() for u in raw.split(",")]`.

## How this skill learns

When the user corrects or steers the style of generated code — not a
correctness bug — and the correction is a pattern likely to
recur, not a one-off:

1. Check whether it's already covered by a bullet above or by the current
   repo's own `AGENTS.md`/`CLAUDE.md`. If it's already in a repo doc, don't
   duplicate it here — this file is for taste that generalizes across repos,
   not a mirror of project-specific docs.
2. If it's new, add a short bullet under the right heading above (or a new
   heading if none fits) in the same voice as the existing entries: state the
   rule first, then the concrete example that prompted it, in one or two
   sentences. Don't write a running log of every session — each entry should
   read as a standing rule, not a diary.
3. If a bullet here turns out to be wrong or the user's taste has shifted,
   edit it in place rather than appending a contradicting entry.
