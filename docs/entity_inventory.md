# Home Assistant Entity Inventory

This document is a factual inventory of entities discovered by directly
inspecting the **live, connected Home Assistant instance** via the Home
Assistant MCP connector's `GetLiveContext` tool. Nothing in this file is
invented — every entity listed here was returned by a real live read.

- **Source:** `mcp__Home_Assistant__GetLiveContext` (no filters — full context)
- **Snapshot taken:** 2026-08-21
- **Total entities returned:** 430

## Important limitation: no entity IDs available

`GetLiveContext` returns **friendly names, domain, state, area, and partial
attributes only** — it does **not** return `entity_id`, `unique_id`,
`device_id`, or integration/platform information. This means:

- This inventory is a snapshot of **what exists and its current state**,
  not a source of `entity_id` strings that can be safely referenced in
  automations, scripts, or dashboards.
- Before writing any automation/script/dashboard YAML that references a
  specific entity, its real `entity_id` must be confirmed separately (e.g.
  via the HA entity registry, Developer Tools → States, or a REST/WebSocket
  API call) — never guessed from the friendly name here.
- Several friendly names are ambiguous or duplicated with no way to
  distinguish the underlying entities from this data alone (see
  "Duplicates and ambiguities" below, and `docs/live_ha_blockers.md`).

## Summary by domain

| Domain | Count |
|---|---|
| sensor | 129 |
| switch | 60 |
| binary_sensor | 47 |
| select | 33 |
| scene | 29 |
| light | 25 |
| event | 22 |
| number | 22 |
| button | 20 |
| media_player | 9 |
| device_tracker | 6 |
| notify | 6 |
| camera | 6 |
| person | 3 |
| remote | 2 |
| zone | 2 |
| time | 2 |
| fan | 1 |
| cover | 1 |
| input_boolean | 1 |
| input_select | 1 |
| weather | 1 |
| climate | 1 |
| todo | 1 |
| **Total** | **430** |

State flags: **74 entities `unavailable`**, **49 entities `unknown`** at
snapshot time (see "Unavailable / unknown clusters" below).

## Areas

10 distinct areas appear in the data. "Network" and "Energy" are
organizational groupings (networking gear; energy/solar monitoring), not
physical rooms. **71 of 430 entities have no area assigned.**

| Area | Entities tagged |
|---|---|
| Network | 96 |
| Living Room | 64 |
| Ray Bedroom | 61 |
| Parents Room | 39 |
| Dining | 27 |
| Energy | 23 |
| Kitchen | 22 |
| Garage | 11 |
| Backyard | 10 |
| Guest Room | 6 |
| *(no area)* | 71 |

No area literally named "Bedroom" (generic), "Bathroom", "Office", or
"Stockroom" exists in the `areas` field, even though some device *names*
reference "Stockroom" (those devices are tagged area `Network` instead —
flagged below).

## Entities by domain

Reproduced as returned by the live read: `name — state [area]`, plus
attributes when present. `[NO AREA]` means the entity had no `areas` field.

### climate (1)
- Parents Room AC — `off` [Parents Room] (current_temperature=20.5)

### cover (1)
- Aqara Roller Shade Driver E1 — `closed` [Ray Bedroom] (current_position=0, device_class=shade)

### fan (1)
- Air purifier — `on` [Living Room]

### weather (1)
- Forecast Home — `cloudy` [Energy] (temperature=12.9°C, humidity=74)

### input_boolean (1)
- Chinese Dashboard — `off` [NO AREA]

### input_select (1)
- Family Location — `Raymond Du` [NO AREA]

### todo (1)
- Shopping List — `0` [NO AREA]

### person (3)
- Ai Q Huang — `not_home` [NO AREA]
- Raymond Du. — `not_home` [NO AREA] *(literal trailing period in name)*
- Vinh Du — `home` [NO AREA]

### device_tracker (6)
- Ai's iPhone — `not_home` [NO AREA]
- CasaRay iPad — `unknown` [NO AREA]
- Deez — `not_home` [NO AREA] *(duplicate row, identical)*
- Deez — `not_home` [NO AREA] *(duplicate row, identical)*
- Raymond's iPad — `home` [NO AREA]
- Vinh's phone — `home` [NO AREA]

