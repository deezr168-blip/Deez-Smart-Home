# PROJECT_STATE.md — Entity & Feature Scout section (this branch only)

> **⚠️ COORDINATION NOTICE — READ BEFORE USING THIS FILE**
>
> The live, authoritative `PROJECT_STATE.md` for this project is maintained
> directly on branch `ha-deploy` (currently ~1,800 lines, covering Main
> CasaRay Upgrade, Billing Dashboard Upgrade, Regression Auditor, CasaRay
> Design Reviewer, Daily Project Coordinator, and Entity & Feature Scout).
> This branch (`claude/determined-thompson-rjnvsx`) was provisioned fresh
> off `main`, which does not contain any of that coordination history —
> `main` still holds only the original repo scaffold. This file therefore
> contains **only** the Entity & Feature Scout section for this run, per
> this routine's own instructions ("update only the Entity & Feature Scout
> section of PROJECT_STATE.md"). It is **not** a substitute for the real
> file on `ha-deploy` and should be reconciled into it by whoever has write
> access there — not merged wholesale, since it does not carry the other
> routines' sections.
>
> **This is at least the third consecutive Entity & Feature Scout run to
> hit this problem.** Branches `claude/determined-thompson-011gju` and
> `claude/determined-thompson-bzjgjs` (earlier runs of this same scheduled
> task) each independently created their own `PROJECT_STATE.md` /
> `DASHBOARD_BACKLOG.md` off `main` for the same reason, and neither was
> ever merged into `ha-deploy` — their findings never reached the shared
> coordination state and are effectively lost. This run's findings are
> captured below and in `DASHBOARD_BACKLOG.md` on this branch so they
> aren't lost a third time, but they still need a human (or whoever
> configures this scheduled task) to either (a) point this scheduled
> task's branch base at `ha-deploy` instead of `main`, or (b) manually
> port this content into `ha-deploy`.

## Entity & Feature Scout

**Run date:** 2026-08-30

**Areas inspected:**
- Full live entity sweep via the Home Assistant connector (`GetLiveContext`,
  read-only, no filters) — 423 entities across 24 domains, 10 named areas
  (Backyard, Dining, Energy, Garage, Guest Room, Kitchen, Living Room,
  Network, Parents Room, Ray Bedroom) plus many entities with no area
  assigned (mobile-device sensors, persons, scenes, zones).
- Cross-referenced against the 36-view dashboard structure in `ha-deploy`'s
  `dashboards/deez_smart_home.yaml` (read-only — not modified, per this
  routine's ownership boundary).
- Reviewed `ha-deploy`'s `PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md`,
  `DASHBOARD_ISSUES.md` and `DASHBOARD_PROGRESS.md` before proposing
  anything, to avoid re-discovering completed or already-queued work.

**Opportunities discovered (new — checked against `ha-deploy`'s current
backlog and issue list, not already tracked there):**

1. **Missing "Backyard" area view.** Live HA reports a `Backyard` area with
   its own entities — `B/Contact Sensor` (door contact, cloud-connectivity,
   signal-level; currently available, door `off`) and
   `B/Freezer/EnergyMonitor/P110M` (energy-monitoring smart plug; currently
   `unavailable`). Every other physical area with entities (Garage, Kitchen,
   Dining, Living Room, Guest Room, Parents Room, Ray Bedroom) has a
   dedicated dashboard view; Backyard has none. See `FEAT-BACKYARD-VIEW-001`
   in `DASHBOARD_BACKLOG.md` on this branch.
2. **Emergency Button entities unavailable (safety-relevant observation,
   not a dashboard defect).** Live `event`-domain entities
   `Emergency Button Dad main` and `Emergency Button Mum main` are both
   `unavailable`. The Parents Room dashboard view already has a working
   binary_sensor/sensor pair for emergency-button status, so there is no
   missing dashboard case here — this reads as a device/connectivity health
   question, similar in kind to the existing owner-only issues `CFG-001` /
   `CFG-002` on `ha-deploy`. Flagging for visibility only, given these are
   panic-button devices; no dashboard code implicated.

**Backlog items added:** `FEAT-BACKYARD-VIEW-001` (proposed on this branch
only — see `DASHBOARD_BACKLOG.md`; confirmed not a duplicate of any item in
`ha-deploy`'s current 5-item active queue: `BILL-001`, `BILL-002`,
`BILL-003`, `UI-032`, `DR-001`). Needs manual reconciliation into
`ha-deploy` by someone with write access there.

**Backlog items closed/updated:** None. This branch has no write access to
the real `DASHBOARD_BACKLOG.md` on `ha-deploy`, so nothing was marked
closed from here. No evidence was found that any existing `ha-deploy`
backlog item is stale or already implemented.

**Verified entity opportunities:** No entity_id was inferred for either
finding above. `ha-deploy`'s own Entity Scout history (the `UI-032`
blocker note) already established that friendly-name-to-entity_id
slugification is unsafe in this instance (confirmed name/ID mismatches and
duplicate/stale entities exist live). Both findings above are stated using
live friendly names, domains, states and areas only — never a guessed
entity_id.

**Blockers:**
- **Process (this run's primary blocker):** this run's designated branch
  (`claude/determined-thompson-rjnvsx`) has no git ancestry relationship
  with `ha-deploy`, so nothing written here reaches the shared coordination
  state without manual reconciliation. See the notice at the top of this
  file.
- **Data:** no persisted entity inventory exists on `ha-deploy` either
  (`docs/entity_inventory.md` is not present there); entity ID verification
  currently depends on ad hoc live `GetLiveContext` calls (friendly
  names/states/areas only — no `entity_id` field is returned) or an
  owner-supplied Developer Tools → States export.

**Next recommended discovery focus:**
- Once entity IDs can be verified (owner States export, or an
  entity_id-capable live query), confirm whether
  `B/Freezer/EnergyMonitor/P110M` is still physically installed, to resolve
  `FEAT-BACKYARD-VIEW-001` either way.
- Continue the domain-by-domain live cross-check that `ha-deploy`'s Entity
  Scout history shows only completed the `sensor` domain so far —
  `switch`, `binary_sensor` and `light` together account for 125 of the 423
  live entities and have not yet been swept for unit/state/reference
  correctness against the dashboard.
