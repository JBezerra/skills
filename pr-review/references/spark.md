# spark Repo-Specific Review Reference

Node/TypeScript monorepo (FeathersJS API + React/Tailwind `.tsx` web) for GovSpend's procurement intelligence platform.

---

## API

Patterns JBezerra consistently flags on backend code (services, hooks, jobs, utils, schemas, AI prompts).

### Types & Schemas

- **`any` type is a blocker** — use proper types or import from `@feathersjs/feathers` (`Params`) or Zod. Flag every occurrence in the PR, not just the first one.
- **Service `create`/`patch` arguments must be typed** — use Zod schemas or explicit TypeScript types for `data`; use `Params` from `@feathersjs/feathers` for `params`. No untyped handler signatures.
- **Unnecessary casts are a blocker** — e.g., `new ObjectId(user.organization)` when the field is already an ObjectId. Flag all instances with "Consider it everywhere applicable."
- **Variable naming convention** — `camelCase` everywhere, including scripts. `create_chat_integration_link_schema` → `createChatIntegrationLinkSchema`.

### Architecture & Co-location

- **Co-location over shared utils** — if a helper is only used in one service, move it next to that service. Generic utils belong in shared files only when they're genuinely reusable across the codebase.
- **Avoid over-abstraction** — inline simple database calls directly in the service so behavior is explicit. One-off wrappers that hide a single call are a net negative.
- **Prefer Feathers service over middleware** — **question:** flag any new middleware that could instead be a standard Feathers service.
- **Config belongs next to its usage, not in env vars** — **blocker:** moving non-secret config into `.env` is wrong; colocate it with the code that uses it.
- **Consolidate auth methods in one service** — don't create a separate service for each auth mechanism; encapsulate all auth variants in the existing `feathers` service.
- **Hook-level filters belong in `api/src/hooks`** — **suggestion:** shared hooks go in the shared hooks directory, not inside a specific service.

### Purity & Mutation

- **No argument mutation** — **blocker:** mutating function arguments violates the codebase's Coding Standards. Extract into a pure function instead.
- **Avoid undo-on-failure patterns** — **suggestion:** check preconditions before writing data rather than rolling back after the fact.
- **Don't fetch the same resource twice in the same handler** — flag it with a line reference.

### Complexity & Resilience

- **Seek the simplest solution** — weigh resilience vs accidental complexity vs likelihood vs downstream effects. "Every line is a liability." Example: a Lua script for Redis atomicity is not worth it when the race condition is rare and low-impact.
- **Don't add `await` to fire-and-forget calls** — if a workflow is time-sensitive and the result is not needed, omit `await`.
- **Caching must be keyed on the actual dependencies** — LLM response caches should be keyed by the source record id, not by derived signal data. Miskeyed caches are a blocker.
- **Don't duplicate utilities** — if something already exists in `common-node`, use it. **question:** why can't we use the one from `common-node`?

### Tests & Observability

- **Tests must gate bugs, not mock configs** — tests that only verify mocks work, configs exist, or that values pass through (`thread_ts`, etc.) add no value. Test business logic extracted into pure functions.
- **`isDeleted: false` is wrong** — **take or leave:** use `isDeleted: { $ne: true }` to match the codebase's pattern.

### AI / Prompts

- **Prompt output must be clean** — **blocker:** prompts that leak chain-of-thought into their output need to be fixed. Output should be clean, not contain internal reasoning.
- **Use the simplest auth method that fits** — prefer API key over access token if user-specific data is not needed.

---

## Web

Patterns JBezerra consistently flags on frontend code (React components, pages, composables, hooks, tests).

### Styling

- **Tailwind is the styling technology** — **blocker:** no inline styles, CSS modules, or non-Tailwind class names. Check `web/src/pages/opportunities/` and `web/src/pages/aiSearch/` as the canonical examples.
- **Use the design system token scale** — **blocker:** spacing classes like `p-8` don't exist; use t-shirt sizes (`p-2xs`, `p-xl`, etc.). Flag all non-token Tailwind values.
- **SVG icons must not have hardcoded `fill`** — **blocker:** remove `fill` from SVGs added to the icon library so they inherit color from the parent.
- **Sticky headers/footers in sidebars** — **blocker:** sidebar `Header` and `Footer` must be sticky; ensure they're excluded from the scrollable area.

