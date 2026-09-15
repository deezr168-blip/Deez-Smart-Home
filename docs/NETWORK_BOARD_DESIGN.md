# CasaRay — Network board: design, data mapping, implementation path

**Status: mockup only.** Nothing in this document has been deployed, and
`dashboards/casaray_v2.yaml` is untouched. Proposed route `/casaray-v2/network`,
title **Network**, with a `network-diagnostics` subview.

- Visual mockup: `mockups/2026-09-15_network_board.png`
- Editable source: `mockups/network_board_mockup.html` (1600 × 900, opens in any
  browser, no dependencies)

## 1. The finding that shapes the whole design

The eero integration on this instance exposes **two entities**:

| Entity | What it gives |
|---|---|
| `binary_sensor.eero_wan_status` | WAN up / down |
| `sensor.eero_external_ip` | current public IP |

There is no throughput sensor, no client count, no router uptime, no latency,
no DNS check and no NBN service feed anywhere in the 970-entity export. A
network board built only from what exists today would be two facts.

So the board is designed to be **honest about that and still worth looking
at**: every card that cannot be powered yet keeps its place in the layout,
greyed and dashed with a `Needs Ping` / `Needs UPnP` pill, exactly the
treatment CasaRay already uses for an unavailable entity. The page reads as a
finished design with known gaps rather than a page with holes in it, and the
gaps double as the build list.

## 2. Card hierarchy

```
Header            Back · Home · "Network" · clock (DD/MM/YY)
Chips             Internet · Gateway · Latency · Devices online
──────────────────────────────────────────────────────────────
Hero (full width) INTERNET ONLINE · More NBN 500/45 · WAN IP ·
                  uptime · last drop · gateway
──────────────────────────────────────────────────────────────
Band 2            Live speed | Network health | Reliability | Eero gateway
Band 3            Connected devices | Latency | Data used | Diagnostics ›
```

Three bands, all above the fold at 16:9. The hero is the only card with a
tinted surface, so internet state reads from across the room; everything else
is the standard glass card.

## 3. Semantic colour, unchanged from CR-232

Green healthy · amber degraded or active · red fault · grey unavailable or no
sensor. The hero's green tint follows `binary_sensor.eero_wan_status`; if it
goes off the card turns red, if it goes unavailable it turns grey and reads
"Internet state unknown" — never a reassuring "online" it cannot see.

## 4. Data mapping

### Available now — no configuration change

| Metric | Source |
|---|---|
| Internet online / offline | `binary_sensor.eero_wan_status` |
| WAN / external IP | `sensor.eero_external_ip` |
| Gateway status | `binary_sensor.eero_wan_status` |
| Home Assistant health | `binary_sensor.matter_zigbee_hub_problem`, update entities |
| Remote access | `binary_sensor.remote_ui` |
| Local Wi-Fi quality | 10 reporting `*_signal_level` sensors + 2 camera `*_rssi` |
| Wi-Fi network name | `sensor.deez_ssid`, `sensor.raymonds_iphone_ssid` |
| Devices online, by category | availability of the entities HA already has |
| Device cloud links | 10 reporting `*_cloud_connection` binary sensors |

### Derivable — templates and core helpers, no new integration

| Metric | How |
|---|---|
| Internet uptime | `as_timestamp(states.binary_sensor.eero_wan_status.last_changed)` |
| Last interruption | same, plus a `history_stats` sensor for the last drop |
| Drops in 7 / 30 days | `history_stats` in `count` mode on the WAN sensor |
| Availability % | `history_stats` in `ratio` mode, 30-day window |
| Last restored | template on `last_changed` when the state is `on` |
| Weakest Wi-Fi link | `min()` across the signal-level sensors, naming the device |
| Devices online / total | template counting entity availability by area or domain |

### Requires a new sensor — core integrations, no add-on

| Metric | Cleanest implementation |
|---|---|
| Latency to internet | **Ping** integration, host `1.1.1.1` |
| Gateway ping | **Ping**, host = the eero's LAN address |
| Packet loss | Ping exposes it as an attribute; surface with a template sensor |
| DNS resolves | **Ping** against a hostname rather than an IP |
| Jitter | Not native. A `statistics` sensor over the ping sensor's standard deviation is the honest approximation, and should be labelled as such |
| Router uptime | `command_line` sensor, or eero cloud API via `rest` |
| Last IP change | template on `sensor.eero_external_ip.last_changed` |

### Not currently available

| Metric | Why |
|---|---|
| Download / upload throughput | Needs the router's byte counters. **UPnP/IGD** pointed at the eero is the one clean route; whether eero 6+ answers IGD byte queries needs testing on the device |
| Data used today / month | Same counters, then `utility_meter` for the daily and monthly cycles |
| Connected client count | The eero *cloud* API has it; the HA integration does not expose it |
| Wi-Fi band breakdown | Same |
| NBN service status | No integration. A `rest` sensor against More's status page is possible but scraping a status page is fragile, and I would not build the family-facing board on it |

## 5. Recommended implementation path

**Step 1 — build the board with what exists.** Hero, Network health, Eero
gateway, Connected devices and Wi-Fi quality are all live today. That is a
useful page on its own and needs no configuration change.

**Step 2 — add the Ping integration.** Three hosts: `1.1.1.1`, the eero's LAN
address, and a hostname for DNS. Core integration, UI-configurable, no add-on.
Lights up Latency, Gateway ping, Packet loss and DNS — four cards for about ten
minutes of setup. Highest value per unit of effort by a distance.

**Step 3 — add the history helpers.** `history_stats` for drops in 7 and 30
days and the availability ratio; templates for uptime, last drop and last
restored. Lights up the whole Reliability card. These only become meaningful
after a few weeks of recorder history, so start them early.

**Step 4 — test UPnP/IGD against the eero.** If it answers, Live speed and Data
used follow, plus a `utility_meter` pair for the daily and monthly cycles. If
it does not, those two cards stay dashed and honest, and the board is still
complete without them.

**Step 5 — the eero cloud API, only if client count matters.** A `rest` sensor
against the eero API would give clients and band detail. It is the most work
and the least family-facing value; I would leave it last or skip it.

## 6. Proposed subviews

`/casaray-v2/network-diagnostics` — "Network diagnostics", `subview: true`,
Back / Home / Network at the top in the camera-subview shape. Carries the ping
targets, DNS checks, IP history, router detail and packet loss. Nothing on it
is needed by a family member, which is the point.

A second subview, `network-devices`, is worth holding in reserve for the full
client list once there is a client list to show.

## 7. What the mockup deliberately does not do

No invented entity, no invented value presented as live. The WAN IP shown in
the render is `203.0.113.48`, which is in the RFC 5737 documentation range and
cannot be a real address. Uptime, drop counts and the availability percentage
are illustrative and marked as derivable above, not implemented.
