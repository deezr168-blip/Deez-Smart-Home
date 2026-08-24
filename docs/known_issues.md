# Known Issues

Observations from live captures. Each entry says when it was seen and how, so
a later session can tell a real regression from a stale note.

**Nothing here has been acted on.** These are reports, not changes. Every one
of them touches live devices or the entity registry, which needs the owner's
decision.

Source: `GetLiveContext` capture, 2026-08-24 (431 exposed entities). Full data
in `entity_inventory.md`; how the capture was taken is in
`access_verification.md`.

---

## 1. Both emergency buttons report `unavailable`

**Priority: check this first.**

| Entity (friendly name) | Domain | State |
|---|---|---|
| Emergency Button Dad main | `event` | `unavailable` |
| Emergency Button Mum main | `event` | `unavailable` |
| Emergency Button Dad Cloud connection | `binary_sensor` | `on` |
| Emergency Button Mum Cloud connection | `binary_sensor` | `on` |

The split is what makes this worth attention: the **cloud connection** sensors
are healthy, while the **main button** entities — the ones that would carry an
actual press — are unavailable.

An `event` entity reads `unknown` before its first trigger, which is normal.
`unavailable` is not that: it means Home Assistant is not currently being given
the entity at all. So "never pressed yet" does not explain this.

Neither button has a live twin, so this is not the stale-duplicate pattern in
issue 2 either.

If anything depends on these buttons, it cannot fire while they are in this
state. Worth confirming at the devices — battery, pairing, and whether the
integration is still providing the button entity — rather than from Home
Assistant alone.

*Not diagnosed further from here: the available access path cannot see
integrations, devices, or the entity registry.*

## 2. Eleven entities look like orphaned duplicates

Of the 65 entities reporting `unavailable`, **11 have a same-name, same-domain
twin that is reporting normally**:

| Name | Domain | Area |
|---|---|---|
| F/Contact Sensor Door | binary_sensor | (none) |
| M/Contact Sensor Door | binary_sensor | (none) |
| B/Contact Sensor Door | binary_sensor | Backyard |
| G/Printer P100 | switch | Guest Room |
| K/Bot P100 | switch | Kitchen |
| K/Coffee P100 | switch | Kitchen |
| K/Motion Sensor Motion | binary_sensor | Kitchen |
| K/Top P100 | switch | Kitchen |
| Samsung Q9 Series (65) | media_player | Living Room |
| 55" QLED 4k AI (×2) | media_player | Parents Room |

That pattern almost always means a stale registry entry left behind when a
device was re-paired or an integration re-added, with the live twin doing the
real work.

This matters for reading the rest of the data: **Kitchen's failure rate drops
from 22% to 4%** once these are set aside — 4 of its 5 unavailable entities are
orphans. Kitchen is fine; it just looked broken.

It also matters for voice control and automations: a duplicate name is
ambiguous, and an automation pointed at the dead half of a pair will silently
never fire.

Cleanup is a registry deletion, so it needs your decision — and confirming
which half of each pair is the live one first.

## 3. The Fronius solar integration appears to be down

**All 12 offline entities in the Energy area are one integration:**

- `Primo 5.0-1 (1)` — AC current, AC power, DC current, DC voltage, Energy day,
  Energy year, Total energy
- `SolarNet` — CO₂ factor, Grid export tariff, Grid import tariff, Meter mode,
  Power photovoltaics

None have live twins. Twelve sensors from one inverter family failing together
points at a single dead integration or an unreachable inverter, not twelve
faults.

Worth prioritising because solar data degrades quietly: history gaps and any
automation or dashboard card reading generation or tariffs will be wrong or
blank rather than visibly broken. If this has been down a while, the energy
history already has a hole in it.

## 4. Backyard: freezer monitoring and cameras offline

Six offline entities, in two groups:

| Entity | Domain |
|---|---|
| B/Freezer/EnergyMonitor/P110M | switch |
| B/Freezer/EnergyMonitor/P110M Energy | sensor |
| B/Freezer/EnergyMonitor/P110M Energy difference | sensor |
| Tapo_C200_5C35 Motion | binary_sensor |
| Tapo_Camera Battery | sensor |
| Tapo_Camera Motion | binary_sensor |

To be precise about the freezer: the **monitoring** is offline, which says
nothing about whether the freezer itself is running. But it does mean a freezer
failure would not be noticed through Home Assistant — and that is the kind of
gap that is only discovered at the worst moment. Worth confirming the appliance
directly.

The Tapo camera entities are a separate group and may be the same root cause as
the plug if both sit behind one hub.

## 5. Seventy-two entities have no area assigned

17% of the exposed set, including both emergency buttons above and four
`Hue ambiance spot` lights.

Not a fault, but it has real costs: area-scoped voice commands ("turn off the
lights in the Guest Room") skip these entities entirely, and they are harder to
group on a dashboard. Assigning areas is low-risk and done in the UI.

## 6. Friendly names are not unique

24 friendly names are shared by more than one entity. Some are benign and
expected — `Air purifier` exists as both a `fan` and a `switch`, `Deez` as both
a `device_tracker` and a `notify` target. Others are the orphan pairs in issue
2.

Two separate `light` entities are both named `Hue ambiance spot 1`, with no
area assigned. That pair is genuinely ambiguous for voice control and worth
renaming.

This is also why `entity_inventory.md` must never be used to derive an
`entity_id`: a friendly name does not identify a single entity in this
instance.
