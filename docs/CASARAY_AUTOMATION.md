# CasaRay maintenance automation

Deployment, validation, backup, rollback, health checks and device-health
watchdogs, so none of it needs a terminal.

Built 2026-09-15. **Everything here is additive and reversible.** No existing
dashboard, entity, service call, theme or navigation target was changed to make
it work, and nothing in it restarts Home Assistant.

---

## Install

One command on the Home Assistant host, in the Terminal & SSH add-on:

```sh
git -C /config/deez_repo pull
sh /config/deez_repo/scripts/casaray_onboard.sh
```

Add `--dry-run` first if you want to see every action without any of them
happening. `--uninstall` removes the installed files again and keeps the
backups.

The onboarding script inspects the host, backs up anything it is about to
replace, installs, parses the package, runs `ha core check`, and **stops and
restores if the check fails**. It never restarts Home Assistant.

### After installing

1. **Reload** — Developer Tools → YAML → Input Booleans, Input Numbers,
   Template Entities, Scripts, Automations.
2. **Restart** — Settings → System → Restart Home Assistant.
   Required once, and only once. `shell_command` and `command_line` are read at
   startup and cannot be reloaded, so the three buttons and
   `sensor.casaray_sync_status` stay dead until a restart. Everything else
   works after a reload.
3. **Verify** — `sh /config/casaray/casaray_health_check.sh`

---

## What it installs

| Where | What |
|---|---|
| `/config/casaray/` | five shell scripts, mode 755 |
| `/config/packages/casaray_automation.yaml` | helpers, sensors, scripts, automations |
| `/config/dashboards/backups/` | pre-deploy dashboard backups |
| `/config/casaray_maintenance.log` | every deploy, rollback and prune |
| `/config/casaray/backups/` | copies of anything onboarding replaced |

Nothing is written anywhere else.

---

## The pieces

### Safe deploy

`casaray_safe_deploy.sh` wraps the deploy you already have — it calls
`/config/deploy_casaray.sh` if that exists, otherwise the repo's
`sync_casaray_to_config.sh`. **Neither is modified.** The wrapper adds:

1. **pre-flight** — source exists and parses. Fails here and nothing is touched.
2. **backup** — timestamped copy of the live dashboard.
3. **deploy** — the existing process, unchanged.
4. **post-flight** — live exists, live parses, `ha core check` passes.
5. **rollback** — any post-flight failure restores the backup and verifies the
   restored file parses.
6. **prune** — keeps the newest 30 pre-deploy backups.

```sh
sh /config/casaray/casaray_safe_deploy.sh            # deploy what the clone has
sh /config/casaray/casaray_safe_deploy.sh --pull     # git pull ha-deploy first
sh /config/casaray/casaray_safe_deploy.sh --dry-run  # check only
```

Exit codes: `0` deployed or already identical · `1` failed and rolled back ·
`2` refused before changing anything.

### Nightly deploy

`automation.casaray_nightly_safe_deploy` runs the wrapper at **03:30**, gated on
`input_boolean.casaray_auto_deploy` (**on** by default). It notifies **only on
failure**, and by the time it notifies the previous dashboard is already back.

**To disable:** turn off `input_boolean.casaray_auto_deploy`. That is the whole
procedure — nothing is removed, and Deploy Now still works.

### Health check

```sh
sh /config/casaray/casaray_health_check.sh
```

Reports repo present, source present and parsing, live present and parsing,
sync status, backup count, `ha core check`. Exits non-zero if any required
check fails. `out_of_sync` is a **warning, not a failure** — a pending change
between a push and 03:30 is normal.

### Manual controls

Three scripts, so each is an entity you can put on a tile or call from Assist:

| Entity | Does |
|---|---|
| `script.casaray_deploy_now` | safe deploy, then a notification either way |
| `script.casaray_health_check` | health check, result as a notification |
| `script.casaray_rollback_previous` | restore the newest pre-deploy backup |

### Out-of-sync detection

`sensor.casaray_sync_status` → `synced` · `out_of_sync` · `missing_repo` ·
`missing_live`, refreshed every five minutes.
`binary_sensor.casaray_out_of_sync` turns it into a problem flag, and a
notification appears only after **ten minutes** of disagreement. It clears
itself the moment they match again.

### Low battery

`sensor.casaray_low_batteries` counts every sensor Home Assistant labels
`device_class: battery` that is below `input_number.casaray_battery_threshold`
(default **20%**). **Discovered dynamically** — no hard-coded list, so a new
battery sensor is covered the day it appears.

Attributes: `low` (names), `detail` (names with levels), `not_reporting`
(batteries with no readable level — counted separately, never as 0%),
`threshold`.

One notification a day at **09:00** if any are low. Clears automatically when
the count reaches zero.

### Internet watchdog

Reads `binary_sensor.eero_wan_status`.

- `off` for **2 minutes** → "Internet is down"
- `unknown`/`unavailable` for **5 minutes** → "Internet state unknown", which
  is a different claim: the sensor is not reporting, so the state cannot be
  confirmed either way.
- back to `on` → notification dismissed.

One fixed `notification_id`, so repeats replace rather than stack.

### Powerpal and Fronius stale data

