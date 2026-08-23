#!/usr/bin/env python3
"""Verify the CasaRay dashboard against a live Home Assistant instance.

Read-only by default. It answers the one question this repository refuses to
guess at: what are the real area IDs and entity IDs?

    export HA_URL=http://homeassistant.local:8123
    export HA_TOKEN=<long-lived access token>

    python3 scripts/ha_verify.py            # check only, changes nothing
    python3 scripts/ha_verify.py --write    # also fill in the generated/ files
    python3 scripts/ha_verify.py --inventory  # refresh docs/entity_inventory.md

Only --write and --inventory modify files, and only files under
home-assistant/dashboards/generated/ and docs/entity_inventory.md. The script
never writes to Home Assistant.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DASHBOARD = REPO / "home-assistant" / "dashboards" / "casaray_home.yaml"
GENERATED = REPO / "home-assistant" / "dashboards" / "generated"
INVENTORY = REPO / "docs" / "entity_inventory.md"

TIMEOUT = 20


# --------------------------------------------------------------- HA plumbing
def _call(path: str, payload: dict | None = None):
    url = os.environ.get("HA_URL", "").rstrip("/")
    token = os.environ.get("HA_TOKEN", "")
    if not url or not token:
        sys.exit("HA_URL and HA_TOKEN must be set. See the docstring at the top "
                 "of this file.")
    req = urllib.request.Request(
        f"{url}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        sys.exit(f"Home Assistant returned {e.code} for {path}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach Home Assistant at {url}: {e.reason}")
    return body


def tpl_json(tpl: str):
    """Render a Jinja template server-side and parse its JSON result."""
    body = _call("/api/template", {"template": tpl})
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        sys.exit(f"Unexpected /api/template response: {body[:300]}")


def states():
    return json.loads(_call("/api/states"))


def entity_areas() -> dict[str, str]:
    """{entity_id: area_id} for every entity, in a single template call."""
    return tpl_json(
        "{% set ns = namespace(d={}) %}"
        "{% for s in states %}"
        "{% set ns.d = dict(ns.d, **{s.entity_id: (area_id(s.entity_id) or '')}) %}"
        "{% endfor %}"
        "{{ ns.d | tojson }}"
    )


# ------------------------------------------------------------------- checks
def live_areas() -> dict[str, str]:
    """{area_id: area_name} straight from the area registry."""
    ids = tpl_json("{{ areas() | list | tojson }}")
    names = tpl_json("{{ areas() | map('area_name') | list | tojson }}")
    return dict(zip(ids, names))


def dashboard_area_ids() -> list[str]:
    text = DASHBOARD.read_text()
    ids = re.findall(r"^\s*area:\s*([a-z0-9_]+)\s*$", text, re.M)
    for path in sorted(GENERATED.glob("*.yaml")):
        ids += re.findall(r"^\s*area:\s*([a-z0-9_]+)\s*$", path.read_text(), re.M)
    return sorted(set(ids))


def check_areas() -> tuple[dict[str, str], list[str]]:
    live = live_areas()
    used = dashboard_area_ids()
    missing = [a for a in used if a not in live]

    print(f"Areas in Home Assistant: {len(live)}")
    for aid, name in sorted(live.items(), key=lambda kv: kv[1].lower()):
        mark = "used" if aid in used else "    "
        print(f"  [{mark}] {aid:<20} {name}")

    if missing:
        print("\nPROBLEM - these area IDs appear in the dashboard but not in "
              "Home Assistant:")
        import difflib
        for a in missing:
            near = difflib.get_close_matches(a, list(live), n=3, cutoff=0.5)
            hint = ", ".join(f"{i} ({live[i]})" for i in near)
            print(f"  {a}" + (f"   did you mean: {hint}" if hint else ""))
        print("\nFix them in home-assistant/dashboards/casaray_home.yaml before "
              "installing the dashboard. Cards pointing at a missing area render "
              "empty.")
    else:
        print("\nAll area IDs used by the dashboard exist. Good to install.")
    return live, missing


# ------------------------------------------------------- generated: cameras
def write_cameras(live: dict[str, str]) -> None:
    cams = [s for s in states() if s["entity_id"].startswith("camera.")]
    if not cams:
        print("No camera entities found; leaving generated/cameras.yaml alone.")
        return

    area_of = entity_areas()

    groups: dict[str, list[dict]] = {}
    for c in cams:
        groups.setdefault(area_of.get(c["entity_id"], ""), []).append(c)

    out = [
        "# GENERATED by scripts/ha_verify.py --write -- do not hand-edit.",
        "# Every entity ID below was read from the live Home Assistant registry.",
        "",
        "- type: grid",
        "  column_span: 3",
        "  cards:",
        "    - type: heading",
        "      heading: Cameras",
        "      heading_style: title",
        "      icon: mdi:cctv",
    ]
    for aid in sorted(groups, key=lambda a: live.get(a, "zzz").lower()):
        label = live.get(aid, "Unassigned")
        out += ["- type: grid",
                "  cards:",
                "    - type: heading",
                f"      heading: {json.dumps(label)}",
                "      heading_style: subtitle",
                "      icon: mdi:cctv"]
        for c in sorted(groups[aid], key=lambda c: c["entity_id"]):
            name = c["attributes"].get("friendly_name", c["entity_id"])
            out += ["    - type: picture-glance",
                    f"      title: {json.dumps(name)}",
                    f"      camera_image: {c['entity_id']}",
                    "      camera_view: auto",
                    "      entities: []"]
    (GENERATED / "cameras.yaml").write_text("\n".join(out) + "\n")
    print(f"Wrote generated/cameras.yaml with {len(cams)} cameras.")


# -------------------------------------------------------- generated: badges
def write_badges() -> None:
    path = GENERATED / "home_badges.yaml"
    text = path.read_text()
    text = re.sub(r"\n*# GENERATED HEAD.*?# END GENERATED HEAD\n*", "\n\n",
                  text, flags=re.S)

    all_states = states()
    weather = [s["entity_id"] for s in all_states
               if s["entity_id"].startswith("weather.")]
    people = sorted(s["entity_id"] for s in all_states
                    if s["entity_id"].startswith("person."))

    head = ["# GENERATED HEAD - written by scripts/ha_verify.py --write."]
    for eid in weather[:1]:
        head += ["- type: entity", f"  entity: {eid}", "  display_type: complete"]
    for eid in people:
        head += ["- type: entity", f"  entity: {eid}", "  show_name: true"]
    head += ["# END GENERATED HEAD", ""]


    lines = text.split("\n")
    insert = next((i for i, l in enumerate(lines)
                   if l.startswith("- type:")), len(lines))
    path.write_text("\n".join(lines[:insert] + head + lines[insert:]))
    print(f"Wrote generated/home_badges.yaml "
          f"({len(weather[:1])} weather, {len(people)} people).")


# ----------------------------------------------------------------- inventory
def write_inventory(live: dict[str, str]) -> None:
    area_of = entity_areas()
    rows = []
    for s in sorted(states(), key=lambda s: s["entity_id"]):
        eid = s["entity_id"]
        rows.append((eid, s["attributes"].get("friendly_name", ""),
                     eid.split(".")[0], live.get(area_of.get(eid, ""), ""),
                     s["state"]))

    from datetime import datetime, timezone
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    body = [
        "# Entity Inventory",
        "",
        f"Status: **VERIFIED** against the live instance at {stamp}.",
        "",
        "Generated by `scripts/ha_verify.py --inventory`. Do not hand-edit; "
        "re-run the script instead.",
        "",
        f"{len(rows)} entities across {len(live)} areas.",
        "",
        "## Areas",
        "",
        "| area_id | name |",
        "|---|---|",
    ]
    body += [f"| `{a}` | {n} |" for a, n in sorted(live.items(),
                                                   key=lambda kv: kv[1].lower())]
    body += ["", "## Entities", "",
             "| entity_id | friendly_name | domain | area | state |", "|---|---|---|---|---|"]
    body += [f"| `{e}` | {f} | {d} | {a} | `{st}` |" for e, f, d, a, st in rows]
    INVENTORY.write_text("\n".join(body) + "\n")
    print(f"Wrote docs/entity_inventory.md with {len(rows)} entities.")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--write", action="store_true",
                   help="fill in home-assistant/dashboards/generated/ from live data")
    p.add_argument("--inventory", action="store_true",
                   help="regenerate docs/entity_inventory.md from live state")
    args = p.parse_args()

    live, missing = check_areas()
    if args.write:
        print()
        write_cameras(live)
        write_badges()
    if args.inventory:
        print()
        write_inventory(live)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
