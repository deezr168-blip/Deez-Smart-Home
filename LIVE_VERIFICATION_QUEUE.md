# Live verification queue

**Authoritative human verification checklist.** Every item below is
implemented, validated and deployed, but has never been seen rendered. This
environment cannot reach the instance — only a person looking at the live
dashboard can close these.

Fill in the **Result** column with `PASS`, `FAIL` or `PARTIAL`. Leave
`PENDING` if you did not check it. Nothing here may be marked verified from
repository evidence.

Grouped by page so one visit clears several checks. Target: seconds per check
on the iPad, landscape.

> **Guard checks.** Several items fix a card that asserted a reassuring state
> it could not see ("Closed", "Quiet", "Normal") when its sensor dropped out.
> With every sensor healthy you can only confirm the card shows a *real*
> reading. To confirm the guard itself, temporarily disable one sensor in
> Home Assistant and look for a neutral/grey "offline"/"—" instead of a
> confident value. Rows needing this are marked **[guard]**.
>
> **Language checks** are marked **[中]**: toggle
> `input_boolean.chinese_dashboard` and re-look at the same page.

---

## Home — `/deez-smart-home/home`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-001 | Home grid rebuilt | Tiles are full width, not 60-85px slivers; lights/doors/solar appear once each | No duplicated tiles; nothing navigates to Home from Home | `119e1cd` | P2 | PENDING |
| UI-002 | Room tiles show guarded live values **[guard]** | Each room tile shows a real temperature/power figure | No static never-changing text; no "unknown °C" or "Freezer unavailable W" | `018610b` | P1 | PENDING |
| UI-008 | Hero, weather and backup timestamps formatted | House Pulse temperature, weather word, and Status backup time | Rounded temperature, "Partly cloudy" not "Partlycloudy", a readable date not a raw ISO string | `bb05c7c` | P1 | PENDING |
| REG-003 | Network nav chip gained an unavailable branch **[guard]** | The Network chip's colour | Green when WAN is up; grey — not red — when the WAN sensor is unavailable | `b5eee22` | P1 | PENDING |
| REG-006 | Energy tile fallback translated **[中]** | Energy tile secondary text with the toggle on | Reads 离线, not bare English `offline`, beside 太阳能 | `dff00f3` | P3 | PENDING |
| REG-007 | House Pulse door count/colour guarded **[guard]** | House Pulse hero with all three door sensors disabled | Text calls out "N door sensor(s) offline" / "N 个门传感器离线" and the icon turns grey, not a confident green "0 open" | `b058006` | P2 | PENDING |
| REG-009 | Quick-control Doors chip guarded and translated **[guard][中]** | Home view's own Doors chip (in the row under the language toggle, not the hero) with all three door sensors disabled | Reads "Sensor offline" / 传感器离线 and turns grey, not a confident bare-English "0 open" / green | `d592692` | P2 | PENDING |
| REG-010 | Rooms → Security card door count guarded **[中]** | The "Security" card in the Rooms grid, with a door sensor disabled | Appends "N unknown" / "N 离线" after the door count instead of silently omitting the sensor; icon turns grey, not green | `d592692` | P2 | PENDING |
| UI-031 | Quick-control Person chip and Rooms → Climate card guarded, bilingual **[guard][中]** | The Person chip (quick-control row) and the Climate card (Rooms grid), with `person.raymond_du` / `climate.bedroom_parents_room_ac` disabled | Person chip shows a distance-based bilingual label (在家/未知/X km away), never the raw entity-state string; Climate card shows "—", never a bare lowercase HVAC mode or a literal `unavailable` | `ccfb0c8` | P3 | PENDING |
| CR-001 | **CasaRay Batch 1 — P1 clock/date added to the Home header** | Directly under the page title, above the English/中文 toggle row: a clock-icon card | Two lines: the time (e.g. `5:42 PM`, no leading zero) with the date **directly underneath it** as `DD/MM/YY` (e.g. `01/09/26`). Watch it tick over a minute boundary — it must update on its own. Tapping it must do nothing. **If the date shows any other format, or sits beside the time rather than under it, mark FAIL** | `5ad2bce` | P2 | PENDING |
| CR-002 | CasaRay Batch 1 — header layout on the iPad | The same clock card, iPad landscape | It sits on the sky with no glass card behind it, matching the title and chip rows around it, and its text stays legible against the background. Note whether it renders **beside** the title or **under** it — that answers whether a follow-up should narrow the title to 8 columns | `5ad2bce` | P3 | PENDING |

| CFG-003 | **Deployment bridge repair, then bridge verification.** Delivery failure CONFIRMED (`sensor.front_door_battery` absent from live raw config); root cause is a replaced branch history, see `DASHBOARD_ISSUES.md` | **On the host, in the clone the deploy script uses:** run the recovery steps in `DASHBOARD_ISSUES.md` — confirm the split with `git merge-base HEAD origin/ha-deploy` (empty), check `git log --oneline origin/ha-deploy..HEAD` is empty **before** resetting, then `git reset --hard origin/ha-deploy` and run the deploy script by hand | **Bridge repaired** when the run reports a candidate commit that is no longer `26c3b14` and an apply rather than a skip. **Bridge verified** when the Raw Configuration Editor contains `UI-032 PROBE v1` and the purple bug-icon card appears directly under the Home page header. Only then is `UI-032` itself judgeable | `2183177` (probe) | **P1** | PENDING |

## Security — `/deez-smart-home/security`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-005 | Door state guarded **[guard]** | The door cards with a contact sensor disabled | Neutral/unknown, never a confident green "Closed" | `b1ef565` | P1 | PENDING |
| REG-001 | Door state translated **[中]** | The three door cards with the toggle on | 开启/关闭, not English Open/Closed | `b5eee22` | P3 | PENDING |

## Energy — `/deez-smart-home/energy`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-011 | Total Solar converted Wh→kWh | Compare Total Solar against Day and Year figures | Same order of magnitude. **If Total reads ~1000× smaller, the conversion is wrong — mark FAIL** | `df457e3` | P1 | **PASS** — 30 Aug 2026. Owner read the native HA Energy dashboard: Solar 16 kWh + Grid 47.83 kWh = Home 63.83 kWh exactly, with the Solar production chart and Energy Distribution card independently showing 16 kWh. No 1000× scaling error. See `DASHBOARD_ISSUES.md` UI-011 for the scope this does and does not cover |
| UI-020 | Total Solar and Powerpal battery guarded **[guard]** | Both readouts carry units; battery colour | No "Battery unavailable%"; battery not green while silent | `df457e3` | P1 | PENDING |
| UI-021 | Energy split into five sections | Page layout in landscape | Cards spread across the width; native energy cards not squeezed into half a page | `df457e3` | P2 | PENDING |

## Network — `/deez-smart-home/network`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-022 | Three static Infrastructure cards removed/wired **[guard]** | Every Infrastructure card | Each reflects a real entity; none permanently reads "fine" regardless of state | `a5dc914` | P1 | PENDING |

## Cameras — `/deez-smart-home/cameras` and the six subviews

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-014 | Camera grid deduplicated | Count the camera entries | Front Door appears once; all six in one uniform grid; previews wider than ~185px | `ae89134` | P2 | PENDING |
| UI-009 | Back chip added to each camera subview | Open a camera, tap the back chip | Returns to Cameras — not stranded with the header hidden by kiosk mode | `e06d0ce` | P1 | PENDING |
| REG-008 | Status chip row Doors chip guarded and translated **[guard][中]** | Doors status chip at the top of the Cameras page, with all three door sensors disabled | Reads "Sensor offline" / 传感器离线 and turns grey, not a confident bare-English "0 open" / green. **Was first logged against `ipad-command-center` — it's actually here, on Cameras** | `b058006` | P2 | PENDING |

## Lights — `/deez-smart-home/lights` and lighting subviews

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| REG-002 | Motion quick-status chips guarded, on **both** Lights and Cameras **[guard]** | Both chips with their motion sensors disabled | Reads offline/—, never a confident "Quiet". Check both pages before recording | `b5eee22` | P1 | PENDING |
| UI-010 | Page title moved above the section heading | Open each of the 4 lighting pages | Page opens with its own title, not a section label | `e06d0ce` | P2 | PENDING |
| REG-013 | `lighting-modes` Current State cards stopped asserting "On" for an unavailable light **[guard][中]** | Current State section (Living Room, Ray Bedroom, Dining), with a light entity made unavailable/unknown | Shows "Offline"/"离线", never a confident "On" | `ccfb0c8` | P2 | PENDING |
| UI-031 | `light-ray-bedroom` Roller Shade card guarded, bilingual **[guard][中]** | Roller Shade card, with the cover or its battery sensor disabled | Shows "—" for an unrecognised shade state and "—" (not "unavailable%") for a dropped battery reading; bilingual open/closed text | `ccfb0c8` | P4 | PENDING |

## People & Locations — `/deez-smart-home/people-locations`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-018 | The 9999 km sentinel removed **[guard]** | Distance text for someone without a GPS fix | Neutral/unknown, never "9999.0 km from home" in red | `76da19b` | P1 | PENDING |
| UI-019 | Person cards deduplicated | Count entries per person | Each person listed once; cards readable, not ~83px wide | `76da19b` | P2 | PENDING |
| REG-004 | "at home" translated **[中]** | A person who is home, toggle on | Reads 在家, not English `home` | `dff00f3` | P3 | PENDING |

## iPad Command Center — `/deez-smart-home/ipad-command-center`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-015 | View rebuilt into four sections | Overall layout on the iPad itself | No nested grids; camera chips not duplicating the tiles below them; load chips guarded | `99a77b4` | P2 | PENDING |
| REG-005 | WAN fallback reworded **[中]** | WAN chip when the sensor is unavailable | Now reads "WAN not reporting" / 网络无数据. **Was `WAN —`. If you wanted the dash kept, mark FAIL** | `dff00f3` | P3 | PENDING |
| REG-011 | Home Pulse chip row Doors chip guarded and translated **[guard][中]** | Doors status chip in the Home Pulse row (beside the already-guarded WAN chip), with all three door sensors disabled | Reads "Sensor offline" / 传感器离线 and turns grey, not a confident bare-English "0 open" / green | `d592692` | P2 | PENDING |

## Climate & Status

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-007 | Climate and Status given structure | Both pages in landscape | Multi-column, not a flat single column; Climate shows the full thermostat | `bb05c7c` | P2 | PENDING |

