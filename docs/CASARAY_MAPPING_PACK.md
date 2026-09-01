# CasaRay Technical Mapping Pack

**Approved mockup component → CasaRay concept → HA area → real entity →
proposed card → notes and limitations.**

CasaRay Design v1 is frozen. This pack is the bridge between that frozen
design and `dashboards/deez_smart_home.yaml`. It does not restate the design —
`DESIGN_REFERENCE.md` transcribes the mockups and the *CasaRay Master Design
Briefing v1* holds the intent. This file answers one question per component:
**can it actually be built, with what, and if not, what is missing.**

- **Created:** 2026-09-01, against `ha-deploy` at `b6e76f5`.
- **Entity truth:** `docs/entity_inventory.md`, reconciled against the live
  instance the same day.
- **Design truth:** `DESIGN_REFERENCE.md` + the Drive briefing (see
  *Sources* below).

> **No entity ID in this document was invented.** Every ID that appears is
> already referenced by the production dashboard or was confirmed live. Where
> a mockup component needs data that does not exist, the row says so and stops
> there. A mockup showing a metric is not evidence that a sensor for it exists.

## Sources

| Artefact | Where | Note |
|---|---|---|
| CasaRay Master Design Briefing v1 | Google Drive → `CasaRay Mockups/` | 25 sections; the authority on intent and implementation priority |
| 24 rendered mockups (PNG) | Google Drive → `CasaRay Mockups/` | The visual source of truth |
| `DESIGN_REFERENCE.md` | this repo | Screen-by-screen transcription of the mockups |
| `docs/entity_inventory.md` | this repo | What actually exists live |

---

## Status vocabulary

Every component below carries exactly one of these.

| Status | Meaning | What unblocks it |
|---|---|---|
| **AVAILABLE NOW** | Every entity exists and is confirmed. Buildable in the next batch. | — |
| **NEEDS HELPER** | Buildable once an `input_*` helper exists. Low risk, owner-created or Claude-created with approval. | A helper |
| **NEEDS TEMPLATE SENSOR** | The raw data exists; it needs a derived sensor in HA configuration (which this repo does not own). | A template sensor in `configuration.yaml` |
| **NEEDS INTEGRATION** | No integration supplies this data. | Installing/configuring an integration |
| **NEEDS HARDWARE/DATA** | No device produces this measurement at all. | Buying/installing hardware |
| **NEEDS ID EXPORT** | The object exists live, but its entity ID cannot be read from this environment. | One owner export (see *Blocker B1*) |
| **DESIGN ADAPTATION REQUIRED** | The mockup form cannot be reproduced in Lovelace; an HA-native equivalent is specified in the row. | — |

---

## Part 1 — Implementation architecture

### The ladder

The briefing's §20 priority, restated as a decision rule. Take the first rung
that does the job; justify in the commit message any time you skip one.

1. **Native Sections layout** with `grid_options` — never nested `grid` cards.
2. **Native `tile`, `heading`, conditional visibility.** A tile with features
   beats a Mushroom card with a template.
3. **Native `thermostat`, `media-control`, `statistic`, `history-graph`,
   `energy-*`** for their own domains.
4. **Mushroom** where a template genuinely improves the UX — the
   bilingual template cards on this dashboard are the legitimate case.
5. **`card_mod`** only where native styling cannot reach. Prefer the theme.
6. **`auto-entities`** only where dynamic generation removes real maintenance.
   **Not currently installed** — see *Blocker B4*.
7. **Anything else** — needs written justification.

**Global first.** Surface treatment belongs in `themes/deez_your_name.yaml`,
not in a `card_mod` per card. The theme already carries the frosted-glass
`card-mod-card` block that every card on the dashboard inherits.

### Installed custom cards

Only these may be depended on. All three are in use across the current
dashboard and therefore proven installed.

| Resource | Used for | Evidence |
|---|---|---|
| `custom:mushroom-*` (title, chips, template, entity) | Bilingual templated cards, chip rows | ~200 uses |
| `custom:webrtc-camera` | The six camera views | 6 uses |
| `card_mod` | Per-card CSS, plus the theme-level block | Theme + ~40 cards |
| `kiosk_mode` | Sidebar/header suppression | View root |

`auto-entities`, `apexcharts-card`, `mini-graph-card`, `button-card`,
`layout-card`, `swipe-card`, `bubble-card` are **not** installed. Do not
design a component that requires one without first getting it installed.

### Layout constraints that override the mockups

| Mockup assumption | Home Assistant reality | Adaptation |
|---|---|---|
| Persistent left sidebar with 12 nav items | `kiosk_mode` hides HA's sidebar; Lovelace has no custom sidebar without `layout-card` | **DESIGN ADAPTATION REQUIRED** — the existing chip rows (top of Home, bottom "Home Systems") are the navigation. Keep and standardise them. |
| Header with page title, status pills, clock on one line | Views have no header slot | The first section (`column_span: 2`) *is* the header. Title card + clock + chip row. |
| Footer status bar pinned below content | No footer slot | The last section is the footer. Weather + next-bill strip. |
| 4–5 equal KPI cards in a strip | 12-column grid | `grid_options.columns: 3` ×4, or `4` ×3. Both already used in this file. |
| 4 columns × 2 rows of cards on room screens | **iPad landscape renders ~2 usable columns** | Design for 2. `max_columns: 2` is correct and must not be raised. |
| Room hero photograph band | No room photography exists in `/config/www` except the theme background | **NEEDS HARDWARE/DATA** (owner-supplied images). Until then the hero band is a heading + status row. |
| Circular climate dial with +/− | Native `thermostat` card is exactly this | AVAILABLE NOW where a `climate` entity exists |
| Ring gauge for percentages | No native ring gauge; `gauge` card is a semicircle | Use `gauge`. Close enough; do not add a dependency for the arc. |
| Donut with legend | No native donut | **DESIGN ADAPTATION REQUIRED** — horizontal proportion bars, or the native Energy dashboard. |

