# Entity Inventory

> **Generated file — do not edit by hand.**
> Regenerate with `python3 scripts/build_entity_inventory.py snapshots/2026-08-23-assist-context.json`.

## How this was produced

This inventory is generated from a Home Assistant **Assist live-context snapshot**, which is the authoritative live view available to this repository's tooling.

Two limitations follow from that source, and both matter when writing dashboards or automations:

1. **No entity IDs.** The Assist context reports friendly names, domains, areas and states, but not canonical `domain.object_id` entity IDs. Entity IDs in this repository must be confirmed against Home Assistant itself (Developer Tools → States) before being referenced in YAML. Names below are *not* a substitute for an entity ID.
2. **Assist-exposed entities only.** Entities hidden from Assist do not appear here, so this is a lower bound on what exists. Notably, no `automation`, `script`, or `alarm_control_panel` entities are present in the snapshot; that means they are not exposed to Assist, not that none are configured.

## Summary

- **Entities captured:** 431
- **Areas:** 10 (+72 entities with no area)
- **Domains:** 25
- **Currently unavailable:** 76

### Entities per domain

| Domain | Count |
| --- | ---: |
| `sensor` | 129 |
| `switch` | 60 |
| `binary_sensor` | 47 |
| `select` | 33 |
| `scene` | 29 |
| `light` | 25 |
| `event` | 22 |
| `number` | 22 |
| `button` | 20 |
| `media_player` | 9 |
| `camera` | 6 |
| `device_tracker` | 6 |
| `notify` | 6 |
| `person` | 3 |
| `remote` | 2 |
| `time` | 2 |
| `zone` | 2 |
| `climate` | 1 |
| `cover` | 1 |
| `fan` | 1 |
| `input_boolean` | 1 |
| `input_number` | 1 |
| `input_select` | 1 |
| `todo` | 1 |
| `weather` | 1 |

### Entities per area

| Area | Count | Unavailable |
| --- | ---: | ---: |
| Backyard | 10 | 7 |
| Dining | 27 | 4 |
| Energy | 23 | 12 |
| Garage | 11 | 1 |
| Guest Room | 6 | 3 |
| Kitchen | 22 | 8 |
| Living Room | 64 | 4 |
| Network | 96 | 10 |
| Parents Room | 39 | 2 |
| Ray Bedroom | 61 | 12 |
| Unassigned | 72 | 13 |

## Entities by area

`unavailable` states are flagged. A `unknown` state on a stateless domain (`button`, `event`, `notify`, `scene`, `select`, `time`) is normal and is not flagged.

### Backyard

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | B/Contact Sensor Cloud connection | `on` | (connectivity) |
| `binary_sensor` | B/Contact Sensor Door | `off` | (door) |
| `binary_sensor` | B/Contact Sensor Door | `unavailable` ⚠️ | (door) |
| `binary_sensor` | Tapo_C200_5C35 Motion | `unavailable` ⚠️ | (motion) |
| `binary_sensor` | Tapo_Camera Motion | `unavailable` ⚠️ | (motion) |
| `sensor` | B/Contact Sensor Signal level | `1` | — |
| `sensor` | B/Freezer/EnergyMonitor/P110M Energy | `unavailable` ⚠️ | kWh (energy) |
| `sensor` | B/Freezer/EnergyMonitor/P110M Energy difference | `unavailable` ⚠️ | kWh (energy) |
| `sensor` | Tapo_Camera Battery | `unavailable` ⚠️ | % (battery) |
| `switch` | B/Freezer/EnergyMonitor/P110M | `unavailable` ⚠️ | — |

### Dining

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | Dining Room Motion Sensor Motion | `off` | (motion) |
| `binary_sensor` | Sensor group Motion | `off` | (motion) |
| `button` | Smart Pet Feeder Restart | `unknown` | (restart) |
| `camera` | Smart Pet Feeder | `idle` | — |
| `light` | Corridor 1 | `unavailable` ⚠️ | — |
| `light` | Corridor 2 | `unavailable` ⚠️ | — |
| `light` | Dining | `on` | — |
| `light` | Dining | `on` | — |
| `light` | Dining Light Left | `unavailable` ⚠️ | — |
| `light` | Dining Light Right | `unavailable` ⚠️ | — |
| `light` | Smart Pet Feeder Indicator light | `on` | — |
| `number` | Smart Pet Feeder Volume | `1.0` | % |
| `scene` | Dining Concentrate | `unknown` | — |
| `scene` | Dining Energize | `unknown` | — |
| `scene` | Dining Midwinter | `unknown` | — |
| `scene` | Dining Nightlight | `unknown` | — |
| `scene` | Dining Read | `unknown` | — |
| `scene` | Dining Relax | `unknown` | — |
| `select` | Smart Pet Feeder Motion detection sensitivity | `1` | — |
| `select` | Smart Pet Feeder Night vision | `0` | — |
| `sensor` | Dining Room Motion Sensor Battery | `100` | % (battery) |
| `sensor` | Dining Room Motion Sensor Illuminance | `165` | lx (illuminance) |
| `sensor` | Dining Room Motion Sensor Temperature | `16.2` | °C (temperature) |
| `sensor` | Sensor group Illuminance | `35` | lx (illuminance) |
| `switch` | Dining Room Motion Sensor Light sensor enabled | `on` | (switch) |
| `switch` | Dining Room Motion Sensor Motion sensor enabled | `on` | (switch) |
| `switch` | Dinning light Switch 1 | `on` | (outlet) |

