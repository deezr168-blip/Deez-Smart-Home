# Billing Dashboard — Progress

Owner: Billing Dashboard routine (architect/developer/ingestion planner).

## Status: BLOCKED — no dashboard/HA scaffolding exists yet

This is the first run of this routine against this repository. Before doing
any billing work, this run read `CLAUDE.md`, checked for
`DASHBOARD_PROGRESS.md`, `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`,
`PROJECT_STATE.md`, recent commits, and any billing-related code/YAML.

None of the prerequisites this routine's charter assumes are present:

- **No `PROJECT_STATE.md`** — the coordination/ownership file this routine is
  required to treat as authoritative before acting does not exist. There is
  no evidence any other coordinated routine (Main CasaRay Upgrade,
  Regression Auditor, Entity & Feature Scout, CasaRay Design Reviewer) has
  run in this repository either.
- **No `DASHBOARD_PROGRESS.md`, `DASHBOARD_ISSUES.md`, or
  `DASHBOARD_BACKLOG.md`** exist.
- **No `ha-deploy` branch** exists. The only branches are `main` and this
  session's working branch.
- **No Home Assistant dashboard YAML anywhere in the repo.** `home-assistant/`
  contains only a placeholder `.gitkeep`.
- **No billing data or code exists to inspect or extend** — no `meter_board`
  architecture, no `bills.json`, no `paid_state.json`, no ingestion code.
- **`docs/entity_inventory.md` is explicitly unpopulated**
  ("NOT VERIFIED — not yet populated"): no live Home Assistant entity IDs
  have been pulled into this repo. Inventing entity IDs is prohibited by
  this routine's charter, so no dashboard YAML referencing real entities can
  be written yet.
- Full repository history is 5 commits total, all scaffold/setup
  (`.gitignore`, folder scaffolding, `CLAUDE.md`, entity-inventory
  placeholder) — none touch a dashboard or billing.

## What this means

Building the Back-navigation control, billing dashboard UX, billing history
view, analytics, or a bill-ingestion pipeline right now would require either
inventing entity IDs, fabricating a dashboard structure that doesn't exist,
or guessing at a data model with no source data to validate against — all
of which this routine's charter explicitly disallows. No safe, meaningful,
unblocked billing work is available this run.

## Current billing architecture

None. Not yet started.

## Implemented features

None.

## Ingestion status

Not started. No Gmail/Drive read access has been exercised for bill
discovery, and no ingestion code exists in the repository.

## Data sources

None configured yet.

## Schema decisions

None yet — no bill data model has been created. When one is built, it will
follow the field list in this routine's charter (provider, utility type,
billing period, issue/due dates, usage, original cost, discounts/credits,
final amount payable, payment status, source traceability) and will
inspect any existing `meter_board`/`bills.json`/`paid_state.json` first —
none currently exist.

## Recent commits (billing-relevant)

None. See repo-wide log above.

## Known limitations / live-verification requirements

N/A — nothing has been built yet to verify against a live dashboard.

## Blockers

1. This repository has no Home Assistant configuration or dashboard content
   synced into it yet (`home-assistant/` is an empty placeholder), and no
   entity inventory. This looks like a bootstrap step that hasn't happened
   yet, owned outside this routine's authority (this routine may not modify
   HA deployment infrastructure or invent entities).
2. `PROJECT_STATE.md` does not exist, so cross-routine coordination/ownership
   cannot be verified as instructed.

## Exact next recommended billing task

1. First (outside this routine's scope): confirm this is the intended
   repository for the Deez Smart Home dashboard, sync real Home Assistant
   config/dashboard YAML into `home-assistant/`, verify API access, and
   populate `docs/entity_inventory.md` with real entity IDs.
2. Once a base dashboard and real entities exist, this routine should
   inspect the actual `meter_board`/billing architecture and begin with the
   highest-priority item in its charter: a reusable Back-navigation control,
   applied to billing views first.
3. Until then: re-check on the next scheduled run whether the bootstrap step
   above has happened (new `PROJECT_STATE.md`, populated entity inventory,
   or dashboard YAML). If nothing has changed after one more run, recommend
   pausing this schedule per the no-op rule until new evidence is supplied.
