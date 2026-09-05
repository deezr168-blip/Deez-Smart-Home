# CasaRay v2 — architecture, entity migration and delivery report

A ground-up rebuild of the CasaRay dashboard as `dashboards/casaray_v2.yaml`,
built on the frozen CasaRay Design v1. The production dashboard
`dashboards/deez_smart_home.yaml` is **untouched** and still the running
system; v2 is a parallel implementation, not a replacement, until the owner
chooses one.

- **Created:** 2026-09-05, against `ha-deploy` at `b65497a`.
- **Design authority:** *CasaRay Master Design Briefing v1* (Drive) and
  `DESIGN_REFERENCE.md`.
- **Entity authority:** `docs/entity_inventory.md`.
- **Buildability authority:** `docs/CASARAY_MAPPING_PACK.md`.

---

## Phase 2 — Architecture

### What is deliberately different from the old dashboard

The brief asked for an architecture, not a reskin. The old file is
222 KB across 4,884 lines: 212 Mushroom cards, 108 `card_mod` blocks, and a
bilingual template wrapped around nearly every one. v2 is 105 KB across 3,326
lines and inverts that dependency profile, following briefing §20's ladder literally
rather than aspirationally.

| | `deez_smart_home.yaml` | `casaray_v2.yaml` |
|---|---|---|
| Custom card types | 6 (`mushroom-*` ×5, `webrtc-camera`) | **1** (`webrtc-camera`) |
| Mushroom card uses | 212 | **0** |
| `card_mod` blocks | 108 | **0** |
| Jinja templates | 426 | 49 |
| Views | 36 | 25 |
| Native `tile` cards | 50 | **252** |
| Size | 222 KB / 4,884 lines | **105 KB / 3,326 lines** |

`card_mod` is gone entirely: surface treatment belongs to
`themes/deez_your_name.yaml`, which every card already inherits. That is the
briefing's "global first" rule taken seriously. Dropping Mushroom removes the
single largest maintenance liability — if that resource ever fails to load,
the old dashboard is 212 blank cards; v2 loses six camera streams.

### The native ladder, as actually used

1. **Sections layout**, `max_columns: 2` on every non-subview. iPad landscape
   renders about two usable columns whatever the mockups show.
2. **`heading` cards** for every section label, with entity badges where a
   heading benefits from live state.
3. **`tile` cards with features** for all control: `light-brightness`,
   `cover-open-close`, `cover-position`, `numeric-input`.
4. **Native domain cards** where one exists: `thermostat` (Parents Room AC),
   `media-control` (×6), `weather-forecast`, `picture-entity`,
   `history-graph` (×8), `statistics-graph`.
5. **`conditional`** for all 31 alerts, so a healthy house shows nothing.
6. **`markdown`** for the interpretation layer — the briefing's requirement
   that CasaRay present interpreted information rather than raw entities.
   Native, template-capable, and no dependency.
7. **`custom:webrtc-camera`** only on the six camera detail subviews, where a
   low-latency live stream has no native equivalent. The camera *grid* uses
   native `picture-entity`.

### Navigation model

`kiosk_mode` hides Home Assistant's own sidebar, and Lovelace cannot render a
custom one without `layout-card`, which is not installed. The mockups'
persistent 12-item left rail is therefore **not reproducible** and was not
faked. Instead:

- **Home** carries an 8-button primary nav (Rooms, Energy, Security, Cameras,
  Bills, Entertainment, Alerts, Health) as native `button` cards.
- **Every other view** opens with a Home button; room views add a Back button.
- **Back** returns to the logical parent — `rooms` from a room, `cameras` from
  a camera subview. Lovelace has no native browser-back action, so "previous
  page" is approximated by parent, which is the brief's
  "where technically feasible".
- All **85 navigation links resolve**; every one of the 25 views is reachable.

### Bilingual behaviour

`input_boolean.chinese_dashboard` is preserved and still drives the interface,
but at a different altitude. The old dashboard templated nearly every card,
which is most of why it is 222 KB. v2 translates the layer that carries
meaning — page titles, room summaries, interpreted status — and leaves device
rows as native tiles showing the device's own name. A reader who does not read
English identifies "Dining light" by icon, position and state, not by its
label; a reader who needs to know whether the house is secure needs that
sentence in their language.

**Script: Simplified Chinese.** v2 first shipped in Traditional, Taiwan-standard
Chinese — `攝影機`, `感測器`, `帳單`, `扇門開著` — while
`dashboards/deez_smart_home.yaml` has been Simplified throughout its 304
bilingual strings: `摄像头`, `传感器`, `账单`, `扇门开启`. Two dashboards driven by
the same household toggle cannot disagree about which Chinese the household
reads, and production's is the only established convention in the repository,
so v2 was converted to match it — script **and** vocabulary, reusing
production's exact phrasing wherever production already had one. Corrected in
`885b03a`. New Chinese strings follow production's wording; grep it before
inventing a term.