### notify (6)
- Ai's iPhone — `unknown` [NO AREA]
- CasaRay iPad — timestamp state [NO AREA]
- Deez — `unknown` [NO AREA] *(duplicate row)*
- Deez — `unknown` [NO AREA] *(duplicate row)*
- Raymond's iPad — `unknown` [NO AREA]
- Vinh's phone — `unknown` [NO AREA]

### zone (2)
- Home — `1` [NO AREA] *(duplicate row, identical)*
- Home — `1` [NO AREA] *(duplicate row, identical)*

### camera (6)
- Front Door Live view — `idle` [Living Room]
- Smart Pet Feeder — `idle` [Dining]
- Tapo C200 - Stockroom HD Stream (Direct) — `idle` [Network]
- Tapo C420 - South Wall HD Stream (Direct) — `idle` [Network]
- Tapo C420 East Wall HD Stream (Direct) — `idle` [Network]
- Tapo C425 - North Wall HD Stream (Direct) — `idle` [Network]

### media_player (9)
- 55" QLED 4k AI — `idle` [Parents Room] (speaker, volume=1.0)
- 55" QLED 4k AI — `off` [Parents Room]
- 55" QLED 4k AI — `off` [Parents Room] (tv)
- 55&amp;quot; QLED 4k AI (QA55Q7FAAWXXY) — `off` [Ray Bedroom] (tv) *(HTML-entity artifact in name)*
- Pogo — `unavailable` [Guest Room]
- Samsung Q9 Series (65) — `idle` [Living Room] (speaker, volume=0.18)
- Samsung Q9 Series (65) — `on` [Living Room] (tv, volume=0.18)
- [TV] Samsung Q9 Series (65) — `idle` [Living Room] (volume=0.18)
- [TV] Samsung Q9 Series (65) — `on` [Living Room] (tv, volume=0.18)

### remote (2)
- 55&amp;quot; QLED 4k AI (QA55Q7FAAWXXY) — `off` [Ray Bedroom]
- [TV] Samsung Q9 Series (65) — `on` [Living Room]

### time (2)
- LPH-SE DCD9 Light off — `18:00:00` [Ray Bedroom]
- LPH-SE DCD9 Light on — `06:00:00` [Ray Bedroom]

### light (25)
- Bedroom — `on` [Ray Bedroom] (brightness=255)
- Corridor 1 — `unavailable` [Dining]
- Corridor 2 — `unavailable` [Dining]
- Dining — `on` [Dining] (brightness=255) *(duplicate row)*
- Dining — `on` [Dining] (brightness=255) *(duplicate row)*
- Dining Light Left — `unavailable` [Dining]
- Dining Light Right — `unavailable` [Dining]
- Hue ambiance spot 1 — `unavailable` [NO AREA] *(duplicate row)*
- Hue ambiance spot 1 — `unavailable` [NO AREA] *(duplicate row)*
- Hue ambiance spot 3 — `unavailable` [NO AREA]
- Hue ambiance spot 4 — `unavailable` [NO AREA]
- Kogan Tv — `unavailable` [Guest Room]
- Living Room Inner Left — `unavailable` [Living Room]
- Living Room Inner Right — `unavailable` [Living Room]
- Living Room Outter Left — `unavailable` [Living Room]
- Living Room Outter Right — `unavailable` [Living Room]
- Living room — `on` [Living Room] (brightness=255) *(duplicate row)*
- Living room — `on` [Living Room] (brightness=255) *(duplicate row)*
- NightLight — `on` [Ray Bedroom] (brightness=255)
- NightLight — `on` [NO AREA] (brightness=255) *(same name, different area — likely a distinct entity)*
- Smart Pet Feeder Indicator light — `on` [Dining]
- Tapo C200 - Stockroom Floodlight (Timed) — `off` [Network]
- Tapo C420 - South Wall Floodlight (Timed) — `off` [Network]
- Tapo C420 East Wall Floodlight (Timed) — `off` [Network]
- Tapo C425 - North Wall Floodlight (Timed) — `off` [Network]

