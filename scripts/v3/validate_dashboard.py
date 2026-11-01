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

ROOT = B.ROOT
ALLOWED_CUSTOM = {"custom:webrtc-camera"}      # V2's only custom card; carried views only
NATIVE_TYPES = {"heading", "markdown", "tile", "button", "picture-entity",
                "weather-forecast", "todo-list"}
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


def validate(g: Gate):
    man = B.load_yaml(B.SRC / "manifest.yaml")
    base = man["baseline"]
    sha = hashlib.sha256((ROOT / base["file"]).read_bytes()).hexdigest()
    g.check(sha == base["sha256"], "V2 baseline unchanged (sha256 pinned)", sha)
    export = B.load_export(ROOT / man["entity_authority"])
    v2 = yaml.safe_load((ROOT / base["file"]).read_text(encoding="utf-8"))
    v2_paths = [v["path"] for v in v2["views"]]

    _, rep, stale = B.build(write=False)
    g.check(not stale, "build reproducible: committed outputs == fresh build", ", ".join(stale))

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

        native = [v for v in views if v["path"] in man["native"]]
        for v in native:
            vt = f"{tag}[{v['path']}]"
            cards = list(walk_cards(v))
            g.check(all(c["type"] in NATIVE_TYPES for c in cards), f"{vt} native card types only",
                    str({c['type'] for c in cards} - NATIVE_TYPES))
            g.check("card_mod" not in yaml.safe_dump(v), f"{vt} no card_mod (styling is the theme's)")
            g.check(all("grid_options" in c for c in cards), f"{vt} every card declares grid_options")
            g.check(v.get("max_columns", 4) <= 2, f"{vt} max_columns <= 2 (DR-013)")
            g.check(all(s.get("column_span", 1) <= 2 for s in v["sections"]), f"{vt} column_span <= 2")
            small = [c for c in cards if c["grid_options"]["columns"] < 2]
            g.check(not small, f"{vt} nothing below columns: 2 (DR-012)")
            dump = yaml.safe_dump(v, allow_unicode=True)
            g.check(not SENTINEL.search(dump), f"{vt} no float(0/100/9999) sentinel")
            # safety boundaries
            acts = list(actions(v))
            hvac = [a for a in acts if "climate." in str(a.get("target")) or str(a.get("perform_action", "")).startswith("climate.")]
            g.check(not hvac, f"{vt} no HVAC action (V3-008 not yet satisfied)")
            sw = [a for a in acts if "switch." in str(a.get("target")) or "siren." in str(a.get("target"))]
            g.check(not sw, f"{vt} no switch/siren actions (privacy, bulb power, sirens stay classic)")
            ro = [c for c in cards if c["type"] == "tile" and c["entity"].split(".")[0] in ("switch", "climate", "siren", "camera")
                  and (c.get("icon_tap_action", {}).get("action") != "none"
                       or c.get("tap_action", {}).get("action") not in ("none", "navigate"))]
            g.check(not ro, f"{vt} switch/climate tiles are read-only", str([c['entity'] for c in ro]))
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
                        stem = re.split(r"\{\w+\}", s)[0].strip() or re.split(r"\{\w+\}", s)[-1].strip()
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
