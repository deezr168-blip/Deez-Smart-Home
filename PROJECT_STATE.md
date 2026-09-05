# PROJECT_STATE.md

Authoritative coordination state for all autonomous Home Assistant dashboard
routines. **Read this file before starting autonomous work.** It is kept short
on purpose so every routine can load it cheaply at the start of each run.

---

## Project

- **Repository:** `deezr168-blip/Deez-Smart-Home`
- **Deployment branch:** `ha-deploy`
- **Canonical CasaRay target:** `dashboards/casaray_v2.yaml` — all new work
- **Legacy / reference dashboard:** `dashboards/deez_smart_home.yaml` — do not
  build new CasaRay features here
- **Deployment model:** validated GitHub changes are polled/deployed by Home
  Assistant independently. No routine deploys, restarts or reloads anything —
  pushing a validated commit to `ha-deploy` is the whole handoff. **That path
  is broken (`CFG-003`); pushed is not deployed.**

---

## Architecture decision: casaray_v2 is CasaRay (owner directive, 2026-09-05)

**The owner has chosen.** `dashboards/casaray_v2.yaml` is the **canonical
CasaRay development target**. The question of which dashboard is CasaRay is
settled and should not be reopened by any routine.

### What targets v2

Every future CasaRay batch, board, UX improvement, bilingual improvement,
entity integration, automation-linked UI, and every Bills, Entertainment,
Camera, People Mapping, Energy or House Health feature — **unless the owner
explicitly directs otherwise**.

### What `dashboards/deez_smart_home.yaml` is now

Legacy, and the reference baseline. It keeps four jobs:

- a reference for **confirmed working entity IDs**,
- a source of **proven templates and logic** worth reusing,
- the **rollback / reference baseline**,
- the running system until v2 is deployed and verified.

**Do not delete, overwrite, merge into, or materially restructure it.** Do not
rebuild v2 features in it — in particular, Batches 2 and 5 are **not** to be
built there; v2 already carries their content. Touch it only for a genuine
regression in it, or on an explicit owner instruction.

### Work already completed in v2 — preserve it

- `885b03a` — the mandated `DD/MM/YY` clock format across all 19 clocks, and
  the conversion from Traditional to Simplified Chinese.
- `3faa830` — the bilingual meaning layer: 21 room, board and status templates.
- `PENDING-SHA` — the 70 bilingual section headings.

These are settled. Do not revert or re-litigate them.

### Facts a routine needs before editing v2

- Native-first: 1 custom card type (`custom:webrtc-camera`) against the legacy
  file's 6, no `card_mod`, no Mushroom, surface treatment from the theme.
- It uses **all 164** of the legacy dashboard's real entity IDs, invents none,
  drops none.
- It assumes url_path **`casaray`**. All 85 navigation links are
  `/casaray/<view>`; mounted anywhere else they break.
- Bilingual conventions are **mandatory** and listed in `CLAUDE.md` and
  `docs/CASARAY_V2_ARCHITECTURE.md`.
- `CFG-003` applies to v2 exactly as it does to the legacy file. Neither can
  be seen live until the bridge is recovered. **Committed is not deployed.**
- `scripts/dashboard_check.py` no longer hardcodes a url_path when resolving
  navigation links, so the gate covers both dashboards.

---

## Schedule Status: ACTIVE — pause lifted (owner directive, 2026-09-01)

**The owner lifted the 2026-08-30 pause on 2026-09-01**, in a live session, by
freezing CasaRay Design v1 and directing the implementation to resume from the
approved mockups and the *CasaRay Master Design Briefing v1*. Autonomous
implementation is permitted again, under the standing rules below.

What the lift does and does not change:

- Implementation, backlog work and pushes to `ha-deploy` are **permitted**
  again. The 2026-08-30 stop is over. Per its own instruction it is replaced
  with this dated note rather than silently deleted; its text is preserved in
  Git history at `b6e76f5`.
- **`CFG-003` is untouched by this and still stands.** The deployment bridge
  does not deliver: the host's clone is orphaned from `ha-deploy`, so nothing
  pushed since `26c3b14` has reached the live dashboard. Work may proceed, but
  every batch lands unverified until the owner runs the recovery procedure in
  `DASHBOARD_ISSUES.md`. Each batch's record must say so rather than imply a
  change went live.
- **`UI-032 PROBE v1` stays on the production Home page** while `CFG-003` is
  open. It is the test instrument for the bridge, not a leftover. Do not
  remove it as cleanup.
- Every other rule in this file — ownership, protected areas, the validation
  gate, the concurrency policy, the entity-verification rule — is unchanged.

### CasaRay Design v1 — frozen

The approved mockups and the *CasaRay Master Design Briefing v1* are the
authoritative visual and UX specification. Both live in the owner's Google
Drive folder `CasaRay Mockups`; `DESIGN_REFERENCE.md` transcribes the renders,
and `docs/CASARAY_MAPPING_PACK.md` maps every mockup component to a real
entity, a proposed card and a buildability status. Do not redesign against
them; where Home Assistant genuinely cannot reproduce a component, record the
adaptation in the mapping pack rather than inventing a new design.

`docs/entity_inventory.md` is the entity truth this work runs on, reconciled
against the live instance on 2026-09-01.

---

## Routine Ownership

### Main CasaRay Upgrade
- Owns general dashboard UX and implementation.
- May modify `dashboards/casaray_v2.yaml` — the canonical target — except
  specialist-owned billing areas.
- **May not** build new CasaRay features in `dashboards/deez_smart_home.yaml`.
  That file is legacy and reference-only per the architecture decision above.

### Billing Dashboard Upgrade
- Owns billing-specific dashboard UX, bill history, analytics,
  bill-ingestion architecture, and billing-supporting repository files.
- Billing work targets **`dashboards/casaray_v2.yaml`**'s `bills` view, not the
  legacy dashboard's `bills` view or its six `bill-*` subviews.
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

### Daily Project Coordinator
- Coordination and tracking maintenance only.
- May modify `PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md`,
  `DASHBOARD_ISSUES.md`, `LIVE_VERIFICATION_QUEUE.md`,
  `DASHBOARD_PROGRESS.md`, and documentation under `archive/`.
- May perform evidence-based reconciliation of coordination and tracking
  state.
- **Must not modify** `dashboards/casaray_v2.yaml`,
  `dashboards/deez_smart_home.yaml`, themes, Home
  Assistant configuration, automations, helpers, integrations, billing
  implementation, scripts, deployment infrastructure, Git/authentication
  infrastructure or secrets.
- Must not take ownership of implementation work belonging to Main CasaRay
  Upgrade or Billing Dashboard Upgrade, take another routine's Active Work
  Lease, or silently transfer another routine's ownership.
- May record a lease past the 4-hour staleness threshold as stale **only**
  when repository evidence clearly establishes it. Ambiguous leases are
  flagged, never cleared.

---

## Protected Areas

All autonomous routines — the three writers and advisory routines, and the
Daily Project Coordinator — must treat these as protected unless explicitly
authorized:

- Home Assistant authentication and secrets
- Deployment scripts and deployment automation
- Git authentication and infrastructure
- Core Home Assistant configuration
- Live entity/device deletion
- Destructive helper or integration changes
- External account actions, bill payment, or email sending

---

## Context Loading Strategy

Recurring routines should orient themselves cheaply. Load in this order and
stop when you have what the task needs.

1. **Always** read `PROJECT_STATE.md` (this file) in full. It is the
   authoritative current coordination state.
2. Read only the **active** sections of `DASHBOARD_BACKLOG.md`.
3. Read only the **Open** and audit sections of `DASHBOARD_ISSUES.md`. Read
   the resolved tables only when a specific ID is in play.
4. Inspect `DASHBOARD_PROGRESS.md` **selectively** — the most recent entries
   and any entry referenced by this file, the backlog or the issues record.
   Never load its full history routinely.
5. Inspect Git history **scoped to the area being worked on**
   (`git log -- <path>`, `git log -S <pattern>`), not the whole branch.
6. Load a specialist progress or reference file only when the routine owns or
   audits that area.
7. Do not load `archive/` at all unless investigating a regression recurrence
   or revisiting a past design decision.
8. Read `LIVE_VERIFICATION_QUEUE.md` only when: deciding whether a
   verification-blocked item has changed state, working on an affected view,
   or reconciling a user-supplied result. Not every run — and when you do,
   read the `PENDING`, `FAIL` and `PARTIAL` rows. Historical `PASS` rows
   matter only when investigating a recurrence or regression.

Cheapness never licenses stale state: the Concurrency / Serialization Policy
still requires a fetch and a re-read of this file before any write, and the
Next Actionable Work pointer must still be revalidated against current `HEAD`.

### Authority

| File | Role |
|---|---|
| `PROJECT_STATE.md` | Authoritative **current coordination state** |
| `DASHBOARD_BACKLOG.md` | Authoritative **detailed active work queue** |
| `DASHBOARD_ISSUES.md` | Authoritative **active regression / issue record** |
| `DASHBOARD_PROGRESS.md` | **Historical** implementation record — not coordination state, carries no priority list |
| `LIVE_VERIFICATION_QUEUE.md` | Authoritative **human verification checklist** — the only place live-check instructions live |
| `archive/*` | Closed detail, retained for investigation only |

---

## Routine Startup Profiles

What each routine loads at startup. Applies the Context Loading Strategy per
routine; it changes **what is read**, never what a routine is allowed to do.
Ownership, authority and every policy below are unaffected.

**Every routine, always:** read `PROJECT_STATE.md` in full · `git fetch origin
ha-deploy` · confirm the branch is current and the worktree clean.

| Routine | Always load | Selective load | Normally skip |
|---|---|---|---|
| **Main CasaRay Upgrade** | `PROJECT_STATE.md`; fetch + branch state | Its own active backlog items; open issues for the target view; `LIVE_VERIFICATION_QUEUE.md` rows (`PENDING`/`FAIL`/`PARTIAL`) for that view; `git log -- <view/theme path>`; recent `DASHBOARD_PROGRESS.md` entries for the same area | Full `DASHBOARD_PROGRESS.md`; resolved issue tables; awaiting/completed backlog; `archive/`; billing-specialist detail |
| **Billing Dashboard Upgrade** | `PROJECT_STATE.md`; fetch + branch state | `BILL-*` backlog items; billing issues; verification rows for `bills`/`bill-*`; `git log -- dashboards/…` scoped to bill views; billing-supporting files | Full `DASHBOARD_PROGRESS.md`; non-billing issues and backlog; `archive/`; general CasaRay UX detail |
| **Regression Auditor** | `PROJECT_STATE.md`; fetch + branch state | Open issues + the active audit section; `git log` for the commit range under audit; the diffs it is auditing; verification `FAIL`/`PARTIAL` rows | Full `DASHBOARD_PROGRESS.md`; resolved issue narrative; `archive/` unless testing a recurrence; backlog items outside the audited range |
| **Entity & Feature Scout** | `PROJECT_STATE.md`; fetch + branch state | The dashboard's current entity references; open issues touching entities; its own backlog items | `DASHBOARD_PROGRESS.md`; issue history; `archive/`; other routines' backlog items; verification queue |
| **CasaRay Design Reviewer** | `PROJECT_STATE.md`; fetch + branch state | The views under review; `themes/deez_your_name.yaml`; design-related backlog (`DR-*`, `UI-027`); verification rows for visual items | Full `DASHBOARD_PROGRESS.md`; implementation narrative; `archive/` unless retrieving prior design rationale; billing internals |
| **Daily Project Coordinator** | `PROJECT_STATE.md`; fetch + branch state | Active backlog; open issues; `PENDING`/`FAIL`/`PARTIAL` verification entries; recent relevant `DASHBOARD_PROGRESS.md` entries; relevant recent `git log` | Complete historical progress; resolved issue narrative; completed backlog history; `archive/` unless investigating reconciliation or history |

Read `archive/` only when investigating a regression recurrence or retrieving
prior design rationale. Read another specialist's area only when auditing it.

### Normalized startup blocks

Drop-in replacements for the routines' existing read lists. Documented here
only — the Claude Routine configuration is not edited by this policy.

**Main CasaRay Upgrade**
```
Read PROJECT_STATE.md in full. Fetch origin/ha-deploy; confirm branch current
and tree clean. Then load only: your active DASHBOARD_BACKLOG.md items, open
DASHBOARD_ISSUES.md entries for the target view, any PENDING/FAIL/PARTIAL rows
in LIVE_VERIFICATION_QUEUE.md for that view, and git log scoped to the files
you will touch. Do not read DASHBOARD_PROGRESS.md or archive/ end to end.
Before touching production implementation, run Pre-Implementation
Revalidation and take the Active Work Lease.
```

**Billing Dashboard Upgrade**
```
Read PROJECT_STATE.md in full. Fetch origin/ha-deploy; confirm branch current
and tree clean. Then load only: BILL-* backlog items, billing-related issues,
verification rows for bills/bill-*, and git log scoped to the bill views and
billing-supporting files. Do not read DASHBOARD_PROGRESS.md or archive/ end to
end, and do not load general CasaRay UX detail. Before touching production
implementation, run Pre-Implementation Revalidation and take the Active Work
Lease.
```

**Regression Auditor**
```
Read PROJECT_STATE.md in full. Fetch origin/ha-deploy; confirm branch current.
Then load only: the Open section of DASHBOARD_ISSUES.md, git log for the
commit range under audit, the diffs in that range, and any FAIL/PARTIAL
verification rows. Skip resolved issue narrative and DASHBOARD_PROGRESS.md
unless testing a recurrence, in which case read the specific archived entry.
Advisory only: record findings as issues/backlog items; never modify
production dashboard YAML.
```

**Entity & Feature Scout**
```
Read PROJECT_STATE.md in full. Fetch origin/ha-deploy; confirm branch current.
Then load only: current entity references in the dashboard, open issues
touching entities, and your own backlog items. Skip DASHBOARD_PROGRESS.md,
archive/, the verification queue and other routines' items. The entity
registry is unavailable here — record findings as claims, not facts. Advisory
only: never modify production dashboard YAML.
```

**CasaRay Design Reviewer**
```
Read PROJECT_STATE.md in full. Fetch origin/ha-deploy; confirm branch current.
Then load only: the views under review, themes/deez_your_name.yaml,
design-related backlog items (DR-*, UI-027) and verification rows for visual
items. Read archive/ only to retrieve prior design rationale. Advisory only:
queue design findings; never modify production dashboard YAML.
```

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

### Impact / Effort / Risk scoring

A lightweight tie-breaker between several actionable items at the same
priority owned by the same routine. Not a substitute for engineering
judgment.

**Authoritative ordering: ownership → P0/P1/P2/P3 priority → actionability →
Selection Score.**

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **Impact** | negligible / cosmetic | minor | meaningful, localized | substantial, important view or workflow | whole-dashboard, safety/privacy, core workflow, frequent UX |
| **Effort** | very small, local | small, contained | moderate, multi-card/file | substantial | major architecture / broad redesign |
| **Risk** | isolated, easily reversible | low | moderate regression potential | high interaction / regression potential | protected, core, high-risk |

**Selection Score = (Impact × 2) − Effort − Risk.**

Safeguards:

1. Priority always outranks Selection Score. A high-scoring P2/P3 item never
   jumps ahead of an actionable P0/P1 item owned by the same routine.
2. Ownership always outranks Selection Score.
3. `BLOCKED` and purely `LIVE_VERIFICATION_REQUIRED` items are excluded from
   autonomous implementation selection, and need not be scored.
4. Recent Change Protection and Active Change Windows still apply.
5. A low or negative score never means delete the item — it only affects
   ordering within its priority.
6. P0 work is handled on urgency and correctness, not score optimization.
7. Security, privacy and data-loss problems must not be down-ranked because
   remediation is difficult. Effort and Risk describe the work; they never
   reduce Impact.
8. Do not inflate Impact or deflate Effort/Risk to justify preferred work.
9. Re-score when repository evidence changes the expected scope.
10. On an equal score at the same priority, prefer: an existing regression
    over a speculative enhancement · then the smaller blast radius · then work
    that unblocks other queued work · then the older actionable item.

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

Digest of the detailed policies below — not a separate authority.

- Read this file before autonomous work.
- Respect routine ownership boundaries.
- Inspect recent commits, `DASHBOARD_ISSUES.md` and `DASHBOARD_BACKLOG.md`
  before modifying an area.
- Do not duplicate work already underway.
- Specialist ownership overrides general ownership.
- Advisory routines queue work rather than implementing production dashboard
  changes.
- Do not claim live verification solely from repository validation.
- Serialize write sequences per the Concurrency / Serialization Policy:
  fetch before writing, fetch again before committing, never force-push.
- Writers revalidate the item against current `HEAD` immediately before
  touching production implementation, and take the lease only after that.

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

Areas under substantial active work. Not a log of every edit. Writers update
their own row; advisory routines read but never take over a writer's entry.
All times UTC. Drop a row once its window has expired **and** the work is
recorded in `DASHBOARD_BACKLOG.md` or `DASHBOARD_ISSUES.md`.

| Area | Owner | Last Significant Commit | State | Protected Until | Notes |
|---|---|---|---|---|---|
| Billing privacy (`bill-electricity`, `bill-gas` account-number literals) | Billing | `23c0301` — 2026-08-30 | `LIVE_VERIFICATION_REQUIRED` | 2026-08-30 +6h from push | Closes the account-number half of `BILL-001`. NMI/MIRN portion intentionally untouched — `BLOCKED`, needs owner decision, see `DASHBOARD_BACKLOG.md`. |
| False-safe door-count aggregates (`home` hero + quick chip + Security card, `cameras` chip row, `ipad-command-center` chip row) | Main | `b058006` + follow-up — 08-30 01:50 | `LIVE_VERIFICATION_REQUIRED` | 08-30 07:50 | Closes REG-007..011. Continuation of the REG-001..006 false-safe-state sequence under RCP rule 5/7 — the same three-sensor door list was copy-pasted unguarded into 5 cards across 3 views; all 5 now guarded. REG-008 was corrected from an initial mislog against `ipad-command-center` to its actual location on `cameras` — see `DASHBOARD_ISSUES.md`. |
| LetPot Grow Light raw-interpolation guard (`ray-bedroom`, ~L859) | Main | `691689a` — 2026-08-30 | `LIVE_VERIFICATION_REQUIRED` | 2026-08-30 +6h from push | Closes `UI-030`. Found while widening the REG-007..011 aggregate sweep to `climate`/`network`/`status`/room views — that sweep itself was clean, no new false-safe instance found anywhere. |
| Raw-interpolation fixes (`home` Person chip, `home` Climate card, `light-ray-bedroom` Roller Shade) + one false-safe fix (`lighting-modes` Current State) | Main | `ccfb0c8` — 2026-08-30 | `LIVE_VERIFICATION_REQUIRED` | 2026-08-30 +6h from push | Closes `UI-031` and `REG-013`. Camera-subview sweep the previous note recommended was clean (six subviews are just back chip + webrtc card); widened to a whole-file raw-interpolation grep instead. See `DASHBOARD_PROGRESS.md` for full detail. |
| Regression audit record (`DASHBOARD_ISSUES.md`) | Regression Auditor | `f52a27b` — 2026-08-30 | `PUSHED` | 2026-08-30 +6h from push | Audited `3116495..ea7289f` (45 commits); filed `REG-012` (verification-queue upkeep gap, now closed by the Daily Project Coordinator — see `DASHBOARD_ISSUES.md`). REG-001..011/UI-027/UI-030/BILL-001 confirmed correctly tracked, no premature `VERIFIED` claims, no cross-routine conflicts. Do not re-audit that range; next scope is `ea7289f..HEAD`. |
| Coordination state (`PROJECT_STATE.md`, `CLAUDE.md` startup block) | Shared | `0351007` — 08-30 00:25 | `PUSHED` | 08-30 06:25 | Structure settled. Append to your own sections; do not restructure. |

Back / previous-page navigation is **complete** (35/36 views, parent-targeted;
`home` is root) and its window long expired — recorded under UI-009/UI-017 in
`DASHBOARD_BACKLOG.md`. Do not redesign it; it needs a live look only.

---

## Concurrency / Serialization Policy

Routines may run concurrently at the scheduler level. What must be
serialized is the **write sequence** — only one routine at a time may be
midway through writing shared project state or production implementation.

### Reading

1. Any routine may inspect or read the repository at any time. Reads are never
   serialized.

### Before any write