### switch (60)
- AdGuard Home Filtering — `on` [Network]
- AdGuard Home Parental control — `off` [Network]
- AdGuard Home Protection — `on` [Network]
- AdGuard Home Query log — `on` [Network]
- AdGuard Home Safe browsing — `off` [Network]
- AdGuard Home Safe search — `on` [Network]
- Air purifier — `on` [Living Room]
- B/Freezer/EnergyMonitor/P110M — `unavailable` [Backyard]
- BedRoomLight Switch 1 — `off` [Ray Bedroom] (outlet)
- Dining Room Motion Sensor Light sensor enabled — `on` [Dining]
- Dining Room Motion Sensor Motion sensor enabled — `on` [Dining]
- Dinning light Switch 1 — `on` [Dining] (outlet)
- Front Door In-home chime — `on` [Living Room]
- Front Door Motion detection — `on` [Living Room]
- G/Monitor Freezer P110M — `on` [Garage]
- G/Printer P100 — `off` [Guest Room]
- G/Printer P100 — `unavailable` [Guest Room] *(duplicate name, differing state)*
- Genio Power Board with USB-LivingRoom Socket 1 — `on` [Living Room] (outlet)
- Genio Power Board with USB-LivingRoom Socket 2 — `on` [Living Room] (outlet)
- Genio Power Board with USB-LivingRoom Socket 3 — `on` [Living Room] (outlet)
- Genio Power Board with USB-LivingRoom Socket 4 — `on` [Living Room] (outlet)
- Genio Power Board with USB-LivingRoom Socket 5 — `on` [Living Room] (outlet)
- Hue Bridge Automation: Coming home — `off` [Network]
- Hue Bridge Automation: Leaving home — `off` [Network]
- Hue Bridge Automation: Nightlight On Nightlight Off — `on` [Network]
- K/Bot P100 — `on` [Kitchen] *(duplicate name, differing state)*
- K/Bot P100 — `unavailable` [Kitchen]
- K/Coffee P100 — `on` [Kitchen] *(duplicate name, differing state)*
- K/Coffee P100 — `unavailable` [Kitchen]
- K/Top P100 — `on` [Kitchen] *(duplicate name, differing state)*
- K/Top P100 — `unavailable` [Kitchen]
- LG-Fridge Express mode — `off` [Kitchen]
- LPH-SE DCD9 Power — `on` [Ray Bedroom]
- LPH-SE DCD9 Pump cycling — `on` [Ray Bedroom]
- Light Sensor - 55" QLED 4k AI — `off` [Parents Room]
- Living Room Motion Sensor Light sensor enabled — `on` [Living Room]
- Living Room Motion Sensor Motion sensor enabled — `on` [Living Room]
- MainRoomLight Switch 1 — `off` [Parents Room] (outlet)
- Master bedroom power point Socket 1 — `on` [Parents Room] (outlet)
- Master bedroom power point Socket 2 — `on` [Parents Room] (outlet)
- Master bedroom power point Socket 3 — `on` [Parents Room] (outlet)
- Master bedroom power point Socket 4 — `on` [Parents Room] (outlet)
- Master bedroom power point Socket 5 — `on` [Parents Room] (outlet)
- Parents Room AC Climate React — `off` [Parents Room]
- Parents Room AC Timer — `off` [Parents Room]
- R/Energy Monitor P110M — `on` [Ray Bedroom]
- R/Laptop/Energy Monitor/P110M — `unavailable` [NO AREA]
- Sensibo Sky Plus — `off` [Parents Room]
- Tapo C200 - Stockroom Auto Track — `on` [Network]
- Tapo C200 - Stockroom Preset Patrol Mode — `off` [Network]
- Tapo C200 - Stockroom Privacy — `off` [Network]
- Tapo C420 - East Wall Motion detection — `on` [Network]
- Tapo C420 - East Wall Person detection — `on` [Network]
- Tapo C420 - East Wall Tapo C420 East Wall — `on` [Network] *(malformed/duplicated name)*
- Tapo C420 - South Wall Motion detection — `on` [Network]
- Tapo C420 - South Wall Person detection — `on` [Network]
- Tapo C420 - South Wall Privacy — `unavailable` [Network]
- Tapo C420 - South Wall Tapo C420 - South Wall — `on` [Network] *(malformed/duplicated name)*
- Tapo C420 East Wall Privacy — `off` [Network]
- Tapo C425 - North Wall Privacy — `off` [Network]

