# CasaRay restore plan — 12 Oct 2026

**PLAN ONLY. Nothing in this file has been run.** Branch `recovery/phase0-diagnostics`.
Every command is for the owner to run at the Green's console (after `login`) and every
step that writes is marked **[APPROVAL]**. No secret is printed by anything here.

## 0. What this plan is built from

| Source | What it gave |
|---|---|
| `RECOVERY_2026-09.md` (29/09) | the 25/09 loss, what was repaired, what stayed open |
| `git log --all` | no commit on any branch after 29/09 15:12 UTC |
| Owner statements | login worked until the Core update; `ba94d3a0` (30/09) exists and reads; very little work since the last recovery |

**Not seen by anyone in this session:** any backup, `ha backups list`, any log, any
`.storage` file. Existence and contents of all three backups are **unverified** until
the gates in section 3 are run.

## 1. Timeline

| When (UTC unless noted) | Event | Source |
|---|---|---|
| ~25/09 | files removed from `/config` during a recovery attempt; default `configuration.yaml` regenerated | record |
| 25/09 | backup `e6cc88bd`, taken **after** the loss | record |
| 28/09–29/09 | safety backup `b0206554`, taken **before any repair** | record, `fix_owner_login.sh` |
| 29/09 03:20 | `cc8e049` owner password store rebuilt with HA's native tool | git |
| 29/09 | time zone and location restored by the owner through onboarding | record |
| 29/09 15:12 (= 30/09 01:12 AEST) | last repo commit, `59c3b92` | git |
| 30/09 | backup `ba94d3a0` | owner (not in any repo file) |
| unknown, before 12/10 | Core update, then restart/reset; login fails | owner |

## 2. Backup candidates

| Slug | Date | Taken relative to | Password store | Verdict |
|---|---|---|---|---|
| `ba94d3a0` | 30/09 | **after** the 29/09 owner repair | expected present — **unverified** | **Recommended**, once gates pass |
| `b0206554` | 28–29/09 | before any repair | absent (that is why it was taken) | fallback; needs R1, R2, R3 |
| `e6cc88bd` | 25/09 | after the loss | absent | fallback; needs R1, R2, R3 |
| `core_<old version>` | the update day | immediately before the Core update | would be present | **better than all three if it exists** — look for it (G4) |

Backups from before 25/09 need the encryption key that was lost with `.storage/backup`.
If the owner ever downloaded the **emergency kit**, those backups may be openable, and
they may hold the original `configuration.yaml`. Ask.

**What no backup can give back:** the original `configuration.yaml` was lost on 25/09,
before all three. Restoring any of them returns a default `configuration.yaml`. The
helpers, people and dashboard registration that lived in it are replay work (section 6).

## 3. Gates — read-only, run on every candidate; all must pass

**G0 existence** — path convention from the earlier scripts.
```sh
ha backups list | grep -E 'slug:|name:|date:|type:|protected'
for s in ba94d3a0 e6cc88bd b0206554; do stat -c '%y %s %n' /mnt/data/supervisor/backup/$s.tar; done
```
Pass: the slug is listed, the file exists, size is plausible (not a few KB).

**G1 archive integrity** — reads the whole file; changes nothing.
```sh
tar -tf /mnt/data/supervisor/backup/ba94d3a0.tar >/dev/null && echo OUTER_TAR_OK
sha256sum /mnt/data/supervisor/backup/ba94d3a0.tar    # record the hash; compare after any copy
ha backups info ba94d3a0                               # type, date, protected, Core version, contents
```
Pass: `OUTER_TAR_OK`, `protected` false, `homeassistant` included, Core version noted.

**G2 contents** — the existing read-only inspector, pointed at the candidate.
```sh
sh /tmp/get.sh inspect_backup.sh
sh /tmp/inspect_backup.sh /mnt/data/supervisor/backup/ba94d3a0.tar
```
Pass criteria, from its own section numbers:
- 1: `protected = False`; note `HA version` and `database excluded`
- 2: `.storage/auth_provider.homeassistant`, `core.config`, `onboarding`, `auth`, `person`, `core.config_entries` all **PRESENT**
- 4: owner line reads `owner=True ... in backup provider=True`; `HA-login credential IDs identical in backup = True`; user IDs: backup set matches live
- 5: `onboarding done: backup = True`; `time_zone` is **not UTC**; `location set = True`
- 6: informational — whether `casaray-v2` is registered and `packages` is included
- no `!! cannot read` line anywhere

