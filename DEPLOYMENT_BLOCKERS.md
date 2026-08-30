# Deployment blockers — `ha-deploy`

What is on this branch, what still stands between it and a fully verified
deployment, and what is needed to clear each item.

Last updated: **2026-08-25**, after the live deployment path was confirmed.

> **Blocker 1 is RESOLVED.** This document previously stated that a sync
> could not make the dashboard live, because a storage-mode dashboard
> ignores files placed in `/config`. That reasoning was correct *about the
> Git Pull add-on* and is no longer the architecture in use. Deployment now
> runs through `/config/deploy_deez_dashboard.sh`, which does not depend on
> HA reading a file from disk. The superseded analysis is retained below,
> struck through, so the change of approach stays traceable.
>
> **Blockers 2-5 still stand.** They were never about the deployment
> mechanism.

## Status summary

| Deliverable | Status |
|---|---|
| `dashboards/deez_smart_home.yaml` | **LIVE** — deployed production dashboard |
| Deployment mechanism | **Automated** — `/config/deploy_deez_dashboard.sh` from `origin/ha-deploy` |
| Live deployment | **Active** — pipeline confirmed reading this branch 2026-08-24 |
| `configuration.yaml` | **Deliberately not created or modified** (see Blocker 2) |
| `automations.yaml` | Not imported — never read from the live instance |
| `scripts.yaml` | Not imported — never read from the live instance |
| `scenes.yaml` | Not imported — 29 scene entities exist live, definitions never read |
| `themes/` | Reserved empty path — no theme file retrieved |
| `.gitignore` | Done — secrets, `.storage/`, databases, logs, backups, keys excluded |
| `main` | **Untouched.** All deployment work is isolated to `ha-deploy` |

## What has actually been verified

Repository-side, static checks:

- **YAML syntax** — parses as one valid YAML document.
- **Duplicate keys** — none, under a strict duplicate-key loader.
- **Template compilation** — all 253 Jinja templates compile; no syntax
  errors, no unbalanced delimiters.
- **Navigation integrity** — all 40 in-dashboard `navigation_path` targets
  resolve to real view paths; zero dangling links.
- **Repository structure** — only intended files tracked.
- **Static secret scan** — no credentials, tokens, passwords, private keys,
  private URLs, hosts or IP addresses. (The utility account identifiers are
  a separate, known exposure — see Blocker 5.)
- **Baseline preservation** — view count, entity IDs, navigation, card
  types, themes, `kiosk_mode`, `card_mod` blocks and all six
  `custom:webrtc-camera` cards verified unchanged on every commit.
- **Deployment input** — the candidate commit named in the deployment log
  is a real commit on this branch (see Blocker 1).

Host-side, the deployment script reports YAML validation and a no-op skip.
Both are consistent with its run log; neither implementation has been read.

## What has NOT been verified

**Home Assistant's own configuration validator has never been run against
this repository.** HA core is not installed in the environment that produces
these files. Everything below is therefore open:

- **HA schema validation** — valid YAML is not valid Lovelace config. Card
  types, option names and nesting are unchecked against HA's schemas by
  either the repository checks or the script's YAML validation.
- **Entity existence** — the entity IDs came out of the live dashboard, so
  they are almost certainly real, but not one has been confirmed against the
  entity registry (see Blocker 3). Several referenced sensors —
  `sensor.bills_unpaid_count`, `sensor.bills_outstanding_total` and the
  Powerpal sensors among them — are not exposed to Assist and cannot be
  confirmed from here at all.
- **Custom card / resource availability** — `custom:mushroom-*` and
  `custom:webrtc-camera` must be installed and registered as Lovelace
  resources for any of this to render.
- **Frontend rendering** — no view has been opened in a browser from here.
  Template errors, layout breakage and card-mod CSS regressions surface only
  there. Since a push now deploys, this is the check that matters most after
  each change.
- **The write step of deployment** — see Blocker 1. The one run on record is
  a no-op, so the apply path itself has not been observed succeeding.

Do not describe this dashboard as "validated for Home Assistant." It is
statically well-formed and it deploys. Those are three different claims.

---

## Blocker 1 — RESOLVED: the deployment path is live

**Status: resolved 2026-08-25.** Deployment runs on the Home Assistant host:

```
/config/deploy_deez_dashboard.sh
```

It fetches `origin/ha-deploy`, resolves a candidate commit, validates the
dashboard YAML, skips when content is unchanged, and applies the dashboard.
A run reported by the owner:

```
=== Deez dashboard deployment started ===
Fetching origin/ha-deploy...
Repository already current
Validating YAML...
YAML VALID
Candidate commit: 26c3b148433919545f6df2b8cc99323cf75cc652
No dashboard content change.
```

### What this repository could verify, and what it could not