### binary_sensor (47)
- Aqara Roller Shade Driver E1 Configuration status — `off` [Ray Bedroom] (problem)
- B/Contact Sensor Cloud connection — `on` [Backyard] (connectivity)
- B/Contact Sensor Door — `off` [Backyard] (door)
- B/Contact Sensor Door — `unavailable` [Backyard] (door) *(duplicate name)*
- Bedroom Hue Sensor Motion — `off` [NO AREA] (motion)
- Dining Room Motion Sensor Motion — `off` [Dining] (motion)
- Emergency Button Dad Cloud connection — `on` [Parents Room] (connectivity)
- Emergency Button Mum Cloud connection — `on` [Parents Room] (connectivity)
- F/Contact Sensor Cloud connection — `on` [Living Room] (connectivity)
- F/Contact Sensor Door — `off` [Living Room] (door)
- F/Contact Sensor Door — `unavailable` [NO AREA] (door) *(duplicate name)*
- G/Monitor Freezer P110M Cloud connection — `on` [Garage] (connectivity)
- G/Monitor Freezer P110M Overheated — `unavailable` [Garage] (problem)
- G/Monitor Freezer P110M Overloaded — `off` [Garage] (problem)
- G/Printer P100 Cloud connection — `on` [Guest Room] (connectivity)
- K/Bot P100 Cloud connection — `on` [Kitchen] (connectivity)
- K/Coffee P100 Cloud connection — `on` [Kitchen] (connectivity)
- K/Motion Sensor Cloud connection — `on` [Kitchen] (connectivity)
- K/Motion Sensor Motion — `off` [Kitchen] (motion) *(duplicate name)*
- K/Motion Sensor Motion — `unavailable` [Kitchen] (motion)
- K/Motion Sensor Occupancy — `off` [Kitchen] (occupancy)
- K/Smart Button Cloud connection — `on` [Kitchen] (connectivity)
- K/Top P100 Cloud connection — `on` [Kitchen] (connectivity)
- LG-Fridge Door — `off` [Kitchen] (door)
- LPH-SE DCD9 Pump — `on` [Ray Bedroom] (running)
- Living Hue Hue Sensor Motion — `off` [NO AREA] (motion)
- Living Room Motion Sensor Motion — `off` [Living Room] (motion)
- Living room Motion — `off` [Living Room] (motion)
- M/Contact Sensor Cloud connection — `on` [Parents Room] (connectivity)
- M/Contact Sensor Door — `off` [Parents Room] (door)
- M/Contact Sensor Door — `unavailable` [NO AREA] (door) *(duplicate name)*
- Parents Room AC Filter clean required — `off` [Parents Room] (problem)
- Parents Room AC Room occupied — `on` [Parents Room] (motion)
- Parents Room Motion Sensor Connectivity — `on` [Parents Room] (connectivity)
- Parents Room Motion Sensor Motion — `off` [Parents Room] (motion)
- Presence Multi-Sensor FP300 Occupancy — `unavailable` [Ray Bedroom] (occupancy)
- R/Energy Monitor P110M Cloud connection — `on` [Ray Bedroom] (connectivity)
- R/Energy Monitor P110M Overloaded — `off` [Ray Bedroom] (problem)
- Raymond's iPad Kiosk Mode — `on` [NO AREA]
- RingRing Motion — `off` [Living Room] (motion)
- Sensor group Motion — `off` [Dining] (motion)
- TP-LinkHub H100 Cloud connection — `on` [Network] (connectivity)
- TP-LinkHub H100 Overheated — `off` [Network] (problem)
- Tapo_C200_5C35 Motion — `unavailable` [Backyard] (motion)
- Tapo_Camera Motion — `unavailable` [Backyard] (motion)
- eero Gateway WAN status — `on` [Network] (connectivity)
- iPhone Presence — `off` [NO AREA] (presence)

