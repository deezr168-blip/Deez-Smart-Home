# Project State — Coordination & Ownership Map

This file is the authoritative coordination/ownership map for the
autonomous dashboard routines working in this repository:

- **Main CasaRay Upgrade** — owns general dashboard implementation.
- **Regression Auditor** — advisory/read-only, feeds issues/backlog.
- **Entity & Feature Scout** — advisory/read-only, feeds issues/backlog.
- **CasaRay Design Reviewer** — advisory/read-only, feeds issues/backlog.
- **Billing Dashboard** — owns billing-specific dashboard UX, billing
  history/analytics, bill-ingestion design, billing-supporting code, and
  `BILLING_PROGRESS.md`.

This file did not exist before this run; it is being created now so that
routine can record status here. Each routine should only edit its own
section below.

Priority model: P0 → P1 → P2 → P3.

---

## Main CasaRay Upgrade — status

_(Not yet run in this repository. No entries yet.)_

## Regression Auditor — status

_(Not yet run in this repository. No entries yet.)_

## Entity & Feature Scout — status

_(Not yet run in this repository. No entries yet.)_

## CasaRay Design Reviewer — status

_(Not yet run in this repository. No entries yet.)_

## Billing Dashboard — status

**Run date:** 2026-08-30

**Work completed:** None. This run performed discovery only (see
`BILLING_PROGRESS.md` for full detail).

**Commit(s):** This run's commit adds `PROJECT_STATE.md` and
`BILLING_PROGRESS.md` only — no dashboard/billing functional changes.

**Verification state:** N/A — no functional changes made.

**Ingestion / data-model progress:** None. No bill-ingestion code or data
model exists yet.

**Outstanding billing issues:** None recorded yet (no `DASHBOARD_ISSUES.md`
exists; nothing billing-specific to log beyond the blocker below).

**Blockers:**
- No Home Assistant dashboard, config, or entity inventory exists in this
  repository yet (`home-assistant/` is an empty placeholder;
  `docs/entity_inventory.md` is explicitly unpopulated). No `ha-deploy`
  branch exists. Building billing dashboard YAML, a Back-navigation control,
  or an ingestion pipeline right now would require inventing entity IDs or
  fabricating dashboard structure, which this routine's charter prohibits.
  This looks like a repository bootstrap step that hasn't happened yet and
  is outside this routine's authority to perform.

**Exact next recommended billing task:** Once real Home Assistant config/
dashboard YAML and a populated entity inventory exist in this repository,
inspect the actual `meter_board`/billing architecture (if any) and begin
with the charter's highest priority: a reusable, touch-friendly Back
navigation control, applied to billing views first, then the billing
history/analytics work. Until then, re-verify on each scheduled run whether
the bootstrap has happened before attempting further billing work.