`binary_sensor.casaray_powerpal_stale` and `binary_sensor.casaray_fronius_stale`
go `on` when their sensor is unavailable/unknown, or has not reported for
**20 minutes**. They use `last_reported` where the core provides it and fall
back to `last_updated`: `last_changed` would flag a healthy sensor holding a
steady figure.

The notification needs the flag held for a further **5 minutes**, so a brief
integration hiccup stays quiet. It clears when **both** are healthy.

### Unavailable-entity spike

**Disarmed by default, deliberately.** `sensor.casa_offline_devices` counts
unavailable **entities**, not devices (`CR-200`). The 2026-09-05 export had 232
unavailable and 86 unknown out of 970, so a plausible-looking threshold like 10
would fire immediately and never clear. The build environment cannot read the
live value, so rather than guess a number that spams, the automation is skipped
while `input_number.casaray_offline_threshold` is `0`.

**To arm it:** read `sensor.casa_offline_devices` in Developer Tools → States,
then set the helper to roughly 20% above that resting value. The alert then
needs the count held above it for **15 minutes**, and clears when it drops.

---

## Backups

| Kind | Where | Pruned by |
|---|---|---|
| Pre-deploy dashboards | `/config/dashboards/backups/casaray_v2.yaml.predeploy.<ts>` | this suite, newest 30 kept |
| The sync script's own | `/config/dashboards/casaray_v2.yaml.bak.<ts>` | **nothing here** |
| Onboarding replacements | `/config/casaray/backups/` | **nothing here** |
| Home Assistant's own backups | wherever HA keeps them | **nothing here** |

Pruning is anchored to one directory *and* one filename prefix. It cannot reach
anything else even if `BACKUP_DIR` were pointed somewhere careless.

---

## Manual recovery

**The dashboard is broken and you want the previous one back:**

```sh
sh /config/casaray/casaray_rollback.sh --list     # see what is available
sh /config/casaray/casaray_rollback.sh            # restore the newest
sh /config/casaray/casaray_rollback.sh casaray_v2.yaml.predeploy.20260915-033001
```

It saves the current file before overwriting it, and refuses to restore a
backup that does not parse. Refresh the browser afterwards — no restart.

Or press `script.casaray_rollback_previous`.

**Everything is wedged and you want it all gone:**

```sh
sh /config/deez_repo/scripts/casaray_onboard.sh --uninstall
```

Then restart Home Assistant. Backups are kept.

**The plain, no-scripts path**, if none of the above is available:

```sh
cp /config/dashboards/backups/casaray_v2.yaml.predeploy.<newest> \
   /config/dashboards/casaray_v2.yaml
```

---

## Known limitations

- **A restart is needed once.** `shell_command` and `command_line` are only
  read at startup. Until then the three buttons and the sync sensor do not
  exist; the helpers, template sensors and automations work after a reload.
- **The build environment cannot verify any of this live.** It has no
  `/config`, no supervisor and no route to the instance. Everything below under
  *Validation* was proven against a simulated host, not the real one.
- **The offline-spike alert ships disarmed** — see above. It is the one feature
  that needs a number only the live instance can supply.
- **`ha core check` is skipped where there is no supervisor CLI.** The scripts
  say so rather than pretending it passed.
- **`--pull` does a hard reset** to `origin/ha-deploy`. Local edits in
  `/config/deez_repo` would be lost, so it is off by default.
- **Nothing notifies through a phone.** Everything uses
  `persistent_notification`, which is visible in the Home Assistant UI. Mobile
  push would need the companion app's notify service, which is a separate
  decision.
- **The nightly deploy does not `git pull` by default.** It deploys whatever
  the clone already has. Add `--pull` to the `shell_command` in the package if
  you want it to fetch first.

---

## Validation

Run in the build environment against a simulated `/config`, 2026-09-15:

| Check | Result |
|---|---|
| `sh -n` on all six scripts | pass |
| `scripts/yaml_check.py packages/casaray_automation.yaml` | pass, no duplicate keys |
| `scripts/ha_validate.sh` (8 sections) | **PASSED** |
| health check, out-of-sync live file | exit 0, warns correctly |
| safe deploy `--dry-run` | exit 0, nothing written |
| safe deploy, real | exit 0, live matched source, backup made |
| safe deploy, already identical | exit 0, no-op |
| **unparseable source** | exit 2, live untouched |
| **deploy writes unparseable live** | exit 1, restored **byte-for-byte**, restore verified |
| rollback `--list` and restore | exit 0, saved current first |
| prune with 40 backups | 30 kept; sync script's `.bak.*` and an unrelated backup untouched |
| sync status: differing / identical / live missing | `out_of_sync` / `synced` / `missing_live` |
| onboard `--dry-run` | no writes |
| onboard, real | five scripts at mode 755, package installed, YAML parsed |
| onboard `--uninstall` | clean, backups kept |

Two real bugs were found by running it rather than reading it, and both are
fixed: `set -e` aborted on `ha_core_check; rc=$?` before the result could be
captured, and the deploy child did not inherit overridden paths.

**Not validated, because it cannot be from here:** `ha core check` against the
real config, whether the package's entities actually appear, and whether the
`command_line` sensor runs under Home Assistant's own shell.
