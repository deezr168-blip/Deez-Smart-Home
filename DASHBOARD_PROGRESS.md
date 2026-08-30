# Dashboard progression record

Historical record of `dashboards/deez_smart_home.yaml` batches. Newest first.
Append after every successful batch; commit with the change it describes.

> **Autonomous routines: do not read this file end to end.** It is history,
> not coordination state. Normally inspect only the most recent entries and
> any entry referenced by `PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md` or
> `DASHBOARD_ISSUES.md`. Full narratives for older batches live in
> `archive/DASHBOARD_PROGRESS_ARCHIVE.md` — read them only when investigating
> a regression or revisiting a design decision.
>
> Authority: `PROJECT_STATE.md` is current coordination state,
> `DASHBOARD_BACKLOG.md` is the work queue, `DASHBOARD_ISSUES.md` is the
> issue record. This file is none of those and carries no priority list.

**Verification.** "Validated" means `scripts/ha_validate.sh` passed — YAML,
duplicate keys, templates, navigation, mass-damage, secrets. It does not mean
anything rendered. Visible results stay unconfirmed until checked on the live
dashboard; see `DASHBOARD_ISSUES.md` for status.

Deployment: a push to `ha-deploy` reaches the live dashboard within 15
minutes.

---

## Recent batches

Detailed. These are the batches current work and open verification depend on.

### `ccfb0c8` — camera-subview sweep (clean); raw-interpolation fixes (UI-031); one new false-safe finding (REG-013)
Purpose: continued the 691689a note's own recommendation — a fresh
raw-interpolation (UI-006/UI-030 class) pass across the six `camera-*`
subviews, since the bill subviews flagged alongside them are Billing-owned
and out of scope for Main.

The six camera subviews themselves were clean: each is just a back chip plus
a `custom:webrtc-camera` card with a static title, no template content to
guard. Widened the grep instead to every remaining raw `{{ states(...) }}`
interpolation in the file (excluding `bill-*`, Billing-owned) and found three
genuine instances, plus one separate false-safe finding noticed while
checking the same `lighting-modes` view:

