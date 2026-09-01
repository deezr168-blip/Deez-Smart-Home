# `ha-deploy` — Home Assistant dashboard deployment branch

This branch mirrors the layout of Home Assistant's `/config` directory. Its
root corresponds to `/config`, with no `ha-config/` wrapper.

**It is the live deployment source for the Deez Smart Home dashboard.** A
deployment script on the Home Assistant host watches this branch, validates
what it finds and applies the dashboard. It remains the rollback baseline as
well — those two roles are not in conflict.

> **Superseded (2026-08-25).** This branch was originally documented as a
> backup-only branch that could not deploy, on the reasoning that a
> storage-mode dashboard ignores files placed in `/config`. That reasoning
> was correct about *Git Pull* and is no longer the architecture in use: the
> current path does not rely on HA reading a file from disk. See
> [Deployment architecture](#deployment-architecture-current) below. The
> superseded text is retained in `DEPLOYMENT_BLOCKERS.md` under Blocker 1 so
> the change of approach stays traceable.

- Branch: `ha-deploy`
- Never merge this branch into `main`, and never merge `main` into it.
  `main` holds project documentation, tooling and notes that must never
  reach `/config`. The two branches are intentionally separate histories
  (see "Branch history" below).
- `main` is untouched by this work. All deployment work is isolated to
  `ha-deploy`.
- **Design reference:** the intended look and content of the dashboard is
  described in [`DESIGN_REFERENCE.md`](DESIGN_REFERENCE.md), transcribed from
  the CasaRay mockups the owner supplied on 2026-08-31. Check layout, wording
  and colour changes against it. It describes intent only — it does not relax
  the entity-verification rules below.
- **Technical mapping:** [`docs/CASARAY_MAPPING_PACK.md`](docs/CASARAY_MAPPING_PACK.md)
  takes each mockup component through to a real entity, a proposed card and a
  buildability status (`AVAILABLE NOW` … `NEEDS HARDWARE/DATA`). Read it before
  building any CasaRay component — it is the record of what can honestly be
  built and what cannot.
- **Entity truth:** [`docs/entity_inventory.md`](docs/entity_inventory.md)
  reconciles every entity the dashboard references against the live instance.
  It is where "does this entity exist?" is answered, and it records the limits
  of what this environment can confirm.

## Deployment architecture (current)

<a id="deployment-architecture-current"></a>

The dashboard stays in **Lovelace storage mode**. Deployment is **automated**
from this branch by a script on the Home Assistant host:

```
/config/deploy_deez_dashboard.sh
```

### The flow

```
commit pushed to origin/ha-deploy
        |
        v
  script fetches origin/ha-deploy
        |
        v
  resolves a candidate commit
        |
        v
  validates the dashboard YAML   --- invalid --> stops, nothing applied
        |
        v
  compares against current content
        |
        +--- no change --> stops, nothing applied
        |
        v
  applies the dashboard to the live instance
```

A successful run reported by the owner:

```
=== Deez dashboard deployment started ===
Fetching origin/ha-deploy...
Repository already current
Validating YAML...
YAML VALID
Candidate commit: 26c3b148433919545f6df2b8cc99323cf75cc652
No dashboard content change.
```

### What is independently verified, and what is not

This repository cannot reach the Home Assistant host: `/config` is not
mounted in the environment that maintains this branch, the script is not
committed here, and direct REST/WebSocket access to the instance is blocked
by network policy. The distinction below matters — do not read the whole
flow as verified.

| Element | Status |
|---|---|
| The pipeline reads `origin/ha-deploy` | **Verified.** `26c3b148…` is a real commit that exists only on this branch — `test(ha): verify automated dashboard deployment`, pushed 2026-08-24. Nothing off this branch could have produced that SHA. |
| It resolves a specific candidate commit | **Verified** — the SHA is exact and correct. |
| It validates YAML before applying | **Reported**, and consistent with the log. The validation implementation has not been read. |
| It skips when content is unchanged | **Reported**, and consistent with the log. |
| It applies the dashboard to the live instance | **Not independently verified.** The quoted run is a no-op ("Repository already current", "No dashboard content change"), so it exercises fetch, validation and comparison but performs no write. |
| Its safety checks and rollback behaviour | **Not verified** — the script has not been read from here. |

**Consequence for anyone editing this branch:** treat every push as reaching
the live house, because the evidence supports that; but do not assume a
particular safety net exists inside the script, because none of it has been
read. The repository-side checks below are the ones known to run.

### Confirming a deployment actually landed

> **This check is no longer usable, corrected 2026-08-30.** It referred to
> commit `1bdd704`, which is **not an ancestor of this branch** — it belongs
> to the superseded orphan history replaced by the `6c3fff5` merge. The
> current baseline has no `TEST` marker either, so seeing "Home control
> centre" now proves nothing about whether a deployment has run.
>
> ~~There is a cheap visual check. Commit `1bdd704` removed a `TEST` marker
> from the Home view subtitle.~~

**Use instead:** search the dashboard's **Raw configuration editor** for a
string unique to the commit you are testing for. That bypasses rendering
entirely and answers the delivery question directly. As of 2026-08-30 the
marker in the tree is `UI-032 PROBE v1` (commit `2183177`) — if the raw
config does not contain it, nothing since has been delivered. See `CFG-003`
in `DASHBOARD_ISSUES.md`.

### Why not the alternatives

**YAML mode was rejected as materially destructive.** A storage dashboard
cannot be converted in place. Registering a dashboard under `lovelace:
dashboards:` creates a *new* dashboard at a `url_path`, and a `url_path`
already held by a storage dashboard is unavailable. All in-dashboard links
are hardcoded to `/deez-smart-home/`, so a YAML dashboard would have to claim
exactly that path — which means deleting the working production dashboard
first, modifying `configuration.yaml`, restarting HA, and permanently losing
both UI editing and the Raw editor for the whole family. That reasoning still
stands, and the current script-based approach avoids it entirely: the
dashboard stays in storage mode and the UI editor keeps working.

**The Git Pull add-on is still not used, and should not be.** Git Pull writes
files into `/config`, where a storage-mode dashboard would ignore them. It
would deploy nothing while still overwriting `/config`. The current script is
a different mechanism and does not depend on HA reading a file from disk. Do
not install Git Pull or point it at this branch.

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
| Deployment mechanism | **Automated** — `/config/deploy_deez_dashboard.sh` from `origin/ha-deploy` |
| Git Pull add-on | **Not used** — and must not be (see above) |
| Live deployment | **Active.** Pipeline confirmed reading this branch on 2026-08-24 |
| Manual paste-back | Still available as a fallback and for rollback |
| `configuration.yaml` | **Deliberately not created or modified** |
| `secrets.yaml` | Not created (and gitignored) |
| Automations / scripts / scenes | Not imported — see `DEPLOYMENT_BLOCKERS.md` |
| Themes | Not imported — `themes/` is a reserved empty path |

### The dashboard baseline

`dashboards/deez_smart_home.yaml` is the **live production dashboard**. It
originated as a verbatim export from the Raw configuration editor and is now
the deployed source of truth.

As of 2026-08-25 it is 36 views (16 subviews), 162 distinct entity IDs, 132
`card_mod` blocks, `kiosk_mode`, five per-view themes (`Deez Cameras`, `Deez
Climate`, `Deez Energy`, `Deez Lighting`, `Deez Security`), 236 Mushroom
cards, six `custom:webrtc-camera` cards, and the English/Chinese toggle.

**This file is also the rollback point.** Treat it as production: no
redesign, no refactor, no reformatting. Changes go in as small, reviewable
diffs.

Dashboard identity: `url_path` **`deez-smart-home`**, title **Deez Smart
Home**.

#### Changes made on this branch since import

Six correctness fixes, all deployed:

| Commit | Change |
|---|---|
| `1bdd704` | Removed a `TEST` marker from the Home view subtitle |
| `4f590e7` | Energy Now cards: missing data no longer renders as a real zero |
| `cc3cd42` | Bills cards: a dead sensor no longer reports "All bills paid" |
| `a49ca72` | Solar readouts show "Offline" instead of "0 W" / "unavailable W" |
| `25abc06` | Remaining energy totals and bill estimates guarded |
| `1e889be` | Emergency button cards show real status instead of raw `on`/`off` |

All six share one root cause: values were piped through `| float(0)` or
`| int(0)`, which turns `unavailable` into `0`. A missing reading became a
plausible-looking measurement — and in the bills case, a green "All bills
paid" produced by a sensor that was not reporting at all.

#### Known hardware gaps

Recorded here rather than as cards on the dashboard. Seven "nothing here yet"
markdown placeholders used to occupy three room pages — on Ray Bedroom they
filled two of the page's four columns — so they were removed and the same
information kept in the repository, where a maintainer will actually look for
it.

| Room | Missing | Where its cards belong once it exists |
|---|---|---|
| Ray Bedroom | Temperature / humidity sensor | New Climate section |
| Ray Bedroom | Thermostat (`climate` entity) | New Climate section |
| Ray Bedroom | Media player (TV or speaker) | New Entertainment section |
| Guest Room | Temperature / humidity sensor | New Climate section |
| Guest Room | Thermostat (`climate` entity) | New Climate section |
| Guest Room | Blinds, fans, other controls | New Controls section |
| Parents Room | Blinds, fans, other controls | Section 2, above Power Boards |

Two more gaps are still shown on the dashboard, deliberately, because they are
about a device that is physically present but not reachable: the Living Room
Mitsubishi AC ("Wi-Fi module not integrated yet", on Climate and Living Room)
and the Garage door ("Shelly / Chamberlain integration planned").

### Sensitive values in this file

> ⚠️ **The two utility account numbers are present in this file, in the
> Electricity Plan and Gas Plan markdown cards.**

An earlier commit (`a084482`) replaced them with `input_text` helper
references. That sanitisation was **reverted** by `921315e`, which imported
the raw production export verbatim at the owner's instruction. The literals
are therefore live again at the branch tip, and they also remain in history
at `a62d49e` — so removing them from the tip would not remove them from the
repository.

Also hardcoded, and never sanitised: the electricity **NMI** and the gas
**MIRN**. No existing entity holds either value.

**Keep this repository private.** That is what makes the exposure
acceptable. None of these are authentication credentials — an NMI or MIRN is
a metering-point identifier — but they are account-identifying, and the
dashboard additionally contains household device names, room layout, family
members' personal device names and one partial street address.

If the repository ever needs to be public, create helpers in Home Assistant
for all four values first, then reference them the way `a084482` did, and
rewrite the history that carries the literals.

## Deployment procedure

### Normal path — automated

Pushing to `origin/ha-deploy` is the deployment. The script on the HA host
fetches the branch, validates the dashboard YAML, skips if nothing changed,
and applies it.

**A push is a production change.** There is no staging step between this
branch and the family's dashboard, so the review has to happen before the
push, not after:

1. Make the smallest change that accomplishes the goal.
2. Validate locally — YAML parse, duplicate keys, `git diff --check`, and a
   secret scan. `scripts/validate.sh` on `main` does all four.
3. Read the whole diff. Confirm entity IDs, navigation paths, `kiosk_mode`
   and the English/Chinese toggle are unchanged unless the change is
   deliberately about one of them.
4. Commit with a message explaining *why*, so a later rollback has context.
5. Push.
6. **Verify in the browser**: views render, cameras stream, kiosk mode
   behaves, the EN/ZH toggle works, no "Entity not available" or "Custom
   element doesn't exist" errors.

Take a full backup (Settings → System → Backups, downloaded off-device)
before any substantial change.

### Rolling back

Roll back the same way you deploy — with Git, not by hand:

1. `git revert <bad commit>` on `ha-deploy`.
2. Validate as above.
3. Push. The script picks up the revert like any other commit.

`git revert` is preferred over force-pushing: it keeps the history that
explains what happened, and never rewrites a branch a deployment script is
watching.

### Manual fallback

Still valid if the script is unavailable, or to restore immediately without
waiting for a deployment cycle:

1. `git show origin/ha-deploy:dashboards/deez_smart_home.yaml`
2. Open the dashboard → ⋮ menu → **Raw configuration editor**.
3. Copy the current live contents out first — that is your immediate undo.
4. Replace the contents, save, reload, verify.

No Home Assistant restart is required — a storage-mode dashboard applies on
save. Restarting is *not* a fix for a bad deploy; restoring the previous
contents is.

### Capturing a live UI change back into Git

If the dashboard is edited through the UI, Git is now stale — and because
Git deploys, the next push would overwrite that UI edit. Copy the Raw
configuration editor contents back into `dashboards/deez_smart_home.yaml`,
review the diff, and commit **before** making any Git-side edit.

## Validation status

Two layers of checking now exist: the repository-side checks below, and the
YAML validation the deployment script performs on the HA host before it
applies anything. Neither is a Home Assistant schema check.

### Verified (repository-side, static)

| Check | Result |
|---|---|
| YAML syntax | Parses as one valid YAML document |
| Duplicate keys | None (strict duplicate-key loader) |
| Template compilation | All 253 Jinja templates compile; no syntax errors, no unbalanced delimiters |
| Navigation integrity | All 40 in-dashboard `navigation_path` targets resolve to real view paths; zero dangling links |
| Repository structure | Only intended files tracked; no `.storage/`, databases, logs, backups or keys |
| Secret scan (static) | No credentials, tokens, passwords, private keys, private URLs, hosts or IPs |
| Baseline preservation | View count, entity IDs, navigation, card types, themes, `kiosk_mode` and `card_mod` verified unchanged on every commit |

### Host-side (deployment script)

| Check | Status |
|---|---|
| YAML validation before applying | **Reported and consistent with the run log** (`Validating YAML... YAML VALID`). Implementation not read from here. |
| No-op skip when content is unchanged | **Reported and consistent with the run log** (`No dashboard content change.`). |
| Any further safety check or rollback | **Unknown** — the script is not committed to this branch and `/config` is not reachable from the environment that maintains it. |

### NOT verified

| Not verified | Why it matters |
|---|---|
| **Home Assistant schema validation** | Valid YAML is not valid Lovelace config. Card types, option names and nesting are unchecked against HA's schemas by either layer. |
| **Existence of every entity** | The entity IDs came from the live dashboard, so they are almost certainly real, but the registry has never been read. Some referenced sensors are not exposed to Assist and cannot be confirmed at all. |
| **Custom card / resource availability** | The `custom:` card types plus `card_mod` and `kiosk-mode` must be installed and registered as Lovelace resources. |
| **Frontend rendering** | No view has been loaded in a browser from here. |
| **Dashboard mode** | Storage mode is strongly indicated and has been adopted, but is not tooling-verified. Confirm at Settings → Dashboards. |

**"Validation passed" means well-formed, not correct.** Both layers check
that the file parses; neither checks that a card renders, that an entity
exists, or that a template produces sensible output. Since a push now
deploys, the browser check after a push is the step that actually catches
those — it is not optional.

## Files on this branch

| Path | Purpose | Parsed by HA? |
|---|---|---|
| `dashboards/deez_smart_home.yaml` | Production dashboard — **deployed** | Applied by `/config/deploy_deez_dashboard.sh`, not read from `/config` by HA |
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
5. **Validate YAML before committing**, and review the whole diff before
   pushing. A push to this branch deploys to the live dashboard — there is
   no staging step and no approval gate.
6. **Keep changes small and reversible.** A dashboard redesign is built as
   a separate candidate file and promoted once reviewed — never as an
   in-place wholesale replacement of a working production dashboard.
