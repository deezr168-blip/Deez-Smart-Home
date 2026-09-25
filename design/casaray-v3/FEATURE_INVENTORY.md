# CasaRay V3 — feature inventory

What CasaRay does today, and where each thing lives in the V3 prototype.
Audited 25/09/2026 on branch `casaray-v3-design` at `18a4e5d` (the tip of
`ha-deploy` when the branch was cut).

**Sources.** `dashboards/casaray_v2.yaml` (28 views, 439 distinct entity IDs),
`docs/live/states_export_2026-09-05.txt` (970 entities), the seven 14/09
mockups in `docs/mockups/`, `CLAUDE.md`, `PROJECT_STATE.md`,
`DASHBOARD_ISSUES.md`, `packages/casaray_automation.yaml`,
`themes/deez_your_name.yaml`, the last 50 commits, and a read-only
`GetLiveContext` query of the live instance on 25/09.

**What was not changed.** `dashboards/casaray_v2.yaml`,
`dashboards/deez_smart_home.yaml`, `themes/`, `packages/` and `scripts/` are
untouched. Everything V3 lives under `design/casaray-v3/`.

---

## 1. Boards

V2 has 28 views: 21 boards and 7 subviews. V3 folds them into 10 boards plus 8
room pages. Nothing is dropped silently. Every row below says where the content
went or why it waits.

| V2 view | V2 content (section headings) | V3 |
|---|---|---|
| `home` | Needs attention · One tap · Rooms · Shopping list · Right now · Who's home · Security · Energy now · Recent activity · More boards | **Home.** Same nine bands, same order. Adds a Powerpal grid-import tile under Energy now, which balances the band against Recent activity. |
| `rooms` | Room conditions | **Rooms.** Two-column list of all eight rooms, each opening a room page. |
| `living-room` | Quick actions · Lights · Power board · Entertainment · Air quality · Sensors · Front door camera · Doorbell · Other motion sensors · Device settings | **Room page.** Lights, air (purifier with a speed segment), sensors, TV, power board, scenes. Doorbell and camera move to **Security**. *Deferred:* device settings, other motion sensors. |
| `kitchen` | Bench plugs · Fridge · Electrolux fridge · Sensors · Shopping list · Plug settings | **Room page.** Bench plugs, fridge (Electrolux probe and LG door), motion. States plainly that no kitchen light is integrated. *Deferred:* plug settings. |
| `dining` | Quick actions · Lights · Sensors · Motion sensors · Pet feeder · Device settings | **Room page.** Lights, temperature, motion, pet feeder camera, scenes. *Deferred:* device settings. |
| `parents-room` | Air conditioning · Lights · Entertainment · Emergency buttons · Sensors · Power point · Television · AC maintenance · Device settings | **Room page.** AC (target and mode), main light, TV, sensors, door. Emergency buttons move to **Security**. *Deferred:* AC maintenance (filter reset), power point sockets, device settings. |
| `ray-bedroom` | Quick actions · Lights · Blind · Grow unit · Power use · Power detail · Device settings | **Room page.** Two dimmable lights, blind with a position bar, TV, desk plug with its load, scenes. Says there is no temperature sensor. *Deferred:* grow unit (every `lph_se_dcd9_*` entity was unavailable in the export), power detail, overload alarm. |
| `garage` | Freezer · Electrical · Device settings | **Room page.** Freezer load, marked **Protected**, with no off switch. |
| `guest-room` | Entertainment · Printer · Printer settings | **Room page.** Printer plug, Pogo speaker (offline). |
| `lighting` | Main lights · Wall switches · Living Room Hue · Other lights · Scene studio | **Lighting.** Every light by room, with brightness bars. "All lights off" is included as a *proposed* action. *Deferred:* scene studio, wall-switch list. |
| `climate` | Parents Room AC · Room readings · Last 24 hours · Advanced | **Climate.** Room temperatures, AC control, purifier, LG set points. *Deferred:* 24-hour history graphs, Advanced. |
| `energy` | Solar · Metered circuits · Trend · Grid and meter · Solar details | **Energy.** Solar (a no-data state while the inverter is dark), forecast today and tomorrow, best time for appliances, grid import (Powerpal), metered circuits, this month, grid carbon, gas on last bill. *Deferred:* trend graph, solar details. |
| `bills` | Bills · Upcoming · Record a payment · This year | **Bills.** Unpaid and paid lists with a *Mark paid* action, this year's totals, and the rule that a bill with no due date is never called overdue. *Deferred:* record-a-payment scripts (they write history helpers, so they wait for approval). |
| `bills-details` *(subview)* | Six bill details, six histories | *Deferred* to a Bills subview in the build. |
| `security` | Doors · Motion · Camera health · Detection settings · Sirens | **Security.** Doors, cameras (live or offline), movement, emergency buttons, sirens shown **display-only**. *Deliberately not carried:* detection settings and camera privacy switches, because turning off camera detection or recording needs the owner's approval. |
| `cameras` | Camera batteries · Floodlights | Merged into **Security** (cameras) and **House health** (batteries). *Deferred:* floodlights. |
| `camera-*` ×6 *(subviews)* | One live stream each (`custom:webrtc-camera`) | *Deferred.* The prototype draws a placeholder frame. The build keeps V2's six subviews. |
| `people` | Household · Device status · Whereabouts · Presence today | **People.** Each person's presence, when it last changed, phone battery, guest mode, the iPad. *Deferred:* presence today (logbook). |
| `automations` | Household behaviours · Hue Bridge automations · System maintenance | *Deferred.* Not a daily-use board on a wall panel. The build keeps it as a subview. |
| `entertainment` | Four TVs / speakers · Room lighting | **Media.** Every player with a power button and volume bar. |
| `house-health` | Overall · Batteries · Network · Offline devices · Backups and updates · Instrumentation notes | **House health.** Updates, last backup, eero WAN, Matter/Zigbee hub, offline entities, six batteries. |
| `network` | Network health · Wi-Fi link quality · Monitored devices · Not measured yet | Merged into **House health**. *Deferred:* Wi-Fi link quality per device. |
| `alerts` | Critical · Warnings · Information | Folded into Home's **Needs attention**, which now counts the checks that could not answer. |

