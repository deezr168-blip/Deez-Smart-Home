# Dashboard progression record

Authoritative record of `dashboards/deez_smart_home.yaml` batches. Newest
first. Append after every successful batch; commit with the change it
describes.

**Verification.** "Validated" means `scripts/ha_validate.sh` passed — YAML,
duplicate keys, templates, navigation, mass-damage, secrets. It does not mean
anything rendered. Visible results stay unconfirmed until checked on the live
dashboard; see `DASHBOARD_ISSUES.md` for status.

Deployment: a push to `ha-deploy` reaches the live dashboard within 15
minutes. Confirmed working 2026-08-29 (manual deploy of `e06d0ce` at
05:39:58; unattended path fixed separately — see `DEPLOY_AUTH.md`).

---

## Next recommended priorities

1. **UI-014** — Cameras: Front Door rendered twice, per-camera chips
   duplicate the tiles, previews cramped. Batch drafted, not yet applied.
2. **UI-012** — bilingual gap: 33 of 36 views are English-only while Home,
   Cameras and Lighting Studio respond to the toggle.
3. **UI-013** — Parents Room and Guest Room each stack a Mushroom media card
   and a native `media-control` for the same player. Confirm intent first.
4. iPad Command Center — 52 cards, never reviewed; nested 3-column grid in a
   third-width section.
5. Bills — nested 2-column grids; six bill subviews unreviewed.
6. **UI-011** — verify the Total Solar unit assumption against the live card.

---

## Batches

### `a5dc914` — Network: static labels stop impersonating live status
Area: `network` view. Purpose: three Infrastructure cards (Aqara M100, Hue
Bridge, HA Green) had no entity, no state and no tap action but rendered
identically to the two real status cards. No hub entity is exposed, so they
keep their inventory value with grey icons and an honest "no status entity"
secondary. The two live cards gained an unavailable branch, `entity`, and
more-info; both sections span the full width, 2-up and 3-up.
Validated: 36 views / 36 links / 0 broken, 275 templates, no entity loss.
Rendered up, down and not-reporting.
Expect: Network fills the iPad width in two full-width rows; the three
hardware cards are visibly grey and captioned; "Home Assistant Green" no
longer truncates.

### `df457e3` — Energy: five sections, two silent readouts guarded
Area: `energy` view. Purpose: 14 cards in one column with the four native
energy cards squeezed into half a page. Now header / Now / Today / Lifetime /
Charts, with the native cards at span 2. Fixed Total Solar (bare unguarded
`states()`, no unit) and Powerpal battery ("Battery unavailable%", and a
`| float(100)` sentinel that painted it green when silent).
Validated: 275 templates, 36/36 links. Rendered live, all-unavailable, and
flat-battery.
Expect: Energy reads as five labelled groups; the energy graphs are roughly
double their previous width.

### `2b80ac6` — deployment auth (not a dashboard change)
Diagnosis and host-side artifacts for the unattended `git fetch` failure.
See `DEPLOY_AUTH.md`. No dashboard file touched.

### `76da19b` — People & Locations rebuilt; the 9999 km sentinel removed
Area: `people-locations`, `people-locations-distance`, `ipad-command-center`.
Purpose: each of three people appeared four times on one page; the card grid
was three cards in a nested 3-column grid inside a half-width section (~83px
each). Now one card per person. All eight `distance(...) | float(9999)`
fallbacks replaced — a person with no GPS fix rendered "9999.0 km from home"
in confident red.
Validated: 273 templates. Rendered five location scenarios.
Expect: People page is one readable list plus a map/routes section; no
absurd distances.

### `34a92e7` — 16 of 19 top-level views were dead ends in kiosk mode
Area: every top-level view. Purpose: `kiosk_mode` hides sidebar and header,
so card tap actions are the only navigation. Only Cameras, Lighting Studio
and iPad Command Center could reach Home. Every top-level view now opens with
the same bilingual back chip; the three pre-existing buried Home chips were
removed so each view has exactly one route back.
Validated: navigation graph — all 36 views reachable from Home, 19/19
top-level views exactly one route back, nothing more than one hop away.
Expect: a back arrow reading Home at the top-left of every page.

