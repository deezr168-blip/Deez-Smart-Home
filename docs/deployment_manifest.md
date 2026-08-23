# Deployment Manifest

Path-by-path map of `ha-config/` — the directory intended to eventually be
pulled into a live Home Assistant `/config` by the official **Git Pull**
add-on — to its target Home Assistant path, what kind of content it is,
and whether it's currently safe for autonomous deployment.

**This repository is not yet configured for automatic deployment, polling,
or restart.** This manifest documents the intended mapping and its current
blockers; it does not imply any pull is currently wired up. See
`docs/deployment.md` for the required manual change workflow, and
`docs/live_ha_blockers.md` for why most of this is still empty.

## Path mapping

| Repo path | HA `/config` target | Type | Safe for autonomous deployment? | Notes |
|---|---|---|---|---|
| `ha-config/configuration.yaml` | `/config/configuration.yaml` | core config | **N/A — does not exist** | Not created. See "Why `configuration.yaml` was not created" below. |
| `ha-config/automations.yaml` | `/config/automations.yaml` | automation | **N/A — does not exist** | No verified automation YAML exists anywhere in this repo. The connector can't even confirm whether `automation.*` entities exist on the live instance (`docs/live_ha_blockers.md`). |
| `ha-config/scripts.yaml` | `/config/scripts.yaml` | script | **N/A — does not exist** | Same reason — no verified script YAML exists. |
| `ha-config/scenes.yaml` | `/config/scenes.yaml` | core config | **N/A — does not exist** | No verified scene YAML exists (HA "scene" *entities* are known from `docs/entity_inventory.md`, but their underlying YAML definitions have never been read). |
| `ha-config/dashboards/` | `/config/dashboards/` (or Lovelace storage, depending on live mode — unconfirmed) | dashboard | **N/A — empty directory** | No dashboard YAML has ever been retrieved from the live instance. Directory exists only as a placeholder (`.gitkeep`). |
| `ha-config/themes/` | `/config/themes/` | theme | **N/A — empty directory** | Same — no theme file has ever been retrieved. |
| `ha-config/packages/` | `/config/packages/` | core config | **N/A — empty directory** | Speculative structure only — no package-style config has been verified to exist on the live instance at all. |
| `ha-config/README.md` | *(not deployed — repo-only)* | documentation | n/a | Explains this directory's purpose and current empty state; not meant to be pulled into `/config` (see note below on Git Pull add-on scoping). |

No file under `ha-config/` currently contains fabricated or guessed
configuration. Every path above is either genuinely absent or a
placeholder directory.

## Why `configuration.yaml` (and automations/scripts/scenes.yaml) were not created

The task of preparing this deployment structure explicitly allows a
"minimal scaffold" **only where justified by existing project content or
minimal HA scaffolding**, and explicitly forbids fabricating unverified
production configuration. Given the current state of this repo:

- No tool available to this repo has ever been able to read the live
  `/config/configuration.yaml`, `automations.yaml`, `scripts.yaml`, or
  `scenes.yaml` (see `docs/live_ha_blockers.md`'s capability matrix — no
  file-read tool exists at all).
- The **Git Pull add-on overwrites the target file(s) on every pull**.
  Writing even a deliberately minimal `configuration.yaml` here — e.g.
  just `default_config:` — would silently replace the real, working
  production file the first time this repo is ever pulled, because there
  is no way to confirm the minimal version is a superset/compatible
  version of what's actually running.
- This is exactly the scenario `CLAUDE.md` rules 3 ("never invent...
  configuration values"), 6 ("never overwrite known-good production
  configuration without a rollback copy"), and 16 ("if raw production
  config cannot be retrieved safely, stop and document the blocker") are
  designed to prevent.

**Conclusion: creating these files now would make the repository *less*
safe to eventually deploy, not more.** The correct next step is resolving
the blockers in `docs/live_ha_blockers.md` (raw file access to `/config`),
not writing placeholder config and hoping it's compatible.

## Git Pull add-on scoping (unresolved — flagged, not solved here)

The official Git Pull add-on is commonly configured to sync a specific
subdirectory of a repo into `/config` (or the whole repo root). **This
repo has not yet been configured with the add-on, and this task does not
configure it** (per the explicit instruction not to enable automatic
deployment yet). When it eventually is configured, it must be pointed at
`ha-config/` specifically — not the repository root — so that
`CLAUDE.md`, `docs/`, `CHANGELOG.md`, and this repo's own tooling
(`scripts/validate_ha_config.sh`) never land in `/config`. This is called
out here as a required setup step for whoever configures the add-on, not
something this repository can self-enforce from the GitHub side.

## Safety gates (protected — never created by automation in this repo)

The following are never created, committed, or exposed by any automation
in this repository, per `CLAUDE.md` rules 12–13 and this task's explicit
safety gates:

- `secrets.yaml` (anywhere in the repo, not just `ha-config/`)
- `.storage/`
- Authentication files, network configuration exports, backups, SSH keys,
  tokens, or passwords

`.gitignore` (repo root) enforces this for anything that might be
accidentally staged; `scripts/validate_ha_config.sh` checks for it before
every validation run.

## Unresolved blockers

1. **No file-level read/write access to live `/config`.** Everything in
   this manifest is scaffolding, not imported config. See
   `docs/live_ha_blockers.md` for the full capability matrix.
2. **Automations/scripts existence is unverified.** The connector cannot
   confirm whether `automation.*`/`script.*` entities exist at all on the
   live instance (a live query for both domains returned zero exposed
   entities — see `docs/entity_inventory.md`).
3. **No entity registry / `entity_id` access.** Even once raw YAML can be
   read, cross-referencing it against `docs/entity_inventory.md` requires
   real `entity_id`s, which no available tool currently exposes.
4. **Git Pull add-on is not configured.** This manifest describes the
   intended mapping; actually wiring up the add-on (and pointing it at
   `ha-config/`, not repo root) is a separate, explicit step for the user
   to take when ready — not automated here.

## Refresh process

Update this manifest whenever a real file is added to `ha-config/` —
change its row from "N/A — does not exist" to a real status, and record
whether it's been validated against the live instance (per `CLAUDE.md`
rule 14).