## 2. Rooms

| Room (HA area) | Lights | Climate / air | Media | Power | Sensors | Scenes | Notes |
|---|---|---|---|---|---|---|---|
| Living room | Hue group + 4 spots (spots offline) | Air purifier, PM2.5 | Samsung Q9 65" | Genio power board, 2 of 5 sockets shown | Hue motion, temperature, illuminance | Bright, Relax, Read, Dimmed, Nightlight | Front doorbell and camera belong to this area in HA |
| Dining | Dining Hue group | — | — | — | Hue motion + temperature (entity IDs say `living_room_*`, HA area says Dining) | Relax, Read | Pet feeder camera |
| Kitchen | **none integrated** | — | — | Coffee, Top bench, Bottom bench | Motion | — | Electrolux fridge probe, LG fridge door |
| Parents' room | Main light (wall switch) | Sensibo AC | Samsung QLED 55" | 5-socket power point (deferred) | Motion, temperature, humidity, AC occupancy | — | Emergency buttons, door contact |
| Ray's room | Bedroom + Nightlight (Hue) | **no temperature sensor** | Samsung QLED 55" | Desk energy monitor | — | Read, Concentrate, Nightlight (+9 more) | Aqara roller blind |
| Garage | — | — | — | Freezer monitor (**protected**) | — | — | |
| Guest room | — | — | Pogo (offline) | Printer plug | — | — | Kogan TV light offline |
| Backyard | — | — | — | — | Back-door contact | — | All 16 entities unavailable in the export (`CR-234`) |

## 3. Controls

The prototype makes each of these work on demo data. The build uses the
native Home Assistant control named in the right-hand column.

| Control | Where | Native HA equivalent |
|---|---|---|
| Light on/off | Tile icon or name | `tile`, tap action `toggle` |
| Brightness bar | Dimmable light tiles | `tile` feature `light-brightness` |
| Purifier speed (off / low / medium / high) | Living room, Climate | `tile` feature `fan-speed` (already in V2) |
| Blind position | Ray's room | `tile` feature `cover-position` (already in V2) |
| AC target ±0.5°, mode | Parents' room, Climate | `thermostat` + `climate-hvac-modes` (already in V2) |
| TV power, volume | Room pages, Media | `tile` + `media-player-volume-slider` feature |
| Plug on/off | Room pages | `tile` toggle. Freezer excluded. |
| Scene | Room pages | `tile` on `scene.*`, action `scene.turn_on` |
| One tap (Evening, Goodnight, Movie, All lights off) | Home, Lighting | **Needs four new scripts (`CR-233`)**. Shown as *Proposed*. |
| Mark bill paid | Bills | `tile` toggle on `input_boolean.*_paid` |
| Shopping list tick | Home | `todo-list` card |
| Guest mode | People | `tile` toggle on `input_boolean.guest_mode` |
| Language EN / 中文 | Top bar | `input_boolean.chinese_dashboard`, as V2 |
| Theme Auto / Light / Dark | Top bar | HA user theme setting. V3 needs a light variant of the `CasaRay` theme. |
| Sirens | Security | **Display-only by design** until the owner approves a siren control. |
| Camera privacy / detection | — | **Not offered.** Disabling a camera needs owner approval. |

