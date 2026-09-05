#!/bin/sh
set -eu

# One-time CasaRay YAML dashboard URL-path migration.
# Home Assistant requires YAML dashboard keys to contain a hyphen.
# CasaRay v2 originally used /casaray/<view>; this script migrates those
# internal navigation links to /casaray-v2/<view> so configuration.yaml can
# register the dashboard as `casaray-v2:` without breaking navigation.

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

TARGET="dashboards/casaray_v2.yaml"

if [ ! -f "$TARGET" ]; then
  echo "ERROR: $TARGET not found" >&2
  exit 1
fi

if ! git diff --quiet -- "$TARGET"; then
  echo "ERROR: $TARGET has uncommitted changes; refusing to modify it." >&2
  git status --short -- "$TARGET"
  exit 1
fi

before="$(grep -o '/casaray/' "$TARGET" | wc -l | tr -d ' ')"
if [ "$before" -eq 0 ]; then
  echo "No /casaray/ links found. Nothing to migrate."
  exit 0
fi

python3 - <<'PY'
from pathlib import Path
p = Path('dashboards/casaray_v2.yaml')
s = p.read_text(encoding='utf-8')
old = '/casaray/'
new = '/casaray-v2/'
if old not in s:
    raise SystemExit('ERROR: expected /casaray/ links were not found')
p.write_text(s.replace(old, new), encoding='utf-8')
PY

after_old="$(grep -o '/casaray/' "$TARGET" | wc -l | tr -d ' ')"
after_new="$(grep -o '/casaray-v2/' "$TARGET" | wc -l | tr -d ' ')"

if [ "$after_old" -ne 0 ]; then
  echo "ERROR: old /casaray/ links remain after migration" >&2
  exit 1
fi

if [ "$after_new" -ne "$before" ]; then
  echo "ERROR: migrated link count mismatch: before=$before after=$after_new" >&2
  exit 1
fi

git diff --check -- "$TARGET"

echo "CasaRay URL-path migration applied successfully."
echo "Migrated links: $after_new"
echo "New YAML dashboard key / URL prefix: casaray-v2"
echo "Next: run bash scripts/ha_validate.sh, inspect the diff, then commit."
