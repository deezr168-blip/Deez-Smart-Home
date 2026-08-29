# Entity Inventory

Status: **Verified against live Home Assistant instance on 2026-08-29 via GetLiveContext MCP tool. 425 entities recorded.**

This file is the source of truth for known Home Assistant entities, used to
validate live entity IDs before any automation/dashboard/script work
references them.

**Known limitation — no `entity_id` values available:** The `GetLiveContext`
MCP tool (the only live Home Assistant access available in this session)
returns each entity's display name, domain, state, area, and attributes, but
does **not** expose the underlying `entity_id` (e.g. `light.living_room`) or
any `unique_id`/`device_id`/`area_id`. Per instructions, entity IDs were
never invented or guessed. Every row below therefore has `unknown` in the
`entity_id` column; `friendly_name` is the only reliable identifier captured
this pass. A future stage with REST/WebSocket API access (entity registry,
device registry, area registry — see below) is required to fill in real
`entity_id` values.

Because names/domains can repeat (e.g. multiple Tapo camera helper entities
sharing a base name, or two distinct entities both named "Living room"
light), duplicate `(friendly_name, domain)` rows below represent genuinely
different entities as reported by the live tool, not parsing errors.

## How this gets populated (Stage 2)

Once read access to the Home Assistant REST/WebSocket API is configured and
verified (see `docs/access_verification.md` once that stage runs), this
file can be re-populated with real `entity_id`, `unique_id`, `device`, and
`exposed_to_assist` values from:

- Live state (`GET /api/states`)
- Entity registry (`config/entity_registry/list` over WebSocket)
- Device registry (`config/device_registry/list` over WebSocket)
- Area registry (`config/area_registry/list` over WebSocket)

## Planned structure

Entities are recorded one per row:

| entity_id | friendly_name | domain | area | device | enabled | exposed_to_assist | status | notes |
|---|---|---|---|---|---|---|---|---|

Where `status` is one of:

- `active` — present, enabled, matches expected config
- `stale` — present in this doc but not seen live on last validation pass
- `renamed` — entity_id changed since last recorded (old ID noted)
- `disabled` — present in registry but disabled
- `hidden` — present but not exposed to Assist / hidden from dashboards
- `duplicate` — ambiguous device with more than one matching entity

## Entities (2026-08-29 live pull)

