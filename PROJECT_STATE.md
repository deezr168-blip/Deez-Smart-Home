# PROJECT_STATE.md

Authoritative coordination state for all autonomous Home Assistant dashboard
routines. **Read this file before starting autonomous work.** It is kept short
on purpose so every routine can load it cheaply at the start of each run.

---

## Project

- **Repository:** `deezr168-blip/Deez-Smart-Home`
- **Deployment branch:** `ha-deploy`
- **Primary dashboard:** `dashboards/deez_smart_home.yaml`
- **Deployment model:** validated GitHub changes are polled/deployed by Home
  Assistant independently. No routine deploys, restarts or reloads anything —
  pushing a validated commit to `ha-deploy` is the whole handoff.

---

## Routine Ownership

### Main CasaRay Upgrade
- Owns general dashboard UX and implementation.
- May modify `dashboards/deez_smart_home.yaml`, except specialist-owned
  billing areas.

### Billing Dashboard Upgrade
- Owns billing-specific dashboard UX, bill history, analytics,
  bill-ingestion architecture, and billing-supporting repository files.
- May also implement the approved global Back-navigation pattern.

### Regression Auditor
- Advisory / audit only.
- May modify tracking and documentation files, but **not** production
  dashboard YAML.

### Entity & Feature Scout
- Advisory / audit only.
- May modify backlog and tracking files, but **not** production dashboard YAML.

### CasaRay Design Reviewer
- Advisory / design-review only.
- May modify backlog and tracking files, but **not** production dashboard YAML.

---

## Protected Areas

All autonomous routines must treat these as protected unless explicitly
authorized:

- Home Assistant authentication and secrets
- Deployment scripts and deployment automation
- Git authentication and infrastructure
- Core Home Assistant configuration
- Live entity/device deletion
- Destructive helper or integration changes
- External account actions, bill payment, or email sending

---

## Priority Model

| Level | Meaning |
|---|---|
| **P0** | Broken functionality / critical regression |
| **P1** | Major usability or navigation improvement |
| **P2** | Architecture / feature improvement |
| **P3** | Visual polish / optimization |

---

## Verification States

| State | Meaning |
|---|---|
| `PLANNED` | Agreed and scoped, not yet written |
| `CODE_VALID` | Written and passing repository validation |
| `PUSHED` | Committed and pushed to `ha-deploy` |
| `DEPLOYED` | Home Assistant has picked the commit up |
| `LIVE_VERIFICATION_REQUIRED` | Deployed; visible result not yet seen |
| `LIVE_VERIFIED` | Confirmed correct on the live frontend by the owner |
| `BLOCKED` | Cannot proceed; blocker recorded below |

---

## Current Global Priorities

1. Consistent Back / previous-page navigation across appropriate dashboard views
2. Continue CasaRay / native HA convergence
3. Billing dashboard architecture and parent-friendly bill workflow
4. Automatic utility-bill ingestion design and implementation
5. Regression cleanup and live verification

---

## Coordination Rules

- Read this file before autonomous work.
- Respect routine ownership boundaries.
- Inspect recent commits before modifying an area.
- Do not duplicate work already underway.
- Specialist ownership overrides general ownership.
- Advisory routines queue work rather than implementing production dashboard
  changes.
- Do not claim live verification solely from repository validation.

---

## Recent Change Protection

Stops routines from redesigning each other's freshly landed work before it has
had a chance to reach the live dashboard.

1. Before proposing or implementing work in an area, inspect the relevant
   recent Git history and the shared progress / issue / backlog records.
2. Treat an area substantially modified within the **last 6 hours** as
   recently changed.
3. Recently changed areas should normally be allowed to settle and reach live
   verification before another speculative redesign.
4. The 6-hour protection is **not an absolute lock.** Immediate changes remain
   permitted for:
   - P0 critical regressions
   - broken functionality
   - validation failures
   - security / privacy exposure
   - data-loss risk
   - clearly documented P1 regressions
5. A specialist owner may continue a planned multi-batch implementation in its
   own recently changed area when `PROJECT_STATE.md`, the relevant progress
   file, or Git history clearly shows the work is part of the same coherent
   implementation sequence.
6. Do not use Recent Change Protection to prevent legitimate continuation work
   by the owning routine.
7. Advisory routines may inspect recently changed areas, but should prefer
   marking them `LIVE_VERIFICATION_REQUIRED` rather than immediately queuing
   another redesign, unless evidence shows a real problem.
8. When another routine owns an area, ownership takes precedence over general
   design authority regardless of the age of the previous commit.
9. Avoid multiple routines implementing competing solutions to the same
   problem.
10. Before changing recently modified code, record why overriding the
    protection is justified, when the reason is not obvious from an existing
    P0/P1 issue.

### Active Change Windows

Only areas under substantial active work. This is not a log of every dashboard
edit. Writer routines update their own row after substantial implementation
work; advisory routines may read this table but must not take ownership of a
writer's entry. All times UTC.

