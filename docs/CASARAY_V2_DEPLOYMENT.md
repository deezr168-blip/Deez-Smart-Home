# CasaRay v2 — registration and deployment runbook

Everything repository-side is done. What remains is registering the dashboard
in Home Assistant, which only the owner can do.

**Status:** `origin/ha-deploy` carries CasaRay v2 with all 87 internal links on
`/casaray-v2/`, 0 references absent from the B1 entity export, and validation
passing 7/7.

---

## The push problem is already solved

The URL-path migration was run on the Home Assistant host, but its push failed
on GitHub authentication. Rather than fix credentials from an iPad, the same
migration was reproduced in the cloud session and pushed.

This was verified, not assumed: `origin/ha-deploy` at `08e632d` still had 87
`/casaray/` links. It now has 87 `/casaray-v2/` links, at `2203fc1`.

`scripts/migrate_casaray_url_path.sh` does one deterministic global replace and
asserts the before/after counts match, so the pushed result is equivalent to
what the host produced. **The host does not need working push credentials.** It
only needs to fetch.

---

## Owner steps — one command at a time

Run these in the **Terminal & SSH** add-on. Each is a single line.

### 1. See whether the host clone has anything unpushed

```sh
git -C /config log --oneline origin/ha-deploy..HEAD
```

**Expected: one commit**, the URL-path migration. That one is now on GitHub, so
it is safe to discard.

- **Nothing listed** → the clone is already clean. Skip to step 3.
- **Only the migration commit** → continue to step 2.
- **Anything else listed** → stop and paste it back. It is work that exists
  nowhere else and must be saved first.

*(If `/config` is not the clone, find it with
`grep -n 'cd \|git ' /config/deploy_deez_dashboard.sh` and use that path in
place of `/config` throughout.)*

### 2. Fetch

```sh
git -C /config fetch origin ha-deploy
```

### 3. Take the GitHub version

```sh
git -C /config reset --hard origin/ha-deploy
```

### 4. Confirm the dashboard file is where the config will look for it

```sh
ls -l /config/dashboards/
```

**Both** `casaray_v2.yaml` and `deez_smart_home.yaml` must be listed. If
`casaray_v2.yaml` is missing, stop — the deploy script only syncs the legacy
file and needs a line adding. Say so and it will be prepared.

### 5. Confirm the links migrated

```sh
grep -c "/casaray-v2/" /config/dashboards/casaray_v2.yaml
```

**Expected: 87.** If it prints 0, step 3 did not take effect.

### 6. Add the dashboard to `configuration.yaml`

Open `/config/configuration.yaml` in the File editor add-on. Find the existing
`lovelace:` block and add the `casaray-v2:` entry **beside** the existing one —
do not replace it:

```yaml
lovelace:
  dashboards:
    deez-smart-home-yaml:
      mode: yaml
      title: Deez Smart Home YAML
      icon: mdi:home-assistant
      show_in_sidebar: true
      filename: dashboards/deez_smart_home.yaml
    casaray-v2:
      mode: yaml
      title: CasaRay
      icon: mdi:home-heart
      show_in_sidebar: true
      filename: dashboards/casaray_v2.yaml
```

Indentation matters: `casaray-v2:` sits at the same depth as
`deez-smart-home-yaml:`, and its five options are indented one level under it.

### 7. Validate the configuration BEFORE restarting

```sh
ha core check
```

**Do not restart until this passes.** If it fails, paste the output back.

### 8. Restart Home Assistant

Settings → System → top right → **Restart Home Assistant**.

A new YAML dashboard needs a **full restart**. Reloading the Lovelace
configuration will not register it.

### 9. Open it

```
/casaray-v2/home
```

A **CasaRay** entry with a heart-house icon should also appear in the sidebar.

---

## What to check once it loads

Tick these off in `LIVE_VERIFICATION_QUEUE.md` or just report what breaks.

### Navigation — every one of these should open

`/casaray-v2/home` · `rooms` · `energy` · `security` · `cameras` · `bills` ·
`entertainment` · `alerts` · `house-health` · and one room, e.g.
`living-room`.

On Home, the 8 nav buttons should all land somewhere. Room pages have Back and
Home buttons; Back goes to `rooms`, and from a camera subview to `cameras`.

### The B1-unblocked features

These were connected from the entity export and have never rendered:

| Check | Where | Expect |
|---|---|---|
| **Scene buttons** | Living Room, Dining, Ray Bedroom quick actions | Tap one — the lights change. Scenes never yet activated show no state; that is normal, not an error. |
| **Air quality** | Living Room, Home indoor climate | PM2.5 / PM10 / PM1 with a health-concern word. |
| **Solar forecast** | Energy | Today / tomorrow / peak-time figures. These work even when the inverter is down. |
| **People batteries** | People | Phone and iPad battery percentages. |
| **Automations board** | Alerts / House Health | Three automations, each with a working enable toggle. |

### Known-offline, not a bug

These will show unavailable because the hardware is down, and the cards are
written to say so honestly:

- All three contact sensors (`b`/`f`/`m`) — **doors cannot be confirmed**
- East Wall and South Wall camera streams
- The four Living Room Hue spots
- The LetPot grow unit, Kogan TV, Pogo

### The two things most likely to be wrong

Both are mechanisms that have never rendered:

1. **Section headings** — flip the Chinese toggle on Home. Exactly one heading
   per section: English off, Simplified Chinese on. If **both** or **neither**
   show, the `visibility` conditions are the fault.
2. **The clock** — every board except the six camera subviews. Time above,
   date below, reading `DD/MM/YY` — `05/09/26`, not `05/09/2026`.

---

## Rollback

The legacy dashboard is untouched and still registered at
`deez-smart-home-yaml`. If CasaRay misbehaves, it costs nothing: delete the
`casaray-v2:` block from `configuration.yaml` and restart. Nothing else is
affected.