| entity_id | friendly_name | domain | area | device | enabled | exposed_to_assist | status | notes |
|---|---|---|---|---|---|---|---|---|
| unknown | B/Contact Sensor Cloud connection | binary_sensor | Backyard | unknown | active | unknown | active |  |
| unknown | B/Contact Sensor Door | binary_sensor | Backyard | unknown | active | unknown | active |  |
| unknown | B/Contact Sensor Door | binary_sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo_C200_5C35 Motion | binary_sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo_Camera Motion | binary_sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | B/Contact Sensor Signal level | sensor | Backyard | unknown | active | unknown | active |  |
| unknown | B/Freezer/EnergyMonitor/P110M Energy | sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | B/Freezer/EnergyMonitor/P110M Energy difference | sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo_Camera Battery | sensor | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | B/Freezer/EnergyMonitor/P110M | switch | Backyard | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Bedroom Hue Sensor Motion | binary_sensor | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Motion | binary_sensor | Dining | unknown | active | unknown | active |  |
| unknown | Sensor group Motion | binary_sensor | Dining | unknown | active | unknown | active |  |
| unknown | Smart Pet Feeder Restart | button | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Smart Pet Feeder | camera | Dining | unknown | active | unknown | active |  |
| unknown | Corridor 1 | light | Dining | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Corridor 2 | light | Dining | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Dining | light | Dining | unknown | active | unknown | active |  |
| unknown | Dining | light | Dining | unknown | active | unknown | active |  |
| unknown | Dining Light Left | light | Dining | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Dining Light Right | light | Dining | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Smart Pet Feeder Indicator light | light | Dining | unknown | active | unknown | active |  |
| unknown | Smart Pet Feeder Volume | number | Dining | unknown | active | unknown | active |  |
| unknown | Dining Concentrate | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Dining Energize | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Dining Midwinter | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Dining Nightlight | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Dining Read | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Dining Relax | scene | Dining | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Smart Pet Feeder Motion detection sensitivity | select | Dining | unknown | active | unknown | active |  |
| unknown | Smart Pet Feeder Night vision | select | Dining | unknown | active | unknown | active |  |
| unknown | Bedroom Hue Sensor Battery | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Bedroom Hue Sensor Illuminance | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Bedroom Hue Sensor Temperature | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Battery | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Illuminance | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Temperature | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Sensor group Illuminance | sensor | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Light sensor enabled | switch | Dining | unknown | active | unknown | active |  |
| unknown | Dining Room Motion Sensor Motion sensor enabled | switch | Dining | unknown | active | unknown | active |  |
| unknown | Dinning light Switch 1 | switch | Dining | unknown | active | unknown | active |  |
| unknown | Electricity Maps CO2 intensity | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Electricity Maps Grid fossil fuel percentage | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) AC current | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) AC power | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) DC current | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) DC voltage | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) Energy day | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) Energy year | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Primo 5.0-1 (1) Total energy | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated energy production - next hour | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated energy production - remaining today | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated energy production - this hour | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated energy production - today | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated energy production - tomorrow | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Estimated power production - now | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Highest power peak time - today | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Solar production forecast Highest power peak time - tomorrow | sensor | Energy | unknown | active | unknown | active |  |
| unknown | SolarNet CO₂ factor | sensor | Energy | unknown | active | unknown | active |  |
| unknown | SolarNet Grid export tariff | sensor | Energy | unknown | active | unknown | active |  |
| unknown | SolarNet Grid import tariff | sensor | Energy | unknown | active | unknown | active |  |
| unknown | SolarNet Meter mode | sensor | Energy | unknown | active | unknown | active |  |
| unknown | SolarNet Power photovoltaics | sensor | Energy | unknown | active | unknown | active |  |
| unknown | Forecast Home | weather | Energy | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Cloud connection | binary_sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Overheated | binary_sensor | Garage | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | G/Monitor Freezer P110M Overloaded | binary_sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Power protection | number | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Current | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Current consumption | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Signal level | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M This month's consumption | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Today's consumption | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M Voltage | sensor | Garage | unknown | active | unknown | active |  |
| unknown | G/Monitor Freezer P110M | switch | Garage | unknown | active | unknown | active |  |
| unknown | G/Printer P100 Cloud connection | binary_sensor | Guest Room | unknown | active | unknown | active |  |
| unknown | Kogan Tv | light | Guest Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Pogo | media_player | Guest Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | G/Printer P100 Signal level | sensor | Guest Room | unknown | active | unknown | active |  |
| unknown | G/Printer P100 | switch | Guest Room | unknown | active | unknown | active |  |
| unknown | G/Printer P100 | switch | Guest Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | K/Bot P100 Cloud connection | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Coffee P100 Cloud connection | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Motion Sensor Cloud connection | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Motion Sensor Motion | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Motion Sensor Motion | binary_sensor | Kitchen | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | K/Motion Sensor Occupancy | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Smart Button Cloud connection | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Top P100 Cloud connection | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | LG-Fridge Door | binary_sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Smart Button main | event | Kitchen | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | LG-Fridge freezer temperature | number | Kitchen | unknown | active | unknown | active |  |
| unknown | LG-Fridge fridge temperature | number | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Bot P100 Signal level | sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Coffee P100 Signal level | sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Top P100 Signal level | sensor | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Bot P100 | switch | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Bot P100 | switch | Kitchen | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | K/Coffee P100 | switch | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Coffee P100 | switch | Kitchen | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | K/Top P100 | switch | Kitchen | unknown | active | unknown | active |  |
| unknown | K/Top P100 | switch | Kitchen | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | LG-Fridge Express mode | switch | Kitchen | unknown | active | unknown | active |  |
| unknown | F/Contact Sensor Cloud connection | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | F/Contact Sensor Door | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | F/Contact Sensor Door | binary_sensor | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Living Hue Hue Sensor Motion | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living room Motion | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Motion | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | RingRing Motion | binary_sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Live view | camera | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Ding | event | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Motion | event | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Switch Button 1 | event | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living Room Switch Button 2 | event | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living Room Switch Button 3 | event | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living Room Switch Button 4 | event | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | RingRing main | event | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier | fan | Living Room | unknown | active | unknown | active |  |
| unknown | Hue ambiance spot 1 | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Hue ambiance spot 1 | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Hue ambiance spot 3 | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Hue ambiance spot 4 | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Living room | light | Living Room | unknown | active | unknown | active |  |
| unknown | Living room | light | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Inner Left | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Living Room Inner Right | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Living Room Outter Left | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Living Room Outter Right | light | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | [TV] Samsung Q9 Series (65) | media_player | Living Room | unknown | active | unknown | active |  |
| unknown | [TV] Samsung Q9 Series (65) | media_player | Living Room | unknown | active | unknown | active |  |
| unknown | Samsung Q9 Series (65) | media_player | Living Room | unknown | active | unknown | active |  |
| unknown | Samsung Q9 Series (65) | media_player | Living Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | [TV] Samsung Q9 Series (65) | remote | Living Room | unknown | active | unknown | active |  |
| unknown | Living room Bright | scene | Living Room | unknown | active | unknown | active |  |
| unknown | Living room Concentrate | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Dimmed | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Energize | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Midwinter | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Nightlight | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Read | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Living room Relax | scene | Living Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Air purifier Lamp | select | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Power-on behavior | select | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier Air quality | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier Odor sensor | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM1 | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM1 health concern | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM10 | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM10 health concern | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM2.5 | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier PM2.5 health concern | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | F/Contact Sensor Signal level | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Battery | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Last activity | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Hue Hue Sensor Battery | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Hue Hue Sensor Illuminance | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Hue Hue Sensor Temperature | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living room Illuminance | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Battery | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Illuminance | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Temperature | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Switch Battery | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | RingRing Battery | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Samsung Q9 Series (65) TV channel | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Samsung Q9 Series (65) TV channel name | sensor | Living Room | unknown | active | unknown | active |  |
| unknown | Air purifier | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door In-home chime | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Front Door Motion detection | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Socket 1 | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Socket 2 | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Socket 3 | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Socket 4 | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Genio Power Board with USB-LivingRoom Socket 5 | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Light sensor enabled | switch | Living Room | unknown | active | unknown | active |  |
| unknown | Living Room Motion Sensor Motion sensor enabled | switch | Living Room | unknown | active | unknown | active |  |
| unknown | eero Gateway WAN status | binary_sensor | Network | unknown | active | unknown | active |  |
| unknown | TP-LinkHub H100 Cloud connection | binary_sensor | Network | unknown | active | unknown | active |  |
| unknown | TP-LinkHub H100 Overheated | binary_sensor | Network | unknown | active | unknown | active |  |
| unknown | Tapo C200 - Stockroom Calibrate | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Manual Alarm Start | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Manual Alarm Stop | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Move Down | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Move Left | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Move Right | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Move Up | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Reboot | button | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Manual Alarm Start | button | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Tapo C425 - North Wall Manual Alarm Stop | button | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Tapo C425 - North Wall Reboot | button | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Tapo H200 Pair new device | button | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | TP-LinkHub H100 Pair new device | button | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Tapo C200 - Stockroom HD Stream (Direct) | camera | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall HD Stream (Direct) | camera | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall HD Stream (Direct) | camera | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall HD Stream (Direct) | camera | Network | unknown | active | unknown | active |  |
| unknown | Tapo C200 - Stockroom Floodlight (Timed) | light | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Floodlight (Timed) | light | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Floodlight (Timed) | light | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Floodlight (Timed) | light | Network | unknown | active | unknown | active |  |
| unknown | RingChime Volume | number | Network | unknown | active | unknown | active |  |
| unknown | Tapo C200 - Stockroom Microphone - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Motion Detection - Digital Sensitivity | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Speaker - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Spotlight Intensity | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Microphone - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Motion Detection - Digital Sensitivity | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Speaker - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Microphone - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Motion Detection - Digital Sensitivity | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Speaker - Volume | number | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Microphone - Volume | number | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Motion Detection - Digital Sensitivity | number | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Speaker - Volume | number | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Spotlight Intensity | number | Network | unknown | active | unknown | active |  |
| unknown | Tapo C200 - Stockroom Light Frequency | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Motion Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Move to Preset | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Night Vision | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Night Vision Switching | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Patrol Mode | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Person Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Light Frequency | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Motion Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Night Vision | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Person Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Pet Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Spotlight Intensity | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Vehicle Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Light Frequency | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Motion Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Night Vision | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Person Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Pet Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Spotlight Intensity | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Vehicle Detection | select | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Motion Detection | select | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Night Vision | select | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Night Vision Switching | select | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Person Detection | select | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Pet Detection | select | Network | unknown | active | unknown | active |  |
| unknown | Tapo C425 - North Wall Vehicle Detection | select | Network | unknown | active | unknown | active |  |
| unknown | CPU Speed | sensor | Network | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Tapo C200 - Stockroom Network SSID | sensor | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - East Wall Battery | sensor | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - South Wall Battery | sensor | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - South Wall Battery | sensor | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 East Wall Battery | sensor | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Battery | sensor | Network | unknown | active | unknown | active |  |
| unknown | TP-LinkHub Alarm | sensor | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | TP-LinkHub H100 Signal level | sensor | Network | unknown | active | unknown | active |  |
| unknown | Hue Bridge Automation: Coming home | switch | Network | unknown | active | unknown | active |  |
| unknown | Hue Bridge Automation: Leaving home | switch | Network | unknown | active | unknown | active |  |
| unknown | Hue Bridge Automation: Nightlight On Nightlight Off | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C200 - Stockroom Auto Track | switch | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Preset Patrol Mode | switch | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C200 - Stockroom Privacy | switch | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - East Wall Motion detection | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - East Wall Person detection | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - East Wall Tapo C420 East Wall | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - South Wall Motion detection | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - South Wall Person detection | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 - South Wall Privacy | switch | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C420 - South Wall Tapo C420 - South Wall | switch | Network | unknown | active | unknown | active |  |
| unknown | Tapo C420 East Wall Privacy | switch | Network | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Tapo C425 - North Wall Privacy | switch | Network | unknown | active | unknown | active |  |
| unknown | Emergency Button Dad Cloud connection | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Emergency Button Mum Cloud connection | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | M/Contact Sensor Cloud connection | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | M/Contact Sensor Door | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | M/Contact Sensor Door | binary_sensor | Parents Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Parents Room AC Filter clean required | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room AC Room occupied | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room Motion Sensor Connectivity | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room Motion Sensor Motion | binary_sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room AC Reset filter | button | Parents Room | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Parents Room AC | climate | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI | media_player | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI | media_player | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI | media_player | Parents Room | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | 55" QLED 4k AI Energy | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI Energy difference | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI Energy saved | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI Power | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI Power energy | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI TV channel | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | 55" QLED 4k AI TV channel name | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Light Sensor - 55" QLED 4k AI Brightness intensity | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Light Sensor - 55" QLED 4k AI Illuminance | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | M/Contact Sensor Signal level | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room AC Timer end time | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room Motion Sensor Battery voltage | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room Motion Sensor Humidity | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room Motion Sensor Temperature | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Sensibo Sky Plus Air conditioner mode | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Sensibo Sky Plus Cooling setpoint | sensor | Parents Room | unknown | active | unknown | active |  |
| unknown | Light Sensor - 55" QLED 4k AI | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | MainRoomLight Switch 1 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Master bedroom power point Socket 1 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Master bedroom power point Socket 2 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Master bedroom power point Socket 3 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Master bedroom power point Socket 4 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Master bedroom power point Socket 5 | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room AC Climate React | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Parents Room AC Timer | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Sensibo Sky Plus | switch | Parents Room | unknown | active | unknown | active |  |
| unknown | Aqara Roller Shade Driver E1 Configuration status | binary_sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Pump | binary_sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Presence Multi-Sensor FP300 Occupancy | binary_sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | R/Energy Monitor P110M Cloud connection | binary_sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M Overloaded | binary_sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Aqara Roller Shade Driver E1 Identify | button | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Presence Multi-Sensor FP300 Identify (1) | button | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Identify (2) | button | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Identify (3) | button | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Identify (4) | button | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Aqara Roller Shade Driver E1 | cover | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Ray Bedroom Switch Button 1 | event | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Ray Bedroom Switch Button 2 | event | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Ray Bedroom Switch Button 3 | event | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Ray Bedroom Switch Button 4 | event | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom | light | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | BedRoomLight Switch 1 | light | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | NightLight | light | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | NightLight | light | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | 55&quot; QLED 4k AI (QA55Q7FAAWXXY) | media_player | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Plants age | number | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Presence Multi-Sensor FP300 Sensitivity | number | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | R/Energy Monitor P110M Power protection | number | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | 55&quot; QLED 4k AI (QA55Q7FAAWXXY) | remote | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Amber bloom | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Baby's breath | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Blossom | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Concentrate | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Dreamy dusk | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Nature's colors | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Nightlight | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Nighttime | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Pensive | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Read | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Silverstone | scene | Ray Bedroom | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Bedroom Soho | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Bedroom Starlight | scene | Ray Bedroom | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Bedroom Suzuka | scene | Ray Bedroom | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Bedroom Vapor wave | scene | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Light brightness | select | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Light mode | select | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Aqara Roller Shade Driver E1 Battery | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Aqara Roller Shade Driver E1 Battery charge state | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Aqara Roller Shade Driver E1 Battery voltage | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | Presence Multi-Sensor FP300 Battery | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Battery type | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Battery voltage | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Humidity | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Illuminance | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Presence Multi-Sensor FP300 Temperature | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | R/Energy Monitor P110M Current | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M Current consumption | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M Signal level | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M This month's consumption | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M Today's consumption | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M Voltage | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Laptop/Energy Monitor/P110M Energy | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | R/Laptop/Energy Monitor/P110M Energy difference | sensor | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Ray Bedroom Switch Battery | sensor | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Power | switch | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Pump cycling | switch | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Energy Monitor P110M | switch | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | R/Laptop/Energy Monitor/P110M | switch | Ray Bedroom | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | LPH-SE DCD9 Light off | time | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | LPH-SE DCD9 Light on | time | Ray Bedroom | unknown | active | unknown | active |  |
| unknown | iPhone Presence | binary_sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Kiosk Mode | binary_sensor | unknown | unknown | active | unknown | active |  |
| unknown | Ai's iPhone | device_tracker | unknown | unknown | active | unknown | active |  |
| unknown | CasaRay iPad | device_tracker | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Deez | device_tracker | unknown | unknown | active | unknown | active |  |
| unknown | Deez | device_tracker | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad | device_tracker | unknown | unknown | active | unknown | active |  |
| unknown | Vinh's phone | device_tracker | unknown | unknown | active | unknown | active |  |
| unknown | BedlightSwitch button2 | event | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | BedlightSwitch button3 | event | unknown | unknown | active | unknown | active |  |
| unknown | BedlightSwitch button4 | event | unknown | unknown | active | unknown | active |  |
| unknown | BedlightSwitch main | event | unknown | unknown | active | unknown | active |  |
| unknown | Emergency Button Dad main | event | unknown | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Emergency Button Mum main | event | unknown | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | LivingroomSwitch button2 | event | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | LivingroomSwitch button3 | event | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | LivingroomSwitch button4 | event | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | LivingroomSwitch main | event | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Chinese Dashboard | input_boolean | unknown | unknown | active | unknown | active |  |
| unknown | Gas Bill Usage MJ | input_number | unknown | unknown | active | unknown | active |  |
| unknown | Family Location | input_select | unknown | unknown | active | unknown | active |  |
| unknown | Ai's iPhone | notify | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | CasaRay iPad | notify | unknown | unknown | active | unknown | active |  |
| unknown | Deez | notify | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Deez | notify | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Raymond's iPad | notify | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Vinh's phone | notify | unknown | unknown | unknown | unknown | active | state: unknown at time of verification |
| unknown | Ai Q Huang | person | unknown | unknown | active | unknown | active |  |
| unknown | Raymond Du. | person | unknown | unknown | active | unknown | active |  |
| unknown | Vinh Du | person | unknown | unknown | active | unknown | active |  |
| unknown | Ai's iPhone Battery Level | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Ai's iPhone Location permission | sensor | unknown | unknown | active | unknown | active |  |
| unknown | BedlightSwitch Battery | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Deez Raymond's iPhone Connection Type | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Deez Raymond's iPhone Distance | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Deez Raymond's iPhone Kiosk Brightness | sensor | unknown | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Deez Raymond's iPhone Kiosk Volume | sensor | unknown | unknown | unavailable | unknown | active | state: unavailable at time of verification |
| unknown | Deez Raymond's iPhone Location permission | sensor | unknown | unknown | active | unknown | active |  |
| unknown | LivingroomSwitch Battery | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Battery Level | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Battery State | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Connection Type | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Geocoded Location | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Kiosk Brightness | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Kiosk Volume | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Location permission | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad SSID | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Raymond's iPad Storage | sensor | unknown | unknown | active | unknown | active |  |
| unknown | sensor Cost | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Solar Power Display | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Vinh's phone Battery level | sensor | unknown | unknown | active | unknown | active |  |
| unknown | Shopping List | todo | unknown | unknown | active | unknown | active |  |
| unknown | Home | zone | unknown | unknown | active | unknown | active |  |
| unknown | Home | zone | unknown | unknown | active | unknown | active |  |

