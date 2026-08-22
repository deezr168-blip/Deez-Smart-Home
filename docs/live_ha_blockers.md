# Live Home Assistant Import Blockers

This document tracks what is currently blocking a full import of the live
Home Assistant setup's real configuration (dashboards, automations,
scripts, themes) into this repository, and exactly what the connected
Home Assistant MCP connector can and cannot do. It is a living document —
update it as blockers are resolved, capabilities change, or new findings
turn up.

## Connector capability matrix (verified 2026-08-22)

Status values used below:
- **VERIFIED** — directly confirmed by a real tool call or by inspecting
  the full list of tools this connector exposes.
- **NOT SUPPORTED** — verified that no tool for this exists in the
  connector's tool list. This is a confirmed fact about the connector, not
  a guess.
- **UNVERIFIED** — genuinely not established either way; do not assume an
  answer in either direction until this is resolved.

| Capability | Status | Evidence |
|---|---|---|
| Reading entity states | **VERIFIED** | `GetLiveContext` returned 430 real entities across two sessions (2026-08-21, 2026-08-22); several states differed between the two reads (e.g. `cover.Aqara Roller Shade Driver E1` closed→open, `person.Raymond Du.` not_home→home), confirming live data, not a cached/static export. |
| Reading attributes | **VERIFIED, partial only** | `GetLiveContext` attributes commonly include `device_class` and/or `unit_of_measurement`, and sometimes a live value (`brightness`, `current_temperature`, `volume_level`, `current_position`). It does **not** return a full attribute dump — no `icon`, `supported_features`, `last_changed`/`last_updated`, or similar were ever observed. |
| Controlling entities | **Tool presence VERIFIED; execution UNVERIFIED** | `HassTurnOn`, `HassTurnOff`, `HassLightSet`, `HassClimateSetTemperature`, `HassFanSetSpeed`, `HassSetPosition`, `HassStopMoving`, `HassSetVolume`/`HassSetVolumeRelative`, `HassMediaPlayerMute`/`Unmute`, `HassMediaNext`/`Previous`/`Pause`/`Unpause`, `HassMediaSearchAndPlay`, `HassListAddItem`/`CompleteItem`/`RemoveItem`, `HassBroadcast`, `HassCancelAllTimers` are all present in the tool list. None have been executed — per `CLAUDE.md` rule 9 (no destructive live changes without confirmation) and this task's rule against controlling devices merely to test, actually invoking one wasn't attempted. |
| Listing entities | **VERIFIED, but scoped** | `GetLiveContext` lists entities, but appears limited to whatever is **exposed to the Assist conversation agent** (Home Assistant's per-entity "expose to Assist" setting) — not necessarily every entity in the system. Confirmed indirectly: querying `domain: automation` and `domain: script` returned `"No exposed entities found"` even though installs this size almost always have some of each. |
| Viewing automation entities | **Currently returns none (VERIFIED); whether any exist is UNVERIFIED** | Live call `GetLiveContext(domain: "automation")` → `{"success": false, "error": "No exposed entities found in domain(s): automation"}`. This is a confirmed connector behavior, but doesn't prove no automations exist — only that none are exposed to Assist (or none exist). Indirect evidence automations likely exist: Hue Bridge Automation switches, motion-sensor-enabled toggles, and AC "Climate React" logic all suggest automation-like behavior is configured somewhere, just not necessarily as native HA `automation.*` entities. |
| Viewing script entities | **Currently returns none (VERIFIED); whether any exist is UNVERIFIED** | Same call, `domain: "script"` → same `"No exposed entities found"` result. Same caveat as above. |
| Reading raw YAML (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, etc.) | **NOT SUPPORTED** | No tool in this connector's full tool list reads files of any kind. |
| Reading Lovelace/dashboard configuration | **NOT SUPPORTED** | Same — no dashboard/frontend/lovelace-config tool exists. |
| Reading `/config` (or any HA filesystem path) | **NOT SUPPORTED** | No filesystem-access tool exists. |
| Modifying raw HA files | **NOT SUPPORTED** | Same — no file-write tool exists. |
| Restarting/reloading Home Assistant | **NOT SUPPORTED** | No `restart`/`reload`/`homeassistant.*` service-call tool exists in the tool list (the closest tools are `HassCancelAllTimers`, which is unrelated). |

**Bottom line:** this connector is a **voice-assistant / Assist-style
control surface** — it reads live entity state (scoped to Assist-exposed
entities) and can issue live control actions, but has no path to read or
write Home Assistant's actual configuration files, dashboards, or restart
the system. If GitHub is going to become a real backup/source-of-truth for
this HA instance, that requires a different access method (see "Next
resource needed from the user" below) — this connector alone cannot get
there.

## What this means for this repo

- `docs/entity_inventory.md` can be (and has been) populated from real,
  non-fabricated data via `GetLiveContext` — twice now (2026-08-21 and
  2026-08-22 snapshots), which also let us confirm the data reflects a
  genuinely live system.
- **This repository is not, and cannot currently become, a full backup of
  the live Home Assistant configuration.** GitHub here documents what's
  been observed about the live system (entity inventory, connector
  capabilities) — it does not contain and cannot currently be used to
  reconstruct `configuration.yaml`, `automations.yaml`, `scripts.yaml`,
  Lovelace dashboards, or `themes.yaml`.
- `dashboards/`, `automations/`, `scripts/`, and `themes/` remain **empty
  scaffolding** — there is no available path through this connector to
  pull the real YAML/config for these out of the live instance.
- Do not regenerate or infer production YAML from entity *states* — states
  say what a value currently is, not how the entity/automation/dashboard
  is actually configured.

## Findings from the entity inventory (2026-08-21 / 2026-08-22)

Live reads via `GetLiveContext` (430 entities each snapshot, see
`docs/entity_inventory.md`) surfaced additional blockers beyond the
missing config-export capability:

- **No `entity_id` values available.** `GetLiveContext` only returns
  friendly name, domain, state, area, and partial attributes — never the
  actual `entity_id`, `unique_id`, or integration/platform name. Real
  entity IDs must be confirmed via the entity registry / Developer Tools /
  REST API before any automation, script, or dashboard in this repo
  references a specific entity.
- **Likely duplicate device registrations.** Several TP-Link Kasa/Tapo
  plugs (`K/Bot P100`, `K/Coffee P100`, `K/Top P100`, `G/Printer P100`) and
  a few contact sensors each show up as two entities with the same name —
  one live, one `unavailable` — suggesting two integrations (cloud +
  local) registered for the same physical device. Worth cleaning up in HA
  directly before this repo starts depending on those entities.
- **Malformed entity names**: `"Tapo C420 - East Wall Tapo C420 East
  Wall"` and `"Tapo C420 - South Wall Tapo C420 - South Wall"` switches
  appear to have the device name duplicated inside the entity name.
- **Devices that fluctuate between offline/online across snapshots**: the
  Primo 5.0-1 solar inverter and the SolarNet integration were fully
  `unavailable` on 2026-08-21 but reporting live values on 2026-08-22 —
  likely intermittent connectivity rather than permanently offline. The
  Presence Multi-Sensor FP300 (whole device) and several light fixtures
  (Living Room Inner/Outer, Dining Corridor/Light Left/Right, Hue ambiance
  spots) were `unavailable` in both snapshots — worth confirming whether
  these are intentionally retired or actually broken.
- **Privacy-sensitive live state values**: a physical street address and
  the home WiFi SSID both appear as literal sensor state values (redacted
  in `docs/entity_inventory.md`). If any automation/dashboard needs to
  reference these, treat the values as sensitive — do not paste them into
  committed YAML/docs.
- **Likely cloud-dependent integrations** present: Ring, TP-Link
  Tapo/Kasa cloud connectivity, Electricity Maps, a solar production
  forecast integration, Hue Bridge's own automation engine (not native HA
  automations), the HA Companion App (iPhones/iPads), and possibly
  Samsung/LG TV cloud features. Config for these typically needs API
  keys/tokens kept out of git (e.g. via `secrets.yaml`, excluded from
  version control).

## Blockers to resolve

- [ ] **Automations/scripts visibility**: determine whether this HA
      instance actually has `automation.*`/`script.*` entities that simply
      aren't exposed to Assist (fixable via HA's Voice Assistants →
      Expose settings) or whether it manages this logic entirely through
      device-native automations (e.g. Hue Bridge) instead. Needed before
      `automations/` or `scripts/` can be populated at all.
