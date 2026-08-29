# Dashboard backlog

Queued work for `dashboards/deez_smart_home.yaml` and its supporting files.
`PROJECT_STATE.md` holds the priority model, queue-selection rules, ownership
and Recent Change Protection; this file holds the items themselves.
`DASHBOARD_ISSUES.md` remains the regression and bug record — an item here
that fixes a tracked defect cites its `UI-`/`REG-` ID rather than restating it.

**Active queue = actionable or queued work only.** Completed work moves to
"Awaiting live verification" below and then out to `DASHBOARD_ISSUES.md`.
Nothing is marked verified from repository evidence.

Every active item carries: stable ID · priority · owning routine · affected
area · objective · state · dependencies/blockers · verification requirement.

---

## Active queue

Ordered by priority, then by ID. Priority definitions and selection rules are
in `PROJECT_STATE.md`.

### P1 — High

#### `BILL-001` — billing privacy remediation
- **Owner:** Billing Dashboard Upgrade
- **Area:** `bill-electricity` (~L4242), `bill-gas` (~L4327)
- **Objective:** remove the hardcoded account numbers, NMI and MIRN from the
  two markdown cards so they are not carried in Git.
- **State:** `PLANNED` — actionable
- **Blockers:** owner decision on whether the *live card* should still display
  these identifiers. Repository removal is safe either way; if the card must
  keep showing them, source them from a helper or `secrets.yaml` rather than
  a literal.
- **Verification:** secret scan clean, plus a live look at both bill subviews
  to confirm nothing reads empty.
- **Notes:** the earlier sanitisation (`a084482`) was **not** deliberately
  reversed — it was lost when `921315e` re-imported the owner's authoritative
  live export wholesale. Re-sanitising is therefore consistent with prior
  intent, not a reversal of an owner decision. Three further `name: Account
  number` strings (`bill-electricity`, `bill-gas`, `bill-water`) are form-field
  labels carrying no value and are **not** part of this item.

#### `UI-011` — Total Solar unit assumption
- **Owner:** Main CasaRay Upgrade
- **Area:** `energy` — Total Solar
- **Objective:** confirm the Wh→kWh conversion applied in `df457e3` matches
  what the Fronius total actually reports.
- **State:** `LIVE_VERIFICATION_REQUIRED` — **not actionable in the repository**
- **Blockers:** needs one look at the live card by the owner. Nothing to
  implement until then.
- **Verification:** owner reads the live Total Solar figure and compares it to
  its two sibling Primo sensors.
- **Notes:** if the Fronius total reports kWh directly, the figure reads 1000×
  low. Per queue rule 4 this item does not block lower-priority work.

### P2 — Improvement

#### `UI-027` — heading-card contrast
- **Owner:** Main CasaRay Upgrade
- **Area:** 52 native `heading` cards; `themes/deez_your_name.yaml`
- **Objective:** give heading cards a theme-level surface or text-shadow rule
  so section labels stay legible over the bright horizon band of the
  background photograph.
- **State:** `PLANNED` — actionable
- **Blockers:** none to implement; confirming the result needs a live look.
- **Verification:** live look at a view whose headings sit over the bright band.
- **Notes:** theme-level per the global-first design rule — not 52 `card_mod`
  blocks. The 69 title and chip cards were already fixed in the dashboard.
  Priority is arguable: see the open question in `PROJECT_STATE.md`.

#### `BILL-002` — bill history and analytics
- **Owner:** Billing Dashboard Upgrade
- **Area:** `bills` and the six `bill-*` subviews
- **Objective:** bill history and analytics supporting the parent-friendly
  workflow — global priority 3.
- **State:** `PLANNED` — scope not yet written
- **Blockers:** bill sensors (`sensor.bills_unpaid_count`,
  `sensor.bills_outstanding_total`) are not exposed to Assist and cannot be
  read from this environment, so figures cannot be confirmed here.
- **Verification:** live look; figures confirmed by the owner.

#### `BILL-003` — automatic utility-bill ingestion
- **Owner:** Billing Dashboard Upgrade
- **Area:** ingestion architecture; billing-supporting repository files
- **Objective:** design, then implement, automatic utility-bill ingestion —
  global priority 4.
- **State:** `PLANNED` — design stage
- **Blockers:** depends on BILL-001 landing first (do not build ingestion on
  top of an unresolved privacy exposure). External account actions, bill
  payment and email sending are protected and out of scope.
- **Verification:** design reviewed by the owner before implementation.

### P3 — Polish

#### `BILING-RESID` — residual bilingual gaps (REG-004, REG-005, REG-006)
- **Owner:** Main CasaRay Upgrade
- **Area:** `people-locations` (~L2872); `ipad-command-center` WAN chip
  (~L3662); `home` Energy tile (~L450)
- **Objective:** wrap the three remaining bare-English fragments the way the
  rest of the file already does.
- **State:** `PLANNED` — actionable
- **Blockers:** none
- **Verification:** live look with the language toggle on.
- **Notes:** grouped because they are one continuation of the UI-012 →
  UI-028 → UI-029 sequence, not three independent defects. Individual REG IDs
  and their per-finding evidence stay in `DASHBOARD_ISSUES.md`; REG-005 may
  instead be closed as intentional if the owner confirms an untranslated dash
  is wanted. REG-001, originally grouped here (the three `security` door
  cards' Open/Closed clause), was fixed together with REG-002/REG-003 in
  `b5eee22` and moved to "Awaiting live verification" below.

#### `DR-001` — iPad Command Center density
- **Owner:** Main CasaRay Upgrade (raised by CasaRay Design Reviewer)
- **Area:** `ipad-command-center`
- **Objective:** review information density — 52 cards, never reviewed end to
  end for hierarchy.
- **State:** `PLANNED` — advisory item, no implementation agreed
- **Blockers:** should follow the P1/P2 items above; respects Active Change
  Windows per queue rule 8.
- **Verification:** design review, then a live look on the iPad itself.
- **Notes:** the structural complaints from UI-015 (nested grids, duplicated
  camera chip row) are already fixed by `99a77b4` and `9b28fdb`. What remains
  is a hierarchy question, not a defect.

---

## Awaiting live verification

Implemented, validated and pushed; visible result never confirmed. **Not
active queue work** — no routine should re-implement these. Full records in
`DASHBOARD_ISSUES.md`.

| Area | Items | Last commit |
|---|---|---|
| Reassuring/false-safe status + bilingual door text | REG-001, REG-002, REG-003 | `b5eee22` |
| Bilingual pass (chrome, status text, number-glued fragments) | UI-012, UI-028, UI-029 | `f04a59f` |
| Back / previous-page navigation | UI-009, UI-017 | `34a92e7` |
| Guarded fallbacks / false-state removal | UI-002, UI-005, UI-006, UI-008, UI-018, UI-020, UI-022 | `a5dc914` |
| Layout: nested grids dissolved, duplicate controls removed | UI-013, UI-014, UI-015, UI-016, UI-019, UI-021 | `9b28fdb` |
| Presentation and placeholders | UI-007, UI-010, UI-023, UI-024 | `3048e54` |

Verified by the owner and closed: UI-025, UI-026.

---

## Maintaining this file

- Writer routines add, re-state and close their own items.
- Advisory routines may add evidence-based items and re-prioritise, but must
  not implement production dashboard changes.
- When two entries describe substantially the same work, merge them and keep
  the evidence and status from both — do not delete the losing entry's history.
- Move completed work out of the active queue in the same commit that
  completes it.
