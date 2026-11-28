#!/usr/bin/env node
/* Task Control Center V5 — browser tests.  DEVELOPMENT ONLY.

     node docs/project-tasks/control-center/test_control_center.cjs

   Drives index.html in headless Chromium (Playwright). GitHub is never
   contacted: every api.github.com and raw.githubusercontent.com request is
   answered by the fixture below, so a test can change "GitHub" between two
   refreshes. The last group runs the page's handoff through the real
   tasks.py on a throwaway copy of the canonical register, to prove the
   batch it prints is one the tool accepts. Nothing is written to the
   repository. Exit 0 only if every check passes. */
'use strict';
const {chromium} = require('playwright');
const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process');

const HERE = __dirname, ROOT = path.resolve(HERE, '..', '..', '..');
const SRC = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8');
const TODAY = '2026-11-16';
// Section 11 runs the real tool on a copy of the real register. tasks.py refuses a row dated before the row above it (E15),
// so the date it stamps must not be earlier than the register's own newest row. Everything else keeps the fixed TODAY.
const NEWEST_ROW = (fs.readFileSync(path.join(ROOT, 'docs', 'project-tasks', 'DECISION_HISTORY.md'), 'utf8').match(/^\| DEC-\d+ \| (\d{4}-\d{2}-\d{2}) /gm) || [])
  .map(m => m.match(/\d{4}-\d{2}-\d{2}/)[0]).sort().pop() || TODAY;
const REAL_TODAY = NEWEST_ROW > TODAY ? NEWEST_ROW : TODAY;
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'tcc-test-'));
let failures = 0, passes = 0; const PAGE_ERRORS = [];
function check(name, ok, detail) { if (ok) { passes++; console.log('  PASS ' + name); } else { failures++; console.log('  FAIL ' + name + (detail ? '\n       ' + String(detail).slice(0, 600).replace(/\n/g, '\n       ') : '')); } }

/* ---------------------------------------------------------------- fixture */
const TASK_COLS = ['ID', 'Project', 'P', 'Status', 'Gate', 'Task', 'Home', 'Evidence', 'Decision', 'Next action', 'Updated'];
const HIST_COLS = ['ID', 'Date', 'Task', 'Event', 'From', 'To', 'Scope', 'Context', 'Basis', 'Via', 'By'];
const LINK_COLS = ['From', 'Relation', 'To', 'Source', 'External status', 'Checked'];
const table = (cols, rows) => ['| ' + cols.join(' | ') + ' |', '|' + cols.map(() => '---').join('|') + '|', ...rows.map(r => '| ' + cols.map(c => r[c] ?? '—').join(' | ') + ' |')].join('\n');
const FRESH = 'VERIFIED · fixture · 2026-11-14 · claude', OLD = 'REPORTED · fixture · 2026-10-01';
function T(id, P, Status, Gate, Task, extra = {}) { return Object.assign({ID: id, Project: 'casaray-v3', P, Status, Gate, Task, Home: 'register', Evidence: FRESH, Decision: '—', 'Next action': 'Do the next thing for ' + id, Updated: '2026-11-10'}, extra); }
function baseTasks() {
  return [
    T('TASK-001', 'P0', 'AWAITING_DECISION', 'none', 'Eligible ungated task with fresh evidence'),
    T('TASK-002', 'P1', 'AWAITING_DECISION', 'protected', 'Protected task awaiting a decision'),
    T('TASK-003', 'P1', 'PAUSED', 'none', 'Task the owner paused'),
    T('TASK-004', 'P2', 'AWAITING_DECISION', 'none', 'Task paused in Issue 7 but not in the register'),
    T('TASK-005', 'P2', 'AWAITING_DECISION', 'none', 'Task with old evidence', {Evidence: OLD}),
    T('TASK-006', 'P3', 'AWAITING_DECISION', 'none', 'Task that depends on an open task'),
    T('TASK-007', 'P3', 'OPEN', 'none', 'Open prerequisite'),
    T('TASK-008', 'P0', 'DONE', 'none', 'Finished task'),
    T('TASK-009', 'P1', 'DENIED', 'none', 'Denied task'),
    T('TASK-010', 'P2', 'IN_PROGRESS', 'none', 'Task in progress', {Home: 'pr:16'}),
    T('TASK-011', 'P3', 'APPROVED', 'none', 'Approved task'),
    T('TASK-012', 'P2', 'BLOCKED', 'none', 'Blocked task'),
    T('TASK-013', 'P1', 'OPEN', 'none', 'Open task with no decision pending', {Home: 'pr:8'}),
    T('TASK-014', 'P0', 'AWAITING_DECISION', 'safety', 'Safety-gated siren test'),
  ];
}
function baseLinks() {
  return [
    {From: 'CR-T01', Relation: 'alias-of', To: 'TASK-003', Source: 'issue:7', 'External status': 'PAUSED', Checked: '2026-11-15'},
    {From: 'CR-T02', Relation: 'alias-of', To: 'TASK-004', Source: 'issue:7', 'External status': 'PAUSED', Checked: '2026-11-15'},
    {From: 'V4:TASK-001X', Relation: 'duplicate-of', To: 'TASK-001', Source: 'control-center:v4', 'External status': '—', Checked: '2026-11-15'},
    {From: 'V4:V3-DEPLOY', Relation: 'duplicate-of', To: 'TASK-013', Source: 'control-center:v4', 'External status': '—', Checked: '2026-11-15'},
    {From: 'TASK-006', Relation: 'depends-on', To: 'TASK-007', Source: 'register', 'External status': '—', Checked: '2026-11-15'},
    {From: 'TASK-010', Relation: 'overlaps', To: 'TASK-012', Source: 'pr:10 and pr:13', 'External status': '—', Checked: '2026-11-15'},
  ];
}
function baseEvents() {
  const ev = []; let n = 0;
  for (const t of baseTasks()) ev.push({ID: 'DEC-' + String(++n).padStart(3, '0'), Date: '2026-11-01', Task: t.ID, Event: 'ADDED', From: '—', To: t.Status, Scope: '—', Context: '—', Basis: '—', Via: '—', By: 'claude'});
  ev.push({ID: 'DEC-' + String(++n).padStart(3, '0'), Date: '2026-11-02', Task: 'TASK-003', Event: 'PAUSED', From: 'AWAITING_DECISION', To: 'PAUSED', Scope: '—', Context: 'Keep the branch for resuming', Basis: 'owner said pause', Via: 'chat', By: 'owner'});
  return ev;
}
function md({tasks = baseTasks(), links = baseLinks(), events = baseEvents(), withLinks = true} = {}) {
  const register = '# Task register\n\n## Tasks\n\n' + table(TASK_COLS, tasks) + '\n' + (withLinks ? '\n## Links\n\n' + table(LINK_COLS, links) + '\n' : '');
  const history = '# Decision history\n\n' + table(HIST_COLS, events) + '\n';
  return {register, history};
}
const ISSUE = (rows) => ({updated_at: '2026-10-12T03:44:10Z', body: '## Owner decisions\n\n| ID | Task | Owner decision | Current implementation state |\n|---|---|---|---|\n' + rows.map(([id, s]) => `| ${id} | Fixture task | **${s}** (previously APPROVED; approval history retained) | Resume: inspect \`x.py\` first |`).join('\n') + '\n'});
const PR = (n, state, sha = 'f'.repeat(40)) => ({number: n, state, title: 'Fixture PR ' + n, head: {sha}});

