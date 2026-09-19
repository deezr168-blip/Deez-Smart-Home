#!/usr/bin/env python3
"""Render a dashboard's markdown cards across live and dark states.

WHY THIS EXISTS

The validation gates prove a template compiles. They cannot read what it says.
The one class of defect that reaches the wall unchallenged is a card that
renders a confident sentence about entities that are not answering — "All
clear", "No dimmable group is on", "Overdue 0", "Offline" — and the only way
to find it is to render the card against a dark instance and look.

Six ad-hoc variants of this script were written in a single session before it
was bundled. Use this one.

WHAT IT DOES

For each markdown card in the chosen views, renders the template twice per
state set (English and Chinese) and prints the result. States come from:

  --states    a JSON file of {entity_id: state} for the live case; anything
              absent reads 'unknown', which is itself a useful default
  --attrs     a JSON file of {'entity.attribute': value}

The dark pass runs automatically (--no-dark turns it off) and forces every
entity in the live set to 'unavailable', dropping attributes with them — a
device that is not answering does not keep reporting its `temperature`.

--list-entities prints what each card references instead of rendering, marking
anything your state file does not pin down.

USAGE

  render_cards.py --view home
  render_cards.py --view energy --view bills --states my_states.json
  render_cards.py --view security --chips-only --width
  render_cards.py --list-entities --view climate > climate_entities.txt

  # measure every chip strip against the observed wrap limit
  render_cards.py --all --chips-only --width

EXIT STATUS

  0  everything rendered
  1  a template raised, or --width found a strip over budget
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import sys

try:
    import yaml
    from jinja2 import Environment
except ImportError as exc:  # pragma: no cover
    sys.exit(f"needs PyYAML and Jinja2: {exc}")

REPO = pathlib.Path(__file__).resolve().parents[4]
DEFAULT_DASH = REPO / "dashboards" / "casaray_v2.yaml"
# Built by scripts/build_render_fixture.py from the entity export. Real
# availability, invented values -- see that script's header before quoting
# anything that comes out of a render.
FIXTURE = REPO / "docs" / "live" / "fixture_states.json"
TOGGLE = "input_boolean.chinese_dashboard"

# The only width measurement that exists for this dashboard: a photograph of
# the wall iPad on 2026-09-19 showed the Home chip strip wrapping after about
# 45 characters at the default type size. It is an estimate read off an image,
# not a measured pixel width, which is why anything relying on it should leave
# margin rather than land on it.
OBSERVED_CHARS_AT_1EM = 45
PADDING_CHARS = 2


def find_scale(card: dict) -> float:
    """The font-size a card's own card_mod sets, or 1.0."""
    m = re.search(r"font-size:\s*([0-9.]+)em", str(card.get("card_mod", "")))
    return float(m.group(1)) if m else 1.0


def is_chip_strip(card: dict) -> bool:
    return "border-radius: 999px" in str(card.get("card_mod", ""))


def markdown_cards(view: dict, chips_only: bool):
    """Yield (section_index, card_index, card) for each markdown card."""
    for si, section in enumerate(view.get("sections") or []):
        for ci, card in enumerate(section.get("cards") or []):
            for c in (card, card.get("card") if isinstance(card, dict) else None):
                if not isinstance(c, dict) or c.get("type") != "markdown":
                    continue
                if not isinstance(c.get("content"), str):
                    continue
                if chips_only and not is_chip_strip(c):
                    continue
                yield si, ci, c


def entities_in(template: str) -> set[str]:
    return set(re.findall(r"[a-z_]+\.[a-z0-9_]+", template)) & {
        e for e in re.findall(r"['\"]([a-z_]+\.[a-z0-9_]+)['\"]", template)
    }


