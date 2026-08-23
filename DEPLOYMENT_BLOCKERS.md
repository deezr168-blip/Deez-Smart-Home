# Deployment blockers — `ha-deploy`

What is on this branch, what still stands between it and a live
deployment, and what is needed to clear each item.

Last updated: **2026-08-23**, after the production dashboard import.

## Status summary

| Deliverable | Status |
|---|---|
| `dashboards/deez_smart_home.yaml` | **PRESENT** — imported production baseline, statically validated |
| `configuration.yaml` | **Deliberately not created or modified** (see Blocker 2) |
| `automations.yaml` | Not imported — never read from the live instance |
| `scripts.yaml` | Not imported — never read from the live instance |
| `scenes.yaml` | Not imported — 29 scene entities exist live, definitions never read |
| `themes/` | Reserved empty path — no theme file retrieved |
| `.gitignore` | Done — secrets, `.storage/`, databases, logs, backups, keys excluded |
| Live deployment | **Has not occurred** |
| `main` | **Untouched.** All deployment work is isolated to `ha-deploy` |

## What has actually been verified

Repository-side, static checks only:

- **YAML syntax** — parses as one valid YAML document.
- **Duplicate keys** — none, under a strict duplicate-key loader.
- **Navigation integrity** — all 32 in-dashboard `navigation_path` targets
  resolve to real view paths; zero dangling links.
- **Repository structure** — only intended files tracked.
- **Static secret scan** — no credentials, tokens, passwords, private
  keys, private URLs, hosts or IP addresses.
- **Baseline preservation** — after sanitisation, view count, entity IDs,
  navigation, card types, themes, `kiosk_mode`, `card_mod` blocks and all
  six `custom:webrtc-camera` cards verified unchanged against the
  pre-edit file.

## What has NOT been verified

**Home Assistant's own configuration validator has never been run against
this repository.** HA core is not installed in the environment that
produced these files, and there is no path from here to the live instance's
config check. Everything below is therefore open:

- **HA schema validation** — valid YAML is not valid Lovelace config.
  Card types, option names and nesting are unchecked against HA's schemas.
- **Entity existence** — the 130 entity IDs came out of the live
  dashboard, so they are almost certainly real, but not one has been
  confirmed against the entity registry (see Blocker 3).
- **Custom card / resource availability** — `custom:mushroom-*` and
  `custom:webrtc-camera` must be installed and registered as Lovelace
  resources for any of this to render.
- **Frontend rendering** — no view has been opened in a browser. Template
  errors, layout breakage and card-mod CSS regressions surface only there.
- **Live deployment behaviour** — nothing has been deployed.

Do not describe this dashboard as "validated for Home Assistant." It is
statically well-formed. That is a different claim.

---

## Blocker 1 — a Git Pull sync will not make this dashboard live

**This is the most important item in this document, and it is new.**

The baseline was captured from Home Assistant's **Raw configuration
editor**. That editor exists for **storage-mode** dashboards, whose config
lives as JSON in `.storage/lovelace*` — not as a file HA reads from
`/config`. The presence of a top-level `kiosk_mode:` key points the same
way.

If the dashboard is in storage mode — which the evidence strongly
indicates, though it has not been confirmed by reading the live
`configuration.yaml` — then:

- Syncing this branch places `dashboards/deez_smart_home.yaml` into
  `/config`, where **Home Assistant will simply ignore it.**
- The file is a **backup and rollback baseline**, not a deployable
  artifact.
- Nothing breaks. Nothing deploys either.

Two ways to close this, both requiring a decision that is out of scope for
this branch:

1. **Keep storage mode.** Deploy by pasting the file's contents back into
   the Raw configuration editor. Manual, but it changes nothing about how
   the dashboard is managed, and the UI editor keeps working.
2. **Convert to YAML mode.** Add a `lovelace:` dashboard block to
   `configuration.yaml` pointing at this file. This makes Git Pull a real
   deployment mechanism — and **disables UI editing of the dashboard**,
   a significant behavioural change to a production family dashboard. It
   also requires modifying `configuration.yaml`, which Blocker 2 forbids
   until the live file has been read.

**Recommendation: confirm the dashboard's actual mode first**
(Settings → Dashboards → Deez Smart Home → three-dot menu; or read
`configuration.yaml` for a `lovelace:` block). Do not convert to YAML mode
without deciding whether losing the UI editor is acceptable.

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

## Blocker 5 — NMI and MIRN remain hardcoded (accepted, low severity)

The Electricity Plan and Gas Plan views each carry a utility identifier
that could not be safely removed:

| View | Identifier | Status |
|---|---|---|
| `bill-electricity` | Account number | **Sanitised** → `input_text.elec_account_number` |
| `bill-electricity` | **NMI** | Remains hardcoded |
| `bill-gas` | Account number | **Sanitised** → `input_text.gas_account_number` |
| `bill-gas` | **MIRN** | Remains hardcoded |

The account numbers were replaceable because the dashboard **already**
uses `input_text.elec_account_number` and `input_text.gas_account_number`
in its Bills entry form, so referencing them invents nothing.

No equivalent helper exists for NMI or MIRN. The alternatives were all
rejected:

- **`!secret`** — does not work here. Storage-mode dashboards never pass
  through HA's YAML loader, so `!secret` would render as literal text.
  Making it work would require YAML-mode conversion, i.e. Blockers 1
  and 2.
- **Inventing a new `input_text` helper** — would mean referencing an
  entity that does not exist, and creating it means touching config.
- **Deleting the lines** — removes information from a working production
  view. Out of scope for a sanitisation pass.

**Severity is low, not zero.** An NMI/MIRN is a metering-point
identifier, not an authentication credential — it cannot be used to log in
anywhere. The repository is **private**, which is what makes leaving them
acceptable.

**Action required: do not make this repository public** while these values
are present. If public access is ever wanted, create the two helpers in HA
first, then swap these references the same way the account numbers were
swapped.

---

## Recommended order of work

1. **Take a full backup.** Settings → System → Backups, downloaded
   off-device. Do this before anything else.
2. **Confirm the dashboard's mode** (Blocker 1) and decide how deployment
   should actually work.
3. **Get file-level access to `/config`** (Blocker 2) — Studio Code Server
   is the easiest.
4. **Commit the real `configuration.yaml` verbatim** as a baseline.
5. **Export real entity IDs** from Developer Tools → States (Blocker 3).
6. **Import automations, scripts, scenes and themes** (Blocker 4).
7. **Only then** wire up the Git Pull add-on, pointed at `ha-deploy`, with
   `auto_restart: false`, and verify the first pull changes nothing
   unexpected.

## Bottom line

This branch is **safe** — nothing on it can break a running Home Assistant
instance, and it now carries a real rollback baseline for the dashboard,
which is a meaningful improvement over an empty repository.

It is **not yet a deployment mechanism.** Blocker 1 is the reason: a pull
would place the dashboard file in `/config` where HA very likely ignores
it. Resolve that, and Blocker 2, before treating this branch as anything
other than a versioned backup.
