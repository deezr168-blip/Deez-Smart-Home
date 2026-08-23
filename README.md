# `ha-deploy` — Home Assistant configuration backup branch

This branch mirrors the layout of Home Assistant's `/config` directory. Its
root corresponds to `/config`, with no `ha-config/` wrapper.

**It is a backup and rollback baseline — not an automatic deployment
source.** See the architecture decision below.

- Branch: `ha-deploy`
- Never merge this branch into `main`, and never merge `main` into it.
  `main` holds project documentation, tooling and notes that must never
  reach `/config`. The two branches are intentionally separate histories
  (see "Branch history" below).
- `main` is untouched by this work. All deployment work is isolated to
  `ha-deploy`.

## Architecture decision — Option A (storage mode), adopted 2026-08-23

The Deez Smart Home dashboard stays in **Lovelace storage mode**. Git's
role is:

- **source-control backup** of the dashboard configuration,
- **rollback baseline** to restore from if a change goes wrong,
- **development copy** for reviewing changes as diffs before applying them.

Deployment stays **manual**, via Home Assistant's Raw configuration editor.

### Why not the alternatives

**YAML mode was rejected as materially destructive.** A storage dashboard
cannot be converted in place. Registering a dashboard under `lovelace:
dashboards:` creates a *new* dashboard at a `url_path`, and a `url_path`
already held by a storage dashboard is unavailable. All **97** in-dashboard
links are hardcoded to `/deez-smart-home/`, so a YAML dashboard would have
to claim exactly that path — which means deleting the working production
dashboard first, modifying `configuration.yaml`, restarting HA, and
permanently losing both UI editing and the Raw editor for the whole family.
That is a large irreversible change to buy an automated deploy.

**The WebSocket API (`lovelace/config/save`) remains a valid future
upgrade** — it is the supported call the Raw editor itself makes, and it
updates a storage dashboard without touching `.storage` directly. It needs
a long-lived access token (a real secret, never committed) and network
reachability to HA. Revisit once `/config` access exists. Not used today.

### The Git Pull add-on is NOT used under this architecture

Home Assistant has no convention that scans a `dashboards/` directory. A
Lovelace YAML file loads *only* when registered under `lovelace:
dashboards:` with `mode: yaml` and a `filename:`. Syncing this branch into
`/config` would therefore place an **inert** file on disk — HA would ignore
it entirely.

Since Git Pull would deploy nothing while still writing into `/config`, it
is deliberately not configured. Do not install or point it at this branch.

## Branch history — orphan by design, no repair needed

`ha-deploy` shares **no common ancestor** with `main`:

| Branch | Root commit |
|---|---|
| `main` | `f2eb5a8` "Initial commit" |
| `ha-deploy` | `2d4b295` "build(ha): create safe HA deployment branch" |

This is intentional, not damage. The branch was created with `git checkout
--orphan` precisely so that `main`'s content (`CLAUDE.md`, `docs/`,
`safework/`) could never appear at a `/config`-shaped root. Investigated and
confirmed: not a reinitialisation, not a force-push (every `ha-deploy`
transition is a verified fast-forward), and not a shallow-clone artifact
(`is-shallow-repository: false`).

**Consequence:** a normal PR or merge `ha-deploy → main` will not work —
`git merge` aborts with *"refusing to merge unrelated histories."* That is
the intended outcome; these branches are meant to stay parallel forever.

If the dashboard is ever wanted on `main`'s history, transplant the file
onto a branch cut from `main` (`git checkout origin/ha-deploy --
dashboards/deez_smart_home.yaml`) and open a normal PR. Never use
`--allow-unrelated-histories`, rebase, or force-push to join them.

## Current state

| | |
|---|---|
| Production dashboard baseline | **Present** — `dashboards/deez_smart_home.yaml` |
| Dashboard mode | **Storage mode** (adopted; see verification caveat below) |
| Deployment mechanism | **Manual** — Raw configuration editor |
| Git Pull add-on | **Not used** |
| Live deployment | **Has not occurred** |
| `configuration.yaml` | **Deliberately not created or modified** |
| `secrets.yaml` | Not created (and gitignored) |
| Automations / scripts / scenes | Not imported — see `DEPLOYMENT_BLOCKERS.md` |
| Themes | Not imported — `themes/` is a reserved empty path |

### The dashboard baseline

`dashboards/deez_smart_home.yaml` contains the **imported production Deez
Smart Home dashboard baseline** — the live dashboard configuration, taken
verbatim from the Raw configuration editor and committed unmodified apart
from one sanitisation pass (below).