### `e06d0ce` — camera subviews were dead ends; lighting pages read backwards
Area: six `camera-*` subviews, four lighting views. Purpose: camera subviews
had no back link under a hidden header. All four lighting views placed the
first section heading before the page title. Lighting Studio's page chips
also sat under the wrong heading; its weather chip was unrounded/unguarded.
Validated: 263 templates, 36/36 links.
Expect: a back chip above each camera; lighting pages open with their title.

### `3048e54` — "nothing here yet" placeholders cleared off room pages
Area: `ray-bedroom`, `guest-room`, `parents-room`, `kitchen`. Purpose: seven
markdown placeholders each under their own heading, filling two of Ray
Bedroom's four columns. Moved to a Known hardware gaps table in `README.md`.
Kitchen's third smart plug had no `name` and a one-off brightness/pink
card_mod unlike its two neighbours.
Validated: 263 templates.
Expect: Ray Bedroom and Guest Room are shorter and denser; the Kitchen plug
row reads Coffee / Kitchen Top / Kitchen Bottom.

### `bb05c7c` — Climate and Status get structure; four weather/date defects
Area: `climate`, `status`, Home hero, Lighting Studio. Purpose: two flat
single-column pages. Climate gained the full native thermostat (previously
only on the room page) plus an Outside reading; Status split into
Connectivity and Updates & Backups. Backup cards printed raw ISO timestamps.
House Pulse rendered "None°C" and an unrounded temperature. Weather read
"Partlycloudy".
Validated: 264 templates.
Expect: "Tue 25 Aug, 04:00" on backups; "21°C" on House Pulse.

### `315323f` — 20 cards asserting a state they cannot see
Area: room views, iPad Command Center, lights, climate, garage, kitchen.
Purpose: eleven two-branch assertions ("Open"/"Closed", "Motion"/"Clear",
"Normal") that reported reassurance on a dropout, plus nine raw
interpolations printing "unknown °C" mid-sentence.
Validated: rendered all 98 guarded templates with every entity forced to
`unavailable` and to `unknown` — no leak.
Expect: "Offline" in grey wherever a sensor is silent.

### `b1ef565` — Security rebuilt; false "Closed" fixed
Area: `security`. Purpose: three door cards claimed green "Closed" when the
sensor was unavailable. Header promised motion but the view had none. Now
Doors / Motion / Emergency & Cameras, with last-changed times.
Validated: 255 templates, three scenarios.
Expect: three labelled sections, door icons that open and close.

### `94a9b42` — views declaring more columns than they have sections
Area: 23 views. Purpose: `max_columns` higher than the number of sections
leaves empty grid tracks; seven views used a quarter of an iPad screen.
Validated: 244 templates, content untouched.
Expect: pages centre and fill instead of hugging one side.

### `b85949e` — one section-header treatment across every view
Area: `home`, `energy`, `bills`. Purpose: 46 native heading cards and 35
Mushroom title cards, mixed on 16 views. Every view now has at most one title
card (the page title); headings do the sections.
Validated: 244 templates.
Expect: consistent, smaller section headers.

### `018610b` — Home room cards get real, guarded, bilingual status
Area: Home Rooms section. Purpose: three tiles showed static placeholder text
("Fridge • power"), three interpolated unguarded sensors, none responded to
the language toggle.
Validated: rendered normal / Chinese / all-unavailable / all-alerting.
Expect: live temperatures and exception states on all seven room tiles.

### `119e1cd` — Home page cramped grids and duplicated tiles
Area: `home`. Purpose: nested 3- and 4-column grids inside a ~280px column
made tiles 60-85px wide. Lights-on appeared four times, doors four times,
solar four times; two tiles navigated to the page they were on. Replaced with
a full-width Today strip; Rooms went to span 2 at 2-up.
Validated: 236 templates, 36/36 links.
Expect: full-width Today strip; a 2-up room grid.
