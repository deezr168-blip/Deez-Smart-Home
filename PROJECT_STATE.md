# Project State

Shared coordination and ownership map for the autonomous routines working on
this repository (Main CasaRay, Billing Dashboard, Regression Auditor, Design
Reviewer, Entity & Feature Scout, and others as introduced). Each routine
owns and updates only its own section below.

This file did not exist prior to this run. It is being created now, with
only the Entity & Feature Scout section populated, because no other
routine's section content can be inferred or fabricated. Routines that run
after this one should add their own section rather than assume any
ownership/priority model beyond what they themselves define.

## Entity & Feature Scout

**Run date:** 2026-08-31

**Areas inspected:**
- Repository root and all tracked files (`CLAUDE.md`, `README.md`,
  `docs/entity_inventory.md`, `home-assistant/`, `safework/`, `scripts/`)
- Git history (all 5 commits, both branches — `main` and
  `claude/gallant-galileo-8jzt83` point to the same commit)
- Home Assistant live connector (read-only query)

**Findings:**
- `dashboards/deez_smart_home.yaml` does not exist. No dashboard has been
  built yet.
- `DASHBOARD_PROGRESS.md`, `DASHBOARD_ISSUES.md`, and this file
  (`PROJECT_STATE.md`) did not exist prior to this run.
- `docs/entity_inventory.md` exists but is an unpopulated Stage 2 scaffold
  ("NOT VERIFIED — not yet populated"), pending a separate access
  verification stage.
- The Home Assistant connector is live and reachable read-only, and returned
  a real, populated instance: ~424 entities across 10 areas (Network,
  Living Room, Ray Bedroom, Parents Room, Dining, Energy, Kitchen, Garage,
  Backyard, Guest Room) and a wide range of domains (sensor, switch,
  binary_sensor, select, scene, light, climate, cover, fan, media_player,
  camera, person, weather, etc.). Full breakdown recorded in
  `DASHBOARD_BACKLOG.md`.

**Opportunities discovered:** None queued this run. Dashboard-improvement
opportunities require an existing dashboard to compare against; none
exists. Proposing views/cards now would mean inventing dashboard structure,
which is out of scope for this routine.

**Backlog items added/updated/closed:** `DASHBOARD_BACKLOG.md` created with
a blocked-status header and the verified live entity summary above, for
reference by whichever routine builds the initial dashboard. No FEAT-XXX
items added — none can be responsibly scoped yet.

**Verified entity opportunities:** None specific yet — the entity landscape
is broad enough (climate, energy, network, multiple rooms, cameras) to
support a full-featured dashboard once one exists, but no entity IDs are
cited here pending `docs/entity_inventory.md` being properly populated by
its owning stage.

**Blockers:**
1. No `dashboards/deez_smart_home.yaml` exists — nothing to scout for gaps
   or redundant/weak presentation against.
2. `docs/entity_inventory.md` is unpopulated, so this routine cannot cite
   specific verified entity IDs in backlog items without re-deriving them
   itself, which would duplicate the access-verification stage's job.
3. No prior `PROJECT_STATE.md` existed to confirm ownership boundaries or
   the P0–P3 priority model against other routines (Main CasaRay, Billing,
   Regression Auditor, Design Reviewer) — this run cannot verify those
   routines' scope, only note that their sections are absent.

**Next recommended discovery focus:** Once a dashboard exists and
`docs/entity_inventory.md` is populated, re-run entity/feature discovery
against the areas with the richest verified entity counts first (Network,
Living Room, Ray Bedroom, Energy) since those offer the most material for
whole-home usefulness and contextual-control opportunities.

**Run outcome:** No-op (run 1 of up to 2 before recommending a pause). This
repository is pre-dashboard; there is no meaningful, safe, unblocked
dashboard-improvement work for this routine to queue. Recommend re-running
this routine only after a dashboard and `PROJECT_STATE.md` ownership
sections exist, or after `docs/entity_inventory.md` is populated — whichever
comes first. If a second consecutive run finds the same blockers, this
schedule should be paused until that foundational work lands.
