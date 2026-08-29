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

---

## Open

| ID | Sev | View / component | Summary | Status |
|---|---|---|---|---|
| UI-011 | S3 | `energy` — Total Solar | Converted Wh→kWh to match its two sibling Primo sensors (`energy_day`, `energy_year`). If the Fronius total reports kWh directly the figure reads 1000× low. Needs one look at the live card. First seen `df457e3`. | OPEN |
| UI-027 | S3 | 52 `heading` cards | Native heading cards render straight onto the photograph with no surface and no text shadow, so section labels lose contrast over the bright horizon band. The 69 title and chip cards were fixed in the dashboard; headings need a theme-level rule and one live look. | FIXED — AWAITING LIVE VERIFICATION |

---

## Regression audit — 2026-08-29

Scheduled regression audit against `ha-deploy` HEAD `7f304ad`. Reviewed the 12
commits since the last recorded batch (`ae89134`..`f04a59f`: camera dedup,
iPad column retuning, glass-to-theme migration, Mushroom→Tile conversions,
the iPad Command Center rebuild, the last nested-`grid` dissolution, the
media-player dedup, and the three-commit bilingual pass) against the current
`dashboards/deez_smart_home.yaml`, plus a full-file sweep for the standing
regression categories (navigation, duplicate controls, reassuring false
status, unguarded numeric fallbacks, language-toggle consistency, iPad
layout). No previous `REG-` audit exists in this file, so this is the
baseline.

