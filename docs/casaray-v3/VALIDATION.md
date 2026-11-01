# CasaRay V3 — validation

**DEVELOPMENT ONLY — NOT DEPLOYED.** Everything below is **offline**. No check
contacted Home Assistant. A pass means the YAML is sound, every reference
exists in the 05/09/26 export and templates say honest things when executed
by a local shim. It does **not** mean any card renders on a device.

## How to run

```sh
python3 scripts/v3/build_dashboard.py --check   # reproducible build
python3 scripts/v3/validate_dashboard.py        # V3 gate
python3 -m unittest discover -s tests/v3        # regression tests
bash scripts/ha_validate.sh                     # repository gate
```

## Results — 01/11/26, branch `feature/casaray-v3-build`

| Check | Result |
|---|---|
| Build reproducible (`--check`: committed outputs == fresh build) | pass |
| V3 gate, 4 locales × 15 native views: structure, navigation, deps, entities, safety, tile safety, protected classes, button confirmations, rendered honesty, secrets, migration map, controls allowlist | **1191 passed, 0 failed**, 12 notes |
| Regression tests (`tests/v3`, 63 tests) | **OK** |
| Migration map: all 16 V2-home entities and the 2 V2-cameras floodlights have a verified V3 place | **18 of 18 native** (CR-V3-17 made the last 6 native) |
| Rebuilt Security, Network, Ray's room, Guest room: every V2 entity on its native rebuild | **4 of 4** (rooms: entity set identical to V2) |
| Rebuilt Rooms index, Living room, Kitchen, Dining, Parents' room, Garage: every V2 entity accounted for | **6 of 6** (155 of 156 per-view entity references on the rebuilds; `zone.home` stays on carried People, a verified migration row) |
| Repository gate `scripts/ha_validate.sh` | **PASSED** (8 sections); its section 8 (HA config check) SKIPPED: no hass, no /config |
| `dashboards/casaray_v2.yaml` sha256 | `77a4991626d6f8afcd9b78f235c34417d84d9f36c129549a386d8a66c324226c` (unchanged) |
| V2, legacy dashboard, `themes/` | unchanged vs `casaray-v3-design` |

### What the V3 gate checks, per locale

YAML parses with duplicate-key detection · output marked DEVELOPMENT ONLY ·
unique view paths · every V2 view has a V3 home · classic copy of every rebuilt
view · no `badges` · every `navigation_path` resolves inside the locale's own
url_path, none left on `/casaray-v2/` · custom cards ⊂ {`webrtc-camera`} ·
every entity exists in the export · no missing string keys.

Once per build: the build runs (baseline pinned, and every row of the
manifest's `migration` map is true: the named view exists, is the stated kind
and really references the entity; no V2 entity of a rebuilt view is left
without a row; `retained` / `blocked` rows carry a reason).

Per native view: native card types only (now incl. `media-control`) · no
`card_mod` · `grid_options` on every card · `max_columns ≤ 2` · nothing below
`columns: 2` · no `float(0/100/9999)` sentinel · no HVAC action · no switch /
siren service action · **tile safety** (`tile_safety`): climate and camera
tiles read-only, a siren tile only as the V2 tile byte for byte, a switch
only if it is in manifest `controls` and behaves exactly as its V2 tile ·
no control on a camera privacy / detection / alert / chime / alarm or
bulb-power switch · templates execute in a normal and an
all-unavailable state set · no markdown starting with four spaces · in the
dark set, no all-clear or partial-clear reassurance and no zero claimed from
nothing.

Secrets: JWT / HA token shapes, Anthropic and GitHub token shapes,
`password|api_key|secret|token: <value>`, IP-address URLs, DuckDNS / Nabu Casa
URLs, private keys — across every V3 file.

### Tests with positive controls

Each honesty test proves it can see what it guards against: the all-clear line
appears when every check answers and disappears when one goes dark; the
sentinel and secret patterns are shown to match planted samples; the baseline
drift test plants a wrong hash and expects the build to refuse; the migration
test plants seven wrong maps (row removed, wrong view, wrong kind, unknown view,
stray key, unreasoned retention, stale row) and expects each to stop the build,
then builds the real map. The tile-safety test feeds the gate's rule five
broken views (a siren icon made to toggle, a siren recoloured, a privacy
switch and the bulb-power switch made controls, a listed switch acting unlike
V2) plus an allowlist missing the printer plug, and expects each to be caught;
the real views pass. Rebuilt views are also checked tile by tile against
their V2 tiles: same effective tap and icon actions, same features, same
scenes, apart from the protected switches, which open the classic controls.
CR-V3-18 adds: ordinary room settings act as in V2 and sensitive switches /
settings are inert and gated; the rooms index opens the same pages as V2;
the air-con stays read-only with one tap to the V2 thermostat; Climate's
controls button opens `v2-parents-room` in every locale; the filter reset
asks first in every locale (and a copy with the confirmation removed is
caught); the freezer line and room conditions never claim what nothing
measured. Three real-build mutants are caught: the freezer plug made a
control, the filter reset without a confirmation, Climate's button pointed
back at the native Parents' room. The unpaid-bills check reports clear only when the
count and all six paid flags answer, and is shown both raising a count and
refusing a zero from dark inputs.

## Notes from the gate (not failures)

- `zh-Hans`: 253 strings fall back to English (partial by design; V2 vocabulary only).
- Native views reference 30 distinct entities that were not `ok` in the 05/09 export
  (Hue spots, two Tapo C420 streams, the three contact sensors, never-used
  scenes). They draw as No data / Offline / State unknown when so.
- `ha_validate.sh` warns that native V3 headings "show in both languages".
  Expected: each V3 dashboard is one language by design (build-time
  localisation), so V2's two-heading visibility pattern does not apply.

## Not verified — requires a live device and owner approval

Rendering and real column count on the wall iPad and iPhone · theme install
and light/dark switching · `webrtc-camera` / `card_mod` installation · tile
features on Core 2026.9.2 · entity availability today · Cantonese and Khmer
wording (native review) · kiosk behaviour.
