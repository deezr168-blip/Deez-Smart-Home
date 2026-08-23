# Deployment blockers — `ha-deploy`

Why this branch contains no real Home Assistant configuration, what is
blocking it, and exactly what is needed to unblock it.

Last verified: **2026-08-23**, against the live instance and against every
branch in this repository.

## Summary

| Deliverable | Status | Blocker |
|---|---|---|
| `configuration.yaml` | **BLOCKED — not created** | Live file has never been read. Fabricating one would overwrite production on first pull. |
| `automations.yaml` | **BLOCKED — not created** | No verified automation YAML exists anywhere in this repository or is readable from the live instance. |
| `scripts.yaml` | **BLOCKED — not created** | Same. |
| `scenes.yaml` | **BLOCKED — not created** | 29 `scene` entities are known to exist live, but their YAML definitions have never been read. |
| `dashboards/` | **BLOCKED — reserved, empty** | No Lovelace/dashboard configuration has ever been retrieved. See "The dashboard" below. |
| `themes/` | **BLOCKED — reserved, empty** | No theme file has ever been retrieved. |
| `.gitignore` | **DONE** | Safety rails are in place and require no live data. |

## Blocker 1 — the live `/config` filesystem cannot be read

The Home Assistant connector available to this repository is an
**Assist-style voice/control surface**. Its complete tool surface is:
live-context reads, entity control actions (turn on/off, light, climate,
fan, cover, media, volume, list items, broadcast, timers), a to-do list
read, and a clock.

Verified by inspecting the full tool list: there is **no tool of any kind
that reads or writes a file**, no tool that reads Lovelace/dashboard
configuration, no tool that reads the entity or device registry, and no
tool that restarts or reloads Home Assistant.

Consequence: `configuration.yaml`, `automations.yaml`, `scripts.yaml`,
`scenes.yaml`, dashboard YAML, and `themes.yaml` cannot be imported.

## Blocker 2 — no real `entity_id` values are available

Re-confirmed live on 2026-08-23 with a direct read. A representative
response:

```
names: Parents Room AC
domain: climate
state: 'off'
areas: Parents Room
attributes:
  current_temperature: 19.4
```

The connector returns **friendly name, domain, state, area, and partial
attributes — never `entity_id`, never `unique_id`, never the integration
name.** A friendly name is not an entity ID and cannot be converted into
one by guessing (`Parents Room AC` could be `climate.parents_room_ac`,
`climate.parents_room_ac_2`, or something else entirely).

`docs/entity_inventory.md` on `main` states this same limitation and
contains **zero entity IDs** — confirmed by search: no `domain.object_id`
string appears anywhere in it.

Consequence: **no automation, script, scene, or dashboard card can be
written in this repository yet**, because every one of them must name a
real entity, and no real entity name is known. Writing YAML against
guessed IDs produces a dashboard full of "Entity not available" cards at
best, and silently broken automations at worst.

## Blocker 3 — there is no dashboard in this repository to deploy

The task that produced this branch asked for "the current verified
production Deez Smart Home dashboard configuration" to be moved into the
deployment paths. **That configuration does not exist in this repository.**

Verified across the entire repository, not just the current branch:

- Every file ever added on any branch was enumerated from git history.
  No dashboard YAML, theme YAML, automation YAML, script YAML, or
  `configuration.yaml` has ever been committed to this repository.
- A full-text search for `dashboard`, `mushroom`, `card-mod`, `kiosk`, and
  `theme` across all tracked files matches only prose in documentation —
  no configuration.
- `main` contains: `CLAUDE.md`, `README.md`, `.gitignore`,
  `docs/entity_inventory.md`, and empty `.gitkeep` scaffolding.
- The `ha-config/` tree on the setup branch is empty placeholders only,
  and its own README states that this is deliberate.

So there is nothing to preserve, because nothing was ever captured. The
production dashboard — its navigation, kiosk mode, themes, bilingual
English/Chinese handling, Mushroom cards, and card-mod styling — **exists
only on the live instance.** None of it is in git.

This is the single most important finding in this document: **this
repository is not currently a backup of the live Home Assistant setup.**
If the live instance were lost today, the dashboard would be lost with it.

## Blocker 4 — automations and scripts may not be visible even live

Live queries for the `automation` and `script` domains return
`"No exposed entities found"`. That confirms they are not exposed to
Assist; it does **not** prove none exist. Evidence suggests automation-like
behaviour is configured somewhere (Hue Bridge automation switches,
motion-sensor-enabled toggles, AC "Climate React" logic), possibly in
device-native engines rather than as Home Assistant `automation.*` entities.

Whether native automations exist at all is genuinely unresolved.

## How to unblock — in order

Each step is a manual action on the live instance. None can be performed
from this repository.

### 1. Take a full backup first

Settings → System → Backups → Create backup (full), and download it off
the device. Do this before anything else.

### 2. Get file-level access to `/config`

Install **one** of the following Home Assistant add-ons:

- **Studio Code Server** (recommended — browse and copy files in-browser)
- **File Editor** (lighter alternative)
- **Samba share** or **Advanced SSH & Web Terminal** (best for bulk copy)

### 3. Export the real config, with secrets stripped

From `/config`, retrieve:

- `configuration.yaml`
- `automations.yaml`, `scripts.yaml`, `scenes.yaml` (if present)
- `themes/` (or `themes.yaml`)
- `dashboards/` — **only if dashboards are in YAML mode.** If dashboards
  are UI-managed (the default), their config lives in
  `.storage/lovelace*` instead. That file is JSON, not YAML, and
  `.storage/` must never be committed to git. Convert it: open the
  dashboard → three-dot menu → **Raw configuration editor** → copy the
  YAML shown there. That YAML is what belongs in `dashboards/`.

Before committing anything, replace every literal secret (tokens, API
keys, passwords, Wi-Fi SSID, latitude/longitude, street address, external
URLs) with a `!secret <key>` reference. `secrets.yaml` itself is
gitignored and stays on the device.

### 4. Capture real entity IDs

Developer Tools → States lists every `entity_id` on the instance. Export
that list and use it to populate `docs/entity_inventory.md` on `main` with
actual IDs. Until this exists, no YAML in this repo may name an entity.

### 5. Commit the live files verbatim as a baseline

Commit exactly what was read, unmodified, as the first real commit on this
branch. This is the rollback point. Only after that baseline exists should
any change be made — as a small, reviewable diff against known-good
production config.

### 6. Only then wire up the Git Pull add-on

Point it at branch `ha-deploy`, with `auto_restart: false` initially.
Verify the first pull changes nothing unexpected before trusting it.

## Bottom line

This branch is safe: it cannot break a running Home Assistant instance,
because it contains nothing Home Assistant will parse. It is also not yet
useful, because the live configuration it is meant to carry has never been
readable from here.

The correct next step is **step 2 above — file-level access to `/config`** —
not writing configuration into this branch from inference.
