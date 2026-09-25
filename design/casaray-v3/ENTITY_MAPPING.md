# CasaRay V3 — entity mapping

Every entity the V3 prototype draws, where it comes from, and what the house
has no entity for.

## 1. Rules this mapping follows

- **The existence authority is `docs/live/states_export_2026-09-05.txt`**
  (970 entities). `tools/verify_entities.py` scans the prototype source and
  this document, and fails if any ID is missing from the export. Current
  result: **132 IDs, all present.**
- **No new dependencies.** All 132 are already on the V2 dashboard, which has
  rendered live. V3 changes how they are presented. It does not change which
  devices CasaRay depends on.
- **Where the house has no entity, the design says so.** Such a card carries
  a *gap* rather than an ID, and "Show entity IDs" in the demo controls
  renders it in red (§3). No placeholder ID was written anywhere.
- **Demo values are not live values.** The states in `prototype/data.js` are
  plausible demonstration data, shaped on the 14/09 mockups and the 05/09
  export. The export's availability column is a snapshot (see `CLAUDE.md`),
  and §4 lists where 25/09 differs.

## 2. Board → entities

| Board | Entities |
|---|---|
| Top bar | `input_boolean.chinese_dashboard` (the language toggle, as in V2) |
| Home chips | `weather.forecast_home`, `sensor.living_room_living_hue_hue_sensor_temperature`, `person.*` ×3, `sensor.casa_monitored_power` |
| Needs attention | batteries (6 sensors, below), `event.master_bedroom_emergency_button_dad_main`, `event.master_bedroom_emergency_button_mum_main` + `binary_sensor.emergency_button_dad_cloud_connection`, `binary_sensor.emergency_button_mum_cloud_connection`, bill helpers, `binary_sensor.b_contact_sensor_door`, lights + people, `sensor.primo_5_0_1_1_ac_power` |
| Right now | `weather.forecast_home`, `sensor.energy_production_today_remaining` |
| Who's home | `person.raymond_du`, `person.vinh_du`, `person.ai_q_huang`, `binary_sensor.bedroom_parents_room_ac_room_occupied` |
| Energy now | `sensor.casa_monitored_power`, `sensor.powerpal_gateway_powerpal_power`, `sensor.powerpal_gateway_powerpal_daily_energy` |
| Shopping list | `todo.shopping_list` |
| Security | doors `binary_sensor.f_contact_sensor_door`, `binary_sensor.b_contact_sensor_door`, `binary_sensor.m_contact_sensor_door`; cameras (6, below); motion ×4; emergency buttons ×2; sirens `siren.tapo_c425_north_wall_siren`, `siren.tapo_c200_stockroom_siren`, `siren.tapo_h200`; doorbell `sensor.front_door_last_activity` |
| Energy | `sensor.primo_5_0_1_1_ac_power`, `binary_sensor.casa_solar_online`, `sensor.energy_production_today`, `sensor.energy_production_tomorrow`, `sensor.power_highest_peak_time_today`, Powerpal ×2, garage and desk monitors (power, voltage, this month), `sensor.electricity_maps_co2_intensity`, `sensor.electricity_maps_grid_fossil_fuel_percentage`, `input_number.gas_bill_mj` |
| Climate | room temperatures, `climate.bedroom_parents_room_ac`, `fan.living_room_air_purifier`, `sensor.living_room_air_purifier_pm2_5`, `number.lg_fridge_fridge_temperature`, `number.lg_fridge_freezer_temperature` |
| Bills | per bill: `input_boolean.<bill>_paid`, `input_number.<bill>_amount`, `input_datetime.<bill>_due` (exact IDs in §2a); `input_number.bills_paid_ytd`, `input_number.bills_saved_ytd` |
| House health | `update.home_assistant_core_update`, `update.home_assistant_operating_system_update`, `update.home_assistant_supervisor_update`, `sensor.backup_last_successful_automatic_backup`, `binary_sensor.eero_wan_status`, `binary_sensor.matter_zigbee_hub_problem`, `sensor.casa_offline_devices`, batteries |
| People | `person.*` ×3 with `sensor.raymonds_iphone_battery_level`, `sensor.vine_s_phone_battery_level`, `sensor.ais_iphone_battery_level`; `input_boolean.guest_mode`; `sensor.raymonds_ipad_battery_level` |

### 2a. Bill helper names are not uniform

The six bills do not share one naming pattern, and each was checked against the export:

