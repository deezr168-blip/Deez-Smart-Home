# CasaRay V3 — decision log

Dated design decisions for V3, newest first. Each entry says what was decided,
why, and whether the owner has approved it. V2 (`dashboards/casaray_v2.yaml`)
and `ha-deploy` are unaffected by everything here.

---

## V3-009 · 01/11/26 · V3 becomes a Lovelace build target, offline, on its own branch

**Status:** owner instruction (01/11/26), implemented on `feature/casaray-v3-build`.
DEVELOPMENT ONLY — NOT DEPLOYED.

The owner directed a complete offline Lovelace build of V3 on a dedicated
branch, `feature/casaray-v3-build`, with paths outside `design/casaray-v3/`
(`src/casaray_v3/`, `scripts/v3/`, `tests/v3/`, `docs/casaray-v3/`, generated
`dashboards/casaray_v3*.yaml`). That instruction is the approval this file's
*Hard boundaries* require for both. Everything else in those boundaries stands:
no deployment, no `ha-deploy` or recovery-branch change, no live writes,
CR-T01 / CR-T02 paused.

Decided in the build (each recorded in `docs/casaray-v3/ARCHITECTURE.md`):

1. **Baseline pinned:** `ha-deploy@18a4e5d` `casaray_v2.yaml`, sha256
   `77a49916…6c`. The build refuses to run on drift.
2. **No silent loss:** V2 views not yet rebuilt are carried verbatim (links
   rewritten); each rebuilt view keeps its V2 original as a `v2-<path>` subview.
3. **Languages:** English, Cantonese (`yue`, Traditional HK script) and Khmer,
   built per locale at build time, because a three-way runtime switch needs a
   new helper and helpers are out of scope. This departs from *Language:
   English and Chinese (Khmer later)* above: Cantonese is the owner's new
   requirement, and Simplified Chinese is kept as a fourth, partial locale
   (`zh-Hans`, V2 vocabulary) for parity. `yue` and `km` are unreviewed drafts.
4. **HVAC read-only** in V3-native views until V3-008's production gate is met.
5. **"All lights off"** no longer cuts `switch.mainroomlight_switch_1` (bulb
   power) in V3-native views. Departure from V2, owner rule on bulb power.
6. **Back = Home** on top-level views: Lovelace has no history-back action.

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
After columns on 05/10/26; the outage row was re-measured on 11/10/26 after the occupancy tile stopped hiding):

| Scenario | Before (English) | After (English) | After (中文) |
|---|---|---|---|
| Evening (4 alerts) | 2,353 px | 1,722 px | 1,683 px |
| Concept review snapshot | 2,250 px | 1,619 px | 1,599 px |
| Everyone away (5 alerts) | 2,326 px | 1,695 px | 1,672 px |
| Device outage | 2,024 px | 1,657 px | 1,608 px |

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

**Hardening, as decided on 11/10/26.** The owner moved four of the eight
follow-ups out of "post-merge" and into PR #4: they were fixed on this branch
before approval (see *Fixed before merge* below). Three stay post-merge and one
is documentation.

1. **Post-merge:** review whether the Parents' room and Climate HVAC mode
   controls need the same safeguards as Home. A hard gate before any build.
2. **Fixed before merge (11/10/26):** the green "Nothing needs attention" card
   when one or more checks are unanswered.
3. **Fixed before merge (11/10/26):** overdue-bill alerts turning a missing
   amount into A$0.00.
4. **Fixed before merge (11/10/26):** the Parents' room occupancy tile
   disappearing when its sensor cannot answer.
5. **Fixed before merge (11/10/26):** interactive targets under 44 × 44 px.
6. **Post-merge:** the slight layout inconsistency of Lighting's "All lights
   off" card.
7. ~~Reconcile the documented 133 entity count with the verifier's 136.~~
   **Resolved in documentation, 10/10/26** (`ENTITY_MAPPING.md` §1): 133 is
   the prototype's own IDs, 136 adds three IDs the notes name as unused.
8. **Post-merge:** conditional More boards visibility, desktop and kiosk
   versus phone.

**Merged 11/10/26.** PR #4 was merged into `casaray-v3-design` at `3eed6ca`
(owner approval; design-branch integration only; nothing deployed, nothing
verified live). The three post-merge items above stay open and are unchanged.

**V3 backlog: latent truthfulness fallbacks (found in the final PR #4
review, 11/10/26).** All three are inherited from Concept D, none is reachable
in a shipped scenario (every real motion and occupancy sensor carries an `ago`,
and the demo data always supplies brightness and position), and **none is
fixed**. Each needs its own authorisation, and each must come with a regression
check like the four hardening fixes above.

9. **`dur(ago || 0)` must not fabricate elapsed time.** When `ago` is absent a
   quiet sensor reads "Quiet · 1 min". It should say no data, or omit the
   duration. In `prototype/app.js`: the Kitchen movement tile (~line 427), the
   Movement chip (~line 571) and the Home occupancy tile (~line 729).
10. **`brightness ?? 0` must not fabricate zero brightness.** A light that
    answers without a brightness attribute gets a 0 % bar (~line 328). It should
    draw no value.
11. **`position ?? 0` must not imply a cover is closed.** A cover that answers
    without a `position` reads "Blind closed", whatever its state (~lines 402
    and 468). It should use the cover's own state, or say no data.

**QA note, 10/10/26 (merge-readiness check of PR #4 at `0d2a241`).** No code
changed. The harness (108/108) and verifier (136/136) were re-run and pass.
The eight follow-ups above were each reproduced against the prototype, and
all of them are **inherited from Concept D at `58c7fdb`**; PR #4 did not
introduce them. Findings (items 2–5 were then fixed, see below):

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

**Fixed before merge, 11/10/26.** Code and tests only; no entity ID was added.

- **All-clear (2).** With no alerts and at least one unanswered check, the card
  is grey with an information icon, titled "Not every check answered", and
  reads "Nothing is flagged, but 1 check could not answer." The green check
  card and "Nothing needs attention" appear only when every check answered.
- **Bill amounts (3).** `num(b.amt) || 0` is gone. A real `0` reads A$0.00;
  an unavailable or unknown amount reads "(amount: no data)", on the Home
  alert and on the Bills board (which also used to drop a real 0). The overdue
  state is still shown, because it comes from the due date and the paid flag.
- **Occupancy (4).** The Parents' room tile stays in Right now. With the
  sensor unavailable or unknown it is a dashed grey "No data" tile; occupied
  and quiet are unchanged. Device outage Home therefore grows from 1,582 to
  1,657 px in English (1,563 to 1,608 px in Chinese).
- **Touch targets (5).** Every button, switch, checkbox and range input is at
  least 44 × 44 px, at wall, portrait and phone sizes, in both languages, on
  every board, the demo panel and the phone More sheet: top-bar language, theme
  and demo buttons (44 px tall), the shopping-list checkbox (a 44 px button
  around the same 24 px box), light and plug icon buttons, the tile name
  buttons, segment buttons, brightness bars, switches, Back and the Mark paid
  buttons. The drawn checkbox and switch track are unchanged in size.

New regression checks cover 0 alerts + 1 unanswered check (grey, and green
only when everything answered), a real zero, an unavailable, an unknown and a
normal bill amount, occupied / quiet / unavailable / unknown occupancy, and a
44 px sweep of every board. Run against the previous prototype they fail 19
times, so they do detect the defects. Harness 140/140.

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
