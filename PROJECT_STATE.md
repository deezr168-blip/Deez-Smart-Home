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

- **Date/time:** 2026-08-29 23:14 UTC
- **Branch:** `ha-deploy`
- **Commit SHA at time of writing:** `31164958ade23554ae69b77eac8d2fc591f871b7`
  (`3116495` — "docs: regression audit 2026-08-29, six findings
  (REG-001..006)"), i.e. the parent of the commit that introduced this file.
