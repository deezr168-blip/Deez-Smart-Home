# Rule sets the orientation tool knows

`scripts/orient.py` carries these as data (`REGIMES`). This file is the human
copy, with the source of each line. If the two disagree, the instruction files
named in the *Source* column win, and both this file and the tool need fixing.

## Branch to rule set

| Branch pattern | Key | Rule set |
|---|---|---|
| `casaray-v3-design` | `v3-integrator` | V3 design, integration branch |
| `casaray-v3/agent-*` | `v3-specialist` | V3 design, specialist branch |
| `ha-deploy` | `v2-deploy` | CasaRay V2 deployment branch |
| `claude/*` | `v2-session` | Session branch; push target **not stated** |
| `recovery/*` | `recovery` | Owner-gated; no rule file checked out |
| anything else (`main`, `autonomous/*`, detached) | `unknown` | **Ask.** Do not assume V2 or V3 |

The first match wins, in that order. `claude/ha-dashboard-upgrades-wui7ig` is
named in the root rules as the V2 mirror but matches `claude/*`, so a session on
it still gets "confirm the target": being the mirror and being the working branch
are different things.

## V3: `v3-integrator` and `v3-specialist`

| Item | Rule | Source |
|---|---|---|
| May write | `design/casaray-v3/` only; anything else needs explicit approval from Ray | `design/casaray-v3/CLAUDE.md`, *Hard boundaries* |
| Integrator push | `origin casaray-v3-design`. Only the integrator commits to, merges into and pushes it | same, *Branches* |
| Specialist push | own `casaray-v3/agent-*` branch only; never merge into `casaray-v3-design` | same |
| Never | commit, merge, rebase, push or open a PR against `ha-deploy`; deploy, sync, reload or restart; change device or configuration state | same |
| Never | force-push, history rewrite | `.claude/settings.json` deny list |
| Gates | `verify_entities.py`; the Playwright harness `test_and_capture.cjs`; `ha_validate.sh` only if anything outside the V3 tree changed | `design/casaray-v3/README.md` *Checks*; `CLAUDE.md` *Relationship to the root rules* |
| Tracking | SHA stamping and `PROJECT_STATE.md` / `DASHBOARD_*.md` are V2 only; V3 records history in `DECISIONS.md` | same |
| Owner review | show a render or screenshot at each design milestone before building on it | same, *Workflow* step 5 |

Drift needles (text this table was written from): `Integration branch:
`casaray-v3-design``, `No changes to `ha-deploy``, `casaray-v3/agent-*`, `explicit
approval from Ray`. Matching ignores line wraps.

## V2: `v2-deploy`

| Item | Rule | Source |
|---|---|---|
| Push | `origin ha-deploy` **and** `origin ha-deploy:claude/ha-dashboard-upgrades-wui7ig`, every batch | root `CLAUDE.md`, *Working rules* |
| Fast-forward first | local `ha-deploy` must be fast-forwarded, or the push reports "Everything up-to-date" and never deploys | same |
| Gate | `bash scripts/ha_validate.sh`, exit 0 or do not push; `verify_change.sh` for a structural and render diff | same; `improve-system` |
| Stamping | commit with a placeholder, then a one-line `docs: stamp` commit; never amend; a rebase invalidates a stamp (`86ec579`) | same |
| Legacy | `dashboards/deez_smart_home.yaml`: do not modify | same |
| Not live until | the owner runs `scripts/sync_casaray_to_config.sh` | same, *Deployment* |

## Protected paths (all rule sets)

`classify()` in `orient.py` blocks these whatever the rule set, and no flag overrides it.

| Paths | Source |
|---|---|
| `secrets.yaml`, `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `known_devices.yaml`, `ip_bans.yaml`, `auth_provider.*`, `.storage/` (any depth), `.env*` except `.env.example` | `scripts/ha_validate.sh` section 4; `MAINTENANCE.md` *Protected* |
| `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.token`, `id_rsa`, `id_ed25519`, `known_hosts`, `authorized_keys` | `scripts/ha_validate.sh` section 5 |
| `scripts/deploy_env.sh`, `scripts/deploy_askpass.sh`, `scripts/deploy_diagnose.sh`, `DEPLOY_AUTH.md` | root `CLAUDE.md`, *Do not touch without an explicit instruction* |
| `.claude/settings.json`, `scripts/deny_device_control.py` | `MAINTENANCE.md`: the device-control guard is part of the recovery path |
| `dashboards/deez_smart_home.yaml` | root `CLAUDE.md`, *legacy* |

One deliberate difference from the gate: `.storage/` is blocked at any depth,
not only at the root.

## What is intentionally not in the table

- **Whether the integration branch may open a pull request.** No repository file
  says. Ask.
- **Whether `PROJECT_STATE.md` is read in full.** Root step 1 says yes; step 3 and
  the file's own *Context Loading Strategy* say selectively. The tool reports the
  contradiction as C5 and does not choose.
- **Anything about the live instance.** The tool reads git and text files only.

## Adding or changing a rule set

1. Edit the entry in `REGIMES` and the table above in the same commit.
2. Record in `sources` the literal text the entry was written from.
3. Add a branch case and, if paths are involved, a classification case to
   `--selftest`, and run it.
