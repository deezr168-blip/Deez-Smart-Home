# BILLING_PROGRESS.md

Owned by the Billing Dashboard routine. Tracks billing dashboard UX,
billing history/analytics, bill-ingestion architecture, and billing
supporting code for Deez Smart Home.

## Current billing architecture

None yet. There is no billing dashboard, no `meter_board`, no
`bills.json`, and no `paid_state.json` anywhere in this repository, and
no `ha-deploy` branch/history to inherit prior work from. This repo is
currently a bare scaffold (`README.md`, `CLAUDE.md`, `docs/entity_inventory.md`
+ empty `.gitkeep`'d directories for `home-assistant/`, `safework/`,
`scripts/`, `docs/`).

## Implemented features

None yet.

## Ingestion status

Not started. Gmail and Google Drive MCP tools are available read-only in
this session, but no bill-discovery pass has been run yet — there is
currently nowhere in the repo to land normalized bill records, and no
confirmed billing entity/account context to cross-check extraction
against (see Blockers).

## Data sources

- Live Home Assistant instance (read-only, via MCP) — confirmed reachable.
  Has general energy/solar monitoring entities but no billing-domain
  entities (checked `utility_meter` domain and name search for "bill" —
  both empty).
- Gmail / Google Drive — available via MCP, not yet used. Intended future
  source for bill discovery per the routine's ingestion design, once a
  storage location and schema exist.

## Schema decisions

Proposed only, not yet implemented. A future `bills.json`-equivalent
record should retain, per bill, where available:

```
{
  "id": "<stable id, e.g. provider+period hash>",
  "provider": "",
  "utility_type": "electricity | gas | water | internet | other",
  "billing_period_start": "YYYY-MM-DD",
  "billing_period_end": "YYYY-MM-DD",
  "issue_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "usage": { "value": null, "unit": "" },
  "original_cost": null,
  "discounts_credits": null,
  "final_amount_payable": null,
  "payment_status": "unpaid | paid",
  "source": { "type": "gmail | drive | manual", "ref": "" },
  "extraction_confidence": "confirmed | uncertain",
  "notes": ""
}
```

`payment_status` is always user-set; ingestion may only ever write
`unpaid`, never `paid`. Fields with uncertain extraction should be left
`null` and flagged via `extraction_confidence: "uncertain"` rather than
guessed. No account numbers, NMI/MIRN, or other unnecessary private
identifiers should be stored in `source.ref` or `notes`.

This schema is a starting proposal for the next run to validate against
real bill samples once ingestion begins — not a committed contract.

## Recent commits

- 2026-08-30: Bootstrapped `PROJECT_STATE.md`, `BILLING_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md` after finding no prior
  billing/dashboard work exists in this repo. No dashboard/ingestion code
  written this run.

## Known limitations

- No dashboard exists at all, so there is no Back-navigation to verify or
  extend, and no billing UI to reorganize.
- `docs/entity_inventory.md` is unpopulated, so no entity IDs can be
  safely referenced yet.

## Live-verification requirements

None yet — nothing has been built to verify.

## Exact next priorities

1. Establish (with a human, or in coordination with Main CasaRay Upgrade)
   where Home Assistant Lovelace config lives in this repo.
2. Populate `docs/entity_inventory.md` (Stage 2, per that file) so future
   billing YAML can reference real entities.
3. Run a first read-only Gmail/Drive bill-discovery pass once there is a
   confirmed place to land normalized records, and validate the schema
   above against real bill samples before treating it as final.
4. Only after 1–3: build the first minimal billing card/dashboard section
   and the reusable Back control, per the routine's stated priorities.
