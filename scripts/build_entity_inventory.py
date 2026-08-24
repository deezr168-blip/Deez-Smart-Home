#!/usr/bin/env python3
"""Regenerate docs/entity_inventory.md from a Home Assistant live-context dump.

Read-only with respect to Home Assistant: this script never contacts HA. It
parses a dump that a Claude session has already captured, so the inventory in
git always traces back to a real observation rather than to guesswork.

Capture the dump first (Claude session, Home Assistant MCP connector):

    GetLiveContext  ->  saved to a tool-results .txt file

Then:

    python3 scripts/build_entity_inventory.py <dump.txt> > docs/entity_inventory.md

The dump is either the raw JSON envelope {"success": true, "result": "..."} or
the bare YAML-ish listing inside it. Both are accepted.

Known limitation, deliberately surfaced in the output: the Assist/MCP channel
reports friendly names, domains, areas and states, but NOT entity_ids. This
script therefore never emits an entity_id column. Entity IDs must come from the
entity registry over an authenticated REST/WebSocket session, and must never be
inferred from a friendly name.
"""

import collections
import json
import re
import sys
from datetime import datetime, timezone

FIELD_RE = re.compile(r"^  ([a-z_]+): (.*)$")
ATTR_RE = re.compile(r"^    ([a-z_]+): (.*)$")
NAME_RE = re.compile(r"^- names: (.*)$")

# "unavailable" means HA cannot currently talk to the thing — a real fault.
# "unknown" is different, and for some domains it is entirely normal: a scene,
# button or event entity holds the timestamp of its last activation, so it
# reads "unknown" simply because it has never been triggered. Conflating the
# two produces a scary-looking number that is mostly noise, so keep them apart.
UNAVAILABLE = "unavailable"
UNKNOWN = "unknown"
STATELESS_DOMAINS = {"scene", "button", "event", "notify"}


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def load_dump(path):
    """Return the listing text from either the JSON envelope or a bare dump."""
    raw = open(path, encoding="utf-8").read()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(parsed, dict) and isinstance(parsed.get("result"), str):
        return parsed["result"]
    raise SystemExit(f"{path}: JSON parsed but has no string 'result' field")


def parse(text):
    """Parse the listing into records. Unrecognised lines are ignored."""
    records = []
    current = None
    for line in text.split("\n"):
        name_match = NAME_RE.match(line)
        if name_match:
            if current:
                records.append(current)
            current = {"name": unquote(name_match.group(1)), "attributes": {}}
            continue
        if current is None:
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            current[field_match.group(1)] = unquote(field_match.group(2))
            continue
        attr_match = ATTR_RE.match(line)
        if attr_match:
            current["attributes"][attr_match.group(1)] = unquote(attr_match.group(2))
    if current:
        records.append(current)
    return records


def cell(value):
    """Escape a value for use inside a markdown table cell."""
    return str(value).replace("|", "\\|").strip() or "—"


def area_of(record):
    return record.get("areas") or "(no area assigned)"


def detail_of(record):
    attrs = record["attributes"]
    bits = []
    if "device_class" in attrs:
        bits.append(attrs["device_class"])
    if "unit_of_measurement" in attrs:
        bits.append(attrs["unit_of_measurement"])
    return ", ".join(bits)