### Component Design

- **No `React.FC`** — **blocker:** type props directly with an interface. Convention: `interface ChatConnectPageProps { ... }`.
- **Use `PageRoute<RouteState>` for route typing** — **blocker:** route config objects must be typed.
- **Remove unused capabilities from component APIs** — **question:** if a feature (e.g. flat sections, `selectionMode`) is not a requirement, remove it from the component API.
- **Inline simple schemas and default values** — **suggestion:** if a Zod schema or default values object is only used in one place, inline it rather than exporting from a separate constant.
- **Comments above JSX sections signal a component boundary** — **suggestion:** if you're adding a comment to label a section of JSX, that section is a good candidate to become its own component or file.
- **Implement side-effects as natural React patterns** — **suggestion:** `setSignalId` as a side-effect of `ModalCloseButton` is cryptic; use a standard `onClose` prop or `useEffect`.

### State & Data Fetching

- **Fetch from React Query cache when possible** — **suggestion:** don't re-fetch data that's already in the query cache.
- **Add `staleTime: Infinity` for stable reference data** — **suggestion:** avoid refetch-on-window-focus for data that doesn't change between sessions.
- **Don't recalculate what's already computed** — if a value is derived in `index.ts` at route init, don't recompute it inside the page component.
- **`select` should narrow to only what's needed** — use `lodash.pick` or equivalent to select specific fields from a query, e.g., `select: (data) => lodash.pick(data.profile, ['signalTypes'])`.
- **Loading skeletons should be independent per data source** — skeleton state for tab A should not block tab B's content from appearing.

### Analytics

- **Analytics event names must match the spec exactly** — **blocker:** implement every event listed in the AC; missing events (e.g. `Dislike_click`) are a blocker. Prefix/naming must match the stakeholder's system.
- **`category` field is required on all analytics calls** — **blocker:** every `analytics.track(...)` must include `category: 'Opportunities'` (or the relevant module name).
- **Don't hardcode domain-specific fields into shared hooks** — **blocker:** `signalType` does not belong in a generic `usePrismaticTriggerFlow` hook; pass it as an arbitrary payload param instead.

### Tests

- **Tests must catch regressions** — **blocker:** a test that still passes when the fix is reverted is not a useful test.
- **Minimize mocks** — excessive mocks (`IntersectionObserver`, `useRouter`, `useRoute` all in one file) are tech debt. Prefer in-memory solutions and real behavior over mock-heavy suites.
- **Don't duplicate test suites** — if `Page.test.tsx` already covers the behavior, drop the redundant `index.test.ts` suite.
- **Test behavior, not pass-through** — don't write tests that verify a value is passed downstream. Test what the user sees or what the system does.

### Copy & UX

- **Error/status messages need product input** — **suggestion:** UI copy (error messages, empty states, token-expired text) must be consistent with the product's tone. Propose copy aligned with the overall voice.
- **Fallback values must not be silently dropped** — **blocker:** when refactoring, verify that dash (`-`) or empty-state fallbacks for optional fields (email, phone, etc.) are preserved.
- **No `console.log` left in production code** — **question:** flag any `console.log` with "why are we logging this?"

---

## Shared (applies to both)

- **No `SCREAMING_CASE` constants** — per Coding Standards, use `camelCase` for all variables and constants, including test fixtures.
- **JS Docs on exported composables/hooks** — **suggestion:** add JSDoc comments to `useUserSignals`, `useLazySignals`, and equivalent hooks that are consumed across the app.
- **Add comments on non-obvious side-effects** — **suggestion:** if a `useEffect` or hook call has a non-obvious reason for existing, add an inline comment explaining why.
- **Conditional chains must be declarative and ordered** — prefer early-return guard clauses over nested conditions. Order: `isPending` → `!hasRequiredData` → happy path. Each branch should be independent, not rely on the negation of previous branches being already checked.
- **Runtime types must not lie** — don't type a value as `Date` if it arrives as `string` at runtime. Keep types honest to avoid subtle bugs downstream.
