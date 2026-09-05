# Entity inventory — Deez Smart Home

Reconciliation of the Home Assistant objects this repository's dashboards
reference against what the live instance actually reports.

> **Read this first — B1 changed what this file can prove.**
>
> The tables below were originally built against the **legacy** dashboard,
> `dashboards/deez_smart_home.yaml`, using the read-only connector, which
> returns friendly names only and only for Assist-exposed entities. That is
> why `NOT EXPOSED` exists as a status.
>
> **That limitation is gone.** `docs/live/states_export_2026-09-05.txt` is a
> full Developer Tools export — 970 entities, every entity ID, friendly name,
> area and availability. It is now the authority on whether an entity exists,
> and a `NOT EXPOSED` row below means only "not re-checked yet", **never**
> "missing". Check the export before treating anything here as a blocker.
>
> The canonical dashboard is now `dashboards/casaray_v2.yaml`. Reconciled
> against B1 on 2026-09-05, and again after the upgrade batches of the same
> day: **297 entity references, 0 absent from the export**, plus two
> **service names** — `scene.turn_on` and `script.turn_on` — which the export
> will never carry because they are not entities.
>
> Of the 297: 249 read `ok`, 30 `unknown`, 18 `unavailable`. Every one of the
> 18 is a known-offline device the cards are written to report honestly —
> the three contact sensors, the four Living Room Hue spots, the East and
> South Wall camera streams, the LetPot grow unit (`lph_se_dcd9_*`), the
> Kogan TV, Pogo and the 55" QLED. **Seeing them unavailable is the guard
> working, not a defect.** See `LIVE_VERIFICATION_QUEUE.md` → *expected
> offline, do not chase*.
>
> Reproduce the reconciliation at any time:
>
> ```sh
> python3 scripts/reconcile_entities.py
> ```

**Generated:** 2026-09-01, against `ha-deploy` at `b6e76f5`.
**B1 reconciliation:** 2026-09-05 from the owner-supplied Home Assistant Developer Tools entity export.
**Method:** repository references plus live/owner-export evidence. The B1 export supplies exact entity IDs, friendly names, states and areas for the exported domains.

| Source | What it proves | What it cannot prove |
|---|---|---|
| `dashboards/deez_smart_home.yaml` | The canonical **entity ID** a card uses. These IDs were originally read out of the live dashboard, so they are real IDs, not invented ones. | That the entity still exists, or what state it is in. |
| Home Assistant connector (`GetLiveContext`) | That an object **exists right now**, its domain, its area and its current state. | The entity **ID**. The connector returns friendly names only. And it returns **only entities exposed to Assist** — absence is not evidence of non-existence. |

Both limits applied **before B1**, and are the reason this file has a
`NOT EXPOSED` column value rather than a `MISSING` one. They no longer bind:
the third source below supersedes them.

| `docs/live/states_export_2026-09-05.txt` | That an entity **exists**, its exact **ID**, friendly name, area and availability — for **every** entity, not just Assist-exposed ones. | Attribute values and history. It deliberately carries no state values, so no addresses or coordinates. |

25 rows below still read `NOT EXPOSED`. That is a **stale label, not a
finding** — it predates the export. Resolve any one of them by grepping the
export rather than by re-querying the connector.

> **Rule this file exists to serve:** never introduce an `entity_id` that is
> not already in the dashboard or confirmed against the live instance. A
> mockup showing a metric is not evidence that a sensor for it exists.

---

## Status vocabulary

| Value | Meaning |
|---|---|
| `LIVE` | A live object of the same domain, with a matching name, exists and is reporting. |
| `LIVE (unavail)` | Matched, but the live object currently reads `unavailable`. The card is correct; the device is not reporting. |
| `NOT EXPOSED` | Not returned by the connector. Not exposed to Assist, so existence is neither confirmed nor denied from here. |
| `NAME DRIFT` | Matched, but the live friendly name no longer resembles the entity ID. Working, but confusing to a future reader. |
| `⚠ CHECK` | A discrepancy worth an owner check before anything is built on it. |

