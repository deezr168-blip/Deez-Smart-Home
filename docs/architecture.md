# Repository Architecture

How this repository is organized, and how it's meant to grow as real Home
Assistant configuration becomes available to import. This is a
**convention document** — it describes the target layout, not a claim
that the layout is already populated. See `docs/live_ha_blockers.md` for
why most of it is still empty.

## Why this repo exists

To become a version-controlled, reviewable source of truth for this
family's Home Assistant setup — dashboards, automations, scripts, and
themes — so changes can be made incrementally, reviewed as diffs, and
rolled back if something breaks. It is **not** currently a full backup of
the live system (see `docs/live_ha_blockers.md`); today it's an accurate
record of what the live system *contains* (via `docs/entity_inventory.md`)
plus scaffolding for what its *configuration* will look like once that
configuration can actually be retrieved.

## Directory purpose

| Path | Purpose | Status |
|---|---|---|
| `dashboards/` | Lovelace dashboard YAML, one file per functional area | empty — no dashboard export path yet |
| `automations/` | Automation definitions, one file per functional area | empty — automation entities aren't visible through the current connector at all (see blockers doc) |
| `scripts/` | Home Assistant script definitions | empty — same reason |
| `themes/` | Lovelace/UI theme files | empty — no theme export path yet |
| `docs/` | All project documentation | populated |
| `CHANGELOG.md` | Human-readable change log | populated, updated per meaningful change |

## Dashboard file split

Once real Lovelace config is available, it will be split by functional
area rather than kept as one monolithic dashboard file, to keep diffs
small and reviewable:

- `dashboards/home.yaml` — main/overview dashboard
- `dashboards/energy.yaml` — solar production, energy-monitor plugs, grid
  import/export tariffs, SolarNet/Primo inverter data
- `dashboards/cameras.yaml` — camera views (Front Door, Tapo C200/C420/C425
  family, Smart Pet Feeder)
- `dashboards/security.yaml` — contact sensors, locks (if any), alarms,
  emergency buttons
- `dashboards/climate.yaml` — AC units, fans, temperature/humidity sensors
- `dashboards/network.yaml` — AdGuard Home, eero, TP-Link hub/cameras
  infrastructure
- `dashboards/people.yaml` — presence, device trackers, persons
- `dashboards/media.yaml` — TVs, media players, remotes

This split roughly mirrors the functional groupings already used in
`docs/entity_inventory.md`, so that document can serve as a checklist of
what each dashboard file needs to cover once it exists.

**Rule (see `CLAUDE.md` #7):** a redesign of the existing production
dashboard is never done by replacing it wholesale in one commit. A new
architecture is built as a separate candidate first (e.g.
`dashboards/home.candidate.yaml` or a feature branch), reviewed, and only
then promoted — see `docs/deployment.md`.

## Automations/scripts file split

Once `automation.*`/`script.*` entities and their definitions can actually
be read (see the open blocker in `docs/live_ha_blockers.md`), automations
will be grouped by functional area, not one automation per file and not
one giant file:

- `automations/lighting.yaml`
- `automations/presence.yaml`
- `automations/parents_room.yaml`
- `automations/business_startup.yaml`
- `automations/security.yaml`
- `automations/energy.yaml`

Scripts will be grouped similarly under `scripts/`, split by the logical
area they serve once real script definitions are available.

## What's deliberately NOT here yet

Per `CLAUDE.md`'s "current state" rule: no file in `dashboards/`,
`automations/`, `scripts/`, or `themes/` is created until it has real
content pulled from the live instance. An empty `home.yaml` with guessed
cards, or an `automations/lighting.yaml` with invented triggers, would
violate rule 3 (never invent entity IDs/configuration) and would be worse
than no file at all — it would look authoritative while being fiction.

## Related docs

- `docs/entity_inventory.md` — what currently exists on the live system
  (entities, states, areas), refreshed periodically via the connector.
- `docs/live_ha_blockers.md` — exactly what the connector can/can't do,
  and what's still needed to import real config.
- `docs/deployment.md` — the required workflow for making a change to
  production dashboards/automations once they do exist in this repo.