2. Before making any repository write, a routine must:
   - `git fetch origin ha-deploy`
   - confirm its local branch is current
   - inspect the commits added since the routine began
   - re-read `PROJECT_STATE.md`
   - re-check ownership, priority, Active Change Windows, Active Work Leases
     and the current Next Actionable Work
3. If `origin/ha-deploy` moved after the routine selected its task, it must
   re-evaluate the task before writing. Never continue from stale assumptions.
4. Fetch again immediately before committing.

### If remote moved during implementation

5. Never force-push and never rewrite published history. Inspect the new
   commits and determine whether they overlap the same area, files or
   objective.
6. **Unrelated and safely reconcilable** — fast-forward or rebase the
   uncommitted work onto current `ha-deploy`, re-run validation, continue.
7. **Overlapping** the same feature, tracking section, ownership area or
   production implementation:
   - stop the conflicting write
   - do not automatically merge competing implementations
   - preserve the local work if it is worth reviewing
   - record the conflict in the routine's own `Current Work / Blockers`
     subsection
   - re-evaluate from current branch state on the next run

### Leases

8. Two production writer routines must never implement the same backlog or
   issue ID concurrently.
9. On beginning substantive implementation, a writer records the item in the
   Active Work Leases table below as `IN_PROGRESS — <routine name>`, with the
   item ID, owning routine, start commit and start timestamp. The lease is
   taken **after** Pre-Implementation Revalidation succeeds, never before —
   see that section. **A lease is a coordination courtesy, not a permanent
   lock.**
10. A routine encountering an `IN_PROGRESS` item owned by another routine must
    not implement it.
11. The owning routine clears or changes its lease as soon as the work becomes
    `PUSHED`, `LIVE_VERIFICATION_REQUIRED`, `BLOCKED`, or is abandoned or
    replanned.
12. A lease older than **4 hours** with no supporting commits or progress
    update is potentially stale. Advisory routines may flag it as stale; they
    must not silently take ownership of it.
13. Specialist ownership still overrides general ownership.

### Write hygiene

14. Documentation-only advisory routines should minimize writes to shared
    files — update their own designated sections and avoid rewriting unrelated
    formatting or content.
15. `DASHBOARD_PROGRESS.md` is historical progress, not a second coordination
    authority.
16. `PROJECT_STATE.md` is the authoritative current coordination state.
17. `DASHBOARD_BACKLOG.md` is the authoritative detailed work queue.
18. **Avoid stamp races.** Only the routine that creates a content commit
    creates its `docs: stamp` commit. Do not stamp another routine's batch
    just because you encountered a `PENDING` placeholder — record the
    unstamped entry for cleanup instead. The single exception is the **Daily
    Project Coordinator**, which may repair a genuinely historical
    missing or stale stamp as explicit coordination maintenance, only when no
    originating routine is concurrently attempting the same stamp. It must
    not race another routine to stamp recent work.

### Active Work Leases

Genuinely active implementation only. Planned work and verification-only work
do **not** belong here.

| Item | Owning Routine | Start Commit | Started | State | Notes |
|---|---|---|---|---|---|
| _(none)_ | — | — | — | — | No routine holds an implementation lease. Main's queue is exhausted and pushed; `BILL-001` is actionable but unstarted, so it is not a lease. |

---

## Pre-Implementation Revalidation

Applies to the two writer routines — **Main CasaRay Upgrade** and **Billing
Dashboard Upgrade** — immediately before modifying production implementation.

This is the stricter form of the "Before any write" gate in the Concurrency /
Serialization Policy, not a second procedure. Every repository write clears
that gate; a write that touches production implementation clears this one too.

### The check

1. `git fetch origin ha-deploy`.
2. Confirm local `HEAD` matches current remote `HEAD`, or fast-forward safely
   first.
3. Re-read: this file · the active item in `DASHBOARD_BACKLOG.md` · the
   matching active issue if one exists · the relevant
   `LIVE_VERIFICATION_QUEUE.md` result if applicable.
4. Confirm **all** of:
   - the item is still actionable
   - the item is still owned by this routine
   - no other routine holds an Active Work Lease on it
   - no newer commit already fixed or materially changed the issue
   - no human verification result has changed its state
   - no higher-priority actionable item has appeared for this routine
5. Recompute Impact/Effort/Risk **only** if repository evidence has materially
   changed the item's scope. Otherwise carry the existing scores.
6. If any of the above changed: abandon the stale selection and re-select from
   current state **before** touching production code.

### Rules

- A routine must not continue implementing merely because it spent time
  planning an item. Sunk planning cost is not a reason.
- Planning effort creates no ownership. Ownership comes from the ownership map
  and the Active Work Lease, nothing else.
- A stale Next Actionable Work pointer never overrides current repository
  evidence.
- A newly recorded `PASS` cancels pending implementation for that same
  verified defect, unless a distinct issue exists.
- A newly recorded `FAIL`, or a P0/P1 regression, may supersede lower-priority
  planned work.
- A specialist-owned item becoming actionable does **not** authorize Main
  CasaRay to take it. Ownership still outranks priority.
- If another commit touched the same view or component but not the exact item,
  inspect that diff before deciding whether the work can safely continue.

This is distinct from Recent Change Protection rule 5. That rule lets an owner
continue a **committed, coherent multi-batch sequence** through its own recent
changes; it never licenses continuing a selection that this check has just
shown to be stale.

### Writer execution sequence

```
Fetch → Re-read state → Revalidate item → Take lease → Implement →
Validate → Fetch again → Reconcile remote changes → Commit → Stamp →
Release/update lease
```

The lease is taken only once revalidation succeeds, and released or updated as
soon as the work reaches `PUSHED`, `LIVE_VERIFICATION_REQUIRED`, `BLOCKED`, or
is abandoned (Concurrency rules 9 and 11).

---

## Live Verification

`LIVE_VERIFICATION_QUEUE.md` is the **authoritative human verification
checklist**. Nothing in this environment can reach the instance, so only a
person looking at the live dashboard can close a verification item.

- Writer and advisory routines must **not** duplicate detailed
  live-verification instructions anywhere else — link to the queue instead.
- Existing `LIVE_VERIFICATION_REQUIRED` states remain valid until a human
  records a result. Creating, reading or reorganising the queue is **not**
  verification.
- **`PASS`** — the routine reconciling it may move the item to
  `LIVE_VERIFIED` in `DASHBOARD_ISSUES.md`.
- **`FAIL`** — reopen an actionable regression, reusing the existing stable ID
  where one exists rather than minting a new one.
- **`PARTIAL`** — preserve the portion that passed and raise a narrowly scoped
  follow-up. Never trigger a wholesale reimplementation from a partial result.
- Verification items are not backlog work. An item awaiting a live check stays
  excluded from autonomous selection (queue rule 4) and does not become
  actionable implementation work just because it is unverified.

### Result syntax

One result per line. Case-insensitive. Batches are accepted — process them
atomically where practical and report any ID that could not be matched.

```
<ID> <RESULT>
<ID> <RESULT> — <short note>
```

- `<ID>` — an existing stable ID (`UI-011`, `REG-005`). Never invent one.
- `<RESULT>` — `PASS` · `FAIL` · `PARTIAL` · `PENDING` (to un-record).
- `<note>` — optional, after `—`, `-` or `:`. Preserve the user's wording
  where it carries the symptom; keep the tracking record concise.

```
UI-027 PASS — readable on iPad landscape
UI-020 FAIL — Total Solar shows a bare number with no unit
REG-005 PARTIAL — English wording works, Chinese is inconsistent
```

### Reconciliation procedure

Before editing: fetch `origin/ha-deploy` and re-read this file, per the
Concurrency / Serialization Policy. Then locate the ID in
`LIVE_VERIFICATION_QUEUE.md`, `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`
(if present) and this file (if referenced), and reconcile consistently across
all of them.

| | `PASS` | `FAIL` | `PARTIAL` |
|---|---|---|---|
| **Queue** | Result → `PASS` | Result → `FAIL` | Result → `PARTIAL` |
| **Issue record** | `LIVE_VERIFICATION_REQUIRED` → `LIVE_VERIFIED` | Reopen the **same stable ID**; state → actionable | Keep the confirmed portion; reopen only the failing part |
| **Priority** | — | Preserve, unless evidence clearly justifies reclassification | Preserve |
| **Owner** | — | Assign the correct owning routine | Assign the correct owning routine |
| **Backlog** | Do not recreate implementation work | Add as actionable, scored per the normal rules | Add only the narrow follow-up |
| **Evidence** | Note optional | Record the observed live symptom | Record which half failed |

- **`PASS`** — remove it from active verification blockers and preserve its
  historical record. Never delete the trail.
- **`FAIL`** — reuse the existing ID rather than minting a duplicate. Update
  Next Actionable Work only if the reopened item now outranks the owning
  routine's current selection, respecting ownership, scoring and concurrency
  rules. **Do not implement the fix during a reconciliation task** unless the
  user asks, or the routine's normal writer workflow later selects it.
- **`PARTIAL`** — reuse the stable ID when the failure is the same underlying
  issue; mint a new linked ID only when the failing portion is genuinely a
  distinct defect. Never let a partial result trigger a wholesale redesign.

### What may never produce LIVE_VERIFIED

A human result is the only source. Never infer `PASS` from a passing
`ha_validate.sh` run, a successful deploy, a screenshot nobody actually
reviewed, or the plausibility of the diff.

### Queue upkeep

Keep `PASS` rows for traceability. Once a page group has no `PENDING`,
`FAIL` or `PARTIAL` rows left, it may collapse into a one-line completed
summary naming the IDs and the date. Do not delete useful history merely to
shorten the file.

---

## Next Actionable Work

Coordination pointer to each writer's current highest actionable item — not a
duplicate backlog. Full items live in `DASHBOARD_BACKLOG.md`. Advisory
routines may update a pointer when evidence changes priority or status;
ownership stays with the writer. Writers refresh their own pointer after
completing work. Within a priority, ties are broken by Selection Score; the
score never changes which priority is selected.

**This pointer is advisory.** It records the correct selection as of the
timestamp below, and this branch moves fast. A routine must revalidate it
against current `HEAD` at execution time, per the Concurrency /
Serialization Policy, before acting on it — the item named here may already
be implemented.

### Main queue — the ordered ladder (owner directive, 2026-09-05)

Implementation is deliberately **stopped at the top of this ladder**. New
CasaRay feature development does not resume until steps 1–5 are done, in order.
Steps 1 and 2 are owner actions; no routine can perform them.

| # | | Step | Owner or Claude | State |
|---|---|---|---|---|
| 1 | 🔴 | **Resolve `CFG-003`** — repair the delivery path. Nothing committed reaches Home Assistant until this is done. Procedure: `DASHBOARD_ISSUES.md` → *Owner recovery, on the host*. | **Owner** | BLOCKED |
| 2 | 🔴 | **Obtain B1** — one Home Assistant Developer Tools → States export. Procedure: `docs/B1_STATES_EXPORT.md`. | **Owner** | BLOCKED |
| 3 | 🟡 | **Reconcile v2 against the B1 entity inventory** — regenerate `docs/entity_inventory.md` from the export, then check every v2 entity ID, and add the scene / automation / air-quality / solar-forecast surfaces the export unblocks. | Claude | waits on 2 |
| 4 | 🟡 | **Deploy v2** through the repaired delivery path, registered at url_path **`casaray`**. | Owner + Claude | waits on 1, 3 |
| 5 | 🟡 | **Live visual verification** on iPad landscape and iPhone. Checklist: `docs/CASARAY_V2_ARCHITECTURE.md` → *What must be verified in the live interface*. | **Owner** | waits on 4 |
| 6 | 🟢 | **Resume new CasaRay feature development** — and only then. | Claude | waits on 5 |

**Do not start another major feature batch ahead of this ladder.** Documentation,
non-destructive validation and small corrections to already-shipped v2 work
remain in scope; new boards and new features do not.

| Routine | Item | Priority | State | Reason Selected |
|---|---|---|---|---|
| Main CasaRay Upgrade | **Ladder step 1 — `CFG-003`**, then step 2 — B1. See the ordered ladder above. | P1 | `BLOCKED` — both are owner actions | **Rewritten 2026-09-05, second revision.** The architecture question is **settled**: `casaray_v2.yaml` is CasaRay, the legacy dashboard is reference-only. Main's implementation queue is deliberately empty, not exhausted — the owner has stopped new feature work at the top of the ladder above until delivery and the entity export are sorted. Everything Main can usefully do without them is done: `885b03a` (clock format, Simplified Chinese), `3faa830` (bilingual meaning layer), `PENDING-SHA` (70 bilingual section headings). What remains needs step 2's export — scenes on every room page, the whole Lighting board's scene rows, the Automations board, air quality, solar forecast — or step 1's delivery path, since nothing can be visually verified until v2 renders. *Superseded pointer text follows.* The owner approved proceeding with Batches 2 and 5 on 2026-09-01. Between the question and the answer, `5dc6f50` landed `dashboards/casaray_v2.yaml` — a from-scratch parallel CasaRay build that **already contains both**: an `alerts` board (Batch 6), a `house-health` board with the battery roll-up (Batch 5), and a Home whose 31 alerts are already grouped and conditional (Batch 2). Doing Batches 2 and 5 against the old file would have been the wasted work this file's own v2 section warns about, so they were **not** done. The same value went into v2 instead: `885b03a` fixed the mandated `DD/MM/YY` date format across all 19 clocks and converted the file from Traditional to Simplified Chinese to match production's 304 strings; `3faa830` completed v2's bilingual meaning layer, which its own architecture document claimed but had not implemented — 21 templates, verified by rendering all 52 through real Jinja2 in both languages with zero errors. **Nothing further should be built on either dashboard until the owner says which one is CasaRay.** Two live tracks is the current cost, and it compounds with every batch. Remaining v2 work that needs no decision: the 70 English `heading` cards (a change to v2's stated bilingual rule, so owner's call). Blockers unchanged: `CFG-003` (nothing reaches the instance), **B1** (entity IDs unreadable — one States export unblocks scenes, automations, air quality, solar forecast), `CFG-001`. *Superseded pointer text follows.* **This pointer was rewritten on 2026-09-01 when the pause lifted and CasaRay Design v1 was frozen.** Main's queue is no longer "exhausted": the mapping pack turned the frozen design into a batch plan, and six batches are buildable with nothing from the owner. Batch 1 (the P1 clock/date shell component) landed this run. **Batch 2 is Home only**: group the 17 loose `conditional` alert cards under an Attention heading, add the P4 KPI strip, and give the Security roll-up an honest shape — doors, motion and camera health only, with **no alarm row**, because no `alarm_control_panel` entity exists. Batch 5 (House Health: three genuinely-low batteries, the offline inverter, backup status) is the highest-value new content and also needs no owner input. Everything involving scenes, automations, air quality, solar forecast or Water & Gas is blocked on **B1**, one Developer Tools → States export. `DR-001` is **not** superseded but is now correctly behind the batch plan: it is a P3 needing a design brief, and the frozen mockups plus the mapping pack are a better brief than anything that existed when it was filed. `CFG-001` and `CFG-003` are unchanged by any of this. |
| ~~Main CasaRay Upgrade (superseded 2026-09-01)~~ | `DR-001` — iPad Command Center density | P3 | `PLANNED` — needs a design decision before implementation | Still the only scoped item in Main's queue after five consecutive clean sweeps this session (raw-interpolation, false-safe aggregate, float-sentinel, icon_color/attribute/int/cover/structural, state_attr/comparison/bare-float/navigation) — score **−2** (Impact 3, Effort 4, Risk 4), selected by being the sole remainder, not by rank. Explicitly "advisory item, no implementation agreed": needs a CasaRay Design Reviewer brief before Main writes code. Everything else Main owns (the REG-001..013/UI-027/UI-030/UI-031 batches) is `LIVE_VERIFICATION_REQUIRED` and waiting on the owner. **The verification drought has broken:** the owner recorded the queue's first-ever live result on 2026-08-30 — `UI-011` `PASS` — taking it to `LIVE_VERIFIED` and the queue from 44 pending to 43. That verification also surfaced `CFG-001` (Energy → Totals grid cost ~31.8× too high), which is **not Main's work and not implementable from here**: it lives in HA's own Energy configuration, is blocked on owner diagnosis, and never enters the verification queue. Main's selection is unchanged by both. |
| Billing Dashboard Upgrade | `BILL-002` — Home Assistant exposure decision for `billing/history.json` (storage now exists, see `billing/README.md`) | P2 | `PARTIAL` — storage scaffolded (`5147eb0`/`ff25626`), read side needs owner direction | `BILL-001`'s account-number portion is fixed and pushed (`23c0301`); its NMI/MIRN portion is `BLOCKED` on an owner decision (no helper exists, cannot invent one) and is excluded from selection (queue rule 4). `BILL-002`'s storage layer (`billing/schema.json`, empty `billing/history.json`) exists; its read side is still blocked on which HA-side mechanism exposes the file to Lovelace (`billing/README.md` point 2). `BILL-003` stays blocked on both. Two runs (`BILL-004`, then `BILL-005` + `REG-014`) found and fixed unblocked work instead of re-deriving the same blocker notes; this run's own full re-read of all seven billing views plus a fresh 5+-digit-literal privacy sweep found nothing further — the coded-fix surface is now genuinely clean, not merely unattempted. `BILL-002`'s exposure question remains the next thing that unblocks real dashboard-history work once decided. |

---

## Current Work / Blockers

### Main (CasaRay Upgrade)

**2026-09-01 — CasaRay Design v1 frozen, pause lifted, Batch 1 landed. This
entry supersedes the "implementable queue exhausted" status below it.**

- **Queue:** the six-batch plan in `docs/CASARAY_MAPPING_PACK.md` Part 4.
  Batches 1–6 need nothing from the owner. **Batch 1 is done** (P1 clock/date,
  Home header). **Batch 2 (Home only) is next and is `READY`.**
- **Why the queue is no longer exhausted.** It was exhausted against the *old*
  backlog, not against the design. Freezing the mockups and mapping every
  component to a real entity produced a concrete, entity-verified work queue
  where there had been a single blocked P3.
- **Entity truth is now written down.** `docs/entity_inventory.md` reconciles
  all 166 referenced IDs against the live instance. Read it before writing a
  card; it is what stops the next invented entity ID.
