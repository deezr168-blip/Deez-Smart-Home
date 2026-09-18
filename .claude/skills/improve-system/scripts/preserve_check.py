#!/usr/bin/env python3
"""Prove a dashboard change lost nothing it should not have.

WHY THIS EXISTS

The dangerous edits here are structural — splicing sections, rebuilding a
navigation index, rolling a pattern across twenty views. They are done with
scripts against a 12,000-line file, and when one goes slightly wrong it does
not produce invalid YAML. It produces a dashboard that parses, validates, and
is quietly missing a service call or a navigation target.

Two such defects in one session were caught only by comparing the parsed tree
against the previous commit: a rebuild that flattened every button from
`rows: 2` to `rows: 1`, and one that rewrote the language toggle from
`tap_action: {action: toggle}` into a different service call. Both passed
every gate.

WHAT IT COMPARES

Views, cards, unique entity references, navigation targets, service calls, and
optionally the exact rendered property set of the cards in one view. Anything
that moved is named, not just counted.

USAGE

  preserve_check.py                       # working tree vs HEAD
  preserve_check.py --ref 5aa567f         # vs a specific commit
  preserve_check.py --ref HEAD~3 --view home --strict

  # after a rollout, confirm the English rendering is untouched
  preserve_check.py --ref HEAD --view home --lang en

EXIT STATUS

  0  nothing lost (additions are always allowed)
  1  something was removed, or --strict and anything changed at all
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"needs PyYAML: {exc}")

REPO = pathlib.Path(__file__).resolve().parents[4]
DEFAULT_DASH = "dashboards/casaray_v2.yaml"
TOGGLE = "input_boolean.chinese_dashboard"

ACTION_KEYS = ("tap_action", "hold_action", "icon_tap_action",
               "double_tap_action")


def load_ref(ref: str, path: str):
    """Parse the dashboard as of a git ref, or from disk when ref is None."""
    if ref is None:
        return yaml.safe_load(open(REPO / path, encoding="utf-8"))
    out = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"],
                         capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"cannot read {path} at {ref}: {out.stderr.strip()}")
    return yaml.safe_load(out.stdout)


def walk(card, sink):
    """Collect every entity, navigation target and service call in a card."""
    sink["cards"] += 1
    if not isinstance(card, dict):
        return
    if card.get("entity"):
        sink["entities"].add(card["entity"])
    for item in card.get("entities") or []:
        e = item.get("entity") if isinstance(item, dict) else item
        if e:
            sink["entities"].add(e)
    for key in ACTION_KEYS:
        action = card.get(key) or {}
        if not isinstance(action, dict):
            continue
        if action.get("navigation_path"):
            sink["navs"].add(action["navigation_path"])
        for svc_key in ("perform_action", "service"):
            if action.get(svc_key):
                sink["services"].add(action[svc_key])
        if action.get("action") in ("toggle", "more-info", "call-service"):
            sink["services"].add(f"<{action['action']}>")
        target = action.get("target") or {}
        if isinstance(target, dict) and target.get("entity_id"):
            tid = target["entity_id"]
            for e in ([tid] if isinstance(tid, str) else tid):
                sink["entities"].add(e)
    if card.get("card"):
        walk(card["card"], sink)
    for sub in card.get("cards") or []:
        walk(sub, sink)


def inventory(doc):
    sink = {"cards": 0, "entities": set(), "navs": set(), "services": set()}
    sink["views"] = {v.get("path") for v in doc.get("views") or []}
    for view in doc.get("views") or []:
        for section in view.get("sections") or []:
            for card in section.get("cards") or []:
                walk(card, sink)
    return sink


def view_fingerprint(doc, path, lang):
    """Every card in one view, as sorted JSON, for exact comparison.

    `lang` filters by the bilingual `visibility` gate so that a rollout which
    adds Chinese twins can still be checked against the untouched English
    rendering — which is the comparison that actually proves nothing regressed.
    """
    view = next((v for v in doc.get("views") or []
                 if v.get("path") == path), None)
    if view is None:
        return None
    out = []
    for section in view.get("sections") or []:
        for card in section.get("cards") or []:
            vis = (card.get("visibility") or [{}])[0]
            if vis.get("entity") == TOGGLE:
                shown_cn = vis.get("state") == "on"
                if lang == "en" and shown_cn:
                    continue
                if lang == "cn" and not shown_cn:
                    continue
            body = {k: v for k, v in card.items() if k != "visibility"}
            out.append(json.dumps(body, sort_keys=True, ensure_ascii=False))
    return out


def report(name, before, after):
    """Print one line, then name what moved. True when something was lost."""
    gone, added = sorted(before - after), sorted(after - before)
    mark = "LOST" if gone else ("    " if not added else " +  ")
    print(f"  {mark} {name:<20} {len(before):>4} -> {len(after):<4}"
          f"  (-{len(gone)} +{len(added)})")
    for item in gone:
        print(f"         - {item}")
    for item in added:
        print(f"         + {item}")
    return bool(gone)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", default="HEAD", help="git ref to compare against")
    ap.add_argument("--path", default=DEFAULT_DASH)
    ap.add_argument("--view", help="also compare this view card-for-card")
    ap.add_argument("--lang", choices=("en", "cn", "both"), default="en",
                    help="which language's cards to fingerprint (default en)")
    ap.add_argument("--strict", action="store_true",
                    help="fail on additions too, not only removals")
    args = ap.parse_args()

    view_differs = False
    before = inventory(load_ref(args.ref, args.path))
    after = inventory(load_ref(None, args.path))

    print(f"{args.path}: working tree vs {args.ref}\n")
    lost = False
    for key in ("views", "entities", "navs", "services"):
        lost |= report(key, before[key], after[key])

    delta = after["cards"] - before["cards"]
    print(f"       {'cards':<20} {before['cards']:>4} -> {after['cards']:<4}"
          f"  ({delta:+d})")

    if args.view:
        fb = view_fingerprint(load_ref(args.ref, args.path), args.view, args.lang)
        fa = view_fingerprint(load_ref(None, args.path), args.view, args.lang)
        print(f"\n  view {args.view!r}, {args.lang} cards, property-for-property:")
        if fb is None or fa is None:
            print("    view missing on one side")
            lost = True
        elif fb == fa:
            print(f"    identical ({len(fa)} cards)")
        else:
            # A changed card is not a lost one. Report it separately, and show
            # WHAT changed -- truncating to the first 150 characters hides the
            # difference exactly when two cards share a long prefix, which is
            # the normal case for card_mod blocks.
            print(f"    DIFFERS  {len(fb)} -> {len(fa)} cards")
            if len(fb) != len(fa):
                print(f"      card count changed by {len(fa) - len(fb):+d}")
                lost = lost or len(fa) < len(fb)
            for i, (before_card, after_card) in enumerate(zip(fb, fa)):
                if before_card == after_card:
                    continue
                print(f"      card {i}:")
                for line in difflib.unified_diff(
                        re.split(r'(?<=[,{}])\s*', before_card),
                        re.split(r'(?<=[,{}])\s*', after_card),
                        lineterm="", n=0):
                    if line.startswith(("---", "+++", "@@")):
                        continue
                    print(f"        {line.strip()[:180]}")
            view_differs = True

    changed = lost or view_differs or any(
        before[k] != after[k] for k in ("views", "entities", "navs", "services"))
    print()
    if lost:
        print("  SOMETHING WAS LOST. If it was a confirmed-broken reference,")
        print("  say so explicitly in the commit message. Otherwise fix it.")
        return 1
    if view_differs:
        print("  Nothing was lost, but cards in that view CHANGED. Read the")
        print("  diff above and confirm every line is a change you meant to")
        print("  make -- this is where a rollout quietly alters a property it")
        print("  was not supposed to touch.")
        return 1 if args.strict else 0
    if args.strict and changed:
        print("  --strict: the inventory changed. Intended?")
        return 1
    print("  nothing lost.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