### Reusable patterns

These are the CasaRay component system (briefing §19) expressed as Lovelace.
Build each one **once**, then reuse verbatim. Where a pattern is already
established in the file, that is noted — reuse the existing form rather than
inventing a second one.

#### P1 — Clock / date  *(mandated form)*

Every clock on every board renders the **time**, and **directly underneath it,
the date as `DD/MM/YY`**. No exceptions, no other date format anywhere a clock
appears.

```yaml
- type: custom:mushroom-template-card
  primary: "{{ now().strftime('%I:%M %p').lstrip('0') }}"
  secondary: "{{ now().strftime('%d/%m/%y') }}"
  icon: mdi:clock-outline
  icon_color: blue
  grid_options: {columns: 4, rows: 1}
```

`primary` is the large line, `secondary` the muted line directly beneath —
which is the mockup's clock exactly. `.lstrip('0')` gives `5:42 PM` rather
than `05:42 PM` without relying on the `%-I` glibc extension, and it is safe
at both ends of the day: midnight renders `12:07 AM`, not `2:07 AM`. `now()`
makes Home Assistant re-render the card at the top of every minute; no helper,
no entity, no polling, and nothing that can go `unavailable`.

**This is the reference instance. Change the pattern here and nowhere else** —
every other board copies it verbatim, and a second variant is how a mandated
format quietly stops being one.

When P1 sits in a page **header** (its normal home) it also takes the
no-surface `card_mod` treatment the title and chip cards already use —
`background: none`, no backdrop filter, no border, no shadow, plus the
`text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` that keeps text legible over
the night-sky background. In a content section it keeps the normal glass card.

**The rationale lives here, not in the YAML.** `dashboards/deez_smart_home.yaml`
contains no comments at all — it round-trips through a YAML dumper on the
storage-mode dashboard path, which would strip them. Explanations go in this
pack; the YAML stays machine-clean.

**Status: AVAILABLE NOW.** First instance: Home header, Batch 1, commit below.

#### P2 — Page header

Section 0 of a view, `column_span: 2`:
title card (or Back pill on a room view) · **P1 clock** · status chip row.
Established: Home already has title + chips; the clock is the addition.

#### P3 — Status strip

A `custom:mushroom-chips-card` of template chips, each
`icon` + `content` + `icon_color` + `tap_action: navigate`. Every chip is
bilingual on `input_boolean.chinese_dashboard` and **must** carry an explicit
`unavailable / unknown / none` branch before any numeric coercion. Established
on Home, Cameras, Security.

#### P4 — KPI / metric card

`custom:mushroom-template-card`, `grid_options.columns: 3` (×4 across) or `4`
(×3). Large value in `primary`, caption in `secondary`, semantic `icon_color`.

#### P5 — Room summary card

`custom:mushroom-template-card` with `tap_action: navigate` to the room view.
Secondary line summarises the room in one sentence. Established — Home's
Rooms section has seven.

#### P6 — Room controls

Native `tile` with `light-brightness` / `target-temperature` /
`cover-open-close` features. Established in Home's Quick Controls.
**Prefer this over a Mushroom light card** — it is native, it is accessible,
and it keeps the control functional.

#### P7 — Alert / attention card

`conditional` wrapping a `custom:mushroom-template-card`. The condition is the
alert's own trigger, so a healthy house shows nothing. Established — Home's
"Active Now" section has 17 of these.

**Never let one assert a reassuring state it cannot see.** "Closed", "Clear",
"Normal", "Up to date" each need a third branch for `unavailable`.

#### P8 — Sensor / status tile

Native `tile`, or a Mushroom template card where the value needs
interpretation ("Comfortable", "Dry / Normal"). Interpretation is CasaRay's
job (briefing §7) — but only over a value that is actually reporting.

#### P9 — Navigation

`tap_action: {action: navigate, navigation_path: /deez-smart-home/<path>}`.
36 view paths exist; `scripts/dashboard_check.py` verifies all 36 internal
links on every validation run. A room view also carries a Back chip to `home`.

#### P10 — Media controls

Native `media-control`. Established on the `media` view.

#### P11 — Camera card

`custom:webrtc-camera` for live view, native `picture-entity` for a preview
tile. Established across the six camera subviews.

#### P12 — Energy metric

Native `statistic` / `energy-*` cards where a statistic exists; otherwise a P4
metric card over the raw sensor. Guard the inverter's `unavailable` — it is
`unavailable` **right now**.

---

## Part 2 — Board-by-board mapping

Columns: **Mockup component** · **CasaRay concept** · **Area** ·
**Real entity / helper** · **Proposed card** · **Status & notes**.

### Global shell & navigation

