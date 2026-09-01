# CasaRay — dashboard design reference

**Status: source reference.** This document is the authoritative description of
the intended look and content of the Deez Smart Home dashboard. When a change to
`dashboards/deez_smart_home.yaml` touches layout, wording, colour or card
structure, it is checked against this file.

## Provenance

Twelve rendered mockups of a design system branded **CasaRay** were supplied by
the owner on 2026-08-31 and designated the source reference for the dashboard.

The mockups were supplied as pasted images in a maintenance session, not as
files, so **the image binaries are not present in this repository** and could not
be committed — nothing was written to disk that could be recovered. This document
is a transcription of them, made while the renders were on screen, and it is the
form the reference survives in here. If the owner still holds the original PNGs,
committing them under `design/mockups/` alongside this file would make the
reference complete; this text stands on its own until then.

Every screen below is described as rendered. Where a mockup contradicts another
mockup, that is recorded rather than silently reconciled — see
[Known inconsistencies](#known-inconsistencies).

## Contents

- [Global design system](#global-design-system)
- [Screen transcriptions](#screen-transcriptions)
- [Mapping to the live dashboard](#mapping-to-the-live-dashboard)
- [Known inconsistencies](#known-inconsistencies)
- [How to use this reference](#how-to-use-this-reference)

---

## Global design system

<a id="global-design-system"></a>

### Canvas

- Landscape, wide — rendered around 1672 × 941, i.e. a 16:9 wall/tablet display.
- Background is a near-black desaturated navy, close to `#080c14`, with a very
  slight vertical lift toward the top of the page.
- Cards sit on that ground as a slightly lighter translucent surface with a
  1px hairline border, generous corner radius (~14–16px) and a soft shadow —
  a restrained "glass" treatment, not a heavy blur.
- Gutters between cards are even and roomy; nothing is edge-to-edge except the
  hero image band and the footer bar.

### Three fixed frames

Every screen is built from the same three fixed elements plus a content area.

**1. Left sidebar** (~180–210px, full height)

- Wordmark top-left: `CASA` in white, `RAY` in blue — one word, two weights of
  emphasis. Rendered both as all-caps `CASARAY` and as `CasaRay`.
- Vertical nav, icon + label, generously spaced:
  Home · Rooms · Energy · Security · Cameras · Climate · Entertainment · Bills ·
  Automations · People · House Health · Settings.
- Active item is a filled rounded rectangle in a blue tint with the icon and
  label brightened; inactive items are mid-grey.
- Pinned to the bottom: a voice-assist card — an icon-labelled block reading
  **CasaRay Assist / Tap to speak** with a circular blue microphone button.

**2. Page header** (top of content area)

- Left: an icon in a rounded tile, then the page name in **large uppercase**,
  with an optional sentence-case subtitle beneath
  (e.g. `CAMERAS` / "Live monitoring and playback").
- Room screens replace the icon tile with a **Back** or **Back to Home** pill,
  and some add a breadcrumb (`Home › Rooms › Ray Bedroom`).
- Right: status pills where relevant (`People Home`, `Internet Online`,
  `2 things need attention`), then the clock — time large, date small beneath
  (`5:42 PM` / `12/09/26`).

**3. Footer status bar** (full width, below the content)

One horizontal strip, always present, in two groups:

- Weather cluster: current temp with icon (`23°C`, Sunny, "Feels like 24°C"),
  then Rain (`No rain 0%`), Wind (`12 km/h NE`), Tomorrow (`24° / 15°`),
  Saturday (`22° / 14°`).
- Bill cluster, right: `Next Bill` with due-in caption, amount in green
  (`$142.62`), then a circular blue microphone button at the far right.

### Content grid

- A **status/KPI strip** directly under the header: 4–5 equal cards, each with a
  circular icon badge, an uppercase micro-label, a large value, and a small
  caption. On room screens this becomes a row of shorter status chips.
- Room screens then run a **hero band**: a wide photographic image of the room,
  darkened, with the room name, a one-line tagline, and a `Room Settings` button
  overlaid on the left.
- Below that, a **card grid**, typically 4 columns × 2 rows on room screens and a
  mixed 2–5 column arrangement on overview screens.
- Section cards carry an uppercase title with a small coloured icon, and an
  optional right-aligned action (`View all`, `Edit`, `All Off`, `+ Add`).
- Lists inside cards are two-line rows: name on top, state beneath in muted grey,
  control on the right (toggle, slider, value, chevron).

### Colour semantics

Colour is used strictly for meaning, never decoration.

| Role | Colour | Used for |
|---|---|---|
| Primary / interactive | Blue (`#3b82f6`-ish) | Active nav, sliders, links, on-toggles, selected mode |
| Good / present / on | Green | "At Home", "Online", "Secure", solar, savings, healthy sensors |
| Caution | Amber / orange | "Due Soon", "Warning", gas, "needs attention" |
| Critical | Red | "Unpaid", "Critical" alerts, person-detected |
| AI / recording / scheduled | Purple | AI Q, recording status, "Scheduled" bills, party/movie scenes |
| Off / idle | Mid-grey | Off states, empty zones, muted captions |

Off-state toggles are grey and unfilled; on-state toggles are filled blue for
lights/generic and filled green for outlets and "always on" circuits.

### Typography

- One sans-serif family throughout.
- Page titles: large, uppercase, tight tracking.
- Card titles: small, uppercase, letter-spaced, muted.
- Metric values: very large and light-weight, with the unit set smaller and
  raised (`22.4` + `°C`).
- Row labels: regular; row states: smaller and muted.

### Recurring components

- **Circular dial** — climate. An arc gauge with the current temperature at the
  centre, a coloured arc segment for the setpoint, +/− buttons beside it.
- **Ring gauge** — percentage health (storage 68%, device health 96%,
  UV index arc, ventilation speed).
- **Area/line chart** — small, smooth, single-series, filled beneath, with a
  light axis and no gridline clutter (presence history, spending trend, power).
- **Donut with legend** — composition (spending breakdown, solar contribution).
- **Bar histogram** — usage over time (water litres, gas MJ, automation activity).
- **Timeline list** — time on the left, icon, two-line event, relative age right.
- **Thumbnail strip** — camera stills and clips with a duration or timestamp.
- **Quick-action tile** — a 2×2 or 1×4 grid of large icon buttons with a label and
  optional caption (`All Off` / "Turn everything off").

---

## Screen transcriptions

<a id="screen-transcriptions"></a>

### 1. Home

Header: sun icon, **"Good afternoon, Ray"**, date `12/09/26`. Centre pill,
amber: **"2 things need attention"**. Right pills: `People Home`,
`Internet Online`. Clock `5:42 PM`.

Top row, five cards:

- **HOUSE POWER** (`Live` badge) — `1.84 kW` Total Usage; Solar `1.30 kW`,
  Grid `540 W`, Battery `Charging • 62%`, each with a small horizontal bar;
  sparkline across `12AM–12AM`.
- **INDOOR CLIMATE** — `22.6 °C` Comfortable; Humidity `51%`, Air Quality `Good`,
  Ventilation `Balanced`; three mini stats: Average `22.0°`, Min `21.5°`,
  Max `23.4°`.
- **SECURITY** — green tick, **Secure**, "All systems normal"; checklist:
  External Doors `3 / 3 closed`, Windows `All clear`, Motion `Normal`,
  Cameras `5 / 5 online`, Alarm System `Armed (Away)`.
- **SUNLIGHT** — arc gauge, UV Index `4` Moderate; Sunrise `6:12 AM`,
  Sunset `6:05 PM`.
- **FAVOURITES** (`Edit`) — four tiles: All Lights `Off`, Climate `Auto • 22°`,
  Movie Time `Living Room`, Good Night `All Rooms`.

**ROOMS** strip (`View all rooms`) — five photo cards with a chevron:
Living Room `22.4 °C` Occupied / 3 Lights On / TV Playing / Denon AVR On ·
Kitchen `21.8 °C` No motion / 1 Light On / Dishwasher Off / Rangehood Off ·
Parents Room `23.1 °C` Occupied / Climate On / 2 Lights On ·
Ray Bedroom `21.5 °C` No motion / All Lights Off / Climate Off ·
Bathroom `22.0 °C` No motion / All Lights Off / Fan Off.

Bottom row, four cards:

- **ENERGY TODAY** — Solar Generated `18.6 kWh`, House Consumed `14.2 kWh`,
  Grid Imported `3.1 kWh`, Grid Exported `7.5 kWh`; donut Solar Contribution
  `78%` with Self Consumption `60%`; footnote "You are exporting 800 W to the
  grid".
- **ATTENTION** — Backyard door open `18 minutes ago`; Garage camera offline
  `2 hours ago`; `View all (2)`.
- **RECENT ACTIVITY** — Front Door unlocked `5:35 PM`; Parents Room climate set
  to 23° `5:21 PM`; Dishwasher cycle finished `4:48 PM`; Ray arrived home
  `4:32 PM`; `View all activity`.
- **CAMERAS** (`View all`) — Front, Driveway, Backyard, Side Gate thumbnails,
  each with a green online dot.

### 2. People Mapping

Header: people icon, **PEOPLE MAPPING**, "Live household location and zone
overview".

KPI strip: Total People Tracked `4` (All family members) · At Home `2`
(50% of household) · Away / Out `1` (25% of household) · Active Zones `5`
(All zones online) · Household Status **All Clear** (Normal activity).

- **LIVE LOCATION MAP** — dark vector map with `Live` badge, zoom `+`/`−` and
  recentre controls. Zone pills pinned on the map: Home `2 people`,
  Work `1 person`, School `0 people`, Shops `1 person`, Gym `0 people`.
  Person markers with dotted route traces; a label "Ray — En route home" and
  "AI Q — Near Shops". Legend: At Home · In Transit · Away · Zone.
- **HOUSEHOLD PEOPLE** — four avatar cards, each with name, state, place,
  "Updated N min ago", battery %, signal icon, and an ETA button:
  Ray `Home` / Home / 2 min / `98%` / ETA 0 min ·
  Parent 1 `Away` / Work / 8 min / `82%` / ETA 28 min ·
  Parent 2 `Away` / School Pick-up / 5 min / `76%` / ETA 12 min ·
  AI Q `In transit` / Near Shops / 1 min / `63%` / ETA 6 min — this card is
  outlined in purple, marking it as the non-human member.

Bottom row, five cards:

- **ZONES** — Home 2 · Work 1 · School 0 · Shopping 1 · Gym 0, each with a
  status dot.
- **RECENT MOVEMENT** — timeline: `5:40 PM` Ray arrived home / Front Door
  Geofence · `5:34 PM` Parent 1 left Work · `5:30 PM` Parent 2 left School ·
  `5:36 PM` AI Q near Shops · `5:20 PM` AI Q left Gym; relative ages on the right.
- **QUICK ACTIONS** — View all people · Navigate home · Share location ·
  Privacy mode (toggle) · Refresh locations.
- **LOCATION ALERTS** — Geofence Exit `Critical`; Delayed Arrival `Warning`;
  Battery Low `Info`; Geofence Enter `Info`.
- **HOUSEHOLD PRESENCE HISTORY** (`Today` dropdown) — green area chart,
  `12AM–12AM`, y-axis 0–6; stats: Peak Presence `4 people` 7:00 PM,
  Average `2.3 people` Today, Total Away Time `6h 45m` Today.

### 3. Cameras

Header: camera icon, **CAMERAS**, "Live monitoring and playback".

KPI strip: Total Cameras Online `6 / 6` · Active Alerts `3` (red, "Require
attention") · Motion Events Today `32` (+12 vs yesterday) · Recording Status
**Recording** (purple) · Storage Health `68% Used` (642 GB of 1 TB) with a ring.

Filter tabs: `All` (active) · Outdoor · Indoor · Alerts · Recordings.
Right: `Layout` dropdown.

Camera grid — one large tile plus five: **Front Door** (large, left),
Driveway, Backyard on the top right; Side Gate, Garage, Living Room beneath.
Each tile shows a `Live` dot, a red `REC` badge, pause and mute controls at the
bottom left, and snapshot / record / fullscreen at the bottom right.

Bottom row, five cards:

- **RECENT MOTION** (`View all`) — thumbnail rows: `5:41 PM` Front Door ·
  `5:26 PM` Driveway · `5:12 PM` Backyard · `4:58 PM` Side Gate ·
  `4:47 PM` Garage.
- **CAMERA HEALTH** (`View all`) — all six cameras listed `Online`.
- **QUICK ACTIONS** — Arm Perimeter · Privacy Mode · All Cameras · Snapshot ·
  Review Events, each with a caption.
- **ALERTS** (`View all`) — Person Detected / Front Door `Critical`;
  Package Detected `Warning`; Garage Motion `Warning`; Side Gate Opened `Info`.
- **STORAGE & RECORDINGS** (`View all`) — Storage Used `68%` with bar,
  Days Retained `18 Days`, `Adjust retention`; Recent Clips — four thumbnails
  with durations `00:24 00:32 00:18 00:26`; `View all recordings`.

### 4. Living Room

Header: `Back to Home`, sofa icon, **LIVING ROOM**.

Status chips: Occupied `3 people` · `22.4 °C` Comfortable · `3 Lights On`
70% Brightness · TV Playing "Queen of Tears" · Air Quality Good • AQI 23.

Hero: living-room photo, tagline **"Living beautifully, living intelligently."**,
`Room Settings`.

- **QUICK ACTIONS** — All Off · Relax · Bright · Movie Time.
- **LIGHTS** — Ceiling Lights `70%` slider, on; Ambient Strip `40%` slider, on.
- **POWER OUTLETS** — TV Console Outlet `On`, Floor Lamp `On`,
  Air Purifier `Off`, Smart Plug (Fan) `Off`.
- **ENTERTAINMENT** — Samsung QN90C, `HDMI 1 • 4K`, power button; now playing
  "Queen of Tears" `S1 E10 • 42:18 / 1:05:10` with poster, transport controls
  and volume `45%`. Beneath: Denon AVR-X3800H, `Stereo • Dolby Atmos`,
  Volume `35%`.
- **CLIMATE** — dial `22.4 °C` Comfortable, +/−; Mode `Cool`, Fan Speed `Auto`,
  Humidity `51%`; range buttons `− 22.0°` / `+ 24.0°`; footer link
  "Good Air Quality • AQI 23".
- **CLOCK / TIMER** — `05:42 PM` `12/09/26`; Lights Auto Off `11:30 PM` Daily;
  Ambient Strip Off `00:30 AM` Daily; TV Sleep Timer `01:15 AM` Once;
  `+ Add Timer`.
- **SENSORS / STATUS** — Motion `No motion`, Temperature `22.4 °C`,
  Humidity `51%`, Air Quality `Good (AQI 23)`, Sound Level `42 dB` Quiet.

Footer nav row above the status bar: `Back` · `Home` · `View All Rooms`.

### 5. Dining

Header: `Back to Home`, cutlery icon, **DINING**, "Monitor and control your
Dining Room". Right chips: `21.9 °C` Comfortable · Lights `All Off` ·
Motion `No Motion` · Status `Ready`. Plus `People Home` / `Internet Online`.

Hero: dining-room photo, **"A space for gathering, sharing and making
memories."**, `Room Settings`.

- **QUICK ACTIONS** — All Off "Turn everything off" · Dinner "Set the mood" ·
  Bright "Full brightness" · Clean "Prep for cleaning".
- **LIGHTS** (`All Off`) — Dining Ceiling, Pendant Light, Wall Sconces,
  Sideboard LED — all `Off`; `View all lights`.
- **POWER OUTLETS** — Sideboard Outlet, Dining Table Outlet, Corner Outlet —
  all off; `View all outlets`.
- **ENTERTAINMENT** — Dining Speaker `• Idle`, "No music playing", transport,
  volume; `View all devices`.
- **CLIMATE** — dial `21.9 °C` Comfortable, `12/09/26`, "Set to 22.0 °C";
  mode buttons `Cool` (selected) · Heat · Auto · Fan; `Climate Settings`.
- **CLOCK / TIMER** (`+ Add`) — Dinner Timer `45:00` "Dinner at 6:30 PM" with a
  play button; Cleanup Reminder `9:00 PM` Daily, toggle on; `View all timers`.
- **SENSORS / STATUS** — full-width strip of six: Temperature `21.9 °C`
  Comfortable · Humidity `52%` Good · Motion `No Motion` Last 5:20 PM ·
  Door/Window `Closed` All secure · Air Quality `Good` AQI 24 ·
  Sound Level `38 dB` Quiet.

### 6. Ray Bedroom

Header: `Back`, breadcrumb `Home › Rooms › Ray Bedroom`, **RAY BEDROOM**,
`Home` button top right.

Status chips: `21.5°C` Comfortable · `No motion` Currently · `All lights off`
Lights · `Climate off` HVAC · `Calm` Room status.

Hero: bedroom photo, eyebrow `RAY BEDROOM`, **"Your personal retreat"**,
"Everything is just the way you like it.", `Room Settings`.

- **QUICK ACTIONS** — 2×2: All Off · Focus · Sleep · Night.
- **LIGHTS** (`All Off`) — Ceiling Light, Bedside Left, Bedside Right, LED Strip
  — all `Off`; `View all lights`.
- **POWER OUTLETS** — Left Nightstand, Right Nightstand, TV Outlet, Smart Plug —
  all `Off`; `View all outlets`.
- **ENTERTAINMENT** — Bedroom TV `Off`, power button; transport row;
  Volume slider; Source `HDMI 1`.
- **CLIMATE** — dial `21.5 °C`, `12/09/26`, "Climate off"; mode list
  `Off` (selected) · Cool · Heat · Auto; `Schedule` and `Settings` buttons.
- **CLOCK / TIMER** — Bedroom Alarm `7:00 AM` toggle on; Sleep Timer `Off`;
  Wake Up Light `Off`; `Add timer`.
- **SENSORS / STATUS** — Motion `No motion`, Temperature `21.5 °C`,
  Humidity `51%`; `View history`.
- **ROOM STATUS** — large blue ring with a leaf icon: **Calm**,
  "Everything looks good."

### 7. Bathroom

Header: `Back`, breadcrumb `Home › Rooms › Bathroom`, **BATHROOM**.
Right pills: `Home`, `People Home`, `Internet Online`.

Status chips: `22.0°C` Temperature · `No motion` Occupancy · `All lights off`
Lighting · `Fan off` Ventilation · `Dry / Normal` Humidity Status.

Hero: bathroom photo on the left half, text on the right —
**"Your bathroom is calm and comfortable."** / "Everything is in perfect
balance." / `Room Settings`.

- **QUICK ACTIONS** — All Off · Shower · Bright · Night.
- **LIGHTS** (`Edit`) — Vanity Light, Mirror Light, Shower Light, Ceiling Light
  — all `Off`.
- **POWER OUTLETS** (`Edit`) — Vanity Outlet, Heater Outlet, Toothbrush Charger
  — all `Off`.
- **VENTILATION / FAN** — arc gauge, `Fan off`, `0%` Speed; segmented control
  `Off` (selected) · Low · Medium · High.
- **CLIMATE / THERMOSTAT** — `22.0 °C` Comfortable; Mode dropdown `Auto`;
  dial "Set to `22.0 °C`" with `−` / `+`; caption "Heating idle".
- **CLOCK / TIMER** — `5:42 PM` `12/09/26` with a `Start` button;
  Shower Timer `00:00:00` `Set`; Fan Timer `Off` `Set`;
  Night Light Timer `Off` `Set`.
- **SENSORS / STATUS** — three tiles each with a green tick: Motion
  `No motion` · Temperature `22.0°C` Comfortable · Humidity `51%` Dry / Normal.

### 8. Kitchen

Header: `Back`, **KITCHEN** with an edit pencil, breadcrumb
`CasaRay Home › Kitchen`, `Home` button.

Status chips: `21.8 °C` Comfortable · `No motion` Motion Sensor ·
`1 Light On` Ceiling Spots · `Rangehood Off` Kitchen · `Normal` All Systems.

Hero: kitchen photo, **KITCHEN** / "Everything is running **smoothly**."
(the last word in green).

- **QUICK ACTIONS** — All Off · Cooking · Clean Up · Night.
- **LIGHTS** — Ceiling Spots `10n` on (blue toggle); Under Cabinet `Off`;
  Island Pendants `Off`; Pantry Light `Off`; `View all lights`.
- **POWER OUTLETS** — Bench Outlets `On`, Island Outlet `Off`,
  Appliance Outlet `On`, Fridge Outlet `On` (green toggles); `View all outlets`.
- **ENTERTAINMENT** — CasaRay Radio, "Lounge Vibes", album tile, transport with
  pause, volume `40%`.
- **CLIMATE** — arc `21.8 °C` Comfortable; Mode `Cool`, Fan `Auto`;
  `−` `21.5 °C` `+`; `View climate settings`.
- **CLOCK / TIMER** — `5:42 PM` `12/09/26`; Kitchen Timer `00:00` play;
  Boil Kettle `00:00` play; `Add New Timer`; `View all timers`.
- **APPLIANCES / STATUS** — Dishwasher `Off`, Rangehood `Off`,
  Kettle (Outlet) `Off`, Oven (Outlet) `Off`; `View appliance settings`.
- **SENSORS / STATUS** — Motion `No motion`, Temperature `21.8 °C`,
  Humidity `51%`, all with green ticks; `View sensor details`.

### 9. Parents Room

Header: `Back`, **PARENTS ROOM**, `Home` button.

Status chips: **Occupied** `2 people in room` (green) · `23.1°C` Room
Temperature · `2 Lights On` Living Room, Bedside · `Climate On` Set to 22°C ·
**Comfortable** All conditions good (green).

Hero: bedroom photo, **PARENTS ROOM** / "Your private sanctuary for rest and
relaxation."

- **QUICK ACTIONS** — 2×2: All Off · Relax · Sleep · Reading;
  `Customise scenes`.
- **LIGHTS** — Ceiling Light (Bedroom) on · Bedside Left (Left Nightstand) on ·
  Bedside Right (Right Nightstand) on · Accent Light (Wall Light) off;
  `View all lights`.
- **POWER OUTLETS** — Left Nightstand `Always On` (green) · Right Nightstand
  `Always On` (green) · Dresser Outlet `Off` · Floor Lamp `Off`;
  `View all outlets`.
- **ENTERTAINMENT** — TV, Samsung QLED, "Living Room TV", `• On`;
  buttons Power · Mute · Source · Volume `− 22 +`; row: Netflix `HDMI 1`;
  `More media controls`.
- **CLIMATE / THERMOSTAT** (gear icon) — dial `23.1 °C` "Feels like 23°C",
  `Cooling`; Set Temperature `22.0 °C` with up/down; mode buttons `Cool`
  (selected) · Fan · Auto; footer "Climate is ON" and "Good air quality".
- **CLOCK / TIMER** — `5:42 PM` `12/09/26`; Sleep Timer "Turns off TV" `1:00`
  Remaining with pause; Wake Up Light "Weekdays" `6:30 AM` Tomorrow, toggle on;
  `Add new timer`.
- **SENSORS / STATUS** — Motion `No motion detected`, Temperature `23.1°C`
  Comfortable, Humidity `51%` Good; `View all sensors`.

### 10. Garage

Header: `Back to Home`, **GARAGE**. Status chips right: `20.8°C` Comfortable ·
Garage Door `Closed` · Camera `Online` · Freezer `Monitored` ·
Utility Status `Normal`.

Hero: garage photo (wide, left ~3/4) with **QUICK ACTIONS** as a 2×2 card
occupying the right quarter: Open Door · All Off · Utility · Night.

- **LIGHTS** — Ceiling Lights `100%` on · Wall Lights `60%` on ·
  Workbench Light `80%` on · Exterior Light `Off`; `View all lights`.
- **POWER OUTLETS** — Garage Outlets `On` · Workbench Outlet `On` ·
  Freezer Outlet `On` · EV Charger `Off`; `View all outlets`.
- **GARAGE DOOR & SECURITY** — Garage Door **Closed** with a door graphic;
  `↑ Open` / `↓ Close` buttons; Auto Close toggle on; Door Lock `Locked`.
- **CAMERA** (`Live`) — Garage Front still with a play overlay, `HD` badge;
  `View all cameras`.
- **CLIMATE & UTILITY** — Temperature `20.8°C` Comfortable with arc,
  "Set to 21°", `−` / `+`; Ventilation `Normal`; Utility Status `Normal`.
- **CLOCK / TIMER** — Clock `5:42 PM` `12/09/26`; Timers: Auto Door Close
  `10:30 PM`, Utility Off `1:00 AM`, Workbench Light Off `11:00 PM`;
  `Manage timers`.
- **SENSORS & STATUS** — six tiles: Motion `No Motion` 2m ago ·
  Door `Closed` 2m ago · Temperature `20.8°C` 2m ago · Power Usage `1.24 kW`
  Live · Freezer `-18.2°C` Normal · Humidity `48%` Normal.

### 11. Bills

Header: **BILLS**, "Track household expenses, due dates, and savings."
Right: amber pill `2 bills need attention`, pill `Auto Pay Active`, clock.

KPI strip: Total Due This Month `$482.15` (Across 6 bills) · Next Due Date
`14 Sep` (Internet) · Paid This Month `$289.53` (5 bills paid) ·
Savings Tracked `$73.40` (This period).

- **BILLING OVERVIEW** (`This Year` dropdown) — Total Due This Month
  `$482.15`; legend rows Paid This Month `$289.53`, Upcoming (Next 30 Days)
  `$635.45`, Savings This Period `$73.40`; Monthly Spending Trend line chart,
  `$0–$800`, Mar → Sep with the current point marked.
- **ALL BILLS** — table with columns Bill · Provider · Amount · Due Date ·
  Period · Status · Actions:

  | Bill | Provider | Amount | Due | Period | Status |
  |---|---|---|---|---|---|
  | Electricity | EnergyAustralia | $142.62 | 18 Sep — in 6 days | 30 Jul — 29 Aug | Due Soon |
  | Gas | EnergyAustralia | $88.41 | 20 Sep — in 8 days | 30 Jul — 29 Aug | Unpaid |
  | Water | South East Water | $76.30 | 25 Sep — in 13 days | 1 Jun — 31 Aug | Upcoming |
  | Council Rates | Local Council | $132.50 | 30 Sep — in 18 days | 1 Jul — 30 Sep | Upcoming |
  | Internet | More NBN 500/45 | $75.00 | 14 Sep — in 2 days | 14 Aug — 13 Sep | Auto Pay |
  | Insurance | AAMI / Vehicle | $214.00 | 2 Oct — in 20 days | 2 Oct — 1 Oct 2026 | Scheduled |

  Row actions: view · mark paid · schedule · more. Footer: `+ Add Bill`.
- **RECENT PAYMENTS** (`View all`) — Electricity `$142.62` Paid 2 Sep ·
  Internet `$75.00` Paid 1 Sep · Water `$76.30` Paid 29 Aug ·
  Insurance `$214.00` Paid 28 Aug.
- **SAVINGS TRACKER** (`View all`) — Electricity discount `22% off plan`
  `$22.10` · Internet plan saving `Promo discount` `$30.00` · Insurance saving
  `Multi-policy` `$21.30`; Total Savings This Period `$73.40`.
- **MONTHLY SPENDING BREAKDOWN** — donut, Total `$725.33` This Month;
  Electricity `$142.62` 19.2% · Gas `$88.41` 12.2% · Water `$76.30` 10.5% ·
  Internet `$75.00` 10.3% · Insurance `$214.00` 29.5% · Rates `$132.50` 18.3%.
- **UPCOMING BILLS** (`View all`) — dated list 14 Sep → 2 Oct with amounts,
  due-in captions colour-coded by urgency.

Footer bill cluster on this screen reads `Next Bill Due` / Internet — 14 Sep /
`$75.00` / in 2 days.

### 12. Contact sheet — nine further screens

A 3×3 contact sheet of additional screens, rendered smaller. Each keeps the
sidebar, header and card grid conventions above.

- **BILLS & EXPENSES** (compact variant) — `Calendar View`, `+ Add Bill`;
  KPIs Total Due `$284.45`, Due Soon `$142.62` in 5 days, Paid This Period
  `$416.03`, Projected Savings `$35.40` vs last period. Upcoming Bills list
  (EnergyAustralia / Origin Energy / South East Water with overdue flags in red)
  and a Bills Overview donut `$700.76` Total split Electricity 41% · Gas 18% ·
  Water 15% · Internet 13% · Rates 13%.
- **AUTOMATIONS** — "Manage your smart rules"; `Create Automation`, `Templates`;
  filter tabs All · Security · Lights · Audio · Climate · Scenes · Scripts;
  rule rows with description and enable toggle (Door → Dining Light ·
  Work Prep Routine · Good Morning · Away Mode · Good Night, the last off);
  **Automation Activity** bar histogram (Today) and **Most Active** list with
  run counts; **Quick Scene Shortcuts** — All Off · Good Night · Party · Away.
- **PEOPLE & PRESENCE** — "Who is home and where"; `Map View`; four person
  cards (Ray `Home` Living Room 5 min ago · Parent 1 `Home` Fitness Room 2 min ·
  Parent 2 `Home` Patio 2 min · AI Q `Away` last seen 2:15 PM);
  **Home Summary** `3` At Home / `0` Away / `1` Zone Active;
  **Zones** Home 3 · Work 0 · School 0 · Shopping 0;
  **Presence History** multi-series line (At Home / Away / Zone Active).
- **LIGHTING STUDIO** — "Design your perfect lighting"; `Presets` / `Editor`;
  **Zones** list All Off · Relax · Bright · Movie Time (selected, purple) ·
  Dinner · Party · Good Night; a live room render showing the current scene;
  **Scene Controls** sliders Ceiling Lights `20%` · LED Strip `65%` ·
  Corner Lamp `20%` · TV Backlight `70%`.
- **MEDIA HUB** — "All your entertainment in one place"; `Devices`;
  **Now Playing** Avengers: Endgame, `2019 • 3h 1m • PG-13`, scrubber
  `1:26:30 / 3:01:06`, transport; device list Netflix `TV` Continue (active) ·
  Parasite `TV` Play · Ray Bedroom TV Chromecast Off · Kitchen Display Spotify
  Off; **Continue Watching** four posters with S/E and remaining time.
- **NETWORK & DEVICES** — "Your network at a glance"; `Speed Test`;
  KPIs Internet Status `Online` · Download `462 Mbps` · Upload `48 Mbps` ·
  Uptime `1d 9h`; **Network Map** tree — Internet → Main Router / Mesh
  Accelerator / Switch (Port 1, Online) → Work Devices `32` / Wear Devices `8` /
  IoT Devices `48`; **Device Health** ring `96% Online` with Online `92`,
  Offline `3`, Unknown `1`; **Top Clients** Ray's iPhone · Living Room TV ·
  AI Q iPad Pro, each `5 GHz` with signal bars.
- **HOUSE HEALTH** — "System health and maintenance"; `Run Diagnostics`;
  **Overall Health** green tick **Excellent** "Everything is working perfectly";
  **System Status** Home Assistant · Zigbee Network · Wi-Fi Network ·
  Thread Network · Solar Inverter · Power Monitoring — all `Online`;
  **Device Uptime** bars Front Door Sensor `99%` · Backyard Sensor `98%` ·
  Pool Pump Main Button `97%` · Kids Bedroom Display `96%` ·
  Garage Door Sensor `95%`; **Recent Issues** (Garage camera offline —
  Resolved · Trainee device rebooted · Pool pump — Resolved);
  **Updates** Home Assistant Core `2025.9` Up to date · Zigbee2MQTT `2.1.0`
  Up to date.
- **WATER & GAS** — "Usage and monitoring"; **Water Today** `142 L` with a blue
  bar histogram, Daily Average `156L`; **Gas Today** `8.6 MJ` orange histogram,
  Daily Average `9.4 MJ`; **Water This Month** `4.3 kL` Total Usage with trend,
  "No leaks detected — All good"; **Gas This Month** `112 MJ` Total Usage
  `-3.2%` vs last month.
- **NOTIFICATIONS & ALERTS** — "Stay informed"; `Mark all read`, settings gear;
  tabs All · Critical · Warnings · Information; feed — Backyard door open 2m
  `Critical` · Garage camera offline 15m `Warning` · Freezer temperature high
  27m `Warning` · Washing machine finished 45m `Info` · Solar production
  milestone `Info`; **Alert Settings** Critical Alerts "Instant, push" ·
  Warnings & Info "Push" · Info Alerts "Enabled", all on;
  **Quiet Hours** `10:00 PM – 7:00 AM` with `Edit`; `Alert History — View all`.

---

## Mapping to the live dashboard

<a id="mapping-to-the-live-dashboard"></a>

`dashboards/deez_smart_home.yaml` already carries views for most of these
screens. The mockups are the design target for those views; they are not a
statement that the entities behind them exist.

| Mockup screen | View `path:` in the YAML |
|---|---|
| Home | `home` |
| People Mapping / People & Presence | `people-locations`, `people-locations-distance` |
| Cameras | `cameras` + the six per-camera views |
| Living Room | `living-room` |
| Dining | `dining` |
| Ray Bedroom | `ray-bedroom` |
| Bathroom | *(no view — Home lists a Bathroom room card)* |
| Kitchen | `kitchen` |
| Parents Room | `parents-room` |
| Garage | `garage` |
| Bills | `bills` + the six per-bill views |
| Automations | *(no view)* |
| Lighting Studio | `lighting-studio`, `lighting-modes`, `lights` |
| Media Hub | `media` |
| Network & Devices | `network` |
| House Health | `status` ("Smart Home Status") |
| Water & Gas | *(no view — `energy` covers electricity only)* |
| Notifications & Alerts | *(no view — the Home "Active Now" strip is the nearest)* |

Views in the YAML with no counterpart in the mockups: `guest-room`, `security`,
`climate`, `settings`, `ipad-command-center`, and the per-light detail views.
The iPad Command Center in particular is a bespoke kiosk layout that the CasaRay
mockups do not describe — it is not covered by this reference.

**Gaps are not a work order.** Nothing above authorises creating the missing
views. They are recorded so the difference between the reference and the live
dashboard is visible.

## Known inconsistencies

<a id="known-inconsistencies"></a>

The mockups disagree with each other in a few places. Where a change has to pick
one, prefer the value that appears in the majority of screens, and note the
choice in the commit message.

1. **Assist card label.** Eleven screens read **"CasaRay Assist / Tap to
   speak"**; the contact-sheet screens read **"CasaRay Aura / Top Speed"**.
   Treat *CasaRay Assist / Tap to speak* as correct.
2. **Next Bill due-in.** The footer reads "Due in 6 days" on most screens,
   "Due in 16 days" on Ray Bedroom, and on the Bills screen it changes shape
   entirely to "Next Bill Due / Internet — 14 Sep / $75.00 / in 2 days".
   The Bills screen form is the detailed one; the rest is placeholder drift.
3. **Presence count.** People Mapping shows 2 at home of 4 tracked; People &
   Presence shows 3 at home, 0 away, AI Q away. Both are illustrative states of
   the same household, not two designs.
4. **Kitchen lights.** The Ceiling Spots row reads `10n` — a rendering artefact
   of `On`, not a real value.
5. **Nav ordering.** The sidebar is stable across the full-size screens. The
   contact sheet shows a longer nav including Lighting Studio, Network,
   Notifications and House Health, and renders "Bills" as "Bilbee" in two
   panels. The full-size sidebar is the reference.
6. **Time is frozen** at `5:42 PM`, `12/09/26` in every screen, and the weather
   strip is identical throughout. These are mock values, not design constants —
   only the *layout* of the clock and weather strip is normative.

## How to use this reference

<a id="how-to-use-this-reference"></a>

- This file describes **intent**. It does not override the safety rules in
  `README.md` and `MAINTENANCE.md` — in particular, never introduce an
  `entity_id` that has not been confirmed against the live instance just because
  a mockup implies the data exists.
- A mockup showing a metric is not evidence that a sensor for it exists. Check
  first; if it does not, the card is not built.
- Keep changes small and reversible, as the existing guidance requires. A
  redesign toward this reference is a series of reviewable commits, not one
  sweep.
- If a change deliberately departs from this reference, say so in the commit
  message and, if the departure is permanent, amend this file in the same
  commit.