| Bill | Paid | Amount | Due |
|---|---|---|---|
| Electricity | `input_boolean.elec_bill_paid` | `input_number.elec_bill_amount` | `input_datetime.elec_bill_due` |
| Gas | `input_boolean.gas_bill_paid` | `input_number.gas_bill_amount` | `input_datetime.gas_bill_due` |
| Water | `input_boolean.water_bill_paid` | `input_number.water_bill_amount` | `input_datetime.water_bill_due` |
| Council rates | `input_boolean.council_rate_paid` | `input_number.council_rate_amount` | `input_datetime.council_rate_due` |
| Registration | `input_boolean.rego_paid` | `input_number.rego_amount` | `input_datetime.rego_due` |
| Car insurance | `input_boolean.car_insurance_paid` | `input_number.car_insurance_amount` | `input_datetime.car_insurance_due` |

### 2b. Naming traps a build must not "correct"

- **Dining's motion and temperature sensors are named `living_room_living_room_*`.**
  `binary_sensor.living_room_living_room_motion` and
  `sensor.living_room_living_room_temperature` are assigned to the **Dining**
  area in HA. The living room's own sensor is the Hue one,
  `*_living_room_living_hue_hue_sensor_*`.
- **`switch.dinning_light_switch_1`** carries the misspelling in its real ID.
- **Duplicate media players.** `media_player.living_room_tv_samsung_q9_series_65`
  is the one V2 uses. `media_player.tv_samsung_q9_series_65` and
  `media_player.samsung_q9_series_65` were unavailable in the export. V3 uses
  the same player as V2.
- **Powerpal is grid import, not whole-house consumption.** It reads the
  meter, so while solar produces it sees less than the house uses. V2's
  comment calls it "whole-house". That is only true while the inverter is dark.
  V3 labels it *Grid import*.
- **Wall switches that feed a Hue group** (`switch.dinning_light_switch_1`,
  `switch.bedroomlight_switch_1`) are left out of the "lights on" count, so
  one lamp is never counted twice. The Parents' room has no Hue group, so its
  wall switch, `switch.mainroomlight_switch_1`, *is* its light.

## 2c. Full list, generated

Regenerate with `python3 design/casaray-v3/tools/gen_entity_table.py`.
Area and availability come from the 05/09 export.

