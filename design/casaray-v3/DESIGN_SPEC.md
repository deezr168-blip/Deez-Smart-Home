# CasaRay V3 — visual design specification

V3 is a refinement of V2, not a rebrand. The 14/09 mockups are still the
visual target, and every rule in `CLAUDE.md` still applies. V3 sets out how
those rules turn into one consistent set of parts, and adds what V2 lacks:
a light theme, a phone layout, a desktop layout and rules for narrow cards.

Screenshots referenced below are in `screenshots/`.

## 1. Principles

1. **Glanceable from across the room.** The wall iPad is read from about three
   metres. The chip strip and Needs attention answer "is anything wrong?"
   before the viewer reaches the first card.
2. **Honest before reassuring.** Every summary has a third branch. The
   outage scenario (`10_wall_home_outage.png`) is part of the spec: it is what
   the page must look like when devices stop answering.
3. **One accent, one meaning.** Amber is "on or active" and nothing else.
   Status colours are never decoration.
4. **Native-portable.** Every part below maps to a native Home Assistant card
   or tile feature (`FEATURE_INVENTORY.md` §3). The prototype is HTML so it
   can be reviewed. It is not a new runtime.

## 2. Colour tokens

Dark is the wall panel's theme. Its values are V2's `--casaray-*` tokens,
sampled from the 14/09 renders and carried over unchanged. Light is new.

| Token | Dark | Light | Use |
|---|---|---|---|
| `--page` | `#0d1114` | `#eef1f4` | Page base |
| `--page-top` | `#0f1418` | `#f5f7f9` | Top edge, sheets, top bar |
| `--surface-1` | glass 4.5% | white 45% | Rail, quiet bands |
| `--surface-2` | glass 6.5% | white 72% | Ordinary card |
| `--surface-3` | glass 10% | white 92% | Icon discs, controls |
| `--border` | `rgba(160,190,220,.14)` | `rgba(28,48,72,.10)` | Card edge |
| `--text` | `#eef2f7` | `#141a20` | Names, values |
| `--text-2` | `#9aa7b8` | `#4d5967` | Secondary lines |
| `--text-muted` | `#6f7b8c` | `#7a8594` | Footnotes, captions |
| `--amber` | `#e8a33d` | `#b36a08` | On / active / selected |
| `--red` | `#e06a6a` | `#b83a38` | Fault, needs attention |
| `--green` | `#5fd39a` | `#1f8057` | Healthy, closed, connected, live |
| `--grey` | `#969ca6` | `#7d8591` | Unavailable, offline, no data |

"Glass" is `rgb(150,175,205)` at the given alpha. Cards lighten what is
behind them rather than being painted one fixed colour (V2 `DR-014`).

The light amber is darkened to `#b36a08` so amber text keeps readable
contrast on a near-white card. Each semantic colour also has a `-bg` tint and
a `-border` for alert cards and active outlines.

**Background:** four stacked gradients (vignette, a soft blue bloom above the
viewport, a vertical lift, the base colour), as V2's `CasaRay` theme.

## 3. Type

| Role | Face | Size / weight |
|---|---|---|
| Page title | Manrope | 24 / 700 (21 on phone) |
| Section heading | Manrope | 16.5 / 700, sentence case, dim 17px icon before |
| Card name | Manrope | 15.5 / 700 |
| Secondary line | Manrope | 13.5 / 400, `--text-2` |
| Chip | Manrope | 14; label `--text-2`, value 700 |
| Big number | Manrope | 16% of card width, 20–34px / 600 |
| Clock | Manrope | 22 / 600 time over 12.5 date |
| Chinese | Noto Sans SC → PingFang SC | Same scale |
| Entity captions | JetBrains Mono | 10.5 |

All digits are tabular. **Build note:** Home Assistant renders in the iPad's
system font unless the theme sets `primary-font-family` and loads the face as
a dashboard resource. Manrope is a proposal. The phone layout was also
checked with fonts unavailable, so it holds in the fallback face too.

## 4. Layout

### Shell

| | Phone < 700px | Portrait tablet 700–1023px | Wall iPad 1024–1439px | Desktop ≥ 1440px |
|---|---|---|---|---|
| Navigation | Bottom tab bar: Home · Rooms · Security · Energy · More | Icon rail, 72px | Icon + label rail, 92px | Icon + label rail |
| Body columns | 1 | 2 | **2** | 2, Home 3 |
| Side gutter | 16px | 24px | 24px | 32px |
| Top bar | Solid, wraps to two rows | Sticky, gradient fade | Sticky, gradient fade | Sticky |

**Two columns on the wall iPad is a measured constraint, not a style
choice.** V2 set Home to three columns, and the live wall iPad resolved two
(`DR-013`). V3 designs for two there. The desktop's third column exists only
at 1440px and above, where there is room for it.

