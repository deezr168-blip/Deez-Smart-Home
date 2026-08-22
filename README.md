# Deez Smart Home

Configuration, documentation and tooling for a Home Assistant installation.

## Repository layout

| Path | Contents |
| --- | --- |
| `home-assistant/` | Home Assistant YAML (configuration, automations, dashboards) |
| `docs/` | Generated and hand-written documentation |
| `scripts/` | Tooling for generating and validating documentation |
| `snapshots/` | Dated captures of live Home Assistant state, used as generator input |
| `safework/` | Unrelated workstream: safety incidents, procedures and corrective actions |

## Documentation

- [`docs/entity_inventory.md`](docs/entity_inventory.md) — every Assist-exposed
  entity, by area, with current state. **Generated**; see below.
- [`docs/health_report.md`](docs/health_report.md) — triage of unavailable
  entities, duplicate integrations and configuration defects found in the live
  system.
- [`docs/improvement_backlog.md`](docs/improvement_backlog.md) — proposed
  automations and dashboard work, and what currently blocks each item.

## Regenerating the entity inventory

The inventory is generated from a Home Assistant Assist live-context snapshot so
that it reflects verified live state rather than assumptions:

```sh
python3 scripts/build_entity_inventory.py snapshots/<dated-snapshot>.json
```

To capture a fresh snapshot, save the raw result of the Home Assistant MCP
server's `GetLiveContext` call (or read the
`homeassistant://assist/context-snapshot` resource) to
`snapshots/YYYY-MM-DD-assist-context.json`, then rerun the command above.

## Comparing two snapshots

```sh
python3 scripts/diff_snapshots.py snapshots/<older>.json snapshots/<newer>.json
```

Reports entities that became unavailable, recovered, appeared or disappeared,
hiding routine state churn unless `--all-changes` is passed. It exits non-zero
when something broke or vanished, so it can gate a check.

## Tests

```sh
python3 scripts/test_snapshot_tools.py
```

No third-party dependencies. The suite also asserts that
`docs/entity_inventory.md` still matches what the generator produces, so a stale
committed inventory fails the run.

### Known limitation: entity IDs

The Assist context does **not** expose canonical `domain.object_id` entity IDs —
only friendly names, domains, areas and states. Before referencing any entity in
dashboard or automation YAML, confirm its real entity ID in Home Assistant under
**Developer Tools → States**. A friendly name from the inventory is not a valid
entity ID.

## Conventions

- No secrets in this repository. `secrets.yaml`, tokens, `.storage/` and
  backups are excluded via `.gitignore`.
- Generated files carry a "do not edit by hand" banner; change the generator
  instead.
