# Access Verification

**This document is protected infrastructure.** It records how Claude actually
reaches Home Assistant and GitHub. Extend it as new access paths are verified;
do not remove a documented path that still works, and never replace a working
path with an unverified one.

No tokens, credentials, URLs or instance identifiers belong in this file. It
describes *which channel works*, not *how to authenticate to it*.

---

## Last verified

**2026-08-24, from a Claude Code remote session.** Every "verified" line below
was executed in that session and returned real data. Anything not confirmed is
listed under *Not available* rather than assumed.

## Path 1 — Home Assistant, via the Assist/MCP connector

**Status: WORKING.** This is the live bridge between Claude and Home Assistant.

Authentication is held by the claude.ai connector configuration, *not* by
anything in this repository. There is no token, `.env` or config file here that
Claude depends on to reach Home Assistant — which also means no change to this
repository can break the connection.

Verified working:

| Capability | Tool | Result |
|---|---|---|
| Read all exposed entity state | `GetLiveContext` | 431 entities, 11 areas, 25 domains |
| Filter by name / domain / area | `GetLiveContext` args | Working (empty result on no match, not an error) |
| Instance clock and timezone | `GetDateTime` | Returned AEST |

Also exposed by the connector, **not exercised** in the verification session
because they change live device state: `HassTurnOn` / `HassTurnOff`,
`HassLightSet`, `HassClimateSetTemperature`, `HassFanSetSpeed`, `HassSetPosition`,
`HassSetVolume`, media transport controls, `HassBroadcast`, list/todo
operations, `HassCancelAllTimers`.

> These are real actuators pointed at real appliances. Treat every one of them
> as a physical action, not an API call.

### Known limitation: no entity IDs

The connector reports **friendly name, domain, area and state — never
`entity_id`**. Confirmed by inspecting a full `GetLiveContext` dump: zero
occurrences of `entity_id`, and the only attributes surfaced are
`brightness`, `current_position`, `current_temperature`, `device_class`,
`humidity`, `temperature`, `temperature_unit`, `unit_of_measurement` and
`volume_level`.

Consequences, which matter for any future work:

- `docs/entity_inventory.md` is **name-keyed, not ID-keyed**.
- Entity IDs cannot be obtained through this path at all. Nothing may reference
  an `entity_id` until it has been read from the entity registry over an
  authenticated session.
- Friendly names in this instance are **not unique** — several distinct
  entities share a name across domains. Slugifying a friendly name into an
  `entity_id` will produce wrong or ambiguous results. Do not do it.

### Not available through this path

Not a fault — simply outside what the connector exposes. Do not attempt to work
around these by guessing:

- REST API (`GET /api/states`, `/api/config`, `/api/services`)
- WebSocket registries (`config/entity_registry/list`, `config/device_registry/list`,
  `config/area_registry/list`)
- Filesystem access to the Home Assistant `/config` directory
- `.storage` contents, including storage-mode dashboards
- `hass --script check_config` or any HA-side config validation
- Entities not exposed to Assist (the 431 figure is the exposed set, not the
  full instance)

## Path 2 — GitHub

**Status: WORKING.** `deezr168-blip/deez-smart-home`, over the GitHub MCP tools.
Note that `git push` over HTTPS has no credentials in this environment and
fails with `could not read Username`; pushes go through the GitHub MCP tools
instead. The `gh` CLI is deliberately **not** present either.

## What this means for future sessions

Claude can **read** live Home Assistant state and **read/write** this
repository. Claude cannot read Home Assistant's configuration files, so the
storage-mode dashboard and the automations are not visible from here — see
`home-assistant/README.md` for why that is expected and how deployment works.

The practical rule that follows: **this repository cannot be treated as a
mirror of the live instance.** It is a place for documentation, verified
inventories, tooling and staged config — not a source of truth about what the
instance currently contains. When the two disagree, the instance is right.
