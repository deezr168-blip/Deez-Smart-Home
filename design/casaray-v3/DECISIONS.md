# CasaRay V3 — decision log

Dated design decisions for V3, newest first. Each entry says what was decided,
why, and whether the owner has approved it. V2 (`dashboards/casaray_v2.yaml`)
and `ha-deploy` are unaffected by everything here.

---

## V3-006 · 25/09/26 · A second session built a full prototype — not reconciled with V3-004

**Status:** open, awaiting the owner. **This entry does not choose a concept
and does not close V3-004.** V3-005 stays reserved for the concept selection.

A second Claude session, working from a direct owner request made before this
workspace's `CLAUDE.md` existed, built a complete interactive prototype in
parallel:

- `prototype/`: vanilla HTML/CSS/JS, 10 boards and 8 room pages, mock data on
  132 real entity IDs (all present in the 05/09 export and all already on V2),
  three scenarios (normal · everyone away · device outage), dark/light, EN/中文
  via `input_boolean.chinese_dashboard`.
- `FEATURE_INVENTORY.md`, `DESIGN_SPEC.md`, `ENTITY_MAPPING.md`, `README.md`,
  and `tools/` (entity verifier, a 68-check Playwright harness).

It conflicts with the review gate in `CLAUDE.md` ("do not complete the
prototype … before" a concept is chosen), and it departs from several rules
added in V3-001:

- **Navigation.** It has Media and People as destinations. It has no separate
  Network, Alerts or Lighting studio.
- **Home and Back.** Back appears only on room pages, not on every screen.
- **Language.** The switch has two states and is not Khmer-ready.
- **Home length.** Home scrolls on the wall iPad.
- **Sirens.** They use a three-across tile, not the large, hard-to-mis-tap
  treatment.
- **Fonts.** It uses three families, not two.
- **Icons.** It uses filled MDI icons, not a stroke set.
- **Names.** Tokens and file names differ from `--v3-*`, `SPEC.md` and
  `FEATURE_PARITY.md`.

It was pushed only so the work is not lost when its container is reclaimed.
The owner was offered three ways forward:

1. Treat it as a fourth concept, **D**, alongside A–C in V3-004.
2. Adopt it as the prototype and update `CLAUDE.md` to match.
3. Set it aside, choose from A–C, and build the prototype under these rules.

**Until the owner answers, do not delete, restructure or build on
`prototype/`, and do not treat it as the chosen direction.** It also found an
error that applies to all V3 work: V2 calls Powerpal "whole-house", but it is
grid import (V3-003 agrees).

## V3-004 · 25/09/26 · Home concept review — awaiting owner selection

**Status:** open, blocking the interactive prototype.

Three Home concepts are drawn at iPad landscape (1180 × 820), using the same
mock data built on the same real entity IDs:

- **A — Minimal architectural.** Typography and whitespace carry the page.
  Hairline rules instead of card fills, one accent, nav as a text rail.
- **B — Modern dark control centre.** A dense tile grid on deep surfaces, a
  live power-flow strip, a camera status matrix, nav as an icon rail.
- **C — Balanced premium family dashboard.** Softer glass cards, larger
  friendly type, people-first, a status sentence in plain words, big scene
  buttons for parents.

The canvas is the design artifact linked in the session. `concepts/` in this
directory holds the same artboard sources. **No concept is chosen until the
owner picks one** (or asks for a mix); the choice will be recorded here as
V3-005.

## V3-003 · 25/09/26 · Energy: export and whole-house consumption have no verified source

**Status:** open finding, needs owner input before the Energy board is built.

The states export has Fronius *inverter* entities
(`sensor.primo_5_0_1_1_ac_power`, `sensor.primo_5_0_1_1_energy_day`,
`sensor.solarnet_power_photovoltaics`) and Powerpal *meter* entities
(`sensor.powerpal_gateway_powerpal_power`,
`sensor.powerpal_gateway_powerpal_daily_energy`,
`sensor.powerpal_gateway_powerpal_total_energy`). It has **no Fronius smart
meter power entity** (no `power_grid` / `power_load` sensor) and no export
energy sensor.

Consequences:

- **Grid import** → Powerpal power. Verified.
- **Solar production** → Primo AC power / energy day. Verified.
- **Export** → no source entity. Drawn as "no source entity" in every concept.
- **Consumption** (import + solar − export) cannot be computed honestly
  without export. The concepts show import and solar, and label consumption
  as unavailable rather than summing two of three terms.
- **Battery** → none installed; a separate "Future battery" section reads
  "not installed".

Open question for the owner: is a Fronius Smart Meter fitted but not
integrated, or does Powerpal read a net (bidirectional) meter? Either would
unlock export.

## V3-002 · 25/09/26 · Live instance mostly dark at the time of design

**Status:** recorded; does not change the design.

A read-only live check on 25/09/26 returned `unavailable` for all three
`person.*` entities, `weather.forecast_home`, four of six camera streams and
most individual lights; `climate.bedroom_parents_room_ac` answered (`off`,
23.2 °C). The Fronius and Powerpal sensors are not exposed to the assistant
API, so their live values could not be read.

The concepts therefore use **mock values** on real entity IDs (a normal
evening), with the cameras that are known to be offline drawn offline — and
each concept states "mock data" on the page. The degraded scenario that the
prototype must include (see `CLAUDE.md`) is essentially today's live state.

## V3-001 · 25/09/26 · Requirements extended before development

**Status:** owner instruction.

Added to `CLAUDE.md`: visual identity; ten-destination navigation with Home
and Back on every screen; Home priorities with minimal scrolling on the wall
iPad; consistent room layout and simple parents' controls; Energy from
verified Fronius and Powerpal data with a separate future battery section;
four distinct camera/security states; consolidated House health; mobile and
desktop hierarchies redesigned rather than scaled; Khmer readiness; and the
three-concept design review gate.

Chinese navigation labels reuse V2 terms; "灯光工作室" (Lighting studio) is
new and provisional.

Khmer: the prototype's language switch is designed as a list. Home Assistant
currently has only the binary `input_boolean.chinese_dashboard`; a third
language would need a successor helper (e.g. an `input_select`). That is an
implementation decision for later, not made here.

## V3-000 · 25/09/26 · V3 workspace established

**Status:** owner instruction.

`design/casaray-v3/CLAUDE.md` created: V3 is a design and prototyping track on
`casaray-v3-design`; no deployment, no changes to `ha-deploy`, no
authentication or backup changes; V2 stays the canonical dashboard.
