// Renders the four Home concepts side by side for the V3-004 design review.
//
//   NODE_PATH="$(npm root -g)" node design/casaray-v3/tools/capture_comparison.cjs <dc-runtime.js>
//
// Concepts A–C are Design-canvas artboards (concepts/*.dc.html). They need
// the canvas runtime as ./support.js, which is not in this repository. Fetch
// artifact-type/dc-runtime.js from the "CasaRay V3 — Home concepts" design
// artifact and pass its path. The concept files are copied, byte for byte,
// into a temporary folder next to that runtime and rendered unmodified.
//
// Concept D is prototype/index.html in its "Concept review" scenario, which
// carries the same snapshot A–C are drawn on (concepts/README.md), with the
// clock fixed at Thursday 25/09/26 16:20.
//
// All four are captured at 1180×820 (the wall iPad), in English and Chinese.
// D also gets a full-page capture, because unlike A–C its Home scrolls.
// Output: screenshots/cmp_*.png (git-ignored, like every render).
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const V3 = path.resolve(__dirname, '..');
const OUT = path.join(V3, 'screenshots');
const runtime = process.argv[2];
if (!runtime || !fs.existsSync(runtime)) {
  console.error('usage: capture_comparison.cjs <path to dc-runtime.js>');
  process.exit(2);
}
const FRAME = { width: 1180, height: 820 };
const CLOCK = new Date(2026, 8, 25, 16, 20, 0); // local time, as the concepts show it

const fontCache = new Map();
async function fonts(route) {
  const url = route.request().url();
  try {
    if (!fontCache.has(url)) fontCache.set(url, execFileSync('curl', ['-sSfL', '--max-time', '30', '-A', 'Mozilla/5.0 Chrome/140', url], { maxBuffer: 64 << 20 }));
    await route.fulfill({ status: 200, body: fontCache.get(url), headers: { 'content-type': url.includes('googleapis') ? 'text/css' : 'font/woff2', 'access-control-allow-origin': '*' } });
  } catch (e) { await route.abort(); }
}

async function open(browser, url) {
  const ctx = await browser.newContext({ viewport: FRAME, deviceScaleFactor: 2, colorScheme: 'dark' });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(String(e)));
  await page.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, fonts);
  await page.clock.setFixedTime(CLOCK);
  await page.goto(url);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  return page;
}

(async () => {
  const stage = fs.mkdtempSync(path.join(os.tmpdir(), 'casaray-concepts-'));
  fs.copyFileSync(runtime, path.join(stage, 'support.js'));
  for (const k of ['A', 'B', 'C']) fs.copyFileSync(path.join(V3, 'concepts', `Concept${k}.dc.html`), path.join(stage, `Concept${k}.dc.html`));

  const browser = await chromium.launch();
  const report = [];
  for (const k of ['A', 'B', 'C']) {
    for (const lang of ['en', 'zh']) {
      const p = await open(browser, 'file://' + path.join(stage, `Concept${k}.dc.html`));
      await p.waitForTimeout(800); // the runtime mounts asynchronously
      if (lang === 'zh') {
        const btn = p.locator('[aria-label="Switch language"]').first();
        if (await btn.count()) { await btn.click(); await p.waitForTimeout(300); } else report.push(`${k}: no language button found`);
      }
      const text = await p.evaluate(() => document.body.innerText.length);
      if (text < 200) report.push(`${k}/${lang}: rendered only ${text} characters, check the runtime`);
      await p.screenshot({ path: path.join(OUT, `cmp_${k}_${lang}.png`) });
      if (p.errors.length) report.push(`${k}/${lang}: ${p.errors.join(' | ')}`);
      await p.context().close();
    }
  }
  for (const lang of ['en', 'zh']) {
    const p = await open(browser, 'file://' + path.join(V3, 'prototype', 'index.html'));
    await p.waitForFunction(() => window.__casaray);
    await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await p.locator('[data-overlay="demo"]').click();
    await p.locator('[data-scenario="review"]').click();
    await p.keyboard.press('Escape');
    if (lang === 'zh') await p.locator('[data-lang]').click();
    await p.evaluate(() => { document.querySelector('#toast-slot').innerHTML = ''; window.scrollTo(0, 0); });
    await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(OUT, `cmp_D_${lang}.png`) });
    if (lang === 'en') {
      await p.screenshot({ path: path.join(OUT, 'cmp_D_en_fullpage.png'), fullPage: true });
      const h = await p.evaluate(() => document.documentElement.scrollHeight);
      report.push(`D: Home is ${h}px tall at 1180×820, ${(h / FRAME.height).toFixed(1)} screens`);
    }
    if (p.errors.length) report.push(`D/${lang}: ${p.errors.join(' | ')}`);
    await p.context().close();
  }
  await browser.close();
  fs.rmSync(stage, { recursive: true, force: true });
  console.log(report.join('\n') || 'ok');
  console.log(`wrote cmp_{A,B,C,D}_{en,zh}.png and cmp_D_en_fullpage.png to ${path.relative(process.cwd(), OUT)}`);
})().catch((e) => { console.error(e); process.exit(1); });
