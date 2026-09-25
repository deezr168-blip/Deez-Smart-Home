# CasaRay V3 — Home concepts (design review)

Three Home screen concepts at iPad landscape, 1180 × 820, for the owner to
choose between (`DECISIONS.md` V3-004). They are Design-canvas artboards
(`.dc.html`). The design artifact linked in the session is where they render.
These copies are the source record.

| File | Concept |
|---|---|
| `ConceptA.dc.html` | A — Minimal architectural |
| `ConceptB.dc.html` | B — Modern dark control centre |
| `ConceptC.dc.html` | C — Balanced premium family dashboard |

Each concept has a working EN / 中文 switch, and its toggles change mock
state only. No concept calls Home Assistant.

## Mock data and the entities behind it

All three concepts show the same snapshot: Thursday 25/09/26, 16:20.
Numbers are **mock**, and every one sits on an entity ID verified in
`docs/live/states_export_2026-09-05.txt`.

| On screen | Mock value | Entity |
|---|---|---|
| Weather | 17°, partly cloudy | `weather.forecast_home` |
| Ray / Ai / Vinh | home / home / away | `person.raymond_du`, `person.ai_q_huang`, `person.vinh_du` |
| Solar now / today | 1.62 kW / 14.2 kWh | `sensor.primo_5_0_1_1_ac_power`, `sensor.primo_5_0_1_1_energy_day` |
| Grid import now / today | 0.38 kW / 6.1 kWh | `sensor.powerpal_gateway_powerpal_power`, `sensor.powerpal_gateway_powerpal_daily_energy` |
| Export | no source entity | none — see V3-003 |
| Consumption | not measured | none — see V3-003 |
| Future battery | not installed | none |
| Living room / dining temperature | 21.4° / 20.8° | `sensor.living_room_living_hue_hue_sensor_temperature`, `sensor.living_room_living_room_temperature` |
| Parents' air-con | off, 23.2° (live value) | `climate.bedroom_parents_room_ac` |
| Front door battery | 12% | `sensor.front_door_battery` |
| Electricity bill | unpaid | `input_boolean.elec_bill_paid` |
| Cameras | 3 online, 2 offline, 1 unknown | `camera.front_door_live_view`, `camera.smart_pet_feeder`, `camera.tapo_c420_south_wall_hd_stream_direct` (online); `camera.tapo_c420_east_wall_hd_stream_direct`, `camera.tapo_c200_stockroom_hd_stream_direct` (offline); `camera.tapo_c425_north_wall_hd_stream_direct` (unknown) |
| Doors | no data | `binary_sensor.front_door_f_contact_sensor_door` and the other contact sensors |
| Scenes | — | `scene.living_room_living_room_bright`, `scene.dining_dining_relax`, `scene.bedroom_bedroom_nightlight` |
| Air purifier | on | `fan.living_room_air_purifier` |
| Language | EN | `input_boolean.chinese_dashboard` |

The "3 lights on · 9 not reporting" and "9 devices not reporting" counts are
illustrative mock totals, not computed from a snapshot.