/* A copy of the page with this snapshot built in, as build.py would embed it. */
let pageN = 0;
function pageWith(snap) {
  const json = JSON.stringify(snap).replace(/<\//g, '<\\/');
  const html = SRC.replace(/(<script type="application\/json" id="snapshot">)[\s\S]*?(<\/script>)/, (m, a, b) => a + json + b);
  const f = path.join(TMP, `tcc-${++pageN}.html`); fs.writeFileSync(f, html); return 'file://' + f;
}

/* ---------------------------------------------------------------- harness */
async function open(browser, {snap, gh, legacy, selections, viewport} = {}) {
  const ctx = await browser.newContext({viewport: viewport || {width: 1280, height: 900}});
  const page = await ctx.newPage();
  const log = {requests: [], dialogs: []};
  const state = Object.assign({fail: false, sha: 'a'.repeat(40)}, gh || {});
  const cors = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'};
  await page.route(/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\/.*/, route => {
    const url = route.request().url(); log.requests.push(url);
    if (state.fail) return route.fulfill({status: 503, headers: cors, body: '{}'});
    if (url.includes('/commits/')) return route.fulfill({status: 200, headers: cors, body: JSON.stringify({sha: state.sha})});
    if (url.endsWith('/TASK_REGISTER.md')) return route.fulfill({status: 200, headers: cors, body: state.register});
    if (url.endsWith('/DECISION_HISTORY.md')) return route.fulfill({status: 200, headers: cors, body: state.history});
    if (url.endsWith('/issues/7')) return state.issue ? route.fulfill({status: 200, headers: cors, body: JSON.stringify(state.issue)}) : route.fulfill({status: 404, headers: cors, body: '{}'});
    if (url.includes('/pulls')) return state.prs ? route.fulfill({status: 200, headers: cors, body: JSON.stringify(state.prs)}) : route.fulfill({status: 404, headers: cors, body: '{}'});
    return route.fulfill({status: 404, headers: cors, body: '{}'});
  });
  page.on('dialog', d => { log.dialogs.push(d.message()); (state.dialog === 'dismiss' ? d.dismiss() : d.accept()); });
  page.on('pageerror', e => { log.requests.push('PAGEERROR ' + e.message); PAGE_ERRORS.push(e.message); });
  await page.addInitScript(([today, legacy, selections]) => {
    window.__TCC_NOW = today;
    if (!sessionStorage.getItem('seeded')) {
      sessionStorage.setItem('seeded', '1');
      if (legacy) localStorage.setItem('casaray-decisions-v2', JSON.stringify(legacy));
      if (selections) localStorage.setItem('casaray-tcc-v5', JSON.stringify({selections}));
    }
  }, [TODAY, legacy || null, selections || null]);
  await page.goto(pageWith(snap || Object.assign(md(), {sha: 'b'.repeat(40), ref: 'fixture', built_at: '2026-11-14'})));
  await settle(page);
  return {page, ctx, log, state};
}
async function settle(page) { await page.waitForFunction(() => !document.getElementById('refresh').disabled && !/Reading|Loading/.test(document.getElementById('sync').textContent)); }
async function refresh(page) { await page.click('#refresh'); await settle(page); }
const listIds = page => page.$$eval('#tasks [data-task]', b => b.map(x => x.dataset.task));
async function allPages(page) { const out = []; while (true) { out.push(...await listIds(page)); if (await page.isDisabled('#nextPage')) break; await page.click('#nextPage'); } return out; }
async function openTask(page, id) {
  await page.evaluate(id => { const v = window.__TCC; }, id);
  await page.fill('#search', id); await page.click(`#tasks [data-task="${id}"]`); await page.fill('#search', '');
}
const btn = (page, v) => page.$(`#detail [data-decision="${v}"]`);
const conflicts = page => page.$$eval('#conflictList .conflict', els => els.map(e => ({sev: e.dataset.sev, text: e.textContent})));

/* ---------------------------------------------------------------- tests */
async function main() {
  const browser = await chromium.launch();
  try {
    const fx = md();
    const ghBase = () => ({register: fx.register, history: fx.history, issue: ISSUE([['CR-T01', 'PAUSED'], ['CR-T02', 'PAUSED']]), prs: [PR(8, 'open'), PR(16, 'open'), PR(99, 'open'), PR(4, 'closed')]});

    console.log('1. Duplicate task ID detection');
    {
      const tasks = baseTasks(); tasks.push(T('TASK-001', 'P3', 'OPEN', 'none', 'A second record that reused TASK-001'));
      const d = md({tasks});
      const {page, ctx} = await open(browser, {gh: Object.assign(ghBase(), d)});
      await page.click('[data-tab="conflicts"]');
      const c = await conflicts(page);
      check('1a a reused ID is listed as an error in Conflicts', c.some(x => x.sev === 'error' && /Duplicate task ID/.test(x.text) && /TASK-001 appears 2 times/.test(x.text)), JSON.stringify(c));
      await page.click('[data-tab="queue"]'); await openTask(page, 'TASK-001');
      check('1b approving the duplicated ID is disabled', await (await btn(page, 'approve')).isDisabled());
      check('1c deny and pause are disabled too until one record remains', await (await btn(page, 'deny')).isDisabled() && await (await btn(page, 'pause')).isDisabled());
      check('1d the stat card counts the error', (await page.textContent('#stats')).includes('Conflicts1') || Number((await page.$$eval('.stat.red strong', s => s.map(x => x.textContent)))[0]) >= 1);
      await ctx.close();
    }

    console.log('2. Conflicting task detection');
    {
      const tasks = baseTasks(); tasks.push(T('TASK-015', 'P3', 'OPEN', 'none', 'Task paused in Issue 7 but not in the register!'));
      const links = baseLinks(); links.push(Object.assign({}, links[0], {From: 'CR-T01', To: 'TASK-003'}));   // a duplicated link row
      const gh = Object.assign(ghBase(), md({tasks, links}), {issue: ISSUE([['CR-T01', 'RESUMED'], ['CR-T02', 'PAUSED'], ['CR-T03', 'PAUSED']])});
      const {page, ctx} = await open(browser, {gh});
      await page.click('[data-tab="conflicts"]');
      const c = await conflicts(page), has = (sev, re) => c.some(x => x.sev === sev && re.test(x.text));
      check('2a a pause in Issue 7 that the register does not record is an error', has('error', /Pause not recorded in the register.*CR-T02.*TASK-004 is AWAITING_DECISION/), JSON.stringify(c));
      check('2b Issue 7 changing since the link was checked is flagged, not applied', has('warn', /Issue #7 now says CR-T01 is RESUMED.*Not applied automatically/));
      check('2c an Issue 7 ID with no canonical task is an error', has('error', /CR-T03 \(PAUSED\) has no canonical task/));
      check('2d an open PR no task covers is flagged', has('warn', /PR #99 .*not in the register/) && !has('warn', /PR #8 /) && !has('warn', /PR #16 /) && !has('warn', /PR #4 /));
      check('2e two tasks with the same title are flagged', has('warn', /TASK-004, TASK-015 have the same title/));
      check('2f a duplicated link row is an error', has('error', /Duplicate link.*CR-T01 alias-of TASK-003/));
      check('2g overlapping responsibilities are listed', has('info', /TASK-010 overlaps TASK-012 — pr:10 and pr:13/));
      check('2h errors sort above warnings above notes', c.map(x => x.sev).join(',') === [...c.map(x => x.sev)].sort((a, b) => ['error', 'warn', 'info'].indexOf(a) - ['error', 'warn', 'info'].indexOf(b)).join(','));
      await page.click('[data-tab="queue"]');
      const pills = await page.$eval('#tasks', el => el.innerHTML);
      check('2i the queue marks the conflicting task with a conflict pill', /data-task="TASK-004"[\s\S]*?⚠ conflict/.test(pills) || (await allPages(page)).length > 0 && await page.evaluate(() => window.__TCC.conflictList().some(c => c.task === 'TASK-004' && c.sev === 'error')));
      await ctx.close();
    }

    console.log('3. Paused-task protection');
    {
      const {page, ctx, log} = await open(browser, {gh: ghBase(), selections: {'TASK-003': {verdict: 'approve', kind: 'review', scope: '', reason: '', fp: '', status: 'PAUSED'}}});
      await openTask(page, 'TASK-003');
      const why = await page.textContent('#approveWhy');
      check('3b and says why: an approval never lifts a pause', /approval never lifts a pause/.test(why) && /DEC-015/.test(why), why);
      check('3c Pause is disabled (already paused); Deny stays available', await (await btn(page, 'pause')).isDisabled() && !(await (await btn(page, 'deny')).isDisabled()));
      check('3d the page offers no resume; it says to resume by name, one task at a time', /resume <b>TASK-003<\/b> by name — one task at a time/.test(await page.innerHTML('#detail')) && !(await page.$('[data-decision="resume"]')));
      await openTask(page, 'TASK-004');
      check('3e Approve is disabled on a task paused only in Issue 7', await (await btn(page, 'approve')).isDisabled() && /paused in CR-T02 \(issue:7\)/.test(await page.textContent('#approveWhy')));
      const sel = await page.$eval('[data-sel="TASK-003"]', e => e.textContent);
      check('3f an approval of a paused task smuggled into storage is held back, never ready', /paused by the owner/.test(sel) && (await page.textContent('#decisionCount')).startsWith('0 ready'), sel);
      await page.check('#confirmDecisions');
      check('3g and Submit stays disabled with nothing else selected', await page.isDisabled('#submitDecisions'));
      await openTask(page, 'TASK-003'); await (await btn(page, 'approve')).click();
      check('3a the ticked Approve only removes the tick; then Approve is disabled on the paused task', await page.evaluate(() => !window.__TCC.store.selections['TASK-003']) && await (await btn(page, 'approve')).isDisabled());
      check('3h no page error', !log.requests.some(r => r.startsWith('PAGEERROR')), log.requests.filter(r => r.startsWith('PAGEERROR')).join('\n'));
      await ctx.close();
    }

    console.log('4. Bulk selection safeguards');
    {
      const {page, ctx, log, state} = await open(browser, {gh: ghBase()});
      state.dialog = 'dismiss';
      await page.click('#bulkApprove');
      const s0 = await page.evaluate(() => Object.keys(window.__TCC.store.selections));
      check('4a cancelling the confirmation selects nothing', s0.length === 0, s0);
      state.dialog = 'accept';
      await page.click('#bulkApprove');
      const msg = log.dialogs[log.dialogs.length - 1] || '';
      const sel = await page.evaluate(() => window.__TCC.store.selections);
      check('4b only the ungated, fresh, unpaused, unblocked task is selected', JSON.stringify(Object.keys(sel)) === '["TASK-001"]', JSON.stringify(sel));
      check('4c and only for read-only review / preparation', sel['TASK-001'] && sel['TASK-001'].kind === 'review' && sel['TASK-001'].bulk === true);
      const skipped = ['TASK-002: protected-gated', 'TASK-014: safety-gated', 'TASK-003: paused by the owner', 'TASK-004: paused in CR-T02', 'TASK-005: evidence is 46 days old', 'TASK-006: depends on TASK-007 (OPEN)'];
      check('4d the confirmation names every skipped task and its reason', skipped.every(s => msg.includes(s)), msg);
      check('4e the confirmation says it never deploys, merges or lifts a pause', /never deployment, a merge, device control or lifting a pause/.test(msg));
      const status = await page.textContent('#bulkStatus');
      check('4f the page reports 1 selected and 6 skipped', /1 selected\. 6 skipped/.test(status), status);
      await page.click('[data-filter="paused"]'); await page.click('#bulkApprove');
      check('4g in the Paused view nothing is eligible', /No task in this view is eligible/.test(await page.textContent('#bulkStatus')));
      const v = await page.evaluate(() => window.__TCC.bulkBlockers(window.__TCC.model.byId['TASK-008']));
      check('4h a completed task is never bulk-approvable', v.some(r => /DONE: closed/.test(r)), v);
      await ctx.close();
    }

    console.log('5. Five-task pagination');
    {
      const {page, ctx} = await open(browser, {gh: ghBase()});
      check('5a page 1 shows five tasks', (await listIds(page)).length === 5);
      check('5b the counter says page 1 of 3 and 12 tasks', (await page.textContent('#pageCount')) === 'Page 1 of 3 · 12 tasks', await page.textContent('#pageCount'));
      check('5c Previous is disabled on page 1', await page.isDisabled('#prevPage'));
      await page.click('#nextPage'); await page.click('#nextPage');
      check('5d the last page shows the remaining two', (await listIds(page)).length === 2 && await page.isDisabled('#nextPage'));
      await page.click('[data-filter="decide"]');
      check('5e changing the filter returns to page 1', (await page.textContent('#pageCount')).startsWith('Page 1 of'));
      await page.setViewportSize({width: 390, height: 844});
      check('5f a phone width still shows five', (await listIds(page)).length === Math.min(5, (await page.evaluate(() => window.__TCC.visibleTasks().length))));
      await ctx.close();
    }

    console.log('6. Priority sorting');
    {
      const {page, ctx} = await open(browser, {gh: ghBase()});
      const order = await allPages(page);
      const want = ['TASK-001', 'TASK-014', 'TASK-002', 'TASK-013', 'TASK-003', 'TASK-005', 'TASK-010', 'TASK-012', 'TASK-004', 'TASK-006', 'TASK-011', 'TASK-007'];
      check('6a highest to lowest priority, then decision first, paused last, then ID', JSON.stringify(order) === JSON.stringify(want), order.join(' '));
      const pri = await page.evaluate(ids => ids.map(i => window.__TCC.model.byId[i].P), order);
      check('6b priorities never go down the list', pri.every((p, i) => i === 0 || p >= pri[i - 1]), pri.join(' '));
      await page.selectOption('#sortOrder', 'low');
      const rev = await page.evaluate(() => window.__TCC.visibleTasks().map(t => t.P));
      check('6c lowest-first reverses it', rev[0] === 'P3' && rev[rev.length - 1] === 'P0', rev.join(' '));
      await page.selectOption('#sortOrder', 'high'); await page.selectOption('#priorityFilter', 'P0');
      check('6d the P0 filter shows only P0 tasks', JSON.stringify(await listIds(page)) === '["TASK-001","TASK-014"]');
      await ctx.close();
    }

    console.log('7. Completed-task filtering');
    {
      const {page, ctx} = await open(browser, {gh: ghBase()});
      const queue = await allPages(page);
      check('7a the queue never lists DONE or DENIED tasks', !queue.includes('TASK-008') && !queue.includes('TASK-009'));
      await page.click('[data-tab="completed"]');
      check('7b the Completed tab lists exactly the DONE and DENIED tasks', JSON.stringify(await listIds(page)) === '["TASK-008","TASK-009"]', await listIds(page));
      check('7c the bulk button is hidden on Completed', await page.isHidden('#bulkBox'));
      await page.click('#tasks [data-task="TASK-008"]');
      check('7d a completed task offers no decision', await (await btn(page, 'approve')).isDisabled() && await (await btn(page, 'deny')).isDisabled() && await (await btn(page, 'pause')).isDisabled());
      check('7e the tab counts agree', (await page.textContent('#countCompleted')) === '2' && (await page.textContent('#countQueue')) === '12');
      await ctx.close();
    }

    console.log('8. GitHub refresh');
    {
      const {page, ctx, log, state} = await open(browser, {gh: ghBase()});
      check('8a the page reads GitHub on open and says which commit', /GitHub feature\/casaray-v3-build @ aaaaaaa/.test(await page.textContent('#sync')), await page.textContent('#sync'));
      check('8b the two files are read at that commit, not at a moving branch', log.requests.filter(u => u.includes('raw.githubusercontent.com')).every(u => u.includes('/' + 'a'.repeat(40) + '/')));
      const tasks = baseTasks(); tasks.find(t => t.ID === 'TASK-013').Status = 'AWAITING_DECISION';
      Object.assign(state, md({tasks}), {sha: 'c'.repeat(40)});
      await refresh(page);
      check('8c a refresh picks up a status change', await page.evaluate(() => window.__TCC.model.byId['TASK-013'].Status) === 'AWAITING_DECISION' && /@ ccccccc/.test(await page.textContent('#sync')));
      state.fail = true; await refresh(page);
      const s = await page.textContent('#sync');
      check('8d when GitHub fails it says so and keeps the last GitHub read', /GitHub unreachable/.test(s) && /last GitHub read/.test(s) && await page.evaluate(() => window.__TCC.model.origin.sha.startsWith('ccc')), s);
      await ctx.close();
      const o = await open(browser, {gh: {fail: true}});
      const s2 = await o.page.textContent('#sync');
      check('8e opened offline it shows the built-in snapshot and says so', /GitHub unreachable/.test(s2) && /snapshot bbbbbbb of 2026-11-14/.test(s2) && (await listIds(o.page)).length === 5, s2);
      await o.ctx.close();
      const nl = await open(browser, {gh: Object.assign(ghBase(), md({withLinks: false}))});
      await nl.page.click('[data-tab="conflicts"]');
      check('8f a register with no Links table still keeps the snapshot pauses', /Register has no Links table/.test(await nl.page.textContent('#conflictList')) && await nl.page.evaluate(() => window.__TCC.approveBlockers(window.__TCC.model.byId['TASK-004']).some(r => /paused in CR-T02/.test(r))));
      await nl.ctx.close();
    }

    console.log('9. Stale decision rejection, and selections kept across refresh');
    {
      const {page, ctx, state} = await open(browser, {gh: ghBase()});
      await openTask(page, 'TASK-001'); await (await btn(page, 'approve')).click();
      check('9a the chosen decision shows a tick on the button and in the list', /✓/.test(await (await btn(page, 'approve')).textContent()) && /✓ APPROVE/.test(await page.textContent('#tasks')));
      await page.reload(); await settle(page);
      check('9b the selection survives a reload and a GitHub refresh', await page.evaluate(() => !!window.__TCC.store.selections['TASK-001']) && (await page.textContent('#decisionCount')).startsWith('1 ready'));
      const events = baseEvents(); events.push({ID: 'DEC-099', Date: '2026-11-15', Task: 'TASK-001', Event: 'NOTE', From: 'AWAITING_DECISION', To: 'AWAITING_DECISION', Scope: '—', Context: 'new evidence', Basis: '—', Via: '—', By: 'claude'});
      const tasks = baseTasks(); tasks[0].Updated = '2026-11-15';
      Object.assign(state, md({tasks, events}), {sha: 'd'.repeat(40)});
      await refresh(page);
      const row = await page.$eval('[data-sel="TASK-001"]', e => ({cls: e.className, text: e.textContent}));
      check('9c a task that changed since the choice is flagged for revalidation', /bad/.test(row.cls) && /changed since you chose/.test(row.text), row.text);
      await page.check('#confirmDecisions');
      check('9d and cannot be submitted until confirmed again', await page.isDisabled('#submitDecisions'));
      await openTask(page, 'TASK-001'); await page.click('#revalidate');
      check('9e Confirm again makes it ready', (await page.textContent('#decisionCount')).startsWith('1 ready') && !(await page.isDisabled('#submitDecisions')));
      tasks[0].Status = 'PAUSED'; Object.assign(state, md({tasks, events}), {sha: 'e'.repeat(40)}); await refresh(page);
      check('9f a task paused after the choice blocks the approval outright', /changed since you chose \(AWAITING_DECISION → PAUSED\)/.test(await page.textContent('[data-sel="TASK-001"]')) && await page.isDisabled('#submitDecisions'));
      await ctx.close();
      const v4 = await open(browser, {gh: ghBase(), legacy: {'TASK-001X': 'approve', 'V3-DEPLOY': 'approve', 'GHOST-1': 'deny'}});
      const sels = await v4.page.evaluate(() => window.__TCC.store.selections);
      check('9g V4 selections are mapped through the register\'s Links', !!sels['TASK-001'] && sels['TASK-001'].migrated === 'TASK-001X' && !!sels['TASK-013']);
      check('9h a mapped V4 selection must be confirmed again before it counts', (await v4.page.textContent('#decisionCount')).startsWith('0 ready'));
      check('9i a V4 approval of a task that is not awaiting a decision stays held back after confirming', await v4.page.evaluate(() => window.__TCC.selectionProblem('TASK-013', Object.assign({}, window.__TCC.store.selections['TASK-013'], {fp: window.__TCC.model.byId['TASK-013'].fp, migrated: undefined}))) === 'OPEN: there is no decision to approve');
      await v4.page.click('[data-tab="conflicts"]');
      check('9j a V4 selection with no canonical task is reported, not carried over', /GHOST-1, which has no canonical task\. Not carried over/.test(await v4.page.textContent('#conflictList')) && !sels['GHOST-1']);
      await v4.ctx.close();
    }

    console.log('10. Claude handoff accuracy');
    {
      const {page, ctx, state} = await open(browser, {gh: ghBase(), selections: {'TASK-003': {verdict: 'approve', kind: 'review', scope: '', reason: '', fp: '', status: 'PAUSED'}}});
      await openTask(page, 'TASK-014'); await (await btn(page, 'approve')).click();
      check('10a a gated approval is held back until its exact scope is written', /safety-gated: write the exact scope/.test(await page.textContent('#selProblem')));
      await page.fill('#scopeField', 'Sound the siren once for 10 seconds with the owner present');
      await page.check('#detail input[value="implement"]');
      await openTask(page, 'TASK-005'); await (await btn(page, 'deny')).click(); await page.fill('#reasonField', 'Superseded by the V3 rebuild');
      await openTask(page, 'TASK-013'); await (await btn(page, 'pause')).click(); await page.fill('#reasonField', 'Keep the branch; resume after PR 16');
      check('10b Submit needs the confirmation box', await page.isDisabled('#submitDecisions'));
      await page.check('#confirmDecisions'); await page.click('#submitDecisions');
      const text = await page.textContent('#handoffOutput');
      const json = JSON.parse(text.split('BATCH JSON\n')[1]);
      check('10c the batch holds exactly the three valid decisions, highest priority first', JSON.stringify(json.answers.map(a => a.task + ':' + a.verdict)) === '["TASK-014:approve","TASK-013:pause","TASK-005:deny"]', JSON.stringify(json));
      check('10d the approval carries its kind and exact scope', json.answers[0].scope === 'Implement on an isolated branch; no merge, no deployment. Exact scope: Sound the siren once for 10 seconds with the owner present');
      check('10e deny and pause carry their reason as context', json.answers[2].context === 'Superseded by the V3 rebuild' && json.answers[1].context === 'Keep the branch; resume after PR 16');
      check('10f the held-back approval of a paused task is listed as not in the handoff', /NOT IN THIS HANDOFF \(1\)\n- TASK-003 APPROVE: paused by the owner/.test(text), text);
      check('10g it says plainly that nothing is recorded yet', /STATUS: NOT RECORDED/.test(text) && /Handoff ready — not recorded/.test(await page.textContent('#handoff')));
      check('10h it names the register commit it was prepared against', /@ feature\/casaray-v3-build \(aaaaaaa\)/.test(text));
      check('10i each decision states what it does NOT authorise', /Not authorised: deployment, merge, Home Assistant or device operations, lifting any pause/.test(text));
      check('10j blockers and the last history row are carried per task', /TASK-014 · APPROVE · P0 · gate safety · was AWAITING_DECISION \(last history row DEC-014\)/.test(text));
      check('10k the command is the owner-decisions tool, as the owner, via chat', /tasks\.py decide --batch - --by owner --via chat --basis "Owner's Task Control Center handoff H-\d{12}/.test(text));
      check('10l the log shows every item as not recorded yet', (await page.textContent('#handoffLog')).split('not recorded yet').length - 1 === 3);
      // Claude records two of them; one row is by claude, which never counts as the owner's decision.
      const events = baseEvents();
      events.push({ID: 'DEC-016', Date: TODAY, Task: 'TASK-014', Event: 'APPROVED', From: 'AWAITING_DECISION', To: 'APPROVED', Scope: 'x', Context: '—', Basis: 'handoff', Via: 'chat', By: 'owner'});
      events.push({ID: 'DEC-017', Date: TODAY, Task: 'TASK-005', Event: 'DENIED', From: 'AWAITING_DECISION', To: 'DENIED', Scope: '—', Context: 'x', Basis: 'handoff', Via: 'chat', By: 'claude'});
      const tasks = baseTasks(); tasks.find(t => t.ID === 'TASK-014').Status = 'APPROVED';
      Object.assign(state, md({tasks, events}), {sha: 'e'.repeat(40)});
      await refresh(page);
      const logText = await page.textContent('#handoffLog');
      check('10m a decision is marked recorded only when GitHub shows the owner\'s row', /TASK-014 recorded DEC-016/.test(logText) && /TASK-005 not recorded yet/.test(logText) && /TASK-013 not recorded yet/.test(logText), logText);
      check('10n the recorded selection is cleared; the others stay', await page.evaluate(() => JSON.stringify(Object.keys(window.__TCC.store.selections).sort())) === '["TASK-003","TASK-005","TASK-013"]');
      await ctx.close();
    }

    console.log('10x. Backlog Cleanup review is isolated from task approvals');
    {
      const {page, ctx} = await open(browser, {gh: ghBase()});
      await page.click('[data-tab="cleanup"]');
      check('10x-a cleanup opens as a separate tab', await page.isVisible('#cleanupView') && !await page.isVisible('#workspace'));
      check('10x-b five flagged tasks per page', await page.locator('#cleanupList .cleanup-entry').count() <= 5);
      check('10x-c normal approval handoff remains empty', await page.textContent('#decisionCount') === '0 ready' && await page.locator('#selList .sel').count() === 0);
      await page.selectOption('#cleanupFilter', 'revalidate');
      check('10x-d filter finds evidence/paused records', await page.locator('#cleanupList .cleanup-entry').count() > 0);
      await page.selectOption('#cleanupFilter', 'all');
      const allIds = [];
      while (true) {
        allIds.push(...await page.locator('#cleanupList [data-cleanup]').evaluateAll(els => els.map(e => e.dataset.cleanup)));
        if (await page.isDisabled('#cleanupNext')) break;
        await page.click('#cleanupNext');
      }
      check('10x-e paused task is visible for review', allIds.includes('TASK-003'));
      await page.selectOption('#cleanupFilter', 'all');
      while (!await page.isDisabled('#cleanupPrev')) await page.click('#cleanupPrev');
      // Locate paused task by navigating pages, without relying on its position.
      for (let n=0; n<allIds.length; n+=5) {
        if (await page.locator('#cleanupList [data-cleanup="TASK-003"]').count()) break;
        if (await page.isDisabled('#cleanupNext')) break;
        await page.click('#cleanupNext');
      }
      const paused = page.locator('#cleanupList [data-cleanup="TASK-003"]');
      check('10x-f paused task cannot be retired or completed', await paused.locator('[data-cleanup-choice="retire"]').isDisabled() && await paused.locator('[data-cleanup-choice="complete"]').isDisabled());
      await paused.locator('[data-cleanup-choice="revalidate"]').click();
      check('10x-g selection ticks but cannot submit without confirmation', await paused.locator('[data-cleanup-choice="revalidate"]').getAttribute('aria-pressed') === 'true' && await page.isDisabled('#cleanupExport'));
      await page.check('#cleanupConfirm');
      await page.click('#cleanupExport');
      const handoff = await page.textContent('#cleanupOutput');
      check('10x-h cleanup handoff says it is not an execution decision', /OWNER REVIEW, NOT A TASK DECISION/.test(handoff) && /Never merge, deploy/.test(handoff));
      check('10x-i pause is explicitly preserved', /TASK-003.*REVALIDATE/.test(handoff) && /paused true/.test(handoff));
      check('10x-j cleanup cannot approve normal task', await page.textContent('#decisionCount') === '0 ready' && await page.locator('#selList .sel').count() === 0);
      check('10x-k stale and dependent tasks cannot be individually approved', await page.evaluate(() => ['TASK-005','TASK-006'].every(id => window.__TCC.approveBlockers(window.__TCC.model.byId[id]).length > 0)));
      await ctx.close();
    }

    console.log('11. The real register, and the real tool');
    {
      const real = JSON.parse(/<script type="application\/json" id="snapshot">([\s\S]*?)<\/script>/.exec(SRC)[1]);
      const stale = cp.spawnSync('python3', [path.join(HERE, 'build.py'), '--check'], {encoding: 'utf8'});
      check('11a the built-in snapshot matches the committed register and history', stale.status === 0, stale.stdout + stale.stderr);
      const {page, ctx} = await open(browser, {snap: real, gh: {register: real.register, history: real.history, issue: ISSUE([['CR-T01', 'PAUSED'], ['CR-T02', 'RESUMED'], ['CR-T03', 'PAUSED'], ['CR-T04', 'PAUSED'], ['CR-T05', 'PAUSED']]), prs: null}});
      const m = await page.evaluate(() => { const m = window.__TCC.model; return {dups: m.dupIds, n: m.tasks.length, bad: m.badRows,
        blocked: ['TASK-010', 'TASK-011', 'TASK-013', 'TASK-014', 'TASK-031'].map(id => window.__TCC.approveBlockers(m.byId[id]).length > 0),
        errors: window.__TCC.conflictList().filter(c => c.sev === 'error').map(c => c.msg)}; });
      check('11b the canonical register has no duplicate ID and no unreadable row', m.dups.length === 0 && m.bad.length === 0 && m.n >= 32, JSON.stringify(m));
      check('11c five tasks behind Issue 7\'s four paused IDs refuse approval', m.blocked.every(Boolean), JSON.stringify(m.blocked));
      check('11d the canonical register raises no conflict error', m.errors.length === 0, m.errors.join('\n'));
      // Approve one gated task with a scope, deny one, pause one; then give the batch to tasks.py.
      await openTask(page, 'TASK-032'); await (await btn(page, 'approve')).click(); await page.fill('#scopeField', 'Read PR 13 and PR 10 side by side and report; no merge, no close');
      await openTask(page, 'TASK-004'); await (await btn(page, 'deny')).click(); await page.fill('#reasonField', 'Fixture denial for the handoff test');
      await openTask(page, 'TASK-003'); await (await btn(page, 'pause')).click(); await page.fill('#reasonField', 'Fixture pause for the handoff test');
      await page.check('#confirmDecisions'); await page.click('#submitDecisions');
      const text = await page.textContent('#handoffOutput');
      await ctx.close();
      const repo = path.join(TMP, 'repo');
      fs.mkdirSync(repo, {recursive: true});
      // the whole committed tree, so every Home the register points at exists; then the working copies of the two files
      cp.execSync(`git -C "${ROOT}" archive HEAD | tar -x -C "${repo}"`);
      for (const f of ['TASK_REGISTER.md', 'DECISION_HISTORY.md']) fs.copyFileSync(path.join(ROOT, 'docs', 'project-tasks', f), path.join(repo, 'docs', 'project-tasks', f));
      cp.spawnSync('git', ['init', '-q', '-b', 'casaray-v3-design'], {cwd: repo});
      const tool = path.join(ROOT, '.claude', 'skills', 'owner-decisions', 'scripts', 'tasks.py');
      const basis = /--basis "([^"]+)"/.exec(text)[1];
      const batch = text.split('BATCH JSON\n')[1];
      const r = cp.spawnSync('python3', [tool, '--root', repo, '--today', REAL_TODAY, 'decide', '--batch', '-', '--by', 'owner', '--via', 'chat', '--basis', basis], {input: batch, encoding: 'utf8'});
      check('11e tasks.py accepts the handoff batch as printed', r.status === 0 && /TASK-032 APPROVED/.test(r.stdout) && /TASK-004 DENIED/.test(r.stdout) && /TASK-003 PAUSED/.test(r.stdout), r.stdout + r.stderr);
      const c = cp.spawnSync('python3', [tool, '--root', repo, '--today', REAL_TODAY, 'check'], {encoding: 'utf8'});
      check('11f and the register it leaves passes tasks.py check', c.status === 0, c.stdout.split('\n').filter(l => /^(ERROR|FAIL)/.test(l)).join('\n') + c.stderr);
      const hist = fs.readFileSync(path.join(repo, 'docs', 'project-tasks', 'DECISION_HISTORY.md'), 'utf8');
      check('11g the recorded approval keeps the exact scope the owner wrote', hist.includes('Exact scope: Read PR 13 and PR 10 side by side and report; no merge, no close'));
      const bad = cp.spawnSync('python3', [tool, '--root', repo, '--today', REAL_TODAY, 'decide', '--batch', '-', '--by', 'owner', '--via', 'chat', '--basis', basis], {input: JSON.stringify({answers: [{task: 'TASK-010', verdict: 'approve', scope: 'Edit the guarded cloud environment now please'}]}), encoding: 'utf8'});
      check('11h the tool still refuses approval of a separately paused task', bad.status !== 0 && /paused in another record: CR-T03/.test(bad.stderr + bad.stdout), bad.stdout + bad.stderr);
    }
    console.log('12. Whole run');
    check('12a no script error on any page in any test', PAGE_ERRORS.length === 0, PAGE_ERRORS.join('\n'));
  } finally {
    await browser.close();
    fs.rmSync(TMP, {recursive: true, force: true});
  }
  console.log(`\n${passes} passed, ${failures} failed`);
  process.exit(failures ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(2); });
