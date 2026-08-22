# Home Assistant Health Report

**Snapshot:** `snapshots/2026-08-23-assist-context.json` — 2026-08-23, 04:31 AEST
**Scope:** 431 Assist-exposed entities; 76 reporting `unavailable`.

This report triages the `unavailable` entities in that snapshot and records
configuration defects visible from live state. Findings are graded by how much
the evidence actually supports them:

| Grade | Meaning |
| --- | --- |
| **Confirmed** | The snapshot alone establishes it. |
| **Likely** | Strong evidence, one plausible alternative remains. |
| **Recheck** | Probably normal for the capture time; needs a daytime snapshot. |

The snapshot was taken before sunrise, which matters for the solar findings.

---

## 1. Both emergency buttons are offline — Confirmed

**Severity: highest.** These are the only entities in the system that look like
a personal-alarm function, and both are dead.

| Entity | Domain | State |
| --- | --- | --- |
| Emergency Button Dad main | `event` | `unavailable` |
| Emergency Button Dad Cloud connection | `binary_sensor` | `unavailable` |
| Emergency Button Mum main | `event` | `unavailable` |
| Emergency Button Mum Cloud connection | `binary_sensor` | `unavailable` |

Unlike the door sensors below, these have **no healthy duplicate entity** — so
this is not merely a stale registry entry. Working TP-Link child devices report
`Cloud connection: on` plus a `Signal level`; both emergency buttons report
neither.

Most likely causes, in order: flat button batteries, or the buttons were paired
to the `Tapo H200` hub that also appears offline (finding 2).

**Recommended action (needs owner):** physically press each button and confirm
it responds, replace the cell (CR2032-class) if not, and re-pair to the H100
hub. Nothing in this repository should be automated against these entities until
they report a live state.

Changing or adding automation around a personal-alarm device falls under the
approval boundary in `CLAUDE.md`, so no automation has been written for these.

## 2. `Tapo H200` hub appears offline while `H100` is healthy — Likely

| Entity | State |
| --- | --- |
| TP-LinkHub H100 Cloud connection | `on` |
| TP-LinkHub H100 Signal level | `3` |
| TP-LinkHub H100 Overheated | `off` |
| TP-LinkHub H100 Pair new device | `unknown` (stateless — normal) |
| TP-LinkHub Alarm | `unavailable` |
| Tapo H200 Pair new device | `unavailable` |

Two hubs are configured. The H100 is fully healthy; every entity attributable to
the H200 is unavailable. `K/Smart Button main` and the emergency buttons —
the child devices with no healthy counterpart — are consistent with having been
paired to the H200.

**Recommended action (needs owner):** confirm whether the H200 is still
physically installed and powered. If it has been retired, its config entry
should be removed in Home Assistant, which also clears finding 3's orphans.

## 3. Duplicate TP-Link/Tapo integrations leaving orphaned entities — Confirmed

Six devices expose **two entities with the identical friendly name**, one
healthy and one permanently `unavailable`:

| Name | Healthy | Orphan |
| --- | --- | --- |
| B/Contact Sensor Door | `off` | `unavailable` |
| F/Contact Sensor Door | `off` | `unavailable` |
| M/Contact Sensor Door | `off` | `unavailable` |
| K/Bot P100 | `on` | `unavailable` |
| K/Coffee P100 | `on` | `unavailable` |
| K/Top P100 | `on` | `unavailable` |
| G/Printer P100 | `off` | `unavailable` |
| Tapo C420 - South Wall Battery | `100` | `unavailable` |

The cameras show the same split under two naming conventions — `Tapo C420 East
Wall Battery` reports `65 %` while `Tapo C420 - East Wall Battery` (hyphenated)
is `unavailable`; the hyphenated variant also contributes the unavailable
`Motion detection` / `Person detection` **switches**, while the healthy
integration provides working `Motion Detection` / `Person Detection`
**selects**.

This is the signature of two integrations covering the same hardware — most
likely the built-in TP-Link/Tapo integration alongside a HACS Tapo integration,
or a stale second config entry.

**Why it matters beyond tidiness:** an automation or dashboard card that picks
the orphaned entity ID will silently never fire, and both entities present the
same name in the UI picker, so choosing the wrong one is easy.

