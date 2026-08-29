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
| UI-012 | S4 | 33 of 36 views | English-only while Home, Cameras and Lighting Studio respond to `input_boolean.chinese_dashboard`. Switching to Chinese leaves most of the dashboard in English. | OPEN |
| UI-013 | S4 | `parents-room`, `guest-room` | Each stacks a Mushroom media card **and** a native `media-control` for the same player. Reads as a deliberate compact-plus-full pairing, so not changed. Confirm intent. | OPEN |
| UI-025 | S2 | theme / background asset | The Your Name background and the six-theme file cannot be installed from this environment — no `/config`, no route to the instance. Until the image is at `/config/www/your_name_night_sky.jpg` and the theme at `/config/themes/`, the retheme is invisible. `THEME_INSTALL.md` lists the 404/401 causes in the order they occur; the usual one is that `/local/` is registered at startup, so a `www/` folder created afterwards needs a restart. | OPEN |
| UI-015 | S4 | `ipad-command-center` | 52 cards, never reviewed. Nested 3-column grid inside a third-width section; no page title card. | OPEN |
| UI-016 | S4 | `bills` + six bill subviews | Nested 2-column grids; subviews never reviewed. | OPEN |

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
| UI-024 | S4 | `kitchen` | Third smart plug had no `name` (rendered its entity ID) and a one-off `brightness(200%)` pink/yellow card_mod unlike its two neighbours. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |

---

## Verified

None yet. Deployment was only confirmed working on 2026-08-29; no batch has
been visually confirmed on the live dashboard.

---

## Process note

Recurring root cause across UI-002, UI-005, UI-006, UI-008, UI-018 and
UI-020: a numeric or boolean fallback used as a sentinel — `| float(0)`,
`| float(100)`, `| float(9999)`, or a two-branch `if is_state(...)` — which
renders a missing reading as a real, plausible, usually reassuring value.
Grep for these before adding any new card.
