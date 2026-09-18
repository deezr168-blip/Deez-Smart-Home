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


# Entities the export lists as `ok` that the LIVE instance does not have.
#
# The export is a snapshot, and a snapshot of an entity REGISTRY keeps rows for
# devices that have been renamed: both identities are listed, both marked `ok`,
# and only one of them answers. CLAUDE.md already warns that "name similarity
# is not proof" (CR-190); this is the same trap from the other direction, where
# the dead ID is the one that looks authoritative because the export vouches
# for it.
#
# The Sensibo Sky Plus was renamed to "Parents Room AC" at some point before
# 2026-09-05. The export carries all ten `*_parents_room_ac_*` entities AND
# three `master_bedroom_sensibo_sky_plus*` rows. The dashboard used the latter,
# this check passed them, and the wall iPad rendered three orange "Entity not
# found" cards on Climate plus a fourth on Parents Room (19/09 photographs).
#
# Add an ID here when live evidence — a photograph, a Developer Tools lookup,
# a GetLiveContext query — shows the instance does not have it, with the reason
# and the replacement. Removing an entry needs the same kind of evidence.
STALE = {
    "sensor.master_bedroom_sensibo_sky_plus_air_conditioner_mode":
        "renamed device; no live mode sensor exists — read climate."
        "bedroom_parents_room_ac instead (19/09 wall photographs)",
    "sensor.master_bedroom_sensibo_sky_plus_cooling_setpoint":
        "renamed device; the setpoint is the `temperature` attribute of "
        "climate.bedroom_parents_room_ac (19/09 wall photographs)",
    "switch.master_bedroom_sensibo_sky_plus":
        "renamed device; no live bridge switch — the AC's own controls are "
        "switch.bedroom_parents_room_ac_climate_react / _timer "
        "(19/09 wall photographs)",
}


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
        stale = sorted(entities & STALE.keys())
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

        if stale:
            failed = True
            print(f"  IN THE EXPORT BUT DEAD   : {len(stale)}")
            for e in stale:
                print(f"    STALE    {e}\n             {STALE[e]}")

        if missing:
            failed = True
            print(f"  NOT IN THE EXPORT        : {len(missing)}")
            for e in missing:
                print(f"    MISSING  {e}")

    if failed:
        print("\n  FAIL  a dashboard references an entity the instance does "
              "not have.\n        Either the ID is wrong or the export is "
              "stale — check before\n        assuming which. An ID flagged "
              "STALE is in the export and still dead:\n        the export "
              "vouches for a registry row, not for a live entity.")
        return 1
    print("\n  ok    every entity reference resolves against the export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
