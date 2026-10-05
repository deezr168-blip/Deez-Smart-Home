#!/usr/bin/env python3
"""Whole-dashboard dependency audit for casaray_v2.yaml.

READ-ONLY and offline. It compares three things that are all in the repository:

  dashboards/casaray_v2.yaml                what the cards reference
  docs/live/states_export_2026-09-05.txt    what the instance had on 05/09
  packages/*.yaml                           what Git itself defines

and classifies every entity reference, navigation target, custom card, theme
and helper the dashboard depends on. The classes are deliberately about what
the REPOSITORY can know, not about what is rendering today:

  confirmed_broken  not in the export, or in reconcile_entities.STALE.
                    A card pointing here cannot work.
  likely_broken     the export lists this ID unavailable while a twin with the
                    same friendly name and domain is ok -- the stale-registry
                    pattern CR-190 documented. Probably the wrong one of a pair.
  live_check        unavailable or unknown in the export with no live twin, or
                    a helper whose definition is not in Git. Only the running
                    instance can say.
  working           present and `ok` in the export. This is a 05/09 snapshot
                    (see CLAUDE.md: the availability column goes stale), so it
                    means "nothing in the repository contradicts it".
  stateless         scene/button/event/update: `unknown` is their normal state.
  obsolete          known-dead IDs and unavailable twins that nothing here
                    should reference (listed so nobody adopts one by name).

Usage:
    python3 scripts/audit_casaray.py                  # write docs/CASARAY_AUDIT.md
    python3 scripts/audit_casaray.py --check          # exit 1 if it would change
    python3 scripts/audit_casaray.py --json           # machine-readable to stdout
    python3 scripts/audit_casaray.py --strict         # exit 1 on confirmed_broken

The output is deterministic (no timestamps) so --check can gate CI.
"""

import argparse
import collections
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import reconcile_entities as rec  # noqa: E402

DASH = os.path.join(ROOT, "dashboards", "casaray_v2.yaml")
THEME = os.path.join(ROOT, "themes", "deez_your_name.yaml")
PACKAGES = os.path.join(ROOT, "packages")
OUT = os.path.join(ROOT, "docs", "CASARAY_AUDIT.md")

STATELESS = {"scene", "button", "event", "update", "script", "automation"}
HELPER_DOMAINS = {"input_boolean", "input_number", "input_select",
                  "input_text", "input_datetime", "counter", "timer"}
# Domains whose definition lives in Home Assistant itself, not in an
# integration: if the definition is not in Git, a lost configuration.yaml
# takes the entity with it.
LOCAL_DEFINITION = HELPER_DOMAINS | {"script", "automation"}
NATIVE_CARDS = {
    "tile", "button", "entities", "entity", "glance", "grid", "heading",
    "markdown", "history-graph", "statistics-graph", "gauge", "sensor",
    "picture-entity", "picture-glance", "todo-list", "thermostat",
    "media-control", "weather-forecast", "logbook", "conditional",
    "vertical-stack", "horizontal-stack", "area", "map", "light",
    "alarm-panel", "energy-distribution", "iframe", "picture",
    # view type, and tile `features:` types (not cards, but they carry `type`)
    "sections", "light-brightness", "fan-speed", "cover-open-close",
    "cover-position", "climate-hvac-modes", "climate-fan-modes",
    "numeric-input",
}
NAV = re.compile(r"/casaray-v2/([a-z0-9-]+)")
CLASSES = ["confirmed_broken", "likely_broken", "live_check", "working",
           "stateless", "obsolete"]


def load_dashboard(path=DASH):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def view_refs(view):
    """Entity IDs one view uses. Dumping the parsed view drops comments, which
    legitimately name dead entities (same reasoning as reconcile_entities)."""
    text = yaml.safe_dump(view, allow_unicode=True, default_flow_style=False)
    return {e for e in re.findall(r"\b([a-z_]+\.[a-z0-9_]+)\b", text)
            if e.split(".")[0] in rec.DOMAINS
            and not rec.SERVICE_CALLS.match(e)}


def repo_defined_helpers():
    """IDs the repository itself defines (see reconcile_entities)."""
    return rec.package_defined(os.path.join(ROOT, "packages"))


def twins(live):
    groups = collections.defaultdict(list)
    for eid, (name, _area, avail) in live.items():
        groups[(eid.split(".")[0], name.strip().lower())].append((eid, avail))
    return groups


