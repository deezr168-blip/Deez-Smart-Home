"""Parsing for Home Assistant Assist live-context snapshots.

Shared by build_entity_inventory.py and diff_snapshots.py.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

HEADER_RE = re.compile(r"^Live Context:")

# Domains whose entities are stateless triggers or activators. Home Assistant
# reports these as "unknown" until first use, which is normal and not a fault.
STATELESS_DOMAINS = frozenset(
    {"button", "event", "scene", "notify", "select", "time"}
)


def load_context(path: Path) -> str:
    """Read a snapshot as either a raw MCP tool result or plain context text."""
    raw = path.read_text(encoding="utf-8")
    if raw.lstrip().startswith("{"):
        payload = json.loads(raw)
        if not payload.get("success", True):
            raise SystemExit(f"{path}: snapshot reports success=false")
        return payload["result"]
    return raw


def parse(context: str) -> list[dict]:
    entities: list[dict] = []
    current: dict | None = None
    in_attrs = False

    for line in context.split("\n"):
        if not line.strip() or HEADER_RE.match(line):
            continue
        if line.startswith("- names: "):
            if current is not None:
                entities.append(current)
            current = {
                "name": html.unescape(line[len("- names: "):]).strip("'"),
                "domain": "",
                "state": "",
                "area": "",
                "attrs": {},
            }
            in_attrs = False
        elif current is None:
            continue
        elif line.startswith("  domain: "):
            current["domain"] = line[len("  domain: "):]
            in_attrs = False
        elif line.startswith("  state: "):
            current["state"] = line[len("  state: "):].strip().strip("'")
            in_attrs = False
        elif line.startswith("  areas: "):
            current["area"] = line[len("  areas: "):]
            in_attrs = False
        elif line.strip() == "attributes:":
            in_attrs = True
        elif in_attrs and line.startswith("    "):
            key, _, value = line.strip().partition(": ")
            current["attrs"][key] = value.strip().strip("'")

    if current is not None:
        entities.append(current)
    return entities


def load(path: Path) -> list[dict]:
    entities = parse(load_context(path))
    if not entities:
        raise SystemExit(f"{path}: no entities parsed — is this a snapshot?")
    return entities


def key(entity: dict) -> tuple[str, str, str]:
    """Identity used to match an entity across snapshots.

    The Assist context exposes no entity IDs, so name+domain+area is the best
    available identity. Duplicate friendly names exist in this system (see
    docs/health_report.md finding 3), so callers must handle repeated keys
    rather than assuming uniqueness.
    """
    return (entity["name"], entity["domain"], entity["area"])