### event (22)
- BedlightSwitch button2 — `unknown` [NO AREA]
- BedlightSwitch button3 — timestamp [NO AREA]
- BedlightSwitch button4 — timestamp [NO AREA]
- BedlightSwitch main — timestamp [NO AREA]
- Emergency Button Dad main — `unavailable` [NO AREA]
- Emergency Button Mum main — `unavailable` [NO AREA]
- Front Door Ding — timestamp [Living Room] (doorbell)
- Front Door Motion — timestamp [Living Room] (motion)
- K/Smart Button main — `unavailable` [Kitchen]
- Living Room Switch Button 1 — `unknown` [Living Room]
- Living Room Switch Button 2 — `unknown` [Living Room]
- Living Room Switch Button 3 — `unknown` [Living Room]
- Living Room Switch Button 4 — `unknown` [Living Room]
- LivingroomSwitch button2 — `unknown` [NO AREA]
- LivingroomSwitch button3 — `unknown` [NO AREA]
- LivingroomSwitch button4 — `unknown` [NO AREA]
- LivingroomSwitch main — `unknown` [NO AREA]
- Ray Bedroom Switch Button 1 — timestamp [Ray Bedroom]
- Ray Bedroom Switch Button 2 — timestamp [Ray Bedroom]
- Ray Bedroom Switch Button 3 — timestamp [Ray Bedroom]
- Ray Bedroom Switch Button 4 — timestamp [Ray Bedroom]
- RingRing main — timestamp [Living Room]

### button (20)
- Aqara Roller Shade Driver E1 Identify — timestamp [Ray Bedroom]
- Parents Room AC Reset filter — `unknown` [Parents Room]
- Presence Multi-Sensor FP300 Identify (1)-(4) — `unavailable` [Ray Bedroom] *(4 entities)*
- Smart Pet Feeder Restart — `unknown` [Dining]
- TP-LinkHub H100 Pair new device — `unknown` [Network]
- Tapo C200 - Stockroom Calibrate — `unknown` [Network]
- Tapo C200 - Stockroom Manual Alarm Start — `unknown` [Network]
- Tapo C200 - Stockroom Manual Alarm Stop — `unknown` [Network]
- Tapo C200 - Stockroom Move Down/Left/Right/Up — `unknown` [Network] *(4 entities)*
- Tapo C200 - Stockroom Reboot — `unknown` [Network]
- Tapo C425 - North Wall Manual Alarm Start — `unknown` [Network]
- Tapo C425 - North Wall Manual Alarm Stop — `unknown` [Network]
- Tapo C425 - North Wall Reboot — `unknown` [Network]
- Tapo H200 Pair new device — `unknown` [Network]

### select (33)
- Air purifier Lamp — `high` [Living Room]
- Genio Power Board with USB-LivingRoom Power-on behavior — `last` [Living Room]
- LPH-SE DCD9 Light brightness — `high` [Ray Bedroom]
- LPH-SE DCD9 Light mode — `vegetable` [Ray Bedroom]
- Smart Pet Feeder Motion detection sensitivity — `1` [Dining]
- Smart Pet Feeder Night vision — `0` [Dining]
- Tapo C200 - Stockroom Light Frequency — `auto` [Network]
- Tapo C200 - Stockroom Motion Detection — `high` [Network]
- Tapo C200 - Stockroom Move to Preset — `unknown` [Network]
- Tapo C200 - Stockroom Night Vision — `Infrared Mode` [Network]
- Tapo C200 - Stockroom Night Vision Switching — `auto` [Network]
- Tapo C200 - Stockroom Patrol Mode — `unknown` [Network]
- Tapo C200 - Stockroom Person Detection — `low` [Network]
- Tapo C420 - South Wall Light Frequency/Motion Detection/Night Vision/Person Detection/Pet Detection/Spotlight Intensity/Vehicle Detection — `unavailable` [Network] *(7 entities, whole device offline)*
- Tapo C420 East Wall Light Frequency — `60` [Network]
- Tapo C420 East Wall Motion Detection — `normal` [Network]
- Tapo C420 East Wall Night Vision — `Infrared Mode` [Network]
- Tapo C420 East Wall Person Detection — `normal` [Network]
- Tapo C420 East Wall Pet Detection — `low` [Network]
- Tapo C420 East Wall Spotlight Intensity — `5` [Network]
- Tapo C420 East Wall Vehicle Detection — `off` [Network]
- Tapo C425 - North Wall Motion Detection — `low` [Network]
- Tapo C425 - North Wall Night Vision — `Infrared Mode` [Network]
- Tapo C425 - North Wall Night Vision Switching — `auto` [Network]
- Tapo C425 - North Wall Person Detection — `low` [Network]
- Tapo C425 - North Wall Pet Detection — `low` [Network]
- Tapo C425 - North Wall Vehicle Detection — `off` [Network]

