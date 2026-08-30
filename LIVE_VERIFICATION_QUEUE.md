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
| REG-007 | House Pulse door count/colour guarded **[guard]** | House Pulse hero with all three door sensors disabled | Text calls out "N door sensor(s) offline" / "N 个门传感器离线" and the icon turns grey, not a confident green "0 open" | (this commit) | P2 | PENDING |

## Security — `/deez-smart-home/security`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-005 | Door state guarded **[guard]** | The door cards with a contact sensor disabled | Neutral/unknown, never a confident green "Closed" | `b1ef565` | P1 | PENDING |
| REG-001 | Door state translated **[中]** | The three door cards with the toggle on | 开启/关闭, not English Open/Closed | `b5eee22` | P3 | PENDING |

## Energy — `/deez-smart-home/energy`

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-011 | Total Solar converted Wh→kWh | Compare Total Solar against Day and Year figures | Same order of magnitude. **If Total reads ~1000× smaller, the conversion is wrong — mark FAIL** | `df457e3` | P1 | PENDING |
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

## Lights — `/deez-smart-home/lights` and lighting subviews

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| REG-002 | Motion quick-status chips guarded, on **both** Lights and Cameras **[guard]** | Both chips with their motion sensors disabled | Reads offline/—, never a confident "Quiet". Check both pages before recording | `b5eee22` | P1 | PENDING |
| UI-010 | Page title moved above the section heading | Open each of the 4 lighting pages | Page opens with its own title, not a section label | `e06d0ce` | P2 | PENDING |

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
| REG-008 | Doors chip guarded and translated **[guard][中]** | Doors status chip with all three door sensors disabled | Reads "Sensor offline" / 传感器离线 and turns grey, not a confident bare-English "0 open" / green | (this commit) | P2 | PENDING |

## Climate & Status

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-007 | Climate and Status given structure | Both pages in landscape | Multi-column, not a flat single column; Climate shows the full thermostat | `bb05c7c` | P2 | PENDING |

## Bills & rooms

| ID | What changed | What to check live | Expected result | Commit | P | Result |
|---|---|---|---|---|---|---|
| UI-016 | Last nested grids dissolved on `bills`, `light-living-room`, `lighting-modes` | All three page layouts | Cards sized normally, not squeezed inside half-width sections; the six bill subviews each read as one clean column | `9b28fdb` | P2 | PENDING |
| UI-013 | Duplicate media cards removed | Parents Room and Guest Room | One media control per player, not a Mushroom card stacked on a native one | `56c7656` | P3 | PENDING |
| UI-023 | Placeholder cards removed | Ray Bedroom and other room pages | No "nothing here yet" cards taking up columns | `3048e54` | P2 | PENDING |
| UI-024 | Third kitchen plug named and restyled | Kitchen plugs | All three named (no raw entity ID) and styled alike | `3048e54` | P3 | PENDING |

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
UI-011 FAIL — Total Solar is about 1000× too small
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

**33 checks pending.** UI-025 and UI-026 are already `VERIFIED` and are not
listed. `BILL-001` (billing privacy) and `DR-001` (iPad density) are
implementation work, not verification items, and stay in
`DASHBOARD_BACKLOG.md`.
