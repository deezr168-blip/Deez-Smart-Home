# Dashboard Progress Log

Tracks dashboard-related work in this repo so removals/replacements of
`dashboards/deez_smart_home.yaml` sections can be traced or reverted. One
entry per work session, newest first.

## 2026-08-29 — Bootstrap run: entity inventory populated, dashboard build blocked

**Trigger:** Scheduled routine with standing authority to redesign
`dashboards/deez_smart_home.yaml` toward a "CasaRay design target."

**Repo state found at start of this run:** no `dashboards/` directory, no
`dashboards/deez_smart_home.yaml`, no `DASHBOARD_PROGRESS.md`, no
`home-assistant/configuration.yaml` (the `home-assistant/` folder is empty
except `.gitkeep`), no `ha-deploy` git remote (only `origin`), and
`docs/entity_inventory.md` was an unpopulated placeholder explicitly marked
"NOT VERIFIED." In other words, none of the prerequisites this task's
instructions assume (an existing dashboard to iterate on, a deploy target,
a verified entity source of truth) existed yet — this repo is still at
Stage 1/2 of its own bootstrap plan (see `docs/entity_inventory.md`).

**What CasaRay means here:** No repo-local design spec exists for
"CasaRay." Researched it externally: CasaRay is a real Apple-native Home
Assistant controller app whose dashboard model is calm, room-first
navigation — entities normalized into rooms → devices → quick actions,
with dedicated camera and energy summary sections, minimal chrome, concise
per-room detail rather than one long flat entity list. Treating this as
the structural/visual target (room-organized sections, quick-action
surfaces, energy and camera rollups) absent a more specific spec.
Source: https://casaray.dev/ and https://casaray.evotec.xyz/.

### Done this run

- Pulled the full live entity set via the `mcp__Home-Assistant__GetLiveContext`
  MCP tool (the only live HA access available in this session) and populated
  `docs/entity_inventory.md`: **425 entities** across 24 domains and 10
  named areas (Network 90, Living Room 73, Ray Bedroom 65, Parents Room 40,
  Dining 31, Energy 23, Kitchen 22, Garage 11, Backyard 10, Guest Room 6;
  54 entities have no area). 144 entities read `unavailable`/`unknown` at
  pull time (flagged per row) — mostly Tapo camera helper entities and some
  Hue scenes/lights, worth checking physically/in the HA UI.

### Blocked this run — did not create `dashboards/deez_smart_home.yaml`

Explicitly did not author dashboard YAML this run because doing so would
have required guessing at real config, which conflicts with "do not invent
entities" and with staying inside the recoverable, verifiable-change
posture this task calls for:

1. **No `entity_id` values are obtainable with current access.**
   `GetLiveContext` returns friendly name, domain, area, state, and
   attributes only — never `entity_id`, `unique_id`, `device_id`, or
   `area_id`. A Lovelace dashboard's cards need real `entity_id`s (e.g.
   `light.dining_left`), and inferring one from a friendly name like
   "Dining Light Left" is a guess, not a verified value — exactly the kind
   of invented entity this task's boundary forbids. Unblocking this needs
   either: a Home Assistant long-lived access token + REST/WebSocket URL
   reachable from this environment, or an MCP tool that surfaces the
   entity/area registries (not just Assist-exposed live state).
2. **No deploy path exists.** The instructions reference pushing to
   `ha-deploy`, but no such git remote, CI workflow, or sync mechanism
   exists anywhere in this repo or session — only `origin` (this GitHub
   repo). Without knowing how a dashboard file in this repo is meant to
   reach the live HA instance (git-ops pull on the HA host? a deploy
   script? manual copy?), I can't validate that anything written here
   would actually take effect, and standing up new deploy infrastructure
   is explicitly outside this task's dashboard-UX boundary without
   separate authorization.
3. **No HA config mirror in this repo to wire a YAML dashboard into.**
   Adding a dashboard file only takes effect if something references it —
   normally a `lovelace: dashboards:` entry in `configuration.yaml` with
   `mode: yaml` and a `filename:`. This repo has no
   `home-assistant/configuration.yaml` (or equivalent) to add that entry
   to, and note also: Home Assistant is deprecating/removing the *global*
   `lovelace: mode: yaml` override as of 2026.8 (right around today's
   date), so it matters which HA core version this instance runs before
   picking the exact wiring approach — worth confirming rather than
   guessing.

### Needed to unblock dashboard authoring (next run or human input)

- A way to read real `entity_id`s (token + API access, or a registry-aware
  MCP tool) — without this, no dashboard YAML can be written without
  guessing IDs.
- Clarification on the `ha-deploy` target / how dashboard changes actually
  reach the live instance.
- Confirmation of the installed HA core version, and whether
  `home-assistant/configuration.yaml` should be mirrored into this repo (or
  the dashboard registered another way).
- Confirmation that the CasaRay app (casaray.dev) is in fact the intended
  reference, since no repo-local spec says so.

Once entity IDs are available, the plan is: build
`dashboards/deez_smart_home.yaml` as room-first sections per area (Living
Room, Ray Bedroom, Parents Room, Dining, Kitchen, Guest Room, Garage,
Backyard), each with a compact quick-actions row plus a details section,
a dedicated Energy view (23 entities already inventoried), and a Cameras
view (6 camera entities) — using only stock Lovelace card types unless a
HACS custom card (e.g. Mushroom) is confirmed installed, which is not yet
known.
