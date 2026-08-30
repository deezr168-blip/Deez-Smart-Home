# Project State — Coordination & Ownership Map

This file is the authoritative coordination point for the autonomous
routines operating on this repository. Each routine owns and updates only
its own section below. Do not overwrite another routine's section.

Priority model used across routines: **P0 → P1 → P2 → P3**
(P0 = safety/correctness blockers, P1 = privacy/security and core
functionality regressions, P2 = planned feature work, P3 = cosmetic/nice
to have).

This file was created by the Billing Dashboard routine on 2026-08-30
because no coordination file existed yet. Sections for other routines are
placeholders until those routines run and claim them.

---

## Main CasaRay Upgrade — general dashboard implementation

Status: **NOT YET RUN.** No entry from this routine yet.

---

## Regression Auditor — advisory/read-only

Status: **NOT YET RUN.** No entry from this routine yet.

---

## Entity & Feature Scout — advisory/read-only

Status: **NOT YET RUN.** No entry from this routine yet.

---

## CasaRay Design Reviewer — advisory/read-only

Status: **NOT YET RUN.** No entry from this routine yet.

---

## Billing Dashboard — billing UX, history, analytics, ingestion

Status: **BLOCKED — no prerequisite infrastructure exists yet.**

### Billing work completed
None. This repository is at genesis: it contains only scaffold folders,
`.gitkeep` placeholders, and `docs/entity_inventory.md` (itself marked
"NOT VERIFIED — not yet populated").

### Commits
- `56e1b64` and earlier — repo scaffolding only (folders, `.gitignore`,
  entity inventory stub). No billing-related commits exist.
- This run: added `PROJECT_STATE.md` and `BILLING_PROGRESS.md` (see
  below) — documentation only, no functional/dashboard changes.

### Verification state
N/A — no billing dashboard, YAML, or code exists to verify.

### Ingestion/data-model progress
None. No `meter_board` architecture, `bills.json`, or `paid_state.json`
exist in this repository. No Home Assistant instance access, live entity
data, or dashboard config is present under `home-assistant/` (it holds
only a `.gitkeep`).

### Outstanding billing issues
None recorded — there is no billing code or dashboard yet to have
regressions. The task brief this routine received assumes a mature,
already-substantially-built billing dashboard (existing back navigation,
existing meter_board/bills.json/paid_state.json, existing CasaRay-style
Lovelace YAML). None of that exists in this repository yet. This is a
mismatch between the routine's assumed starting state and the actual
repository state, not a code defect.

### Blockers
1. **No live Home Assistant entity access has been established or
   verified.** `docs/entity_inventory.md` is explicitly unpopulated
   pending that step. Building billing dashboard YAML or referencing
   entities without verified live entity IDs would violate the
   "never invent entity IDs" rule.
2. **No dashboard scaffold exists** (`home-assistant/` is empty). Billing
   is meant to extend an existing CasaRay-style dashboard structure that
   has not yet been created — that is Main CasaRay Upgrade's ownership,
   not Billing's.
3. **No existing billing data model** (`bills.json` / `paid_state.json` /
   meter_board code) to inspect, preserve, or extend, so no ingestion
   pipeline can be safely designed against real structures yet — doing so
   now would mean guessing a schema with nothing to validate it against.
4. No Gmail/Drive-sourced bill samples have been reviewed in this repo's
   context, so no ingestion/extraction logic has been written.

### Exact next recommended billing task
Do not start billing YAML, ingestion code, or a Back-navigation
component yet. First, either:
- Main CasaRay Upgrade routine should scaffold the initial Home
  Assistant dashboard structure and confirm live entity access
  (populating `docs/entity_inventory.md`), or
- A human should confirm whether this repository is intentionally at
  genesis (in which case the billing routine's brief should be
  updated/re-scoped for a from-scratch build), or point the routine at
  the actual location of existing billing dashboard YAML / meter_board /
  bills.json if those exist elsewhere and simply haven't been synced to
  this repo yet.

Once entity access and a base dashboard scaffold exist, the next Billing
run should: inspect the real entities available for utility/billing
sensors, then design the minimal `bills.json` schema (provider, utility
type, billing period, issue/due dates, usage, original cost,
discounts/credits, final amount, payment status, source traceability)
before writing any Lovelace YAML.
