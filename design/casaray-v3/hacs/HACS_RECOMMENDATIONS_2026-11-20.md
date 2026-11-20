# Custom cards (HACS) worth adding to CasaRay — verified recommendation, 20/11/26

DESIGN PROPOSAL — NOTHING INSTALLED, NOTHING DEPLOYED. Owner request, 20/11/26: mockups of
the dashboard with the custom cards worth adding, each checked to be really buildable.

Mockups: `hacs/mockups/make_mockups.py` draws seven (iPad landscape 1180 × 820, one iPhone
390 × 844). They are illustrations in the CasaRay V3 style with sample values, **not
renders of the cards and not Home Assistant screenshots**. Renders are not committed
(`../.gitignore`); regenerate them as the script's docstring says.

## How each card was checked

Every card below passed all four checks on 20/11/26, from this session:

1. **In HACS's default store:** listed in `hacs/default` (`plugin` and `integration`).
2. **Maintained:** last push and archive flag from GitHub's repository search.
3. **Every option drawn is documented:** read in the card's own README or `docs/` at its
   default branch. An option not found there is not drawn (Advanced Camera Card's
   per-tile names, "LIVE" badges and microphone were removed for that reason).
4. **Every entity is real:** in `docs/live/states_export_2026-09-05.txt`, and where the
   read-only connector can see it, read live on 19–20/11.

## What the Green has today (blocks every card)

- **18/09** (`docs/CASARAY_MAPPING_PACK.md`): installed custom resources were Mushroom,
  WebRTC Camera, card-mod and kiosk-mode.
- **02/11** (`DECISIONS.md`, V3 camera entry): the owner reported `/config/custom_components`
  missing and the Lovelace **Resources list empty**. Whether HACS itself is still installed is
  unknown from here.
- So **each card below needs installing** through HACS (Download → the resource is added) and a
  browser refresh on the wall iPad. That is a live change: the owner does it.
- **Repository rule:** CasaRay V3 is native-only by gate (`validate_dashboard.py`
  `NATIVE_TYPES`); V2 allows one custom card, `custom:webrtc-camera`. Building any card below
  into a dashboard needs an owner decision recorded in `DECISIONS.md` first.

## Found live this week, and it matters for every card

