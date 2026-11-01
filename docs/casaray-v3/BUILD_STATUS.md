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
| 6 | Security | **native** (CR-V3-17) | doors, motion, cameras, sirens, detection; sirens are the V2 tiles byte for byte; camera switches read-only (controls on classic `v2-security`) |
| 6a | Network | **native** (CR-V3-17) | 14 cloud-linked devices online / offline / not reporting, Wi-Fi signal, devices HA can read; read-only, as V2 |
| 6b | Ray's room, Guest room | **native** (CR-V3-17) | every V2 device control kept (allowlisted switches, blind features, scenes, media); bulb-power wall switch read-only |
| 7 | People / household | **native** (CR-V3-19) | presence never inferred from silent people; `zone.home` beside them, a zero only while all answer |
| 8 | Bills, Bill setup | carried (V2) | baseline lacks the "silent bill" honesty fix — see below |
| 6c | Rooms index, Living room, Kitchen, Dining, Parents' room, Garage | **native** (CR-V3-18) | every V2 room control kept or, where sensitive, read-only with the V2 control one tap away on the classic subview; Parents' room air-con read-only (V3-008) |
| 6d | House health, Alerts | **native** (CR-V3-19) | V2's alert conditions, severities and thresholds; unverified summary sensors retained on classic (CR-213); HA system updates read-only |
| — | Automations, Entertainment, 6 camera subviews | carried (V2) | |

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
| native since CR-V3-17 | 6 | **Security**: kitchen, living-room and dining motion · **Network**: printer plug's cloud link · **Ray's room**: roller shade · **Guest room**: printer plug — each rebuilt natively, so all 16 are now native |

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

- ~~The 6 carried entities become native when Security, Network and the room
  boards are rebuilt.~~ Done in CR-V3-17 (below).
- No Appliances board exists in V2 or V3. The freezer and printer plugs live on
  Energy, Garage, Guest room and Network; a dedicated board would be a new
  destination (owner call).
- Not on native Home by design: Recent activity (→ House health, V3-007, not
  rebuilt yet) and the language toggle button (replaced by per-locale
  dashboards). V2's twelve conditional alert cards are one Needs-attention list.
- `v2-home` stays until native parity is verified on a device.

## CR-V3-17: Security, Network, Ray's room and Guest room rebuilt natively (01/11/26)

Every V2 entity of the four views is on its native rebuild (the build checks
it; no migration row is needed). Each keeps its V2 original as a classic
`v2-<path>` subview, linked from its More boards band, until parity is seen on
a device.

