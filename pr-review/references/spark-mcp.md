# spark-mcp Repo-Specific Review Checklist

This file applies when reviewing PRs in `smartprocure/spark-mcp`. Load it when `--repo spark-mcp` is passed or when the git remote is `smartprocure/spark-mcp`.

spark-mcp is a Python MCP server that exposes data tools to AI agents (Claude, etc.) via both the MCP protocol and a REST API. Every feature must work in both transports.

---

## New MCP tool — mandatory checklist

When a PR adds a new tool or feature package, every item below is required. Missing items are **blockers** unless the PR explicitly and intentionally defers them (with a follow-up ticket or note).

- [ ] **REST parity**: `routes.py` exists under `spark_mcp/features/<tool_name>/`. Every MCP tool must also be accessible via REST.
- [ ] **Both auth methods work on REST routes**: Bearer token AND API key. Test mentally against both. A route that only accepts one is broken for the other half of clients.
- [ ] **Observability mapping**: entry added to `spark_mcp/core/observability.py`. Every tool must be mapped.
- [ ] **Observability events**: events emitted from the tool (as done in `execute_tool_with_guards`). Check that the pattern is followed, not just the mapping entry.
- [ ] **Entitlement gate**: if the feature is permission-gated, the gate is applied. Check `spark_mcp/entitlements.py` and the relevant middleware. Reference the org's `permission` field — entitlements do NOT come from `userProfile`.
- [ ] **Cache layer**: if other search/data tools in the codebase cache (they do), this tool should too. Also check the TTL — the default (8h) may be too long for the data type. Lower TTLs are often appropriate for user-specific or frequently-changing data.
- [ ] **AI-facing instructions**: `instructions.md` exists, is accurate, and only describes capabilities the system actually has. Outdated or hallucinated capabilities in instructions directly mislead the agent at runtime.

---

## Analytics tools — additional requirements

Analytics tools (bids, contracts, federal contracts, federal opportunities, contacts, spending, etc.) have additional requirements beyond the base checklist:

- [ ] Instructions include aggregation types context (so the agent knows how to build queries)
- [ ] Instructions include the data type's schema / field list (so the agent can construct trees)
- [ ] Deprecated fields are removed from instructions
- [ ] Instructions are aligned with the consolidated analytics instructions pattern (check existing analytics tool instructions for the expected format)

---

## Auth changes — regression check

When a PR touches `spark_mcp/auth.py`, `spark_mcp/middleware.py`, OAuth routes, or any auth-related code:

- [ ] All three existing auth paths still work: AMA JWT, API key, WorkOS OAuth
- [ ] No path that previously accepted tokens now rejects them
- [ ] Env var names accurately describe what they hold (e.g., `WORKOS_APP_API_KEY` not a generic or misleading name)

Auth regressions are hard blockers. The AMA JWT path in particular is easy to accidentally break when adding WorkOS logic — verify explicitly.

---

## General patterns to enforce

**Feature package structure**: new tools live in `spark_mcp/features/<tool_name>/` with `__init__.py`, `tool.py`, `routes.py`, `instructions.md`, and `models.py` as needed.

**Entitlement/permission source**: entitlement data lives on the org's `permission` field. Not on `userProfile`. Flag any code or documentation that confuses these.

**Gate bypass logic**: if a gate has a bypass condition (e.g., embedded access, govspendMCP permission), that bypass logic belongs in the specific middleware where it applies — not as a parameter threaded through a generic filter function like `filter_tools_by_permissions`. Colocation makes it discoverable and auditable.

**Tool registration integrity**: new tool additions must not inadvertently remove or shadow existing tool registrations. Check `__init__.py` files and any config registry that lists tools (e.g., `tree_pipeline/configs/pipelines/__init__.py`). A PR that adds tool B while accidentally removing tool A from the registry is a regression blocker.

**Instruction accuracy**: AI-facing `instructions.md` files must only describe what the system can actually do. Don't describe SAM.gov search if there's no SAM.gov tool. Don't reference capabilities that require a web search harness if none is wired. Wrong instructions cause silent agent failures.
