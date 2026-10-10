# CasaRay V3 — decision log

Dated design decisions for V3, newest first. Each entry says what was decided,
why, and whether the owner has approved it. V2 (`dashboards/casaray_v2.yaml`)
and `ha-deploy` are unaffected by everything here.

---

## V3-007 · 05/10/26 · Owner review of PR #4: air-con is navigation, Home is shorter

**Status:** owner decisions, recorded and applied in the prototype.

**1. Parents' air-con is not approved as an Off ↔ Cool toggle.**
`climate.bedroom_parents_room_ac` is not a switch. Restoring "on" needs a
target temperature, a fan mode, a swing mode and a decision about which HVAC
mode (Cool, Heat, Dry, Auto) was meant. The earlier toggle was acceptable as
a demo and must not become production behaviour.

- Home's fourth One tap slot stays, and still shows the state in words
  ("Off · room 23.3°") and the no-data card. It is now **navigation**: a tap
  opens the Parents' room page, where the climate controls are. Home issues
  no HVAC change. The demo power handler is deleted, not hidden.
- A direct power control may return only as a defined preset, for example
  "Parents Comfort": Cool, 23 °C, Auto fan, a known swing setting. That is
  **not built and not approved**; it needs the owner to define it.

**2. About three screens is too long for Home.**
Home is current state plus immediate action. Detail, history and
configuration belong on other boards. Target: zero scrolling for the
glanceable first screen, and a full page of about 1.5–2 wall-iPad screens
(preferred ≤ about 1,640 px).

| Removed from Home | Now lives on |
|---|---|
| Whole-house scenes (proposed): Evening, Goodnight, Movie, All lights off | **Lighting**, as "Whole-house scenes (proposed)", each still marked Proposed (CR-233) |
| Recent activity | **House health** |
| Four-day forecast | **Climate** (Home keeps the current reading) |
| Monitored power with its 12-hour bars | **Energy** (Home keeps a one-line tile that says two circuits, not the whole house) |

Nothing was deleted. The proposal, its strings and its gap captions are
intact. Home's first-screen hierarchy is unchanged.

**Measured at 1180 × 820** (full-page `scrollHeight`; QA re-measured the
After columns on 05/10/26 and corrected the outage figure, which read 1,612 px):

| Scenario | Before (English) | After (English) | After (中文) |
|---|---|---|---|
| Evening (4 alerts) | 2,353 px | 1,722 px | 1,683 px |
| Concept review snapshot | 2,250 px | 1,619 px | 1,599 px |
| Everyone away (5 alerts) | 2,326 px | 1,695 px | 1,672 px |
| Device outage | 2,024 px | 1,582 px | 1,563 px |

The two worst days sit slightly above the preferred 1,640 px because the
alert cards grow with the number of alerts, not because Home grew. Rooms stay
(two across, three rows). If Home must get shorter still, the next candidates
are the Security summary row and More boards, which duplicates the rail.

**Addendum · 05/10/26 · owner decision after QA of PR #4.** The QA verdict
was *pass with non-blocking recommendations* (commit `1aef726`). The owner
decided:

- **Keep the current Home as built in `1aef726`.** No further Home
  compression in PR #4. **Keep the Security summary. Keep More boards for
  now. Keep the dense-alert truncation** (from five alerts: three across, one
  line of detail, still one tap to the board).
- **≤ 1,640 px is a preferred target, not a blocking requirement.** Evening
  and Everyone away sit slightly over it because of genuine alert growth, and
  that is accepted. First-viewport hierarchy is not traded for page height.
- Hiding More boards where the persistent rail is visible stays a **future
  design candidate only**.

**Post-merge hardening.** Recorded as follow-ups. **None is done in PR #4.**

1. Review whether the Parents' room and Climate HVAC mode controls need the
   same safeguards as Home.
2. Review the green "Nothing needs attention" heading when one or more checks
   are unanswered.
