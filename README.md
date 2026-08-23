# `ha-deploy` — Home Assistant deployment branch

**The root of this branch is Home Assistant's `/config` directory.**

Anything committed here is intended to land directly in `/config` on the
live instance when the official **Git Pull** add-on syncs this branch.
There is no `ha-config/` wrapper directory — the branch root *is* the
deployment root.

- Branch: `ha-deploy`
- Never merge this branch into `main`. `main` holds project documentation,
  tooling, and notes that must never reach `/config`.
- Never merge `main` into this branch for the same reason.

## Current state: structure and safety rails only — no live config yet

This branch deliberately contains **no `configuration.yaml`,
`automations.yaml`, `scripts.yaml`, `scenes.yaml`, dashboard YAML, or theme
YAML.** That is not an oversight, and it is not something to "fill in"
later from memory or inference.

The reason is documented in full in [`DEPLOYMENT_BLOCKERS.md`](DEPLOYMENT_BLOCKERS.md):
no tool available to this repository has ever been able to read the live
`/config` directory, the live Lovelace/dashboard configuration, or real
Home Assistant `entity_id` values. Nothing verified exists to deploy.

**Why this matters more than usual here:** the Git Pull add-on overwrites
files in `/config` with whatever the repo contains. A "minimal" or
"reasonable-looking" `configuration.yaml` committed to this branch would
silently replace the real, working production file on the very first pull.
Writing one without having read the live original would make this branch
*more* dangerous, not more complete.

## Files currently on this branch

| Path | Purpose | Lands in `/config`? |
|---|---|---|
| `.gitignore` | Blocks secrets, `.storage/`, databases, logs, backups, keys from ever being committed to this branch | Yes (inert) |
| `README.md` | This file | Yes (inert) |
| `DEPLOYMENT_BLOCKERS.md` | What is blocking real config from being added here, and what is needed to unblock it | Yes (inert) |
| `dashboards/.gitkeep` | Reserved deployment path for Lovelace YAML dashboards | Yes (inert) |
| `themes/.gitkeep` | Reserved deployment path for theme YAML | Yes (inert) |

"Inert" means Home Assistant ignores the file — it is not parsed as
configuration and has no effect on a running instance.

## Intended layout once real config is available

```
/config
├── configuration.yaml     # core config — NOT YET PRESENT (blocked)
├── automations.yaml       # NOT YET PRESENT (blocked)
├── scripts.yaml           # NOT YET PRESENT (blocked)
├── scenes.yaml            # NOT YET PRESENT (blocked)
├── dashboards/            # Lovelace YAML dashboards — reserved, empty
└── themes/                # theme YAML — reserved, empty
```

## Rules for adding anything to this branch

1. **Never commit a file here that has not been read from the live
   instance first.** Import, then commit — never author from inference.
   For `configuration.yaml` in particular, read the live file, commit it
   verbatim as a baseline, *then* make changes as reviewable diffs.
2. **Never reference an `entity_id` that has not been confirmed** in Home
   Assistant's Developer Tools → States (or the entity registry / REST
   API). A friendly name is not an entity ID. See `DEPLOYMENT_BLOCKERS.md`.
3. **Never commit secrets.** Reference `secrets.yaml` by key only;
   `secrets.yaml` itself stays out of git and is listed in `.gitignore`.
   Never commit `.storage/`, the recorder database, logs, or backups.
4. **Take a backup before the first pull.** Settings → System → Backups,
   full backup, downloaded off-device. The first sync is the one that can
   overwrite a working file.
5. **Validate YAML before committing**, and review the diff before pushing.
6. **Keep changes small and reversible.** A dashboard redesign is built as
   a separate candidate file and promoted once reviewed — never as an
   in-place wholesale replacement of a working production dashboard.

## Git Pull add-on notes

If this branch is ever pointed at the Git Pull add-on:

- Set the branch to `ha-deploy` explicitly. The add-on's default branch is
  usually `main`/`master`, and `main` must never be pulled into `/config`.
- Prefer `auto_restart: false` until real config exists here and has been
  reviewed. There is currently nothing on this branch that would require
  a restart to take effect.
- Understand the add-on's overwrite behaviour before adding real config:
  files present in this branch replace same-named files in `/config`.
  Files that exist only in `/config` are left alone.
- Pointing the add-on at this branch **in its current state** is harmless
  but also pointless — it would deposit three inert documentation files
  and two empty directories. There is no operational reason to wire it up
  until the blockers below are resolved.
