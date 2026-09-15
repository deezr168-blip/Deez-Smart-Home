#!/bin/sh
set -eu

LIVE="/config/dashboards/casaray_v2.yaml"
BACKUP_DIR="/config/dashboards/backups"
DEPLOY="/config/deploy_casaray.sh"
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

ROLLBACK=""
if [ -f "$LIVE" ]; then
  ROLLBACK="$BACKUP_DIR/casaray_v2_predeploy_${STAMP}.yaml"
  cp "$LIVE" "$ROLLBACK"
  echo "pre-deploy backup: $ROLLBACK"
fi

if [ ! -x "$DEPLOY" ]; then
  echo "ERROR: $DEPLOY is missing or not executable" >&2
  exit 2
fi

set +e
"$DEPLOY"
RC=$?
set -e

if [ "$RC" -ne 0 ]; then
  echo "ERROR: CasaRay deploy failed with return code $RC" >&2
  if [ -n "$ROLLBACK" ] && [ -f "$ROLLBACK" ]; then
    cp "$ROLLBACK" "$LIVE"
    echo "restored previous dashboard from $ROLLBACK" >&2
  fi
  exit "$RC"
fi

# Keep the newest 30 dedicated automation backups. Existing .bak files made by
# the sync script are intentionally left alone.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'casaray_v2_predeploy_*.yaml' -printf '%T@ %p\n' 2>/dev/null \
  | sort -nr \
  | awk 'NR>30 {sub(/^[^ ]+ /, ""); print}' \
  | while IFS= read -r old; do [ -n "$old" ] && rm -f "$old"; done

echo "CasaRay safe deploy complete"