---

## Live areas

The instance reports these areas. **There is no Bathroom area**, and no
Bathroom-assigned entity of any domain.

| Area | Notes |
|---|---|
| Living Room | Lights, Hue spots, motion/illuminance/temp, front door contact + doorbell, TV, air purifier, power board |
| Ray Bedroom | Bedroom light, NightLight, roller shade, LetPot grow unit, energy monitor, wall switch |
| Parents Room | AC (Sensibo), motion/temp/humidity, contact sensor, emergency buttons, TV, power board, main light switch |
| Dining | Dining light, motion group, illuminance, pet feeder + camera |
| Kitchen | Three P100 plugs, motion sensor, LG fridge, smart button |
| Garage | Freezer energy monitor (P110M) |
| Guest Room | Printer plug, Kogan TV, Pogo media player |
| Backyard | Contact sensor, freezer plug (unavailable), Tapo camera (unavailable) |
| Network | Cameras (Tapo C200/C420 ×2/C425), eero gateway, TP-Link hub, Ring chime |
| Energy | Fronius Primo inverter, SolarNet, solar forecast, Electricity Maps |

**Area modelling note.** All four wall cameras are filed under **Network**, not
under the outdoor areas they watch. That is why an area-driven camera card
cannot be built yet — see the mapping pack's Cameras row.

---

## A. Entities the dashboard references

### light (9 real + 2 service names)

| Entity ID | Live name | Area | State | Status |
|---|---|---|---|---|
| `light.bedroom_bedroom` | Bedroom | Ray Bedroom | on (151) | LIVE |
| `light.dining` | Dining | Dining | on (227) | LIVE |
| `light.kogan_tv` | Kogan Tv | Guest Room | unavailable | LIVE (unavail) |
| `light.living_room` | Living room | Living Room | on (227) | LIVE |
| `light.living_room_hue_ambiance_spot_1` | Hue ambiance spot 1 | Living Room | unavailable | LIVE (unavail) |
| `light.living_room_hue_ambiance_spot_2` | *(not observed by name)* | Living Room | — | ⚠ CHECK |
| `light.living_room_hue_ambiance_spot_3` | Hue ambiance spot 3 | Living Room | unavailable | LIVE (unavail) |
| `light.living_room_hue_ambiance_spot_4` | Hue ambiance spot 4 | Living Room | unavailable | LIVE (unavail) |
| `light.smart_pet_feeder_indicator_light` | Smart Pet Feeder Indicator light | Dining | on | LIVE |

`light.turn_on` / `light.turn_off` in the YAML are **service names**, not
entities. Same for `input_boolean.turn_on` / `turn_off`.

The Living Room Hue group is messy live: four `Hue ambiance spot N` entities
plus four `Living Room Inner/Outter Left/Right` entities, **all eight
unavailable**. Spot 2 was not observed under that name. The Hue bridge appears
to be offline or the group renamed; the four dashboard cards are not wrong,
they are pointing at a bridge that is not answering.

### switch (24)

