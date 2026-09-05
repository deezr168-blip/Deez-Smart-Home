#!/bin/sh
set -eu

# Copy the CasaRay v2 dashboard from the git clone into the directory Home
# Assistant actually reads.
#
# WHY THIS EXISTS
#
# configuration.yaml registers the dashboard as:
#     filename: dashboards/casaray_v2.yaml
# which Home Assistant resolves relative to /config. So HA reads
#     /config/dashboards/casaray_v2.yaml
# but the git clone lives at
#     /config/deez_repo/dashboards/casaray_v2.yaml
# Those are different files. Something has to bridge them.
#
# /config/deploy_deez_dashboard.sh does that for the legacy dashboard. It is a
# protected file under CLAUDE.md and MAINTENANCE.md and is NOT modified here.
# This script is a separate, additive helper: run it after each pull until the
# owner chooses to add CasaRay to the deploy bridge itself.
#
# WHAT IT WILL NOT DO
#
#   - It never touches dashboards/deez_smart_home.yaml. That is the rollback
#     baseline and the running system; the existing bridge owns it.
#   - It never writes outside /config/dashboards/.
#   - It refuses to copy a file that does not parse as YAML, so a half-written
#     or truncated pull cannot take the dashboard down.
#   - It keeps a timestamped backup of whatever it replaces.
#
# USAGE (on the Home Assistant host, Terminal & SSH add-on)
#
#     sh /config/deez_repo/scripts/sync_casaray_to_config.sh

REPO="${REPO:-/config/deez_repo}"
DEST="${DEST:-/config/dashboards}"
NAME="casaray_v2.yaml"

SRC="$REPO/dashboards/$NAME"
TGT="$DEST/$NAME"

echo "source: $SRC"
echo "target: $TGT"
echo

if [ ! -f "$SRC" ]; then
  echo "ERROR: source not found. Is $REPO the clone, and is it up to date?" >&2
  echo "       try: git -C $REPO fetch origin ha-deploy && git -C $REPO reset --hard origin/ha-deploy" >&2
  exit 1
fi

if [ ! -d "$DEST" ]; then
  echo "ERROR: $DEST does not exist. Home Assistant reads dashboards from there;" >&2
  echo "       if the legacy dashboard works, that directory should already exist." >&2
  exit 1
fi

# Refuse to publish a file that will not parse. A dashboard that fails to load
# is worse than one that is a day stale.
if command -v python3 >/dev/null 2>&1; then
  if ! err="$(python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1],encoding='utf-8'))" "$SRC" 2>&1)"; then
    echo "ERROR: $SRC does not parse as YAML. Refusing to copy." >&2
    echo "$err" | tail -3 >&2
    exit 1
  fi
  echo "yaml parse       : ok"
else
  echo "yaml parse       : SKIPPED (no python3 on this host)"
fi

links_new="$(grep -c '/casaray-v2/' "$SRC" || true)"
links_old="$(grep -c '/casaray/' "$SRC" || true)"
echo "casaray-v2 links : $links_new"
if [ "$links_old" -ne 0 ]; then
  echo "ERROR: $links_old stale /casaray/ links in the source. Expected none." >&2
  echo "       The clone is behind; pull again before syncing." >&2
  exit 1
fi

if [ -f "$TGT" ] && cmp -s "$SRC" "$TGT"; then
  echo
  echo "Already identical. Nothing to do."
  exit 0
fi

if [ -f "$TGT" ]; then
  BAK="$TGT.bak.$(date +%Y%m%d-%H%M%S)"
  cp "$TGT" "$BAK"
  echo "backup           : $BAK"
fi

cp "$SRC" "$TGT"
echo "copied           : yes"

echo
echo "Done. $NAME is now in place for Home Assistant."
echo "A NEW dashboard registration needs a full restart, not a Lovelace reload."
echo "An UPDATE to an already-registered dashboard needs only a browser refresh."
