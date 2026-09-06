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
#   - It never writes outside /config/dashboards/ and /config/themes/.
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

# The dashboard declares `theme: CasaRay`, which lives in the theme file. A
# dashboard deployed without its theme falls back to the user's default and
# loses the background, the glass surfaces and the palette -- so the two are
# synced together rather than left as two things to remember.
THEME_DEST="${THEME_DEST:-/config/themes}"
THEME_NAME="deez_your_name.yaml"
THEME_SRC="$REPO/themes/$THEME_NAME"
THEME_TGT="$THEME_DEST/$THEME_NAME"

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

# --- theme -----------------------------------------------------------------
echo
if [ ! -f "$THEME_SRC" ]; then
  echo "WARNING: $THEME_SRC not found; theme not synced." >&2
elif [ ! -d "$THEME_DEST" ]; then
  echo "WARNING: $THEME_DEST does not exist, so the theme was not synced." >&2
  echo "         Create it and re-run, or CasaRay will render unthemed." >&2
elif [ -f "$THEME_TGT" ] && cmp -s "$THEME_SRC" "$THEME_TGT"; then
  echo "theme            : already identical"
else
  if command -v python3 >/dev/null 2>&1; then
    if ! err="$(python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1],encoding='utf-8'))" "$THEME_SRC" 2>&1)"; then
      echo "ERROR: $THEME_SRC does not parse as YAML. Refusing to copy it." >&2
      echo "$err" | tail -3 >&2
      exit 1
    fi
  fi
  if [ -f "$THEME_TGT" ]; then
    TBAK="$THEME_TGT.bak.$(date +%Y%m%d-%H%M%S)"
    cp "$THEME_TGT" "$TBAK"
    echo "theme backup     : $TBAK"
  fi
  cp "$THEME_SRC" "$THEME_TGT"
  echo "theme copied     : yes"
  echo
  echo "The theme changed. Reload it before looking at the dashboard:"
  echo "  Developer Tools -> YAML -> Reload Themes    (no restart needed)"
fi

echo
echo "Done. $NAME is now in place for Home Assistant."
echo "A NEW dashboard registration needs a full restart, not a Lovelace reload."
echo "An UPDATE to an already-registered dashboard needs only a browser refresh."