### Energy

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `sensor` | Electricity Maps CO2 intensity | `700.0` | gCO2eq/kWh |
| `sensor` | Electricity Maps Grid fossil fuel percentage | `87.57` | % |
| `sensor` | Primo 5.0-1 (1) AC current | `unavailable` ⚠️ | A (current) |
| `sensor` | Primo 5.0-1 (1) AC power | `unavailable` ⚠️ | W (power) |
| `sensor` | Primo 5.0-1 (1) DC current | `unavailable` ⚠️ | A (current) |
| `sensor` | Primo 5.0-1 (1) DC voltage | `unavailable` ⚠️ | V (voltage) |
| `sensor` | Primo 5.0-1 (1) Energy day | `unavailable` ⚠️ | Wh (energy) |
| `sensor` | Primo 5.0-1 (1) Energy year | `unavailable` ⚠️ | Wh (energy) |
| `sensor` | Primo 5.0-1 (1) Total energy | `unavailable` ⚠️ | Wh (energy) |
| `sensor` | Solar production forecast Estimated energy production - next hour | `0.0` | kWh (energy) |
| `sensor` | Solar production forecast Estimated energy production - remaining today | `13.3` | kWh (energy) |
| `sensor` | Solar production forecast Estimated energy production - this hour | `0.0` | kWh (energy) |
| `sensor` | Solar production forecast Estimated energy production - today | `12.5` | kWh (energy) |
| `sensor` | Solar production forecast Estimated energy production - tomorrow | `6.6` | kWh (energy) |
| `sensor` | Solar production forecast Estimated power production - now | `0` | W (power) |
| `sensor` | Solar production forecast Highest power peak time - today | `2026-08-23T12:00:00+10:00` | (timestamp) |
| `sensor` | Solar production forecast Highest power peak time - tomorrow | `2026-08-24T12:00:00+10:00` | (timestamp) |
| `sensor` | SolarNet CO₂ factor | `unavailable` ⚠️ | kg/kWh |
| `sensor` | SolarNet Grid export tariff | `unavailable` ⚠️ | AUD/kWh |
| `sensor` | SolarNet Grid import tariff | `unavailable` ⚠️ | AUD/kWh |
| `sensor` | SolarNet Meter mode | `unavailable` ⚠️ | — |
| `sensor` | SolarNet Power photovoltaics | `unavailable` ⚠️ | W (power) |
| `weather` | Forecast Home | `partlycloudy` | — |

### Garage

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | G/Monitor Freezer P110M Cloud connection | `on` | (connectivity) |
| `binary_sensor` | G/Monitor Freezer P110M Overheated | `unavailable` ⚠️ | (problem) |
| `binary_sensor` | G/Monitor Freezer P110M Overloaded | `off` | (problem) |
| `number` | G/Monitor Freezer P110M Power protection | `2149` | — |
| `sensor` | G/Monitor Freezer P110M Current | `0.03` | A (current) |
| `sensor` | G/Monitor Freezer P110M Current consumption | `1.7` | W (power) |
| `sensor` | G/Monitor Freezer P110M Signal level | `2` | — |
| `sensor` | G/Monitor Freezer P110M This month's consumption | `10.034` | kWh (energy) |
| `sensor` | G/Monitor Freezer P110M Today's consumption | `0.064` | kWh (energy) |
| `sensor` | G/Monitor Freezer P110M Voltage | `232.4` | V (voltage) |
| `switch` | G/Monitor Freezer P110M | `on` | — |

### Guest Room

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | G/Printer P100 Cloud connection | `on` | (connectivity) |
| `light` | Kogan Tv | `unavailable` ⚠️ | — |
| `media_player` | Pogo | `unavailable` ⚠️ | — |
| `sensor` | G/Printer P100 Signal level | `3` | — |
| `switch` | G/Printer P100 | `off` | — |
| `switch` | G/Printer P100 | `unavailable` ⚠️ | — |