| Area | Owning Routine | Last Significant Commit | State | Protected Until | Notes |
|---|---|---|---|---|---|
| Bilingual template pass (status text across all 36 views) | Main CasaRay Upgrade | `f04a59f` — 2026-08-29 20:51 | `LIVE_VERIFICATION_REQUIRED` | 2026-08-30 02:51 | Third and final batch of one sequence (`f4e7ec3`, `fa286de`, `f04a59f`). Continuation by Main is permitted under rule 5; REG-001/004/005/006 are in-sequence fixes, not a redesign. |
| Regression audit record (`DASHBOARD_ISSUES.md`) | Regression Auditor | `3116495` — 2026-08-29 22:49 | `PUSHED` | 2026-08-30 04:49 | Baseline REG-001..006 is fresh — do not re-audit the same range. Findings are queued for Main; the auditor does not implement them. |
| Coordination state (`PROJECT_STATE.md`) | Shared — writer routines update their own rows | `STAMPSHA` — 2026-08-29 23:30 | `PUSHED` | 2026-08-30 05:30 | Structure is settled. Routines append to their own sections and rows rather than restructuring the file. |
| Back / previous-page navigation (all views) | Billing Dashboard Upgrade (approved global pattern) | `34a92e7` — 2026-08-28 19:44 | `LIVE_VERIFICATION_REQUIRED` | expired 2026-08-29 01:44 | Protection expired, but implementation is **complete**: 35/36 views carry a parent-targeted `mdi:arrow-left` chip, `home` is root. Priority 1 needs a live look, not a redesign — rule 9 applies. |

---

## Current Work / Blockers

### Main (CasaRay Upgrade)
- Back-navigation pattern is implemented in the repository: 35 of 36 views
  carry a parent-targeted `mdi:arrow-left` chip; `home` is the root and
  correctly has none. Remaining work on priority 1 is live verification, not
  implementation.
- Bilingual pass is complete across chrome, status words and number-glued
  fragments (`f4e7ec3`, `fa286de`, `f04a59f`). State:
  `LIVE_VERIFICATION_REQUIRED`.
- Open: **UI-011** (P3) Total Solar Wh→kWh assumption needs one live look;
  **UI-027** (P3) heading-card contrast needs a theme-level rule plus a live
  look. Both are blocked on the owner, not on code.
- Next convergence candidates: iPad Command Center review depth, remaining
  Mushroom→native conversions.

### Billing
- Six bill subviews (`bill-electricity`, `-gas`, `-car-insurance`, `-water`,
  `-council-rates`, `-rego`) exist, each one section / one column, each with a
  back chip to `bills`. Layout reviewed under `9b28fdb`; no change needed.
- Not yet started: bill history, analytics, and the parent-friendly workflow
  (priority 3); automatic utility-bill ingestion is still design-stage
  (priority 4) — `PLANNED`.
- **Blocker:** `bill-electricity` and `bill-gas` carry hardcoded account
  numbers, an NMI and a MIRN (sanitisation reverted by `921315e`). Treat as
  P1 and resolve before widening billing scope.
- Bill sensors (`sensor.bills_unpaid_count`,
  `sensor.bills_outstanding_total`) are not exposed to Assist and cannot be
  read from this environment — billing figures are `CODE_VALID` at best.

### Regression
- Baseline audit recorded 2026-08-29 at `7f304ad`; six findings
  **REG-001..REG-006**, all `OPEN`, all unowned.
- REG-001/002/003 MEDIUM: untranslated Open/Closed on three `security` door
  cards; unguarded motion-aggregate chips on `lights` and `cameras` that
  report a reassuring "Quiet" when every sensor is unavailable; `home`
  Network chip with no unavailable branch. REG-002 is the P0-adjacent one —
  it shows false-safe state.
- REG-004/005/006 LOW: three residual untranslated fragments.
- Auditor is advisory: these are queued for Main, not for the auditor to fix.

### Entity Scout
- No backlog file exists yet. `docs/entity_inventory.md` lives on `main`, not
  on this branch.
- Entity registry is unavailable from this environment; entity existence is
  inferred from the imported live dashboard and has never been confirmed.
  Scout findings should be recorded as claims, not facts.

### Design Review
- No design-review backlog file exists yet.
- Standing items handed to review: heading-card contrast over the photographic
  background (UI-027), and iPad Command Center density (52 cards, never
  reviewed end to end).

---

## Last Coordination Update

- **Date/time:** 2026-08-29 23:30 UTC
- **Branch:** `ha-deploy`
- **`ha-deploy` HEAD before this update:** `618347f291a89d6db3f194f746d1a1184b104820`
  (`618347f` — "docs: PROJECT_STATE.md as the coordination state for
  autonomous routines")
- **This update's commit:** `STAMPSHA` — adds Recent Change Protection and the
  Active Change Windows table.

Per `CLAUDE.md`, a commit cannot contain its own hash: this update's SHA is
written by the `docs: stamp` commit that immediately follows it.
