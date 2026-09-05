# B1 — the entity export

**One copy-and-paste on the Home Assistant machine.** It unblocks more CasaRay
work than anything else outstanding, and it takes about a minute.

---

## Why this is needed

Claude reads the live instance through a read-only Home Assistant connector.
That connector returns **friendly names only** — "Living room Bright",
"Parents Room AC" — and **never entity IDs**. It also only sees entities that
are exposed to Assist, which is a minority of them.

So Claude can prove an object *exists*, but cannot address it. And the rule that
keeps this dashboard honest is that **an entity ID is never invented**. The
result is a list of things that are confirmed real and still cannot be built:

| Blocked right now | What the export unlocks |
|---|---|
| **29 Hue scenes** | Quick Actions on every room page, and the whole Lighting board's scene rows |
| **All automations and scripts** | The Automations board — nothing of it can be built today |
| Air-quality sensors (PM1 / PM2.5 / PM10 / CAQI) | Air quality on Home, Living Room, Dining, Kitchen — the mockups ask for it on all four |
| Solar production forecast | Energy forecast, which works **even while the inverter is offline** |
| Per-person device batteries | The People board's battery and ETA columns |
| Shopping List, Family Location helper | A Kitchen list, and a People control that already exists but has no surface |
| Tapo camera detection controls, hub health | Camera board controls and House Health rows |

**You do not need to work out which entities Claude needs.** The export below is
everything. Claude does the reconciliation from it.

---

## The procedure

1. Open Home Assistant.
2. Go to **Developer tools** → the **Template** tab.
3. Delete whatever is in the left-hand editor.
4. Paste this in, exactly:

```jinja
{%- for s in states -%}
{{ s.entity_id }}|{{ s.name | replace('|','/') }}|{{ area_name(s.entity_id) or '-' }}|{{ 'unavailable' if s.state == 'unavailable' else ('unknown' if s.state in ['unknown','none',''] else 'ok') }}
{% endfor -%}
```

5. The right-hand pane fills in with one line per entity. Wait for it to settle.
6. **Select the whole right-hand result and copy it.**
7. Either paste it straight into the chat, or save it as
   `docs/states_export.txt` in the repository and say it is there.

That is the whole task.

### If the result pane is slow or truncated

Some instances struggle rendering every entity at once. Run it one domain at a
time instead, changing `'scene'` each time and copying each result:

```jinja
{%- for s in states.scene -%}
{{ s.entity_id }}|{{ s.name | replace('|','/') }}|{{ area_name(s.entity_id) or '-' }}|{{ 'unavailable' if s.state == 'unavailable' else ('unknown' if s.state in ['unknown','none',''] else 'ok') }}
{% endfor -%}
```

In priority order, the domains that unblock the most: **`scene`**,
**`automation`**, **`script`**, then `sensor`, `input_select`, `input_number`,
`input_boolean`, `input_datetime`, `input_text`, `todo`, `event`, `select`,
`number`, `button`.

---

## What the export contains, and what it deliberately does not

Each line is four fields separated by `|`:

```
sensor.front_door_battery|Front Door Battery|Living Room|ok
scene.living_room_bright|Living room Bright|Living Room|ok
camera.tapo_c420_east_wall_hd_stream_direct|Tapo C420 East Wall HD Stream (Direct)|Network|unavailable
```

`entity_id` · `friendly name` · `area` · `availability`.

**It carries no state values.** That is deliberate, not an oversight. A raw
States dump would include things this repository must never hold — the
`sensor.*_geocoded_location` entities contain the home's street address, and
device trackers carry coordinates. The fourth field is reduced to
`ok` / `unavailable` / `unknown`, which is everything Claude needs to know
about health and nothing it needs to know about you.

So the export is **safe to commit**. No tokens, no passwords, no URLs, no
addresses, no coordinates. Entity IDs and area names are not credentials. The
repository's secret scanner runs over it like any other file.

---

## What Claude does with it

1. Regenerates `docs/entity_inventory.md` from the export — every ID, real
   name, area and availability, replacing the 78 rows currently marked
   `NOT EXPOSED` because the connector could not see them.
2. Checks every entity ID in `dashboards/casaray_v2.yaml` against it and
   reports any that no longer resolve.
3. Resolves the open `⚠ CHECK` items in the inventory —
   `switch.bedroomlight_switch_1` reporting in the `light` domain,
   `input_number.gas_bill_mj` versus the live "Gas Bill Usage MJ", and the
   fourth Living Room Hue spot.
4. Builds the surfaces the export unblocks, in the table at the top.

That is ladder step 3 in `PROJECT_STATE.md`.

---

## Where this sits

Step **2** of the Main queue ladder. Step 1 is `CFG-003`, the delivery-path
repair, whose procedure is in `DASHBOARD_ISSUES.md` under *Owner recovery, on
the host*.

The two are independent — neither blocks the other, and either can be done
first. This one is the smaller job by a wide margin.
