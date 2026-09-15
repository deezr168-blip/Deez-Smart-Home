#!/bin/sh
# CasaRay health check — is the deployment chain sound right now?
#
# Reports, and exits non-zero if any REQUIRED check fails:
#   - repo clone present, source dashboard present and parsing
#   - live dashboard present and parsing
#   - repo vs live sync status
#   - how many pre-deploy backups exist
#   - `ha core check` result, where a supervisor CLI exists
#
# It reads files and calls `ha core check`. It never writes, never deploys and
# never needs a token, so it is safe to run from a button on the wall panel.
#
# out_of_sync is reported but is NOT a failure: a pending change is a normal
# state between a push and the nightly deploy. Missing or unparseable files
# are failures.
#
# USAGE
#   sh /config/casaray/casaray_health_check.sh
#   sh /config/casaray/casaray_health_check.sh --quiet    # one summary line
#
# EXIT CODES
#   0 healthy    1 one or more required checks failed

set -eu
DIR="$(dirname "$0")"
# shellcheck source=casaray_common.sh
. "$DIR/casaray_common.sh"

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

FAILED=0
WARNED=0

say() { [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"; }
ok()   { say "  ok    $*"; }
bad()  { say "  FAIL  $*"; FAILED=$((FAILED + 1)); }
warn() { say "  warn  $*"; WARNED=$((WARNED + 1)); }

say "CasaRay health check — $(now)"
say ""
say "paths"
say "  repo        $REPO"
say "  live        $LIVE"
say "  backups     $BACKUP_DIR"
say ""
say "checks"

# --- repo and source -------------------------------------------------------
if [ -d "$REPO" ]; then ok "repo clone present"; else bad "repo clone missing: $REPO"; fi

if [ -f "$SRC" ]; then
  ok "source dashboard present"
  if have_python; then
    if yaml_parses "$SRC"; then ok "source parses"; else bad "source does NOT parse"; fi
  else
    warn "no python3 on this host; YAML parsing not checked"
  fi
else
  bad "source dashboard missing: $SRC"
fi

# --- live ------------------------------------------------------------------
if [ -f "$LIVE" ]; then
  ok "live dashboard present"
  if have_python; then
    if yaml_parses "$LIVE"; then ok "live parses"; else bad "live does NOT parse"; fi
  fi
else
  bad "live dashboard missing: $LIVE"
fi

# --- sync ------------------------------------------------------------------
STATUS="$(sync_status)"
case "$STATUS" in
  synced)       ok   "repo and live are identical" ;;
  out_of_sync)  warn "repo and live DIFFER — a deploy is pending" ;;
  missing_repo) bad  "sync: source file missing" ;;
  missing_live) bad  "sync: live file missing" ;;
esac

# --- backups ---------------------------------------------------------------
BC="$(backup_count)"
if [ "$BC" -gt 0 ]; then
  ok "$BC pre-deploy backup(s), newest $(basename "$(latest_backup)")"
else
  warn "no pre-deploy backups yet — the first safe deploy will make one"
fi

# --- Home Assistant config -------------------------------------------------
if ha_core_check; then rc=0; else rc=$?; fi
case "$rc" in
  0) ok   "ha core check passed" ;;
  1) bad  "ha core check FAILED — run 'ha core check' to see why" ;;
  2) warn "no supervisor CLI here; ha core check not run" ;;
esac

say ""
if [ "$FAILED" -eq 0 ]; then
  say "RESULT: healthy ($WARNED warning(s))"
  [ "$QUIET" -eq 1 ] && echo "healthy: $STATUS, $BC backup(s), $WARNED warning(s)"
  exit 0
fi
say "RESULT: $FAILED check(s) FAILED ($WARNED warning(s))"
[ "$QUIET" -eq 1 ] && echo "UNHEALTHY: $FAILED failed, $STATUS, $BC backup(s)"
exit 1