**Coverage: the meaning layer is now complete.** The rule above was stated
before it was fully implemented. As first shipped, every page had a bilingual
*title* but an English-only *subtitle*, and none of the eight interpreted-status
panels translated at all — so in Chinese mode a reader got `客厅` followed by
"Temperature not reporting · no motion", and a House Health page that was
entirely English. `3faa830` closes that: all 13 room and board summaries and
all 8 status panels are bilingual, plus the three "why this panel is absent"
notes, which are on-screen text like anything else.

Where a list is rendered into a sentence, the **items** are translated too, not
just the sentence around them — the camera roll-up names `东墙、南墙`, House
Health names `前门、门铃、北墙摄像头`, and Bills names `电费` — via a Chinese
label carried alongside the English one in the same tuple. Chinese enumerations
use `、`, not `,`. Proper nouns stay Latin: CasaRay, Hue, Fronius Primo, eero,
Lovelace, WAN, Ray.

**Still English: the 70 `heading` cards** — "Needs attention", "Lights",
"Power outlets". They are section labels rather than page titles, room
summaries or interpreted status, so they sit outside the rule as written, and
translating them is a change to the rule rather than a completion of it. That
is an owner decision, not an autonomous one. Everything the rule does cover is
now done.

### View list (25)

| Path | Title | Sub | Justification |
|---|---|---|---|
| `home` | CasaRay | | Executive overview |
| `rooms` | Rooms | | Room index, Back target |
| `living-room` | Living Room | | 15 entities |
| `kitchen` | Kitchen | | 7 entities |
| `dining` | Dining | | 8 entities |
| `parents-room` | Parents Room | | 18 entities, the only `climate` |
| `ray-bedroom` | Ray Bedroom | | 13 entities incl. grow unit |
| `garage` | Garage | | 6 entities |
| `guest-room` | Guest Room | | 8 entities |
| `lighting` | Lighting | | 11 lights + 3 wall switches |
| `climate` | Climate | | Thermostat + 4 readings |
| `energy` | Energy | | Powerpal, Fronius, 2 metered circuits |
| `bills` | Bills | | 51 helpers + 7 bill sensors |
| `security` | Security | | 3 doors, 4 motion, 6 cameras |
| `cameras` | Cameras | | 6 cameras |
| `camera-*` ×6 | per camera | ✓ | Live stream detail |
| `people` | People | | 3 persons + home zone |
| `entertainment` | Entertainment | | 3 media players |
| `house-health` | House Health | | Batteries, network, backups, offline |
| `alerts` | Alerts | | 31 live conditions, 3 severities |

### Pages the briefing asks for that were NOT created

Per the brief's "do not create empty pages simply to satisfy this list":

| Page | Why not |
|---|---|
| **Bathroom** | No Bathroom area and no Bathroom entity of any domain exists. The mockup page has nothing behind it. |
| **Automations** | No `automation.*` or `script.*` entity ID can be read from this environment (blocker B1). A board listing nothing is worse than no board. |
| **Water & Gas** | No water or gas metering sensor exists. The only water/gas figures are bill helpers, which live on Bills where they belong. |
| **Network** | An eero WAN binary sensor and a remote-UI sensor do not justify a page. Merged into House Health. Throughput, uptime and a device map have no sensors at all. |
| **Lighting Studio scenes** | 29 Hue scenes exist live; their entity IDs cannot be read (B1). `lighting` ships with real per-light control and no scene row rather than a guessed `scene.living_room_relax`. |
| **Settings** | Nothing to put on it beyond the language toggle, which sits on Home. |

### Mockup components deliberately absent

Each of these appears in an approved mockup and has **no data source**:

