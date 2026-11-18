# CasaRay V3 — decision log

Dated design decisions for V3, newest first. Each entry says what was decided,
why, and whether the owner has approved it. V2 (`dashboards/casaray_v2.yaml`)
and `ha-deploy` are unaffected by everything here.

---

## V3-023 · 18/11/26 · PR #21: regression on the new head; top bar and Home, measured against the frontend's own rules

**Status:** owner brief (18/11/26): finish PR #21's validation round, then
the already-authorised Home visual items — large labelled navigation,
consistent alignment and spacing, readable Cantonese-first labels, compact
everyday controls. Same `feature/casaray-v3/weather-rubbish` branch, PR #21
still draft. DEVELOPMENT ONLY — NOT DEPLOYED; no merge, no live change.

1. **Regression, both heads, run here.** The earlier session's background
   result was not reachable from this container, so the full suite was run
   again: `56c0405` — **105 tests, 0 failures, exit 0** (512.7 s), clean tree.
   While it ran, a parallel session pushed `69b5164` (V3-022). That head was
   re-run in a clean worktree pinned to exactly `69b5164`: **105 tests,
   0 failures, exit 0** (604.5 s); `build_dashboard.py --check` current;
   `validate_dashboard.py` 1569 passed / 0 failed; `ha_validate.sh` PASSED.
2. **Built on V3-022, not redone.** V3-022 had already named every rail
   button, corrected `nav.climate` (氣候) and balanced Climate now. The
   preview it was judged in drew button labels at 14 px with side padding;
   the pinned frontend (20260826.7) draws them at `--ha-font-size-l`, 16 px,
   unpadded and clipped, never ellipsised. Corrected (`fd0b3df`, tooling
   only), the same build measured: four of six English rail labels clipped
   on a phone (2-unit buttons, ~55 px), "Cameras" clipped on the wall, the
   wall row two heights again (auto wordmark and clock, ~87 px, beside
   120 px buttons), and — with every button named — no visible mark on the
   current destination (V3 CLAUDE.md: "always marked in the navigation").
3. **Shared top bar** (`components.topbar`, every native view):
   - Header cell (6 units, 2 rows) + six named buttons at 3 units, 2 rows:
     one 120 px row on the wall (buttons ~132 px wide, up from ~77), two
     equal rows on a phone (~87 px, up from 55). Every cell one height.
   - Header: title, then the time above the `DD/MM/YY` date, then a short
     development marker, `app.dev_short` — in each locale an exact part of
     its own `app.dev_banner` (en "Not deployed", yue/zh-Hans 未部署,
     km កំណែអភិវឌ្ឍន៍), so no new vocabulary. Khmer uses the banner's
     first half because its second half wraps the line on a phone.
   - Current destination: inert, as before, and its icon tinted with the
     button card's own `color: accent` — read from the pinned source: it
     applies with no entity, and `accent` resolves to `var(--accent-color)`,
     which the installed CasaRay V3 theme maps to `--v3-accent` (amber,
     "selected"). No theme file change, so nothing to re-install.
   - `header_title` (optional view key, generator commit on its own): a
     shorter key for the header only. Used once, Rubbish collection (181 px
     of title in a 151 px cell); the page keeps its full name everywhere
     else. Without the key the output is unchanged.
4. **Home** (`src/casaray_v3/views/home.yaml`):
   - One tap's air-con slot keeps V3-007's role (state in words, a tap opens
     Climate) and now says which air-con it is: 「爸媽房冷氣機」 / "Parents'
     air-con", then mode and room temperature on one line, V3-007's own
     "Off · room 23.3°" form. It read only 「而家：冷氣」 before, and it
     overran its cell in Khmer. Climate now gets the same name line. The
     name reuses each catalogue's own words (爸媽房 + 冷氣機; V2's 父母房空调).
   - People at two rows, the vertical tile's minimum and the render's
     ~115 px; three rows left each card about half empty.
   - The "monitored" footnote moves inside the plugs card it qualifies.
   - Solar expected today moves from Right now to Energy now, beside Solar
     now and Solar today. **Departs from the 14/09 render**, which keeps it in
     its left column: with people compacted, it made Right now ~100 px
     taller than Who's home beside it. Still on Home (the V3-013 migration
     test only pins presence).
   - Shopping list at five rows: level with Rooms in Cantonese, the priority
     locale. Room lines are auto-height, so the list can only trade the gap
     between locales: English now has 43 px under Shopping, Cantonese 21 px.
   - More boards at 4 units: six across on the wall (two rows, not three),
     three on a phone (four rows, not six). At 6 units each icon drew
     ~100 px, the largest glyph on the page.
