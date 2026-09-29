# CasaRay recovery record — September 2026

Branch `recovery/phase0-diagnostics`. Nothing here is on `ha-deploy`.

## What happened

During an attempt to recover CasaRay on ~25/09, several files under `/config`
were removed while Home Assistant was running. Home Assistant regenerated a
default `configuration.yaml` on the next start. Everything else survived:
integrations, device and entity registries, Zigbee, Matter, history, the
dashboard files and the git clone.

| Lost | Effect | Status |
|---|---|---|
| `.storage/auth_provider.homeassistant` | every password login rejected | **fixed** by `fix_owner_login.sh` (owner) |
| `.storage/core.config` | time zone UTC, location unset | **fixed** by the owner through onboarding (instance reports AEST, 29/09) |
| `.storage/backup` | encryption key for older backups gone | open, see below |
| `configuration.yaml` (original) | CasaRay unregistered; `packages/` not loaded, so its helpers and people went `unavailable` | **fix prepared**: `casaray_config_block.yaml` |

The 25/09 backup (`e6cc88bd`) was taken after the loss, so it holds none of
these files. The safety backup `b0206554` was taken before any repair.

## Why CasaRay is missing

CasaRay is a **YAML-mode** dashboard at url_path `casaray-v2`, registered in
`configuration.yaml`. That file is now the default and registers nothing.
`dashboards/casaray_v2.yaml` is still on disk; it just isn't registered.

The legacy **Deez Smart Home** dashboard is a **UI (storage-mode)** dashboard
at `deez-smart-home`. Its registration lives in `.storage` and survived. It
must **not** be added to `configuration.yaml`, because that would claim the
same url_path. `repair_login.sh` made that mistake and is withdrawn.

## The repair: `casaray_config_block.yaml`

Append it to `/config/configuration.yaml`. It restores two things:

1. `homeassistant: packages: !include_dir_named packages`, which reloads the
   helpers and people defined in `/config/packages/`.
2. `lovelace: dashboards: casaray-v2`, in YAML mode, from
   `dashboards/casaray_v2.yaml`.

Registering a new dashboard needs a Home Assistant restart.

### Offline validation (done)

- Home Assistant's own `check_config` (2026.2.3) on the default config plus
  the block, with the `ha-deploy` dashboard, theme and package: **pass**.
- The same check with no `packages/` folder: **pass**, so the block is safe
  whether or not the folder exists.
- Negative control, with the registration deliberately corrupted: **fails**
  and names the line, so the check really inspects the block.
- `scripts/ha_validate.sh` on `ha-deploy` `18a4e5d`: **passed**. 28/28 views,
  0 broken links, every entity in the export, no secrets.
- Pre-existing and not caused by this repair: HA's loader warns about a
  duplicate `ha-card-border-color` key in `themes/deez_your_name.yaml`. It is
  a warning, not an error.

### Needs the running Green (not yet verified)

- Whether `/config/packages/` still holds the helper and person definitions.
  If the helpers stay `unavailable` after the restart, they were defined
  directly in the lost `configuration.yaml` and must be rebuilt. Their
  entity IDs are in `docs/live/states_export_2026-09-05.txt`, but their
  settings (min/max/options) are not in this repository.
- Whether `/config/dashboards/casaray_v2.yaml` matches `ha-deploy`.
  It renders whichever version is on disk.
- Whether CasaRay renders on the iPad.

## Rollback

Remove the block, or restore the `configuration.yaml` copy taken before
editing, then check the configuration and restart. Last resort:
`ha backups restore b0206554 --homeassistant`.

## Still open

- **Encryption key** for backups taken before 25/09 (`.storage/backup` was
  lost). Set a new key in Settings → System → Backups and download the
  emergency kit.
- **The other three users' passwords.** Only the owner was restored. The
  People page's "Change password" will fail for them ("user not found"),
  because the password store has no entry for them. The native fix is the
  same tool, `hass --script auth add <username> <password>` with Core
  stopped, which needs the console. `fix_owner_login.sh` handles the owner
  only and now refuses to run, because the store exists. The alternative
  without the console is to delete and re-create those users in the UI, which
  gives them NEW user IDs; their person entities would need re-linking.
- **The deploy bridge** (`shell_command` in the lost config) is gone until
  it is re-added.
