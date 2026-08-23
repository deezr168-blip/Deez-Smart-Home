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

## Two different kinds of directory

This repo has both **development-only reference directories at the repo
root** and a single **deployment root**, `ha-config/`. They are not
interchangeable, and only one of them is ever meant to be pulled into a
live Home Assistant `/config`:

| Path | Purpose | Deployed? | Status |
|---|---|---|---|
| `dashboards/` (root) | dev-only scratch/reference for dashboard work | no | empty — no dashboard export path yet |
| `automations/` (root) | dev-only scratch/reference for automation work | no | empty — automation entities aren't visible through the current connector at all (see blockers doc) |
| `themes/` (root) | dev-only scratch/reference for theme work | no | empty — no theme export path yet |
| `scripts/` (root) | **repo tooling** (e.g. `validate_ha_config.sh`) — not HA script YAML | no | contains `validate_ha_config.sh` |
| `ha-config/` | **the deployment root** — only this directory is ever pulled into `/config` (e.g. via the Git Pull add-on) | **yes, once populated** | structure only — see `docs/deployment_manifest.md` |
| `docs/` | All project documentation | no | populated |
| `CHANGELOG.md` | Human-readable change log | no | populated, updated per meaningful change |

**Why keep root-level `dashboards/`/`automations/`/`themes/` at all if
they're never deployed?** They predate `ha-config/` and are kept as a
place for draft/candidate work and notes that shouldn't go anywhere near
`/config` yet — e.g. an early draft of a dashboard redesign before it's
promoted into `ha-config/dashboards/`. See `docs/deployment_manifest.md`
for the authoritative, path-by-path deployment mapping.

## Dashboard file split

Once real Lovelace config is available, it will be split by functional
area under `ha-config/dashboards/` rather than kept as one monolithic
dashboard file, to keep diffs small and reviewable:

- `ha-config/dashboards/home.yaml` — main/overview dashboard
- `ha-config/dashboards/energy.yaml` — solar production, energy-monitor
  plugs, grid import/export tariffs, SolarNet/Primo inverter data
- `ha-config/dashboards/cameras.yaml` — camera views (Front Door, Tapo
  C200/C420/C425 family, Smart Pet Feeder)
- `ha-config/dashboards/security.yaml` — contact sensors, locks (if any),
  alarms, emergency buttons
- `ha-config/dashboards/climate.yaml` — AC units, fans, temperature/
  humidity sensors
- `ha-config/dashboards/network.yaml` — AdGuard Home, eero, TP-Link
  hub/cameras infrastructure
- `ha-config/dashboards/people.yaml` — presence, device trackers, persons
- `ha-config/dashboards/media.yaml` — TVs, media players, remotes

This split roughly mirrors the functional groupings already used in
`docs/entity_inventory.md`, so that document can serve as a checklist of
what each dashboard file needs to cover once it exists.

**Rule (see `CLAUDE.md` #7):** a redesign of the existing production
dashboard is never done by replacing it wholesale in one commit. A new
architecture is built as a separate candidate first (e.g. a
`.candidate.yaml` file or a feature branch), reviewed, and only then
promoted into `ha-config/` — see `docs/deployment.md`.

## Automations/scripts file split

Once `automation.*`/`script.*` entities and their definitions can actually
be read (see the open blocker in `docs/live_ha_blockers.md`), automations
will initially land as a single `ha-config/automations.yaml` (the
conventional HA layout the Git Pull add-on / `automation: !include` expect)
grouped internally by functional area — lighting, presence, parents room,
business startup, security, energy — with a split into
`ha-config/packages/*.yaml` considered later if the file grows unwieldy.
Scripts follow the same pattern under `ha-config/scripts.yaml`.

The `automations/lighting.yaml`-per-area root-level layout described in
earlier drafts of this document was aspirational and has been superseded
by this `ha-config/`-rooted plan — see `docs/deployment_manifest.md` for
the authoritative current mapping.

## What's deliberately NOT here yet

Per `CLAUDE.md`'s "current state" rule and `docs/deployment_manifest.md`:
no file under `ha-config/` is created until it has real content pulled
from the live instance and confirmed against it. A `ha-config/
configuration.yaml` with a guessed `default_config:` scaffold, an
`ha-config/dashboards/home.yaml` with invented cards, or an
`ha-config/automations.yaml` with invented triggers would all violate
rule 3 (never invent entity IDs/configuration) — and, worse, would
silently overwrite the real production files the first time a Git Pull
add-on ever syncs this repo. See `ha-config/README.md` for the full
reasoning.

## Related docs

- `docs/entity_inventory.md` — what currently exists on the live system
  (entities, states, areas), refreshed periodically via the connector.
- `docs/live_ha_blockers.md` — exactly what the connector can/can't do,
  and what's still needed to import real config.
- `docs/deployment.md` — the required workflow for making a change to
  production dashboards/automations once they do exist in this repo.
- `docs/deployment_manifest.md` — the authoritative, path-by-path mapping
  of `ha-config/` to its Home Assistant `/config` target.
