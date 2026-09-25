# Home concepts A–D — side-by-side comparison

For the owner's review (`DECISIONS.md` V3-004, V3-006). **This document does
not choose a concept.** V3-005 stays open for the owner's selection.

## How the comparison was made

- **Same frame:** every concept captured at **1180 × 820** (the wall iPad,
  landscape), device scale 2, dark, English and Chinese.
- **Same data:** the snapshot A–C are drawn on (`concepts/README.md`),
  Thursday 25/09/26 16:20: 17° and partly cloudy, Ray and Ai home, Vinh
  away, solar 1.62 kW (14.2 kWh today), grid import 0.38 kW (6.1 kWh), no
  export source, living room 21.4°, dining 20.8°, parents' air-con off at
  23.2°, front-door battery 12%, electricity unpaid, cameras 3 online,
  2 offline and 1 unknown, doors with no data, purifier on.
- **A, B, C** are rendered from `concepts/Concept{A,B,C}.dc.html`
  **unmodified** (SHA-256 checked before and after), using the design
  canvas's own runtime.
- **D** is `prototype/index.html` in its **Concept review** scenario, a
  data patch carrying the same snapshot, with the clock fixed at 16:20. The
  prototype itself was not rebuilt.
- Regenerate with `tools/capture_comparison.cjs` (see its header). Output:
  `screenshots/cmp_*.png`.

### Where the same data still reads differently in D

These differences come from each concept's rules, not from different data.
They are part of what is being compared:

| On the snapshot | A, B, C | D |
|---|---|---|
| Electricity bill unpaid | Listed in Needs attention | Not an alert: D raises only *overdue* bills. It shows on the Bills board. |
| 2 cameras offline | Listed in Needs attention | Not an alert: D counts cameras in the Security summary, which is below the fold on Home |
| North wall camera `unknown` | Drawn as *unknown*, separate from offline (A, B, C) | Folded into *no data*. D has no separate unknown state. |
| Emergency buttons | Not shown | Shown as a red alert. D's data carries the export's finding that both `event.*_emergency_button_*` entities are unavailable. |
| One tap | Three existing room scenes, plus purifier (and AC in A/B) | Four *proposed* whole-home scripts, which do not exist yet (`CR-233`) |
| Time | 24-hour `16:20` | `4:20 pm` in English, `16:20` in Chinese |

## At a glance

| | **A — Minimal architectural** | **B — Modern dark control centre** | **C — Balanced family dashboard** | **D — V2 continuation (prototype)** |
|---|---|---|---|---|
| Idea | Type and whitespace. Hairline rules instead of cards. | Dense instrument panel. Power flow, camera matrix. | Plain words, big targets, people first | V2's glass cards and bands, extended to a whole dashboard |
| Fits 1180 × 820 without scrolling | **Yes** | **Yes** | **Yes** | **No:** 2.6 screens (2,097 px). First screen shows attention, weather, people and One tap. |
| What exists | One Home artboard | One Home artboard | One Home artboard | Full prototype: 10 boards, 8 room pages, 4 scenarios |
| Themes | Dark | Dark | Dark | Dark + light + auto |
| Phone / desktop | Not drawn | Not drawn | Not drawn | Phone (tab bar), portrait tablet, desktop (3 columns) |
| Palette | Own: `#0e0f10` page, gold `#c9a86a` accent | Own: `#07090c` page, **teal** `#4fc4bd` accent + amber | Own: `#111315` page, warm amber `#e9b872` | **V2's sampled tokens** (`#0d1114`, amber `#e8a33d`) + a new light set |
| Type families | 2 (Archivo, Noto Sans SC) | 3 (Space Grotesk, JetBrains Mono, Noto Sans SC) | 2 (Plus Jakarta Sans, Noto Sans SC) | 3 (Manrope, Noto Sans SC, JetBrains Mono for entity captions) |
| Icons | Stroke, hand-drawn set | Stroke, same set | Stroke, same set | Filled Material Design Icons (the set HA itself uses) |
| Automated checks | None | None | None | 68 (navigation, overflow, interaction, honesty, bilingual) |

## By the criteria asked for

### Navigation

| | A | B | C | D |
|---|---|---|---|---|
| Form | Left text rail, 216 px, labels | Left icon rail, 48 px buttons, **no labels** | **Bottom** bar, labels | Left rail, 92 px, icon + label. Phone: bottom tab bar + More sheet. |
| Destinations | The workspace's 10 (Home … Bills) | The workspace's 10 | The workspace's 10 | 10, but a different set: Media and People in place of Network and Alerts. Security in place of "Cameras & security", Lighting in place of "Lighting studio". |
| Works in the artboard | Not wired (single screen) | Not wired | Not wired | Wired: every board and room, back, browser back, deep links |
| Language switch | In rail, `EN / 中文` | Rail foot, `中文` | Top right, `中文` | Top bar, `中文`. Also in the demo panel. |

### Home layout (first screen)

