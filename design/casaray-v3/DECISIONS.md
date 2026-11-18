# CasaRay V3 — decision log

Dated design decisions for V3, newest first. Each entry says what was decided,
why, and whether the owner has approved it. V2 (`dashboards/casaray_v2.yaml`)
and `ha-deploy` are unaffected by everything here.

---

## V3-024 · 18/11/26 · Release preview integration: PR #16's cameras with one named, readable top bar

**Status:** owner brief (18/11/26, "CasaRay V3 release preparation"), against the gate
document of PR #23 (`docs/casaray-v3/RELEASE_PREVIEW_GATE_2026-11-19.md`). Built on the isolated
branch `feature/casaray-v3-release-preview`, from `feature/casaray-v3-build` at `116c043`.
DEVELOPMENT ONLY — NOT DEPLOYED. Not merged; merging and any deployment each need a separate
owner approval. Numbered after PR #21's V3-020–023 so both logs stay unique.

1. **What was integrated, and how.**
   - PR #16 (`97e9bce`, V3-014) merged whole: the camera slots, the same-size Offline cards,
     the native full-screen tap, the Cameras `band_grid: 24` layout and the Home sizing. No
     file it touches had changed on the build since its base, so the merge was clean, and
     all four gates passed at the merge (`5407cd2`): build `--check` current,
     `validate_dashboard.py` 1437 / 0, `tests/v3` 105 OK, `ha_validate.sh` PASSED.
   - PR #23 (`e413aaa`) merged: the gate document only.
   - From PR #21, **one tooling commit only**, cherry-picked with provenance: `fd0b3df`, the
     preview's button and markdown metrics read from the pinned frontend. Without it the
     preview drew labels at 14 px with padding and under-reported clipping. Its markdown
     hunk conflicted with PR #16's identical correction; PR #16's side was kept.
   - **Not integrated:** PR #21's Weather and Rubbish pages, its reminder proposal, its
     `header_title` key, its Home changes (V3-023 4), and its new-page generator.
2. **Navigation: the conflict between PR #16 and PR #21, settled for this release.**
   PR #16's bar was six icon-only buttons, so no destination had a word. Every other native
   view still had the older bar, where only the current page was named and was twice the
   height of the rest. Measured before the change (offline preview, all four locales):
   "Lighting" clipped on a phone in its own rail, and the Khmer header overflowed its
   56 px cell on Home and Cameras.
   - **One bar on every native view** (`components.topbar`), re-implemented here from
     V3-023's measured geometry, not copied. A text-only header (6 units × 2 rows: title,
     then the time over `DD/MM/YY`, then "Preview"), then six named buttons at 3 units ×
     2 rows. On the wall iPad that is one 120 px row; on a phone, two 120 px rows. Every
     cell is one height, so Home sits in the same place on every page.
   - **The current page is marked**, not only inert: `color: accent` on its button. Read
     from the pinned frontend (`20260826.7`, `hui-button-card.ts` `_computeColor`; and
     `compute-color.ts`): with no entity, `color` sets `--state-color`, which tints the
     icon, and `accent` resolves to `var(--accent-color)`. The V3 theme maps that to
     `--v3-accent`, amber, "selected". No theme or card_mod change.
   - **More boards** on the 16 views not on `band_grid: 24`: 4 units (it was 3) and the 2
     rows a named button draws anyway. Six across on the wall, three on a phone at about
     119 px. At 3 units, "Entertainment" clipped on a phone. Home and Cameras keep PR #16's
     6 units.
3. **Measured** (`preview_view.py --shots`: the frontend's grid, approximated card
   interiors, fixture states, Khmer OS for Khmer, WenQuanYi for Han; **not a device**):

   | | PR #16 (before) | V3-024 (after) |
   |---|---|---|
   | Rail labels on Home and Cameras | none (icons only) | all six named, every locale |
   | Rail button width, wall / phone | 79 / 56 px | 122 / 88 px |
   | Top bar height on the 18 native views, wall | 56 px (Home, Cameras), 96–120 px elsewhere | 120 px everywhere |
   | Top bar height, phone | 120 px (Home, Cameras), 160–262 px elsewhere | 248 px everywhere |
   | Rail labels clipped or wrapped, 18 views × 4 locales × 2 devices | "Lighting" (en, phone); km "ថាមពល" (phone) | **none** |
   | Header overflow | km Home and Cameras | **none** |
   | Tap targets under 44 px | none | none |
   | Home page height, en, wall / phone | 2,566 / 4,679 px | 2,630 / 4,807 px |
   | Cameras page height, en, wall / phone | 2,161 / 3,971 px | 2,225 / 4,099 px |
   | Band holes under the bar (Home, Cameras) | unchanged | unchanged |

   The cost is the labels' height: +64 px on the wall and +128 px on a phone for Home and
   Cameras. Elsewhere the bar was 96–120 px on the wall (now up to 24 px taller) and
   160–262 px on a phone (now 248 px: shorter on Lighting and Energy in km, taller on Rooms).