### Kitchen

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | K/Bot P100 Cloud connection | `on` | (connectivity) |
| `binary_sensor` | K/Coffee P100 Cloud connection | `on` | (connectivity) |
| `binary_sensor` | K/Motion Sensor Cloud connection | `unavailable` ⚠️ | (connectivity) |
| `binary_sensor` | K/Motion Sensor Motion | `unavailable` ⚠️ | (motion) |
| `binary_sensor` | K/Motion Sensor Motion | `unavailable` ⚠️ | (motion) |
| `binary_sensor` | K/Motion Sensor Occupancy | `on` | (occupancy) |
| `binary_sensor` | K/Smart Button Cloud connection | `unavailable` ⚠️ | (connectivity) |
| `binary_sensor` | K/Top P100 Cloud connection | `on` | (connectivity) |
| `binary_sensor` | LG-Fridge Door | `off` | (door) |
| `event` | K/Smart Button main | `unavailable` ⚠️ | (button) |
| `number` | LG-Fridge freezer temperature | `-18` | °C |
| `number` | LG-Fridge fridge temperature | `3` | °C |
| `sensor` | K/Bot P100 Signal level | `3` | — |
| `sensor` | K/Coffee P100 Signal level | `3` | — |
| `sensor` | K/Top P100 Signal level | `3` | — |
| `switch` | K/Bot P100 | `on` | — |
| `switch` | K/Bot P100 | `unavailable` ⚠️ | — |
| `switch` | K/Coffee P100 | `on` | — |
| `switch` | K/Coffee P100 | `unavailable` ⚠️ | — |
| `switch` | K/Top P100 | `on` | — |
| `switch` | K/Top P100 | `unavailable` ⚠️ | — |
| `switch` | LG-Fridge Express mode | `off` | (switch) |

### Living Room

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | F/Contact Sensor Cloud connection | `on` | (connectivity) |
| `binary_sensor` | F/Contact Sensor Door | `off` | (door) |
| `binary_sensor` | Living room Motion | `off` | (motion) |
| `binary_sensor` | Living Room Motion Sensor Motion | `off` | (motion) |
| `binary_sensor` | RingRing Motion | `off` | (motion) |
| `camera` | Front Door Live view | `idle` | — |
| `event` | Front Door Ding | `2026-08-21T05:01:40.921+00:00` | (doorbell) |
| `event` | Front Door Motion | `2026-08-21T05:06:45.397+00:00` | (motion) |
| `event` | Living Room Switch Button 1 | `unknown` | (button) |
| `event` | Living Room Switch Button 2 | `unknown` | (button) |
| `event` | Living Room Switch Button 3 | `unknown` | (button) |
| `event` | Living Room Switch Button 4 | `unknown` | (button) |
| `event` | RingRing main | `2026-08-22T07:14:05.294+00:00` | (button) |
| `fan` | Air purifier | `on` | — |
| `light` | Living room | `on` | — |
| `light` | Living room | `on` | — |
| `light` | Living Room Inner Left | `unavailable` ⚠️ | — |
| `light` | Living Room Inner Right | `unavailable` ⚠️ | — |
| `light` | Living Room Outter Left | `unavailable` ⚠️ | — |
| `light` | Living Room Outter Right | `unavailable` ⚠️ | — |
| `media_player` | [TV] Samsung Q9 Series (65) | `idle` | — |
| `media_player` | [TV] Samsung Q9 Series (65) | `on` | (tv) |
| `media_player` | Samsung Q9 Series (65) | `idle` | (speaker) |
| `media_player` | Samsung Q9 Series (65) | `on` | (tv) |
| `remote` | [TV] Samsung Q9 Series (65) | `on` | — |
| `scene` | Living room Bright | `2026-08-14T16:35:51.021009+00:00` | — |
| `scene` | Living room Concentrate | `unknown` | — |
| `scene` | Living room Dimmed | `unknown` | — |
| `scene` | Living room Energize | `unknown` | — |
| `scene` | Living room Midwinter | `unknown` | — |
| `scene` | Living room Nightlight | `unknown` | — |
| `scene` | Living room Read | `unknown` | — |
| `scene` | Living room Relax | `unknown` | — |
| `select` | Air purifier Lamp | `high` | — |
| `select` | Genio Power Board with USB-LivingRoom Power-on behavior | `last` | — |
| `sensor` | Air purifier Air quality | `1` | CAQI |
| `sensor` | Air purifier Odor sensor | `1` | — |
| `sensor` | Air purifier PM1 | `5` | μg/m³ (pm1) |
| `sensor` | Air purifier PM1 health concern | `good` | (enum) |
| `sensor` | Air purifier PM10 | `5` | μg/m³ (pm10) |
| `sensor` | Air purifier PM10 health concern | `good` | (enum) |
| `sensor` | Air purifier PM2.5 | `5` | μg/m³ (pm25) |
| `sensor` | Air purifier PM2.5 health concern | `good` | (enum) |
| `sensor` | F/Contact Sensor Signal level | `3` | — |
| `sensor` | Front Door Battery | `24` | % (battery) |
| `sensor` | Front Door Last activity | `2026-08-23T00:31:14+10:00` | (timestamp) |
| `sensor` | Living room Illuminance | `35` | lx (illuminance) |
| `sensor` | Living Room Motion Sensor Battery | `100` | % (battery) |
| `sensor` | Living Room Motion Sensor Illuminance | `35` | lx (illuminance) |
| `sensor` | Living Room Motion Sensor Temperature | `18.4` | °C (temperature) |
| `sensor` | Living Room Switch Battery | `58` | % (battery) |
| `sensor` | RingRing Battery | `28` | % (battery) |
| `sensor` | Samsung Q9 Series (65) TV channel | — | — |
| `sensor` | Samsung Q9 Series (65) TV channel name | `9Ur5IzDKqV.TizenYouTube` | — |
| `switch` | Air purifier | `on` | — |
| `switch` | Front Door In-home chime | `on` | — |
| `switch` | Front Door Motion detection | `on` | — |
| `switch` | Genio Power Board with USB-LivingRoom Socket 1 | `on` | (outlet) |
| `switch` | Genio Power Board with USB-LivingRoom Socket 2 | `on` | (outlet) |
| `switch` | Genio Power Board with USB-LivingRoom Socket 3 | `on` | (outlet) |
| `switch` | Genio Power Board with USB-LivingRoom Socket 4 | `on` | (outlet) |
| `switch` | Genio Power Board with USB-LivingRoom Socket 5 | `on` | (outlet) |
| `switch` | Living Room Motion Sensor Light sensor enabled | `on` | (switch) |
| `switch` | Living Room Motion Sensor Motion sensor enabled | `on` | (switch) |

