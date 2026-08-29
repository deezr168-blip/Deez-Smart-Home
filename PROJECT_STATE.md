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

| Level | Class | Covers |
|---|---|---|
| **P0** | Critical | Broken functionality, deployment/validation failures, data-loss risk, security/privacy exposure, critical regression. |
| **P1** | High | Major usability problems, broken or inferior navigation, important functional regressions, significant incorrect state presentation, billing privacy remediation, accessibility problems materially affecting use. |
| **P2** | Improvement | Meaningful architecture improvements, new useful features, contextual controls, information-hierarchy improvements, worthwhile CasaRay convergence, billing functionality and analytics. |
| **P3** | Polish | Cosmetic refinement, minor spacing, typography tweaks, icon consistency and other low-risk visual optimization. |

### Queue selection

1. Writer routines must inspect `PROJECT_STATE.md`, `DASHBOARD_ISSUES.md` and
   `DASHBOARD_BACKLOG.md` before independently selecting new work.
2. Normally select the highest-priority **actionable** item owned by that
   routine.
3. A lower-priority item must not displace an actionable higher-priority item
   merely because it is easier, more visually interesting or faster.
4. Higher-priority items that are `BLOCKED` or purely
   `LIVE_VERIFICATION_REQUIRED` do not prevent implementation of the next
   actionable priority.
5. Do not let accumulated live-verification items stall autonomous
   development. They stay queued for human verification while safe
   implementation continues elsewhere.
6. **P0 may override Recent Change Protection** when necessary.
7. **P1 may override Recent Change Protection** when there is concrete
   evidence of a regression, privacy problem or significant usability
   failure. Record the reason.
8. P2/P3 work should normally respect Active Change Windows.
9. **Specialist ownership still takes precedence over priority.** Main CasaRay
   must not implement a Billing-owned P1 merely because it outranks Main's P2
   work — leave that P1 for Billing and select Main's highest actionable owned
   item.
10. Advisory routines may create and re-prioritise evidence-based queue items
    but must not implement production changes.
11. Deduplicate issue and backlog entries describing substantially the same
    work. Preserve the useful history and status of both — do not simply
    delete evidence.
12. Completed items must not remain in the active queue.
13. Every active queue item should identify, where applicable: stable ID ·
    priority · owning routine · affected area · concise objective · current
    state · dependencies/blockers · verification requirement.

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
- Inspect recent commits, `DASHBOARD_ISSUES.md` and `DASHBOARD_BACKLOG.md`
  before modifying an area.
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
| Coordination state (`PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md`) | Shared — writer routines update their own rows and items | `ecc8af7` — 2026-08-29 23:35 | `PUSHED` | 2026-08-30 05:35 | Structure is settled. Routines append to their own sections, rows and backlog items rather than restructuring the files. |
| Back / previous-page navigation (all views) | Billing Dashboard Upgrade (approved global pattern) | `34a92e7` — 2026-08-28 19:44 | `LIVE_VERIFICATION_REQUIRED` | expired 2026-08-29 01:44 | Protection expired, but implementation is **complete**: 35/36 views carry a parent-targeted `mdi:arrow-left` chip, `home` is root. Priority 1 needs a live look, not a redesign — rule 9 applies. |

---

## Next Actionable Work

Coordination pointer to each writer's current highest actionable item — not a
duplicate backlog. Full items live in `DASHBOARD_BACKLOG.md`. Advisory
routines may update a pointer when evidence changes priority or status;
ownership stays with the writer. Writers refresh their own pointer after
completing work.

