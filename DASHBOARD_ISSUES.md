# Dashboard issue tracker

Authoritative regression and bug record for `dashboards/deez_smart_home.yaml`.
Check unresolved issues before planning a batch; fix high-severity
regressions before cosmetic work.

## Statuses

| Status | Meaning |
|---|---|
| `OPEN` | Identified, not yet worked on |
| `IN PROGRESS` | Being worked on now |
| `FIXED — AWAITING LIVE VERIFICATION` | Change committed and validated in the repository; the visible result has **not** been seen on the live dashboard |
| `VERIFIED` | Confirmed correct on the live Home Assistant frontend by the owner |

**A passing `ha_validate.sh` run never justifies `VERIFIED`.** This
environment cannot reach the instance, cannot check Lovelace schema and
cannot confirm an entity exists. Anything depending on the real frontend or
live entity data stays `FIXED — AWAITING LIVE VERIFICATION` until the owner
confirms it.

Severity: **S1** wrong/unsafe information · **S2** broken function or
navigation · **S3** layout or readability · **S4** polish.

ID series: `UI-` dashboard cards and views · `REG-` regressions and tracking
integrity · `BILL-` billing views and store · `DR-` design review ·
**`CFG-` Home Assistant configuration outside this repository** — a defect
seen on the live instance whose cause and fix live in HA's own config
(`.storage/`, an integration), not in any tracked file here. A `CFG-` item is
never fixed by a push to this branch, and never enters the verification
queue: the queue is for deployed changes awaiting a look, whereas a `CFG-`
item is awaiting a *diagnosis* the owner alone can perform.

---

## Open