4. **Scope, checked by script against the integration head:** in all four locales 28 views
   are byte-identical; on the 18 native views only section 0 (the top bar) changed, plus
   the More boards buttons' `grid_options` on 16 of them — nothing else in those cards.
   No camera card, entity ID, navigation path, safety rule or locale string changed.
5. **Gate and tests.**
   - `validate_dashboard.topbar_problems` runs on every native view in every locale (+72
     checks, 1509 passed). It checks the time over `DD/MM/YY`, six rail buttons in order,
     each named and at least 3 units, one cell height, whole rows on 24 and 12 units,
     exactly one inert amber button on a rail destination and none elsewhere, and every
     other button navigating to its own page.
   - `tests/v3/test_topbar_v3_024.py` (12 tests): the gate on every view, one bar shape
     everywhere, labels from each locale's own catalogue, the marked page, the row
     arithmetic, the header, More boards sizing. It also plants PR #16's icon-only bar,
     the older named-current-only bar, an unmarked current page, a wrong link and a
     four-digit year, and checks that the gate rejects each one.
   - PR #16's `CompactTopBar` tests asserted the icon-only design and were retired with it.
     Two Alerts tests picked rendered cards by position; they now skip however many cards
     the top bar emits, with every assertion unchanged.
   - `preview_view.py` now also reports wrapped labels, tap targets under 44 px, the top
     bar's height and the rail widths.
   - At `c97db94`: `tests/v3` **114 tests, 0 failures** (533 s); `ha_validate.sh` PASSED with
     the same 470 warnings as the merge; a fresh build in a clean worktree is byte-identical
     to the committed outputs in all four locales.
6. **Found, not changed here (outside navigation):**
   - Lighting's scene buttons on a phone: "Concentrate" clips, and five two-word scene names
     wrap.
   - "Classic V2 view" wraps at a word boundary on a phone (en, zh-Hans, km). It is
     readable, but not a single line.
   - The km strings remain a draft awaiting a native reader.
7. **Still needs a device:** label fit with Home Assistant's own fonts, the amber icon on the
   current page, and the header at the frontend's real type sizes. Each is from the pinned
   source and a simulation, not a screenshot. See the gate document's preflight.

---

## V3-014 · 15/11/26 · Camera slots that say Offline, a native full-screen tap, and a one-height top bar

**Status:** owner request (15/11/26), prepared on `feature/casaray-v3-cameras-layout`, branched
from `feature/casaray-v3-build` at `1a669a3`. DEVELOPMENT ONLY — NOT DEPLOYED. Waiting for the
owner's approval before anything goes to the Green.

1. **Baseline.** The live dashboard configuration could not be read from this session. No
   computer is connected through Remote Control, and the Home Assistant connector reads entity
   states, not dashboards. Neither the live export nor `casaray-v3-before-home-upgrade.yaml`
   reached the session. The baseline is the repo at `7f16e79`. Before any deploy, the live
   export is diffed against it, so edits made on the Green are not overwritten.
