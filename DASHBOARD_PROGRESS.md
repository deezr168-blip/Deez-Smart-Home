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

**Superseded.** The authoritative work queue is now `DASHBOARD_BACKLOG.md`,
selected under the priority model and queue-selection rules in
`PROJECT_STATE.md`. This section previously listed seven items, four of which
had already shipped (UI-012 in `f4e7ec3`, UI-013 in `56c7656`, and the nested
`bills` and iPad grids in `9b28fdb`), so it is no longer maintained here.
Nothing below this line changes: the batch record is history and stays intact.

---

## Batches

### `PENDING` — three reassuring/untranslated regressions closed (REG-001/002/003)
Area: `security` (3 door cards), `lights` + `cameras` (motion-aggregate quick
chips), `home` (Network nav chip). Purpose: closes the three MEDIUM findings
from the 2026-08-29 regression audit, queued for Main.
REG-001: the three door cards' Open/Closed clause was bare English inside an
otherwise-bilingual template — the same gap `fa286de` closed on five other
door cards but missed here. Now reads `开启`/`关闭` when the toggle is on,
matching the existing pattern elsewhere in the file byte-for-byte.
REG-002: the `lights` (2-sensor) and `cameras` (4-sensor) motion-aggregate
chips had no unavailable branch, so a dropout showed a confident "Quiet" —
this project's own recurring false-safe-state root cause (see Process note).
Both now report "Sensor offline" when every watched sensor in the group is
unavailable/unknown/none, honest "Motion"/"Quiet" otherwise, and bilingual
either way.
REG-003: the `home` page's own Network nav chip was a bare two-branch
`green`/`red`, unlike the dedicated `network` view which already guards this
exact sensor (`a5dc914`). Added the same third grey branch.
Verified each new branch by rendering the extracted Jinja logic standalone
across all state combinations (on/off/unavailable/unknown/none, both
languages) rather than by inspection alone: REG-001's ternary reproduces the
existing five-instance pattern exactly on English; REG-002's guard confirmed
to report offline only when *every* sensor in its group is unavailable, and
real Motion/Quiet otherwise — never "Quiet" from a dropout.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss.
Expect: no visible change when sensors are healthy; a dropped door/motion/WAN
sensor now shows grey "offline" instead of a confident wrong colour, in
either language.

### `f04a59f` — the number-glued status fragments (UI-029)
Area: 34 templates across home, kitchen, garage, energy, cameras, climate,
status, people-locations, lights, light-ray-bedroom, ipad-command-center and
bills. Purpose: closes the bilingual work. These were left out of the previous
pass on purpose — a fragment glued to a number cannot be swapped word for word
when the target language orders it differently.
Split by whether Chinese keeps the English position:
  - Position-stable, so fragment-swapped: "Fridge {{ t }}°C" -> 冰箱,
    "W • measured" -> W • 实测, "Paid • $" -> 已付 • $, "Battery {{ b }}%" ->
    电量, "Never"/"Not scheduled" -> 从未/未安排, the three energy
    "Unavailable • X not reporting" sentences, and 20 more.
  - Genuinely reordered, so rewritten as a whole clause per language:
    "{{ d }} km away" and "km from home" become 距家 {{ d }} 公里 — the
    qualifier moves in front of the value; "{{ n }} of 6 offline" becomes
    {{ n }}/6 离线; and the offline-camera list joins on 、 rather than a
    comma, which is the correct Chinese list separator.
One real gap was caught by rendering rather than reading: the iPad presence
card printed "Home" in both languages, because that branch had never been in
any phrase map. Fixed.
Verified the same way as the previous pass and with distance added to the
matrix: all 257 templates rendered from HEAD and from the new file across five
entity states x four distances. English output difference after whitespace
normalisation: zero. Every edited template produces Chinese in at least one
reachable branch.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss.
Expect: no English left in card status text when the toggle is on, and the
Chinese reads in Chinese order rather than transliterated English order.