def classify(eid, live, groups, defined):
    """-> (class, reason)"""
    dom = eid.split(".")[0]
    if eid in rec.STALE:
        return "confirmed_broken", rec.STALE[eid]
    if eid not in live:
        if eid in defined:
            return "live_check", ("defined by packages/ in Git; exists only "
                                  "once `packages:` is loaded")
        return "confirmed_broken", "not in the 05/09 export"
    name, _area, avail = live[eid]
    siblings = [(e, a) for e, a in groups[(dom, name.strip().lower())]
                if e != eid]
    live_sib = [e for e, a in siblings if a == "ok"]
    if avail == "unavailable":
        if live_sib:
            return "likely_broken", f"twin {live_sib[0]} is ok"
        return "live_check", "unavailable in the export, no live twin"
    if avail == "unknown":
        if dom in STATELESS:
            return "stateless", "unknown is normal for this domain"
        if dom in LOCAL_DEFINITION:
            return "live_check", "unknown in the export; helper never set"
        return "live_check", "unknown in the export"
    if dom in LOCAL_DEFINITION and eid not in defined:
        return "live_check", ("ok on 05/09 but its definition is not in Git; "
                              "lost with configuration.yaml if it was YAML-defined")
    if dom in STATELESS:
        return "stateless", "stateless domain"
    return "working", ("repo packages define it" if eid in defined
                       else "ok in the 05/09 export")


def audit():
    dash = load_dashboard()
    live = rec.load_export(rec.EXPORT)
    groups = twins(live)
    defined = repo_defined_helpers()

    per_view = collections.OrderedDict()
    where = collections.defaultdict(list)
    for v in dash["views"]:
        path = v.get("path", "?")
        refs = view_refs(v)
        per_view[path] = refs
        for e in refs:
            where[e].append(path)

    entities = {}
    for e in sorted(where):
        cls, why = classify(e, live, groups, defined)
        entities[e] = {"class": cls, "reason": why, "views": where[e],
                       "name": live.get(e, ("", "", ""))[0],
                       "area": live.get(e, ("", "", ""))[1]}

    # Obsolete: unavailable twins of something the dashboard DOES use, so no
    # one adopts the wrong one by name.
    obsolete = {}
    used = set(entities)
    for e, info in entities.items():
        if e in live:
            dom = e.split(".")[0]
            for sib, avail in groups[(dom, live[e][0].strip().lower())]:
                if sib != e and sib not in used and avail == "unavailable" \
                        and info["class"] in ("working", "live_check"):
                    obsolete[sib] = f"unavailable twin of {e}"
    for e, why in rec.STALE.items():
        obsolete.setdefault(e, why)

    view_table = []
    for path, refs in per_view.items():
        c = collections.Counter(entities[e]["class"] for e in refs)
        view_table.append((path, len(refs), c))

    # Navigation.
    view_ids = {v.get("path") for v in dash["views"]}
    nav_targets, bad_nav = set(), []

    def nav_scan(node):
        for k in ("navigation_path", "path"):
            val = node.get(k)
            if isinstance(val, str):
                m = NAV.match(val)
                if m:
                    nav_targets.add(m.group(1))
                    if m.group(1) not in view_ids:
                        bad_nav.append(val)
    walk(dash["views"], nav_scan)
    unreachable = sorted(view_ids - nav_targets - {"home"})

    # Custom cards and theme.
    cards = collections.Counter()

    def card_scan(node):
        t = node.get("type")
        if isinstance(t, str):
            cards[t] += 1
    walk(dash["views"], card_scan)
    custom = {k: n for k, n in cards.items() if k.startswith("custom:")}
    unknown_native = {k: n for k, n in cards.items()
                      if not k.startswith("custom:") and k not in NATIVE_CARDS}
    theme_ok = None
    themes_declared = set()
    if os.path.exists(THEME):
        with open(THEME, encoding="utf-8") as fh:
            try:
                themes_declared = set(
                    (yaml.safe_load(fh) or {}).keys())
            except yaml.YAMLError:
                themes_declared = set()
    dash_theme = dash.get("theme")
    if dash_theme:
        theme_ok = dash_theme in themes_declared

    # Helper dependency table.
    helpers = {e: info for e, info in entities.items()
               if e.split(".")[0] in LOCAL_DEFINITION}
    helpers_external = sorted(e for e in helpers if e not in defined
                              and e in live)

    return {
        "entities": entities, "obsolete": obsolete, "views": view_table,
        "bad_nav": sorted(set(bad_nav)), "unreachable_views": unreachable,
        "custom_cards": custom, "unknown_card_types": unknown_native,
        "theme": dash_theme, "theme_declared": theme_ok,
        "helpers_external": helpers_external, "helpers_in_git": sorted(
            e for e in helpers if e in defined),
        "view_count": len(view_ids),
        "export_size": len(live),
    }


