# Deez Smart Home — project rules

Permanent rules and architecture for this repository. Read this, then
`PROJECT_STATE.md`, at the start of every session. Resume from that recorded
state; do not re-audit from scratch.

## What this repository is

`ha-deploy` is the deployment branch for the household's Home Assistant
dashboards. It carries **two**, and they have different jobs.

### `dashboards/casaray_v2.yaml` — the canonical CasaRay target

**Owner decision, 2026-09-05.** This is where CasaRay is built. Every future
batch, board, UX improvement, bilingual improvement, entity integration,
automation-linked UI, and every Bills, Entertainment, Camera, People Mapping,
Energy or House Health feature targets **this file**, unless the owner says
otherwise in so many words.

Identity: url_path **`casaray-v2`** — Home Assistant requires the hyphen in a
YAML dashboard key (all 124 internal links are `/casaray-v2/<view>`; mounted
anywhere else, navigation breaks), 28 views (7 subviews), native-first —
one custom card type (`custom:webrtc-camera`), no Mushroom, surface treatment from the
theme, and `card_mod` only where a native card provably cannot reach the
mockup: the tinted surface on alert cards (since `color:` paints a tile's icon
and the renders tint the whole card), the state-driven dashed treatment on
offline tiles, the pill radius on every view's chip strip, and right-aligning
the clock. Bilingual on `input_boolean.chinese_dashboard`; see *Bilingual
conventions* below.

**Home carries the design system.** It was rebuilt against the 14/09 wall
render on 2026-09-15, corrected twice against the live iPad, and reordered on
2026-09-20 against the approved MOBILE render, and is the reference every
other view follows as it is rebuilt in turn. Nine bands, top to bottom:
**top bar** (wordmark and clock over a row of six nav icons) ·
**chip strip** (one full-width card) · **Needs attention** ·
**One tap** (full width) · **Rooms | Shopping list** ·
**Right now | Who's home** · **Security** (full width) ·
**Energy now | Recent activity** · **More boards** (full width).

**One tap and Rooms sit directly under Needs attention, and that is
deliberate** — `docs/mockups/2026-09-14_mobile_home.png` puts the controls
you actually touch there, and before the reorder One tap was about two and a
half screens down on a phone. `CVA-004`. Moving Rooms without Shopping list
would strand both as lone `column_span: 1` sections, so the three move
together; the YAML's `BAND n` comments are numbered in this order.
Two columns, horizontal bands, not vertical stacks — see the geometry rules
below for why, and do not raise `max_columns` without a live screenshot.
Navigation lives **in the page**, not in Home Assistant's
chrome — `kiosk_mode` hides the sidebar and header, so Home's icon rail and
its named More boards index are the only way around the dashboard. Do not
remove either.

### `dashboards/deez_smart_home.yaml` — legacy, and the reference baseline

The older production dashboard. It is **not** the target for new CasaRay work.
It remains valuable and stays exactly where it is, as:

- a reference for **confirmed working entity IDs**,
- a source of **proven templates and logic** worth reusing,
- the **rollback / reference baseline**,
- the running system until v2 is deployed and verified.

**Do not delete, overwrite, merge into, or materially restructure it.** Do not
rebuild v2 features in it. Touch it only for a genuine regression in it, or on
an explicit owner instruction.

Identity: url_path `deez-smart-home`, title **Deez Smart Home**, 36 views
(16 subviews), Mushroom + card_mod + kiosk_mode, five per-view themes, the same
language toggle.

### Deployment

`CFG-003` is **RESOLVED**: pushes reach the host clone at `/config/deez_repo`,
and CasaRay has been deployed and seen rendering.

Delivery is still **not automatic for CasaRay**.
`/config/deploy_deez_dashboard.sh` syncs the legacy dashboard only; CasaRay
reaches `/config/dashboards/` when the owner runs
`scripts/sync_casaray_to_config.sh`. So "committed in Git" and "live in Home
Assistant" remain different things and must never be reported as the same one
— the reason is now a manual step, not a broken bridge.