## Bills & rooms

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| BILL-001 | Account-number literal replaced with `input_text.elec_account_number`/`..._gas_account_number` **[guard]** | `bill-electricity` and `bill-gas` plan-details cards | Same account number as entered in the Bills form (or "Not entered" if the helper is empty), not a hardcoded number that no longer matches. NMI/MIRN unchanged — not part of this check | `23c0301` | P1 | PENDING |
| BILL-004 | Bill status/amount cards guarded against raw `unavailable`/`unknown` interpolation **[guard][中]** | `bills` landing tiles (Electricity, Gas, Car Insurance, Council Rates, South East Water, VicRoads Rego) and the status card on `bill-car-insurance`/`bill-water`/`bill-council-rates`/`bill-rego`, with the underlying `input_number`/`sensor` disabled | Shows "Not entered" / 未输入 (or "Status unavailable" / 状态不可用 for the electricity/gas status word), never a literal `$unavailable` or raw `unavailable` status | `d570a82` | P3 | PENDING |
| BILL-005 | Title-card `card_mod` text-shadow added to the 4 title cards dashboard-wide that were missing it | `bill-car-insurance`, `bill-water`, `bill-council-rates`, `bill-rego` page titles | Title/subtitle text has the same subtle shadow as every other page title (e.g. `bills`, `bill-electricity`) for contrast over the night-sky background, not flat/harder-to-read text | `73813e8` | P3 | PENDING |
| UI-016 | Last nested grids dissolved on `bills`, `light-living-room`, `lighting-modes` | All three page layouts | Cards sized normally, not squeezed inside half-width sections; the six bill subviews each read as one clean column | `9b28fdb` | P2 | PENDING |
| UI-013 | Duplicate media cards removed | Parents Room and Guest Room | One media control per player, not a Mushroom card stacked on a native one | `56c7656` | P3 | PENDING |
| UI-023 | Placeholder cards removed | Ray Bedroom and other room pages | No "nothing here yet" cards taking up columns | `3048e54` | P2 | PENDING |
| UI-024 | Third kitchen plug named and restyled | Kitchen plugs | All three named (no raw entity ID) and styled alike | `3048e54` | P3 | PENDING |
| UI-030 | LetPot Grow Light card guarded **[guard]** | Ray Bedroom room page — Grow Light card, with `select.lph_se_dcd9_light_mode`/`..._light_brightness` disabled | Shows "— • —" or bilingual "Offline"/"离线", never the literal word "unavailable" | `691689a` | P4 | PENDING |

## Global — check on any two or three views

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-027 | Heading cards given a theme-level text shadow | Section titles sitting over the bright horizon band | Titles clearly legible, without adding a heavy card surface behind them | `9926233` | P2 | PENDING |
| UI-003 | One section-header treatment | Any view with several sections | Headers look consistent; not two competing styles on one page | `b85949e` | P2 | PENDING |
| UI-004 | `max_columns` matched to section count | Any view, iPad landscape | No empty grid tracks; pages fill the width | `94a9b42` | P2 | PENDING |
| UI-017 | Back chip added to 16 top-level views | Open a room, tap back | Returns to Home; no view is a dead end under kiosk mode | `34a92e7` | P1 | PENDING |
| UI-006 | 20 cards stopped asserting unseen state **[guard]** | Any guarded card with its sensor disabled | Neutral/unknown, never "Clear"/"Normal"/"Up to date" | `315323f` | P1 | PENDING |
| UI-012 | Page titles, subtitles, headings translated **[中]** | Any two views, toggle on | Titles and headings in Chinese, no English chrome left | `f4e7ec3` | P3 | PENDING |
| UI-028 | Status words translated **[中]** | Card status text, toggle on | Offline/Open/Motion/Occupied etc. in Chinese | `fa286de` | P3 | PENDING |
| UI-029 | Number-glued fragments translated **[中]** | Text with numbers in it, toggle on | Reads in Chinese order — 距家 5 公里, not "5 km away" transliterated | `f04a59f` | P3 | PENDING |

---

# CasaRay v2 — `/casaray-v2/…`

**A different dashboard.** Everything above this line is the legacy
`/deez-smart-home/…` dashboard. Everything below is `dashboards/casaray_v2.yaml`.
Do not merge the two sets of results.

## 🎉 DEPLOYED AND RENDERING — 2026-09-06

**CasaRay v2 is live at `homeassistant.local:8123/casaray-v2/`.** Registered
alongside the legacy dashboard, which is untouched. First owner screenshots
2026-09-06 04:31 covering `home`, `rooms`, `living-room`, `kitchen`, `dining`.

Six rows moved to PASS on that evidence. **Two layout defects were found and
fixed the same day** — see `CR-160` and `CR-161` below; both need a re-check
after the next sync.

What the screenshots proved beyond the individual rows:

- The dashboard registers, loads and navigates under `casaray-v2`. The 87
  migrated links resolve — the single biggest deployment risk is retired.
- **Scene buttons render on real rooms.** Living Room shows Relax · Bright ·
  Read · Nightlight · Energize · Concentrate; Dining shows its six. The B1
  export delivered usable scene IDs.
- The `markdown` interpretation layer, native `tile` grids, `heading` cards
  and the theme all render together.
- Guards behave: "Hue spot 1 — Unavailable" rather than a confident state.
- The clock reads `4:31 AM` over `06/09/26` — **the mandated DD/MM/YY**.

## CasaRay — does it load at all

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-100 | Open `/casaray-v2/home` | The page renders. A **CasaRay** entry with a heart-house icon is in the sidebar. | `2203fc1` | **P1** | **PASS** — 06/09/26. Loads at `/casaray-v2/home`. Greeting and nav render.
| CR-101 | The legacy dashboard, straight after | Still at `/deez-smart-home/home`, unchanged. Registering CasaRay must not disturb it. | `2203fc1` | **P1** | PENDING |

## CasaRay — navigation

All 87 internal links moved to `/casaray-v2/`. If the dashboard was registered
under any other key, **every one of them breaks** — that is the single most
likely failure.

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-110 | Home's 8 nav buttons | Rooms, Energy, Security, Cameras, Bills, Entertainment, Alerts, Health all open | `2203fc1` | **P1** | **PASS** — 06/09/26. All 8 nav buttons render: Rooms, Health, Energy, Security, Cameras, Bills, Entertainment, Automations, Alerts.
| CR-111 | `rooms` · `energy` · `security` · `cameras` · `bills` | Each loads | `2203fc1` | **P1** | PENDING |
| CR-112 | `entertainment` · `alerts` · `house-health` · `automations` · `lighting` · `climate` · `people` | Each loads | `2203fc1` | **P1** | PENDING |
| CR-113 | One room, e.g. `living-room` | Loads; Back goes to `rooms`, Home to `home` | `2203fc1` | **P1** | **PASS** — 06/09/26. `living-room`, `kitchen`, `dining` all load with working Back and Home.
| CR-114 | A camera subview from the Cameras grid | Opens; Back returns to `cameras` | `2203fc1` | P2 | PENDING |

## CasaRay — the features B1 unblocked

These were connected from the entity export and have **never** rendered.
Readiness was computed from B1 first, so each row states what it should do.

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-120 | Room scene buttons — Living Room, Dining, Ray Bedroom | Tap one; the lights change. 29 scenes wired, all present in B1. A scene not recalled since the last restart shows no state — **normal, not an error** | `13d21c4` | **P1** | **PASS (renders)** — 06/09/26. Living Room shows Relax · Bright · Read · Nightlight · Energize · Concentrate; Dining shows Relax · Read · Nightlight · Energize · Concentrate · Midwinter. Scene IDs resolve. *Tap-to-activate not yet exercised.*
| CR-121 | Lighting board | Per-light control works; scene rows present | `13d21c4` | P2 | PENDING |
| CR-122 | Living Room air quality | PM1 / PM2.5 / PM10 with a health-concern word. All 5 sensors live in B1 | `13d21c4` | P2 | PENDING |
| CR-123 | Energy → solar forecast | Today / tomorrow / peak-time figures. All 6 live. Works even when the inverter is down | `13d21c4` | P2 | PENDING |
| CR-124 | Energy → Fronius + Powerpal | Inverter and whole-house power reporting. All 8 live in B1 | `13d21c4` | P2 | PENDING |
| CR-125 | People board | Phone and iPad battery percentages, presence per person. All 6 live | `13d21c4` | P2 | PENDING |
| CR-126 | Automations board | **Exactly three** `automation.*` entities, each with a working enable toggle. Three is all that exists — not a truncated list. *(A separate Hue Bridge section was added later; see CR-191.)* | `13d21c4` | P2 | PENDING |

## CasaRay — the 2026-09-05 autonomous upgrade batches

