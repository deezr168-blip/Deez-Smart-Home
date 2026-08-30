# Billing progression record

Historical record of billing-specific work: `dashboards/deez_smart_home.yaml`
batches touching `bills`/`bill-*`, billing data-architecture decisions, and
bill-ingestion design. Newest first. Owned by the Billing Dashboard Upgrade
routine — see `PROJECT_STATE.md` for cross-routine coordination state and
`DASHBOARD_PROGRESS.md` for the general dashboard record.

> Authority: `PROJECT_STATE.md` is current coordination state,
> `DASHBOARD_BACKLOG.md` is the billing work queue (`BILL-*` items). This
> file is historical narrative and carries no priority list.

**Verification.** "Validated" means `scripts/ha_validate.sh` passed. It does
not mean anything rendered. See `DASHBOARD_BACKLOG.md` / `PROJECT_STATE.md`
for live-verification state; billing items do not yet have dedicated rows in
`DASHBOARD_ISSUES.md` since none has been a regression — they are tracked as
`BILL-*` backlog items instead.

---

## Current billing architecture (as found, 2026-08-30)

- **Bill entry is entirely manual.** Each of six bill types (Electricity,
  Gas, Car Insurance, Council Rates, South East Water, VicRoads Rego) has its
  own `input_number`/`input_boolean`/`input_datetime` helpers for amount,
  due date, period start and a paid toggle. There is no historical store —
  entering a new bill overwrites the previous cycle's helper values (a
  "previous bill" `input_number` keeps only the immediately prior amount).
- **No `bills.json`, `paid_state.json` or `meter_board` architecture exists
  anywhere in this repository.** The task brief that seeded this routine
  assumed that data model already existed; it does not. `BILL-002`/`BILL-003`
  below start from a clean slate, not an extension of prior work.
- Electricity and gas get a rough in-cycle estimate from
  `sensor.electricity_bill_estimate` / `sensor.gas_bill_estimate` (Powerpal
  for electricity; gas requires MJ entered manually). The other four utilities
  show only the last entered invoice/renewal amount.
- Per-utility status (`Paid`/`Overdue`/`Due soon`) comes from
  `sensor.electricity_bill_status` / `sensor.gas_bill_status`, driving icon
  colour on the `bills` landing tiles.
- The `bills` landing view (`dashboards/deez_smart_home.yaml` ~L4015) is a
  tile grid, one tile per utility, tap-to-navigate into that utility's
  subview. Layout already reviewed and fixed under `UI-016` (`9b28fdb`) — one
  column per subview, no nested grids. No changes needed there for BILL-001.
- **None of the bill sensors are exposed to Home Assistant's Assist surface**
  (`sensor.bills_unpaid_count`, `sensor.bills_outstanding_total`,
  `sensor.electricity_bill_status`, the `*_bill_estimate` sensors) — confirmed
  this run via the read-only `GetLiveContext` connector (`name: bill` →
  "No exposed entities matched"). Their existence and current values can only
  be trusted from what the dashboard YAML already references; this
  environment cannot independently confirm them.

---

## Recent batches