## The chip strip — every view has one, and no view has badges

As of 2026-09-18 all 28 CasaRay views carry the mockups' pill row: **one
full-width `markdown` card**, section 2, directly under the top bar, with the
pill radius from `card_mod`. Three to five readings, ` · ` between them, the
label dim and the value bold.

**Never add a `badges:` block to `casaray_v2.yaml`.** Home Assistant renders
badges above the sections and CasaRay's first section IS the top bar, so a
badge row lands on top of the wordmark (`DR-011`). `dashboard_check.py`
check 15b fails the build on one. The legacy dashboard is out of scope — its
views have no top bar, so badges sit correctly there.

The strip is a card rather than badges for a second reason worth keeping in
mind when writing one: **most of what the mockups put in a pill is not any
entity's state.** `Movement Quiet, 22 min` is elapsed time from
`last_changed`; `Unpaid 3 of 6` is a count across six helper pairs;
`Warnings 3 (+2 unknown)` re-evaluates the conditions the alert cards fire
on. A badge can show a state. It cannot show a computation, and it has
nowhere to put the third branch every one of those computations needs.

Three rules for a new chip, all of them learned by getting one wrong:

1. **A denominator is what ANSWERED, not the length of the list.** Five of
   the fourteen cloud sensors are unavailable on this instance; `9/14` would
   read as five dead devices rather than five that are not reporting.
2. **A count of zero is only claimed when something was measured.** `Overdue
   0` across six unpaid bills that all lack a due date is a reassurance built
   on nothing — it says `No data`. So does `Lights on` when no light is in a
   known state, and `Offline` when the gate sensor that would say so is
   itself dark.
3. **Render it before committing it**, across a live-shaped state set and a
   fully dark one, in both languages. That is what caught all three of the
   above. A passing validation run proves the Jinja compiles and the entities
   exist; it cannot read what the card says.

## Bilingual conventions — mandatory

These apply to `casaray_v2.yaml` and to any new bilingual work. They are
requirements, not preferences.

1. **Clock date format is `DD/MM/YY`**, produced by
   `now().strftime('%d/%m/%y')`. Never `%Y`. The time sits above the date.
2. **Chinese is Simplified**, matching the legacy dashboard's established
   vocabulary. Grep it for an existing term before inventing one.
3. **Proper nouns and device names may stay Latin** — CasaRay, Hue, Fronius
   Primo, eero, Lovelace, WAN, Ray, Pogo.
4. **Chinese enumerations use `、`**, not `,`.
5. **Bilingual:** page titles, section headings, room summaries, interpreted
   status text, alerts, warnings, explanatory text, and any other user-facing
   dynamic summary.
6. **Never translated:** entity IDs, internal identifiers, YAML keys,
   navigation paths, implementation metadata.

Headings use two `heading` cards with `visibility` conditions rather than a
templated string — the native `heading` card does not render templates. The
English card uses `state_not: 'on'`, so it also shows if the toggle helper ever
goes unavailable and a section never loses its label.

## Session start

1. Read `CLAUDE.md` and `PROJECT_STATE.md` in full. `PROJECT_STATE.md` is the
   authoritative coordination state and carries your routine's startup
   profile.
2. `git fetch origin ha-deploy`, `git log --oneline -15 ha-deploy`, confirm
   the tree is clean and the branch is current.
3. Load everything else **selectively**, per the Context Loading Strategy and
   Routine Startup Profiles in `PROJECT_STATE.md`. Do not read
   `DASHBOARD_PROGRESS.md` or `archive/` end to end as a matter of course.
4. Check open issues and the active backlog **before** planning new work.
   High-severity regressions come before cosmetic improvement.

## Working rules