def build_context(states: dict, cn: bool, now: _dt.datetime, attrs: dict,
                  names: dict | None = None):
    """A Home Assistant-shaped template context.

    `states` is callable AND carries domain attributes, because templates use
    both `states('sensor.x')` and `states.sensor['x'].last_changed`.

    A domain is also ITERABLE, over its state objects, the way it is in Home
    Assistant. That matters more than it looks: `states.update | list` is how
    the House health update card counts, and against an empty domain it
    rendered "All 0 update entities are up to date" -- a reassurance built on
    nothing, in a tool whose job is to catch exactly that.
    """
    st = dict(states)
    st[TOGGLE] = "on" if cn else "off"
    nm = dict(names or {})

    class _Obj:
        def __init__(self, entity_id, value):
            self.entity_id = entity_id
            self.object_id = entity_id.split(".", 1)[-1]
            self.domain = entity_id.split(".", 1)[0]
            self.state = value
            self.name = nm.get(entity_id, self.object_id.replace("_", " ").title())
            self.attributes = {
                k.split(".", 2)[-1]: v for k, v in attrs.items()
                if k.startswith(entity_id + ".")}
            # Far enough back to exercise the "N minutes ago" branches.
            self.last_changed = now - _dt.timedelta(minutes=22)
            self.last_updated = self.last_changed
            self.last_reported = self.last_changed

    class _Domain(dict):
        def __init__(self, name):
            super().__init__()
            self.name = name
            prefix = name + "."
            for eid in st:
                if eid.startswith(prefix):
                    dict.__setitem__(self, eid[len(prefix):], eid)

        def __getitem__(self, key):
            return _Obj(f"{self.name}.{key}",
                        st.get(f"{self.name}.{key}", "unknown"))

        def __getattr__(self, key):
            return self[key]

        def __iter__(self):
            # Home Assistant iterates a domain over its STATE OBJECTS, not its
            # keys. A dict would yield object ids and every `selectattr` on the
            # result would silently match nothing.
            for key in list(dict.keys(self)):
                yield self[key]

    def states_fn(entity=None):
        return st.get(entity, "unknown")

    for domain in ("sensor", "binary_sensor", "switch", "light", "climate",
                   "cover", "media_player", "person", "zone", "camera",
                   "input_boolean", "input_number", "input_datetime",
                   "input_text", "input_select", "automation", "weather",
                   "todo", "siren", "number", "select", "button", "update"):
        setattr(states_fn, domain, _Domain(domain))

    def as_timestamp(value, default="__raise__"):
        if isinstance(value, _dt.datetime):
            return value.timestamp()
        try:
            return _dt.datetime.fromisoformat(str(value)).timestamp()
        except (TypeError, ValueError):
            if default == "__raise__":
                return None
            return default

    return {
        "states": states_fn,
        "is_state": lambda e, v: st.get(e, "unknown") == v,
        "state_attr": lambda e, a: attrs.get(f"{e}.{a}"),
        "now": lambda: now,
        "utcnow": lambda: now,
        "as_timestamp": as_timestamp,
        "as_local": lambda d: d,
    }


def make_env() -> Environment:
    env = Environment()
    env.filters["timestamp_custom"] = (
        lambda t, fmt, local=True: _dt.datetime.fromtimestamp(t).strftime(fmt))
    env.filters["as_timestamp"] = lambda v: (
        v.timestamp() if isinstance(v, _dt.datetime) else None)
    return env


