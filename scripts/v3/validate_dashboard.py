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


def band_problems(view, spec):
    """For a `band_grid: 24` view, against the frontend's own layout rules
    (ha_layout.py): headings in two-column bands that are not full width (they
    would sit BESIDE their cards), bands that leave empty cells on the wall
    iPad (24 units) or a phone (12), and cards drawn at a size other than the
    one their grid_options state (a card minimum overriding the YAML). The
    shared top bar is not the spec's to size and is skipped."""
    skip = {i for i, s in enumerate(spec.get("sections", [])) if s.get("topbar")}
    heads, holes, clamps = [], [], []
    for i, s in enumerate(view["sections"]):
        if i in skip:
            continue
        span = s.get("column_span", 1)
        for c in s.get("cards", []):
            if c.get("type") == "heading" and span == 2 and L.effective(c)[0] != "full":
                heads.append(f"section {i}")
            if L.configured(c) != L.effective(c):
                clamps.append(f"section {i} {c['type']} {L.configured(c)} draws {L.effective(c)}")
        for where, resolved in (("wall iPad", 2), ("phone", 1)):
            n = L.section_holes(s, L.units(span, resolved))
            if n:
                holes.append(f"section {i}: {n} empty cells on the {where}")
    return heads, holes, clamps


def band_note(view):
    """What a view not yet on band_grid 24 looks like on the wall iPad."""
    half = sum(1 for i, s in enumerate(view["sections"]) if s.get("column_span", 1) == 2 and i > 0
               for c in s.get("cards", []) if L.effective(c)[0] != "full")
    big = sum(1 for s in view["sections"] for c in s.get("cards", []) if L.configured(c) != L.effective(c))
    return half, big


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
        g.check(customs <= ALLOWED_CUSTOM, f"{tag} custom cards limited to {sorted(ALLOWED_CUSTOM)}",
                str(customs - ALLOWED_CUSTOM))

        # entities
        ents = B.entities_in(dash)
        unknown = sorted(e for e in ents if e not in export)
        g.check(not unknown, f"{tag} every referenced entity exists in the states export", str(unknown[:10]))

        # CR-V3-20: pages with no V2 equivalent (`new_views`) get every safety,
        # geometry and honesty check a V2 rebuild gets — a new page is not a
        # lower-trust path through this gate.
        new_view_paths = set(man.get("new_views", []) or [])
        native = [v for v in views if v["path"] in man["native"] or v["path"] in new_view_paths]
        for v in native:
            vt = f"{tag}[{v['path']}]"
            cards = list(walk_cards(v))
            g.check(all(c["type"] in NATIVE_TYPES for c in cards), f"{vt} native card types only",
                    str({c['type'] for c in cards} - NATIVE_TYPES))
            g.check("card_mod" not in yaml.safe_dump(v), f"{vt} no card_mod (styling is the theme's)")
            g.check(all("grid_options" in c for c in cards), f"{vt} every card declares grid_options")
            g.check(v.get("max_columns", 4) <= 2, f"{vt} max_columns <= 2 (DR-013)")
            g.check(all(s.get("column_span", 1) <= 2 for s in v["sections"]), f"{vt} column_span <= 2")
            small = [c for c in cards if not (c["grid_options"]["columns"] == "full" or (
                isinstance(c["grid_options"]["columns"], int) and c["grid_options"]["columns"] >= 2))]
            g.check(not small, f"{vt} nothing below columns: 2 (DR-012); columns is a number or full",
                    str([c["grid_options"]["columns"] for c in small]))
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
