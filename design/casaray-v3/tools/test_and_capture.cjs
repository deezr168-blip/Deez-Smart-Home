// CasaRay V3 prototype — test harness and screenshot capture.
//
//   NODE_PATH="$(npm root -g)" node design/casaray-v3/tools/test_and_capture.cjs
//
// Loads prototype/index.html from disk in headless Chromium, then:
//   1. navigation   — every board opens from the rail and from the phone tab bar,
//                     room drill-in and back work, deep links resolve
//   2. responsive   — no horizontal page scroll on any board at phone, portrait
//                     tablet, landscape wall iPad and desktop widths
//   3. interaction  — lights, brightness, language, theme, scenarios, bills,
//                     climate and the shopping list change what is drawn
//   4. honesty      — the outage scenario draws "No data", never a zero
//   5. console      — no page errors
// and writes the screenshots to design/casaray-v3/screenshots/.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const V3 = path.resolve(__dirname, '..');
const URL = 'file://' + path.join(V3, 'prototype', 'index.html');
const SHOTS = path.join(V3, 'screenshots');

const VIEWPORTS = {
  wall: { width: 1180, height: 820 },     // iPad Air 11" landscape, the wall panel
  wallPro: { width: 1366, height: 1024 }, // iPad Pro 12.9" landscape
  portrait: { width: 820, height: 1180 },
  phone: { width: 390, height: 844 },
  desktop: { width: 1600, height: 1000 },
};
const BOARDS = ['home', 'rooms', 'security', 'energy', 'climate', 'lighting', 'media', 'people', 'bills', 'health'];
const ROOMS = ['living', 'dining', 'kitchen', 'parents', 'ray', 'garage', 'guest', 'backyard'];

const { execFileSync } = require('child_process');
const fontCache = new Map();
async function fetchFont(route) {
  const url = route.request().url();
  try {
    if (!fontCache.has(url)) {
      const body = execFileSync('curl', ['-sSfL', '--max-time', '30', '-A', 'Mozilla/5.0 Chrome/140', url], { maxBuffer: 64 << 20 });
      fontCache.set(url, body);
    }
    const type = url.includes('googleapis') ? 'text/css' : 'font/woff2';
    await route.fulfill({ status: 200, body: fontCache.get(url), headers: { 'content-type': type, 'access-control-allow-origin': '*' } });
  } catch (e) {
    await route.abort();
  }
}

const results = [];
function check(name, ok, detail = '') {
  results.push({ name, ok: !!ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
}

async function newPage(browser, vp, opts = {}) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: opts.dpr || 2, colorScheme: opts.scheme || 'dark', hasTouch: !!opts.touch });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') page.errors.push(m.text()); });
  // Google Fonts go through curl, which trusts this environment's proxy CA,
  // so the screenshots use the real faces without disabling TLS checks.
  await page.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, (route) => fetchFont(route));
  await page.goto(URL + (opts.hash || ''));
  await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  await page.waitForFunction(() => window.__casaray);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  return page;
}
const h1 = (p) => p.locator('#topbar h1').innerText();
const chips = (p) => p.locator('#chips').innerText();
const overflow = (p) => p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);

