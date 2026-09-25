#!/usr/bin/env python3
"""Fail if the V3 prototype or its mapping doc names an entity ID that is not
in docs/live/states_export_2026-09-05.txt.

The export is the repository's authority for which IDs exist (CLAUDE.md).
It is NOT authoritative for availability today; see ENTITY_MAPPING.md.
Run from anywhere: python3 design/casaray-v3/tools/verify_entities.py
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
V3 = HERE.parent
ROOT = V3.parent.parent
EXPORT = ROOT / "docs/live/states_export_2026-09-05.txt"
DOMAINS = (
    "binary_sensor|button|camera|climate|cover|event|fan|input_boolean|input_datetime|"
    "input_number|input_select|input_text|light|media_player|number|person|remote|scene|"
    "script|select|sensor|siren|switch|todo|update|weather|zone|device_tracker|automation"
)
ID = re.compile(rf"\b(?:{DOMAINS})\.[a-z0-9_]+\b")

known = {line.split("|", 1)[0] for line in EXPORT.read_text().splitlines() if "|" in line}
targets = sorted((V3 / "prototype").glob("*.js")) + [V3 / "ENTITY_MAPPING.md"]
bad, seen = [], set()
for path in targets:
    if not path.exists() or path.name == "icons.js":
        continue
    for n, line in enumerate(path.read_text().splitlines(), 1):
        for eid in ID.findall(line):
            seen.add(eid)
            if eid not in known:
                bad.append(f"{path.relative_to(ROOT)}:{n}: {eid}")
print(f"{len(seen)} distinct entity IDs checked against {EXPORT.name} ({len(known)} known)")
if bad:
    print("NOT IN EXPORT:\n  " + "\n  ".join(bad))
    sys.exit(1)
print("OK — every referenced ID exists in the export")
