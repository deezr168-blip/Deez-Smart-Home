# CLAUDE.md

Operating rules for any AI assistant (or human) working in this repository.
This repo manages configuration, dashboards, automations, scripts, and
documentation for a **live, production Home Assistant instance**.

## Ground rules

1. **The existing Home Assistant setup is production.** Treat every entity,
   automation, and dashboard currently running on the live instance as
   production infrastructure — not a sandbox.

2. **Preserve working functionality.** Never remove or restructure existing
   behavior as a side effect of an unrelated change. If a change could break
   something that currently works, call it out explicitly before making it.

3. **Never invent entity IDs.** Do not guess, assume, or fabricate entity
   IDs, device names, area names, or configuration values. Only reference
   entities that have been confirmed to exist, either by direct inspection
   of the live system (see `docs/entity_inventory.md`) or by files already
   present in this repository. If an entity isn't confirmed, say so instead
   of guessing.

4. **Prefer additive and reversible changes.** Favor changes that can be
   cleanly reverted (new files, new automations, feature-flagged additions)
   over edits that overwrite or delete existing working configuration.
   Destructive or hard-to-reverse changes require explicit confirmation.

5. **Validate YAML before committing.** Any YAML added or modified in this
   repository must be checked for valid syntax before it is committed.

6. **Never commit secrets.** Never commit passwords, tokens, API keys,
   long-lived access tokens, private URLs, hostnames/IPs that expose the
   live instance, or any other credentials. Use placeholders and
   `secrets.yaml`-style references (excluded from version control) instead.

7. **Distinguish repository-only work from live-tested work.** Clearly
   label whether a change:
   - exists only in this repository (not yet applied to the live instance), or
   - has been tested/verified against the live Home Assistant instance.

   Use this distinction in commit messages, PR descriptions, and docs
   (e.g. `docs/live_ha_blockers.md`) so it's always clear what is real vs.
   proposed.

8. **Use the Home Assistant connector for live inspection where available.**
   When live inspection tools are connected, use them to verify entity IDs,
   current state, and configuration before writing automations, dashboards,
   or docs that reference the live system — rather than relying on memory
   or assumption.

9. **No destructive live changes without confirmation.** Do not call any
   Home Assistant service/tool that turns things off, deletes, overwrites,
   or otherwise materially changes the state of the live system without
   explicit user confirmation first. Read-only inspection is always fine.

## Repository layout

- `dashboards/` — Lovelace dashboard YAML/config, once imported from live HA.
- `automations/` — Automation definitions.
- `scripts/` — Home Assistant script definitions.
- `themes/` — Lovelace/UI themes.
- `docs/` — Project documentation.
  - `docs/entity_inventory.md` — Inventory of entities/config discovered on
    the live instance via the connector, kept factual and unfabricated.
  - `docs/live_ha_blockers.md` — Open questions/blockers preventing full
    import of live config into this repository.
- `CHANGELOG.md` — Human-readable log of notable changes to this repo.

## Current state

This repository was just scaffolded and does not yet contain real Home
Assistant configuration. Only safe scaffolding and documentation exist
until actual configuration is exported/imported from the live instance.
Do not create placeholder or example dashboards/automations/scripts that
reference made-up entities — leave those directories empty (aside from a
`.gitkeep`) until real config is available.