### (no area)

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.casa_solar_online` | Casa Solar Online | ok | yes |
| `binary_sensor.matter_zigbee_hub_problem` | Matter ZigBee Hub Problem | ok | yes |
| `event.master_bedroom_emergency_button_dad_main` | Emergency Button Dad main | unavailable | yes |
| `event.master_bedroom_emergency_button_mum_main` | Emergency Button Mum main | unavailable | yes |
| `input_boolean.car_insurance_paid` | car_insurance_paid | ok | yes |
| `input_boolean.chinese_dashboard` | Chinese Dashboard | ok | yes |
| `input_boolean.council_rate_paid` | council_rate_paid | ok | yes |
| `input_boolean.elec_bill_paid` | Electricity Bill Paid | ok | yes |
| `input_boolean.gas_bill_paid` | Gas Bill Paid | ok | yes |
| `input_boolean.guest_mode` | Guest Mode | ok | yes |
| `input_boolean.rego_paid` | rego_paid | ok | yes |
| `input_boolean.water_bill_paid` | water_bill_paid | ok | yes |
| `input_datetime.car_insurance_due` | car_insurance_due | ok | yes |
| `input_datetime.council_rate_due` | council_rate_due | ok | yes |
| `input_datetime.elec_bill_due` | Electricity Bill Due | ok | yes |
| `input_datetime.gas_bill_due` | Gas Bill Due | ok | yes |
| `input_datetime.rego_due` | rego_due | ok | yes |
| `input_datetime.water_bill_due` | water_bill_due | ok | yes |
| `input_number.bills_paid_ytd` | Bills Paid YTD | ok | yes |
| `input_number.bills_saved_ytd` | Bills Saved YTD | ok | yes |
| `input_number.car_insurance_amount` | car_insurance_amount | ok | yes |
| `input_number.council_rate_amount` | council_rate_amount | ok | yes |
| `input_number.elec_bill_amount` | Electricity Bill Amount | ok | yes |
| `input_number.gas_bill_amount` | Gas Bill Amount | ok | yes |
| `input_number.gas_bill_mj` | Gas Bill Usage MJ | ok | yes |
| `input_number.rego_amount` | rego_amount | ok | yes |
| `input_number.water_bill_amount` | water_bill_amount | ok | yes |
| `person.ai_q_huang` | Ai Q Huang | ok | yes |
| `person.raymond_du` | Raymond Du. | ok | yes |
| `person.vinh_du` | Vinh Du | ok | yes |
| `sensor.ais_iphone_battery_level` | Ai’s iPhone Battery Level | ok | yes |
| `sensor.backup_last_successful_automatic_backup` | Backup Last successful automatic backup | ok | yes |
| `sensor.casa_monitored_power` | Casa Monitored Power | ok | yes |
| `sensor.casa_offline_devices` | Casa Offline Devices | ok | yes |
| `sensor.house_lights_on` | House Lights On | ok | yes |
| `sensor.raymonds_ipad_battery_level` | Raymond’s iPad Battery Level | ok | yes |
| `sensor.raymonds_iphone_battery_level` | Deez Raymond’s iPhone Battery Level | ok | yes |
| `sensor.sun_next_setting` | Sun Next setting | ok | yes |
| `sensor.vine_s_phone_battery_level` | Vinh’s phone Battery level | ok | yes |
| `todo.shopping_list` | Shopping List | ok | yes |
| `update.home_assistant_core_update` | Home Assistant Core Update | ok | yes |
| `update.home_assistant_operating_system_update` | Home Assistant Operating System Update | ok | yes |
| `update.home_assistant_supervisor_update` | Home Assistant Supervisor Update | ok | yes |

### Living Room

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.f_contact_sensor_door` | F/Contact Sensor Door | unavailable | yes |
| `binary_sensor.living_room_living_hue_hue_sensor_motion` | Living Room Motion Sensor Motion | ok | yes |
| `camera.front_door_live_view` | Front Door Live view | ok | yes |
| `fan.living_room_air_purifier` | Air purifier | ok | yes |
| `light.living_room` | Living room | ok | yes |
| `light.living_room_hue_ambiance_spot_1` | Living Room Inner Left | unavailable | yes |
| `light.living_room_hue_ambiance_spot_2` | Living Room Inner Right | unavailable | yes |
| `light.living_room_hue_ambiance_spot_3` | Living Room Outter Left | unavailable | yes |
| `light.living_room_hue_ambiance_spot_4` | Living Room Outter Right | unavailable | yes |
| `media_player.living_room_tv_samsung_q9_series_65` | [TV] Samsung Q9 Series (65) | ok | yes |
| `scene.living_room_living_room_bright` | Living room Bright | ok | yes |
| `scene.living_room_living_room_dimmed` | Living room Dimmed | unknown | yes |
| `scene.living_room_living_room_nightlight` | Living room Nightlight | unknown | yes |
| `scene.living_room_living_room_read` | Living room Read | unknown | yes |
| `scene.living_room_living_room_relax` | Living room Relax | unknown | yes |
| `sensor.front_door_battery` | Front Door Battery | ok | yes |
| `sensor.front_door_last_activity` | Front Door Last activity | ok | yes |
| `sensor.living_room_air_purifier_pm2_5` | Air purifier PM2.5 | ok | yes |
| `sensor.living_room_living_hue_hue_sensor_battery` | Living Room Motion Sensor Battery | ok | yes |
| `sensor.living_room_living_hue_hue_sensor_illuminance` | Living Room Motion Sensor Illuminance | ok | yes |
| `sensor.living_room_living_hue_hue_sensor_temperature` | Living Room Motion Sensor Temperature | ok | yes |
| `switch.front_door_motion_detection` | Front Door Motion detection | ok | yes |
| `switch.genio_power_board_with_usb_livingroom_socket_1` | Genio Power Board with USB-LivingRoom Socket 1 | ok | yes |
| `switch.genio_power_board_with_usb_livingroom_socket_2` | Genio Power Board with USB-LivingRoom Socket 2 | ok | yes |

### Dining

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.living_room_living_room_motion` | Dining Room Motion Sensor Motion | ok | yes |
| `camera.smart_pet_feeder` | Smart Pet Feeder | ok | yes |
| `light.dining` | Dining | ok | yes |
| `scene.dining_dining_read` | Dining Read | unknown | yes |
| `scene.dining_dining_relax` | Dining Relax | unknown | yes |
| `sensor.living_room_living_room_temperature` | Dining Room Motion Sensor Temperature | ok | yes |
| `switch.dinning_light_switch_1` | Dinning light Switch 1 | ok | yes |

### Kitchen

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.k_motion_sensor_motion` | K/Motion Sensor Motion | ok | yes |
| `binary_sensor.lg_fridge_door` | LG-Fridge Door | ok | yes |
| `number.lg_fridge_freezer_temperature` | LG-Fridge freezer temperature | ok | yes |
| `number.lg_fridge_fridge_temperature` | LG-Fridge fridge temperature | ok | yes |
| `sensor.kitchen_electrolux_fridge_temperature` | Electrolux Fridge Temperature | ok | yes |
| `switch.k_bot_p100` | K/Bot P100 | ok | yes |
| `switch.k_coffee_p100` | K/Coffee P100 | ok | yes |
| `switch.k_top_p100` | K/Top P100 | ok | yes |

