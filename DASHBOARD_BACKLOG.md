# Dashboard backlog

Authoritative detailed work queue. `PROJECT_STATE.md` holds the priority
model, scoring, ownership and concurrency rules; this file holds the items.
`DASHBOARD_ISSUES.md` holds issue evidence — items here cite `UI-`/`REG-` IDs
rather than restating it.

Active queue = actionable or queued work only. Completed work moves to the
reference section below. Nothing is marked verified from repository evidence.

---

## Active queue

Ordered by priority, then Selection Score (`Impact × 2 − Effort − Risk`).
Score breaks ties **within** a priority for one owner; it never outranks
priority or ownership.

| ID | P | Owner | Area | Objective | State | I | E | R | Score | Blocker / verification |
|---|---|---|---|---|---|---|---|---|---|---|
| `BILL-001` | P1 | Billing | `bill-electricity` (~L4238), `bill-gas` (~L4323) | Remove hardcoded NMI and MIRN so they are not carried in Git (account numbers already resolved) | `BLOCKED` — needs owner decision | 5 | 3 | 3 | **4** | No `input_text` helper exists for NMI/MIRN and one must not be invented (never-invent-entity-IDs rule). Owner must either (a) create `input_text.elec_nmi` / `input_text.gas_mirn` helpers in HA so the dashboard can reference them, or (b) approve removing the NMI/MIRN text from the card outright. Verify once resolved: secret scan clean + live look at both subviews |
| `UI-011` | P1 | Main | `energy` — Total Solar | Confirm the Wh→kWh conversion from `df457e3` matches what the Fronius total reports | `LIVE_VERIFICATION_REQUIRED` — excluded from selection, unscored | — | — | — | — | Needs one owner look; if the total reports kWh the figure reads 1000× low |
| `BILL-002` | P2 | Billing | `billing/` (storage, done) + `bills` + six `bill-*` subviews (read side, blocked) | Bill history and analytics for the parent-friendly workflow (global priority 3) | `PARTIAL` — storage layer scaffolded (`billing/schema.json`, `billing/history.json`, empty); dashboard read side `BLOCKED` on owner decision | 4 | 4 | 3 | **1** | Bill sensors (`sensor.electricity_bill_status`, `*_bill_estimate`, etc.) are not exposed to Assist (confirmed via `GetLiveContext`, no match) — figures unconfirmable from here. Storage no longer blocks progress; the remaining blocker is purely the HA-exposure mechanism (see `billing/README.md` point 2) — owner must pick one before any `bills-history` dashboard work starts. Verify: live look, figures confirmed by owner |
| `BILL-003` | P2 | Billing | Ingestion architecture | Design then implement automatic utility-bill ingestion (global priority 4) | `PLANNED` — design stage, blocked | 4 | 5 | 4 | **−1** | Blocked on `BILL-001` (NMI/MIRN portion still open) and on `BILL-002`'s storage model. Verify: design reviewed by owner before implementation |
| `DR-001` | P3 | Main | `ipad-command-center` | Review information density — 52 cards, never reviewed end to end for hierarchy | `PLANNED` — advisory, no implementation agreed | 3 | 4 | 4 | **−2** | Needs a design brief first. Verify: design review, then a live look on the iPad |

### Notes that affect implementation

- **`BILL-001`** — Impact 5 is the privacy band and is not reduced by
  remediation cost; the item is not demoted from P1 for effort. The account
  number half is done (see Awaiting live verification below): both markdown
  blocks now render `{{ states('input_text.elec_account_number') }}` /
  `..._gas_account_number` — entities already used elsewhere in the same
  views, not invented — with a guarded `'Not entered'` fallback, instead of
  the literal digits. NMI and MIRN remain hardcoded: no helper exists for
  either, `!secret` does not work in storage-mode dashboards, and inventing
  a new `input_text.elec_nmi`/`gas_mirn` entity without HA config access
  would mean referencing a nonexistent entity, which the never-invent rule
  forbids. Three `name: Account number` strings (`bill-electricity`,
  `bill-gas`, `bill-water`) are form-field labels holding no value and are
  **not** part of this item.