### number (22)
- G/Monitor Freezer P110M Power protection — `2149` [Garage]
- LG-Fridge freezer temperature — `-18°C` [Kitchen]
- LG-Fridge fridge temperature — `3°C` [Kitchen]
- LPH-SE DCD9 Plants age — `50d` [Ray Bedroom]
- Presence Multi-Sensor FP300 Sensitivity — `unavailable` [Ray Bedroom]
- R/Energy Monitor P110M Power protection — `2136` [Ray Bedroom]
- RingChime Volume — `5.0` [Network]
- Smart Pet Feeder Volume — `1.0%` [Dining]
- Tapo C200 - Stockroom Microphone/Speaker Volume, Motion Sensitivity, Spotlight Intensity — [Network] *(4 entities)*
- Tapo C420 - South Wall Microphone/Motion Sensitivity/Speaker Volume — `unavailable` [Network] *(3 entities)*
- Tapo C420 East Wall Microphone/Motion Sensitivity/Speaker Volume/Spotlight Intensity — [Network] *(4 entities)*
- Tapo C425 - North Wall Microphone/Motion Sensitivity/Speaker Volume/Spotlight Intensity — [Network] *(4 entities)*

### sensor (129)
This domain is the largest and covers TV/media power+energy stats, air
purifier air-quality readings, device batteries/signal levels, per-room
motion-sensor illuminance/temperature/humidity, energy monitor plugs
(current/power/voltage/monthly & daily consumption), solar production
forecast and SolarNet/Primo inverter telemetry (mostly `unavailable`),
Electricity Maps grid CO2/fossil-fuel %, and several personal-device
sensors (see "Privacy-sensitive data" below). Given the size of this list
(129 entities), the full exact set is preserved in the source agent
transcript rather than duplicated line-by-line here; re-run a live
`GetLiveContext` filtered by `domain: sensor` when a specific entity needs
to be confirmed for automation/dashboard use.

Two names worth flagging directly:
- `sensor Cost` — `49.229928 AUD` [NO AREA] — generic/unnamed, looks like
  an unrenamed default entity name.
- `Solar Power Display` — `0 W` [NO AREA]

### scene (29)
Lighting scenes per area, named e.g. "Bedroom Amber bloom", "Bedroom
Nightlight", "Dining Concentrate", "Dining Relax", "Living room Bright",
"Living room Nightlight", etc., covering Ray Bedroom (10), Dining (6),
and Living Room (7), plus a few duplicates. `state` on a scene entity is
the last-activation timestamp (or `unknown` if never triggered) — this is
normal Home Assistant behavior, not an error.

## Duplicates and ambiguities

Because this data has no `entity_id`, several friendly names are
indistinguishable between what are likely separate underlying entities:

- **Kasa/Tapo plugs with an "on/off" row and a separate "unavailable" row**
  under the identical name — `K/Bot P100`, `K/Coffee P100`, `K/Top P100`,
  `G/Printer P100` — strongly suggests **two integrations are registered
  for the same physical device** (e.g. both a cloud and a local/tplink
  integration). Worth investigating and likely deduplicating before this
  repo starts referencing these entities.
