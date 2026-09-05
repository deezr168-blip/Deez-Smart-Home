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
| CR-196 | Living Room — Air quality | PM1, PM2.5 and PM10, each paired with its health-concern word. This is what CR-122 always expected; only now is it built | `28b520e` | P2 | PENDING |
| CR-197 | Ray Bedroom / Garage — socket overload | A "Socket overloaded" tile in Ray Bedroom's Power use, and "Socket reachable" in the Garage Freezer section | `28b520e` | P2 | PENDING |
| CR-198 | House Health — updates | Core, Supervisor and Operating System tiles, plus a line counting every pending update across all 74 update entities | `614ad5e` | P2 | PENDING |
| CR-199 | Dining — Temperature | A temperature tile in Sensors, reading the same figure the Climate board shows as Dining. **If the two disagree, say so** | `PLACEHOLDER` | P2 | PENDING |

### Needs an owner answer before it can be built

| ID | Question | Why it is blocked |
|---|---|---|
| CR-183 | What is `input_select.input_select_family_location_selected` for, and what are its options? | Live and `ok`, but the B1 export carries names only, not option lists or the automations that read them. Surfacing a selector whose effect is unknown could change household state by mis-tap. Not added. |
| CR-190 | **Three `media_player` entities exist for the one Parents Room TV.** Which is the real one? | `media_player.55_qled_4k_ai` reads `unavailable`; `..._qa55q7faawxxy` and `master_bedroom_55_qled_4k_ai` both read `ok`. CasaRay was pointing at the unavailable one, so that card has never worked. It now points at `..._qa55q7faawxxy`, chosen because it pairs with `remote.55_qled_4k_ai_qa55q7faawxxy` — a matched media_player + remote pair is what a current Samsung integration entry looks like, where `master_bedroom_` is the prefix carried by several known-dead duplicates in this instance. **Reasoned, not conclusive.** If the Parents Room TV card still does not work, the answer is one of the other two. The legacy dashboard was left on the old ID on purpose: it is the rollback baseline, and a TV that is switched off at the wall can legitimately read `unavailable`, so this is not conclusive enough to edit it. Deleting the stale duplicates is an owner action, not one this routine takes. |
| CR-195 | **Do the Parents Room emergency buttons actually register a press?** | This is the one item in this queue that is a safety question rather than a display question. `binary_sensor.emergency_button_dad_cloud_connection` and the Mum equivalent both read `ok`, so the page can honestly say the buttons are connected and their signal is good. But the two press-event entities, `event.master_bedroom_emergency_button_dad_main` and `event.master_bedroom_emergency_button_mum_main`, both read **`unavailable`** — so as far as this export shows, a press produces nothing Home Assistant can see. The page now says so in both languages rather than letting "Both emergency buttons are connected" be read as "the buttons work". **Please press one and check Developer Tools → States for that event entity, or Settings → Devices for a logged press.** If it stays unavailable the buttons are connectivity indicators only, and whatever is meant to happen when someone presses one is not wired up. Nothing was added or changed on the devices themselves. |

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

**87 checks pending**, in two separate sets that must not be merged:

| Set | Dashboard | Rows | Pending | Passed |
|---|---|---|---|---|
| `UI-*` / `REG-*` / `BILL-*` / `CR-001`–`CR-002` | legacy `/deez-smart-home/…` | 48 | 47 | 1 |
| **`CR-1xx`** | **CasaRay `/casaray-v2/…`** | **46** | **40** | **6** |

`CR-183` and `CR-190` are excluded from both counts: they are questions for
the owner, not checks that can pass or fail.

The CasaRay rows started at 23, added 2026-09-05 ahead of first deployment;
six passed on the 06/09 screenshots and the 2026-09-05 upgrade batches added
`CR-170`–`CR-189`. Start with `CR-100` (does it load) and `CR-110`–`CR-114`
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