### Network

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | eero Gateway WAN status | `on` | (connectivity) |
| `binary_sensor` | TP-LinkHub H100 Cloud connection | `on` | (connectivity) |
| `binary_sensor` | TP-LinkHub H100 Overheated | `off` | (problem) |
| `button` | Tapo C200 - Stockroom Calibrate | `unknown` | — |
| `button` | Tapo C200 - Stockroom Manual Alarm Start | `unknown` | — |
| `button` | Tapo C200 - Stockroom Manual Alarm Stop | `unknown` | — |
| `button` | Tapo C200 - Stockroom Move Down | `unknown` | — |
| `button` | Tapo C200 - Stockroom Move Left | `unknown` | — |
| `button` | Tapo C200 - Stockroom Move Right | `unknown` | — |
| `button` | Tapo C200 - Stockroom Move Up | `unknown` | — |
| `button` | Tapo C200 - Stockroom Reboot | `unknown` | (restart) |
| `button` | Tapo C425 - North Wall Manual Alarm Start | `unknown` | — |
| `button` | Tapo C425 - North Wall Manual Alarm Stop | `unknown` | — |
| `button` | Tapo C425 - North Wall Reboot | `unknown` | (restart) |
| `button` | Tapo H200 Pair new device | `unavailable` ⚠️ | — |
| `button` | TP-LinkHub H100 Pair new device | `unknown` | — |
| `camera` | Tapo C200 - Stockroom HD Stream (Direct) | `idle` | — |
| `camera` | Tapo C420 - South Wall HD Stream (Direct) | `idle` | — |
| `camera` | Tapo C420 East Wall HD Stream (Direct) | `idle` | — |
| `camera` | Tapo C425 - North Wall HD Stream (Direct) | `idle` | — |
| `light` | Tapo C200 - Stockroom Floodlight (Timed) | `off` | — |
| `light` | Tapo C420 - South Wall Floodlight (Timed) | `off` | — |
| `light` | Tapo C420 East Wall Floodlight (Timed) | `off` | — |
| `light` | Tapo C425 - North Wall Floodlight (Timed) | `off` | — |
| `number` | RingChime Volume | `5.0` | — |
| `number` | Tapo C200 - Stockroom Microphone - Volume | `0` | — |
| `number` | Tapo C200 - Stockroom Motion Detection - Digital Sensitivity | `80` | — |
| `number` | Tapo C200 - Stockroom Speaker - Volume | `100` | — |
| `number` | Tapo C200 - Stockroom Spotlight Intensity | `5` | — |
| `number` | Tapo C420 - South Wall Microphone - Volume | `100` | — |
| `number` | Tapo C420 - South Wall Motion Detection - Digital Sensitivity | `60` | — |
| `number` | Tapo C420 - South Wall Speaker - Volume | `85` | — |
| `number` | Tapo C420 East Wall Microphone - Volume | `100` | — |
| `number` | Tapo C420 East Wall Motion Detection - Digital Sensitivity | `60` | — |
| `number` | Tapo C420 East Wall Speaker - Volume | `85` | — |
| `number` | Tapo C425 - North Wall Microphone - Volume | `100` | — |
| `number` | Tapo C425 - North Wall Motion Detection - Digital Sensitivity | `30` | — |
| `number` | Tapo C425 - North Wall Speaker - Volume | `100` | — |
| `number` | Tapo C425 - North Wall Spotlight Intensity | `5` | — |
| `select` | Tapo C200 - Stockroom Light Frequency | `auto` | — |
| `select` | Tapo C200 - Stockroom Motion Detection | `high` | (motion_detection) |
| `select` | Tapo C200 - Stockroom Move to Preset | `unknown` | — |
| `select` | Tapo C200 - Stockroom Night Vision | `Infrared Mode` | (night_vision) |
| `select` | Tapo C200 - Stockroom Night Vision Switching | `auto` | (night_vision) |
| `select` | Tapo C200 - Stockroom Patrol Mode | `unknown` | (patrol_mode) |
| `select` | Tapo C200 - Stockroom Person Detection | `low` | (person_detection) |
| `select` | Tapo C420 - South Wall Light Frequency | `60` | — |
| `select` | Tapo C420 - South Wall Motion Detection | `normal` | (motion_detection) |
| `select` | Tapo C420 - South Wall Night Vision | `Infrared Mode` | (night_vision) |
| `select` | Tapo C420 - South Wall Person Detection | `normal` | (person_detection) |
| `select` | Tapo C420 - South Wall Pet Detection | `normal` | (pet_detection) |
| `select` | Tapo C420 - South Wall Spotlight Intensity | `5` | — |
| `select` | Tapo C420 - South Wall Vehicle Detection | `off` | (vehicle_detection) |
| `select` | Tapo C420 East Wall Light Frequency | `60` | — |
| `select` | Tapo C420 East Wall Motion Detection | `normal` | (motion_detection) |
| `select` | Tapo C420 East Wall Night Vision | `Infrared Mode` | (night_vision) |
| `select` | Tapo C420 East Wall Person Detection | `normal` | (person_detection) |
| `select` | Tapo C420 East Wall Pet Detection | `low` | (pet_detection) |
| `select` | Tapo C420 East Wall Spotlight Intensity | `5` | — |
| `select` | Tapo C420 East Wall Vehicle Detection | `off` | (vehicle_detection) |
| `select` | Tapo C425 - North Wall Motion Detection | `low` | (motion_detection) |
| `select` | Tapo C425 - North Wall Night Vision | `Infrared Mode` | (night_vision) |
| `select` | Tapo C425 - North Wall Night Vision Switching | `auto` | (night_vision) |
| `select` | Tapo C425 - North Wall Person Detection | `low` | (person_detection) |
| `select` | Tapo C425 - North Wall Pet Detection | `low` | (pet_detection) |
| `select` | Tapo C425 - North Wall Vehicle Detection | `off` | (vehicle_detection) |
| `sensor` | CPU Speed | `unknown` | GHz (frequency) |
| `sensor` | Tapo C200 - Stockroom Network SSID | `homeAI` | — |
| `sensor` | Tapo C420 - East Wall Battery | `unavailable` ⚠️ | % (battery) |
| `sensor` | Tapo C420 - South Wall Battery | `100` | % (battery) |
| `sensor` | Tapo C420 - South Wall Battery | `unavailable` ⚠️ | % (battery) |
| `sensor` | Tapo C420 East Wall Battery | `65` | % (battery) |
| `sensor` | Tapo C425 - North Wall Battery | `24` | % (battery) |
| `sensor` | TP-LinkHub Alarm | `unavailable` ⚠️ | (enum) |
| `sensor` | TP-LinkHub H100 Signal level | `3` | — |
| `switch` | AdGuard Home Filtering | `on` | — |
| `switch` | AdGuard Home Parental control | `off` | — |
| `switch` | AdGuard Home Protection | `on` | — |
| `switch` | AdGuard Home Query log | `on` | — |
| `switch` | AdGuard Home Safe browsing | `off` | — |
| `switch` | AdGuard Home Safe search | `on` | — |
| `switch` | Hue Bridge Automation: Coming home | `off` | (switch) |
| `switch` | Hue Bridge Automation: Leaving home | `off` | (switch) |
| `switch` | Hue Bridge Automation: Nightlight On Nightlight Off | `on` | (switch) |
| `switch` | Tapo C200 - Stockroom Auto Track | `on` | — |
| `switch` | Tapo C200 - Stockroom Preset Patrol Mode | `off` | — |
| `switch` | Tapo C200 - Stockroom Privacy | `off` | — |
| `switch` | Tapo C420 - East Wall Motion detection | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 - East Wall Person detection | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 - East Wall Tapo C420 East Wall | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 - South Wall Motion detection | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 - South Wall Person detection | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 - South Wall Privacy | `off` | — |
| `switch` | Tapo C420 - South Wall Tapo C420 - South Wall | `unavailable` ⚠️ | — |
| `switch` | Tapo C420 East Wall Privacy | `off` | — |
| `switch` | Tapo C425 - North Wall Privacy | `off` | — |

