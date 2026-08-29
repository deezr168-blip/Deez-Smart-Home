# Installing the CasaRay × Your Name theme

Two files go onto the Home Assistant host. Neither reaches it through the
`ha-deploy` bridge — that path is documented as applying
`dashboards/deez_smart_home.yaml`, and whether it also syncs `themes/` is
unknown from this environment, so treat this as a one-time manual install.

## 1. The background image

```sh
mkdir -p /config/www
cp your_name_night_sky.jpg /config/www/your_name_night_sky.jpg
```

The filename is referenced verbatim by the theme, so keep it exactly
`your_name_night_sky.jpg` — lowercase, underscores, no spaces. `/config/www/`
is served at `/local/`, so the file becomes
`/local/your_name_night_sky.jpg`.

## 2. The theme

```sh
cp themes/deez_your_name.yaml /config/themes/deez_your_name.yaml
```

`configuration.yaml` needs, once:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

Then **restart Home Assistant** (not just "reload themes" — see below).

## 3. Verify the image actually loads

Before judging the design, confirm the asset resolves. In a browser tab
already logged in to Home Assistant, open:

```
http://<your-ha-address>/local/your_name_night_sky.jpg
```

You should see the picture. If you do not, work through this list — these are
the causes of the 404/401 you hit previously, in the order they actually
occur:

| Symptom | Cause | Fix |
|---|---|---|
| **404**, file is definitely in `/config/www/` | `www/` did not exist when Home Assistant started. The static route for `/local/` is registered **at startup**, so a folder created afterwards is not served. | Restart Home Assistant. This is by far the most common cause. |
| **404** | Filename case or spacing differs. `/local/` is case-sensitive. | Match `your_name_night_sky.jpg` exactly. |
| **404**, correct name, after a restart | The file landed in `/config/` rather than `/config/www/`, or in an add-on's own container filesystem rather than the shared `/config`. | Check with `ls -l /config/www/`. |
| **401** | The URL was written as `/config/www/...` or `/api/...` rather than `/local/...`. Those are authenticated endpoints; `/local/` is not. | Use `/local/your_name_night_sky.jpg`. |
| **401**, correct `/local/` path | A reverse proxy in front of Home Assistant is requiring auth for static paths. | Allow `/local/` through the proxy. |
| Loads in a tab, still blank behind the dashboard | Browser cached the earlier failure. | Hard-reload the iPad tab; on iOS, close the tab and reopen. |
| Loads, but the dashboard is plain dark | The theme is not applied. | Profile → Theme, or confirm the six theme names below exist under Developer Tools → template `{{ themes }}`. |

## 4. What the theme defines

One file, six themes, one shared base. The dashboard references all six by
name — `Deez Smart Home` at the root plus `Deez Cameras`, `Deez Climate`,
`Deez Energy`, `Deez Lighting` and `Deez Security` per view — so all six must
exist or those views fall back to the default theme.

Each shares the palette, the frosted-glass surface and the background, and
differs only in accent colour: cyan for the home view (the comet), cooler
blue for cameras, teal for climate, ember for energy, warm gold for lighting,
violet for security (the fragment beside the comet).

Colours are sampled from the image rather than invented:

| Token | Sampled from |
|---|---|
| `#0b1524` base | deepest sky at the top of the frame |
| `#101f36` surface | midnight blue behind the clouds |
| `#7fd4f0` primary accent | the comet's cyan core |
| `#b078d8` violet accent | the magenta fragment beside it |
| `#f0a860` / `#ffc98a` warm accents | the horizon glow and the city lights |
| `#eef3f9` text | starlight |

## 5. The frosted glass is global, not per-card

The theme carries a `card-mod-theme` block, so every card on every view gets
the backdrop blur and the translucent surface from one place:

```yaml
card-mod-card: |
  ha-card {
    backdrop-filter: blur(14px) saturate(118%);
  }
```

This matters for maintenance: new cards inherit the treatment automatically,
and the ~100 per-card `card_mod` blocks currently in the dashboard become
redundant. They are being removed progressively rather than in one sweep, so
the dashboard stays revertible batch by batch.

Browsers without `backdrop-filter` fall back to the translucent background
alone, which still reads correctly — it is a progressive enhancement, not a
requirement.

## 6. If it looks wrong

Reverting the theme is safe and instant: remove
`/config/themes/deez_your_name.yaml`, restart, and the dashboard returns to
whatever the previous six themes did. No dashboard YAML depends on this file
existing — the view `theme:` keys were already there.