Entities B1 confirms live that no board was reading. Every ID here was
checked against `docs/live/states_export_2026-09-05.txt` and is recorded
`ok` there; none was inferred from a name.

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-170 | Bills — This year, Bill history, per-bill discount rows | Amounts and a savings rate, not "Not yet available". 53 helpers back this | `df413b5` | P2 | PENDING |
| CR-171 | Climate — Dining temperature | Present, and labelled **Dining**. Its entity ID says `living_room` but B1 puts it in Dining; the label follows B1, not the ID | `142bb7d` | P2 | PENDING |
| CR-172 | Kitchen — Electrolux fridge block and the shopping list | Fridge temp/humidity/battery, motion, and a working `todo.shopping_list` card | `142bb7d` | P2 | PENDING |
| CR-173 | Energy — inverter health row | Online state plus the Primo status and error strings. These must read even when yield is 0; that is the point of the row | `bf1bc62` | P2 | PENDING |
| CR-174 | Energy — grid carbon | CO2 intensity and fossil-fuel percentage from Electricity Maps | `bf1bc62` | P3 | PENDING |
| CR-175 | House Health — Overall | Four tiles: house status, offline devices, rooms in use, lights on. **No open-doors count** — see CR-176 | `9aaadb5` | P2 | PENDING |
| CR-176 | House Health — Overall, doors | There must be **no** "0 doors open" tile. All three contact sensors are down, so that number is a sentinel, not a measurement. Consistent with CR-130 | `9aaadb5` | **P1** | PENDING |
| CR-177 | House Health — battery board | **15** battery tiles, and the paragraph above them counts the same 15. If the paragraph says "N not reporting" the N must be countable from the tiles | `9aaadb5` | P2 | PENDING |
| CR-178 | House Health — Network | A Zigbee hub problem tile beside WAN and Remote access | `9aaadb5` | P3 | PENDING |
| CR-179 | Any summary paragraph — Home, Energy, Bills, Parents Room, House Health | **Prose, not grey monospace.** These rendered as indented code blocks; if any still does, the `-%}` fix did not take | `d991e39` | **P1** | PENDING |
| CR-180 | People — Device status | Four devices, each level paired with a charge state, including Raymond's iPad | `ddd7c93` | P2 | PENDING |
| CR-181 | People — Guest mode tile | Tapping opens more-info; it must **not** toggle on tap | `ddd7c93` | P2 | PENDING |
| CR-182 | People — Whereabouts | Raymond's distance and activity, plus the note explaining why the other two have neither | `ddd7c93` | P3 | PENDING |
| CR-184 | Security — Detection settings | Twelve switch tiles, and a paragraph counting privacy-mode cameras and switched-off detection. A tap must open more-info, **not** toggle | `64ae00e` | **P1** | PENDING |
| CR-185 | Security — Sirens | Three siren tiles, display-only, with the note naming the three that do not report | `64ae00e` | P3 | PENDING |
| CR-186 | House Health — counts at exactly 1 | Reads "1 battery is under 30%" and "1 device is offline", not "1 batteries" / "1 devices" | `a495a24` | P3 | PENDING |
| CR-187 | Entertainment — Parents Room TV | The card **works** now. It was pointing at `media_player.55_qled_4k_ai`, which is unavailable — see CR-190 | `0d2b58a` | **P1** | PENDING |
| CR-188 | Entertainment — Ray Bedroom TV | A third TV section that has never appeared on this board | `0d2b58a` | P2 | PENDING |
| CR-189 | Entertainment — TV power tiles and Pogo note | A Power tile under each Samsung TV; the Pogo section says it is not reporting rather than showing dead controls | `0d2b58a` | P3 | PENDING |
| CR-191 | Automations — Hue Bridge section | Three switches: Coming home, Leaving home, Nightlight schedule, plus the note saying they run on the bridge and Home Assistant cannot see what they did | `9b02120` | P2 | PENDING |
| CR-192 | Home — daylight | Sun, Sunrise and Sunset tiles beside the forecast | `120dba1` | P3 | PENDING |
| CR-193 | Cameras — Floodlights | North Wall and Stockroom, each with a brightness slider. These **are** meant to be tappable, unlike the Security detection tiles | `120dba1` | P2 | PENDING |
| CR-194 | Ray Bedroom — Nightlight | A light tile with brightness, distinct from the Nightlight scene button in Quick actions above it | `120dba1` | P3 | PENDING |
| CR-200 | House Health — Overall | The tile reads **Unavailable entities**, not "Offline devices", and the card under it explains why that number and "N devices are offline" differ | `1d1f871` | **P1** | PENDING |
| CR-201 | House Health — battery roll-up | "N batteries are not reporting" now **names** them. Cross-check the named one against the tile grid below — they must agree | `1d1f871` | P2 | PENDING |
| CR-202 | Bills — overview paragraph | One canonical narrative computed from the same helpers the bill cards show. No more "5 overdue" beside "A$0.00" and "Unpaid 1". Any past-due bill is named **with its due date** | `81e7c8e` | **P1** | PENDING |
| CR-203 | Bills — unconfigured helpers | The overview says how many of the six bills have no amount entered, and calls that an unconfigured helper rather than a zero balance | `81e7c8e` | **P1** | PENDING |
| CR-204 | Bills — sensor disagreement | If `sensor.bills_unpaid_count` or `sensor.bills_outstanding_total` disagrees with the helper-derived figures, the paragraph says so by name. **If that note appears, paste it back** — it means the Home Assistant template sensors need fixing, which is outside this repository | `81e7c8e` | **P1** | PENDING |
| CR-205 | Bills — electricity quarter | Reads "Imported this quarter **N kWh**", not "Billing cycle 1234.56789…" | `63ac907` | P2 | PENDING |
| CR-206 | Energy — header and summaries | Whole watts, e.g. "1626 W now". No long decimals on Energy, Home, Living Room, Parents Room or Garage | `63ac907` | **P1** | PENDING |
| CR-207 | Energy — solar above 100% | Reads "Solar is covering all household demand and producing surplus", with both figures. It must **not** claim an export amount — no import/export entity exists | `63ac907` | P2 | PENDING |
| CR-208 | Energy — forecast section | Says the figures are forecast, not inverter readings, and that "still to come" is the integration's own remaining forecast rather than today minus generated | `63ac907` | P2 | PENDING |
| CR-209 | Climate — indoor average | Says **3 rooms**, the mean of Living Room, Parents Room and Dining — the three the Readings section shows | `d2a8a18` | P2 | PENDING |
| CR-210 | Climate — AC mode | Tile reads "AC mode when on"; the line below explains that with the unit off the mode is what it will use next. `fanOnly` shows as "Fan only" / 仅送风 | `d2a8a18` | P2 | PENDING |
| CR-211 | Parents Room — Reset filter | A **button** labelled "Reset filter timer" with a confirmation, not a tile reading "Unknown" | `059f65a` | P2 | PENDING |
| CR-220 | **Any page — is it themed at all?** | Night-sky background, frosted-glass cards, the amber/cyan palette. CasaRay now declares its own `theme: CasaRay`. **If the page is plain grey on white, the theme did not reach `/config/themes/` or was not reloaded** — run the sync helper and Developer Tools → YAML → Reload Themes | `f310cc1` | **P1** | PENDING |
| CR-221 | Any board — card titles | Section headings are small, UPPERCASE and letter-spaced, as the mockups render them. Chinese headings are unaffected — CJK has no case | `f310cc1` | P2 | PENDING |
| CR-222 | Any board — page title | Large and uppercase: LIVING ROOM, CAMERAS, HOUSE HEALTH. **Home is the exception** and should still read "Good morning, Ray" in sentence case | `59bebfc` | P2 | PENDING |
| CR-223 | Home — KPI strip | Four cards under the nav row: HOUSE POWER in kW, INDOOR CLIMATE with a comfort word, SECURITY, SOLAR TODAY as a percentage. 2×2 on the iPad | `03e6633` | **P1** | PENDING |
| CR-224 | Home — KPI honesty | The SECURITY card should read **Unconfirmed**, not "Secure". All three door sensors are down; the mockup's "Secure" is a design, not a claim about this house | `03e6633` | **P1** | PENDING |
| CR-225 | Every room page — status chips | A row of chips under the header: a bold value and a muted caption. Two across. Check one room in each language | `87d388f` | P2 | PENDING |
| CR-226 | Ray Bedroom — blind chip | Reads **Blind open** or **Blind closed**, never "not reporting" while the blind plainly works. Covers report open/closed, and the first draft tested for on/off | `87d388f` | P2 | PENDING |
| CR-227 | Every room page — footer | Home and All rooms buttons at the bottom of the page | `59bebfc` | P3 | PENDING |
| CR-228 | Any board — icon colour | An open door, an overloaded socket and an unpaid bill are **red**; solar, internet and savings are **green**; house draw and outstanding bills are **amber**. Everything else keeps the theme's amber-active. Lights are deliberately untouched | `dd93a54` | P3 | PENDING |
| CR-196 | Living Room — Air quality | PM1, PM2.5 and PM10, each paired with its health-concern word. This is what CR-122 always expected; only now is it built | `28b520e` | P2 | PENDING |
| CR-197 | Ray Bedroom / Garage — socket overload | A "Socket overloaded" tile in Ray Bedroom's Power use, and "Socket reachable" in the Garage Freezer section | `28b520e` | P2 | PENDING |
| CR-198 | House Health — updates | Core, Supervisor and Operating System tiles, plus a line counting every pending update across all 74 update entities | `614ad5e` | P2 | PENDING |
| CR-199 | Dining — Temperature | A temperature tile in Sensors, reading the same figure the Climate board shows as Dining. **If the two disagree, say so** | `4429a7f` | P2 | PENDING |

### Needs an owner answer before it can be built

| ID | Question | Why it is blocked |
|---|---|---|
| CR-183 | **What is the Family Location selector for?** | **Partly answered 2026-09-07 from the live connector.** It is exposed to Assist as **"Family Location"** and currently reads **`Raymond Du`** — so its options are people, and it selects *whose* location something should show. That is a display-scope picker, not a device control, which makes it safe to surface on the People board beside presence. Still unknown: what reads it. **If it drives a map or a location card, say so and it goes on People next batch.** Not added yet — a selector whose consumer is unknown could still be load-bearing for an automation. |
| CR-190 | **Which Parents Room TV entity, and which Ray Bedroom one?** | **Rewritten 2026-09-07 from the live connector, which corrects what this row previously said.** B1 listed `media_player.55_qled_4k_ai` as unavailable **and in Ray Bedroom** — so the real defect was that the *Parents Room* page was driving a *Ray Bedroom* entity, not that the entity was dead. Repointing it to `..._qa55q7faawxxy` in `0d2b58a` was right, for a better reason than that commit gave. **Live now: all four report, none is unavailable.** Parents Room holds two, both `off`, both `device_class: tv` — `master_bedroom_55_qled_4k_ai` and `..._qa55q7faawxxy`; either works and the page uses the latter. Ray Bedroom also holds two: one `off` with no device class (`55_qled_4k_ai`) and one `idle` with **`device_class: speaker`** and volume 1.0, which is `q70f8036` — the entity the new Ray Bedroom TV card uses. **A speaker endpoint is probably the wrong half of that pair for a TV card.** Please confirm in Settings → Devices which entity is the Ray Bedroom television itself, and whether the two Parents Room entries are one TV listed twice. Nothing is broken today; this is about picking the right half of each pair. |
| CR-195 | **Do the Parents Room emergency buttons actually register a press?** | This is the one item in this queue that is a safety question rather than a display question. `binary_sensor.emergency_button_dad_cloud_connection` and the Mum equivalent both read `ok`, so the page can honestly say the buttons are connected and their signal is good. But the two press-event entities, `event.master_bedroom_emergency_button_dad_main` and `event.master_bedroom_emergency_button_mum_main`, both read **`unavailable`** — so as far as this export shows, a press produces nothing Home Assistant can see. The page now says so in both languages rather than letting "Both emergency buttons are connected" be read as "the buttons work". **Please press one and check Developer Tools → States for that event entity, or Settings → Devices for a logged press.** If it stays unavailable the buttons are connectivity indicators only, and whatever is meant to happen when someone presses one is not wired up. Nothing was added or changed on the devices themselves. |
| CR-212 | **Where does "Not yet available" come from?** | It is no longer anywhere in `casaray_v2.yaml` — `df413b5` removed the last of it. So if it is still on screen it is an **entity state**, most likely `sensor.electricity_bill_status` or `sensor.gas_bill_status`, which the Bills page shows as "Status" tiles and whose templates live in Home Assistant's config, not this repository. **Check:** Developer Tools → States, filter `bill_status`, and read the two values. If either literally is "Not yet available", the fix belongs in the Home Assistant template that defines it. If neither is, the deployed copy of the dashboard is older than `df413b5` and the sync step needs running. |
| CR-213 | **What do `sensor.house_status`, `sensor.active_rooms_count` and `sensor.house_lights_on` actually count?** | All three are template sensors defined in Home Assistant's config, so the dashboard shows them without being able to verify their definitions. `sensor.casa_offline_devices` turned out to count entities while being labelled devices (CR-200), so the same doubt applies to these three. **Check:** Developer Tools → Template, and paste back what each resolves to. Not changed in the meantime — the labels are plausible readings of their names. |
| CR-230 | **The briefing approves a Bathroom room page. CasaRay has none.** | Master Design Briefing v1 §5 lists seven approved room pages — Living Room, Kitchen, Dining, Parents Room, Ray Bedroom, **Bathroom**, Garage — and §24 puts Bathroom ninth in the implementation order. There is a `CasaRay_Bathroom_Mockup.png`. CasaRay v2 has the other six plus Guest Room, and no Bathroom. **The blocker is data:** the entity export contains **zero** entities in a Bathroom area. A page can be built when there is something to put on it. Which is it — is there bathroom hardware not yet integrated, or should the briefing's room list drop Bathroom and gain Guest Room? |
| CR-231 | **The briefing approves a dedicated Water & Gas view. CasaRay has none.** | §15 asks for water/gas today and this month, trend, comparison against normal, leak state and cost projection. What exists: `counter.gas_meter_pulses` and `counter.water_meter_pulses` (both ok), `binary_sensor.gas_meter_pulse_sensor` (ok) — but the **entire water meter chain is unavailable**: sensor, battery, firmware and identify button. Gas alone could carry a partial view. Build gas-only now, or wait until the water meter is back? |
| CR-232 | **RESOLVED 14/09 — amber.** The owner approved the four-way system: green healthy/secure/connected/closed/normal · amber active/running/currently on/selected · red fault/urgent/needs attention · grey unavailable/offline/unknown/no data. Blue appears nowhere in the 14/09 renders and has been removed from the three cards that carried it. Recorded in `CLAUDE.md`; applied in `dc06245` (alert cards) and the theme. | Closed. |
| CR-233 | *(still open, 14/09 — the 14/09 mockups draw a "One tap" row of Evening / Goodnight / Movie / All lights off, and it is the one thing on those renders this instance cannot build.)* **Home Favourites and the Lighting Studio need whole-home scenes that do not exist.** | Briefing §4 gives Home a Favourites tile group — the render shows All Lights / Climate / Movie Time / Good Night — and §12 asks the Lighting Studio for All Off, Relax, Bright, Movie Time, Dinner, Party and Good Night. This instance has **29 per-room scenes** (Living Room Relax, Dining Nightlight and so on) and **six bill-payment scripts**. It has no whole-home scene of any kind. Nothing was built, because building it means inventing scene IDs or wiring buttons that do nothing. **This is an owner action:** create the scenes in Home Assistant (Settings → Automations & scenes → Scenes), tell Claude their entity IDs, and both the Home Favourites group and the Lighting Studio rows can be wired in one batch. A useful minimum is `All Off`, `Movie Time` and `Good Night`. |
| CR-234 | **The Backyard area exists in Home Assistant and every entity in it is dead.** | Sixteen entities are assigned to **Backyard** — the Kogan Freezer, a Tapo camera, the B/Contact door sensor and the B/Freezer energy monitor — and **not one of them reports**. That is why there is no Backyard page: a page built from them would be sixteen dashes. The one Backyard entity CasaRay does use is `binary_sensor.b_contact_sensor_door`, on Security, where it correctly reads as not reporting. **Is this hardware you intend to bring back, or has it been retired?** If retired, the entities can be removed in Home Assistant and the House Health unavailable-entity count drops by sixteen. If it is coming back, a Backyard page becomes worth building. |
| CR-235 | **Three motion sensors report from the Living Room area. Are they three devices?** *(investigated 2026-09-13 — not resolved, nothing removed)* | `binary_sensor.living_room_living_hue_hue_sensor_motion` ("Living Room Motion Sensor"), `binary_sensor.master_bedroom_living_hue_hue_sensor_motion` ("Living Hue Hue Sensor") and `binary_sensor.living_room_living_room_motion_2` ("Living room Motion"). All three are on the Living Room page under **Other motion sensors**, named by friendly name so a reading traces back to its device. **What the live check showed:** the connector returns only two of the three — Living Hue Hue Sensor and Living Room Motion Sensor — and the third is simply not exposed to Assist, which is not evidence either way. Of the two returned, battery reads 97% on both and illuminance 2 lx on both, which *suggests* one device exposed twice; but temperature reads 19.1 °C against 24.3 °C, which a single sensor cannot do. **So duplication is not proven and nothing has been removed.** The battery and lux agreement is consistent with two identical Hue sensors in one dark room at the same charge. **Verification, one minute:** Settings → Devices & services → Entities, filter "motion", and read the *device* column for those three — one device name for two rows proves duplication; three device names proves three sensors. |