| Mockup component | Concept | Area | Entity | Card | Status |
|---|---|---|---|---|---|
| `CASARAY` wordmark | Brand | — | — | `custom:mushroom-title-card` | AVAILABLE NOW — currently reads "🏠 Deez Smart Home". Renaming is an owner decision, not a technical one. |
| Left sidebar, 12 items | Global nav | — | — | Chip rows | **DESIGN ADAPTATION REQUIRED** — no custom sidebar without `layout-card`. Chip rows carry the same IA. |
| Active nav highlight | Nav state | — | — | — | DESIGN ADAPTATION REQUIRED — a chip row cannot know the current view. Per-view chip rows can omit their own entry instead. |
| `CasaRay Assist / Tap to speak` | Voice entry | — | — | — | **NEEDS INTEGRATION** — no `assist_satellite` or `conversation` entity exposed. A chip opening HA's Assist dialog is possible; the mockup's mic card is not. |
| Page header clock `5:42 PM` / `12/09/26` | Clock | — | `now()` | **P1** | **AVAILABLE NOW** — Batch 1 |
| `People Home` pill | Presence | — | `zone.home` (=2), `person.raymond_du`, `person.vinh_du`, `person.ai_q_huang` | P3 chip | AVAILABLE NOW |
| `Internet Online` pill | WAN | Network | `binary_sensor.eero_wan_status` | P3 chip | AVAILABLE NOW — already on Home |
| `2 things need attention` pill | Attention count | — | derived from the P7 conditions | P3 chip | **DESIGN ADAPTATION REQUIRED** — a template chip can count the same conditions inline; it cannot count rendered cards. |
| Footer weather cluster | Weather strip | — | `weather.forecast_home` | `weather-forecast` | AVAILABLE NOW |
| Footer `Next Bill` cluster | Bill strip | — | `sensor.bills_unpaid_count`, `sensor.bills_outstanding_total` | P4 | AVAILABLE NOW (already on Home) — both sensors NOT EXPOSED to the connector, so keep their existing `unavailable` guards. |

### Home

| Mockup component | Concept | Area | Entity | Card | Status |
|---|---|---|---|---|---|
| `Good afternoon, Ray` + date | Greeting | — | `now()` | P1 + title | AVAILABLE NOW |
| **HOUSE POWER** — total, solar, grid, battery, sparkline | Live power | Energy | `sensor.primo_5_0_1_1_ac_power` (**unavailable now**), `sensor.powerpal_gateway_powerpal_power` (NOT EXPOSED) | P4 + `history-graph` | **PARTIAL** — solar and whole-house exist. **Grid import/export: NEEDS HARDWARE/DATA. Battery: NEEDS HARDWARE/DATA** (no battery entity exists). Build the three that exist; omit the battery row rather than faking it. |
| **INDOOR CLIMATE** — temp, humidity, air quality, ventilation | Comfort | Living Room / Parents Room | `sensor.living_room_living_hue_hue_sensor_temperature` (18.7), `sensor.bedroom_motion_sensor_temperature` (23.2), `sensor.bedroom_motion_sensor_humidity` (65) | P4 | AVAILABLE NOW for temp + humidity. **Air Quality: AVAILABLE NOW but unused** — the Living Room air purifier exposes PM1/PM2.5/PM10 + CAQI + health-concern sensors. **NEEDS ID EXPORT** for their IDs. Ventilation = the purifier `fan`; also NEEDS ID EXPORT. |
| **SECURITY** — doors, windows, motion, cameras, alarm | Security roll-up | — | `binary_sensor.{m,f,b}_contact_sensor_door`, `binary_sensor.{k_motion_sensor,sensor_group,living_room_living_hue_hue_sensor,bedroom}_motion*`, 6 `camera.*` | P4 + P8 | **PARTIAL** — doors, motion and camera health AVAILABLE NOW. **Windows: NEEDS HARDWARE/DATA. Alarm System: NEEDS INTEGRATION** — no `alarm_control_panel` exists. Do not render "Armed (Away)". |
| **SUNLIGHT** — UV arc, sunrise, sunset | Sun | — | `sun.sun` not exposed; `weather.forecast_home` | `gauge` / P4 | **NEEDS ID EXPORT** for `sun.sun`. UV index: **NEEDS INTEGRATION**. |
| **FAVOURITES** — All Lights, Climate, Movie Time, Good Night | Quick actions | — | 29 Hue scenes exist live | P6 tiles | **NEEDS ID EXPORT** — see *Blocker B1*. This one export converts the whole row. |
| **ROOMS** strip — 5 photo cards | Room summaries | all | 7 room views exist | **P5** | AVAILABLE NOW — already built. Photography: NEEDS HARDWARE/DATA. Per-room temperature is available for **Living Room, Dining and Parents Room only**; Kitchen, Ray Bedroom, Garage and Guest Room have no temperature sensor. |
| **ENERGY TODAY** — generated / consumed / imported / exported, donut | Energy summary | Energy | `sensor.primo_5_0_1_1_energy_day` (**unavailable**), `sensor.powerpal_gateway_powerpal_daily_energy` | P12 | **PARTIAL** — generated + consumed only. **Imported/exported: NEEDS HARDWARE/DATA.** Solar-contribution donut: DESIGN ADAPTATION REQUIRED (proportion bar). |
| **ATTENTION** panel | Exceptions | — | the P7 conditions | P7 | AVAILABLE NOW — 17 already exist; they need grouping under one heading, which is Batch 2. |
| **RECENT ACTIVITY** timeline | Event feed | Living Room | `event.*` for Front Door Ding / Front Door Motion / RingRing / wall switches; `sensor.front_door_last_activity` | `logbook` | **NEEDS ID EXPORT** — event entities confirmed live, IDs unknown. Native `logbook` card is the HA-native equivalent of the mockup timeline. |
| **CAMERAS** preview row | Camera strip | Network | 6 `camera.*` | P11 | AVAILABLE NOW — East Wall and South Wall are **unavailable right now**, so the card must show that, not a black tile. |

### Living Room

