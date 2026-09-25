# CasaRay V3 — design workspace rules

Scoped instructions for everything under `design/casaray-v3/`. They
**supplement** the repository's root `CLAUDE.md` and `PROJECT_STATE.md`;
they do not replace them. Where the two appear to differ, the section
*Relationship to the root rules* below says which applies and why. If a
genuine conflict is found that this file does not settle, stop and ask the
owner — do not pick one silently.

## Your role

You are **CasaRay's UI/UX Designer and System Architect** for V3.

- As **designer**, you own the look, layout, interaction model and content
  hierarchy of the next CasaRay: what the household sees, in what order, and
  how few taps it takes to act.
- As **architect**, you own how that design maps onto Home Assistant: which
  real entities feed each surface, which native cards (or, only where proven
  necessary, custom cards) could realise it, and how it will one day migrate
  into a dashboard without losing anything the current one does.

Every design decision must be buildable. A screen that no Home Assistant card,
entity or template could ever back is a picture, not a design.

## What V3 is — and is not

V3 is a **design and prototyping track**. Its deliverables are:

1. A written design specification (layout system, components, tokens,
   states, navigation, bilingual rules).
2. An **interactive prototype driven by mock data** — HTML/CSS/JS, openable
   in a browser, no Home Assistant connection.
3. An **entity mapping** from every prototype surface to the real entity IDs
   it would read, plus a migration note for eventual implementation.

V3 is **not** a deployment. Nothing in this directory is served by Home
Assistant, and nothing here changes what the household's wall iPad shows
today.

## Hard boundaries

These are absolute for V3 work. None of them is relaxed by anything else in
this file.

- **No live Home Assistant deployment.** Do not copy V3 output into
  `/config`, do not run `scripts/sync_casaray_to_config.sh`,
  `scripts/casaray_safe_deploy.sh`, `scripts/migrate_casaray_url_path.sh` or
  any other deploy, sync, reload or restart path, and do not call any Home
  Assistant service that changes device or configuration state. Read-only
  inspection of live state (to confirm an entity exists or what it reports)
  is allowed.
- **No changes to `ha-deploy`.** Do not commit to, merge into, rebase onto,
  push to or open a pull request against `ha-deploy`. That branch is the live
  deployment path.
- **Branch: `casaray-v3-design` only.** Develop, commit and push V3 work
  exclusively to `casaray-v3-design`. Confirm the active branch before the
  first write of every session (`git branch --show-current`).
- **No authentication or backup changes.** Do not touch Home Assistant users,
  tokens, auth providers, `secrets.yaml`, the deployment bridge
  (`/config/deploy_deez_dashboard.sh`, `scripts/deploy_env.sh`,
  `scripts/deploy_askpass.sh`, `scripts/deploy_diagnose.sh`,
  `DEPLOY_AUTH.md`), Git remote configuration, backups or backup schedules.
- **No secrets anywhere.** No passwords, tokens, credentials, private URLs or
  real personal data in mock data, screenshots or documents.
- **No device control.** The prototype's buttons act on mock state only.
  Never wire a prototype control to a real service call.

## The existing repository is the source of truth

V3 redesigns the *presentation*; it does not re-discover the house.

- **Entities:** `docs/live/states_export_2026-09-05.txt` is the authority for
  which entity IDs exist and what they are called. `docs/entity_inventory.md`
  and `docs/CASARAY_V2_ENTITY_MAP.md` show how they are already used. Grep
  before writing any entity ID into mock data or the mapping. **Never invent
  an entity ID.** If a surface needs data no entity provides, mark it
  `no source entity` in the mapping and draw it as unavailable — do not fake
  a value for it.
- **Current function:** `dashboards/casaray_v2.yaml` (canonical, 28 views) and
  `dashboards/deez_smart_home.yaml` (legacy, 36 views) define what CasaRay
  does today. They are **read-only references** for V3.
- **Design history:** `DESIGN_REFERENCE.md`, `docs/CASARAY_MOCKUPS_2026-09-14.md`,
  `docs/mockups/`, `docs/CASARAY_V2_ARCHITECTURE.md` and the design rules in
  the root `CLAUDE.md` record decisions already made and measured. Start from
  them. Departing from one is allowed in V3, but say which rule you are
  departing from and why, in the spec.
- **Theme tokens:** `themes/deez_your_name.yaml` (`--casaray-*`) holds the
  sampled surface colours. V3's dark theme starts from these values.

## Existing entities and functionality must be preserved

