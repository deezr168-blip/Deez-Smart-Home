# Project State

Shared coordination and ownership map for all autonomous routines operating
on this repository (Main CasaRay, Billing Dashboard Routine, Regression
Auditor, Design Reviewer, Entity & Feature Scout). Each routine owns and
updates only its own section below. Do not overwrite another routine's
section.

## Main CasaRay

_(not yet populated by owning routine)_

## Billing Dashboard Routine

_(not yet populated by owning routine)_

## Regression Auditor

_(not yet populated by owning routine)_

## Design Reviewer

_(not yet populated by owning routine)_

## Entity & Feature Scout

**Last run:** 2026-08-30

**Status: BLOCKED — project not yet bootstrapped.**

### Areas inspected

- Repository root and full file tree (only scaffold files present:
  `.gitkeep` placeholders under `home-assistant/`, `safework/`, `scripts/`;
  `README.md`; `CLAUDE.md`; `docs/entity_inventory.md`).
- `docs/entity_inventory.md` — confirmed status "NOT VERIFIED — not yet
  populated." No live Home Assistant entity/device/area data has been
  pulled or recorded (Stage 2 of that document's own process has not run).
- Searched for `PROJECT_STATE.md`, `DASHBOARD_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`, and
  `dashboards/deez_smart_home.yaml` — none exist in the repository.
- Git history (`git log`) — 5 commits total, all initial scaffolding
  (`Initial commit`, `Add CLAUDE.md if missing`, folder scaffolding,
  `.gitignore` + entity inventory scaffold). No dashboard or entity-scout
  work has landed yet.

### Opportunities discovered

None. There is no dashboard (`dashboards/deez_smart_home.yaml` does not
exist) and no verified entity inventory to evaluate opportunities against.
Per this routine's own operating rules, entity IDs, capabilities, devices,
and states must never be invented — with no verified inventory available,
no opportunity can be responsibly proposed this run.

### Backlog items added/updated/closed

None. `DASHBOARD_BACKLOG.md` created as an empty, ready-to-use scaffold
(see that file) — no items added, since there is nothing yet to queue.

### Verified entity opportunities

None available — entity inventory is unpopulated (see
`docs/entity_inventory.md`, Status: NOT VERIFIED).

### Blockers

1. **No dashboard exists yet.** `dashboards/deez_smart_home.yaml` has not
   been created by Main CasaRay or any implementation routine. There is
   nothing to compare entities/opportunities against.
2. **No verified entity inventory.** `docs/entity_inventory.md` Stage 2
   (live Home Assistant REST/WebSocket pull and verification) has not run.
   This routine does not own that verification step and will not perform
   it or invent entity data to work around it.
3. **No PROJECT_STATE.md history.** This is the first recorded run of the
   Entity & Feature Scout routine; no prior no-op count exists yet.

### Next recommended discovery focus

Once Home Assistant read access is configured and `docs/entity_inventory.md`
Stage 2 completes (verified entities recorded), and once Main CasaRay
publishes an initial `dashboards/deez_smart_home.yaml`, re-run this routine
to compare verified entities against dashboard usage and identify real
opportunities. Until then, there is no safe, evidence-based scouting work
available.

**No-op run count: 1 of 2.** If the next scheduled run finds the same
blockers with no new evidence (no dashboard, no verified inventory, no new
commits), this schedule should be paused per this routine's own stopping
rule until new evidence, defects, entities, or requirements are supplied.
