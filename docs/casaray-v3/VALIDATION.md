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
| V3 gate, 4 locales × structure, navigation, deps, entities, safety, rendered honesty, secrets | **367 passed, 0 failed**, 4 notes |
| Regression tests (`tests/v3`, 24 tests) | **OK** |
| Repository gate `scripts/ha_validate.sh` | **PASSED** (8 sections); its section 8 (HA config check) SKIPPED: no hass, no /config |
| `dashboards/casaray_v2.yaml` sha256 | `77a4991626d6f8afcd9b78f235c34417d84d9f36c129549a386d8a66c324226c` (unchanged) |
| V2, legacy dashboard, `themes/` | unchanged vs `casaray-v3-design` |

### What the V3 gate checks, per locale

YAML parses with duplicate-key detection · output marked DEVELOPMENT ONLY ·
unique view paths · every V2 view has a V3 home · classic copy of every rebuilt
view · no `badges` · every `navigation_path` resolves inside the locale's own
url_path, none left on `/casaray-v2/` · custom cards ⊂ {`webrtc-camera`} ·
every entity exists in the export · no missing string keys.

Per native view: native card types only · no `card_mod` · `grid_options` on
every card · `max_columns ≤ 2` · nothing below `columns: 2` · no
`float(0/100/9999)` sentinel · no HVAC action · no switch / siren action ·
switch and climate tiles read-only · templates execute in a normal and an
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
drift test plants a wrong hash and expects the build to refuse.

## Notes from the gate (not failures)

- `zh-Hans`: 97 strings fall back to English (partial by design).
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
