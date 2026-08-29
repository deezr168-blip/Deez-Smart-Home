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

Priority first, then Selection Score within a priority. Scores are a
tie-breaker, not a ranking of worth — see `PROJECT_STATE.md` for the scales,
the formula and the safeguards.

| ID | P | Owner | Area | I | E | R | Score | State |
|---|---|---|---|---|---|---|---|---|
| `BILL-001` | P1 | Billing | `bill-electricity`, `bill-gas` | 5 | 3 | 3 | **4** | actionable |
| `UI-011` | P1 | Main | `energy` | — | — | — | — | `LIVE_VERIFICATION_REQUIRED` — excluded |
| `UI-027` | P2 | Main | 52 heading cards + theme | 4 | 2 | 3 | **3** | actionable |
| `BILL-002` | P2 | Billing | `bills` + six subviews | 4 | 4 | 3 | **1** | actionable |
| `BILL-003` | P2 | Billing | ingestion architecture | 4 | 5 | 4 | **−1** | blocked on `BILL-001` |
| `BILING-RESID` | P3 | Main | 3 views | 2 | 1 | 1 | **2** | actionable |
| `DR-001` | P3 | Main | `ipad-command-center` | 3 | 4 | 4 | **−2** | actionable |

### P1 — High

#### `BILL-001` — billing privacy remediation
- **Owner:** Billing Dashboard Upgrade
- **Area:** `bill-electricity` (~L4242), `bill-gas` (~L4327)
- **Objective:** remove the hardcoded account numbers, NMI and MIRN from the
  two markdown cards so they are not carried in Git.
- **State:** `PLANNED` — actionable
- **Score:** Impact 5 · Effort 3 · Risk 3 → **4**
- **Blockers:** owner decision on whether the *live card* should still display
  these identifiers. Repository removal is safe either way; if the card must
  keep showing them, source them from a helper or `secrets.yaml` rather than
  a literal.
- **Verification:** secret scan clean, plus a live look at both bill subviews
  to confirm nothing reads empty.
- **Notes:** Impact 5 is the privacy band and is **not** reduced by the effort
  of remediation (scoring safeguard 7), nor is the item demoted from P1 for
  implementation cost. It is Billing's only actionable P1, so the score does
  not affect selection here. The earlier sanitisation (`a084482`) was not
  deliberately reversed; `921315e` re-imported the owner's authoritative live
  export wholesale and the literals came back with it. Three further
  `name: Account number` strings are form-field labels carrying no value and
  are not part of this item.

#### `UI-011` — Total Solar unit assumption
- **Owner:** Main CasaRay Upgrade
- **Area:** `energy` — Total Solar
- **Objective:** confirm the Wh→kWh conversion applied in `df457e3` matches
  what the Fronius total actually reports.
- **State:** `LIVE_VERIFICATION_REQUIRED` — **excluded from autonomous
  selection** (scoring safeguard 3); deliberately not scored.
- **Blockers:** needs one look at the live card by the owner.
- **Verification:** owner reads the live Total Solar figure and compares it to
  its two sibling Primo sensors.
- **Notes:** if the Fronius total reports kWh directly, the figure reads 1000×
  low. Per queue rule 4 this does not gate lower-priority work.

### P2 — Improvement

#### `UI-027` — heading-card contrast
- **Owner:** Main CasaRay Upgrade
- **Area:** 52 native `heading` cards; `themes/deez_your_name.yaml`
- **Objective:** give heading cards a theme-level surface or text-shadow rule
  so section labels stay legible over the bright horizon band of the
  background photograph.
- **State:** `PLANNED` — actionable
- **Score:** Impact 4 · Effort 2 · Risk 3 → **3**
- **Blockers:** none to implement; confirming the result needs a live look.
- **Verification:** live look at a view whose headings sit over the bright band.
- **Notes:** Risk 3 because a theme rule reaches every view and card type —
  broad blast radius despite small effort. Implementing it as a theme rule
  (global-first) also keeps it clear of the Active Change Window `b5eee22`
  opened on four view templates. Priority stays P2 on repository evidence; the
  accessibility argument for P1 is an open question recorded in
  `PROJECT_STATE.md` and is not settled by scoring.

#### `BILL-002` — bill history and analytics
- **Owner:** Billing Dashboard Upgrade
- **Area:** `bills` and the six `bill-*` subviews
- **Objective:** bill history and analytics supporting the parent-friendly
  workflow — global priority 3.