| | A | B | C | D |
|---|---|---|---|---|
| Hierarchy | Clock → energy strip → attention \| house summary → One tap | Chips → power flow \| attention → cameras \| climate \| people → quick row | Greeting and sentence → people \| energy \| AC → controls \| attention → nav | Chips → attention → weather \| people → One tap → *(scroll)* rooms, shopping, security, energy, activity, boards |
| Headline element | 16:20 at about 150 px | Power-flow diagram | "Good afternoon" + status sentence | Chip strip |
| Density | Low | High | Medium | Medium, but long |

### Room access

| | A | B | C | D |
|---|---|---|---|---|
| From Home | Rooms in nav only | Rooms in nav only (icon) | Rooms in nav only | Rooms in nav **and** six room rows on Home, each with a status line (below the fold) |
| Room pages | Not drawn | Not drawn | Not drawn | 8 built, same section order in each |

### Energy information on Home

| | A | B | C | D |
|---|---|---|---|---|
| Solar now / today | 1.62 kW · 14.2 kWh | 1.62 kW · 14.2 kWh + hourly bars | 1.62 kW "from the sun" | Forecast remaining only on the first screen. Solar now is on the Energy board. |
| Grid import | 0.38 kW · 6.1 kWh | 0.38 kW | 0.38 kW | 0.38 kW (Powerpal), below the fold |
| Export | "No source entity" | "No source entity" | "No source entity" | Not shown |
| Consumption | Not shown | **"Not measured"** | Not shown | "Monitored 147.9 W" chip: a two-circuit subset, footnoted |
| Battery | Not shown | **"Future battery · not installed"** | Not shown | Not shown |

### Security on Home

| | A | B | C | D |
|---|---|---|---|---|
| Cameras | One line: 3 online · 2 offline · 1 unknown | **Six tiles**: online / offline / unknown, each distinct in dot, border and word | One line, plus "doors: no data" | Count inside the Security summary, below the fold. Full board with live frames. |
| Doors | Not shown | Not shown | "no data" | Security summary reads "No data" here, because all three contact sensors are unanswered. With some answering it counts them, e.g. "2 closed · 1 no data". |
| Alerts | Camera outage listed | Camera outage listed | Camera outage listed | Batteries, emergency buttons, overdue bills, back door, inverter |
| Sirens | Not shown | Not shown | Not shown | Security board, display-only |

### Usability

| | A | B | C | D |
|---|---|---|---|---|
| Smallest tap target | 44 px nav | 44–48 px | 52 px; 88–104 px controls | 58 px nav; tiles ≥ 64 px |
| Parents' test (plain words, one action, state in words) | Good: short labels, few controls | Weakest: unlabelled icon nav, mono numerals | **Strongest**: "On — tap to turn off", a big AC button | Good: words on every tile, but more to scan and a long scroll |
| Glance from 3 m | Strong: the clock and four big numbers | Moderate: many small panels | Strong: sentence plus big figures | Moderate: chips are small, and the first screen shows no energy |
| Unknown vs offline kept apart | Yes (in text) | Yes (visually) | Yes (in text) | No |

## Features that can be combined whichever concept is chosen

None of these depends on a visual style:

1. **Energy truth strip** (A, B, C): solar, grid import, *Export: no source
   entity*, *Consumption: not measured*, *Battery: not installed*. It puts
   V3-003 on screen.
2. **Four camera states** (B): online, offline, **unknown**, alert, each
   distinct in dot, border and word. D lacks the unknown state and would
   need it.
3. **Plain-language status sentence** (C), generated from the same checks
   as Needs attention: "Ray and Ai are home, Vinh is out. 3 things need a
   look."
4. **Needs attention that counts what could not answer** (D): "1 check
   could not answer", and never an all-clear while a check is dark.
5. **One tap in two stages** (A–C + D): ship now with existing room scenes
   (`scene.living_room_living_room_bright`, `scene.dining_dining_relax`,
   `scene.bedroom_bedroom_nightlight`). Add whole-home scripts once the
   owner approves them (`CR-233`).
6. **Parents' controls** (C): big, worded, one action. For example "Off ·
   room 23.2°" with a single "Turn on".
7. **House health one-liner** (B): "9 devices not reporting", linking to
   the board.
8. **Room rows with a status line** (D): one tap into any room from Home.
   None of A–C offers this.
9. **Prototype infrastructure** (D): light theme, phone and desktop
   layouts, the narrow-card rule, the outage and review scenarios, the
   entity-ID overlay, the 68-check harness and the entity verifier. It can
   be re-skinned to any concept.
10. **Recent activity** and **shopping list** (D): present in V2, absent
    from A–C. The parity rule in `CLAUDE.md` needs them somewhere.

## Decisions this comparison leaves to the owner

- Which concept, or which mix, becomes V3's visual language (**V3-005**).
- Whether Home must fit one screen (A–C) or may scroll (D).
- Whether the accent stays V2 amber (C, D), moves to gold (A) or adds teal (B).
- Whether navigation labels are required (A, C, D) or icons alone are
  enough (B).
