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
| UI-029 | S4 | ~12 templates | Status fragments glued to a number or unit — "{{ d }} km away", "{{ n }} of 6 offline", "W • measured", "kWh this quarter". Chinese places the unit and qualifier differently, so translating the fragment alone yields broken grammar; each needs restructuring as a whole sentence per language. Left English on purpose rather than done badly. | OPEN |
| UI-027 | S3 | 52 `heading` cards | Native heading cards render straight onto the photograph with no surface and no text shadow, so section labels lose contrast over the bright horizon band. The 69 title and chip cards were fixed in the dashboard; headings need a theme-level rule and one live look. | OPEN |

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
| UI-028 | S4 | status text across all views | 57 guarded templates now carry bilingual status text — Offline, Sensor offline, Open/Closed, Motion/Clear, Occupied/Empty, Clean required, Up to date, Paid/Payment Outstanding and the rest. Number-glued fragments ("{{ d }} km away", "N of 6 offline", "W • measured") are deliberately still English; see UI-029. | `__SHA__` | FIXED — AWAITING LIVE VERIFICATION |
| UI-024 | S4 | `kitchen` | Third smart plug had no `name` (rendered its entity ID) and a one-off `brightness(200%)` pink/yellow card_mod unlike its two neighbours. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |

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
