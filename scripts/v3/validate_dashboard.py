#!/usr/bin/env python3
"""CasaRay V3 offline validation gate.  DEVELOPMENT ONLY — NOT DEPLOYED.

    python3 scripts/v3/validate_dashboard.py      # exit 0 = every check passed

Checks every generated locale dashboard. Nothing here contacts Home
Assistant; a pass means the YAML is structurally sound, its references exist
in the 05/09 export and its templates say honest things offline. It does NOT
mean any card renders on the wall iPad.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_dashboard as B  # noqa: E402
import render_check as R  # noqa: E402
import components as C  # noqa: E402
import ha_layout as L  # noqa: E402

ROOT = B.ROOT
ALLOWED_CUSTOM = {"custom:webrtc-camera"}      # V2's only custom card; carried views only
NATIVE_TYPES = {"heading", "markdown", "tile", "button", "picture-entity",
                "weather-forecast", "todo-list", "history-graph", "media-control"}
# Switches no V3-native view may ever control, whatever the manifest says:
# anything that disables a camera or reduces alerting, and bulb-power wall
# switches (owner rule). Their V2 controls stay on the classic subviews.
PROTECTED_SWITCH = re.compile(
    r"privacy|detection|notification|chime|alarm|siren"   # cameras and alerting
    r"|sensor_enabled"                                     # turning a motion / light sensor off
    r"|child_lock"                                         # a safety lock
    r"|socket_\d"                                          # power-strip sockets: what each powers is not recorded
    r"|climate_react|_ac_timer")                           # air-con behaviour (V3-008)
BULB_POWER = {"switch.mainroomlight_switch_1", "switch.bedroomlight_switch_1",
              "switch.dinning_light_switch_1"}
# Appliance power that is critical (the freezer) or whose load is not recorded
# (kitchen bench plugs, the coffee machine), with the auto-off that can cut it.
CRITICAL_LOADS = {
    "switch.g_monitor_freezer_p110m", "switch.g_monitor_freezer_p110m_auto_off_enabled",
    "switch.k_coffee_p100", "switch.k_coffee_p100_auto_off_enabled",
    "switch.k_top_p100", "switch.k_top_p100_auto_off_enabled",
    "switch.k_bot_p100", "switch.k_bot_p100_auto_off_enabled",
}
# Non-switch settings that reduce what a camera or doorbell can do.
PROTECTED_SETTING = re.compile(r"detection|night_vision|privacy|front_door_volume")
# Home Assistant's own Core / Supervisor / OS updates: an install from a wall
# panel restarts the house system (CR-V3-19).
SYSTEM_UPDATE = re.compile(r"^update\.home_assistant_")


def protected_switch(entity):
    return entity.startswith("switch.") and (bool(PROTECTED_SWITCH.search(entity)) or entity in BULB_POWER
                                             or entity in CRITICAL_LOADS)


def protected_setting(entity):
    return ((entity.split(".")[0] in ("select", "number") and bool(PROTECTED_SETTING.search(entity)))
            or bool(SYSTEM_UPDATE.search(entity)))


def v2_tiles(v2_view, entity):
    return [c for s in v2_view.get("sections", []) for c in walk_cards(s.get("cards", []), True)
            if c.get("type") == "tile" and c.get("entity") == entity]


def acting(card):
    """A tile whose tap or icon tap can change something (not none / navigate / more-info only)."""
    tap, icon = C.effective_tile_actions(card)
    return tap not in ("none", "navigate") or icon not in ("none",)
SENTINEL = re.compile(r"\|\s*float\(\s*(0|100|9999)\s*\)")
SECRET_PATTERNS = [
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT / HA token
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)\b(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9/+_-]{8,}"),
    re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}"),
    re.compile(r"(?i)https?://[a-z0-9.-]+\.(?:duckdns\.org|ui\.nabu\.casa)"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
# Reassurances that must never appear when nothing answered.
DARK_FORBIDDEN_KEYS = ["att.all_clear", "att.clear_partial"]


def reassurance_stem(s):
    """The most distinctive literal part of a reassurance string: its longest
    run between {placeholders}. (The first run alone was 'All' in English,
    which any 'All rooms' label matched.)"""
    return max(re.split(r"\{\w+\}", s), key=lambda x: len(x.strip())).strip()


class Gate:
    def __init__(self):
        self.fail, self.warn, self.passed = [], [], []

    def check(self, ok, name, detail=""):
        (self.passed if ok else self.fail).append(name + (f" — {detail}" if detail and not ok else ""))

    def note(self, msg):
        self.warn.append(msg)


def walk_cards(node, is_card=False):
    """Cards only: follow views/sections/cards/card, never features or actions."""
    if isinstance(node, list):
        for x in node:
            yield from walk_cards(x, is_card)
    elif isinstance(node, dict):
        if is_card and node.get("type") != "grid":
            yield node
        for k in ("views", "sections"):
            if k in node:
                yield from walk_cards(node[k], False)
        for k in ("cards", "card"):
            if k in node:
                yield from walk_cards(node[k], True)


def nav_paths(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "navigation_path" and isinstance(v, str):
                yield v
            else:
                yield from nav_paths(v)
    elif isinstance(node, list):
        for x in node:
            yield from nav_paths(x)


def actions(node):
    if isinstance(node, dict):
        if node.get("action") == "perform-action" or "perform_action" in node:
            yield node
        for v in node.values():
            yield from actions(v)
    elif isinstance(node, list):
        for x in node:
            yield from actions(x)


def unconfirmed_presses(view):
    """Targets of button / input_button presses that do not ask first."""
    return [a.get("target") for a in actions(view)
            if str(a.get("perform_action", "")).startswith(("button.", "input_button."))
            and not (a.get("confirmation") or {}).get("text")]


def tile_safety(view, v2_by_path, controls, old_url, new_url):
    """(problems, protected_controls) for one native view's tiles.

    climate / camera tiles must be read-only; a siren tile may act only if it
    IS the V2 tile for that entity on the same V2 view (byte for byte, links
    rewritten); a switch may act only if it is in manifest `controls`, not a
    protected class, and behaves exactly like its tile on the named V2 view."""
    v2v = v2_by_path.get(view["path"], {})
    bad, prot = [], []
    for c in walk_cards(view):
        if c.get("type") != "tile":
            continue
        e = c["entity"]
        dom = e.split(".")[0]
        if (protected_switch(e) or protected_setting(e)) and acting(c):
            prot.append(e)
        if dom not in ("switch", "input_boolean", "climate", "siren", "camera") or not acting(c):
            continue
        if dom == "siren":
            if c not in [B.rewrite_links(x, old_url, new_url) for x in v2_tiles(v2v, e)]:
                bad.append(e + " (siren tile differs from V2)")
        elif dom in ("switch", "input_boolean"):   # a helper toggle is gated like a switch
            ctl = controls.get(e)
            src = v2_tiles(v2_by_path.get((ctl or {}).get("v2_view"), {}), e)
            if protected_switch(e):
                bad.append(e + " (protected class)")
            elif not ctl:
                bad.append(e + " (not in manifest controls)")
            elif not any(C.effective_tile_actions(x) == C.effective_tile_actions(c) for x in src):
                bad.append(e + " (behaves differently from its V2 tile)")
        else:
            bad.append(e)
    return bad, prot


def band_scenarios():
    """State sets a band must pack under: the fixture, everything answering,
    everything dark. Cards hidden by their visibility take no space."""
    normal, _ = R.scenarios()["normal"]
    return {"fixture": normal,
            "answering": {e: ("idle" if e.startswith("camera.") else "on") for e in normal},
            "dark": R.scenarios()["dark"][0]}


def band_problems(view, spec):
    """For a `band_grid: 24` view, against the frontend's own layout rules
    (ha_layout.py): headings in two-column bands that are not full width (they
    would sit BESIDE their cards), bands that leave empty cells on the wall
    iPad (24 units) or a phone (12) in any band scenario, and cards drawn at a
    size other than the one their grid_options state (a card minimum
    overriding the YAML). The shared top bar is included (and has its own
    gate, topbar_problems, on every native view)."""
    heads, holes, clamps = [], [], []
    scen = band_scenarios()
    for i, s in enumerate(view["sections"]):
        span = s.get("column_span", 1)
        for c in s.get("cards", []):
            if c.get("type") == "heading" and span == 2 and L.effective(c)[0] != "full":
                heads.append(f"section {i}")
            if L.configured(c) != L.effective(c):
                clamps.append(f"section {i} {c['type']} {L.configured(c)} draws {L.effective(c)}")
        for name, states in scen.items():
            for where, resolved in (("wall iPad", 2), ("phone", 1)):
                n = L.section_holes(s, L.units(span, resolved), states)
                if n:
                    holes.append(f"section {i}: {n} empty cells on the {where} ({name})")
    return heads, holes, clamps


def topbar_problems(view):
    """V3-024: the shared top bar on a native view, against the frontend's own
    layout rules (ha_layout.py). Kiosk mode hides Home Assistant's chrome, so
    this bar is the way around the dashboard; a regression here strands a page.

    Checks: the header holds the time above a DD/MM/YY date; the six rail
    destinations, in order, each NAMED and at least 3 units wide (2 units
    clipped labels on a phone); every cell one height; whole rows on the wall
    iPad (24 units) and a phone (12); on a rail destination exactly one button
    inert and tinted (the current page), elsewhere none; every other button
    navigates to its own page."""
    bad = []
    if not view.get("sections"):
        return ["no sections"]
    top = view["sections"][0]
    cards = top.get("cards", [])
    if top.get("column_span") != 2:
        bad.append("top bar is not a two-column band")
    head = cards[0] if cards else {}
    body = head.get("content", "")
    if head.get("type") != "markdown" or not head.get("text_only"):
        bad.append("first card is not the text-only header")
    t, d = body.find("%H:%M"), body.find("%d/%m/%y")
    if t < 0 or d < 0 or t > d or "%Y" in body:
        bad.append("header lacks the time above a DD/MM/YY date")
    btns = [c for c in cards if c.get("type") == "button"]
    paths = [p for p, _, _ in C.RAIL]
    if len(btns) != len(paths) or len(cards) != len(btns) + 1:
        bad.append(f"expected the header and {len(paths)} rail buttons, got {len(cards)} cards")
        return bad
    for p, b in zip(paths, btns):
        if b.get("show_name") is False or not str(b.get("name", "")).strip() or b.get("show_icon") is False:
            bad.append(f"rail {p}: not named, or no icon")
        cols = L.effective(b)[0]
        if not isinstance(cols, int) or cols < 3:
            bad.append(f"rail {p}: {cols} units, under 3")
        tap = b.get("tap_action") or {}
        cur = p == view["path"]
        if cur and (tap != {"action": "none"} or b.get("color") != "accent"):
            bad.append(f"rail {p}: the current page is not inert and tinted")
        if not cur and (tap.get("action") != "navigate" or not str(tap.get("navigation_path", "")).endswith("/" + p)
                        or "color" in b):
            bad.append(f"rail {p}: does not navigate to its own page, or is tinted")
    heights = {L.effective(c)[1] for c in cards}
    if len(heights) != 1:
        bad.append(f"cells of different heights {sorted(map(str, heights))}")
    for units, where in ((24, "wall iPad"), (12, "phone")):
        holes = L.place([L.effective(c) for c in cards], units)[2]
        if holes:
            bad.append(f"{holes} empty cells on the {where}")
    return bad


def band_note(view):
    """What a view not yet on band_grid 24 looks like on the wall iPad."""
    half = sum(1 for i, s in enumerate(view["sections"]) if s.get("column_span", 1) == 2 and i > 0
               for c in s.get("cards", []) if L.effective(c)[0] != "full")
    big = sum(1 for s in view["sections"] for c in s.get("cards", []) if L.configured(c) != L.effective(c))
    return half, big


CJK = re.compile(r"[㐀-鿿]")
LATIN = re.compile(r"[A-Za-z]")
# What the preview's own words claim. None may appear when nothing answered.
PREVIEW_DARK_FORBIDDEN = ["已開", "已關", "在線", "有動靜", "暫無動作", "需要清潔濾網", "暫時唔使清潔",
                          "冇設定定時", "運行中", r"\bOn\b", r"\bOff\b", r"\bOnline\b", "Movement", "No motion",
                          "needs cleaning", "No cleaning needed", "No timer set", "Running"]
PREVIEW_ACTIONS = {"light.turn_on", "light.turn_off"}   # the existing, owner-approved light actions only
# V3-026 (owner, 20/11/26): the preview may also use these custom cards, and the
# native entities card that auto-entities fills; nothing else.
PREVIEW_TYPES = NATIVE_TYPES | {"entities"} | C.PREVIEW_CUSTOM
PREVIEW_ROOT = {"kiosk_mode": {"hide_header", "hide_sidebar"},
                "wallpanel": {"enabled", "hide_toolbar", "hide_sidebar", "fullscreen", "idle_time",
                              "image_url", "cards"}}
READ_ACTIONS = {None, "none", "more-info", "navigate"}
# V3-027: the working dashboards may carry four of the seven, each on its page,
# in a band after the page's native readings, with a note naming what it needs.
WORKING_CUSTOM = dict(C.WORKING_CUSTOM, home={C.CLOCK_WEATHER})
WORKING_INNER = C.WORKING_INNER
PRODUCT = {"custom:power-flow-card-plus": "Power Flow Card Plus", "custom:apexcharts-card": "ApexCharts",
           "custom:auto-entities": "auto-entities", C.CLOCK_WEATHER: "Clock Weather Card"}
# V3-029: the owner put the weather on Home mid-page; the chip strip's Outside reading
# (same entity, native) above it is the fallback, so the band-order rule does not apply
ORDER_EXEMPT = {"home": {C.CLOCK_WEATHER}}
CWC_KEYS = {"type", "entity", "locale", "sections", "grid_options"}
CWC_SEGMENTS = {"icon", "weather", "spacer", "time", "date"}
DATA_TYPES = {"tile", "history-graph", "picture-entity", "weather-forecast", "todo-list", "media-control"}


def loc_t(loc, key):
    """A working string as the generator resolves it: the locale, its fallbacks, then en."""
    for code in [loc["code"]] + list(loc.get("fallback", [])) + ["en"]:
        cat = B.load_yaml(B.SRC / "i18n" / f"{code}.yaml")
        if key in cat:
            return str(cat[key])
    raise KeyError(key)


NAVBAR = C.NAVBAR
# Navbar card options, exactly those used and documented (V3-028)
NAVBAR_KEYS = {"type", "routes", "desktop", "mobile", "layout", "grid_options"}
NAVBAR_ROUTE_KEYS = {"url", "icon", "label", "tap_action", "popup"}
NAVBAR_SUB = {"desktop": {"show_labels"}, "mobile": {"show_labels", "safe_area"}, "layout": {"reflect_child_state"}}


def navbar_problems(view, url_base, paths):
    """V3-028, one native page: exactly one Navbar card, the last card on the page;
    only the documented options it uses; every route and popup item a labelled
    link to a page of this dashboard (or the More route that opens the popup);
    and Home among the routes."""
    bad = []
    bars = [c for c in walk_cards(view) if c.get("type") == NAVBAR]
    if len(bars) != 1:
        return [f"{len(bars)} navbar cards"]
    nb = bars[0]
    last = (view.get("sections") or [{}])[-1].get("cards") or [{}]
    if last[-1] is not nb:
        bad.append("the navbar is not the page's last card")
    if set(nb) - NAVBAR_KEYS:
        bad.append(f"unreviewed options {sorted(set(nb) - NAVBAR_KEYS)}")
    for k, allowed in NAVBAR_SUB.items():
        if set(nb.get(k) or {}) - allowed:
            bad.append(f"{k}: unreviewed options {sorted(set(nb[k]) - allowed)}")

    def link_ok(url):
        part = str(url).strip("/").split("/")
        return len(part) == 2 and part[0] == url_base and part[1] in paths

    urls = []
    for r in nb.get("routes", []):
        if set(r) - NAVBAR_ROUTE_KEYS:
            bad.append(f"route {r.get('label')!r}: unreviewed keys {sorted(set(r) - NAVBAR_ROUTE_KEYS)}")
        if not nonempty(r.get("label", "")) or not str(r.get("icon", "")).startswith("mdi:"):
            bad.append(f"route without a label or an mdi icon: {r}")
        if "popup" in r:
            if r.get("tap_action") != {"action": "open-popup"} or "url" in r:
                bad.append(f"popup route {r.get('label')!r} must open its popup and nothing else")
            for it in r["popup"]:
                if set(it) - {"url", "icon", "label"} or not nonempty(it.get("label", "")) or not link_ok(it.get("url")):
                    bad.append(f"popup item {it}")
                urls.append(it.get("url"))
        else:
            if "tap_action" in r or not link_ok(r.get("url")):
                bad.append(f"route {r}")
            urls.append(r.get("url"))
    if f"/{url_base}/home" not in urls:
        bad.append("no Home route")
    if len(urls) != len(set(urls)):
        bad.append("a destination appears twice")
    return bad


def working_custom_problems(view):
    """V3-027, one working page: the custom types allowed on it and nowhere else;
    each band holding one names it in a note (what the family sees until it is
    installed); and no native reading comes after such a band."""
    bad = []
    allowed = WORKING_CUSTOM.get(view["path"], set())
    secs = view.get("sections", [])
    data_at, custom_at = [], []
    for i, sec in enumerate(secs):
        cards = list(walk_cards(sec.get("cards", []), True))
        customs = {c["type"] for c in cards if str(c.get("type", "")).startswith("custom:")} - {NAVBAR}
        if customs - allowed:
            bad.append(f"section {i}: {sorted(customs - allowed)} not allowed on {view['path']}")
        if customs:
            custom_at.append(i)
            notes = " ".join(c.get("content", "") for c in cards if c.get("type") == "markdown")
            missing = [PRODUCT[t] for t in customs if t in PRODUCT and PRODUCT[t] not in notes]
            if missing:
                bad.append(f"section {i}: no note naming {missing}")
        elif any(c.get("type") in DATA_TYPES for c in cards):
            data_at.append(i)
    exempt = ORDER_EXEMPT.get(view["path"], set())
    custom_at = [i for i in custom_at
                 if not ({c["type"] for c in walk_cards(secs[i].get("cards", []), True)
                          if str(c.get("type", "")).startswith("custom:")} - {NAVBAR}) <= exempt]
    if custom_at and data_at and max(data_at) > min(custom_at):
        bad.append(f"native readings in section {max(data_at)} come after the custom band {min(custom_at)}")
    bad += custom_problems(view, label_ok=nonempty)
    return bad


def nonempty(text):
    return bool(str(text).strip())


def custom_problems(view, label_ok=None):
    """V3-026: what each owner-approved custom card on a page may do. Labels are
    bilingual on the preview; on the working dashboards (V3-027) one language
    per locale, so `label_ok` is just non-empty there."""
    label_ok = label_ok or bilingual
    bad = []
    cards = list(walk_cards(view))
    hashes = {c["hash"] for c in cards if c.get("type") == "custom:bubble-card" and c.get("card_type") == "pop-up"}
    links = {n for n in nav_paths(view) if n.startswith("#")}
    if hashes != links:
        bad.append(f"pop-ups {sorted(hashes)} vs '#' links {sorted(links)}")
    for c in cards:
        t = c.get("type")
        if t == "custom:bubble-card":
            label = c.get("name", "")
            if not label_ok(str(label)):
                bad.append(f"bubble name not bilingual: {label!r}")
            if c.get("card_type") == "pop-up":
                continue
            if c.get("card_type") != "button":
                bad.append(f"bubble card_type {c.get('card_type')!r}")
                continue
            e = str(c.get("entity", ""))
            kind = c.get("button_type", "switch")          # Bubble's default is a switch: it toggles
            if kind == "slider":
                if not e.startswith("light."):
                    bad.append(f"slider on a non-light: {e}")
            elif kind in ("state", "name"):
                acts = [(c.get("tap_action") or {}).get("action"),
                        ((c.get("button_action") or {}).get("tap_action") or {}).get("action")]
                if any(a not in READ_ACTIONS for a in acts):
                    bad.append(f"reading {e} acts: {acts}")
            else:
                bad.append(f"bubble {e}: button_type {kind!r} acts")
            if c.get("sub_button"):
                bad.append(f"bubble {e}: sub-buttons are not reviewed")
        elif t == "custom:advanced-camera-card":
            for cam in c.get("cameras", []):
                if not str(cam.get("camera_entity", "")).startswith("camera."):
                    bad.append(f"acc camera without a camera_entity: {cam}")
                if not label_ok(str(cam.get("title", ""))):
                    bad.append(f"acc title not bilingual: {cam.get('title')!r}")
            if "menu" in c or "ptz" in str(c):
                bad.append("acc menu or PTZ settings are not reviewed")
        elif t == "custom:power-flow-card-plus":
            for k, ent in (c.get("entities") or {}).items():
                if not label_ok(str(ent.get("name", ""))):
                    bad.append(f"power flow {k} name not bilingual")
        elif t == "custom:apexcharts-card":
            for se in c.get("series", []):
                if not label_ok(str(se.get("name", ""))):
                    bad.append(f"apex series name not bilingual: {se.get('name')!r}")
        elif t == C.CLOCK_WEATHER:
            if set(c) - CWC_KEYS:
                bad.append(f"clock weather: unreviewed options {sorted(set(c) - CWC_KEYS)}")
            if not str(c.get("entity", "")).startswith("weather."):
                bad.append("clock weather: entity is not a weather entity")
            if c.get("locale") not in C.CWC_LOCALE.values():
                bad.append(f"clock weather: locale {c.get('locale')!r} not reviewed")
            secs_c = c.get("sections") or {}
            if set(secs_c) - {"header"} or set(secs_c.get("header") or {}) - {"rows"}:
                bad.append("clock weather: only header rows are set; strip and list stay the card's defaults")
            for row in (secs_c.get("header") or {}).get("rows", []):
                for seg in row.get("segments", []):
                    if seg.get("type") not in CWC_SEGMENTS:
                        bad.append(f"clock weather: segment {seg.get('type')!r} not reviewed")
                    if seg.get("type") == "date" and seg.get("date_pattern") != "dd/MM/yy":
                        bad.append(f"clock weather: date must be DD/MM/YY, not {seg.get('date_pattern')!r}")
                    if seg.get("type") == "time" and seg.get("time_pattern") != "HH:mm":
                        bad.append(f"clock weather: time must be HH:mm, not {seg.get('time_pattern')!r}")
        elif t == "custom:auto-entities":
            for rule in (c.get("filter") or {}).get("include", []):
                if set(rule) - {"domain", "state"}:
                    bad.append(f"auto-entities filter beyond domain/state: {rule}")
            if not label_ok(str((c.get("card") or {}).get("title", ""))):
                bad.append("auto-entities title not bilingual")
            if not c.get("else"):
                bad.append("auto-entities with no else card: an empty list would say nothing")
    return bad


def root_problems(dash, export, label_ok=None, forbidden=None, reviewed=None):
    """V3-026: the preview's dashboard-level settings of Kiosk Mode and WallPanel.
    V3-027 reuses it for the working dashboards' WallPanel, one language per
    locale, with that locale's own reassuring words forbidden when dark."""
    label_ok = label_ok or bilingual
    forbidden = PREVIEW_DARK_FORBIDDEN if forbidden is None else forbidden
    bad = []
    for key, allowed in (reviewed or PREVIEW_ROOT).items():
        if key in dash and set(dash[key]) - allowed:
            bad.append(f"{key}: unreviewed options {sorted(set(dash[key]) - allowed)}")
    km = dash.get("kiosk_mode") or {}
    if km and km != {"hide_header": True, "hide_sidebar": True}:
        bad.append(f"kiosk_mode is not the legacy dashboard's settings: {km}")
    wp = dash.get("wallpanel") or {}
    if wp.get("hide_toolbar") or wp.get("hide_sidebar"):
        bad.append("wallpanel hides chrome too: leave that to Kiosk Mode")
    normal, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]
    for c in wp.get("cards", []):
        if c.get("type") != "markdown":
            bad.append(f"wallpanel info card {c.get('type')!r} is not reviewed")
            continue
        for e in B.entities_in(c):
            if e not in export:
                bad.append(f"wallpanel: {e} not in the export")
        try:
            txt = R.env_for(normal, attrs).from_string(c["content"]).render()
            dtxt = R.env_for(dark, {}).from_string(c["content"]).render()
        except Exception as e:  # noqa: BLE001
            bad.append(f"wallpanel template: {type(e).__name__}")
            continue
        if not label_ok(re.sub(r"<[^>]+>", " ", txt)):
            bad.append(f"wallpanel card label check failed: {txt[:40]!r}")
        hits = [w for w in forbidden if re.search(w, re.sub(r"<[^>]+>", " ", dtxt))]
        if hits:
            bad.append(f"wallpanel dark says {hits}")
    return bad