**Clean:** all 130 `navigate` targets resolve to one of the 36 declared view
paths; zero same-view duplicate entity controls; zero nested `grid` cards
remain (9b28fdb's dissolution is complete); all ~50 converted Tile cards
carry the features their Mushroom predecessors had (color-temp, cover
position); all 38 `float(0)` casts are properly guarded by a prior
unavailable/unknown/none check, and no `float(100)`/`float(9999)` sentinel
exists anywhere; every `max_columns` in the file is ≤2; the iPad Command
Center's 4-section structure matches its commit message with no drift; all
6 camera back-chips are bilingual; no inverted or scope-leaking `cn`
template variable found anywhere.

**Findings** (severity per task scale: CRITICAL / HIGH / MEDIUM / LOW):

| ID | Sev | View / component | Evidence | Suspected commit | Recommended action | Status |
|---|---|---|---|---|---|---|
| REG-001 | MEDIUM | `security` — 3 door cards (Living Room Door, Main/Parents Door, Back Door) | Lines 2192, 2200, 2208: `{{ ''Open'' if v == ''on'' else ''Closed'' }}` is bare English inside a template whose own "Sensor offline" fallback, one clause earlier in the same string, IS bilingual. Identical door-state logic elsewhere in the file (lines 647, 1059, 3694, 3705, 3716) already reads `''开启'' if cn else ''Open''` / `''关闭'' if cn else ''Closed''`. | `fa286de` (UI-028) — that commit's own message lists Open/Closed among the words it translated, but these three cards were missed. | Wrap the Open/Closed clause the same way as the other five instances in the file. | FIXED — AWAITING LIVE VERIFICATION |
| REG-002 | MEDIUM | `lights` quick-status chip + `cameras` quick-status chip ("Motion"/"Quiet") | Lines 3020-3027 (`lights`) and 1611-1620 (`cameras`): both aggregate several `binary_sensor.*_motion` entities with `select('eq','on') | count > 0`, no unavailable/unknown branch, and bare English text. If every watched sensor goes unavailable, `count` is 0 and the chip confidently shows "Quiet" — the exact reassuring-false-state anti-pattern this project's own process note calls out (root cause of UI-002/005/006/008/018/020). Also untranslated regardless of the Chinese toggle. | Predates tracked batch history — from the `61273b1` baseline sync (2026-08-25), before `d01e813` established tracking. Not introduced by the 12 audited commits, but never caught by the UI-006 guard pass or the three bilingual passes that touched nearly every other status chip in the file. | Add a `bad = [unavailable, unknown, none]` branch (grey/"—") ahead of the count check, and bilingual text, matching the treatment already used on the sibling per-sensor motion cards a few lines above line 3025. | FIXED — AWAITING LIVE VERIFICATION |
| REG-003 | MEDIUM | `home` — Network nav chip | Lines 547-548: `icon_color: '{{ ''green'' if is_state(''binary_sensor.eero_wan_status'',''on'') else ''red'' }}'` — two-branch only, no unavailable guard, so a dropped WAN sensor shows confident red rather than an unknown state. The dedicated `network` view fixed this exact pattern (`a5dc914`); this duplicate summary chip on `home` was missed. | Predates tracked batch history (`61273b1` baseline). Not fixed by `a5dc914`, which only touched the `network` view itself. | Add a third `grey` branch for unavailable/unknown, mirroring `a5dc914`'s treatment on the Network view. | FIXED — AWAITING LIVE VERIFICATION |
| REG-004 | LOW | `people-locations` — per-person markdown loop | Line 2872: the "at home" (🟢) branch renders the bare English word `home` regardless of the toggle, while the "away" branches on the same line are properly bilingual (`距家 {{ d }} 公里` / `{{ d }} km away`). | `f04a59f` — the commit whose stated purpose was closing exactly this class of gap (number/fragment-glued bilingual text) touched this template and missed the most common case. | Wrap as `{{ ''在家'' if cn else ''home'' }}`. | OPEN |
| REG-005 | LOW | `ipad-command-center` — WAN chip | Line 3662: the unavailable-state fallback renders literal `WAN —` in both languages, while the sibling Online/Offline branches on the same line are bilingual, and an equivalent unavailable case elsewhere in the file (~line 1623, "网络无数据") is translated. | `fa286de` | Cosmetic only. Translate the placeholder, or confirm with the owner that an untranslated dash is intentional. | OPEN |
| REG-006 | LOW | `home` — Energy tile secondary | Line 450: bare lowercase `offline` fallback sits untranslated next to `''太阳能'' if cn else ''Solar''` in the same template. | Originally introduced `a49ca72` (2026-08-25, pre-tracked-history); `f04a59f` edited this exact line for an unrelated word and left `offline` untouched. | Wrap as `{{ ''离线'' if cn else ''offline'' }}`. | OPEN |

No CRITICAL or HIGH findings. No broken navigation, no lost functionality,
no duplicate controls, no invalid subview references, no card-config or
grid-structure regressions, and no unguarded numeric sentinels were found in
the audited commits or the file as a whole.

---

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
| UI-027 | S3 | 52 native `heading` cards; `themes/deez_your_name.yaml` | Heading cards render with no `ha-card` wrapper, so `card-mod-card` never reached them — the 52 of them sat directly on the photograph with no text-shadow, unlike the 69 title/chip cards `cbec78b` already covered. Added a theme-level `card-mod-card-heading` rule (card-mod's per-card-type key) targeting `:host` with the same `text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` — one rule, not 52 per-card blocks, per the global-first design direction. | pending stamp | FIXED — AWAITING LIVE VERIFICATION |

---

## Verified

Confirmed by the owner on the live dashboard.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-025 | S2 | theme / background asset | Your Name background installed at `/local/your_name_night_sky.jpg` and the six-theme file at `/config/themes/`. | `88be895` | VERIFIED |
| UI-026 | S3 | all views | Per-card glass retired in favour of the theme surface. Precondition met — the background renders, which is only possible with the theme installed, so cards are drawing on the themed surface rather than the default opaque one. | `0f620f2` | VERIFIED |


---

## Process note

Recurring root cause across UI-002, UI-005, UI-006, UI-008, UI-018 and
UI-020: a numeric or boolean fallback used as a sentinel — `| float(0)`,
`| float(100)`, `| float(9999)`, or a two-branch `if is_state(...)` — which
renders a missing reading as a real, plausible, usually reassuring value.
Grep for these before adding any new card.
