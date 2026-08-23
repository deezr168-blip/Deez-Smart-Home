# ha-config/

This directory is the **deployment root** — the subset of this repository
intended to eventually be pulled into a live Home Assistant `/config`
directory by the official **Git Pull** add-on. It is deliberately kept
separate from the repository root so that:

- Development material (`CLAUDE.md`, `docs/`, `CHANGELOG.md`, this
  project's own scaffolding) never lands in `/config`.
- Nothing gets pulled into `/config` until it's been reviewed here first.

See `docs/deployment_manifest.md` at the repo root for the full path-by-
path mapping of what's in this directory, what HA path it targets, and
whether it's currently safe to deploy.

## Current state: structure only, no content

As of this writing, **every subdirectory here is empty** (aside from a
`.gitkeep`). No `configuration.yaml`, `automations.yaml`, `scripts.yaml`,
or `scenes.yaml` exists in this directory, and none will be added until
they contain real, verified content — see
`docs/live_ha_blockers.md` for exactly why: the Home Assistant connector
available to this repository has no tool that can read the live
`/config` directory, so there is nothing verified to put here yet.

**This is intentional, not an oversight.** Writing even a "minimal"
`configuration.yaml` here would be dangerous: once the Git Pull add-on is
configured, whatever exists at `ha-config/configuration.yaml` in this repo
will overwrite the real, working `configuration.yaml` on `/config` the
next time it pulls — regardless of how minimal or well-intentioned it is.
Since this repo cannot currently verify what the live file actually
contains, writing a substitute would risk destroying production
configuration on the very first pull. See `CLAUDE.md` rules 3, 6, and 16.

## What goes here once real config exists

| Path | Home Assistant target | Status |
|---|---|---|
| `configuration.yaml` | `/config/configuration.yaml` | not created — see above |
| `automations.yaml` | `/config/automations.yaml` | not created — no verified automation YAML exists in this repo (see `docs/live_ha_blockers.md`; the connector can't even confirm whether `automation.*` entities exist) |
| `scripts.yaml` | `/config/scripts.yaml` | not created — same reason |
| `scenes.yaml` | `/config/scenes.yaml` | not created — same reason |
| `dashboards/` | `/config/dashboards/` (or wherever Lovelace storage/YAML mode expects) | empty — no dashboard export path exists yet |
| `themes/` | `/config/themes/` | empty — no theme export path exists yet |
| `packages/` | `/config/packages/` | empty — no package-style config verified yet |

`secrets.yaml` will **never** be created or committed here, in this
directory or anywhere else in this repository — see the repo root
`.gitignore` and `CLAUDE.md` rules 12–13.