### Parents Room

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.bedroom_motion_sensor_motion` | Parents Room Motion Sensor Motion | ok | yes |
| `binary_sensor.bedroom_parents_room_ac_room_occupied` | Parents Room AC Room occupied | ok | yes |
| `binary_sensor.emergency_button_dad_cloud_connection` | Emergency Button Dad Cloud connection | ok | yes |
| `binary_sensor.emergency_button_mum_cloud_connection` | Emergency Button Mum Cloud connection | ok | yes |
| `binary_sensor.m_contact_sensor_door` | M/Contact Sensor Door | unavailable | yes |
| `climate.bedroom_parents_room_ac` | Parents Room AC | ok | yes |
| `media_player.55_qled_4k_ai_qa55q7faawxxy` | 55" QLED 4k AI (QA55Q7FAAWXXY) | ok | yes |
| `sensor.bedroom_motion_sensor_humidity` | Parents Room Motion Sensor Humidity | ok | yes |
| `sensor.bedroom_motion_sensor_temperature` | Parents Room Motion Sensor Temperature | ok | yes |
| `switch.mainroomlight_switch_1` | MainRoomLight Switch 1 | ok | yes |

### Ray Bedroom

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `cover.aqara_roller_shade_driver_e1` | Aqara Roller Shade Driver E1 | ok | yes |
| `light.bedroom_bedroom` | Bedroom | ok | yes |
| `light.bedroom_nightlight` | NightLight | ok | yes |
| `media_player.q70f8036` | 55" QLED 4k AI | ok | yes |
| `scene.bedroom_bedroom_concentrate` | Bedroom Concentrate | ok | yes |
| `scene.bedroom_bedroom_nightlight` | Bedroom Nightlight | ok | yes |
| `scene.bedroom_bedroom_read` | Bedroom Read | ok | yes |
| `sensor.aqara_roller_shade_driver_e1_battery` | Aqara Roller Shade Driver E1 Battery | ok | yes |
| `sensor.r_energy_monitor_p110m_current_consumption` | R/Energy Monitor P110M Current consumption | ok | yes |
| `sensor.r_energy_monitor_p110m_this_month_s_consumption` | R/Energy Monitor P110M This month's consumption | ok | yes |
| `sensor.r_energy_monitor_p110m_voltage` | R/Energy Monitor P110M Voltage | ok | yes |
| `switch.r_energy_monitor_p110m` | R/Energy Monitor P110M | ok | yes |

### Garage

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `sensor.g_monitor_freezer_p110m_current_consumption` | G/Monitor Freezer P110M Current consumption | ok | yes |
| `sensor.g_monitor_freezer_p110m_this_month_s_consumption` | G/Monitor Freezer P110M This month's consumption | ok | yes |
| `sensor.g_monitor_freezer_p110m_voltage` | G/Monitor Freezer P110M Voltage | ok | yes |
| `switch.g_monitor_freezer_p110m` | G/Monitor Freezer P110M | ok | yes |

### Guest Room

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `media_player.pogo` | Pogo | unavailable | yes |
| `switch.g_printer_p100` | G/Printer P100 | ok | yes |

### Backyard

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.b_contact_sensor_door` | B/Contact Sensor Door | unavailable | yes |

### Network

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `binary_sensor.eero_wan_status` | eero Gateway WAN status | ok | yes |
| `camera.tapo_c200_stockroom_hd_stream_direct` | Tapo C200 - Stockroom HD Stream (Direct) | ok | yes |
| `camera.tapo_c420_east_wall_hd_stream_direct` | Tapo C420 East Wall HD Stream (Direct) | unavailable | yes |
| `camera.tapo_c420_south_wall_hd_stream_direct` | Tapo C420 - South Wall HD Stream (Direct) | unavailable | yes |
| `camera.tapo_c425_north_wall_hd_stream_direct` | Tapo C425 - North Wall HD Stream (Direct) | ok | yes |
| `sensor.tapo_c425_north_wall_battery` | Tapo C425 - North Wall Battery | ok | yes |
| `siren.tapo_c200_stockroom_siren` | Tapo C200 - Stockroom Siren | ok | yes |
| `siren.tapo_c425_north_wall_siren` | Tapo C425 - North Wall Siren | ok | yes |
| `siren.tapo_h200` | Tapo H200 | ok | yes |