def counted_table(header, counter):
    lines = [f"| {header} | Count |", "|---|---:|"]
    for key, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {cell(key)} | {count} |")
    return lines


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <live-context-dump.txt>")

    records = parse(load_dump(sys.argv[1]))
    if not records:
        raise SystemExit("no entities parsed — is this a GetLiveContext dump?")

    captured = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by_area = collections.Counter(area_of(r) for r in records)
    by_domain = collections.Counter(r.get("domain", "(unknown)") for r in records)

    def state_of(record):
        return record.get("state", "").lower()

    # An entity that is unavailable while another entity of the same name AND
    # domain is reporting normally is almost always an orphaned registry entry
    # — the leftover from a re-paired device or a re-added integration. Those
    # are stale bookkeeping, not an outage, and separating them stops a real
    # outage from being buried under them.
    states_by_identity = collections.defaultdict(list)
    for record in records:
        states_by_identity[(record["name"], record.get("domain"))].append(
            record.get("state", "").lower()
        )

    def has_live_twin(record):
        states = states_by_identity[(record["name"], record.get("domain"))]
        return len(states) > 1 and any(s != UNAVAILABLE for s in states)

    unavailable = [r for r in records if state_of(r) == UNAVAILABLE]
    orphaned = [r for r in unavailable if has_live_twin(r)]
    faulted = [r for r in unavailable if not has_live_twin(r)]
    unknown = [r for r in records if state_of(r) == UNKNOWN]
    unexpected_unknown = [
        r for r in unknown if r.get("domain") not in STATELESS_DOMAINS
    ]
    faults_by_area = collections.Counter(area_of(r) for r in faulted)

    out = []
    add = out.append

    add("# Entity Inventory")
    add("")
    add(f"Status: **VERIFIED against the live instance — {captured}.**")
    add("")
    add("Generated by `scripts/build_entity_inventory.py`. Do not hand-edit: "
        "re-run the script against a fresh capture instead, so this file always "
        "reflects something that was actually observed.")
    add("")
    add(f"- Entities visible to Claude: **{len(records)}**")
    add(f"- Areas: **{len(by_area)}**  |  Domains: **{len(by_domain)}**")
    add(f"- Reporting `unavailable`: **{len(unavailable)}** — of which "
        f"**{len(faulted)}** look genuinely offline and **{len(orphaned)}** "
        "look like orphaned duplicates")
    add(f"- Reporting `unknown`: **{len(unknown)}**, of which "
        f"**{len(unexpected_unknown)}** are outside the normally-stateless "
        "domains")
    add("")
    add("> **Keep this repository private.** The names below identify "
        "household devices, room layout and family members' personal phones. "
        "They are not credentials, but they are not public information "
        "either.")
    add("")
    add("## Important: no entity IDs here, by design")
    add("")
    add("The access path currently available to Claude (the Home Assistant "
        "Assist/MCP connector) reports **friendly names, domains, areas and "
        "states — but not `entity_id`s**. See `docs/access_verification.md`.")
    add("")
    add("So this inventory is **name-keyed, not ID-keyed**. Treat it as a map of "
        "what exists, not as a source of entity IDs.")
    add("")
    add("> **Never infer an `entity_id` from a friendly name in this file.** "
        "Friendly names are not unique here — several devices below share a "
        "name across different domains — and HA's slugification is lossy. "
        "Entity IDs must be read from the entity registry over an "
        "authenticated REST/WebSocket session before anything references them.")
    add("")
    add("## Entities per area")
    add("")
    out.extend(counted_table("Area", by_area))
    add("")
    add("## Entities per domain")
    add("")
    out.extend(counted_table("Domain", by_domain))
    add("")

    if orphaned:
        add("## Probable orphaned duplicates")
        add("")
        add("Each entity below is `unavailable` **while another entity with "
            "the same name and domain is reporting normally**. That pattern "
            "almost always means a stale registry entry left behind when a "
            "device was re-paired or an integration re-added — the live twin "
            "is doing the work.")
        add("")
        add("These inflate the unavailable count without anything actually "
            "being broken, so they are separated out here. Removing one is a "
            "registry deletion and needs the owner's decision; confirm which "
            "of the pair is live first.")
        add("")
        add("| Name | Domain | Area |")
        add("|---|---|---|")
        for r in sorted(orphaned, key=lambda r: (area_of(r), r["name"])):
            add(f"| {cell(r['name'])} | {cell(r.get('domain'))} | "
                f"{cell(area_of(r))} |")
        add("")

    if faulted:
        add("## Entities that look genuinely offline")
        add("")
        add("`unavailable`, with no live twin to explain it. A handful is "
            "ordinary — powered-off equipment, seasonal devices. A **cluster "
            "inside one area** usually means one dead integration or one "
            "offline hub, rather than many independent faults, and is worth "
            "investigating before anything new is built on top of it.")
        add("")
        add("Concentration by area (unavailable / total in that area):")
        add("")
        add("| Area | Unavailable | Total | Share |")
        add("|---|---:|---:|---:|")
        for area, count in sorted(
            faults_by_area.items(),
            key=lambda kv: (-(kv[1] * 100 // by_area[kv[0]]), -kv[1]),
        ):
            share = count * 100 // by_area[area]
            add(f"| {cell(area)} | {count} | {by_area[area]} | {share}% |")
        add("")
        add("<details><summary>Full list of offline entities</summary>")
        add("")
        add("| Name | Domain | Area |")
        add("|---|---|---|")
        for r in sorted(faulted, key=lambda r: (area_of(r), r.get("domain", ""), r["name"])):
            add(f"| {cell(r['name'])} | {cell(r.get('domain'))} | "
                f"{cell(area_of(r))} |")
        add("")
        add("</details>")
        add("")

    if unexpected_unknown:
        add("## Entities reporting `unknown` outside the stateless domains")
        add("")
        add("Scene, button, event and notify entities read `unknown` until "
            "first triggered, which is normal and excluded here. The entities "
            "below are not in that category, so `unknown` may indicate a "
            "sensor that has never reported.")
        add("")
        add("| Name | Domain | Area |")
        add("|---|---|---|")
        for r in sorted(unexpected_unknown, key=lambda r: (area_of(r), r["name"])):
            add(f"| {cell(r['name'])} | {cell(r.get('domain'))} | "
                f"{cell(area_of(r))} |")
        add("")

    add("## Full inventory by area")
    add("")
    for area in sorted(by_area, key=lambda a: (a.startswith("("), a)):
        members = [r for r in records if area_of(r) == area]
        add(f"### {area} ({len(members)})")
        add("")
        add("| Name | Domain | State | Detail |")
        add("|---|---|---|---|")
        for r in sorted(members, key=lambda r: (r.get("domain", ""), r["name"])):
            add(f"| {cell(r['name'])} | {cell(r.get('domain'))} | "
                f"{cell(r.get('state'))} | {cell(detail_of(r))} |")
        add("")

    add("## Change log")
    add("")
    add(f"- {captured} — first live capture: {len(records)} entities across "
        f"{len(by_area)} areas; {len(faulted)} offline, "
        f"{len(orphaned)} probable orphans.")
    add("")

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