## CasaRay — expected-offline, do not chase

Confirmed offline in B1. The cards are written to say so rather than assert a
healthy state. **Seeing these as unavailable is the guard working.**

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-130 | Security and Home door state | Says door state **cannot be confirmed** — all three contact sensors are down. It must **not** claim "All doors closed" | `6de86ba` | **P1** | PENDING |
| CR-131 | Cameras grid | East Wall and South Wall show offline; the other four stream | `6de86ba` | P2 | PENDING |
| CR-132 | House Health batteries | **One** East Wall row, not an East Wall plus a Backyard row. There is no Backyard camera on this dashboard | `6de86ba` | P2 | PENDING |
| CR-133 | Living Room lights | Four Hue spots unavailable — Hue bridge, not the dashboard | `6de86ba` | P3 | **PASS** — 06/09/26. Living Room reads "Hue spot 1 — Unavailable". Honest, not a false state.

## CasaRay — the two mechanisms never yet rendered

Highest risk after CR-100, because neither has run anywhere.

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-140 | Flip the Chinese toggle on Home, then look at any board's section headings **[中]** | **Exactly one** heading per section — English off, Simplified Chinese on. **Both** showing means the `visibility` conditions are not applied; **neither** means they are inverted | `1d1f443` | **P1** | PENDING |
| CR-141 | The clock, on any board except a camera subview | Time above, date directly below, reading `DD/MM/YY` — `05/09/26`, **not** `05/09/2026` | `885b03a` | **P1** | **PASS** — 06/09/26. Reads `4:31 AM` over `06/09/26`. Correct DD/MM/YY.
| CR-142 | Chinese mode on House Health and Security **[中]** | Interpreted status sentences in Simplified Chinese — `摄像头`, not `攝影機` | `3faa830` | P2 | PENDING |
| CR-143 | Heading icons and badges in Chinese mode **[中]** | Identical to English mode. Check Home → Security, which carries a door badge | `1d1f443` | P3 | PENDING |

## CasaRay — Home visual rebuild, 2026-09-15

Home was rebuilt against the approved 14/09 wall render
(`docs/mockups/2026-09-14_wall_home.png`) rather than adjusted card by card:
12 sections became 10, `max_columns` 2 became 3, and the composition is now
the render's — top bar, chip strip, alert band, three equal body columns, then
full-width bands. Entity references are unchanged at 434 and every one of the
28 navigation targets survives.

**Everything here is layout.** No entity ID, no service call, no navigation
path and no bilingual rule was changed by this batch, so a `FAIL` below is a
rendering fault, not a data one.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-236 | **Home is a three-column page.** `max_columns` 2 -> 3; page-level bands are `column_span: 3` | Open Home on the wall panel and on the iPad in landscape | Three body columns side by side — Right now, Who's home, Rooms — not two columns with a stray third | `262d59d` | **P1** | PENDING |
| CR-237 | **Top bar, now two rows.** Wordmark(6) + clock(6), then six nav icons at 2 columns each. Superseded the one-row 3+6×1+3 build, which wrapped live | Look at the first two rows | `CasaRay` on **one line**, hard left, greeting under it; time and date hard right; six evenly spaced icons beneath with **Home tinted amber**. No vertical wrapping anywhere | `b5e8522` | **P1** | PENDING |
| CR-238 | **`kiosk_mode` hides HA's own nav, so the icon rail is the only way off Home.** Six destinations: Home, Rooms, Security, Energy, Climate, Cameras | Tap each of the six icons | Each opens the right board, and the Back control on that board returns | `262d59d` | **P1** | PENDING |
| CR-239 | **Chip strip is now one full-width card**, not four. Superseded the four-pill build, which rendered as circles | Look at the strip under the top bar | One long low pill reading `Outside 8° · Inside 17.2° · Home 2 of 3 · Monitored 0 W`, text starting at the left. Wider than it is tall | `b5e8522` | **P1** | PENDING |
| CR-240 | **`Home` chip no longer prints `0 of 3` when the trackers are down** [guard] | Disable one person's device tracker, then all three | One down -> `1 of 3 · 1 unknown`; all down -> `No data`. Never a bare `0 of 3` | `262d59d` | P2 | PENDING |
| CR-241 | **Clock is `#` sized, right-aligned, with lowercase meridiem** — `8:14 pm` over `15/09/26` | Read the top right corner | Time dominant, date beneath, `DD/MM/YY`, **never** `DD/MM/YYYY`. The other 20 clocks on the dashboard still show `PM`; that is expected until those views are rebuilt | `262d59d` | P2 | PENDING |
| CR-242 | **Needs attention no longer repeats its own cards.** The roll-up counts them, then reports only what has no card because it has no reading | Look at the band with something actually wrong | e.g. `4 things need attention. 3 door sensors are not reporting.` — and the four red/amber cards below it, two across, not a duplicate bullet list | `262d59d` | P2 | PENDING |
| CR-243 | **An unpaid bill is now an attention card**, replacing the two bill tiles that used to sit in Home's footer | With a bill unpaid, look at Needs attention | An amber `Bills unpaid` card that opens Bills | `262d59d` | P3 | PENDING |
| CR-244 | **One tap.** Four presets carried across unchanged from the legacy dashboard's Whole Home Presets — same services, same targets, same brightness | Tap Evening, Night, Bright, All lights off | Evening: Living Room to 55%. Night: Living + Ray + Dining to 10%. Bright: the same three to 100%. All lights off: those three plus `switch.mainroomlight_switch_1` off | `262d59d` | **P1** | PENDING |
| CR-245 | **Shopping list on Home**, reading `todo.shopping_list` | Look under Rooms; add and tick an item | The real list, editable in place | `262d59d` | P3 | PENDING |
| CR-246 | **`sensor.casa_monitored_power` is on a board for the first time** — the `Monitored` chip and the amber `Monitored power` card | Compare against Developer Tools | The same figure, and the footnote below it reads "Two circuits are metered…" | `262d59d` | P2 | PENDING |
| CR-247 | **Security is one composed panel** — interpreted summary and the front-door camera side by side, then Front door / Parents Room / Backyard / All cameras | Look at the Security band | Two half-width cards above four equal tiles. The three door tiles are **dashed and grey** while their sensors are down, not green "Closed" | `262d59d` | **P1** | PENDING |
| CR-248 | **Dropped from Home:** the Indoor climate tile group (4 tiles), the `sun.sun` tile, and the Outstanding/Unpaid bill tiles | Confirm nothing you rely on daily is gone | Indoor temperature is in the `Inside` chip and on Climate; sunrise/sunset are still in Right now; bills raise themselves via CR-243. Say so if any of these should come back | `262d59d` | P3 | PENDING |
| CR-249 | **RESOLVED, not accepted.** The four pills were nearly circular because a markdown card has a minimum height and a 3/12 cell came out narrower than that height. One full-width card cannot deform that way at any size | Confirm the chip strip is a compact horizontal strip | Short, wide, readable, grouped left. If it still looks wrong the container is narrower than anything assumed here — say so and I will drop it to plain text | `b5e8522` | P2 | PENDING |
| CR-250 | **Bilingual** [中] | Toggle `input_boolean.chinese_dashboard` on Home | Every heading, chip, summary and footnote switches; entity names, room names and board names stay English by the established convention | `262d59d` | P2 | PENDING |