5. **Measured, simulated** (`preview_view.py --shots`, frontend geometry,
   approximated card interiors, fixture states; not a device):

   | | 69b5164 | V3-023 |
   |---|---|---|
   | Wall band holes, yue (rooms · right now · energy) | 43 · 77 · 36 px | 21 · 31 · 11 px |
   | Wall band holes, en | 21 · 77 · 14 px | 43 · 31 · 32 px |
   | Wall page height, yue / en | 2,644 / 2,644 px | 2,396 / 2,439 px |
   | Phone page height, yue / en | 4,738 / 4,803 px | 4,357 / 4,401 px |
   | Clipped labels on a phone, en / yue | 4 / 0 | 0 / 0 |
   | Top bar on all 20 native pages × 3 locales | not measured | wall: no fault; phone: only km Living room and Parents' room (title wraps) |

6. **Scope, checked:** in all four locales 28 views are byte-identical to
   `69b5164`, 19 native views differ only in the top bar section, and Home.
   Every changed card was rendered against the normal and the fully dark
   fixture in English and Cantonese: dark reads 「離線 · 冇數據」 / "Offline ·
   No data", never a stale temperature.
7. **Overlap with PR #16 (open, awaiting the owner, TASK-028):** PR #16 made
   the top bar icon-only to hold one row; this brief asks for named
   buttons, and V3-022 already named them. The two conflict in
   `components.topbar`; whichever merges second must choose. PR #16's equal
   room heights (rows 2) were not copied: by the frontend's row arithmetic
   (four 120 px rows against ~85 px auto lines) they would add roughly
   140 px on a phone, for alignment the Shopping list already gives in
   Cantonese. An estimate, not a measurement.
8. **Gated, so it cannot regress silently.** `band_problems()` skips the
   top bar by design ("not the spec's to size"), which is how V3-022's row
   passed. `validate_dashboard.py` now runs `topbar_problems()` on every
   native page in every locale (+80 checks, 1649 passed): whole rows on the
   wall and a phone, one cell height, every rail button named and at least
   3 units, and on a rail page exactly one inert, tinted button (none
   elsewhere). `tests/v3/test_topbar_home_v3_023.py` (12 tests) pins it,
   including a test that the gate rejects V3-022's bar on all three counts.
9. **Still open — needs a device or the owner:**
   - Nothing here was seen in Home Assistant. Typography, the amber icon,
     the header fit and every height above are from the pinned source and a
     simulation.
   - Khmer (draft, awaiting native review): the Living room and Parents'
     room titles wrap the header on a phone; "Automations" may clip in More
     boards on a phone; កំណែអភិវឌ្ឍន៍ fits by 4 px.
   - Tile states, the to-do card's "Add item" and the weather words are
     Home Assistant's own text, in the HA user's profile language, not this
     catalogue's. A Cantonese wall needs that user set to Chinese.
   - From the pinned sanitiser: markdown accepts `<ha-icon icon=…>`, so the
     room lines could carry the render's room icons (V3-013 listed this as
     unverified). Not done here.
   - The rubbish reminder automation proposal (V3-021) is still **not**
     checked by a Home Assistant schema validator.

## V3-022 · 18/11/26 · PR #21 full-suite validation; Home visual pass against the 14/09 wall render

**Status:** owner-relayed round, implemented on the same
`feature/casaray-v3/weather-rubbish` branch, same PR #21 (still draft, no
merge, no live changes). DEVELOPMENT ONLY — NOT DEPLOYED.

1. **Full-suite regression, run to completion.** `python3 -m unittest
   discover -s tests/v3` — **105 tests, 0 failures, exit 0, 679.990s**,
   against commit `56c0405` (the V3-021 review-fix commit). No file edits
   occurred between launching that run and `56c0405` landing, so the tree the
   suite tested is exactly that commit's tree. Not re-run a second time for
   this round's own changes below — a *targeted* `unittest discover` was run
   instead (same command, full `tests/v3` package, just not re-described as
   "the full-suite round" a second time) after the Home edits, and is logged
   under point 4.