| Mockup component | Concept | Entity | Card | Status |
|---|---|---|---|---|
| Status chips — occupancy, temp, lights, TV, air quality | P3 | `binary_sensor.living_room_living_hue_hue_sensor_motion`, `sensor.living_room_living_hue_hue_sensor_temperature`, `light.living_room`, `media_player.living_room_tv_samsung_q9_series_65` | P3 | AVAILABLE NOW. Air quality NEEDS ID EXPORT. |
| Hero photo + tagline | Hero | — | `heading` | NEEDS HARDWARE/DATA (image) |
| Quick Actions — All Off / Relax / Bright / Movie Time | Scenes | 8 Living room Hue scenes exist | P6 | **NEEDS ID EXPORT** |
| Lights — ceiling, ambient, sliders | Lights | `light.living_room`, `light.living_room_hue_ambiance_spot_1..4` | P6 tile + `light-brightness` | AVAILABLE NOW — **all four Hue spots read `unavailable`**; the Hue bridge is not answering. |
| Power Outlets | Outlets | `switch.genio_power_board_with_usb_livingroom_socket_1..5` | P6 tiles | AVAILABLE NOW — five sockets, all on. The mockup shows four; use the five that exist. |
| Entertainment — TV + AVR | Media | `media_player.living_room_tv_samsung_q9_series_65` (on), `remote.*` for the same TV | `media-control` | AVAILABLE NOW for the TV. **AVR: NEEDS HARDWARE/DATA** — no Denon entity exists. |
| Climate dial | Climate | — | — | **NEEDS HARDWARE/DATA** — the only `climate` entity is the Parents Room AC. Living Room has no thermostat. |
| Clock / Timer | Clock | `now()` | **P1** | AVAILABLE NOW for the clock. Timers: **NEEDS HELPER** (`input_datetime` per timer). |
| Sensors — motion, temp, humidity, air quality, sound | P8 | motion + temp + illuminance confirmed | `tile` | PARTIAL — **humidity and sound level: NEEDS HARDWARE/DATA** in this room. |

### Kitchen

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Status chips — temp, motion, lights, rangehood | `binary_sensor.k_motion_sensor_motion` | P3 | PARTIAL — **no Kitchen temperature sensor exists.** Motion AVAILABLE NOW. |
| Quick Actions — All Off / Cooking / Clean Up / Night | — | P6 | **NEEDS ID EXPORT** (no Kitchen Hue scenes observed — may be **NEEDS HELPER** + script instead) |
| Lights — ceiling spots, under-cabinet, pendants, pantry | — | — | **NEEDS HARDWARE/DATA** — no `light` entity in the Kitchen area at all. |
| Power Outlets — bench, island, appliance, fridge | `switch.k_top_p100`, `switch.k_bot_p100`, `switch.k_coffee_p100` | P6 tiles | AVAILABLE NOW — three plugs, named Top / Bot / Coffee. Label them as they are. |
| Appliances — dishwasher, rangehood, kettle, oven | `binary_sensor.lg_fridge_door`, `number.lg_fridge_fridge_temperature` (3 °C), `number.lg_fridge_freezer_temperature` (−18 °C), `switch.lg_fridge_express_mode` | `tile` | **The fridge is the appliance that exists.** Dishwasher / rangehood / kettle / oven: NEEDS HARDWARE/DATA. |
| Shopping list | `todo.*` "Shopping List" | `todo-list` | **NEEDS ID EXPORT** — confirmed live, 0 items. Not in the mockup; a genuine Kitchen win. |
| Entertainment / radio | — | — | NEEDS HARDWARE/DATA |
| Clock / timers | `now()` | **P1** | AVAILABLE NOW |

### Dining Room

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Status chips — temp, lights, motion | `sensor.sensor_group_illuminance` (34 lx), `binary_sensor.sensor_group_motion` (on), `light.dining` (on) | P3 | AVAILABLE NOW. Temperature: the **Dining Room Motion Sensor Temperature** (18.5 °C) and **Bedroom Hue Sensor Temperature** (19.5 °C) are both live in this area — **NEEDS ID EXPORT**. |
| Quick Actions — All Off / Dinner / Bright / Clean | 6 Dining Hue scenes live | P6 | **NEEDS ID EXPORT** |
| Lights | `light.dining`, `switch.dinning_light_switch_1` | P6 | AVAILABLE NOW. `light.corridor_1/2`, `light.dining_light_left/right` are live but **unavailable**. |
| Pet feeder | `camera.smart_pet_feeder`, `light.smart_pet_feeder_indicator_light`, `switch.smart_pet_feeder_{motion_alarm,privacy_mode}` | P11 + tiles | AVAILABLE NOW — already built. Not in the mockup; keep it. |
| Climate dial | — | — | NEEDS HARDWARE/DATA |
| Clock / timers | `now()` | **P1** | AVAILABLE NOW |

