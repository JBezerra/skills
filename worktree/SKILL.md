---
name: worktree
description: Borrow an isolated, pre-warmed git worktree from the treehouse pool and return it when done. Use whenever a task needs a worktree or its own checkout, or the user asks how treehouse works.
---

# Worktree (treehouse)

`treehouse` keeps a pool of reusable git worktrees per repo at `~/.treehouse/<repo>-<hash>/<N>/<repo>`, at most 5. A returned slot keeps its gitignored files (`node_modules`, `dist`), so the next borrower starts warm. Reach for a treehouse slot instead of `EnterWorktree` with `name` or a bare `git worktree add`.

## Steps

1. **Borrow.** From the repo: `treehouse get --lease --lease-holder "claude:$CLAUDE_CODE_SESSION_ID"`. Stdout carries only the slot path; banners go to stderr. Each lease gets its own slot, so parallel sessions stay isolated. Done when you hold the path.
2. **Enter.** `EnterWorktree` with that `path`.
3. **Branch.** The slot is a detached HEAD at the latest default branch. Run `git switch -c <branch>` (or `git switch <existing>`) before the first commit.
4. **Set up.** Gitignored build output is left over from the slot's previous borrower, built from another branch. Run the repo's setup before any check (Spark: `yarn install && yarn build`, with `yarn build:clean` first if the build acts strange). Done when setup exits 0.
5. **Return**, only once the user says the work is done. `ExitWorktree` with `action: "keep"`, then `treehouse return --if-lease-holder "claude:$CLAUDE_CODE_SESSION_ID" <path>`, which refuses a slot another session holds. Return kills processes still running in the slot and resets it to the default branch, so uncommitted work and commits on no branch are gone. Exit 3 means the slot is dirty and was left untouched: show the user what is uncommitted, and add `--force` only with their approval.

## Reference

- **Sandbox.** treehouse writes under `~/.treehouse` and fetches origin, so run `get`, `return`, `destroy`, and `prune` with the sandbox disabled.
- **Seeding.** A user-level `post_create` hook (`~/.config/treehouse/seed.sh`, set in `~/.config/treehouse/config.toml`) copies the files listed in `~/.config/treehouse/include/<repo>` (local config, `.tool-versions`, `.claude/settings.local.json`) from the main checkout into the slot on every borrow. To give every slot another file, add it to that list.
- **Pool full.** `get` fails when all 5 slots are in use, leased, or dirty. Run `treehouse status` and ask the user which slot to free; removing slots is the user's call.
- **Leases outlive the session.** A leased slot stays out of the pool until `treehouse return`. `treehouse status` lists leases by holder, so this session's slot is the one held by `claude:$CLAUDE_CODE_SESSION_ID`. A slot from an earlier or forked session carries another id; return it with a plain `treehouse return <path>` only when the user asks.
- **Version.** Installed is v2.3.0. The online README documents unreleased features (`--include-file`, `--base`, `.worktreeinclude`, `--unique-leaf`, `--worktree-path`); `treehouse <cmd> --help` is the source of truth.
- **Human use.** The user's own flow is interactive: `treehouse` opens a subshell in a slot, `exit` returns it to the pool. The slot stays on disk; only `treehouse prune --yes` or `treehouse destroy <path> --yes` delete slots.
