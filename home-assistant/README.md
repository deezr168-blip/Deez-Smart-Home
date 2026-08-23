# Home Assistant configuration

Contents of this folder:

| Path | What it is |
|---|---|
| `dashboards/casaray_home.yaml` | The CasaRay-style dashboard (YAML mode). |
| `dashboards/generated/` | The only entity-specific config. Ships as working stubs; filled in from your live registry by `scripts/ha_verify.py --write`. |
| `packages/casaray_summary.yaml` | Template sensors behind the summary badges. No hardcoded entity IDs. |

Design rationale and the mapping to CasaRay's model: [`docs/casaray_dashboard.md`](../docs/casaray_dashboard.md).

Requires **Home Assistant 2025.2 or newer** — sections views, the heading card,
the redesigned area card with `area-controls`, and the `area` view strategy all
landed in that release.

---

## Install

Nothing here replaces or edits your existing dashboard. This adds a second one
alongside it, so you can flip between the two and delete this one if you don't
like it.

### 1. Copy the files into your HA config directory

```
<ha-config>/
  casaray/
    casaray_home.yaml            <- from home-assistant/dashboards/
    generated/
      home_badges.yaml
      cameras.yaml
  packages/
    casaray_summary.yaml         <- from home-assistant/packages/
```

The `!include` paths inside `casaray_home.yaml` are relative to that file, so
keep `generated/` as a sibling directory.

### 2. Enable packages (skip if you already have them)

In `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

### 3. Register the dashboard

Also in `configuration.yaml`:

```yaml
lovelace:
  mode: storage          # leave your existing UI dashboards alone
  dashboards:
    casaray:
      mode: yaml
      title: Home
      icon: mdi:home-variant
      show_in_sidebar: true
      filename: casaray/casaray_home.yaml
```

The dashboard's URL prefix must stay `casaray` — the internal navigation links
(`/casaray/living_room` and friends) are built from it. If you rename the key,
run a find-and-replace for `/casaray/` in `casaray_home.yaml`.

### 4. Check the config, then restart

Developer Tools → YAML → **Check configuration**, then restart Home Assistant.

### 5. Verify area IDs

The dashboard's cards are addressed by **area ID**, and area IDs are not
guessable with certainty — they're assigned when an area is created and don't
always match the current name. Confirm them once:

```bash
export HA_URL=http://homeassistant.local:8123
export HA_TOKEN=<long-lived access token>   # Profile -> Security -> Long-lived access tokens

python3 scripts/ha_verify.py
```

It prints every area in your instance, flags any ID the dashboard references
that doesn't exist, suggests the closest real match, and exits non-zero if
anything is wrong. It is read-only and never writes to Home Assistant.

### 6. Fill in the entity-specific bits

```bash
python3 scripts/ha_verify.py --write
```

This reads your live registry and rewrites `generated/cameras.yaml` (one card
per camera, grouped by area) and `generated/home_badges.yaml` (your real weather
and person entities). Re-run it whenever you add a camera or a person; it's
idempotent.

Optionally refresh the entity inventory in this repo:

```bash
python3 scripts/ha_verify.py --inventory     # rewrites docs/entity_inventory.md
```

---

## Rollback

Remove the `lovelace:` block added in step 3 and restart. The dashboard
disappears; your existing dashboards were never touched.

To also drop the helper sensors, delete `packages/casaray_summary.yaml` and
restart. Nothing else in your config depends on them.

---

## Why there are almost no entity IDs in here

`docs/entity_inventory.md` is this repo's rule that entity IDs are never
invented or guessed. This dashboard honours that by being built almost entirely
out of things that aren't entity IDs:

- **Area cards and area view strategies** address rooms by area ID and populate
  themselves from whatever is in the room.
- **Group buttons** target `entity_id: all` within a domain, so "lights off"
  means every light, not a list someone has to maintain.
- **Summary sensors** iterate live state objects (`states.light | selectattr(...)`)
  rather than naming entities.

The consequence: no card in this dashboard can point at an entity that doesn't
exist, and none of it goes stale when a device is renamed or replaced. The
handful of genuinely entity-specific cards — cameras, people, weather — are
isolated in `generated/` and written from your live registry, never by hand.
