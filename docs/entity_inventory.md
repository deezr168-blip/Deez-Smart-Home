# Entity Inventory

Status: **PARTIALLY VERIFIED — 425 live entities enumerated, entity_id column unresolved.**

This file is the source of truth for known Home Assistant entities, used to
validate live entity IDs before any automation/dashboard/script work
references them. Entity IDs must never be invented or guessed.

## Access verification pass — 2026-08-29

This session has live read access to the Home Assistant instance through
the `Home-Assistant` MCP connector's Assist-style tools
(`GetLiveContext`, `HassTurnOn`, `HassLightSet`, etc.), not through the
REST `/api/states` or WebSocket `config/*_registry/list` endpoints
originally planned for Stage 2 in this file. That matters because
`GetLiveContext` returns friendly `names`, `domain`, `state`, `areas`, and
`attributes` for each entity, but it does **not** return the entity's
`entity_id`. Every row below is a real entity confirmed live in this
installation, but the `entity_id` column could only be filled by guessing
from the friendly name — which this project's rule explicitly forbids, since
a wrong guess could reference (and control) the wrong device.

**What's needed to finish Stage 2 (fill in real `entity_id` values):**
either a Home Assistant Long-Lived Access Token with REST API access
(`GET /api/states` returns `entity_id` directly), or an MCP/tool connector
that exposes the entity/device/area registries over WebSocket
(`config/entity_registry/list`, `config/device_registry/list`,
`config/area_registry/list`). Until one of those is available, this file —
and any dashboard work that depends on exact entity IDs — stays blocked on
that specific gap, not on live access in general.

## Verified areas (from live data)

Network (90 entities, infra/cameras — not a physical room), Living Room (73),
Ray Bedroom (65), Parents Room (40), Dining (31), Energy (23), Kitchen (22),
Garage (11), Backyard (10), Guest Room (6).

## Verified domains (from live data)

sensor (129), switch (53), binary_sensor (47), select (33), scene (29),
light (26), number (22), event (22), button (20), media_player (9),
notify (6), device_tracker (6), camera (6), person (3), zone (2), time (2),
remote (2), weather (1), todo (1), input_select (1), input_number (1),
input_boolean (1), fan (1), cover (1), climate (1).

## Planned structure

Once entity_id resolution is unblocked, entities are recorded one per row:

| entity_id | friendly_name | domain | area | device | enabled | exposed_to_assist | status | notes |
|---|---|---|---|---|---|---|---|---|

Where `status` is one of:

- `active` — present, enabled, matches expected config
- `stale` — present in this doc but not seen live on last validation pass
- `renamed` — entity_id changed since last recorded (old ID noted)
- `disabled` — present in registry but disabled
- `hidden` — present but not exposed to Assist / hidden from dashboards
- `duplicate` — ambiguous device with more than one matching entity

## Live entity snapshot — 2026-08-29 (entity_id unresolved)

Pulled via `Home-Assistant` MCP `GetLiveContext` (Assist API), full sweep,
no domain/area filter. 425 entities across 10 areas. `entity_id` is
`_unresolved_` for every row per the blocker above — treat these as
confirmed-live friendly names only, not deploy-ready references.