### `fa286de` — status text answers the toggle too (UI-028)
Area: 58 guarded templates across every view. Purpose: the chrome pass made
titles and headings bilingual, leaving the actual state words in English —
a Chinese dashboard reading "Sensor offline" under a Chinese heading.
39 whole-branch phrases translated: Offline, Sensor offline, Open/Closed,
Motion/Clear, Motion now, Occupied/Empty, Clean required/Clean, Connected/
Disconnected, Up to date/Update available, Overload/Normal, Shade open/
closed, Location unknown, Paid/Payment Outstanding, Battery not reporting,
and the Unavailable/Not reporting family.
Method matters here, because these are the templates carrying this branch's
correctness work. Each template was tokenised on its Jinja tags and only the
literal text BETWEEN tags was rewritten — no condition, no guard, no entity
reference was touched. A `cn` variable is prepended only where one was not
already defined.
Verified by differential rendering rather than inspection: every one of the
257 templates was rendered from HEAD and from the new file across five entity
states, and the English output compared. After whitespace normalisation the
difference is zero — the 20 raw diffs were newline-versus-space inside folded
scalars, which collapse identically in HTML. The guards behave exactly as
before; only a new Chinese branch was added.
One apparent failure was chased down rather than waved through: a shade card
looked untranslated because the test never exercised the cover's open/closed
states. It renders Chinese correctly; its "Shade —" fallback was the only
real gap and is translated now.
Not done, deliberately, and logged as UI-029: fragments glued to a number or
unit — "{{ d }} km away", "N of 6 offline", "W • measured". Chinese orders
the unit and qualifier differently, so translating the fragment alone
produces broken grammar. Those need whole-sentence restructuring per
language.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss.
Expect: with the toggle on, card status text reads Chinese as well as the
headings above it.

### `f4e7ec3` — every view now answers the language toggle (UI-012)
Area: all 36 views. Purpose: the Chinese toggle existed on Home, Cameras and
Lighting Studio and nowhere else, so switching language left 33 views in
English — the toggle looked broken rather than partial.
Translated, 120 strings: 23 page titles, 26 subtitles, 55 section headings,
10 `entities` card titles and the six camera-subview back chips. Every one of
the 36 views now contains Chinese; CJK characters go from 171 to 742.
Scope was chosen, not accidental. Brand and product names stay as they are —
LetPot, Hue, Pogo, EnergyAustralia, United Energy, Multinet, South East
Water, VicRoads, Home 365 — and so do device names, which is how bilingual
Home Assistant dashboards normally read: the integration names the device,
the dashboard names the room. The six webrtc camera overlays keep their
location label for the same reason.
Verified by rendering every bilingual chrome string in both languages and
asserting the Chinese branch actually contains Chinese, with the brand-name
exceptions allowed for explicitly.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss.
Expect: flipping the toggle changes every page title, section heading and
subtitle on every view instead of three.

### `56c7656` — two media players stop being controlled twice (UI-013)
Area: `parents-room`, `guest-room`. Purpose: each stacked a Mushroom media
card directly above a native `media-control` for the same player. Checked
rather than assumed before removing anything: the native card carries
artwork, transport, volume and a power button, so it is a strict superset of
what each Mushroom card offered — `media_controls: [on_off]` on the Parents
TV, media info plus volume on Pogo. Removing them costs no control.
Deliberately not touched, because there the second card is not a duplicate:
  - the four Mushroom media cards in living-room, dining and media are the
    only card for their player;
  - the parents-room climate pair, where the compact Mushroom card is one
    half of a 2-up "Temperature | Lights" summary row and the thermostat
    below is the detailed control. Removing the compact card would leave a
    heading with nothing under it.
Validated: 264 templates, 36/36 links, 0 broken, no entity loss.
Expect: both rooms lose a redundant player card; every media player still has
a full control card.

### `9b28fdb` — the last nested grids are gone (UI-016)
Area: `bills` (2), `light-living-room` (1), `lighting-modes` (1). Purpose:
finishes a thread running through this whole branch. A `grid` card nested in
a section sizes its children against a width it cannot measure, which is what
made the Home tiles 60px and the camera previews 185px earlier. These four
were the last of them.
Each dissolved into its children carrying native `grid_options: columns: 6` —
the same two-across result, but decided by Home Assistant's section grid
rather than by a card guessing inside a column. The dashboard now contains
zero nested grid cards, down from eleven when this branch started.
The moved cards were re-serialised, so the diff is large. Verified that this
was purely mechanical: all 264 Jinja templates compare identical before and
after, none changed, none appeared, none vanished.
The six bill subviews were reviewed at the same time and need no layout
change — one section and one column each is already right for a plan detail
page.
Validated: 264 templates, 36/36 links, 0 broken, no entity loss.
Expect: no visible change to how these three pages are arranged; they are
laid out by the same rules as every other view now instead of by a nested
card.

### `99a77b4` — the wall panel itself: iPad Command Center rebuilt (UI-015)
Area: `ipad-command-center`. Purpose: the view the wall iPad actually runs was
the last one never reviewed — 52 cards, three nested `grid` cards inside
half-width sections, and the heaviest single section on the dashboard.
Structure, four sections instead of three, every row filling the width:
  Home Pulse   span 2  back bar, heading, one status strip
  Doors/Lights/Climate   left column
  Control Centre / Active Loads / Go To   right column
  Live Cameras span 2  six previews 3-across at grid_options columns 4