2. **Camera audit.** Entity IDs and names come from the 05/09 export. "Live" means read
   through the connector on 15/11; that gives state only, never playback.

   | Slot | Entity (unchanged) | 05/09 export | Live 15/11 |
   |---|---|---|---|
   | Front door | `camera.front_door_live_view` (Ring) | ok | idle; battery 66 % |
   | North wall | `camera.tapo_c425_north_wall_hd_stream_direct` (Tapo Control) | ok | idle; its battery and privacy entities unavailable |
   | East wall | `camera.tapo_c420_east_wall_hd_stream_direct` (Tapo Control) | unavailable | unavailable |
   | South wall | `camera.tapo_c420_south_wall_hd_stream_direct` (Tapo Control) | unavailable | unavailable |
   | Stockroom | `camera.tapo_c200_stockroom_hd_stream_direct` (Tapo Control) | ok | idle |
   | Pet feeder | `camera.smart_pet_feeder` | ok | not exposed to the connector, so unread |

   - **No camera is remapped. No replacement entity exists.**
   - Each C420 has a second device record. For East wall it is `tapo_camera_bcca_*`; for
     South wall it uses the same name prefix.
   - That record answers live: its battery reads 100 %, and its detection switches respond.
   - In the export it has **no camera entity**, so there is nothing to stream from.
   - The cameras answer, but Tapo Control's streams do not. The cause is not established
     from here.
3. **Full screen.**
   - Every camera tap used to open its V2 page, which streams through `custom:webrtc-camera`.
     That needs the WebRTC Camera integration from HACS and its front-end resource. On 02/11
     Ray reported `/config/custom_components` missing and the Resources list empty.
   - Tapo Control's cameras answer live now, so some custom components are back; whether
     WebRTC Camera is among them is unknown.
   - A tap now opens Home Assistant's own camera dialog. Its live view needs no custom card,
     and its video can go full screen.
   - The six V2 camera pages stay one tap away under More boards, with a note saying what
     they need.
4. **Offline in words, same size.**
   - The installed frontend draws an unavailable camera as a broken image or a spinner, with
     no state word (`hui-image.ts`, 20260826.7).
   - Each camera slot is now a picture shown while the camera is not `unavailable`, plus a
     same-size card shown only while it is. The card reads "*Name* · Offline", "No stream
     from Home Assistant" and the camera's battery reading, or "No battery reading".
   - An idle camera shows its picture.
5. **Compact top bar** (views on `band_grid: 24`: Home, Cameras).
   - A button showing an icon and a name is at least two rows. The current page's named rail
     button was twice the height of the rest, which made the iPhone's oversized Home tile
     and the gap before the chip strip.
   - Now the rail is six icon-only buttons; the current one is inert, and the title names the
     page.
   - The title and clock are text-only markdown, each one heading split by a line break, so
     no margin overflows the row.
   - The result is one 56 px row on the wall iPad and two on a phone, every cell the same
     height.
   - The clock keeps the time above `DD/MM/YY`.
   - The banner reads "Preview": it is the V3 Preview on the Green.
   - Other views keep their top bar until they are reviewed.
6. **Tightened against the preview**, measured on the frontend's own grid:
   - Rooms are all two rows, and the shopping list is eight rows to match.
   - Parents' room occupancy is three rows, and the air-con summary in Climate now is two,
     closing the gaps beside Right now and Energy now.
   - Cameras: two across on the wall iPad, one on a phone, Front door first.
   - Camera health sits beside the batteries, and the privacy tiles are named by camera (the
     friendly names were cut off).
   - In the preview, with no horizontal scroll, clipped label or overflowing card on either
     size: Home's paired sections end within 0, 12 and 25 px of each other, and Cameras'
     within 1 px.
7. **Gate.** On `band_grid: 24` views, packing is now checked with visibility applied, in
   three states: the fixture, everything answering and everything dark. The compact top bar
   is checked too. A test proves a half-size Offline card is caught.
8. **Needs action on the Green** (not done from here):
   - **East and South wall streams:** in Settings → Devices & services → Tapo Control, read
     each C420 entry's error. That decides re-authentication, a new address, or re-adding the
     camera through its hub.
   - **The V2 camera pages:** they need the WebRTC Camera integration (HACS) and its resource.
     Install it only if the owner wants those pages back.
   - **North wall:** its battery and privacy entities went unavailable after 05/09 while its
     camera still answers.

---

## V3-013 · 14/11/26 · Home against the 14/09 wall render; two-column bands sized for the grid Home Assistant draws

**Status:** owner request (14/11/26), implemented on
`feature/casaray-v3-home-mockup`, branched from `feature/casaray-v3-build` at
`7aaff9e`. DEVELOPMENT ONLY — NOT DEPLOYED. Waiting for the owner's review of
the side-by-side preview; nothing goes to the Green without that approval.