`26c3b148433919545f6df2b8cc99323cf75cc652` was checked against Git. It is a
real commit that exists **only on this branch** — `test(ha): verify automated
dashboard deployment`, authored 2026-08-24. Nothing outside `ha-deploy` could
have produced that SHA, so the pipeline is demonstrably reading this branch
and resolving commits from it. That much is independently established.

The rest is not. `/config` is not mounted in the environment that maintains
this branch, the script is not committed here, and direct REST/WebSocket
access to the instance is blocked by network policy — so the script has never
been read from here.

| Claim | Status |
|---|---|
| Reads `origin/ha-deploy`, resolves a candidate commit | **Verified** against Git |
| Validates YAML before applying | **Reported**; consistent with the log; implementation unread |
| Skips when content is unchanged | **Reported**; consistent with the log |
| Applies the dashboard to the live instance | **Not independently verified** — the quoted run is a no-op and performs no write |
| Safety checks, rollback behaviour, failure handling | **Unknown** — unread |

### 2026-08-30 — evidence that the apply step is not writing

The table above said the apply step was "not independently verified". It is
now worse than unverified. Three consecutive pushes changed
`dashboards/deez_smart_home.yaml` and produced **no visible change on the live
dashboard**, the third being a card carrying **no condition of any kind**
(`UI-032 PROBE v1`, `2183177`), whose absence cannot be explained by any gate,
template, entity or schema question.

Two further facts point the same way:

- **Nothing the owner has ever reported seeing is unique to a commit after
  the `6c3fff5` merge.** The `Home Systems` heading, its seven cards and its
  exact five-chip row all date from that merge or earlier, so every live
  observation to date is equally consistent with the dashboard being frozen
  at `6c3fff5`-era content.
- **No change to this file has ever been independently confirmed live.** The
  three `VERIFIED` items in `DASHBOARD_ISSUES.md` are a theme file and a
  `/local/` image (`UI-025`), an inference from the background rendering
  (`UI-026`), and a reading taken off Home Assistant's **native Energy panel**
  (`UI-011`) — none of them this Lovelace config.

**12 commits have touched the dashboard file since `26c3b14`**, the single
deployment run on record, and that run wrote nothing.

**Root cause found and confirmed, 2026-08-30.** The owner's Raw Configuration
Editor check settled delivery (`sensor.front_door_battery` absent), and git
settled the cause: **`ha-deploy` was replaced with an unrelated history on
2026-08-29**, and the host's clone was left on the old one.
`git merge-base 26c3b14 HEAD` — the deploy log's own candidate commit against
the current tip — returns nothing. `6c3fff5` is a **parentless root commit**
despite its merge-shaped message. A branch cannot fast-forward across
disjoint roots, so the host's checked-out commit never advances, the content
never differs, and the apply step is never reached.

So Blocker 1's open question resolves in an unexpected direction: **the apply
step is not proven broken — it has never been given anything to apply.** The
single run on record was a no-op because it could only ever be a no-op.

Tracked as `CFG-003` in `DASHBOARD_ISSUES.md`, which carries the proof and
the owner recovery procedure. Until it is settled, treat every
`FIXED — AWAITING LIVE VERIFICATION` row in this repository as **unproven at
the delivery step**, not merely unobserved: they may be sitting in Git.

**To clear the remainder:** commit the script to this branch (it is HA
configuration and belongs under version control alongside the dashboard it
deploys), or provide file-level access to `/config`. Until then, treat the
script's internal safety behaviour as unknown rather than assumed — do not
rely on a rollback or guard inside it that has not been read.

### Superseded analysis (retained for traceability)

> ~~The baseline was captured from Home Assistant's Raw configuration
> editor. That editor exists for storage-mode dashboards, whose config lives
> as JSON in `.storage/lovelace*` — not as a file HA reads from `/config`.
> Syncing this branch places `dashboards/deez_smart_home.yaml` into
> `/config`, where Home Assistant will simply ignore it. The file is a
> backup and rollback baseline, not a deployable artifact.~~

That reasoning still holds **for the Git Pull add-on specifically**, which is
why Git Pull remains unused and must not be pointed at this branch: it would
write into `/config` and deploy nothing. The current script is a different
mechanism. What the old analysis got wrong was concluding that *no*
automated path could exist.

## Blocker 2 — `configuration.yaml` has never been read

No tool available to this repository has read the live
`/config/configuration.yaml`. It is therefore **deliberately absent** from
this branch, and must stay absent.

The Git Pull add-on overwrites files in `/config` with whatever the repo
contains. A "minimal" or "reasonable-looking" `configuration.yaml`
committed here — even just `default_config:` — would silently replace the
real, working production file on the first pull. Writing one without
having read the original would make this branch dangerous.

**To clear:** get file-level access to `/config` (Studio Code Server, File
Editor, Samba, or SSH add-on), read the real file, and commit it verbatim
as a baseline before changing anything in it.

## Blocker 3 — no real `entity_id` values are available from tooling

