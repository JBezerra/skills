---
name: mergi-backlog
description: >
  Drives a single mergi backlog item end to end: pick a ticket from the mergi
  backlog, present a solution path, get the user's sign-off, plan it with /sdd
  (simplest solution), implement the lazy way (/ponytail), self-verify in
  isolation, then clean up temporary scaffolding and commit. Trigger whenever
  the user wants to work a mergi backlog item — "let's do another one", "pick a
  ticket", "work the mergi backlog", "implement a backlog item", "/mergi-backlog".
  Mergi is the Electron + React + TypeScript GitHub PR-review app at
  ~/source/mergi; its backlog lives at ~/source/@specs/mergi/backlog.md.
---

# Mergi backlog flow

Ship one backlog item at a time, smallest correct change, with a hard sign-off
gate before any code is written. The order below is the whole skill — do not
skip or reorder.

## 0. Context

- **App:** `~/source/mergi` — Electron (main/preload/renderer) + React + TS. Read
  `AGENTS.md` for the traps (two "god files", duplicated thread UI, dual-schema
  DB, copy-pasted offline fallback).
- **Backlog:** `~/source/@specs/mergi/backlog.md` — each item has a type,
  description, `file:line` references, ACs, and per-item open questions. This is
  the source of tickets.
- **Recalled memory:** `build-ui-cdp-gotchas` covers the CDP force-reload and
  the dev-harness route for auth-gated views — reuse it, don't rediscover it.

## 1. Pick a ticket

If the user named an item, use it. Otherwise read the backlog and **recommend
one**, favoring self-contained, low-risk, high-value items (no new IPC/backend,
no design mock needed) unless the user asks for something bigger. State your
pick and a one-line why; offer one or two alternatives. Let the user redirect.

## 2. Present a solution path

Ground it in the real code first (read the files the backlog cites; confirm
they still say what the backlog claims). Then present, concisely:

- **Where** — the exact file(s) and roughly where in them.
- **How** — the approach, at the altitude of "what I'll change", not a diff.
- **Behaviors** — the observable outcomes, including edge cases.
- **What I'm skipping** and when it'd be worth adding (ponytail framing).

If there are genuine scope-defining forks (behavior choices, hosting, UX shape),
ask them with `AskUserQuestion`, recommendation first. Don't ask about things
with an obvious default or answerable from the code.

## 3. Sign-off gate — STOP HERE

**Do not run /sdd, write code, create files, or start the app until the user
signs off on the solution path.** Present it and wait.

The only exception: the user has explicitly granted autonomy for this run
("go ahead without asking", "you don't need my sign-off", "just do it"). Absent
that, a plausible-looking plan is not permission. (This gate exists because the
user prefers the simplest solution and wants to veto approach before code —
e.g. "just hide the button" beat a new IPC + menu item.)

## 4. Plan with /sdd

After sign-off, invoke the `/sdd` skill to turn the agreed approach into a
reviewed plan, steering it toward the **simplest** implementation. Fold any
`AskUserQuestion` answers into the plan.

## 5. Implement the simplest solution

- Invoke `/ponytail` first (the repo's `CLAUDE.md` requires it). Shortest
  working diff; no unrequested abstractions; reuse what's there.
- Leave one runnable check behind for non-trivial logic (a parser/branch): a
  co-located vitest `*.test.ts` exporting the pure helper, matching the repo's
  existing test style.
- After editing, run prettier on **exactly the files you touched** (never the
  whole repo): `./node_modules/.bin/prettier --write <files>`.
- Typecheck with tsc directly (see toolchain notes):
  `./node_modules/.bin/tsc --noEmit -p tsconfig.web.json --composite false`
  (and `tsconfig.node.json` for main/preload changes).

## 6. Verify it yourself, in isolation

Prove the change works at its real surface by running the app — not by running
tests. Most UI logic can be exercised **offline, in isolation**, without real
GitHub data. See `references/verify-in-isolation.md` for the full recipe
(temporary harness route, CDP driving, the node/toolchain gotchas). The shape:

1. `npm run dev` (enables CDP on :9222 in dev). Use the **x64 node** — see notes.
2. Add a **temporary** dev-only route (e.g. `/harness`) in `App.tsx`, outside
   `AuthGuard`, that mounts just the changed component with local state. This
   avoids auth and real PRs entirely.
3. Drive it with `playwright-core` over `connectOverCDP('http://127.0.0.1:9222')`:
   force a reload (Fast-Refresh staleness), type with a **~50–60ms per-key
   delay** (fast synthetic typing races controlled React inputs and scrambles
   text), and read state back (e.g. `inputValue()`) as evidence.
4. Cover the happy path **and** at least one off-path probe (escape hatch,
   empty input, non-matching input). Capture a screenshot for the report.

Report PASS/FAIL with the observed outputs, not just a verdict.

## 7. Clean up and commit

Only when everything passes:

- **Remove all temporary scaffolding**: revert the harness route
  (`git checkout -- src/renderer/src/App.tsx`), delete temp driver scripts, and
  stop the dev server you started (`pkill -f electron-vite`; confirm :9222 is
  down). Verify `git status` shows only the real change + its test.
- **Commit** (mergi convention): commit to `main` (the established pattern),
  **no `Co-Authored-By` trailer**, concise message. Push only if asked.

---

## Toolchain notes (this environment)

- **asdf shims are broken in the non-interactive shell** (`exec: asdf: not
  found`). Run node tools via an absolute install path instead of `npm`/`npx`.
- **arm64 vs x64 mismatch:** `prettier` and `tsc` run fine under the arm64 node
  (`~/.asdf/installs/nodejs/20.20.2/bin`). But the installed rollup binary is
  `rollup-darwin-x64`, so the **dev server / vite must run under x64 node**
  (`/usr/local/bin/node`, i.e. `PATH="/usr/local/bin:$PATH" npm run dev`).
- **vitest cannot run in this sandbox** (arm64 → missing rollup native binary;
  x64 → `ERR_REQUIRE_ESM`). The committed test still verifies logic in CI. To
  sanity-check a pure helper locally, copy it into a scratch `.mjs` and run
  `node`-assert against it — but that is not a substitute for step 6.
