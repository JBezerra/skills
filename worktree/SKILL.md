---
name: worktree
description: Borrow an isolated, pre-warmed git worktree from the treehouse pool and return it when done. Use whenever a task needs a worktree or its own checkout, before starting dev servers inside a treehouse slot (cwd under ~/.treehouse), or when the user asks how treehouse works.
---

# Worktree (treehouse)

`treehouse` keeps a pool of reusable git worktrees per repo at `~/.treehouse/<repo>-<hash>/<N>/<repo>`, at most 5. A returned slot keeps its gitignored files (`node_modules`, `dist`), so the next borrower starts warm. Reach for a treehouse slot instead of `EnterWorktree` with `name` or a bare `git worktree add`.

## Steps

1. **Borrow.** From the repo: `treehouse get --lease --lease-holder "claude:$CLAUDE_CODE_SESSION_ID"`, plus `-b <branch>` when the work needs a new branch. Stdout carries only the slot path; banners go to stderr. Each lease gets its own slot, so parallel sessions stay isolated. Done when you hold the path.
2. **Enter.** `EnterWorktree` with that `path`.
3. **Branch.** With `-b`, the slot is already on the new branch. Without it, the slot is a detached HEAD at the latest default branch: for an existing branch (a PR), `git fetch origin <branch>` then `git switch -c <branch> --track origin/<branch>`. `-b` fails if the branch already exists locally, so never use it for a PR branch.
4. **Set up.** Gitignored build output is left over from the slot's previous borrower, built from another branch. Run the repo's setup before any check (Spark: `yarn install && yarn build`, with `yarn build:clean` first if the build acts strange). Done when setup exits 0.
5. **Return**, only once the user says the work is done. Stop any dev servers you started, then `ExitWorktree` with `action: "keep"`, then `treehouse return --if-lease-holder "claude:$CLAUDE_CODE_SESSION_ID" <path>`, which refuses a slot another session holds. Return kills processes still running in the slot and resets it to the default branch, so uncommitted work and commits on no branch are gone. Exit 3 means the slot is dirty and was left untouched: show the user what is uncommitted, and add `--force` only with their approval.

## Dev servers

Every Spark checkout claims the same ports: API `1337`, web `3000`. A second slot's servers collide with the first, or its web quietly talks to the other slot's API, because web's dev config pins `apiUrl: 'http://localhost:1337'`. Before starting dev servers in a slot:

1. **Pick ports.** Walk up from `1337` and from `3000` with `lsof -nP -iTCP:<port> -sTCP:LISTEN`; take the first free port of each. For each busy port, `lsof -a -p <pid> -d cwd` names the checkout holding it.
2. **Point web at its API.** Add `apiUrl: 'http://localhost:<api>'` to the slot's `web/src/config/env/local.js`. It is gitignored, so the slot stays clean, and the next borrow re-seeds the original.
3. **Start API and web separately**, not with the root `yarn start`. vite does not skip a busy `3000` reliably: when the main checkout holds `127.0.0.1:3000`, the slot's vite binds `[::1]:3000` beside it and `localhost:3000` becomes ambiguous. Put this in a script file and run it in the background (a worktree-isolated session refuses an inline env-prefixed `yarn` command):

   ```sh
   cd <slot>
   export NODE_CONFIG='{"port":<api>,"apiUrl":"http://localhost:<api>","apiUrlInternal":"http://localhost:<api>","appUrl":"http://localhost:<web>"}'
   (cd api && yarn start:watch) &
   cd web
   export NODE_ENV=development NODE_APP_INSTANCE=govspend VITE_NODE_ENV=development VITE_NODE_APP_INSTANCE=govspend
   ./scripts/build-public.sh
   yarn vite --port <web> --strictPort &
   wait
   ```

   `NODE_CONFIG` outranks every config file, `local.json` included; web ignores it. The web exports mirror `web/scripts/start.sh`; re-read it if that script changes. Done when `lsof` shows both ports listening and `curl` (sandbox disabled) gets any HTTP status from each; the API answers `404` on `/`.
4. **Report.** Done when the user has the slot path, the API URL, the web URL, and which checkout holds each port you skipped.

## Reference

- **Sandbox.** treehouse writes under `~/.treehouse` and fetches origin, so run `get`, `return`, `destroy`, and `prune` with the sandbox disabled.
- **Seeding.** A user-level `post_create` hook (`~/.config/treehouse/seed.sh`, set in `~/.config/treehouse/config.toml`) copies the files listed in `~/.config/treehouse/include/<repo>` (local config, `.tool-versions`, `.claude/settings.local.json`) from the main checkout into the slot on every borrow. To give every slot another file, add it to that list.
- **Pool full.** `get` fails when all 5 slots are in use, leased, or dirty. Run `treehouse status` and ask the user which slot to free; removing slots is the user's call.
- **Leases outlive the session.** A leased slot stays out of the pool until `treehouse return`. `treehouse status` lists every slot with its checked-out branch and its lease holder, so this session's slot is the one held by `claude:$CLAUDE_CODE_SESSION_ID`. A slot from an earlier or forked session carries another id; return it with a plain `treehouse return <path|name>` only when the user asks. `treehouse lease <name>` leases a slot that is already in use without touching its files.
- **Version.** Installed is v3.1.2. `get` also takes `--base <branch>` (cut from a branch other than the default), `--include-file` (a one-off seeding list), `--unique-leaf` and `--worktree-path`; none are needed for the steps above. `treehouse <cmd> --help` is the source of truth.
- **Human use.** The user's own flow is interactive: `treehouse` opens a subshell in a slot, `exit` returns it to the pool. The slot stays on disk; only `treehouse prune --yes` or `treehouse destroy <path> --yes` delete slots.
