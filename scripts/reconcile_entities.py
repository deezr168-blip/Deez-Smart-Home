#!/usr/bin/env python3
"""Reconcile dashboard entity references against the B1 live export.

Read-only. Never contacts Home Assistant — it compares two files that are
already in the repository:

  dashboards/*.yaml                        what the cards reference
  docs/live/states_export_2026-09-05.txt   what the instance actually has

The export is a Developer Tools template dump of every entity, one per line
as `entity_id|friendly name|area|availability`. It deliberately carries no
state values, so no addresses, coordinates or readings are in the repository.

Exits non-zero if a dashboard references an entity the export does not have.
That is the check worth gating on: an invented entity ID renders as a blank
or an error on a wall panel, and is the single easiest mistake to make when
building cards from a design rather than from the instance.

Usage:
    python3 scripts/reconcile_entities.py [dashboard ...]

With no arguments it reconciles the canonical dashboard, casaray_v2.yaml.
"""

import collections
import os
import re
import sys

EXPORT = "docs/live/states_export_2026-09-05.txt"
DEFAULT = ["dashboards/casaray_v2.yaml"]

# `<domain>.turn_on` and friends are service names, not entities. They appear
# in `perform_action:` and are correct; the export will never carry them.
SERVICE_CALLS = re.compile(r"^[a-z_]+\.(turn_on|turn_off|toggle|"
                           r"select_option|set_value|reload|press)$")

# Live observations verified individually against the instance on a known date.
# Optional: absent, every count below still computes, `recovered` is simply 0.
OBSERVATIONS = "docs/live/observations_2026-09-17.txt"

# Domains where `unknown` is the resting state, not a fault.
#
# A `scene`'s state is the timestamp it was last ACTIVATED; a `button`'s is the
# timestamp it was last PRESSED. Neither holds a reading. Before the first
# activation after a restart both are legitimately `unknown`, and 17 of this
# dashboard's references sat in that bucket while being perfectly healthy --
# verified live on 2026-09-17, every one of them present and responding.
#
# This list is deliberately TWO domains long. It must never grow to include a
# domain that carries a reading or a position: for `sensor`, `binary_sensor`,
# `light`, `switch`, `media_player`, `camera`, `climate`, `cover`, `fan`,
# `lock`, `number`, `select` and friends, `unknown` means the card is about to
# render a blank where a value belongs, which is exactly what this tool exists
# to catch. Widening it would hide real faults to make a number look better.
BENIGN_UNKNOWN_DOMAINS = {"scene", "button"}

DOMAINS = {
    "light", "switch", "sensor", "binary_sensor", "media_player", "climate",
    "fan", "cover", "scene", "script", "automation", "input_boolean",
    "input_number", "input_select", "input_text", "input_datetime", "camera",
    "person", "device_tracker", "todo", "weather", "number", "select",
    "button", "event", "remote", "zone", "update", "sun", "lock", "vacuum",
}


def load_export(path):
    """{entity_id: (name, area, availability)} from the B1 export."""
    live = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("|")
            if len(parts) >= 4 and "." in parts[0]:
                live[parts[0]] = (parts[1], parts[2], parts[3])
    return live


def references(path):
    """Entity IDs a dashboard actually uses, ignoring comments.

    Comments legitimately name entities the cards must NOT use -- a dead
    duplicate, the reason an ID was changed, an entity deliberately left off.
    Counting those as references makes the offline list wrong and would push
    an author to write worse comments to keep a tool quiet.

    Whole-line comments only. Every comment in these files is one, and a `#`
    inside a value (a colour, a card_mod style) is not a comment.
    """
    raw = open(path, encoding="utf-8").read()
    body = "\n".join(l for l in raw.split("\n") if not l.lstrip().startswith("#"))
    return {e for e in re.findall(r"\b([a-z_]+\.[a-z0-9_]+)\b", body)
            if e.split(".")[0] in DOMAINS}


def load_observations(path):
    """{entity_id: (observed_state, verdict)} from the dated overlay.

    Optional by design. The overlay records entities whose live state was
    checked individually on a known date; it never introduces an entity ID the
    export does not already carry, and it is not a second export.
    """
    obs = {}
    if not os.path.exists(path):
        return obs
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) >= 3 and "." in parts[0]:
                obs[parts[0]] = (parts[1], parts[2])
    return obs


def duplicate_names(live):
    """(domain, friendly name) pairs carried by more than one entity.

    A reference to such an entity is not wrong -- the ID is exact -- but it
    cannot be confirmed to point at the INTENDED one, because this instance
    carries stale duplicates that share a name, an area and a domain with the
    entity that still works. That is CR-190, and it is why a mapping is never
    accepted on name similarity.

    Keyed on DOMAIN AND NAME, not name alone. One device legitimately appears
    under several domains -- a TV is a `media_player` and a `remote`, an air
    purifier is a `fan` and a `switch` -- and they share a friendly name
    because they are the same appliance, not because one is stale. Flagging
    those produced 20 hits where 8 are real; keying on the domain drops every
    cross-domain pair and keeps every same-domain collision.
    """
    counts = collections.Counter(
        (e.split(".", 1)[0], v[0]) for e, v in live.items())
    return {k for k, c in counts.items() if c > 1}