**Navigation stays in the page.** `kiosk_mode` hides HA's sidebar and header,
so the rail, the tab bar and Home's More boards grid are the only way around.

### Home bands (wall iPad)

| Band | Layout |
|---|---|
| Top bar | Title · Demo data pill · Language · Theme · Demo controls · Clock |
| Chip strip | Outside · Inside · Home · Monitored |
| Needs attention | Full width, alert cards two across |
| Right now \| Who's home | Weather + solar \| three people + Parents' room occupancy |
| One tap | Full width, four across |
| Rooms \| Shopping list + Security | Six room rows \| list + security summary |
| Energy now \| Recent activity | Monitored load + sparkline + grid import \| last six changes |
| More boards | Full width, three across |

On desktop the board flows three across with `grid-auto-flow: dense`, so
Rooms fills the space beside Right now and Who's home.

### Room pages

Sections in this order, each only when the room has something for it:
Lights · Air & climate · Sensors · Fridge · Media · Power · Pet feeder ·
Scenes (full width). **If the count of half-width sections is odd, the last
one widens to full width**, so no room page leaves half a row empty. This is
V2's gate check 15, applied automatically.

## 5. Components

| Component | Anatomy | States |
|---|---|---|
| **Tile** | 42px icon disc · name · secondary line · optional pill · optional feature | rest (grey disc) · **on** (amber disc, amber border) · **green** (secure) · **red** (fault) · **no data** (dashed grey card, `NO DATA` / `OFFLINE` pill, keeps its place) |
| **Feature bar** | 38px rounded track, amber fill with a 2px amber leading edge, label left, value right. The whole bar is the drag target. | Brightness, volume, blind position |
| **Segment** | 4px inset track, 32px buttons, selected = amber tint + inset border | Purifier speed, AC mode, scenario, theme |
| **Alert card** | Red / amber / grey tinted tile with a chevron. The whole card links to its board. | Colour follows what the condition *means*: a flat battery is red, a door left open is amber, an unreachable inverter is grey |
| **Room row** | Icon · name · meta line (amber for active facts) · chevron | Dark room: dashed, grey icon |
| **Chip** | Pill · dim icon · dim label · bold value | `na` (muted value) · `warn` (amber) · `bad` (red) |
| **Camera tile** | 16:10 frame · name · `● LIVE` in green | Offline: becomes a no-data tile saying "No stream and no battery reading" |
| **Footnote** | 13px muted text under the section it qualifies, max 70 characters wide | Used for every honesty caveat |

### Narrow-card rule (new in V3)

A card measures its own width with a container query, not the viewport:

- **≤ 300px:** the status pill drops under the name instead of taking a column.
- **≤ 220px:** the icon moves above the text, so the name gets the full width.

This fixes a failure the first render hit on the phone: two-up One tap tiles
squeezed "Goodnight" into a column one letter wide. The test harness now fails
on any card name that is under 64px wide *and* wrapping.

## 6. Bilingual

Driven by `input_boolean.chinese_dashboard`, exactly as V2. The toggle writes
the helper, and the page reads the helper.

- Simplified Chinese, using V2's existing vocabulary: 首页, 安防, 需要注意,
  此刻, 谁在家, 一键, 购物清单, 近期活动, 无数据, 离线, Ray 卧室.
- Clock date `DD/MM/YY` in both languages. Time is `8:14 pm` in English and
  `20:14` in Chinese.
- Chinese enumerations join with `、`. English joins with ` · `.
- Device and brand names stay Latin: CasaRay, Hue, Fronius Primo, eero,
  Powerpal, Pogo.
- Entity IDs, paths and YAML keys are never translated.
- The `lang` attribute switches to `zh-Hans`, so the Chinese font stack takes
  over.

## 7. Motion and interaction

- Cards scale to 98.5% on press, and borders brighten on hover. There is no
  other motion. `prefers-reduced-motion` removes transitions.
- Every control shows a 2px focus ring. Escape closes sheets.
- A demo action shows a toast: "Demo: … No device was contacted."

## 8. Moving this into Home Assistant

1. Add a light `CasaRay` theme variant from §2. The dark tokens already exist.
2. Rebuild views in `casaray_v2.yaml` (or a new `casaray_v3.yaml` on this
   branch) using the native cards in `FEATURE_INVENTORY.md` §3. `card_mod`
   stays limited to V2's four allowed uses.
3. The narrow-card rule has no native equivalent. In HA it becomes a choice
   per card: `grid_options.columns` must keep a two-up tile at 6 columns or
   more, and text-bearing cards at 3 or more (`DR-012`).
4. Wire the four One tap scripts only after the owner approves what each one
   switches (`CR-233`).
5. Re-check availability against the live instance before building, not the
   export (`ENTITY_MAPPING.md` §4).