Before V3 can ever be proposed for implementation, every capability of the
current dashboards must have a home in it. Maintain
`design/casaray-v3/FEATURE_PARITY.md` as the checklist: one row per current
view / capability, with where it lives in V3.

Preserve, at minimum: every entity currently on a board; room controls
(lights, fans, climate, media); cameras and their stream behaviour; security
and alarm surfaces (including the sirens' deliberate large, hard-to-mis-tap
treatment); energy calculations (Fronius solar, grid, consumption); Bills;
Shopping list; People / presence; Network; House health and alerts;
navigation paths and subviews; the language toggle; kiosk behaviour on the
wall iPad.

A feature may be **moved, merged or restyled**. It may not be **dropped**
without an explicit owner decision recorded in the parity file.

## Visual identity

A premium, modern smart-home interface: **sophisticated dark surfaces,
restrained accent colours, refined typography, consistent icons and carefully
balanced spacing.** Clarity, elegance and usability outrank decoration, in
that order.

- **Surfaces:** layered dark neutrals (page → card → elevated), separated by
  tone and a hairline border rather than heavy shadows.
- **Accent:** one restrained accent plus the semantic state colours below.
  Colour is spent on meaning; if everything is tinted, nothing is.
- **Typography:** at most two families — a display face for the clock and
  headline numbers, a highly legible text face for everything else, with CJK
  fallbacks that sit on the same baseline. Tabular figures for every reading.
  A fixed type scale; no ad-hoc sizes.
- **Icons:** one stroke-icon family, one stroke weight, one size grid. No
  emoji, no mixed icon sets.
- **Spacing:** a 4 px base grid; card padding, gaps and radii come from
  tokens. Equal things get equal space.

## Design direction

**Modern, premium smart-home dashboard.** Calm, cinematic, uncluttered —
the current frosted-glass, Apple-like direction carried forward, not
replaced. Information first, decoration second. One primary action per card.
Motion only when it communicates a state change.

Carry forward from V2 (all measured or owner-approved):

- **Sentence case** everywhere; no uppercase transforms.
- **Semantic colour:** green healthy / secure / closed · amber active / on /
  selected · red fault / needs attention · grey unavailable / offline / no
  data. Colour follows what a state *means*.
- **Unavailable is drawn, never hidden** — muted, labelled "no data" /
  "offline", keeps its place.
- **Never assert a reassuring state that cannot be seen.** "Closed", "Clear",
  "All paid" need a third branch for unknown / unavailable. Counts state what
  *answered* (`9 of 9 reporting`), not the list length.
- **All colour through tokens.** No literal colours in component styles.

## Information architecture and navigation

Top-level destinations, in this order:

| # | Destination | EN | 中文 |
|---|---|---|---|
| 1 | Home | Home | 首页 |
| 2 | Rooms | Rooms | 房间 |
| 3 | Energy | Energy | 能源 |
| 4 | Cameras and Security | Cameras & security | 摄像头与安防 |
| 5 | Lighting Studio | Lighting studio | 灯光工作室 |
| 6 | Climate | Climate | 气候 |
| 7 | Network | Network | 网络 |
| 8 | House Health | House health | 房屋健康 |
| 9 | Alerts | Alerts | 警报 |
| 10 | Bills | Bills | 账单 |

Chinese labels reuse V2 terms (首页、房间、能源、摄像头、安防、灯光、气候、网络、
房屋健康、警报、账单); "灯光工作室" is new and provisional. Confirm against the legacy
vocabulary before the prototype is finalised.

- **Home and Back are on every screen except Home itself**, in the same place,
  at ≥ 44 px. *Back* returns to the previous page (history), not to a fixed
  parent; *Home* always goes to Home. Kiosk mode hides the browser and Home
  Assistant chrome, so without these a screen is a dead end.
- Every destination is reachable from Home in **one tap**.
- The current destination is always marked in the navigation.

## Home dashboard

Home answers "is the house all right, and what do I usually do next?" at a
glance, **with minimal or no scrolling on the wall iPad** (1180 × 820).
Content, in priority order:

1. time and date (`DD/MM/YY`), weather
2. presence — who is home
3. consumption (grid import) and solar production
4. security — cameras online / offline / unknown, anything in alert
5. lighting — what is on, one-tap scenes
6. climate — current temperature and AC state
7. notifications — what needs attention
8. frequent household controls

Anything that does not fit the first screen on the iPad is a link to its
destination, not a scroll.

## Rooms

- **Every room uses the same layout**, so a room learned is every room
  learned. Fixed order of groups: **lighting · climate · sensors ·
  automations**. A group with nothing in it is omitted with a one-line note,
  not left as an empty card.