1. **Home follows the wall render.** `docs/mockups/2026-09-14_wall_home.png`,
   which is page 1 of *CasaRay Wall Panel.pdf*, is the reference. It was drawn
   for the wall iPad in landscape, in the language V3 uses: sentence case,
   amber for active, and cards that say one interpreted line. *Casa Ray
   Dashboard.pdf* (`2026-09-14_dash_home.png`) is not used for Home. Its
   uppercase section titles break the owner's sentence-case rule (14/09), and
   its content already exists on Home: room status and the camera row. Its
   three columns fold into two (DR-013).
2. **Finding: the installed frontend sizes two-column bands on 24 units.**
   This was read from home-assistant/frontend at `20260826.7`, the version
   Core 2026.9.2 pins; it was not seen on a device.
   - `hui-sections-view.ts` hands each section `--column-span`, clamped to the
     columns that resolve.
   - `hui-grid-section.ts` gives the section 12 × that span units.
   - On the wall iPad a `column_span: 2` band therefore has 24 units, and V3's
     `columns: 12` cards fill half of it.
   - `hui-card.ts` merges a card's own minimums under the YAML. A tile asked
     for 3 columns draws 6, and a button with an icon and a name asked for 1
     row draws 2.
   - Before this change, Home's chip strip filled half its band. The Needs
     attention, One tap and Security headings sat beside their cards. The
     Security band left 48 empty cells.
   - The finding is consistent with DR-012's live observation: a "3/12" pill
     drew as a circle, and `columns: 1` broke "CasaRay" vertically. On 24
     units those cells are about 120 px and 35 px wide.
   - It applies to every V3 native view, and to V2.
3. **What changed on Home** (`src/casaray_v3/views/home.yaml`, opted in with
   `band_grid: 24`):
   - **Chip strip:** the render's four pills — Outside (the weather entity's
     temperature), Inside (living-room sensor), Home (three people, what
     answered), **Two monitored plugs**. These are the four V2 Home showed.
     The plug total is shown only while both plugs it adds up answer;
     otherwise it says No data and "1 of 2 reporting". Lights on, Cameras
     online, House now and Solar now left the strip. Each is still on Home
     below: in the room lines, the Security summary and the Energy band.
   - **Bands at full width:** the chip strip, Needs attention, One tap (four
     across on the wall, two by two on a phone), Security and More boards
     (four across, at the two rows a named button really takes).
   - **Room tiles:** each room is one markdown card. It shows the name over
     one line of what its sensors say, and a tap opens the room. These are V2
     Home's room cards, ported with V2's Simplified Chinese vocabulary. A dark
     reading is counted ("1 not reporting"), never shown. A room where
     nothing answers says No data.
   - **Right now** carries the render's left column: the weather, sunrise and
     sunset, the two-plug card ("garage freezer and Ray's desk"), Solar
     expected today, and the footnote on what monitored means.
   - **Who's home** carries the people and the Parents' room occupancy card
     (state and time since change), as V2 and the render do.
   - Eleven of the sixteen V2-Home entities that V3 had moved elsewhere are
     on Home again. Their migration rows are removed. They stay on the boards
     they moved to.
4. **Kept as they were:**
   - Every entity ID, navigation path and view path.
   - The three lighting actions, byte for byte.
   - The air-con as navigation (V3-007), and every tile read-only.
   - The four-language build.
   - Recent activity stays on House health (V3-007). Neither render shows it
     on Home.
   - Whole-house scenes stay on Lighting (V3-007, CR-233).
   - The shared top bar is not changed.
   - Every other view is unchanged: none opts in to `band_grid`, and a test
     says so.
5. **Gate:**
   - `scripts/v3/ha_layout.py` holds the frontend's rules.
   - For a `band_grid: 24` view, `validate_dashboard.py` fails a band heading
     that is not full width, a band that leaves empty cells on the 24-unit or
     the 12-unit grid, and a card drawn at another size than its YAML says.
   - Every other native view gets a note giving its count of half-width and
     clamped cards.
   - The dark-state reassurance check now keys on the longest literal part of
     each reassurance string. Its first word, "All", matched any "All rooms"
     label. A test pins that the check still sees the real sentence.
