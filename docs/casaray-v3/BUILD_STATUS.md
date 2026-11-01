# CasaRay V3 — build status

**DEVELOPMENT ONLY — NOT DEPLOYED.** Not registered, synced, reloaded or seen
on any device. Live Home Assistant was not used to build or validate V3.

Branch: `feature/casaray-v3-build` (from `casaray-v3-design` `27f3fed`).

## View status (priority order)

| # | View | Status | Notes |
|---|---|---|---|
| 1 | Home | **native** | 9 bands; V3-007 shape; classic `v2-home` kept |
| 2 | Lighting | **native** | all V2 lights + 29 scenes; wall switches read-only |
| 3 | Climate | **native, HVAC read-only** | V3-008 not satisfied in Lovelace; controls via classic Parents' room |
| 4 | Cameras | **native** | 6 cameras, state in words; streams via carried webrtc subviews |
| 5 | Energy | carried (V2) | next native rebuild |
| 6 | Security | carried (V2) | sirens keep V2 treatment; rebuild needs owner review of siren UX |
| 7 | People / household | carried (V2) | |
| 8 | Bills, Bill setup | carried (V2) | baseline lacks the "silent bill" honesty fix — see below |
| — | Rooms ×8, Network, House health, Alerts, Automations, Entertainment, 6 camera subviews | carried (V2) | |

Per-view entity counts and every V2 entity not yet on a native view:
`VIEW_INVENTORY.md` (generated).

## Not yet migrated from V2 Home onto native Home (still on `v2-home`)

16 entities, all still on `v2-home` and on their own carried boards: motion
sensors, the roller shade, printer plug, freezer and Ray-bedroom power
readings, monitored power and solar-expected (→ Energy, V3-007), the unpaid
bills count (→ Bills), Parents' occupancy, Dining temperature, two batteries,
and the bulb-power switch. Also not on native Home: Recent activity (→ House
health, V3-007) and the language toggle button (replaced by per-locale
dashboards). V2's twelve conditional alert cards are consolidated into one
honest Needs-attention list. Exact list: `VIEW_INVENTORY.md`.

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
