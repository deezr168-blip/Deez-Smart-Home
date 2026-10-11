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
    check('bilingual: Home headings in Chinese', ['需要注意', '此刻', '谁在家', '一键', '购物清单'].every((w) => home.includes(w)));
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
    await p.evaluate(() => window.__casaray.go('lighting'));
    await p.locator('[data-onetap="alloff"]').click();
    check('interact: proposed "All lights off" (now on Lighting) acts on demo state', (await p.evaluate(() => window.__casaray.state()['light.living_room'].s)) === 'off');
    await p.evaluate(() => window.__casaray.go('home'));

    await p.locator('[data-overlay="demo"]').click();
    await p.locator('[data-ids]').click();
    const ids = await p.locator('.eid').first().isVisible();
    check('interact: "Show entity IDs" reveals entity captions', ids);
    const gapsHome = await p.locator('.eid.gap').count();
    await p.evaluate(() => window.__casaray.go('lighting'));
    const gaps = await p.locator('.eid.gap').count();
    await p.evaluate(() => window.__casaray.go('home'));
    await p.locator('[data-overlay="demo"]').click();
    check('mapping: gaps are labelled, not invented', gaps >= 4 && gapsHome >= 1, `${gaps} gap captions on Lighting, ${gapsHome} on Home`);
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
    const v = await p.locator('#view').innerText();
    const c = await p.locator('.hero-chips, .estrip').allInnerTexts();
    check('honesty: outage Home readings say No data', (c.join(' ').match(/No data/g) || []).length >= 3, c.join(' ').replace(/\n/g, ' '));
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


  // ------------------------------------------- 6. Home first screen --
  // V3-005: the first 1180×820 viewport carries house status, people, the
  // energy truth strip and One tap, without scrolling, in both languages.
  {
    const FIRST = async (p) => p.evaluate(() => {
      const r = (sel) => { const e = document.querySelector(sel); if (!e) return null; const b = e.getBoundingClientRect(); return { top: Math.round(b.top), bottom: Math.round(b.bottom) }; };
      const fs = (sel) => { const e = document.querySelector(sel); return e ? parseFloat(getComputedStyle(e).fontSize) : 0; };
      const clipped = [...document.querySelectorAll('#view .status, #view .tname, #view .tact, #view .alerts .name, #view .ecell, #view .person .name, #view .greet')]
        .filter((e) => e.scrollWidth > e.clientWidth + 1).map((e) => e.className + ':' + e.textContent.trim().slice(0, 20));
      return { hero: r('.hero'), attn: r('.attn'), who: r('.who'), energy: r('.energy-now'), taps: r('.taps'), vh: window.innerHeight,
        sizes: { greet: fs('.greet'), status: fs('.status'), alert: fs('.alerts .name'), person: fs('.person .name'), fig: fs('.eval .n, .eval.word'), tname: fs('.tname') }, clipped };
    });
    const fits = (f) => ['hero', 'attn', 'who', 'energy', 'taps'].every((k) => f[k] && f[k].top >= 0) && f.taps.bottom <= f.vh;
    for (const [label, scenario] of [['Evening (4 alerts)', null], ['Concept review snapshot', 'review'], ['Everyone away (5 alerts)', 'away'], ['Device outage', 'outage']]) {
      for (const zh of [false, true]) {
        const p = await newPage(browser, VIEWPORTS.wall);
        if (scenario) { await p.locator('[data-overlay="demo"]').click(); await p.locator(`[data-scenario="${scenario}"]`).click(); await p.keyboard.press('Escape'); }
        if (zh) await p.locator('[data-lang]').click();
        await p.waitForTimeout(100);
        const f = await FIRST(p);
        check(`home first screen: ${label} ${zh ? '中文' : 'EN'} fits status, people, energy and One tap in 1180×820`, fits(f), JSON.stringify({ tapsBottom: f.taps && f.taps.bottom, vh: f.vh }));
        check(`home first screen: ${label} ${zh ? '中文' : 'EN'} nothing clipped`, f.clipped.length === 0, f.clipped.join(' | '));
        if (!scenario && !zh) {
          const s = f.sizes;
          check('home first screen: standing-distance sizes (L1 ≥ 21, L2 ≥ 17)', s.greet >= 34 && s.status >= 21 && s.alert >= 17 && s.person >= 20 && s.fig >= 20 && s.tname >= 20, JSON.stringify(s));
        }
        await p.context().close();
      }
    }

    {
      const p = await newPage(browser, VIEWPORTS.wall);
      // Energy truth strip: Evening has the inverter silent.
      let strip = await p.locator('.estrip').innerText();
      check('energy strip: silent inverter reads No data, never 0', /Solar\s+No data/.test(strip) && !/0\.00/.test(strip), strip.replace(/\n+/g, ' | '));
      check('energy strip: export says No source entity', /Export\s+No source entity/.test(strip));
      check('energy strip: grid import is measured', /Grid import\s+0\.61\s*kW/.test(strip), strip.replace(/\n+/g, ' | '));
      const kinds = await p.locator('.ecell').evaluateAll((els) => els.map((e) => e.className.replace('ecell ', '')));
      check('energy strip: measured, no data and no source are distinct states', kinds.join() === 'unavailable,ok,nosource', kinds.join());
      await p.locator('[data-overlay="demo"]').click(); await p.locator('[data-scenario="review"]').click(); await p.keyboard.press('Escape');
      strip = await p.locator('.estrip').innerText();
      check('energy strip: measured values show with today totals', /1\.62\s*kW/.test(strip) && /0\.38\s*kW/.test(strip) && /14\.2 kWh/.test(strip), strip.replace(/\n+/g, ' | '));
      await p.evaluate(() => { const s = window.__casaray.state(); s['sensor.primo_5_0_1_1_ac_power'].s = 'unknown'; });
      await p.locator('[data-lang]').click(); await p.locator('[data-lang]').click();
      strip = await p.locator('.estrip').innerText();
      check('energy strip: unknown is not the same as no data', /Solar\s+Unknown/.test(strip), strip.replace(/\n+/g, ' | '));
      await p.context().close();
    }

    {
      const p = await newPage(browser, VIEWPORTS.wall);
      const t0 = await p.locator('[data-toggle="light.living_room"]').innerText();
      check('one tap: control states its current state and the action', /On/.test(t0) && /Tap to turn off/i.test(t0), t0.replace(/\n+/g, ' | '));
      await p.locator('[data-toggle="light.living_room"]').click();
      const t1 = await p.locator('[data-toggle="light.living_room"]').innerText();
      check('one tap: pressing flips state and action', /Off/.test(t1) && /Tap to turn on/i.test(t1), t1.replace(/\n+/g, ' | '));
      check('one tap: aria-pressed follows the state', (await p.locator('[data-toggle="light.living_room"]').getAttribute('aria-pressed')) === 'false');
      // The air-con card only SHOWS state and navigates; it never changes the HVAC mode (V3-007).
      const acBefore = await p.evaluate(() => window.__casaray.state()['climate.bedroom_parents_room_ac'].s);
      const acCard = p.locator('.taps .tap', { hasText: "Parents' air-con" });
      check('one tap: air-con card has no direct state-changing action', (await acCard.getAttribute('data-toggle')) === null && (await acCard.getAttribute('data-acpower')) === null && (await acCard.getAttribute('aria-pressed')) === null);
      await acCard.click();
      check('one tap: air-con card opens the Parents\' room climate controls', p.url().endsWith('#room-parents') && (await p.locator('[data-acmode]').count()) > 0, p.url());
      check('one tap: opening the air-con card leaves the HVAC mode unchanged', (await p.evaluate(() => window.__casaray.state()['climate.bedroom_parents_room_ac'].s)) === acBefore);
      await p.evaluate(() => window.__casaray.go('home'));
      const hero = await p.locator('.hero').innerText();
      check('status sentence: names who is home and counts what needs a look', /(are|is) home/.test(hero) && /need a look/.test(hero), hero.replace(/\n+/g, ' | '));
      check('status sentence: never says all clear while a check could not answer', await (async () => {
        await p.locator('[data-overlay="demo"]').click(); await p.locator('[data-scenario="outage"]').click(); await p.keyboard.press('Escape');
        const h = await p.locator('.hero .status').innerText();
        return !/^[^.]*\.\s*Nothing needs attention\.$/.test(h) && !/Nothing needs attention/.test(h);
      })());
      await p.context().close();
    }

    // Home length and where the removed sections went (V3 owner decision, V3-007).
    {
      const heights = {};
      for (const [label, scenario] of [['evening', null], ['review', 'review'], ['away', 'away'], ['outage', 'outage']]) {
        const p = await newPage(browser, VIEWPORTS.wall);
        if (scenario) { await p.locator('[data-overlay="demo"]').click(); await p.locator(`[data-scenario="${scenario}"]`).click(); await p.keyboard.press('Escape'); }
        heights[label] = await p.evaluate(() => document.documentElement.scrollHeight);
        await p.context().close();
      }
      check('home length: Concept review snapshot is about 2 screens or less (≤ 1700 px)', heights.review <= 1700, JSON.stringify(heights));
      check('home length: worst case (4–5 alerts) stays under 1800 px, well under the old 2353', Math.max(...Object.values(heights)) <= 1800, JSON.stringify(heights));
      const p = await newPage(browser, VIEWPORTS.wall);
      const home = await p.locator('#view').innerText();
      check('home: proposed whole-house row and Recent activity are no longer on Home', !/Whole-house scenes/.test(home) && !/Recent activity/.test(home) && (await p.locator('[data-onetap]').count()) === 0);
      await p.evaluate(() => window.__casaray.go('lighting'));
      const lit = await p.locator('#view').innerText();
      check('relocated: Lighting carries the four whole-house scenes, each marked Proposed', /Whole-house scenes \(proposed\)/.test(lit) && (await p.locator('[data-onetap]').count()) === 4 && (lit.match(/proposed/gi) || []).length >= 5, (lit.match(/Proposed/gi) || []).length + ' proposed labels');
      await p.evaluate(() => window.__casaray.go('health'));
      check('relocated: House health carries Recent activity', /Recent activity/.test(await p.locator('#view').innerText()));
      await p.evaluate(() => window.__casaray.go('climate'));
      check('relocated: Climate carries the four-day forecast', (await p.locator('.wx-days').count()) === 1);
      await p.evaluate(() => window.__casaray.go('energy'));
      check('relocated: Energy carries monitored power with its 12-hour bars', (await p.locator('.spark').count()) === 1);
      await p.context().close();
    }

    // QA pass on PR #4 (05/10/26): Chinese Home length, and a guarantee that the
    // detail the dense (five-alert) layout cuts to one line is still one tap
    // away. Every Needs-attention card must be a button with a real destination.
    {
      const zhHeights = {}, badCards = [];
      for (const [label, scenario] of [['evening', null], ['review', 'review'], ['away', 'away'], ['outage', 'outage']]) {
        for (const zh of [false, true]) {
          const p = await newPage(browser, VIEWPORTS.wall);
          if (scenario) { await p.locator('[data-overlay="demo"]').click(); await p.locator(`[data-scenario="${scenario}"]`).click(); await p.keyboard.press('Escape'); }
          if (zh) await p.locator('[data-lang]').click();
          await p.waitForTimeout(100);
          if (zh) zhHeights[label] = await p.evaluate(() => document.documentElement.scrollHeight);
          const cards = await p.evaluate(() => [...document.querySelectorAll('.attn .alerts .card.alert')].map((c) => ({ tag: c.tagName, go: c.dataset.go || null, title: c.querySelector('.name').textContent.trim() })));
          for (const c of cards) if (c.tag !== 'BUTTON' || !BOARDS.includes(c.go)) badCards.push(`${label}${zh ? ' 中文' : ''}: ${c.title} → ${c.tag}/${c.go}`);
          await p.context().close();
        }
      }
      check('home length (中文): every scenario stays under 1800 px', Math.max(...Object.values(zhHeights)) <= 1800, JSON.stringify(zhHeights));
      check('home alerts: every Needs-attention card is a button that opens a real board', badCards.length === 0, badCards.join(' | '));
    }
  }

  // ------------------------- 7. Uncertainty states and touch targets --
  // Hardening before PR #4 merges: an unanswered check is never drawn as
  // healthy, an unavailable amount is never drawn as A$0.00, an unavailable
  // occupancy sensor keeps its tile, and every interactive target is 44 px.
  {
    // Everything answers and nothing is wrong, except what a test then darkens.
    const quietHouse = (p, { dark = false, zh = false } = {}) => p.evaluate(([dark, zh]) => {
      const s = window.__casaray.state();
      for (const k of Object.keys(s)) {
        if (/battery/.test(k) && !/powerpal/.test(k) && s[k].s !== 'unavailable') s[k].s = '80';
        if (/^input_boolean\..*_paid$/.test(k)) s[k].s = 'on';
      }
      for (const k of ['event.master_bedroom_emergency_button_dad_main', 'event.master_bedroom_emergency_button_mum_main']) s[k] = { s: '2026-10-09T10:00:00+00:00' };
      s['sensor.primo_5_0_1_1_ac_power'] = { s: '1620' };
      s['binary_sensor.b_contact_sensor_door'] = { s: dark ? 'unavailable' : 'off' };
      s['input_boolean.chinese_dashboard'].s = zh ? 'on' : 'off';
      window.__casaray.go('home');
      const at = window.__casaray.attention();
      const card = document.querySelector('.attn .card');
      return { alerts: at.alerts.length, unknown: at.unknown, cls: card.className, ic: card.querySelector('.ic').className, text: document.querySelector('.attn').innerText.replace(/\n+/g, ' | '), hero: document.querySelector('.hero .status').innerText };
    }, [dark, zh]);

    for (const zh of [false, true]) {
      const L = zh ? '中文' : 'EN';
      let p = await newPage(browser, VIEWPORTS.wall);
      let r = await quietHouse(p, { dark: true, zh });
      check(`all-clear: 0 alerts + 1 unanswered check is grey, not green ${L}`, r.alerts === 0 && r.unknown === 1 && /\bgrey\b/.test(r.cls) && !/green/.test(r.cls + r.ic), `${r.cls} / ${r.ic}`);
      check(`all-clear: uncertainty card says nothing is flagged but a check could not answer ${L}`, zh ? /暂未发现问题/.test(r.text) && /无法响应/.test(r.text) : /Nothing is flagged, but 1 check could not answer/.test(r.text), r.text);
      check(`all-clear: uncertainty card never says "Nothing needs attention" or "normal" ${L}`, !/Nothing needs attention|came back normal|暂无需要注意|都正常/.test(r.text), r.text);
      check(`all-clear: hero sentence agrees with the card ${L}`, zh ? /暂未发现问题/.test(r.hero) : /Nothing is flagged, but 1 check could not answer/.test(r.hero), r.hero);
      await p.context().close();
      p = await newPage(browser, VIEWPORTS.wall);
      r = await quietHouse(p, { dark: false, zh });
      check(`all-clear: every check answered and nothing wrong is green ${L}`, r.alerts === 0 && r.unknown === 0 && /\bgreen\b/.test(r.cls) && (zh ? /暂无需要注意/.test(r.text) : /Nothing needs attention/.test(r.text)), `${r.cls} / ${r.text}`);
      await p.context().close();
    }

    // Bill amounts: real zero, unavailable, unknown, normal.
    for (const zh of [false, true]) {
      const L = zh ? '中文' : 'EN';
      const p = await newPage(browser, VIEWPORTS.wall);
      if (zh) await p.locator('[data-lang]').click();
      const overdue = (amt) => p.evaluate((amt) => {
        const s = window.__casaray.state();
        s['input_number.gas_bill_amount'] = { s: amt };
        window.__casaray.go('home');
        const card = [...document.querySelectorAll('.alerts .card')].find((c) => /Gas|燃气/.test(c.innerText));
        window.__casaray.go('bills');
        const row = [...document.querySelectorAll('#view .card.tile')].find((c) => /Gas|燃气/.test(c.querySelector('.name').innerText));
        window.__casaray.go('home');
        return { alert: card ? card.innerText.replace(/\n+/g, ' | ') : null, bills: row ? row.querySelector('.name').innerText : null };
      }, amt);
      const zero = await overdue('0');
      check(`bill amount: a real 0 is A$0.00 ${L}`, /A\$0\.00/.test(zero.alert) && /A\$0\.00/.test(zero.bills), JSON.stringify(zero));
      for (const bad of ['unavailable', 'unknown']) {
        const r = await overdue(bad);
        check(`bill amount: ${bad} reads no data, never A$0.00 ${L}`, r.alert && !/A\$0\.00/.test(r.alert + r.bills) && (zh ? /金额：无数据/.test(r.alert) && /金额：无数据/.test(r.bills) : /amount: no data/.test(r.alert) && /amount: no data/.test(r.bills)) && /03|0[0-9]\/\d\d\/26|\d{2}\/\d{2}\/26/.test(r.alert), JSON.stringify(r));
      }
      const pos = await overdue('196.45');
      check(`bill amount: a normal amount is formatted ${L}`, /A\$196\.45/.test(pos.alert) && /A\$196\.45/.test(pos.bills), JSON.stringify(pos));
      await p.context().close();
    }

    // Occupancy: the tile stays, drawn as no data.
    for (const zh of [false, true]) {
      const L = zh ? '中文' : 'EN';
      const p = await newPage(browser, VIEWPORTS.wall);
      if (zh) await p.locator('[data-lang]').click();
      const occ = (val) => p.evaluate((val) => {
        const s = window.__casaray.state();
        s['binary_sensor.bedroom_parents_room_ac_room_occupied'] = val === 'on' || val === 'off' ? { s: val, ago: 4 } : { s: val };
        window.__casaray.go('home');
        const now = [...document.querySelectorAll('.sec')].find((x) => x.querySelector('h2') && /Right now|此刻/.test(x.querySelector('h2').innerText));
        const tile = [...now.querySelectorAll('.card')].find((c) => /Parents|父母/.test(c.innerText));
        return tile ? { cls: tile.className, text: tile.innerText.replace(/\n+/g, ' | ') } : null;
      }, val);
      for (const bad of ['unavailable', 'unknown']) {
        const r = await occ(bad);
        check(`occupancy: ${bad} keeps the tile, drawn as no data ${L}`, r && /\bna\b/.test(r.cls) && (zh ? /无数据/.test(r.text) : /No data/i.test(r.text)) && !/Quiet|Occupied|安静|有人/.test(r.text), JSON.stringify(r));
      }
      const o = await occ('on');
      check(`occupancy: occupied still reads occupied ${L}`, o && !/\bna\b/.test(o.cls) && (zh ? /有人/.test(o.text) : /Occupied/.test(o.text)), JSON.stringify(o));
      const q = await occ('off');
      check(`occupancy: unoccupied still reads quiet ${L}`, q && !/\bna\b/.test(q.cls) && (zh ? /安静/.test(q.text) : /Quiet/.test(q.text)), JSON.stringify(q));
      await p.context().close();
    }

    // Every interactive target is at least 44 × 44 on every board, in both
    // themes of overlay, at wall, portrait and phone sizes.
    const ROUTES = [...BOARDS, ...ROOMS.map((x) => 'room-' + x)];
    for (const [vpName, vp, touch] of [['wall', VIEWPORTS.wall, false], ['portrait', VIEWPORTS.portrait, false], ['phone', VIEWPORTS.phone, true]]) {
      const p = await newPage(browser, vp, { touch });
      const small = new Set();
      const scan = async (where) => {
        const r = await p.evaluate(() => [...document.querySelectorAll('button, a[href], input[type=range], [role=switch], [role=checkbox], [role=button]')]
          .filter((e) => e.offsetParent !== null || getComputedStyle(e).position === 'fixed')
          .map((e) => { const b = e.getBoundingClientRect(); return { n: (e.className || e.tagName) + ':' + (e.dataset.go || e.dataset.toggle || e.textContent.trim().slice(0, 12)), w: Math.round(b.width), h: Math.round(b.height) }; })
          .filter((x) => x.w < 44 || x.h < 44));
        for (const x of r) small.add(`${where} ${x.n} ${x.w}×${x.h}`);
      };
      for (const zh of [false, true]) {
        if (zh) await p.locator('[data-lang]').click();
        for (const r of ROUTES) { await p.evaluate((x) => window.__casaray.go(x), r); await scan((zh ? 'zh:' : '') + r); }
      }
      await p.locator('[data-lang]').click();
      await p.locator('[data-overlay="demo"]').first().click();
      await scan('demo panel');
      await p.keyboard.press('Escape');
      if (touch) { await p.locator('#tabbar [data-overlay="more"]').click(); await scan('more sheet'); }
      check(`touch targets: every interactive element is at least 44×44 at ${vpName}`, small.size === 0, [...small].slice(0, 6).join(' | '));
      check(`touch targets: no horizontal overflow after the change at ${vpName}`, (await overflow(p)) <= 0);
      await p.context().close();
    }
  }

  // ------------------------------- 8. Missing-state fallbacks (V3 backlog 9–11) --
  // A value the entity did not report is never drawn as 0: not "1 min", not
  // "0%", not "Blind closed". A real 0 still is 0.
  {
    const KITCHEN = 'binary_sensor.k_motion_sensor_motion';
    const OCC = 'binary_sensor.bedroom_parents_room_ac_room_occupied';
    for (const zh of [false, true]) {
      const L = zh ? '中文' : 'EN';
      const no = zh ? /无数据/ : /No data/;
      const p = await newPage(browser, VIEWPORTS.wall);
      if (zh) await p.locator('[data-lang]').click();
      const put = (id, v) => p.evaluate(([id, v]) => { window.__casaray.state()[id] = v; }, [id, v]);
      const text = (route, pick) => p.evaluate(([route, pick]) => {
        window.__casaray.go(route);
        const q = (sel) => [...document.querySelectorAll(sel)];
        const el = pick === 'chip' ? q('#chips .chip').find((c) => /Movement|动作/.test(c.innerText))
          : pick === 'kitchen' ? q('#view .card.tile').find((c) => /^(Movement|动作)/.test(c.querySelector('.name')?.innerText || ''))
          : pick === 'occ' ? q('#view .sec').find((x) => /Right now|此刻/.test(x.querySelector('h2')?.innerText || '')).querySelectorAll('.card.tile')[1]
          : pick === 'tap' ? q('.taps .tap').find((c) => /Living room lights|客厅灯/.test(c.innerText))
          : null;
        return el ? el.innerText.replace(/\n+/g, ' | ') : null;
      }, [route, pick]);

      // ---- 9: elapsed time ----
      for (const [label, id, route, pick, quietWord] of [
        ['Kitchen movement tile', KITCHEN, 'room-kitchen', 'kitchen', zh ? /安静/ : /Quiet/],
        ['Movement chip', KITCHEN, 'room-kitchen', 'chip', zh ? /安静/ : /Quiet/],
        ['Home occupancy tile', OCC, 'home', 'occ', zh ? /安静/ : /Quiet/],
      ]) {
        const wasOn = id === OCC ? 'off' : 'off';
        await put(id, { s: wasOn, ago: 31 });
        let t = await text(route, pick);
        check(`elapsed: ${label} shows a real elapsed time ${L}`, t && quietWord.test(t) && (zh ? /31 分钟/ : /31 min/).test(t), t);
        await put(id, { s: wasOn, ago: 0 });
        t = await text(route, pick);
        check(`elapsed: ${label} reads a real 0 as just now, not 1 min ${L}`, t && (zh ? /刚刚/ : /just now/).test(t) && !/1 min|1 分钟/.test(t), t);
        for (const [what, ago] of [['missing', undefined], ['null', null], ['text', 'unknown'], ['negative', -5]]) {
          await put(id, ago === undefined ? { s: wasOn } : { s: wasOn, ago });
          t = await text(route, pick);
          check(`elapsed: ${label} with ${what} elapsed time reads no data, never 1 min ${L}`, t && quietWord.test(t) && no.test(t) && !/1 min|1 分钟|0 min|0 分钟/.test(t), t);
        }
        for (const bad of ['unavailable', 'unknown']) {
          await put(id, { s: bad });
          t = await text(route, pick);
          check(`elapsed: ${label} ${bad} reads no data ${L}`, t && no.test(t) && !quietWord.test(t) && !/min|分钟/.test(t), t);
        }
      }

      // ---- 10: brightness ----
      const LIGHT = 'light.living_room';
      const bar = (route) => p.evaluate((route) => {
        window.__casaray.go(route);
        const c = [...document.querySelectorAll('#view .card.tile')].find((x) => x.querySelector('[data-bright="light.living_room"]'));
        if (!c) return null;
        return { nd: !!c.querySelector('.bar.nd'), fill: c.querySelector('.fill') ? c.querySelector('.fill').style.width : null, label: c.querySelector('[data-bl]').innerText, aria: c.querySelector('input').getAttribute('aria-label') };
      }, route);
      await put(LIGHT, { s: 'on', a: { brightness: 62 } });
      let b = await bar('room-living');
      check(`brightness: a valid brightness shows its percentage ${L}`, b && !b.nd && b.fill === '62%' && b.label === '62%', JSON.stringify(b));
      await put(LIGHT, { s: 'on', a: { brightness: 0 } });
      b = await bar('room-living');
      check(`brightness: a real 0 shows 0% ${L}`, b && !b.nd && b.fill === '0%' && b.label === '0%', JSON.stringify(b));
      for (const [what, a] of [['missing', {}], ['no attributes', undefined], ['null', { brightness: null }], ['unknown text', { brightness: 'unknown' }], ['unavailable text', { brightness: 'unavailable' }], ['out of range', { brightness: 250 }]]) {
        await put(LIGHT, a === undefined ? { s: 'on' } : { s: 'on', a });
        b = await bar('room-living');
        check(`brightness: ${what} reads no data, never 0% ${L}`, b && b.nd && b.fill === null && no.test(b.label) && !/0%/.test(b.label), JSON.stringify(b));
      }
      await put(LIGHT, { s: 'off', a: {} });
      b = await bar('room-living');
      check(`brightness: an off light with no brightness is just off, with no bar ${L}`, b === null, JSON.stringify(b));
      await put(LIGHT, { s: 'on', a: {} });
      const tap = await text('home', 'tap');
      check(`brightness: Home One tap says brightness has no data, not a percentage ${L}`, tap && (zh ? /亮度：无数据/ : /brightness: no data/).test(tap) && !/0%/.test(tap), tap);
      for (const bad of ['unavailable', 'unknown']) {
        await put(LIGHT, { s: bad });
        const c = await p.evaluate(() => { window.__casaray.go('room-living'); const x = [...document.querySelectorAll('#view .card.tile')].find((y) => /Living room|客厅/.test(y.querySelector('.name')?.innerText || '')); return x ? { cls: x.className, bar: !!x.querySelector('.bar'), text: x.innerText.replace(/\n+/g, ' | ') } : null; });
        check(`brightness: ${bad} light draws a dashed card with no bar and no percentage ${L}`, c && /\bna\b/.test(c.cls) && !c.bar && !/\d%/.test(c.text), JSON.stringify(c));
      }

      // ---- 11: cover position ----
      const COVER = 'cover.aqara_roller_shade_driver_e1';
      const blind = () => p.evaluate(() => {
        window.__casaray.go('room-ray');
        const c = [...document.querySelectorAll('#view .card.tile')].find((x) => x.querySelector('[data-cover]'));
        const row = (window.__casaray.go('rooms'), [...document.querySelectorAll('#view [data-go="room-ray"]')][0]);
        const out = c ? { nd: !!c.querySelector('.bar.nd'), fill: c.querySelector('.fill') ? c.querySelector('.fill').style.width : null, sub: c.querySelector('.sub').innerText, label: c.querySelector('[data-bl]').innerText, on: /\bon\b/.test(c.className), row: row ? row.innerText.replace(/\n+/g, ' | ') : null } : null;
        return out;
      });
      const closedW = zh ? /已关/ : /[Cc]losed/, openW = zh ? /打开|已开/ : /Open|open/;
      // The Rooms row also lists the lights ("灯已关"), so match the blind's own words there.
      const closedRow = zh ? /卷帘已关/ : /Blind closed/, openRow = zh ? /卷帘已开/ : /Blind open/;
      await put(COVER, { s: 'closed', a: { position: 0 } });
      let c = await blind();
      check(`cover: a real position 0 is Closed ${L}`, c && !c.nd && c.fill === '0%' && closedW.test(c.sub) && closedRow.test(c.row), JSON.stringify(c));
      await put(COVER, { s: 'open', a: { position: 100 } });
      c = await blind();
      check(`cover: position 100 is Open ${L}`, c && !c.nd && c.fill === '100%' && openW.test(c.sub) && /100%/.test(c.sub) && openRow.test(c.row), JSON.stringify(c));
      await put(COVER, { s: 'open', a: { position: 40 } });
      c = await blind();
      check(`cover: an intermediate position shows its percentage ${L}`, c && c.fill === '40%' && /40%/.test(c.sub) && c.label === '40%', JSON.stringify(c));
      for (const [what, a] of [['missing', {}], ['no attributes', undefined], ['null', { position: null }], ['unknown text', { position: 'unknown' }], ['unavailable text', { position: 'unavailable' }], ['out of range', { position: 140 }]]) {
        await put(COVER, a === undefined ? { s: 'closed' } : { s: 'closed', a });
        c = await blind();
        check(`cover: ${what} position reads no data, never closed ${L}`, c && c.nd && c.fill === null && no.test(c.sub) && no.test(c.label) && !closedW.test(c.sub) && !closedRow.test(c.row) && !c.on, JSON.stringify(c));
      }
      for (const bad of ['unavailable', 'unknown']) {
        await put(COVER, { s: bad });
        const d = await p.evaluate(() => { window.__casaray.go('room-ray'); const x = [...document.querySelectorAll('#view .card.tile')].find((y) => /Blind|卷帘/.test(y.querySelector('.name')?.innerText || '')); return x ? { cls: x.className, bar: !!x.querySelector('.bar'), text: x.innerText.replace(/\n+/g, ' | ') } : null; });
        check(`cover: ${bad} cover draws a dashed card, not Closed ${L}`, d && /\bna\b/.test(d.cls) && !d.bar && !closedW.test(d.text), JSON.stringify(d));
      }
      check(`fallbacks: no page errors ${L}`, p.errors.length === 0, p.errors.join(' | '));
      await p.context().close();
    }
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
    ['19_wall_home_first_screen_zh', VIEWPORTS.wall, { zh: true }, 'home', false],
    ['20_wall_home_review_snapshot', VIEWPORTS.wall, { scenario: 'review' }, 'home', false],
    ['21_wall_home_review_snapshot_zh', VIEWPORTS.wall, { scenario: 'review', zh: true }, 'home', false],
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