### Parents Room

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | Emergency Button Dad Cloud connection | `unavailable` ⚠️ | (connectivity) |
| `binary_sensor` | Emergency Button Mum Cloud connection | `unavailable` ⚠️ | (connectivity) |
| `binary_sensor` | M/Contact Sensor Cloud connection | `on` | (connectivity) |
| `binary_sensor` | M/Contact Sensor Door | `off` | (door) |
| `binary_sensor` | Parents Room AC Filter clean required | `off` | (problem) |
| `binary_sensor` | Parents Room AC Room occupied | `off` | (motion) |
| `binary_sensor` | Parents Room Motion Sensor Connectivity | `on` | (connectivity) |
| `binary_sensor` | Parents Room Motion Sensor Motion | `off` | (motion) |
| `button` | Parents Room AC Reset filter | `unknown` | — |
| `climate` | Parents Room AC | `off` | — |
| `media_player` | 55" QLED 4k AI | `off` | — |
| `media_player` | 55" QLED 4k AI | `idle` | (speaker) |
| `media_player` | 55" QLED 4k AI | `off` | (tv) |
| `sensor` | 55" QLED 4k AI Energy | `0.00` | kWh (energy) |
| `sensor` | 55" QLED 4k AI Energy difference | `0.00` | kWh (energy) |
| `sensor` | 55" QLED 4k AI Energy saved | `0.00` | kWh (energy) |
| `sensor` | 55" QLED 4k AI Power | `0.00` | W (power) |
| `sensor` | 55" QLED 4k AI Power energy | `0.00` | kWh (energy) |
| `sensor` | 55" QLED 4k AI TV channel | — | — |
| `sensor` | 55" QLED 4k AI TV channel name | `9Ur5IzDKqV.TizenYouTube` | — |
| `sensor` | Light Sensor - 55" QLED 4k AI Brightness intensity | `1` | level |
| `sensor` | Light Sensor - 55" QLED 4k AI Illuminance | `0` | lx (illuminance) |
| `sensor` | M/Contact Sensor Signal level | `3` | — |
| `sensor` | Parents Room AC Timer end time | `2025-03-10T14:21:21+11:00` | (timestamp) |
| `sensor` | Parents Room Motion Sensor Battery voltage | `3000` | V (voltage) |
| `sensor` | Parents Room Motion Sensor Humidity | `61.0` | % (humidity) |
| `sensor` | Parents Room Motion Sensor Temperature | `23.0` | °C (temperature) |
| `sensor` | Sensibo Sky Plus Air conditioner mode | `fanOnly` | — |
| `sensor` | Sensibo Sky Plus Cooling setpoint | `19.0` | °C (temperature) |
| `switch` | Light Sensor - 55" QLED 4k AI | `off` | — |
| `switch` | MainRoomLight Switch 1 | `off` | (outlet) |
| `switch` | Master bedroom power point Socket 1 | `on` | (outlet) |
| `switch` | Master bedroom power point Socket 2 | `on` | (outlet) |
| `switch` | Master bedroom power point Socket 3 | `on` | (outlet) |
| `switch` | Master bedroom power point Socket 4 | `on` | (outlet) |
| `switch` | Master bedroom power point Socket 5 | `on` | (outlet) |
| `switch` | Parents Room AC Climate React | `off` | (switch) |
| `switch` | Parents Room AC Timer | `off` | (switch) |
| `switch` | Sensibo Sky Plus | `off` | — |