## CasaRay — half-empty rows removed from seven views, 2026-09-18

The hole Ray reported on Home was not unique to Home. Simulating the
two-column packing across all 28 views found the same shape on seven more: a
lone `column_span: 1` section that does not stretch, so it sits in half a row
and leaves the rest empty.

**Geometry only.** Parsing before and after with `grid_options` and
`column_span` stripped returns identical — no card moved between sections, no
card was added or removed, no entity, template, service call or navigation
target changed. Entity references 434, navigation 124 across 28 targets.

| ID | View | What changed | What to check live | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-277 | Kitchen | Shopping list → full width | The list fills the page rather than leaving a gap beside it | `7fb4a71` | P2 | PENDING |
| CR-278 | Dining | Motion sensors → full width, six tiles 2-across → **3-across**, two even rows | Six sensor tiles in two rows of three, no stragglers | `7fb4a71` | P2 | PENDING |
| CR-279 | Ray Bedroom | Power detail → full width, three tiles → **3-across**, one row | Three power tiles on a single row | `7fb4a71` | P2 | PENDING |
| CR-280 | Energy | Metered circuits → full width, four tiles → **4-across**, one row | Four circuit tiles on a single row. This is the one I negative-tested the gate against | `7fb4a71` | P2 | PENDING |
| CR-281 | Bills | Water history → full width | Three tiles then two, both rows full | `7fb4a71` | P2 | PENDING |
| CR-282 | Automations | System maintenance → full width, tile → full-width | Tile and note stacked full width, no gap | `7fb4a71` | P3 | PENDING |
| CR-283 | Entertainment | Room lighting → full width, two tiles side by side | Two lighting tiles filling one row | `7fb4a71` | P3 | PENDING |
| CR-284 | Security | **Deliberately NOT changed.** Sirens stay half-width — they are controls that must not be mis-tapped, and full-page-width makes that worse | Confirm the sirens are unchanged and still hard to hit by accident | `7fb4a71` | P2 | PENDING |
| CR-285 | all | `check 15` gates this from here | — (repository check, nothing to look at) | `7fb4a71` | P4 | PENDING |

## CasaRay — mockup convergence, 2026-09-18

Eight batches. The chip strip -- the pill row the mockups put under every page
header -- reached every one of the 28 views, and with it every `badges:` block
came off the dashboard. That was not cosmetic: Home Assistant renders badges
ABOVE the sections (DR-011) and CasaRay's first section IS the top bar, so
eighteen views were drawing a row of native pills **on top of the wordmark**.

Every strip was rendered against a live-shaped state set and a fully dark one,
in both languages, before it was committed. Four branches were caught that
way and are listed below as their own rows, because each one is a card
claiming something it could not see -- the class of fault CLAUDE.md singles
out, and the class a validation run cannot find.

| ID | Page | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|---|
| CR-286 | Energy | Four tall KPI cards → one chip strip; four sections → two paired bands | The pill row under the header, then Solar beside Metered circuits | `House power 1.24 kW · Today 8.4 kWh · Solar now … · Solar today …`, two columns below it | `0548483` | P2 | PENDING |
| CR-287 | Energy | Solar gate is three-state: `on` shows the reading, `off` says Offline, anything else says No data | With the inverter unreachable, read both solar chips and the dashed note | Both chips agree; the note says "offline" only when the gate says `off`, otherwise "status unknown" | `0548483` | P1 | PENDING |
| CR-288 | Energy, Security | Duplicate badge rows removed — both pages had a badge row AND a chip strip | Above the wordmark | Nothing above the wordmark; one pill row, under the header | `09135ce` | P1 | PENDING |
| CR-289 | Bills | Bill history (selector + ~50 tiles) moved to `bills-details` | The Bills page ends at This year; the subview carries six history sections | Bills is six sections, not twelve; nothing lost — every helper is on the subview | `f253f85` | P2 | PENDING |
| CR-290 | Bills | The six bill cards take semantic colour | With one bill overdue and one due this week | Red overdue, amber inside a week, green paid, grey dashed for an empty helper, no tint beyond a week | `f253f85` | P2 | PENDING |
| CR-291 | Bills | `Overdue 0` across unpaid bills that have no due date now reads No data | Clear every due date, leave amounts | Overdue chip says No data, not 0 | `f253f85` | P1 | PENDING |
| CR-292 | Bills | `Next due` distinguishes nothing-owed from nothing-dated | Mark all six paid | "Nothing due", not "None dated" | `f253f85` | P3 | PENDING |
| CR-293 | Bills | Upcoming and Record a payment pair into a band; payment buttons 3-across → 2-across | Look for label truncation on `Council rates` and `Car insurance` | Both labels fit on one line | `f253f85` | P2 | PENDING |
| CR-294 | Network | Chip strip from the 15/09 board render | The pill row | `Internet · Remote access · Hub · Devices · Weakest` | `2726deb` | P2 | PENDING |
| CR-295 | Network | Hub chip polarity — `matter_zigbee_hub_problem` is device_class problem, so `on` IS the fault | Compare the Hub chip against the Zigbee hub tile below | They agree; `on` reads Problem, not Healthy | `2726deb` | P1 | PENDING |
| CR-296 | Network | Device count's denominator is what ANSWERED, not the list length | Count the cloud chips against the live export's five unavailable | Reads `9/9`, not `9/14` | `2726deb` | P2 | PENDING |
| CR-297 | 7 rooms + Rooms | Chip strip replaces the badge row on all eight | Each room's pill row, under the title | Living Room reads `Room 19.7° · Movement Quiet, 22 min · Light level 33 lx`, matching the render | `2c4ec5e` | P1 | PENDING |
| CR-298 | rooms | Movement chip shows elapsed time from `last_changed` | Leave a room still for an hour | `Quiet, 1 h`, and `just now` right after movement stops | `2c4ec5e` | P3 | PENDING |
| CR-299 | 10 boards | Chip strip added ABOVE each board's existing summary cards, not replacing them | Every board | The explanatory cards ("the group being on does not mean the spots are online") are all still there | `8f5b851` | P1 | PENDING |
| CR-300 | alerts | Strip counts the SAME conditions the conditional cards fire on | Count the visible alert cards against the three chip numbers | They match; a silent entity counts as `(+N unknown)`, never as no alert | `8f5b851` | P1 | PENDING |
| CR-301 | lighting | Brightness chip said "None on" when all three dimmable groups were unavailable | Pull the Hue bridge | Reads No data, not None on | `8f5b851` | P2 | PENDING |
| CR-302 | bills, bills-details | `sensor.bills_outstanding_total` is no longer referenced anywhere on the dashboard | — | The entity still exists in Home Assistant; nothing on a board reads it, because it reports $0.00 when its helpers are blank | `8f5b851` | P3 | PENDING |
| CR-303 | all | `check 15b` fails the build on any `badges:` block in casaray_v2 | — (repository check, negative-tested) | Adding one badge back to Network produces VALIDATION FAILED naming that view | `6dc3f88` | P4 | PENDING |
| CR-304 | rooms | Room index buttons → tiles matching Home's Rooms section | Tap through to each room | Each tile shows state AND how long it has been that way; destinations unchanged | `f013e35` | P2 | PENDING |
| CR-305 | rooms | New Room conditions card | The list of seven | Three rooms say "no temperature or movement sensor" in those words; none borrows a neighbour's reading | `f013e35` | P2 | PENDING |

**What a passing validation run still cannot tell us about this batch.** Every
chip strip is a `markdown` card with a `card_mod` pill radius. The repository
checks prove the Jinja compiles, the entities exist and the geometry is
declared; they cannot prove the pill renders as a pill rather than a circle at
the width the iPad actually resolves. `DR-012` is exactly that failure, and it
is why every strip is ONE full-width card rather than several narrow ones.

## Entity audit against the live instance, 2026-09-19

The first audit run with a live Home Assistant connection rather than the
export alone. It found no defect on CasaRay, which is itself the result worth
recording — and it found that the premise several decisions rested on has
expired.

**The export's availability column is two weeks stale.** Confirmed live today:

| Entity | 05/09 export | 19/09 live |
|---|---|---|
| `binary_sensor.f_contact_sensor_door` | unavailable | **on** (front door open) |
| `binary_sensor.m_contact_sensor_door` | unavailable | **on** |
| `binary_sensor.b_contact_sensor_door` | unavailable | **off** |
| `sensor.b_contact_sensor_signal_level` | unavailable | **1** |
| `camera.tapo_c420_south_wall_hd_stream_direct` | unavailable | **idle** |
| `camera.tapo_c420_east_wall_hd_stream_direct` | unavailable | **idle** |
| `switch.tapo_c420_south_wall_privacy` | unavailable | **off** |

The door sensors matter most: CasaRay's Security and Home boards were written
defensively around them being dark, and the defensive branches mean the cards
now simply show real door states with no change needed. That is the three-branch
guard rule earning its keep rather than a fix being required.

| ID | Page | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-318 | security, home | The Doors chip and Home's door summary now that the contact sensors report | Real states, not "No data" — and an open door should read amber, not grey | — | P1 | PENDING |
| CR-319 | — | `scripts/audit_duplicate_entities.py` — 27 friendly names carry two entity IDs on this instance | Re-run it whenever a fresh export lands; it exits non-zero if a dashboard wires up the wrong twin | `2d42e1a` | P2 | PENDING |
| CR-320 | — | **Needs Developer Tools.** Seven duplicate pairs where the export says one twin is live and one is dead. CasaRay uses the live one in every case, but nobody has confirmed which is which from the instance itself | For each pair below, look up both IDs and confirm the one CasaRay uses is the one that answers | — | P2 | **NEEDS THE OWNER** |
| CR-321 | legacy | `dashboards/deez_smart_home.yaml` references `media_player.55_qled_4k_ai`, which the export marks unavailable; CasaRay uses `media_player.q70f8036` for the same television | Not fixed — the legacy dashboard is the rollback baseline and off-limits without an instruction. Recorded so it is a known difference, not a surprise | — | P3 | **OWNER DECISION** |

### CR-320 — the seven pairs

`switch.g_printer_p100` / `…guest_room_g_printer_p100` ·
`switch.k_bot_p100` / `…kitchen_k_bot_p100` ·
`switch.k_coffee_p100` / `…kitchen_k_coffee_p100` ·
`switch.k_top_p100` / `…kitchen_k_top_p100` ·
`binary_sensor.k_motion_sensor_motion` / `…kitchen_k_motion_sensor_motion` ·
`light.bedroom_nightlight` / `light.master_bedroom_nightlight` ·
`sensor.tapo_c420_south_wall_battery` / `…_battery_2`

CasaRay uses the first of each pair. The export agrees in every case, and for
the Backyard contact sensor there is independent live evidence — its signal
level and cloud-connection entities both use the non-prefixed family and both
answer. The area-prefixed and `_2` forms look like re-added orphans. That is
a pattern, not a proof, which is why it is a row here rather than an entry in
`reconcile_entities.py`'s STALE map: a wrong entry there fails the build on a
working entity.

