# Home Assistant Entity Inventory

Factual inventory of the live, connected Home Assistant instance, built
entirely from real reads via the Home Assistant MCP connector
(`GetLiveContext`, `GetDateTime`). Nothing here is invented — every row was
returned by a live call. See `docs/live_ha_blockers.md` for exactly what
this connector can and cannot do.

- **Snapshot taken:** 2026-08-22, 16:44 AEST (Saturday)
- **Total live entities returned:** 430 (unchanged count vs. the prior
  2026-08-21 snapshot; several individual states have changed since then —
  this is a live system, not a static export)
- **Domains observed:** 24 (see counts below)
- **Areas observed:** 10, plus 71 entities with no area assigned

## Read this first: what fields are (and aren't) available

`GetLiveContext` returns **`names` (friendly name), `domain`, `state`,
`areas`, and a partial `attributes` map** (commonly `device_class` and/or
`unit_of_measurement`, sometimes a live value like `brightness` or
`current_temperature`). It does **not** return:

- `entity_id` (e.g. `light.living_room`) — not exposed by this tool at all.
- `unique_id` / `device_id` — not exposed.
- Integration/platform name (e.g. `tplink`, `hue`, `ring`) — not exposed;
  inferred only informally from device naming below, never asserted as fact.

**Consequence:** this inventory tells you *what exists and its current
state*, grouped by area and function. It is **not** sufficient to write
`entity_id`-referencing YAML (automations, scripts, Lovelace cards) —
those IDs must be confirmed by another method before use (entity registry,
Developer Tools → States, or the REST/WebSocket API). Per `CLAUDE.md` rule
3, no `entity_id` is ever guessed in this repo.

