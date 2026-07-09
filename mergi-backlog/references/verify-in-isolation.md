# Verifying a mergi UI change in isolation (offline)

The goal: run the real changed component at its real surface, without auth or
live GitHub data, and observe behavior. This is the recipe that worked.

## 1. Start the dev app (CDP on :9222)

Dev mode enables Chrome DevTools Protocol on port 9222 (`is.dev` gate in
`src/main/index.ts`). Launch with **x64 node** to match the installed
`rollup-darwin-x64` binary:

```bash
cd ~/source/mergi
PATH="/usr/local/bin:$PATH" nohup npm run dev > /tmp/mergi-dev.log 2>&1 &
# wait for CDP:
for i in $(seq 1 20); do
  curl -s http://127.0.0.1:9222/json/list | grep -q '"type": "page"' && { echo UP; break; }
  sleep 3
done
```

## 2. Add a temporary harness route

Mount only the component under test, with local state, on a route **outside
`AuthGuard`** so it needs no login and touches no real PR. In
`src/renderer/src/App.tsx`:

```tsx
// TEMP verify harness — remove after verifying
function Harness() {
  const [value, setValue] = useState('')
  const [preview, setPreview] = useState(false)
  return (
    <div style={{ padding: 24 }}>
      <ReviewEditor value={value} onChange={setValue}
        previewMode={preview} onPreviewModeChange={setPreview} />
    </div>
  )
}
```

Add it as the first route, before `/login` and the `*` AuthGuard route:

```tsx
<Route path="/harness" element={<Harness />} />
```

Check the component mounts without its usual providers (e.g. mergi's
`useImageUpload()` returns `null` with no provider — fine unless you paste).

## 3. Drive it with playwright-core over CDP

`playwright-core` is a devDependency. The script must live **inside the repo**
(so `node_modules` resolves) — the scratchpad won't resolve the import. Run
with x64 node.

```js
import { chromium } from 'playwright-core'
const b = await chromium.connectOverCDP('http://127.0.0.1:9222')
const page = b.contexts()[0].pages()[0]

async function fresh() {
  await page.goto('http://localhost:5173/#/harness', { waitUntil: 'domcontentloaded' })
  await page.reload({ waitUntil: 'domcontentloaded' })   // beat Fast-Refresh staleness
  await page.waitForSelector('textarea', { timeout: 8000 })
  await page.locator('textarea').first().click()
}
const val = () => page.locator('textarea').first().inputValue()

await fresh()
await page.keyboard.type('- first', { delay: 60 })   // slow typing! see gotcha below
await page.keyboard.press('Enter')
await page.keyboard.type('second', { delay: 60 })
console.log(JSON.stringify(await val()))              // evidence
await page.screenshot({ path: 'scratchpad/evidence.png' })
await b.close()
```

## Gotchas (learned the hard way)

- **Force reload after adding/editing the harness** — Fast Refresh can serve a
  stale tree; `page.reload()` after `goto` fixes it.
- **Type slowly (`{ delay: 50-60 }`).** Fast synthetic `keydown`s race a
  controlled React `<textarea>` (state update + `setSelectionRange` in a
  `requestAnimationFrame`) and scramble the text (`- first` → `-o lfirst`).
  This is a test-driving artifact, NOT a product bug — real typing is fine.
- **Reload between scenarios** for deterministic empty state, or select-all +
  delete via keyboard (setting `.value` in JS won't update React state).
- **Read `inputValue()`**, not the DOM text, to get the true textarea value.
- Typing into the composer does **not** submit — submit is Cmd+Enter. So you
  can exercise the editor freely without posting anything.

## 4. Clean up (always)

```bash
cd ~/source/mergi
git checkout -- src/renderer/src/App.tsx      # drop the harness route + Harness()
rm -f ./_verify_tmp.mjs                        # any in-repo driver scripts
pkill -f electron-vite ; pkill -f "source/mergi/node_modules/electron"
curl -s http://127.0.0.1:9222/json/list >/dev/null && echo "still up" || echo "down"
git status --short                             # confirm only the real change remains
```