**Four more pairs are genuinely inconclusive** — both twins were dark when the
export was taken, so it says nothing about which is real: the three contact
sensor doors, and the two Deez Camera entities. The contact sensors have since
come back, which is exactly why "both unavailable" must not be read as "one of
these is stale".

## CasaRay — live render correction, 2026-09-19

The first pass driven by photographs of the actual wall iPad rather than by
arithmetic. Seven defects, three of them things no repository check could have
found: two dashboards' worth of kiosk configuration that has never done
anything, three dead entities the export vouches for, and a pill that does not
fit the width it is given.

| ID | Page | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|---|
| CR-306 | all | `kiosk_mode` investigated; `ignore_per_user` (not a real option) replaced by `ignore_entity_settings: true` | Run `scripts/casaray_kiosk_diagnose.sh` on the host and report its three sections | Tells us whether kiosk-mode is absent, unregistered, or registered and failing — see DR-015 | `d22ce8e` | P1 | **BLOCKED — needs the host** |
| CR-307 | climate | Three dead Sensibo tiles under Advanced → Climate React, Timer, Room occupied | The Advanced section | Three working tiles, no orange "Entity not found" | `d22ce8e` | P1 | PENDING |
| CR-308 | parents-room | The SAME dead switch under Device settings — not in the photographs, found by grep | Device settings | "Climate React", not a broken card | `d22ce8e` | P1 | PENDING |
| CR-309 | climate | The Advanced note read the dead mode sensor; now reads the live climate entity and its `temperature` attribute | Turn the AC off, then on | Off → "The air conditioner is off. Target 22°"; on → "Running in Cool, target 22°" | `d22ce8e` | P1 | PENDING |
| CR-310 | — | `reconcile_entities.py` STALE blocklist: an ID in the export but known dead now fails the build | — (repository check, negative-tested) | Re-adding one gives "IN THE EXPORT BUT DEAD: 1" | `d22ce8e` | P2 | PENDING |
| CR-311 | home | Chip strip fits one line: 0.78em, tighter padding, "2/3", whole-degree Inside | The pill under the header | `Outside 14° · Inside 20° · At home 2/3 · Monitored 0 W` on ONE line | `0d95183` | P1 | PENDING |
| CR-312 | energy, bills, security, network | These four CANNOT fit one line — 72–74 chars worst case. They now wrap into two balanced centred lines instead of an orphan | Each page's pill | Two even lines inside the pill, not a two-word second row | `0d95183` | P2 | **DECISION NEEDED — see below** |
| CR-313 | all | Footer buttons made a compact horizontal band: icon beside label, one row, smaller type | Any page's footer | A slim bar, not two near-square cards | — | P2 | PENDING |
| CR-314 | lighting | Four summary cards reduced to figure + short qualifier | The four cards | `2/6 · Living Room, Dining · 1 not reporting`, and no explanatory paragraph | — | P2 | PENDING |
| CR-315 | rooms | Room conditions shows only rooms WITH instrumentation; the other three become one closing line | The card under the tiles | Four rooms with readings, then "3 more rooms have no temperature or movement sensor — see House health" | — | P2 | PENDING |
| CR-316 | house-health | New "Instrumentation notes" section carrying the prose moved off Lighting and Rooms | Bottom of House health | Four bullets: brightness average, Living Room spots, floodlights, room sensors | — | P3 | PENDING |
| CR-317 | rooms | CN separator fixed — `、` separated both within and between rooms, so `安静、**厨房**` read as one list | Rooms with 中文 on | Rooms split by ` · `, readings within a room by `、` | — | P2 | PENDING |

### CR-312 — the strips that cannot fit, and what you can do about it

**Corrected 2026-09-19 — six pages overflow with data, nine counting dark
states, not four.** The original figures came from a throwaway script and a
hand-written state set. They have been re-measured against
`docs/live/fixture_states.json`, which takes each entity's availability from
the export and gives the answering ones a value of plausible length. Two
pages that fit under the old measurement do not, and three more overflow only
once their sensors go quiet:

| Page | With data (EN/CN) | Everything dark (EN/CN) | Over by, with data |
|---|---|---|---|
| energy | 71 / 73 | 71 / 69 | 12–14 |
| network | 70 / 72 | 78 / 79 | 11–13 |
| security | 67 / 57 | 74 / 64 | 8 |
| alerts | 65 / 46 | 78 / 57 | 6 |
| home | 61 / 51 | 70 / 57 | 2 |
| bills | 61 / — | 73 / — | 2 |
| lighting, people, house-health | fits | 60–63 EN | — |

Budget is 59 characters: the photograph's ~45 at full size, divided by the
0.78 scale, plus two bought back from padding. CJK glyphs count double.

Three things this changes:

- **`CR-311` is right in practice and wrong at the margin.** Home measures 61
  with data, two over, and the two characters are `Outside No data` — the
  outdoor sensor was dark when the export was taken. With a real outdoor
  reading Home comes in around 53 and the photograph agrees. It is not a
  defect; it is two characters of margin that do not exist.
- **`alerts` was never on the list and should have been.** 65 with data, 78
  when dark.
- **English is consistently the long language here.** Every dark-state
  overflow is English, because four repetitions of `No data` cost 32
  characters where 无数据 costs 12. That is the single biggest lever if these
  ever need to fit.

Sixteen of the twenty-two strips fit with data; three more (lighting, people,
house health) fit until their sensors go quiet and then run 1–4 over in
English. The six that are over with data carry four or five labelled readings,
and at a size that stays legible across a room there is no arrangement of five
of them that fits one line. Three ways out, none of which I took without
asking:

1. **Leave them wrapping** onto two balanced lines. Nothing is lost and the
   pill looks deliberate. This is what is shipped.
2. **Drop one reading** from each of them. Security's `Motion` and Network's
   `Hub` are the weakest — both are also tiles further down the same page.
3. **Split into two pills** per page, a row of two. Keeps every reading, costs
   a card and some vertical space.

Say which and it is a small change either way.

## Host — disk space, and a rollback bug the report found, 2026-09-24

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CFG-004 | Run `sh /config/casaray/casaray_disk_report.sh` on the host and paste the output back | A categorised read-only report: filesystem free space, the largest consumers under `/config`, and the database, logs, backups, media, cache, CasaRay backups and git clone each measured separately. It deletes nothing | — | P1 | PENDING |
| REG-016 | `sh /config/casaray/casaray_rollback.sh --list` on a host that has BOTH backup naming schemes | The list is ordered by date, and the last line is genuinely the most recent — not the newest `casaray_v2_predeploy_*` file sitting below five newer `casaray_v2.yaml.predeploy.*` ones | — | P1 | PENDING |

`REG-016` is the more important of the two. See `DASHBOARD_ISSUES.md`: a bare
rollback on a mixed-scheme host restored the newest backup of the OLD naming
scheme whatever the dates were, and `casaray_safe_deploy.sh` calls rollback
on post-flight failure — so a bad deploy would have been "recovered" into a
months-old dashboard and logged as a success.

## Tooling — the rollback drill, 2026-09-24

`casaray_rollback.sh` is the last line of defence for every deployment —
`casaray_safe_deploy.sh` calls it on post-flight failure — and it had never
been executed. A rollback that silently does nothing is worse than no
rollback, because the deploy script would then report success.

`scripts/test_rollback.sh` now proves the LOGIC: 17 assertions against a
throwaway `/config` tree, all passing. What it cannot prove is that the paths
on the host are right, that the suite is installed, or that Home Assistant
picks up a changed file at all. That is `docs/ROLLBACK_DRILL.md`, and it is
ten minutes.

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CAP-004 | Run `docs/ROLLBACK_DRILL.md` end to end on the host | Marker appears at step 3, rollback restores at step 4, `cmp` says IDENTICAL at step 5, page normal afterwards | `9fbdbcb` | P1 | PENDING |
| CAP-005 | **Step 3 specifically:** does the edited file reach the screen after a refresh, and does it need a HARD refresh? | The marker appears. If it does NOT appear even after a hard refresh, that is a bigger finding than the drill — it would mean a deployed file does not reach the screen without a reload step nobody has written down, and every "deployed" claim in this project needs revisiting | `9fbdbcb` | P1 | PENDING |

The drill is safe by construction: step 1 takes a copy outside the suite's
reach, the only change is one cosmetic word, and a single `cp` ends it at any
point. Worst case if interrupted is `CasaRay ROLLBACK TEST` on the wall.

## CasaRay — bilingual collisions from the CVA-013 room summaries, 2026-09-24

`2016214` (room-centric Home summaries) left `ha-deploy` **failing its own
validation gate** with four check-15e collisions. It was on the branch, and
`scripts/sync_casaray_to_config.sh` would have put it on the wall.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| REG-015 | Three new Chinese phrasings replaced by the terms already established elsewhere in the file: 卷帘关闭→卷帘已关, 卷帘打开→卷帘已开, 冰箱门关闭→冰箱已关闭. Separately, `Movement` was doing two jobs — a chip-strip LABEL and a room-summary STATE — so the senses are split: labels are `Motion`/动作 on all four chip strips, the state stays `Movement`/有动作 as the wall mockup calls it | With 中文 on: a room summary with the blind closed, and the Kitchen/Living Room/Ray Bedroom chip strips. Then in English | CN: 卷帘已关, 冰箱已关闭, 有动作 — one term per meaning, matching the rest of the page. EN: chip strips read `Motion  Quiet`, room summaries read `Movement` | `53f18e9` | P1 | PENDING |

Found by `scripts/verify_change.sh` on the first run after rebasing onto the
new commits — which is the whole reason it exists.

## CasaRay — band reorder against the mobile mockup, 2026-09-20

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CVA-004 | Home's bands reordered: One tap, then Rooms and Shopping list, now sit directly under Needs attention. Right now and Who's home moved below them. Nothing else changed — no card, no entity, no geometry | **iPhone:** scroll Home from the top. **Wall iPad, landscape:** look at the whole page | Phone: the scene bar is reachable without scrolling past the weather. iPad: One tap is still four across and full width; Rooms sits beside Shopping list and Right now beside Who's home, with **no half-empty row anywhere**. If any band has a hole in it, mark FAIL — that is the failure mode DR-013 describes and it is invisible from here | `fa816a1` | P2 | PENDING |

Rooms and Shopping list moved with One tap rather than after it: both are
`column_span: 1` and moving either alone would strand the other as a lone
half-row, which `dashboard_check.py` check 15 fails the build on.

## CasaRay — iPhone live render, 2026-09-19

Six photographs of the live dashboard on the iPhone. The first thing they
establish is not a defect: **the instance is running an older build.** Its
Home chip strip reads `Inside 24.0°` and `At home 1 of 3`; the committed one
reads `Inside 24°` and `At home 1/3`, and the wording in the photographs is
`d22ce8e` exactly. So nothing from `0d95183` onward — the chip compaction,
the compact footers, the plainer Lighting, the compact Rooms conditions, the
dead-Sensibo fixes, CR-322 and CR-323 — is live. Running
`scripts/sync_casaray_to_config.sh` is what closes most of what these
photographs show.