| Entity ID | Live name | Area | State | Status |
|---|---|---|---|---|
| `switch.bedroom_parents_room_ac_climate_react` | Parents Room AC Climate React | Parents Room | off | LIVE |
| `switch.bedroom_parents_room_ac_timer` | Parents Room AC Timer | Parents Room | off | LIVE |
| `switch.bedroomlight_switch_1` | BedRoomLight Switch 1 | Ray Bedroom | off | ⚠ CHECK — live object is in the **`light`** domain |
| `switch.dinning_light_switch_1` | Dinning light Switch 1 | Dining | on | LIVE |
| `switch.g_monitor_freezer_p110m` | G/Monitor Freezer P110M | Garage | on | LIVE |
| `switch.g_printer_p100` | G/Printer P100 | Guest Room | off | LIVE |
| `switch.g_printer_p100_auto_off_enabled` | — | — | — | NOT EXPOSED |
| `switch.g_printer_p100_auto_update_enabled` | — | — | — | NOT EXPOSED |
| `switch.g_printer_p100_led` | — | — | — | NOT EXPOSED |
| `switch.genio_power_board_with_usb_livingroom_socket_1` … `_5` | Genio Power Board with USB-LivingRoom Socket 1–5 | Living Room | all on | LIVE |
| `switch.k_bot_p100` | K/Bot P100 | Kitchen | on | LIVE |
| `switch.k_coffee_p100` | K/Coffee P100 | Kitchen | on | LIVE |
| `switch.k_top_p100` | K/Top P100 | Kitchen | on | LIVE |
| `switch.lg_fridge_express_mode` | LG-Fridge Express mode | Kitchen | off | LIVE |
| `switch.lph_se_dcd9_power` | LPH-SE DCD9 Power | Ray Bedroom | on | LIVE |
| `switch.lph_se_dcd9_pump_cycling` | LPH-SE DCD9 Pump cycling | Ray Bedroom | on | LIVE |
| `switch.mainroomlight_switch_1` | MainRoomLight Switch 1 | Parents Room | off | LIVE |
| `switch.r_energy_monitor_p110m` | R/Energy Monitor P110M | Ray Bedroom | on | LIVE |
| `switch.smart_pet_feeder_motion_alarm` | — | — | — | NOT EXPOSED |
| `switch.smart_pet_feeder_privacy_mode` | — | — | — | NOT EXPOSED |

**`switch.bedroomlight_switch_1` is the one genuine discrepancy in this
inventory.** The live instance reports `BedRoomLight Switch 1` in the **light**
domain, in Ray Bedroom. The two sibling switches on the same dashboard —
`switch.mainroomlight_switch_1` and `switch.dinning_light_switch_1` — are both
still `switch`. The most likely explanation is a *Change device type of a
switch* helper applied to this one only, which leaves the original
`switch.*` entity in place but hidden. If so the dashboard card still works.
Owner check listed in the mapping pack.

### binary_sensor (16)

| Entity ID | Live name | Area | State | Status |
|---|---|---|---|---|
| `binary_sensor.b_contact_sensor_door` | B/Contact Sensor Door | Backyard | off | LIVE |
| `binary_sensor.bedroom_motion_sensor_motion` | Parents Room Motion Sensor Motion | Parents Room | off | NAME DRIFT |
| `binary_sensor.bedroom_parents_room_ac_filter_clean_required` | Parents Room AC Filter clean required | Parents Room | off | LIVE |
| `binary_sensor.bedroom_parents_room_ac_room_occupied` | Parents Room AC Room occupied | Parents Room | off | LIVE |
| `binary_sensor.eero_wan_status` | eero Gateway WAN status | Network | on | LIVE |
| `binary_sensor.emergency_button_dad_cloud_connection` | Emergency Button Dad Cloud connection | Parents Room | on | LIVE |
| `binary_sensor.emergency_button_mum_cloud_connection` | Emergency Button Mum Cloud connection | Parents Room | on | LIVE |
| `binary_sensor.f_contact_sensor_door` | F/Contact Sensor Door | Living Room | off | LIVE |
| `binary_sensor.g_monitor_freezer_p110m_overloaded` | G/Monitor Freezer P110M Overloaded | Garage | off | LIVE |
| `binary_sensor.k_motion_sensor_motion` | K/Motion Sensor Motion | Kitchen | off | LIVE |
| `binary_sensor.lg_fridge_door` | LG-Fridge Door | Kitchen | off | LIVE |
| `binary_sensor.living_room_living_hue_hue_sensor_motion` | Living Hue Hue Sensor Motion | Living Room | on | LIVE |
| `binary_sensor.lph_se_dcd9_pump` | LPH-SE DCD9 Pump | Ray Bedroom | off | LIVE |
| `binary_sensor.m_contact_sensor_door` | M/Contact Sensor Door | Parents Room | off | LIVE |
| `binary_sensor.remote_ui` | — | — | — | NOT EXPOSED |
| `binary_sensor.sensor_group_motion` | Sensor group Motion | Dining | on | LIVE |