| friendly_name | domain | area | device_class | unit | state | entity_id | status | notes |
|---|---|---|---|---|---|---|---|---|
| TP-LinkHub H100 Cloud connection | binary_sensor | Network | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| TP-LinkHub H100 Overheated | binary_sensor | Network | problem |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| eero Gateway WAN status | binary_sensor | Network | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| TP-LinkHub H100 Pair new device | button | Network |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Calibrate | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Manual Alarm Start | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Manual Alarm Stop | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Move Down | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Move Left | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Move Right | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Move Up | button | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Reboot | button | Network | restart |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Manual Alarm Start | button | Network |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Manual Alarm Stop | button | Network |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Reboot | button | Network | restart |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo H200 Pair new device | button | Network |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom HD Stream (Direct) | camera | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall HD Stream (Direct) | camera | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall HD Stream (Direct) | camera | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall HD Stream (Direct) | camera | Network |  |  | idle | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Floodlight (Timed) | light | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Floodlight (Timed) | light | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Floodlight (Timed) | light | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Floodlight (Timed) | light | Network |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| RingChime Volume | number | Network |  |  | '5.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Microphone - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Motion Detection - Digital Sensitivity | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Speaker - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Spotlight Intensity | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Microphone - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Motion Detection - Digital Sensitivity | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Speaker - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Microphone - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Motion Detection - Digital Sensitivity | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Speaker - Volume | number | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Microphone - Volume | number | Network |  |  | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Motion Detection - Digital Sensitivity | number | Network |  |  | '30' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Speaker - Volume | number | Network |  |  | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Spotlight Intensity | number | Network |  |  | '5' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Light Frequency | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Motion Detection | select | Network | motion_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Move to Preset | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Night Vision | select | Network | night_vision |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Night Vision Switching | select | Network | night_vision |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Patrol Mode | select | Network | patrol_mode |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Person Detection | select | Network | person_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Light Frequency | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Motion Detection | select | Network | motion_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Night Vision | select | Network | night_vision |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Person Detection | select | Network | person_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Pet Detection | select | Network | pet_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Spotlight Intensity | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Vehicle Detection | select | Network | vehicle_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Light Frequency | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Motion Detection | select | Network | motion_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Night Vision | select | Network | night_vision |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Person Detection | select | Network | person_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Pet Detection | select | Network | pet_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Spotlight Intensity | select | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Vehicle Detection | select | Network | vehicle_detection |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Motion Detection | select | Network | motion_detection |  | low | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Night Vision | select | Network | night_vision |  | Infrared Mode | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Night Vision Switching | select | Network | night_vision |  | auto | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Person Detection | select | Network | person_detection |  | low | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Pet Detection | select | Network | pet_detection |  | low | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Vehicle Detection | select | Network | vehicle_detection |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| CPU Speed | sensor | Network | frequency | GHz | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| TP-LinkHub Alarm | sensor | Network | enum |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| TP-LinkHub H100 Signal level | sensor | Network |  |  | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Network SSID | sensor | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - East Wall Battery | sensor | Network | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Battery | sensor | Network | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Battery | sensor | Network | battery | '%' | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Battery | sensor | Network | battery | '%' | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Battery | sensor | Network | battery | '%' | '29' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 'Hue Bridge Automation: Coming home' | switch | Network | switch |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 'Hue Bridge Automation: Leaving home' | switch | Network | switch |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 'Hue Bridge Automation: Nightlight On Nightlight Off' | switch | Network | switch |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Auto Track | switch | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Preset Patrol Mode | switch | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C200 - Stockroom Privacy | switch | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - East Wall Motion detection | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - East Wall Person detection | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - East Wall Tapo C420 East Wall | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Motion detection | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Person detection | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Privacy | switch | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 - South Wall Tapo C420 - South Wall | switch | Network |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C420 East Wall Privacy | switch | Network |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo C425 - North Wall Privacy | switch | Network |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| F/Contact Sensor Cloud connection | binary_sensor | Living Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| F/Contact Sensor Door | binary_sensor | Living Room | door |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| F/Contact Sensor Door | binary_sensor | Living Room | door |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Hue Hue Sensor Motion | binary_sensor | Living Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Motion | binary_sensor | Living Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Motion | binary_sensor | Living Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| RingRing Motion | binary_sensor | Living Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Live view | camera | Living Room |  |  | idle | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Ding | event | Living Room | doorbell |  | '2026-08-21T05:01:40.921+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Motion | event | Living Room | motion |  | '2026-08-29T21:07:23.351+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Switch Button 1 | event | Living Room | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Switch Button 2 | event | Living Room | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Switch Button 3 | event | Living Room | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Switch Button 4 | event | Living Room | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| RingRing main | event | Living Room | button |  | '2026-08-28T06:23:51.800+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier | fan | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Hue ambiance spot 1 | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Hue ambiance spot 1 | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Hue ambiance spot 3 | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Hue ambiance spot 4 | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Inner Left | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Inner Right | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Outter Left | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Outter Right | light | Living Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room | light | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room | light | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| '[TV] Samsung Q9 Series (65)' | media_player | Living Room |  |  | idle | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| '[TV] Samsung Q9 Series (65)' | media_player | Living Room | tv |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Samsung Q9 Series (65) | media_player | Living Room | tv |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Samsung Q9 Series (65) | media_player | Living Room | speaker |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| '[TV] Samsung Q9 Series (65)' | remote | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Bright | scene | Living Room |  |  | '2026-08-14T16:35:51.021009+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Concentrate | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Dimmed | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Energize | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Midwinter | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Nightlight | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Read | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Relax | scene | Living Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier Lamp | select | Living Room |  |  | high | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Power-on behavior | select | Living Room |  |  | last | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier Air quality | sensor | Living Room |  | CAQI | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier Odor sensor | sensor | Living Room |  |  | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM1 | sensor | Living Room | pm1 | μg/m³ | '5' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM1 health concern | sensor | Living Room | enum |  | good | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM10 | sensor | Living Room | pm10 | μg/m³ | '5' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM10 health concern | sensor | Living Room | enum |  | good | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM2.5 | sensor | Living Room | pm25 | μg/m³ | '5' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier PM2.5 health concern | sensor | Living Room | enum |  | good | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| F/Contact Sensor Signal level | sensor | Living Room |  |  | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Battery | sensor | Living Room | battery | '%' | '21' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Last activity | sensor | Living Room | timestamp |  | '2026-08-30T07:07:22+10:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Hue Hue Sensor Battery | sensor | Living Room | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Hue Hue Sensor Illuminance | sensor | Living Room | illuminance | lx | '34' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Hue Hue Sensor Temperature | sensor | Living Room | temperature | °C | '18.8' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Battery | sensor | Living Room | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Illuminance | sensor | Living Room | illuminance | lx | '37' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Temperature | sensor | Living Room | temperature | °C | '18.8' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Switch Battery | sensor | Living Room | battery | '%' | '53' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living room Illuminance | sensor | Living Room | illuminance | lx | '37' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| RingRing Battery | sensor | Living Room | battery | '%' | '21' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Samsung Q9 Series (65) TV channel | sensor | Living Room |  |  | '' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Samsung Q9 Series (65) TV channel name | sensor | Living Room |  |  | 9Ur5IzDKqV.TizenYouTube | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Air purifier | switch | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door In-home chime | switch | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Front Door Motion detection | switch | Living Room |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Socket 1 | switch | Living Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Socket 2 | switch | Living Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Socket 3 | switch | Living Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Socket 4 | switch | Living Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Genio Power Board with USB-LivingRoom Socket 5 | switch | Living Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Light sensor enabled | switch | Living Room | switch |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Living Room Motion Sensor Motion sensor enabled | switch | Living Room | switch |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 Configuration status | binary_sensor | Ray Bedroom | problem |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Pump | binary_sensor | Ray Bedroom | running |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Occupancy | binary_sensor | Ray Bedroom | occupancy |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Cloud connection | binary_sensor | Ray Bedroom | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Overloaded | binary_sensor | Ray Bedroom | problem |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 Identify | button | Ray Bedroom | identify |  | '2026-08-15T16:47:24.535859+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Identify (1) | button | Ray Bedroom | identify |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Identify (2) | button | Ray Bedroom | identify |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Identify (3) | button | Ray Bedroom | identify |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Identify (4) | button | Ray Bedroom | identify |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 | cover | Ray Bedroom | shade |  | open | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ray Bedroom Switch Button 1 | event | Ray Bedroom | button |  | '2026-08-29T17:13:23.734+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ray Bedroom Switch Button 2 | event | Ray Bedroom | button |  | '2026-07-24T17:56:15.603+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ray Bedroom Switch Button 3 | event | Ray Bedroom | button |  | '2026-08-26T16:03:15.101+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ray Bedroom Switch Button 4 | event | Ray Bedroom | button |  | '2026-08-29T17:19:44.707+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedRoomLight Switch 1 | light | Ray Bedroom |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom | light | Ray Bedroom |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| NightLight | light | Ray Bedroom |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| NightLight | light | Ray Bedroom |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55&quot; QLED 4k AI (QA55Q7FAAWXXY) | media_player | Ray Bedroom | tv |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Plants age | number | Ray Bedroom |  | d | '58' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Sensitivity | number | Ray Bedroom |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Power protection | number | Ray Bedroom |  |  | '2136' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55&quot; QLED 4k AI (QA55Q7FAAWXXY) | remote | Ray Bedroom |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Amber bloom | scene | Ray Bedroom |  |  | '2026-08-14T16:36:00.727360+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Baby's breath | scene | Ray Bedroom |  |  | '2026-08-14T16:36:03.067639+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Blossom | scene | Ray Bedroom |  |  | '2026-08-14T16:36:07.329159+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Concentrate | scene | Ray Bedroom |  |  | '2026-08-14T16:36:05.881515+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Dreamy dusk | scene | Ray Bedroom |  |  | '2026-08-14T16:36:12.609951+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Nature's colors | scene | Ray Bedroom |  |  | '2026-08-14T16:36:11.265968+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Nightlight | scene | Ray Bedroom |  |  | '2026-08-14T16:36:08.401613+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Nighttime | scene | Ray Bedroom |  |  | '2026-08-14T16:36:09.417815+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Pensive | scene | Ray Bedroom |  |  | '2026-08-08T15:17:52.698273+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Read | scene | Ray Bedroom |  |  | '2026-08-08T15:17:51.941886+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Silverstone | scene | Ray Bedroom |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Soho | scene | Ray Bedroom |  |  | '2026-08-08T15:17:50.089018+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Starlight | scene | Ray Bedroom |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Suzuka | scene | Ray Bedroom |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Vapor wave | scene | Ray Bedroom |  |  | '2026-08-08T15:17:55.612180+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Light brightness | select | Ray Bedroom |  |  | high | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Light mode | select | Ray Bedroom |  |  | vegetable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 Battery | sensor | Ray Bedroom | battery | '%' | '70' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 Battery charge state | sensor | Ray Bedroom | enum |  | not_charging | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Aqara Roller Shade Driver E1 Battery voltage | sensor | Ray Bedroom | voltage | V | '3.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Battery | sensor | Ray Bedroom | battery | '%' | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Battery type | sensor | Ray Bedroom |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Battery voltage | sensor | Ray Bedroom | voltage | V | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Humidity | sensor | Ray Bedroom | humidity | '%' | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Illuminance | sensor | Ray Bedroom | illuminance | lx | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Presence Multi-Sensor FP300 Temperature | sensor | Ray Bedroom | temperature | °C | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Current | sensor | Ray Bedroom | current | A | '0.21' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Current consumption | sensor | Ray Bedroom | power | W | '31.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Signal level | sensor | Ray Bedroom |  |  | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M This month's consumption | sensor | Ray Bedroom | energy | kWh | '12.407' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Today's consumption | sensor | Ray Bedroom | energy | kWh | '0.189' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M Voltage | sensor | Ray Bedroom | voltage | V | '230.9' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Laptop/Energy Monitor/P110M Energy | sensor | Ray Bedroom | energy | kWh | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Laptop/Energy Monitor/P110M Energy difference | sensor | Ray Bedroom | energy | kWh | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ray Bedroom Switch Battery | sensor | Ray Bedroom | battery | '%' | '90' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Power | switch | Ray Bedroom |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Pump cycling | switch | Ray Bedroom |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Energy Monitor P110M | switch | Ray Bedroom |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| R/Laptop/Energy Monitor/P110M | switch | Ray Bedroom |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Light off | time | Ray Bedroom |  |  | '18:00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LPH-SE DCD9 Light on | time | Ray Bedroom |  |  | 06:00:00 | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Emergency Button Dad Cloud connection | binary_sensor | Parents Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Emergency Button Mum Cloud connection | binary_sensor | Parents Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| M/Contact Sensor Cloud connection | binary_sensor | Parents Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| M/Contact Sensor Door | binary_sensor | Parents Room | door |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| M/Contact Sensor Door | binary_sensor | Parents Room | door |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Filter clean required | binary_sensor | Parents Room | problem |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Room occupied | binary_sensor | Parents Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room Motion Sensor Connectivity | binary_sensor | Parents Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room Motion Sensor Motion | binary_sensor | Parents Room | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Reset filter | button | Parents Room |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC | climate | Parents Room |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI | media_player | Parents Room |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI | media_player | Parents Room | tv |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI | media_player | Parents Room | speaker |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI Energy | sensor | Parents Room | energy | kWh | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI Energy difference | sensor | Parents Room | energy | kWh | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI Energy saved | sensor | Parents Room | energy | kWh | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI Power | sensor | Parents Room | power | W | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI Power energy | sensor | Parents Room | energy | kWh | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI TV channel | sensor | Parents Room |  |  | '' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| 55" QLED 4k AI TV channel name | sensor | Parents Room |  |  | 9Ur5IzDKqV.TizenYouTube | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Light Sensor - 55" QLED 4k AI Brightness intensity | sensor | Parents Room |  | level | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Light Sensor - 55" QLED 4k AI Illuminance | sensor | Parents Room | illuminance | lx | '0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| M/Contact Sensor Signal level | sensor | Parents Room |  |  | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Timer end time | sensor | Parents Room | timestamp |  | '2025-03-10T14:21:21+11:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room Motion Sensor Battery voltage | sensor | Parents Room | voltage | V | '2994' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room Motion Sensor Humidity | sensor | Parents Room | humidity | '%' | '75.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room Motion Sensor Temperature | sensor | Parents Room | temperature | °C | '16.3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Sensibo Sky Plus Air conditioner mode | sensor | Parents Room |  |  | fanOnly | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Sensibo Sky Plus Cooling setpoint | sensor | Parents Room | temperature | °C | '19.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Light Sensor - 55" QLED 4k AI | switch | Parents Room |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| MainRoomLight Switch 1 | switch | Parents Room | outlet |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Master bedroom power point Socket 1 | switch | Parents Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Master bedroom power point Socket 2 | switch | Parents Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Master bedroom power point Socket 3 | switch | Parents Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Master bedroom power point Socket 4 | switch | Parents Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Master bedroom power point Socket 5 | switch | Parents Room | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Climate React | switch | Parents Room | switch |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Parents Room AC Timer | switch | Parents Room | switch |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Sensibo Sky Plus | switch | Parents Room |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Hue Sensor Motion | binary_sensor | Dining | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Motion | binary_sensor | Dining | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Sensor group Motion | binary_sensor | Dining | motion |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder Restart | button | Dining | restart |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder | camera | Dining |  |  | idle | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Corridor 1 | light | Dining |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Corridor 2 | light | Dining |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining | light | Dining |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining | light | Dining |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Light Left | light | Dining |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Light Right | light | Dining |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder Indicator light | light | Dining |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder Volume | number | Dining |  | '%' | '1.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Concentrate | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Energize | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Midwinter | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Nightlight | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Read | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Relax | scene | Dining |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder Motion detection sensitivity | select | Dining |  |  | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Smart Pet Feeder Night vision | select | Dining |  |  | '0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Hue Sensor Battery | sensor | Dining | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Hue Sensor Illuminance | sensor | Dining | illuminance | lx | '152' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Bedroom Hue Sensor Temperature | sensor | Dining | temperature | °C | '16.4' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Battery | sensor | Dining | battery | '%' | '100' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Illuminance | sensor | Dining | illuminance | lx | '152' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Temperature | sensor | Dining | temperature | °C | '16.4' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Sensor group Illuminance | sensor | Dining | illuminance | lx | '37' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Light sensor enabled | switch | Dining | switch |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dining Room Motion Sensor Motion sensor enabled | switch | Dining | switch |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Dinning light Switch 1 | switch | Dining | outlet |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Electricity Maps CO2 intensity | sensor | Energy |  | gCO2eq/kWh | '547.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Electricity Maps Grid fossil fuel percentage | sensor | Energy |  | '%' | '65.75' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) AC current | sensor | Energy | current | A | '1.99' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) AC power | sensor | Energy | power | W | '461' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) DC current | sensor | Energy | current | A | '1.51' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) DC voltage | sensor | Energy | voltage | V | '424' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) Energy day | sensor | Energy | energy | Wh | '194' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) Energy year | sensor | Energy | energy | Wh | '4571742' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Primo 5.0-1 (1) Total energy | sensor | Energy | energy | Wh | '48409600' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated energy production - next hour | sensor | Energy | energy | kWh | '0.4' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated energy production - remaining today | sensor | Energy | energy | kWh | '5.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated energy production - this hour | sensor | Energy | energy | kWh | '0.2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated energy production - today | sensor | Energy | energy | kWh | '5.5' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated energy production - tomorrow | sensor | Energy | energy | kWh | '5.2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Estimated power production - now | sensor | Energy | power | W | '336' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Highest power peak time - today | sensor | Energy | timestamp |  | '2026-08-30T12:00:00+10:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar production forecast Highest power peak time - tomorrow | sensor | Energy | timestamp |  | '2026-08-31T13:00:00+10:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| SolarNet CO₂ factor | sensor | Energy |  | kg/kWh | '0.53' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| SolarNet Grid export tariff | sensor | Energy |  | AUD/kWh | '0.015' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| SolarNet Grid import tariff | sensor | Energy |  | AUD/kWh | '0.2880' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| SolarNet Meter mode | sensor | Energy |  |  | produce-only | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| SolarNet Power photovoltaics | sensor | Energy | power | W | '458' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Forecast Home | weather | Energy |  |  | cloudy | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Bot P100 Cloud connection | binary_sensor | Kitchen | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Coffee P100 Cloud connection | binary_sensor | Kitchen | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Motion Sensor Cloud connection | binary_sensor | Kitchen | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Motion Sensor Motion | binary_sensor | Kitchen | motion |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Motion Sensor Motion | binary_sensor | Kitchen | motion |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Motion Sensor Occupancy | binary_sensor | Kitchen | occupancy |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Smart Button Cloud connection | binary_sensor | Kitchen | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Top P100 Cloud connection | binary_sensor | Kitchen | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LG-Fridge Door | binary_sensor | Kitchen | door |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Smart Button main | event | Kitchen | button |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LG-Fridge freezer temperature | number | Kitchen |  | °C | '-18' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LG-Fridge fridge temperature | number | Kitchen |  | °C | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Bot P100 Signal level | sensor | Kitchen |  |  | '2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Coffee P100 Signal level | sensor | Kitchen |  |  | '2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Top P100 Signal level | sensor | Kitchen |  |  | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Bot P100 | switch | Kitchen |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Bot P100 | switch | Kitchen |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Coffee P100 | switch | Kitchen |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Coffee P100 | switch | Kitchen |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Top P100 | switch | Kitchen |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| K/Top P100 | switch | Kitchen |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LG-Fridge Express mode | switch | Kitchen | switch |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Cloud connection | binary_sensor | Garage | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Overheated | binary_sensor | Garage | problem |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Overloaded | binary_sensor | Garage | problem |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Power protection | number | Garage |  |  | '2149' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Current | sensor | Garage | current | A | '0.00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Current consumption | sensor | Garage | power | W | '0.0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Signal level | sensor | Garage |  |  | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M This month's consumption | sensor | Garage | energy | kWh | '13.474' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Today's consumption | sensor | Garage | energy | kWh | '0.000' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M Voltage | sensor | Garage | voltage | V | '232.7' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Monitor Freezer P110M | switch | Garage |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Contact Sensor Cloud connection | binary_sensor | Backyard | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Contact Sensor Door | binary_sensor | Backyard | door |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Contact Sensor Door | binary_sensor | Backyard | door |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo_C200_5C35 Motion | binary_sensor | Backyard | motion |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo_Camera Motion | binary_sensor | Backyard | motion |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Contact Sensor Signal level | sensor | Backyard |  |  | '1' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Freezer/EnergyMonitor/P110M Energy | sensor | Backyard | energy | kWh | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Freezer/EnergyMonitor/P110M Energy difference | sensor | Backyard | energy | kWh | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Tapo_Camera Battery | sensor | Backyard | battery | '%' | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| B/Freezer/EnergyMonitor/P110M | switch | Backyard |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Printer P100 Cloud connection | binary_sensor | Guest Room | connectivity |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Kogan Tv | light | Guest Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Pogo | media_player | Guest Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Printer P100 Signal level | sensor | Guest Room |  |  | '3' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Printer P100 | switch | Guest Room |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| G/Printer P100 | switch | Guest Room |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Kiosk Mode | binary_sensor | (no area) |  |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| iPhone Presence | binary_sensor | (no area) | presence |  | 'on' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ai’s iPhone | device_tracker | (no area) |  |  | not_home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| CasaRay iPad | device_tracker | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez | device_tracker | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez | device_tracker | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad | device_tracker | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Vinh’s phone | device_tracker | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedlightSwitch button2 | event | (no area) | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedlightSwitch button3 | event | (no area) | button |  | '2026-08-26T16:03:15.650+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedlightSwitch button4 | event | (no area) | button |  | '2026-08-29T17:19:44.995+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedlightSwitch main | event | (no area) | button |  | '2026-08-29T17:13:24.091+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Emergency Button Dad main | event | (no area) | button |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Emergency Button Mum main | event | (no area) | button |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LivingroomSwitch button2 | event | (no area) | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LivingroomSwitch button3 | event | (no area) | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LivingroomSwitch button4 | event | (no area) | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LivingroomSwitch main | event | (no area) | button |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Chinese Dashboard | input_boolean | (no area) |  |  | 'off' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Gas Bill Usage MJ | input_number | (no area) |  | MJ | '9437.04' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Family Location | input_select | (no area) |  |  | Raymond Du | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ai’s iPhone | notify | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| CasaRay iPad | notify | (no area) |  |  | '2026-08-14T17:30:43.775571+00:00' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez | notify | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez | notify | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad | notify | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Vinh’s phone | notify | (no area) |  |  | unknown | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ai Q Huang | person | (no area) |  |  | not_home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond Du. | person | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Vinh Du | person | (no area) |  |  | home | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ai’s iPhone Battery Level | sensor | (no area) | battery | '%' | '50' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Ai’s iPhone Location permission | sensor | (no area) |  |  | Authorized when in use | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| BedlightSwitch Battery | sensor | (no area) | battery | '%' | '90' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez Raymond’s iPhone Connection Type | sensor | (no area) |  |  | Wi-Fi | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez Raymond’s iPhone Distance | sensor | (no area) |  | m | '22' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez Raymond’s iPhone Kiosk Brightness | sensor | (no area) |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez Raymond’s iPhone Kiosk Volume | sensor | (no area) |  |  | unavailable | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Deez Raymond’s iPhone Location permission | sensor | (no area) |  |  | Authorized Always | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| LivingroomSwitch Battery | sensor | (no area) | battery | '%' | '53' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Battery Level | sensor | (no area) | battery | '%' | '90' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Battery State | sensor | (no area) |  |  | Charging | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Connection Type | sensor | (no area) |  |  | Wi-Fi | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Geocoded Location | sensor | (no area) |  |  | '12 Edmond St | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Kiosk Brightness | sensor | (no area) |  |  | '85' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Kiosk Volume | sensor | (no area) |  |  | '25' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Location permission | sensor | (no area) |  |  | Authorized Always | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad SSID | sensor | (no area) |  |  | homeAI | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Raymond’s iPad Storage | sensor | (no area) |  | '% available' | '21.96' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Solar Power Display | sensor | (no area) |  |  | 461 W | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Vinh’s phone Battery level | sensor | (no area) | battery | '%' | '91' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| sensor Cost | sensor | (no area) | monetary | AUD | '5.36059216' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Shopping List | todo | (no area) |  |  | '0' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Home | zone | (no area) |  |  | '2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |
| Home | zone | (no area) |  |  | '2' | _unresolved_ | active (id unresolved) | seen via Assist GetLiveContext, 2026-08-29 |

## Change log

- 2026-08-29 — First live access pass via `Home-Assistant` MCP connector
  (Assist API / `GetLiveContext`). Enumerated 425 live entities across 10
  areas (see snapshot table above). Could not resolve real `entity_id`
  values — the Assist API exposes friendly names only, not entity_id — so
  no `entity_id` was recorded or guessed for any row. This blocks building
  `dashboards/deez_smart_home.yaml` with real entity references, since the
  project rule is that entity IDs must never be invented or guessed. Next
  step: get REST `/api/states` (via a Long-Lived Access Token) or
  WebSocket registry access, re-run this pass, and fill in `entity_id`.
