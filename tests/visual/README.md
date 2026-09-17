# Visual tests

Browser-driven checks for the CasaRay dashboard markup.

## Running

`playwright` is installed in the **global** Node root, not in this repo — there
is no `node_modules/` here at all. A bare `node` run therefore fails with
`MODULE_NOT_FOUND`, because module resolution walks up from `tests/visual/`
and never reaches `/opt/node22/lib/node_modules`:

```bash
NODE_PATH="$(npm root -g)" node tests/visual/browser_smoke.js
```

`browser_smoke.js` confirms the toolchain end to end: it launches headless
Chromium, renders a trivial page and writes a PNG. Exit 0 and a
`PASS:` line mean the browser stack is usable.

## Environment

| Piece | State |
|---|---|
| `playwright` | 1.56.1, global (`npm root -g`) |
| `@playwright/test` | **not installed** — no runner, no `test()`/`expect()` |
| Chromium | 141.0.7390.37 at `/opt/pw-browsers/chromium` |

Scripts pass `executablePath: '/opt/pw-browsers/chromium'` explicitly, so they
keep working if a differently-pinned Playwright is installed later. Never run
`playwright install` here: `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` is set and the
browser is already provisioned.

## Scope — read before writing a test

This environment has **no `/config`, no supervisor and no route to the Home
Assistant instance** (`CLAUDE.md`, "What cannot be verified from here";
`ha_validate.sh` section 8 SKIPs for exactly this reason). So these tests can
only exercise markup rendered from static content in the page. They **cannot**
load the live dashboard, and a passing run here still never proves a card
renders on the wall iPad. Layout claims — `columns`, `max_columns`, whether a
band resolves two across — need a live screenshot, per `DR-012` and `DR-013`.

## Screenshots

`screenshots/` is generated output and is gitignored; see the note in
`screenshots/.gitignore` before adding baselines, as committing binaries there
fails `ha_validate.sh` section 7.
