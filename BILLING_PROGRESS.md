# Billing Progress

## Current billing architecture

None yet. This repository does not currently contain a Home Assistant
dashboard checkout, Lovelace YAML, or any billing-related code. Confirmed
by full repository search on 2026-08-30 (see run log below).

## Implemented features

None.

## Ingestion status

Not started. No Gmail/Drive-based bill ingestion code exists. Per the
task brief this should eventually be read-only discovery/extraction with
user-controlled Paid/Unpaid state, but no groundwork (schema, dashboard,
verified entities) exists yet to build on.

## Data sources

None configured/verified in-repo yet.

## Schema decisions

None made yet. Planned fields (provider, utility type, billing period,
issue date, due date, usage, original/pre-discount cost, discounts/
credits, final amount payable, payment status, source traceability) are
recorded here as the target shape for a future `bills.json` /
`paid_state.json`, not yet implemented.

## Recent commits

- 2026-08-30: Added `PROJECT_STATE.md` coordination scaffold and this
  file, documenting that no billing dashboard work exists yet.

## Known limitations

- No verified Home Assistant entity inventory (`docs/entity_inventory.md`
  is explicitly marked NOT VERIFIED, awaiting a live validation pass that
  hasn't happened).
- No base dashboard/Lovelace structure to attach a billing view to.
- No existing `meter_board`, `bills.json`, or `paid_state.json` to
  inspect/extend, despite the task brief assuming these exist.

## Live-verification requirements

N/A this run — nothing was built.

## Exact next priorities

1. Confirm with the user/other routines whether this is the correct
   repository/branch for the described CasaRay billing dashboard work, or
   whether that work lives elsewhere and this repo is still in initial
   scaffolding (Stage 1: entity inventory not yet populated).
2. Once a verified entity inventory and a base dashboard structure exist,
   implement the Back-navigation component for the billing view first
   (global priority), then the `bills.json`/`paid_state.json` data model.
3. Do not create speculative billing dashboard YAML or invented entity
   references before those prerequisites land — this was the deliberate
   choice made this run per the "no exploratory refactoring without
   evidence" rule and the "never invent entity IDs" rule.

## Run log

- **2026-08-30 (run 1):** Read CLAUDE.md, README.md, `.gitignore`,
  `docs/entity_inventory.md`, full git log (5 commits, all scaffold-only),
  and the full repository file tree. Found no `DASHBOARD_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`, `BILLING_PROGRESS.md`, or
  `PROJECT_STATE.md`. Found no dashboard YAML, no ha-deploy history
  distinct from the scaffold commits, and no billing-related files
  anywhere in the tree. Created `PROJECT_STATE.md` and this file to record
  the blocked state rather than fabricate dashboard/billing
  infrastructure against a nonexistent live system. No dashboard YAML,
  entity references, or billing data files were created. This is a
  genuine blocker, not a routine no-op — flagging for the user.