2. **Home compared against the established mockup.** `docs/mockups/2026-09-14_wall_home.png`
   (= "CasaRay Wall Panel.pdf" p.1), the reference V3-013 already built Home
   against — no new mockup was supplied this round. Rendered the current
   build offline with `scripts/v3/preview_view.py` (real Home Assistant
   sections-view grid geometry at frontend 20260826.7, hand-approximated
   card interiors, fixture data — **not a Home Assistant screenshot**) at
   iPad landscape (1180×820) and iPhone (390×844) before any change, to
   compare against like for like rather than from memory.
3. **Four visual fixes, each tied to something the offline render actually
   showed, not a stylistic guess:**
   - **Large, labelled navigation.** The in-page rail (`topbar()`,
     `scripts/v3/components.py`) showed a name only on the current page's
     icon; the other five were unlabelled dots, and — because a
     `button` card draws one row icon-only and two rows once it shows a
     name (`ha_layout.py` `element_grid`) — the row was two different
     heights at once. Changed to `show_name=True` for every rail button, not
     just the current page's. Same six `columns: 2` slots (2×6=12, plus the
     12 the wordmark and clock already take = the full 24-unit band), now
     all two rows tall and all labelled.
   - **Cantonese-first label correction.** `nav.climate` in `yue.yaml` read
     "冷氣同天氣" ("air-con and weather", 5 characters) — materially longer
     than every sibling rail label (2–4 characters) and not what
     `climate.yaml`'s page actually is (climate/AC control; weather is its
     own separate page, CR-V3-20). Replaced with "氣候", the Traditional
     form of the term `zh-Hans.yaml` already uses for the same destination
     ("气候") — grepped the existing vocabulary first per `CLAUDE.md`, not
     invented.
   - **Climate now vs. Energy now, an oversized empty area.** The paired
     Band 8 sections packed to visibly different heights in the offline
     render — Energy now: 4 tiles + a note; Climate now: 1 markdown card +
     2 tiles — leaving a real gap under Climate now, the same "a lone short
     section leaves a hole beside it" failure mode `CLAUDE.md` documents for
     Home's own bands, just between two paired sections instead of within
     one. First attempt sized the two existing tiles to `columns: 4` to fit
     a third in one row; `validate_dashboard.py` correctly failed it — a
     native `tile` card's own minimum is `columns: 6`
     (`ha_layout.py` `element_grid`), so it always draws 6 wide regardless
     of what is asked, which would have shipped the same hole plus a
     "draws larger than grid_options" fault. Fixed instead with two more
     REAL readings at the tile's real minimum width: Dining
     (`sensor.living_room_living_room_temperature`, already used by the
     Dining room_tile above) and Ray's room
     (`sensor.presence_multi_sensor_fp300_temperature`, Ray Bedroom —
     reported `unavailable` in the 05/09 export per
     `docs/entity_inventory.md`'s "device is down" note, drawn honestly as
     "No data" rather than hidden or omitted). Four tiles at `columns: 6`
     now fill two full rows, matching Energy now's own 2×2 grid, with no
     invented filler.
   - **Consistent alignment**, largely a side effect of the nav-rail fix
     above (one row height instead of two) — no other card-alignment fault
     was found in the offline render; the "One tap" row's three action
     buttons and the `ac_summary` tile already draw at the same `rows: 2`.
4. **Re-validated after the change, not re-run blind.** `python3 scripts/v3/build_dashboard.py`
   (0 missing, 0 unexpected fallback deltas) → `python3 scripts/v3/validate_dashboard.py`
   (first attempt: 8 failures, exactly the `columns: 4` mistake above, on
   `home` in all 4 locales; after the fix: **1569 passed, 0 failed**, same 33
   pre-existing NOTEs) → `python3 -m unittest discover -s tests/v3` (targeted
   re-run, warranted by an actual change, not a blind repeat of point 1).
5. **Before/after previews delivered**, iPad landscape and iPhone, each
   pair composited side by side with `preview_view.py --side-by-side` and
   captioned in the image itself: *"Offline preview, not a Home Assistant
   screenshot: layout from Home Assistant's sections-view CSS (frontend
   20260826.7); card interiors approximated; fixture states, not live
   readings."* Icons render as plain dots in every shot — the preview's
   Material Design Icons folder (`--icons`) was not supplied this round;
   that is a limitation of this offline tool, not evidence about the
   dashboard, and is said so to the owner rather than left to look like a
   missing-icon bug.
