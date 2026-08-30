# PROJECT_STATE.md

Authoritative coordination and ownership map for all autonomous routines
operating on this repository. Each routine updates only its own section.
Do not overwrite another routine's section.

Priority model used across all routines: **P0 → P1 → P2 → P3**
(P0 = critical/broken, P1 = required correctness or privacy, P2 = quality
improvement, P3 = cosmetic/nice-to-have.)

This file did not previously exist. It was bootstrapped by the Billing
Dashboard routine on 2026-08-30 because it is required reading for that
routine before doing any work, and none of the coordinating routines had
run yet. Sections for other routines are stubbed accurately as "not yet
run" — no work is claimed on their behalf.

---

## Repository-wide baseline (as of 2026-08-30)

This repository is currently a **bare scaffold**, not a populated Home
Assistant config/dashboard project:

- No Lovelace/dashboard YAML exists anywhere in the repo.
- No `home-assistant/` config content exists (folder has only `.gitkeep`).
- No `ha-deploy` branch exists (only `main` and active `claude/*` branches).
- `docs/entity_inventory.md` is explicitly **NOT VERIFIED — not yet populated**.
- No billing-related files (`bills.json`, `paid_state.json`, `meter_board`,
  etc.) exist anywhere in the repo.
- A live Home Assistant instance **is** reachable via MCP and does expose
  real energy/solar entities (see Billing section below), but nothing
  billing-specific has been built to consume them yet, in the repo or live.

Any routine whose instructions assume prior dashboard/billing/navigation
work exists should treat those assumptions as **not yet true** until this
file records otherwise.

---

## Main CasaRay Upgrade — status

Not yet run. No entries.

## Regression Auditor — status

Not yet run. No entries.

## Entity & Feature Scout — status

Not yet run. No entries.

## CasaRay Design Reviewer — status

Not yet run. No entries.

---

## Billing Dashboard — status

**Owner:** Billing Dashboard routine. Last run: 2026-08-30.

### Billing work completed
- Read CLAUDE.md, README.md, docs/entity_inventory.md, .gitignore, git log/branches.
- Confirmed no billing dashboard, billing data files, or `meter_board`
  architecture exist in the repository.
- Confirmed no `ha-deploy` branch/commit history exists to inspect.
- Queried the live Home Assistant instance (read-only, via MCP) for
  billing-relevant entities. Found general energy/solar monitoring sensors
  (e.g. SolarNet import/export tariff, Primo inverter energy/power, per-plug
  P110M energy monitors, an ungrouped `sensor Cost` entity in AUD) but
  **no bill, invoice, or utility_meter domain entities** — a search for
  `utility_meter` domain and for entities named "bill" returned no matches.
- Created `PROJECT_STATE.md` (this file), `BILLING_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md` as tracking scaffolding.
- No dashboard YAML, ingestion code, or billing UI was written this run —
  see Blockers below for why.

### Commit(s)
- (this run's commit — see BILLING_PROGRESS.md for hash once committed)

### Verification state
- N/A — no runtime/visual functionality was touched. Nothing to mark
  VERIFIED or FIXED — AWAITING LIVE VERIFICATION this run.

### Ingestion/data-model progress
- Not started. No `bills.json`/`paid_state.json` schema exists yet to
  extend. See BILLING_PROGRESS.md for the proposed starting schema.

### Outstanding billing issues
- None filed yet (repo has no billing feature to regress). See
  DASHBOARD_ISSUES.md.

### Blockers
- **No dashboard exists to add a "Back" control or billing UI to.** The
  routine's brief assumes an established CasaRay-style Lovelace dashboard
  with a substantially-implemented Back navigation system and an existing
  `meter_board`/`bills.json`/`paid_state.json` billing area. None of that
  is present in this repository. Building it from scratch would mean
  inventing dashboard architecture, file layout, and entity usage that no
  other routine or human has specified — against this routine's explicit
  instruction not to guess uncertain structure.
  Needs a human (or the Main CasaRay Upgrade routine, which owns general
  dashboard implementation) to establish the base dashboard structure
  (where HA config/Lovelace YAML will live in this repo, e.g. under
  `home-assistant/`) before billing-specific UI can be layered on it.
- **No bill-ingestion source has been confirmed.** Gmail/Google Drive MCP
  tools are available in this session, but no search for actual bill
  emails/documents has been run pending confirmation this is in scope for
  an otherwise-empty scaffold repo, and pending a place to write the
  extracted/normalized data.
- **`docs/entity_inventory.md` is unpopulated**, so no entity IDs can be
  safely referenced from dashboard YAML yet (this routine's instructions
  forbid inventing entity IDs).

### Exact next recommended billing task
1. Confirm with a human (or wait for Main CasaRay Upgrade) where Home
   Assistant Lovelace config will live in this repo, and get a minimal
   dashboard scaffold in place.
2. Once a dashboard scaffold exists, populate `docs/entity_inventory.md`
   from the live entity registry (Stage 2, per that file's own notes),
   then identify/confirm which entities are genuinely billing-relevant.
3. Only then begin the billing data model (`bills.json`/`paid_state.json`
   equivalent) and the first minimal billing card, per the proposed schema
   in BILLING_PROGRESS.md.
