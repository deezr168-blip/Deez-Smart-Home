# CasaRay live entity reconciliation — 2026-09-17

Reconciles `dashboards/casaray_v2.yaml`'s 434 entity references against live
Home Assistant state via the connected `Home_Assistant` MCP server.

**Authorities, as instructed.** `docs/live/states_export_2026-09-05.txt` (970
entities, 12 days old) is the authority for canonical entity IDs. The MCP
server is the authority for current state and availability. No ID was inferred
from name similarity alone; a mapping was accepted only where the friendly
name is **unique in the export** and domain and area both agree.

No dashboard file was changed. No new export was created. No URL, token or
credential was written to disk or used — the MCP server was already connected.

## Method, and one correction worth recording

The MCP server returns friendly name, domain, area, state and attributes. It
does **not** return entity IDs, so every mapping here runs name+domain+area
against the export.

**The `name` filter is unreliable and produced four false negatives.** Queries
for `Contact Sensor`, `LPH-SE DCD9`, `Tapo C420` and `H100` each returned
*"No exposed entities matched"*. All four families are in fact exposed and
returned normally under `domain`+`area` queries. Had that first result been
taken at face value, 21 references would have been misfiled as unverifiable
and several genuine recoveries missed. **Only `domain`/`area` queries are
trusted below**; the one `name`-style conclusion retained is the `input_text`
result, which came from a domain query.

Exposure is per-entity, so an entity absent from a domain+area slice may be
unexposed *or* may not exist. Absence is therefore never read as deletion.

## 1. Confirmed live mappings

**20 of the 29 export-`unavailable` references have recovered** and are
serving real values now. All 20 have a unique friendly name in the export with
domain and area agreeing.

| Entity ID | Live state |
|---|---|
| `binary_sensor.b_contact_sensor_cloud_connection` | `on` |
| `binary_sensor.f_contact_sensor_cloud_connection` | `on` |
| `binary_sensor.m_contact_sensor_cloud_connection` | `on` |
| `binary_sensor.network_tp_linkhub_h100_cloud_connection` | `on` |
| `binary_sensor.lph_se_dcd9_pump` | `on` |
| `camera.tapo_c420_east_wall_hd_stream_direct` | `idle` |
| `camera.tapo_c420_south_wall_hd_stream_direct` | `idle` |
| `light.tapo_c420_east_wall_floodlight_timed` | `off` |
| `light.tapo_c420_south_wall_floodlight_timed` | `off` |
| `number.lph_se_dcd9_plants_age` | `76` d |
| `select.lph_se_dcd9_light_brightness` | `high` |
| `select.lph_se_dcd9_light_mode` | `vegetable` |
| `sensor.b_contact_sensor_signal_level` | `1` |
| `sensor.f_contact_sensor_signal_level` | `3` |
| `sensor.m_contact_sensor_signal_level` | `3` |
| `sensor.network_tp_linkhub_h100_signal_level` | `3` |
| `switch.lph_se_dcd9_power` | `on` |
| `switch.lph_se_dcd9_pump_cycling` | `on` |
| `switch.tapo_c420_east_wall_privacy` | `off` |
| `switch.tapo_c420_south_wall_privacy` | `off` |

The whole LPH-SE DCD9 plant unit (6 entities), both Tapo C420 cameras with
their floodlights and privacy switches (6), all four cloud-connection and all
four signal-level sensors (8) are back.

**17 of the 30 export-`unknown` references are live and healthy.** Their
`unknown` is semantics, not a fault: a `scene` entity's state is the timestamp
it was last activated, and a `button`'s is the timestamp it was last pressed.
`unknown` means "not triggered since the last restart".

- 16 scenes — 3 Ray Bedroom (Silverstone, Starlight, Suzuka), 6 Dining,
  7 Living room. All 16 matched by unique name + area.
- `button.bedroom_parents_room_ac_reset_filter` — live, `unknown`.

## 2. Confirmed unavailable / stale mappings

**6 references are genuinely still down.** Each has a unique export name with
domain and area agreeing, and the live entity reports `unavailable`.

| Entity ID | Friendly name | Area |
|---|---|---|
| `light.living_room_hue_ambiance_spot_1` | Living Room Inner Left | Living Room |
| `light.living_room_hue_ambiance_spot_2` | Living Room Inner Right | Living Room |
| `light.living_room_hue_ambiance_spot_3` | Living Room Outter Left | Living Room |
| `light.living_room_hue_ambiance_spot_4` | Living Room Outter Right | Living Room |
| `light.kogan_tv` | Kogan Tv | Guest Room |
| `media_player.pogo` | Pogo | Guest Room |