**G3 readable is not healthy** — [APPROVAL], optional but recommended before an irreversible step.
Extract the backup's `homeassistant.tar*` into a **new empty scratch directory** (mode 700,
outside `/config` and `supervisor/`), then run Home Assistant's own config check against it
in a throwaway container, the same pattern `fix_owner_login.sh` uses:
```sh
docker run --rm -v <scratch>/config:/config --entrypoint python3 "$(docker inspect -f '{{.Config.Image}}' homeassistant)" -m homeassistant --script check_config -c /config
```
Pass: no errors. **Delete the scratch directory afterwards — it holds token copies.**
Needs free space of about twice the backup size (`df -h /mnt/data`).

**G4 look for a pre-update backup**
```sh
ha backups list | grep -E 'name:|date:' | grep -i core_
```
If one is dated at or after 30/09, run G0–G3 on it first. It is the closest thing to
"the last working state".

**G5 quantify work done after the candidate** — read-only; the backup file is the time reference.
```sh
find /mnt/data/supervisor/homeassistant -xdev -type f -newer /mnt/data/supervisor/backup/ba94d3a0.tar \
  ! -path '*/deez_repo/*' ! -path '*/_recovery/*' ! -name '*.db' ! -name '*.db-*' ! -name '*.log*' \
  | while read f; do stat -c '%y %s %n' "$f"; done | sort | head -200
```
Expect noise: the Core update rewrites many `.storage` files. What matters is anything
under `packages/`, `dashboards/`, `themes/`, `automations.yaml`, `scripts.yaml`, and any
`.storage/input_*`, `.storage/lovelace*`, `.storage/person`.

**Decision:** all of G0–G2 (and G3 if approved) pass on the same slug → that slug is the
restore point. If a `core_*` backup passes, prefer it. If `ba94d3a0` fails, go to
`b0206554` and plan R1–R3 as mandatory.

## 4. Work after the backup

- **Git:** none. Every branch tip is at or before 29/09 15:12 UTC (`ha-deploy` `18a4e5d`,
  25/09; recovery `59c3b92`, 29/09). The repo is unaffected by a restore.
- **On the device:** unknown. G5 measures it. Known candidates: the Core update itself,
  and anything the owner changed in the UI since 30/09.
- **History:** if the backup includes the recorder database, restoring replaces it, so
  about 12 days of history and energy statistics (30/09 to 12/10) are lost.

## 5. Safe restore procedure

1. **P0 freeze.** Change nothing in Home Assistant. Do not run `fix_owner_login.sh finish`,
   `recover_login.sh` or `deploy_casaray.sh`. Do not install the recovered package.
2. **P1 copy the candidates off-device first** (read-only on the source), through the
   Samba `backup` share to the laptop. Compare `sha256sum` before and after. Reason:
   automatic-backup retention can delete older automatic backups when a new one completes,
   and `ba94d3a0` may be one. Keep the copies out of Git — they hold secrets.
3. **P2 preserve the present state** [APPROVAL]. Same form the earlier scripts use:
   `ha backups new --name "pre-restore-2026-10-12"`, confirm with `ha backups info <slug>`,
   then copy it off-device too. This is a new backup; nothing existing is overwritten.
4. **P3 gates G0–G5**, then **STOP**. Report the results. The owner approves a slug.
5. **P4 restore** [APPROVAL — explicit, naming the slug]. By console, because the login is
   broken: `ha backups info <slug>` first, then `ha backups restore <slug> --homeassistant`
   (Home Assistant component only; add-ons are not touched). Allow up to 15 minutes. Do
   not interrupt it.
6. **P5 verify** with section 8.
7. **P6 replay** with section 6, one approval per step.

**Rollback of the restore:** `ha backups restore <pre-restore slug> --homeassistant`. That
returns to today's state, including the login failure; it is the escape hatch, not a fix.

## 6. Replay checklist

