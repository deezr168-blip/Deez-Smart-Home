#!/usr/bin/env python3
"""Find friendly names that carry more than one entity_id, and say which one
each dashboard uses.

WHY THIS EXISTS

This instance re-adds devices rather than renaming them, so the entity registry
accumulates twins: `switch.k_bot_p100` and `switch.kitchen_k_bot_p100`,
`binary_sensor.b_contact_sensor_door` and
`binary_sensor.backyard_b_contact_sensor_door`. Both carry the same friendly
name. One answers and one does not, and the export lists both.

Wiring a card to the wrong twin produces a tile that is permanently dead and
looks like a device fault. That is exactly what happened to the Sensibo air
conditioner (DR-015): three cards rendered "Entity not found" on the wall for
two weeks, and the gate passed them because the export vouched for the IDs.

`reconcile_entities.py` catches an ID that is *known* dead, once someone has
put it in the STALE map. This finds the candidates in the first place.

WHAT IT CANNOT DO

Decide which twin is live. The export's availability column is a snapshot and
goes stale — on 2026-09-19 the three contact sensors were reporting normally
while the 2026-09-05 export still listed them `unavailable`. Home Assistant's
own `GetLiveContext` returns friendly names, not IDs, so it cannot tell two
twins apart either.

So this script reports and ranks; a human with Developer Tools decides. Rows
marked CHECK are the ones worth looking up.

USAGE

  audit_duplicate_entities.py
  audit_duplicate_entities.py --export docs/live/states_export_2026-10-01.txt
  audit_duplicate_entities.py --unused        # candidates not on any dashboard

EXIT STATUS

  0  no dashboard references a twin that the export marks unavailable
  1  at least one does — look at it before it reaches the wall
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_EXPORT = "docs/live/states_export_2026-09-05.txt"
DEFAULT_DASHES = ["dashboards/casaray_v2.yaml", "dashboards/deez_smart_home.yaml"]

# A friendly name shared by two entities is not always a duplicate. A modern TV
# exposes the screen and its speaker as separate media_players under one name,
# and the speaker is legitimately unavailable while the set is off. Blocklisting
# one of those would fire the moment someone turned the television on.
SPEAKER_ENDPOINT = re.compile(r"media_player\.")


def load_export(path: pathlib.Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.count("|") != 3:
            continue
        eid, name, area, avail = (p.strip() for p in line.split("|"))
        rows.append((eid, name, area, avail))
    return rows


def references(paths):
    """Entity IDs each dashboard actually uses, excluding comment mentions.

    A comment naming the dead twin to explain why it is NOT used is the
    opposite of a defect, and counting it as a reference was the first thing
    this audit got wrong.
    """
    used = {}
    for rel in paths:
        f = REPO / rel
        if not f.exists():
            continue
        body = "\n".join(
            line.split("#", 1)[0] if line.lstrip().startswith("#") else line
            for line in f.read_text(encoding="utf-8").splitlines())
        used[rel] = body
    return used


def cited(body: str, eid: str) -> bool:
    # Word boundary: `light.dining` must not match inside `light.dining_dining`.
    return re.search(re.escape(eid) + r"(?![A-Za-z0-9_])", body) is not None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", default=DEFAULT_EXPORT)
    ap.add_argument("--dashboard", action="append", default=[])
    ap.add_argument("--unused", action="store_true",
                    help="also list twins no dashboard references")
    args = ap.parse_args()

    export = REPO / args.export
    if not export.exists():
        sys.exit(f"no export at {export}")
    rows = load_export(export)
    bodies = references(args.dashboard or DEFAULT_DASHES)

    groups = collections.defaultdict(list)
    for eid, name, area, avail in rows:
        groups[(name, area, eid.split(".")[0])].append((eid, avail))

    dupes = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"export: {export.name}  ({len(rows)} entities)")
    print(f"{len(dupes)} friendly names carry more than one entity_id\n")

    problems, checks, quiet = [], [], []
    for (name, area, domain), ids in sorted(dupes.items()):
        rendered = []
        for eid, avail in sorted(ids):
            where = [d for d, body in bodies.items() if cited(body, eid)]
            rendered.append((eid, avail, where))
        used_dead = [r for r in rendered if r[2] and r[1] == "unavailable"]
        any_used = [r for r in rendered if r[2]]
        all_dark = all(r[1] == "unavailable" for r in rendered)

        if all_dark:
            # Both twins were quiet when the snapshot was taken, so it says
            # nothing about which one is real — the device was simply offline.
            # The three contact sensors looked exactly like this on 05/09 and
            # were reporting normally a fortnight later. Calling this "uses a
            # dead twin" sends someone to rewire a card that is already right.
            bucket, tag = (checks, "INCONCLUSIVE — whole device was offline "
                                   "at export time")
        elif used_dead:
            bucket, tag = problems, "USES A DEAD TWIN"
        elif any_used and any(r[1] == "unavailable" for r in rendered):
            bucket, tag = checks, ("CHECK — speaker endpoint?"
                                   if SPEAKER_ENDPOINT.match(rendered[0][0])
                                   else "CHECK — which twin is real?")
        elif any_used:
            bucket, tag = quiet, "both twins live"
        else:
            if not args.unused:
                continue
            bucket, tag = quiet, "unreferenced"
        bucket.append((name, area, domain, rendered, tag))

    for title, bucket in (("REFERENCES A TWIN THE EXPORT MARKS UNAVAILABLE", problems),
                          ("WORTH A LOOK IN DEVELOPER TOOLS", checks),
                          ("NO ACTION", quiet)):
        if not bucket:
            continue
        print(f"--- {title}")
        for name, area, domain, rendered, tag in bucket:
            print(f"  {name}  [{area or '-'}]   {tag}")
            for eid, avail, where in rendered:
                mark = ",".join(pathlib.Path(w).stem for w in where) or "-"
                print(f"      {avail:<12} {eid:<56} {mark}")
        print()

    print("The export's availability column is a SNAPSHOT. On 2026-09-19 the")
    print("three contact sensors were reporting while the 2026-09-05 export")
    print("still called them unavailable, so treat `unavailable` here as")
    print("'was not answering when this was taken', not as 'dead'.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