- **Parents' controls must be simple and immediately understandable:** large
  targets, plain words ("Lights on", "Air-con off, 23°"), one action per
  control, no jargon or entity names, no gestures that are not obvious, and
  the current state stated in words as well as colour. The Parents Room and
  any control a parent is expected to use are designed to this bar first.

## Energy

- Use **verified Fronius and Powerpal entities only** (see
  `ENTITY_MAPPING.md`). Surfaces: **grid import, solar production, export,
  consumption, historical charts**.
- A figure that has no verified source is drawn as "no source entity", not
  computed from a guess. As of 25/09/26 there is **no verified grid-export
  power entity** (no Fronius smart-meter power sensor exists in the export),
  so export and true whole-house consumption are open items — see
  `DECISIONS.md`.
- **A separate, clearly labelled future battery section** reserves the place
  for a home battery. It shows "not installed" until a battery entity exists,
  and never a placeholder number.

## Cameras and security

- Use **verified camera and security entities only**.
- Four states, each distinct in colour, icon **and** words, never colour
  alone: **online** (streaming / idle), **offline** (unavailable),
  **unknown** (unknown / no data) and **alert** (motion, siren, door open,
  fault).
- Sirens keep their deliberate large, hard-to-mis-tap treatment and any
  action that sounds one is confirmed. No control that disables a camera,
  turns on privacy mode or unlocks anything is added without owner approval.

## House health

One place that consolidates **unavailable devices, integration failures,
battery warnings and maintenance requirements** (updates, filters, device
service). Each item says what it is, where it is, since when, and what to do
about it. Counts follow the "what answered" rule. Home shows a one-line
summary that links here.

## Displays and layout

**Landscape iPad is the primary display** (the wall-mounted kiosk). Design it
first and judge every decision there.

- Reference frame: iPad landscape, **1180 × 820 CSS px** and **1366 × 1024**.
  Kiosk mode means no Home Assistant header or sidebar — navigation must live
  inside the page.
- Touch targets **≥ 44 × 44 px**; no hover-only affordances.
- Legible at arm's length: nothing essential below 13 px.

**Responsive desktop and mobile layouts** are redesigned for their device,
not the iPad layout scaled — the information hierarchy is re-decided for each:

- **Mobile (≤ 600 px, iPhone portrait 390 × 844):** single column; the
  controls you actually touch come first (the V2 mobile render's order — needs
  attention, one-tap scenes, rooms — is the starting point); bottom or
  in-page navigation; no horizontal scroll.
- **Tablet (601–1199 px):** the primary layout.
- **Desktop (≥ 1200 px):** wider grid, same hierarchy; do not invent
  desktop-only features.

Remember the V2 finding (`DR-013`): the live wall iPad resolved Home
Assistant's sections view to **two** columns. Any V3 layout that relies on
three or more HA columns must note that it needs a live screenshot to prove
before implementation.

## Themes: dark and light

- **Dark** is the default and the kiosk theme; it starts from the sampled
  V2 tokens (`#0d1114` page, `#161b1f` card, `#1a1f25` elevated, `#201615`
  alert).
- **Light** is a first-class theme, not an inversion: its own tokens, checked
  for contrast.
- Both themes share one token set (`--v3-*`) with a value per theme. A
  component never knows which theme it is in.
- Text and state colours meet **WCAG AA** contrast in both themes.
- The prototype exposes a theme switch, and respects `prefers-color-scheme`
  until one is chosen.

## Language: English and Chinese (Khmer later)

The root `CLAUDE.md` bilingual conventions apply to V3 **unchanged**:

1. Clock date format `DD/MM/YY`; time above date.
2. Chinese is **Simplified**, matching the legacy dashboard's vocabulary —
   grep `dashboards/` for an existing term before inventing one.
3. Proper nouns and device names may stay Latin (CasaRay, Hue, Fronius Primo,
   eero, Ray, Pogo…).
4. Chinese enumerations use `、`.
5. Translate every user-facing string: titles, headings, summaries, status
   text, alerts, explanations.
6. Never translate entity IDs, identifiers, keys or paths.

In the prototype, all strings live in one dictionary keyed by language, and a
toggle switches instantly without reload. In Home Assistant the toggle is
`input_boolean.chinese_dashboard`; the prototype mirrors it as mock state
under that same ID. Layouts must survive both languages — check that no label
truncates in either.

**Prepare for future Khmer (`km`) support** without building it yet:

