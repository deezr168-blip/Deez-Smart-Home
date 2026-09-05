#!/usr/bin/env python3
"""Structural checks for the Deez Smart Home Lovelace dashboard.

Read-only. Never contacts Home Assistant. Exits non-zero on failure so it can
gate a deployment.

Covers the checks that are possible without Home Assistant itself:
  - every Jinja template compiles
  - every in-dashboard navigation_path resolves to a real view
  - card-type / property mismatches (e.g. `color` on a Mushroom card, which
    Home Assistant silently ignores)
  - /local/ resource paths exist in www/ when www/ is present
  - mass-damage detection against the committed version of the same file

It does NOT check Lovelace schema or entity existence: valid YAML is not valid
Lovelace config, and the entity registry is not reachable from here. See
DEPLOYMENT_BLOCKERS.md.
"""

import json
import os
import re
import subprocess
import sys

import yaml

try:
    from jinja2 import Environment, TemplateSyntaxError
except ImportError:
    sys.exit("jinja2 is required: pip install jinja2")

# Properties that belong to native tile cards; inert on Mushroom cards.
TILE_ONLY = {"color", "features_position", "vertical", "hide_state", "state_content"}
# Anything below this fraction of the committed size is treated as truncation.
MIN_SIZE_RATIO = 0.80
# A drop of more than this many views/entities needs a human explanation.
MAX_VIEW_DROP = 1
MAX_ENTITY_DROP = 5

DOMAINS = {
    "light", "switch", "sensor", "binary_sensor", "media_player", "climate",
    "fan", "cover", "scene", "script", "automation", "input_boolean",
    "input_number", "input_select", "input_text", "input_datetime", "camera",
    "person", "device_tracker", "todo", "weather", "number", "select",
    "button", "event", "remote", "zone", "update", "sun", "lock", "vacuum",
}

fails = []
warns = []


def entity_ids(text):
    return {e for e in re.findall(r"\b([a-z_]+\.[a-z0-9_]+)\b", text)
            if e.split(".")[0] in DOMAINS}


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def committed(path):
    """The version of `path` in HEAD, or None if it is a new file."""
    r = subprocess.run(["git", "show", f"HEAD:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def check(path):
    raw = open(path, encoding="utf-8").read()
    doc = yaml.safe_load(raw)
    if not isinstance(doc, dict) or "views" not in doc:
        fails.append(f"{path}: not a Lovelace dashboard (no top-level 'views')")
        return

    views = doc["views"]

    # 1. templates compile
    env = Environment()
    n_tpl = 0

    def tpl(node):
        nonlocal n_tpl
        for k, v in node.items():
            if isinstance(v, str) and ("{{" in v or "{%" in v):
                n_tpl += 1
                try:
                    env.from_string(v)
                except TemplateSyntaxError as exc:
                    fails.append(f"{path}: template syntax in '{k}': {exc}")
    walk(doc, tpl)
    print(f"  templates compiled       : {n_tpl}")

    # 2. navigation integrity
    #
    # A dashboard's own links are "/<url_path>/<view path>". The url_path is
    # not in the file -- it is set where the dashboard is registered -- so it
    # is inferred: any prefix whose links resolve against this file's own view
    # paths is this dashboard's. That keeps every dashboard covered instead of
    # only the one whose url_path happened to be hardcoded here, and a link
    # into a *different* dashboard is still correctly left unchecked.
    paths = {v.get("path") for v in views}
    navs = set(re.findall(r"navigation_path:\s*([^\s,}]+)", raw))
    prefixes = {n.split("/")[1] for n in navs if n.count("/") >= 2}
    internal, broken = set(), []
    for prefix in sorted(prefixes):
        marker = f"/{prefix}/"
        group = {n for n in navs if n.startswith(marker)}
        misses = sorted(n for n in group if n.split(marker, 1)[1] not in paths)
        # Every target resolving means this prefix is this dashboard. A prefix
        # where none resolve is a link to another dashboard: not ours to check.
        if len(misses) < len(group):
            internal |= group
            broken += misses
    broken = sorted(broken)
    if broken:
        fails.append(f"{path}: navigation targets do not resolve: {broken}")
    print(f"  views / internal links   : {len(views)} / {len(internal)}"
          f"  broken={len(broken)}")

    # 3. card-type property mismatches
    bad_props = []

    def props(node):
        t = node.get("type")
        if isinstance(t, str) and t.startswith("custom:mushroom-"):
            for k in node:
                if k == "color" and "icon_color" not in node:
                    bad_props.append((t, k, str(node.get("primary"))[:30]))
    walk(doc, props)
    if bad_props:
        for t, k, who in bad_props:
            warns.append(f"{path}: '{k}' is inert on {t} (use icon_color) — {who!r}")
    print(f"  inert card properties    : {len(bad_props)}")

    # 4. /local/ resources
    local_refs = sorted(set(re.findall(r"/local/([A-Za-z0-9_./-]+)", raw)))
    if local_refs:
        if os.path.isdir("www"):
            missing = [r for r in local_refs if not os.path.exists(os.path.join("www", r))]
            if missing:
                fails.append(f"{path}: /local/ resources missing from www/: {missing}")
            print(f"  /local/ resources        : {len(local_refs)}, missing {len(missing)}")
        else:
            print(f"  /local/ resources        : {len(local_refs)} (www/ not in repo — UNVERIFIED)")
    else:
        print("  /local/ resources        : none referenced")

    # 5. mass-damage detection against HEAD
    old = committed(path)
    if old is None:
        print("  mass-damage check        : new file, no baseline")
        return
    ratio = len(raw) / max(len(old), 1)
    if ratio < MIN_SIZE_RATIO:
        fails.append(f"{path}: shrank to {ratio:.0%} of committed size "
                     f"({len(old)} -> {len(raw)} bytes) — possible truncation")
    try:
        old_doc = yaml.safe_load(old)
        dv = len(old_doc.get("views", [])) - len(views)
        if dv > MAX_VIEW_DROP:
            fails.append(f"{path}: {dv} views disappeared "
                         f"({len(old_doc['views'])} -> {len(views)})")
        de = len(entity_ids(old)) - len(entity_ids(raw))
        if de > MAX_ENTITY_DROP:
            fails.append(f"{path}: {de} entity IDs disappeared")
        print(f"  vs HEAD                  : size {ratio:.0%}, views {dv:+d}, entities {de:+d}")
    except yaml.YAMLError:
        warns.append(f"{path}: committed version does not parse; skipped delta check")


def main():
    targets = sys.argv[1:]
    if not targets:
        print("  no dashboard files to check")
        return 0
    for t in targets:
        print(f"\n  --- {t} ---")
        check(t)
    print()
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