**Recommended action (needs owner):** identify the redundant config entry and
remove it. Deleting live entities is an approval-boundary action, so this is
recorded rather than performed.

## 4. Backyard freezer power monitoring is down — Confirmed

| Entity | State |
| --- | --- |
| B/Freezer/EnergyMonitor/P110M | `unavailable` |
| B/Freezer/EnergyMonitor/P110M Energy | `unavailable` |
| B/Freezer/EnergyMonitor/P110M Energy difference | `unavailable` |

The Garage equivalent is healthy for comparison (`G/Monitor Freezer P110M`: on,
232.4 V, 1.7 W — a low draw consistent with the compressor resting between
cycles).

With the Backyard plug offline there is no signal if that freezer loses power.
The Garage unit's `Overheated` sensor is also `unavailable` while its
`Overloaded` sensor works.

**Recommended action:** restore the Backyard P110M (power-cycle / re-add to
Wi-Fi). Once it reports reliably, a freezer-failure alert is worth adding — see
`docs/improvement_backlog.md`.

## 5. Outdoor camera coverage is partly degraded — Confirmed

`Tapo C420 - East Wall` and `Tapo C420 - South Wall` contribute unavailable
control switches (finding 3), and two older camera entities are fully dead:

| Entity | Area | State |
| --- | --- | --- |
| Tapo_C200_5C35 Motion | Backyard | `unavailable` |
| Tapo_Camera Motion | Backyard | `unavailable` |
| Tapo_Camera Battery | Backyard | `unavailable` |

The four camera *streams* themselves are healthy (`idle`) — Stockroom, East,
South and North Wall. The underscore-named entities look like leftovers from an
earlier camera setup.

Camera and security changes are approval-boundary work; no changes made.

## 6. Solar inverter reporting nothing — Recheck after sunrise

All twelve `Primo 5.0-1 (1)` and `SolarNet` entities are `unavailable`. The
snapshot was taken at **04:31, before sunrise**, and Fronius inverters power
down overnight and drop off the network — so this is very likely normal.

Two details argue for a daytime recheck anyway:

- `SolarNet Grid import tariff`, `Grid export tariff` and `Meter mode` come from
  the smart meter, which is normally mains-powered and reachable 24/7.
- The Solcast forecast entities are healthy and predict `13.3 kWh` remaining
  today, so a daytime snapshot will clearly distinguish "inverter asleep" from
  "integration broken".

**Action:** capture a snapshot around midday and rerun the inventory. If the
`Primo` entities are still unavailable in daylight, the integration is broken.

## 7. Orphaned Hue light entities — Likely

Group entities are alive while individual bulb entities are not:

| Entity | Area | State |
| --- | --- | --- |
| Living room (×2, group) | Living Room | `on` |
| Living Room Inner Left / Inner Right / Outter Left / Outter Right | Living Room | `unavailable` |
| Dining (×2, group) | Dining | `on` |
| Dining Light Left / Dining Light Right | Dining | `unavailable` |
| Corridor 1 / Corridor 2 | Dining | `unavailable` |
| Hue ambiance spot 1, Hue ambiance spot 1, Hue ambiance spot 3, Hue ambiance spot 4 | — | `unavailable` |

Two things point to orphaned registry entries rather than genuinely offline
bulbs: the Hue bridge is clearly online (its `Hue Bridge Automation: …` entities
are reporting `on`/`off` normally), and a Hue group cannot report `on` unless at
least one reachable member is lit. **`Hue ambiance spot 1` appears twice and
`spot 2` does not exist at all**, which is a duplicate-registry pattern, not a
lighting pattern.

The alternative — that these bulbs sit on a wall switch currently cut at
04:31 — cannot be ruled out from one overnight snapshot.

**Action:** confirm with a daytime snapshot. If they are still unavailable while
the groups are lit, delete the orphaned entities (approval-boundary).

## 8. Battery levels needing attention — Confirmed

| Entity | Level |
| --- | --- |
| Tapo C425 - North Wall Battery | **24 %** |
| Front Door Battery | **24 %** |
| RingRing Battery | **28 %** |
| Raymond's iPad Battery Level | 35 % |
| Living Room Switch / LivingroomSwitch Battery | 58 % |

The first three are security-relevant (an outdoor camera and the front-door
hardware) and should be charged or replaced soon. There is no low-battery alert
in the system today; one is proposed in the backlog.

