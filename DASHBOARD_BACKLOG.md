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
| `BILL-002` | P2 | Billing | `billing/` (storage, done) + `bills` + six `bill-*` subviews (read side, blocked) | Bill history and analytics for the parent-friendly workflow (global priority 3) | `PARTIAL` — storage layer scaffolded (`billing/schema.json`, `billing/history.json`, empty); dashboard read side `BLOCKED` on owner decision | 4 | 4 | 3 | **1** | Bill sensors (`sensor.electricity_bill_status`, `*_bill_estimate`, etc.) are not exposed to Assist (confirmed via `GetLiveContext`, no match) — figures unconfirmable from here. Storage no longer blocks progress; the remaining blocker is purely the HA-exposure mechanism (see `billing/README.md` point 2) — owner must pick one before any `bills-history` dashboard work starts. Verify: live look, figures confirmed by owner |
| `BILL-003` | P2 | Billing | Ingestion architecture | Design then implement automatic utility-bill ingestion (global priority 4) | `PLANNED` — design stage, blocked | 4 | 5 | 4 | **−1** | Blocked on `BILL-001` (NMI/MIRN portion still open) and on `BILL-002`'s storage model. Verify: design reviewed by owner before implementation |
| `UI-032` | P2 | Main | `cameras`, `security`, or a maintenance section on `home` | Surface device battery levels — the dashboard shows 2 of ~12 live battery entities, and three are already low | `BLOCKED` — needs confirmed entity IDs | 4 | 2 | 3 | **3** | Scouted from live read-only data 2026-08-30, see notes below. Blocked by `DEPLOYMENT_BLOCKERS.md` Blocker 3: the connector returns friendly names, never `entity_id`, and this instance has **demonstrated** name↔ID divergence, so the IDs cannot be inferred. Unblocked by a Developer Tools → States export. Verify: live look, plus one battery confirmed against its real reading |
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
- **`UI-032`** — scouted 2026-08-30 from a read-only `GetLiveContext` sweep of
  the `sensor` domain, the first live entity data any run has had. Three
  findings, recorded as claims per the Entity Scout rule:

  1. **Coverage gap.** The dashboard references exactly two battery entities
     (`sensor.aqara_roller_shade_driver_e1_battery`,
     `sensor.powerpal_gateway_powerpal_battery`), both correctly guarded. The
     live `sensor` domain exposes roughly a dozen.
  2. **Three are already low**, and nothing on the dashboard would tell the
     household: **Front Door Battery 21%**, **RingRing Battery 21%**, **Tapo
     C425 – North Wall Battery 29%**. The `cameras` view's chip reads "6/6
     online" — true, and silent about the 29%. This is an omission, not a
     false-safe assertion, which is why it is P2 rather than P1.
  3. **Why it is blocked, with evidence.** Entity IDs must not be inferred
     from friendly names *in this instance specifically*. Two live
     observations show why:
     - **Name↔ID divergence is real here.** The dashboard uses
       `sensor.living_room_living_hue_hue_sensor_temperature`; the live
       friendly name is "Living Hue Hue Sensor Temperature", which would
       slugify to `living_hue_hue_sensor_temperature`. The working ID and the
       current name already disagree.
     - **Stale duplicates exist.** "Tapo C420 - South Wall Battery" appears
       **twice** live — once at 100%, once `unavailable` — and "Tapo C420 East
       Wall Battery" (`unavailable`) sits beside "Tapo C420 - East Wall
       Battery" (100%). A card built on a guessed ID could bind to the dead
       duplicate and read "unavailable" forever: precisely the false-status
       class REG-001..013 has been clearing all session.

  So this stays `BLOCKED` rather than being attempted with plausible IDs. It
  becomes a straightforward P2 batch — a guarded battery row following the
  existing Powerpal card's convention — the moment a States export lands.

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
| Missing title-card `card_mod` text-shadow on 4 of 29 title cards dashboard-wide (`bill-car-insurance`, `bill-water`, `bill-council-rates`, `bill-rego`) — added the same block already used by the other 25 | `BILL-005` | `73813e8` |
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

Verified by the owner and closed: UI-025, UI-026, UI-011 (Total Solar
Wh→kWh conversion — see `DASHBOARD_ISSUES.md`; removed from the active queue
per rule 12, no longer `LIVE_VERIFICATION_REQUIRED`).

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