## 4. Integrations

The domain and naming patterns in the 05/09 export give strong evidence for
each of these. Integrations marked *inferred* are read from entity names only;
none of them was confirmed from the integrations page, which this environment
cannot see.

| Integration | Evidence (entity examples) | Used by V3 |
|---|---|---|
| Philips Hue | `light.living_room`, `*_hue_sensor_*`, `switch.hue_bridge_automation_*` | Lights, motion, temperature, illuminance |
| TP-Link Tapo | `camera.tapo_*`, `switch.k_*_p100`, `switch.*_p110m`, `siren.tapo_h200`, `*_contact_sensor_*` | Cameras, plugs, energy monitors, sirens, door contacts, emergency buttons |
| Ring *(inferred)* | `camera.front_door_live_view`, `sensor.front_door_last_activity`, `switch.front_door_in_home_chime` | Doorbell |
| Samsung TV / SmartThings | `media_player.living_room_tv_samsung_q9_series_65`, `media_player.q70f8036` | Media |
| Sensibo *(inferred)* | `climate.bedroom_parents_room_ac`, `switch.bedroom_parents_room_ac_climate_react` | AC |
| LG ThinQ | `binary_sensor.lg_fridge_door`, `number.lg_fridge_*_temperature` | Fridge |
| Electrolux | `sensor.kitchen_electrolux_fridge_temperature` | Fridge probe |
| Aqara (via Matter) *(inferred)* | `cover.aqara_roller_shade_driver_e1` | Blind |
| Genio power board *(inferred Tuya)* | `switch.genio_power_board_with_usb_livingroom_socket_*` | Living room power |
| Fronius SolarNet | `sensor.primo_5_0_1_1_*` | Solar (unreachable) |
| Forecast.Solar *(inferred)* | `sensor.energy_production_today`, `sensor.power_highest_peak_time_today` | Solar forecast |
| Electricity Maps | `sensor.electricity_maps_co2_intensity` | Grid carbon |
| Powerpal | `sensor.powerpal_gateway_powerpal_*` | Grid import (reads the meter, so it is not consumption while solar produces) |
| eero | `binary_sensor.eero_wan_status`, `sensor.eero_external_ip` | Internet status |
| Met / weather | `weather.forecast_home` | Weather |
| Mobile app | `sensor.*_battery_level`, `device_tracker.*` | People |
| Backup, Supervisor | `sensor.backup_*`, `update.home_assistant_*` | House health |
| Helpers (`input_*`, `todo`, template sensors) | 59 `input_number`, 26 `input_datetime`, 8 `input_boolean`, `sensor.casa_*` | Bills, language, guest mode, summaries |

Present in the export but not used by V3: Music Assistant, Spotify, VLC,
ESPHome, Mosquitto, OpenThread, Matter Server add-on updates, `ai_task`,
`conversation`, `stt`/`tts`.

## 5. Design requirements carried into V3

All of these come from `CLAUDE.md` and the 14/09 mockups, and V3 keeps them:

1. **Semantic colour.** Green = healthy / closed / connected. Amber = active / on. Red = fault / needs attention. Grey = unavailable. Owner-approved 14/09 (`CR-232`).
2. **Unavailable is drawn, not hidden.** Dashed border, muted card, a `No data` / `Offline` pill, and the card keeps its place.
3. **Three-branch honesty.** No reassuring state without a third branch. Denominators count what answered. A zero is claimed only when something was measured.
4. **Sentence case**, modest page titles, and a chip strip on every board.
5. **Bilingual.** Simplified Chinese from V2's vocabulary, dates as `DD/MM/YY`, `、` in Chinese lists, device names in Latin.
6. **Wall iPad first.** Two body columns on the landscape wall iPad (`DR-013`, measured). Navigation is in the page, because kiosk mode hides HA's own chrome.
7. **Native first.** Every V3 control maps to a native HA card or tile feature (section 3).
8. **Surface tokens.** Page, card and alert colours are the sampled `--casaray-*` tokens.
9. **Security posture.** No control that disables a camera, unlocks anything or sounds a siren without approval.

## 6. Open items that shape V3

| ID | What | Effect on V3 |
|---|---|---|
| `CR-233` | No whole-home scenes | One tap needs four new scripts. Shown as *Proposed*. |
| `CR-234` | All 16 Backyard entities unavailable | Backyard page kept, drawn as offline |
| `CFG-001` | Energy panel cost figure about 31.8× too high | Energy shows no dollar figure |
| `DR-013` | Wall iPad resolves two columns | Two-column body on the wall iPad. Three columns only at ≥1440px desktop. |
| Live 25/09 | See `ENTITY_MAPPING.md` §4 | Several entities the demo shows as live were unavailable on 25/09 |
