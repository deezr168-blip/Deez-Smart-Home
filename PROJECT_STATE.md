# Project State

Authoritative coordination and ownership map for autonomous routines working
on the Deez Smart Home dashboard project. Each section below is owned by one
routine. A routine must only write to its own section.

Status: **bootstrap** — this file did not exist prior to 2026-08-30. No
dashboard, progress log, or issues log exists yet in this repository. The
sections for routines other than Entity & Feature Scout are placeholders
until those routines run for the first time and populate their own state.

## Main CasaRay (dashboard build/maintenance routine)

_Not yet initialized. No `dashboards/deez_smart_home.yaml`,
`DASHBOARD_PROGRESS.md`, or `DASHBOARD_ISSUES.md` exist in this repository
as of 2026-08-30. Reserved for the Main CasaRay routine to populate on its
first run._

## Billing Dashboard Routine

_Not yet initialized. Reserved for the Billing Dashboard Routine._

## Regression Auditor

_Not yet initialized. Reserved for the Regression Auditor routine._

## Design Reviewer

_Not yet initialized. Reserved for the Design Reviewer routine._

## Entity & Feature Scout

_Owner: Entity & Feature Scout routine. Last run: 2026-08-30._

### Areas inspected

- Full live entity/device set pulled read-only via the Home Assistant
  connector (`GetLiveContext`, unfiltered) — 426 entities/devices across
  areas: Network (90), Living Room (73), Ray Bedroom (65), unassigned (54),
  Parents Room (40), Dining (31), Energy (23), Kitchen (22), Garage (11),
  Backyard (10), Guest Room (6).
- Repository tracking docs: `CLAUDE.md`, `README.md`,
  `docs/entity_inventory.md`, full git log/history, full working-tree file
  listing.

### Opportunities discovered

Logged to `DASHBOARD_BACKLOG.md` (FEAT-001 through FEAT-006). Summary:

1. Redundant duplicate entities representing the same physical device
   (e.g. two `media_player` entities for the same Samsung Q9 TV, one
   bracketed `'[TV] ...'` name from a second integration).
2. Home-wide unavailable-entity rate is high: 105 of 426 live
   entities/devices (~25%) currently report `unavailable`. This is
   foundational — any view design should assume graceful unavailable
   handling from the start rather than retrofitting it.
3. Verified data exists for a family-presence / "who's home" contextual
   card (`person` x3, `device_tracker` x6, `input_select.family_location`)
   that isn't backed by any dashboard yet.
4. Verified camera domain (6 cameras: Front Door, Smart Pet Feeder, 3x
   TP-Link Tapo, — half currently unavailable) suitable for a Security
   view once one is built.
5. A manually-tracked billing-adjacent helper,
   `input_number` "Gas Bill Usage MJ", exists live — queued for Billing
   Dashboard Routine rather than implemented here.
6. Several same-name, same-area entity pairs that look like duplicate
   device registrations (Hue ambiance spot 1, "Living room" light,
   "Dining" light, "NightLight") — flagged as needing entity_id-level
   verification, not yet confirmed as true duplicates from names alone.

### Backlog items added/updated/closed this run

- Added: FEAT-001 through FEAT-006 (all new; `DASHBOARD_BACKLOG.md` did not
  exist before this run).
- Closed: none (no prior backlog existed to audit).

### Verified entity opportunities

See `DASHBOARD_BACKLOG.md` for the full list with area/domain evidence.
Note: `GetLiveContext` returns friendly names, domains, states, areas, and
attributes, but not raw `entity_id` values. No `entity_id` has been
invented anywhere in this document or the backlog — all entities are
referenced by their verified friendly name and domain only. Resolving
exact `entity_id`s is a prerequisite for implementation and belongs to
`docs/entity_inventory.md` Stage 2 (REST/WebSocket registry pull), which
has not run yet (`docs/entity_inventory.md` still reads "NOT VERIFIED —
not yet populated").

### Blockers

- No dashboard exists yet (`dashboards/deez_smart_home.yaml` is absent),
  so there is nothing to compare live entities against for "missing from
  dashboard" style findings, and no view/card structure to attach
  recommendations to. Backlog items below are therefore framed as
  forward-looking opportunities for whichever routine builds the initial
  dashboard, not as changes to existing views.
- `docs/entity_inventory.md` Stage 2 (verified entity_id-level inventory)
  has not run, so backlog items can only cite friendly names/domains/areas,
  not entity_ids. Implementation work will need Stage 2 to complete first.
- `DASHBOARD_PROGRESS.md` and `DASHBOARD_ISSUES.md` do not exist, so this
  run could not cross-check recent dashboard progress/known issues before
  proposing opportunities — cross-checked git history instead (only
  scaffold/inventory commits exist, no dashboard work yet).

### Next recommended discovery focus

- Once Main CasaRay produces an initial `dashboards/deez_smart_home.yaml`
  and `DASHBOARD_PROGRESS.md`/`DASHBOARD_ISSUES.md`, re-run this scout to
  do genuine live-entity-vs-dashboard-usage comparison (missing entities,
  redundant cards, weak static presentations).
- Once `docs/entity_inventory.md` Stage 2 completes, re-check the
  duplicate-looking entity pairs (Hue ambiance spot 1, Living room light,
  Dining light, NightLight, the two "Deez" device_trackers/notify targets)
  against real entity_ids to confirm or rule out true duplicates.
- Investigate the `Network` area (90 entities/devices, the largest single
  area) for a dedicated Network view once a dashboard exists — largely
  unexplored in this pass beyond camera/Tapo battery entities.
