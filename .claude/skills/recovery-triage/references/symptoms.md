# Symptom map

The human copy of `SYMPTOMS` in `scripts/triage_plan.py`. The script is the
working version; this explains it. Every check names the repository file that
documents it, and `--selftest` fails if a cited file goes missing.

Where a check runs:

| Where | Meaning | Who |
|---|---|---|
| **REPO** | Reading a file or git history in this checkout | Claude |
| **LIVE_READ** | The read-only Home Assistant connector (`GetLiveContext`). The device-control guard denies anything that acts | Claude |
| **HOST** | A shell on the Home Assistant host (Terminal & SSH add-on, or a `shell_command`) | **The owner.** This environment has no `/config` |
| **ASK** | A question for the owner | Claude asks |

| Symptom | First check | Then | Never |
|---|---|---|---|
| **stale-dashboard**: the iPad or a browser shows an old or wrong dashboard | Is the entity `sensor.casaray_sync_status` present (it may not be: the package that defines it is not in the 2026-09-05 export and may be inactive) | `casaray_sync_status.sh`, `casaray_health_check.sh`, `git log`, and ask whether the sync step and a browser refresh were done | tell the owner a push is live; run the sync script yourself; suggest a restart |
| **deploy-fetch-fails**: the unattended deploy cannot fetch or apply | `deploy_diagnose.sh` **through a `shell_command`**, not the terminal | paste of the sanitised deploy log; `DEPLOY_AUTH.md` steps 1 to 3 | touch the deployment bridge; print or store a credential |
| **kiosk-header**: HA's own header or sidebar still shows | `casaray_kiosk_diagnose.sh` (read-only) | `DR-015` | edit YAML to work around a missing frontend resource; re-add kiosk configuration removed in `fc208cd` |
| **disk-pressure**: storage filling | `casaray_disk_report.sh` (no redirect if nearly full) | | delete, truncate, purge or VACUUM; remove backups |
| **bad-deploy-rollback**: broken after a deploy, previous wanted | `casaray_rollback.sh --list` | `casaray_health_check.sh`; the rehearsed procedure in `docs/ROLLBACK_DRILL.md` | `git reset` or force-push; run the restore yourself |
| **lost-config-or-login**: locked out, config or registration lost, helpers unavailable after a restore | **STOP.** Ask what the owner can still reach | the recovery branch's read-only Phase 0 diagnostic and latest plan (not in this checkout) | run anything; ask for or store a password, hash, token or key; use a withdrawn script |
| **ha-unreachable**: will not start or cannot be reached | ask what the browser shows and what changed last | `casaray_health_check.sh` if any host shell works | invent Supervisor or OS commands; suggest a restart or restore first |
| **card-renders-wrong**, **entity-unavailable**, **gate-fails** | not an operational fault: use **`improve-system`** | | |

## `casaray_sync_status.sh`, one word

From `sync_status()` in `scripts/casaray_common.sh`:

| Word | Meaning |
|---|---|
| `synced` | repository copy and live file are byte-identical (`cmp`). The fault is not delivery |
| `out_of_sync` | they differ. **Expected after any push** until the owner runs `scripts/sync_casaray_to_config.sh` |
| `missing_repo` | the host clone has no dashboard file: the delivery chain is broken at the source |
| `missing_live` | `/config/dashboards/casaray_v2.yaml` is absent: not installed, or lost. Treat as owner-only |

## Coverage gaps, stated plainly

- **An instance that is down** has no repository procedure. The nearest thing is the recovery branch's Phase 0 diagnostic.
- **Lost configuration or login** is documented only on the recovery branch, in commit messages and scripts that are not in this checkout.
- **Nothing here can verify a HOST command's result.** Everything about the live system is the owner's word, and the record says REPORTED, not VERIFIED.

## Adding a symptom

1. Add a `Symptom` to `SYMPTOMS`, with at least one keyword that distinguishes it.
2. Every check cites a repository file in `source` and `verify_path`. If no file documents the step, do not add the step.
3. Add a classification case to `--selftest`, run it, and update this table.