- **`light."NightLight"`** appears once tagged `Ray Bedroom` and once with
  no area — likely two distinct physical nightlights, not one entity.
- **`switch."Tapo C420 - East Wall Tapo C420 East Wall"`** and **`switch."Tapo
  C420 - South Wall Tapo C420 - South Wall"`** — the device name looks
  duplicated inside the entity name itself, likely a naming/templating bug
  worth cleaning up in Home Assistant directly.
- **Inconsistent naming** between the two similar cameras: `"Tapo C420 -
  South Wall"` (with a dash) vs. `"Tapo C420 East Wall"` (no dash) — same
  device family, different naming convention.
- **`zone.Home`** and **`device_tracker`/`notify` "Deez"** each appear as
  exact duplicate rows (identical name/state) — likely the same entity
  reported twice by the live-context tool, but not confirmed.

## Unavailable / unknown clusters

74 entities were `unavailable` at snapshot time, including entire devices
that look offline:
- All 4 **Hue ambiance spot** lights
- **Corridor 1/2**, **Dining Light Left/Right**, all 4 **Living Room
  Inner/Outer Left/Right** lights
- The entire **Presence Multi-Sensor FP300** device (9 entities: battery,
  humidity, illuminance, occupancy, sensitivity, temperature, 4 identify
  buttons)
- The entire **Primo 5.0-1 (1)** solar inverter (7 sensors)
- The entire **SolarNet** integration (5 sensors)
- **Tapo C420 - South Wall** camera's number/select sub-entities (its
  sibling "Tapo C420 East Wall" device has working values)
- **B/Freezer/EnergyMonitor/P110M** and **R/Laptop/Energy Monitor/P110M**
  (entire devices)
- **Kogan Tv** light, **Pogo** media_player

49 entities were `unknown` — mostly `button` entities (normal until first
press) and `scene` entities never triggered (normal), plus
`device_tracker.CasaRay_iPad`.

## Privacy-sensitive data present in live state (redacted here)

The live state snapshot includes some values that are sensitive personal
information rather than device/automation-relevant data. Per this repo's
`CLAUDE.md` rule against committing secrets/private data, exact values are
**redacted** in this document even though this repository is private:

- A **physical street address** appeared as the state of an iPad's
  "Geocoded Location" sensor.
- The **home WiFi SSID** appeared as the state of two separate sensors
  (an iPad's SSID sensor and a Tapo camera's network SSID sensor).
- Multiple **person / device_tracker entities** directly expose real-time
  home/away presence for named household members.

These entity *names* and domains are listed above (unredacted) since
they're needed to reason about automations; only their literal *state
values* containing address/SSID text are omitted from this file. See
`docs/live_ha_blockers.md` for the recommended handling of this data
before any of it is used in dashboards or automations committed to git.

## Possible cloud-dependent integrations

Relevant because cloud-dependent integrations typically need API
keys/OAuth tokens managed outside this repo (never committed) and can't be
fully captured as portable local YAML:

- **Ring** (Front Door doorbell/camera, "RingRing" contact/chime entities)
- **TP-Link Tapo/Kasa** cloud-connection binary_sensors (present across
  most P100/P110M plugs and Tapo cameras)
- **Electricity Maps** (grid CO2 intensity / fossil fuel %)
- **Solar production forecast** entities (likely Forecast.Solar or similar)
- **Hue Bridge Automation** switches (Hue Bridge's own automation engine,
  not native HA automations)
- **Home Assistant Companion App** entities for iPhones/iPads (notify,
  device_tracker, Kiosk Brightness/Volume, battery, SSID, geocoded location)
- **Samsung/LG Smart TV** integrations (may depend on a cloud account link
  for full remote-control features)

## Refresh process

Re-run `mcp__Home_Assistant__GetLiveContext` (optionally filtered by
`domain` or `area`) and update this document — do not hand-edit entity
names/states from memory or guesswork. Update the snapshot date above when
refreshed.
