#!/usr/bin/env python3
"""Print the per-area entity table for ENTITY_MAPPING.md §2, generated from
the prototype source so the table cannot drift from what the prototype uses.

    python3 design/casaray-v3/tools/gen_entity_table.py
"""
import collections
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROTO = ROOT / "design/casaray-v3/prototype"

exp = {}
for line in (ROOT / "docs/live/states_export_2026-09-05.txt").read_text().splitlines():
    p = line.split("|")
    if len(p) == 4:
        exp[p[0]] = p[1:]
src = (PROTO / "data.js").read_text() + (PROTO / "app.js").read_text()
v2 = (ROOT / "dashboards/casaray_v2.yaml").read_text()
ids = sorted({i for i in re.findall(r"\b[a-z_]+\.[a-z0-9_]+\b", src) if i in exp})

by_area = collections.defaultdict(list)
for i in ids:
    by_area[exp[i][1] if exp[i][1] != "-" else "(no area)"].append(i)
order = ["(no area)", "Living Room", "Dining", "Kitchen", "Parents Room", "Ray Bedroom",
         "Garage", "Guest Room", "Backyard", "Network", "Energy"]
new = 0
for area in order + [a for a in by_area if a not in order]:
    if area not in by_area:
        continue
    print(f"\n### {area}\n\n| Entity ID | Export name | 05/09 | In V2 |\n|---|---|---|---|")
    for i in by_area[area]:
        name = exp[i][0].strip().replace("|", "/").replace("&quot;", '"')
        in_v2 = re.search(r"\b" + re.escape(i) + r"\b", v2) is not None
        new += not in_v2
        print(f"| `{i}` | {name} | {exp[i][2]} | {'yes' if in_v2 else '**new**'} |")
print(f"\n_{len(ids)} entity IDs; {len(ids) - new} already on V2, {new} new to CasaRay._")