def classify(entity, live, obs, dup_names):
    """One bucket per reference. Order matters; first match wins.

    ambiguous      the name is duplicated, so the reference may be pointing at
                   a dead twin -- the most actionable defect, so it is checked
                   before availability and carved out of the other counts
    benign_unknown scene/button with no activation since restart: not a fault
    recovered      the overlay saw it live after the export called it down
    unavailable    genuinely down, and confirmed so where the overlay reaches
    unresolved     `unknown` in a domain that should carry a value
    live           `ok` in the export
    """
    name, _area, avail = live[entity]
    domain = entity.split(".", 1)[0]

    if (domain, name) in dup_names:
        return "ambiguous"
    if domain in BENIGN_UNKNOWN_DOMAINS and avail == "unknown":
        return "benign_unknown"
    if obs.get(entity, (None, None))[1] == "recovered" and avail != "ok":
        return "recovered"
    if avail == "unavailable":
        return "unavailable"
    if avail == "unknown":
        return "unresolved"
    return "live"


def main():
    if not os.path.exists(EXPORT):
        sys.exit(f"missing {EXPORT} — the export is the authority here, and "
                 f"there is nothing to reconcile against without it")
    live = load_export(EXPORT)
    print(f"  export: {len(live)} entities  ({EXPORT})")

    obs = load_observations(OBSERVATIONS)
    if obs:
        print(f"  overlay: {len(obs)} live observations  ({OBSERVATIONS})")
    else:
        print("  overlay: none — 'recovered' cannot be distinguished from "
              "'unavailable'")
    dup_names = duplicate_names(live)

    targets = sys.argv[1:] or DEFAULT
    failed = False
    for path in targets:
        refs = references(path)
        services = {e for e in refs if SERVICE_CALLS.match(e)}
        entities = refs - services
        missing = sorted(entities - live.keys())

        bucket = {}
        for e in sorted(entities - set(missing)):
            bucket[e] = classify(e, live, obs, dup_names)
        n = collections.Counter(bucket.values())

        print(f"\n  --- {path} ---")
        print(f"  entity references        : {len(entities)}"
              f"  (+{len(services)} service names)")
        # One machine-greppable line; ha_validate.sh surfaces this.
        print(f"  counts: live {n['live']} / recovered {n['recovered']} / "
              f"benign-unknown {n['benign_unknown']} / unavailable "
              f"{n['unavailable']} / ambiguous {n['ambiguous']} / unresolved "
              f"{n['unresolved']}")

        resolved = n["live"] + n["recovered"] + n["benign_unknown"] + n["unavailable"]
        print(f"  accounted for            : {resolved + n['ambiguous'] + n['unresolved']}"
              f" of {len(entities)}")

        for e, b in bucket.items():
            if b != "ambiguous":
                continue
            name, area, _ = live[e]
            twins = sorted(k for k, v in live.items()
                           if v[0] == name and k != e
                           and k.split(".", 1)[0] == e.split(".", 1)[0])
            print(f"    AMBIGUOUS  {e}  ({name}, {area or 'no area'})")
            for t in twins:
                print(f"               shares its name with  {t}")

        for e, b in bucket.items():
            if b != "unavailable":
                continue
            name, area, _ = live[e]
            seen = obs.get(e, (None, None))[1]
            note = "  [confirmed live-down]" if seen == "confirmed_unavailable" else ""
            print(f"    offline  {e}  ({name}, {area or 'no area'}){note}")

        for e, b in bucket.items():
            if b != "unresolved":
                continue
            name, area, _ = live[e]
            print(f"    unresolved  {e}  ({name}, {area or 'no area'})")

        if n["ambiguous"]:
            print(f"  WARN  {n['ambiguous']} reference(s) share a friendly name "
                  f"with another entity.\n        The ID is exact, but it cannot "
                  f"be confirmed to be the WORKING twin\n        rather than the "
                  f"stale one. Resolve from Developer Tools → States.")

        if missing:
            failed = True
            print(f"  NOT IN THE EXPORT        : {len(missing)}")
            for e in missing:
                print(f"    MISSING  {e}")

    if failed:
        print("\n  FAIL  a dashboard references an entity the instance does "
              "not have.\n        Either the ID is wrong or the export is "
              "stale — check before\n        assuming which.")
        return 1
    print("\n  ok    every entity reference resolves against the export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