### Ray Bedroom

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | Aqara Roller Shade Driver E1 Configuration status | `off` | (problem) |
| `binary_sensor` | LPH-SE DCD9 Pump | `on` | (running) |
| `binary_sensor` | Presence Multi-Sensor FP300 Occupancy | `unavailable` ⚠️ | (occupancy) |
| `binary_sensor` | R/Energy Monitor P110M Cloud connection | `on` | (connectivity) |
| `binary_sensor` | R/Energy Monitor P110M Overloaded | `off` | (problem) |
| `button` | Aqara Roller Shade Driver E1 Identify | `2026-08-15T16:47:24.535859+00:00` | (identify) |
| `button` | Presence Multi-Sensor FP300 Identify (1) | `unavailable` ⚠️ | (identify) |
| `button` | Presence Multi-Sensor FP300 Identify (2) | `unavailable` ⚠️ | (identify) |
| `button` | Presence Multi-Sensor FP300 Identify (3) | `unavailable` ⚠️ | (identify) |
| `button` | Presence Multi-Sensor FP300 Identify (4) | `unavailable` ⚠️ | (identify) |
| `cover` | Aqara Roller Shade Driver E1 | `open` | (shade) |
| `event` | Ray Bedroom Switch Button 1 | `2026-08-21T07:26:07.702+00:00` | (button) |
| `event` | Ray Bedroom Switch Button 2 | `2026-07-24T17:56:15.603+00:00` | (button) |
| `event` | Ray Bedroom Switch Button 3 | `2026-08-22T17:15:19.840+00:00` | (button) |
| `event` | Ray Bedroom Switch Button 4 | `2026-08-22T17:15:17.804+00:00` | (button) |
| `light` | Bedroom | `on` | — |
| `light` | NightLight | `on` | — |
| `media_player` | 55" QLED 4k AI (QA55Q7FAAWXXY) | `off` | (tv) |
| `number` | LPH-SE DCD9 Plants age | `51` | d |
| `number` | Presence Multi-Sensor FP300 Sensitivity | `unavailable` ⚠️ | — |
| `number` | R/Energy Monitor P110M Power protection | `2136` | — |
| `remote` | 55" QLED 4k AI (QA55Q7FAAWXXY) | `off` | — |
| `scene` | Bedroom Amber bloom | `2026-08-14T16:36:00.727360+00:00` | — |
| `scene` | Bedroom Baby's breath | `2026-08-14T16:36:03.067639+00:00` | — |
| `scene` | Bedroom Blossom | `2026-08-14T16:36:07.329159+00:00` | — |
| `scene` | Bedroom Concentrate | `2026-08-14T16:36:05.881515+00:00` | — |
| `scene` | Bedroom Dreamy dusk | `2026-08-14T16:36:12.609951+00:00` | — |
| `scene` | Bedroom Nature's colors | `2026-08-14T16:36:11.265968+00:00` | — |
| `scene` | Bedroom Nightlight | `2026-08-14T16:36:08.401613+00:00` | — |
| `scene` | Bedroom Nighttime | `2026-08-14T16:36:09.417815+00:00` | — |
| `scene` | Bedroom Pensive | `2026-08-08T15:17:52.698273+00:00` | — |
| `scene` | Bedroom Read | `2026-08-08T15:17:51.941886+00:00` | — |
| `scene` | Bedroom Silverstone | `unknown` | — |
| `scene` | Bedroom Soho | `2026-08-08T15:17:50.089018+00:00` | — |
| `scene` | Bedroom Starlight | `unknown` | — |
| `scene` | Bedroom Suzuka | `unknown` | — |
| `scene` | Bedroom Vapor wave | `2026-08-08T15:17:55.612180+00:00` | — |
| `select` | LPH-SE DCD9 Light brightness | `high` | — |
| `select` | LPH-SE DCD9 Light mode | `vegetable` | — |
| `sensor` | Aqara Roller Shade Driver E1 Battery | `74` | % (battery) |
| `sensor` | Aqara Roller Shade Driver E1 Battery charge state | `not_charging` | (enum) |
| `sensor` | Aqara Roller Shade Driver E1 Battery voltage | `3.00` | V (voltage) |
| `sensor` | Presence Multi-Sensor FP300 Battery | `unavailable` ⚠️ | % (battery) |
| `sensor` | Presence Multi-Sensor FP300 Battery type | `unavailable` ⚠️ | — |
| `sensor` | Presence Multi-Sensor FP300 Battery voltage | `unavailable` ⚠️ | V (voltage) |
| `sensor` | Presence Multi-Sensor FP300 Humidity | `unavailable` ⚠️ | % (humidity) |
| `sensor` | Presence Multi-Sensor FP300 Illuminance | `unavailable` ⚠️ | lx (illuminance) |
| `sensor` | Presence Multi-Sensor FP300 Temperature | `unavailable` ⚠️ | °C (temperature) |
| `sensor` | R/Energy Monitor P110M Current | `0.10` | A (current) |
| `sensor` | R/Energy Monitor P110M Current consumption | `12.8` | W (power) |
| `sensor` | R/Energy Monitor P110M Signal level | `1` | — |
| `sensor` | R/Energy Monitor P110M This month's consumption | `8.627` | kWh (energy) |
| `sensor` | R/Energy Monitor P110M Today's consumption | `0.078` | kWh (energy) |
| `sensor` | R/Energy Monitor P110M Voltage | `230.9` | V (voltage) |
| `sensor` | Ray Bedroom Switch Battery | `97` | % (battery) |
| `switch` | BedRoomLight Switch 1 | `off` | (outlet) |
| `switch` | LPH-SE DCD9 Power | `on` | — |
| `switch` | LPH-SE DCD9 Pump cycling | `on` | — |
| `switch` | R/Energy Monitor P110M | `on` | — |
| `time` | LPH-SE DCD9 Light off | `18:00:00` | — |
| `time` | LPH-SE DCD9 Light on | `06:00:00` | — |

