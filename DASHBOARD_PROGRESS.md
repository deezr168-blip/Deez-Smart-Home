# Dashboard Progress Log

Tracks meaningful changes, removals, and replacements made to the Home
Assistant dashboard (`dashboards/deez_smart_home.yaml`) under the CasaRay
redesign mandate, so decisions can be traced or reverted. Newest entries
first.

## 2026-08-29 — First pass: infrastructure audit, no dashboard changes yet

**Repo state found:** `dashboards/deez_smart_home.yaml` does not exist yet
in this repository (checked working tree and full history on `main` and
this branch — no prior commit ever created it). There is also no
`ha-deploy` git remote configured (only `origin`, pointing at this GitHub
repo) and no deployment script or CI pipeline that pushes dashboard YAML to
the live Home Assistant instance. `docs/entity_inventory.md` was still in
its unpopulated "Stage 2 not started" scaffold state.

**What this means:** the redesign mandate assumes an existing dashboard and
an established `ha-deploy` push target to iterate against. Neither exists
yet, so there is nothing to redesign, reorganize, or remove this pass —
only groundwork to lay first.

**What was verified live:** this session does have live read access to the
real Home Assistant instance via the `Home-Assistant` MCP connector, but
only its Assist-style tools (`GetLiveContext`, `HassTurnOn`,
`HassLightSet`, etc.) — not the REST `/api/states` endpoint or the
WebSocket entity/device/area registries. `GetLiveContext` confirmed 425
live entities across 10 areas (Network, Living Room, Ray Bedroom, Parents
Room, Dining, Energy, Kitchen, Garage, Backyard, Guest Room), but it
returns friendly names only — never the underlying `entity_id`.

**Why no `dashboards/deez_smart_home.yaml` was written this pass:** every
Lovelace card needs a real `entity_id` (e.g. `light.living_room`), and
guessing one from a friendly name is explicitly against this project's
rule ("Do not invent entities") and the entity inventory's own rule ("IDs
must never be invented or guessed"). With three same-named-but-different
entities already observed live (e.g. three `55" QLED 4k AI` rows in
Parents Room — one `media_player`/tv, one `media_player`/speaker, one
`sensor`), a naive slugify-the-name guess would be wrong often enough to
risk controlling or displaying the wrong device. That's a correctness and
safety issue, not a style one, so it wasn't done.

**What was done instead:**
- Updated `docs/entity_inventory.md` with a full live snapshot (425
  entities: name, domain, area, device_class, unit, state), explicitly
  marking `entity_id` as unresolved on every row and documenting exactly
  what access is missing to unblock it (a Long-Lived Access Token for the
  REST API, or WebSocket registry access).
- Created this file to track dashboard-specific decisions going forward.
- No entities, automations, helpers, or deployment infrastructure were
  touched. No dashboard file was created or deleted.

**Next steps once entity IDs are resolvable:**
1. Re-run the live pull with `entity_id`-capable access and fill in
   `docs/entity_inventory.md` for real.
2. Draft `dashboards/deez_smart_home.yaml` as a native-Lovelace (no
   assumed HACS cards, since none are confirmed installed) CasaRay-style
   layout — Sections views grouped by area, tile/area cards, minimal
   chrome — built only from verified entity IDs.
3. Confirm (or ask the user for) an actual `ha-deploy` target before ever
   trying to push dashboard config to the live instance; until then,
   dashboard work stays in this repo as a reviewable draft.
