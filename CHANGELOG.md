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
