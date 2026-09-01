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
| CR-001 | **CasaRay Batch 1 — P1 clock/date added to the Home header** | Directly under the page title, above the English/中文 toggle row: a clock-icon card | Two lines: the time (e.g. `5:42 PM`, no leading zero) with the date **directly underneath it** as `DD/MM/YY` (e.g. `01/09/26`). Watch it tick over a minute boundary — it must update on its own. Tapping it must do nothing. **If the date shows any other format, or sits beside the time rather than under it, mark FAIL** | `PENDING-SHA` | P2 | PENDING |
| CR-002 | CasaRay Batch 1 — header layout on the iPad | The same clock card, iPad landscape | It sits on the sky with no glass card behind it, matching the title and chip rows around it, and its text stays legible against the background. Note whether it renders **beside** the title or **under** it — that answers whether a follow-up should narrow the title to 8 columns | `PENDING-SHA` | P3 | PENDING |

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

**47 checks pending** (45 carried forward + 2 rows added this run by the
CasaRay Batch 1 implementation: `CR-001` and `CR-002`, the P1 clock/date
component in the Home header — see `DASHBOARD_PROGRESS.md`. That 45 was
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