`GetLiveContext` also appears to only return entities **exposed to the
Assist conversation agent** (HA's "expose to Assist" per-entity setting) —
confirmed by a live check that querying `domain: automation` and
`domain: script` returns `"No exposed entities found"` even though most
installs have at least a few of each. That doesn't prove no automations or
scripts exist, only that this connector can't see them if they do. See
`docs/live_ha_blockers.md`.

---

## Area / Room overview

| Area | Entities tagged | Notes |
|---|---|---|
| Network | 96 | Not a physical room — networking/security-camera equipment (AdGuard, eero, TP-Link Tapo cameras/hub, Hue Bridge automations) |
| Living Room | 64 | |
| Ray Bedroom | 61 | |
| Parents Room | 39 | |
| Dining | 27 | |
| Energy | 23 | Not a physical room — solar/energy monitoring grouping |
| Kitchen | 22 | |
| Garage | 11 | |
| Backyard | 10 | |
| Guest Room | 6 | |
| *(no area)* | 71 | Mostly person-tracking, notify, helpers, and a few sensor devices — see "Other" below |

No area literally named "Bedroom" (generic), "Bathroom", "Office", or
"Stockroom" exists in the data — a device family named "Tapo C200 -
Stockroom" is tagged area `Network`, not a "Stockroom" area, worth
confirming in HA if a real Stockroom area is expected.

---

## Lights (25 entities)

| Name | Area | State | Attributes | Notes |
|---|---|---|---|---|
| Bedroom | Ray Bedroom | off | brightness: (none) | |
| NightLight | Ray Bedroom | off | brightness: (none) | |
| NightLight | *(no area)* | off | brightness: (none) | duplicate name, different area — likely a separate physical light |
| Smart Pet Feeder Indicator light | Dining | on | | |
| Dining | Dining | on | brightness 255 | duplicate row (x2), identical |
| Corridor 1 | Dining | unavailable | | |
| Corridor 2 | Dining | unavailable | | tagged "Dining" despite "Corridor" name — worth confirming area mapping |
| Dining Light Left | Dining | unavailable | | |
| Dining Light Right | Dining | unavailable | | |
| Living room | Living Room | on | brightness 255 | duplicate row (x2), identical |
| Living Room Inner Left | Living Room | unavailable | | |
| Living Room Inner Right | Living Room | unavailable | | |
| Living Room Outter Left | Living Room | unavailable | | |
| Living Room Outter Right | Living Room | unavailable | | |
| Kogan Tv | Guest Room | unavailable | | light entity despite "Tv" name |
| Hue ambiance spot 1 | *(no area)* | unavailable | | duplicate row (x2) |
| Hue ambiance spot 3 | *(no area)* | unavailable | | |
| Hue ambiance spot 4 | *(no area)* | unavailable | | |
| Tapo C200 - Stockroom Floodlight (Timed) | Network | off | | camera-integrated floodlight |
| Tapo C420 - South Wall Floodlight (Timed) | Network | off | | |
| Tapo C420 East Wall Floodlight (Timed) | Network | off | | |
| Tapo C425 - North Wall Floodlight (Timed) | Network | off | | |

10 of 25 light entities are currently `unavailable` — see "Devices that
appear offline" below.

## Switches (60 entities)

Grouped by rough purpose; area shown per row.

**Outlets / power boards**
| Name | Area | State |
|---|---|---|
| BedRoomLight Switch 1 | Ray Bedroom | off |
| MainRoomLight Switch 1 | Parents Room | off |
| Dinning light Switch 1 | Dining | on |
| Genio Power Board with USB-LivingRoom Socket 1–5 | Living Room | on (all 5) |
| Master bedroom power point Socket 1–5 | Parents Room | on (all 5) |

**Appliances / device power**
| Name | Area | State |
|---|---|---|
| Air purifier | Living Room | on |
| G/Monitor Freezer P110M | Garage | on |
| K/Bot P100 | Kitchen | on / unavailable (duplicate rows) |
| K/Coffee P100 | Kitchen | on / unavailable (duplicate rows) |
| K/Top P100 | Kitchen | on / unavailable (duplicate rows) |
| G/Printer P100 | Guest Room | off / unavailable (duplicate rows) |
| R/Energy Monitor P110M | Ray Bedroom | on |
| B/Freezer/EnergyMonitor/P110M | Backyard | unavailable |
| R/Laptop/Energy Monitor/P110M | *(no area)* | unavailable |
| LG-Fridge Express mode | Kitchen | off |
| LPH-SE DCD9 Power | Ray Bedroom | on |
| LPH-SE DCD9 Pump cycling | Ray Bedroom | on |
| Sensibo Sky Plus | Parents Room | off |
| Light Sensor - 55" QLED 4k AI | Parents Room | off |

**Motion/light sensor config toggles**
| Name | Area | State |
|---|---|---|
| Dining Room Motion Sensor Light/Motion sensor enabled | Dining | on / on |
| Living Room Motion Sensor Light/Motion sensor enabled | Living Room | on / on |

**Doorbell / security**
| Name | Area | State |
|---|---|---|
| Front Door In-home chime | Living Room | on |
| Front Door Motion detection | Living Room | on |
| Parents Room AC Climate React | Parents Room | off |
| Parents Room AC Timer | Parents Room | off |

**Network / cameras**
| Name | Area | State |
|---|---|---|
| AdGuard Home Filtering / Protection / Query log / Safe search | Network | on (all) |
| AdGuard Home Parental control / Safe browsing | Network | off (both) |
| Hue Bridge Automation: Coming home | Network | off |
| Hue Bridge Automation: Leaving home | Network | off |
| Hue Bridge Automation: Nightlight On Nightlight Off | Network | on |
| Tapo C200 - Stockroom Auto Track | Network | on |
| Tapo C200 - Stockroom Preset Patrol Mode | Network | off |
| Tapo C200 - Stockroom Privacy | Network | off |
| Tapo C420 - East Wall Motion/Person detection | Network | on / on |
| Tapo C420 - East Wall Tapo C420 East Wall | Network | on | *malformed name — see "Naming issues"* |
| Tapo C420 - South Wall Motion/Person detection | Network | on / on |
| Tapo C420 - South Wall Privacy | Network | unavailable |
| Tapo C420 - South Wall Tapo C420 - South Wall | Network | on | *malformed name* |
| Tapo C420 East Wall Privacy | Network | off |
| Tapo C425 - North Wall Privacy | Network | off |

## Sensors (129 entities)

The largest domain — device batteries/signal levels, per-room motion
sensor illuminance/temperature/humidity, TV/media power+energy, air
purifier air-quality readings, and several personal-device sensors.
Selected entries (grouped by rough purpose; full raw data was captured
during this session and is available on request — this list omits none of
the 129, condensed for readability where a device has many near-identical
sub-sensors):

**Room climate sensors** (each is a full set: Battery, Illuminance,
Temperature per device)
| Device | Area | Temp | Illuminance | Battery |
|---|---|---|---|---|
| Dining Room Motion Sensor | Dining | 18.2°C | 160 lx | 100% |
| Living Room Motion Sensor | Living Room | 20.8°C | 35 lx | 100% |
| Bedroom Hue Sensor | *(no area)* | 18.2°C | 161 lx | 100% |
| Living Hue Hue Sensor | *(no area)* | 20.8°C | 36 lx | 100% |
| Parents Room Motion Sensor | Parents Room | 19.6°C | — | (voltage 3000, humidity 66.0%) |
| Presence Multi-Sensor FP300 | Ray Bedroom | unavailable | unavailable | unavailable |

**Energy-monitor plugs** (Current, Power, Voltage, Today's/Month's
consumption — see Energy section below for full detail)
- G/Monitor Freezer P110M (Garage), R/Energy Monitor P110M (Ray Bedroom),
  B/Freezer/EnergyMonitor/P110M (Backyard, unavailable),
  R/Laptop/Energy Monitor/P110M (no area, unavailable)

**Device batteries / signal levels** (battery % unless noted)
| Device | Area | Value |
|---|---|---|
| Aqara Roller Shade Driver E1 Battery | Ray Bedroom | 75% (3.00V, not_charging) |
| Front Door Battery | Living Room | 26% |
| Living Room Switch Battery | Living Room | 58% |
| Ray Bedroom Switch Battery | Ray Bedroom | 97% |
| RingRing Battery | Living Room | 28% |
| BedlightSwitch Battery | *(no area)* | 97% |
| LivingroomSwitch Battery | *(no area)* | 58% |
| Tapo C420 - East/South Wall / C425 North Wall Battery | Network | 66% / 100% (dup row) / 27% |
| Tapo_Camera Battery | Backyard | unavailable |
| G/Printer P100 / K/Bot / K/Coffee / K/Top P100 Signal level | Guest Room / Kitchen | 3 / 3 / 2 / 2 |
| B/Contact / F/Contact / M/Contact Sensor Signal level | Backyard / Living Room / Parents Room | 1 / 3 / 3 |
| TP-LinkHub H100 Signal level | Network | 3 |
| CPU Speed | Network | unknown (GHz) |

**Air purifier air quality** (Living Room): Air quality 1 CAQI, Odor 1,
PM1/PM10/PM2.5 = 5 μg/m³ each, health concern "good" for all three.

**Doorbell / activity**: Front Door Last activity — timestamp, Living Room.

**Fridge**: LG-Fridge freezer temperature −18°C, fridge temperature 3°C
(Kitchen).

**Climate control detail**: Sensibo Sky Plus Air conditioner mode
"fanOnly", Cooling setpoint 19.0°C (Parents Room). Light Sensor - 55" QLED
4k AI Brightness intensity 1, Illuminance 10 lx (Parents Room). Parents
Room AC Timer end time — a timestamp from 2025-03-10 (stale — the AC timer
switch is currently off, consistent with an old/unused timer value).

**TV/media energy & channel**: 55" QLED 4k AI Energy/Energy
difference/Energy saved/Power/Power energy (all ~0.00–0.01, Parents Room),
TV channel (empty) / TV channel name "9Ur5IzDKqV.TizenYouTube" (Parents
Room and, separately, Living Room's Samsung Q9 Series carries the same
channel-name sensor pair).

**Misc / unnamed**: `sensor Cost` — 579.82 AUD, monetary, no area
(generic/unrenamed-looking name). `Solar Power Display` — 400 W, no area.

**Personal device sensors** (Ai's iPhone, Raymond's iPad, Deez Raymond's
iPhone, Vinh's phone): battery level, connection type, location
permission, kiosk brightness/volume, storage. Two values are **redacted
here** as privacy-sensitive — see "Privacy-sensitive data" below.

See the Energy and Network sections for the remaining sensor entities
(SolarNet, Primo inverter, Electricity Maps, solar forecast, Tapo camera
network/detection sensors).

## Binary sensors (47 entities)

**Doors / contacts**
| Name | Area | State |
|---|---|---|
| B/Contact Sensor Door | Backyard | off / unavailable (dup rows) |
| F/Contact Sensor Door | Living Room | on / unavailable, no area (dup rows) |
| M/Contact Sensor Door | Parents Room | off / unavailable, no area (dup rows) |
| LG-Fridge Door | Kitchen | off |

**Motion**
| Name | Area | State |
|---|---|---|
| Dining Room Motion Sensor Motion | Dining | off |
| Sensor group Motion | Dining | off |
| Living Room Motion Sensor Motion | Living Room | off |
| Living room Motion | Living Room | off |
| RingRing Motion | Living Room | off |
| K/Motion Sensor Motion | Kitchen | off / unavailable (dup rows) |
| K/Motion Sensor Occupancy | Kitchen | off |
| Parents Room Motion Sensor Motion | Parents Room | off |
| Parents Room AC Room occupied | Parents Room | off |
| Bedroom Hue Sensor Motion | *(no area)* | off |
| Living Hue Hue Sensor Motion | *(no area)* | off |
| Presence Multi-Sensor FP300 Occupancy | Ray Bedroom | unavailable |
| Tapo_C200_5C35 Motion | Backyard | unavailable |
| Tapo_Camera Motion | Backyard | unavailable |
| iPhone Presence | *(no area)* | on |

**Cloud connectivity** (device_class: connectivity)
B/Contact, F/Contact, M/Contact Sensor, G/Monitor Freezer P110M, G/Printer
P100, K/Bot P100, K/Coffee P100, K/Motion Sensor, K/Smart Button, K/Top
P100, R/Energy Monitor P110M, TP-LinkHub H100, eero Gateway WAN status,
Emergency Button Dad/Mum — all `on` at snapshot time (i.e. all currently
cloud-connected).

**Problem / diagnostic**
| Name | Area | State |
|---|---|---|
| Aqara Roller Shade Driver E1 Configuration status | Ray Bedroom | off (no problem) |
| G/Monitor Freezer P110M Overheated | Garage | unavailable |
| G/Monitor Freezer P110M Overloaded | Garage | off |
| R/Energy Monitor P110M Overloaded | Ray Bedroom | off |
| TP-LinkHub H100 Overheated | Network | off |
| Parents Room AC Filter clean required | Parents Room | off |

**Other**
LPH-SE DCD9 Pump (running) — on, Ray Bedroom. Parents Room Motion Sensor
Connectivity — on. Raymond's iPad Kiosk Mode — on, no area.

## Climate (1 entity)

| Name | Area | State | Attributes |
|---|---|---|---|
| Parents Room AC | Parents Room | off | current_temperature: 19.6°C |

Related entities in other domains: **Sensibo Sky Plus** (switch, off;
sensor mode "fanOnly", setpoint 19.0°C) also targets Parents Room's AC —
likely a smart-IR controller for the same physical unit as `climate.Parents
Room AC`, but this cannot be confirmed without entity IDs/device registry
data.

## Media players (9 entities)

| Name | Area | State | Volume |
|---|---|---|---|
| 55" QLED 4k AI | Parents Room | idle / off / on (3 rows) | 1.0 / — / 0.19 |
| 55&quot; QLED 4k AI (QA55Q7FAAWXXY) | Ray Bedroom | on | 0.19 |
| Pogo | Guest Room | unavailable | — |
| Samsung Q9 Series (65) | Living Room | idle / on (2 rows) | 0.20 |
| [TV] Samsung Q9 Series (65) | Living Room | idle / on (2 rows) | 0.20 |

Related **remote** entities: `55&quot; QLED 4k AI (QA55Q7FAAWXXY)` (Ray
Bedroom, on) and `[TV] Samsung Q9 Series (65)` (Living Room, on).

Note: `55&quot;` is a raw HTML-entity artifact (should render as `55"`) —
likely double-encoded somewhere upstream; worth cleaning up in HA if it
shows up the same way in the UI.

## Cameras (6 entities)

| Name | Area | State |
|---|---|---|
| Front Door Live view | Living Room | idle |
| Smart Pet Feeder | Dining | idle |
| Tapo C200 - Stockroom HD Stream (Direct) | Network | idle |
| Tapo C420 - South Wall HD Stream (Direct) | Network | idle |
| Tapo C420 East Wall HD Stream (Direct) | Network | idle |
| Tapo C425 - North Wall HD Stream (Direct) | Network | idle |

All camera domain entities are currently `idle` (streaming-ready), i.e.
none are reporting a hard failure at the camera-entity level — though see
Network section for camera *sub-entities* (motion/person detection,
battery) that are `unavailable`.

## Persons / presence (3 person + 6 device_tracker + 2 zone entities)

| Name | Domain | State |
|---|---|---|
| Ai Q Huang | person | not_home |
| Raymond Du. | person | home |
| Vinh Du | person | home |
| Ai's iPhone | device_tracker | not_home |
| CasaRay iPad | device_tracker | unknown |
| Deez | device_tracker | home (duplicate row, identical, x2) |
| Raymond's iPad | device_tracker | home |
| Vinh's phone | device_tracker | home |
| Home | zone | 2 (people currently in zone; duplicate row x2) |

`person."Raymond Du."` has a literal trailing period in its name. Presence
here directly reveals real-time household member locations — see
"Privacy-sensitive data."

Six matching **notify** entities exist (Ai's iPhone, CasaRay iPad, Deez
×2, Raymond's iPad, Vinh's phone) — all state `unknown`/timestamp, which is
normal for `notify` (it reflects last-notification metadata, not a
readable value).

## Energy (23 area-tagged entities, plus related plugs/helpers elsewhere)

**Solar / inverter** (area: Energy)
| Name | State | Unit |
|---|---|---|
| Primo 5.0-1 (1) AC current | 1.74 | A |
| Primo 5.0-1 (1) AC power | 400 | W |
| Primo 5.0-1 (1) DC current | 1.24 | A |
| Primo 5.0-1 (1) DC voltage | 425 | V |
| Primo 5.0-1 (1) Energy day | 19375 | Wh |
| Primo 5.0-1 (1) Energy year | 4439046 | Wh |
| Primo 5.0-1 (1) Total energy | 48276900 | Wh |
| SolarNet CO₂ factor | 0.53 | kg/kWh |
| SolarNet Grid export tariff | 0.015 | AUD/kWh |
| SolarNet Grid import tariff | 0.288 | AUD/kWh |
| SolarNet Meter mode | produce-only | |
| SolarNet Power photovoltaics | 392 | W |
| Solar Power Display | 400 W | *(no area)* |

**Solar production forecast** (area: Energy)
| Name | State | Unit |
|---|---|---|
| Estimated energy production - next hour | 0.7 | kWh |
| Estimated energy production - remaining today | 1.2 | kWh |
| Estimated energy production - this hour | 0.9 | kWh |
| Estimated energy production - today | 8.2 | kWh |
| Estimated energy production - tomorrow | 10.4 | kWh |
| Estimated power production - now | 821 | W |
| Highest power peak time - today | 2026-08-22T10:00:00+10:00 | |
| Highest power peak time - tomorrow | 2026-08-23T13:00:00+10:00 | |

**Grid carbon intensity** — Electricity Maps CO2 intensity 502.0
gCO2eq/kWh, Grid fossil fuel percentage 60.67% (area: Energy).

**Weather** — Forecast Home: partlycloudy, 13.0°C, 71% humidity (area:
Energy — grouped here rather than a physical room).

**Per-device energy monitor plugs** (not tagged area Energy, but
functionally energy monitoring — see Sensors/Switches above for full
detail): G/Monitor Freezer P110M (Garage), R/Energy Monitor P110M (Ray
Bedroom), B/Freezer/EnergyMonitor/P110M (Backyard, unavailable),
R/Laptop/Energy Monitor/P110M (no area, unavailable), plus their Power
protection number entities and Cloud connection binary_sensors. Also 55"
QLED 4k AI Energy/Power sensors (Parents Room).

**Helper**: `input_number."Gas Bill Usage MJ"` — 9437.04 MJ (no area) —
a manually-tracked gas usage helper, not from a live meter integration.

## Network (96 area-tagged entities)

Dominated by the TP-Link Tapo camera family (C200 Stockroom, C420 East
Wall, C420 South Wall, C425 North Wall) and their many sub-entities
(motion/person/pet/vehicle detection selects, microphone/speaker volume
numbers, night vision selects, battery/signal sensors, floodlight/privacy
switches, HD stream cameras, buttons) — see Lights/Switches/Sensors/
Selects/Numbers/Buttons sections above for the full per-entity breakdown,
all tagged area `Network`.

Also in this area:
- **AdGuard Home** (switch): Filtering, Parental control, Protection,
  Query log, Safe browsing, Safe search
- **eero Gateway WAN status** (binary_sensor): on
- **TP-LinkHub H100**: Cloud connection, Overheated (binary_sensor),
  Signal level (sensor), Pair new device (button), Alarm (sensor,
  unavailable)
- **Hue Bridge Automation** switches: Coming home / Leaving home /
  Nightlight On Nightlight Off — these are the Hue Bridge's own built-in
  automation engine exposed as switches, **not** native Home Assistant
  automations (relevant to `docs/live_ha_blockers.md`'s automation-domain
  finding)
- **Tapo H200 Pair new device** (button): unknown
- **RingChime Volume** (number): 5.0
- **CPU Speed** (sensor): unknown, GHz — likely a Home Assistant host/add-on
  system sensor

## Helpers (4 entities)

| Name | Domain | State | Notes |
|---|---|---|---|
| Chinese Dashboard | input_boolean | off | purpose not confirmable from name alone |
| Family Location | input_select | Raymond Du | current option |
| Gas Bill Usage MJ | input_number | 9437.04 MJ | manual/periodic entry, not live-metered |
| Shopping List | todo | 0 items | |

A combined live check for `input_number`, `input_text`, `input_datetime`,
`timer`, `counter`, and `schedule` domains returned **only** the one
`input_number` above — no entities of the other helper types were
returned. This may mean none exist, or that they exist but aren't exposed
to Assist; not distinguishable from this connector (see blockers doc).

## Scripts (0 entities — unverified whether any exist)

A live query for `domain: script` returned **"No exposed entities found"**.
Home Assistant scripts run as `script.*` entities, so either no scripts
are defined, or scripts exist but are not exposed to the Assist
conversation agent (the scope this connector reads from). **Not
distinguishable from here — do not assume either way.** See
`docs/live_ha_blockers.md`.

## Automations (0 entities — unverified whether any exist)

Same finding as Scripts: a live query for `domain: automation` returned
**"No exposed entities found"**. This system almost certainly has
automations in some form given its scale (Hue Bridge automation switches,
motion-sensor-enabled toggles, AC "Climate React" logic, etc.), but none
are visible as `automation.*` entities through this connector. **Do not
write or assume any automation configuration based on this inventory** —
see `docs/live_ha_blockers.md` for what's needed to actually inspect them.

## Other (scenes, events, buttons, time)

**Scenes (29)** — lighting presets. Ray Bedroom (15): Amber bloom, Baby's
breath, Blossom, Concentrate, Dreamy dusk, Nature's colors, Nightlight,
Nighttime, Pensive, Read, Silverstone, Starlight, Suzuka, Vapor wave, plus
one more. Dining (6): Concentrate, Energize, Midwinter, Nightlight, Read,
Relax. Living Room (8): Bright, Concentrate, Dimmed, Energize, Midwinter,
Nightlight, Read, Relax. `state` on a scene is its last-activation
timestamp, or `unknown` if never triggered — normal behavior, not an error.

**Events (22)** — physical button press events from Aqara/smart switches:
BedlightSwitch (main + button2/3/4, no area), Living Room Switch Button
1–4 (Living Room), LivingroomSwitch (main + button2/3/4, no area), Ray
Bedroom Switch Button 1–4 (Ray Bedroom), Front Door Ding/Motion (Living
Room), RingRing main (Living Room), Emergency Button Dad/Mum main
(unavailable, no area), K/Smart Button main (unavailable, Kitchen).

**Buttons (20)** — mostly Tapo camera control actions (Calibrate, Manual
Alarm Start/Stop, Move Up/Down/Left/Right, Reboot, Pair new device) for
Stockroom/North Wall cameras and the H200/H100 hub (all `unknown` — normal
for buttons, which have no persistent state until pressed), plus Aqara
Roller Shade Identify (timestamp), Parents Room AC Reset filter
(unknown), Presence Multi-Sensor FP300 Identify ×4 (unavailable), Smart
Pet Feeder Restart (unknown).

**Time (2)** — LPH-SE DCD9 Light off (18:00:00), Light on (06:00:00), Ray
Bedroom — a grow-light device's schedule.

**Cover (1)** — Aqara Roller Shade Driver E1, Ray Bedroom: `open`,
position 100% at snapshot time (was `closed`/0% in the prior 2026-08-21
snapshot — confirms this is live, changing data).

**Fan (1)** — Air purifier, Living Room: `on`.

---

## Duplicates and ambiguities

No `entity_id` is available, so several friendly names can't be
distinguished between what are likely separate underlying entities:

- **Kasa/Tapo plugs with an "on/off" row and a separate "unavailable" row**
  under the identical name — `K/Bot P100`, `K/Coffee P100`, `K/Top P100`,
  `G/Printer P100` — suggests **two integrations registered for the same
  physical device** (e.g. cloud + local). Worth deduplicating in HA before
  this repo depends on these entities.
- **`light."NightLight"`** appears once tagged `Ray Bedroom`, once with no
  area — likely two distinct physical nightlights.
- **`switch."Tapo C420 - East Wall Tapo C420 East Wall"`** and **`switch."Tapo
  C420 - South Wall Tapo C420 - South Wall"`** — device name appears
  duplicated inside the entity name — likely a naming/templating bug.
- Inconsistent naming between the two similar cameras: `"Tapo C420 - South
  Wall"` (with a dash) vs. `"Tapo C420 East Wall"` (no dash).
- **`zone.Home`** and **`device_tracker`/`notify` "Deez"** each appear as
  exact duplicate rows — possibly the live-context tool reporting the same
  entity twice, not confirmed.

## Devices that appear offline (currently `unavailable`)

- All 4 **Hue ambiance spot** lights
- **Corridor 1/2**, **Dining Light Left/Right**, all 4 **Living Room
  Inner/Outer Left/Right** lights
- The entire **Presence Multi-Sensor FP300** device (battery, humidity,
  illuminance, occupancy, sensitivity, temperature, 4 identify buttons)
- The entire **Primo 5.0-1 (1)** solar inverter — **now reporting live
  values** as of this 2026-08-22 snapshot (was fully `unavailable` on
  2026-08-21) — likely intermittent connectivity, not permanently offline
- **SolarNet** — same: was fully `unavailable` 2026-08-21, now reporting
  live values 2026-08-22
- **Tapo C420 - South Wall** camera's Privacy switch remains `unavailable`
  (its other sub-entities recovered and now report normally, unlike the
  2026-08-21 snapshot where most were unavailable)
- **B/Freezer/EnergyMonitor/P110M**, **R/Laptop/Energy Monitor/P110M**
  (entire devices)
- **Kogan Tv** light, **Pogo** media_player, **Tapo_Camera** (Backyard,
  motion + battery)

## Privacy-sensitive data present in live state (redacted here)

Per `CLAUDE.md`'s rule against committing secrets/private data, the
following are **redacted** even though this repository is private:

- A **physical street address**, the state of an iPad's "Geocoded
  Location" sensor.
- The **home WiFi SSID**, appearing as the state of two sensors (an iPad's
  SSID sensor and a Tapo camera's network SSID sensor).
- **person / device_tracker** entities directly expose real-time home/away
  presence for named household members (see "Persons / presence" above —
  names and states are kept since they're needed to reason about
  presence-based automations, but should not be pasted into any
  automation/dashboard YAML verbatim without considering who can see this
  repo).

## Possible cloud-dependent integrations

Relevant because cloud-dependent integrations typically need API
keys/OAuth tokens kept out of git (e.g. via `secrets.yaml`):

- **Ring** (Front Door doorbell/camera, "RingRing" entities)
- **TP-Link Tapo/Kasa** cloud-connection binary_sensors (present on most
  P100/P110M plugs and Tapo cameras)
- **Electricity Maps** (grid CO2 intensity / fossil fuel %)
- **Solar production forecast** (likely Forecast.Solar or similar)
- **Hue Bridge Automation** switches (Hue Bridge's own engine, not native
  HA automations)
- **Home Assistant Companion App** entities for iPhones/iPads (notify,
  device_tracker, kiosk brightness/volume, battery, SSID, geocoded
  location)
- **Samsung/LG Smart TV** integrations (may depend on a cloud account link)

## Naming issues worth cleaning up in HA

- `person."Raymond Du."` — literal trailing period.
- `sensor."sensor Cost"` — literally starts with the word "sensor",
  looks like an unrenamed default name.
- `55&quot; QLED 4k AI (QA55Q7FAAWXXY)` — raw HTML-entity artifact instead
  of a rendered `"`.
- `switch."Tapo C420 - East Wall Tapo C420 East Wall"` / `"Tapo C420 -
  South Wall Tapo C420 - South Wall"` — device name duplicated inside the
  entity name.

## Refresh process

Re-run `mcp__Home_Assistant__GetLiveContext` (optionally filtered by
`domain` and/or `area` to stay under the tool's response-size limit — a
single unfiltered call returns 400+ entities and can exceed it) and update
this document. Do not hand-edit entity names/states from memory. Update
the snapshot date/time above whenever refreshed.