### Unassigned

| Domain | Name | State | Unit / class |
| --- | --- | --- | --- |
| `binary_sensor` | Bedroom Hue Sensor Motion | `off` | (motion) |
| `binary_sensor` | F/Contact Sensor Door | `unavailable` ⚠️ | (door) |
| `binary_sensor` | iPhone Presence | `on` | (presence) |
| `binary_sensor` | Living Hue Hue Sensor Motion | `off` | (motion) |
| `binary_sensor` | M/Contact Sensor Door | `unavailable` ⚠️ | (door) |
| `binary_sensor` | Raymond’s iPad Kiosk Mode | `on` | — |
| `device_tracker` | Ai’s iPhone | `not_home` | — |
| `device_tracker` | CasaRay iPad | `unknown` | — |
| `device_tracker` | Deez | `home` | — |
| `device_tracker` | Deez | `home` | — |
| `device_tracker` | Raymond’s iPad | `home` | — |
| `device_tracker` | Vinh’s phone | `home` | — |
| `event` | BedlightSwitch button2 | `unknown` | (button) |
| `event` | BedlightSwitch button3 | `2026-08-22T17:15:20.315+00:00` | (button) |
| `event` | BedlightSwitch button4 | `2026-08-22T17:15:18.158+00:00` | (button) |
| `event` | BedlightSwitch main | `2026-08-21T07:26:08.070+00:00` | (button) |
| `event` | Emergency Button Dad main | `unavailable` ⚠️ | (button) |
| `event` | Emergency Button Mum main | `unavailable` ⚠️ | (button) |
| `event` | LivingroomSwitch button2 | `unknown` | (button) |
| `event` | LivingroomSwitch button3 | `unknown` | (button) |
| `event` | LivingroomSwitch button4 | `unknown` | (button) |
| `event` | LivingroomSwitch main | `unknown` | (button) |
| `input_boolean` | Chinese Dashboard | `off` | — |
| `input_number` | Gas Bill Usage MJ | `9437.04` | MJ |
| `input_select` | Family Location | `Raymond Du` | — |
| `light` | Hue ambiance spot 1 | `unavailable` ⚠️ | — |
| `light` | Hue ambiance spot 1 | `unavailable` ⚠️ | — |
| `light` | Hue ambiance spot 3 | `unavailable` ⚠️ | — |
| `light` | Hue ambiance spot 4 | `unavailable` ⚠️ | — |
| `light` | NightLight | `on` | — |
| `notify` | Ai’s iPhone | `unknown` | — |
| `notify` | CasaRay iPad | `2026-08-14T17:30:43.775571+00:00` | — |
| `notify` | Deez | `unknown` | — |
| `notify` | Deez | `unknown` | — |
| `notify` | Raymond’s iPad | `unknown` | — |
| `notify` | Vinh’s phone | `unknown` | — |
| `person` | Ai Q Huang | `not_home` | — |
| `person` | Raymond Du. | `home` | — |
| `person` | Vinh Du | `home` | — |
| `sensor` | Ai’s iPhone Battery Level | `60` | % (battery) |
| `sensor` | Ai’s iPhone Location permission | `Authorized when in use` | — |
| `sensor` | BedlightSwitch Battery | `97` | % (battery) |
| `sensor` | Bedroom Hue Sensor Battery | `100` | % (battery) |
| `sensor` | Bedroom Hue Sensor Illuminance | `165` | lx (illuminance) |
| `sensor` | Bedroom Hue Sensor Temperature | `16.2` | °C (temperature) |
| `sensor` | Deez Raymond’s iPhone Connection Type | `Cellular` | — |
| `sensor` | Deez Raymond’s iPhone Distance | `22` | m |
| `sensor` | Deez Raymond’s iPhone Kiosk Brightness | `unavailable` ⚠️ | — |
| `sensor` | Deez Raymond’s iPhone Kiosk Volume | `unavailable` ⚠️ | — |
| `sensor` | Deez Raymond’s iPhone Location permission | `Authorized Always` | — |
| `sensor` | Living Hue Hue Sensor Battery | `100` | % (battery) |
| `sensor` | Living Hue Hue Sensor Illuminance | `36` | lx (illuminance) |
| `sensor` | Living Hue Hue Sensor Temperature | `18.4` | °C (temperature) |
| `sensor` | LivingroomSwitch Battery | `58` | % (battery) |
| `sensor` | R/Laptop/Energy Monitor/P110M Energy | `unavailable` ⚠️ | kWh (energy) |
| `sensor` | R/Laptop/Energy Monitor/P110M Energy difference | `unavailable` ⚠️ | kWh (energy) |
| `sensor` | Raymond’s iPad Battery Level | `35` | % (battery) |
| `sensor` | Raymond’s iPad Battery State | `Not Charging` | — |
| `sensor` | Raymond’s iPad Connection Type | `Wi-Fi` | — |
| `sensor` | Raymond’s iPad Geocoded Location | `12 Edmond St` | — |
| `sensor` | Raymond’s iPad Kiosk Brightness | `0` | — |
| `sensor` | Raymond’s iPad Kiosk Volume | `10` | — |
| `sensor` | Raymond’s iPad Location permission | `Authorized Always` | — |
| `sensor` | Raymond’s iPad SSID | `homeAI` | — |
| `sensor` | Raymond’s iPad Storage | `22.84` | % available |
| `sensor` | sensor Cost | `unknown` | AUD (monetary) |
| `sensor` | Solar Power Display | `0 W` | — |
| `sensor` | Vinh’s phone Battery level | `95` | % (battery) |
| `switch` | R/Laptop/Energy Monitor/P110M | `unavailable` ⚠️ | — |
| `todo` | Shopping List | `0` | — |
| `zone` | Home | `2` | — |
| `zone` | Home | `2` | — |