- Small, controlled batches. One meaningful improvement per batch.
- Inspect the current YAML before changing it. Never edit blind.
- **Never invent entity IDs.** The authority is
  `docs/live/states_export_2026-09-05.txt` — 970 entities with exact IDs,
  friendly names, areas and availability. Grep it before writing any ID;
  `ha_validate.sh` section 3 fails the build on one that is not there.
  Name similarity is not proof: this instance has stale duplicates that
  look right and are dead (see `CR-190`). If no entity exists, say so on the
  card rather than faking status — the established convention is a grey icon
  and an honest secondary ("no status entity", "Wi-Fi module not integrated
  yet").
- Preserve: entity IDs, navigation paths, `/deez-smart-home/` links, the
  language toggle, kiosk mode, subviews, camera functionality, energy
  calculations, room controls, themes, popups.
- Never `| float(0)`, `| float(100)` or `| float(9999)` as a fallback for a
  missing reading. A sentinel renders as a real measurement. Guard with an
  explicit `unavailable / unknown / none` branch, or test `is number`.
- Never let a card assert a reassuring state it cannot see. "Closed",
  "Clear", "Normal", "Up to date" all need a third branch. This also rules
  out a *summary sensor* whose inputs are down: `sensor.open_doors_count`
  reads `0` when the contact sensors are `unavailable`, so it is a sentinel
  wearing a number's clothes and is deliberately on no board. (The three
  contact sensors were all dark when the 05/09 export was taken and were
  reporting again on 19/09 — the sensor is no less dangerous for that. It
  still cannot tell you the difference between "no doors open" and "no doors
  answering", which is the whole objection.)
- **The export's availability column is a snapshot, and it goes stale.**
  `docs/live/states_export_2026-09-05.txt` is authoritative for which entity
  IDs *exist* and what they are called. It is NOT authoritative for what is
  answering today: by 19/09 the three contact sensors, both Tapo C420 camera
  streams and the South Wall privacy switch had all come back while the
  export still called them `unavailable`. Check the live instance before
  writing a card around a device being dead — and before concluding from
  `unavailable` that an ID is the wrong one of a pair.
- A `markdown` card must not start with four or more spaces of output. A
  `{% set %}` preamble emits the spaces between its tags, and four of them
  make CommonMark render the whole card as a grey code block. End preamble
  tags with `-%}`. Gated by `dashboard_check.py`.
- Run `bash scripts/ha_validate.sh` after every batch. Exit 0 or do not push.
- If validation fails, fix or revert before pushing. Never force-push, never
  rewrite published history.
- Push to `ha-deploy` **and** `claude/ha-dashboard-upgrades-wui7ig`. Local
  `ha-deploy` must be fast-forwarded before pushing it, or the push reports
  "Everything up-to-date" and the commit silently never deploys.
- Commit tracking-document updates together with the dashboard change they
  describe.
- A commit cannot contain its own hash. Write the batch's dashboard change
  and its tracking entries in one commit with the SHA left as a placeholder,
  then stamp the real SHA in a one-line `docs: stamp` commit immediately
  after. Do not amend to insert it — amending changes the hash again.

## Do not touch without an explicit instruction

The deployment bridge and its authentication: `/config/deploy_deez_dashboard.sh`,
`scripts/deploy_env.sh`, `scripts/deploy_askpass.sh`, `scripts/deploy_diagnose.sh`,
`DEPLOY_AUTH.md`, the deployment automation, Git remote configuration and
onboarding infrastructure. See `MAINTENANCE.md` for the wider protected list
(secrets, auth, users, tokens, network gear, supervisor operations) and for
the prohibition on device control.

No passwords, tokens, credentials or private Home Assistant URLs in any
tracked file, tracking documents included. The validation gate fails the
build if one appears.

## Design direction

**The 14/09 mockups are the current visual target.** Seven owner-supplied
renders live in `docs/mockups/`, transcribed in
`docs/CASARAY_MOCKUPS_2026-09-14.md`. Where they disagree with anything below
or with `DESIGN_REFERENCE.md`, they win. What they settle so far:

- **Sentence case everywhere** — page titles, section headings, KPI labels.
  No uppercase transform; the theme no longer applies one.
- **The semantic colour system, owner-approved 14/09 (CR-232 closed, amber
  wins; blue does not appear in the mockups at all):**
  **green** healthy, secure, connected, closed, normal ·
  **amber** active, running, currently on, selected ·
  **red** fault, urgent issue, needs attention ·
  **grey** unavailable, offline, unknown, no data.
  An alert card's colour follows what its condition *means*: a flat battery
  or a dead link is red; a door that is simply open is amber; an inverter
  that is not answering is grey.
- **Unavailable is drawn, never hidden**: muted card, a "no data" or "offline"
  note, and it keeps its place in the layout.
- **Controls are tile features** — a light's brightness bar, a fan's speed —
  not custom cards.

**Cinematic, calm, premium, and still native to Home Assistant.** Cards are
frosted glass — translucent, light-bordered, no heavy shadows.

**The background is CSS, not the photograph, as of 2026-09-15.** The Your Name
night-sky frame is still what the LEGACY dashboard uses and its five themes are
untouched. CasaRay's is four stacked gradients — vignette, one soft blue bloom
centred above the viewport, a vertical lift, a base colour. The reason is
measurement, not taste: a canvas readback of all three approved wall renders
returns a flat `#0d1114` body and `#0f1418` top edge at every background probe,
with no image detail anywhere, and the mockups win where they disagree with
this section. `DR-014`. Restoring the photograph is one commented line in the
`CasaRay` theme's `lovelace-background`.

**Every CasaRay surface colour is sampled, and lives in a token.** The renders
give `#0d1114` page, `#161b1f` card, `#1a1f25` elevated, `#201615` alert red.
One glass tint at three alphas reproduces all of them, so cards *lighten what
is behind them* rather than being painted a fixed colour. The tokens are
`--casaray-*` in `themes/deez_your_name.yaml`; the dashboard carries **no
hardcoded colour at all** — 138 rgba literals were replaced by `var()` on
2026-09-15. Retune from the theme; never reintroduce a literal into a card_mod
block.

Global first: put surface treatment in the theme so future cards inherit it,
rather than adding a `card_mod` block per card. Reach for a native Tile or
Section treatment before custom CSS.

**Every card declares its own geometry.** A card with no `grid_options`
takes whatever width the renderer gives it, which goes ragged beside sized
siblings — and only on the device you were not looking at. `dashboard_check.py`
check 13 fails the build on an unsized card in `casaray_v2.yaml`.

The width follows the section, and that is the page's visual hierarchy:

- **A body column** (`column_span: 1`) is a detail list. Tiles, buttons and
  conditionals take `columns: 6` (two across); prose, graphs, media, rooms and
  thermostats take `columns: 12`.
- **A page-level band** (`column_span` equal to the view's `max_columns`) is
  the top bar, the chip strip, Needs attention, Quick actions, media blocks,
  the footer. Tiles take `columns: 2`, `3` or `4`, chosen so the card count
  divides evenly and no row is left with an orphan.

Two deliberate exceptions, both full-width-of-a-half-section: the Security
sirens and the Ray Bedroom overload alarm. Long names, and controls that must
not be mis-tapped. If you normalise them to 6 columns you have made the page
worse, not more consistent.

**The wall iPad resolves TWO columns. This is measured, not chosen.** Home
was set to `max_columns: 3` on 2026-09-15 to match the 14/09 render's three
equal body columns. Live — with `kiosk_mode` hiding both the sidebar and the
header, so nothing was stealing width — the wall iPad still resolved the
sections view as **two** columns. `column_span: 3` clamped to 2, and every
group meant for a third column dropped onto a row of its own with a hole
beside it. Home is now `max_columns: 2` and every view on this dashboard is
two. See `DR-013`.

Do not raise `max_columns` above 2 on any view without a live screenshot
proving the extra column resolves. A passing validation run cannot see it, the
geometry arithmetic here was wrong twice, and the failure mode is silent:
the YAML is valid, the page just grows holes.

**Compose for two, in explicit horizontal bands.** A section is a grid item;
sections in a row top-align and the row is as tall as its tallest member, so
a lone `column_span: 1` section leaves half a row empty. Every band is either
a pair of comparable height or one full-width group:

| Band | Layout |
|---|---|
| top bar | full width — wordmark(6) + clock(6), then six nav icons at 2 each |
| chip strip | full width — one card |
| Needs attention | full width — alert cards at `columns: 6`, two across |
| One tap | full width — four scene cards at `columns: 3`, four across |
| Rooms \| Shopping list | one column each |
| Right now \| Who's home | one column each |
| Security | full width |
| Energy now \| Recent activity | one column each |
| More boards | full width |

**A row of buttons that must not reflow should sum to exactly 12.** Four at
`columns: 3` fill the grid, so the renderer cannot pack five onto a row or
spread them to eight — eight would need 24 columns of 12. That is how More
boards holds its four-across shape and how One tap holds its scene bar. Do not
rely on wrapping.

**`columns` is a fraction of the RENDERED width, and this environment cannot
measure it.** The 2026-09-15 Home rebuild assumed a full-width band on an iPad
in landscape is about 1150px, so `columns: 3` would be ~280px. Live it was far
less — enough that a 3/12 markdown card came out narrower than a markdown
card's own minimum height and drew a circle instead of a pill, and `columns: 1`
broke the word `CasaRay` vertically. See `DR-012`. The floors that came out of
that, for `casaray_v2.yaml`:

- **Nothing below `columns: 2`**, ever — a 1/12 cell is not a usable card.
- **No text-bearing card below `columns: 3`.** A button whose label is longer
  than `Bills` wants 3; `Entertainment` proved 2 is not enough.
- **A single wide card beats several narrow ones** for a row of readings. The
  chip strip is one full-width markdown card, not four pills, because one card
  is always wider than it is tall whatever the container does.
- **`white-space: nowrap`** on any card whose text must not break — the
  wordmark and the clock carry it. It is a guarantee; a `columns` value is a bet.

**Rows are as tall as their tallest member.** Sections placed side by side are
CSS grid items: the short one does not shrink the row, it leaves a hole under
itself. Pair groups of comparable height across a band, and give an
under-filled card an explicit `rows:` rather than leaving it `auto` beside a
tall neighbour. Home's bands (top bar · chips · Needs attention · One tap ·
Rooms/Shopping · Right now/Who's home · Security · Energy/Recent ·
More boards) are arranged on exactly that principle.

**A lone `column_span: 1` section leaves half a row empty, and this is now
gated.** A section does not stretch to fill its row; it sits in half of it.
The 2026-09-18 audit found that shape on seven views besides Home — Kitchen,
Dining, Ray Bedroom, Energy, Bills, Automations, Entertainment. `check 15` in
`dashboard_check.py` fails the build on any new one. The fix is always a
`column_span` edit, never moving a card between sections.

**One exception is allowed, and it is in the gate's own list:** Security's
sirens stay half-width. They are controls that must not be mis-tapped, and a
full-page-width siren button is a *bigger* accidental-tap surface, not a
smaller one. Adding another exception means editing `ALLOWED_HALF_ROWS` and
saying why.

Still true from the previous direction: calm, minimal, Apple-like.
Sections layout with `grid_options`, not nested `grid` cards. One `heading`
card per section; the single `mushroom-title-card` is the page title and
comes first. Restrained amber for active state. Consistent 18px radius glass
surface. iPad landscape is the primary target — `max_columns` must match the
width a view actually fills, and no label should truncate.

## What cannot be verified from here

The build environment has no `/config`, no supervisor, no route to the
instance. YAML parsing, templates, navigation and structure are checkable;
Lovelace schema, entity existence and anything visual are not. A passing
validation run never means a card renders. See `DEPLOYMENT_BLOCKERS.md`.
