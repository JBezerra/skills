# agent-browser tactics

Learned the hard way. Each of these has produced a false positive or a wasted hour at least once.

## Reading the page

- **`agent_browser_snapshot` is extremely verbose.** Prefer `agent_browser_eval` returning `element.innerText.split('\n').filter(Boolean)` scoped to the feature's container. Use `agent_browser_screenshot` (jpeg, quality 70-75) for visual ACs, and describe what you see in prose rather than saving files.
- **Only rows in the DOM are the visible window.** Never conclude "the list has N items" from a `querySelectorAll` length on a virtualized list. Counts come from the app's own count label, the API response, or the database.

## Selectors

- **React Aria ids contain colons and break CSS selectors.** Target them with suffix attribute selectors: `[id$="-option-<key>"]`.
- Prefer accessible names and `data-*` attributes over structural selectors; the diff told you the exact aria-label, use it.

## Input

- **`agent_browser_fill` with an empty string is a no-op.** To clear a field: `type` with `clear: true` and a single character, then press `Backspace`.
- **`Meta+a` / `Control+a` do not select-all inside these search fields.** Don't rely on them to clear input.

## Scrolling

- **Virtualized lists only scroll for real input.** `mouse_move` over the list, then `mouse_wheel`. Setting `scrollTop` or using the scroll tool silently does nothing, and the resulting "pagination is broken" is a false positive.
- To reach the end of a long list, focus a row and press `End`.

## Races

- To test a same-tick race, dispatch `pointerdown` / `pointerup` / `click` on two elements inside a single `agent_browser_eval`.
- Then repeat the same two actions as normal tool clicks. If the second attempt passes, report the race as **needing sub-frame timing** rather than as a plain bug: a real user is unlikely to hit it.

## Verifying network behavior

`curl` to localhost is blocked by the sandbox, so the browser is the only path to the API. Use `agent_browser_network_requests` (or `network_har_start` / `network_har_stop` around a flow) to inspect the actual request and response payloads a save produced.
