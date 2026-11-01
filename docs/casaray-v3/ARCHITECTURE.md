# CasaRay V3 — architecture

**DEVELOPMENT ONLY — NOT DEPLOYED.** Branch `feature/casaray-v3-build`. Nothing
here is registered in Home Assistant, synced to `/config`, or validated against
the live instance. Owner instruction, 01/11/26: build V3 completely offline.

## Sources of truth

| What | Where | Status |
|---|---|---|
| Recovery baseline | `dashboards/casaray_v2.yaml`, `ha-deploy@18a4e5d`, sha256 `77a49916…6c` | **pinned**: the build refuses to run if it changes |
| Entity existence | `docs/live/states_export_2026-09-05.txt` (970 IDs) | authoritative for *exists / name / area*; its availability column is a 05/09 snapshot |
| Design direction | `design/casaray-v3/` (DESIGN_SPEC, DECISIONS V3-005/007, ENTITY_MAPPING) | reused; this build implements it in Lovelace |
| HVAC contract | `casaray-v3/hardening-1`, DECISIONS V3-008 | honoured by leaving HVAC **read-only** (not merged; prototype-only code) |
| Root rules | `CLAUDE.md` (bilingual conventions, geometry DR-011/012/013, honesty rules) | applied to V3-native views and gated |

The V3 branch was cut from `casaray-v3-design` (which contains `ha-deploy`), so
all existing V3 design work is preserved untouched. No recovery branch,
`ha-deploy`, or PR #10 is modified.

## Layout

```
src/casaray_v3/                 sources (outside dashboards/: the repo gate
  manifest.yaml                 treats every YAML there as a live dashboard)
  views/{home,lighting,climate,cameras,energy}.yaml   V3-native view specs
  i18n/{en,yue,km,zh-Hans}.yaml                string catalogues
  themes/casaray_v3.yaml                       dark + light token theme
scripts/v3/
  components.py                 reusable native-card components
  build_dashboard.py            deterministic build (+ --check)
  render_check.py               offline Jinja shim for template execution
  validate_dashboard.py         the V3 gate
tests/v3/test_v3.py             offline regression tests (unittest, stdlib only)
dashboards/casaray_v3.yaml      GENERATED — English, url_path casaray-v3
dashboards/casaray_v3/dist/     GENERATED — yue / km / zh-Hans
docs/casaray-v3/                ARCHITECTURE, DESIGN_SYSTEM, BUILD_STATUS,
                                VALIDATION (hand-written); VIEW_INVENTORY,
                                ENTITY_MATRIX, build_report.json (generated)
```

## Build pipeline

`python3 scripts/v3/build_dashboard.py` → for each locale in the manifest:

1. Verify the V2 baseline hash. Drift aborts the build.
2. For each V2 view, in V2 order:
   - **native** (listed in `manifest.native`): expand `src/casaray_v3/views/<path>.yaml`.
     A view spec is plain YAML; `{c: component, …}` calls a function in
     `components.py`, `{t: key}` is a localised string.
   - **carried**: the V2 view verbatim, every `/casaray-v2/` link rewritten to
     the locale's url_path, `theme: CasaRay` set so it renders as V2 does.
3. Append a **classic** `v2-<path>` subview for every native rebuild, so no
   V2 function is lost while the rebuild matures; each native view links to it.
   Verify the manifest's `migration` map: every V2 entity of a rebuilt view is
   on the rebuild or has a row naming where it went, and every row is true
   of the generated views. A false or missing row aborts the build.
4. Dump with fixed settings (no timestamps, insertion order, literal blocks),
   then write the build report, view inventory and entity matrix.

`--check` rebuilds in memory and fails if any committed output differs, so the
committed dashboards are always exactly what the sources produce.

## Localisation

Home Assistant has no runtime i18n, and the V2 runtime toggle is a binary
`input_boolean.chinese_dashboard`. Three languages would need a new
`input_select` helper — out of scope (no helper changes). So V3 localises **at
build time**: one dashboard per locale, each with its own url_path
(`/casaray-v3`, `/casaray-v3-yue`, `/casaray-v3-km`, `/casaray-v3-zh`). A device
bookmarks its language.

- Lookup: locale → its `fallback` list → English. Every fallback and missing
  key is recorded in `build_report.json`; a missing key fails the gate.
- `en` is the reference catalogue; tests require every other catalogue's keys
  and `{placeholders}` to match it.
- `yue` (Traditional HK script, colloquial Cantonese) and `km` are **complete
  drafts, not native-reviewed**. `zh-Hans` reuses V2 vocabulary and is partial
  by design (68 keys fall back to English).
- **Carried and classic views stay V2-bilingual** (EN/简体 on
  `input_boolean.chinese_dashboard`) in every locale until rebuilt.
- Runtime strings (counts, states) are compiled into Jinja at build time, so a
  Khmer dashboard's templates emit Khmer.

Future option (needs approval): an `input_select.casaray_language` helper and
one dashboard with per-language visibility, generated from the same catalogues.

## Honest-state architecture

Every component follows the root rules, and the gate tests them by rendering:

- unavailable / unknown / missing → "No data", "Offline" or "State unknown";
  never a sentinel (`| float(0)` is gated);
- counts state what answered (`4 of 6 reporting`);
- a summary count sensor (unpaid bills) is a hit above zero, but its zero is
  an answer only while the inputs it summarises answer too, because a count
  over dark inputs reads 0 without measuring anything;
- Needs attention says "nothing needs attention" **only** when every check
  answered; otherwise it states how many are not reporting;
- the air-con shows the reported mode as reported (an unknown mode is shown
  raw), and room / target only from the entity's own attributes.

## Safety boundaries in V3-native views

| Surface | V3 behaviour | Why |
|---|---|---|
| Parents' air-con | read-only; link to classic Parents' room controls | V3-008: no HVAC implementation until the contract is satisfied |
| Camera privacy / detection | read-only tiles | approval boundary: nothing may disable a camera |
| Bulb-power wall switches | read-only tiles | owner rule: avoid toggling physical power to smart bulbs |
| Sirens | not on native views (Security is carried, V2 treatment intact) | — |
| All lights off | `light.turn_off` on the three lights only | V2 also cut `switch.mainroomlight_switch_1`; recorded departure |

Each is enforced by `validate_dashboard.py` and `tests/v3`.

## Dependencies

- V3-native views: **native cards only**, no `card_mod`, no HACS. Styling is
  the theme's.
- Carried / classic views: as V2 — `custom:webrtc-camera` (6 camera subviews)
  and `card_mod` (217 uses). Their installation on the Green is not verified
  from here.
- Theme: `src/casaray_v3/themes/casaray_v3.yaml` (dark + light modes). Not in
  `/themes`, so no include can pick it up. Installing it is a deployment step.
- Kiosk: V2 at the baseline carries no `kiosk_mode` block (removed on
  `ha-deploy`, "kiosk mode lockout"); V3 matches. Restoring it is an owner
  decision.
