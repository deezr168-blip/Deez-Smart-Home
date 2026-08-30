# Project State

Shared coordination and ownership map for the autonomous routines operating
on this repository (Main CasaRay, Billing Dashboard, Entity & Feature Scout,
Regression Auditor, Design Reviewer). Each routine owns and updates only its
own section below. Do not overwrite another routine's section.

This file did not exist prior to 2026-08-30. It is being created now by the
Entity & Feature Scout routine's first run, which only populates the section
below. Other routines should add their own sections on their own runs rather
than have content invented on their behalf here.

## Entity & Feature Scout

**Last run:** 2026-08-30

**Status: blocked at pre-dashboard stage.** This run found none of the
inputs the scout routine depends on yet exist in the repository:

- `dashboards/deez_smart_home.yaml` — does not exist (repo-wide search, incl.
  `.gitignore`, confirms no dashboard file has been created anywhere)
- `DASHBOARD_PROGRESS.md` — does not exist
- `DASHBOARD_ISSUES.md` — does not exist
- `DASHBOARD_BACKLOG.md` — did not exist; created empty as a scaffold by
  this run (see below)
- `docs/entity_inventory.md` — exists but is explicitly unpopulated
  ("NOT VERIFIED — not yet populated"); it documents that entity
  registry/state population is a separate later stage, not yet run

Repository state as of this run: only scaffold content exists
(`CLAUDE.md`, `README.md`, `docs/entity_inventory.md`, empty `.gitkeep`
placeholder directories for `home-assistant/`, `safework/`, `scripts/`).
Git history is limited to initial scaffold commits (see `git log`).

### What this run did

- Confirmed no dashboard, no other tracking docs, and no populated entity
  inventory exist (see above).
- Confirmed the Home Assistant MCP connector is reachable read-only from
  this session and returns live entity/area data (~54KB of live context
  on an unfiltered query), so live verification is technically available
  once there is a dashboard to compare it against.
- Did not populate `docs/entity_inventory.md` — that document states its
  own population is a distinct later stage (see
  `docs/access_verification.md`, once that stage runs), not this scout
  routine's responsibility.
- Did not create or modify `dashboards/deez_smart_home.yaml` or any
  specialist implementation file, per this routine's constraints.
- Created an empty `DASHBOARD_BACKLOG.md` scaffold (no items yet — there
  is no dashboard or verified entity inventory to generate evidence-based
  opportunities from).

### Areas inspected

Whole repository (root, `docs/`, `home-assistant/`, `safework/`,
`scripts/`) and full git history. No dashboard views exist to inspect
(Home, Energy, Security, Climate, Network, rooms, etc.).

### Opportunities discovered

None. Opportunity discovery requires a dashboard to evaluate and/or a
populated, verified entity inventory to compare against — neither exists
yet. Proposing opportunities now would be speculative rather than
evidence-based, which this routine's operating rules disallow.

### Backlog items added/updated/closed

None added. `DASHBOARD_BACKLOG.md` created as an empty ranked-queue
scaffold for future runs.

### Verified entity opportunities

None recorded. Live Home Assistant data is reachable read-only, but with
no dashboard yet built there is nothing to compare it against, and this
routine does not own populating `docs/entity_inventory.md`.

### Blockers

1. No `dashboards/deez_smart_home.yaml` exists — the project has not
   reached the dashboard-implementation stage this routine assumes.
2. `docs/entity_inventory.md` is unpopulated — no verified entity list to
   reason from without duplicating another stage's work.
3. No `DASHBOARD_PROGRESS.md` / `DASHBOARD_ISSUES.md` exist to check
   before proposing opportunities.
4. This was the first write to `PROJECT_STATE.md`; no ownership context
   from Main CasaRay, Billing, Regression Auditor, or Design Reviewer
   exists yet to coordinate against.

### Next recommended discovery focus

Re-run once (a) `docs/entity_inventory.md` has been populated from a
verified live Home Assistant pull (Stage 2, per that document), and
(b) an initial `dashboards/deez_smart_home.yaml` exists from the Main
CasaRay routine. At that point, this routine can meaningfully compare
live verified entities against dashboard usage and surface evidence-based
opportunities per its normal remit.