6. **Preview, not device:**
   - `scripts/v3/preview_view.py` lays a view out with the frontend's
     sections CSS at 1180 × 820 and 390 × 844. It draws approximate card
     interiors with fixture values.
   - Measured there, Home's page height went from 2,340 to 2,492 px on the
     wall iPad and from 3,568 to 4,454 px on a phone. The room lines and full
     band headings account for it.
   - Nothing in this entry was seen on the wall iPad or a phone.
7. **Left for a second pass:**
   - The shared top bar: the current destination's button is named, so it
     draws two rows tall, and the clock is not at the right edge.
   - The other native views' bands (their gate notes count the cards).
   - Room icons: there is no verified way to draw one in a markdown card.
   - Amber emphasis on the active part of a room line.
   - Tinted alert cards: the native card cannot, and V3 has no card_mod.
   - "Home 2 of 3" wording: V3 says "Home 2" and adds a reporting count.
   - The forecast row, which is on Climate (V3-007).
   - The render's Evening, Goodnight and Movie scenes, which still need
     owner-defined scripts (CR-233).
   - The yue and km strings for the room lines are new and want a native
     speaker's read.

---

## V3-012 · 01/11/26 · House health, Alerts and People rebuilt natively; presence never inferred

**Status:** owner instruction CR-V3-19 (01/11/26), implemented on
`feature/casaray-v3-build`. DEVELOPMENT ONLY — NOT DEPLOYED. V3-011's main-light
question stays open: Parents' main light remains read-only until its load is
verified.

1. **Presence is only what a person entity says.** A silent person is "not
   reporting a location", never "away". "Nobody is home" is said only when
   all three people answered and none is home. V2 said it with two of three
   silent, so this is a departure, recorded. With some people silent and none
   home, V3 says "Nobody confirmed at home".
2. **`zone.home` is native on People.** Its migration row moved from
   `carried` to `native`. It sits beside the people, never as a bare tile,
   because a bare tile would show a 0 the people cannot back. A zero is
   stated only while all three people answer; otherwise it says "Not
   confirmed" and how many are silent. The zone-versus-people comparison
   is shown only while everyone answers. V2 said "agrees with the count by
   person" when both were 0 only because nobody answered.
3. **Alerts keeps V2's conditions, severities and thresholds** (batteries
   under 30%), as three lists plus a count strip built from the same check
   semantics, so they cannot disagree.
   - **The internet link and both emergency buttons are "only on is fine"**
     (V2: `state_not: on`). Off is "not connected"; dark or any unexpected
     state is "cannot be confirmed", raised as an alert and never folded
     into a count.
   - **Read-only:** V2 has no acknowledge, dismiss or quiet-hours action,
     and neither has V3; V2's note on why carries over.
4. **House health keeps the unavailable-entity count, with V2's caveat that
   it counts entities, not devices (CR-200).**
   - **Retained on the classic view:** `sensor.house_status`,
     `sensor.active_rooms_count` and `sensor.house_lights_on`. Their
     definitions are unverified (CR-213), and a summary count reads 0
     while its inputs are dark.
   - **Counted from verified entities instead:** lights on and rooms with
     movement, each stating what answered.
5. **New protected class: Home Assistant Core, Supervisor and OS updates.**
   They are read-only, and a tap opens the classic view. An install from a
   wall panel restarts the house system. The air-con firmware keeps V2's
   tile, as on Parents' room.
6. **Helper toggles are gated like switches.** `input_boolean.guest_mode`
   keeps V2's tile behaviour only as a manifest `controls` entry; removing it
   fails the gate.
7. **Frozen V2 claims reworded:** "Ai's iPhone location sensors are currently
   not reporting" and "Hue bridge not answering" (inferred from one spot).
   V3 states what the board shows: which phone reports distance, and which
   spot is offline.

---

## V3-011 · 01/11/26 · The room boards rebuilt natively; which room switches stay read-only

**Status:** owner instruction CR-V3-18 (01/11/26), implemented on
`feature/casaray-v3-build`. DEVELOPMENT ONLY — NOT DEPLOYED. Item 3 needs the
owner's review.

1. **Rooms index, Living room, Kitchen, Dining, Parents' room and Garage are
   native.** Every V2 entity of each is on its rebuild, apart from one:
   `zone.home`, which stays on the carried People board (item 4).
