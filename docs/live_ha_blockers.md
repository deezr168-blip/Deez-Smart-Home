# Live Home Assistant Import Blockers

This document tracks what is currently blocking a full import of the live
Home Assistant setup's real configuration (dashboards, automations,
scripts, themes) into this repository. It is a living document — update it
as blockers are resolved or new ones are found.

## Connector capabilities (as inspected 2026-08-21)

This repo is connected to a live Home Assistant instance via an MCP
connector. Inspecting the available tools shows it exposes a **voice
assistant / Assist-style control surface**, not a configuration/file
export API:

**Read (state/context only):**
- `GetLiveContext` — current state of entities/areas (supports filtering by
  domain, area, name). Used to build `docs/entity_inventory.md`.
- `GetDateTime` — current date/time on the HA instance.
- `todo_get_items` — read items on `todo` lists.

**Write (live control actions only, no config authoring):**
- `HassTurnOn` / `HassTurnOff` — toggle entities.
- `HassLightSet` — set light attributes (brightness/color/etc).
- `HassClimateSetTemperature` — set climate target temperature.
- `HassFanSetSpeed` — set fan speed.
- `HassSetPosition` / `HassStopMoving` — cover/positionable entity control.
- `HassSetVolume` / `HassSetVolumeRelative` / `HassMediaPlayerMute` /
  `HassMediaPlayerUnmute` / `HassMediaNext` / `HassMediaPrevious` /
  `HassMediaPause` / `HassMediaUnpause` / `HassMediaSearchAndPlay` — media
  player control.
- `HassListAddItem` / `HassListCompleteItem` / `HassListRemoveItem` — manage
  `todo`/list items.
- `HassBroadcast` — send a broadcast/announcement.
- `HassCancelAllTimers` — cancel active timers.

**What's missing:** there is no tool exposed to read or write
`configuration.yaml`, `automations.yaml`, `scripts.yaml`, Lovelace
dashboard YAML/storage config, `themes.yaml`, or the underlying HA file
system/`.storage` directory. This connector cannot export existing
dashboards, automations, scripts, or themes as config — it can only read
current entity **state** and issue live control actions.

## What this means for this repo

- `docs/entity_inventory.md` can be (and has been) populated from real,
  non-fabricated data via `GetLiveContext`.
- `dashboards/`, `automations/`, `scripts/`, and `themes/` remain **empty
  scaffolding** — there is currently no available path to pull the real
  YAML/config for these out of the live instance through this connector.

## Blockers to resolve

- [ ] **Dashboard config**: need the real Lovelace YAML/storage config
      (e.g. via the HA File editor add-on, Samba/SSH add-on, or the
      `frontend`/`lovelace` sections of `.storage`) to populate
      `dashboards/`.
- [ ] **Automations**: need `automations.yaml` (or equivalent `.storage`
      entries if managed via UI) to populate `automations/`.
- [ ] **Scripts**: need `scripts.yaml` (or `.storage` equivalent) to
      populate `scripts/`.
- [ ] **Themes**: need `themes.yaml` or theme files to populate `themes/`.
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
3. A different MCP connector/tool with file-level HA config access.
