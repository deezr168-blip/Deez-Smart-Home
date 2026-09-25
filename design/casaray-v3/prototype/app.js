// CasaRay V3 prototype — application.
// Vanilla JS, no build step. Every control changes local demo state only.
(() => {
  'use strict';

  // ------------------------------------------------------------ helpers --
  const NA = new Set(['unavailable', 'unknown', 'none', '']);
  const $ = (s) => document.querySelector(s);
  const esc = (v) => String(v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const store = {
    get(k, d) { try { const v = localStorage.getItem('casaray-v3:' + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem('casaray-v3:' + k, JSON.stringify(v)); } catch (e) { /* storage blocked: the page still works */ } },
  };

  let S = {};
  const UI = {
    theme: store.get('theme', 'auto'),
    ids: store.get('ids', false),
    scenario: store.get('scenario', 'evening'),
    route: 'home',
    overlay: null,
  };

  const lang = () => (st('input_boolean.chinese_dashboard').s === 'on' ? 'zh' : 'en');
  function t(key, vars) {
    let s = I18N[lang()][key] ?? I18N.en[key] ?? key;
    if (vars) for (const k in vars) s = s.split('{' + k + '}').join(vars[k]);
    return s;
  }
  const join = (arr) => arr.join(lang() === 'zh' ? '、' : ' · ');
  const st = (id) => S[id] || { s: 'unavailable' };
  const na = (id) => NA.has(String(st(id).s));
  const on = (id) => st(id).s === 'on';
  function num(id) {
    if (na(id)) return null;
    const n = parseFloat(st(id).s);
    return Number.isFinite(n) ? n : null;
  }
  function dur(min) {
    if (min < 60) return t('m.min', { n: Math.max(1, Math.round(min)) });
    return t('m.hours', { n: Math.round(min / 60) });
  }
  const ago = (min) => (min == null ? '' : min < 1 ? t('m.just_now') : t('m.ago', { t: dur(min) }));
  const fmt = (n, d = 1) => (n == null ? '—' : Number(n).toLocaleString(lang() === 'zh' ? 'zh-CN' : 'en-AU', { minimumFractionDigits: d, maximumFractionDigits: d }));
  const money = (n) => 'A$' + Number(n).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function icon(name) {
    const p = window.CR_ICONS[name] || window.CR_ICONS['information-outline'];
    return `<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="${p}"/></svg>`;
  }
  // The entity caption shown when "Show entity IDs" is on. gap = no entity exists.
  function eid(ids, gap) {
    if (gap) return `<div class="eid gap">no entity · ${esc(gap)}</div>`;
    const list = [].concat(ids || []).filter(Boolean);
    return list.length ? `<div class="eid">${list.map(esc).join('<br>')}</div>` : '';
  }

  // Demo dates are written relative to 25/09/2026 and shifted to today, so a
  // bill that is overdue in the demo stays overdue whenever it is opened.
  const ANCHOR = Date.UTC(2026, 8, 25);
  const todayUTC = () => { const d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()); };
  function dueIn(id) {
    if (na(id)) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(st(id).s);
    if (!m) return null;
    return Math.round((Date.UTC(+m[1], m[2] - 1, +m[3]) - ANCHOR) / 864e5);
  }
  function dayLabel(offset) {
    const d = new Date(todayUTC() + offset * 864e5);
    const dd = String(d.getUTCDate()).padStart(2, '0');
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
    const yy = String(d.getUTCFullYear()).slice(2);
    return `${dd}/${mm}/${yy}`;
  }

  // -------------------------------------------------------------- model --
  const NAV = [
    ['home', 'home'], ['rooms', 'sofa'], ['security', 'shield-home'], ['energy', 'flash'],
    ['climate', 'thermometer'], ['lighting', 'lightbulb-group'], ['media', 'television'],
    ['people', 'account-group'], ['bills', 'receipt-text'], ['health', 'heart-pulse'],
  ];
  const TABS = ['home', 'rooms', 'security', 'energy'];

  // Lights counted for "lights on". Wall switches that feed a Hue group are
  // left out so one lamp is not counted twice.
  const LIGHTS = ['light.living_room', 'light.dining', 'light.bedroom_bedroom', 'light.bedroom_nightlight', 'switch.mainroomlight_switch_1'];
  const PEOPLE = [
    { id: 'person.raymond_du', n: 'Raymond', bat: 'sensor.raymonds_iphone_battery_level' },
    { id: 'person.vinh_du', n: 'Vinh', bat: 'sensor.vine_s_phone_battery_level' },
    { id: 'person.ai_q_huang', n: 'Ai', bat: 'sensor.ais_iphone_battery_level' },
  ];
  const DOORS = [
    { id: 'binary_sensor.f_contact_sensor_door', n: { en: 'Front door', zh: '前门' } },
    { id: 'binary_sensor.b_contact_sensor_door', n: { en: 'Back door', zh: '后门' } },
    { id: 'binary_sensor.m_contact_sensor_door', n: { en: "Parents' door", zh: '父母房门' } },
  ];
  const CAMERAS = [
    { id: 'camera.front_door_live_view', n: { en: 'Front door', zh: '前门' }, ic: 'cctv' },
    { id: 'camera.tapo_c425_north_wall_hd_stream_direct', n: { en: 'North wall', zh: '北墙' }, ic: 'cctv' },
    { id: 'camera.tapo_c200_stockroom_hd_stream_direct', n: { en: 'Stockroom', zh: '储藏室' }, ic: 'cctv' },
    { id: 'camera.smart_pet_feeder', n: { en: 'Pet feeder', zh: '喂食器' }, ic: 'paw' },
    { id: 'camera.tapo_c420_south_wall_hd_stream_direct', n: { en: 'South wall', zh: '南墙' }, ic: 'cctv' },
    { id: 'camera.tapo_c420_east_wall_hd_stream_direct', n: { en: 'East wall', zh: '东墙' }, ic: 'cctv' },
  ];
  const BATTERIES = [
    { id: 'sensor.front_door_battery', n: { en: 'Front doorbell', zh: '前门门铃' } },
    { id: 'sensor.tapo_c425_north_wall_battery', n: { en: 'North wall camera', zh: '北墙摄像头' } },
    { id: 'sensor.aqara_roller_shade_driver_e1_battery', n: { en: "Ray's blind", zh: 'Ray 卷帘' } },
    { id: 'sensor.living_room_living_hue_hue_sensor_battery', n: { en: 'Living room Hue sensor', zh: '客厅 Hue 传感器' } },
    { id: 'sensor.gas_meter_pulse_sensor_battery', n: { en: 'Gas meter pulse', zh: '燃气表脉冲' } },
    { id: 'sensor.powerpal_gateway_powerpal_battery', n: { en: 'Powerpal', zh: 'Powerpal' } },
  ];
  const BILLS = [
    { k: 'elec', n: { en: 'Electricity', zh: '电费' }, paid: 'input_boolean.elec_bill_paid', amt: 'input_number.elec_bill_amount', due: 'input_datetime.elec_bill_due', ic: 'flash' },
    { k: 'gas', n: { en: 'Gas', zh: '燃气费' }, paid: 'input_boolean.gas_bill_paid', amt: 'input_number.gas_bill_amount', due: 'input_datetime.gas_bill_due', ic: 'fire' },
    { k: 'water', n: { en: 'Water', zh: '水费' }, paid: 'input_boolean.water_bill_paid', amt: 'input_number.water_bill_amount', due: 'input_datetime.water_bill_due', ic: 'water-percent' },
    { k: 'council', n: { en: 'Council rates', zh: '市政费' }, paid: 'input_boolean.council_rate_paid', amt: 'input_number.council_rate_amount', due: 'input_datetime.council_rate_due', ic: 'home' },
    { k: 'rego', n: { en: 'Car registration', zh: '车辆注册' }, paid: 'input_boolean.rego_paid', amt: 'input_number.rego_amount', due: 'input_datetime.rego_due', ic: 'calendar' },
    { k: 'insurance', n: { en: 'Car insurance', zh: '车险' }, paid: 'input_boolean.car_insurance_paid', amt: 'input_number.car_insurance_amount', due: 'input_datetime.car_insurance_due', ic: 'receipt-text' },
  ];
  const nm = (o) => (typeof o === 'string' ? t(o) : o[lang()] || o.en);

  // Rooms. Every ID below exists in the 05/09 export; `gap` marks what the
  // house has no entity for.
  const ROOMS = [
    {
      id: 'living', n: 'room.living', ic: 'sofa',
      temp: 'sensor.living_room_living_hue_hue_sensor_temperature',
      motion: 'binary_sensor.living_room_living_hue_hue_sensor_motion',
      lux: 'sensor.living_room_living_hue_hue_sensor_illuminance',
      lights: [
        { id: 'light.living_room', n: { en: 'Living room', zh: '客厅' }, dim: true },
        { id: 'light.living_room_hue_ambiance_spot_1', n: { en: 'Hue spot 1', zh: 'Hue 射灯 1' } },
        { id: 'light.living_room_hue_ambiance_spot_2', n: { en: 'Hue spot 2', zh: 'Hue 射灯 2' } },
        { id: 'light.living_room_hue_ambiance_spot_3', n: { en: 'Hue spot 3', zh: 'Hue 射灯 3' } },
        { id: 'light.living_room_hue_ambiance_spot_4', n: { en: 'Hue spot 4', zh: 'Hue 射灯 4' } },
      ],
      air: [{ kind: 'purifier', id: 'fan.living_room_air_purifier', pm: 'sensor.living_room_air_purifier_pm2_5' }],
      media: ['media_player.living_room_tv_samsung_q9_series_65'],
      power: [
        { id: 'switch.genio_power_board_with_usb_livingroom_socket_1', n: { en: 'Power board 1', zh: '排插 1' } },
        { id: 'switch.genio_power_board_with_usb_livingroom_socket_2', n: { en: 'Power board 2', zh: '排插 2' } },
      ],
      scenes: [
        ['scene.living_room_living_room_bright', { en: 'Bright', zh: '明亮' }],
        ['scene.living_room_living_room_relax', { en: 'Relax', zh: '放松' }],
        ['scene.living_room_living_room_read', { en: 'Read', zh: '阅读' }],
        ['scene.living_room_living_room_dimmed', { en: 'Dimmed', zh: '调暗' }],
        ['scene.living_room_living_room_nightlight', { en: 'Nightlight', zh: '夜灯' }],
      ],
    },
    {
      id: 'dining', n: 'room.dining', ic: 'silverware-fork-knife',
      temp: 'sensor.living_room_living_room_temperature',
      motion: 'binary_sensor.living_room_living_room_motion',
      lights: [{ id: 'light.dining', n: { en: 'Dining', zh: '餐厅' }, dim: true }],
      feeder: 'camera.smart_pet_feeder',
      scenes: [
        ['scene.dining_dining_relax', { en: 'Relax', zh: '放松' }],
        ['scene.dining_dining_read', { en: 'Read', zh: '阅读' }],
      ],
    },
    {
      id: 'kitchen', n: 'room.kitchen', ic: 'stove',
      motion: 'binary_sensor.k_motion_sensor_motion',
      lightsGap: 'f.kitchen_lights',
      power: [
        { id: 'switch.k_coffee_p100', n: { en: 'Coffee', zh: '咖啡机' }, ic: 'coffee' },
        { id: 'switch.k_top_p100', n: { en: 'Top bench', zh: '上层台面' } },
        { id: 'switch.k_bot_p100', n: { en: 'Bottom bench', zh: '下层台面' } },
      ],
      fridge: { temp: 'sensor.kitchen_electrolux_fridge_temperature', door: 'binary_sensor.lg_fridge_door' },
    },
    {
      id: 'parents', n: 'room.parents', ic: 'bed-king',
      temp: 'sensor.bedroom_motion_sensor_temperature',
      hum: 'sensor.bedroom_motion_sensor_humidity',
      motion: 'binary_sensor.bedroom_motion_sensor_motion',
      occupied: 'binary_sensor.bedroom_parents_room_ac_room_occupied',
      lights: [{ id: 'switch.mainroomlight_switch_1', n: { en: 'Main light', zh: '主灯' } }],
      air: [{ kind: 'ac', id: 'climate.bedroom_parents_room_ac' }],
      media: ['media_player.55_qled_4k_ai_qa55q7faawxxy'],
      door: 'binary_sensor.m_contact_sensor_door',
    },
    {
      id: 'ray', n: 'room.ray', ic: 'bed',
      tempGap: 'f.ray_temp',
      lights: [
        { id: 'light.bedroom_bedroom', n: { en: 'Bedroom', zh: '卧室' }, dim: true },
        { id: 'light.bedroom_nightlight', n: { en: 'Nightlight', zh: '夜灯' }, dim: true },
      ],
      cover: 'cover.aqara_roller_shade_driver_e1',
      media: ['media_player.q70f8036'],
      power: [{ id: 'switch.r_energy_monitor_p110m', n: { en: "Ray's desk", zh: 'Ray 书桌' }, w: 'sensor.r_energy_monitor_p110m_current_consumption' }],
      scenes: [
        ['scene.bedroom_bedroom_read', { en: 'Read', zh: '阅读' }],
        ['scene.bedroom_bedroom_concentrate', { en: 'Concentrate', zh: '专注' }],
        ['scene.bedroom_bedroom_nightlight', { en: 'Nightlight', zh: '夜灯' }],
      ],
    },
    {
      id: 'garage', n: 'room.garage', ic: 'garage',
      power: [{ id: 'switch.g_monitor_freezer_p110m', n: { en: 'Garage freezer', zh: '车库冰柜' }, w: 'sensor.g_monitor_freezer_p110m_current_consumption', protected: true, ic: 'fridge' }],
      note: 'f.freezer',
    },
    {
      id: 'guest', n: 'room.guest', ic: 'bed-outline',
      power: [{ id: 'switch.g_printer_p100', n: { en: 'Printer', zh: '打印机' }, ic: 'printer' }],
      media: ['media_player.pogo'],
    },
    {
      id: 'backyard', n: 'room.backyard', ic: 'pine-tree',
      door: 'binary_sensor.b_contact_sensor_door',
      note: 'f.backyard',
    },
  ];
  const room = (id) => ROOMS.find((r) => r.id === id);
  const MEDIA_NAMES = {
    'media_player.living_room_tv_samsung_q9_series_65': { en: 'Living room TV', zh: '客厅电视' },
    'media_player.55_qled_4k_ai_qa55q7faawxxy': { en: "Parents' TV", zh: '父母房电视' },
    'media_player.q70f8036': { en: "Ray's TV", zh: 'Ray 房电视' },
    'media_player.pogo': { en: 'Pogo', zh: 'Pogo' },
  };

  // --------------------------------------------------------- derivations --
  // Every summary returns null when nothing it depends on answered, so the
  // caller can say "No data" instead of claiming a zero.
  function lightsOn(ids = LIGHTS) {
    const known = ids.filter((i) => !na(i));
    if (!known.length) return null;
    return known.filter(on).length;
  }
  function peopleHome() {
    const known = PEOPLE.filter((p) => !na(p.id));
    if (!known.length) return null;
    return { x: known.filter((p) => st(p.id).s === 'home').length, y: known.length };
  }
  function doorsSummary() {
    const known = DOORS.filter((d) => !na(d.id));
    const open = known.filter((d) => on(d.id));
    return { known: known.length, open, dark: DOORS.length - known.length };
  }
  function camerasOnline() { return CAMERAS.filter((c) => !na(c.id)).length; }
  function lowBatteries() {
    const known = BATTERIES.filter((b) => num(b.id) != null);
    return { known: known.length, low: known.filter((b) => num(b.id) < 25) };
  }
  function billState(b) {
    if (na(b.paid)) return 'na';
    if (on(b.paid)) return 'paid';
    const d = dueIn(b.due);
    if (d == null) return 'nodue';
    return d < 0 ? 'overdue' : 'due';
  }

  // Needs-attention checks. Each returns an alert, null (checked and fine), or
  // 'unknown' (its inputs did not answer), which is counted, never hidden.
  const CHECKS = [
    () => {
      const b = lowBatteries();
      if (!b.known) return 'unknown';
      if (!b.low.length) return null;
      return { tone: 'red', ic: 'battery-alert', title: t('a.batteries'), ids: b.low.map((x) => x.id),
        detail: join(b.low.map((x) => `${nm(x.n)} ${num(x.id)}%`)), go: 'health' };
    },
    () => {
      const ev = ['event.master_bedroom_emergency_button_dad_main', 'event.master_bedroom_emergency_button_mum_main'];
      const link = ['binary_sensor.emergency_button_dad_cloud_connection', 'binary_sensor.emergency_button_mum_cloud_connection'];
      if (link.every(na)) return 'unknown';
      if (!ev.some(na)) return null;
      return { tone: 'red', ic: 'bell-ring', title: t('a.emergency'), detail: t('a.emergency_d'), ids: ev.concat(link), go: 'security' };
    },
    () => {
      const over = BILLS.filter((b) => billState(b) === 'overdue');
      if (BILLS.every((b) => na(b.paid))) return 'unknown';
      if (!over.length) return null;
      return { tone: 'red', ic: 'receipt-text', title: t('a.bill_overdue'), ids: over.flatMap((b) => [b.paid, b.due]),
        detail: join(over.map((b) => `${nm(b.n)} ${money(num(b.amt) || 0)} · ${t('s.due')} ${dayLabel(dueIn(b.due))}`)), go: 'bills' };
    },
    () => {
      const d = 'binary_sensor.b_contact_sensor_door';
      if (na(d)) return 'unknown';
      if (!on(d)) return null;
      return { tone: 'amber', ic: 'door-open', title: t('a.backdoor'), detail: ago(st(d).ago), ids: [d], go: 'security' };
    },
    () => {
      const p = peopleHome(), l = lightsOn();
      if (!p || l == null) return 'unknown';
      if (p.x > 0 || l === 0) return null;
      return { tone: 'amber', ic: 'lightbulb', title: t('a.away_lights'), detail: t('m.lights_on', { n: l }), ids: LIGHTS, go: 'lighting' };
    },
    () => {
      const inv = 'sensor.primo_5_0_1_1_ac_power';
      if (!na(inv)) return null;
      return { tone: 'grey', ic: 'solar-power', title: t('a.solar'), detail: t('a.solar_d'), ids: [inv], go: 'energy' };
    },
  ];
  function attention() {
    const out = CHECKS.map((c) => c());
    return { alerts: out.filter((x) => x && x !== 'unknown'), unknown: out.filter((x) => x === 'unknown').length };
  }

  // ------------------------------------------------------------ widgets --
  const h2 = (key, ic, extra = '') => `<h2>${icon(ic)}<span>${t(key)}</span>${extra}</h2>`;
  const sec = (body, cls = '') => `<section class="sec ${cls}">${body}</section>`;
  const foot = (key) => `<p class="foot">${t(key)}</p>`;
  const grid = (cells, cols = 2, colsSm = 1) => `<div class="grid" style="--cols:${cols};--cols-sm:${colsSm}">${cells.join('')}</div>`;

  function tile({ ids, ic, name, sub, state = 'off', pill = '', action = '', feature = '', gap = '', tag = 'div', label = '' }) {
    const cls = state === 'on' ? 'on' : state === 'na' ? 'na' : '';
    const attrs = tag === 'button' ? ` type="button" ${action}${label ? ` aria-label="${esc(label)}"` : ''}` : '';
    return `<${tag} class="card tile ${cls}"${attrs}>
      <div class="ic ${state === 'green' ? 'green' : state === 'red' ? 'red' : ''}">${icon(ic)}</div>
      <div><div class="name">${name}</div>${sub ? `<div class="sub">${sub}</div>` : ''}</div>
      <div class="pc">${pill}</div>${feature}${eid(ids, gap)}</${tag}>`;
  }
  const naPill = (key = 's.no_data') => `<span class="pill">${t(key)}</span>`;

  function lightTile(l) {
    const id = l.id;
    if (na(id)) return tile({ ids: id, ic: 'lightbulb-off', name: nm(l.n), sub: t('s.offline'), state: 'na', pill: naPill('s.offline') });
    const isOn = on(id);
    const b = st(id).a?.brightness ?? 0;
    const sub = isOn ? `<span class="hl">${t('s.on')}</span>${st(id).a?.color ? ' · ' + esc(lang() === 'zh' ? '暖白' : st(id).a.color) : ''}` : t('s.off');
    const feature = l.dim && isOn
      ? `<div class="feature"><div class="bar"><div class="fill" style="width:${b}%"></div>
          <div class="lbl"><span>${t('u.brightness')}</span><span data-bl="${id}">${b}%</span></div>
          <input type="range" min="1" max="100" value="${b}" data-bright="${id}" aria-label="${esc(nm(l.n))} ${t('u.brightness')}"></div></div>`
      : '';
    // The toggle is a button inside the card so the brightness bar can be dragged without toggling.
    return `<div class="card tile ${isOn ? 'on' : ''}">
      <button class="ic" type="button" data-toggle="${id}" aria-label="${esc(nm(l.n))}: ${isOn ? t('s.on') : t('s.off')}">${icon(isOn ? 'lightbulb' : 'lightbulb-outline')}</button>
      <button type="button" data-toggle="${id}" style="text-align:left"><div class="name">${nm(l.n)}</div><div class="sub">${sub}</div></button>
      <div></div>${feature}${eid(id)}</div>`;
  }

  function plugTile(p) {
    const id = p.id;
    if (na(id)) return tile({ ids: id, ic: p.ic || 'power-socket-au', name: nm(p.n), sub: t('s.offline'), state: 'na', pill: naPill('s.offline') });
    const w = p.w ? num(p.w) : null;
    const sub = [on(id) ? `<span class="hl">${t('s.on')}</span>` : t('s.off')];
    if (p.w) sub.push(w == null ? t('s.no_data') : `${fmt(w)} W`);
    if (p.protected) {
      return tile({ ids: [id, p.w], ic: p.ic || 'power-socket-au', name: nm(p.n), sub: sub.join(' · '), state: on(id) ? 'on' : 'off', pill: `<span class="pill green">${t('s.protected')}</span>` });
    }
    return tile({ tag: 'button', action: `data-toggle="${id}"`, label: nm(p.n), ids: [id, p.w], ic: p.ic || 'power-socket-au', name: nm(p.n), sub: sub.join(' · '), state: on(id) ? 'on' : 'off' });
  }

  function mediaTile(id) {
    const n = nm(MEDIA_NAMES[id]);
    if (na(id)) return tile({ ids: id, ic: 'television', name: n, sub: t('s.offline'), state: 'na', pill: naPill('s.offline') });
    const s = st(id);
    const isOn = s.s === 'on' || s.s === 'playing';
    const vol = s.a?.volume ?? 20;
    const feature = isOn ? `<div class="feature"><div class="bar"><div class="fill" style="width:${vol}%"></div>
      <div class="lbl"><span>${t('u.volume')}</span><span data-bl="${id}">${vol}%</span></div>
      <input type="range" min="0" max="100" value="${vol}" data-volume="${id}" aria-label="${esc(n)} ${t('u.volume')}"></div></div>` : '';
    return `<div class="card tile ${isOn ? 'on' : ''}">
      <button class="ic" type="button" data-toggle="${id}" aria-label="${esc(n)}">${icon('power')}</button>
      <div><div class="name">${n}</div><div class="sub">${isOn ? `<span class="hl">${t('s.on')}</span>${s.a?.source ? ' · ' + esc(s.a.source) : ''}` : t('s.off')}</div></div>
      <div></div>${feature}${eid(id)}</div>`;
  }

  function purifierTile(a) {
    const id = a.id;
    if (na(id)) return tile({ ids: [id, a.pm], ic: 'air-purifier', name: t('h.air'), sub: t('s.offline'), state: 'na', pill: naPill() });
    const sp = on(id) ? st(id).a?.speed || 'low' : 'off';
    const pm = num(a.pm);
    const quality = pm == null ? t('s.no_data') : `PM2.5 ${pm} µg/m³${pm <= 12 ? (lang() === 'zh' ? '，良好' : ', good') : ''}`;
    const opts = [['off', t('s.off')], ['low', t('u.low')], ['medium', t('u.medium')], ['high', t('u.high')]];
    return `<div class="card tile ${on(id) ? 'on' : ''}">
      <div class="ic">${icon('air-purifier')}</div>
      <div><div class="name">${lang() === 'zh' ? '空气净化器' : 'Air purifier'}</div><div class="sub">${on(id) ? `<span class="hl">${t('s.on')}</span> · ` : ''}${quality}</div></div><div></div>
      <div class="feature"><div class="seg" role="group" aria-label="${t('u.speed')}">${opts.map(([v, l]) => `<button type="button" data-speed="${id}" data-v="${v}" aria-pressed="${sp === v}">${l}</button>`).join('')}</div></div>
      ${eid([id, a.pm])}</div>`;
  }

  function acCard(id) {
    if (na(id)) return tile({ ids: id, ic: 'snowflake', name: t('h.ac'), sub: t('s.offline'), state: 'na', pill: naPill() });
    const a = st(id).a;
    const mode = st(id).s;
    const modes = [['off', t('s.off'), 'power'], ['cool', t('u.cool'), 'snowflake'], ['heat', t('u.heat'), 'fire'], ['fan_only', t('u.fan_only'), 'fan']];
    const active = mode !== 'off';
    return `<div class="card ${active ? 'on' : ''}">
      <div class="tile"><div class="ic">${icon(mode === 'heat' ? 'fire' : 'snowflake')}</div>
        <div><div class="name">${lang() === 'zh' ? '父母房空调' : "Parents' room AC"}</div>
        <div class="sub">${active ? `<span class="hl">${t(mode === 'heat' ? 's.heating' : mode === 'cool' ? 's.cooling' : 's.on')}</span> · ` : `${t('s.off')} · `}${lang() === 'zh' ? '室温' : 'Room'} ${fmt(a.current)}°</div></div><div></div></div>
      <div class="thermo"><button class="round" type="button" data-ac="-0.5" aria-label="${t('u.target')} −">${icon('minus')}</button>
        <div class="target"><div class="n">${fmt(a.target)}°</div><div class="l">${t('u.target')}</div></div>
        <button class="round" type="button" data-ac="0.5" aria-label="${t('u.target')} +">${icon('plus')}</button></div>
      <div class="feature" style="margin-top:12px"><div class="seg" role="group" aria-label="Mode">${modes.map(([v, l]) => `<button type="button" data-acmode="${v}" aria-pressed="${mode === v}">${l}</button>`).join('')}</div></div>
      ${eid(id)}</div>`;
  }

  function coverTile(id) {
    if (na(id)) return tile({ ids: id, ic: 'blinds-horizontal', name: lang() === 'zh' ? '卷帘' : 'Blind', sub: t('s.offline'), state: 'na', pill: naPill() });
    const p = st(id).a?.position ?? 0;
    return `<div class="card tile ${p > 0 ? 'on' : ''}"><div class="ic">${icon('blinds-horizontal')}</div>
      <div><div class="name">${lang() === 'zh' ? '卷帘' : 'Blind'}</div><div class="sub">${p > 0 ? `<span class="hl">${t('s.open')}</span> · ${p}%` : t('s.closed')}</div></div><div></div>
      <div class="feature"><div class="bar"><div class="fill" style="width:${p}%"></div>
        <div class="lbl"><span>${t('u.position')}</span><span data-bl="${id}">${p}%</span></div>
        <input type="range" min="0" max="100" step="5" value="${p}" data-cover="${id}" aria-label="${t('u.position')}"></div></div>${eid(id)}</div>`;
  }

  function sceneBtn([id, n]) {
    if (na(id)) return tile({ ids: id, ic: 'palette', name: nm(n), sub: t('s.no_data'), state: 'na' });
    return tile({ tag: 'button', action: `data-scene="${id}" data-name="${esc(nm(n))}"`, ids: id, ic: 'palette', name: nm(n), sub: t('h.scenes') });
  }

  function doorTile(d) {
    const id = d.id;
    if (na(id)) return tile({ ids: id, ic: 'door-closed', name: nm(d.n), sub: t('s.no_data'), state: 'na', pill: naPill() });
    const open = on(id);
    return tile({ ids: id, ic: open ? 'door-open' : 'door-closed', name: nm(d.n), state: open ? 'on' : 'green',
      sub: `${open ? `<span class="hl">${t('s.open')}</span>` : t('s.closed')} · ${ago(st(id).ago)}` });
  }

  function motionTile(id, name, extra) {
    if (na(id)) return tile({ ids: id, ic: 'motion-sensor', name, sub: t('s.no_data'), state: 'na', pill: naPill() });
    const m = on(id);
    return tile({ ids: [id, extra], ic: 'motion-sensor', name, state: m ? 'on' : 'off',
      sub: m ? `<span class="hl">${t('s.movement_now')}</span>` : `${t('s.quiet')} · ${dur(st(id).ago || 0)}` });
  }

  function camTile(c) {
    if (na(c.id)) {
      return tile({ ids: c.id, ic: c.ic, name: nm(c.n), sub: lang() === 'zh' ? '无画面，也无电池读数' : 'No stream and no battery reading', state: 'na', pill: naPill('s.offline') });
    }
    return `<div class="card cam"><div class="frame">${icon(c.ic)}</div>
      <div class="cap"><span>${nm(c.n)}</span><span class="live">${t('s.live').toUpperCase()}</span></div>${eid(c.id)}</div>`;
  }

  function statCard(n, unit, label, ids) {
    return `<div class="card stat${n == null ? ' na' : ''}"><div class="n">${n == null ? '—' : n}<small>${n == null ? t('s.no_data') : unit}</small></div><div class="sub">${label}</div>${eid(ids)}</div>`;
  }

  function alertCard(a) {
    return `<button type="button" class="card alert tile ${a.tone}" data-go="${a.go}">
      <div class="ic ${a.tone === 'amber' ? 'amber' : a.tone}">${icon(a.ic)}</div>
      <div><div class="name">${a.title}</div><div class="sub">${a.detail}</div></div>
      <div class="chev" style="color:var(--text-muted);font-size:20px">${icon('chevron-right')}</div>${eid(a.ids)}</button>`;
  }

  function roomLine(r) {
    const bits = [];
    if (r.lights) {
      const n = lightsOn(r.lights.map((l) => l.id));
      if (n == null) bits.push(`<span>${t('s.no_data')}</span>`);
      else bits.push(n ? `<span class="hl">${n === 1 ? t('m.light_on') : t('m.lights_on', { n })}</span>` : `<span>${t('s.lights_off')}</span>`);
    }
    if (r.motion && !na(r.motion) && on(r.motion)) bits.unshift(`<span class="hl">${t('c.movement')}</span>`);
    if (r.occupied && !na(r.occupied) && on(r.occupied) && !(r.motion && on(r.motion))) bits.unshift(`<span>${t('s.occupied')}</span>`);
    if (r.power && !r.lights) {
      const known = r.power.filter((p) => !na(p.id));
      if (known.length) {
        const k = known.filter((p) => on(p.id)).length;
        if (r.id === 'garage') {
          const w = num(r.power[0].w);
          bits.push(`<span>${w == null ? t('s.no_data') : `${fmt(w)} W`}</span>`);
        } else bits.push(`<span>${t('m.plugs_on', { n: k })}</span>`);
      }
    }
    if (r.cover && !na(r.cover)) bits.push(`<span>${(st(r.cover).a?.position ?? 0) > 0 ? t('s.blind_open') : t('s.blind_closed')}</span>`);
    if (r.door) {
      if (na(r.door)) bits.push(`<span>${lang() === 'zh' ? '门：无数据' : 'Door: no data'}</span>`);
      else if (r.id === 'backyard') bits.push(on(r.door) ? `<span class="hl">${lang() === 'zh' ? '门开着' : 'Door open'}</span>` : `<span>${lang() === 'zh' ? '门已关闭' : 'Door closed'}</span>`);
    }
    if (r.temp) bits.push(`<span>${num(r.temp) == null ? '—°' : fmt(num(r.temp)) + '°'}</span>`);
    return bits.join('');
  }
  function roomRow(r) {
    const allDark = roomIds(r).length && roomIds(r).every(na);
    return `<button type="button" class="card row ${allDark ? 'na' : ''}" data-go="room-${r.id}">
      <div class="ic ${allDark ? 'grey' : ''}">${icon(r.ic)}</div>
      <div><div class="name">${t(r.n)}</div><div class="meta">${roomLine(r) || `<span>${t('s.no_data')}</span>`}</div></div>
      <div class="chev">${icon('chevron-right')}</div></button>`;
  }
  function roomIds(r) {
    return [r.temp, r.motion, r.door, r.cover, ...(r.lights || []).map((l) => l.id), ...(r.power || []).map((p) => p.id), ...(r.media || [])].filter(Boolean);
  }

  // Monitored load over the last 12 hours. Shape only; demo data.
  const SPARK = [96, 120, 88, 170, 110, 72, 131, 139, 98, 118, 104, 148];

  // ------------------------------------------------------------ chips --
  function chip(ic, label, value, tone = '') {
    return `<div class="chip ${tone}" role="listitem">${icon(ic)}<span class="l">${label}</span><span class="v">${value}</span></div>`;
  }
  const noData = () => t('s.no_data');
  function chipsFor(route) {
    const out = [];
    const temp = (id) => (num(id) == null ? null : fmt(num(id)) + '°');
    if (route === 'home') {
      const wx = st('weather.forecast_home');
      out.push(chip('weather-cloudy', t('c.outside'), na('weather.forecast_home') ? noData() : `${wx.a.temperature}°`, na('weather.forecast_home') ? 'na' : ''));
      const inside = temp('sensor.living_room_living_hue_hue_sensor_temperature');
      out.push(chip('thermometer', t('c.inside'), inside ?? noData(), inside ? '' : 'na'));
      const p = peopleHome();
      out.push(chip('account', t('c.home'), p ? t('m.x_of_y', { x: p.x, y: p.y }) : noData(), p ? '' : 'na'));
      const w = num('sensor.casa_monitored_power');
      out.push(chip('flash', t('c.monitored'), w == null ? noData() : `${fmt(w)} W`, w == null ? 'na' : ''));
    } else if (route === 'security') {
      const d = doorsSummary();
      let v, tone = '';
      if (!d.known) { v = noData(); tone = 'na'; }
      else if (d.open.length) { v = join(d.open.map((x) => nm(x.n))) + ' ' + t('s.open').toLowerCase(); tone = 'warn'; }
      else v = d.dark ? `${d.known} ${t('s.closed').toLowerCase()} · ${d.dark} ${t('s.no_data').toLowerCase()}` : t('s.all_closed');
      out.push(chip('door-closed', t('c.doors'), v, tone));
      const c = camerasOnline();
      out.push(chip('cctv', t('c.cameras'), t('m.x_of_y', { x: c, y: CAMERAS.length }) + (lang() === 'zh' ? ' 在线' : ' online'), c < CAMERAS.length ? 'warn' : ''));
      const db = 'sensor.front_door_last_activity';
      out.push(chip('bell-ring', t('c.doorbell'), na(db) ? noData() : (lang() === 'zh' ? st(db).s.replace('Yesterday', '昨天') : st(db).s), na(db) ? 'na' : ''));
    } else if (route === 'energy') {
      const w = num('sensor.casa_monitored_power');
      out.push(chip('flash', t('c.monitored'), w == null ? noData() : `${fmt(w)} W`, w == null ? 'na' : ''));
      const f = num('sensor.energy_production_today');
      out.push(chip('solar-power', t('c.forecast'), f == null ? noData() : `${fmt(f)} kWh`, f == null ? 'na' : ''));
      const co = num('sensor.electricity_maps_co2_intensity');
      out.push(chip('leaf', t('c.carbon'), co == null ? noData() : `${fmt(co, 0)} g/kWh`, co == null ? 'na' : ''));
    } else if (route === 'climate') {
      const wx = st('weather.forecast_home');
      out.push(chip('weather-cloudy', t('c.outside'), na('weather.forecast_home') ? noData() : `${wx.a.temperature}°`, na('weather.forecast_home') ? 'na' : ''));
      const temps = ROOMS.filter((r) => r.temp && num(r.temp) != null).map((r) => [t(r.n), num(r.temp)]);
      if (temps.length) {
        temps.sort((a, b) => b[1] - a[1]);
        out.push(chip('fire', t('c.warm'), `${temps[0][0]} ${fmt(temps[0][1])}°`));
        out.push(chip('snowflake', t('c.cool'), `${temps[temps.length - 1][0]} ${fmt(temps[temps.length - 1][1])}°`));
      } else out.push(chip('thermometer', t('c.inside'), noData(), 'na'));
    } else if (route === 'lighting') {
      const n = lightsOn();
      const known = LIGHTS.filter((i) => !na(i)).length;
      out.push(chip('lightbulb', t('c.lights_on'), n == null ? noData() : t('m.x_of_y', { x: n, y: known }), n == null ? 'na' : n ? 'warn' : ''));
    } else if (route === 'people') {
      const p = peopleHome();
      out.push(chip('account', t('c.home'), p ? t('m.x_of_y', { x: p.x, y: p.y }) : noData(), p ? '' : 'na'));
      out.push(chip('account-group', lang() === 'zh' ? '访客模式' : 'Guest mode', on('input_boolean.guest_mode') ? t('s.on') : t('s.off')));
    } else if (route === 'media') {
      const players = Object.keys(MEDIA_NAMES);
      const known = players.filter((p) => !na(p));
      const playing = known.filter((p) => ['on', 'playing'].includes(st(p).s)).length;
      out.push(chip('television', t('c.playing'), known.length ? t('m.x_of_y', { x: playing, y: known.length }) : noData(), known.length ? '' : 'na'));
    } else if (route === 'bills') {
      const states = BILLS.map(billState);
      const unpaid = states.filter((s) => ['due', 'overdue', 'nodue'].includes(s)).length;
      out.push(chip('receipt-text', t('c.unpaid'), t('m.x_of_y', { x: unpaid, y: BILLS.length })));
      const measured = states.filter((s) => s === 'due' || s === 'overdue').length;
      const over = states.filter((s) => s === 'overdue').length;
      out.push(chip('alert-circle', t('c.overdue'), measured ? String(over) : noData(), measured ? (over ? 'bad' : '') : 'na'));
      const next = BILLS.filter((b) => billState(b) === 'due').sort((a, b) => dueIn(a.due) - dueIn(b.due))[0];
      out.push(chip('calendar', t('c.next_due'), next ? `${nm(next.n)} ${dayLabel(dueIn(next.due))}` : noData(), next ? '' : 'na'));
    } else if (route === 'health') {
      const ups = ['update.home_assistant_core_update', 'update.home_assistant_operating_system_update', 'update.home_assistant_supervisor_update'];
      const known = ups.filter((u) => !na(u));
      const n = known.filter(on).length;
      out.push(chip('update', t('c.updates'), known.length ? (n ? String(n) : t('s.up_to_date')) : noData(), known.length ? (n ? 'warn' : '') : 'na'));
      const bk = 'sensor.backup_last_successful_automatic_backup';
      out.push(chip('database', t('c.backup'), na(bk) ? noData() : (lang() === 'zh' ? st(bk).s.replace('Today', '今天') : st(bk).s), na(bk) ? 'na' : ''));
      const wan = 'binary_sensor.eero_wan_status';
      out.push(chip('wifi', t('c.wan'), na(wan) ? noData() : on(wan) ? t('s.connected') : t('s.offline'), na(wan) ? 'na' : on(wan) ? '' : 'bad'));
    } else if (route === 'rooms') {
      out.push(chip('lightbulb', t('c.lights_on'), lightsOn() == null ? noData() : String(lightsOn())));
      const moving = ROOMS.filter((r) => r.motion && !na(r.motion) && on(r.motion)).map((r) => t(r.n));
      const anyMotion = ROOMS.some((r) => r.motion && !na(r.motion));
      out.push(chip('motion-sensor', t('c.movement'), anyMotion ? (moving.length ? join(moving) : t('s.quiet')) : noData(), anyMotion ? (moving.length ? 'warn' : '') : 'na'));
    } else if (route.startsWith('room-')) {
      const r = room(route.slice(5));
      if (r.temp) out.push(chip('thermometer', t('c.room'), temp(r.temp) ?? noData(), temp(r.temp) ? '' : 'na'));
      if (r.motion) {
        const m = r.motion;
        out.push(chip('motion-sensor', t('c.movement'), na(m) ? noData() : on(m) ? t('s.movement_now') : `${t('s.quiet')}, ${dur(st(m).ago || 0)}`, na(m) ? 'na' : on(m) ? 'warn' : ''));
      }
      if (r.lux) out.push(chip('white-balance-sunny', t('c.light_level'), num(r.lux) == null ? noData() : `${fmt(num(r.lux), 0)} lx`, num(r.lux) == null ? 'na' : ''));
      if (r.lights) {
        const n = lightsOn(r.lights.map((l) => l.id));
        out.push(chip('lightbulb', t('c.lights_on'), n == null ? noData() : String(n), n == null ? 'na' : ''));
      }
      if (!out.length) out.push(chip('information-outline', t('c.room'), noData(), 'na'));
    }
    return out.join('');
  }

  // ------------------------------------------------------------- views --
  const VIEWS = {};

  VIEWS.home = () => {
    const att = attention();
    const alerts = att.alerts.length
      ? grid(att.alerts.map(alertCard), 2, 1)
      : `<div class="card alert green tile"><div class="ic green">${icon('check-circle')}</div><div><div class="name">${t('a.all_clear')}</div><div class="sub">${t('a.all_clear_d')}</div></div><div></div></div>`;
    const unknownNote = att.unknown ? `<span class="count">${t(att.unknown === 1 ? 'a.unknown_check' : 'a.unknown_checks', { n: att.unknown })}</span>` : '';

    const wxId = 'weather.forecast_home';
    const wx = st(wxId);
    const dayName = (d) => (lang() === 'zh' ? { sun: '周日', mon: '周一', tue: '周二', wed: '周三' } : { sun: 'Sun', mon: 'Mon', tue: 'Tue', wed: 'Wed' })[d];
    const cIc = { partly: 'weather-partly-cloudy', rainy: 'weather-rainy', cloudy: 'weather-cloudy', sunny: 'weather-sunny' };
    const weather = na(wxId)
      ? tile({ ids: wxId, ic: 'weather-cloudy', name: lang() === 'zh' ? '天气' : 'Weather', sub: t('s.no_data'), state: 'na', pill: naPill() })
      : `<div class="card"><div class="wx-top">${icon('weather-cloudy')}<div><div class="big">${wx.a.temperature}°</div>
          <div class="sub">${lang() === 'zh' ? '多云' : 'Cloudy'} · ${lang() === 'zh' ? '湿度' : 'humidity'} ${wx.a.humidity}%</div></div></div>
          <div class="wx-days">${wx.a.forecast.map((f) => `<div>${dayName(f.d)}${icon(cIc[f.c])}<b>${f.hi}°</b> ${f.lo}°</div>`).join('')}</div>${eid(wxId)}</div>`;
    const w = num('sensor.casa_monitored_power');
    const rem = num('sensor.energy_production_today_remaining');
    const nowSec = sec(h2('h.now', 'weather-partly-cloudy') + `<div class="stack">${weather}
      ${tile({ ids: 'sensor.energy_production_today_remaining', ic: 'solar-power', name: lang() === 'zh' ? '今日太阳能' : 'Solar expected today',
        sub: rem == null ? t('s.no_data') : (lang() === 'zh' ? `预计还有 ${fmt(rem)} kWh` : `${fmt(rem)} kWh still forecast`), state: rem == null ? 'na' : 'off' })}</div>`);

    const people = PEOPLE.map((p) => {
      if (na(p.id)) return `<div class="card person na"><div class="avatar">${p.n[0]}</div><div><div class="name">${p.n}</div><div class="sub">${t('s.no_data')}</div></div>${eid(p.id)}</div>`;
      const home = st(p.id).s === 'home';
      const where = home ? t('s.home') : (st(p.id).a?.zone === 'Work' ? (lang() === 'zh' ? '上班' : 'At work') : t('s.away'));
      return `<div class="card person"><div class="avatar ${home ? 'home' : ''}">${p.n[0]}</div><div><div class="name">${p.n}</div><div class="sub">${home ? `<span class="ok">${where}</span>` : where}</div></div>${eid(p.id)}</div>`;
    });
    const occ = 'binary_sensor.bedroom_parents_room_ac_room_occupied';
    const whoSec = sec(h2('h.who', 'account-group') + grid(people, 3, 3) +
      (na(occ) ? '' : tile({ ids: occ, ic: 'motion-sensor', name: t('room.parents'), state: on(occ) ? 'on' : 'off',
        sub: on(occ) ? `${t('s.occupied')} · ${ago(st(occ).ago)}` : `${t('s.quiet')} · ${dur(st(occ).ago || 0)}` })));

    const oneTap = [['evening', 'weather-sunset-down'], ['goodnight', 'weather-night'], ['movie', 'movie-open'], ['alloff', 'lightbulb-off']]
      .map(([k, ic]) => tile({ tag: 'button', action: `data-onetap="${k}"`, ic, name: t('o.' + k), sub: t('o.' + k + '_d'),
        pill: `<span class="pill amber">${t('s.proposed')}</span>`, gap: 'whole-home script required (CR-233)' }));
    const oneTapSec = sec(h2('h.onetap', 'gauge') + grid(oneTap, 4, 2) + foot('o.note'), 'full');

    const roomsSec = sec(h2('h.rooms', 'home') + `<div class="stack">${ROOMS.filter((r) => r.id !== 'backyard' && r.id !== 'guest').map(roomRow).join('')}</div>`);

    const list = st('todo.shopping_list');
    const items = na('todo.shopping_list') ? null : list.a?.items || [];
    const done = UI.done || (UI.done = {});
    const shop = items == null
      ? tile({ ids: 'todo.shopping_list', ic: 'cart', name: t('h.shopping'), sub: t('s.no_data'), state: 'na' })
      : items.length
        ? `<div class="card"><div class="list">${items.map((it, i) => `<div class="li ${done[i] ? 'done' : ''}"><button class="check" type="button" role="checkbox" aria-checked="${!!done[i]}" data-shop="${i}" aria-label="${esc(it)}">${icon('check')}</button><span class="txt">${esc(it)}</span><span></span></div>`).join('')}</div>${eid('todo.shopping_list')}</div>`
        : `<div class="card na"><div class="sub">${t('s.nothing_on_list')}</div></div>`;
    const d = doorsSummary();
    const secSummary = tile({ tag: 'button', action: 'data-go="security"', ids: DOORS.map((x) => x.id), ic: 'shield-home', name: t('h.security'),
      state: !d.known ? 'na' : d.open.length ? 'on' : 'green',
      sub: `${!d.known ? t('s.no_data') : d.open.length ? join(d.open.map((x) => nm(x.n))) + ' ' + t('s.open').toLowerCase() : d.dark ? `${d.known} ${t('s.closed').toLowerCase()} · ${d.dark} ${t('s.no_data').toLowerCase()}` : t('s.all_closed')} · ${t('m.x_of_y', { x: camerasOnline(), y: CAMERAS.length })} ${lang() === 'zh' ? '摄像头在线' : 'cameras online'}` });
    const sideSec = sec(h2('h.shopping', 'cart') + shop + h2('h.security', 'shield-home') + secSummary);

    const energySec = sec(h2('h.energy_now', 'flash') + `<div class="card ${w == null ? 'na' : ''}">
      <div class="tile"><div class="ic ${w == null ? 'grey' : 'amber'}">${icon('flash')}</div><div><div class="name">${lang() === 'zh' ? '已监控负载' : 'Monitored power'}</div>
      <div class="sub">${w == null ? t('s.no_data') : `${fmt(w)} W · ${lang() === 'zh' ? '车库冰柜和 Ray 书桌' : "garage freezer and Ray's desk"}`}</div></div><div></div></div>
      ${w == null ? '' : `<div class="spark" role="img" aria-label="${lang() === 'zh' ? '过去 12 小时的已监控负载（演示）' : 'Monitored load, last 12 hours (demo)'}">${SPARK.map((v) => `<span style="height:${Math.round((v / 180) * 100)}%"></span>`).join('')}</div>
      <div class="spark-axis"><span>−12 h</span><span>${lang() === 'zh' ? '现在' : 'now'}</span></div>`}${eid('sensor.casa_monitored_power')}</div>` +
      wholeHouseTile() + foot('f.monitored'));

    const recentSec = sec(h2('h.recent', 'clock-outline') + recentActivity());

    const boards = NAV.filter(([k]) => k !== 'home').map(([k, ic]) =>
      `<button type="button" class="card" data-go="${k}"><div class="ic">${icon(ic)}</div><div class="name">${t('nav.' + k)}</div></button>`);
    const boardsSec = sec(h2('u.more_boards', 'dots-horizontal') + `<div class="boards">${grid(boards, 3, 2)}</div>`, 'full');

    return `<div class="board b3">${sec(h2('h.attention', 'alert', unknownNote) + alerts, 'full')}
      ${nowSec}${whoSec}${oneTapSec}${roomsSec}${sideSec}${energySec}${recentSec}${boardsSec}</div>`;
  };

  function wholeHouseTile() {
    const house = 'sensor.powerpal_gateway_powerpal_power', day = 'sensor.powerpal_gateway_powerpal_daily_energy';
    const hw = num(house), hd = num(day);
    return tile({ ids: [house, day], ic: 'home', name: lang() === 'zh' ? '电网取电（Powerpal）' : 'Grid import (Powerpal)', state: hw == null ? 'na' : 'on',
      sub: hw == null ? t('s.no_data') : `${fmt(hw, 0)} W${hd == null ? '' : ` · ${lang() === 'zh' ? '今天' : 'today'} ${fmt(hd)} kWh`}`, pill: hw == null ? naPill() : '' });
  }

  function recentActivity() {
    const ev = [
      ['binary_sensor.k_motion_sensor_motion', () => `${t('room.kitchen')} · ${on('binary_sensor.k_motion_sensor_motion') ? t('s.movement_now') : t('s.quiet')}`, 'motion-sensor'],
      ['binary_sensor.bedroom_parents_room_ac_room_occupied', () => `${t('room.parents')} · ${on('binary_sensor.bedroom_parents_room_ac_room_occupied') ? t('s.occupied') : t('s.quiet')}`, 'motion-sensor'],
      ['light.dining', () => `${t('room.dining')} · ${lang() === 'zh' ? '灯' : 'lights'} ${on('light.dining') ? t('s.on').toLowerCase() : t('s.off').toLowerCase()}`, 'lightbulb'],
      ['binary_sensor.living_room_living_hue_hue_sensor_motion', () => `${t('room.living')} · ${t('s.quiet')}`, 'motion-sensor'],
      ['binary_sensor.lg_fridge_door', () => `${t('h.fridge')} · ${lang() === 'zh' ? '门已关闭' : 'door closed'}`, 'fridge'],
      ['binary_sensor.m_contact_sensor_door', () => `${lang() === 'zh' ? '父母房门' : "Parents' door"} · ${t('s.closed').toLowerCase()}`, 'door-closed'],
      ['light.living_room', () => `${t('room.living')} · ${lang() === 'zh' ? '灯' : 'lights'} ${on('light.living_room') ? t('s.on').toLowerCase() : t('s.off').toLowerCase()}`, 'lightbulb'],
      ['person.vinh_du', () => `Vinh · ${st('person.vinh_du').s === 'home' ? (lang() === 'zh' ? '到家' : 'arrived home') : (lang() === 'zh' ? '离开' : 'left')}`, 'account'],
      ['person.ai_q_huang', () => `Ai · ${lang() === 'zh' ? '离开' : 'left'}`, 'account'],
      ['binary_sensor.b_contact_sensor_door', () => `${lang() === 'zh' ? '后门' : 'Back door'} · ${t('s.open').toLowerCase()}`, 'door-open'],
    ].filter(([id]) => !na(id) && st(id).ago != null).sort((a, b) => st(a[0]).ago - st(b[0]).ago).slice(0, 6);
    if (!ev.length) return `<div class="card na"><div class="sub">${t('s.no_data')}</div></div>`;
    return `<div class="card"><div class="list">${ev.map(([id, f, ic]) =>
      `<div class="li"><span class="ic" style="width:32px;height:32px;font-size:17px">${icon(ic)}</span><span>${f()}${eid(id)}</span><span class="when">${ago(st(id).ago)}</span></div>`).join('')}</div></div>`;
  }

  VIEWS.rooms = () => `<div class="board">${sec(h2('u.all_rooms', 'home') + `<div class="grid" style="--cols:2;--cols-sm:1">${ROOMS.map(roomRow).join('')}</div>`, 'full')}</div>`;

  function roomView(r) {
    const parts = [];
    if (r.lights) parts.push(sec(h2('h.lights', 'lightbulb') + grid(r.lights.map(lightTile), 2, 1)));
    else if (r.lightsGap) parts.push(sec(h2('h.lights', 'lightbulb') + tile({ ic: 'lightbulb-off', name: t('h.lights'), sub: t(r.lightsGap), state: 'na', gap: 'no kitchen light entity' })));
    const air = [];
    (r.air || []).forEach((a) => air.push(a.kind === 'ac' ? acCard(a.id) : purifierTile(a)));
    if (r.temp) {
      const v = num(r.temp);
      air.push(tile({ ids: [r.temp, r.hum], ic: 'thermometer', name: lang() === 'zh' ? '温度' : 'Temperature', state: v == null ? 'na' : 'off',
        sub: v == null ? t('s.no_data') : `${fmt(v)}°${r.hum && num(r.hum) != null ? ` · ${lang() === 'zh' ? '湿度' : 'humidity'} ${num(r.hum)}%` : ''}` }));
    } else if (r.tempGap) air.push(tile({ ic: 'thermometer', name: lang() === 'zh' ? '温度' : 'Temperature', sub: t(r.tempGap), state: 'na', gap: 'no temperature sensor in room' }));
    if (r.cover) air.push(coverTile(r.cover));
    if (air.length) parts.push(sec(h2('h.air', 'fan') + `<div class="stack">${air.join('')}</div>`));
    if (r.motion || r.door) {
      const s = [];
      if (r.motion) s.push(motionTile(r.motion, t('h.movement')));
      if (r.door) s.push(doorTile({ id: r.door, n: { en: 'Door', zh: '门' } }));
      parts.push(sec(h2('h.sensors', 'motion-sensor') + `<div class="stack">${s.join('')}</div>`));
    }
    if (r.fridge) {
      const tv = num(r.fridge.temp);
      const door = r.fridge.door;
      parts.push(sec(h2('h.fridge', 'fridge') + `<div class="stack">
        ${tile({ ids: r.fridge.temp, ic: 'fridge', name: 'Electrolux', sub: tv == null ? t('s.no_data') : `${fmt(tv)}°`, state: tv == null ? 'na' : 'off' })}
        ${na(door) ? tile({ ids: door, ic: 'fridge', name: 'LG', sub: t('s.no_data'), state: 'na' }) : tile({ ids: door, ic: 'fridge', name: lang() === 'zh' ? 'LG 门' : 'LG door', state: on(door) ? 'on' : 'green', sub: `${on(door) ? t('s.open') : t('s.closed')} · ${ago(st(door).ago)}` })}
      </div>` + foot('f.fridge_ids')));
    }
    if (r.media) parts.push(sec(h2('h.media', 'television') + `<div class="stack">${r.media.map(mediaTile).join('')}</div>`));
    if (r.power) parts.push(sec(h2('h.power', 'power-socket-au') + grid(r.power.map(plugTile), r.power.length > 1 ? 2 : 1, 1) + (r.note === 'f.freezer' ? foot('f.freezer') : '')));
    if (r.feeder) parts.push(sec(h2('h.feeder', 'paw') + camTile({ id: r.feeder, n: { en: 'Pet feeder', zh: '喂食器' }, ic: 'paw' })));
    if (r.scenes) parts.push(sec(h2('h.scenes', 'palette') + grid(r.scenes.map(sceneBtn), 3, 2), 'full'));
    if (r.note === 'f.backyard') parts.push(sec(foot('f.backyard'), 'full'));
    // A lone half-width section would leave half a row empty; widen the last one.
    const halves = parts.filter((p) => !p.includes('sec  full') && !p.includes('sec full'));
    if (halves.length % 2 === 1) {
      const last = halves[halves.length - 1];
      parts[parts.indexOf(last)] = last.replace('class="sec "', 'class="sec full"');
    }
    return `<div class="board">${parts.join('')}</div>`;
  }

  VIEWS.security = () => {
    const doors = sec(h2('h.doors', 'door-closed') + grid(DOORS.map(doorTile), 3, 1), 'full');
    const live = CAMERAS.filter((c) => !na(c.id));
    const dead = CAMERAS.filter((c) => na(c.id));
    const cams = sec(h2('h.cameras', 'cctv', `<span class="count">${t('m.x_of_y', { x: live.length, y: CAMERAS.length })}</span>`) +
      grid(live.map(camTile), 2, 1) + (dead.length ? grid(dead.map(camTile), 2, 1) : '') + foot('f.c420'));
    const moves = [
      ['binary_sensor.living_room_living_hue_hue_sensor_motion', 'room.living'],
      ['binary_sensor.k_motion_sensor_motion', 'room.kitchen'],
      ['binary_sensor.living_room_living_room_motion', 'room.dining'],
      ['binary_sensor.bedroom_motion_sensor_motion', 'room.parents'],
    ].map(([id, n]) => motionTile(id, t(n)));
    const emerg = [
      ['event.master_bedroom_emergency_button_dad_main', 'binary_sensor.emergency_button_dad_cloud_connection', { en: "Dad's button", zh: '爸爸的按钮' }],
      ['event.master_bedroom_emergency_button_mum_main', 'binary_sensor.emergency_button_mum_cloud_connection', { en: "Mum's button", zh: '妈妈的按钮' }],
    ].map(([ev, link, n]) => {
      if (na(link)) return tile({ ids: [ev, link], ic: 'bell-ring', name: nm(n), sub: t('s.no_data'), state: 'na', pill: naPill() });
      if (na(ev)) return `<div class="card alert tile"><div class="ic red">${icon('bell-ring')}</div><div><div class="name">${nm(n)}</div><div class="sub">${lang() === 'zh' ? '已连接，但按下后没有记录' : 'Connected, press not registering'}</div></div><div></div>${eid([ev, link])}</div>`;
      return tile({ ids: [ev, link], ic: 'bell-ring', name: nm(n), sub: t('s.connected'), state: 'green' });
    });
    const side = sec(h2('h.movement', 'motion-sensor') + `<div class="stack">${moves.join('')}</div>` + h2('h.emergency', 'bell-ring') + `<div class="stack">${emerg.join('')}</div>`);
    const sirens = [['siren.tapo_c425_north_wall_siren', { en: 'North wall siren', zh: '北墙警报器' }], ['siren.tapo_c200_stockroom_siren', { en: 'Stockroom siren', zh: '储藏室警报器' }], ['siren.tapo_h200', { en: 'Tapo hub siren', zh: 'Tapo 网关警报器' }]]
      .map(([id, n]) => na(id) ? tile({ ids: id, ic: 'alarm-light', name: nm(n), sub: t('s.no_data'), state: 'na', pill: naPill() })
        : tile({ ids: id, ic: 'alarm-light', name: nm(n), sub: on(id) ? `<span class="bad">${t('s.on')}</span>` : t('s.off'), pill: `<span class="pill">${t('s.demo_only')}</span>` }));
    const sirenSec = sec(h2('h.sirens', 'alarm-light') + grid(sirens, 3, 1) + foot('f.sirens'), 'full');
    return `<div class="board">${doors}${cams}${side}${sirenSec}</div>`;
  };

  VIEWS.energy = () => {
    const inv = 'sensor.primo_5_0_1_1_ac_power';
    const invCard = na(inv)
      ? tile({ ids: [inv, 'binary_sensor.casa_solar_online'], ic: 'solar-power', name: t('a.solar'), sub: 'Fronius Primo 5.0-1', state: 'na', pill: naPill() })
      : tile({ ids: inv, ic: 'solar-power', name: lang() === 'zh' ? '太阳能发电' : 'Solar now', sub: `${fmt(num(inv), 0)} W`, state: 'on' });
    const kwh = (id, name) => { const v = num(id); return tile({ ids: id, ic: 'solar-power', name, sub: v == null ? t('s.no_data') : `${fmt(v)} kWh`, state: v == null ? 'na' : 'off' }); };
    const peak = 'sensor.power_highest_peak_time_today';
    const solar = sec(h2('h.solar', 'solar-power') + `<div class="stack">${invCard}
      ${grid([kwh('sensor.energy_production_today', t('c.forecast')), kwh('sensor.energy_production_tomorrow', lang() === 'zh' ? '明天' : 'Tomorrow')], 2, 2)}
      ${tile({ ids: peak, ic: 'clock-outline', name: lang() === 'zh' ? '最佳用电时段' : 'Best time for appliances', sub: na(peak) ? t('s.no_data') : `${lang() === 'zh' ? '今天' : 'Today'} ${st(peak).s}`, state: na(peak) ? 'na' : 'off' })}
      </div>` + foot('f.solarnet'));
    const plugs = [room('garage').power[0], room('ray').power[0]].map((p) => {
      const w = num(p.w), v = num(p.w.replace('current_consumption', 'voltage'));
      if (na(p.id) || w == null) return tile({ ids: [p.id, p.w], ic: 'power-socket-au', name: nm(p.n), sub: t('s.no_data'), state: 'na', pill: naPill() });
      return tile({ ids: [p.w, p.w.replace('current_consumption', 'voltage')], ic: p.ic || 'power-socket-au', name: nm(p.n), sub: `${fmt(w)} W${v == null ? '' : ` · ${fmt(v)} V`}`, state: 'on' });
    });
    const using = sec(h2('h.using', 'flash') + `<div class="stack">${wholeHouseTile()}${plugs.join('')}</div>` + foot('f.monitored'));
    const co = num('sensor.electricity_maps_co2_intensity'), ff = num('sensor.electricity_maps_grid_fossil_fuel_percentage');
    const month = sec(h2('h.month', 'calendar') + grid([
      statCard(num('sensor.g_monitor_freezer_p110m_this_month_s_consumption') == null ? null : fmt(num('sensor.g_monitor_freezer_p110m_this_month_s_consumption')), 'kWh', lang() === 'zh' ? '车库冰柜' : 'Garage freezer', 'sensor.g_monitor_freezer_p110m_this_month_s_consumption'),
      statCard(num('sensor.r_energy_monitor_p110m_this_month_s_consumption') == null ? null : fmt(num('sensor.r_energy_monitor_p110m_this_month_s_consumption')), 'kWh', lang() === 'zh' ? 'Ray 书桌' : "Ray's desk", 'sensor.r_energy_monitor_p110m_this_month_s_consumption'),
    ], 2, 2) + h2('h.grid', 'leaf') + tile({ ids: ['sensor.electricity_maps_co2_intensity', 'sensor.electricity_maps_grid_fossil_fuel_percentage'], ic: 'leaf', name: t('c.carbon'),
      sub: co == null ? t('s.no_data') : `${fmt(co, 0)} g/kWh${ff == null ? '' : ` · ${lang() === 'zh' ? '化石燃料' : 'fossil'} ${fmt(ff, 0)}%`}`, state: co == null ? 'na' : 'off' }) +
      `<p class="foot">${lang() === 'zh' ? '尚无电费金额：成本数据在 Home Assistant 能源面板中有误（CFG-001），修复前不显示金额。' : 'No electricity cost yet. The cost figure on the Home Assistant Energy panel is wrong (CFG-001), so no dollar amount is shown until it is fixed.'}</p>`);
    return `<div class="board">${solar}${using}${month}${sec(h2('h.solar', 'fire').replace(t('h.solar'), lang() === 'zh' ? '燃气' : 'Gas') + tile({ ids: 'input_number.gas_bill_mj', ic: 'fire', name: lang() === 'zh' ? '上期账单燃气用量' : 'Gas on last bill', sub: num('input_number.gas_bill_mj') == null ? t('s.no_data') : `${fmt(num('input_number.gas_bill_mj'), 0)} MJ` }))}</div>`;
  };

  VIEWS.climate = () => {
    const temps = ROOMS.filter((r) => r.temp || r.tempGap).map((r) => {
      if (r.tempGap) return tile({ ic: 'thermometer', name: t(r.n), sub: t(r.tempGap), state: 'na', gap: 'no temperature sensor in room' });
      const v = num(r.temp);
      return tile({ tag: 'button', action: `data-go="room-${r.id}"`, ids: r.temp, ic: r.ic, name: t(r.n), sub: v == null ? t('s.no_data') : `${fmt(v)}°`, state: v == null ? 'na' : 'off' });
    });
    return `<div class="board">
      ${sec(h2('h.temps', 'thermometer') + grid(temps, 2, 2))}
      ${sec(h2('h.ac', 'snowflake') + acCard('climate.bedroom_parents_room_ac'))}
      ${sec(h2('h.air', 'air-purifier') + purifierTile(room('living').air[0]))}
      ${sec(h2('h.fridge', 'fridge') + tile({ ids: ['number.lg_fridge_fridge_temperature', 'number.lg_fridge_freezer_temperature'], ic: 'fridge', name: lang() === 'zh' ? 'LG 设定温度' : 'LG set points',
        sub: `${lang() === 'zh' ? '冷藏' : 'Fridge'} ${num('number.lg_fridge_fridge_temperature') ?? '—'}° · ${lang() === 'zh' ? '冷冻' : 'freezer'} ${num('number.lg_fridge_freezer_temperature') ?? '—'}°` }))}
    </div>`;
  };

  VIEWS.lighting = () => {
    const rooms = ROOMS.filter((r) => r.lights);
    const n = lightsOn();
    const bar = tile({ tag: 'button', action: 'data-onetap="alloff"', ic: 'lightbulb-off', name: t('o.alloff'), sub: n == null ? t('s.no_data') : t('m.lights_on', { n }),
      pill: `<span class="pill amber">${t('s.proposed')}</span>`, gap: 'whole-home script required (CR-233)' });
    return `<div class="board">${sec(bar, 'full')}${rooms.map((r) => sec(`<h2>${icon(r.ic)}<span>${t(r.n)}</span></h2>` + grid(r.lights.map(lightTile), 2, 1))).join('')}</div>`;
  };

  VIEWS.media = () => `<div class="board">${sec(h2('h.tvs', 'television') + grid(Object.keys(MEDIA_NAMES).map(mediaTile), 2, 1), 'full')}</div>`;

  VIEWS.people = () => {
    const cards = PEOPLE.map((p) => {
      if (na(p.id)) return tile({ ids: [p.id, p.bat], ic: 'account', name: p.n, sub: t('s.no_data'), state: 'na', pill: naPill() });
      const home = st(p.id).s === 'home';
      const b = num(p.bat);
      return tile({ ids: [p.id, p.bat], ic: 'account', name: p.n, state: home ? 'green' : 'off',
        sub: `${home ? t('s.home') : (st(p.id).a?.zone === 'Work' ? (lang() === 'zh' ? '上班' : 'At work') : t('s.away'))} · ${ago(st(p.id).ago)} · ${icon('cellphone')} ${b == null ? t('s.no_data') : b + '%'}` });
    });
    const g = 'input_boolean.guest_mode';
    const guest = `<div class="card"><div class="switch-row"><span>${lang() === 'zh' ? '访客模式' : 'Guest mode'}</span><button type="button" class="toggle" role="switch" aria-checked="${on(g)}" data-toggle="${g}" aria-label="${lang() === 'zh' ? '访客模式' : 'Guest mode'}"></button></div>${eid(g)}</div>`;
    const ipad = num('sensor.raymonds_ipad_battery_level');
    return `<div class="board">${sec(h2('h.people', 'account-group') + `<div class="stack">${cards.join('')}</div>`)}
      ${sec(h2('h.devices', 'tablet') + `<div class="stack">${guest}${tile({ ids: 'sensor.raymonds_ipad_battery_level', ic: 'tablet', name: lang() === 'zh' ? 'Raymond 的 iPad' : "Raymond's iPad", sub: ipad == null ? t('s.no_data') : `${ipad}%`, state: ipad == null ? 'na' : 'off' })}</div>`)}</div>`;
  };

  VIEWS.bills = () => {
    const row = (b) => {
      const s = billState(b);
      const amt = num(b.amt);
      const d = dueIn(b.due);
      const when = s === 'na' ? t('s.no_data') : s === 'paid' ? t('s.paid') : s === 'nodue' ? t('s.no_due') : `${s === 'overdue' ? `<span class="bad">${t('s.overdue')}</span>` : t('s.due')} · ${dayLabel(d)}`;
      const pill = s === 'overdue' ? `<span class="pill red">${t('s.overdue')}</span>` : s === 'paid' ? `<span class="pill green">${t('s.paid')}</span>` : s === 'nodue' ? `<span class="pill">${t('s.no_data')}</span>` : '';
      return `<div class="card tile ${s === 'na' ? 'na' : ''}"><div class="ic ${s === 'overdue' ? 'red' : s === 'paid' ? 'green' : ''}">${icon(b.ic)}</div>
        <div><div class="name">${nm(b.n)}${amt ? ` · ${money(amt)}` : ''}</div><div class="sub">${when}</div></div><div>${pill}</div>
        ${s === 'na' ? '' : `<div class="feature"><button type="button" class="btn" data-toggle="${b.paid}">${s === 'paid' ? t('u.mark_unpaid') : t('u.mark_paid')}</button></div>`}
        ${eid([b.paid, b.amt, b.due])}</div>`;
    };
    const unpaid = BILLS.filter((b) => ['due', 'overdue', 'nodue'].includes(billState(b)));
    const paid = BILLS.filter((b) => billState(b) === 'paid');
    const ytd = grid([
      statCard(num('input_number.bills_paid_ytd') == null ? null : money(num('input_number.bills_paid_ytd')), '', lang() === 'zh' ? '今年已付' : 'Paid this year', 'input_number.bills_paid_ytd'),
      statCard(num('input_number.bills_saved_ytd') == null ? null : money(num('input_number.bills_saved_ytd')), '', lang() === 'zh' ? '今年节省' : 'Saved this year', 'input_number.bills_saved_ytd'),
    ], 2, 2);
    return `<div class="board">${sec(h2('h.unpaid', 'receipt-text') + `<div class="stack">${unpaid.map(row).join('') || `<div class="card"><div class="sub">—</div></div>`}</div>` + foot('f.bills'))}
      ${sec(h2('h.ytd', 'cash-multiple') + ytd + h2('h.paid', 'check-circle') + `<div class="stack">${paid.map(row).join('')}</div>`)}</div>`;
  };

  VIEWS.health = () => {
    const ups = [['update.home_assistant_core_update', 'Core'], ['update.home_assistant_operating_system_update', 'OS'], ['update.home_assistant_supervisor_update', 'Supervisor']].map(([id, n]) => {
      if (na(id)) return tile({ ids: id, ic: 'update', name: n, sub: t('s.no_data'), state: 'na' });
      const a = st(id).a;
      return tile({ ids: id, ic: 'update', name: n, state: on(id) ? 'on' : 'green', sub: on(id) ? `<span class="hl">${t('s.update_available')}</span> · ${a.installed} → ${a.latest}` : `${t('s.up_to_date')} · ${a.installed}` });
    });
    const bk = 'sensor.backup_last_successful_automatic_backup';
    ups.push(tile({ ids: bk, ic: 'database', name: t('c.backup'), sub: na(bk) ? t('s.no_data') : (lang() === 'zh' ? st(bk).s.replace('Today', '今天') : st(bk).s), state: na(bk) ? 'na' : 'green' }));
    const wan = 'binary_sensor.eero_wan_status', hub = 'binary_sensor.matter_zigbee_hub_problem', off = 'sensor.casa_offline_devices';
    const net = [
      na(wan) ? tile({ ids: wan, ic: 'wifi', name: 'eero WAN', sub: t('s.no_data'), state: 'na' }) : tile({ ids: wan, ic: on(wan) ? 'wifi' : 'wifi-off', name: 'eero WAN', sub: on(wan) ? t('s.connected') : t('s.offline'), state: on(wan) ? 'green' : 'red' }),
      na(hub) ? tile({ ids: hub, ic: 'router-wireless', name: 'Matter / Zigbee hub', sub: t('s.no_data'), state: 'na' }) : tile({ ids: hub, ic: 'router-wireless', name: 'Matter / Zigbee hub', sub: on(hub) ? (lang() === 'zh' ? '有问题' : 'Problem reported') : (lang() === 'zh' ? '正常' : 'Normal'), state: on(hub) ? 'red' : 'green' }),
      tile({ ids: off, ic: 'circle-off-outline', name: lang() === 'zh' ? '离线实体' : 'Offline entities', sub: num(off) == null ? t('s.no_data') : String(num(off)), state: num(off) == null ? 'na' : 'off' }),
    ];
    const bats = BATTERIES.map((b) => {
      const v = num(b.id);
      return tile({ ids: b.id, ic: v != null && v < 25 ? 'battery-alert' : 'battery-50', name: nm(b.n), sub: v == null ? t('s.no_data') : `${v}%`, state: v == null ? 'na' : v < 25 ? 'red' : 'off' });
    });
    return `<div class="board">${sec(h2('h.updates', 'update') + `<div class="stack">${ups.join('')}</div>`)}
      ${sec(h2('h.network', 'router-wireless') + `<div class="stack">${net.join('')}</div>` + foot('f.offline'))}
      ${sec(h2('h.batteries', 'battery-50') + grid(bats, 3, 1), 'full')}</div>`;
  };

  // ------------------------------------------------------------- render --
  function titleFor(route) {
    if (route.startsWith('room-')) return t(room(route.slice(5)).n);
    return route === 'home' ? 'CasaRay' : t('nav.' + route);
  }
  function renderShell() {
    const L = lang();
    document.documentElement.lang = L === 'zh' ? 'zh-Hans' : 'en';
    const current = UI.route.startsWith('room-') ? 'rooms' : UI.route;
    const navBtn = ([k, ic]) => `<button type="button" class="nav-btn" data-go="${k}" ${current === k ? 'aria-current="page"' : ''}>${icon(ic)}<span>${t('nav.' + k)}</span></button>`;
    $('#rail').innerHTML = `<div class="mark">Casa<b>Ray</b></div>${NAV.map(navBtn).join('')}`;
    const moreActive = !TABS.includes(current);
    $('#tabbar').innerHTML = NAV.filter(([k]) => TABS.includes(k)).map(navBtn).join('') +
      `<button type="button" class="nav-btn" data-overlay="more" ${moreActive ? 'aria-current="page"' : ''}>${icon('dots-horizontal')}<span>${t('nav.more')}</span></button>`;
    const back = UI.route.startsWith('room-') ? `<button type="button" class="back-btn" data-go="rooms" aria-label="${t('u.back')}">${icon('chevron-left')}</button>` : '';
    const themeIc = { auto: 'theme-light-dark', light: 'white-balance-sunny', dark: 'weather-night' }[UI.theme];
    $('#topbar').innerHTML = `<div class="title">${back}<h1>${esc(titleFor(UI.route))}</h1></div>
      <span class="demo-pill" title="${esc(t('app.demo_long'))}">${icon('flask-outline')}${t('app.demo')}</span>
      <div class="spacer"></div>
      <div class="tools">
        <button type="button" class="tool" data-lang aria-label="${t('u.language')}">${icon('translate')}<span>${L === 'zh' ? 'EN' : '中文'}</span></button>
        <button type="button" class="tool" data-theme-cycle aria-label="${t('u.theme')}: ${t('u.' + UI.theme)}">${icon(themeIc)}<span class="lbl-md">${t('u.' + UI.theme)}</span></button>
        <button type="button" class="tool" data-overlay="demo" aria-label="${t('u.demo_panel')}" aria-pressed="${UI.overlay === 'demo'}">${icon('tune')}<span class="lbl-md hide-md">${t('u.demo_panel')}</span></button>
      </div>
      <div class="clock" id="clock"></div>`;
    tick();
  }
  function tick() {
    const el = $('#clock');
    if (!el) return;
    const d = new Date();
    const hh = d.getHours(), mm = String(d.getMinutes()).padStart(2, '0');
    const time = lang() === 'zh' ? `${String(hh).padStart(2, '0')}:${mm}` : `${hh % 12 || 12}:${mm} ${hh < 12 ? 'am' : 'pm'}`;
    const date = `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getFullYear()).slice(2)}`;
    el.innerHTML = `<div class="t">${time}</div><div class="d">${date}</div>`;
  }
  function renderOverlay() {
    const slot = $('#overlay');
    if (!UI.overlay) { slot.innerHTML = ''; return; }
    if (UI.overlay === 'demo') {
      const sc = [['evening', 'u.sc_evening'], ['away', 'u.sc_away'], ['outage', 'u.sc_outage']];
      slot.innerHTML = `<div class="scrim" data-close><div class="sheet" role="dialog" aria-modal="true" aria-labelledby="demo-h">
        <h3 id="demo-h">${t('u.demo_panel')}<button type="button" class="back-btn" data-close aria-label="${t('u.close')}">${icon('close')}</button></h3>
        <p>${t('app.demo_long')}</p>
        <div><div class="lbl">${t('u.scenario')}</div><div class="seg" role="group">${sc.map(([k, l]) => `<button type="button" data-scenario="${k}" aria-pressed="${UI.scenario === k}">${t(l)}</button>`).join('')}</div></div>
        <div class="switch-row"><span>${t('u.show_ids')}</span><button type="button" class="toggle" role="switch" id="ids-toggle" aria-checked="${UI.ids}" data-ids aria-label="${t('u.show_ids')}"></button></div>
        <div class="switch-row"><span>${t('u.language')}</span><div class="seg" role="group" style="width:160px"><button type="button" data-setlang="en" aria-pressed="${lang() === 'en'}">EN</button><button type="button" data-setlang="zh" aria-pressed="${lang() === 'zh'}">中文</button></div></div>
        <div class="switch-row"><span>${t('u.theme')}</span><div class="seg" role="group" style="width:240px">${['auto', 'light', 'dark'].map((k) => `<button type="button" data-settheme="${k}" aria-pressed="${UI.theme === k}">${t('u.' + k)}</button>`).join('')}</div></div>
        <button type="button" class="btn" data-reset>${t('u.reset')}</button>
      </div></div>`;
    } else if (UI.overlay === 'more') {
      slot.innerHTML = `<div class="scrim" data-close><div class="sheet" role="dialog" aria-modal="true" aria-labelledby="more-h">
        <h3 id="more-h">${t('u.more_boards')}<button type="button" class="back-btn" data-close aria-label="${t('u.close')}">${icon('close')}</button></h3>
        <div class="boards">${grid(NAV.filter(([k]) => !TABS.includes(k)).map(([k, ic]) => `<button type="button" class="card" data-go="${k}"><div class="ic">${icon(ic)}</div><div class="name">${t('nav.' + k)}</div></button>`), 2, 2)}</div>
      </div></div>`;
    }
  }
  function render() {
    applyTheme();
    document.body.classList.toggle('show-ids', UI.ids);
    renderShell();
    $('#chips').innerHTML = chipsFor(UI.route);
    const r = UI.route;
    $('#view').innerHTML = r.startsWith('room-') ? roomView(room(r.slice(5))) : VIEWS[r]();
    renderOverlay();
  }
  function applyTheme() {
    const root = document.documentElement;
    if (UI.theme === 'auto') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', UI.theme);
  }

  let toastTimer;
  function toast(msg) {
    $('#toast-slot').innerHTML = `<div class="toast">${msg}</div>`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { $('#toast-slot').innerHTML = ''; }, 3200);
  }

  // --------------------------------------------------------- scenarios --
  function loadScenario(name) {
    const keepLang = S['input_boolean.chinese_dashboard'];
    S = clone(window.DEMO_STATES);
    const patch = window.SCENARIOS[name];
    if (patch === '__all_devices_unavailable__') {
      for (const id of Object.keys(S)) if (!window.OUTAGE_SURVIVORS.test(id)) S[id] = { s: 'unavailable' };
    } else Object.assign(S, clone(patch || {}));
    if (keepLang) S['input_boolean.chinese_dashboard'] = keepLang;
    UI.done = {};
  }

  // ------------------------------------------------------------ routing --
  const VALID = new Set([...NAV.map(([k]) => k), ...ROOMS.map((r) => 'room-' + r.id)]);
  function go(route, push = true) {
    if (!VALID.has(route)) route = 'home';
    UI.route = route;
    UI.overlay = null;
    if (push && location.hash !== '#' + route) history.pushState(null, '', '#' + route);
    render();
    window.scrollTo({ top: 0 });
  }
  window.addEventListener('popstate', () => go((location.hash || '#home').slice(1), false));
  window.addEventListener('hashchange', () => go((location.hash || '#home').slice(1), false));

  // ------------------------------------------------------------- events --
  function toggleEntity(id) {
    const s = st(id);
    if (na(id)) return;
    const domain = id.split('.')[0];
    if (domain === 'media_player') s.s = ['on', 'playing'].includes(s.s) ? 'off' : 'on';
    else s.s = s.s === 'on' ? 'off' : 'on';
    s.ago = 0;
    if (domain === 'light' && s.s === 'on') { s.a = s.a || {}; if (!s.a.brightness) s.a.brightness = 70; }
    if (domain === 'fan') { s.a = s.a || {}; s.a.speed = s.s === 'on' ? (s.a.speed && s.a.speed !== 'off' ? s.a.speed : 'low') : 'off'; }
    const quiet = domain === 'input_boolean' && id.includes('bill');
    if (!quiet) toast(t('t.demo', { what: t('t.toggled', { name: id.split('.')[1].replace(/_/g, ' '), state: s.s === 'off' ? t('s.off').toLowerCase() : t('s.on').toLowerCase() }) }));
  }
  const ONETAP = {
    evening: () => { ['light.living_room', 'light.dining'].forEach((i) => { if (!na(i)) { S[i].s = 'on'; S[i].a.brightness = 60; S[i].ago = 0; } }); },
    goodnight: () => {
      LIGHTS.forEach((i) => { if (!na(i)) { S[i].s = 'off'; S[i].ago = 0; } });
      Object.keys(MEDIA_NAMES).forEach((i) => { if (!na(i)) S[i].s = 'off'; });
      const c = 'cover.aqara_roller_shade_driver_e1'; if (!na(c)) { S[c].s = 'closed'; S[c].a.position = 0; }
    },
    movie: () => { if (!na('light.living_room')) { S['light.living_room'].s = 'on'; S['light.living_room'].a.brightness = 20; } const tv = 'media_player.living_room_tv_samsung_q9_series_65'; if (!na(tv)) S[tv].s = 'on'; },
    alloff: () => { LIGHTS.forEach((i) => { if (!na(i)) { S[i].s = 'off'; S[i].ago = 0; } }); },
  };

  document.addEventListener('click', (e) => {
    const el = e.target.closest('button, [data-close]');
    if (!el) return;
    const d = el.dataset;
    if ('close' in d && (el === e.target || el.tagName === 'BUTTON')) { UI.overlay = null; renderOverlay(); renderShell(); return; }
    if (d.go) return go(d.go);
    if (d.overlay) { UI.overlay = UI.overlay === d.overlay ? null : d.overlay; renderOverlay(); renderShell(); return; }
    if ('lang' in d) { S['input_boolean.chinese_dashboard'].s = lang() === 'zh' ? 'off' : 'on'; return render(); }
    if (d.setlang) { S['input_boolean.chinese_dashboard'].s = d.setlang === 'zh' ? 'on' : 'off'; return render(); }
    if ('themeCycle' in d) { UI.theme = { auto: 'light', light: 'dark', dark: 'auto' }[UI.theme]; store.set('theme', UI.theme); return render(); }
    if (d.settheme) { UI.theme = d.settheme; store.set('theme', UI.theme); return render(); }
    if ('ids' in d) { UI.ids = !UI.ids; store.set('ids', UI.ids); return render(); }
    if (d.scenario) {
      UI.scenario = d.scenario; store.set('scenario', UI.scenario); loadScenario(UI.scenario); render();
      return toast(t('t.scenario', { name: t('u.sc_' + d.scenario) }));
    }
    if ('reset' in d) { UI.scenario = 'evening'; store.set('scenario', 'evening'); S = {}; loadScenario('evening'); UI.overlay = null; return render(); }
    if (d.toggle) { toggleEntity(d.toggle); return render(); }
    if (d.scene) { return toast(t('t.demo', { what: t('t.scene', { name: d.name }) })); }
    if (d.onetap) { ONETAP[d.onetap](); render(); return toast(t('t.demo', { what: t('t.onetap', { name: t('o.' + d.onetap) }) })); }
    if (d.speed) { const s = st(d.speed); s.a.speed = d.v; s.s = d.v === 'off' ? 'off' : 'on'; return render(); }
    if (d.ac) { const s = st('climate.bedroom_parents_room_ac'); s.a.target = Math.min(30, Math.max(16, s.a.target + parseFloat(d.ac))); return render(); }
    if (d.acmode) { st('climate.bedroom_parents_room_ac').s = d.acmode; return render(); }
    if (d.shop) { UI.done[d.shop] = !UI.done[d.shop]; return render(); }
  });
  // Sliders: live label while dragging, full render on release.
  document.addEventListener('input', (e) => {
    const el = e.target;
    const id = el.dataset.bright || el.dataset.volume || el.dataset.cover;
    if (!id) return;
    const v = +el.value;
    const lbl = document.querySelector(`[data-bl="${id}"]`);
    if (lbl) lbl.textContent = v + '%';
    const fill = el.parentElement.querySelector('.fill');
    if (fill) fill.style.width = v + '%';
  });
  document.addEventListener('change', (e) => {
    const el = e.target;
    const v = +el.value;
    if (el.dataset.bright) { const s = st(el.dataset.bright); s.a.brightness = v; }
    else if (el.dataset.volume) { const s = st(el.dataset.volume); s.a.volume = v; }
    else if (el.dataset.cover) { const s = st(el.dataset.cover); s.a.position = v; s.s = v > 0 ? 'open' : 'closed'; }
    else return;
    render();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && UI.overlay) { UI.overlay = null; renderOverlay(); renderShell(); } });
  // The OS theme can change under "Auto"; tokens follow on their own.

  // --------------------------------------------------------------- boot --
  S = {};
  loadScenario(UI.scenario);
  UI.route = VALID.has((location.hash || '').slice(1)) ? location.hash.slice(1) : 'home';
  render();
  setInterval(tick, 15000);
  // Exposed for the test harness only.
  window.__casaray = { go, state: () => S, ui: () => UI, attention: () => attention() };
})();