2. **The allowlist grew only by ordinary settings.** These are the kitchen and
   freezer plug LEDs, the fridge's express mode, the TV light-sensor setting
   and the pet feeder's video timestamp. Each keeps V2's exact tile behaviour.
3. **Read-only on native views, and gated as protected classes so the
   allowlist cannot unlock them.** Their V2 controls are unchanged on each
   room's classic subview:
   - the freezer plug and its auto-off: a critical load, and a mis-tap
     thaws it;
   - the coffee machine and both bench plugs, and their auto-offs: appliance
     power whose loads are not recorded;
   - every power-strip socket, and the board's child lock;
   - the Hue / dining sensors' motion and light sensing switches: turning one
     off silently stops what relies on it;
   - Climate React and the AC timer: air-con behaviour, V3-008;
   - the pet feeder's night-vision and detection-sensitivity selects, and
     the doorbell chime volume: camera and alerting.

   **Owner call:** the parents' main light is `switch.mainroomlight_switch_1`,
   a bulb-power switch. It is read-only, as on V3 Lighting, so native
   Parents' room has no light control; the control is one tap away on the
   classic view. If those bulbs are not smart bulbs, the switch is the light,
   and it should probably be a control.
4. **`zone.home` is not used on native Rooms.** A zone count reads 0 while the
   people it counts are dark, which would be a fabricated zero. Native Rooms
   counts the three people instead (what answered). The entity keeps its
   place on the carried People board, a verified migration row.
5. **Climate's "Air-con controls (classic)" button now opens
   `v2-parents-room`.** Parents' room is native with read-only HVAC, so V2's
   thermostat lives on its classic copy. This is the only change to an
   earlier native view, and it is tested.
6. **V2 statements that nothing measures were reworded, not copied.** V2
   Garage said "running normally" when the plug was on and not overloaded;
   V3 says just that. V2 Parents' room said the button-press entities "are
   currently not reporting", a claim frozen in text; V3 states what the page
   shows and does not show. The filter-reset button keeps V2's action and
   asks first, now in each language.

---

## V3-010 · 01/11/26 · Security, Network and two rooms rebuilt natively; how controls carry over

**Status:** owner instruction CR-V3-17 (01/11/26), implemented on
`feature/casaray-v3-build`. DEVELOPMENT ONLY — NOT DEPLOYED. Items 4 and 5
need the owner's review.

1. **Sirens are carried, not rebuilt.** The owner asked that siren operation
   be preserved exactly, so native Security holds the three V2 siren tiles
   copied byte for byte from the pinned baseline (`v2_verbatim`). Behaviour, read
   from the frontend source (`tile-card-helpers.ts`, fetched 01/11/26): tap
   opens details; an unset icon tap does nothing for `siren`. A siren sounds
   only from the control inside Home Assistant's own details dialog. No
   arming, disarming or emergency action was added. The gate refuses any
   siren tile that differs from V2's.
2. **Room switches keep V2's behaviour only from an allowlist.** V3-native
   views remain read-only for switches by default. The nine room device
   switches that V2 lets you toggle (desk plug, grow unit, printer plug and
   their LED / auto-off / auto-update settings) are listed in the manifest's
   `controls` and keep V2's exact tile behaviour. Everything else is refused.
3. **Protected classes stay read-only whatever the list says.** These are
   camera privacy, detection, notification, chime and alarm switches, and
   bulb-power wall switches. Their V2 controls stay on the classic subviews,
   which are unchanged and one tap away.
4. **Finding, for the owner:** on V2 Security today an icon tap on a camera
   privacy, detection or alert tile toggles it in one tap. The tiles set only
   `tap_action: more-info`, and Home Assistant toggles a `switch` on an unset
   icon tap. V2's note says the tiles open details. V3 does not reproduce
   this; the classic `v2-security` subview does, because it is V2 verbatim.
5. **Open against this file's Cameras and security rule ("any action that
   sounds one is confirmed").** Preserving V2 exactly means sounding a siren
   from the details dialog is not confirmed by CasaRay; Home Assistant's
   dialog has no confirmation step. Adding one means changing the siren
   tiles, so it is the owner's call.
6. **Sensor tiles open their details again.** A V3 reading without a
   navigation target now opens more-info on tap, as a V2 tile does (history;
   read-only domains only). This touched 37 tiles on the earlier native views.

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