- Alarm arm/disarm and "Armed (Away)" — no `alarm_control_panel` entity.
- Door lock rows — no `lock` entity.
- Garage door open/close — no `cover` in Garage (the only cover is Ray
  Bedroom's roller shade).
- Grid import/export, battery charge — no such sensor.
- Room hero photography — no images in `/config/www` (blocker B5).
- Spending trend, payment history, YTD totals — blocker B6.
- Mark-as-read, alert history, quiet hours — no notification entity exists to
  store the state. A read flag that resets on refresh is worse than none.

---

## Phase 3 — Entity migration map

**No working entity was dropped.** v2 references **all 164** real entity IDs
the production dashboard uses — the same set, neither extended nor reduced.
The four service names (`light.turn_on/off`, `input_boolean.turn_on/off`) are
not entities and are excluded throughout.

| Action | Count |
|---|---|
| **RETAIN** — same entity, same conceptual page | **158** |
| **RELOCATE** — same entity, better page | **6** |
| **REPLACE** — superseded by a better existing entity | **0** |
| **DEPRECATED** — no longer used | **0** |
| **NEW / invented** | **0** |

| Verification status | Count |
|---|---|
| Confirmed live against the instance | **74** |
| Live but currently `unavailable` (hardware down, cards correct) | **12** |
| Requires Home Assistant verification (not exposed to Assist) | **78** |

### The six relocations

| Entity | From | To | Reason |
|---|---|---|---|
| `switch.genio_power_board_with_usb_livingroom_socket_1`…`_5` | `parents-room` | `living-room` | **Owner check — see below.** |
| `sensor.tapo_camera_bcca_battery` | `home` | `cameras`, `house-health` | Battery readings consolidated onto the two pages that own device health. |

> ### ⚠ Owner check: the Genio power board
>
> The production dashboard puts these five sockets on the **Parents Room**
> page. Two independent sources disagree with it: the entity ID says
> `...usb_livingroom_socket_N`, and the live area registry assigns all five to
> **Living Room**. The brief's source-of-truth order puts the entity inventory
> above the existing dashboard for device/entity relationships, so v2 follows
> the inventory and shows them on Living Room.
>
> **If the board is physically in the Parents Room**, five working controls are
> now on the wrong page and this must be reverted. That is a two-minute
> look at the wall. It is flagged rather than silently "fixed" because the
> production placement may encode something the registry does not.

### Deliberate non-changes

- **`bedroom_motion_sensor_*` stays on Parents Room.** The device was renamed
  to *Parents Room Motion Sensor*; the entity IDs kept the old `bedroom_` slug.
  Every such reference is a Parents Room reading and v2 uses them that way.
  Do not repoint them at Ray Bedroom.
- **`switch.bedroomlight_switch_1` is unchanged**, despite the live instance
  reporting that object in the `light` domain while its two sibling switches
  remain `switch`. Most likely a *change device type* helper, which leaves the
  original entity working. Flagged in the inventory; not touched here.
- **The four unavailable Hue spots are retained.** The cards are correct; the
  bridge is not answering. Living Room and Lighting both say so in words
  rather than showing four dead toggles with no explanation.

### Full table

The complete per-entity map — old location, new location, action, live status
and verification state for all 164 — is generated by the command in
*Maintenance* below and reproduced in `docs/CASARAY_V2_ENTITY_MAP.md`.

---

## Phase 5 — Static QA results

| Check | Result |
|---|---|
| YAML syntax | **PASS** — parses clean |
| Duplicate keys | **PASS** — none |
| Jinja templates compile | **PASS** — 49/49 |
| Entity references vs. inventory | **PASS** — 164 used, **0 invented** |
| Entities dropped from production | **PASS** — 0 |
| Navigation targets resolve | **PASS** — 85 links, 0 broken |
| Views reachable | **PASS** — 25/25, none orphaned |
| Duplicate view paths | **PASS** — none |
| Inert card properties | **PASS** — 0 |
| Banned numeric sentinels (`float(0/100/9999)`) | **PASS** — 0 |
| Unavailable-state handling | **PASS** — every interpreted read has an explicit unavailable branch |
| Custom component dependencies | **PASS** — 1 (`custom:webrtc-camera`), proven installed |
| `bash scripts/ha_validate.sh` | **PASS** 7/7, exit 0 |
| `ha core check` | **NOT AVAILABLE** — no `/config`, no supervisor, no API route |

### Tooling change made to support this

`scripts/dashboard_check.py` hardcoded `/deez-smart-home/` when resolving
navigation links, so it silently reported **0 internal links** for any other
dashboard — v2's 85 links were invisible to the gate. It now infers each
dashboard's `url_path` prefix from the links themselves: a prefix whose
targets resolve against that file's own view paths is that dashboard's, and a
prefix where none resolve is a link into a *different* dashboard and stays
unchecked. Production still reports 36/36 broken=0, unchanged; v2 now reports
25/25 broken=0; and a deliberately broken link was confirmed to fail the check
with exit 1.

---

## What must be verified in the live interface

Repository checks cannot substitute for any of this. Valid YAML is not valid
Lovelace.

1. **Register the dashboard at url_path `casaray`.** Every one of the 85
   navigation links is `/casaray/<view>`. Mounted at any other path, all
   internal navigation breaks. This is the single highest-risk item.
2. **`CFG-003` is still open.** The deployment bridge does not deliver, so
   nothing here reaches the instance until the owner runs the recovery on the
   host. v2 cannot be seen, let alone verified, before that.
3. **Card schema.** 25 views of native cards have never been rendered. Check
   in particular: `heading` badges, `tile` `features_position` defaults,
   `numeric-input` on the fridge setpoints, `statistics-graph` on
   `sensor.powerpal_gateway_powerpal_daily_energy` (needs long-term
   statistics to exist for that sensor).
4. **The 78 unverified entity IDs**, above all the 51 bill helpers. If a
   helper does not exist, its tile renders as unavailable rather than
   breaking the view — but the Bills board would be substantially empty.
5. **The Genio power board placement** — see the owner check above.
6. **iPad landscape.** Confirm two columns read correctly and no label
   truncates; `max_columns: 2` is set on every non-subview.
7. **Bilingual toggle.** Confirm the Chinese strings render and that the
   toggle on Home flips them. Confirm they are **Simplified** and read the
   same way as the old dashboard — `摄像头`, not `攝影機`.
8. **The clock, on every board.** All 19 non-subview pages carry the P1
   clock. Confirm the time sits above the date and the date reads
   `DD/MM/YY` — `05/09/26`, **not** `05/09/2026`. The six single-camera
   subviews have no clock by design.

## Maintenance

Regenerate the entity map when either dashboard changes shape:

```sh
python3 scripts/casaray_v2_entity_map.py > docs/CASARAY_V2_ENTITY_MAP.md
```
