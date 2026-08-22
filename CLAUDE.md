# CLAUDE.md

Operating rules for any AI assistant (or human) working in this repository.
This repo manages configuration, dashboards, automations, scripts, and
documentation for a **live, production, family Home Assistant instance**.
These rules apply to every future session, not just the one that wrote
them.

## Ground rules

### Production posture

1. **The existing Home Assistant setup is production.** Treat every
   entity, automation, and dashboard currently running on the live
   instance as production infrastructure — not a sandbox. This is a
   family's home, not a test environment: assume real people depend on it
   working.

2. **Preserve existing functionality.** Never remove or restructure
   working behavior as a side effect of an unrelated change. If a
   requested change could break something that currently works, call it
   out explicitly *before* making it, unless the request explicitly asks
   to replace that behavior.

3. **Never invent entity IDs, device names, area names, or configuration
   values.** Only reference entities that have been confirmed to exist —
   either by direct live inspection via the Home Assistant connector, by
   `docs/entity_inventory.md`, or by files already present in this
   repository. If an entity isn't confirmed, say so instead of guessing.

4. **Validate before you reference.** Before writing any automation,
   script, or dashboard entry that names a specific entity, confirm it
   against the live connector or `docs/entity_inventory.md`. Note that
   this connector does not expose real `entity_id` values (see
   `docs/live_ha_blockers.md`) — a friendly name alone is not enough to
   safely write YAML; the real `entity_id` must be separately confirmed.

### Change discipline

5. **Prefer additive, reversible, and incremental changes.** Favor new
   files, new automations, and feature-flagged additions over edits that
   overwrite or delete existing working configuration.

6. **Never delete or overwrite known-good production configuration
   without a rollback copy.** Before a destructive or hard-to-reverse
   edit, create a clearly identified backup/checkpoint (a copy of the file
   under a `.bak`/dated name, a backup branch or tag, or an explicit
   "before" snapshot recorded in the commit) so the prior state can be
   restored.

7. **Never perform a large, uncontrolled refactor in one change** —
   dashboards especially. A cleaner architecture is never worth breaking a
   working production dashboard/automation set in a single big edit. If a
   major redesign is worthwhile, build it as a separate candidate
   version instead of replacing the working one outright. See
   `docs/deployment.md` for the required incremental change workflow.

8. **Avoid changing unrelated parts of working YAML.** Keep diffs scoped
   to what was actually asked for — don't reformat, reorder, or "clean up"
   surrounding config as a side effect.

### Validation and Git hygiene

9. **Validate YAML before committing.** Any YAML added or modified in this
   repository must be checked for valid syntax before it is committed.

10. **Keep Git commits small and logically scoped.** Do not bundle
    unrelated work into one giant commit — e.g. a docs update and a
    dashboard change should usually be separate commits.

11. **Record meaningful changes in `CHANGELOG.md`** as they're made, not
    as an afterthought.

### Secrets

12. **Never commit secrets.** This includes passwords, tokens, API keys,
    long-lived access tokens, webhook URLs, Nabu Casa credentials, Wi-Fi
    credentials/SSIDs, private URLs, hostnames/IPs that expose the live
    instance, or any other credentials. Use placeholders and
    `secrets.yaml`-style references (excluded from version control)
    instead.

13. **Never commit the actual contents of `secrets.yaml`** (or any
    equivalent secrets store), even partially, even redacted-looking.
    Reference it by key only.

### Transparency

14. **Distinguish repository-only work from live-tested work.** Clearly
    label whether a change exists only in this repository (not yet
    applied to the live instance) or has been tested/verified against the
    live system. Use this distinction in commit messages, PR descriptions,
    and docs (e.g. `docs/live_ha_blockers.md`).

15. **Use the Home Assistant connector for live inspection where
    available.** When live inspection tools are connected, use them to
    verify entity IDs, current state, and configuration before writing
    automations, dashboards, or docs that reference the live system —
    rather than relying on memory or assumption.