| ID | Sev | View / component | Summary | Status |
|---|---|---|---|---|
| CFG-001 | S1 | Home Assistant **Energy dashboard configuration** (`.storage/energy`) — *not* `dashboards/deez_smart_home.yaml` | Energy → Totals reports Grid total **47.83 kWh** costing **A$437.60**, an implied **A$9.1491/kWh** and about **31.8×** the real tariff. Observed live by the owner 30 Aug 2026 while verifying `UI-011`. **Not a scaling bug — an accumulation read as a period total.** The one exposed monetary entity is named literally `sensor Cost` (`device_class: monetary`, `AUD`, no area) and read **451.1649** the same day; `451.1649 − 437.60 = 13.5649`, and A$13.5649 over 47.83 kWh is **0.2836 AUD/kWh** — an entirely ordinary rate, within 1.6% of the `SolarNet Grid import tariff` entity (0.2880 AUD/kWh) and 3.7% of the contracted peak rate (0.2734996 incl GST, per the `bill-electricity` view). So today's true cost is ≈A$13.56 sitting inside a wrong figure; the ≈A$437.60 on screen is the cost entity's accumulated total, not its increase across the selected period. That also explains why the factor is an odd 31.8× rather than a clean power of ten. **Leading hypothesis, stated as a hypothesis:** grid-consumption cost is set to *use an entity tracking the total costs*, pointed at a cumulative lifetime cost sensor whose statistic history effectively begins inside the current period, so its whole accumulated total was recorded as one jump and attributed to today. `451.16 ÷ 0.288 ≈ 1567 kWh` ≈ 33 days of import, consistent with a counter that started about a month ago. The sensor's name is itself a signal: HA auto-names a cost sensor `<source name> Cost`, so a bare `sensor Cost` means the source-name half resolved to nothing — consistent with a renamed source or a hand-made sensor. A `state_class: total` without `last_reset`, or a `total_increasing` sensor that reset, would produce similar symptoms by a different route. **Not diagnosable from here and deliberately not changed:** the cost source lives in `.storage/energy`, which this environment cannot read (`/config` unmounted, REST/WebSocket blocked — `DEPLOYMENT_BLOCKERS.md` Blockers 2/3), and the grid source entity itself is a Powerpal sensor, not exposed to Assist. Editing a production money figure blind is exactly what the owner's instruction ruled out. **Owner action to unblock:** Settings → Dashboards → Energy → Grid consumption → its cost setting. Report (1) which entity is the grid consumption source; (2) which cost option is selected — *do not track costs* / *static price* / *entity with the current price* / *entity tracking the total costs*; (3) if an entity is named, which one, plus its `state_class`, `device_class`, unit and current state from Developer Tools → States (≈451 if it is the `sensor Cost` above); (4) from Developer Tools → Statistics, whether that entity is flagged with a units/reset issue and when its history starts. **Nothing in this repository changes as part of the fix** — the Energy dashboard's configuration is not under version control here. Take a full backup first; HA backups are unavailable from this environment (`MAINTENANCE.md`). | OPEN — blocked on owner diagnosis |
| CFG-002 | S4 | Fronius / SolarNet integration — *not* `dashboards/deez_smart_home.yaml` | The `SolarNet Grid import tariff` entity reads **0.2880 AUD/kWh** while the contracted Home 365 Solar peak rate shown on the `bill-electricity` view is **0.2734996 incl GST** — a 1.45 c/kWh gap, about 5% on every cost figure derived from the entity. Possibly a deliberate rounded-up estimate, possibly stale from a previous plan; the current contract began 31 Jul 2026, recently enough for a stale rate to be plausible. Lives in the integration, not in this repository, so there is nothing to change on this branch. **Logged separately so it is not mistaken for part of `CFG-001`** — it is a ~5% difference, not a 31.8× one, and correcting it would not move A$437.60 anywhere near A$13. | OPEN — owner decision |
| REG-014 | LOW | `DASHBOARD_ISSUES.md` (tracking, not the dashboard YAML) | This file's own header describes it as "the authoritative regression and bug record for `dashboards/deez_smart_home.yaml`", but two genuine bug-class fixes to that file by the Billing routine are absent from it entirely: `BILL-001`'s account-number de-hardcoding (raw account-number literals replaced with guarded `input_text` references, commit `23c0301`) and `BILL-004` (ten `bills`/`bill-*` cards guarded against raw `unavailable`/`unknown` interpolation — the same UI-006/UI-030/UI-031 class already logged here for Main's fixes — commit `d570a82`). Both are correctly tracked in `DASHBOARD_BACKLOG.md`'s "Awaiting live verification" table and in `LIVE_VERIFICATION_QUEUE.md` (rows present, footer count accurate at 44/44), so nothing is unverifiable or lost — this is a completeness gap in one tracking file, not a live-dashboard defect or a lost fix. Same class of issue as `REG-012` (tracking upkeep falling behind a routine's own batch), this time in `DASHBOARD_ISSUES.md` itself rather than the verification queue. **Recommended corrective action:** Billing or the Daily Project Coordinator adds `BILL-001`/`BILL-004` entries to this file's fixed record (without reproducing the NMI/MIRN digit values — those remain correctly `BLOCKED` and untouched), or this file's header is amended to state that `BILL-*` fixes are tracked in `DASHBOARD_BACKLOG.md`/`BILLING_PROGRESS.md` instead, if that split is intentional. Not self-fixed — advisory only, per Regression Auditor's role (tracking-file writes are in scope, but this file's authority and structure belong to Billing/the Daily Project Coordinator, not the Auditor). | OPEN |

## Fixed — tracking only (no live dashboard component)

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-012 | MED | `LIVE_VERIFICATION_QUEUE.md` (tracking, not the dashboard YAML) | Verification-queue upkeep fell behind the REG-007..011 / UI-030 batch, in two ways: (1) `691689a` (UI-030) never added a queue row for the LetPot Grow Light guard; (2) the queue's own "N checks pending" footer undercounted its table. By the time this was reconciled, a later batch (`ccfb0c8`) had already corrected the footer arithmetic (39→42, matching the table) as a side effect of adding its own two rows, but the underlying `UI-030` row itself was still genuinely missing — grepping the queue for `LetPot`/`ray-bedroom`/`UI-030` still returned nothing. **Corrective action taken:** added the missing `UI-030` row to `LIVE_VERIFICATION_QUEUE.md` (Bills & rooms section) citing commit `691689a`, and updated the footer to 43. No dashboard YAML touched. | Daily Project Coordinator, this run | FIXED — no live check needed; the queue row's own presence is directly verifiable by inspection, not a rendered-dashboard question |

---

## False-safe-state sweep — 2026-08-30

A narrow re-sweep for the recurring false-safe-state class (see Process note)
beyond the REG-001..006 baseline, targeting cards that aggregate multiple
sensors — the per-sensor guards already fixed under REG-001..003 don't
automatically cover an aggregate that silently drops an unavailable sensor
from its count instead of flagging it. This was the exact same
three-door-sensor list (`m_contact_sensor_door`, `f_contact_sensor_door`,
`b_contact_sensor_door`) copy-pasted into five separate cards across three
views, of which only REG-003 (a different chip on the same list) had ever
been guarded. All five instances found and fixed; grepping the raw sensor
list afterward confirms none remain.

**Correction:** REG-008 was first logged against `ipad-command-center`. The
chip is actually on the `cameras` view's status chip row (line ~1590) — the
`ipad-command-center` view starts later in the file, at a different chip row
entirely (which turned out to have its own, distinct instance of the same
bug — see REG-011). Corrected below; `LIVE_VERIFICATION_QUEUE.md` was moved
to the right page section in the same commit as REG-009..011.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-007 | MED | `home` — House Pulse hero card | The door-open count and its icon_color silently dropped any door sensor reporting `unavailable`/`unknown`/`none` from the tally instead of flagging it, so all three sensors going offline showed a confident "0 open" and (with WAN up) a green icon — the same false-safe pattern REG-003 fixed on the sibling Network nav chip two cards away. Now surfaces "N door sensor(s) offline" / "N 个门传感器离线" and the icon falls back to grey rather than green when any door state is unknown. | `b058006` | FIXED — AWAITING LIVE VERIFICATION |
| REG-008 | MED | `cameras` — status chip row Doors chip | Same root cause as REG-007, worse: the chip had no unavailable guard at all and was still bare English ("N open"), unlike its two siblings in the same chip row (Motion, WAN) which were already guarded. All three door sensors offline showed "0 open" / green. Now matches the Motion chip's own guard convention: all-unknown → "Sensor offline" / grey, bilingual. **View corrected from an initial mislog against `ipad-command-center` — see note above.** | `b058006` | FIXED — AWAITING LIVE VERIFICATION |
| REG-009 | MED | `home` — quick-control chip row Doors chip | Same unguarded template as REG-008, also still bare English, on the `home` view's own quick-control chip row (separate card from the House Pulse hero). Fixed to the same guarded/bilingual convention. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |
| REG-010 | MED | `home` — Rooms section Security card | The "N doors open • motion monitoring" summary silently dropped unavailable door sensors from its count/colour. Now appends "N unknown" / "N 离线" when any door sensor is unavailable and the icon falls back to grey instead of a confident green. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |
| REG-011 | MED | `ipad-command-center` — Home Pulse chip row Doors chip | The genuine `ipad-command-center` instance (see correction note): unguarded and still bare English, sitting beside an already-guarded WAN chip (REG-005) in the same row. Fixed to the same guarded/bilingual convention as REG-008/009. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |

---

## False-safe + raw-interpolation sweep — 2026-08-30 (person chip, Climate summary, Roller Shade, Lighting Modes)

A fresh pass over the areas the previous run's `LIVE_VERIFICATION_QUEUE.md`
note flagged as next-plausible (raw-interpolation class beyond `ray-bedroom`).
The six `camera-*` subviews themselves turned out clean — each is just a back
chip plus a `webrtc-camera` card, no template content to guard. Widening the
grep for raw `{{ states(...) }}` interpolation elsewhere in the file (outside
Billing's `bill-*` views, which are out of scope) turned up three unguarded
instances, plus one genuine false-safe finding caught while checking the
same `lighting-modes` view.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-031 | S4 | `home` quick-control chip row (Person); `home` Rooms grid (Climate card); `light-ray-bedroom` (Roller Shade card) | Same raw-interpolation class as UI-006/UI-030: three cards printed a raw `states(...)` value with no guard and no bilingual text — the `home` view's Person chip showed the literal `person.raymond_du` state string (`home`/`not_home`, or `unavailable` verbatim) instead of the distance-based bilingual convention already used on `people-locations` and `ipad-command-center`; the `home` Rooms-grid Climate card printed the raw lowercase HVAC mode (or `unavailable`) instead of the guarded/title-cased convention already used two cards away (Parents Room, line ~375); the Roller Shade card on `light-ray-bedroom` printed the raw cover state and an unguarded battery percentage that would render `unavailable%` exactly like the Powerpal battery card UI-020 already fixed. All three now use the guards/bilingual conventions already established elsewhere in the same file for the same entities. | `ccfb0c8` | FIXED — AWAITING LIVE VERIFICATION |
| REG-013 | MED | `lighting-modes` — Current State section (Living Room, Ray Bedroom, Dining cards) | The recurring false-safe-state class: each card read `'Off' if is_state(light,'off') else (<percent> if brightness is not none else 'On')`. An `unavailable`/`unknown` light is neither `off` nor has a brightness attribute, so it fell into the final `else` and confidently asserted **"On"** — the exact same class CLAUDE.md's process note warns about ("never let a card assert a reassuring state it cannot see"), just for a light instead of a door/motion sensor. Now shows bilingual "Offline"/"离线" when the light is unavailable/unknown, ahead of the existing off/percentage branches. Icon colour was already safe (defaults to grey unless confirmed `on`) — text was the only false-safe surface. | `ccfb0c8` | FIXED — AWAITING LIVE VERIFICATION |

---

## Regression audit — 2026-08-29

Baseline audit against `ha-deploy` HEAD `7f304ad`, covering the 12 commits
`ae89134`..`f04a59f` plus a full-file sweep for the standing regression
categories. **All six findings are now fixed.** Full evidence, per-finding
suspected commits and recommended actions are preserved in
`archive/DASHBOARD_ISSUES_ARCHIVE.md`.

Clean at audit time: all 130 `navigate` targets resolved; no same-view
duplicate entity controls; no nested `grid` cards; converted Tile cards kept
their Mushroom features; all 38 `float(0)` casts guarded and no
`float(100)`/`float(9999)` sentinel anywhere; every `max_columns` ≤2; all six
camera back-chips bilingual.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-001 | MED | `security` — 3 door cards | Bare-English `Open`/`Closed` inside an otherwise-bilingual template. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-002 | MED | `lights` + `cameras` motion chips | Motion-aggregate chips showed a confident "Quiet" when every watched sensor was unavailable — the project's recurring false-safe-state class. Also untranslated. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-003 | MED | `home` — Network nav chip | Two-branch green/red with no unavailable guard, so a dropped WAN sensor showed confident red. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-004 | LOW | `people-locations` | The "at home" branch rendered bare English `home` while its sibling away-branches were bilingual. | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| REG-005 | LOW | `ipad-command-center` — WAN chip | Unavailable fallback rendered literal `WAN —` in both languages. Fix also changed the English text to "WAN not reporting" to match an equivalent case elsewhere — **owner may want the dash kept; not decided.** | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| REG-006 | LOW | `home` — Energy tile | Bare lowercase `offline` fallback beside an already-bilingual "Solar"/"太阳能". | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |

## Fixed — awaiting live verification

Every entry below is committed, validated and pushed to `ha-deploy`. None has
been seen rendered.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-001 | S3 | `home` | Nested 3/4-column grids inside a ~280px section made tiles 60-85px wide; lights/doors/solar each duplicated four times; two tiles navigated to the page they were already on. | `119e1cd` | FIXED — AWAITING LIVE VERIFICATION |
| UI-002 | S1 | `home` room tiles | Three tiles showed static text that never changed; three interpolated unguarded sensors ("unknown °C", "Freezer unavailable W"). | `018610b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-003 | S3 | 16 views | Two different section-header treatments (46 heading cards vs 35 Mushroom title cards) mixed within single views. | `b85949e` | FIXED — AWAITING LIVE VERIFICATION |
| UI-004 | S3 | 23 views | `max_columns` exceeded the section count, leaving empty grid tracks; seven views used a quarter of the iPad screen. | `94a9b42` | FIXED — AWAITING LIVE VERIFICATION |
| UI-005 | S1 | `security` doors | `'Open' if is_state(...) else 'Closed'` — an unavailable contact sensor reported a confident green "Closed" on the security page. | `b1ef565` | FIXED — AWAITING LIVE VERIFICATION |
| UI-006 | S1 | 20 cards across 8 views | Same class as UI-005: "Clear", "Normal", "Door Closed", "Up to date" asserted on dropout, incl. the three iPad Command Center door cards. Nine raw interpolations printed state names mid-sentence. | `315323f` | FIXED — AWAITING LIVE VERIFICATION |
| UI-007 | S3 | `climate`, `status` | Flat single-column pages; Climate lacked the full thermostat for the house's only climate device. | `bb05c7c` | FIXED — AWAITING LIVE VERIFICATION |
| UI-008 | S1 | `status` backups, Home hero, weather | Raw ISO timestamps ("Last success 2026-08-25T04:00:12+00:00"); House Pulse rendered "None°C" and an unrounded temperature; conditions read "Partlycloudy". | `bb05c7c` | FIXED — AWAITING LIVE VERIFICATION |
| UI-009 | S2 | six `camera-*` subviews | No back link. `kiosk_mode` hides the header, so a full-screen camera had no exit. | `e06d0ce` | FIXED — AWAITING LIVE VERIFICATION |
| UI-010 | S3 | 4 lighting views | Section heading card placed before the page title, so each page opened with a section label. | `e06d0ce` | FIXED — AWAITING LIVE VERIFICATION |
| UI-017 | S2 | 16 of 19 top-level views | No route back to Home under kiosk mode; tapping a room stranded you there. | `34a92e7` | FIXED — AWAITING LIVE VERIFICATION |
| UI-018 | S1 | `people-locations`, `people-locations-distance`, `ipad-command-center` | `distance(...) \| float(9999)` rendered "9999.0 km from home" in red for anyone without a GPS fix. Eight occurrences. | `76da19b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-019 | S3 | `people-locations` | Each of three people listed four times on one page; person cards ~83px wide in a nested 3-column grid. | `76da19b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-020 | S1 | `energy` | Total Solar was a bare unguarded `states()` with no unit; Powerpal battery read "Battery unavailable%" and its `\| float(100)` sentinel painted it green when silent. | `df457e3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-021 | S3 | `energy` | 14 cards in one column; the four native energy cards squeezed into half a page. | `df457e3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-022 | S1 | `network` | Three Infrastructure cards with no entity, no state and no tap action rendered identically to real status cards, so three of five could never say anything but "fine". | `a5dc914` | FIXED — AWAITING LIVE VERIFICATION |
| UI-023 | S3 | room pages | Seven "nothing here yet" markdown placeholders under their own headings, filling two of Ray Bedroom's four columns. Moved to `README.md`. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |
| UI-014 | S3 | `cameras` | Front Door rendered twice (picture-entity plus a template card doing the same navigation); five per-camera chips duplicated the tiles above them; the "All Cameras" heading sat over a grid excluding Front Door; a 2-up nested grid in a third-width section gave ~185px previews. | `ae89134` | FIXED — AWAITING LIVE VERIFICATION |
| UI-015 | S3 | `ipad-command-center` | 52 cards, three nested grids inside half-width sections, and a six-chip camera status row sitting directly above the six camera tiles it described. Two load chips were unguarded. | `99a77b4` | FIXED — AWAITING LIVE VERIFICATION |
| UI-016 | S3 | `bills`, `light-living-room`, `lighting-modes` | The last four nested `grid` cards sizing themselves inside half-width sections. Dissolved into native `grid_options`; the dashboard now has none. The six bill subviews are reviewed and need no layout change — one section, one column each. | `9b28fdb` | FIXED — AWAITING LIVE VERIFICATION |
| UI-013 | S4 | `parents-room`, `guest-room` | Each stacked a Mushroom media card and a native `media-control` for the same player. The native card is a superset — artwork, transport, volume and power — so the Mushroom card was removed from both. The four Mushroom media cards that are the ONLY card for their player were left alone. The parents-room climate pair was also left: there the compact card is half of a deliberate 2-up summary row, not a duplicate. | `56c7656` | FIXED — AWAITING LIVE VERIFICATION |
| UI-012 | S4 | all 36 views | Only Home, Cameras and Lighting Studio responded to the language toggle; switching to Chinese left 33 views in English. The navigation-level chrome — 23 page titles, 26 subtitles, 55 section headings, 10 entities-card titles and the six camera back chips — is now bilingual. Every view responds. Device names and per-card status text are deliberately still English; see UI-028. | `f4e7ec3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-028 | S4 | status text across all views | 57 guarded templates now carry bilingual status text — Offline, Sensor offline, Open/Closed, Motion/Clear, Occupied/Empty, Clean required, Up to date, Paid/Payment Outstanding and the rest. Number-glued fragments ("{{ d }} km away", "N of 6 offline", "W • measured") are deliberately still English; see UI-029. | `fa286de` | FIXED — AWAITING LIVE VERIFICATION |
| UI-029 | S4 | ~34 templates | Number- and unit-glued status fragments. The position-stable ones ("Fridge {{ t }}°C", "W • measured", "Paid • $") were fragment-swapped; the four that Chinese genuinely reorders ("{{ d }} km away", "km from home", "N of 6 offline", the offline-camera join) were rewritten as whole per-language clauses. | `f04a59f` | FIXED — AWAITING LIVE VERIFICATION |
| UI-024 | S4 | `kitchen` | Third smart plug had no `name` (rendered its entity ID) and a one-off `brightness(200%)` pink/yellow card_mod unlike its two neighbours. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |
| UI-027 | S3 | 52 native `heading` cards; `themes/deez_your_name.yaml` | Heading cards render with no `ha-card` wrapper, so `card-mod-card` never reached them — the 52 of them sat directly on the photograph with no text-shadow, unlike the 69 title/chip cards `cbec78b` already covered. Added a theme-level `card-mod-card-heading` rule (card-mod's per-card-type key) targeting `:host` with the same `text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` — one rule, not 52 per-card blocks, per the global-first design direction. | `9926233` | FIXED — AWAITING LIVE VERIFICATION |
| BILING-RESID | S4 | `people-locations`, `ipad-command-center`, `home` Energy tile | Closes REG-004/005/006: the "at home" branch of the per-person markdown loop, the WAN chip's unavailable fallback, and the Energy tile's offline fallback were the last three bare-English fragments left over from the UI-012 -> UI-028 -> UI-029 bilingual sequence. | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-030 | S4 | `ray-bedroom` — LetPot Grow Light card | Raw `states()` interpolation for `select.lph_se_dcd9_light_mode` / `..._light_brightness` printed the literal string "unavailable" mid-sentence with no guard at all — the same raw-interpolation class UI-006 fixed elsewhere. Found while widening the REG-007..011 aggregate sweep to `climate`/`network`/`status`/room views (that sweep itself found no new false-safe instances — clean). Now falls back to an em dash per field, or bilingual "Offline"/"离线" when both underlying selects are unavailable. | `691689a` | FIXED — AWAITING LIVE VERIFICATION |

---

## Verified

Confirmed by the owner on the live dashboard.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-025 | S2 | theme / background asset | Your Name background installed at `/local/your_name_night_sky.jpg` and the six-theme file at `/config/themes/`. | `88be895` | VERIFIED |
| UI-026 | S3 | all views | Per-card glass retired in favour of the theme surface. Precondition met — the background renders, which is only possible with the theme installed, so cards are drawing on the themed surface rather than the default opaque one. | `0f620f2` | VERIFIED |
| UI-011 | S3 | `energy` — Total Solar | Wh→kWh conversion confirmed correct. Owner read the native HA Energy dashboard live on 30 Aug 2026: Solar 16 kWh, Grid 47.83 kWh, Home consumption 63.83 kWh — `16 + 47.83 = 63.83` exactly — with the Solar production chart and the Energy Distribution card independently showing 16 kWh, so the figure held across three renderings of the same statistic rather than one card's formatting. Corroborated from this environment the same day by a read-only entity query: `Primo 5.0-1 (1) Energy day` = **16558 Wh** (`unit_of_measurement: Wh`) = 16.56 kWh, matching. The sibling `Total energy` sensor reads 48425900 Wh, which the card's `/1000` renders as 48425.9 kWh — the same order of magnitude as `Energy year` (4588108 Wh → 4588.1 kWh) and larger than it, as a lifetime counter must be. The feared 1000×-low reading does not occur. **Scope, stated precisely:** the owner's evidence is from the **native HA Energy dashboard**. It settles the Wh→kWh question this issue was about, and the entity read above independently confirms the card's own arithmetic. It does **not** close `UI-020`, a different check on the same card (that the readout carries a unit, and that the Powerpal battery is guarded), which stays `PENDING` in the queue. | `df457e3` | VERIFIED |


---

## Process note

Recurring root cause across UI-002, UI-005, UI-006, UI-008, UI-018 and
UI-020: a numeric or boolean fallback used as a sentinel — `| float(0)`,
`| float(100)`, `| float(9999)`, or a two-branch `if is_state(...)` — which
renders a missing reading as a real, plausible, usually reassuring value.
Grep for these before adding any new card.
