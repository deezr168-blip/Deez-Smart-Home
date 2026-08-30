# Project State — Autonomous Routine Coordination

This file is the shared coordination and ownership map for the autonomous
routines operating on this repository:

- **Main CasaRay Upgrade** — owns general dashboard implementation
- **Billing Dashboard** — owns billing UX, billing history/analytics, bill
  ingestion, billing-specific supporting code
- **Regression Auditor** — advisory/read-only, feeds issues/backlog
- **Entity & Feature Scout** — advisory/read-only, feeds issues/backlog
- **CasaRay Design Reviewer** — advisory/read-only, feeds issues/backlog

This file did not exist before 2026-08-30. It is created here by the
Billing Dashboard routine, which was invoked first, only because the
routines' shared coordination file needs to exist for any of them to
follow their instructions to "read PROJECT_STATE.md before acting." Each
routine should only ever edit its own section below. If Main CasaRay (or
another routine) already has its own conventions for this file (priority
definitions, section format), its next run should reconcile this scaffold
with that convention rather than treat this layout as fixed.

Priority model referenced by all routines (placeholder pending
confirmation by Main CasaRay — no prior definition existed in-repo):
- **P0** — broken/blocking core functionality or safety/privacy issue
- **P1** — significant functional gap or documented regression
- **P2** — meaningful UX/quality improvement
- **P3** — cosmetic/nice-to-have

---

## Main CasaRay Upgrade — status

_Not yet run. No entries yet._

---

## Billing Dashboard — status

**Last run:** 2026-08-30 (first run)

**Repository reality check:** This repository is currently an early
scaffold, not a working Home Assistant dashboard checkout. There is no
`home-assistant` dashboard YAML, no Lovelace configuration, no
`meter_board`, no `bills.json`, no `paid_state.json`, and no billing code
of any kind. `docs/entity_inventory.md` explicitly states entities are
**NOT VERIFIED** — no live Home Assistant API access has been established
or recorded in this repo, so no real entity IDs are available yet.

**Billing work performed this run:** None (see blockers below). Created
this coordination file and `BILLING_PROGRESS.md` to record state honestly
rather than fabricate dashboard YAML, entity references, or a billing
data model against a nonexistent live system.

**Blockers:**
1. No verified Home Assistant entity inventory exists yet (Entity Scout
   prerequisite). Building billing dashboard YAML or automations that
   reference entities now would mean inventing entity IDs, which is
   explicitly disallowed.
2. No base dashboard/Lovelace structure exists yet (Main CasaRay
   prerequisite) for a billing view to be added into.
3. No existing billing data architecture (`bills.json`, `paid_state.json`,
   `meter_board`) to inspect, preserve, or extend — this would be a
   greenfound build, which increases the risk of conflicting with Main
   CasaRay's dashboard structure decisions if built unilaterally before
   that structure exists.

**Verification state:** N/A — no billing UI exists to verify.

**Ingestion/data-model progress:** Not started. Design for a
provider/utility/billing-period/due-date/usage/original-cost/discounts/
final-amount/payment-status/source-traceability schema is planned per the
task brief but not yet written to disk, pending confirmation that this is
the correct repository/checkout for that work (see note to user).

**Outstanding billing issues:** See `DASHBOARD_ISSUES.md`.

**Exact next recommended billing task:** Once (a) a verified
`docs/entity_inventory.md` exists with real entity IDs and (b) a base
dashboard/Lovelace layout exists from Main CasaRay to attach a billing
view to, begin with the Back-navigation component (global priority) scoped
to whatever billing view exists, then stand up the `bills.json` /
`paid_state.json` schema. Until then, this routine should not invent
dashboard files.

---

## Regression Auditor — status

_Not yet run. No entries yet._

---

## Entity & Feature Scout — status

_Not yet run. No entries yet._

---

## CasaRay Design Reviewer — status

_Not yet run. No entries yet._