### `<PENDING_SHA>` — NMI/MIRN blocked, account numbers de-hardcoded (`BILL-001`, partial)
Area: `bill-electricity` (~L4238), `bill-gas` (~L4323).
Both subviews' plan-details `markdown` cards carried the real, live account
number as a literal digit string, alongside the NMI (electricity) and MIRN
(gas) — see `DEPLOYMENT_BLOCKERS.md` Blocker 5 and `BILL-001` in
`DASHBOARD_BACKLOG.md` for the full history (a `a084482` sanitisation to
`input_text` helpers, reverted by `921315e`'s wholesale re-import of the
owner's live export — not a deliberate re-exposure decision, per the
backlog's own note).
Fixed the account-number half: both markdown blocks now render
`{% set a = states('input_text.elec_account_number') %}{{ a if a not in
['unavailable','unknown','none',''] else 'Not entered' }}` (gas: the
`_gas_account_number` equivalent) instead of the literal. Both helper
entities were already referenced elsewhere in the same view's `entities`
card (the "Account number" form field), so this is not a new entity
reference — it reuses what the card's own edit form already writes to.
Guarded the same way the rest of the file guards a possibly-empty/unknown
state, rather than assuming the helper is always populated.
**NMI and MIRN are still hardcoded** (`6407640515` electricity,
`5310552355` gas) and are **not** fixed by this batch. No `input_text`
helper exists for either, and this routine cannot create Home Assistant
helpers (no `/config` access, and inventing an entity ID without one
existing violates the project's never-invent-entity-IDs rule — see
`CLAUDE.md`). Recorded as `BILL-001`'s remaining, blocked scope in
`DASHBOARD_BACKLOG.md`: the owner needs to either create
`input_text.elec_nmi` / `input_text.gas_mirn` in Home Assistant (after which
a follow-up batch wires them up exactly like the account numbers), or decide
the NMI/MIRN text should simply be removed from the card. Not guessed either
way.
**Also note:** removing the literals from the current tip does not remove
them from Git history — they remain readable at `a084482`'s parent and
`921315e`. `DEPLOYMENT_BLOCKERS.md` Blocker 5 already documents this and the
repository stays private as the mitigating control; this batch does not
change that history and was not asked to.
Validated: `bash scripts/ha_validate.sh` passed clean (7/7 sections);
templates 384 → 386 (2 new guarded expressions), 36/36 views resolve, no
entity loss, no protected path touched, no credential-shaped literal
introduced.
Expect: no visible change if `input_text.elec_account_number` /
`..._gas_account_number` are already populated with the same digits the
owner had entered into the Bills form; if either helper is empty, the card
now reads "Not entered" instead of a stale/wrong number. NMI and MIRN
unchanged. **FIXED — AWAITING LIVE VERIFICATION** (repository-side check
only; nothing here can confirm what actually renders).

---

## `BILL-002` scope proposal (design only, no implementation this run)

Written this run per the "prefer structured bill storage rather than
embedding historical bill data directly into Lovelace YAML" direction. Not
started — recorded here so a future batch does not re-derive it, and so the
owner can react before code is written.

**Why now:** the current architecture (above) has no history at all — each
new bill entry overwrites the last, keeping only a single "previous bill"
number per utility. Building "bill history" or "YTD" cards against that
today would mean fabricating numbers, which the project's own rules and this
routine's brief both forbid.

**Proposed shape:**
1. **Storage.** A JSON file per utility-type, or one JSON keyed by utility,
   committed under a new `billing/` path in this repository (not
   `dashboards/`) — e.g. `billing/history.json` — holding one record per
   billing period: provider, utility type, period start/end, issue date, due
   date, usage, original/pre-discount cost, discounts/credits, final amount
   payable, payment status, source traceability. This matches the field list
   in this routine's brief and keeps historical data out of the Lovelace YAML
   entirely, addressing `BILL-002`'s own blocker note about unconfirmable
   sensor-driven figures — a repository-stored record does not depend on a
   live sensor being exposed.
2. **Population, this phase:** manual only. A new bill closes out (marked
   Paid, or a new period starts) → the current `input_number`/`input_boolean`
   values for that utility get appended to `billing/history.json` as one more
   record, once a mechanism to do that append exists. This phase does not
   yet decide what writes that record (a Node-RED/pyscript automation living
   in HA config is plausible but is HA configuration, outside this routine's
   authority to create; an owner-run script is another option). Flagging as
   an open question rather than guessing.
3. **Dashboard read side:** a new `bills-history` subview (parallel to the
   six existing `bill-*` subviews) reading `billing/history.json` — but
   Lovelace/storage-mode dashboards cannot read an arbitrary repository file
   at render time without a `sensor` or `template` HA can evaluate. This is
   the open architectural question for `BILL-002`: either (a) a File/RESTful
   or template sensor in HA config exposes the JSON's contents as
   attributes the dashboard can template against, or (b) the JSON is
   ingested into HA's recorder/statistics via helper entities and the
   dashboard uses native History/Statistics-graph cards against those. Both
   require HA configuration changes outside this repository and this
   routine's current authority — **this is the actual blocker for
   `BILL-002`**, not dashboard YAML effort.
4. **Filtering (All/Electricity/Gas/Water):** once (3) is resolved, a
   `select`/`input_select` filter and a template-driven history list/table
   is a normal dashboard build — no new architecture needed at that point.
5. **Charts:** native HA `statistics-graph` or `history-graph` cards once (3)
   exposes the data as HA statistics; a bar/line comparison of
   original-cost vs. actual-paid vs. savings is a card-composition problem
   once real numbers exist, not before.

**Do not build:** any `bills-history` card against invented or assumed
sensor names before (3) is resolved by the owner — that would produce a
"Sensor Unavailable" card or, worse, one that quietly renders nothing
useful. `BILL-002` stays `PLANNED` in `DASHBOARD_BACKLOG.md` until the owner
picks a direction for (3).

---

## Ingestion (`BILL-003`)

Not started, and correctly blocked: `BILL-001`'s NMI/MIRN portion is still
open, and `BILL-003` additionally depends on `BILL-002`'s storage model
existing before ingestion has anywhere safe to write. Per this routine's
brief: discovery/extraction may eventually be automated (Gmail/Google Drive,
read-only), but uncertain extracted values require review and payment status
stays user-controlled — never auto-marked Paid. No Gmail/Drive calls were
made this run; there was nothing safe yet for them to feed.

---

## Known limitations / live-verification requirements

- Nothing in this environment can confirm what actually renders on the iPad.
  Every entry above validated only against `scripts/ha_validate.sh`.
- Bill sensors are not exposed to Assist — this routine cannot independently
  confirm `sensor.electricity_bill_status`, the `*_bill_estimate` sensors, or
  `sensor.bills_unpaid_count`/`bills_outstanding_total` still exist or hold
  sane values; it can only confirm they are referenced consistently in the
  YAML.
- `BILL-002`'s history-store design is a proposal, not a decision — needs
  owner input on how HA config should expose repository-stored history data
  to the dashboard (see point 3 above) before any implementation batch.

## Exact next billing task

1. **If the owner has looked at `BILL-001`:** either create
   `input_text.elec_nmi` and `input_text.gas_mirn` helpers in Home Assistant
   (then a follow-up batch wires them into `bill-electricity`/`bill-gas`
   exactly like the account numbers), or confirm the NMI/MIRN text should be
   removed from the card outright.
2. **Otherwise, next actionable Billing work:** react to the `BILL-002`
   scope proposal above — specifically, decide how HA should expose
   `billing/history.json` (or equivalent) to the dashboard (proposal point
   3). That decision is what unblocks real implementation of bill history
   and YTD analytics, not further dashboard YAML work.
3. `BILL-003` (ingestion) stays blocked until both of the above move.
4. Back navigation: per `PROJECT_STATE.md`, already complete (35/36 views)
   and needs a live look only — no rebuild attempted this run, consistent
   with this routine's own brief.
