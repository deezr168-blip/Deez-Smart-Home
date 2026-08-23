# `ha-deploy` — Home Assistant deployment branch

**The root of this branch is Home Assistant's `/config` directory.**

Anything committed here is intended to land in `/config` on the live
instance when the official **Git Pull** add-on syncs this branch. There is
no `ha-config/` wrapper directory — the branch root *is* the deployment
root.

- Branch: `ha-deploy`
- Never merge this branch into `main`. `main` holds project documentation,
  tooling, and notes that must never reach `/config`.
- Never merge `main` into this branch for the same reason.
- `main` is untouched by this work. All deployment work is isolated to
  `ha-deploy`.

## Current state

| | |
|---|---|
| Production dashboard baseline | **Present** — `dashboards/deez_smart_home.yaml` |
| Live deployment | **Has not occurred** |
| `configuration.yaml` | **Deliberately not created or modified** |
| `secrets.yaml` | Not created (and gitignored) |
| Automations / scripts / scenes | Not imported — see `DEPLOYMENT_BLOCKERS.md` |
| Themes | Not imported — `themes/` is a reserved empty path |

### The dashboard baseline

`dashboards/deez_smart_home.yaml` contains the **imported production Deez
Smart Home dashboard baseline** — the live dashboard configuration, taken
verbatim from Home Assistant's Raw configuration editor and committed
unmodified apart from one sanitisation pass (below).

It is 32 views (12 subviews), 130 distinct entity IDs, 113 `card_mod`
blocks, `kiosk_mode`, five per-view themes, Mushroom cards, six
`custom:webrtc-camera` cards, and the English/Chinese toggle — preserved
as-is. **This file is the rollback point.** Treat it as production: no
redesign, no refactor, no reformatting. Changes go in as small, reviewable
diffs against it.

### Sanitisation applied

Two hardcoded utility account numbers were replaced with references to
`input_text` helpers the dashboard already uses for that purpose in its
Bills entry form. No new entity IDs were introduced.

The electricity **NMI** and gas **MIRN** remain hardcoded — no existing
entity holds them. See `DEPLOYMENT_BLOCKERS.md` for why that was left
alone rather than worked around.

## Validation status

Be precise about what has and has not been checked. The dashboard has
passed every check this repository can run, and **no check that requires
Home Assistant itself has been run at all.**

### Verified (repository-side, static)

| Check | Result |
|---|---|
| YAML syntax | Parses as one valid YAML document |
| Duplicate keys | None (strict duplicate-key loader) |
| Navigation integrity | All 32 in-dashboard `navigation_path` targets resolve to real view paths; zero dangling links |
| Repository structure | Only intended files tracked; no `.storage/`, databases, logs, backups or keys |
| Secret scan (static) | No credentials, tokens, passwords, private keys, private URLs, hosts or IPs |
| Baseline preservation | View count, entity IDs, navigation, card types, themes, `kiosk_mode` and `card_mod` verified unchanged against the pre-sanitisation file |

### NOT yet verified

None of the following has been done, and nothing in this repository can do
it. Each requires the live Home Assistant instance.

| Not verified | Why it matters |
|---|---|
| **Home Assistant schema validation** | HA's own config check has never been run. Valid YAML is not the same as valid Lovelace config. Card option names and structures are unchecked. |
| **Existence of every entity on the live instance** | The 130 entity IDs came from the live dashboard, but none has been confirmed against the entity registry. The available connector returns no `entity_id` values at all. |
| **Custom card / resource availability** | `custom:mushroom-*` and `custom:webrtc-camera` must be installed and registered as Lovelace resources. Unverified from here. |
| **Frontend rendering** | No view has been loaded in a browser. Template errors, layout breakage and card-mod CSS regressions would only appear there. |
| **Live deployment behaviour** | Nothing has been deployed. How this file interacts with the live instance is untested — and see the dashboard-mode blocker in `DEPLOYMENT_BLOCKERS.md`. |

**Do not read "validation passed" as "safe to deploy unattended."** It
means the file is well-formed and internally consistent, nothing more.

## Files on this branch

| Path | Purpose | Parsed by HA? |
|---|---|---|
| `dashboards/deez_smart_home.yaml` | Production dashboard baseline | See dashboard-mode blocker |
| `themes/.gitkeep` | Reserved deployment path for theme YAML | No |
| `.gitignore` | Blocks secrets, `.storage/`, databases, logs, backups, keys | No |
| `README.md` | This file | No |
| `DEPLOYMENT_BLOCKERS.md` | What still blocks deployment and how to clear it | No |

## Rules for adding anything to this branch

1. **Never commit a file here that has not been read from the live
   instance first.** Import, then commit — never author from inference.
   For `configuration.yaml` in particular, read the live file, commit it
   verbatim as a baseline, *then* change it as reviewable diffs.
2. **Never reference an `entity_id` that has not been confirmed** in
   Developer Tools → States. A friendly name is not an entity ID.
3. **Never commit secrets.** Reference `secrets.yaml` by key only in files
   that support it; `secrets.yaml` itself stays out of git. Never commit
   `.storage/`, the recorder database, logs, or backups.
4. **Take a full backup before the first pull.** Settings → System →
   Backups, downloaded off-device.
5. **Validate YAML before committing**, and review the diff before pushing.
6. **Keep changes small and reversible.** A dashboard redesign is built as
   a separate candidate file and promoted once reviewed — never as an
   in-place wholesale replacement of a working production dashboard.

## Git Pull add-on notes

- Set the branch to `ha-deploy` explicitly. The add-on defaults to
  `main`/`master`, and `main` must never be pulled into `/config`.
- Keep `auto_restart: false` for now. Nothing on this branch currently
  requires a restart to take effect.
- Files present in this branch replace same-named files in `/config`.
  Files that exist only in `/config` are left alone.
- **Syncing this branch will not make the dashboard live.** Read the
  dashboard-mode blocker in `DEPLOYMENT_BLOCKERS.md` before assuming a
  pull deploys anything.
