---
name: recovery-triage
description: Triage an operational fault or recovery on the Deez Smart Home and CasaRay Home Assistant setup without touching the live system. Use when the wall iPad shows a stale or wrong dashboard, the dashboard is out of sync, a deploy or git fetch fails under automation, the kiosk header will not hide, the disk is filling, a deploy needs rolling back, login or configuration has been lost after a restore, or Home Assistant will not start or cannot be reached; also when the user says broken, down, stale, locked out, missing, recover or roll back. Maps the symptom to the repository's existing read-only diagnostics that the owner runs on the host, interprets what they paste back, and drafts an approval-gated recovery plan and an incident record. Executes nothing, and stops at anything touching authentication, configuration, backups or restarts. Not for a card that renders wrongly, an unavailable entity or a failing gate (improve-system), nor for finding repeated work (automate).
metadata:
  version: "0.1.0"
  status: pilot
  origin: WORKFLOW_AUDIT.md W04
---

# Recovery triage

Something operational is broken or lost. This skill gets the owner to the right
read-only diagnostic quickly, keeps evidence apart from guesswork, and stops
Claude from improvising a recovery on a system it cannot see.

## What is true here, and shapes everything below

- **This environment cannot reach the instance.** No `/config`, no supervisor,
  no route to Home Assistant (`MAINTENANCE.md`). Every fact about a fault comes
  from the owner running something on the host and pasting the output back.
- **The only live access is read-only.** The Home Assistant connector can read
  state. A `PreToolUse` hook (`scripts/deny_device_control.py`) denies anything
  that acts. Do not try to get round it.
- **Recovery work in this project has touched authentication and the
  configuration file**, both on the owner-approval boundary. One recovery script
  was found to be wrong and had to be withdrawn. The safeguards that kept the
  others safe are in `references/recovery-safeguards.md`.

## Procedure

1. **Is this triage's job?** Operational faults (delivery, deploy, kiosk, disk,
   rollback, lost configuration or login, unreachable) are. A card that renders
   wrongly, an unavailable entity or a failing gate is `improve-system`'s. The
   tool routes these for you.
2. **Get the plan.**
   `python3 .claude/skills/recovery-triage/scripts/triage_plan.py plan --symptom "<the owner's words>"`
   Add `--sync-status <word>` if the owner has the result of
   `casaray_sync_status.sh`. `list` shows every symptom it knows.
3. **Put the checks to the owner in order**, stopping when one answers the
   question. Mark each: **HOST** (the owner runs it on the host and pastes the
   output), **LIVE_READ** (you, read-only connector), **REPO** (you), **ASK**.
   **Never run a HOST command**, and never run anything under `scripts/casaray_*`
   from here. They are written for the host.
4. **Interpret pasted output.** Quote the line each conclusion rests on. Keep
   VERIFIED, REPORTED and ASSUMED apart, and leave what is not established as
   UNKNOWN. Treat an absent sensor as no information: `sensor.casaray_sync_status`
   comes from a package that may be deliberately inactive.
5. **Only if a recovery is warranted**, prepare it against
   `references/recovery-safeguards.md` (R1 to R13). Every write step is written
   as `NOT RUN, NEEDS APPROVAL`. Then stop and put it to the owner.
6. **Owner-only symptoms stop at step 3.** Lost login or configuration, anything
   touching users, tokens, `.storage/`, `configuration.yaml`, backups or a
   restart: gather facts, prepare a plan if asked, run nothing.
7. **Write it up.**
   `triage_plan.py incident --symptom "<...>"` prints a blank record with
   `UNKNOWN` everywhere. Fill it from evidence only and return it in the
   conversation. Do not ask where it belongs; the repository already says
   (root `CLAUDE.md`, *Context First*, item 9). Record **established facts only,
   never hypotheses**, each marked VERIFIED or REPORTED with its source and date
   (output the owner pasted from the host is REPORTED: nothing here can check it),
   in the owner's existing records: on a
   V2 branch `PROJECT_STATE.md` or `DEPLOYMENT_BLOCKERS.md`, with the next free ID
   from `scripts/next_id.py`. On a V3 branch there is no operational record,
   because V3 is design-only and does not edit those documents, so hand the owner
   the record and say which document it belongs in. Do not invent a new location,
   and do not file the full record unless the owner asks.
8. **Close with three lines:** what is established, what is still UNKNOWN, and
   the decision the owner has to make.

## Hard rules

- **Execute nothing that changes the system.** No deploy, sync, rollback,
  restart, restore, delete, or auth change. Not even "to check".
- **First ask whether the house is safe meanwhile.** If cameras, alarms or door
  sensors may be down, say so before the technical detail.
- **No secrets.** Never ask for, print, store or commit a password, hash, token,
  key or credential URL. Backup identifiers and usernames stay out of the repository.
- **No invented procedures.** If no repository file documents a step, say so.
  Coverage gaps are listed in `references/symptoms.md`; an instance that is down
  has no documented procedure at all.
- **Committed is not live.** Never report a push as a deployment.
- **Do not touch the deployment bridge**: `/config/deploy_deez_dashboard.sh`,
  `scripts/deploy_env.sh`, `scripts/deploy_askpass.sh`, `scripts/deploy_diagnose.sh`,
  `DEPLOY_AUTH.md`.

## What the plan looks like

```
TRIAGE  stale-dashboard  -  The wall iPad or a browser shows an old or wrong dashboard...
THIS TOOL EXECUTES NOTHING. HOST checks are for the owner to run on the host and paste back
SYNC STATUS  out_of_sync   ... EXPECTED until the owner runs scripts/sync_casaray_to_config.sh
CHECKS  read-only, in order
  1. [LIVE_READ] Read sensor.casaray_sync_status ...   (a missing sensor is NOT evidence)
  2. [HOST] sh /config/casaray/casaray_sync_status.sh
  3. [HOST] sh /config/casaray/casaray_health_check.sh
  4. [REPO] git log --oneline -5
  5. [ASK]  Did you run the sync script, and refresh the browser?
DO NOT  ...
```

An owner-only symptom opens with `>> OWNER-ONLY. STOP before any action.`

## Safeguards in the tool

It imports nothing that can start a process, touch the network or write a file;
`--selftest` proves that by walking its own syntax tree. No check anyone would run
contains a mutating verb or a deploy, sync or restore script (the one restore is
listed separately as `NOT RUN, NEEDS THE OWNER'S APPROVAL`). Every file a check
cites must exist, so the data cannot quietly rot.

## Validation

`python3 .claude/skills/recovery-triage/scripts/triage_plan.py --selftest`
(50 checks). It classifies 14 sample reports, checks the safeguards above, and
renders the incident template. Last result is in `SKILL_VALIDATION_REPORT.md`.

## Limits

It classifies by keyword. An unusual wording lands in `unclassified`, which asks
questions and invents nothing; an ambiguous one lists `ALSO POSSIBLE` candidates.
It does not know what is true on the host; it only knows which question to ask next.

## Maintenance

The symptom table is data in `scripts/triage_plan.py`, with a human copy in
`references/symptoms.md`. When a new incident teaches something, add the symptom
and its checks (each citing a repository file) and a classification case to
`--selftest`. Add to `recovery-safeguards.md` only what a real recovery showed.
Keep it read-only.