## Change log

- 2026-08-29 — Initial live validation pass. Populated table with 425 entities
  pulled from the Home Assistant `GetLiveContext` MCP tool (full unfiltered
  call, cross-checked with additional `domain`-filtered calls for `light`
  and `climate`, which returned matching counts of 26 and 1 respectively,
  confirming the full pull was not truncated). `entity_id` could not be
  captured because `GetLiveContext` does not expose it — every row shows
  `entity_id: unknown` pending a future pass with REST/WebSocket registry
  access. Domain breakdown: sensor 129, switch 53, binary_sensor 47, select
  33, scene 29, light 26, number 22, event 22, button 20, media_player 9,
  camera 6, device_tracker 6, notify 6, person 3, remote 2, time 2, zone 2,
  climate 1, cover 1, fan 1, input_boolean 1, input_number 1, input_select 1,
  todo 1, weather 1. Area breakdown (from `areas` field where present):
  Network 90, Living Room 73, Ray Bedroom 65, Parents Room 40, Dining 31,
  Energy 23, Kitchen 22, Garage 11, Backyard 10, Guest Room 6; 54 entities
  had no `areas` value in the live tool output (mostly device_tracker,
  notify, person, and standalone sensors/helpers not assigned to a room).
  144 entities were observed with `state: unavailable` or `state: unknown`
  at pull time (noted per-row); this does not necessarily mean disabled —
  it reflects a point-in-time snapshot (many are Tapo camera sub-entities
  and Hue scenes/lights that report unavailable/unknown transiently).