### Energy

| Entity ID | Export name | 05/09 | In V2 |
|---|---|---|---|
| `sensor.electricity_maps_co2_intensity` | Electricity Maps CO2 intensity | ok | yes |
| `sensor.electricity_maps_grid_fossil_fuel_percentage` | Electricity Maps Grid fossil fuel percentage | ok | yes |
| `sensor.energy_production_today` | Solar production forecast Estimated energy production - today | ok | yes |
| `sensor.energy_production_today_remaining` | Solar production forecast Estimated energy production - remaining today | ok | yes |
| `sensor.energy_production_tomorrow` | Solar production forecast Estimated energy production - tomorrow | ok | yes |
| `sensor.gas_meter_pulse_sensor_battery` | Gas Meter Pulse Sensor Battery | ok | yes |
| `sensor.power_highest_peak_time_today` | Solar production forecast Highest power peak time - today | ok | yes |
| `sensor.powerpal_gateway_powerpal_battery` | Powerpal Gateway Powerpal Battery | ok | yes |
| `sensor.powerpal_gateway_powerpal_daily_energy` | Powerpal Gateway Powerpal Daily Energy | ok | yes |
| `sensor.powerpal_gateway_powerpal_power` | Powerpal Gateway Powerpal Power | ok | yes |
| `sensor.primo_5_0_1_1_ac_power` | Primo 5.0-1 (1) AC power | ok | yes |
| `weather.forecast_home` | Forecast Home | ok | yes |

_132 entity IDs; 132 already on V2, 0 new to CasaRay._

## 3. Gaps: things the design shows that no entity provides

| Where | What is missing | What the prototype does | To close it |
|---|---|---|---|
| Home › One tap, Lighting | Whole-home Evening, Goodnight, Movie and All lights off (`CR-233`) | *Proposed* pill; acts on demo state only | Four new scripts. **Needs owner approval**, because they switch real devices, and Goodnight closes the blind. |
| Kitchen › Lights | No kitchen light is integrated | Grey card saying so | Integrate a light, if one exists |
| Ray's room › Temperature | No temperature sensor in the room | Grey card saying so | Add a sensor, or accept the gap |
| Energy › cost | No trustworthy electricity cost | No dollar figure; footnote cites `CFG-001` | Owner fixes the Energy dashboard cost source |
| Home › Energy now sparkline | Twelve hours of monitored load | Demo shape (fixed values) | Native `statistics-graph` on `sensor.casa_monitored_power` in the build |
| Light colour ("warm white") | Colour-temperature *name* | Demo attribute | Derive from `color_temp_kelvin` in a template |

## 4. Live check, 25/09/2026

A read-only `GetLiveContext` query on 25/09 reported entities **by friendly
name, not ID**. The names below are unambiguous against the export. Where this
differs from the demo data, the prototype's outage scenario shows how the page
behaves.

| Entity | Demo data | Live 25/09 | Consequence |
|---|---|---|---|
| `person.raymond_du`, `person.vinh_du`, `person.ai_q_huang` | home / home / away | **unavailable, all three** | Who's home and the Home chip would read *No data* today. **Worth checking before any build:** three person entities down at once usually means their trackers or the mobile app integration, not the people. |
| `weather.forecast_home` | cloudy 10° | **unavailable** | Right now would show the grey Weather card |
| `camera.tapo_c425_north_wall_hd_stream_direct` | live | **unavailable** | Cameras chip would read 2 of 6 |
| `camera.tapo_c200_stockroom_hd_stream_direct` | live | **unavailable** | as above |
| `camera.front_door_live_view`, `camera.smart_pet_feeder` | live | idle (live) | matches |
| `light.living_room` | on, 89% | on, 100% | matches (brightness differs) |
| `climate.bedroom_parents_room_ac` | off, 23.3° room | off, 23.3° | matches |
| `fan.living_room_air_purifier` | on, high | off | demo differs; harmless |
| `cover.aqara_roller_shade_driver_e1` | closed | closed | matches |

`CLAUDE.md` records the three C420-era cameras and contact sensors coming
*back* by 19/09. This check shows the reverse on the same day for other
devices. Availability on this instance moves, and a build must be checked
against the live instance, not the export.
