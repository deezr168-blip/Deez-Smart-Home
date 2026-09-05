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
    raw = open(path, encoding="utf-8").read()
    return {e for e in re.findall(r"\b([a-z_]+\.[a-z0-9_]+)\b", raw)
            if e.split(".")[0] in DOMAINS}


def main():
    if not os.path.exists(EXPORT):
        sys.exit(f"missing {EXPORT} — the export is the authority here, and "
                 f"there is nothing to reconcile against without it")
    live = load_export(EXPORT)
    print(f"  export: {len(live)} entities  ({EXPORT})")

    targets = sys.argv[1:] or DEFAULT
    failed = False
    for path in targets:
        refs = references(path)
        services = {e for e in refs if SERVICE_CALLS.match(e)}
        entities = refs - services
        missing = sorted(entities - live.keys())
        avail = collections.Counter(live[e][2] for e in entities if e in live)

        print(f"\n  --- {path} ---")
        print(f"  entity references        : {len(entities)}"
              f"  (+{len(services)} service names)")
        print(f"  ok / unknown / unavail   : {avail['ok']} / "
              f"{avail['unknown']} / {avail['unavailable']}")

        for e in sorted(entities):
            if e in live and live[e][2] == "unavailable":
                name, area, _ = live[e]
                print(f"    offline  {e}  ({name}, {area or 'no area'})")

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
