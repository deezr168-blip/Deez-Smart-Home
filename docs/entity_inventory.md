# Entity Inventory

Status: **PARTIALLY VERIFIED — areas and domain counts observed live; entity
IDs still not populated.**

This file is the source of truth for known Home Assistant entities, used to
validate live entity IDs before any automation/dashboard/script work
references them. It still contains no entity IDs: the live read done so far
went through the Home Assistant MCP tool, which reports friendly names,
domains, and areas but not entity IDs. IDs must never be invented or guessed,
so they stay absent until a REST-API pass fills them in.

## How this gets populated

Run, with a long-lived access token:

```bash
export HA_URL=http://homeassistant.local:8123
export HA_TOKEN=<long-lived access token>
python3 scripts/ha_verify.py --inventory
```

That rewrites this file from `GET /api/states` plus an `area_id()` template
pass, so every row below comes from the live instance. The script is read-only
against Home Assistant.

## Observed live (2026-08-23)

Read via the Home Assistant MCP tool, which exposes friendly names, domains, and
areas but **not entity IDs** — which is why the table below is still empty.

431 entities across 10 areas.

### Areas

`area_id` values are the slugified area names. Home Assistant assigns that slug
at creation time, but an area renamed later keeps its original ID, so these are
**assumed, not verified** — `python3 scripts/ha_verify.py` confirms or corrects
them against the live area registry.

| assumed area_id | area name | entities | role |
|---|---|---|---|
| `living_room` | Living Room | 64 | room |
| `ray_bedroom` | Ray Bedroom | 61 | room |
| `parents_room` | Parents Room | 39 | room |
| `dining` | Dining | 27 | room |
| `kitchen` | Kitchen | 22 | room |
| `garage` | Garage | 11 | room |
| `backyard` | Backyard | 10 | room |
| `guest_room` | Guest Room | 6 | room |
| `network` | Network | 96 | infrastructure bucket, not a place |
| `energy` | Energy | 23 | organisational bucket, not a place |
| — | (no area) | 72 | unassigned |

### Domains

`sensor` 129 · `switch` 60 · `binary_sensor` 47 · `select` 33 · `scene` 29 ·
`light` 25 · `event` 22 · `number` 22 · `button` 20 · `media_player` 9 ·
`device_tracker` 6 · `notify` 6 · `camera` 6 · `person` 3 · `remote` 2 ·
`zone` 2 · `time` 2 · `climate` 1 · `cover` 1 · `fan` 1 · `weather` 1 ·
`todo` 1 · `input_boolean` 1 · `input_number` 1 · `input_select` 1

### Device classes in use

- `binary_sensor` — `connectivity` 16, `motion` 13, `door` 7, `problem` 6,
  `occupancy` 2, `presence` 1, `running` 1
- `sensor` — `battery` 21, `energy` 20, `illuminance` 8, `temperature` 7,
  `power` 6, `voltage` 6, `enum` 5, `current` 4, `timestamp` 4, `humidity` 2,
  `pm1`/`pm10`/`pm25` 1 each, `frequency` 1, `monetary` 1

These counts are what
[`home-assistant/dashboards/casaray_home.yaml`](../home-assistant/dashboards/casaray_home.yaml)
selects its `alert_classes` and `sensor_classes` from — see
[`docs/casaray_dashboard.md`](casaray_dashboard.md).

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

- **2026-08-23** — First live read (via the Home Assistant MCP tool). Areas,
  domain counts, and device classes recorded above. Entity IDs still outstanding:
  the MCP tool does not expose them. Run `scripts/ha_verify.py --inventory`
  against the REST API to fill in the table.