## 9. Unit-of-measurement defect — Confirmed

`Parents Room Motion Sensor Battery voltage` reports **`3000 V`**.

The value is millivolts published with a volts unit. For comparison, `Aqara
Roller Shade Driver E1 Battery voltage` correctly reports `3.00 V` for the same
class of coin cell. A 3000 V reading also distorts any auto-scaled voltage graph
it appears on.

**Fix:** override the unit to `mV` in the entity settings, or divide by 1000 in
a template sensor.

## 10. Malformed sensor: `sensor Cost` — Confirmed

| Field | Value |
| --- | --- |
| Name | `sensor Cost` |
| State | `unknown` |
| Unit | `AUD` |
| Device class | `monetary` |
| Area | none |

The friendly name is the literal word "sensor" plus "Cost", which is what Home
Assistant produces when a template or utility-meter sensor is defined without a
proper `name`. It has never produced a value.

**Fix:** locate the defining config (likely a `utility_meter` cost sensor or an
Energy-dashboard cost entity), give it a real name, and either repair its source
or remove it.

## 11. Area assignment inconsistencies — Confirmed

- **`55" QLED 4k AI`** — three `media_player` entities in **Parents Room**, but
  its `remote` and a fourth `media_player` in **Ray Bedroom**. One physical TV
  is split across two areas, so neither area's "turn off everything" grouping is
  complete.
- **`F/Contact Sensor Door`** — healthy copy in **Living Room**, orphan copy
  with no area. **`M/Contact Sensor Door`** — healthy copy in **Parents Room**,
  orphan with no area.
- **All six cameras sit in an area called `Network`**, alongside AdGuard and
  router entities, rather than the physical locations their names describe
  (Stockroom, East/South/North Wall). Area-based dashboard cards and voice
  commands like "show me the backyard camera" will not resolve correctly.
- **72 entities have no area at all** (17 % of the system), including the
  `NightLight`, `BedlightSwitch` and `LivingroomSwitch` entities that clearly
  belong to known rooms.

**Fix:** reassign areas in the Home Assistant UI. This is low-risk and improves
both voice control and dashboard generation, but it changes live registry data,
so it is listed rather than performed.

## 12. Presence Multi-Sensor FP300 is entirely offline — Confirmed

All twelve entities of the `Presence Multi-Sensor FP300` in **Ray Bedroom** are
`unavailable`: occupancy, temperature, humidity, illuminance, battery, battery
voltage, sensitivity and four identify buttons. Nothing from this device is
reporting.

This is a whole-device failure rather than an orphaned-entity artifact — there
is no healthy duplicate set, and the device's own battery sensor is unavailable
so its charge state is unknown.

Ray Bedroom retains working occupancy coverage from other sensors, so this is
not urgent, but any automation depending on FP300 occupancy is silently dead.

**Recommended action:** power-cycle or recharge the FP300 and confirm it
rejoins. If it has been retired, remove its config entry (approval-boundary).

---

## Summary of `unavailable` entities by cause

| Cause | Count | Grade |
| --- | ---: | --- |
| Duplicate/orphaned TP-Link & Tapo entities (findings 2, 3, 5) | 26 | Confirmed |
| Orphaned Hue bulb entities (finding 7) | 12 | Likely |
| Presence Multi-Sensor FP300 offline (finding 12) | 12 | Confirmed |
| Solar inverter asleep overnight (finding 6) | 12 | Recheck |
| Other single devices (Pogo, Kogan Tv, R/Laptop P110M, iPhone kiosk sensors) | 7 | Confirmed |
| Emergency buttons (finding 1) | 4 | Confirmed |
| Backyard freezer monitor (finding 4) | 3 | Confirmed |
| **Total** | **76** | |

### Not a fault

49 entities report `unknown`, but almost all are stateless `button`, `event`,
`scene`, `select` and `notify` entities that have no state until first use. The
inventory generator does not flag these. The one genuine exception is
`sensor Cost` (finding 10).

## What needs the owner

Every remaining action in this report either deletes live entities, changes
registry data, or touches security and personal-alarm hardware — all
approval-boundary items under `CLAUDE.md`. They are documented here rather than
executed. The highest-priority one by a wide margin is **finding 1: both
emergency buttons are non-functional.**