def bilingual(text):
    return bool(CJK.search(text) and LATIN.search(text))


def preview_problems(view, spec, export, own_paths, own_base, working_paths, working_base, tabs):
    """The bilingual design preview (V3-025), one page. Returns {check: [problems]}."""
    foot = (view.get("footer") or {}).get("card")
    cards = list(walk_cards(view)) + (list(walk_cards(foot, True)) if foot else [])
    out = {k: [] for k in ("types", "entities", "links", "actions", "tiles", "tabs", "bilingual",
                           "bands", "dark", "renders", "custom")}
    out["types"] = sorted({c["type"] for c in cards} - PREVIEW_TYPES)
    out["custom"] = custom_problems(view)
    popups = {c["hash"] for c in cards if c.get("type") == "custom:bubble-card" and c.get("card_type") == "pop-up"}
    out["entities"] = sorted(e for e in B.entities_in(view) if e not in export)
    for n in nav_paths(view):
        if n.startswith("#"):
            if n not in popups:   # a hash opens a Bubble Card pop-up on this page (V3-026)
                out["links"].append(n)
            continue
        part = n.strip("/").split("/")
        if len(part) != 2:
            out["links"].append(n)
        elif part[0] == own_base:
            if part[1] not in own_paths:
                out["links"].append(n)
        elif part[0] == working_base:
            # a working page that shares a preview page's name would make the
            # repository gate read every working link as internal (see c5247b3)
            if part[1] not in working_paths or part[1] in own_paths:
                out["links"].append(n)
        else:
            out["links"].append(n)
    for a in actions(view):
        tgt = (a.get("target") or {}).get("entity_id")
        tgts = tgt if isinstance(tgt, list) else [tgt]
        if a.get("perform_action") not in PREVIEW_ACTIONS or not all(str(t).startswith("light.") for t in tgts):
            out["actions"].append(f"{a.get('perform_action')} -> {tgt}")
    for c in cards:
        if c.get("type") != "tile" or not acting(c) or c["entity"].startswith("light."):
            continue
        # a read-only domain's details dialog has no control (the working views' rule)
        if C.effective_tile_actions(c) == ("more-info", "none") and c["entity"].split(".")[0] in C.READ_ONLY_DOMAINS:
            continue
        out["tiles"].append(c["entity"])
    if not foot or foot.get("type") != "grid":
        out["tabs"].append("no tab bar in the footer")
    else:
        btns = foot.get("cards", [])
        want = spec.get("tab", view["path"])
        tinted = [b for b in btns if b.get("color")]
        if [b["tap_action"].get("navigation_path", "").rsplit("/", 1)[-1] or view["path"] for b in btns] != \
                [t[0] for t in tabs]:
            out["tabs"].append("tabs differ from the manifest's")
        if len(tinted) != 1:
            out["tabs"].append(f"{len(tinted)} tinted tabs")
        for b, (path, _, _) in zip(btns, tabs):
            here = path == view["path"]
            act = b["tap_action"].get("action")
            if here != (act == "none"):
                out["tabs"].append(f"{path}: inert={act == 'none'} on page {view['path']}")
            if bool(b.get("color")) != (path == want):
                out["tabs"].append(f"{path}: tinted={bool(b.get('color'))}, current tab is {want}")
    for c in cards:
        label = c.get("heading") if c.get("type") == "heading" else c.get("name") if c.get("type") == "button" else None
        if label is not None and not bilingual(str(label)):
            out["bilingual"].append(str(label))
    heads, holes, clamps = band_problems(view, spec)
    out["bands"] = heads + holes + clamps
    normal, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]
    for c in cards:
        if c.get("type") != "markdown":
            continue
        try:
            txt = R.env_for(normal, attrs).from_string(c["content"]).render()
            dtxt = R.env_for(dark, {}).from_string(c["content"]).render()
        except Exception as e:  # noqa: BLE001 — a template that cannot render is a broken card
            out["renders"].append(f"{type(e).__name__}: {str(e)[:60]}")
            continue
        # a self-hiding card (show_empty: false) is read where it shows, and must show somewhere
        hides = c.get("show_empty") is False
        if hides and not txt and not dtxt:
            out["renders"].append("self-hiding card empty in both the fixture and the dark: never shows")
        for t in ([x for x in (txt, dtxt) if x] if hides else [txt]):
            if not bilingual(re.sub(r"<[^>]+>", " ", t)):
                out["bilingual"].append(re.sub(r"\s+", " ", t)[:50])
        plain = re.sub(r"<[^>]+>", " ", dtxt)
        hits = [w for w in PREVIEW_DARK_FORBIDDEN if re.search(w, plain)]
        if hits:
            out["dark"].append(f"{hits} in: {re.sub(r'\s+', ' ', plain)[:60]}")
    return out


