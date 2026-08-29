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
| `BILL-001` | P1 | Billing | `bill-electricity` (~L4242), `bill-gas` (~L4327) | Remove hardcoded account numbers, NMI and MIRN so they are not carried in Git | `PLANNED` — actionable | 5 | 3 | 3 | **4** | Owner decision on whether the live card still displays them. Verify: secret scan clean + live look at both subviews |
| `UI-011` | P1 | Main | `energy` — Total Solar | Confirm the Wh→kWh conversion from `df457e3` matches what the Fronius total reports | `LIVE_VERIFICATION_REQUIRED` — excluded from selection, unscored | — | — | — | — | Needs one owner look; if the total reports kWh the figure reads 1000× low |
| `BILL-002` | P2 | Billing | `bills` + six `bill-*` subviews | Bill history and analytics for the parent-friendly workflow (global priority 3) | `PLANNED` — scope not written | 4 | 4 | 3 | **1** | Bill sensors not exposed to Assist; figures unconfirmable here. Verify: live look, figures confirmed by owner |
| `BILL-003` | P2 | Billing | Ingestion architecture | Design then implement automatic utility-bill ingestion (global priority 4) | `PLANNED` — design stage, blocked | 4 | 5 | 4 | **−1** | Blocked on `BILL-001`. Verify: design reviewed by owner before implementation |
| `DR-001` | P3 | Main | `ipad-command-center` | Review information density — 52 cards, never reviewed end to end for hierarchy | `PLANNED` — advisory, no implementation agreed | 3 | 4 | 4 | **−2** | Needs a design brief first. Verify: design review, then a live look on the iPad |

### Notes that affect implementation

- **`BILL-001`** — Impact 5 is the privacy band and is not reduced by
  remediation cost; the item is not demoted from P1 for effort. If the live
  card must keep showing the identifiers, source them from a helper or
  `secrets.yaml` rather than a literal. The earlier sanitisation (`a084482`)
  was not deliberately reversed: `921315e` re-imported the owner's
  authoritative live export wholesale and the literals returned with it, so
  re-sanitising is consistent with prior intent. Three `name: Account number`
  strings (`bill-electricity`, `bill-gas`, `bill-water`) are form-field labels
  holding no value and are **not** part of this item.
- **`BILL-003`** — do not build ingestion over an unresolved privacy exposure.
  External account actions, bill payment and email sending are protected and
  out of scope. A negative score is not a deletion signal.
- **`DR-001`** — do not start a 52-card redesign speculatively. The structural
  defects from UI-015 are already fixed; what remains is a judgment question a
  score should not settle. Risk 4 because the view was rebuilt in `99a77b4`.
- **`BILL-002`** — Effort 4 reflects unwritten scope; revise down once scoped.

---

## Awaiting live verification

Implemented, validated and pushed; visible result never confirmed. **Not
active queue work** — no routine should re-implement these. Full records in
`DASHBOARD_ISSUES.md`.

| Area | Items | Last commit |
|---|---|---|
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
