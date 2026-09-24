#!/bin/sh
# CasaRay rollback — restore the most recent pre-deploy backup.
#
# Only ever restores from $BACKUP_DIR and only files named with
# $BACKUP_PREFIX, so the sync script's .bak.* files and Home Assistant's own
# backups are out of reach. Verifies the candidate parses BEFORE overwriting
# the live dashboard: a corrupt backup must not be able to take the page down.
#
# USAGE
#   sh /config/casaray/casaray_rollback.sh            # newest backup
#   sh /config/casaray/casaray_rollback.sh --list     # show what is available
#   sh /config/casaray/casaray_rollback.sh <file>     # a specific one
#
# EXIT CODES
#   0 restored   1 restore failed   2 nothing to restore / bad argument

set -eu
DIR="$(dirname "$0")"
# shellcheck source=casaray_common.sh
. "$DIR/casaray_common.sh"

if [ "${1:-}" = "--list" ]; then
  # Ordered by timestamp, not filename: sorting the two naming schemes
  # together puts every `.predeploy.` file below every `_predeploy_` one
  # whatever the dates are, so "newest last" would be a lie on a host that
  # carries both. See latest_backup() in casaray_common.sh.
  echo "backups in $BACKUP_DIR (newest last):"
  if [ "$(backup_count)" -eq 0 ]; then
    echo "  (none)"
  else
    find "$BACKUP_DIR" -maxdepth 1 -type f \
         \( -name "$BACKUP_PREFIX*" -o -name "$BACKUP_PREFIX_ALT*" \) \
      | while read -r f; do
          _d=$(basename "$f" | tr -cd '0-9')
          [ -n "$_d" ] || continue
          while [ "${#_d}" -lt 14 ]; do _d="${_d}0"; done
          printf '%s\t%s\n' "$(echo "$_d" | cut -c1-14)" "$f"
        done | sort | cut -f2- \
      | while read -r f; do printf '  %s  %s\n' "$(basename "$f")" "$(wc -c <"$f" | tr -d ' ') bytes"; done
  fi
  exit 0
fi

if [ -n "${1:-}" ]; then
  CAND="$1"
  case "$CAND" in
    */*) : ;;
    *) CAND="$BACKUP_DIR/$CAND" ;;
  esac
  case "$(basename "$CAND")" in
    "$BACKUP_PREFIX"*|"$BACKUP_PREFIX_ALT"*) : ;;
    *) log ERROR "refusing: $CAND is not one of this suite's backups"; exit 2 ;;
  esac
else
  CAND="$(latest_backup)"
fi

[ -n "$CAND" ] && [ -f "$CAND" ] || { log ERROR "no backup to restore from $BACKUP_DIR"; exit 2; }

log INFO "=== rollback starting: $(basename "$CAND") ==="

if have_python && ! yaml_parses "$CAND"; then
  log ERROR "that backup does not parse. Refusing to restore it."
  log ERROR "try an older one:  sh $0 --list"
  exit 2
fi

if [ -f "$LIVE" ]; then
  PRE="$BACKUP_DIR/$BACKUP_PREFIX$(ts)"
  cp "$LIVE" "$PRE"
  log INFO "current dashboard saved first: $(basename "$PRE")"
fi

cp "$CAND" "$LIVE"
if have_python && ! yaml_parses "$LIVE"; then
  log ERROR "restored file does not parse. Something is wrong with $LIVE_DIR."
  exit 1
fi

log INFO "restored: $(basename "$CAND") -> $LIVE"
log INFO "Refresh the browser. No Home Assistant restart is needed."
log INFO "=== rollback finished: OK ==="
exit 0