| # | Step | Source | Needed when | Approval |
|---|---|---|---|---|
| R1 | Owner password store: `fix_owner_login.sh check` then `run` | `cc8e049`, 29/09 | only if the restored `.storage/auth_provider.homeassistant` is missing | yes — stops Core |
| R2 | Time zone, location, units | owner, UI (record) | only if restored `core.config` says UTC | owner |
| R3 | Register CasaRay (`lovelace: dashboards: casaray-v2`) | `casaray_config_block.yaml` `490afac`; `deploy_casaray.sh` `59c3b92` | if the restored `configuration.yaml` lacks it | yes — restart |
| R4 | Dashboard and theme on disk equal `ha-deploy` `18a4e5d` | `sync_casaray_to_config.sh` | compare `sha256sum` first; run only if different | yes |
| R5 | Helpers and people: `input_boolean.chinese_dashboard`, `input_boolean.elec_bill_paid`, `person.raymond_du`, `person.ai_q_huang`, `person.vinh_du` | `deploy_casaray.sh` health list | any `unavailable` after restore; their settings are **not in the repo** | owner |
| R6 | Passwords of the other three users | record "Still open" | always | owner decision: `hass --script auth add` (keeps IDs) or recreate (new IDs) |
| R7 | New backup encryption key and emergency kit | record "Still open" | always | owner |
| R8 | Deploy bridge `shell_command` | record "Still open" | protected file; only on explicit instruction | yes |
| R9 | Automation package `packages/casaray_automation.yaml` | — | **not part of this replay** | separate decision |
| R10 | Core update | — | defer; read the 2026.10 breaking changes first; turn on backup-before-update | owner |

**R3 and R9 collide.** The prepared block also contains `homeassistant: packages:
!include_dir_named packages`. Including it loads the whole package: 12 automations
(including the 03:30 deploy and a start-up health check), 3 scripts, 3 helpers and 3
shell commands. So `deploy_casaray.sh apply` must not be used as written while the
package must stay inactive. Register the dashboard alone, validate that variant (it was
never validated; only the combined block was, and on Core 2026.2.3), and add the
packages line later by its own decision. Note `chinese_dashboard` is **not** defined in
the repo's package, so the helper has to come from the restore or from R5.

## 7. Compatibility risks

1. **Core version.** Unverified: whether restoring the Home Assistant component also
   reinstalls the Core version recorded in the backup. Read `ha backups info` and plan for
   both outcomes. Older data into a newer Core migrates forward; the risky direction
   is the reverse.
2. **Sessions and tokens.** Restoring `.storage/auth` removes every token created after
   the backup: phone and tablet app sessions, and any integration using a newer token,
   possibly including the assistant's own Home Assistant connection.
3. **Recorder database.** Replaced by the backup's, or kept if the backup excluded it
   (`database excluded` in G2 section 1).
4. **Devices and entities added or renamed since.** The restored registries won't know
   them. New devices come back as new entity IDs, and dashboards reference IDs.
5. **Zigbee.** `zigbee.db` reverts with the config. Devices paired since need re-pairing.
6. **Add-ons are not restored** by `--homeassistant`. Their data stays newer than the
   restored config entries.
7. **Mobile-app registrations** and the **Cloud** link made after the backup are missing.
8. **Encrypted backups.** `ba94d3a0` must be unencrypted; the inspector requires it.
9. **Core 2026.10 itself.** Reportedly 22 breaking changes (secondary source; official
   notes unreachable from the sandbox). Re-updating without reading them repeats today.
10. **Deploy credentials** (`.deez_deploy.env`, `deez_repo` clone state) revert to the
    backup's. `get.sh` depends on them.

## 8. Post-restore verification checklist (read-only)

- [ ] `ha core info`: running; the version matches what G1 recorded or is understood
- [ ] `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8123/api/` returns **401** (up, auth required)
- [ ] `ha core logs | grep -iE 'error|critical|Traceback|Unable to find configuration|Creating default' | tail -30` is clean or explained; not in recovery or safe mode
- [ ] `.storage/auth_provider.homeassistant` exists with the backup's size and date
- [ ] Owner logs in on the **laptop** and the **iPad** (owner action)
- [ ] `core.config`: time zone is not UTC; location set; onboarding done
- [ ] Integrations loaded with no setup failures; entity count near the 970 of the 05/09 export
- [ ] Helpers and people above are not `unavailable`
- [ ] Legacy **Deez Smart Home** dashboard opens (storage-mode, must survive)
- [ ] CasaRay: registered or not, as R3 intends
- [ ] **No** `automation.casaray_*` or `script.casaray_*` exist; `input_boolean.casaray_auto_deploy` absent
- [ ] Spot-check three Zigbee/Matter devices respond; energy sensors updating
- [ ] A fresh full backup is taken **after** login is confirmed, copied off-device and recorded
- [ ] Auto-update of Core stays off until R10 is decided

## 9. Unknowns

- Existence, dates and contents of all three slugs, and whether a `core_*` pre-update backup exists
- The exact time of `ba94d3a0` relative to the 29/09 repairs (a few hours either way)
- The Core versions before and after the update; what "reset" did
- Whether `/config/packages/` and `dashboards/casaray_v2.yaml` on the device match Git
- Whether an emergency kit exists for the pre-25/09 backups