It is 32 views (12 subviews), 130 distinct entity IDs, 113 `card_mod`
blocks, `kiosk_mode`, five per-view themes, Mushroom cards, six
`custom:webrtc-camera` cards, and the English/Chinese toggle — preserved
as-is. **This file is the rollback point.** Treat it as production: no
redesign, no refactor, no reformatting. Changes go in as small, reviewable
diffs against it.

Dashboard identity: `url_path` **`deez-smart-home`**, title **Deez Smart
Home**.

### Sanitisation applied

Two hardcoded utility account numbers were replaced with references to
`input_text` helpers the dashboard already uses for that purpose in its
Bills entry form. No new entity IDs were introduced.

> ⚠️ **Verify before the first paste-back.** The Electricity Plan card
> references `input_text.elec_account_number` — the ID this dashboard
> already used. Confirm the real ID in Developer Tools → States. If the
> helper is actually named `input_text.electricity_account_number`, correct
> line 4592 first. Worst case is a card showing `unknown`; it cannot break
> the dashboard.

The electricity **NMI** and gas **MIRN** remain hardcoded — no existing
entity holds them. **Keep this repository private** while they are present.

## Deployment procedure (manual)

Nothing here is automatic. Both procedures are deliberate, human-driven
steps.

### Applying a change from Git to Home Assistant

1. **Back up first.** Settings → System → Backups → Create backup (full),
   downloaded off-device.
2. Review the change as a diff in Git and confirm it is what you intend.
3. Open the dashboard → ⋮ menu → **Raw configuration editor**.
4. **Copy the current live contents out first** and keep them until the
   change is verified — that is your immediate undo.
5. Replace the contents with `dashboards/deez_smart_home.yaml`.
6. Save. Reload the page.
7. **Verify in the browser**: views render, cameras stream, kiosk mode
   behaves, the EN/ZH toggle works, no "Entity not available" or "Custom
   element doesn't exist" errors.
8. If anything is wrong, paste back the copy from step 4.

### Rolling back to the committed baseline

1. `git show origin/ha-deploy:dashboards/deez_smart_home.yaml` (or check
   out an earlier commit for an older state).
2. Open the Raw configuration editor, replace the contents, save.
3. Reload and verify as above.

No Home Assistant restart is required — a storage-mode dashboard applies on
save. Restarting is *not* a fix for a bad paste; restoring the previous
contents is.

### Capturing a live change back into Git

If the dashboard is edited in the UI, Git is now stale. Copy the Raw
configuration editor contents back into
`dashboards/deez_smart_home.yaml`, review the diff, and commit. Do this
before making Git-side edits, or the two will diverge.

## Validation status

The dashboard has passed every check this repository can run, and **no
check that requires Home Assistant itself has been run at all.**

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

Each requires the live Home Assistant instance.

| Not verified | Why it matters |
|---|---|
| **Home Assistant schema validation** | HA's own config check has never been run. Valid YAML is not valid Lovelace config. |
| **Existence of every entity** | The 130 entity IDs came from the live dashboard, but none has been confirmed against the entity registry. |
| **Custom card / resource availability** | The nine `custom:` card types plus `card_mod` and `kiosk-mode` must be installed and registered as Lovelace resources. |
| **Frontend rendering** | No view has been loaded in a browser. |
| **Dashboard mode** | Storage mode is strongly indicated and has been adopted, but is not tooling-verified. Confirm at Settings → Dashboards. |

**Do not read "validation passed" as "safe to paste in unattended."** It
means the file is well-formed and internally consistent, nothing more —
which is exactly why step 4 of the procedure above exists.

## Files on this branch

| Path | Purpose | Parsed by HA? |
|---|---|---|
| `dashboards/deez_smart_home.yaml` | Production dashboard baseline | **No** — inert on disk; applied manually |
| `themes/.gitkeep` | Reserved path for theme YAML | No |
| `.gitignore` | Blocks secrets, `.storage/`, databases, logs, backups, keys | No |
| `README.md` | This file | No |
| `DEPLOYMENT_BLOCKERS.md` | Open blockers and how to clear them | No |

## Rules for adding anything to this branch

1. **Never commit a file here that has not been read from the live
   instance first.** Import, then commit — never author from inference.
2. **Never reference an `entity_id` that has not been confirmed** in
   Developer Tools → States. A friendly name is not an entity ID.
3. **Never commit secrets.** `secrets.yaml` stays out of git. Never commit
   `.storage/`, the recorder database, logs, or backups.
4. **Never edit `.storage/` directly**, through Git or otherwise.
5. **Validate YAML before committing**, and review the diff before pushing.
6. **Keep changes small and reversible.** A dashboard redesign is built as
   a separate candidate file and promoted once reviewed — never as an
   in-place wholesale replacement of a working production dashboard.
