# CasaRay V3 — build status

**DEVELOPMENT ONLY — NOT DEPLOYED.** Not registered, synced, reloaded or seen
on any device. Live Home Assistant was not used to build or validate V3.

Branch: `feature/casaray-v3-build` (from `casaray-v3-design` `27f3fed`).

## View status (priority order)

| # | View | Status | Notes |
|---|---|---|---|
| 1 | Home | **native** | 9 bands; V3-007 shape; all 16 V2-only entities placed (below); classic `v2-home` kept |
| 2 | Lighting | **native** | all V2 lights + 29 scenes; wall switches read-only |
| 3 | Climate | **native, HVAC read-only** | V3-008 not satisfied in Lovelace; controls via classic Parents' room |
| 4 | Cameras | **native** | 6 cameras, state in words; streams via carried webrtc subviews |
| 5 | Energy | **native** | Powerpal + Fronius only; monitored-circuit total; export and battery stated as no source / not installed (V3-003) |
| 6 | Security | carried (V2) | sirens keep V2 treatment; rebuild needs owner review of siren UX |
| 7 | People / household | carried (V2) | |
| 8 | Bills, Bill setup | carried (V2) | baseline lacks the "silent bill" honesty fix — see below |
| — | Rooms ×8, Network, House health, Alerts, Automations, Entertainment, 6 camera subviews | carried (V2) | |

Per-view entity counts and every V2 entity not yet on a native view:
`VIEW_INVENTORY.md` (generated).

## V2 Home entities: where the 16 went (01/11/26)

All 16 have a verified V3 place, and none is retained or blocked. The build
checks each row of `src/casaray_v3/manifest.yaml` `migration` against the
generated dashboard and refuses to run on a false or missing one, so the table
in `VIEW_INVENTORY.md` cannot drift into a claim.

| Coverage | Count | Where |
|---|---|---|
| native | 10 | **Climate**: Parents' room occupancy, dining temperature · **Energy**: monitored total (new), solar expected, freezer and Ray's-room power · **Cameras**: doorbell and east-wall batteries · **Lighting**: bulb-power switch (read-only) · **Home**: unpaid-bills count (new, in Needs attention) |
| carried | 6 | **Security**: kitchen, living-room and dining motion · **Network**: printer plug's cloud link · **Rooms**: roller shade (Ray's room), printer plug (Guest room) |

Changed in this batch:

- `sensor.casa_monitored_power` is on native Energy, at the top of Monitored
  circuits beside both circuits it totals, with V2's footnote "two circuits
  are metered, not the whole house" (V3-007 moved it off Home).
- `sensor.bills_unpaid_count` is back in Home's Needs attention, where V2 raised
  it (CR-243). The earlier note said "→ Bills", but the carried Bills board
  never reads this sensor. Its definition lives on the instance, not in git,
  so a zero counts as an answer only while all six paid flags answer;
  otherwise it is "not reporting". A count above zero is always raised.
- Fix: native Home's roller-shade battery alert said "Living room"; the export
  puts the shade in Ray's room.

Still open:

- The 6 carried entities become native when Security, Network and the room
  boards are rebuilt; until then they render as V2 (V2 controls included).
- No Appliances board exists in V2 or V3. The freezer and printer plugs live on
  Energy, Garage, Guest room and Network; a dedicated board would be a new
  destination (owner call).
- Not on native Home by design: Recent activity (→ House health, V3-007, not
  rebuilt yet) and the language toggle button (replaced by per-locale
  dashboards). V2's twelve conditional alert cards are one Needs-attention list.
- `v2-home` stays until native parity is verified on a device.

## Known discrepancies carried from the baseline

- `recovery/casaray-continuation` and `autonomous/casaray-dev` hold a newer
  28-view V2 (blob `bb50feb`) with honesty fixes the pinned baseline lacks:
  silent bill helpers showing "No data", unanswered bills blocking the
  all-paid message, People "No location data". Carried Bills / People views
  inherit the baseline behaviour. Folding those fixes into native rebuilds is
  the safe route; changing the baseline is the owner's call.
- V2 "All lights off" also turned off `switch.mainroomlight_switch_1` (bulb
  power). V3-native drops that; the classic view still has it.

## Owner decisions needed (none block offline work)

1. Cantonese script: Traditional HK was used for `yue`. Confirm, or ask for
   Simplified-script Cantonese.
2. Native review of the `yue` and `km` catalogues.
3. Whether to keep the `zh-Hans` locale (V2 parity) as a fourth dashboard.
4. Runtime language switching would need a new `input_select` helper
   (helpers are out of scope today).
5. Kiosk mode: V2 baseline has none; restore for V3 or not.

## Live-only verification (cannot be done offline)

Rendering on the wall iPad and iPhone, the real column count, custom-card and
`card_mod` installation, theme install, entity availability today, and anything
the Green's recovery changes. None of it is claimed.