| Routine | Item | Priority | State | Reason Selected |
|---|---|---|---|---|
| Main CasaRay Upgrade | `REG-002` — false-safe motion chips on `lights` and `cameras` | P1 | `PLANNED` — actionable | Highest actionable Main-owned item. Both chips read a confident "Quiet" when every watched sensor is unavailable, which is incorrect state presentation with concrete evidence, so queue rule 7 permits proceeding inside the open bilingual window; the chips were untouched by that pass. `UI-011` is also P1 but purely `LIVE_VERIFICATION_REQUIRED` (rule 4). `BILL-001` is P1 and outranks Main's P2 work, but is Billing-owned — rule 9 leaves it alone. |
| Billing Dashboard Upgrade | `BILL-001` — remove hardcoded account / NMI / MIRN from `bill-electricity` and `bill-gas` | P1 | `PLANNED` — actionable | Highest actionable Billing-owned item, and named explicitly in the P1 class. Blocks `BILL-003`: ingestion should not be built over an unresolved privacy exposure. Repository removal is safe now; only the question of what the live card displays needs the owner. |

---

## Current Work / Blockers

### Main (CasaRay Upgrade)
- Queue: `REG-002` (P1) → `REG-003` (P1) → `UI-027` (P2) → `BILING-RESID`
  (P3) → `DR-001` (P3). Detail in `DASHBOARD_BACKLOG.md`.
- Back-navigation pattern is implemented in the repository: 35 of 36 views
  carry a parent-targeted `mdi:arrow-left` chip; `home` is the root and
  correctly has none. Remaining work on priority 1 is live verification, not
  implementation.
- Bilingual pass is complete across chrome, status words and number-glued
  fragments (`f4e7ec3`, `fa286de`, `f04a59f`). State:
  `LIVE_VERIFICATION_REQUIRED`.
- `UI-011` is P1 but purely `LIVE_VERIFICATION_REQUIRED` — blocked on one
  owner look, not on code, and per queue rule 4 it does not gate the rest.

### Billing
- Six bill subviews (`bill-electricity`, `-gas`, `-car-insurance`, `-water`,
  `-council-rates`, `-rego`) exist, each one section / one column, each with a
  back chip to `bills`. Layout reviewed under `9b28fdb`; no change needed.
- Queue: `BILL-001` (P1) → `BILL-002` (P2) → `BILL-003` (P2).
- **`BILL-001`:** `bill-electricity` and `bill-gas` carry hardcoded account
  numbers, an NMI and a MIRN. Corrected from the earlier record: the
  sanitisation was not deliberately reverted — `a084482` sanitised the old
  baseline and `921315e` then re-imported the owner's authoritative live
  export wholesale, bringing the literals back as a side effect. Resolve
  before widening billing scope.
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
- Queued as backlog items: REG-002 and REG-003 as standalone P1s;
  REG-001/004/005/006 merged into `BILING-RESID` (P3) as one continuation of
  the UI-012 → UI-028 → UI-029 sequence. Per-finding evidence stays in
  `DASHBOARD_ISSUES.md`.
- Auditor is advisory: these are queued for Main, not for the auditor to fix.

### Entity Scout
- `DASHBOARD_BACKLOG.md` now exists — file scout findings there as evidence-
  based items, not in this file. `docs/entity_inventory.md` lives on `main`,
  not on this branch.
- Entity registry is unavailable from this environment; entity existence is
  inferred from the imported live dashboard and has never been confirmed.
  Scout findings should be recorded as claims, not facts.

### Design Review
- Standing items are now backlog entries rather than prose here: `UI-027`
  (heading-card contrast, P2, Main-owned) and `DR-001` (iPad Command Center
  density, P3). Both were duplicated between this file and
  `DASHBOARD_ISSUES.md` — deduplicated under those IDs per queue rule 11.

---

## Last Coordination Update

- **Date/time:** 2026-08-29 23:35 UTC
- **Branch:** `ha-deploy`
- **`ha-deploy` HEAD before this update:** `6741ab885d67f4f104a20ce65e1bb859d07f378b`
  (`6741ab8` — "docs: stamp 07d3ff2 into the coordination state")
- **This update's commit:** `ecc8af7` — priority model, queue-selection
  rules, Next Actionable Work, and `DASHBOARD_BACKLOG.md`.

Per `CLAUDE.md`, a commit cannot contain its own hash: this update's SHA is
written by the `docs: stamp` commit that immediately follows it.