**Name drift, recorded so nobody "fixes" it:** the device behind
`bedroom_motion_sensor_*` was renamed **Parents Room Motion Sensor**. The
entity IDs kept the old slug. Every `bedroom_motion_sensor_*` reference on the
dashboard is a **Parents Room** reading, and the dashboard already uses them
that way. Do not repoint them at Ray Bedroom.

### sensor (40)

| Entity ID | Live value | Status |
|---|---|---|
| `sensor.aqara_roller_shade_driver_e1_battery` | 70 % | LIVE |
| `sensor.backup_last_successful_automatic_backup` | — | NOT EXPOSED |
| `sensor.backup_next_scheduled_automatic_backup` | — | NOT EXPOSED |
| `sensor.bedroom_motion_sensor_humidity` | 65.0 % | NAME DRIFT (Parents Room Motion Sensor Humidity) |
| `sensor.bedroom_motion_sensor_temperature` | 23.2 °C | NAME DRIFT (Parents Room Motion Sensor Temperature) |
| `sensor.bedroom_parents_room_ac_filter_last_reset` | — | NOT EXPOSED |
| `sensor.bedroom_parents_room_ac_timer_end_time` | 2025-03-10T14:21 | LIVE |
| `sensor.bills_outstanding_total` | — | NOT EXPOSED |
| `sensor.bills_unpaid_count` | — | NOT EXPOSED |
| `sensor.electricity_bill_estimate` | — | NOT EXPOSED |
| `sensor.electricity_bill_status` | — | NOT EXPOSED |
| `sensor.electricity_billing_cycle` | — | NOT EXPOSED |
| `sensor.emergency_button_dad_signal_level` | — | NOT EXPOSED |
| `sensor.emergency_button_mum_signal_level` | — | NOT EXPOSED |
| `sensor.front_door_battery` | **22 %** | LIVE — **low** |
| `sensor.g_monitor_freezer_p110m_current` | 0.03 A | LIVE |
| `sensor.g_monitor_freezer_p110m_current_consumption` | 2.7 W | LIVE |
| `sensor.g_monitor_freezer_p110m_today_s_consumption` | 0.177 kWh | LIVE |
| `sensor.g_monitor_freezer_p110m_voltage` | 230.1 V | LIVE |
| `sensor.g_printer_p100_auto_off_at` | — | NOT EXPOSED |
| `sensor.gas_bill_estimate` | — | NOT EXPOSED |
| `sensor.gas_bill_status` | — | NOT EXPOSED |
| `sensor.living_room_living_hue_hue_sensor_illuminance` | 35 lx | LIVE |
| `sensor.living_room_living_hue_hue_sensor_temperature` | 18.7 °C | LIVE |
| `sensor.living_room_ringring_battery` | **21 %** | LIVE — **low** |
| `sensor.powerpal_gateway_powerpal_battery` | — | NOT EXPOSED |
| `sensor.powerpal_gateway_powerpal_daily_energy` | — | NOT EXPOSED |
| `sensor.powerpal_gateway_powerpal_power` | — | NOT EXPOSED |
| `sensor.powerpal_gateway_powerpal_total_energy` | — | NOT EXPOSED |
| `sensor.primo_5_0_1_1_ac_power` | **unavailable** | LIVE (unavail) |
| `sensor.primo_5_0_1_1_energy_day` | **unavailable** | LIVE (unavail) |
| `sensor.primo_5_0_1_1_energy_year` | **unavailable** | LIVE (unavail) |
| `sensor.primo_5_0_1_1_total_energy` | **unavailable** | LIVE (unavail) |
| `sensor.r_energy_monitor_p110m_current_consumption` | 38.6 W | LIVE |
| `sensor.r_energy_monitor_p110m_today_s_consumption` | 0.055 kWh | LIVE |
| `sensor.sensor_group_illuminance` | 34 lx | LIVE |
| `sensor.tapo_c420_east_wall_battery` | 100 % | LIVE |
| `sensor.tapo_c420_south_wall_battery` | 100 % | LIVE |
| `sensor.tapo_c425_north_wall_battery` | **25 %** | LIVE — **low** |
| `sensor.tapo_camera_bcca_battery` | **unavailable** | LIVE (unavail) |

