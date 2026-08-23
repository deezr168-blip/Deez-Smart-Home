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

### Added (Git Pull deployment prep)
- Added `ha-config/` as the dedicated deployment root for a future
  official Git Pull add-on setup, with placeholder `dashboards/`,
  `themes/`, and `packages/` subdirectories and a `README.md` explaining
  why `configuration.yaml`/`automations.yaml`/`scripts.yaml`/
  `scenes.yaml` were deliberately **not** created (no verified content
  exists, and a Git Pull sync would overwrite live production files with
  unverified scaffolding).
- Added `docs/deployment_manifest.md` — the authoritative path-by-path
  map of `ha-config/` to its Home Assistant `/config` target, deployment
  safety status per path, and open blockers.
- Added `.gitignore` (none existed before) covering `secrets.yaml`,
  `.storage/`, databases, logs, backups, credentials/tokens, and SSH keys.
- Added `scripts/validate_ha_config.sh` — non-destructive validation
  (YAML syntax + duplicate-key detection via PyYAML, `git diff --check`,
  forbidden secret-file/`.storage` detection, private-key detection).
  Documents what it does *not* run (Home Assistant's own config checker,
  yamllint) rather than pretending to.
- Updated `CLAUDE.md` and `docs/architecture.md` to distinguish the
  repo-root `dashboards/`/`automations/`/`themes/` (development-only,
  never deployed) from `ha-config/` (the only directory ever meant to be
  pulled into `/config`), and clarified that repo-root `scripts/` holds
  repo tooling, not HA script YAML.
