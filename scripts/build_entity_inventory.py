#!/usr/bin/env python3
"""Turn a Home Assistant Assist live-context snapshot into docs/entity_inventory.md.

The Assist context is the only authoritative view of the live system available to
this repository's tooling, so the inventory is generated from it rather than
maintained by hand. See docs/entity_inventory.md for what the snapshot does and
does not contain.

Usage:
    python3 scripts/build_entity_inventory.py snapshots/<file> [-o docs/entity_inventory.md]

The input may be either the raw MCP tool result (``{"success": ..., "result": "..."}``)
or the plain text of the context itself.
"""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ha_snapshot import STATELESS_DOMAINS, load  # noqa: E402


def escape_cell(text: str) -> str:
    return text.replace("|", r"\|")


def repo_relative(path: Path) -> str:
    """Path as written in the regenerate banner.

    Kept relative to the repository root so the generated file is identical
    whether the script was invoked with a relative or absolute path.
    """
    repo = Path(__file__).resolve().parent.parent
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def render(entities: list[dict], source: Path) -> str:
    by_area: dict[str, list[dict]] = collections.defaultdict(list)
    for entity in entities:
        by_area[entity["area"] or "Unassigned"].append(entity)

    domains = collections.Counter(e["domain"] for e in entities)
    unavailable = [e for e in entities if e["state"] == "unavailable"]

    out: list[str] = []
    add = out.append

    add("# Entity Inventory")
    add("")
    add("> **Generated file — do not edit by hand.**")
    add("> Regenerate with "
        f"`python3 scripts/build_entity_inventory.py {repo_relative(source)}`.")
    add("")
    add("## How this was produced")
    add("")
    add("This inventory is generated from a Home Assistant **Assist live-context "
        "snapshot**, which is the authoritative live view available to this "
        "repository's tooling.")
    add("")
    add("Two limitations follow from that source, and both matter when writing "
        "dashboards or automations:")
    add("")
    add("1. **No entity IDs.** The Assist context reports friendly names, domains, "
        "areas and states, but not canonical `domain.object_id` entity IDs. "
        "Entity IDs in this repository must be confirmed against Home Assistant "
        "itself (Developer Tools → States) before being referenced in YAML. "
        "Names below are *not* a substitute for an entity ID.")
    add("2. **Assist-exposed entities only.** Entities hidden from Assist do not "
        "appear here, so this is a lower bound on what exists. Notably, no "
        "`automation`, `script`, or `alarm_control_panel` entities are present in "
        "the snapshot; that means they are not exposed to Assist, not that none "
        "are configured.")
    add("")
    add("## Summary")
    add("")
    add(f"- **Entities captured:** {len(entities)}")
    add(f"- **Areas:** {len([a for a in by_area if a != 'Unassigned'])} "
        f"(+{len(by_area.get('Unassigned', []))} entities with no area)")
    add(f"- **Domains:** {len(domains)}")
    add(f"- **Currently unavailable:** {len(unavailable)}")
    add("")
    add("### Entities per domain")
    add("")
    add("| Domain | Count |")
    add("| --- | ---: |")
    for domain, count in sorted(domains.items(), key=lambda kv: (-kv[1], kv[0])):
        add(f"| `{domain}` | {count} |")
    add("")
    add("### Entities per area")
    add("")
    add("| Area | Count | Unavailable |")
    add("| --- | ---: | ---: |")
    for area in sorted(by_area, key=lambda a: (a == "Unassigned", a.lower())):
        items = by_area[area]
        bad = sum(1 for e in items if e["state"] == "unavailable")
        add(f"| {escape_cell(area)} | {len(items)} | {bad or ''} |")
    add("")
    add("## Entities by area")
    add("")
    add("`unavailable` states are flagged. A `unknown` state on a stateless domain "
        f"({', '.join('`' + d + '`' for d in sorted(STATELESS_DOMAINS))}) is normal "
        "and is not flagged.")
    add("")

    for area in sorted(by_area, key=lambda a: (a == "Unassigned", a.lower())):
        items = sorted(by_area[area], key=lambda e: (e["domain"], e["name"].lower()))
        add(f"### {area}")
        add("")
        add("| Domain | Name | State | Unit / class |")
        add("| --- | --- | --- | --- |")
        for entity in items:
            attrs = entity["attrs"]
            meta = " ".join(
                part for part in (
                    attrs.get("unit_of_measurement", ""),
                    f"({attrs['device_class']})" if attrs.get("device_class") else "",
                ) if part
            )
            state = entity["state"]
            flag = " ⚠️" if state == "unavailable" else ""
            state_cell = f"`{state}`{flag}" if state else "—"
            add(f"| `{entity['domain']}` | {escape_cell(entity['name'])} "
                f"| {state_cell} | {escape_cell(meta) or '—'} |")
        add("")

    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Assist live-context snapshot")
    parser.add_argument("-o", "--output", type=Path,
                        default=Path("docs/entity_inventory.md"))
    args = parser.parse_args(argv)

    entities = load(args.snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(entities, args.snapshot), encoding="utf-8")
    print(f"Wrote {args.output} ({len(entities)} entities)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