**Two findings that matter for design, both live-confirmed:**

1. **The Fronius Primo inverter is offline.** Every `primo_5_0_1_1_*` sensor,
   and every `SolarNet *` sensor, reads `unavailable`. The Home solar chip
   already handles this correctly (`red` icon, "Offline"), which is exactly
   why the no-sentinel rule exists. Any CasaRay Energy work must assume the
   inverter can be absent, not merely low.
2. **Three batteries are genuinely under 30 %:** Front Door `22`,
   RingRing `21`, Tapo C425 North Wall `25`. Tapo C420 East/South read `100`
   and Tapo Camera (Backyard) reads `unavailable`. This is the live answer to
   the `UI-032` question — a low-battery card would legitimately show **3**,
   not 0 and not 6.

### climate · camera · cover · media_player · person · number · select · button · update · weather · zone

| Entity ID | Live name | State | Status |
|---|---|---|---|
| `climate.bedroom_parents_room_ac` | Parents Room AC | off, 23.2 °C ambient | LIVE |
| `camera.front_door_live_view` | Front Door Live view | idle | LIVE |
| `camera.smart_pet_feeder` | Smart Pet Feeder | idle | LIVE |
| `camera.tapo_c200_stockroom_hd_stream_direct` | Tapo C200 - Stockroom HD Stream (Direct) | idle | LIVE |
| `camera.tapo_c420_east_wall_hd_stream_direct` | Tapo C420 East Wall HD Stream (Direct) | **unavailable** | LIVE (unavail) |
| `camera.tapo_c420_south_wall_hd_stream_direct` | Tapo C420 - South Wall HD Stream (Direct) | **unavailable** | LIVE (unavail) |
| `camera.tapo_c425_north_wall_hd_stream_direct` | Tapo C425 - North Wall HD Stream (Direct) | idle | LIVE |
| `cover.aqara_roller_shade_driver_e1` | Aqara Roller Shade Driver E1 | closed, 0 % | LIVE |
| `media_player.55_qled_4k_ai` | 55" QLED 4k AI | off | LIVE |
| `media_player.living_room_tv_samsung_q9_series_65` | [TV] Samsung Q9 Series (65) | on, vol 0.28 | LIVE |
| `media_player.pogo` | Pogo | **unavailable** | LIVE (unavail) |
| `person.ai_q_huang` | Ai Q Huang | not_home | LIVE |
| `person.raymond_du` | Raymond Du. | home | LIVE |
| `person.vinh_du` | Vinh Du | home | LIVE |
| `weather.forecast_home` | Forecast Home | rainy | LIVE |
| `zone.home` | Home | 2 | LIVE |

---

## B. Useful live objects not currently used by the dashboard

These are not reasons to add cards automatically. They are the **real options**
the design can choose from without inventing anything.