- **State:** `PLANNED` — scope not yet written
- **Score:** Impact 4 · Effort 4 · Risk 3 → **1**
- **Blockers:** bill sensors (`sensor.bills_unpaid_count`,
  `sensor.bills_outstanding_total`) are not exposed to Assist and cannot be
  read from this environment, so figures cannot be confirmed here.
- **Verification:** live look; figures confirmed by the owner.
- **Notes:** Effort 4 is honest for unwritten scope — revise it down once the
  scope is written and proves smaller (scoring safeguard 9).

#### `BILL-003` — automatic utility-bill ingestion
- **Owner:** Billing Dashboard Upgrade
- **Area:** ingestion architecture; billing-supporting repository files
- **Objective:** design, then implement, automatic utility-bill ingestion —
  global priority 4.
- **State:** `PLANNED` — design stage; blocked
- **Score:** Impact 4 · Effort 5 · Risk 4 → **−1**
- **Blockers:** depends on `BILL-001` landing first — do not build ingestion
  over an unresolved privacy exposure. External account actions, bill payment
  and email sending are protected and out of scope.
- **Verification:** design reviewed by the owner before implementation.
- **Notes:** a negative score is not a deletion signal (safeguard 5). This is
  global priority 4 and stays queued; the score only says it should not be
  picked ahead of `BILL-002` at the same priority.

### P3 — Polish

#### `BILING-RESID` — residual bilingual gaps (REG-004, REG-005, REG-006)
- **Owner:** Main CasaRay Upgrade
- **Area:** `people-locations` (~L2872); `ipad-command-center` WAN chip
  (~L3662); `home` Energy tile (~L450)
- **Objective:** wrap the three remaining bare-English fragments the way the
  rest of the file already does.
- **State:** `PLANNED` — actionable
- **Score:** Impact 2 · Effort 1 · Risk 1 → **2**
- **Blockers:** none. `home` sits inside the Active Change Window opened by
  `b5eee22`; as owner of this bilingual sequence Main may continue under
  Recent Change Protection rule 5, but this is P3 and ranks below `UI-027`
  anyway, so the question does not currently bite.
- **Verification:** live look with the language toggle on.
- **Notes:** REG-001 was part of this group and is now fixed in `b5eee22`, so
  the group is REG-004/005/006. **REG-005 stays unresolved by design** —
  whether the untranslated `WAN —` placeholder is intentional is an open owner
  question, not a scoring matter. Per-finding evidence stays in
  `DASHBOARD_ISSUES.md`.

#### `DR-001` — iPad Command Center density
- **Owner:** Main CasaRay Upgrade (raised by CasaRay Design Reviewer)
- **Area:** `ipad-command-center`
- **Objective:** review information density — 52 cards, never reviewed end to
  end for hierarchy.
- **State:** `PLANNED` — advisory item, no implementation agreed
- **Score:** Impact 3 · Effort 4 · Risk 4 → **−2**
- **Blockers:** respects Active Change Windows per queue rule 8.
- **Verification:** design review, then a live look on the iPad itself.
- **Notes:** Risk 4 because the view was rebuilt recently (`99a77b4`) and a
  hierarchy rework would touch all four of its sections. The structural
  defects from UI-015 are already fixed; what remains is a judgment question —
  exactly the kind of item a score should not be used to settle.

---

## Awaiting live verification

Implemented, validated and pushed; visible result never confirmed. **Not
active queue work** — no routine should re-implement these. Full records in
`DASHBOARD_ISSUES.md`.

| Area | Items | Last commit |
|---|---|---|
| Bilingual pass (chrome, status text, number-glued fragments) | UI-012, UI-028, UI-029 | `f04a59f` |
| Back / previous-page navigation | UI-009, UI-017 | `34a92e7` |
| Guarded fallbacks / false-state removal | UI-002, UI-005, UI-006, UI-008, UI-018, UI-020, UI-022 | `a5dc914` |
| Layout: nested grids dissolved, duplicate controls removed | UI-013, UI-014, UI-015, UI-016, UI-019, UI-021 | `9b28fdb` |
| Presentation and placeholders | UI-007, UI-010, UI-023, UI-024 | `3048e54` |
| Reassuring / untranslated status regressions | REG-001, REG-002, REG-003 | `b5eee22` |

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
- Re-score an item when repository evidence changes its expected scope
  (scoring safeguard 9). Never adjust a score to justify preferred work.