Three things in them are new, and two are fixed here.

| ID | Page | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|---|
| CR-324 | home | Needs attention named what its count is made of. It read `1 thing needs attention. 1 battery is not reporting.` while the only card on screen was Bills unpaid — the second sentence read as the first one's explanation and was a different fact | Home → Needs attention, with an unpaid bill and a silent battery sensor | `1 thing needs attention: 1 unpaid bill. 1 battery is not reporting.` The colon list must always match the count and the cards below it | `b96067e` | P1 | PENDING |
| CR-325 | home | Two tile names truncated at phone width: `House pow…` and `Parents Ro…`. Renamed `House power` → `House now` and `Parents Room` → `Parents`; `Front door` → `Front` follows it so the door row is three place names | Home on the **iPhone** → Energy now, and the door row under Security | Energy reads `House now · Used today` over `Solar now · Solar today` — a now/today, house/solar matrix, nothing clipped. Doors read `Front · Parents · Backyard` | `b96067e` | P2 | PENDING |
| CR-326 | home, energy | **Not fixed — needs you.** `Used today` reads `22.187 kWh` and `Solar today` reads `17,630 Wh`: same quantity, same band, different unit and precision. Both are plain tiles, so the unit comes from Home Assistant's entity settings, not from this repository | Settings → Devices & services → Entities → `sensor.primo_5_0_1_1_energy_day` → unit of measurement | Set it to `kWh` and display precision to 2, so the pair reads `22.19 kWh` and `17.63 kWh`. Say the word and I will do the same for `Used today`'s three decimals | — | P3 | **OWNER ACTION** |

Also confirmed on the phone, all previously recorded: `kiosk_mode` still does
not hide Home Assistant's header or tab bar (`DR-015`/`CR-306`, still waiting
on `scripts/casaray_kiosk_diagnose.sh` from the host); the chip strip wraps to
two lines, which at phone width is the shipped behaviour and not `CR-312`;
and all six cameras are answering (`Cameras 6/6`), so the export's
`unavailable` rows for them are stale, as `CLAUDE.md` already warns.

## CasaRay — truthfulness pass from a populated render, 2026-09-19

The first pass run against `docs/live/fixture_states.json` rather than an
empty state map. Rendering every markdown card with its entities *present*
surfaced two things the all-dark pass could not, and one of the two turned
out to be a defect in the renderer rather than in a card.

| ID | Page | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|---|
| CR-322 | network | Cloud-linked devices printed `0/0` when no device answered. The denominator was already "what answered", which is right; nothing being 0 of is not | Network → the Cloud-linked devices card, with the Tapo cloud sensors healthy, then with the integration reloading | Healthy: `9/10 · 4 not reporting` (a real fraction). Nothing answering: `No data · 14 not reporting`, never `0/0` | `2d42e1a` | P2 | PENDING |
| CR-323 | house-health | The update card said how many devices were silent but not how many were fine, so `7 not reporting` carried no scale. The healthy count is appended, and only when it is non-zero | House health → the update status card | `7 devices are not reporting an update state; 67 are up to date.` With a pending update: `2 updates available: <names>.` first. With everything dark: the count of silent devices ALONE, never "0 are up to date" | `2d42e1a` | P2 | PENDING |

Neither is visible on a healthy instance in the way that matters — both
concern what the card says when a sensor drops out — so both are **[guard]**
checks. To see CR-322's, reload the Tapo integration and look before it
finishes.

## Tooling — live screenshot capture, 2026-09-19

`scripts/casaray_capture.sh` writes a deterministic PNG of a rendered CasaRay
view into `artifacts/screenshots/`, where it is committed and read back here.
It is the first thing in this project that lets a visual check run without Ray
photographing the wall iPad.

Every path is exercised against a local stand-in — see
`CASARAY_VISUAL_WORKFLOW.md`. What a stand-in cannot prove is that it works
against a real Home Assistant, because this environment has no route to one.
These three rows are that proof, and they are one command each.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CAP-001 | Capture script added | On any LAN machine with Chromium: `sh scripts/casaray_capture.sh --url http://<ha-host>:8123 --check` | Prints `reachable : yes` and `dom probe : dashboard`. If it says `login`, that is the expected answer on a secured instance and CAP-002 covers it | `55631a1` | P1 | PENDING |
| CAP-002 | Token path via Playwright | Only if CAP-001 printed `login`: create a long-lived token (profile → Security), `export CASARAY_HA_TOKEN=...`, `pip install playwright && playwright install chromium`, re-run `--check` | `playwright : python`, `dom probe : login`, then `method : playwright-python` — the script proceeds instead of refusing. **Do not pass the token as an argument**; it would land in `ps` and shell history | `55631a1` | P1 | PENDING |
| CAP-003 | First real capture | `sh scripts/casaray_capture.sh --url http://<ha-host>:8123 --label first home`, then commit `artifacts/screenshots/` | A PNG of the CasaRay **Home** view, not the login form and not a blank page. If the page is half-drawn, the settle time is too short — re-run with `--wait 8000` and say so | `55631a1` | P1 | PENDING |

## CasaRay — theme, background and glass rebuild, 2026-09-15

The dashboard did not look like the renders because of what was underneath it:
the approved 14/09 mockups have **no photographic background**, and the theme
was compositing glass over one. Every surface colour is now sampled from the
renders and lives in a `--casaray-*` token; the dashboard carries no hardcoded
colour at all. `DR-014`.

**Layout is untouched.** No card moved, no `grid_options` changed, no section
span changed. Entity references 434, navigation 124 links across 28 targets,
all identical. The legacy dashboard and its five themes keep the photograph.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-268 | **Background is four CSS gradients, not the night-sky photo** | Open any CasaRay view | A deep charcoal-navy field, marginally lighter at the top, one soft blue bloom bleeding down from the upper right, edges slightly darker. **No photograph.** If you want it back it is one commented line in the theme — say so | `63dc2b8` | **P1** | PENDING |
| CR-269 | **Legacy dashboard must be unaffected** | Open `/deez-smart-home/` | Still the Your Name night sky, exactly as before. If this changed, something reached the shared anchor and I need to know | `63dc2b8` | **P1** | PENDING |
| CR-270 | **Card surfaces rebuilt from sampled values** — one glass tint at three alphas | Look at any card against the background | Cards clearly float above the background but stay quiet; they *lighten* what is behind them rather than being a flat colour | `63dc2b8` | **P1** | PENDING |
| CR-271 | **Three depth levels.** L1 background · L2 ordinary card · L3 chip strip and status cards, brighter with a stronger border | Compare the chip strip against an ordinary tile | Visibly different, not identical. If they read the same the third level is not landing | `63dc2b8` | P2 | PENDING |
| CR-272 | **138 hardcoded rgba literals replaced by theme tokens** across 69 card_mod blocks | Look at a red alert, an amber alert, and a dashed grey unavailable tile | All three still tinted correctly. This is the change most likely to have broken something invisible, because it touched 69 blocks | `63dc2b8` | **P1** | PENDING |
| CR-273 | **Blur halved and `saturate` dropped** — `blur(14px) saturate(118%)` to `blur(6px)` | Scroll Home on the wall iPad | Should feel *smoother* than before, not worse. Over a flat gradient the heavy blur was doing almost nothing visible | `63dc2b8` | **P1** | PENDING |
| CR-274 | **Typography lifted for the darker background** — secondary `#9fb0c6` → `#9aa7b8`, muted → `#6f7b8c` | Read a tile's second line and a footnote from across the room | Six levels legible: heading, value, name, secondary, muted, "no data". Tell me if anything is too dim — the background is darker than it was, so these were raised, not carried across | `63dc2b8` | **P1** | PENDING |
| CR-275 | **Section containers were deliberately NOT given a surface** | Look at any section heading | Headings sit on the background with a dim icon, as the renders draw them. Wrapping sections in a panel would have moved cards, which this pass was not allowed to do | `63dc2b8` | P3 | PENDING |
| CR-276 | **Domain state colours now come from the theme** (`error`/`warning`/`success`/`info`) | Look at a tile that colours itself by state | CR-232 semantics without a per-card `color:` | `63dc2b8` | P3 | PENDING |

## CasaRay — Home recomposed for TWO columns, 2026-09-15

Ray's live check of `9534181` settled the question the last two passes had to
assume: **with kiosk_mode hiding both the sidebar and the header, the wall
iPad resolves the sections view as two columns, not three.** Right now went
left, Who's home went right, and One tap dropped to a row of its own with a
hole beside it — the signature of a `column_span: 3` page getting two columns.

So Home is now `max_columns: 2`, composed as bands in which every row is
either a matched pair or one full-width group. `DR-013`.

**Layout only.** No entity, service call, template, navigation target,
bilingual rule, kiosk setting or data guard changed. Entity references 434,
distinct entities 447, navigation 124 links across 28 targets, five
service-call types — every one identical to `b5e8522`.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-260 | **`max_columns` 3 → 2**, and every page-level band `column_span` 3 → 2 | Open Home on the wall iPad | Two body columns, and **no row with an empty half**. This is the check that matters; everything below is detail | `e39b2bb` | **P1** | PENDING |
| CR-261 | **Row: Right now \| Who's home** | Look below Needs attention | Side by side. Right now is the taller of the two — a modest gap under Who's home is expected and is not the defect being fixed | `e39b2bb` | **P1** | PENDING |
| CR-262 | **One tap is now full width**, four scene cards across at `columns: 3` | Look at the One tap band | Evening, Night, Bright, All lights off in **one row of four**, evenly spaced, large. Tap each — same brightness presets, unchanged | `e39b2bb` | **P1** | PENDING |
| CR-263 | **Row: Rooms \| Shopping list** | Look at the Rooms band | Seven room rows in the left column at roughly the width the 14/09 render draws them; the list beside them, not under them | `e39b2bb` | **P1** | PENDING |
| CR-264 | **Security stays full width** — splitting the summary/camera/tiles panel would have broken a composition that already reads well | Look at the Security band | Unchanged from the last sync | `e39b2bb` | P2 | PENDING |
| CR-265 | **Row: Energy now \| Recent activity.** Energy's four tiles went 4-across to **2-across, two rows** — at half the page width four in a row is ~140px each and `House power` breaks. Logbook `rows` 2 → 4 to sit level | Look at the lower band | Four energy figures in two rows on the left, logbook on the right, roughly level. `House power` on one line. Solar still reads no data while the inverter is unreachable — that is correct, not a bug | `e39b2bb` | **P1** | PENDING |
| CR-266 | **More boards unchanged in shape**, now full width of two columns | Read every label | Still three rows of four, then House health and English / 中文. 4 × `columns: 3` fills the 12-column grid exactly, so the renderer **cannot** pack them eight-across — that was the explicit ask | `e39b2bb` | P2 | PENDING |
| CR-267 | **Deviation from the requested Row B.** The brief asked for One tap on the left with compact content on the right. At two columns every other section is already paired, and the only candidates were sections pinned to other rows or content that would have had to be invented. Full width was the honest answer | Judge whether the One tap scene bar works | If you would rather have One tap \| Shopping list with Rooms full width, say so — it is two `column_span` values. Note Rooms across the whole page becomes a name and a state at opposite ends of a long empty row | `e39b2bb` | P3 | PENDING |