def display_width(text: str) -> int:
    """CJK glyphs render about twice as wide as latin ones."""
    return sum(2 if "一" <= ch <= "鿿" else 1 for ch in text)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dashboard", default=str(DEFAULT_DASH))
    ap.add_argument("--view", action="append", default=[],
                    help="view path; repeatable. Omit with --all for every view.")
    ap.add_argument("--all", action="store_true", help="every view")
    ap.add_argument("--chips-only", action="store_true",
                    help="only the pill-radius chip strips")
    ap.add_argument("--states",
                    help="JSON {entity_id: state} for the populated case. "
                         "Defaults to docs/live/fixture_states.json.")
    ap.add_argument("--no-fixture", action="store_true",
                    help="do not fall back to the committed fixture — every "
                         "entity then reads `unknown`, which is a second dark "
                         "pass, not a live one")
    ap.add_argument("--attrs", help="JSON {'entity.attribute': value}")
    ap.add_argument("--no-dark", action="store_true",
                    help="skip the all-unavailable pass (you usually want it)")
    ap.add_argument("--width", action="store_true",
                    help="measure against the observed wrap limit")
    ap.add_argument("--list-entities", action="store_true",
                    help="list each card's entities instead of rendering")
    args = ap.parse_args()

    doc = yaml.safe_load(open(args.dashboard, encoding="utf-8"))
    views = [v for v in doc["views"]
             if args.all or v.get("path") in args.view]
    if not views:
        return int(bool(sys.stderr.write(
            "no views matched — pass --view <path> or --all\n")))

    # Without a state map every states() call returns `unknown`, so the
    # "live" pass becomes a second dark pass wearing a different label -- and
    # a width measured that way describes an instance where nothing is
    # answering. The committed fixture is the default so that stops happening
    # by accident; `--no-fixture` restores the old behaviour deliberately.
    if args.states:
        live = json.load(open(args.states, encoding="utf-8"))
        case_label = "live"
    elif args.no_fixture or not FIXTURE.exists():
        live = {}
        case_label = "empty"
    else:
        live = json.load(open(FIXTURE, encoding="utf-8"))
        case_label = "fixture"
    # `_meta` and anything else underscored documents the file; it is not an
    # entity and must not be darkened or looked up as one. Its `names` map is
    # kept, because a domain-iterating template asks each state object for its
    # friendly name.
    names = (live.get("_meta") or {}).get("names") or {}
    live = {k: v for k, v in live.items() if not k.startswith("_")}
    attrs = json.load(open(args.attrs)) if args.attrs else {}
    env = make_env()
    now = _dt.datetime(2026, 9, 19, 20, 14, 0)

    # (name, states, attrs). Dark means every entity the live set mentions goes
    # quiet AND every attribute goes with it -- a device that is not answering
    # does not keep reporting its `temperature` attribute, and leaving those in
    # makes a dark render look healthier than the real thing.
    cases = [(case_label, live, attrs)]
    if not args.no_dark:
        # With no live set there is nothing to darken, so darken whatever each
        # card references instead; that is resolved per card below.
        cases.append(("dark", {k: "unavailable" for k in live} if live else None, {}))

    failed = False
    over_budget = []

    for view in views:
        path = view.get("path")
        for si, ci, card in markdown_cards(view, args.chips_only):
            label = f"{path} [section {si}, card {ci}]"

            if args.list_entities:
                refs = sorted(entities_in(card["content"]))
                print(f"\n=== {label}")
                for e in refs:
                    mark = " " if e in live else "?"
                    print(f"  {mark} {e}")
                continue

            print(f"\n=== {label}")
            scale = find_scale(card)
            budget = int(OBSERVED_CHARS_AT_1EM / scale) + PADDING_CHARS

            for case_name, states, case_attrs in cases:
                if states is None:
                    states = {e: "unavailable" for e in entities_in(card["content"])}
                for cn in (False, True):
                    tag = f"{case_name}/{'CN' if cn else 'EN'}"
                    try:
                        out = env.from_string(card["content"]).render(
                            **build_context(states, cn, now, case_attrs,
                                            names)).strip()
                    except Exception as exc:
                        print(f"  {tag:10s} RENDER FAILED: {exc}")
                        failed = True
                        continue
                    plain = out.replace("**", "")
                    if args.width:
                        w = display_width(plain)
                        flag = "OVER" if w > budget else "    "
                        print(f"  {tag:10s} {flag} {w:3d}/{budget}  {plain}")
                        if w > budget:
                            over_budget.append((label, tag, w, budget))
                    else:
                        print(f"  {tag:10s} " + plain.replace("\n", "\n            "))

    if args.width and over_budget:
        print(f"\n{len(over_budget)} rendering(s) over budget "
              f"(budget = {OBSERVED_CHARS_AT_1EM} observed chars / font scale "
              f"+ {PADDING_CHARS} padding):")
        for label, tag, w, budget in over_budget:
            print(f"  {w:3d}/{budget}  {label}  [{tag}]")
        print("\nThe limit is estimated from a photograph, not measured here. "
              "Leave margin rather than landing on it.")
        failed = True

    if not failed:
        print("\nread the output above — a template that compiles can still "
              "assert something it did not measure")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