| Live object / family | Domain | Area | Current state | Design opportunity |
|---|---|---|---|---|
| Air purifier PM1 / PM2.5 / PM10 + health concern | `sensor` | Living Room | all 5 μg/m³ / good | **Indoor Climate → Air Quality**; House Health |
| Air purifier Odor Sensor | `sensor` | Living Room | 1 | Indoor Climate / air quality |
| Air purifier Fan | `fan` | Living Room | off | Living Room / Climate control |
| Air purifier Fan mode | `select` | Living Room | smart | Purifier detail |
| Air purifier Lamp | `select` | Living Room | high | Purifier detail |
| Living Room / Dining Room Motion Sensor Temperature + Illuminance + Battery | `sensor` | Living Room, Dining | 18.7 °C / 34 lx, 18.5 °C / 137 lx | Per-room temperature on room cards — **currently only Parents Room has one** |
| Bedroom Hue Sensor Temperature / Illuminance / Battery | `sensor` | Dining | 19.5 °C / 138 lx | Dining climate readings |
| Solar production forecast — today / tomorrow / next hour / peak time | `sensor` | Energy | 6.9 kWh, 11.2 kWh | **Energy forecast** — works even while the inverter is offline |
| Electricity Maps CO2 intensity / fossil % | `sensor` | Energy | 551 gCO₂/kWh, 66.78 % | Energy interpretation layer |
| Front Door Ding / Front Door Motion | `event` | Living Room | timestamped | **Recent Activity** feed on Home |
| RingRing main, Living Room / Ray Bedroom Switch Button 1–4, BedlightSwitch | `event` | various | timestamped | Recent Activity, physical-button context |
| Front Door Last activity | `sensor` (timestamp) | Living Room | 2026-09-01T23:08 | Recent Activity |
| Shopping List | `todo` | — | 0 items | Kitchen board |
| Family Location | `input_select` | — | "Raymond Du" | People page — an existing helper, unused |
| Raymond's iPad Battery / Kiosk Brightness / Kiosk Volume / SSID / Storage | `sensor` | — | 50 %, 85, 25, homeAI, 22.59 % | **House Health** and the iPad Command Center |
| Ai's iPhone Battery, Vinh's phone Battery, Deez Raymond's iPhone Distance | `sensor` | — | 85 %, 88 %, 22 m | People & Presence battery/ETA columns |
| Raymond's iPad / Ai's iPhone / Vinh's phone / Deez / CasaRay iPad | `device_tracker` | — | home / not_home | People & Presence |
| Sensibo Sky Plus AC mode / Cooling setpoint | `sensor` | Parents Room | fanOnly / 19.0 °C | Climate board detail |
| Hue scenes — Living room ×8, Dining ×6, Bedroom ×14 | `scene` | per room | — | **Lighting Studio + room Quick Actions.** IDs unknown — see below |
| Tapo camera detection selects/numbers (motion, person, pet, vehicle, night vision, spotlight) | `select`, `number` | Network | mixed | Cameras board advanced controls |
| TP-LinkHub H100 Cloud connection / Overheated / Signal | `binary_sensor`, `sensor` | Network | on / off / 3 | House Health |
| Presence Multi-Sensor FP300 (occupancy, temp, humidity, lux, battery) | mixed | Ray Bedroom | **all unavailable** | Ray Bedroom sensors — device is down |
| Kogan Freezer temperature, B/Freezer plug | `sensor`, `switch` | Backyard | **unavailable** | Garage/utility freezer monitoring — device is down |

### B1 scene catalogue — RESOLVED 2026-09-05

The owner supplied a Developer Tools entity export containing the exact IDs for
all **29 Hue scenes**, so the previous B1 scene blocker is closed. The catalogue
is now safe to use in CasaRay Quick Actions and Lighting Studio.

- **Living Room (8):** `scene.living_room_living_room_relax`,
  `scene.living_room_living_room_bright`, `scene.living_room_living_room_read`,
  `scene.living_room_living_room_nightlight`,
  `scene.living_room_living_room_energize`,
  `scene.living_room_living_room_concentrate`,
  `scene.living_room_living_room_dimmed`,
  `scene.living_room_living_room_midwinter`.
- **Dining (6):** `scene.dining_dining_relax`, `scene.dining_dining_read`,
  `scene.dining_dining_nightlight`, `scene.dining_dining_energize`,
  `scene.dining_dining_concentrate`, `scene.dining_dining_midwinter`.