6. **Outstanding, restated:** the rubbish reminder automation proposal
   (`docs/casaray-v3/proposals/rubbish_reminder_automation.yaml`, corrected
   in V3-021) is still **not** covered by an actual Home Assistant schema
   validator — no `hass` CLI, no reachable instance in this environment. It
   rests on documented HA automation-config behaviour only, and that gap
   does not close until there is a real instance to check it against.

---

## V3-021 · 18/11/26 · PR #21 review fixes (ChatGPT review on the V3-020 diff)

**Status:** owner-relayed review, implemented on the same
`feature/casaray-v3/weather-rubbish` branch, same PR #21 (still draft, no
merge). DEVELOPMENT ONLY — NOT DEPLOYED.

1. **Automation schema correction.** `docs/casaray-v3/proposals/rubbish_reminder_automation.yaml`
   used `enabled: false` on both automations. That is not a key the
   automation schema reads — Home Assistant does not reject an unknown key
   on an automation item, so this would have been silently ignored rather
   than erroring, and neither automation would actually have started off.
   Replaced with `initial_state: false`, the schema's real supported
   mechanism for a default-off YAML automation's startup/reload state. The
   header's explanation was rewritten to describe what that key actually
   does (startup/reload state only) versus the separate, independent
   `input_boolean` condition gate, rather than conflating the two.
   **Not covered by an actual HA schema validator** — this environment has
   no `hass` CLI and no reachable instance (`ha_validate.sh` section 8 is a
   standing SKIP for exactly this reason), so the correction rests on
   documented Home Assistant automation-config behaviour, not a live or
   CLI-run schema check. That check still needs to happen once there is a
   reachable instance, before this file is ever installed.
2. **Exact-equality rewrite of the "unchanged when unconfigured" test.**
   The original `test_empty_new_views_yields_unchanged_output` checked that
   every line of a `new_views`-stripped build appeared, in order, somewhere
   in the real build — a subsequence check. That passes even when a card
   was duplicated or an extra one silently inserted into an existing view,
   because every original line is still present, just with extras
   interleaved. Rewritten to parse both builds and compare per-view dict
   structures for exact equality, plus an independently-derived expected
   view count (from `len(v2_views) + len(native)` computed directly off
   `dashboards/casaray_v2.yaml` and the manifest, not from running the
   generator a second time). A new test,
   `test_exact_comparison_rejects_duplicated_or_inserted_card`, proves the
   new check has teeth: it duplicates one card in a cloned `home` view and
   confirms the same comparison helper raises, rather than merely asserting
   `!=` on hand-built dicts.
3. **Cantonese correction.** `weather.unverified_note` in `yue.yaml` had an
   actual bug — two English words ("answering") left embedded mid-sentence
   from an earlier draft — not a style issue. Fixed, and all three
   family-facing strings (`weather.unverified_note`, `rubbish.not_configured`,
   `rubbish.setup_path`) shortened across en/yue/km: what the household sees
   on the dashboard is now a short, plain sentence with no entity IDs, dates
   or technical reasoning in it. That detail — `weather.forecast_home`, the
   05/09/26 export, the entity contract — stays in this file, the view
   source comments and the automation proposal's header, which is where an
   implementer needs it and a family member reading the dashboard does not.
4. **Rubbish wording.** `rubbish.not_configured` changed to "Collection
   schedule not connected or verified." (and the matching yue/km
   translations), replacing a sentence that stated — in the user-facing
   string — that no entity exists, which is an inference from a single
   stale export, not a current fact a family-facing card should assert.
   The page's source-file comments still state plainly, as documentation,
   that no such entity was found in the 05/09/26 export; only the
   dashboard string itself was softened to not overclaim from that.