### Parents Room

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Status chips — occupancy, temp, lights, climate | `binary_sensor.bedroom_parents_room_ac_room_occupied`, `sensor.bedroom_motion_sensor_temperature` (23.2), `switch.mainroomlight_switch_1`, `climate.bedroom_parents_room_ac` | P3 | AVAILABLE NOW |
| Quick Actions — All Off / Relax / Sleep / Reading | — | P6 | **NEEDS ID EXPORT** (no Parents Room Hue scenes observed — likely **NEEDS HELPER**) |
| Lights — ceiling, bedside ×2, accent | `switch.mainroomlight_switch_1` | P6 | PARTIAL — **one** switched light exists, not four. Bedside/accent: NEEDS HARDWARE/DATA. |
| Power Outlets | `switch.genio_power_board_with_usb_livingroom_socket_1..5` | P6 tiles | ⚠ **The Genio power board is in the Living Room area live, but this dashboard shows it on the Parents Room view.** Live also reports a separate `Master bedroom power point Socket 1–5`. **NEEDS ID EXPORT** to point this view at the right board. |
| Entertainment | `media_player.55_qled_4k_ai` (off), `remote.*` same TV | `media-control` | AVAILABLE NOW |
| Climate / thermostat dial | `climate.bedroom_parents_room_ac` | **native `thermostat`** | **AVAILABLE NOW** — this is the mockup's dial, natively. |
| Emergency buttons | `binary_sensor.emergency_button_{dad,mum}_cloud_connection` | `tile` | AVAILABLE NOW — already built. Not in the mockup; safety feature, keep. |
| Clock / timers | `now()`, `sensor.bedroom_parents_room_ac_timer_end_time`, `switch.bedroom_parents_room_ac_timer` | **P1** + tiles | AVAILABLE NOW |

### Ray Bedroom

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Status chips | `light.bedroom_bedroom` (on), `cover.aqara_roller_shade_driver_e1` (closed) | P3 | PARTIAL — **no temperature or motion sensor in Ray Bedroom.** The Presence Multi-Sensor FP300 is present but **entirely `unavailable`**. |
| Quick Actions — All Off / Focus / Sleep / Night | 14 Bedroom Hue scenes live (`Read`, `Nightlight`, `Nighttime`, `Concentrate`, …) | P6 | **NEEDS ID EXPORT** — the richest scene set in the house. |
| Lights | `light.bedroom_bedroom`, `switch.bedroomlight_switch_1` | P6 | AVAILABLE NOW. ⚠ `switch.bedroomlight_switch_1` reports live in the **`light`** domain — see the inventory. |
| Roller shade | `cover.aqara_roller_shade_driver_e1`, `sensor.aqara_roller_shade_driver_e1_battery` (70 %) | `tile` + `cover-open-close` | AVAILABLE NOW |
| LetPot grow unit | `switch.lph_se_dcd9_power`, `switch.lph_se_dcd9_pump_cycling`, `binary_sensor.lph_se_dcd9_pump`, `select.lph_se_dcd9_light_{mode,brightness}`, `number.lph_se_dcd9_plants_age` | tiles | AVAILABLE NOW — already built. Not in the mockup; keep. |
| Entertainment | — | — | NEEDS HARDWARE/DATA |
| Climate dial | — | — | NEEDS HARDWARE/DATA |
| Clock / alarm / sleep timer | `now()` | **P1** | Clock AVAILABLE NOW; alarm and sleep timer **NEEDS HELPER**. |
| Room Status ring — "Calm" | interpreted | `gauge` / P4 | DESIGN ADAPTATION REQUIRED — buildable from motion + lights once a motion sensor exists. |

### Bathroom

**No view exists, and none should be created yet.**

The live instance has **no Bathroom area and no Bathroom-assigned entity of any
domain** — no light, no fan, no humidity sensor, no motion sensor, no outlet.
Every component on the mockup (Vanity/Mirror/Shower/Ceiling lights, three
outlets, ventilation arc, thermostat, shower timer, humidity status) is
**NEEDS HARDWARE/DATA**.

Building a Bathroom page now would mean inventing every entity on it. The page
waits for hardware.

### Garage

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Status chips — temp, door, camera, freezer | `binary_sensor.g_monitor_freezer_p110m_overloaded`, `switch.g_monitor_freezer_p110m` | P3 | PARTIAL — **no Garage temperature sensor, no garage door, no garage camera.** |
| Quick Actions — Open Door / All Off / Utility / Night | — | — | **NEEDS HARDWARE/DATA** — no `cover` in the Garage area. ⚠ *A door-opening control is also inside the approval boundary and must not be created without explicit owner approval.* |
| Lights / outlets | `switch.g_monitor_freezer_p110m` | P6 | PARTIAL — one monitored outlet only. |
| Garage door & security | — | — | **NEEDS HARDWARE/DATA** + owner approval |
| Camera | — | — | NEEDS HARDWARE/DATA — the four Tapo cameras are filed under **Network**, none in Garage |
| Freezer monitoring | `sensor.g_monitor_freezer_p110m_{current,current_consumption,today_s_consumption,voltage}` | P4 + `tile` | **AVAILABLE NOW** — power, current, voltage, daily kWh all live. **Freezer *temperature* is NEEDS HARDWARE/DATA** — the only freezer temperature sensor (Kogan Freezer, Backyard) reads `unavailable`. |
| Clock / timers | `now()` | **P1** | AVAILABLE NOW |

### Energy

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Solar generation | `sensor.primo_5_0_1_1_ac_power`, `_energy_day`, `_energy_year`, `_total_energy` | P12 | AVAILABLE NOW — ⚠ **all four read `unavailable` right now.** Every card must keep its explicit offline branch. |
| House consumption | `sensor.powerpal_gateway_powerpal_power`, `_daily_energy`, `_total_energy` | P12 | AVAILABLE NOW (NOT EXPOSED to the connector; already on the dashboard) |
| Solar forecast — today / tomorrow / next hour / peak | Solar production forecast sensors, live | P4 | **NEEDS ID EXPORT** — high value: the forecast works **while the inverter is offline**. |
| Grid import / export | — | — | **NEEDS HARDWARE/DATA** |
| Battery state | — | — | **NEEDS HARDWARE/DATA** |
| Cost estimate / billing-period projection | `sensor.electricity_bill_estimate`, `sensor.electricity_billing_cycle` | P4 | AVAILABLE NOW (already built) |
| Self-consumption / solar contribution donut | derived | proportion bar | **NEEDS TEMPLATE SENSOR** + DESIGN ADAPTATION REQUIRED |
| "Solar is supplying 78 % of demand" | interpretation | P4 secondary | NEEDS TEMPLATE SENSOR — needs both solar and whole-house in one template |
| CO₂ intensity / grid fossil % | Electricity Maps sensors, live | P4 | **NEEDS ID EXPORT** |
| Unusual usage alert | derived | P7 | NEEDS TEMPLATE SENSOR |