- **Ray Bedroom (15):** `scene.bedroom_bedroom_read`,
  `scene.bedroom_bedroom_nightlight`, `scene.bedroom_bedroom_nighttime`,
  `scene.bedroom_bedroom_concentrate`, `scene.bedroom_bedroom_silverstone`,
  `scene.bedroom_bedroom_soho`, `scene.bedroom_bedroom_suzuka`,
  `scene.bedroom_bedroom_baby_s_breath`, `scene.bedroom_bedroom_starlight`,
  `scene.bedroom_bedroom_amber_bloom`, `scene.bedroom_bedroom_vapor_wave`,
  `scene.bedroom_bedroom_blossom`, `scene.bedroom_bedroom_dreamy_dusk`,
  `scene.bedroom_bedroom_pensive`, `scene.bedroom_bedroom_nature_s_colors`.

### Other B1-unblocked entities

**Automations (3 exact IDs):**
- `automation.deploy_deez_dashboard_updates`
- `automation.gas_meter_pulse_counter`
- `automation.bills_reset_ytd_totals`

No `automation.*` entity matching Door → Dining Lights, Work Prep, Good Morning,
Away Mode or Good Night appears in the B1 export. Those names remain design
examples, not runtime facts.

**Living Room air quality:**
- `fan.living_room_air_purifier`
- `sensor.living_room_air_purifier_air_quality`
- `sensor.living_room_air_purifier_pm1`
- `sensor.living_room_air_purifier_pm2_5`
- `sensor.living_room_air_purifier_pm10`
- `sensor.living_room_air_purifier_odor_sensor`
- corresponding PM1/PM2.5/PM10 health-concern sensors are also present.

**Solar forecast:**
- `sensor.energy_production_today`
- `sensor.energy_production_today_remaining`
- `sensor.energy_production_tomorrow`
- `sensor.power_production_now`
- `sensor.energy_current_hour`
- `sensor.energy_next_hour`
- `sensor.power_highest_peak_time_today`
- `sensor.power_highest_peak_time_tomorrow`

**People/device status:** exact tracker and phone battery IDs are now confirmed,
including `device_tracker.raymonds_iphone`, `device_tracker.ais_iphone`,
`device_tracker.vine_s_phone`, `sensor.raymonds_iphone_battery_level`,
`sensor.ais_iphone_battery_level` and `sensor.vine_s_phone_battery_level`.

### What is missing entirely

No live object of any kind exists for these, in any area:

- **Bathroom** — no area, no entity. The mockup's Bathroom page has no data
  behind it at all.
- **Alarm panel** — no `alarm_control_panel` entity. "Armed (Away)" on the
  mockup's Home Security card has no source.
- **Locks** — no `lock` entity. "Front Door unlocked", "Door Lock Locked".
- **Garage door** — no `cover` in Garage. The only cover is the Ray Bedroom
  roller shade. "Open Door" on the Garage mockup has nothing behind it.
- **Water and gas metering** — no water or gas `sensor`. The Water & Gas board
  has no live source; the Bills page's gas figures come from manual helpers.
- **Battery storage** — no battery entity. "Battery Charging • 62 %".
- **Grid import/export** — no such sensor. Powerpal (whole-house power) is not
  exposed, and the inverter is offline.
- **Automations are sparse, not absent.** B1 confirms exactly three `automation.*`
  entities. CasaRay may show those three, but must not fabricate the design
  examples that are not present.
- **Network throughput** — no download/upload/uptime sensor. eero exposes WAN
  up/down only.

---

## Maintenance

Regenerate this file when the live instance changes shape, not on a schedule.
The two commands that produce section A's ID list and the per-view map:

```sh
# every entity ID the dashboard references, by domain
python3 - <<'PY'
import re, collections
txt = open('dashboards/deez_smart_home.yaml').read()
DOM = {'light','switch','sensor','binary_sensor','climate','camera','media_player',
       'person','cover','fan','scene','script','automation','input_boolean',
       'input_number','input_select','input_text','input_datetime','number',
       'select','button','update','weather','zone'}
c = collections.Counter(m.group(0) for m in re.finditer(r'\b([a-z_]+)\.([a-z0-9_]+)\b', txt)
                        if m.group(1) in DOM)
for e in sorted(c): print(c[e], e)
PY
```

Then re-run the connector queries by domain and re-join by friendly name.