## CasaRay — Home live-render geometry correction, 2026-09-15

The 2026-09-15 rebuild was structurally right and visually wrong on the real
iPad. Every symptom Ray reported shares one cause: **`grid_options.columns` is
a fraction of the width the renderer actually gives a section, and that width
was far smaller than the grid arithmetic predicted.** A 1/12 cell broke
`CasaRay` vertically; a 3/12 markdown card came out narrower than its own
minimum height and drew a circle; a 2/12 button could not hold
`Entertainment`.

So this pass widened everything and rebuilt the page as explicit horizontal
bands instead of three vertical stacks of unequal height. No entity, service
call, navigation target, template or bilingual rule changed — entity
references stayed at 434, navigation at 124 links across the same 28 targets,
and the five service calls are byte-identical.

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| CR-251 | **The page is horizontal bands now.** A: Right now / Who's home / One tap. B: Rooms (2 of 3) / Shopping list (1 of 3). C: Security, full width. D: Energy now (2 of 3) / Recent activity (1 of 3). E: More boards, full width | Look at the page as a whole on the wall iPad | Five readable bands, each filled across. **No tall blank gaps** below a short group | `b5e8522` | **P1** | PENDING |
| CR-252 | **Rooms went from 1 column of 3 to 2 of 3** | Look at the room rows | Room name and its state line comfortable on one row each, not fighting for space. All seven rooms present, each still opening its own board | `b5e8522` | **P1** | PENDING |
| CR-253 | **More boards rebuilt 6-across → 4-across**, `rows: 2`, in the order Rooms/Lighting/Climate/Energy · Bills/Entertainment/Security/Cameras · Network/People/Automations/Alerts, then House health and English / 中文 at half width each | Read every board label | **Every label fully readable, none running into its neighbour.** Large targets. All 14 still navigate | `b5e8522` | **P1** | PENDING |
| CR-254 | **Shopping list sized `rows: 6`** so it fills the band beside Rooms instead of leaving a hole | Look right of Rooms | A full-height list card, still editable, still `todo.shopping_list` | `b5e8522` | P2 | PENDING |
| CR-255 | **Recent activity moved beside Energy** at 1 of 3, logbook `rows: 2` | Look at the lower band | Energy figures left, logbook right, roughly level. No near-empty strip across the page | `b5e8522` | P2 | PENDING |
| CR-256 | **One tap and Who's home cards are taller** — scene buttons `rows: 3`, person cards `rows: 3` | Tap a scene button | Big elder-friendly targets; same four presets, same brightness values, unchanged behaviour | `b5e8522` | P2 | PENDING |
| CR-257 | **`white-space: nowrap` on the wordmark and clock** — a hard guarantee, not a width bet | Look at the top corners | Neither can wrap, whatever the container. If either is ever *clipped* instead, that is the container being narrower than expected — worth telling me | `b5e8522` | P3 | PENDING |
| CR-258 | **Chip separator disambiguated.** The strip joins its four readings with ` · `, so the Home chip's own separator became `,` in English and `、` in Chinese | With one tracker down, read the Home chip | `Home 1 of 3, 1 unknown` — not a fifth reading | `b5e8522` | P3 | PENDING |
| CR-259 | **Monitored power prints `0 W`, not `0.0 W`**, while `147.9 W` keeps its decimal | Read the Monitored chip at a moment of zero draw | `Monitored 0 W` | `b5e8522` | P4 | PENDING |

**If three columns are not what the iPad renders**, say so — the whole band
plan assumes three, and at two the `column_span: 2` groups (Rooms, Energy)
take a full row and leave their partner half a row to itself. That is one
line of YAML to change, but only Ray can see which it is.

## CasaRay — defects found live on 2026-09-06 and fixed

Both were invisible to every repository check, because both are about how wide
a card renders — exactly the class `DEPLOYMENT_BLOCKERS.md` says this
environment cannot see. They were caught in the first five screenshots.

| ID | What was wrong | Fix | Commit | P | Result |
|---|---|---|---|---|---|
| CR-160 | **Room page titles broke mid-word** — "Livin g Roo", "Kitch en", "Dinin g". The 7 room views gave the title card `columns: 4` while all 13 board views gave it `6`, so `Rooms` rendered correctly and `Living Room` did not. Not a font problem; a grid-width one | Room titles widened 4 → 6, matching the boards. Row 1 becomes Back(2)+Home(2)+title(6); the clock wraps to its own row on room pages only | `3683782` | **P1** | PENDING — recheck |
| CR-161 | **Every page had a horizontal scrollbar on the clock card.** The clock was an `<h1>` inside a 4-column card, so its content was wider than the card. It was also the wrong heading level — the page title is the h1, and two h1s per page is simply incorrect | Clock demoted `#` → `##` on all 20 non-subview pages. Still the large line with the date directly beneath, so the mandated form is unchanged | `3683782` | **P1** | PENDING — recheck |

**Re-check both after the next sync:** open any room page. The title must read
as one word — `Living Room`, not `Livin g Roo` — and no card may have a
scrollbar under it. Then check one board page (`energy`) for the scrollbar too.

## CasaRay — layout

| ID | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-150 | Any board, **iPad landscape** | Two readable columns. No label truncated, no empty grid tracks | `5dc6f50` | P2 | PENDING |
| CR-151 | Home and one room, **iPhone** | Usable; cards stack rather than squash | `5dc6f50` | P3 | PENDING |
| CR-152 | Any board | Frosted-glass cards over the night-sky background, as the legacy dashboard has. If surfaces look flat, the theme is not applying — v2 carries no `card_mod` and relies entirely on the theme | `5dc6f50` | P2 | PENDING |

---

## Recording results

Either edit the Result cell directly, or just tell the routine — one result
per line, batches fine:

```
UI-027 PASS — readable on iPad landscape
UI-020 FAIL — Total Solar shows a bare number with no unit
REG-005 PARTIAL — English wording works, Chinese is inconsistent
```

`PASS` · `FAIL` · `PARTIAL` · `PENDING`. The note after `—` is optional and
is kept where it carries the symptom. Full reconciliation rules — what each
result does to the issue record, the backlog and ownership — are in
`PROJECT_STATE.md` under **Live Verification**.

- A short note after the result is welcome.
- A routine reconciling results applies the rules in `PROJECT_STATE.md`:
  `PASS` may move the item to `LIVE_VERIFIED`; `FAIL` reopens an actionable
  regression under the same stable ID; `PARTIAL` keeps the passing portion and
  creates a narrowly scoped follow-up rather than a wholesale reimplementation.
- Creating or reading this queue is **not** verification, and neither is a
  passing validation run, a successful deploy, or an unreviewed screenshot.
  A human result is the only source of `LIVE_VERIFIED`.
- `PASS` rows stay for traceability. A page group with nothing left
  outstanding may collapse to a one-line summary naming its IDs and date.

**115 checks pending**, in two separate sets that must not be merged:

| Set | Dashboard | Rows | Pending | Passed |
|---|---|---|---|---|
| `UI-*` / `REG-*` / `BILL-*` / `CR-001`–`CR-002` | legacy `/deez-smart-home/…` | 48 | 47 | 1 |
| **`CR-1xx` / `CR-2xx`** | **CasaRay `/casaray-v2/…`** | **74** | **68** | **6** |

**Check `CR-220` first.** CasaRay now declares its own theme, so a deploy
that misses `themes/deez_your_name.yaml` renders the whole dashboard
unstyled. Everything else on the list is unreadable through that.

**Five owner questions sit outside both counts** — they cannot pass or fail,
they need an answer:

| | |
|---|---|
| **`CR-195`** | **Do the Parents Room emergency buttons register a press?** The one safety question here. **Deferred by the owner 06/09/26** — left open, untouched, and not investigated this session. |
| `CR-212` | Where does "Not yet available" come from? It is no longer in the dashboard file at all, so it is either an entity state or a stale deployed copy. |
| `CR-213` | What do `house_status`, `active_rooms_count` and `house_lights_on` actually count? `casa_offline_devices` was mislabelled; these three are unverified. |
| `CR-190` | Which half of each TV pair is the real television? Narrowed 07/09 from live data. |
| `CR-183` | What reads the Family Location selector? Its options are people — confirmed live 07/09. |

The CasaRay rows started at 23, added 2026-09-05 ahead of first deployment;
six passed on the 06/09 screenshots and the 2026-09-05 upgrade batches added
`CR-170`–`CR-199`. Start with `CR-100` (does it load) and `CR-110`–`CR-114`
(navigation) — if the dashboard was registered under any key other than
`casaray-v2`, all 87 internal links break at once and everything below is
noise until that is fixed. After that, `CR-179` is the one to check on every
board at a glance: it is a rendering fault that would be obvious in a
screenshot and affects six pages.

The legacy 47 are **lower priority now**. That dashboard is the rollback
baseline, not the build target; verifying its backlog matters less than
verifying the one replacing it.

*Legacy count derivation, retained:* 47 = 45 carried forward + 2 rows added by
the CasaRay Batch 1 implementation: `CR-001` and `CR-002`, the P1 clock/date
component in the legacy Home header — see `DASHBOARD_PROGRESS.md`. That 45 was
44 carried forward + 1 row: `UI-032`,
the battery-health alert on Home — see `DASHBOARD_ISSUES.md`. That 44 was
43 carried forward + 1 row added by the Billing
Dashboard Upgrade routine: `BILL-005`, a `card_mod` text-shadow
fix on 4 title cards — see `BILLING_PROGRESS.md` for the full batch. The
43 itself was 44 carried forward, less `UI-011` which the owner recorded
`PASS` on 30 Aug 2026 — the first live result this queue has received; that
44 was in turn 43 carried forward + 1 row added by the Billing Dashboard
Upgrade routine: `BILL-004`, guarding ten bill status/amount cards on
`bills` and four `bill-*` subviews against raw `unavailable`/`unknown`
interpolation).
UI-025, UI-026 and `UI-011` are `VERIFIED`; `UI-011`'s row is kept above
for traceability, per Queue upkeep. The Energy group still has `UI-020` and
`UI-021` `PENDING`, so it does not collapse yet — and note that `UI-020`
(Total Solar *carries a unit*, Powerpal battery guarded) is a **different**
check on the same card and was **not** covered by the UI-011 result. `BILL-001`'s
account-number fix is now pushed and listed above under Bills & rooms; its
still-`BLOCKED` NMI/MIRN portion is implementation work, not a verification
item, and stays in `DASHBOARD_BACKLOG.md`. `DR-001` (iPad density) is also
implementation work, not yet coded, and stays in `DASHBOARD_BACKLOG.md`.