⚠ **`CFG-001` is open against this board** — the Energy → Totals grid cost reads
roughly 31.8× too high. That fault is in Home Assistant's own Energy
configuration, not in this dashboard, and is not fixable from this repository.

### Billing

The Bills board is the most complete on the dashboard: a `bills` view plus six
per-bill subviews, all driven by 52 `input_*` helpers.

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Total Due This Month | `sensor.bills_outstanding_total` | P4 | AVAILABLE NOW |
| Next Due Date | `input_datetime.{elec,gas,water,council_rate,car_insurance,rego}_*_due` | P4 | AVAILABLE NOW |
| Paid This Month | `input_boolean.*_paid` ×6 | P4 | AVAILABLE NOW |
| Bills needing attention | `sensor.bills_unpaid_count` | P3 chip | AVAILABLE NOW (already on Home) |
| All-bills table | the six per-bill helper sets | subviews | **DESIGN ADAPTATION REQUIRED** — Lovelace has no table card. The six subviews are the HA-native form and already work. |
| Monthly spending trend | `billing/history.json` | — | **BLOCKED** — `BILL-002`: storage scaffolded, but no HA-side mechanism exposes the file to Lovelace yet. |
| Savings tracker | — | — | **NEEDS HELPER** |
| Monthly spending breakdown donut | six `input_number.*_amount` | proportion bars | DESIGN ADAPTATION REQUIRED |
| Upcoming bills timeline | six `input_datetime.*_due` | P8 rows | AVAILABLE NOW |
| Internet bill | — | — | **NEEDS HELPER** — the mockup shows an Internet bill; no internet helper set exists. |
| Payment actions | — | — | Out of scope: external account actions are inside the approval boundary. |

### Security

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Overall secure state | the three door contacts + four motion sensors | P4 | AVAILABLE NOW — must keep the third branch for offline sensors |
| External doors | `binary_sensor.{m,f,b}_contact_sensor_door` | `tile` | AVAILABLE NOW |
| Motion status | `binary_sensor.{k_motion_sensor,sensor_group,living_room_living_hue_hue_sensor,bedroom}_motion*` | `tile` | AVAILABLE NOW |
| Camera health | 6 `camera.*` + 4 battery sensors | P8 | AVAILABLE NOW |
| Alarm state | — | — | **NEEDS INTEGRATION** — no `alarm_control_panel` exists |
| Door locks | — | — | **NEEDS HARDWARE/DATA** + inside the approval boundary |
| Emergency buttons | `binary_sensor.emergency_button_{dad,mum}_cloud_connection` | `tile` | AVAILABLE NOW |

### Cameras

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Live preview grid | 6 `camera.*` | P11 | AVAILABLE NOW |
| Online / offline state | camera states | P3 | AVAILABLE NOW — **East Wall and South Wall are `unavailable` now** |
| Tap for larger view | 6 subviews | P9 | AVAILABLE NOW |
| Camera battery health | `sensor.tapo_c42{0,5}_*_battery`, `sensor.tapo_camera_bcca_battery` | P8 | AVAILABLE NOW — North Wall at **25 %**, Backyard `unavailable` |
| Motion / person detection toggles | Tapo `select`/`switch` entities, live | `tile` | **NEEDS ID EXPORT** |
| Privacy mode | `switch.smart_pet_feeder_privacy_mode` + Tapo privacy switches | `tile` | PARTIAL — pet feeder AVAILABLE NOW; Tapo privacy switches NEEDS ID EXPORT. ⚠ *Disabling a camera is inside the approval boundary.* |
| Recent motion thumbnails | — | — | **NEEDS INTEGRATION** — no event-clip storage |
| Storage health / retention | — | — | NEEDS INTEGRATION |
| Recording status | — | — | NEEDS INTEGRATION |

### Climate

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Thermostat dial | `climate.bedroom_parents_room_ac` | **native `thermostat`** | AVAILABLE NOW |
| Room temperatures | Parents Room / Living Room / Dining sensors | P8 | AVAILABLE NOW for three rooms; Kitchen, Ray Bedroom, Garage, Guest Room have none |
| Humidity | `sensor.bedroom_motion_sensor_humidity` | P8 | AVAILABLE NOW — Parents Room only |
| Climate React / timer | `switch.bedroom_parents_room_ac_{climate_react,timer}`, `sensor.bedroom_parents_room_ac_timer_end_time` | `tile` | AVAILABLE NOW |
| Filter status | `binary_sensor.bedroom_parents_room_ac_filter_clean_required`, `button.bedroom_parents_room_ac_reset_filter` | `tile` | AVAILABLE NOW |
| Air purifier / ventilation | Living Room `fan` + PM sensors, live | `tile` | **NEEDS ID EXPORT** |
| Whole-home climate schedule | — | — | NEEDS HELPER |

