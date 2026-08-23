# Entity Inventory

Status: **NOT VERIFIED — not yet populated.**

This file is the source of truth for known Home Assistant entities, used to
validate live entity IDs before any automation/dashboard/script work
references them. It intentionally contains no entity IDs yet — none have
been pulled from a live Home Assistant instance in this repository's
context, and IDs must never be invented or guessed.

## How this gets populated (Stage 2)

Once read access to the Home Assistant REST/WebSocket API is configured and
verified (see `docs/access_verification.md` once that stage runs), this
file will be filled in from:

- Live state (`GET /api/states`)
- Entity registry (`config/entity_registry/list` over WebSocket)
- Device registry (`config/device_registry/list` over WebSocket)
- Area registry (`config/area_registry/list` over WebSocket)

## Planned structure

Once populated, entities are recorded one per row:

| entity_id | friendly_name | domain | area | device | enabled | exposed_to_assist | status | notes |
|---|---|---|---|---|---|---|---|---|

Where `status` is one of:

- `active` — present, enabled, matches expected config
- `stale` — present in this doc but not seen live on last validation pass
- `renamed` — entity_id changed since last recorded (old ID noted)
- `disabled` — present in registry but disabled
- `hidden` — present but not exposed to Assist / hidden from dashboards
- `duplicate` — ambiguous device with more than one matching entity

## Change log

- _(none yet — awaiting first live validation pass)_