| View | What is native now | Safety behaviour |
|---|---|---|
| Security | chips (doors open, motion, cameras online, alerting, internet), Needs attention (doors, cameras, a sounding siren), doors + 24 h history, motion + 12 h history, camera health with a tile to each stream page, detection settings | **Sirens: the three V2 tiles copied byte for byte** (`v2_verbatim`): tap opens details, the icon does nothing (Home Assistant's tile default for `siren`), same red, same full-width-of-a-half-section shape. No arming, disarming or emergency action. The 12 privacy / detection / alert / chime / alarm switches are read-only and open the classic `v2-security`, where V2's controls are unchanged. |
| Network | chips (internet, cloud-linked online, remote access, Zigbee hub), internet tiles, Wi-Fi signal, each of 14 cloud-linked devices as Online / Offline / Not reporting with its signal when it reports one, "devices HA can read" by kind, what is not measured | read-only, as V2 |
| Ray's room | chips (light, blind, desk power, overload), lights with brightness, the 6 V2 scenes, roller shade with V2's open/close and position features, grow unit, desk plug and its readings, plug settings | switches keep V2's exact tile behaviour (tap = details, icon = toggle) **only** because each is in the manifest's `controls`; the bulb-power wall switch is read-only (owner rule, as on Lighting) |
| Guest room | chips (printer, TV backlight, internet), TV backlight, printer plug, Pogo media control, printer plug settings | as Ray's room |

Gated (`validate_dashboard.py` `tile_safety`, `tests/v3` `NativeRebuilds`):

- a siren tile may act only if it **is** the V2 tile (deep-equal);
- a switch may act only if it is in `controls`, behaves exactly as its tile on
  the named V2 view, and is not a protected class (privacy, detection,
  notification, chime, alarm, siren, or a bulb-power wall switch) — whatever
  the manifest says;
- every tile on a rebuilt view does what its V2 tile did, except those
  protected switches, which lead to the classic controls instead.

Also changed: a V3 sensor tile without a navigation target now opens its
details on tap, as a V2 tile does (history; read-only domains only, whose
dialog has no control). This touched 37 reading tiles on Home, Climate,
Cameras and Energy; nothing else on those views moved.

Found while doing this (V2 today, unchanged here): Home Assistant's tile card
toggles a `switch` on an icon tap when `icon_tap_action` is unset. So on V2
Security, tapping the icon of a camera privacy, detection or alert tile flips
it in one tap, although the V2 note says the tiles open details. V3 keeps those
read-only; the classic view carries V2's behaviour as it is. Worth an owner
look before V2 is retired or kept as the fallback.

Still carried after CR-V3-17: the room boards (rebuilt in CR-V3-18, below),
House health, Alerts, Automations, Entertainment, People, Bills and the six
camera stream subviews.

## CR-V3-18: the room boards rebuilt natively (01/11/26)

Rooms index, Living room, Kitchen, Dining, Parents' room and Garage are native.
Every V2 entity of each is on its rebuild, except `zone.home`, which stays on
the carried People board (a verified migration row; see below). Each keeps its
V2 original as a classic `v2-<path>` subview.

| View | Native now | Kept exactly as V2 | Read-only here (V2 control on the classic subview) |
|---|---|---|---|
| Rooms index | the eight room tiles (same entity, same page, icon inert, as V2), people home, internet, room conditions | every tile's tap target | — |
| Living room | room light + four Hue spots, six scenes, air purifier, air quality, sensors and history, TV, front-door camera and doorbell, power board, settings | brightness, fan-speed feature, scenes, media card, camera opens its stream, selects | 5 power-board sockets, child lock, Hue motion / light sensing, doorbell chime volume |
| Kitchen | chips, bench plugs, fridge, Electrolux sensor, motion and history, shopping list, plug settings | fridge / freezer setpoints (number feature), express mode, plug LEDs, auto-off timers | coffee machine and both bench plugs, and their auto-off switches |
| Dining | dining light, six scenes, sensors, pet feeder camera and settings | brightness, scenes, indicator light, feeder volume, video timestamp | bulb-power wall switch, feeder privacy and motion alarm, night vision, detection sensitivity, motion / light sensing |
| Parents' room | occupancy, temperature, humidity, air-con stated in words, sensors, emergency buttons (connectivity and signal), TV, power point, air-con maintenance | TV media card, TV light-sensor switch, firmware tile, filter reset (asks first, now localised), timer end shown only while the timer is on | **air-con** (V3-008; one large button opens the V2 thermostat), Climate React, AC timer, main light (bulb power), 5 power-point sockets |
| Garage | freezer status, electrical readings and history, settings | plug LED, power-protection and auto-off timer numbers | the freezer plug and its auto-off |

- **Allowlist additions (ordinary settings only):** kitchen and freezer plug
  LEDs, fridge express mode, TV light sensor, pet-feeder video timestamp.
- **New protected classes in the gate:** power-strip sockets, child locks,
  sensing switches, air-con switches, critical / unrecorded appliance loads,
  and camera / doorbell settings. These are read-only whatever the manifest
  says (`validate_dashboard.py`).
- **Climate's "Air-con controls (classic)" button now opens `v2-parents-room`**.
  This is the only change to an earlier native view, and it is tested in every
  locale.
- **`zone.home`:** native Rooms counts the three people (what answered)
  instead, because a zone count reads 0 while the people it counts are dark.
- **Owner call:** the parents' main light is a bulb-power wall switch, so
  native Parents' room has no light control. See DECISIONS V3-011.

Still carried: House health, Alerts, Automations, Entertainment, People, Bills,
Bill setup and the six camera stream subviews.

## CR-V3-19: House health, Alerts and People rebuilt natively (01/11/26)

All three are native, and each keeps its V2 original as a classic `v2-<path>`
subview.

| View | Native now | Not inferred | Read-only / retained |
|---|---|---|---|
| People | chips, presence (at home / away / not reporting), the three people, guest mode, the home-zone count, phone batteries and charging, Ray's distance and activity, 24 h presence history | a silent person is never "away"; "Nobody is home" only when all three answered; a zero zone is "Not confirmed" while anyone is silent | — (guest mode keeps V2's toggle as a manifest `controls` entry) |
| Alerts | count strip, Critical, Warnings and Information lists: V2's conditions and thresholds | the link and both emergency buttons: off is "not connected", dark or odd is "cannot be confirmed", raised and never folded into a count; "nothing needs attention" only when every check answered | no state-changing action exists (none in V2 either) |
| House health | unavailable entities (CR-200 caveat), updates available, internet, lights on and rooms with movement, 15 batteries (lowest, under 30%), network, named offline devices, backups and updates, wiring notes | lights and movement counted from verified entities, stating what answered | retained on classic: `house_status`, `active_rooms_count`, `house_lights_on` (CR-213); HA Core / Supervisor / OS updates read-only |

- **Migration:** `zone.home` moved from `carried` to `native` (People). The
  three summary sensors are `retained`, each with its reason in the manifest.
  Every other V2 entity of the three views is on its rebuild.
- **Gate:** HA system updates are a protected class; helper toggles are gated
  like switches; every native button press must ask first (all 18 native
  views pass, and a planted bare press is caught).
- **No earlier native view changed.** All 15, and their classic copies, are
  identical to `ddba0a6` in every locale.

Still carried: Automations, Entertainment, Bills, Bill setup and the six camera
stream subviews.

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
