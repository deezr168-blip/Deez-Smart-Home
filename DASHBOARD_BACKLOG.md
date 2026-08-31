# Dashboard Backlog

Ranked implementation queue for `dashboards/deez_smart_home.yaml`, maintained
by the Entity & Feature Scout routine. Each item includes an ID, priority,
affected view, verified entities, problem/opportunity, recommended
implementation, and expected benefit.

## Status: Blocked — no dashboard exists yet

As of 2026-08-31, this repository has no `dashboards/deez_smart_home.yaml`,
no `DASHBOARD_PROGRESS.md`, no `DASHBOARD_ISSUES.md`, and no
`PROJECT_STATE.md`. The repo is still at initial scaffold stage (see
`docs/entity_inventory.md`, which is explicitly marked "NOT VERIFIED — not
yet populated").

The Entity & Feature Scout routine's job is to find gaps and opportunities
in an *existing* dashboard relative to verified entities. With no dashboard
in the repo, there is nothing to compare against, so no dashboard-improvement
items can be responsibly queued yet — doing so would mean inventing
structure (views, cards, navigation) that belongs to whichever routine
builds the initial dashboard (per PROJECT_STATE.md, this appears to be
"Main CasaRay," though that file does not yet exist to confirm it).

## Verified live entity landscape (reference only, not backlog items)

A read-only query against the Home Assistant connector confirmed a live,
populated instance is reachable (this is evidence the connector works, not
a substitute for `docs/entity_inventory.md`, which remains the source of
truth once populated by its owning stage):

- ~424 entities total
- Areas: Network (90), Living Room (71), Ray Bedroom (65), Parents Room (40),
  Dining (31), Energy (23), Kitchen (22), Garage (11), Backyard (10),
  Guest Room (6)
- Top domains: sensor (128), switch (53), binary_sensor (46), select (33),
  scene (29), light (26), event (22), number (22), button (20),
  media_player (9), device_tracker (6), notify (6), camera (6), person (3),
  climate (1), cover (1), fan (1), weather (1), todo (1)

This confirms a rich, real entity set exists for a future dashboard to draw
on (whole-home, energy, climate, network, and per-room views all have
verified underlying data), but no entity IDs are recorded here — this
routine does not invent or copy raw IDs into planning docs without a
verified inventory file to cite them from.

## No FEAT items yet

No backlog items are queued. Once `dashboards/deez_smart_home.yaml` and
`PROJECT_STATE.md` exist and `docs/entity_inventory.md` is populated with
verified entity IDs, this routine will resume normal discovery (inspect
recent commits, `DASHBOARD_PROGRESS.md`, `DASHBOARD_ISSUES.md`, and this
file) and queue ranked, evidence-based opportunities here.