def render(a):
    ents = a["entities"]
    counts = collections.Counter(i["class"] for i in ents.values())
    out = []
    w = out.append
    w("# CasaRay dashboard audit")
    w("")
    w("*Generated by `scripts/audit_casaray.py` — do not edit by hand; run it "
      "again. Deterministic, so CI can check it for drift.*")
    w("")
    w("**What this is and is not.** An offline classification of every "
      "dependency `dashboards/casaray_v2.yaml` has, made from the repository "
      "and the 05/09 entity export. It says what the repository can know. It "
      "does **not** say what renders today: the export's availability column "
      "is a snapshot and goes stale (CLAUDE.md), and nothing here has seen the "
      "running instance. `working` therefore means *nothing in the repository "
      "contradicts it*.")
    w("")
    w("## Summary")
    w("")
    w(f"- {a['view_count']} views, {len(ents)} distinct entity references, "
      f"{a['export_size']} entities in the export")
    w("")
    w("| Class | Count |")
    w("|---|---|")
    for c in CLASSES:
        n = counts.get(c, 0) if c != "obsolete" else len(a["obsolete"])
        w(f"| {c} | {n} |")
    w("")
    w(f"- navigation targets that do not exist: **{len(a['bad_nav'])}**"
      + (f" ({', '.join(a['bad_nav'])})" if a["bad_nav"] else ""))
    w(f"- views with no inbound link from any card: "
      f"**{len(a['unreachable_views'])}**"
      + (f" ({', '.join(a['unreachable_views'])})"
         if a["unreachable_views"] else ""))
    w(f"- custom card types: "
      + (", ".join(f"`{k}` ×{n}" for k, n in sorted(a["custom_cards"].items()))
         or "none"))
    w(f"- card types outside the audit's native list: "
      + (", ".join(f"`{k}` ×{n}" for k, n in sorted(
          a["unknown_card_types"].items())) or "none"))
    if a["theme"]:
        w(f"- dashboard theme `{a['theme']}` declared in "
          f"`themes/deez_your_name.yaml`: **{a['theme_declared']}**")
    w("")

    w("## Views")
    w("")
    w("| View | Refs | working | stateless | live_check | likely_broken | "
      "confirmed_broken |")
    w("|---|---|---|---|---|---|---|")
    for path, n, c in a["views"]:
        w(f"| {path} | {n} | {c['working']} | {c['stateless']} | "
          f"{c['live_check']} | {c['likely_broken']} | "
          f"{c['confirmed_broken']} |")
    w("")

    for cls, title in (("confirmed_broken", "Confirmed broken"),
                       ("likely_broken", "Likely broken"),
                       ("live_check", "Live check required")):
        rows = [(e, i) for e, i in ents.items() if i["class"] == cls]
        w(f"## {title} ({len(rows)})")
        w("")
        if not rows:
            w("None.")
            w("")
            continue
        w("| Entity | Name | Why | Views |")
        w("|---|---|---|---|")
        for e, i in rows:
            w(f"| `{e}` | {i['name'] or '—'} | {i['reason']} | "
              f"{', '.join(i['views'])} |")
        w("")

    w("## Helpers the repository cannot rebuild")
    w("")
    w("These entities are defined by Home Assistant itself (helpers, scripts, "
      "automations). Their *definitions* are not in Git, so if they were "
      "YAML-defined in the lost `configuration.yaml` they cannot be recreated "
      "from here without inventing their settings. They were `ok` on 05/09.")
    w("")
    by_dom = collections.defaultdict(list)
    for e in a["helpers_external"]:
        by_dom[e.split(".")[0]].append(e)
    for dom in sorted(by_dom):
        w(f"- **{dom}** ({len(by_dom[dom])}): "
          + ", ".join(f"`{e.split('.', 1)[1]}`" for e in by_dom[dom]))
    w("")
    w(f"Defined in Git (`packages/`): "
      + (", ".join(f"`{e}`" for e in a["helpers_in_git"]) or "none"))
    w("")

    w("## Obsolete twins — do not reference these")
    w("")
    for e in sorted(a["obsolete"]):
        w(f"- `{e}` — {a['obsolete'][e]}")
    w("")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    a = audit()
    if args.json:
        json.dump(a, sys.stdout, indent=1, sort_keys=True, default=str)
        print()
        return 0
    text = render(a)
    broken = [e for e, i in a["entities"].items()
              if i["class"] == "confirmed_broken"]
    if args.check:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if have != text:
            print("docs/CASARAY_AUDIT.md is out of date — run "
                  "python3 scripts/audit_casaray.py", file=sys.stderr)
            return 1
        print("audit report up to date")
    else:
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {os.path.relpath(OUT, ROOT)}")
    if args.strict and (broken or a["bad_nav"]):
        print(f"{len(broken)} confirmed-broken reference(s), "
              f"{len(a['bad_nav'])} bad nav target(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