- **Live findings Main must design around:** the Fronius inverter is
  **offline** (every `primo_5_0_1_1_*` sensor `unavailable`); three batteries
  are genuinely under 30 % (Front Door 22, RingRing 21, Tapo C425 25 — this is
  `UI-032`'s answer); Tapo East/South Wall cameras and all four Living Room
  Hue spots are `unavailable`; there is **no Bathroom area, no alarm panel, no
  lock, no garage door, no water or gas meter, no battery, and no
  grid import/export sensor**. Do not build a card over any of them.
- **Blockers:** `CFG-003` (nothing pushed reaches the live dashboard) and
  **B1** (entity IDs are not readable from this environment — one Developer
  Tools → States export unblocks the scene rows on every room page, the whole
  Lighting Studio and the entire Automations board). Neither blocks Batches
  2–6.
- **Verification:** Batch 1 is `PUSHED`, not `LIVE_VERIFIED`. Queued as
  `CR-001`/`CR-002` in `LIVE_VERIFICATION_QUEUE.md`.

*Superseded status, retained for history:*

- **Queue:** `DR-001` (P3, score −2) only, and it needs a design brief before
  code. No actionable P1 or P2 remains. `UI-011` is **no longer queued at
  all** — the owner returned a `PASS` on 2026-08-30 and it is now
  `LIVE_VERIFIED` (see the reconciliation entry at the end of this section).
- **Status:** implementable queue exhausted. Three batches landed and pushed
  this run — `b5eee22` (REG-001/002/003), `9926233` (UI-027), `dff00f3`
  (REG-004/005/006) — closing every open coded Main item. Details in
  `DASHBOARD_PROGRESS.md`; states in `DASHBOARD_ISSUES.md`.
- **Verification:** all of it `PUSHED`, none `LIVE_VERIFIED`. 33 checks are
  queued in `LIVE_VERIFICATION_QUEUE.md` — that file, not this one, carries
  the instructions. Per queue rule 5 the debt does not stall development.
- **Blockers:** none on code. Out of scoped, actionable Main-owned items.
- **Next task, in order of value:** (1) owner live-verifies this run's
  batches and `UI-011`; (2) if `DR-001` gets a concrete brief it becomes
  Main's next P3 — do not start a 52-card redesign speculatively; (3) failing
  both, a fresh narrow sweep for the false-safe-state class REG-002/003
  closed, which was not exhaustively re-run this session.
- `REG-005`'s fix changed the English text from `WAN —` to "WAN not
  reporting". Deliberate consistency choice, **not** owner-confirmed.
- **2026-08-30 00:35 UTC re-check (no code change):** fetched `origin/ha-deploy`
  — HEAD unchanged at `928fa78`, tree clean. Re-read `DASHBOARD_ISSUES.md`,
  `DASHBOARD_BACKLOG.md` and `LIVE_VERIFICATION_QUEUE.md` (all 33 rows still
  `PENDING`, none recorded). Confirmed no new actionable Main item exists:
  `DR-001` is still explicitly gated on a design brief Main should not write
  itself, and every other Main-owned item is `LIVE_VERIFICATION_REQUIRED`
  with zero human results recorded since the last update. Ran
  `bash scripts/ha_validate.sh` — passes clean (7/7) with no drift. Did not
  invent speculative work against Recent Change Protection: every area Main
  would touch was substantially modified within the last hour. No commit
  this run. **Next recommended work, unchanged:** owner live-verifies the
  pushed batches (`LIVE_VERIFICATION_QUEUE.md`) and gives `UI-011` one look
  at the Energy card, or the CasaRay Design Reviewer scopes a `DR-001`
  brief — either unblocks Main's next batch. Until one of those lands, a
  future run should re-fetch and re-check this same gate rather than
  re-deriving it from scratch.
- **2026-08-30 01:35-01:50 UTC — REG-007..011 (`b058006` + follow-up):**
  performed the fresh narrow false-safe-state sweep recommended by the 00:35
  re-check, scoped to aggregate cards (multiple sensors combined into one
  count/color) rather than the single-sensor cards REG-001..006 already
  covered. First pass (`b058006`) found and fixed two: the `home` House
  Pulse hero's door-open count/icon_color (REG-007), and a Doors status chip
  that was logged as `ipad-command-center` but is actually on `cameras`
  (REG-008 — see the correction note in `DASHBOARD_ISSUES.md`). Grepping
  the raw three-sensor door list afterward turned up three more unguarded
  copies of the identical template: the `home` view's own quick-control
  Doors chip (REG-009), the `home` Rooms grid's Security card
  (REG-010), and the genuine `ipad-command-center` Home Pulse chip row
  (REG-011) — sitting right beside its already-guarded REG-005 WAN sibling.
  All five silently dropped an unavailable door sensor from the tally
  instead of flagging it; three had no guard or bilingual text at all,
  unlike their Motion/WAN chip-row siblings. Fixed all five to the existing
  guarded/bilingual convention (see `DASHBOARD_ISSUES.md`); a final grep for
  the raw sensor list confirms every instance is now guarded.
  `bash scripts/ha_validate.sh` passes clean on both passes (7/7, 36/36
  views resolve). Pushed to `ha-deploy` and
  `claude/ha-dashboard-upgrades-wui7ig`. Treated as a legitimate RCP
  override (rules 5 and 7): same recurring defect class as the just-landed
  REG-001..006 sequence, found by design authority Main holds, not a
  redesign of anyone else's recent work. **Next recommended work:** queue is
  exhausted again — same as the 00:35 note, the owner live-verifying the
  growing `LIVE_VERIFICATION_QUEUE.md` backlog (now 38 rows) or a `DR-001`
  design brief are what unblock Main's next batch. A future run could widen
  this same aggregate-card sweep to `climate`, `status`, `network` and the
  room pages, which were not part of this pass — this run's own experience
  (5 instances of one bug, one mislabeled on first log) argues for grepping
  the exact sensor/entity list across the whole file rather than trusting a
  single spot-checked card.
- **2026-08-30 (this run) — widened the aggregate sweep; found `UI-030`
  (`691689a`):** confirmed no new-actionable P1/P2 item exists for Main:
  `DR-001` still explicitly needs a design brief before code, and every
  other Main-owned item is still `LIVE_VERIFICATION_REQUIRED` with no new
  human results recorded. Per the previous note's own recommendation, ran
  the false-safe aggregate sweep (`states() | select('eq','on') | count`
  dropping unavailable sensors from a tally) across `climate`, `network`,
  `status` and all seven room views (`parents-room`, `ray-bedroom`,
  `guest-room`, `living-room`, `kitchen`, `dining`, `garage`) — grepped the
  raw three-door-sensor array, every `namespace(`/`reduce(` aggregate, any
  combined `is_state(...) and/or is_state(...)` boolean, and every
  remaining reassuring-text literal (`Closed`, `Clear`, `Normal`, etc.) in
  the whole file. **Clean** — every instance already carries the
  unavailable/unknown/none guard, including the camera "N of 6 offline"
  aggregates on `cameras`/`ipad-command-center`, which turned out to
  already use a guarded `namespace()` pattern. While doing that sweep, also
  grepped for the separate UI-006 class (a raw `states()` interpolation
  printing a literal state name mid-sentence with no guard) and found one
  survivor: `ray-bedroom`'s LetPot "Grow Light" card (~L859), printing
  `select.lph_se_dcd9_light_mode`/`..._light_brightness` completely
  unguarded — an unavailable select would render as the literal word
  "unavailable". Both entities were already referenced only at that one
  line (confirmed by grep), so nothing was invented; added the same
  `bad = [unavailable, unknown, none]` guard used throughout the file,
  falling back to an em dash per field or a bilingual "Offline"/"离线" when
  both are unavailable. Filed as `UI-030` (S4 — cosmetic, not the
  security-class false-safe pattern: no reassuring claim was made, just a
  raw state name). `bash scripts/ha_validate.sh` passes clean (7/7, 386
  templates, 36/36 views, no entity/view loss). Pushed to `ha-deploy` and
  `claude/ha-dashboard-upgrades-wui7ig`; full narrative in
  `DASHBOARD_PROGRESS.md`. **Next recommended work:** queue is exhausted
  again — the false-safe aggregate class now appears fully closed
  dashboard-wide (two full sweeps, zero remaining instances), so a further
  identical sweep is unlikely to be productive. The next actionable options
  for a future run are, in order: (1) the owner live-verifies the
  growing `LIVE_VERIFICATION_QUEUE.md` backlog (now 39 rows) or gives
  `UI-011` one look at the Energy card; (2) if `DR-001` gets a concrete
  design brief it becomes Main's next P3 — still do not start a 52-card
  redesign speculatively; (3) failing both, a fresh pass specifically for
  the raw-interpolation (UI-006/UI-030) class across the six camera
  subviews and the `bills`/`bill-*` views is the next plausible source of
  small, safe, high-confidence fixes — not attempted this run, and the bill
  subviews are Billing-owned so would need Billing's routine, not Main's.
- **2026-08-30 (this run) — camera-subview sweep (clean); `UI-031`/`REG-013`
  fixed (`ccfb0c8`):** followed the previous note's own recommendation (3):
  the six `camera-*` subviews turned out clean — each is only a back chip and
  a `custom:webrtc-camera` card, no template content at all to guard, so no
  fix was possible or needed there. Widened the same raw-interpolation grep
  to the rest of the non-billing file instead and found three genuine
  unguarded/untranslated `{{ states(...) }}` instances: the `home`
  quick-control Person chip (raw `home`/`not_home`/`unavailable` state
  string, now the same distance-based bilingual convention already used on
  `people-locations`/`ipad-command-center`), the `home` Rooms-grid Climate
  card (raw lowercase HVAC mode, now guarded/title-cased like the adjacent
  Parents Room card), and the `light-ray-bedroom` Roller Shade card (raw
  cover state plus an **unguarded battery percentage** that would have
  rendered `unavailable%` — the exact UI-020 class). Filed as `UI-031`. While
  checking `lighting-modes` for the same class, found a genuine false-safe
  regression instead (not raw-interpolation): its three "Current State"
  light cards asserted a confident "On" for an `unavailable`/`unknown` light
  (neither the `off` branch nor the brightness-not-none branch caught it).
  Filed as `REG-013` and fixed with the standard bilingual
  "Offline"/"离线" branch. No entity invented — all four entities were
  already referenced elsewhere in the file under the conventions reused.
  Deliberately left the dashboard-wide `'On' if is_state(...,'on') else
  'Off'` toggle-chip pattern untouched — same theoretical gap, but a direct
  control on nearly every lighting view, never flagged across five prior
  regression sweeps, and redesigning it now would be a large speculative
  change outside this batch's scope; flagged for a future run if the owner
  wants it addressed. `bash scripts/ha_validate.sh` passes clean (7/7), 386
  templates, 36/36 views, no entity/view loss. Added `REG-013`/`UI-031` rows
  to `LIVE_VERIFICATION_QUEUE.md` and corrected its pending-count footer for
  this batch's own additions (39→42) in the same commit, to avoid repeating
  `REG-012`'s drift — `REG-012`'s own pre-existing gap (the still-missing
  `UI-030` row and the `34`→`39` portion of the undercount) is unchanged and
  stays with the Regression Auditor / Daily Project Coordinator, not
  self-fixed here. Full narrative in `DASHBOARD_PROGRESS.md`. **Next
  recommended work:** queue is exhausted again. In order: (1) the owner
  live-verifies the now-42-row `LIVE_VERIFICATION_QUEUE.md` backlog, gives
  `UI-011` one look at the Energy card, or confirms/rejects the toggle-chip
  question raised above; (2) if `DR-001` gets a concrete design brief it
  becomes Main's next P3 — still do not start a 52-card redesign
  speculatively; (3) failing both, the `bills`/`bill-*` raw-interpolation
  pass is still open but Billing-owned, not Main's to take; a fresh
  whole-file grep for any remaining `| float(0)` cast that lost its guard, or
  a second look at the six camera subviews' `webrtc-camera` config itself
  (not template content) for a UX-only improvement, are the next plausible
  low-risk sources if nothing above unblocks first.
- **2026-08-30 (same run) — `float(0)` sentinel re-check (no code change):**
  ran option (3) from the note above before ending the run: grepped every
  `| float(0)` cast in the file (39 occurrences, one more than the previous
  session's count of the combined `float(0)`/`float(100)`/`float(9999)`
  patterns, since this batch's own Roller Shade fix added one). Read each in
  context — **all 39 are already inside an `in bad`/`in [...]` guard branch**,
  none used as a bare unguarded sentinel; confirmed zero remaining
  `float(100)`/`float(9999)` instances anywhere in the file. Clean — no fix
  needed or made. No new actionable Main item exists after this: `DR-001`
  still needs a design brief, `UI-011` is still purely
  `LIVE_VERIFICATION_REQUIRED`, and the `bills`/`bill-*` raw-interpolation
  pass remains Billing-owned. Ending this run here — the coded-fix surface
  this session could reach (raw-interpolation class, false-safe class,
  float-sentinel class) is now swept clean; further identical sweeps are
  unlikely to be productive without new repository evidence or an owner
  decision. **Next recommended work, unchanged from above:** owner
  live-verification of the 42-row queue, or a `DR-001` design brief, are what
  unblock Main's next batch.
- **2026-08-30 — fresh Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `1bbe035`, tree clean before and
  after. Re-read `CLAUDE.md`, this file, `DASHBOARD_ISSUES.md` (Open section:
  only `UI-011`, excluded by queue rule 4, and `REG-012`, tracking-only and
  not Main-owned) and `DASHBOARD_BACKLOG.md`'s active queue (only `DR-001`,
  gated on a design brief this routine should not write itself). Confirmed no
  new actionable P0/P1/P2 Main item exists. Ran four grep sweeps the prior
  notes had not yet tried: (1) `icon_color` two-branch templates without an
  unavailable guard — the only unguarded instances are the dashboard-wide
  light/motion toggle-chip pattern (already flagged and deliberately left
  alone under `ccfb0c8`) and the `input_boolean.*_paid` bill-status chips,
  which are Billing-owned (`bill-*` views), not Main's; (2) every
  `.attributes.` read in the file — all already guarded with `is not
  none`/`default(`, none bare; (3) `int(0)` casts (5 total) and every
  `round(...)` chained off a raw `states()` read — all sit behind an existing
  `bad`/unavailable guard branch; (4) every `cover.` entity reference — all
  three roller-shade cards already fall back to an em dash / "Shade —" rather
  than asserting `open`/`closed` for an unavailable state, so no UI-031-class
  regression remains there. Also checked structural design compliance from
  `CLAUDE.md`'s Design Direction section: every `max_columns` in the file is
  ≤2, the theme's single `ha-card-border-radius: 18px` rule is the only
  radius definition found (no per-card override), and a scripted count of
  `custom:mushroom-title-card` per view confirms exactly one on every view
  that has one — the seven views with zero (six `camera-*` subviews plus
  `ipad-command-center`) are intentional: the camera subviews are back-chip +
  `webrtc-camera` only (already confirmed clean under `ccfb0c8`), and
  `ipad-command-center` is a kiosk wall panel built on `heading` cards with
  no page title by design (`99a77b4`) — its density is exactly `DR-001`'s
  open question, not a bug to fix speculatively. `bash scripts/ha_validate.sh`
  passes clean (7/7, no drift). **No fix made — nothing found to fix.** This
  is the fourth consecutive sweep (raw-interpolation, false-safe aggregate,
  float-sentinel, and now icon_color/attribute/int/cover/structural) to come
  back clean; Main's coded-fix surface appears genuinely exhausted without
  new repository evidence or an owner decision. **Next recommended work,
  unchanged:** (1) owner live-verification of the `LIVE_VERIFICATION_QUEUE.md`
  backlog (42 rows) or one look at `UI-011`'s Energy card; (2) a concrete
  `DR-001` design brief, which would become Main's next actionable P3; (3)
  failing both, the `bills`/`bill-*` raw-interpolation pass is still open but
  Billing-owned; a future run should look for genuinely new evidence (e.g.
  entities added since the last Entity Scout pass) rather than repeating this
  run's now four-times-clean sweep classes.
- **2026-08-30 — fifth Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `975a2b1`, tree clean before and
  after. Re-read `PROJECT_STATE.md`, `DASHBOARD_ISSUES.md`'s Open section
  (still only `UI-011`, excluded by queue rule 4, and `REG-012`,
  tracking-only) and `DASHBOARD_BACKLOG.md`'s active queue (still only
  `DR-001`, gated on a design brief). No new human verification result
  recorded in `LIVE_VERIFICATION_QUEUE.md` (still 42 pending, all `PENDING`
  or the syntax-doc example rows — no real `PASS`/`FAIL`/`PARTIAL` since the
  last check). Ran four grep classes not yet tried by prior sweeps: (1) every
  `state_attr(...)` call (14 total) — each is either inside an existing
  `is not none`/`bad`-list guard, or rendered only by a `conditional` card
  whose own conditions already exclude `unavailable`/`unknown`/`off` before
  the template runs (the Parents AC hero card, ~L146-172); none unguarded;
  (2) direct `states(...)` numeric comparisons with no `float()`/`int()`
  cast (a real Jinja bug class — comparing a string state to a number) —
  zero instances found anywhere in the file; (3) bare `| float` with no
  explicit default (hides a silent `0.0` sentinel differently from the
  already-audited `| float(0)` class) — five instances, all reading a
  `brightness` attribute already proven not-`none` by the enclosing
  `if b is not none` branch, so none is reachable with a bad value; (4) a
  full navigation-graph diff — extracted all 36 `path:` view IDs and all
  `navigation_path: /deez-smart-home/...` targets referenced anywhere in the
  file and compared them: **exact match, 36/36, zero broken links and zero
  orphaned views**. `bash scripts/ha_validate.sh` passes clean (7/7, 386
  templates, 36/36 views, no drift). **No fix made — nothing found to fix.**
  This is the fifth consecutive sweep this session to come back clean
  (raw-interpolation, false-safe aggregate, float-sentinel,
  icon_color/attribute/int/cover/structural, and now
  state_attr/comparison/bare-float/navigation). Main's coded-fix surface
  looks genuinely exhausted without new repository evidence or an owner
  decision — further sweeps of this shape are unlikely to be productive.
  **Next recommended work, unchanged and now overdue for owner attention:**
  (1) the 42-row `LIVE_VERIFICATION_QUEUE.md` backlog has had zero results
  recorded across at least five consecutive autonomous runs — this is the
  single highest-value unblock available, starting with `UI-011` (Total
  Solar, P1, possibly reading 1000× low) since it is the only open
  non-tracking issue; (2) a concrete `DR-001` design brief would become
  Main's next actionable P3; (3) the `bills`/`bill-*` raw-interpolation pass
  remains open but Billing-owned. A future autonomous run should not repeat
  this session's five clean sweep classes without new evidence — it should
  instead re-check whether any `LIVE_VERIFICATION_QUEUE.md` results or a
  `DR-001` brief have landed since this note.
- **2026-08-30 — `UI-011` live result reconciled (verification, no code
  change):** the owner returned the queue's **first live result**, from the
  native Home Assistant Energy dashboard: Solar 16 kWh, Grid 47.83 kWh, Home
  consumption 63.83 kWh, summing exactly, with the Solar production chart and
  Energy Distribution card independently showing 16 kWh. Corroborated
  read-only from here the same day — `Primo 5.0-1 (1) Energy day` = 16558 Wh
  (`unit_of_measurement: Wh`) = 16.56 kWh, and `Total energy` = 48425900 Wh,
  which the card's `/1000` renders as 48425.9 kWh: the same order of
  magnitude as `Energy year` (4588.1 kWh) and larger, as a lifetime counter
  must be. The feared 1000×-low reading does not occur. Reconciled per the
  `PASS` column of the Reconciliation procedure: queue Result → `PASS` (row
  kept for traceability), `DASHBOARD_ISSUES.md` `OPEN` → `VERIFIED` under the
  same stable ID, no backlog item recreated, priority and ownership untouched.
  Queue footer 44 → 43. **Scope kept narrow on purpose:** `UI-020` is a
  different check on the same card (that the readout carries a unit, and the
  Powerpal battery guard) and stays `PENDING`; a result on one surface does
  not clear a different check that happens to share a sensor.
