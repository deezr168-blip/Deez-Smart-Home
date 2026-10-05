# Owner action queue

Things only the owner can do, or must approve. Everything else is in
`docs/AUTONOMOUS_BACKLOG.md` and is worked without asking. Each item says what
is needed, why, the risk, and what unblocks once it is done.

*State as of 2026-10-05, branch `autonomous/casaray-dev`. Live facts from the
owner that supersede earlier uncertainty: owner login works, CasaRay is visible
and navigates, some entities and helpers still read unavailable / No data.*

## A. Needed to finish recovery (live system)

### A1. Find out which helpers actually exist — **read-only, 2 minutes**

Open **Settings → Devices & services → Helpers**, or look at the new
**House health → Setup status** card once the dashboard is synced (A6). It
reports answered/total for seven helper groups.

- *Why:* about 110 helper entities (the language toggle, the bills board's
  paid flags, amounts, due dates and year totals) have **no definition in Git**.
  `docs/CASARAY_AUDIT.md` lists them. If they were YAML-defined in the lost
  `configuration.yaml`, they are gone; if they were UI helpers they survive.
- *Unblocks:* the whole Bills board (34 of 34 references need them), the
  language toggle, People.
- *Risk:* none.

### A2. Look for the backup emergency kit / encryption key

Backups taken before 25/09 are encrypted and `.storage/backup` (their key) was
lost. If you saved the emergency kit or key, an older backup holds the original
`configuration.yaml`, which is the only complete source for the helper
definitions. It is the single most valuable thing you can look for.

- *Do not paste the key into chat or Git.* Restoring from it is a console
  action; ask for the exact steps when you have it.

### A3. Set a new backup encryption key (Settings → System → Backups)

Download the new emergency kit and keep it outside Home Assistant.

### A4. Recreate the other three users' passwords

Only the owner's password was restored. Native fix needs the console
(`hass --script auth add <username> <password>` with Core stopped); the
alternative is delete-and-recreate in the UI, which gives **new user IDs** and
means re-linking their `person` entities. Credentials never go through chat.

### A5. Install the helper-boolean proposal — only if A1 says they are YAML orphans

`proposals/casaray_helper_booleans.proposed.yaml` re-creates the language
toggle and the six bill-paid flags (seven on/off helpers; nothing invented).
Its header says exactly what to check first, because installing it over
surviving UI helpers would create `_2` duplicates no card reads. Number, date,
text and select helpers are **not** proposed: their settings are not in Git.

### A6. Sync this branch's dashboard to the host — only after review and merge

`scripts/sync_casaray_to_config.sh` on the host. Committed is not deployed.
**Merging to `ha-deploy` is production if `input_boolean.casaray_auto_deploy`
is on:** `casaray_safe_deploy.sh` runs `git reset --hard origin/ha-deploy` in
`/config/deez_repo` and deploys at 03:30 (see `DECISION_LOG.md` D-004).

### A7. Re-add the deploy bridge (only if you want automated deploys)

The `shell_command` bridge went with `configuration.yaml`. `packages/` defines
`shell_command.casaray_*`, so loading packages brings it back, but it needs
`/config/casaray/*.sh` installed (`scripts/casaray_onboard.sh`). Leave
`casaray_auto_deploy` **off** until you have read D-004.

## B. Approvals the autonomous agent is not permitted to give itself

### B1. Delete the dead duplicate block in `scripts/ha_validate.sh`

- *Finding (confirmed):* lines 182–316 of `ha_validate.sh` on `ha-deploy`
  `18a4e5d` are a second, stale copy of the script body after its final
  `exit 1`, appended by the 25/09 commits `7309bd8`/`18a4e5d` instead of
  replacing the section they edited. The script runs correctly because bash
  parses lazily and exits first, but `bash -n scripts/ha_validate.sh` fails
  (`line 182: syntax error near unexpected token '||'`). Any tool that
  parses without running it will reject the gate.
- *Why it is here:* the agent's attempt to delete the block was blocked by the
  environment's security-test-removal guard, because it edits the validation
  gate. The agent did not retry or work around it. A test
  (`tests/test_casaray.py::Scripts`) records the issue and fails the day it is
  fixed, so this entry cannot be forgotten.
- *To approve:* run `sed -i '182,316d' scripts/ha_validate.sh`, then
  `bash -n scripts/ha_validate.sh && bash scripts/ha_validate.sh`, then remove
  `ha_validate.sh` from `KNOWN_SYNTAX_ISSUES` in `tests/test_casaray.py`. Or
  tell the agent in so many words that editing the gate is approved.
- *Risk:* low; the lines are unreachable.

### B2. Branch protection on `ha-deploy`, and the Codex reviewer identity

Per `docs/CODEX_REVIEW.md`: require the CI checks and one approving review
from a *separate* identity. Settings → Branches on GitHub; needs an owner
account. The agent cannot and should not set this.

### B3. Decide whether the 25/09 deletion needs an investigation

The cause of `auth_provider.homeassistant`'s disappearance is not in Git or
any project document (the audit found no script that deletes it). If you know
what was run, record it in `DECISION_LOG.md`; it decides whether any
recovery tooling needs hardening.

## C. Information only you can supply

| Need | Why |
|---|---|
| A photograph of the wall iPad on Home, House health and Bills after sync | Nothing offline can measure width or wrapping (DR-012, DR-013) |
| Whether the kiosk-mode resource is installed (HACS) | `kiosk_mode:` was removed from the dashboard on 25/09 (`fc208cd`); without the resource it never did anything (DR-015) |
| Bill helper ranges, if A1 shows they are missing | Without the originals the agent would be inventing min/max/step |

## D. Blocked and parked (nothing to do yet)

- Rebuilding bills helpers from scratch — blocked on A1/A2.
- A self-hosted CI runner for deploys — a proposal only
  (`scripts/recovery/AUTOMATION_PLAN.md` on `recovery/phase0-diagnostics`).