### Entertainment / Media Hub

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Now playing | `media_player.living_room_tv_samsung_q9_series_65` (on) | `media-control` | AVAILABLE NOW |
| Device list | `media_player.55_qled_4k_ai`, `media_player.pogo` (**unavailable**) | `tile` | AVAILABLE NOW |
| Transport / volume / source | the same media players | `media-control` | AVAILABLE NOW |
| Room output selection | — | — | NEEDS HARDWARE/DATA — no multi-room audio |
| Continue watching / posters | — | — | **NEEDS INTEGRATION** — no media library integration |
| Movie / Relax / Good Night scene links | Hue scenes | P6 | **NEEDS ID EXPORT** |
| Asian drama emphasis | — | — | NEEDS INTEGRATION |

### Automations

**No view exists. It cannot be built from here.**

The connector returns **zero `automation.*` and zero `script.*` entities**.
Every component on the mockup — the rule rows with enable toggles, the
activity histogram, the "Most Active" list, the scene shortcuts — needs those
entity IDs.

**NEEDS ID EXPORT** for the whole board. Once the export exists, rule rows and
enable toggles are AVAILABLE NOW (native `tile` on an `automation` entity does
exactly what the mockup row does); the activity histogram is **NEEDS TEMPLATE
SENSOR**.

### People Mapping

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| At Home / Away counts | `zone.home` (=2), three `person.*` | P4 | AVAILABLE NOW |
| Person cards | `person.raymond_du` (home), `person.vinh_du` (home), `person.ai_q_huang` (not_home) | `tile` | AVAILABLE NOW — **three people, not four** |
| Live map | `person.*` | native `map` | AVAILABLE NOW — the native `map` card is the HA-native form of the mockup's map |
| Distance / ETA | `distance(zone.home, person.*)`, `sensor.*_distance` | P4 | AVAILABLE NOW — already built on `people-locations-distance` |
| Device battery per person | `Ai's iPhone Battery Level` (85), `Vinh's phone Battery level` (88), `Raymond's iPad Battery Level` (50) | P8 | **NEEDS ID EXPORT** |
| Zone list | only `zone.home` confirmed | P8 | PARTIAL — Work / School / Shops / Gym: **NEEDS HELPER** (zones are HA config) |
| Presence history chart | `zone.home` | `history-graph` | AVAILABLE NOW |
| Family Location selector | `input_select` "Family Location", live, **unused** | `tile` | **NEEDS ID EXPORT** — an existing helper with no surface |
| Recent movement timeline | `device_tracker.*` | `logbook` | NEEDS ID EXPORT |

### Lighting Studio

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Zone / scene list — All Off, Relax, Bright, Movie Time, Dinner, Party, Good Night | 29 Hue scenes live | P6 | **NEEDS ID EXPORT** — the single biggest unblock in the pack |
| Per-group brightness sliders | `light.living_room`, `light.dining`, `light.bedroom_bedroom` | `tile` + `light-brightness` | AVAILABLE NOW — already built |
| All Off | the three group lights + `switch.mainroomlight_switch_1` | P6 | AVAILABLE NOW |
| Scene preview render | — | — | NEEDS HARDWARE/DATA (imagery) |
| Lighting modes | existing `lighting-modes` subview | — | AVAILABLE NOW |

### Network & Devices

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Internet online state | `binary_sensor.eero_wan_status` (on) | P3 | AVAILABLE NOW |
| Remote UI status | `binary_sensor.remote_ui` | P8 | AVAILABLE NOW (NOT EXPOSED to the connector) |
| Download / upload / uptime | — | — | **NEEDS INTEGRATION** — eero exposes WAN up/down only |
| Network map tree | — | — | DESIGN ADAPTATION REQUIRED — no tree card |
| Device health ring | Cloud-connection binary sensors across TP-Link devices | `gauge` | **NEEDS TEMPLATE SENSOR** to count them; the inputs exist |
| Top clients | `device_tracker.*`, `sensor.*_ssid` | P8 | NEEDS ID EXPORT |
| Hub health | TP-LinkHub H100 cloud connection / overheated / signal, live | `tile` | **NEEDS ID EXPORT** |

### House Health

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Overall health state | derived | P4 | NEEDS TEMPLATE SENSOR |
| Home Assistant status | `update.home_assistant_core_update` | `tile` | AVAILABLE NOW (already built) |
| Backups | `sensor.backup_{last_successful,next_scheduled}_automatic_backup` | P8 | AVAILABLE NOW (already built) |
| Wi-Fi / internet | `binary_sensor.eero_wan_status`, `binary_sensor.remote_ui` | `tile` | AVAILABLE NOW |
| Solar inverter status | `sensor.primo_5_0_1_1_ac_power` | P8 | **AVAILABLE NOW — and it would currently read *offline*, correctly.** A House Health card is the right place to surface that. |
| Device batteries | `sensor.front_door_battery` (22), `sensor.living_room_ringring_battery` (21), `sensor.tapo_c425_north_wall_battery` (25), `sensor.tapo_c420_{east,south}_wall_battery` (100), `sensor.tapo_camera_bcca_battery` (unavail), `sensor.aqara_roller_shade_driver_e1_battery` (70) | P8 | **AVAILABLE NOW — three are genuinely under 30 %.** This is `UI-032`, and the live data now answers it. |
| Offline devices | camera + light + media states | P4 | **NEEDS TEMPLATE SENSOR** to count; inputs exist |
| Zigbee / Thread status | — | — | NEEDS INTEGRATION |
| Device uptime bars | — | — | NEEDS TEMPLATE SENSOR |
| Run diagnostics action | — | — | Out of scope: supervisor operations are protected |

### Water & Gas

**No view exists.** The board is almost entirely unbacked.