All three nested grids are gone, replaced by native `grid_options` on the
cards themselves, so Home Assistant sizes them rather than a grid card
guessing inside a column it cannot measure.
Duplication removed: a six-chip camera status row sat directly above the six
camera tiles it described. It is now one chip in the summary strip that names
what is down — "North Wall, East Wall offline" — degrading to "N of 6
offline" past two. Same treatment the Cameras page got, so the two views
agree.
Two unguarded readouts fixed: the Ray and Freezer load chips interpolated
their sensor raw and rendered "Ray unavailable W". The WAN chip gained the
third branch it was missing, and now navigates to Network like its twin on
Cameras.
Verified nothing was lost by diffing the parsed view before and after: no
entity ID and no navigation target dropped; one added (Network).
Rendered live, WAN down, all-silent and two-cameras-down.
Expect: a shorter panel with a single status strip at the top, controls in two
readable columns, and camera previews about 380px wide instead of 285px.

### `f7d5b13` — switch and cover controls become native Tile cards
Area: 26 cards across home, parents-room, ray-bedroom, guest-room, kitchen,
dining, cameras, climate, lights. Purpose: completes the control-card pass
started in the previous batch. All 25 `mushroom-entity-card` switch controls
and the one `mushroom-cover-card` are now `type: tile`.
The switch conversion was a clean 1:1 — zero Mushroom-only keys had to be
dropped, because those cards used nothing a tile does not do natively. The
roller shade needed two features to keep what it had: `cover-open-close` for
the buttons and `cover-position` for the slider, replacing
`show_buttons_control` and `show_position_control`.
50 tile cards on the dashboard now. Two card types stay Mushroom on purpose,
because there a tile would lose something real: the two climate cards
(temperature control) and the six media-player cards (media info and volume).
That is the "Mushroom only where it genuinely improves functionality" line.
Validated: 268 templates, 36/36 links, 0 broken, no entity loss, 0 inert
card properties.
Expect: switch rows read as one consistent native control across every room
page, and toggle from the icon as well as opening more-info.

### `c6a8118` — light controls become native Tile cards
Area: 20 cards across home, ray-bedroom, guest-room, living-room, dining,
lights, light-living-room, light-ray-bedroom. Purpose: the brief asks for
native Tiles where practical and for compact, calm controls; the Mushroom
light cards with their own brightness sliders were the bulkiest thing on the
Home view.
All 20 are now `type: tile` with a native `light-brightness` feature. 17 use
`features_position: inline`, so the slider shares the row instead of adding
one — a one-row control rather than a two-row card. The three tiles already
native on the iPad Command Center were switched from `bottom` to `inline`
too, so all 24 tiles now behave the same way on the view where vertical space
is tightest.
Functionality preserved, not traded for appearance: six of the twenty offered
`show_color_temp_control` — the two dimmable room lights on their detail
pages. Inline position takes a single feature, so those six stack
`light-brightness` + `light-color-temp` instead, keeping the colour
temperature control that would otherwise have been silently dropped. Home's
copies of the same two lights never had it and stay compact and inline.
Mushroom-only rendering options that the tile reproduces natively or that no
longer apply were dropped: use_light_color, collapsible_controls,
fill_container, show_brightness_control, show_color_temp_control.
Validated: 268 templates, 36/36 links, 0 broken, no entity loss, 0 inert
card properties.
Expect: shorter, flatter light controls; tapping the icon toggles and tapping
the card opens more-info, where the Mushroom card only did the latter.

### `cbec78b` — legible text where cards deliberately have no surface
Area: 69 cards across all views. Purpose: with the photograph live, the cards
that intentionally strip their own surface — 25 page titles, 44 chip rows —
render their text directly on the sky. Over the bright horizon band and the
city lights that is the worst contrast on the dashboard, and it only appeared
once the background went in. Both chrome-strip styles gain
`text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` — enough to hold an edge
against the brightest part of the image, small enough to stay Apple-like
rather than glowing.
Two styles edited, 69 cards covered; no new card_mod block was added.
Validated: 268 templates, 36/36 links, 0 broken, no entity loss.
Expect: page titles and chip rows keep their edge over the comet and city
lights. The 52 native heading cards are NOT covered — they have no card_mod
and need a theme rule; logged as UI-027.

