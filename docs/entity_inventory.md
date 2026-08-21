# Home Assistant Entity Inventory

This document is a factual inventory of entities and configuration
discovered by directly inspecting the **live, connected Home Assistant
instance**. Nothing in this file is invented — every entity listed here
must come from a real read via the Home Assistant connector (e.g.
`GetLiveContext`) or from actual repository config once imported.

Status: **populating.** The connector only exposes live entity *state*
(no raw YAML/config export — see `docs/live_ha_blockers.md` for what the
connector can and cannot read/write). This file will be filled in with the
full entity list, grouped by domain and area, from a live read.

## How this is generated

- Source: `mcp__Home_Assistant__GetLiveContext` (and related read-only
  Home Assistant connector tools), queried against the live instance.
- Last refreshed: 2026-08-21
- Refresh process: re-run a live inspection and update this file — do not
  hand-edit entity IDs from memory or guesswork.

## Summary

_Pending — full domain/area breakdown to be added from the live read._

## Entities by domain

_Pending._

## Notes

- If an entity appears here, it was confirmed present on the live instance
  at the time of the refresh noted above. Entities may be added, renamed,
  or removed over time — always re-verify before relying on an entity ID
  in an automation, script, or dashboard.
