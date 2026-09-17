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

---

# Addendum — classifier rebuild, same day

`reconcile_entities.py` now classifies every reference into six buckets rather
than three, and the counts above are reproducible from the repository instead
of living only in this document. No dashboard file was changed.

## New counts

```
entity references        : 434  (+4 service names)
counts: live 363 / recovered 20 / benign-unknown 17 / unavailable 6
        / ambiguous 15 / unresolved 13
accounted for            : 434 of 434
```

Against the old `ok 375 / unknown 30 / unavail 29`:

| Bucket | Count | Was |
|---|---:|---|
| live | 363 | part of `ok` 375 |
| recovered | 20 | counted as `unavail` |
| benign-unknown | 17 | counted as `unknown` — never a fault |
| unavailable | 6 | the real remainder of `unavail` 29 |
| ambiguous | 15 | **invisible** — 12 were inside `ok` |
| unresolved | 13 | the real remainder of `unknown` 30 |

The legacy dashboard, reconciled with the same tool:
`live 121 / recovered 8 / benign-unknown 1 / unavailable 7 / ambiguous 14 /
unresolved 13`.

## The significant new finding: 15 ambiguous, not 3

§3 above found three door sensors sharing a friendly name with a stale twin.
That search only covered the 59 `unknown`/`unavailable` references. Running the
duplicate check across **all 434** finds **15**, and twelve of them were sitting
in the `ok` bucket being reported as perfectly healthy.

Every one follows the same shape — `X` beside `<area>_X`, the signature of an
integration re-added without the old entities being removed:

| Referenced | Twin |
|---|---|
| `binary_sensor.b_contact_sensor_door` | `binary_sensor.backyard_b_contact_sensor_door` |
| `binary_sensor.f_contact_sensor_door` | `binary_sensor.front_door_f_contact_sensor_door` |
| `binary_sensor.m_contact_sensor_door` | `binary_sensor.master_bedroom_m_contact_sensor_door` |
| `binary_sensor.k_motion_sensor_motion` | `binary_sensor.kitchen_k_motion_sensor_motion` |
| `light.bedroom_nightlight` | `light.master_bedroom_nightlight` |
| `light.dining` | `light.dining_dining` |
| `light.living_room` | `light.living_room_living_room` |
| `switch.g_printer_p100` | `switch.guest_room_g_printer_p100` |
| `switch.k_bot_p100` | `switch.kitchen_k_bot_p100` |
| `switch.k_coffee_p100` | `switch.kitchen_k_coffee_p100` |
| `switch.k_top_p100` | `switch.kitchen_k_top_p100` |
| `sensor.tapo_c420_south_wall_battery` | `sensor.tapo_c420_south_wall_battery_2` |
| `media_player.living_room_tv_samsung_q9_series_65` | `media_player.tv_samsung_q9_series_65` |
| `media_player.q70f8036` | `media_player.55_qled_4k_ai`, `media_player.master_bedroom_55_qled_4k_ai` |
| `zone.home` | `zone.home_2` |

The four `switch.k_*` and `switch.g_printer_p100` entries matter most: those are
**appliance switches** — kettle, coffee, printer. A card bound to the dead twin
of a kettle switch reports the wrong power state, and per CLAUDE.md appliances
are the place to be conservative.

`media_player.q70f8036` is worth a note: its twin `media_player.55_qled_4k_ai`
is `unavailable` **in the same area**, so the referenced ID appears to be the
surviving one. That is a reasonable inference, not a verification, and it is
recorded as ambiguous regardless.

**Ambiguity is a WARN, not a build failure.** The IDs are exact and present, so
the gate stays green; failing on them would block all work to report a risk
that needs a human with Developer Tools to resolve.

**Cross-domain name sharing is not ambiguity.** The first implementation keyed
on friendly name alone and returned 20 hits, five of which were one appliance
appearing under two domains — a TV is a `media_player` and a `remote`, an air
purifier is a `fan` and a `switch`. Keying on `(domain, name)` drops those five
and keeps every real collision.

## Benign-unknown is narrowly scoped, and now tested

`BENIGN_UNKNOWN_DOMAINS = {"scene", "button"}`, and only in combination with
`unknown` — a `scene` that is `unavailable` is still a fault.

`scripts/test_reconcile_classify.py` gates this, and runs inside
`ha_validate.sh` before the counts are printed. It asserts that 21 state-bearing
domains still fault on `unknown`, that `unavailable` never becomes benign, that
the benign set has not drifted, that cross-domain names are not ambiguous, and
that the overlay cannot recount an already-`ok` entity. Verified by mutation:
adding `sensor` to the benign set fails the gate with both the domain-level and
set-level assertions.

## Evidence overlay

`docs/live/observations_2026-09-17.txt` — 26 dated observations, the
machine-readable form of §1 and §2. It is **not** a states export: it adds no
entity ID of its own, every ID in it came from `states_export_2026-09-05.txt`,
and that file remains the sole ID authority. It is optional; without it the
tool still runs and `recovered` is simply 0.

## Card honesty check — `light.kogan_tv` and `media_player.pogo`

Requested verification. Read-only; nothing was changed.

**`light.kogan_tv` — honest in all four places.**

| Line | Card | Treatment |
|---|---|---|
| 4348 | markdown | three-branch; falls to "No reading · TV backlight not reporting" / "无数据" |
| 4372 | tile | `card_mod` dashed border + grey on `unavailable/unknown/none` |
| 8949 | tile | same dashed-grey treatment |
| 9330 | conditional tile | "Kogan TV offline", shown only when `unavailable` |

**`media_player.pogo` — honest in three places, with one gap.**

| Line | Card | Treatment |
|---|---|---|
| 8911 | media-control | bare, but 8915 markdown immediately follows: "Pogo is not reporting, so the controls above will not work" / "Pogo 目前未上报状态" |
| 9319 | conditional tile | "Pogo offline" when `unavailable` |
| 8800 | `dead` list | listed as a known-dead device |
| **4385** | **media-control** | **bare — no caveat, no `card_mod`, no dashed treatment** |

The Entertainment block at 4385 carries the same `media-control` card as 8911
but without the explanatory markdown its twin has. Live, Pogo is `unavailable`,
so that card renders transport controls for a device that cannot answer — the
one place either entity currently asserts more health than it has.

Not fixed, per instruction. The fix is small and has an in-repo precedent: the
markdown caveat at 8915, copied beneath 4385.

## Observation, not acted on

The offline conditional tiles at 9310, 9319 and 9330 use `color: orange`.
CLAUDE.md's semantic colour system assigns **grey** to "unavailable, offline,
unknown, no data" and reserves amber for "active, running, currently on", with
the worked example that "an inverter that is not answering is grey". These
tiles are internally consistent with each other but not with that rule. Flagged
for a decision rather than changed, since it is a visual call across several
cards and the mockups are the authority.

## Next, still blocked on the owner

1. **Disambiguate the 15** — needs entity IDs from Developer Tools → States.
   The five appliance switches are the ones to do first.
2. **Four Living Room Hue spots** — still `unavailable`, physical check.
3. **Pogo card at 4385** — one markdown card, ready when approved.