16. **If raw production config cannot be retrieved safely through
    available tools, stop and document the blocker** in
    `docs/live_ha_blockers.md` rather than reconstructing or guessing at
    it from entity states alone. Entity *state* is not the same as
    configuration — never regenerate `automations.yaml`, dashboard YAML,
    or similar from live state snapshots.

### Live device safety

17. **No destructive live changes without explicit confirmation.** Do not
    call any Home Assistant service/tool that turns things off, deletes,
    overwrites, or otherwise materially changes the state of the live
    system without explicit user confirmation first. Read-only inspection
    is always fine.

18. **Do not control live devices merely to test something**, unless doing
    so is actually necessary and safe — and say so before doing it. A
    passing curiosity ("let me just toggle this to see") is not
    justification for touching a live device.

19. **Extra caution for anything involving alarms, locks, security,
    heating/cooling, appliances, or high-power loads.** These categories
    get a higher bar for confirmation than an ordinary light or switch —
    a mistake here has real physical, safety, or cost consequences for the
    family living in this home.

## Repository layout

- `dashboards/` — Lovelace dashboard YAML/config, once imported from live
  HA. See "File conventions" below for the intended per-dashboard split.
  Currently empty (no real dashboard config has been retrievable through
  the connected tools yet — see `docs/live_ha_blockers.md`).
- `automations/` — Automation definitions, one file per functional area.
  Currently empty — see `docs/live_ha_blockers.md` (this connector cannot
  currently confirm whether `automation.*` entities even exist on the live
  instance).
- `scripts/` — Home Assistant script definitions. Currently empty, same
  reason.
- `themes/` — Lovelace/UI themes. Currently empty, same reason.
- `docs/` — Project documentation.
  - `docs/entity_inventory.md` — Inventory of entities discovered on the
    live instance via the connector, kept factual and unfabricated.
  - `docs/live_ha_blockers.md` — Exactly what the live connector can and
    cannot do, and open blockers preventing full import of live config
    into this repository.
  - `docs/architecture.md` — Repository conventions: how dashboards,
    automations, and scripts are expected to be organized once real
    config can be imported.
  - `docs/deployment.md` — The required change workflow for production
    dashboard/automation edits (backup → small edit → validate → deploy →
    verify → commit).
- `CHANGELOG.md` — Human-readable log of notable changes to this repo.

## File conventions (for when real config can be imported)

These are the intended file names/splits for when real Home Assistant
config becomes available to import — see `docs/architecture.md` for the
full rationale. **Do not pre-create these as empty files** — only create
a file once it has real content; empty placeholder files invite exactly
the kind of guessed/fabricated content rule 3 forbids.

```
dashboards/
  home.yaml       # main/overview dashboard
  energy.yaml      # solar, energy monitor plugs, grid tariffs
  cameras.yaml     # camera views
  security.yaml    # locks, contact sensors, alarms
  climate.yaml     # AC, fans, temperature/humidity
  network.yaml     # AdGuard, eero, TP-Link hub
  people.yaml      # presence, device trackers
  media.yaml       # TVs, media players
automations/
  lighting.yaml
  presence.yaml
  parents_room.yaml
  business_startup.yaml
  security.yaml
  energy.yaml
scripts/
  (one file per logical group of scripts, once scripts.yaml is available)
themes/
  (one file per theme)
```

## Current state

As of this writing, this repository contains **documentation and
scaffolding only** — no real Home Assistant configuration
(`configuration.yaml`, `automations.yaml`, `scripts.yaml`, Lovelace
dashboard YAML, `themes.yaml`) has been imported, because the connected
Home Assistant MCP connector has no tool that can read those files (see
`docs/live_ha_blockers.md` for the full capability breakdown). What *has*
been done from real, live data:

- `docs/entity_inventory.md` — a verified snapshot of live entity state,
  refreshed and re-verified as of 2026-08-22.
- `docs/live_ha_blockers.md` — a verified capability matrix for the
  connector, plus what's still needed to go further.

Do not create placeholder or example dashboards/automations/scripts that
reference made-up entities — leave those directories empty (aside from a
`.gitkeep`) until real config is available.
