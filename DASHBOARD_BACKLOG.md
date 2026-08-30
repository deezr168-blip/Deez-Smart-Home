# DASHBOARD_BACKLOG.md

Shared backlog for future dashboard work across all routines. Add items
under your routine's section; do not remove or reprioritize another
routine's items.

This file was created 2026-08-30 by the Billing Dashboard routine.

## Billing

- P1: Establish where Home Assistant Lovelace/dashboard config lives in
  this repo (currently nowhere) — prerequisite for all billing UI work.
- P1: Populate `docs/entity_inventory.md` (Stage 2) so billing YAML can
  reference verified, real entity IDs instead of none.
- P2: Run a first read-only Gmail/Google Drive bill-discovery pass and
  validate the proposed bill record schema in `BILLING_PROGRESS.md`
  against real bill samples.
- P2: Build the first minimal parent-facing billing card (provider,
  utility, period, due date, amount, Paid/Unpaid) once a dashboard and
  data model exist.
- P3: Billing history view with All/Electricity/Gas/Water filtering.
- P3: YTD analytics (original cost vs actual paid vs savings).

## Navigation (cross-cutting, Back-button priority)

- P1: Reusable, touch-friendly Back control — cannot be built as
  "improve existing navigation" since no dashboard/navigation currently
  exists in this repo. First implementation, not an iteration.