| Mockup component | Entity | Status |
|---|---|---|
| Water today / this month, trend, leak state | — | **NEEDS HARDWARE/DATA** — no water sensor of any kind |
| Gas today / this month, trend | — | **NEEDS HARDWARE/DATA** — no gas meter |
| Gas billed usage | `input_number.gas_bill_mj` (manual, per bill) | AVAILABLE NOW — ⚠ see the inventory's *Gas Bill Usage MJ* name discrepancy |
| Water billed usage | `input_number.water_bill_usage_kl` (manual, per bill) | AVAILABLE NOW |
| Cost projection | `input_number.*_amount` + `input_datetime.*` | AVAILABLE NOW |

**Adaptation:** what can honestly be built is a *billed-usage* board over the
manual helpers — quarterly kL and MJ with period comparison — not the
mockup's live daily histograms. Say so on the card.

### Notifications & Alerts

| Mockup component | Entity | Card | Status |
|---|---|---|---|
| Alert feed with severity | the 17 P7 conditions on Home | P7 | **AVAILABLE NOW** — the components exist and already work; what is missing is the *board* that gathers them and the severity taxonomy. This is the cheapest whole new board in the pack. |
| Filter by severity | — | `conditional` on a helper | **NEEDS HELPER** (`input_select`) |
| Mark as read | — | — | NEEDS HELPER |
| Alert history | — | `logbook` | AVAILABLE NOW (native logbook) |
| Quiet hours | — | — | NEEDS HELPER (`input_datetime` ×2) |
| Per-category settings | — | — | NEEDS HELPER |

---

## Part 3 — Blocker register

| ID | Blocker | Impact | Owner action |
|---|---|---|---|
| **B1** | **Entity IDs cannot be read from this environment.** The HA connector returns friendly names only, and only for Assist-exposed entities. | **The single largest constraint in the programme.** It blocks all 29 Hue scenes (every room's Quick Actions, the whole Lighting Studio), all automations and scripts (the entire Automations board), air-quality sensors, solar forecast, per-person device batteries, the Shopping List, the Family Location helper, hub health, and Tapo camera controls. | **Developer Tools → States → download/copy the entity list**, or Settings → Devices & Services → Entities → export. Paste it into the repo (no secrets are involved — entity IDs are not credentials). One export unblocks ~10 mapping rows. |
| **B2** | **`CFG-003` — the deployment bridge does not deliver.** The host's local clone is orphaned from `ha-deploy`, so the deploy script compares stale content, finds no change and never reaches its apply step. Confirmed 2026-08-30: the live raw config does not contain `sensor.front_door_battery`. | **Nothing pushed since `26c3b14` has reached the live dashboard.** Every CasaRay batch will validate, commit and push correctly and remain invisible. | The recovery procedure is written out in `DASHBOARD_ISSUES.md` → *Owner recovery, on the host*. It is the owner's to run — the deployment bridge is protected. |
| **B3** | **No HA schema validation is possible here.** No `/config`, no supervisor, no API route. Valid YAML is not valid Lovelace. | Card types, option names and nesting are unchecked. A batch can pass every repository check and still not render. | Browser check after each deploy — which needs B2 first. |
| **B4** | `auto-entities` is not installed. | Dynamic generation (the mockups' filtered lists, "View all" expansions) must be hand-written. | Install via HACS if dynamic lists become worth the dependency. Not required for Batches 1–2. |
| **B5** | **No room photography.** Every room mockup opens with a hero image band. | Room pages will look flatter than the mockups until images exist. | Drop images into `/config/www/` and name them here. |
| **B6** | `BILL-002` — no HA-side mechanism exposes `billing/history.json` to Lovelace. | Blocks the spending-trend chart and bill history. | Decide the mechanism (see `billing/README.md`). |

### Deliberate temporary artefact

**`UI-032 PROBE v1` is on the production Home page on purpose.** It is a purple
bug-icon card, unconditional, at the top of the "Active Now" section, reading
"N of 6 read under 30 · remove after diagnosis". It is the test instrument for
B2: once delivery works, its appearance proves the whole chain end to end in
one look.

**Do not remove it while B2 is open.** Removing it destroys the only
instrument that can confirm the bridge without touching the bridge.

For the record, the live answer it is waiting to display is **3 of 6**.

---

## Part 4 — Batch plan

Following the briefing's §24 order, filtered by what is actually buildable.

| Batch | Scope | Depends on | State |
|---|---|---|---|
| **1** | **Global CasaRay shell** — the P1 clock/date component, first instance in the Home header; header pattern established. | — | **DONE** — `5ad2bce`, 2026-09-01. Validated 7/7. Queued live as `CR-001`/`CR-002`. |
| **2** | **Home only** — group the 17 loose alert cards under an Attention heading; KPI strip using P4; honest Security roll-up with **no alarm row** (no `alarm_control_panel` exists). | Batch 1 | **NEXT — ready, needs nothing from the owner** |
| 3 | Room template system — apply P2/P3/P5/P6 + the P1 clock uniformly across the seven room views. | Batch 2 | Queued |
| 4 | Parents Room — native `thermostat` replacing the templated climate block. | Batch 3 | Queued |
| 5 | House Health — battery board (3 low), inverter-offline surface, backup status. | Batch 3 | Queued — highest-value new content that needs **no** export |
| 6 | Notifications & Alerts — a real board over the existing P7 conditions. | Batch 5 | Queued |
| — | Lighting Studio scenes · Automations board · air quality · solar forecast · Water & Gas | **B1 export** | **Blocked** |
| — | Bathroom · Garage door · alarm · locks · grid/battery · water/gas metering | Hardware | **Blocked** |

**Batches 1–6 need nothing from the owner.** Everything after them needs B1,
B2, or hardware.
