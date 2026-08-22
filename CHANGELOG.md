# Changelog

All notable changes to this repository are documented here.

## [Unreleased]

### Added
- Initial repository scaffolding: `CLAUDE.md` operating rules, `dashboards/`,
  `automations/`, `scripts/`, `themes/`, and `docs/` directories.
- `docs/entity_inventory.md` — initial inventory of entities/config
  discovered via the connected Home Assistant instance.
- `docs/live_ha_blockers.md` — tracking doc for what still needs to be
  imported from the live instance before this repo reflects real config.
- Populated `docs/entity_inventory.md` with a full live snapshot (430
  entities across 24 domains, 10 areas) read via the Home Assistant
  connector's `GetLiveContext` tool. Documented duplicate/likely-offline
  devices, malformed entity names, and privacy-sensitive state values
  (redacted) found during the read.
- Expanded `docs/live_ha_blockers.md` with concrete findings from the
  live snapshot: missing `entity_id` data, suspected duplicate device
  registrations, offline devices, and likely cloud-dependent integrations.
- Reorganized `docs/entity_inventory.md` area-first (Area/room, Lights,
  Switches, Sensors, Binary sensors, Climate, Media players, Cameras,
  Persons/presence, Energy, Network, Helpers, Scripts, Automations,
  Other), refreshed against a new live snapshot (2026-08-22), and added a
  live-verified finding that `automation` and `script` entities are not
  currently exposed through the connector.
- Added a connector capability matrix to `docs/live_ha_blockers.md`
  (VERIFIED / NOT SUPPORTED / UNVERIFIED) covering state/attribute reads,
  entity control, entity listing scope, automation/script visibility, raw
  YAML, Lovelace config, `/config`, file writes, and restart/reload.
- Expanded `CLAUDE.md` ground rules from 9 to 19: rollback checkpoints
  before destructive edits, a ban on large uncontrolled dashboard
  refactors, Git/CHANGELOG discipline, a wider secrets list, a rule
  against regenerating config from live state, and extra caution for
  alarms/locks/security/climate/appliances/high-power loads. Documented
  the intended `dashboards/`/`automations/`/`scripts/` file-naming
  convention (not yet created — no real config exists to populate them).
- Added `docs/architecture.md` (repository/file conventions) and
  `docs/deployment.md` (the required backup → edit → validate → deploy →
  verify → commit workflow for future production changes).