The Home Assistant connector available here is an Assist-style
voice/control surface. A live read returns friendly name, domain, state,
area and partial attributes — **never `entity_id`, `unique_id`, or the
integration name.** There is no file-read tool, no Lovelace-config tool,
and no entity-registry tool.

The 130 entity IDs in the dashboard are trustworthy *because they came out
of the live dashboard*, not because this repository verified them. Any
**new** YAML written here still cannot safely name an entity until the
registry can be read.

**To clear:** export Developer Tools → States and populate
`docs/entity_inventory.md` on `main` with real IDs.

## Blocker 4 — automations, scripts, scenes and themes are not imported

Live queries for the `automation` and `script` domains return
`"No exposed entities found"`. That confirms they are not exposed to
Assist; it does not prove none exist. Evidence suggests automation-like
behaviour is configured somewhere — Hue Bridge automation switches,
motion-sensor toggles, AC "Climate React" logic — possibly in
device-native engines rather than as HA `automation.*` entities.

**To clear:** same as Blocker 2 — file-level access to `/config`.

## Blocker 5 — utility identifiers are hardcoded (partially resolved, low severity)

**Updated 2026-08-30: the account-number sanitisation has been re-applied**
(`23c0301`, Billing Dashboard Upgrade routine). NMI and MIRN remain
literals — see below.

| View | Identifier | Status |
|---|---|---|
| `bill-electricity` | Account number | **Sanitised** — sourced from `input_text.elec_account_number` again as of `23c0301` |
| `bill-electricity` | **NMI** | Hardcoded — never sanitised |
| `bill-gas` | Account number | **Sanitised** — sourced from `input_text.gas_account_number` again as of `23c0301` |
| `bill-gas` | **MIRN** | Hardcoded — never sanitised |

Commit `a084482` had replaced the two account numbers with
`input_text.elec_account_number` and `input_text.gas_account_number`, which
the dashboard already used in its Bills entry form. `921315e` then imported
the raw production export verbatim at the owner's instruction, restoring the
literals — not a deliberate decision to re-expose them, per
`DASHBOARD_BACKLOG.md`'s own note on `BILL-001`. `23c0301` restores the
`a084482` approach for the two account numbers only. They, and NMI/MIRN,
also remain in history at `a62d49e`/`921315e`, so removing them from the tip
does not remove them from the repository — history was not rewritten and is
not expected to be.

No helper exists for NMI or MIRN. The alternatives were all rejected:

- **`!secret`** — does not work here. A storage-mode dashboard never passes
  through HA's YAML loader, so `!secret` would render as literal text.
- **Inventing a new `input_text` helper** — would mean referencing an entity
  that does not exist, and creating it means touching config.
- **Deleting the lines** — removes information from a working production
  view.

**Severity is low, not zero.** None is an authentication credential — an NMI
or MIRN is a metering-point identifier and cannot be used to log in
anywhere. The repository being **private** is what makes this acceptable.

Note that the dashboard also carries household device names, room layout,
family members' personal device names and one partial street address. The
privacy case for keeping this repository private does not rest on the
utility identifiers alone.

**Action required: do not make this repository public.** If public access is
ever wanted: create `input_text` helpers in HA for NMI and MIRN, reference
them the way the account numbers now are, and rewrite the history that
carries all four literals (account numbers included — sanitising the tip
does not clear history).

---

## Recommended order of work

1. **Take a full backup.** Settings → System → Backups, downloaded
   off-device. Do this before anything else.
2. **Commit `/config/deploy_deez_dashboard.sh` to this branch**, or provide
   file-level access to `/config`. It is the one piece of the deployment
   path that cannot currently be reviewed, and it belongs under version
   control next to the dashboard it deploys (clears the remainder of
   Blocker 1).
3. **Get file-level access to `/config`** (Blocker 2) — Studio Code Server
   is the easiest.
4. **Commit the real `configuration.yaml` verbatim** as a baseline.
5. **Export real entity IDs** from Developer Tools → States (Blocker 3),
   and confirm the sensors that are not exposed to Assist actually exist.
6. **Import automations, scripts, scenes and themes** (Blocker 4).

Do **not** wire up the Git Pull add-on. It would write into `/config` and
deploy nothing, while overwriting files there. The current script is the
deployment mechanism.

## Bottom line

This branch **is the deployment mechanism.** A push to `origin/ha-deploy`
reaches the family's dashboard, with no staging step and no approval gate in
between. Review happens before the push or not at all.

What is proven: the pipeline reads this branch and resolves commits from it.
What is not: everything inside the script — its validation implementation,
its safety checks, its rollback behaviour, and the apply step itself, which
has never been observed on a run that actually wrote anything.

The practical consequence is narrow but real: **do not rely on a safety net
inside the script that nobody here has read.** The repository-side checks
are the ones known to run. Getting the script under version control (step 2
above) closes the last gap in the deployment path.