def validate(g: Gate):
    man = B.load_yaml(B.SRC / "manifest.yaml")
    base = man["baseline"]
    sha = hashlib.sha256((ROOT / base["file"]).read_bytes()).hexdigest()
    g.check(sha == base["sha256"], "V2 baseline unchanged (sha256 pinned)", sha)
    export = B.load_export(ROOT / man["entity_authority"])
    v2 = yaml.safe_load((ROOT / base["file"]).read_text(encoding="utf-8"))
    v2_paths = [v["path"] for v in v2["views"]]
    v2_by_path = {v["path"]: v for v in v2["views"]}
    controls = man.get("controls", {}) or {}
    # The allowlist itself: each entry a real V2 toggle, never a protected class.
    for e, ctl in sorted(controls.items()):
        src = v2_tiles(v2_by_path.get(ctl.get("v2_view"), {}), e)
        g.check(e in export, f"controls: {e} exists in the states export")
        g.check(not protected_switch(e), f"controls: {e} is not a protected switch")
        g.check(any(C.effective_tile_actions(x)[1] == "toggle" for x in src),
                f"controls: {e} is a toggle on V2 {ctl.get('v2_view')} today", str(len(src)) + " V2 tiles")

    try:
        _, rep, stale = B.build(write=False)
    except SystemExit as e:  # baseline drift or a false / missing migration row
        g.check(False, "build runs (baseline pinned, migration map verified)", str(e)[:400])
        return
    g.check(True, "build runs (baseline pinned, migration map verified)")
    g.check(not stale, "build reproducible: committed outputs == fresh build", ", ".join(stale))
    for r in rep["views"]:
        if r["kind"] == "native":
            g.check(isinstance(r.get("migration"), list),
                    f"[{r['path']}] every V2 entity has a verified V3 place ({len(r.get('migration', []))} moved)")

    en_cat = B.load_yaml(B.SRC / "i18n" / "en.yaml")
    for loc in man["locales"]:
        tag = f"[{loc['code']}]"
        path = ROOT / loc["output"]
        text = path.read_text(encoding="utf-8")
        g.check("DEVELOPMENT ONLY — NOT DEPLOYED" in text[:600], f"{tag} output marked DEVELOPMENT ONLY")
        try:
            dash = B.load_yaml(path)  # duplicate-key-aware
            g.check(True, f"{tag} YAML parses, no duplicate keys")
        except yaml.YAMLError as e:
            g.check(False, f"{tag} YAML parses, no duplicate keys", str(e)[:200])
            continue
        views = dash["views"]
        paths = [v["path"] for v in views]
        g.check(len(paths) == len(set(paths)), f"{tag} view paths unique")
        g.check(all(p in paths for p in v2_paths), f"{tag} every V2 view has a V3 home",
                str([p for p in v2_paths if p not in paths]))
        g.check(all(f"v2-{n}" in paths for n in man["native"]), f"{tag} classic copy of every rebuilt view")
        g.check(all("badges" not in v for v in views), f"{tag} no badges block (DR-011)")

        # navigation
        bad_nav = [n for n in nav_paths(dash)
                   if not n.startswith(f"/{loc['url_base']}/") or n.split("/")[2].split("#")[0] not in paths]
        g.check(not bad_nav, f"{tag} every navigation_path resolves inside /{loc['url_base']}/",
                str(sorted(set(bad_nav))[:8]))
        g.check(f"/{base['url_base']}/" not in text, f"{tag} no link left pointing at /{base['url_base']}/")

        # dependencies
        customs = {c["type"] for c in walk_cards(dash) if str(c.get("type", "")).startswith("custom:")}
        allowed_custom = ALLOWED_CUSTOM.union(*WORKING_CUSTOM.values(), {NAVBAR})
        g.check(customs <= allowed_custom, f"{tag} custom cards limited to {sorted(allowed_custom)}",
                str(customs - allowed_custom))
        g.check("kiosk_mode" not in dash, f"{tag} no kiosk_mode on the working dashboards "
                "(removed after the kiosk mode lockout; restoring it is the owner's call, V3-027)")
        rp = root_problems(dash, export, label_ok=nonempty,
                           forbidden=[re.escape(loc_t(loc, "s.open")), re.escape(loc_t(loc, "s.closed"))],
                           reviewed={"wallpanel": PREVIEW_ROOT["wallpanel"]})
        g.check(not rp, f"{tag} WallPanel only, with the preview's reviewed options; dark says no data, "
                "never open or closed (V3-027)", str(rp[:4]))

        # entities
        ents = B.entities_in(dash)
        unknown = sorted(e for e in ents if e not in export)
        g.check(not unknown, f"{tag} every referenced entity exists in the states export", str(unknown[:10]))

        native = [v for v in views if v["path"] in man["native"]]
        for v in native:
            vt = f"{tag}[{v['path']}]"
            cards = list(walk_cards(v))
            inner = WORKING_INNER.get(v["path"], set())
            ok_types = NATIVE_TYPES | WORKING_CUSTOM.get(v["path"], set()) | inner | {NAVBAR}
            g.check(all(c["type"] in ok_types for c in cards),
                    f"{vt} native card types only (plus its V3-027 custom cards)",
                    str({c['type'] for c in cards} - ok_types))
            wc = working_custom_problems(v)
            g.check(not wc, f"{vt} custom cards: only its own, in a band after its native readings, "
                    "named in a note, with the preview's reviewed behaviour (V3-027)", str(wc[:4]))
            cards = [c for c in cards if c["type"] not in inner]   # laid out by auto-entities, not the section
            if man.get("navbar"):
                nbp = navbar_problems(v, loc["url_base"], paths)
                g.check(not nbp, f"{vt} navbar: one, last, documented options only, every route a labelled "
                        "link to a page here, Home included (V3-028)", str(nbp[:4]))
            elif any(c.get("type") == NAVBAR for c in cards):
                g.check(False, f"{vt} navbar present but the manifest has none", "")
            g.check("card_mod" not in yaml.safe_dump(v), f"{vt} no card_mod (styling is the theme's)")
            g.check(all("grid_options" in c for c in cards), f"{vt} every card declares grid_options")
            g.check(v.get("max_columns", 4) <= 2, f"{vt} max_columns <= 2 (DR-013)")
            g.check(all(s.get("column_span", 1) <= 2 for s in v["sections"]), f"{vt} column_span <= 2")
            small = [c for c in cards if not (c["grid_options"]["columns"] == "full" or (
                isinstance(c["grid_options"]["columns"], int) and c["grid_options"]["columns"] >= 2))]
            g.check(not small, f"{vt} nothing below columns: 2 (DR-012); columns is a number or full",
                    str([c["grid_options"]["columns"] for c in small]))
            tb = topbar_problems(v)
            g.check(not tb, f"{vt} shared top bar: time over DD/MM/YY, six named rail buttons (>= 3 units), "
                    "one height, whole rows on wall and phone, current page inert and tinted", str(tb))
            band = next((r.get("band_grid", 12) for r in rep["views"] if r["path"] == v["path"]), 12)
            if band == 24:
                spec = B.load_yaml(B.SRC / "views" / f"{v['path']}.yaml")
                heads, holes, clamps = band_problems(v, spec)
                g.check(not heads, f"{vt} band_grid 24: every two-column band heading is full width", str(heads))
                g.check(not holes, f"{vt} band_grid 24: every band packs into whole rows on the wall iPad "
                        "(24 units) and a phone (12)", str(holes))
                g.check(not clamps, f"{vt} band_grid 24: every card draws at the size its grid_options say",
                        str(clamps[:6]))
            elif loc["code"] == "en":
                half, big = band_note(v)
                if half or big:
                    g.note(f"[{v['path']}] not on band_grid 24: on the wall iPad {half} card(s) in its two-column "
                           f"bands draw at half the width written, and {big} card(s) draw larger than their "
                           "grid_options (card minimums) — V3-013 second pass")
            dump = yaml.safe_dump(v, allow_unicode=True)
            g.check(not SENTINEL.search(dump), f"{vt} no float(0/100/9999) sentinel")
            # safety boundaries
            acts = list(actions(v))
            hvac = [a for a in acts if "climate." in str(a.get("target")) or str(a.get("perform_action", "")).startswith("climate.")]
            g.check(not hvac, f"{vt} no HVAC action (V3-008 not yet satisfied)")
            sw = [a for a in acts if "switch." in str(a.get("target")) or "siren." in str(a.get("target"))]
            g.check(not sw, f"{vt} no switch/siren actions (privacy, bulb power, sirens stay classic)")
            bad_ro, prot = tile_safety(v, v2_by_path, controls, base["url_base"], loc["url_base"])
            g.check(not bad_ro, f"{vt} climate/camera tiles read-only; switches act only as in V2 (manifest controls); sirens only as the V2 tile",
                    str(bad_ro))
            g.check(not prot, f"{vt} no control on a protected switch or setting (camera, alerting, sensing, sockets, HVAC, critical loads, bulb power)", str(prot))
            bare = unconfirmed_presses(v)
            g.check(not bare, f"{vt} every button press asks first", str(bare))
            # rendered honesty
            for scen, (states, attrs) in R.scenarios().items():
                try:
                    outs = R.render_view(v, states, attrs)
                    g.check(True, f"{vt} templates render offline ({scen})")
                except Exception as e:  # noqa: BLE001
                    g.check(False, f"{vt} templates render offline ({scen})", repr(e)[:200])
                    continue
                g.check(all(not o.startswith("    ") for o in outs),
                        f"{vt} no markdown starts with 4 spaces ({scen})")
                if scen == "dark":
                    cat = B.load_yaml(B.SRC / "i18n" / f"{loc['code']}.yaml")
                    joined = "\n".join(outs)
                    leaks = []
                    for k in DARK_FORBIDDEN_KEYS:
                        s = str(cat.get(k, en_cat[k]))
                        stem = reassurance_stem(s)
                        if stem and stem in joined:
                            leaks.append(k)
                    g.check(not leaks, f"{vt} no reassurance when everything is dark", str(leaks))
                    g.check(not re.search(r"\*\*0\*\*|\b0 W\b|\b0\.0 W\b", joined),
                            f"{vt} no zero claimed from nothing (dark)")

        lr = rep["locales"][loc["code"]]
        g.check(not lr["missing_keys"], f"{tag} no missing string keys", str(lr["missing_keys"]))
        if lr["fallback_keys"]:
            g.note(f"{tag} {len(lr['fallback_keys'])} strings fall back to English")

    # secrets: everything V3 owns
    files = [p for p in (ROOT / "src/casaray_v3").rglob("*") if p.is_file()]
    files += [p for p in (ROOT / "dashboards/casaray_v3").rglob("*") if p.is_file()]
    files += [ROOT / "dashboards/casaray_v3.yaml"] + list((ROOT / "scripts/v3").glob("*.py"))
    files += [p for p in (ROOT / "docs/casaray-v3").rglob("*") if p.is_file()]
    files += [p for p in (ROOT / "tests/v3").rglob("*.py") if p.is_file()]
    hits = []
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        for rx in SECRET_PATTERNS:
            for m in rx.finditer(t):
                if p.name == "validate_dashboard.py":
                    continue  # the patterns themselves
                hits.append(f"{p.relative_to(ROOT)}:{rx.pattern[:20]}")
    g.check(not hits, "no secrets, tokens or private URLs in V3 files", str(hits[:5]))
    # the bilingual design preview (V3-025): a separate dashboard, its own gate
    pv = man.get("preview")
    g.check(bool(pv) == ("preview" in rep), "preview: built exactly when the manifest declares it")
    if pv:
        pdash = yaml.safe_load((ROOT / pv["output"]).read_text(encoding="utf-8"))
        wloc = next(l for l in man["locales"] if l["url_base"] == pv["working_url_base"])
        wpaths = {v["path"] for v in yaml.safe_load((ROOT / wloc["output"]).read_text(encoding="utf-8"))["views"]}
        g.check([v["path"] for v in pdash["views"]] == list(pv["views"]), "preview: its pages, in order")
        g.check(not rep["preview"]["missing_keys"], "preview: no missing string keys",
                str(rep["preview"]["missing_keys"]))
        g.check(not any(pv["output"] == l["output"] for l in man["locales"])
                and pv["url_base"] not in {l["url_base"] for l in man["locales"]},
                "preview: its own file and url_path, never a working dashboard's")
        g.check(not root_problems(pdash, export), "preview: Kiosk Mode and WallPanel settings as reviewed (V3-026)",
                str(root_problems(pdash, export)[:4]))
        what = {"types": "native card types, plus the owner-approved custom cards (V3-026)",
                "custom": "each custom card only does what was reviewed (V3-026)", "entities": "every entity exists in the states export",
                "links": "every link opens a preview page or a real working page (no shared names)",
                "actions": "no action but the existing light actions",
                "tiles": "only light tiles act; every other tile is read-only",
                "tabs": "the tab bar: the manifest's tabs, one tinted, inert only on its own page",
                "bilingual": "every heading, button and card says both languages",
                "bands": "every band packs on the wall iPad and a phone, lit, answering and dark",
                "dark": "nothing reassuring when nothing answers",
                "renders": "every template renders (live-shaped and dark)"}
        for v in pdash["views"]:
            spec = B.load_yaml(B.SRC / "preview" / f"{v['path']}.yaml")
            probs = preview_problems(v, spec, export, set(pv["views"]), pv["url_base"], wpaths,
                                     pv["working_url_base"], pv["tabs"])
            for k, msg in what.items():
                g.check(not probs[k], f"preview[{v['path']}] {msg}", str(probs[k][:4]))

    for r in rep["views"]:
        if r["dark_at_export"] and r["kind"] == "native":
            g.note(f"[{r['path']}] {len(r['dark_at_export'])} entities were not 'ok' in the 05/09 export "
                   "(drawn as no data/offline when so; not re-checked live — offline build)")


def main():
    g = Gate()
    validate(g)
    for w in g.warn:
        print("NOTE ", w)
    for f in g.fail:
        print("FAIL ", f)
    print(f"\n{len(g.passed)} passed, {len(g.fail)} failed, {len(g.warn)} notes")
    return 1 if g.fail else 0


if __name__ == "__main__":
    sys.exit(main())