### `0f620f2` — the per-card glass retires; the theme paints the surface
Area: all views, 32 cards. Purpose: every card carried its own
`background: rgba(255,255,255,0.07)` panel with a drop shadow. Over a
photographic background a white tint washes out rather than frosts, and it
would have sat on top of the theme's navy-tinted frosted surface and cancelled
it. All 32 white and blue glass panels are gone; the surface now comes from
`ha-card-background` and the theme's `card-mod-theme` blur, in one place.
Kept, because a theme cannot express them: `overflow: hidden` on the twelve
cards that clip an image to the corner radius, `min-height: 125px` on six,
the 14 entity-row width rules, and the 69 chrome-stripping blocks that
deliberately give title and chip cards no surface at all — without those they
would each grow a frosted panel.
The three active-state glows are retuned rather than removed, since a subtle
glow on an active device is wanted: comet cyan (127,212,240) for the AC,
violet (176,120,216) for the TV, sea green (126,214,176) for the pump, each
matching a Mushroom ramp colour in the theme.
card_mod blocks: 136 -> 104, distinct styles 12 -> 8. File 5% smaller.
Validated: 268 templates, 36/36 links, 0 broken, no entity loss.
Expect: **only correct once the theme is installed.** Until then cards render
with Home Assistant's default opaque surface, which will look flatter than
before, not better. Install the theme first.

### `366a894` — every view retuned for the iPad's two usable columns
Area: all 36 views. Purpose: the dashboard declared up to four columns while
the wall-mounted iPad renders about two, so eight views were dividing that
width three or four ways. `max_columns` is capped at 2 everywhere (home,
parents-room, guest-room, cameras, security, lights, light-living-room,
ipad-command-center) and five `column_span` values wider than the grid were
narrowed to match.
Row packing rather than a blind cap: after the cap Home left Quick Control
and Home Systems each alone on a half-empty row, so Rooms drops to half width
to pair with Quick Control, and Home Systems takes the full width its eight
tiles want, 4-across. Camera tiles were sized for a 2-of-3 section and would
have ballooned to ~570px at full width, so they regrade from 2-across to
3-across and keep their intended size.
No background key was added to any view: the theme's `lovelace-background`
covers every view globally, which is both the mechanism the brief asked for
and zero schema risk on a live dashboard.
Validated: 268 templates, 36/36 links, 0 broken, no entity loss.
Expect: no view splits the iPad width more than two ways; Home reads header /
alerts / today / (quick control | rooms) / home systems with no ragged rows.

### `88be895` — design target moves to CasaRay × Your Name (theme layer)
Area: `themes/deez_your_name.yaml` (new), `THEME_INSTALL.md` (new),
`scripts/yaml_check.py`. No dashboard file touched, so nothing in this batch
can affect the live dashboard until the theme is installed by hand.
Purpose: establish the palette and surface treatment as one design system
rather than editing cards individually. One file defines all six themes the
dashboard references, sharing a base via a YAML anchor and differing only in
accent — cyan (comet), cool blue, teal, ember, warm gold, violet (the
fragment). Colours are sampled from the image, not invented. The frosted
glass is global: a `card-mod-theme` block in the theme gives every card the
backdrop blur, so the ~100 per-card card_mod blocks in the dashboard become
redundant and can be retired progressively.
Background: `lovelace-background`, fixed / cover / centred / no-repeat, under
a two-stop scrim that is 40% at the top, **15% across the middle band where
the comet sits**, and 60% at the base where the cards land — legible without
flattening the comet, stars or city lights.
Validation gate fixed as part of this: the strict duplicate-key loader never
called `flatten_mapping`, so it rejected `<<:` merge keys outright. It now
resolves merges while still catching real duplicates, and checks BEFORE
flattening so a deliberate override of an inherited value is not misreported.
Negative-tested both ways.
Expect: nothing, until `THEME_INSTALL.md` steps 1-2 are done on the host.

### `ae89134` — Cameras: one uniform grid, no camera listed three times
Area: `cameras` view. Purpose: every camera appeared in up to three places at
once — a "N/6 online" summary chip, a picture-entity tile, and a per-camera
status chip below the tiles. Front Door additionally had both a live preview
and a Mushroom card doing the same navigation, and the "All Cameras" heading
sat over a grid that excluded it. Now one grid of six identical tiles at
grid_options columns 6 in a span-2 section; the five duplicate chips are gone.
The summary chip absorbed what they carried: it names the offline cameras
("North Wall, Stockroom offline") rather than only counting, and degrades to
"4 of 6 offline" instead of truncating. The WAN chip gained an unavailable
branch. Front Door's one-off 0.20 border was unified to the 0.18 used by the
other five.
Validated: 268 templates, 36/36 links, all six camera entities and all six
subview links intact. Chip rendered at zero, one, two and four cameras down.
Expect: two-across previews roughly double their old width, one row of status
chips instead of two, and a named camera when one drops.

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