3. Fix overdue-bill alerts so a missing amount does not become A$0.00.
4. Define the Parents' room occupancy no-data behaviour.
5. Raise the shopping-list checkbox and touch targets toward 44 px.
6. Review the slight layout inconsistency of Lighting's "All lights off" card.
7. ~~Reconcile the documented 133 entity count with the verifier's 136.~~
   **Resolved in documentation, 10/10/26** (`ENTITY_MAPPING.md` §1): 133 is
   the prototype's own IDs, 136 adds three IDs the notes name as unused.
8. Consider conditional More boards visibility: desktop and kiosk versus phone.

**QA note, 10/10/26 (merge-readiness check of PR #4 at `0d2a241`).** No code
changed. The harness (108/108) and verifier (136/136) were re-run and pass.
The eight follow-ups above were each reproduced against the prototype, and
all of them are **inherited from Concept D at `58c7fdb`**; PR #4 did not
introduce them. Findings, so the deferral can be confirmed with evidence:

1. *HVAC safeguards.* Home has **no** HVAC control. The Parents' room page and
   Climate board still offer Off / Cool / Heat / Fan and ±0.5° steps. They
   change mock state only (the prototype makes no network call) and `acCard` is
   byte-identical to the base. A hard gate before any build.
2. *Green all-clear.* Reproduced: with no alerts and one unanswered check, the
   card is still green with a check icon and reads "Nothing needs attention",
   while the heading says "1 check could not answer" and the hero sentence is
   correct ("Nothing is flagged, but 1 check could not answer"). The words are
   qualified; the tone is not.
3. *A$0.00.* Reproduced: with `input_number.gas_bill_amount` unavailable the
   overdue alert reads "Gas A$0.00" (`num(b.amt) || 0`). No shipped scenario
   makes a bill amount unavailable.
4. *Occupancy.* Reproduced: with the Parents' room occupancy sensor unavailable
   the tile is omitted from Right now, not drawn as no data. It happens in the
   Device outage scenario.
5. *Touch targets.* Measured: shopping-list checkboxes are 24 × 24 px (rows
   are 44 px tall, but only the box is a button); the top-bar language, theme
   and demo buttons are 40 px tall.
6. *Lighting "All lights off".* The tile's detail wraps to two lines, so its
   icon sits higher than the other three. Size is identical (251 × 177 px).
7. *133 vs 136.* Resolved above.
8. *More boards.* A design choice, not a defect.

---

## V3-005 · 05/10/26 · Home direction — OWNER-CONFIRMED

**Status:** selected, then **explicitly confirmed by the owner on 05/10/26**
after QA of PR #4. The confirmation settles the provenance question QA raised;
V3-005 is neither open nor inferred. This is a deliberate hybridisation of
approved elements, **not a new independent concept** and **not a wholesale
merge of all four concepts**. The V3-007 decisions remain authoritative.

**Owner confirmation (05/10/26).**

- **Concept D is the primary CasaRay V3 design base.**
- **Concept C shapes the Home-page information hierarchy and presentation.**
- **Concepts A and B may be used as supporting design patterns where they
  improve usability without conflicting with D and C.**
- This does **not** mean wholesale merging of all four concepts.
- Existing V3-007 decisions remain authoritative.

**What that covers.**

- **Concept D is the architectural base:** system shell, design tokens,
  responsive architecture, room templates, component architecture, test
  harness.
- **Concept C shapes Home:** Home-screen hierarchy, plain-language household
  status, large controls, people first, wall-iPad usability.
- **Concept A's energy truth strip** is used as a supporting pattern:
  measured, unavailable, unknown and no-source readings never share a look.
- **Concept B's four-state camera presentation** is a supporting pattern for
  later. It is **not** built in this sprint.

**Rationale.** D has the strongest scalability and maintainability: the only
candidate that covers all boards, rooms, themes and breakpoints, on V2's
sampled tokens, with a 68-check harness. C has the strongest wall-iPad and
household usability: a sentence in plain words, 52 px+ controls, people
first. A makes the energy gaps (no export source, V3-003) visible instead of
hiding them. B keeps *offline* and *unknown* apart for cameras.

**Not adopted:** B's icon-only navigation; B's dense custom power-flow as
Home; A's thin type and gold accent; C's ten-label bottom bar; D's old
2.6-screen Home.

**First visual sprint (Home first screen only).** The first 1180 × 820
viewport now holds, in this order: greeting and a status sentence built from
the Needs-attention checks (Level 1), Needs attention, Who's home beside the
Energy truth strip (Level 2), and four large One tap controls that say state
*and* action ("On — tap to turn off"). Details are in `DESIGN_SPEC.md` §4a.

- Navigation is unchanged apart from legibility: rail labels 11.5 → 12.5 px,
  clock 22 → 28 px, tool buttons 13 → 14 px.
- Home's chip strip is gone; Outside and Inside moved into the hero, Home
  count into the people cards, Monitored into its own section below.
- The four whole-house scripts (CR-233) first stayed on Home as a second,
  quieter row labelled *proposed*; V3-007 moved them to Lighting. One tap's
  row uses controls that exist today:
  `light.living_room`, `light.dining`, `fan.living_room_air_purifier`,
  `climate.bedroom_parents_room_ac`.
- No entity ID was introduced. Export has no source: V3-003 still applies.
- Other boards, Security and Cameras are untouched.

**Both open questions were answered in V3-007.** The air-con is navigation,
not a toggle; Home is cut to about two screens, and the whole-house row and
Recent activity moved off it.

---

## V3-006 · 25/09/26 · Parallel prototype registered as Concept D (reconciled)

**Status:** reconciled by owner instruction on 25/09/26. **This does not
choose a concept.** V3-005 stays reserved for the owner's selection among
A, B, C and D, or a mix of them. *(Resolved 05/10/26: see V3-005.)*

A second Claude session, working from a direct owner request made before this
workspace's `CLAUDE.md` existed, built a complete interactive prototype in
parallel (`prototype/`, `FEATURE_INVENTORY.md`, `DESIGN_SPEC.md`,
`ENTITY_MAPPING.md`, `tools/`). It was first logged here as unreconciled.

**Owner decision (25/09/26):** the prototype is registered as **Concept D —
V2 continuation**, a fourth design candidate beside A, B and C. It is **not**
an approved production implementation, and it is not the chosen direction.

What changed to reconcile it:

- `CLAUDE.md` design review gate lists four concepts. D's location is
  recorded, and the gate still blocks building other destinations in a
  chosen style until V3-005.
- `concepts/README.md` indexes D. `concepts/COMPARISON.md` compares A–D on
  one snapshot at 1180 × 820: navigation, Home layout, room access, energy,
  security, usability, and features that combine whatever is chosen.
- D gained a **Concept review** scenario carrying A–C's exact snapshot, so
  all four compare on the same data. It also got one fix: its weather card
  now follows the entity's condition instead of always saying "Cloudy". The
  prototype was not rebuilt, and its 68 checks still pass.
- Concepts A, B and C are byte-identical. SHA-256 was checked before and
  after.

Where D departs from the V3-001 rules still stands, and is set out in
`concepts/COMPARISON.md`:

- **Navigation:** a different set of destinations, and Back appears only on
  room pages.
- **Home length:** Home scrolls (2.6 screens) rather than fitting the wall
  iPad.
- **Cameras:** no separate *unknown* state.
- **Language:** a two-state switch, not Khmer-ready.
- **Type and icons:** three type families, and filled rather than stroke
  icons.
- **Sirens:** a three-across tile rather than the large treatment.
- **Names:** tokens and file names differ from `--v3-*`, `SPEC.md` and
  `FEATURE_PARITY.md`.

These matter only if D, or part of it, is chosen.

It also found an error that applies whichever concept is chosen: V2 calls
Powerpal "whole-house", but it is grid import (V3-003 agrees).

## V3-004 · 25/09/26 · Home concept review — awaiting owner selection (closed by V3-005)

**Status:** closed 05/10/26 by V3-005 (owner-confirmed). Kept as the record of
the review; it was open and blocking when written.

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
