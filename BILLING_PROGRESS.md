# Billing Progress

Owner: Billing Dashboard routine.

## Current billing architecture
None exists yet. There is no `home-assistant/` dashboard content beyond a
`.gitkeep` placeholder, no Lovelace YAML, and no billing-specific code
anywhere in this repository.

## Implemented features
None.

## Ingestion status
Not started. No Gmail/Drive bill-ingestion code exists. No safe design
work has been done against real data because no sample bills, entities,
or existing `bills.json`/`paid_state.json` structures are present in this
repo to inspect.

## Data sources
None configured/verified in-repo yet.

## Schema decisions
None made yet — deferred until a base dashboard scaffold and verified
live entity access exist (see `docs/entity_inventory.md`, currently
unpopulated). Making schema decisions now would mean designing against
nothing, with no way to validate against real bill data or entities.

## Recent commits
- `56e1b64` (merge), `319b115`, `e79be47`, `3efbd3e`, `f2eb5a8` — all
  repository scaffolding (folders, `.gitignore`, entity inventory stub).
  None touch billing.
- This run added `PROJECT_STATE.md` (new coordination file) and this
  file. No functional changes.

## Known limitations
- Repository is at genesis for billing purposes: no meter_board, no
  bills.json, no paid_state.json, no billing dashboard YAML to preserve
  or extend.
- Back navigation (described in this routine's brief as "substantially
  implemented") does not exist in this repository at all. Treat that
  brief as written for a further-along project state than what is
  actually present here.

## Live-verification requirements
N/A until a dashboard exists.

## Exact next priorities
1. Confirm with a human (or with the Main CasaRay Upgrade routine, once
   it has run) whether this repo is genuinely starting from scratch, or
   whether existing billing dashboard/meter_board/bills.json content
   should be present and is simply missing/not yet synced.
2. Once live Home Assistant entity access is verified and
   `docs/entity_inventory.md` is populated, identify actual
   utility/billing-related entities before designing any ingestion
   schema or dashboard YAML.
3. Do not perform speculative billing YAML/ingestion work before (1) and
   (2) — there is nothing real to build against yet, and inventing
   structure now risks conflicting with whatever Main CasaRay/Entity
   Scout establish first.

## Run log
- 2026-08-30: First Billing Dashboard routine run. Read CLAUDE.md,
  README.md, full repo tree; confirmed no DASHBOARD_PROGRESS.md,
  DASHBOARD_ISSUES.md, DASHBOARD_BACKLOG.md, or prior
  BILLING_PROGRESS.md existed. Confirmed no billing dashboard, HA config,
  or entity data exists in-repo. Created `PROJECT_STATE.md` and this file
  to record the blocked state rather than fabricating dashboard/ingestion
  work with no real infrastructure or entities to build against. No
  billing dashboard changes made. Recommend pausing this schedule until
  a base dashboard/entity-access foundation exists or a human clarifies
  the intended starting state.
