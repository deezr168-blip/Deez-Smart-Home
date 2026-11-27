# Bilingual mockups (19/11/26) against CasaRay V3 — comparison and entity check

DEVELOPMENT ONLY — NOT DEPLOYED. Reference sheets: `docs/mockups/2026-11-19_bilingual_*.png`
(owner-supplied, 20 screens). Scope of this round: **Home, Rooms, Lighting, Climate and the
Cameras overview**. The other 15 screens (camera details, Energy, Bills, Bill setup, People,
Automations, House health, Network, Alerts, Living room, Kitchen, Dining, Parents' room) are
recorded for later rounds and are not built here.

Baseline compared: `feature/casaray-v3-release-preview` at `0f90277` (draft PR #24: PR #16's
camera slots + the V3-024 named top bar). Entity authority: `docs/live/states_export_2026-09-05.txt`
(existence and names). Availability is a 05/09 snapshot; a read-only live read on 19/11 is
quoted where it differs. Nothing here was seen on a device.

Status key: **exists** (on the working V3 view today, same entity) · **restyle** (exists, the
mockup changes its look or place) · **new card, verified entity** (not on V3 today; the entity
is in the export) · **no verified entity** (nothing in the export backs it; drawn honestly or
left out, never faked).

## Shared chrome (every screen)

| Mockup element | Working V3 today | Status | Entity / source |
|---|---|---|---|
| Header: CasaRay, page name 中文 / English | top bar header cell (V3-024) | restyle | — |
| Badge 「設計預覽 · 示例數據」 | — | restyle | the preview says 設計預覽 · 未部署 / Design preview · not deployed: a dashboard on Home Assistant reads live entities, so "sample data" would be false there. "示例數據" is used only on the offline renders, which do show the mockup's values |
| Weather ☀ 21°C | chip strip / Right now | restyle | `weather.forecast_home` |
| Time 09:41 over 星期三 · 18/11 | header (time over `DD/MM/YY`) | restyle | `now()`; the date keeps the repository's `DD/MM/YY` (18/11/26), the weekday is added |
| Bottom tab bar: 主頁 Home · 房間 Rooms · 燈光 Lighting · 鏡頭 Cameras · 更多 More, current tab amber | top rail: Home, Lighting, Climate, Cameras, Energy, Security | restyle | Home Assistant's own sticky sections-view `footer` (frontend 20260826.7), one grid card of five buttons; current tab tinted with the button's `color: accent` |

## Home (主頁)

| Mockup element | Working V3 today | Status | Entity |
|---|---|---|---|
| Greeting 早晨，今日屋企點？ / Good morning, how's home today? | — | new card, no entity needed | time-of-day template |
| Weather 21°C 多雲間晴 Partly cloudy | Right now weather card | restyle | `weather.forecast_home` |
| Banner 前門現正開啟 Front door is open, 查看門口 | Needs attention ("door open") | restyle | `binary_sensor.f_contact_sensor_door` (unavailable at 05/09; reporting again by 19/09). The preview also shows a grey "not reporting" banner, so silence is never read as closed |
| 房間燈光 Room lights: 客廳 Living room, 飯廳 Dining, Ray 房 Ray room, state pills | room lines | restyle | `light.living_room`, `light.dining`, `light.bedroom_bedroom` — read-only on Home (a tap opens Lighting), as V3 Home's gate requires |
| 門口鏡頭 Front door camera + 睇門口 View front door | Security band picture | restyle | `camera.front_door_live_view`; Offline card of the same size when unavailable (PR #16) |
| 爸媽房溫度 Parents room temperature 23°C | Climate now tile | restyle | `sensor.bedroom_motion_sensor_temperature` |
| — | chips, Needs attention list, One tap, Shopping list, Who's home, Security summary, Energy now, More boards | **not on the mockup** | kept on the working dashboard; the preview's 更多 More lists every board. Dropping any of them from Home is an owner decision (feature parity) |

## Rooms (房間)

| Mockup row (status shown) | Working V3 today | Status | Entity |
|---|---|---|---|
| 客廳 Living room — 燈光 Lights | Rooms tile | restyle | `light.living_room` |
| 廚房 Kitchen — 燈光 Lights: Off | Rooms tile (motion) | **no verified entity** | no `light.*` in the Kitchen area. Preview row says 「冇燈光實體 · No light entity」 and shows the kitchen motion it does have (`binary_sensor.k_motion_sensor_motion`) |
| 飯廳 Dining — 燈光 Lights | Rooms tile | restyle | `light.dining` (`light.dining_dining_1/_2` are dead duplicates) |
| 爸媽房 Parents — 溫度 Temperature 23°C | Rooms tile (air-con) | restyle | `sensor.bedroom_motion_sensor_temperature` |
| Ray 房 Ray room — 燈光 Lights | Rooms tile | restyle | `light.bedroom_bedroom` |
| 車房 Garage — 燈光 Lights: Off | Rooms tile (freezer plug) | **no verified entity** | no garage light. Preview shows the freezer plug it does have (`sensor.g_monitor_freezer_p110m_current_consumption`) |
| 客房 Guest — 燈光：無資料 Lights: Unavailable | Rooms tile (printer) | **no verified entity** | no guest-room light; `light.kogan_tv` is a TV backlight, not a room light. Preview shows the printer plug (`switch.g_printer_p100`, read-only) |
| Row tap › | room pages | exists | opens the working dashboard's room page (`/casaray-v3/<room>`) — room pages are not in this preview |

## Lighting (燈光)

| Mockup element | Working V3 today | Status | Entity |
|---|---|---|---|
| 客廳燈 Living room light + brightness 70% | light tile + brightness | restyle | `light.living_room` |
| 飯廳燈 Dining light | light tile | restyle | `light.dining` |
| Ray 房燈 Ray room light + brightness 80% | light tile | restyle | `light.bedroom_bedroom` |
| 夜燈 Nightlight | light tile | restyle | `light.bedroom_nightlight` (Ray's room; `light.master_bedroom_nightlight` is a dead duplicate, CR-190) |
| 情境模式 Scenes: 日常 Normal · 日間 Daytime · 晚間 Night, one selected | whole-house One tap actions (Evening, Night, Bright, All off) | **no verified entity** for Normal and Daytime, and none for the "selected" mode | `input_select.lighting_scene` exists (ok at 05/09) but its options are defined on the instance, not in git, and it is not exposed to the read-only connector — so it cannot back the three modes until its options are read on the Green. 晚間 Night uses the existing, owner-approved Night action (three lights to 10%). It fires on one tap with **no confirmation step**, the same as the working dashboard's Night button (corrected 19/11: an earlier draft of this table said it asks first; only the filter reset and the bill records ask). Normal and Daytime are drawn 「未設定 Not set up」 |
| 關於無資料 About "Unavailable" | Lighting note | restyle | static text |

## Climate (冷氣)

| Mockup element | Working V3 today | Status | Entity |
|---|---|---|---|
| 爸媽房冷氣 Parents room AC — 運行中（只供查看）Running (view only) | air-con summary, read-only (V3-008) | restyle | `climate.bedroom_parents_room_ac`; no control on the page, a tap opens the working Parents' room page |
| 室內溫度 Room temperature 23°C | air-con summary | restyle | the climate entity's `current_temperature` attribute |
| 目標溫度 Target temperature 22°C | air-con summary | restyle | the climate entity's `temperature` attribute |
| 濕度 Humidity 55% | AC status tile | restyle | `sensor.bedroom_motion_sensor_humidity` (Parents' room) |
| 濾網提示 Filter reminder — clean in about 30 days | filter tiles | restyle, **countdown has no verified entity** | `binary_sensor.bedroom_parents_room_ac_filter_clean_required`, `sensor.bedroom_parents_room_ac_filter_last_reset`. No entity gives a cleaning interval, so the preview shows "needs cleaning / not yet" and the last reset, not "30 days" |
| 定時設定 Timer — 時間資料待核實 pending | AC timer tile (read-only) | restyle | `switch.bedroom_parents_room_ac_timer`, `sensor.bedroom_parents_room_ac_timer_end_time` (the end time only while the timer is on). The HACS sheet's "no timer" blocker is about a `timer.*` helper for a custom card; the air-con's own timer entities exist |
| 客廳溫度（環境感測器）Living room temperature 24°C | temperature tile | restyle | `sensor.living_room_living_hue_hue_sensor_temperature` |
| Climate has no tab in the mockup's bar | rail button | restyle | reached from 更多 More (as the mockup implies) and from Home's parents-room temperature |

## Cameras overview (鏡頭)

| Mockup cell | Working V3 today | Status | Entity (05/09 · live 19/11) |
|---|---|---|---|
| 前門 Front Door | camera slot | restyle | `camera.front_door_live_view` (ok · idle) |
| 北牆 North Wall | camera slot | restyle | `camera.tapo_c425_north_wall_hd_stream_direct` (ok · not exposed to the connector) |
| 東牆 East Wall — 無資料 | camera slot / Offline card | restyle | `camera.tapo_c420_east_wall_hd_stream_direct` (unavailable · idle) |
| 南牆 South Wall | camera slot | restyle | `camera.tapo_c420_south_wall_hd_stream_direct` (unavailable · idle) |
| 儲物房 Stockroom | camera slot | restyle | `camera.tapo_c200_stockroom_hd_stream_direct` (ok · idle) |
| 寵物鏡頭 Pet Feeder | camera slot | restyle | `camera.smart_pet_feeder` (ok · idle; unavailable on 18/11) |
| 點擊查看畫面 Tap to view | native camera dialog (PR #16) | exists | — |
| (20/11 trial) one slot per camera | name cell + picture in 2914b09 | restyle | one 12 × 3 slot: the picture, or Offline / State unknown in words, same size (V3-025 item 12) |
| Camera photos | live camera images | **sample only** | the photos in the mockups are illustrations: used only on the offline renders, labelled 示例圖片 Sample image. Home Assistant shows the camera's own picture |

## Mockup controls with no verified entity (report)

1. Kitchen lights, Garage lights, Guest-room lights (Rooms) — no light entity in those areas.
2. Scene modes 日常 Normal and 日間 Daytime, and which mode is selected (Lighting) — no scene, script or readable `input_select` options. Needs the owner to define them (CR-233) or `input_select.lighting_scene`'s options read on the Green.
3. Filter "clean in about 30 days" countdown (Climate) — no interval entity; last reset and the needs-cleaning flag exist.
4. Camera details (later round): "Streaming compatibility" status — no entity reports it.

## House Map — follow-up only, nothing wired

The owner supplied a measured floorplan (a room-scan export dated 23/08/26). It is **not committed**:
it prints the street address. It names ten spaces — Living Room 22 m², Kitchen 15 m², Bedroom 1
14 m², Bedroom 2 8.3 m², Laundry 4.1 m², Bathroom 1 4.3 m², Bathroom 2 2.5 m², Hallway 2.9 m²,
Closet 0.4 m², Other 3.4 m² — with wall dimensions and door swings.

Before any interactive control is placed on a map:

- **Openings:** the scan's door and window openings must be confirmed on site (the scan marks
  door swings; windows and the "Other" space are not labelled).
- **Room names do not match V3's rooms.** The scan has no Dining, Garage or Guest room, and
  "Bedroom 1 / Bedroom 2" do not say whose. The export's areas are Living Room, Dining, Kitchen,
  Parents Room, Ray Bedroom, Guest Room, Backyard and Network. Which bedroom is Parents', Ray's
  or Guest, and whether Dining is part of the Living Room or Kitchen space, is the owner's
  answer to give, not an inference.
- **Device placement:** an area tells which room a device is in, not where in the room. Positions
  for lights, cameras, sensors and doors need the owner's confirmation.
- **Before committing a map:** remove the address and any other personal detail from the drawing.

## Not used

- The HACS card sheet (`CasaRay_HACS_card_verification.xlsx`) names seven custom cards. V3 is
  native-only by gate, and the Green's HACS resources were last seen missing (02/11) and have not
  been rechecked, so none is used. Its entity findings were re-checked above.
- A photo attached with the mockups was not a dashboard file and was not used or kept.
