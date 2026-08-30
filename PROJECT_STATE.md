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

### Daily Project Coordinator
- Coordination and tracking maintenance only.
- May modify `PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md`,
  `DASHBOARD_ISSUES.md`, `LIVE_VERIFICATION_QUEUE.md`,
  `DASHBOARD_PROGRESS.md`, and documentation under `archive/`.
- May perform evidence-based reconciliation of coordination and tracking
  state.
- **Must not modify** `dashboards/deez_smart_home.yaml`, themes, Home
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
| Bilingual template pass (all 36 views) | Main | `f04a59f` — 08-29 20:51 | `LIVE_VERIFICATION_REQUIRED` | 08-30 02:51 | Sequence `f4e7ec3`→`fa286de`→`f04a59f`; Main may continue under RCP rule 5. |
| False-safe status regressions (`security`, `lights`, `cameras`, `home`) | Main | `b5eee22` — 08-29 23:37 | `LIVE_VERIFICATION_REQUIRED` | 08-30 05:37 | Closes REG-001/002/003. |
| Heading-card contrast (`themes/deez_your_name.yaml`) | Main | `9926233` — 08-29 23:42 | `LIVE_VERIFICATION_REQUIRED` | 08-30 05:42 | Closes UI-027; theme-level rule, no dashboard YAML. |
| Residual bilingual gaps (`people-locations`, `ipad-command-center`, `home`) | Main | `dff00f3` — 08-29 23:45 | `LIVE_VERIFICATION_REQUIRED` | 08-30 05:45 | Closes REG-004/005/006. REG-005 changed English `WAN —` → "WAN not reporting" — owner may want to review. |
| Regression audit record (`DASHBOARD_ISSUES.md`) | Regression Auditor | `3116495` — 08-29 22:49 | `PUSHED` | 08-30 04:49 | Baseline REG-001..006 fresh; do not re-audit that range. |
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
UI-011 FAIL — Total Solar is about 1000× too small
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

| Routine | Item | Priority | State | Reason Selected |
|---|---|---|---|---|
| Main CasaRay Upgrade | `DR-001` — iPad Command Center density | P3 | `PLANNED` — needs a design decision before implementation | `BILING-RESID` (REG-004/005/006) is fixed and pushed in `dff00f3`, so `DR-001` is the only item left in Main's queue and the Selection Score no longer has anything to choose between — it scores **−2** (Impact 3, Effort 4, Risk 4) and is selected by being the sole remainder, not by rank. It is explicitly "advisory item, no implementation agreed": a density *review* the CasaRay Design Reviewer should scope before Main writes code, not a coded fix to start speculatively. Everything else Main owns (`UI-011`, and this run's own REG-001..006/UI-027 batches) is `LIVE_VERIFICATION_REQUIRED` and waiting on the owner. |
| Billing Dashboard Upgrade | `BILL-001` — remove hardcoded account / NMI / MIRN from `bill-electricity` and `bill-gas` | P1 | `PLANNED` — actionable | Highest actionable Billing-owned item, and named explicitly in the P1 class. Blocks `BILL-003`: ingestion should not be built over an unresolved privacy exposure. Repository removal is safe now; only the question of what the live card displays needs the owner. Unchanged by scoring — Billing's only actionable P1 (score 4). |

---

## Current Work / Blockers

### Main (CasaRay Upgrade)
- **Queue:** `DR-001` (P3, score −2) only, and it needs a design brief before
  code. No actionable P1 or P2 remains; `UI-011` is P1 but purely
  `LIVE_VERIFICATION_REQUIRED` (queue rule 4).
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

### Billing
- **Queue:** `BILL-001` (P1) → `BILL-002` (P2) → `BILL-003` (P2).
- **`BILL-001` is the live blocker:** `bill-electricity` and `bill-gas` still
  carry hardcoded account numbers, an NMI and a MIRN. Re-verified this run —
  both lines present, no commit has touched the bill subviews. Resolve before
  widening billing scope.
- Six bill subviews exist, one section / one column each, back chip to
  `bills`; layout reviewed under `9b28fdb`, no change needed.
- Bill sensors (`sensor.bills_unpaid_count`, `sensor.bills_outstanding_total`)
  are not exposed to Assist — billing figures are `CODE_VALID` at best.

### Regression
- Baseline audit `3116495` against `7f304ad`: REG-001..006, **all six now
  fixed** and awaiting live verification. Evidence in `DASHBOARD_ISSUES.md`;
  full audit detail in `archive/DASHBOARD_ISSUES_ARCHIVE.md`.
- No open regressions. Next audit should re-sweep the false-safe-state class.
- Auditor is advisory: findings queue for Main, never self-implemented.

### Entity Scout
- File findings in `DASHBOARD_BACKLOG.md` as evidence-based items.
- Entity registry is unavailable here; entity existence is inferred from the
  imported live dashboard and never confirmed. Record findings as claims.

### Design Review
- Standing item: `DR-001` (P3, Main-owned) — needs a brief, not a redesign.
- `UI-027` is implemented (`9926233`) and awaiting live verification.

---

## Last Coordination Update

- **Date/time:** 2026-08-30 00:30 UTC
- **Branch:** `ha-deploy`
- **`ha-deploy` HEAD before this update:** `88c345b`
- **This update's commit:** `c5584c2` — Daily Project Coordinator added to
  the ownership map, protected areas, stamp rule 18 and the startup profiles.
  Final framework correction. No priority, backlog item, issue status,
  verification result, score, change window or Next Actionable Work altered.

Per `CLAUDE.md`, a commit cannot contain its own hash: this update's SHA is
written by the `docs: stamp` commit that immediately follows it.