- **`UI-031`** — three unguarded/untranslated raw interpolations:
  - `home` quick-control Person chip: printed the raw `person.raymond_du`
    state string verbatim (`home`/`not_home`, or a literal `unavailable`).
    Replaced with the distance-based bilingual convention already
    established for the same person on `people-locations` and
    `ipad-command-center` (在家/未知/`X km away`), and the icon colour now
    uses the same grey/green/orange/red distance banding instead of a
    two-branch green/blue that had no unavailable case.
  - `home` Rooms-grid Climate card: printed the raw lowercase HVAC mode (or
    `unavailable`) with no guard, two cards away from the Parents Room
    card (~L375) which already guards the identical entity with a
    `bad`/title-case convention. Now reuses that same convention.
  - `light-ray-bedroom` Roller Shade card: printed the raw cover state and
    an **unguarded battery percentage** that would render `unavailable%` —
    the exact class UI-020 already fixed for the Powerpal battery card.
    Now guards both the cover state (matching the `home`/`ipad-command-center`
    Ray Bedroom summary cards' existing 开/关/— convention) and the battery
    reading (matching the Powerpal card's `bad`-list convention, ~L1492).
  No entity was invented — all four entities were already referenced
  elsewhere in the file under the conventions this batch reused.
- **`REG-013`** — a genuine false-safe finding, not the raw-interpolation
  class: the `lighting-modes` "Current State" section's three light cards
  (Living Room, Ray Bedroom, Dining) read
  `'Off' if is_state(light,'off') else (<percent> if brightness is not none else 'On')`.
  An `unavailable`/`unknown` light is neither `off` nor has a `brightness`
  attribute, so all three fell into the final branch and confidently showed
  **"On"** — CLAUDE.md's process note by name ("never let a card assert a
  reassuring state it cannot see"), just for a light rather than a
  door/motion sensor. Icon colour was already safe (grey unless confirmed
  `on`); only the status text was the false-safe surface. Now shows
  bilingual "Offline"/"离线" ahead of the off/percentage branches.

Deliberately **not** touched: the widespread `'On' if is_state(...,'on') else
'Off'` toggle-chip pattern used across most light rows in the file (e.g.
`light-living-room`, `light-ray-bedroom` power chips). That pattern has the
same theoretical gap (an unavailable light reads "Off") but is a direct
toggle control rather than a status-summary card, appears on essentially
every lighting view, and was never flagged by the REG-001..012 audits despite
several thorough sweeps — redesigning it dashboard-wide would be a large,
speculative redesign outside this batch's small-controlled-batch scope, not
a targeted fix. Left as a candidate for a future run if the owner confirms
it's wanted.

Validated: `bash scripts/ha_validate.sh` passes clean (7/7), 386 templates
compiled (unchanged), 36/36 views resolve, no entity/view loss, diff touches
only the four cards described above (7 insertions / 14 deletions net, single
file). Added `REG-013`/`UI-031` rows to `LIVE_VERIFICATION_QUEUE.md` and
corrected its "checks pending" footer to the table's actual current count
(42) in the same commit — the prior batch's `REG-012` finding was exactly
this kind of drift, so this batch does not repeat it for its own additions
(the pre-existing `691689a`/`REG-007..011` gap `REG-012` describes is
unchanged and still owned by the Regression Auditor / Daily Project
Coordinator).

### `691689a` — false-safe aggregate sweep widened; one raw-interpolation fix (UI-030)
Purpose: Main's queue was exhausted (`DR-001` needs a design brief, everything
else `LIVE_VERIFICATION_REQUIRED`), so this run carried out the widened sweep
the 01:50 note recommended — the REG-007..011 aggregate-door pattern
(`states() | select('eq','on') | count`, unavailable sensors silently dropped
from the tally) checked against `climate`, `network`, `status` and all seven
room views (`parents-room`, `ray-bedroom`, `guest-room`, `living-room`,
`kitchen`, `dining`, `garage`), not just the three views REG-007..011 covered.
Grepped for the raw three-door-sensor array, `namespace(`/`reduce(` aggregate
patterns, combined `is_state(...) and/or is_state(...)` boolean checks, and
every remaining reassuring-text literal (`Closed`, `Clear`, `Normal`, etc.) in
the file. **Clean result** — every instance already carries the
unavailable/unknown/none guard; no new false-safe aggregate found. The one
open camera-count aggregate not covered by REG-007..011 (`ns.down`-based
"N of 6 offline" on `cameras` and `ipad-command-center`) was already guarded.
Also grepped for un-guarded raw `states()` interpolations printing a literal
state name mid-sentence (UI-006's class) and found exactly one survivor:
`ray-bedroom`'s LetPot "Grow Light" card (~L859) printed
`states('select.lph_se_dcd9_light_mode')` and `..._light_brightness` with no
guard at all — an unavailable select would have rendered the literal word
"unavailable" as if it were a real mode/brightness reading. Both entities
were already referenced only at that one line, so no entity was invented;
added the same `bad = [unavailable, unknown, none]` guard used throughout the
file, falling back to an em dash per field, or a bilingual "Offline"/"离线"
when both are unavailable. Filed as `UI-030` (S4 — cosmetic, not a
security-class false-safe: no reassuring claim was made, just a raw state
name).
Validated: 386 templates, 36/36 links, 0 broken, no entity/view loss.
Expect: no visible change to the sweep-checked views (nothing there needed
fixing); the LetPot Grow Light card now reads "— • —" or "Offline" instead of
"unavailable • unavailable" whenever the LetPot select entities go offline.

### `b058006` + `d592692` — five copies of one false-safe door-count aggregate closed (REG-007..011)
Area: `home` (House Pulse hero, quick-control chip row, Rooms → Security
card), `cameras` (status chip row), `ipad-command-center` (Home Pulse chip
row). Purpose: continues the REG-001..006 false-safe-state sequence with the
narrow re-sweep the 00:35 re-check recommended, scoped to aggregates
(multiple sensors folded into one count/colour) rather than the
single-sensor cards REG-001..003 already covered.
The exact same three-element list — `states('binary_sensor.m_contact_sensor_door')`,
`f_contact_sensor_door`, `b_contact_sensor_door` — had been copy-pasted into
six cards across three views (a seventh, the `home`/`network` Network nav
chip, was already guarded under REG-003). Every unguarded copy did
`doors | select('eq','on') | list | count`: an unavailable door sensor is
neither `'on'` nor counted, so it silently vanished from the tally instead
of being flagged — all three sensors dropping out showed a confident
"0 open" and a green/safe icon, this project's own named recurring defect.
Three of the five (the `cameras` chip, and the `ipad-command-center` and
`home` quick-control Doors chips) had no guard branch at all and were still
bare English, unlike their already-guarded Motion/WAN siblings sitting in
the same chip rows.
Fixed all five to the existing guarded/bilingual convention: standalone
"Doors" chips now show "Sensor offline" / 传感器离线 and turn grey when every
door sensor is unavailable (matching the Motion chip's own convention);
mixed-info cards (the House Pulse hero, the Rooms Security card) keep their
other fields and append "N door sensor(s) offline" / "N unknown" instead,
turning grey rather than green when any door state is unknown. A `b058006`.
`d592692` correction: the first pass mislabeled one fix as
`ipad-command-center` when the chip is actually on `cameras` — the actual
`ipad-command-center` Home Pulse row turned out to have its own, previously
undiscovered instance of the same bug (REG-011). Caught by grepping the raw
sensor list after the first commit rather than trusting the initial
spot-check; a repeat of that grep after the second commit confirms no
unguarded copy remains anywhere in the file.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss, on both
commits.
Expect: no visible change when all three door sensors are healthy; with one
or more disabled, the affected card now says so instead of a confident
"0 open" / green.

### `dff00f3` — the last three bare-English fragments close the bilingual thread (BILING-RESID)
Area: `people-locations` (~L2879), `ipad-command-center` WAN chip (~L3675),
`home` Energy tile (~L450). Purpose: closes REG-004/005/006, the residue left
after the UI-012 → UI-028 → UI-029 sequence and the REG-001/002/003 batch.
REG-004: the "at home" (🟢) branch of the per-person distance loop printed
bare `home` while its own "away" branches on the same line were already
bilingual. Now `{{ '在家' if cn else 'home' }}`.
REG-005: the WAN chip's unavailable fallback read literal `WAN —` in both
languages. Rather than translate the dash in isolation, matched the wording
an equivalent unavailable case already uses elsewhere in the file
(`~L1636`, "网络无数据"): now `{{ '网络无数据' if cn else 'WAN not reporting' }}`.
This changes the English text from "WAN —" to "WAN not reporting" — a
deliberate consistency choice per the audit's own recommendation, not a pure
translation; flag if the owner wanted the dash kept literally.
REG-006: the Energy tile's `offline` fallback sat untranslated beside its own
already-bilingual "Solar"/"太阳能" label. Now `{{ '离线' if cn else 'offline' }}`.
Verified each branch by rendering the extracted Jinja logic standalone: all
three reproduce their existing English exactly (REG-005's fallback text
change aside, which is intentional) and produce Chinese when the toggle is on.
Validated: 384 templates, 36/36 links, 0 broken, no entity loss.
Expect: no visible change in English; with the toggle on, the three remaining
gaps in the bilingual pass are closed.

### `9926233` — heading cards get their contrast back (UI-027)
Area: `themes/deez_your_name.yaml` (one rule, shared base). Purpose: the 52
native `heading` cards across every section render with no `ha-card` wrapper,
so the theme's existing `card-mod-card` rule — the one place `cbec78b` put
the frosted-glass and text-shadow treatment — never reaches them. They sit
straight on the photograph, and lose contrast over the bright horizon band
exactly as UI-027 described.
`card-mod-card-heading` is card-mod's documented per-card-type theme key: it
targets that one card type's own host element instead of assuming an
`ha-card` child exists. `text-shadow` is an inherited CSS property, so
setting it on `:host` reaches the label and icon text underneath without
needing to know the heading card's internal DOM — the same
`0 1px 3px rgba(4, 10, 20, 0.55)` value the 69 title and chip cards already
carry, so all three chrome types now read with one consistent edge.
One rule at the theme base, not 52 per-card `card_mod` blocks, per the
global-first design direction in `CLAUDE.md`.
Validated: dashboard YAML/templates untouched (0% size change on the
dashboard file), theme YAML parses with no duplicate keys.
Expect: every section heading keeps a legible edge over the comet and city
lights, matching the page titles and chip rows above and below it. This
environment cannot render Lovelace or card-mod's shadow-DOM behaviour, so
this stays AWAITING LIVE VERIFICATION until checked on the iPad.

### `b5eee22` — three reassuring/untranslated regressions closed (REG-001/002/003)
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

---

## Earlier batches

Compacted. Full narratives in `archive/DASHBOARD_PROGRESS_ARCHIVE.md`.

| Date | Commit | Area / result | Verification |
|---|---|---|---|
| 2026-08-29 | `56c7656` | two media players stop being controlled twice (UI-013) | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `9b28fdb` | the last nested grids are gone (UI-016) | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `99a77b4` | the wall panel itself: iPad Command Center rebuilt (UI-015) | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `f7d5b13` | switch and cover controls become native Tile cards | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `c6a8118` | light controls become native Tile cards | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `cbec78b` | legible text where cards deliberately have no surface | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `0f620f2` | the per-card glass retires; the theme paints the surface | LIVE_VERIFIED (UI-026) |
| 2026-08-29 | `366a894` | every view retuned for the iPad's two usable columns | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `88be895` | design target moves to CasaRay × Your Name (theme layer) | LIVE_VERIFIED (UI-025) |
| 2026-08-29 | `ae89134` | Cameras: one uniform grid, no camera listed three times | LIVE_VERIFICATION_REQUIRED |
| 2026-08-29 | `a5dc914` | Network: static labels stop impersonating live status | LIVE_VERIFICATION_REQUIRED |
| 2026-08-28 | `df457e3` | Energy: five sections, two silent readouts guarded | LIVE_VERIFICATION_REQUIRED |
| 2026-08-28 | `2b80ac6` | deployment auth (not a dashboard change) | n/a — deployment auth, not a dashboard change |
| 2026-08-28 | `76da19b` | People & Locations rebuilt; the 9999 km sentinel removed | LIVE_VERIFICATION_REQUIRED |
| 2026-08-28 | `34a92e7` | 16 of 19 top-level views were dead ends in kiosk mode | LIVE_VERIFICATION_REQUIRED |
| 2026-08-26 | `e06d0ce` | camera subviews were dead ends; lighting pages read backwards | LIVE_VERIFICATION_REQUIRED |
| 2026-08-26 | `3048e54` | "nothing here yet" placeholders cleared off room pages | LIVE_VERIFICATION_REQUIRED |
| 2026-08-26 | `bb05c7c` | Climate and Status get structure; four weather/date defects | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `315323f` | 20 cards asserting a state they cannot see | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `b1ef565` | Security rebuilt; false "Closed" fixed | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `94a9b42` | views declaring more columns than they have sections | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `b85949e` | one section-header treatment across every view | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `018610b` | Home room cards get real, guarded, bilingual status | LIVE_VERIFICATION_REQUIRED |
| 2026-08-25 | `119e1cd` | Home page cramped grids and duplicated tiles | LIVE_VERIFICATION_REQUIRED |
