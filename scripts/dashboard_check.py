#!/usr/bin/env python3
"""Structural checks for the Deez Smart Home Lovelace dashboard.

Read-only. Never contacts Home Assistant. Exits non-zero on failure so it can
gate a deployment.

Covers the checks that are possible without Home Assistant itself:
  - every Jinja template compiles
  - every in-dashboard navigation_path resolves to a real view
  - card-type / property mismatches (e.g. `color` on a Mushroom card, which
    Home Assistant silently ignores)
  - markdown cards do not emit enough leading whitespace to render as a
    CommonMark indented code block
  - no line inside a folded scalar is indented deeper than its block, which
    would stop YAML folding it and break a sentence in half
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


def strip_jinja_tags(body):
    """`body` with every {% ... %} removed, honouring Jinja whitespace control.

    `{%- ... %}` eats the whitespace before the tag and `{% ... -%}` the
    whitespace after it, so a naive strip would report whitespace that Jinja
    never emits and flag cards that are already correct.
    """
    out, pos = [], 0
    for m in re.finditer(r"\{%(.*?)%\}", body, flags=re.S):
        inner = m.group(1)
        chunk = body[pos:m.start()]
        if inner.startswith("-"):
            chunk = chunk.rstrip()
        out.append(chunk)
        pos = m.end()
        if inner.endswith("-"):
            while pos < len(body) and body[pos].isspace():
                pos += 1
    out.append(body[pos:])
    return "".join(out)


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

    # 4. markdown cards must not render as an indented code block
    #
    # A `{% set %}` preamble leaves its inter-tag spaces in the output. Four
    # or more of them at the start makes CommonMark treat the whole card as
    # an indented code block, so a house summary renders as grey monospace.
    # Counted statically: strip the tags, and whatever spaces remain in front
    # are what the card will emit before its first real character. The fix is
    # `-%}` on the preamble tags, which eats the whitespace after them.
    #
    # Static, so it is deliberately conservative: whitespace emitted from
    # inside a branch that only some states take is not counted, and no card
    # is ever flagged for whitespace Jinja will not actually emit.
    indented = []

    def md_indent(node):
        if node.get("type") != "markdown":
            return
        body = node.get("content")
        if not isinstance(body, str) or "{%" not in body:
            return
        # Folded YAML scalars arrive with newlines already folded to spaces.
        lead = strip_jinja_tags(body)
        n = len(lead) - len(lead.lstrip(" "))
        if n >= 4:
            indented.append((n, re.sub(r"\s+", " ", body)[:60]))
    walk(doc, md_indent)
    for n, who in indented:
        fails.append(f"{path}: markdown card emits {n} leading spaces — renders "
                     f"as a code block; use -%}} on the preamble tags — {who!r}")
    print(f"  markdown code-block risk : {len(indented)}")

    # 5. folded scalars must not have accidentally more-indented lines
    #
    # In a YAML folded block, a line indented deeper than the block is "more
    # indented": YAML stops folding around it and keeps the newlines. One
    # stray leading space therefore breaks a sentence in half mid-render --
    # "All 3 update entities are up to\ndate." -- and nothing else catches it,
    # because the YAML is valid and the template compiles.
    #
    # Deliberate deeper indentation inside a folded scalar is a thing YAML
    # supports, but nothing in these dashboards uses it: every block is one
    # flat run of text. So any deeper line here is a typo.
    ragged = []
    lines = raw.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)\S.*:\s*>-?\s*$", lines[i])
        if not m:
            i += 1
            continue
        key_indent = len(m.group(1))
        body = []
        j = i + 1
        while j < len(lines) and (not lines[j].strip()
                                  or len(lines[j]) - len(lines[j].lstrip()) > key_indent):
            body.append((j, lines[j]))
            j += 1
        widths = [len(l) - len(l.lstrip()) for _, l in body if l.strip()]
        if widths:
            base = min(widths)
            for n, l in body:
                if l.strip() and (len(l) - len(l.lstrip())) > base:
                    ragged.append((n + 1, l.strip()[:50]))
        i = j
    for n, text in ragged:
        fails.append(f"{path}:{n}: line is indented deeper than its folded "
                     f"block, so YAML keeps the line break instead of folding "
                     f"it — {text!r}")
    print(f"  ragged folded scalars    : {len(ragged)}")

    # 6. /local/ resources
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

    # 7. mass-damage detection against HEAD
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
        # dv and de are DROPS (old - new). Negate for display so the sign reads
        # from the file's point of view: +3 means three were added, -3 lost.
        # Printing the raw drop made "entities -53" mean 53 were *gained*, which
        # every reader, human and machine, got backwards.
        print(f"  vs HEAD                  : size {ratio:.0%}, "
              f"views {-dv:+d}, entities {-de:+d}")
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