5. **`weather_detail()` no longer trusts a dark entity's leftover
   attributes.** It read `state_attr(entity, 'temperature')` /
   `...'humidity')` and showed them whenever the ATTRIBUTE value itself
   was numeric, on the documented assumption (`deg_expr()`'s own docstring)
   that Home Assistant always clears attributes once an entity goes
   unavailable/unknown. That is not guaranteed, and the condition word
   (`word_expr()`) was already gated on the entity's own state first,
   which temperature/humidity were not — an inconsistency between two
   readings on the same card. Both readings now check
   `states(entity) not in ['unavailable','unknown','none','']` before ever
   looking at the attribute, matching the pattern `word_expr()` already
   uses. Two new regression tests
   (`test_weather_detail_suppresses_stale_attributes_when_entity_dark` and
   its positive control) render the card with the entity `unavailable` but
   the attributes still carrying plausible numbers (21.3°, 55%) and confirm
   "No data" is shown for both — this is an offline Jinja render
   (`scripts/v3/render_check.py`), proof of what the template says, not
   proof of how the live card draws.

None of this changes scope, the entity contract, the more_boards padding
reasoning, or the task-register scope conflict recorded under V3-020 above —
those stand as written. Build/validate/test run again clean after these
fixes: `build_dashboard.py` (48 views × 4 locales, 0 missing), 
`validate_dashboard.py` (1569 passed, 0 failed), `python3 -m unittest
discover -s tests/v3` (full suite, including the rewritten and two new
cases), `ha_validate.sh` (VALIDATION PASSED, 8 sections).

## V3-020 · 18/11/26 · Generator extended for pages with no V2 equivalent; Weather and Rubbish Collection added

**Status:** owner instruction (18/11/26), implemented on
`feature/casaray-v3/weather-rubbish`, branched from `feature/casaray-v3-build`
at `777f836`. DEVELOPMENT ONLY — NOT DEPLOYED.

**Evidence-handling correction, carried forward from this point on.** The
owner corrected two framings in an earlier reply this same session: repository
deployment notes (e.g. `docs/casaray-v3/BUILD_STATUS.md` saying V3 "is not
registered, synced, reloaded or seen on any device") cannot disprove the
owner's own report that a V3 dashboard is live on a device — both are stated
as independently unverified from this offline session, never as one
disproving the other. Likewise `weather.forecast_home`'s presence, with
availability `ok`, in `docs/live/states_export_2026-09-05.txt` proves only
that it existed on 05/09/26; it is not evidence of today's availability or of
which forecast types it serves. Both caveats are written into
`src/casaray_v3/i18n/en.yaml`'s `weather.unverified_note` (and its yue/km
drafts) and onto the Weather page itself, not only here.

1. **Generator extended with a `new_views:` manifest key.** Until now
   `scripts/v3/build_dashboard.py` could only ever rebuild a path that already
   existed in `dashboards/casaray_v2.yaml` — a `native:` entry for a
   non-existent V2 path would silently never be emitted; there was no code
   path for a genuinely new page. `new_views:` (manifest.yaml) lists paths
   with no V2 equivalent; the build validates each one up front (must have a
   source file, must not collide with an existing V2 path, must not also be
   in `native:`, must not start with the reserved `v2-` prefix, no
   duplicates) and appends them last, per locale, so existing output is
   byte-identical when the key is empty or absent — proved by
   `tests/v3/test_new_views.py::test_empty_new_views_yields_unchanged_output`,
   which rebuilds with the key stripped and checks every line of the
   unconfigured build appears, in order, in the real one.
   `scripts/v3/validate_dashboard.py`'s safety/geometry/honesty gate filter
   (`native = [...]`) was broadened to include `new_views` paths too — a new
   page is not a lower-trust path through that gate; missing this would have
   silently excluded Weather and Rubbish Collection from every HVAC,
   protected-switch, native-card-type and band-packing check the existing
   boards get.
2. **Weather page** (`src/casaray_v3/views/weather.yaml`): current
   conditions and daily forecast only, both from `weather.forecast_home`
   (provisional — see the evidence-handling note above). HA core's fixed
   `ATTR_CONDITION_*` vocabulary is translated (`weather.cond.*`, 15 keys),
   not invented; `weather_detail()` (new in `scripts/v3/components.py`) reads
   unavailable/unknown as explicit branches rather than trusting the native
   `weather-forecast` card's own rendering. No radar, UV or any other reading
   — no entity exists for them. A build-time bug in this component double
   translated every condition word (pre-resolving the key, then passing the
   resolved text back into `word_expr()`, which translates its own values) —
   harmless in the rendered output but it logged 15 false "missing" keys per
   locale in the build report; fixed by passing the keys through untouched.
3. **Rubbish Collection page** (`src/casaray_v3/views/rubbish-collection.yaml`):
   no entity of any kind exists in the states export for a bin, a collection
   day or a council schedule, so the page states "not configured" and nothing
   else — no invented sensor ID, date, bin service or weekday. The future
   entity contract (one entity reporting the next collection date, optionally
   which bin) is documented on the page itself and is the same contract the
   proposed Home reminder (below) is written against.
4. **No conditional Home reminder was wired in.** `shown_when()` already
   exists and is the right component for "a card that appears only when valid
   data exists," but wiring it needs a real entity, and none exists. Rather
   than invent one or leave the requirement half-done, the entity contract is
   documented (point 3) and a reminder automation is drafted but not
   installed: `docs/casaray-v3/proposals/rubbish_reminder_automation.yaml`,
   two `time`-triggered automations (18:00 the evening before, 07:00 the
   collection morning, both evaluated in Home Assistant's own configured
   Australia/Melbourne timezone) gated by a default-off `input_boolean` and
   `enabled: false`, both reading the hypothetical
   `sensor.rubbish_collection_next_date` with unavailable/unknown treated as
   "do nothing." It lives under `docs/casaray-v3/`, not `design/casaray-v3/`
   or `packages/` — the latter is auto-included by Home Assistant's own
   `packages: !include_dir_named packages`, and a drafted-not-installed file
   has no business sitting in a directory that loads itself.
5. **Translations.** `en.yaml` is the reference catalogue (all keys land
   there). `yue.yaml` (priority — Traditional, HK Cantonese) and `km.yaml`
   got full draft translations for every new key, pending owner or
   native-speaker review — flagged here rather than presented as verified.
   `zh-Hans.yaml` was deliberately left to its existing English-fallback
   convention: that file's own header says it is "partial on purpose,"
   reusing only vocabulary already established in
   `dashboards/casaray_v2.yaml`, and V2 has no weather or rubbish-collection
   page to borrow a Simplified term from — inventing one would depart from
   the file's own stated convention, not follow it.
6. **Home's `more_boards` band needed four real links, not two, to stay
   valid — this was a real gate, not a style note.** Linking only the two new
   pages took the band from 8 items (7 existing + the V2 classic-copy link, a
   clean multiple of four) to 10, and `validate_dashboard.py`'s band-packing
   check — a literal simulation of Home Assistant's own CSS grid packing
   (`scripts/v3/ha_layout.py`, read from the pinned frontend source, the same
   method behind V3-013) — failed on all four locales with a genuine 24-cell
   hole in the last row. Rather than pad with an invented filler tile (a
   blank clickable-to-nothing button would itself be dishonest content), two
   more *real, already-existing* boards were added: `lighting` (which turned
   out to have no other Home navigation target at all — One tap only fires
   lighting scenes, it never opens the Lighting board itself, a genuine
   pre-existing gap this surfaced) and `rooms` (duplicates the "All rooms"
   room_tile the same way `alerts.yaml`'s own `more_boards` already duplicates
   links — security, energy, network — that Home also reaches elsewhere; an
   established pattern in this codebase, not an invented one). 11 items +
   classic_of = 12, a clean multiple of four; the validation gate now passes
   with 0 failures on all four locales.
7. **`entity_matrix()` left native-only, deliberately.** It is not extended
   to cover `kind: "new"` rows; Weather and Rubbish Collection have no V2
   migration to track (there is nothing to migrate from), so there is nothing
   for that report to usefully say about them. `view_inventory()` and the
   `unverified`/`dark_at_export` reporting, which are generic, do cover the
   two new pages correctly.
8. **Scope conflict surfaced, not resolved.** The owner's standing
   instruction to "update the established task register" names
   `docs/project-tasks/TASK_REGISTER.md` / `DECISION_HISTORY.md`, but
   `session-orient --scope` on this branch reports those paths outside
   `feature/casaray-v3/weather-rubbish`'s `MAY WRITE` scope. Per the root
   `CLAUDE.md`'s own Standing Rule ("a conflict between two governing
   instructions is not a safe ambiguity to resolve unilaterally"), this is
   reported to the owner rather than silently written to or silently
   skipped.

Build and validation, this batch: `python3 scripts/v3/build_dashboard.py`
(48 views × 4 locales, 0 fallback for en/yue/km, 0 missing keys for every
locale); `python3 scripts/v3/validate_dashboard.py` (1569 passed, 0 failed,
33 notes — all pre-existing `band_grid`-24 and dark-at-export notes, in the
same shape every other non-Home native view already carries);
`python3 -m unittest discover -s tests/v3` (full suite, including nine new
`tests/v3/test_new_views.py` cases); `bash scripts/ha_validate.sh`
(VALIDATION PASSED, 8 sections — the zh-Hans bilingual-heading warnings on
the two new pages are the same pre-existing WARN class every other zh-Hans
view already carries from its English-fallback convention, not a new one).

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
