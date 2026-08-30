# Structured billing history store

Repository-side storage for historical bill records, kept out of
`dashboards/deez_smart_home.yaml` per the project direction to "prefer
structured bill storage rather than embedding historical bill data directly
into Lovelace YAML." Owned by the Billing Dashboard Upgrade routine. See
`BILLING_PROGRESS.md` for the full narrative and `DASHBOARD_BACKLOG.md`
(`BILL-002`) for status.

## Files

- `schema.json` — JSON Schema (draft-07) for one bill record. Field list
  matches the brief: provider, utility type, billing period, issue/due date,
  usage, original/pre-discount cost, discounts/credits, final payable
  amount, payment status, and source traceability.
- `history.json` — the actual store. Currently `[]`: no bill has been
  appended yet, because no mechanism to append one exists (see "Not yet
  decided" below). This is intentional — nothing here is fabricated or
  backfilled from guesswork.

## Status (2026-08-30)

**Scaffolded, not wired to anything.** This is the storage layer only. Two
things this does *not* do yet:

1. **Nothing writes to `history.json` yet.** The plan is: a bill closes out
   (marked Paid, or a new period starts) → append one record here. What
   performs that append — an HA automation, a pyscript script, an
   owner-run tool — is an open decision, not this routine's to make
   unilaterally (HA configuration changes are outside this routine's
   authority; see `CLAUDE.md`).
2. **Nothing reads from `history.json` yet.** Lovelace (storage-mode)
   cannot read an arbitrary repository file directly at render time. Before
   any `bills-history` dashboard subview or chart can be built against real
   data, the owner needs to pick how Home Assistant exposes this file's
   contents to the dashboard — e.g. a File/RESTful/template sensor, or
   ingesting records into HA's recorder/statistics. See `BILLING_PROGRESS.md`
   → "`BILL-002` scope proposal" for the fuller writeup of that decision.

Until (1) and (2) are resolved, **do not** build a `bills-history` card
against invented or assumed sensor names, and do not hand-populate
`history.json` with real bill figures pulled only from memory/guesswork —
every record here must be traceable to something the owner entered or an
ingestion pipeline (`BILL-003`) actually extracted.

## Privacy

Bill records may reference a provider name, dates, and amounts. They must
**not** contain account numbers, NMI/MIRN, policy numbers, customer numbers
or other unnecessary private identifiers — those stay in Home Assistant
`input_text` helpers (already the existing pattern for the dashboard's own
bill-entry forms), never duplicated into this repository-tracked file. The
`source.reference` field is for a non-sensitive pointer (a message/file id),
not document content.

## Payment status is always user-controlled

`payment_status` starts `"unpaid"` for every new record and is only ever
flipped to `"paid"` by an explicit user action reflected back into this
store. No automated process — ingestion included — may set it to `"paid"`.
