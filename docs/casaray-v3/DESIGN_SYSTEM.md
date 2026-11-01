# CasaRay V3 — design system

**DEVELOPMENT ONLY — NOT DEPLOYED.** Implements `design/casaray-v3/DESIGN_SPEC.md`
and the owner-confirmed direction (V3-005: Concept D base, C's Home hierarchy;
V3-007: Home is glance + action, air-con is navigation) in native Lovelace.

## Tokens (`src/casaray_v3/themes/casaray_v3.yaml`)

One token set, a value per mode; components read only tokens and the HA
variables mapped from them.

| Token | Dark | Light | Meaning |
|---|---|---|---|
| `v3-page` | `#0d1114` | `#f3f5f8` | page |
| `v3-card` | `#161b1f` | `#ffffff` | card |
| `v3-elevated` | `#1a1f25` | `#eef1f5` | elevated / secondary |
| `v3-text` / `v3-text-2` | `#eef2f7` / `#a9b4c3` | `#141a21` / `#4a5666` | text |
| `v3-accent` | `#e8a33d` | `#9a5b00` | **amber** — active, on, selected |
| `v3-ok` | `#5fd39a` | `#1f7a4f` | **green** — healthy, secure, closed |
| `v3-alert` | `#f07a7a` | `#b42318` | **red** — fault, needs attention |
| `v3-muted` | `#9aa3ae` | `#5f6b7a` | **grey** — unavailable, offline, no data |
| `v3-radius` | 18px | 18px | every card |
| `v3-space-1…4` | 4/8/12/16px | same | 4 px grid |
| `v3-line-height` | 1.55 | 1.55 | room for Khmer |

Dark starts from V2's sampled surfaces. Light is its own palette (amber is
darkened to hold contrast on white). **Every text and state colour clears
WCAG AA (4.5:1) on page, card and elevated in both modes** —
`tests/v3/test_v3.py::Theme`.

Fonts: Inter / system for text; CJK (`Noto Sans HK`, `Noto Sans SC`) and Khmer
(`Noto Sans Khmer`, `Khmer OS`) fallbacks in the same stack.

## Geometry (inherited, gated)

- `max_columns: 2` on every native view (DR-013, measured on the wall iPad).
- Every card declares `grid_options`; nothing below `columns: 2` (DR-012).
- Bands: full-width (`column_span: 2`) or a pair of `column_span: 1` sections.
- Rows of buttons sum to 12 (4 × 3) so they cannot reflow.
- No `badges:` (DR-011). Chip strip = one full-width markdown card.

## Components (`scripts/v3/components.py`)

| Component | Card | Notes |
|---|---|---|
| `topbar` | 2 × markdown + 6 × button | title + dev banner, clock `HH:MM` over `DD/MM/YY`, six-glyph rail; current destination shown named and inert |
| `chips` + `chip_count` / `chip_value` / `chip_cameras` | markdown | `n of m reporting`; "No data" when nothing answered |
| `attention` | markdown | one honest list; all-clear only when every check answered |
| `action_button` | button | one action per button; hold does nothing |
| `nav_button`, `more_boards` | button | named index, 4 across |
| `light_tile` | tile + `light-brightness` feature | |
| `readonly_tile`, `sensor_tile`, `person_tile` | tile | tap / icon-tap / hold cannot act |
| `ac_summary` | markdown | V3-008 R1/R7 wording; read-only |
| `camera_summary`, `camera_card` | markdown, picture-entity | state in words; tap opens the V2 webrtc subview |
| `weather`, `todo`, `scene_buttons`, `note`, `heading` | native | scene labels from the export's friendly names |

## State language

| State | EN | yue | km |
|---|---|---|---|
| no reading | No data | 冇數據 | គ្មានទិន្នន័យ |
| unavailable | Offline | 離線 | ដាច់បណ្ដាញ |
| unknown | State unknown | 狀態未知 | មិនដឹងស្ថានភាព |
| answering camera | Online | 在線 | កំពុងដំណើរការ |

Colour is never the only carrier: every state is also a word.

## Navigation

- Rail on every native view: Home · Lighting · Climate · Cameras · Energy ·
  Security. Every top-level board is reachable from Home in one tap (tested).
- Back: Lovelace has no native history-back action and kiosk mode hides the
  header, so on a top-level view Back is Home. Camera subviews are V2's own.
- Native views keep V2's paths, so every carried link still lands.