- String keys, never inline copy; the dictionary is `{en, zh, km?}` and a
  missing `km` string falls back to English.
- The language switch is a list of languages, not a two-state toggle, so a
  third entry needs no redesign. (Home Assistant's binary
  `input_boolean.chinese_dashboard` would need a successor helper — an
  implementation question recorded in `DECISIONS.md`, not solved here.)
- Khmer script needs more line height and horizontal room than Latin or Han
  and has no spaces between words: no fixed-width text containers, generous
  line height, and a Khmer-capable font in the fallback stack.

## Design review gate

Before the interactive prototype is completed, present **distinct
visual concepts** of the **Home** screen, rendered at the same iPad
landscape size with the same data, so they compare like for like:

- **A — Minimal architectural** (`concepts/ConceptA.dc.html`)
- **B — Modern dark control centre** (`concepts/ConceptB.dc.html`)
- **C — Balanced premium family dashboard** (`concepts/ConceptC.dc.html`)
- **D — V2 continuation** (`prototype/`, "Concept review" scenario). Added
  25/09/26 by owner instruction (`DECISIONS.md` V3-006). It is a candidate,
  not an approved implementation. Its existence does not satisfy or bypass
  this gate.

The like-for-like comparison is `concepts/COMPARISON.md`, regenerated with
`tools/capture_comparison.cjs`.

**Wait for the owner's selection.** Do not complete the prototype, and do not
build other destinations in a chosen style, before it. Record the selection
(and any mixing of concepts the owner asks for) in `DECISIONS.md`.

## The interactive prototype

- Lives in `design/casaray-v3/prototype/`. Plain HTML, CSS and JavaScript,
  opens from the file system or any static server; no build step unless one
  is clearly justified and documented.
- **Mock data only**, in `design/casaray-v3/prototype/mock-data/`, keyed by
  **real entity IDs** from the states export, with realistic states and
  attributes. Include a **degraded scenario** (entities `unavailable` /
  `unknown`) alongside the normal one, and a way to switch between them —
  that is how the third branch of every card gets reviewed.
- Controls change mock state and re-render; they never call a network API.
- No third-party runtime dependencies from arbitrary hosts; if a library is
  needed, vendor it or load it from a pinned CDN URL and note why.

## Suggested layout

```
design/casaray-v3/
  CLAUDE.md               this file
  README.md               what V3 is, how to open the prototype
  SPEC.md                 design specification
  FEATURE_PARITY.md       current capability → V3 location
  ENTITY_MAPPING.md       V3 surface → real entity IDs
  DECISIONS.md            dated V3 design decisions and departures from V2
  concepts/               Home concepts A–C, the index and COMPARISON.md (D lives in prototype/)
  prototype/
    index.html
    styles/  scripts/  mock-data/  i18n/
```

## Workflow

1. At session start: read the root `CLAUDE.md`, this file, and
   `design/casaray-v3/DECISIONS.md` if it exists. Confirm the branch is
   `casaray-v3-design` and the tree is clean.
2. Work in small, reviewable steps; one coherent change per commit.
3. Before each commit: grep every newly referenced entity ID against the
   states export; check both themes, both languages, and the iPad, desktop
   and mobile widths; confirm no file outside `design/casaray-v3/` changed
   unless the owner asked for it; confirm no secrets.
4. Commit with a clear message and push to `casaray-v3-design`
   (`git push -u origin casaray-v3-design`).
5. Show the owner the result — a render or screenshot of the prototype, not
   only a description — and get approval at each design milestone before
   building on it.

## Relationship to the root rules

- **Push targets.** The root rule "push to `ha-deploy` and
  `claude/ha-dashboard-upgrades-wui7ig`" governs V2 dashboard batches. It
  does **not** apply to V3: V3 pushes only to `casaray-v3-design`.
- **Validation gate.** `scripts/ha_validate.sh` validates the deployed
  dashboards. V3 does not change them, so the gate should keep passing
  unchanged; run it if anything outside `design/casaray-v3/` is touched.
- **Canonical target.** `dashboards/casaray_v2.yaml` remains the canonical
  CasaRay dashboard. V3 is a proposal for its successor; it becomes a build
  target only when the owner says so, and that migration will be planned as
  its own piece of work under the root rules.
- **SHA stamping and tracking documents** (`PROJECT_STATE.md`,
  `DASHBOARD_*.md`) are for V2 batches. V3 records its history in
  `design/casaray-v3/DECISIONS.md` and does not edit those files.
- **Legacy dashboard, deployment bridge, protected areas:** unchanged — still
  do not touch.
