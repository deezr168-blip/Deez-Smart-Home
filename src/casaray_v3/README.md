# CasaRay V3 sources — DEVELOPMENT ONLY — NOT DEPLOYED

Edit here; never edit the generated dashboards.

```sh
python3 scripts/v3/build_dashboard.py           # build every locale
python3 scripts/v3/build_dashboard.py --check   # fail if outputs are stale
python3 scripts/v3/validate_dashboard.py        # V3 gate
python3 -m unittest discover -s tests/v3        # regression tests
bash scripts/ha_validate.sh                     # repository gate (must stay green)
```

- New native view: add `views/<v2-path>.yaml`, list it in `manifest.yaml`
  `native:`. The V2 view becomes a `v2-<path>` classic subview automatically.
- New string: add the key to `i18n/en.yaml` first, then every other catalogue.
- Never write an entity ID that is not in `docs/live/states_export_2026-09-05.txt`.

Docs: `docs/casaray-v3/ARCHITECTURE.md`.