The four Living Room Hue spots are one fixture group and have been down since
at least 05/09 — worth a physical check rather than a dashboard change.

## 3. Ambiguous mappings — NOT resolved

**3 references cannot be mapped safely.** This is `CR-190` exactly, and it is
live right now rather than historical.

Each door sensor name exists **twice** in the export, same name, same area,
same domain:

| Referenced by dashboard | Twin in export |
|---|---|
| `binary_sensor.b_contact_sensor_door` | `binary_sensor.backyard_b_contact_sensor_door` |
| `binary_sensor.f_contact_sensor_door` | `binary_sensor.front_door_f_contact_sensor_door` |
| `binary_sensor.m_contact_sensor_door` | `binary_sensor.master_bedroom_m_contact_sensor_door` |

Live, each name returns **two entities — one `off`, one `unavailable`**. So one
of each pair is a working door sensor and the other is dead. Because the MCP
server does not return entity IDs and the names are identical, **there is no
way from here to tell which ID is the live one.** Guessing has a 50% chance of
pointing three security-relevant cards at a dead entity, so no mapping is made.

This matters more than the count suggests: it means the dashboard may currently
be reading the dead twin of each door sensor, which would make the door state
on the Security band wrong rather than merely stale.

Resolution needs entity IDs — Developer Tools → States, or a REST
`/api/states` call. It is the single highest-value unblock in this report.

A related duplicate family, not referenced by the dashboard and therefore not
a defect, is recorded so it is not rediscovered: `light.master_bedroom_hue_
ambiance_spot_1`, `_1_2`, `_3`, `_4` carry the names "Hue ambiance spot 1/1/3/4"
but sit in **Living Room** despite `master_bedroom` in the ID, and two of them
share one name. `light.living_room` and `light.living_room_living_room` are
likewise both "Living room", both Living Room, both `ok`, both `on` at
brightness 227.

## 4. Entities present live but absent from the dated export

**None found.** 111 distinct live friendly names were collected across
`person`, `climate`, `scene`, `camera`, and per-area slices of
`binary_sensor`, `sensor`, `switch`, `light`, `number`, `select`, `button` and
`media_player`, then checked against all 970 export names. Every one was
present.

Three slices matched exactly, count for count: 29 scenes ↔ 29 export scene
rows with identical names; 3 persons ↔ 3; 10 Living Room lights ↔ 10.

**This is a bounded result, not a clean bill of health.** It covers only the
areas and domains queried, and only entities exposed to Assist. It shows no
drift where it can see, which is a reason to trust the 05/09 export for ID
lookups — not a proof that nothing was added elsewhere.

## 5. Counts

| Export status | Total | Resolved safely | How |
|---|---:|---:|---|
| `unknown` | 30 | **17** | 16 scenes + 1 button confirmed live; `unknown` is by design |
| | | 13 | unverifiable — 12 `input_text` (domain not exposed), 1 `sensor.g_printer_p100_auto_off_at` (not in exposed slice) |
| `unavailable` | 29 | **26** | 20 recovered, 6 confirmed still down |
| | | 3 | ambiguous — door sensors, see §3 |
| **Total** | **59** | **43 (73%)** | |

Of the 16 unresolved: 13 unverifiable from this environment, 3 blocked on
entity-ID disambiguation.

No reference is missing from the export (`MISSING: 0`), so the validation gate
stays green either way; these are accuracy findings, not build breaks.

## Recommended next steps — none taken yet

1. **Disambiguate the three door sensors.** Needs IDs. Blocked on owner.
2. **Re-check the four Living Room Hue spots physically.** Down 12+ days;
   a dashboard change cannot fix a dark fixture.
3. **Consider teaching `reconcile_entities.py` that `scene` and `button`
   `unknown` is benign.** 17 of the 30 `unknown` are noise in the current
   count, which hides the 13 that are genuinely unverified.
4. **Kogan Tv and Pogo** are honestly dead; the existing convention (grey icon,
   honest secondary) already covers them. Verify the cards say so.

The 20 recovered entities need no dashboard change — those cards should simply
be showing real values now. Worth confirming on the wall iPad, which this
environment cannot see.
