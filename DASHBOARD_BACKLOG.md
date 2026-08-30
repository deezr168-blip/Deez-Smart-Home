# DASHBOARD_BACKLOG.md (this branch — proposed additions only)

> This branch does not carry the real backlog, which lives on `ha-deploy`
> (currently active: `BILL-001`, `BILL-002`, `BILL-003`, `UI-032`,
> `DR-001`, plus a long verified/awaiting-verification history). This file
> lists only the item proposed by this Entity & Feature Scout run, already
> checked against that list to avoid duplication. A human or coordinator
> routine with `ha-deploy` write access should port this into the real
> file; this file can then be discarded. See `PROJECT_STATE.md` on this
> branch for why this run could not write directly into `ha-deploy`.

## FEAT-BACKYARD-VIEW-001

- **Priority:** P2 (Improvement)
- **Owning routine:** Main CasaRay Upgrade (implementation); Entity &
  Feature Scout (discovery, this item)
- **Affected view/area:** New/missing — Home Assistant area `Backyard`;
  no existing dashboard view covers it
- **Verified entities involved** (friendly names only — entity_ids not
  confirmed; see dependencies below):
  - `B/Contact Sensor` — door contact (`device_class: door`), plus
    cloud-connectivity binary_sensor and signal-level sensor. Area:
    Backyard. State at time of sweep: available, door `off`.
  - `B/Freezer/EnergyMonitor/P110M` — energy-monitoring smart plug
    (switch entity plus energy / energy-difference sensors, unit kWh).
    Area: Backyard. State at time of sweep: `unavailable`.
- **Current problem/opportunity:** Every other physical HA area with
  entities (Garage, Kitchen, Dining, Living Room, Guest Room, Parents
  Room, Ray Bedroom) has a dedicated dashboard view. `Backyard` has real,
  area-tagged entities but no view — it is currently invisible on the
  dashboard.
- **Recommended implementation:** Confirm live entity IDs and current
  availability of `B/Freezer/EnergyMonitor/P110M` via a Developer Tools →
  States export before building anything (do not infer IDs from friendly
  names — this instance has confirmed name/ID mismatches and duplicate/
  stale entities; see `ha-deploy`'s `PROJECT_STATE.md` / `UI-032` note). If
  the plug is still installed and live, add a small Backyard view
  mirroring the existing Garage view's pattern (one energy-monitoring plug
  tile + one door-contact tile). If the plug is decommissioned, close this
  item as not-applicable and record that the area is intentionally
  unrepresented.
- **Expected benefit:** Closes the one remaining gap in whole-home
  room-view coverage; surfaces backyard freezer power/energy state and
  door security status that currently exist in Home Assistant but are
  unreachable from the dashboard.
- **Dependencies/blockers:** Confirmed live entity_ids for both entities
  (owner States export); confirmation of whether the freezer plug is
  still physically installed, given its current `unavailable` state.
