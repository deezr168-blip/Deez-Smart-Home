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