async function shot(page, name, full = false) {
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(SHOTS, name + '.png'), fullPage: full });
}

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch();

  // ------------------------------------------------------ 1. navigation --
  {
    const p = await newPage(browser, VIEWPORTS.wall);
    for (const b of BOARDS) {
      await p.locator(`#rail [data-go="${b}"]`).click();
      const title = await h1(p);
      const cur = await p.locator(`#rail [data-go="${b}"]`).getAttribute('aria-current');
      check(`nav: rail opens ${b}`, cur === 'page' && title.length > 0 && p.url().endsWith('#' + b), title);
    }
    await p.locator('#rail [data-go="rooms"]').click();
    for (const r of ROOMS) {
      await p.locator(`#view [data-go="room-${r}"]`).click();
      const ok = p.url().endsWith('#room-' + r) && (await p.locator('.back-btn').count()) === 1;
      check(`nav: room drill-in ${r}`, ok, await h1(p));
      await p.locator('.back-btn').click();
    }
    check('nav: back returns to Rooms', p.url().endsWith('#rooms'));
    await p.goBack();
    check('nav: browser back works', /#room-backyard$/.test(p.url()), p.url());
    await p.locator('#rail [data-go="home"]').click();
    await p.locator('#view [data-go="energy"]').first().click();
    check('nav: More boards card opens a board', p.url().endsWith('#energy'));
    await p.goto(URL + '#room-kitchen');
    await p.waitForFunction(() => window.__casaray);
    check('nav: deep link #room-kitchen', (await h1(p)) === 'Kitchen');
    await p.goto(URL + '#no-such-board');
    await p.waitForFunction(() => window.__casaray);
    check('nav: unknown hash falls back to Home', (await h1(p)) === 'CasaRay');
    check('console: no errors on wall iPad', p.errors.length === 0, p.errors.join(' | '));
    await p.context().close();
  }
  {
    const p = await newPage(browser, VIEWPORTS.phone, { touch: true });
    check('nav: rail hidden on phone', !(await p.locator('#rail').isVisible()));
    check('nav: tab bar shown on phone', await p.locator('#tabbar').isVisible());
    await p.locator('#tabbar [data-overlay="more"]').click();
    check('nav: More sheet opens', await p.locator('.sheet').isVisible());
    await p.locator('.sheet [data-go="bills"]').click();
    check('nav: More sheet opens Bills', p.url().endsWith('#bills') && (await p.locator('.sheet').count()) === 0);
    const more = await p.locator('#tabbar [data-overlay="more"]').getAttribute('aria-current');
    check('nav: More tab marked current on a More board', more === 'page');
    await p.context().close();
  }

  // ------------------------------------------------------ 2. responsive --
  for (const [vpName, vp] of Object.entries(VIEWPORTS)) {
    const p = await newPage(browser, vp);
    const bad = [], narrow = [];
    for (const r of [...BOARDS, ...ROOMS.map((x) => 'room-' + x)]) {
      await p.evaluate((x) => window.__casaray.go(x), r);
      const o = await overflow(p);
      if (o > 0) bad.push(`${r}+${o}px`);
      // A name squeezed below 64px AND wrapping is the one-letter-per-line failure found on phone One tap.
      const thin = await p.evaluate(() => [...document.querySelectorAll('#view .name')]
        .filter((n) => { if (!n.offsetParent) return false; const r = n.getBoundingClientRect(); const lh = parseFloat(getComputedStyle(n).lineHeight) || 21; return r.width < 64 && r.height > lh * 1.6; }).map((n) => n.textContent.trim()));
      if (thin.length) narrow.push(`${r}: ${thin.join(', ')}`);
    }
    // Chinese is the wider language on some labels; check it too.
    await p.locator('[data-lang]').click();
    for (const r of BOARDS) {
      await p.evaluate((x) => window.__casaray.go(x), r);
      const o = await overflow(p);
      if (o > 0) bad.push(`zh:${r}+${o}px`);
      const thin = await p.evaluate(() => [...document.querySelectorAll('#view .name')]
        .filter((n) => { if (!n.offsetParent) return false; const r = n.getBoundingClientRect(); const lh = parseFloat(getComputedStyle(n).lineHeight) || 21; return r.width < 64 && r.height > lh * 1.6; }).map((n) => n.textContent.trim()));
      if (thin.length) narrow.push(`zh:${r}: ${thin.join(', ')}`);
    }
    check(`responsive: no horizontal scroll at ${vpName} ${vp.width}×${vp.height}`, bad.length === 0, bad.join(', '));
    check(`responsive: no card name squeezed below 64px at ${vpName}`, narrow.length === 0, narrow.join(' | '));
    await p.context().close();
  }
  {
    const p = await newPage(browser, VIEWPORTS.wall);
    const cols = await p.evaluate(() => getComputedStyle(document.querySelector('.board')).gridTemplateColumns.split(' ').length);
    check('layout: wall iPad resolves two body columns', cols === 2, `${cols} columns`);
    await p.context().close();
    const d = await newPage(browser, VIEWPORTS.desktop);
    const dc = await d.evaluate(() => getComputedStyle(document.querySelector('.board')).gridTemplateColumns.split(' ').length);
    check('layout: desktop Home resolves three columns', dc === 3, `${dc} columns`);
    await d.context().close();
    const ph = await newPage(browser, VIEWPORTS.phone);
    const pc = await ph.evaluate(() => getComputedStyle(document.querySelector('.board')).gridTemplateColumns.split(' ').length);
    check('layout: phone resolves one column', pc === 1, `${pc} column`);
    await ph.context().close();
  }

  // ----------------------------------------------------- 3. interaction --
  {
    const p = await newPage(browser, VIEWPORTS.wall);
    await p.evaluate(() => window.__casaray.go('lighting'));
    const before = await chips(p);
    await p.locator('[data-toggle="light.bedroom_bedroom"]').first().click();
    const after = await chips(p);
    check('interact: tapping a light changes the lights-on chip', before !== after, `${before.replace(/\n/g, ' ')} → ${after.replace(/\n/g, ' ')}`);
    check('interact: toast confirms demo-only action', /No device was contacted/.test(await p.locator('.toast').innerText()));
    const slider = p.locator('[data-bright="light.living_room"]');
    await slider.fill('35');
    await slider.dispatchEvent('change');
    const b = await p.evaluate(() => window.__casaray.state()['light.living_room'].a.brightness);
    check('interact: brightness bar sets brightness', b === 35, `brightness ${b}`);

    await p.locator('[data-lang]').click();
    const nav = await p.locator('#rail [data-go="security"]').innerText();
    const lang = await p.evaluate(() => document.documentElement.lang);
    check('interact: language toggle switches to Simplified Chinese', nav.includes('安防') && lang === 'zh-Hans', nav);
    const helper = await p.evaluate(() => window.__casaray.state()['input_boolean.chinese_dashboard'].s);
    check('interact: language is driven by input_boolean.chinese_dashboard', helper === 'on');
    const date = await p.locator('#clock .d').innerText();
    check('bilingual: clock date is DD/MM/YY', /^\d{2}\/\d{2}\/\d{2}$/.test(date), date);
    await p.evaluate(() => window.__casaray.go('home'));
    const home = await p.locator('#view').innerText();
    check('bilingual: Home headings in Chinese', ['需要注意', '此刻', '谁在家', '一键', '购物清单', '近期活动'].every((w) => home.includes(w)));
    check('bilingual: Chinese enumerations use 、', /、/.test(home));
    await p.locator('[data-lang]').click();

    await p.locator('[data-theme-cycle]').click();
    check('interact: theme cycles to light', (await p.evaluate(() => document.documentElement.dataset.theme)) === 'light');
    const bgLight = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await p.locator('[data-theme-cycle]').click();
    const bgDark = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
    check('interact: theme cycles to dark with a different page colour', bgLight !== bgDark, `${bgLight} / ${bgDark}`);
    await p.locator('[data-theme-cycle]').click();
    check('interact: theme cycles back to auto', (await p.evaluate(() => document.documentElement.getAttribute('data-theme'))) === null);

    await p.evaluate(() => window.__casaray.go('bills'));
    const u1 = await chips(p);
    await p.locator('[data-toggle="input_boolean.gas_bill_paid"]').click();
    const u2 = await chips(p);
    check('interact: marking a bill paid updates Unpaid and Overdue', u1 !== u2, `${u1.replace(/\n/g, ' ')} → ${u2.replace(/\n/g, ' ')}`);

    await p.evaluate(() => window.__casaray.go('climate'));
    const t0 = await p.evaluate(() => window.__casaray.state()['climate.bedroom_parents_room_ac'].a.target);
    await p.locator('[data-ac="0.5"]').click();
    const t1 = await p.evaluate(() => window.__casaray.state()['climate.bedroom_parents_room_ac'].a.target);
    check('interact: AC target steps by 0.5°', t1 - t0 === 0.5, `${t0} → ${t1}`);
    await p.locator('[data-acmode="cool"]').click();
    check('interact: AC mode segment selects Cool', (await p.locator('[data-acmode="cool"]').getAttribute('aria-pressed')) === 'true');
    await p.locator('[data-speed="fan.living_room_air_purifier"][data-v="low"]').click();
    check('interact: purifier speed segment', (await p.evaluate(() => window.__casaray.state()['fan.living_room_air_purifier'].a.speed)) === 'low');

    await p.evaluate(() => window.__casaray.go('home'));
    await p.locator('[data-shop="0"]').click();
    check('interact: shopping item ticks', (await p.locator('[data-shop="0"]').getAttribute('aria-checked')) === 'true');
    await p.locator('[data-onetap="alloff"]').click();
    check('interact: One tap "All lights off" acts on demo state', (await p.evaluate(() => window.__casaray.state()['light.living_room'].s)) === 'off');

    await p.locator('[data-overlay="demo"]').click();
    await p.locator('[data-ids]').click();
    const ids = await p.locator('.eid').first().isVisible();
    check('interact: "Show entity IDs" reveals entity captions', ids);
    const gaps = await p.locator('.eid.gap').count();
    check('mapping: gaps are labelled, not invented', gaps >= 4, `${gaps} gap captions on Home`);
    await p.locator('[data-ids]').click();
    await p.keyboard.press('Escape');
    check('interact: Escape closes the demo panel', (await p.locator('.sheet').count()) === 0);
    check('console: no errors during interaction', p.errors.length === 0, p.errors.join(' | '));
    await p.context().close();
  }

  // --------------------------------------------------------- 4. honesty --
  {
    const p = await newPage(browser, VIEWPORTS.wall);
    await p.locator('[data-overlay="demo"]').click();
    await p.locator('[data-scenario="outage"]').click();
    await p.keyboard.press('Escape');
    const c = await chips(p);
    check('honesty: outage chips say No data', (c.match(/No data/g) || []).length >= 3, c.replace(/\n/g, ' '));
    const v = await p.locator('#view').innerText();
    check('honesty: outage never claims 0 W or 0 lights', !/\b0 W\b/.test(v) && !/0 lights on/.test(v));
    check('honesty: unanswered checks are counted', /checks? could not answer/.test(v));
    check('honesty: bill with no due date is not overdue', await p.evaluate(() => {
      const s = window.__casaray.state();
      return s['input_datetime.council_rate_due'].s === 'unknown';
    }));
    await p.evaluate(() => window.__casaray.go('security'));
    const sv = await chips(p);
    check('honesty: doors with no answers do not read "All closed"', !/All closed/.test(sv), sv.replace(/\n/g, ' '));
    await p.context().close();
  }

  // ----------------------------------------------------- screenshots --
  const plan = [
    ['01_wall_home_dark_en', VIEWPORTS.wall, {}, 'home', true],
    ['02_wall_home_light_en', VIEWPORTS.wall, { scheme: 'light' }, 'home', true],
    ['03_wall_home_dark_zh', VIEWPORTS.wall, { zh: true }, 'home', true],
    ['04_wall_security_dark', VIEWPORTS.wall, {}, 'security', true],
    ['05_wall_energy_dark', VIEWPORTS.wall, {}, 'energy', true],
    ['06_wall_room_living_dark', VIEWPORTS.wall, {}, 'room-living', true],
    ['07_wall_bills_light', VIEWPORTS.wall, { scheme: 'light' }, 'bills', true],
    ['08_wall_climate_dark', VIEWPORTS.wall, {}, 'climate', true],
    ['09_wall_health_dark', VIEWPORTS.wall, {}, 'health', true],
    ['10_wall_home_outage', VIEWPORTS.wall, { scenario: 'outage' }, 'home', true],
    ['11_wall_home_entity_ids', VIEWPORTS.wall, { ids: true }, 'home', false],
    ['12_wall_demo_panel', VIEWPORTS.wall, { panel: true }, 'home', false],
    ['13_phone_home_dark', VIEWPORTS.phone, { touch: true }, 'home', true],
    ['14_phone_room_ray_light', VIEWPORTS.phone, { scheme: 'light', touch: true }, 'room-ray', true],
    ['15_phone_more_sheet', VIEWPORTS.phone, { touch: true, more: true }, 'home', false],
    ['16_desktop_home_dark', VIEWPORTS.desktop, { dpr: 1 }, 'home', true],
    ['17_portrait_rooms_dark', VIEWPORTS.portrait, {}, 'rooms', false],
    ['18_wall_home_first_screen', VIEWPORTS.wall, {}, 'home', false],
  ];
  for (const [name, vp, o, route, full] of plan) {
    const p = await newPage(browser, vp, o);
    if (o.scenario) {
      await p.locator('[data-overlay="demo"]').click();
      await p.locator(`[data-scenario="${o.scenario}"]`).click();
      await p.keyboard.press('Escape');
    }
    if (o.zh) await p.locator('[data-lang]').click();
    if (o.ids) { await p.locator('[data-overlay="demo"]').click(); await p.locator('[data-ids]').click(); await p.keyboard.press('Escape'); }
    await p.evaluate((r) => window.__casaray.go(r), route);
    if (o.panel) await p.locator('[data-overlay="demo"]').click();
    if (o.more) await p.locator('#tabbar [data-overlay="more"]').click();
    await p.waitForTimeout(250);
    // Keep the toast out of the frame.
    await p.evaluate(() => { const t = document.querySelector('#toast-slot'); if (t) t.innerHTML = ''; });
    await shot(p, name, full);
    await p.context().close();
  }

  await browser.close();
  const failed = results.filter((r) => !r.ok);
  fs.writeFileSync(path.join(SHOTS, 'test_results.json'), JSON.stringify({ passed: results.length - failed.length, failed: failed.length, results }, null, 2));
  console.log(`\n${results.length - failed.length}/${results.length} checks passed; ${plan.length} screenshots in ${path.relative(process.cwd(), SHOTS)}`);
  process.exit(failed.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