- **Six entity IDs are not on the instance** (owner's photos, 20/11): `light.living_room`,
  `light.dining`, `camera.tapo_c425_north_wall_hd_stream_direct`,
  `camera.tapo_c420_east_wall_hd_stream_direct`, `camera.tapo_c420_south_wall_hd_stream_direct`,
  `camera.smart_pet_feeder`. The devices answer under other IDs. Any card bound to them shows
  nothing until the real IDs are confirmed in Settings → Entities.
- **`weather.forecast_home` shows No data** on the wall iPad and is not exposed to the
  connector. A weather card waits on it.

## Recommendation

| # | Card | Verdict | What it fixes here | Options drawn (all documented) | Entities | Repo · HACS · last push · ★ |
|---|---|---|---|---|---|---|
| 1 | **Kiosk Mode** | **Add first** | The trial photos show Home Assistant's header and sidebar on the wall iPad; the legacy dashboard used this card for exactly that | `kiosk_mode: {kiosk: true}`; `?disable_km` in the URL to get the chrome back | none | NemesisRE/kiosk-mode · default · 17/11/26 · 836 |
| 2 | **Bubble Card** | **Add** | Rooms open as a pop-up sheet over the page instead of navigating away; big slider buttons are easier for parents than tiles | `card_type: pop-up` with `hash: '#living-room'`; `card_type: button`, `button_type: slider`; `sub_button` | lights and sensors of each room — the Living room and Dining light IDs to confirm first | Clooos/Bubble-Card · default · 31/10/26 · 4741 |
| 3 | **Advanced Camera Card** | **Add, after the camera IDs** | One card shows every camera in a fixed grid (the trial's uneven, vanishing slots), with zoom and full screen | `cameras: [{camera_entity: …}]`; `live.display.mode: grid`, `grid_columns: 3`; menu `cameras`, `live`, `display_mode`, `fullscreen`; `status_bar` | six cameras — four IDs to confirm | dermotduffy/advanced-camera-card · default · 20/11/26 · 1218 |
| 4 | **auto-entities** | **Add** | House health lists every unavailable entity by itself; no hand-kept list goes stale | `filter.include: [{domain: light, state: unavailable}]` (one card per domain); `show_empty` | any — names in the mockup are the connector's, 19–20/11 | thomasloven/lovelace-auto-entities · default · 09/05/26 · 1842 |
| 5 | **ApexCharts Card** | **Add** | Today's solar against grid import, one honest chart from two measured sensors | `graph_span: 24h`; series `type: area` | `sensor.primo_5_0_1_1_ac_power`, `sensor.powerpal_gateway_powerpal_power` (export; not visible to the connector) | RomRider/apexcharts-card · default · 03/02/26 · 1905 |
| 6 | **Power Flow Card Plus** | **Add with a caveat** | Solar → home ← grid at a glance | `entities.solar.entity`, `entities.grid.entity` | the same two sensors | flixlix/power-flow-card-plus · default · 15/11/26 · 1220 |
| 7 | **WallPanel** | **Optional** | A screensaver on the wall iPad: your photos with a clock and two readings; a touch returns to the dashboard | `wallpanel: {enabled: true, idle_time: …, image_url: media-source://…}`; info box `cards:` | `sensor.bedroom_motion_sensor_temperature`, `binary_sensor.f_contact_sensor_door` (both answering live) | j-a-n/lovelace-wallpanel · default · 14/11/26 · 892 |
| 8 | Clock Weather Card | **Later** | A polished clock-and-forecast header | `date_pattern` (Luxon tokens, so `dd/MM/yy` works), `time_pattern` | waits on a working weather entity | pkissling/clock-weather-card · default · 20/11/26 · 918 |
| 9 | Timer Bar Card | Later | The air-con's sleep timer as a countdown bar | the switch as the entity, `end_time: {entity: sensor.bedroom_parents_room_ac_timer_end_time}` | `switch.bedroom_parents_room_ac_timer` — **corrects the owner's sheet: not a blocker**, no `timer.*` helper is needed | rianadon/timer-bar-card · default · **19/07/25**, 100 open issues — weakest maintenance here |
| 10 | Navbar Card | Not now | — | its option docs are on a site this session cannot reach, so none was verified | — | joseluis9595/lovelace-navbar-card · default · 27/10/26 · 892 |
| 11 | Thermostat Dark Card | **Not recommended** | — | it is a control; the Parents' air-con is read-only on V3 by owner decision (V3-008) | — | ciotlosm/lovelace-thermostat-dark-card · default · 15/11/26 · 749 |

Already the legacy dashboard's stack and still maintained (Mushroom 12/11/26, card-mod
30/09/26, WebRTC Camera 15/10/26): reinstall them if the legacy dashboard is still in use and
the Resources list is still empty. They are not new recommendations for V3.

### Caveats that keep the mockups honest

- **Power Flow "Home" is a sum, not a measurement.** The card adds the sources unless
  `entities.home.entity` with `override_state: true` supplies a consumption sensor. Powerpal
  reads grid import only, and there is no export sensor (ENTITY_MAPPING, V3-003), so "Home"
  reads high whenever the panels export. The mockup is an evening scene (importing, nothing
  exported) and carries the caveat on the card. A Fronius smart meter or any consumption
  sensor would remove it.
- **Navbar Card vs the native footer.** The sticky native footer worked on the wall iPad in
  the trial photos. A custom card for something native already does is a dependency without
  a gain, unless its extras (a side rail on tablets, badges) are wanted.
- **WallPanel and Kiosk Mode both hide chrome.** Use Kiosk Mode for that and WallPanel only for
  the screensaver, so the two do not fight over the header.
- **Advanced Camera Card plays live streams in the grid.** On a battery doorbell (the front
  door reads 65 %) a constantly streaming grid costs battery; its `live.preload: false` and
  `lazy_load: true` are the defaults and keep it on demand.

## The mockups

| File | Shows | Cards |
|---|---|---|
| `1_home_kiosk_mode` | Home with no Home Assistant header or sidebar | Kiosk Mode |
| `2_rooms_bubble_popup_ipad` | Rooms with the Living room pop-up open | Bubble Card |
| `3_rooms_bubble_popup_iphone` | the same pop-up on an iPhone | Bubble Card |
| `4_cameras_advanced_camera_card` | six cameras in a 3 × 2 grid, one offline | Advanced Camera Card |
| `5_energy_power_flow_apexcharts` | power now and today's chart | Power Flow Card Plus, ApexCharts |
| `6_house_health_auto_entities` | 14 unavailable entities, grouped by domain | auto-entities (+ a native count) |
| `7_wallpanel_screensaver` | the idle screen with clock and readings | WallPanel |

Camera pictures are the owner's 19/11 mockup sheet's illustrations, labelled sample images;
the house's own camera photos are not used.

## Owner decisions needed before any of this is built

1. Allow custom cards in V3 (it is native-only by gate), and which of 1–7.
2. Install HACS (if missing) and the chosen cards on the Green.
3. Confirm the six entity IDs above.
4. Fix or replace the weather entity, if Clock Weather Card is wanted.