- **2026-08-30 — `CFG-001`/`CFG-002` filed from that same verification (not
  Main's work):** the owner also observed Energy → Totals reporting Grid
  total 47.83 kWh at **A$437.60** — an implied A$9.1491/kWh, ~31.8× the real
  tariff. Investigated read-only, without touching any configuration. The one
  exposed monetary entity is named literally `sensor Cost` and read 451.1649
  AUD; `451.1649 − 437.60 = 13.5649`, which over 47.83 kWh is 0.2836 AUD/kWh —
  an ordinary rate. So this is **not a scaling bug**: today's true cost
  (≈A$13.56) is sitting inside the cost entity's accumulated total, which is
  being read as a period total. That is recorded as a hypothesis, not a
  finding — the cost source lives in `.storage/energy`, unreadable from here,
  and the grid source is a Powerpal sensor not exposed to Assist. Per the
  owner's explicit instruction and `MAINTENANCE.md`, **no configuration was
  changed**; `DASHBOARD_ISSUES.md` carries the four things the owner needs to
  read out of Settings → Dashboards → Energy to unblock it. `CFG-002` (the
  SolarNet import-tariff entity at 0.2880 vs the contracted 0.2734996) is
  logged separately and deliberately, so a 5% discrepancy is not confused
  with the 31.8× one. A new `CFG-` ID series was opened for defects whose
  cause and fix live in HA's own configuration rather than in any tracked
  file here; by definition no push to this branch can close one, and they do
  not enter the verification queue, which is for deployed changes awaiting a
  look.
- **2026-08-30 — sixth Main sweep, no code change:** fetched
  `origin/ha-deploy` — found `HEAD` had moved past this routine's initial read
  (to `7df2f5b`, the `UI-011` reconciliation + result-syntax cleanup above),
  re-fetched and re-read this file, `DASHBOARD_ISSUES.md` and
  `DASHBOARD_BACKLOG.md` fresh per the Concurrency policy before writing
  anything. Confirmed the reconciliation didn't change what's actionable for
  Main: `UI-011` is now `VERIFIED` and gone from the queue entirely (not
  merely `LIVE_VERIFICATION_REQUIRED`), and `CFG-001`/`CFG-002` are Home
  Assistant configuration defects outside this repository — not implementable
  from here regardless of severity, and explicitly excluded from the
  verification queue by their own new ID series. `DR-001` remains the only
  scoped Main item and still needs a design brief before code. Cleaned one
  piece of drift the reconciliation commit left behind: `DASHBOARD_BACKLOG.md`
  still listed `UI-011` in the active queue table as
  `LIVE_VERIFICATION_REQUIRED` — removed it (queue rule 12, completed items
  must not remain in the active queue) and added it to the closed one-line
  summary alongside `UI-025`/`UI-026`. Then ran three grep classes not yet
  tried by the prior five sweeps: (1) a structural scan for nested `type:
  grid` cards (a `grid` card whose own `cards:` list contains another `grid`
  card) — `CLAUDE.md`'s Sections convention calls for `grid_options` on leaf
  cards, not nested grids for column layout; scripted an indent-based pass
  over all 74 `type: grid` occurrences — **zero nested instances**, every
  grid is a top-level per-view section; (2) re-checked the one
  `state_attr(...)` read gated by a `conditional` card rather than an inline
  guard (the `home` Living Room TV "now playing" card, ~L199) — its
  `conditional` requires `state: playing` before the template card renders at
  all, so `media_title` cannot read on an idle/unavailable player, and the
  existing `or 'Playing'` already covers a null title; no fix needed; (3)
  audited static (non-templated) `icon_color:` literals dashboard-wide (29
  blue / 9 amber / 7 cyan / 6 grey / 4 green / 3 red / 3 purple / 3 indigo /
  2 orange) against `CLAUDE.md`'s "restrained amber for active state"
  direction — the palette is not amber-exclusive, but most of these are
  stable identity colors (media = purple, water = blue/cyan, alerts = red),
  not competing active-state indicators; recoloring ~29 static icons on
  Main's own unilateral judgment would be exactly the speculative visual
  change `DR-001`'s own note warns against, so **not touched** — flagged here
  as a candidate question for a future `DR-001`/design-brief discussion
  instead. `bash scripts/ha_validate.sh` passes clean (7/7, 386 templates,
  36/36 views, no drift). **No dashboard-code fix made this run** — the
  grep-sweep surface (raw-interpolation, false-safe aggregate, float-sentinel,
  icon_color/attribute/int/cover/structural, state_attr/comparison/bare-float/
  navigation, nested-grid/conditional-guard/color-palette) is six-for-six
  clean or non-actionable without a design decision. **Next recommended
  work:** (1) `UI-011`'s `PASS` shows the owner is now actively working
  through the verification queue — the highest-value unblock is simply
  continuing that: `UI-020`/`UI-021` are the two remaining `energy`-group
  `PENDING` rows, then the rest of the ~43-row queue; (2) `CFG-001` (S1, grid
  cost ~31.8× too high) needs the owner to read four specific values out of
  Settings → Dashboards → Energy per `DASHBOARD_ISSUES.md` — genuinely
  outside any autonomous routine's reach; (3) a concrete `DR-001` design
  brief would become Main's next actionable P3. A future run should check for
  new verification results or a design brief before repeating this session's
  now six-times-clean sweep classes.
- **2026-08-30 — seventh Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `7b42918`, tree clean before and
  after. Re-read `CLAUDE.md`, this file in full, `DASHBOARD_ISSUES.md`'s Open
  section (still only `CFG-001`/`CFG-002` — both Home Assistant configuration
  defects outside this repository, not implementable from here regardless of
  severity — and `REG-014`, tracking-completeness only, owned by Billing/the
  Daily Project Coordinator, not Main) and `DASHBOARD_BACKLOG.md`'s active
  queue (still only `DR-001`, gated on a design brief this routine should not
  write itself). Checked `LIVE_VERIFICATION_QUEUE.md` directly: still 43
  `PENDING` rows, zero `PASS`/`FAIL`/`PARTIAL` recorded since `UI-011` — no
  new human result to reconcile. Ran one grep class not yet tried by the prior
  six sweeps: cross-referenced every `theme:` reference in the dashboard file
  against the theme names actually defined in `themes/deez_your_name.yaml`.
  Five distinct per-view themes are referenced (`Deez Energy`, `Deez
  Cameras`, `Deez Security`, `Deez Climate`, `Deez Lighting`, matching
  `CLAUDE.md`'s "five per-view themes" claim) against six defined (`Deez
  Smart Home`, `Deez Cameras`, `Deez Climate`, `Deez Energy`, `Deez
  Lighting`, `Deez Security`) — every referenced name exists, no orphaned or
  undefined theme, and `Deez Smart Home` is the intentional default for views
  with no per-view override. **Clean — no fix needed.** `bash
  scripts/ha_validate.sh` passes clean (7/7, 386 templates, 36/36 views, no
  drift). **No dashboard-code fix made this run** — this is now seven
  consecutive clean or non-actionable sweeps this session with zero new
  repository evidence and zero new human verification results since the last
  check. Per this file's own guidance not to keep re-deriving the same
  conclusion, this run stops here rather than manufacturing an eighth grep
  pass with negligible expected yield. **Next recommended work, unchanged
  and now increasingly overdue for owner attention:** (1) the 43-row
  `LIVE_VERIFICATION_QUEUE.md` backlog has had exactly one result
  (`UI-011` `PASS`) across at least seven consecutive autonomous runs — this
  remains the single highest-value unblock, with `UI-020`/`UI-021` (same
  `energy` group as the just-verified `UI-011`) the natural next two to
  check; (2) `CFG-001` (S1, grid cost ~31.8× too high) needs the owner to
  read four specific values out of Settings → Dashboards → Energy per
  `DASHBOARD_ISSUES.md` — genuinely outside any autonomous routine's reach;
  (3) a concrete `DR-001` design brief would become Main's next actionable
  P3. A future autonomous run should check for new verification results or a
  design brief before attempting further identical sweep classes — the
  coded-fix surface reachable by grep sweeps alone appears to be genuinely
  exhausted for this session.
- **2026-08-30 — eighth Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `28b1caf`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full. `DASHBOARD_ISSUES.md`'s
  Open section is unchanged: only `CFG-001`/`CFG-002` (Home Assistant
  configuration, outside this repository) — `REG-012`/`REG-014` are
  tracking-only and already closed. `DASHBOARD_BACKLOG.md`'s active queue is
  unchanged: `DR-001` is still the only Main-owned item, still gated on a
  design brief this routine should not write itself; `BILL-001/002/003`
  remain Billing-owned. `LIVE_VERIFICATION_QUEUE.md` still shows zero new
  `PASS`/`FAIL`/`PARTIAL` since `UI-011`. Rather than repeat one of the seven
  already-clean sweep classes, ran two genuinely new, narrow checks: (1)
  audited every guard list containing `'unavailable'`/`'unknown'` for a
  missing `'none'` sentinel (the file's own three-value convention) —
  grepping for `unavailable` without `none` nearby returned five hits, but
  all were false positives from YAML line-folding (the `'none'` value sits on
  the next folded line, e.g. ~L1598/1605) except two `climate` `icon_color`
  guards (~L376, ~484) checking `states('climate...') not in
  ['off','unavailable','unknown']` with no `'none'` branch — confirmed **not**
  a gap: a Home Assistant entity's own `.state` is never the literal string
  `'none'` (that sentinel exists in this file's convention to guard attribute
  reads via `state_attr`/`brightness`, which can be Python `None`, not entity
  states), so omitting it here is correct, not a regression; (2) extracted
  every view's `path:` value (36 total) and confirmed zero duplicates — no
  two views collide on the same URL segment. Both checks clean, nothing to
  fix. `bash scripts/ha_validate.sh` passes clean (7/7, 386 templates, 36/36
  views, no drift). **No dashboard-code fix made this run** — eight
  consecutive sweeps this session are now clean or non-actionable without a
  design decision or a human verification result. Per this file's own
  guidance against re-deriving the same conclusion, this run does not attempt
  a ninth grep pass; the coded-fix surface reachable by static repository
  inspection alone appears genuinely exhausted for this session. **Next
  recommended work, unchanged:** (1) the `LIVE_VERIFICATION_QUEUE.md` backlog
  (43 rows, one `PASS` recorded across eight consecutive runs) is the
  single highest-value unblock — `UI-020`/`UI-021` are the natural next two
  in the same `energy` group as the verified `UI-011`; (2) `CFG-001` needs
  the owner to read four values out of Settings → Dashboards → Energy per
  `DASHBOARD_ISSUES.md`, outside any autonomous routine's reach; (3) a
  concrete `DR-001` design brief would become Main's next actionable P3. A
  future run should check for new verification results or a design brief
  before attempting further sweeps of this shape.
- **2026-08-30 — ninth Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `f9cb18a`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full. `DASHBOARD_ISSUES.md`'s
  Open section is unchanged: only `CFG-001`/`CFG-002` (Home Assistant
  configuration, outside this repository). `DASHBOARD_BACKLOG.md`'s active
  queue is unchanged: `DR-001` is still the only Main-owned item, still
  gated on a design brief this routine should not write itself;
  `BILL-001/002/003` remain Billing-owned and blocked/partial.
  `LIVE_VERIFICATION_QUEUE.md` still shows exactly one recorded result
  (`UI-011` `PASS`) across nine consecutive autonomous runs — 44 rows,
  no new `PASS`/`FAIL`/`PARTIAL` to reconcile. Rather than repeat one of
  the eight already-clean sweep classes, ran a genuinely new one: a
  repository-wide credential/PII exposure scan beyond the already-tracked
  billing account-number/NMI/MIRN checks. Grepped the whole dashboard and
  theme file for API-key/token/password/bearer/client-secret-shaped
  literals outside `!secret` usage — zero hits. Separately scanned for
  hardcoded GPS coordinate pairs, IPv4 addresses, email addresses and phone
  numbers that could leak a home address or personal contact detail outside
  the already-tracked, entity-driven person-location cards — zero hits; the
  only decimal-pair matches found were billing tariff/rate figures (e.g.
  `27.34996`), not coordinates. `bash scripts/ha_validate.sh` passes clean
  (7/7, 386 templates, 36/36 views, no drift). **No dashboard-code fix made
  this run** — nine consecutive sweeps this session are now clean or
  non-actionable without a design decision or a human verification result.
  **Next recommended work, unchanged and now increasingly overdue for owner
  attention:** (1) the `LIVE_VERIFICATION_QUEUE.md` backlog (44 rows, one
  `PASS` recorded across nine consecutive autonomous runs) remains the
  single highest-value unblock — `UI-020`/`UI-021` are the natural next two
  in the same `energy` group as the verified `UI-011`; (2) `CFG-001` (S1,
  grid cost ~31.8× too high) needs the owner to read four specific values
  out of Settings → Dashboards → Energy per `DASHBOARD_ISSUES.md`, outside
  any autonomous routine's reach; (3) a concrete `DR-001` design brief would
  become Main's next actionable P3. A future autonomous run should check for
  new verification results or a design brief before attempting further
  identical sweep classes — static-repository-inspection sweeps of this
  shape now appear exhausted for this session without new evidence.
- **2026-08-30 — tenth Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `9f75c79`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full. `DASHBOARD_ISSUES.md`'s
  Open section is unchanged: only `CFG-001`/`CFG-002` (Home Assistant
  configuration, outside this repository, blocked on owner diagnosis).
  `DASHBOARD_BACKLOG.md`'s active queue is unchanged: `DR-001` is still the
  only Main-owned item, still gated on a design brief this routine should not
  write itself; `BILL-001/002/003` remain Billing-owned and blocked/partial.
  `LIVE_VERIFICATION_QUEUE.md` still shows exactly one recorded result
  (`UI-011` `PASS`) — confirmed the `UI-020 FAIL`/`REG-005 PARTIAL` lines a
  raw grep of that file turns up are the same Result-syntax documentation
  examples already quoted in this file, not real entries. Rather than repeat
  one of the nine already-clean grep-based sweep classes, parsed the
  dashboard as structured YAML (not text grep) for three genuinely new
  checks: (1) cross-referenced every direct-control card
  (`light`/`cover`/`climate`/`fan`/`lock`/`media-control`/domain-matched
  `tile` cards) against its own `entity` across all 36 views — 58 total
  control-card entity references, zero duplicates in any view, extending the
  `UI-013` media-player-duplication class to every controllable domain
  instead of just media players; (2) checked every fixed-type control card
  for a domain mismatch between its declared card type and its entity's
  actual domain (e.g. a `light` card pointed at a `switch` entity) — zero
  mismatches; (3) re-examined the two `{% for %}` loops in the file (the
  camera-status aggregates on `cameras` and `ipad-command-center`) for the
  classic Jinja loop-scoping gotcha (a `{% set %}` inside a `for` not
  surviving past `endfor`) — both already use `namespace()` correctly. While
  there, checked whether the file's pervasive `{% set x = ... %}` inside
  `{% if %}/{% elif %}/{% else %}` pattern (e.g. the Roller Shade `shade`
  variable, ~L384) has the same class of bug — confirmed by rendering the
  exact construct standalone that it does not: Jinja's `if` blocks, unlike
  `for` loops, do not introduce a new variable scope, so the value set in
  whichever branch runs is visible after `endif`. Also re-tried
  `GetLiveContext` directly against "Front Door Battery" to check whether the
  connector now exposes `entity_id` for `UI-032` — it still returns only
  name/domain/state/area/attributes, confirming that block is unchanged.
  `bash scripts/ha_validate.sh` passes clean (7/7, 386 templates, 36/36
  views, no drift). **No dashboard-code fix made this run** — ten
  consecutive sweeps this session are now clean or non-actionable without a
  design decision or a human verification result, spanning
  raw-interpolation, false-safe aggregate, float-sentinel,
  icon_color/attribute/int/cover/structural,
  state_attr/comparison/bare-float/navigation,
  nested-grid/conditional-guard/color-palette, theme cross-reference,
  guard-list-none-sentinel/duplicate-path, credential/PII exposure, and now
  duplicate-control/type-domain-mismatch/loop-scoping classes. **Next
  recommended work, unchanged and now significantly overdue for owner
  attention:** (1) the `LIVE_VERIFICATION_QUEUE.md` backlog (44 rows, one
  `PASS` recorded across ten consecutive autonomous runs) remains the single
  highest-value unblock — `UI-020`/`UI-021` are the natural next two in the
  same `energy` group as the verified `UI-011`; (2) `CFG-001` (S1, grid cost
  ~31.8× too high) needs the owner to read four specific values out of
  Settings → Dashboards → Energy per `DASHBOARD_ISSUES.md`, genuinely outside
  any autonomous routine's reach; (3) a concrete `DR-001` design brief would
  become Main's next actionable P3; (4) `UI-032` (device battery coverage)
  stays `BLOCKED` — `GetLiveContext` still does not expose `entity_id`,
  reconfirmed this run. A future autonomous run should not attempt further
  static-repository-inspection sweeps without new evidence — this class of
  check now appears exhausted for Main; the next productive Main run is one
  that reacts to a new human verification result or design brief, not one
  that invents an eleventh grep class.
- **2026-08-30 — eleventh Main sweep, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `e9a22fc`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full. `DASHBOARD_ISSUES.md`'s
  Open section is unchanged: only `CFG-001`/`CFG-002` (Home Assistant Energy
  configuration, outside this repository, blocked on owner diagnosis).
  `DASHBOARD_BACKLOG.md`'s active queue is unchanged: `DR-001` (still gated
  on a design brief this routine should not write itself) and `UI-032`
  (still `BLOCKED` on a Developer Tools → States export the owner must
  supply) remain the only Main-owned items; `BILL-001/002/003` stay
  Billing-owned. `LIVE_VERIFICATION_QUEUE.md` is unchanged since the last
  run: 44 rows, all `PENDING`, zero `PASS`/`FAIL`/`PARTIAL` recorded (the
  single `UI-011` `PASS` already reconciled off the queue previously) — no
  new human result to react to. Per the prior note's own explicit guidance
  not to invent another grep-sweep class, ran two bounded, genuinely new
  compliance checks instead of repeating one of the ten already-clean
  classes: (1) every `icon:` field in the file (excluding templated
  `{{ }}` values) — confirmed 100% use a valid `mdi:` prefix, zero bare or
  malformed icon literals; (2) audited every `column_span:` value (16
  occurrences) against `CLAUDE.md`'s explicit "iPad landscape renders about
  two usable columns... design for two" rule — all 16 are exactly `2`, zero
  violations, so no card claims a wider span than the design direction
  allows. Both clean. `bash scripts/ha_validate.sh` passes clean (7/7, 386
  templates, 36/36 views, no drift). **No dashboard-code fix made this
  run** — eleven consecutive sweeps this session are now clean or
  non-actionable without a design decision or a human verification result.
  **Next recommended work, unchanged and now significantly overdue for
  owner attention:** (1) the `LIVE_VERIFICATION_QUEUE.md` backlog (44 rows,
  one `PASS` recorded across eleven consecutive autonomous runs) remains
  the single highest-value unblock — `UI-020`/`UI-021` are the natural next
  two in the same `energy` group as the verified `UI-011`; (2) `CFG-001`
  (S1, grid cost ~31.8× too high) needs the owner to read four specific
  values out of Settings → Dashboards → Energy per `DASHBOARD_ISSUES.md`,
  genuinely outside any autonomous routine's reach; (3) a concrete `DR-001`
  design brief would become Main's next actionable P3; (4) `UI-032` (device
  battery coverage) stays `BLOCKED` on a States export. A future autonomous
  run should not attempt further static-repository-inspection sweeps
  without new evidence — the next productive Main run is one that reacts to
  a new human verification result, entity export, or design brief.
- **2026-08-30 — twelfth Main check, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `bc15e9d`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full, `DASHBOARD_ISSUES.md`'s
  Open section (unchanged: only `CFG-001`/`CFG-002`, both Home Assistant
  configuration outside this repository, blocked on owner diagnosis) and
  `DASHBOARD_BACKLOG.md`'s active queue (unchanged: `UI-032` still `BLOCKED`
  on a Developer Tools → States export, `DR-001` still gated on a design
  brief this routine should not write itself). Checked
  `LIVE_VERIFICATION_QUEUE.md` directly rather than trusting the prior
  note's count: 47 `PENDING` rows, still exactly one real result recorded
  (`UI-011` `PASS`) — no new `PASS`/`FAIL`/`PARTIAL` to reconcile. Per the
  eleventh sweep's own explicit conclusion, did not invent a twelfth
  static-repository-inspection grep class with no new evidence to justify
  it — eleven consecutive sweeps this session (raw-interpolation,
  false-safe aggregate, float-sentinel, icon_color/attribute/int/cover/
  structural, state_attr/comparison/bare-float/navigation, nested-grid/
  conditional-guard/color-palette, theme cross-reference, guard-list-none-
  sentinel/duplicate-path, credential/PII exposure, duplicate-control/
  type-domain-mismatch/loop-scoping, icon-prefix/column-span) already cover
  that surface. **No dashboard-code fix made this run** — genuinely no safe,
  actionable, unblocked Main-owned work exists. **Next recommended work,
  unchanged:** (1) the `LIVE_VERIFICATION_QUEUE.md` backlog (47 rows, one
  `PASS` recorded across twelve consecutive autonomous runs) remains the
  single highest-value unblock — `UI-020`/`UI-021` are the natural next two
  in the same `energy` group as the verified `UI-011`; (2) `CFG-001` (S1,
  grid cost ~31.8× too high) needs the owner to read four specific values
  out of Settings → Dashboards → Energy per `DASHBOARD_ISSUES.md`; (3) a
  concrete `DR-001` design brief would become Main's next actionable P3;
  (4) `UI-032` stays `BLOCKED` on a States export. A future autonomous run
  should check for new verification results, an entity export, or a design
  brief before attempting any further static-repository-inspection sweep.
- **2026-08-30 — thirteenth Main check, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `7171427`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full, `DASHBOARD_ISSUES.md`'s
  Open section (unchanged: only `CFG-001`/`CFG-002`, both Home Assistant
  Energy configuration outside this repository, blocked on owner diagnosis)
  and `DASHBOARD_BACKLOG.md`'s active queue (unchanged: `UI-032` still
  `BLOCKED` on a Developer Tools → States export, `DR-001` still gated on a
  design brief this routine should not write itself; `BILL-001/002/003`
  remain Billing-owned and blocked/partial). Checked
  `LIVE_VERIFICATION_QUEUE.md` directly: 47 `PENDING` rows, still exactly one
  real result recorded (`UI-011` `PASS`) across thirteen consecutive
  autonomous runs — no new `PASS`/`FAIL`/`PARTIAL` to reconcile. Per the
  twelfth check's own explicit conclusion, did not invent a thirteenth
  static-repository-inspection grep class with no new evidence to justify
  it — eleven distinct sweep classes already cover that surface and a
  twelfth confirmed no drift. Ran `bash scripts/ha_validate.sh` as a baseline
  health check only (not a substitute for new work): passes clean (7/7, 386
  templates, 36/36 views, no drift). **No dashboard-code fix made this run —
  genuinely no safe, actionable, unblocked Main-owned work exists.** The
  session is now fully gated on human input across all three of Main's open
  threads: (1) `LIVE_VERIFICATION_QUEUE.md`'s 47-row backlog has had exactly
  one result in thirteen runs; (2) `CFG-001` (S1, Energy → Totals grid cost
  ~31.8× too high, real money on a live dashboard) needs the owner to read
  four specific values out of Settings → Dashboards → Energy per
  `DASHBOARD_ISSUES.md` — genuinely outside any autonomous routine's reach;
  (3) `DR-001` needs a concrete design brief before it can become Main's next
  actionable P3. Flagging this explicitly rather than filing a fourteenth
  identical note: a future autonomous run should not attempt further
  static-repository-inspection sweeps without new evidence — the next
  productive Main run is one that reacts to a new human verification result,
  entity export, or design brief, and this state should be surfaced to the
  owner rather than silently re-confirmed indefinitely.
- **2026-08-30 — fourteenth Main check, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `8f07bb4`, tree clean before and
  after. Re-read `CLAUDE.md` and this file in full, `DASHBOARD_ISSUES.md`'s
  Open section (unchanged: only `CFG-001`/`CFG-002`, both Home Assistant
  Energy configuration outside this repository) and `DASHBOARD_BACKLOG.md`'s
  active queue (unchanged: `UI-032` `BLOCKED` on a States export, `DR-001`
  gated on a design brief). `LIVE_VERIFICATION_QUEUE.md` unchanged: still no
  new `PASS`/`FAIL`/`PARTIAL` beyond the one `UI-011` result. Per the
  thirteenth check's own conclusion, did not manufacture a twelfth
  static-repository grep class; instead ran three narrow, targeted checks
  aimed specifically at gaps the prior twelve sweep classes could plausibly
  have missed: (1) cross-referenced every `action: navigate` occurrence (119)
  against an immediately-following `navigation_path:` — 119/119 paired, no
  orphaned navigate action; (2) inventoried every `custom:` card type used
  (six: `mushroom-chips-card`, `mushroom-climate-card`,
  `mushroom-media-player-card`, `mushroom-template-card`,
  `mushroom-title-card`, `webrtc-camera`) — stable, consistent with
  `CLAUDE.md`'s stated stack, nothing to cross-check further since Lovelace
  resource registration lives outside this repository; (3) checked whether
  any `primary:`/`secondary:` field on a templated card holds a bare,
  untemplated English literal alongside sibling cards that do use the
  `chinese_dashboard` bilingual ternary — found none; every non-empty
  `primary`/`secondary` value in the file is already a template. All three
  clean. `bash scripts/ha_validate.sh` passes clean (7/7, 386 templates,
  36/36 views, no drift). **No dashboard-code fix made this run — genuinely
  no safe, actionable, unblocked Main-owned work exists**, fourteen
  consecutive runs now. Notified the owner directly this run (push
  notification) that `CFG-001` (real money, ~31.8× overstated Energy cost)
  and the now-dormant 47-row verification queue need their attention, since
  this file's own thirteenth-check note asked for exactly that escalation
  and no prior run appears to have sent one. **Next recommended work,
  unchanged:** (1) owner works `CFG-001`'s four-point diagnostic in
  `DASHBOARD_ISSUES.md`; (2) owner clears any of the 47-row
  `LIVE_VERIFICATION_QUEUE.md` backlog; (3) a concrete `DR-001` design brief;
  (4) a Developer Tools → States export unblocks `UI-032`. A future
  autonomous run should check for movement on any of these four before
  attempting a fifteenth static-repository sweep.
- **2026-08-30 — post-`UI-032` check, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `15ec422` (the `UI-032` stamp
  commit), tree clean before and after. The battery-coverage export the
  fourteenth check flagged as the outstanding unblock arrived and was
  consumed: `UI-032` is implemented (`a183d5f`, all six owner-verified
  entities bound, RingRing included, none invented) and correctly moved to
  `FIXED — AWAITING LIVE VERIFICATION` in `DASHBOARD_ISSUES.md` and out of
  the active queue in `DASHBOARD_BACKLOG.md`. Re-read `CLAUDE.md`, this file
  in full, `DASHBOARD_ISSUES.md`'s Open section (unchanged: only
  `CFG-001`/`CFG-002`, both Home Assistant Energy configuration outside this
  repository, blocked on owner diagnosis) and `DASHBOARD_BACKLOG.md`'s active
  queue (now contains only `DR-001`, Main-owned but still gated on a design
  brief this routine should not write itself, plus `BILL-001/002/003`, all
  Billing-owned and blocked/partial). Checked `LIVE_VERIFICATION_QUEUE.md`
  directly: 45 rows, still exactly one real result recorded (`UI-011`
  `PASS`) — no new `PASS`/`FAIL`/`PARTIAL` to reconcile, and no movement on
  `CFG-001` since the owner notification two checks ago. Confirmed via
  `git log a183d5f..HEAD` that no other routine has committed since the
  stamp. `bash scripts/ha_validate.sh` passes clean (7/7, 389 templates,
  36/36 views, no drift). **No dashboard-code fix made this run — consuming
  the one new piece of evidence (`UI-032`'s entity export) closed the only
  gap that had opened since the fourteenth check, and nothing has replaced
  it.** Main is back to exactly the state the fourteenth check already
  escalated: zero actionable P0/P1/P2 work, `DR-001` the only P3 and not
  startable without a brief, both real blockers (`CFG-001`, the 45-row
  verification backlog) still owner-side and already reported. Did not
  invent a fifteenth static-repository sweep — twelve grep/structural
  classes already swept this session came back clean or non-actionable, and
  this run's own re-read found no new file, entity or issue evidence to
  justify a thirteenth. **Recommendation: pause this schedule.** This is the
  project's stable/blocked state per this run's own instructions — no new
  evidence since the last check, and the fourteenth check already sent the
  one owner notification this class of finding warrants; repeating it here
  would be a duplicate, not new information. Resume when any of: an owner
  live-verification result lands in `LIVE_VERIFICATION_QUEUE.md`, `CFG-001`'s
  four-point diagnostic is answered, a `DR-001` design brief is supplied, or
  a new entity/defect/requirement is otherwise supplied. **Exact next
  recommended task, unchanged:** (1) owner works `CFG-001`'s diagnostic in
  `DASHBOARD_ISSUES.md`; (2) owner records any result in the 45-row
  `LIVE_VERIFICATION_QUEUE.md`, starting with `UI-020`/`UI-021`
  (same `energy` group as the already-verified `UI-011`) or `UI-032` itself
  now that it is deployed; (3) a concrete `DR-001` design brief. No
  fifteenth sweep should be attempted without one of those landing first.
- **2026-08-30 — post-`CFG-003` check, no code change:** fetched
  `origin/ha-deploy` — `HEAD` unchanged at `83110de` (the `CFG-003` stamp
  commit), tree clean before and after. Re-read `CLAUDE.md` and this file in
  full, `DASHBOARD_ISSUES.md`'s Open section (`CFG-001`/`CFG-002`/`CFG-003`,
  all Home Assistant / deployment-bridge issues outside this repository's
  reach) and `DASHBOARD_BACKLOG.md`'s active queue (unchanged: `DR-001`
  Main-owned, still gated on a design brief this routine should not write
  itself; `BILL-001/002/003` Billing-owned and blocked/partial). Checked
  `LIVE_VERIFICATION_QUEUE.md` directly: 45 rows, still exactly one real
  result recorded (`UI-011` `PASS`) — no new `PASS`/`FAIL`/`PARTIAL` since the
  last check, and no movement on `CFG-001` or the owner diagnostic steps
  `CFG-003` names. `bash scripts/ha_validate.sh` passes clean (7/7, 389
  templates, 36/36 views, no drift). **No dashboard-code fix made this run.**
  `CFG-003` — filed last run — is now the dominant blocker for this entire
  routine, not merely another queue item: it states plainly that no change to
  `dashboards/deez_smart_home.yaml` has ever been independently confirmed
  live, that 12+ commits (now more) have touched the file since the one
  deployment run on record, which itself wrote nothing, and it explicitly
  instructs every routine not to queue further dashboard work on the
  assumption it will deploy. Honoured that instruction this run: did not
  attempt a fifteenth static-repository sweep (the coded-fix surface was
  already exhausted before `CFG-003`, and finding another cosmetic fix would
  not address the actual problem — a fix nobody can confirm is reaching the
  dashboard is not a productive use of a batch). **Recommendation, now
  stronger than the prior check's: pause this schedule until the owner
  completes `CFG-003`'s five-step diagnostic** (`DASHBOARD_ISSUES.md`
  steps a–e: check the Raw configuration editor for `UI-032 PROBE v1`,
  search for `front_door_battery`, look for any alert card directly under
  the Home page header, run the deploy script by hand and capture its
  output, and check Settings → Dashboards for a duplicate `deez-smart-home`
  entry). Continuing to run autonomous batches while the deployment path
  itself is unconfirmed risks compounding unverifiable work: every further
  push is one more commit in the same unproven state `CFG-003` describes.
  Sent the owner a push notification this run flagging `CFG-003` directly,
  since the previous check's own escalation (fourteenth check, `CFG-001`)
  predates `CFG-003`'s discovery and does not cover it. **Exact next
  recommended task, unchanged in substance, reordered by severity:**
  (1) owner works `CFG-003`'s five-step diagnostic — decisive and the
  fastest of the three to check; (2) owner works `CFG-001`'s four-point
  diagnostic in `DASHBOARD_ISSUES.md` (real money, ~31.8× overstated Energy
  cost); (3) owner records any result in the 45-row
  `LIVE_VERIFICATION_QUEUE.md`; (4) a concrete `DR-001` design brief. A
  future autonomous run should re-check `CFG-003`'s status before resuming
  any dashboard-code batch, not merely before resuming a sweep.
- **2026-08-30 (this run) — re-check after `CFG-003` root cause, no code
  change:** fetched `origin/ha-deploy` — `HEAD` unchanged at `56d6dd0` (the
  `CFG-003` root-cause stamp commit), tree clean before and after. Re-read
  `CLAUDE.md` and this file in full, `DASHBOARD_ISSUES.md`'s `CFG-003`
  root-cause section and Open section (`CFG-001`/`CFG-002`/`CFG-003`, all
  outside this repository's reach), and `DASHBOARD_BACKLOG.md`'s active
  queue (unchanged: `DR-001` the sole item, still gated on a design brief
  this routine should not write itself). `bash scripts/ha_validate.sh`
  passes clean (7/7, 424 templates, 36/36 views, no drift). **No
  dashboard-code change made.** `CFG-003` is now root-caused, not merely
  filed: `ha-deploy`'s history was force-replaced on 2026-08-29, and the
  Home Assistant host's clone is still on the old, disjoint history, so
  **no push since `376f3d8` has ever reached the live dashboard** — every
  `FIXED`/`PUSHED` row for that entire range is unproven at the delivery
  step, not merely unobserved. A five-step owner recovery procedure is
  recorded in `DASHBOARD_ISSUES.md` (`git fetch`, confirm the disjoint
  merge-base, check for host-only commits worth saving, then
  `git reset --hard origin/ha-deploy` on the host). That recovery is
  git/deployment infrastructure on the HA host itself — protected under
  `CLAUDE.md`/`MAINTENANCE.md`, not something this routine executes. No new
  evidence since `ec10656`/`56d6dd0`: no live-verification result recorded,
  no `DR-001` brief, no owner confirmation the host recovery has run. Sent
  the owner a push notification this run with the confirmed root cause and
  the exact recovery commands, since the prior notification (fourteenth
  check) predates this finding. **Recommendation: hold dashboard-code
  batches until the owner completes the `CFG-003` host recovery** — the
  coded-fix surface was already exhausted before `CFG-003`, and pushing
  further work into a pipe confirmed not to be delivering is not
  productive. **Exact next recommended task:** (1) owner runs the `CFG-003`
  recovery procedure on the HA host and confirms `git rev-parse --short
  HEAD` there advances past `376f3d8`; (2) owner (or a future run once
  confirmed) runs `/config/deploy_deez_dashboard.sh` by hand and checks for
  `UI-032 PROBE v1` live, closing the loop `CFG-003` describes; (3) failing
  owner action, no new dashboard-code work is warranted this run — `DR-001`
  remains blocked on a design brief only the owner can supply, and no other
  actionable Main-owned item exists.
- **2026-08-30 (this run) — honoring owner-directed pause, no code change:**
  fetched `origin/ha-deploy` — `HEAD` unchanged at `7b077c3`, tree clean
  before and after. That commit, landed after this routine's last check-in
  (`c40072c`), added the **Schedule Status: PAUSED** section now at the top
  of this file: the owner told a live session directly to pause all
  autonomous dashboard upgrade work, independent of and stacked on top of
  the still-unresolved `CFG-003` deploy-pipeline blocker. Per that section's
  own instruction — "if you are an autonomous routine reading this after
  being fired by an external schedule, honor it immediately and do not
  require further confirmation" — this run did not read
  `DASHBOARD_ISSUES.md`/`DASHBOARD_BACKLOG.md` beyond a light skim, did not
  run a sweep, and made **no dashboard-code change**, since implementation
  itself is the thing paused, not merely today's specific queue item.
  `DR-001` and every `CFG-00x` blocker are unchanged and not re-derived
  here. **This is not a stale-queue no-op** — it is a hard stop the owner
  set on purpose, and should not be treated as "no worthwhile work found"
  for the purposes of any 2-consecutive-no-op pause recommendation; that
  recommendation is superseded by the owner's own explicit pause. Sent the
  owner a push notification this run noting the schedule fired again after
  the pause was recorded, since the pause section itself observes that
  disabling the external trigger is a separate, owner-side step this file
  cannot perform. **Exact next recommended task:** none from this routine
  until the owner explicitly lifts the Schedule Status: PAUSED section (by
  replacing it with a dated note of who lifted it and when, per its own
  instructions) — at that point resume from `DR-001` / the `CFG-003` host
  recovery status as the last active-check note above describes. A future
  run should re-fetch and re-read the top of this file first, before doing
  anything else, to check whether the pause is still in effect.
- **2026-08-30 (this run) — re-check, pause still in effect, no code
  change:** fetched `origin/ha-deploy` — `HEAD` unchanged at `2b71373`, tree
  clean before and after. The **Schedule Status: PAUSED** section is
  unmodified: no dated lift note has been added, so the owner-directed pause
  from the previous check-in still applies. No new commits, no new evidence,
  no human verification results recorded since the last check-in. Made no
  dashboard-code change and did not start any queued item, per the pause.
  Did **not** send a duplicate push notification — the previous run already
  alerted the owner that the external schedule keeps firing after the pause
  was recorded, and nothing has changed since that alert, so a second one
  would be redundant per the routine's own notification guidance. **Exact
  next recommended task:** unchanged — none from this routine until the
  owner lifts the pause (dated note replacing the Schedule Status section);
  at that point resume from `DR-001` / the `CFG-003` host recovery status.
  If the owner has not yet disabled the external recurring trigger, that is
  the actual unblock here, not further repository work. A future run should
  again re-fetch and re-read the top of this file first.
- **2026-08-30 (this run) — second re-check, pause still in effect, no code
  change:** fetched `origin/ha-deploy` — `HEAD` unchanged at `a0df98a`, tree
  clean before and after. The **Schedule Status: PAUSED** section is still
  unmodified: no dated lift note, so the owner-directed pause still applies.
  No new commits, no new evidence, no human verification results recorded
  since the previous check-in. Made no dashboard-code change and did not
  start any queued item, per the pause. Did **not** send a push
  notification — this is the third consecutive fire since the pause was
  recorded, nothing has changed since the last alert, and a repeat would be
  redundant noise per the routine's own notification guidance. **Exact next
  recommended task:** unchanged — none from this routine until the owner
  lifts the pause (dated note replacing the Schedule Status section); at
  that point resume from `DR-001` / the `CFG-003` host recovery status. The
  external recurring trigger firing three times against an explicit pause
  is itself the notable fact here — the owner disabling it (outside this
  repository) is the actual unblock, not further repository work. A future
  run should again re-fetch and re-read the top of this file first.
- **2026-08-30 21:35 UTC (this run) — third re-check, pause still in
  effect, no code change:** fetched `origin/ha-deploy` — `HEAD` unchanged at
  `e83920b` (the Regression Auditor's second clean-audit stamp, which itself
  recommended pausing this routine's schedule), tree clean before and after.
  The **Schedule Status: PAUSED** section is still unmodified: no dated lift
  note, so the owner-directed pause still applies. No new commits touch
  `dashboards/deez_smart_home.yaml`, `DASHBOARD_ISSUES.md` or
  `DASHBOARD_BACKLOG.md` since the last Main check-in — only two more
  documentation-only re-check commits and the Regression Auditor's clean
  sweep landed, and that audit independently reached the same conclusion
  this note would. No human verification results recorded. Made no
  dashboard-code change and did not start any queued item, per the pause.
  Did **not** send a push notification — this is now the fifth consecutive
  external-trigger fire since the pause was recorded (two Main
  re-check commits plus this one, plus the Regression Auditor's own two
  check-ins), nothing has changed since the original alert, and the
  Regression Auditor's latest audit reached the identical "recommend
  pausing this schedule" conclusion independently — a fourth notification
  would be redundant noise. **Exact next recommended task:** unchanged —
  none from this routine until the owner lifts the pause (dated note
  replacing the Schedule Status section); at that point resume from
  `DR-001` / the `CFG-003` host recovery status. Two independent routines
  (Main and the Regression Auditor) have now each recommended the owner
  disable the external recurring trigger outside this repository — that is
  the actual unblock, not further repository work. A future run should
  again re-fetch and re-read the top of this file first before doing
  anything else.
- **2026-08-30 22:36 UTC (this run) — fourth re-check, pause still in
  effect, no code change:** fetched `origin/ha-deploy` — `HEAD` unchanged at
  `37ce58e` (the previous Main check-in itself), tree clean before and
  after. The **Schedule Status: PAUSED** section is still unmodified: no
  dated lift note, so the owner-directed pause still applies. Zero commits
  of any kind have landed since the last check-in — not even another
  routine's audit — so there is no new evidence whatsoever to record this
  time, unlike the prior two re-checks which each had at least one other
  routine's commit to confirm against. Confirmed `CronList` (this session's
  own scheduler) has no jobs, ruling out this session as the source of the
  repeated firing — the external recurring trigger is account-level and
  outside this repository's or this session's reach, consistent with the
  pause section's own note that only the owner can disable it. Made no
  dashboard-code change and did not start any queued item, per the pause.
  Did **not** send a push notification — this is now the sixth-plus
  consecutive external-trigger fire since the pause was recorded, nothing
  has changed since the last alert, and a repeat would be redundant noise
  per the routine's own notification guidance. **Exact next recommended
  task:** unchanged — none from this routine until the owner lifts the
  pause (dated note replacing the Schedule Status section); at that point
  resume from `DR-001` / the `CFG-003` host recovery status. Given four
  consecutive no-op re-checks with zero new evidence between them, this
  routine recommends the owner disable the external recurring trigger (or
  extend its interval substantially) until ready to lift the pause, rather
  than continuing to fire this routine on an unchanged, already-paused
  state — a future run should still re-fetch and re-read the top of this
  file first, in case the pause has been lifted, but should expect to find
  the same result if it has not.
- **2026-08-30 23:35 UTC (this run) — fifth re-check, pause still in
  effect, no code change:** fetched `origin/ha-deploy` — `HEAD` unchanged at
  `987407b` (the previous Main check-in itself), tree clean before and
  after. **Schedule Status: PAUSED** is still unmodified — no dated lift
  note — so the owner-directed pause still applies. Zero commits of any
  kind have landed since the last check-in; re-read `DASHBOARD_ISSUES.md`'s
  Open section (still only `CFG-001`/`CFG-003`, both blocked on the owner
  and outside this repository's reach) and confirmed `LIVE_VERIFICATION_QUEUE.md`
  still shows 48 `PENDING` rows with no new `PASS`/`FAIL`/`PARTIAL` since the
  last check. No dashboard-code change made, no queued item started, per the
  pause. **Not** sending a push notification — this is now the seventh-plus
  consecutive external-trigger fire against an unchanged, already-paused
  state, the prior two runs already made the same "disable the external
  trigger" recommendation, and nothing has changed since either alert; a
  repeat would be redundant noise. **Exact next recommended task:**
  unchanged — none from this routine until the owner lifts the pause (a
  dated note replacing the Schedule Status section); at that point resume
  from `DR-001` / the `CFG-003` host recovery status. Repeating the standing
  recommendation once more for the record: the owner should disable or
  substantially extend the external recurring trigger until ready to lift
  the pause, since this file cannot stop the trigger itself from firing.
- **2026-08-31 (this run) — sixth re-check, pause still in effect, no code
  change:** fetched `origin/ha-deploy` — `HEAD` unchanged at `b2fa3b6` (the
  Regression Auditor's third consecutive clean audit), tree clean before and
  after. **Schedule Status: PAUSED** is still unmodified — no dated lift
  note — so the owner-directed pause still applies. Zero new commits beyond
  the Billing and Regression Auditor re-checks already recorded; `CFG-001`
  and `CFG-003` in `DASHBOARD_ISSUES.md` are unchanged (both `OPEN`/blocked
  on the owner), and `LIVE_VERIFICATION_QUEUE.md` still shows 48 `PENDING`
  rows. No dashboard-code change made, no queued item started, per the
  pause. **Not** sending a push notification — this is now the eighth-plus
  consecutive external-trigger fire against an unchanged, already-paused
  state with nothing new to report since the standing recommendation;
  another alert would be redundant noise per this routine's own
  notification guidance. **Exact next recommended task:** unchanged — none
  from this routine until the owner lifts the pause (a dated note replacing
  the Schedule Status section) or supplies new `CFG-003`/live-verification
  evidence; at that point resume from `DR-001` / the `CFG-003` host recovery
  status. The standing recommendation stands: the owner should disable or
  substantially extend the external recurring trigger until ready to lift
  the pause.
- **2026-08-31 01:35 UTC (this run) — seventh re-check, pause still in
  effect, no code change:** fetched `origin/ha-deploy` — `HEAD` unchanged at
  `cb189f3`, tree clean. **Schedule Status: PAUSED** still has no dated lift
  note. Zero new commits since the sixth re-check one hour prior; `CFG-001`
  and `CFG-003` unchanged (`OPEN`/blocked on the owner). No code change, no
  push notification (nothing new since the standing recommendation).
  **Exact next recommended task:** unchanged — none from this routine until
  the owner lifts the pause or supplies new evidence; resume from `DR-001` /
  `CFG-003` at that point. This schedule has now fired seven-plus times in a
  row against an unchanged paused state; a future run should not restate
  this note in full — a one-line HEAD-unchanged confirmation is sufficient
  until something actually changes.
- **2026-08-31 (this run) — eighth re-check, pause still in effect, no code
  change:** fetched `origin/ha-deploy` — HEAD `1b2d82f` (Billing's second
  re-check), tree clean. Pause note still undated-lifted; `CFG-001`/`CFG-003`
  unchanged. No new evidence, no push notification. Next recommended task
  unchanged: `DR-001` / `CFG-003` once the owner lifts the pause.

### Billing
- **2026-08-31 — Billing honors owner-directed pause, no code change:**
  fetched `origin/ha-deploy` (HEAD `d05075b`), tree clean before and after.
  Read `CLAUDE.md`, this file in full (including the `Schedule Status:
  PAUSED` notice added 2026-08-30 18:15 UTC), `DASHBOARD_ISSUES.md`,
  `DASHBOARD_BACKLOG.md` and `BILLING_PROGRESS.md`. This is the first
  Billing-routine run since the owner's pause directive (`7b077c3`); six
  Main re-checks and one Regression Auditor pass have confirmed it still
  holds, with no lift recorded anywhere in this file. Per the pause notice,
  performed no implementation, redesign, or push of any dashboard change,
  and did not start any new backlog/issue item. Confirmed by re-reading the
  active queue that nothing has changed since the last Billing run
  (`9f75c79`, pre-pause): `BILL-001`'s NMI/MIRN portion, `BILL-002`'s
  dashboard read side and `BILL-003` remain `BLOCKED`/`PARTIAL`/`PLANNED` on
  the same owner decisions, unmodified; `BILL-004`/`BILL-005` remain `FIXED
  — AWAITING LIVE VERIFICATION`, no new human verification result recorded
  for either; no other routine has touched billing files. No new evidence,
  defect, entity or requirement has appeared since the pre-pause clean sweep.
  No commit-worthy repository state changed other than this documentation
  entry itself.
- **Exact next recommended billing task:** none actionable while the pause
  holds. When the owner lifts it (see this file's pause notice for the lift
  procedure), resume in this order: (1) a live look at `BILL-004`'s ten
  guarded cards and `BILL-005`'s four re-styled titles in
  `LIVE_VERIFICATION_QUEUE.md`; (2) whichever `BILL-001` NMI/MIRN direction
  the owner has chosen (create the two `input_text` helpers, or approve
  removing the text); (3) the owner's `BILL-002` HA-exposure decision for
  `billing/history.json` (`billing/README.md` point 2); (4) `BILL-003`
  stays not-yet-actionable until (2) and (3) move, plus a design review
  before any Gmail/Drive read-only call.
- **Recommendation:** this is Billing's first no-op run under the pause, but
  the eighth consecutive no-code-change run project-wide since `7b077c3`
  with zero new evidence surfacing in any of them. Recommend the owner
  disable this schedule's external trigger (this file cannot do that) until
  ready to either supply a NMI/MIRN or `BILL-002` decision, report a live
  verification result, or explicitly lift the pause.
- **2026-08-30 (this run) — `BILL-005` fixed (title-card text-shadow guard)
  + `REG-014` closed (tracking backfill), no owner decision needed:** fetched
  `origin/ha-deploy` (HEAD `a8bf91c`), confirmed tree clean before and after.
  Read `CLAUDE.md`, this file in full, `DASHBOARD_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`, `BILLING_PROGRESS.md` and
  recent `ha-deploy` history before starting. Re-confirmed via
  `GetLiveContext` (`name: nmi`, `name: mirn`, `name: bill` — no matches)
  that `BILL-001`'s NMI/MIRN portion, `BILL-002`'s read side and `BILL-003`
  are all still genuinely `BLOCKED`/`PARTIAL` on owner decisions this routine
  cannot make (queue rule 4 excludes them from selection), and that no other
  routine had touched billing files since the last update. Rather than
  re-log another "still blocked" check, swept the live `bills`/`bill-*` YAML
  and this file's own tracking record directly for new, unblocked,
  actionable work — the same strategy that found `BILL-004` last run — and
  found two things: (1) grepping every one of the dashboard's 29
  `mushroom-title-card` instances for the standard `card_mod` text-shadow
  block showed exactly 4 missing it, all four Billing's own
  (`bill-car-insurance`, `bill-water`, `bill-council-rates`, `bill-rego`) —
  the only 4 of 29 dashboard-wide with no shadow guaranteeing title/subtitle
  contrast over the CasaRay night-sky background. Added the identical
  existing block already used by the other 25 (no new CSS invented; new
  ID `BILL-005`, S3). (2) `DASHBOARD_ISSUES.md`'s own open `REG-014` (filed
  by the Regression Auditor) correctly identified that `BILL-001`'s and
  `BILL-004`'s fixes, while properly tracked in `DASHBOARD_BACKLOG.md` and
  `LIVE_VERIFICATION_QUEUE.md`, were missing from `DASHBOARD_ISSUES.md`'s own
  "Fixed — awaiting live verification" table — backfilled both rows (without
  reproducing the NMI/MIRN digit values) and closed `REG-014` into the
  "Fixed — tracking only" table, citing "Billing Dashboard Upgrade, this run"
  rather than a self-referencing commit hash, matching the convention
  `REG-012` set. Also swept all six `bill-*` markdown/entities blocks for any
  other 5+ digit literal beyond the already-known, already-`BLOCKED`
  NMI/MIRN pair — found none (only tariff/rate figures, not identifiers), so
  no new privacy exposure exists. Re-verified all six `bill-*` subviews still
  carry a working "Back to Bills" control — no missing/broken billing
  back-nav case found, none rebuilt, per this routine's brief. `bash
  scripts/ha_validate.sh` passed clean (7/7) both before committing and
  after the stamp; 386 templates (unchanged — `BILL-005` is CSS only, no new
  template), 36/36 views resolve, no entity/view loss. Added `BILL-005` rows
  to `DASHBOARD_BACKLOG.md`'s "Awaiting live verification" table and
  `LIVE_VERIFICATION_QUEUE.md` (Bills & rooms, footer 43→44) in the same
  commit as the dashboard change, per the write-hygiene rule `REG-012`/
  `REG-014` both exist to prevent. Full narrative in `BILLING_PROGRESS.md`.
  Fetched again immediately before each push — no drift. Pushed to
  `ha-deploy` and `claude/ha-dashboard-upgrades-wui7ig` (`73813e8` content,
  `f95bb71` stamp).
- **Verification state:** `BILL-005` is `FIXED — AWAITING LIVE
  VERIFICATION` — repository validation only, nothing here can confirm what
  renders. `REG-014` needed no live check — it is a tracking-file
  completeness fix, directly verifiable by inspection.
- **Blockers (unchanged by this run):** `BILL-001`'s NMI/MIRN portion needs
  the owner to either create `input_text.elec_nmi`/`input_text.gas_mirn` or
  approve removing that text from the cards. `BILL-002`'s dashboard read
  side needs the owner to pick an HA-exposure mechanism for
  `billing/history.json`. `BILL-003` stays blocked on both, plus a design
  review before any Gmail/Drive read-only calls are made — none were made
  this run.
- **Exact next recommended billing task:** (1) a live look at `BILL-005`'s
  four re-styled titles (or `BILL-004`'s ten guarded cards, still pending
  from last run); (2) if the owner has looked at `BILL-001`, act on
  whichever NMI/MIRN direction they choose; (3) otherwise, react to
  `BILL-002`'s open read-side question in `billing/README.md`; (4)
  `BILL-003` stays not-yet-actionable until (2) and (3) move. See
  `BILLING_PROGRESS.md` → "Exact next billing task" for the fuller version.
- **Queue:** `BILL-001` (P1, partial/blocked) → `BILL-002` (P2, partial) →
  `BILL-003` (P2, blocked). All three remain blocked-or-partial pending an
  owner decision. This run found and fixed unblocked, unscored `BILL-004`
  (S3/S4 raw-interpolation guard, see below) instead of re-deriving the same
  blocker notes again.
- **2026-08-30 (this run) — clean verification sweep, no code change:**
  fetched `origin/ha-deploy` — `HEAD` unchanged at `c9429b1`, tree clean
  before and after. Read `CLAUDE.md`, `PROJECT_STATE.md` in full,
  `BILLING_PROGRESS.md`, `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md` and
  recent `ha-deploy` history before starting. Re-confirmed via
  `GetLiveContext` (`name: nmi`, `name: mirn`, `name: bill` — no matches)
  that `BILL-001`'s NMI/MIRN portion, `BILL-002`'s read side and `BILL-003`
  are all still genuinely blocked on owner decisions this routine cannot
  make, unchanged since the last run, and that no other routine had touched
  billing files since. Rather than only re-log the standing blockers, read
  every one of the seven billing views (`bills`, `bill-electricity`,
  `bill-gas`, `bill-car-insurance`, `bill-water`, `bill-council-rates`,
  `bill-rego`) end to end line by line — not just grepped — to check
  whether anything survived the `BILL-004`/`BILL-005` sweeps. Confirmed: all
  landing tiles and subview status cards already guard against
  `unavailable`/`unknown`/`none`; all six subviews still carry a working
  "Back to Bills" chip; every paid/unpaid `icon_color` and primary-text
  branch already fails cautious (orange/"Payment Outstanding"), never a
  reassuring green, when its `input_boolean` is unavailable — no false-safe
  instance found. Ran a fresh privacy sweep for any 5+ digit literal across
  the whole dashboard file (not just the `bill-*` blocks) — the only
  matches are the already-tracked, already-`BLOCKED` NMI
  (`bill-electricity`) and MIRN (`bill-gas`) literals; no new identifier
  exposure found. Also re-checked `billing/schema.json` (unchanged, valid)
  and `billing/history.json` (still `[]`, nothing fabricated). `bash
  scripts/ha_validate.sh` passes clean (7/7, 386 templates, 36/36 views, no
  drift). **No fix made — nothing found to fix.** This is the third
  consecutive billing run to sweep for new unblocked work (after
  `BILL-004` and `BILL-005`), and the first to come back clean on a full
  line-by-line read rather than finding something — the coded-fix surface
  reachable without an owner decision now appears genuinely exhausted, not
  merely unattempted. No dashboard/theme/billing-storage commit this run
  (documentation-only update to this section and `BILLING_PROGRESS.md`).
- **Exact next recommended billing task (unchanged, now confirmed rather
  than assumed):** (1) the owner decides `BILL-001`'s NMI/MIRN direction —
  create `input_text.elec_nmi`/`input_text.gas_mirn`, or approve removing
  the text from the two cards; (2) the owner picks `BILL-002`'s
  HA-exposure mechanism for `billing/history.json` (template/RESTful sensor
  vs. ingestion into HA statistics — see `billing/README.md` point 2); (3)
  `BILL-003` stays not-yet-actionable until (1) and (2) move, plus a design
  review before any Gmail/Drive read-only call is made — none were made
  this run, there being nothing safe yet for ingestion to write to. A
  future billing run should check whether either owner decision has landed
  before repeating this run's now-clean full-file sweep.
- **2026-08-30 (this run) — `BILL-004` fixed, no owner decision needed:**
  fetched `origin/ha-deploy` (HEAD `0081429`), confirmed tree clean before and
  after. Read `CLAUDE.md`, `PROJECT_STATE.md` in full, `DASHBOARD_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md`, `BILLING_PROGRESS.md` and
  recent `ha-deploy` history before starting. Confirmed `BILL-001`'s NMI/MIRN
  portion, `BILL-002`'s read side and `BILL-003` are all still genuinely
  `BLOCKED`/`PARTIAL` on owner decisions this routine cannot make (queue rule
  4 excludes them from selection), and that no other routine had touched
  billing files since the last update — so rather than log another
  "still blocked" re-check, inspected the live `bills`/`bill-*` YAML directly
  for new, actionable, unblocked work. Found ten `custom:mushroom-template-card`
  secondary fields (six on the `bills` landing tiles, four on `bill-*`
  subview status cards) printing a raw `states(...)` value with no guard —
  the same raw-interpolation class `UI-006`/`UI-030`/`UI-031` fixed elsewhere,
  never swept here because `bills`/`bill-*` is Billing-owned and explicitly
  out of scope for Main. Guarded all ten against `unavailable`/`unknown`/
  `none`, reusing only entities already referenced in the same views (none
  invented) and the existing "Not entered" / bilingual-fallback conventions
  already established by `BILL-001` and `UI-030`/`UI-031`. Did **not** touch
  the hardcoded NMI/MIRN literals (still `BILL-001`'s own `BLOCKED` scope) or
  any protected path. `bash scripts/ha_validate.sh` passed clean (7/7) both
  before committing and after the stamp; 386 templates (unchanged),
  36/36 views resolve, no entity/view loss. Added a `BILL-004` row to
  `LIVE_VERIFICATION_QUEUE.md` (Bills & rooms, footer 43→44) and to
  `DASHBOARD_BACKLOG.md`'s "Awaiting live verification" table in the same
  commit as the dashboard change, per the write-hygiene rule `REG-012`
  exists to prevent. Full narrative in `BILLING_PROGRESS.md`. Fetched again
  immediately before pushing — no drift. Pushed to `ha-deploy` and
  `claude/ha-dashboard-upgrades-wui7ig`.
- **Verification state:** `BILL-004` is `FIXED — AWAITING LIVE VERIFICATION`
  — repository validation only, nothing here can confirm what renders.
- **Blockers (unchanged by this run):** `BILL-001`'s NMI/MIRN portion needs
  the owner to either create `input_text.elec_nmi`/`input_text.gas_mirn` or
  approve removing that text from the cards. `BILL-002`'s dashboard read side
  needs the owner to pick an HA-exposure mechanism for `billing/history.json`.
  `BILL-003` stays blocked on both, plus a design review before any Gmail/
  Drive read-only calls are made — none were made this run; `BILL-004` did
  not need them.
- **Exact next recommended billing task:** (1) a live look at `BILL-004`'s
  ten guarded cards (or disable one `input_number`/`sensor` to confirm the
  guard fires); (2) if the owner has looked at `BILL-001`, act on whichever
  NMI/MIRN direction they choose; (3) otherwise, react to `BILL-002`'s open
  read-side question in `billing/README.md`; (4) `BILL-003` stays not-yet-
  actionable until (2) and (3) move. See `BILLING_PROGRESS.md` → "Exact next
  billing task" for the fuller version.
- **2026-08-30 (this run) — `BILL-002` storage layer scaffolded
  (`5147eb0`/`ff25626`), no code change to any dashboard YAML:** re-read
  `CLAUDE.md`, `PROJECT_STATE.md`, `BILLING_PROGRESS.md`,
  `DASHBOARD_ISSUES.md`/`DASHBOARD_BACKLOG.md`'s `BILL-*` rows and recent
  `ha-deploy` history before starting; confirmed `HEAD` matched
  `origin/ha-deploy` (`574b16c`) and the tree was clean both before and
  before committing. Confirmed `BILL-001` and `BILL-002`'s dashboard read
  side are both genuinely `BLOCKED` on owner decisions (queue rule 4
  excludes them from selection) and that no other routine had touched
  billing files or `PROJECT_STATE.md` since the last update. Built the part
  of `BILL-002`'s proposal that does **not** depend on the owner's
  read-side decision: a new `billing/` directory with `schema.json` (JSON
  Schema for one bill record — provider, utility type, period, issue/due
  date, usage, original/pre-discount cost, discounts/credits, final
  amount, user-controlled `payment_status`, and a `source` traceability
  object) and `history.json` initialized to `[]` — no record fabricated or
  backfilled. Also redacted the literal NMI/MIRN digit values
  `BILLING_PROGRESS.md` had been carrying in its own `BILL-001` narrative,
  per the P1 privacy requirement against reproducing sensitive billing
  identifiers in tracking files — the dashboard YAML itself is unchanged
  (still `BLOCKED`, see `BILL-001`); only this routine's own tracking
  document's copy of the digits was removed. Re-verified this run that all
  six `bill-*` subviews already carry a working, consistent "Back to
  Bills" control (`/deez-smart-home/bills`) — no missing/broken billing
  back-nav case found, so none rebuilt, per this routine's brief. Also
  swept the repo for the NMI/MIRN digit values outside the dashboard YAML
  and this file's own already-fixed copy — found none elsewhere. Validated:
  `bash scripts/ha_validate.sh` passed clean (7/7) both before committing
  and after the stamp; both new JSON files parse; no protected path
  touched, no credential-shaped literal introduced, no dashboard YAML
  diff. Pushed to `ha-deploy` and `claude/ha-dashboard-upgrades-wui7ig`
  (`5147eb0` content, `ff25626` stamp) after re-fetching immediately before
  each push — no drift either time. `BILL-002` moves `PLANNED` → `PARTIAL`
  in `DASHBOARD_BACKLOG.md`.
- **Verification state:** nothing here needs a `LIVE_VERIFICATION_QUEUE.md`
  row — no dashboard YAML changed, so there is nothing new to render or
  check on the iPad. The `billing/` files themselves are validated only as
  well-formed JSON; they are not yet exercised by anything (nothing writes
  to `history.json`, nothing reads it), so "scaffolded" should not be
  read as "working."
- **Blockers (unchanged by this run, still genuine):** `BILL-001`'s
  NMI/MIRN portion needs the owner to either create
  `input_text.elec_nmi`/`input_text.gas_mirn` or approve removing that text
  from the cards. `BILL-002`'s dashboard read side needs the owner to pick
  an HA-exposure mechanism for `billing/history.json` (template/RESTful
  sensor vs. ingestion into HA statistics — see `billing/README.md`).
  `BILL-003` stays blocked on both plus needing a design review before any
  Gmail/Drive read-only calls are made. None of these can be resolved by
  guessing; recorded as blockers rather than guessed at, per this routine's
  brief.
- **Exact next recommended billing task:** (1) if the owner has looked at
  `BILL-001`, act on whichever NMI/MIRN direction they choose; (2)
  otherwise, react to `BILL-002`'s open read-side question — once an
  exposure mechanism is picked, the next batch can wire a `bills-history`
  subview against `billing/history.json`'s real (if still empty) shape
  instead of guessing at one; (3) `BILL-003` remains not-yet-actionable
  until (1) and (2) move — no Gmail/Drive calls should be made before then.
  See `BILLING_PROGRESS.md` → "Exact next billing task" for the fuller
  version of this same pointer.
- **2026-08-30 — `BILL-001` account-number portion fixed:** `bill-electricity`
  and `bill-gas` markdown blocks now render
  `input_text.elec_account_number` / `..._gas_account_number` (guarded,
  already-referenced entities — not invented) instead of the literal account
  numbers. **NMI and MIRN remain hardcoded** — no helper entity exists for
  either and one must not be invented; needs an owner decision (create the
  helpers, or approve removing the text). `BILL-001` is now `BLOCKED` on that
  decision and excluded from autonomous selection. Commit: `23c0301`.
  Full detail in `BILLING_PROGRESS.md`.
- Confirmed via `GetLiveContext` this run: no bill-related entity is exposed
  to Assist (`name: bill` → no match) — billing figures stay `CODE_VALID` at
  best, unconfirmable live from here.
- Six bill subviews exist, one section / one column each, back chip to
  `bills`; layout reviewed under `9b28fdb`, no change needed.
- **`BILL-002` scoped, not implemented:** no `bills.json`/`paid_state.json`/
  `meter_board` architecture exists anywhere in this repository — confirmed
  by inspection this run, contrary to what this routine's task brief
  assumed. Wrote a storage-architecture proposal in `BILLING_PROGRESS.md`
  (structured `billing/history.json`, populated manually until `BILL-003`
  ingestion exists). The real blocker is architectural, not effort: Lovelace
  cannot read an arbitrary repository JSON file directly, so an HA-side
  exposure mechanism (template/RESTful sensor, or ingestion into HA
  statistics) needs an owner decision before any dashboard implementation.
- **`BILL-003`** unchanged: blocked on both `BILL-001`'s remaining scope and
  `BILL-002`'s storage decision. No Gmail/Drive calls made this run — nothing
  safe yet for ingestion to write to.
- Back navigation: per this file's own record, already complete and needs a
  live look only; no rebuild attempted this run, consistent with this
  routine's brief.
- **Next task:** see `BILLING_PROGRESS.md` → "Exact next billing task".
- **2026-08-31 02:13 UTC (this run) — second re-check, pause still in
  effect, no code change:** fetched `origin/ha-deploy` (HEAD `0243fd1`),
  tree clean before and after. Re-read this file's `Schedule Status: PAUSED`
  notice in full — unmodified, no dated lift note, so the owner-directed
  pause still applies. Commits since the last Billing entry (`89313e6`) are
  `b2fa3b6`, `cb189f3`, `0243fd1` — a regression-audit pass and two Main
  re-checks, none touching billing files. `DASHBOARD_ISSUES.md` and
  `DASHBOARD_BACKLOG.md` `BILL-*` rows are unchanged from the prior run:
  `BILL-001` NMI/MIRN and `BILL-002`'s read-side exposure decision remain
  `BLOCKED` on the same owner decisions, `BILL-003` remains blocked on both.
  No new evidence, defect, entity or requirement for billing has appeared.
  Made no dashboard-code change and did not start any queued item, per the
  pause. **Not** sending a push notification — this is now the tenth-plus
  consecutive no-code-change run project-wide since `7b077c3` with nothing
  new to report. **Recommendation unchanged:** the owner should disable
  this schedule's external trigger (this file cannot do that) until ready
  to supply a `BILL-001`/`BILL-002` decision, report a live verification
  result, or explicitly lift the pause. A future run should keep this to a
  one-line HEAD-unchanged confirmation, per Main's own note, rather than
  restating this in full again.

### Regression
- Baseline audit `3116495` against `7f304ad`: REG-001..006, **all six now
  fixed** and awaiting live verification. Evidence in `DASHBOARD_ISSUES.md`;
  full audit detail in `archive/DASHBOARD_ISSUES_ARCHIVE.md`.
- **2026-08-30 audit (this run) — scope `3116495..ea7289f` (45 commits):**
  read every commit touching `dashboards/deez_smart_home.yaml` or
  `themes/deez_your_name.yaml` in range (`b5eee22`, `9926233`, `dff00f3`,
  `b058006`, `d592692`, `23c0301`, `691689a`) plus the merge commits that
  crossed those files (`a0b05ce`, `5dca7f0`) to check for a bad conflict
  resolution. Each diffed cleanly against its stated purpose in
  `DASHBOARD_ISSUES.md`/`DASHBOARD_PROGRESS.md`; no routine undid another's
  work, no cross-ownership boundary violation found (Billing's `23c0301`
  touched only `bill-electricity`/`bill-gas` plus its own `PROJECT_STATE.md`
  section; Main's batches stayed general-dashboard). REG-008's
  `ipad-command-center`→`cameras` self-correction verified against the file
  (the chip is at L1595–1601, inside the `cameras` view, path confirmed by
  line position). The still-hardcoded NMI/MIRN in `bill-electricity`/
  `bill-gas` was checked against the privacy-flagging brief: it is already
  correctly tracked as `BILL-001`'s `BLOCKED` remainder in
  `DASHBOARD_BACKLOG.md` with a documented reason (no helper entity exists,
  `!secret` does not work in storage mode, inventing an entity is
  forbidden) — not re-logged here, per "do not manufacture issues."
- **New issue: `REG-012`** (MED) — `LIVE_VERIFICATION_QUEUE.md` upkeep fell
  behind the REG-007..011/UI-030 batch: `691689a` (UI-030) added no queue
  row at all, and the queue's "N checks pending" footer was never
  incremented for the five REG-007..011 rows (`b058006`/`d592692`), then
  `23c0301` bumped 33→34 accounting only for its own new `BILL-001` row.
  Actual pending rows counted directly from the table: **39**, not 34. Full
  evidence and suspected commits in `DASHBOARD_ISSUES.md`. Not self-fixed —
  advisory only; recommended owner is Main (who pushed the under-tracked
  batch) or the Daily Project Coordinator.
- **Resolved/stale issues identified:** none. REG-001..011, UI-027, UI-030
  and BILL-001's account-number portion remain correctly
  `FIXED — AWAITING LIVE VERIFICATION` / `LIVE_VERIFICATION_REQUIRED` per
  repository evidence — no premature `VERIFIED` claims found anywhere in
  `DASHBOARD_ISSUES.md`, `DASHBOARD_BACKLOG.md` or this file.
- **Cross-routine conflicts:** none found in this range. No routine
  overwrote another's completed work; no billing change outside Billing's
  ownership; no unrelated dashboard edit from Billing.
- **Verification requirements:** none of REG-001..011/UI-027/UI-030/BILL-001
  can become `LIVE_VERIFIED` from this environment — human check only, per
  `LIVE_VERIFICATION_QUEUE.md`. Existing Back/previous-page navigation is
  substantially implemented (35/36 views, parent-targeted) and was not
  touched by any commit in this audit range; treated as
  `LIVE_VERIFICATION_REQUIRED` only, no new navigation regression opened —
  no repository evidence of a defect surfaced this run.
- **Next recommended audit focus:** once `REG-012` is corrected, re-check
  that future batches add both a queue row and an updated pending-count in
  the same commit as the dashboard fix (write-hygiene gap, not a one-off);
  otherwise the next audit's default scope is `ea7289f..HEAD` for whatever
  Main/Billing push next, plus a fresh look at `UI-011` (Energy — Total
  Solar) if it is ever coded, since it remains the only open dashboard
  (non-tracking) issue.
- Auditor is advisory: findings queue for Main, never self-implemented.
- **2026-08-30 audit (this run) — scope `ea7289f..HEAD` (15 commits,
  `50fc733`):** fetched `origin/ha-deploy`, confirmed local matched remote
  (`50fc733`) with a clean tree, no drift before writing. Of the 15 commits
  in range, only two touch `dashboards/deez_smart_home.yaml`: `ccfb0c8`
  (Main — UI-031/REG-013) and `d570a82` (Billing — BILL-004); the rest are
  docs-only stamps/confirmation notes or Billing's non-dashboard
  `billing/` storage scaffold (`5147eb0`/`ff25626`). Diffed both dashboard
  commits directly against the view-boundary line map (`grep -n '^  path:'`)
  rather than trusting the commit messages alone: `ccfb0c8`'s four hunks all
  fall inside `home` (L9–560) and `light-ray-bedroom`/`lighting-modes`
  (L3354–3586) — no billing view touched. `d570a82`'s ten hunks all fall
  inside `bills` (L4007–4178) and `bill-car-insurance`/`bill-water`/
  `bill-council-rates`/`bill-rego` (L4374–end) — no non-billing view
  touched. **No cross-routine boundary violation, no undone work, no
  billing change by Main, no unrelated change by Billing.** Both commits'
  narratives in `DASHBOARD_ISSUES.md`/`DASHBOARD_BACKLOG.md`/
  `BILLING_PROGRESS.md` match their actual diffs. Re-verified `LIVE_VERIFICATION_QUEUE.md`'s
  "44 checks pending" footer against an actual row count (`grep -c '|
  PENDING |'` = 44) — accurate this time, no REG-012-class drift.
  Re-checked the billing-privacy brief directly against the live YAML: the
  NMI/MIRN literals at `bill-electricity`/`bill-gas` are still hardcoded
  (confirmed present, digits not reproduced here) and remain correctly
  tracked as `BILL-001`'s `BLOCKED` remainder with a documented reason — not
  re-logged, per "do not manufacture issues." `billing/history.json` is
  still `[]` and `BILLING_PROGRESS.md`'s own NMI/MIRN digits remain redacted
  from the previous run — no new privacy exposure found.
- **New issue: `REG-014`** (LOW) — `DASHBOARD_ISSUES.md` describes itself as
  the authoritative bug record for `dashboards/deez_smart_home.yaml`, but
  neither `BILL-001`'s account-number fix (`23c0301`) nor `BILL-004`
  (`d570a82`) — both genuine fixes to that file, same raw-interpolation
  class already logged here for Main's `UI-030`/`UI-031` — appear in it at
  all, even though both are correctly present in `DASHBOARD_BACKLOG.md` and
  `LIVE_VERIFICATION_QUEUE.md`. Tracking-completeness gap only; nothing is
  lost, unverifiable, or wrongly marked complete. Full evidence and
  recommended action in `DASHBOARD_ISSUES.md`'s Open table. Not self-fixed —
  recommended owner is Billing (who authored both fixes) or the Daily
  Project Coordinator.
- **Resolved/stale issues identified this run:** none.
- **Cross-routine conflicts this run:** none.
- **Verification requirements:** unchanged — `UI-011` remains the only open
  non-tracking issue; `REG-014` is tracking-only and has no live-dashboard
  component.
- **Next recommended audit focus:** once `REG-014` is corrected (or the
  `DASHBOARD_ISSUES.md` scope is deliberately narrowed to exclude
  `BILL-*`), the next audit's default scope is `50fc733..HEAD` for whatever
  Main/Billing push next. `UI-011` (Energy — Total Solar) remains worth a
  fresh look if it is ever coded.
- **2026-08-30 audit (this run) — scope `50fc733..HEAD` (11 commits,
  `291a976`):** fetched `origin/ha-deploy`, confirmed local matched remote
  with a clean tree before writing. Of the 11 commits in range, only one
  touches `dashboards/deez_smart_home.yaml`: `73813e8` (Billing —
  `BILL-005`, backfilling `REG-014`'s tracking gap in the same commit). The
  other ten are docs-only: `b8d7807`/`ca1fa32` (prior Regression Auditor
  audit + stamp), `afef82c`/`401e904` (`UI-011` `PASS` reconciliation +
  `CFG-001`/`CFG-002` filing), `7df2f5b` (verification-syntax doc cleanup),
  `7b42918`/`a8bf91c` (Main's sixth/seventh clean sweeps, no code),
  `f95bb71`/`28b1caf` (Billing's `BILL-005` stamp + coordination note), and
  `291a976` (Main's eighth clean sweep, no code). Diffed `73813e8` directly:
  all four hunks add the identical existing `card_mod` text-shadow block to
  `bill-car-insurance`/`bill-water`/`bill-council-rates`/`bill-rego` title
  cards (L4380–4619 region) — CSS-only, no template/entity/navigation
  change, confined entirely to Billing's own four subviews. **No
  cross-routine boundary violation, no undone work, no billing change by
  Main, no unrelated change by Billing.** Cross-checked the commit's own
  narrative against `DASHBOARD_ISSUES.md` (`BILL-005` row present, correct
  commit, NMI/MIRN digits not reproduced; `REG-014` correctly closed into
  "Fixed — tracking only") and `DASHBOARD_BACKLOG.md` ("Awaiting live
  verification" row present, correct commit) — both match, no drift this
  time (unlike the REG-012/REG-014 gaps the last two audits caught).
  Re-verified `LIVE_VERIFICATION_QUEUE.md`'s "44 checks pending" footer
  against an actual row count (`grep -c '| PENDING |'` = 44) — accurate.
  Re-checked the billing-privacy brief directly against the live YAML: the
  NMI/MIRN literals at `bill-electricity`/`bill-gas` are still hardcoded
  (confirmed present, digits not reproduced here) and remain correctly
  tracked as `BILL-001`'s `BLOCKED` remainder with a documented reason — not
  re-logged, per "do not manufacture issues." No new repository-visible
  billing identifier found elsewhere. Re-checked Back/previous-page
  navigation per this run's brief: untouched by any commit in range: still
  `LIVE_VERIFICATION_REQUIRED` only, no repository evidence of a new defect,
  so no new navigation regression opened.
- **New issues this run:** none — nothing to file.
- **Resolved/stale issues identified this run:** none newly found; `REG-012`
  and `REG-014` (closed by prior runs) remain correctly closed, no
  regression of either.
- **Cross-routine conflicts this run:** none.
- **Verification requirements:** unchanged — `CFG-001`/`CFG-002` are Home
  Assistant configuration defects outside this repository, correctly
  excluded from the verification queue; `BILL-005` is `FIXED — AWAITING
  LIVE VERIFICATION` and already queued.
- **Next recommended audit focus:** this run found no actionable
  regression — a clean audit. Next default scope is `291a976..HEAD` for
  whatever Main/Billing push next. Worth a specific look next time: (1)
  whether `BILL-001`'s NMI/MIRN or `BILL-002`'s HA-exposure decision has
  moved, since either would open new billing-code surface to audit; (2)
  `DR-001` if it ever gets a design brief and code; (3) whether any human
  verification result (`PASS`/`FAIL`/`PARTIAL`) has finally landed in
  `LIVE_VERIFICATION_QUEUE.md` beyond `UI-011`, since a `FAIL`/`PARTIAL`
  would need reconciliation against the right stable ID.
- **2026-08-30 audit (this run) — scope `291a976..HEAD` (27 commits,
  `6d951dc`):** fetched `origin/ha-deploy`, confirmed local matched remote
  with a clean tree before writing. **Read the owner-directive pause section
  at the top of this file first**, per this run's own instruction to treat
  it as authoritative; honored it as an advisory-only run — read and file,
  no implementation. Of the 27 commits in range, only three touch
  `dashboards/deez_smart_home.yaml`: `a183d5f`, `0fec9bb` and `2183177`, all
  three Main's own `UI-032` attempts (feat → fix → diagnostic probe), diffed
  directly against the view-boundary line map. All three stay entirely
  inside the `home` view's Active Now strip (`sections[1]`); no other view
  touched, no billing surface touched. **No cross-routine boundary
  violation, no undone work, no billing change by Main, no unrelated change
  by Billing.** The repeated `UI-032` rewrites are not
  reimplementation-of-already-completed-work: each carries a distinct,
  falsified hypothesis (consolidated `condition: or` → per-entity flat
  conditions → an unconditional probe) and the commit trail says so
  explicitly — this is live debugging of a still-open item, not churn on a
  closed one. Independently re-derived the `CFG-003` root-cause chain
  (`d200945` → `ec10656`) against the raw evidence rather than trusting the
  prose: `git merge-base 26c3b14 HEAD` in this worktree returns nothing,
  confirming `ha-deploy`'s current history and the deploy script's last
  candidate commit are unrelated roots — the disjoint-history diagnosis
  holds. `CFG-003`'s `DASHBOARD_ISSUES.md` row is accurately `CONFIRMED`
  (owner-verified `sensor.front_door_battery` absent live), not prematurely
  closed, and already carries the recovery procedure — nothing to add.
  Re-checked `DASHBOARD_ISSUES.md`'s Open table and `UI-032`'s own entry
  against the file: both correctly state `BLOCKED on CFG-003`, matching the
  three commits' own record. Re-verified the three post-pause "no code
  change" check-ins (`2b71373`, `a0df98a`, `6d951dc`) each touch only
  `PROJECT_STATE.md` — confirmed no dashboard/theme/billing file in any of
  their diffs, so the pause is being honored in practice, not just in
  prose. No repository-visible billing identifier found in range (`9f75c79`
  billing sweep is docs-only, no new digits). Back/previous-page navigation
  untouched by any commit in range: still `LIVE_VERIFICATION_REQUIRED` only,
  no new regression opened.
- **New issues this run:** none.
- **Resolved/stale issues identified this run:** none; `CFG-003` correctly
  remains open pending owner recovery action, not marked resolved anywhere.
- **Cross-routine conflicts this run:** none.
- **Verification requirements:** unchanged — every `FIXED — AWAITING LIVE
  VERIFICATION` row remains unproven at the delivery step per `CFG-003`
  until the owner's recovery procedure (`DEPLOYMENT_BLOCKERS.md`) runs and
  the host clone is confirmed to fast-forward. `UI-032` itself cannot be
  live-verified while blocked.
- **Two consecutive clean audits now** (this run and the prior
  `50fc733..HEAD` run): no actionable regression found in either. Combined
  with the owner's explicit cross-routine pause already in effect above,
  **recommend the external schedule for this routine be paused** alongside
  the others until the pause is lifted or `CFG-003` produces new
  dashboard-facing evidence to audit — a fresh audit pass adds no value
  while implementation itself is halted.
- **Next recommended audit focus:** once the owner lifts the pause and/or
  `CFG-003` is recovered, resume at `6d951dc..HEAD` for whatever Main/Billing
  push next; re-check `UI-032`'s eventual live result first, since it is the
  only item with three prior live `FAIL`s on record.
- **2026-08-31 audit (this run) — scope `e83920b..HEAD` (4 commits,
  `89313e6`):** fetched `origin/ha-deploy`, confirmed local matched remote
  with a clean tree before writing. All four commits in range
  (`37ce58e`, `987407b`, `d05075b` — Main's third/fourth/fifth pause
  re-checks — and `89313e6` — Billing's pause acknowledgement) are
  docs-only "no code change" entries; confirmed directly via
  `git diff --stat e83920b HEAD` that only `PROJECT_STATE.md` and
  `BILLING_PROGRESS.md` changed (133 insertions, 0 deletions) — no
  `dashboards/deez_smart_home.yaml`, theme, script or `billing/` file
  touched by any of them. **No cross-routine boundary violation, no
  undone work, no billing change by Main, no unrelated change by
  Billing** — there is no dashboard diff in range to violate a boundary
  with. Owner-directed pause (top of this file) remains in effect and is
  being honored in practice by every routine, not just in prose. No new
  repository-visible billing identifier introduced. `CFG-003` remains
  open, correctly `BLOCKED` pending the owner's recovery procedure;
  `UI-032` remains correctly blocked on it. Back/previous-page navigation
  untouched in range: still `LIVE_VERIFICATION_REQUIRED` only, no new
  regression opened.
- **New issues this run:** none.
- **Resolved/stale issues identified this run:** none; no tracking file
  disagrees with repository state found this run.
- **Cross-routine conflicts this run:** none.
- **Verification requirements:** unchanged.
- **Three consecutive clean/no-op audits now** (`50fc733..HEAD`,
  `291a976..HEAD`, and this run), spanning zero dashboard-code commits
  since the pause took effect. The prior run's recommendation to pause
  this routine's external schedule stands and is reinforced, not
  superseded — nothing has changed to warrant lifting it. Continuing to
  fire this schedule while the owner's pause holds produces audits of
  docs-only "no code change" commits with no actionable content;
  recommend the owner disable the external trigger until the pause is
  lifted or `CFG-003` produces new dashboard-facing evidence.
- **Next recommended audit focus:** unchanged from the prior run — once
  the owner lifts the pause and/or `CFG-003` is recovered, resume at
  `89313e6..HEAD` for whatever Main/Billing push next; re-check
  `UI-032`'s eventual live result first.
- **2026-08-31 audit (this run) — scope `89313e6..HEAD` (5 commits,
  `fd9b925`):** fetched `origin/ha-deploy`, confirmed local matched remote
  with a clean tree before writing. `git diff --stat 89313e6 fd9b925` shows
  exactly one file touched across all five commits — `PROJECT_STATE.md`,
  94 insertions, 0 deletions — confirmed directly rather than trusted from
  commit messages. All five (`b2fa3b6` — prior Regression Auditor audit +
  pause-schedule recommendation, `cb189f3`/`0243fd1`/`fd9b925` — Main's
  sixth/seventh/eighth pause re-checks, `1b2d82f` — Billing's second pause
  re-check) are docs-only "no code change" entries. **No
  `dashboards/deez_smart_home.yaml`, theme, script or `billing/` file
  touched by any commit in range — no cross-routine boundary violation, no
  undone work, no billing change by Main, no unrelated change by Billing,
  because there is no dashboard diff in range to violate a boundary with.**
  Owner-directed pause remains in effect and is being honored in practice by
  every routine, not just in prose. Re-read `DASHBOARD_ISSUES.md`'s Open
  table directly: `CFG-001`, `CFG-002`, `CFG-003` remain the only open
  items, all three correctly `OPEN`/`BLOCKED` on owner diagnosis, none
  mismarked complete, none reproducing a sensitive billing value. No new
  repository-visible billing identifier introduced anywhere in range.
  Back/previous-page navigation untouched in range: still
  `LIVE_VERIFICATION_REQUIRED` only, no new regression opened — consistent
  with this routine's standing brief to treat it as substantially
  implemented absent a specific new defect.
- **New issues this run:** none — nothing to file.
- **Resolved/stale issues identified this run:** none; no tracking file
  disagrees with repository state found this run.
- **Cross-routine conflicts this run:** none.
- **Verification requirements:** unchanged.
- **Four consecutive clean/no-op audits now** (`50fc733..HEAD`,
  `291a976..HEAD`, `e83920b..HEAD`, and this run), plus three further
  Main/Billing pause re-checks landing in between with no dashboard-code
  content of their own. Nothing has changed since the pause took effect
  that this routine can act on: still zero dashboard-code commits, still
  the same three owner-blocked issues, still no new evidence. The prior
  two runs' recommendation to disable this routine's external schedule
  stands, is reinforced again, and has not yet been acted on by the
  scheduler — this run fired despite it. Repeating that recommendation a
  further time would not change the underlying fact, so this entry states
  it once more and stops: **pause this schedule until the owner lifts the
  cross-routine pause or `CFG-003` produces new dashboard-facing
  evidence.**
- **Next recommended audit focus:** unchanged — once the owner lifts the
  pause and/or `CFG-003` is recovered, resume at `fd9b925..HEAD` for
  whatever Main/Billing push next; re-check `UI-032`'s eventual live
  result first.

### Entity Scout
- File findings in `DASHBOARD_BACKLOG.md` as evidence-based items.
- Entity registry is unavailable here; entity existence is inferred from the
  imported live dashboard and never confirmed. Record findings as claims.
- **2026-08-30 — `UI-032` implemented and out of the active queue.** The owner
  supplied verified entity IDs for all six battery sensors, RingRing included,
  which is exactly the unblock the sweep below said was needed. Built on those
  IDs only; the stale `_battery_2` duplicate the sweep warned about was
  excluded by name. Full record in `DASHBOARD_ISSUES.md`.
- **2026-08-30 — first live `sensor`-domain sweep (advisory, no YAML
  touched).** Ran `GetLiveContext` over the `sensor` domain while verifying
  `UI-011` — the first live entity data any run has had. Two results:
  - **Unit and scale cross-check: clean.** Every one of the 34 `sensor.`
    references in the dashboard that could be matched to a live entity
    handles its unit correctly. Specifically confirmed: the four Primo
    sensors report **Wh** and every card that reads them divides by 1000
    (`Solar Today`, `Solar Year`, `Total Solar`); the two P110M plugs report
    **W** for `current_consumption` and **kWh** for `today_s_consumption`,
    and both cards label them that way; `sensor_group_illuminance` is lx and
    the Aqara shade battery is %. No sentinel fallbacks remain
    (`float(100)`/`float(9999)`: zero hits). A prior suspicion that motion
    and door references sat in the wrong domain was **checked and is false**
    — all 8 are correctly `binary_sensor.`, the apparent hits were `sensor.`
    matching the tail of `binary_sensor.`.
  - **One new item: `UI-032`** (P2, score 3, Main-owned, `BLOCKED`) — battery
    coverage. Full evidence in `DASHBOARD_BACKLOG.md`.
- **Blocker 3 is now evidenced, not just asserted.** This sweep produced
  concrete proof that entity IDs cannot be slugified from friendly names *in
  this instance*: the dashboard's working
  `sensor.living_room_living_hue_hue_sensor_temperature` against a live name
  of "Living Hue Hue Sensor Temperature", plus live duplicate battery
  entities where one copy is permanently `unavailable`. Any future routine
  tempted to infer an ID should read the `UI-032` note first.

### Design Review
- Standing item: `DR-001` (P3, Main-owned) — needs a brief, not a redesign.
- `UI-027` is implemented (`9926233`) and awaiting live verification.

### Daily Project Coordinator
- **2026-08-30 05:47 UTC run — reconciliation only, no dashboard YAML
  touched:** fetched `origin/ha-deploy`, confirmed local branch matched
  remote (`20a468d`) with a clean tree before and after. Read
  `PROJECT_STATE.md` in full, the active section of `DASHBOARD_BACKLOG.md`,
  the Open section of `DASHBOARD_ISSUES.md`, all `PENDING` rows in
  `LIVE_VERIFICATION_QUEUE.md`, and recent `DASHBOARD_PROGRESS.md`/git
  history per the Context Loading Strategy.
- **Coordination health:** good. No cross-routine conflicts found in the
  commits reviewed this run; no routine has crossed its ownership boundary;
  no duplicate or contradictory issue/backlog entries found.
- **Stale leases:** none found or cleared — the Active Work Leases table was
  already empty; no routine currently holds a lease.
- **Stale change windows found/cleared:** 4 removed — their 6-hour
  protection had expired (checked against actual commit timestamps, not
  calendar dates) and their work is already recorded in
  `DASHBOARD_BACKLOG.md`'s "Awaiting live verification" table and
  `DASHBOARD_ISSUES.md`'s fixed tables, per this file's own drop rule:
  bilingual template pass (`f04a59f`, protected until 08-30 02:51), false-safe
  status regressions (`b5eee22`, REG-001/002/003, until 05:37), heading-card
  contrast (`9926233`, UI-027, until 05:42), and residual bilingual gaps
  (`dff00f3`, REG-004/005/006, until 05:45). The remaining rows (billing
  privacy, the REG-007..011 batch, `UI-030`, `UI-031`/`REG-013`, the
  regression-audit record, and this file's own coordination-state row) are
  all still inside their 6-hour window and were left as-is.
- **Backlog/issues reconciled:** closed `REG-012` (verification-queue upkeep
  gap). Its recommended corrective action had only been half-done by a later
  batch — the "N checks pending" footer arithmetic became internally
  consistent (39→42) as a side effect of `ccfb0c8` adding two unrelated rows,
  but the actual missing `UI-030` row (LetPot Grow Light guard, `691689a`)
  was still absent, confirmed by grepping the queue for
  `LetPot`/`ray-bedroom`/`UI-030` before touching anything. Added that row to
  `LIVE_VERIFICATION_QUEUE.md` under Bills & rooms and corrected the footer
  to 43; closed `REG-012` in `DASHBOARD_ISSUES.md` with the fixing detail
  under a new "tracking only" status, since there is no live-dashboard
  component to this fix — it does not go through
  `LIVE_VERIFIED`/live-verification. No dashboard YAML, theme, backlog
  score, priority, or ownership altered.
- **Current Main next actionable item:** unchanged — `DR-001` (P3), still
  gated on a design brief; every other Main-owned item is
  `LIVE_VERIFICATION_REQUIRED` with zero human results recorded.
- **Current Billing next actionable item:** unchanged — `BILL-002`'s
  HA-exposure decision (P2, `PARTIAL`); `BILL-001`'s NMI/MIRN portion and
  `BILL-003` remain genuinely `BLOCKED` on owner decisions.
- **Cross-routine conflicts:** none found.
- **Verification backlog summary:** 43 rows in `LIVE_VERIFICATION_QUEUE.md`,
  all `PENDING` — zero human results recorded across at least six
  consecutive autonomous runs now. This remains the single highest-value
  unblock available; `UI-011` (Total Solar, P1, possibly reading 1000× low)
  is the only open non-tracking dashboard issue.
- **Unresolved ambiguity requiring human input:** none new from this run.
  Standing items already on record: `UI-011` needs one look at the Energy
  card; `BILL-001`'s NMI/MIRN helper decision; `BILL-002`'s HA-exposure
  mechanism; `REG-005`'s reworded English text ("WAN not reporting") may want
  review; `DR-001` needs a design brief.

---

## Last Coordination Update

- **Date/time:** 2026-08-30 (this run) — CFG-003 root cause found
- **Branch:** `ha-deploy`
- **`ha-deploy` HEAD before this update:** `6d5acd1`
- **This update's commit:** `ec10656` — `CFG-003` confirmed by the owner and
  **root cause established**. `ha-deploy` was replaced with an **unrelated
  history on 2026-08-29** and the Home Assistant host's clone was left on the
  old one. Proof: `git merge-base 26c3b14 HEAD` — the deploy log's own
  candidate commit against the current tip — returns nothing, and `6c3fff5`
  is a **parentless root commit** despite its merge-shaped message. A branch
  cannot fast-forward across disjoint roots, so the host's commit never
  advances, the content never differs, and the apply step is never reached.
  The propagation stops **at the host's local clone**, not in the script's
  validate/compare/apply stages, which are all behaving correctly on stale
  input. This also reframes Blocker 1: the apply step is **not proven
  broken — it has never been given anything to apply.** Recovery procedure
  written for the owner (protected area, not executed from here), including
  the warning to check `git log origin/ha-deploy..HEAD` for host-only commits
  before any reset. `DEPLOY_AUTH.md`'s credential fault is **independent and
  still outstanding** — fixing the clone may leave manual deploys working and
  scheduled ones still failing. No dashboard YAML change; the probe is
  preserved as the bridge test instrument, per instruction.
  `CFG-001`/`CFG-002` untouched. Validation 7/7.
- **Correction to the record:** the earlier note that "nothing the owner has
  reported seeing is unique to a commit after `6c3fff5`" pointed the right
  way but named the wrong boundary. The real boundary is the history split
  itself — the live dashboard is serving the **pre-2026-08-29 history**, which
  is why `6c3fff5`-era content looked like a match: both histories were
  independently derived from the same production export.

### Superseded — previous update

- **This update's commit:** `d200945` — the `UI-032` probe did not render
  either. An unconditional card's absence cannot be explained by any gate,
  template, entity or schema question, so the fault is not in this file's
  logic. Filed **`CFG-003`** (S1): pushes to `ha-deploy` are not reaching the
  live dashboard. Evidence, not hypothesis: (1) nothing the owner has ever
  reported seeing is unique to a commit after the `6c3fff5` merge — the
  `Home Systems` heading, its 7 cards and its exact 5-chip row all predate it,
  so every live observation to date is equally consistent with the dashboard
  being frozen there; (2) **no change to `dashboards/deez_smart_home.yaml` has
  ever been independently confirmed live** — `UI-025` is a theme file and a
  `/local/` image, `UI-026` was inferred from the background, and `UI-011` was
  read off HA's native Energy panel, none of them this config; (3) 12 commits
  have touched the file since `26c3b14`, the only deployment run on record,
  and it wrote nothing. **Confound stated rather than buried:** the area the
  owner inspected is `sections[5]` at the bottom of the page; the probe is in
  `sections[1]`, second block from the top. Cheap to eliminate, and step (c)
  of the queue row does it. No `UI-032` logic change made, per instruction;
  the probe stays as the deployment test instrument. Also corrected the
  README's documented landing check, which cited `1bdd704` — **not an ancestor
  of this branch**, it belongs to the superseded orphan history — and
  strengthened `DEPLOYMENT_BLOCKERS.md` Blocker 1 from "unverified" to
  "evidence the apply step is not writing". `CFG-001`/`CFG-002` untouched.
  Validation 7/7, dashboard YAML unchanged this commit.
- **Consequence for every other routine:** until `CFG-003` is settled, treat
  each `FIXED — AWAITING LIVE VERIFICATION` row as **unproven at the delivery
  step**, not merely unobserved. Roughly 45 queued checks may be describing
  cards that never reached a screen. Do not queue further dashboard work on
  the assumption it will deploy.

### Superseded — previous update

- **This update's commit:** `2183177` — `UI-032` failed live a second time
  after `0fec9bb`. The flat per-entity conditionals fail exactly as the `or`
  version did, so **`condition: or` was not the cause** — that first diagnosis
  was reasoning by elimination stated with more confidence than one unverified
  variable deserved, and it is corrected in `DASHBOARD_ISSUES.md` rather than
  quietly dropped. Parsing the committed YAML positively rules out placement
  (Home `sections[1]`, beside the 5 working conditionals), `grid_options`
  nesting, section structure, and card shape — mine is key-for-key identical
  to the Solar alert that renders, differing only in `below` vs `above`. The
  two survivors, entity-ID resolution and whether the deploy is at the stamped
  commit, are both unreachable from here. So instead of a third rewrite:
  **`UI-032 PROBE v1`**, one unconditional card first in the same section,
  reading out raw `states()` for all six IDs and counting how many satisfy the
  gates' own test. Its three outcomes are mutually exclusive and each names a
  different root cause — see the queue row. The 12 conditionals stay in place
  so a probe-renders-but-cards-hidden result isolates the gate.
  `CFG-001`/`CFG-002` untouched. Validation 7/7.
- **Standing lesson, strengthened:** the earlier note said to prefer a proven
  construct. The sharper version is that when this environment cannot observe
  the failure, **the next commit should acquire evidence rather than attempt a
  fix**. Two speculative rewrites cost two deploy cycles and the owner's time.

### Superseded — previous update

- **This update's commit:** `0fec9bb` — reconciled a live `FAIL` on `UI-032`
  and shipped the rework. The owner reported no battery alert on Home despite
  batteries at 20/21/28%. Cause: `condition: or`, the one construct in
  `a183d5f` with no precedent anywhere in this file, flagged at the time as
  the first thing to check. Replaced with **one conditional card per entity
  per situation, each with a single flat condition** — the exact shape the
  Active Now strip's existing Solar/Bills/Climate/Media alerts use and which
  the live dashboard demonstrably renders. 12 cards, 6 entities × 2 gates
  (`numeric_state below: 30`, `state: unavailable`); verified by parsing the
  YAML that no `conditions:` list has more than one entry and none is nested.
  Template guard logic, `is_number` handling, unavailable behaviour and the
  six verified entity IDs are all preserved unchanged; the stale
  `_battery_2` duplicate stays excluded. Reconciled per the `FAIL` column:
  same stable ID reused, observed symptom recorded, queue row reset to
  `PENDING` naming the failed attempt. `CFG-001`/`CFG-002` untouched.
  Validation 7/7, no entity or view loss.
- **Standing lesson recorded in `DASHBOARD_ISSUES.md`:** a construct with no
  precedent in this file cannot be validated from this environment, so
  introducing one stakes the whole change on a single unverifiable bet. Prefer
  a pattern the file already proves, even when it is more verbose.

### Superseded — previous update

- **This update's commit:** `a183d5f` — implemented `UI-032` on owner-verified
  entity IDs. One conditional card added to the `home` Active Now strip;
  contextual, so it is absent from the screen entirely when no battery is low
  or unreadable. Six verified entities bound, the stale
  `sensor.tapo_c420_south_wall_battery_2` deliberately excluded. RingRing's ID
  arrived mid-implementation and is included, so **no part of `UI-032` remains
  blocked on entity identification**. `condition: or` is the one construct new
  to this file and is flagged in the verification queue as the first thing to
  check if the card fails to appear. Templates render-tested across six
  scenarios including the 29/30 boundary and non-numeric input. `CFG-001` and
  `CFG-002` untouched and still evidence-blocked. Validation 7/7, no entity or
  view loss.

### Superseded — previous update

- **This update's commit:** `9abf860` — Entity Scout: first live
  `sensor`-domain sweep. Unit/scale cross-check across all 34 `sensor.`
  references came back **clean**; filed `UI-032` (P2, battery coverage —
  2 of ~12 battery entities surfaced, three already low: Front Door 21%,
  RingRing 21%, Tapo C425 North Wall 29%) as `BLOCKED` rather than
  implementing it on inferred IDs, and recorded the live evidence that makes
  inference unsafe here. Advisory only: no dashboard YAML, theme, Energy
  configuration, priority, score or ownership of existing items touched.

### Superseded — CFG-001/CFG-002 diagnostic protocol

- **This update's commit:** `09eb377` — recorded, at the owner's direction,
  the seven determinations `CFG-001` must answer once Energy Dashboard
  evidence is supplied, the correction options ranked by how much Energy
  history each preserves, and an explicit split between what is **established
  read-only** and what is **hypothesis only** — determination 6 (does the cost
  statistic's history start inside the period?) can falsify the hypothesis
  column outright, and the protocol says to report that rather than reshape
  the model. Added a `CFG-002` change gate: the 0.2880 vs 0.2734996 gap is not
  on its own grounds to change the tariff, since a time-of-use band, the 24%
  discount's basis, or a post-31-Jul-2026 rate change would explain it equally
  well. Amended the `CFG-` series definition: a `CFG-` item's **close still
  requires live verification** — its fix is applied in HA rather than pushed,
  so it gains a `LIVE_VERIFICATION_QUEUE.md` row at the point a fix is
  applied. Both remain `OPEN`. **No Energy configuration read, guessed at or
  changed**; no dashboard YAML, theme, priority, score or ownership touched.
- **Mirror:** `claude/ha-dashboard-upgrades-wui7ig` fast-forwarded to match
  `ha-deploy` at `6d5acd1` with the owner's explicit approval, after
  confirming by `git merge-base --is-ancestor` that it was a true
  fast-forward. No force-push, no history rewritten.

### Superseded — previous update

- **Date/time:** 2026-08-30 — live verification reconciliation
- **Branch:** `ha-deploy`
- **`ha-deploy` HEAD before this update:** `ca1fa32`
- **This update's commit:** `afef82c` — reconciled the owner's `UI-011`
  `PASS`, the first live result this queue has ever received: queue Result →
  `PASS` (row kept), `DASHBOARD_ISSUES.md` `OPEN` → `VERIFIED` under the same
  stable ID, footer 44 → 43, Main's pointer and queue entry updated. Filed
  `CFG-001` (S1 — Energy → Totals grid cost ~31.8× too high, blocked on owner
  diagnosis) and `CFG-002` (S4 — SolarNet import tariff 0.2880 vs contracted
  0.2734996) from the same verification, opening the `CFG-` series for
  defects living in HA's configuration rather than in a tracked file. No
  dashboard YAML, theme, Home Assistant configuration, priority, score or
  ownership touched; no device controlled. `bash scripts/ha_validate.sh`
  passes 7/7.

### Superseded — previous update

- **Date/time:** 2026-08-30 — Regression Auditor
- **`ha-deploy` HEAD before that update:** `50fc733`
- **That update's commit:** `b8d7807` — Regression Auditor run: audited
  `ea7289f..HEAD` (15 commits, 2 dashboard-touching), confirmed no
  cross-routine boundary violation between `ccfb0c8` (Main) and `d570a82`
  (Billing), re-verified the verification-queue footer count and the
  billing-privacy remainder are both accurate. Filed `REG-014` (LOW,
  tracking-completeness gap: `BILL-001`/`BILL-004` missing from
  `DASHBOARD_ISSUES.md`). No dashboard YAML, theme, priority, score,
  ownership or `LIVE_VERIFIED` state touched.

Per `CLAUDE.md`, a commit cannot contain its own hash: this update's SHA is
written by the `docs: stamp` commit that immediately follows it.
