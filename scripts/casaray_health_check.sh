#!/bin/sh
set -eu

REPO="/config/deez_repo/dashboards/casaray_v2.yaml"
LIVE="/config/dashboards/casaray_v2.yaml"
BACKUP_DIR="/config/dashboards/backups"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

[ -f "$REPO" ] || fail "repo dashboard missing: $REPO"
[ -s "$LIVE" ] || fail "live dashboard missing or empty: $LIVE"

if command -v python3 >/dev/null 2>&1; then
  python3 -c "import yaml; yaml.safe_load(open('$REPO', encoding='utf-8')); yaml.safe_load(open('$LIVE', encoding='utf-8'))" \
    || fail "dashboard YAML parse failed"
fi

if cmp -s "$REPO" "$LIVE"; then
  echo "sync: synced"
else
  echo "sync: out_of_sync"
fi

if [ -d "$BACKUP_DIR" ]; then
  count="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'casaray_v2_*.yaml' 2>/dev/null | wc -l | tr -d ' ')"
else
  count=0
fi
echo "backups: $count"

ha core check >/tmp/casaray_ha_check.log 2>&1 || {
  tail -20 /tmp/casaray_ha_check.log >&2
  fail "Home Assistant core check failed"
}

echo "ha core check: ok"
echo "CasaRay health: ok"