- **`BILL-003`** — do not build ingestion over an unresolved privacy exposure.
  External account actions, bill payment and email sending are protected and
  out of scope. A negative score is not a deletion signal.
- **`DR-001`** — do not start a 52-card redesign speculatively. The structural
  defects from UI-015 are already fixed; what remains is a judgment question a
  score should not settle. Risk 4 because the view was rebuilt in `99a77b4`.
- **`BILL-002`** — Storage layer now exists (`billing/schema.json` +
  `billing/history.json`, both empty of real data — nothing fabricated).
  Nothing writes to or reads from it yet: population mechanism and HA-side
  exposure are both still open owner decisions, see `billing/README.md`.
  Effort/Risk here reflect the remaining read-side work only; revise once the
  owner picks an exposure mechanism.

---

## Awaiting live verification

Implemented, validated and pushed; visible result never confirmed. **Not
active queue work** — no routine should re-implement these. Full records in
`DASHBOARD_ISSUES.md`.

| Area | Items | Last commit |
|---|---|---|
| False-safe "On" text for an unavailable/unknown light (`lighting-modes` Current State: Living Room, Ray Bedroom, Dining) | `REG-013` | `ccfb0c8` |
| Raw-interpolation/bilingual gaps (`home` Person chip, `home` Climate card, `light-ray-bedroom` Roller Shade) now guarded and bilingual | `UI-031` | `ccfb0c8` |
| Account-number literals replaced with existing `input_text.elec_account_number` / `input_text.gas_account_number` references, guarded (`bill-electricity`, `bill-gas`) | `BILL-001` (account-number portion; NMI/MIRN still open, see active queue) | `23c0301` |
| Bill status/amount cards guarded against raw `unavailable`/`unknown` interpolation — `bills` landing tiles (Electricity, Gas, Car Insurance, Council Rates, South East Water, VicRoads Rego) and the status card on `bill-car-insurance`/`bill-water`/`bill-council-rates`/`bill-rego`, all reusing existing entities | `BILL-004` | `d570a82` |
| Raw unguarded `select()` interpolation on LetPot Grow Light card (`ray-bedroom`) now falls back to em dash / bilingual "Offline" | `UI-030` | `691689a` |
| False-safe door-count aggregates (`home` hero + quick chip + Security card, `cameras` chip row, `ipad-command-center` chip row) — same three-sensor list copy-pasted into 5 cards, now all guarded | REG-007, REG-008, REG-009, REG-010, REG-011 | `b058006` + this run's follow-up commit |
| Residual bilingual gaps (per-person "at home", WAN chip fallback, Energy tile fallback) | REG-004, REG-005, REG-006 | `dff00f3` |
| Heading-card contrast (theme-level `card-mod-card-heading` rule) | UI-027 | `9926233` |
| Reassuring/false-safe status + bilingual door text | REG-001, REG-002, REG-003 | `b5eee22` |
| Bilingual pass (chrome, status text, number-glued fragments) | UI-012, UI-028, UI-029 | `f04a59f` |
| Back / previous-page navigation | UI-009, UI-017 | `34a92e7` |
| Guarded fallbacks / false-state removal | UI-002, UI-005, UI-006, UI-008, UI-018, UI-020, UI-022 | `a5dc914` |
| Layout: nested grids dissolved, duplicate controls removed | UI-013, UI-014, UI-015, UI-016, UI-019, UI-021 | `9b28fdb` |
| Presentation and placeholders | UI-007, UI-010, UI-023, UI-024 | `3048e54` |

Verified by the owner and closed: UI-025, UI-026.

---

## Maintaining this file

- Writer routines add, re-state and close their own items; advisory routines
  may add evidence-based items and re-prioritise, but must not implement
  production dashboard changes.
- Merge entries describing substantially the same work, keeping both sides'
  evidence and status.
- Move completed work out of the active queue in the same commit that
  completes it.
- Re-score when repository evidence changes an item's expected scope. Never
  adjust a score to justify preferred work.
- Do not restate issue evidence that already lives in `DASHBOARD_ISSUES.md`.