- [ ] **Dashboard config**: need the real Lovelace YAML/storage config
      (e.g. via the HA File editor add-on, Samba/SSH add-on, or the
      `frontend`/`lovelace` sections of `.storage`) to populate
      `dashboards/`.
- [ ] **Automations**: need `automations.yaml` (or equivalent `.storage`
      entries if managed via UI) to populate `automations/`.
- [ ] **Scripts**: need `scripts.yaml` (or `.storage` equivalent) to
      populate `scripts/`.
- [ ] **Themes**: need `themes.yaml` or theme files to populate `themes/`.
- [ ] **Entity IDs / registry**: need a way to read the entity/device
      registry (real `entity_id`s, `unique_id`s, integration names) before
      any future automation/script/dashboard YAML can safely reference
      specific entities.
- [ ] **Secrets handling**: once real config is imported, confirm how
      `secrets.yaml` (or equivalent) is excluded from this repo (e.g. via
      `.gitignore`) before committing anything that references it.
- [ ] **File-level access**: determine how the user wants to get raw config
      out of HA — options include the HA File Editor / Studio Code Server
      add-on, SSH/Samba add-on, or a manual export/paste. None of these are
      available through the current connector and require user action.

## Next resource needed from the user

To move past this, the user needs to provide one of:
1. Access to the raw HA config files (e.g. via SSH, Samba, or the File
   Editor/Studio Code Server add-on), or
2. Manually exported copies of `automations.yaml`, `scripts.yaml`,
   dashboard YAML/storage JSON, and `themes.yaml` (with secrets redacted),
   or
3. A different MCP connector/tool with file-level HA config access, entity
   registry access, or Lovelace config access.

Separately, and independent of the above: if automations/scripts do exist
in this HA instance but aren't currently exposed to Assist, exposing them
(HA → Settings → Voice assistants → Expose) would let this connector at
least *see* them going forward, though still not read their raw YAML
definitions.
