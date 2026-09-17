#!/bin/sh
# CasaRay safe deploy — refresh, validate, back up, deploy, validate, roll back.
#
# WHAT IT DOES, IN ORDER
#   1. refresh      strictly fetch/reset to origin/ha-deploy (default)
#   2. pre-flight   source exists, parses, and dashboard_check.py passes
#   3. backup       timestamped copy of the live dashboard into backups/
#   4. deploy       runs the EXISTING deploy process, unmodified
#   5. post-flight  live exists, live parses, `ha core check` passes
#   6. rollback     restores the backup if post-flight validation fails
#   7. prune        keeps the newest 30 of OUR backups, nothing else
#
# It never restarts Home Assistant. A dashboard update needs a browser
# refresh, not a restart, and an unattended restart is not something this
# script should decide to do on its own.
#
# IMPORTANT
#   - Git refresh is ON by default so unattended deployments cannot silently
#     deploy a stale local clone.
#   - A failed fetch/reset aborts BEFORE the live dashboard is touched.
#   - dashboard_check.py is a mandatory pre-deployment gate when Python is
#     available; failure aborts BEFORE backup/deploy.
#
# USAGE (on the Home Assistant host)
#   sh /config/casaray/casaray_safe_deploy.sh
#   sh /config/casaray/casaray_safe_deploy.sh --dry-run
#   sh /config/casaray/casaray_safe_deploy.sh --no-pull   # manual/offline only
#
# EXIT CODES
#   0  deployed and validated, or already identical
#   1  deployment failed and the previous dashboard was restored
#   2  refused before touching anything (fetch/check/source/path failure)

set -eu

DIR="$(dirname "$0")"
# shellcheck source=casaray_common.sh
. "$DIR/casaray_common.sh"

PULL=1
DRY=0
for arg in "$@"; do
  case "$arg" in
    --pull)    PULL=1 ;;  # retained for backward compatibility
    --no-pull) PULL=0 ;;
    --dry-run) DRY=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

log INFO "=== safe deploy starting (pull=$PULL dry_run=$DRY) ==="

# ---------------------------------------------------------------- pre-flight
[ -d "$REPO" ] || { log ERROR "repo not found: $REPO"; exit 2; }
[ -d "$LIVE_DIR" ] || { log ERROR "live dashboard dir not found: $LIVE_DIR"; exit 2; }

# Strict by default: an unattended deployment must either prove it has the
# current ha-deploy branch or do nothing. Never fall back to stale local code.
if [ "$PULL" -eq 1 ]; then
  if ! command -v git >/dev/null 2>&1; then
    log ERROR "git is not on PATH; refusing deployment because strict refresh is enabled"
    exit 2
  fi

  log INFO "refresh: fetching origin/ha-deploy"
  if ! git -C "$REPO" fetch --quiet origin ha-deploy 2>>"$LOG"; then
    log ERROR "refresh: git fetch failed; refusing to deploy stale local code"
    exit 2
  fi

  log INFO "refresh: resetting clone to origin/ha-deploy"
  if ! git -C "$REPO" reset --quiet --hard origin/ha-deploy 2>>"$LOG"; then
    log ERROR "refresh: git reset failed; refusing deployment"
    exit 2
  fi

  log INFO "refresh: repository is current"
else
  log WARN "refresh: skipped by --no-pull (manual/offline override)"
fi

[ -f "$SRC" ] || { log ERROR "source dashboard missing: $SRC"; exit 2; }

if have_python; then
  if yaml_parses "$SRC"; then
    log INFO "pre-flight: source parses"
  else
    log ERROR "pre-flight: $SRC does not parse as YAML. Nothing was changed."
    exit 2
  fi
else
  log ERROR "pre-flight: python3 unavailable; refusing deployment because dashboard validation is mandatory"
  exit 2
fi

# Mandatory structural dashboard validation. This catches failures that
# `ha core check` does not: broken internal navigation, Jinja syntax errors,
# missing grid geometry, inert card properties and accidental mass damage.
DASH_CHECK="$REPO/scripts/dashboard_check.py"
[ -f "$DASH_CHECK" ] || {
  log ERROR "pre-flight: mandatory dashboard checker missing: $DASH_CHECK"
  exit 2
}

log INFO "pre-flight: running dashboard_check.py"
if python3 "$DASH_CHECK" "$SRC" >>"$LOG" 2>&1; then
  log INFO "pre-flight: dashboard structural check passed"
else
  log ERROR "pre-flight: dashboard structural check FAILED; refusing deployment"
  log ERROR "details: $LOG"
  exit 2
fi

if [ "$(sync_status)" = "synced" ]; then
  log INFO "already identical; nothing to deploy"
  log INFO "=== safe deploy finished: no change ==="
  exit 0
fi

if [ "$DRY" -eq 1 ]; then
  log INFO "dry run: would back up $LIVE and deploy $SRC"
  log INFO "=== safe deploy finished: dry run, nothing changed ==="
  exit 0
fi

# ------------------------------------------------------------------- backup
mkdir -p "$BACKUP_DIR"
BACKUP=""
if [ -f "$LIVE" ]; then
  BACKUP="$BACKUP_DIR/$BACKUP_PREFIX$(ts)"
  cp "$LIVE" "$BACKUP"
  log INFO "backup: $BACKUP"
else
  log WARN "no live dashboard to back up; this looks like a first install"
fi

# ------------------------------------------------------------------- deploy
# The EXISTING deploy process, whichever of the two this host has. Neither is
# modified here -- this only wraps them. /config/deploy_casaray.sh wins if it
# exists, because a host that has one is using it.
if [ -f /config/deploy_casaray.sh ]; then
  DEPLOY_CMD="sh /config/deploy_casaray.sh"
elif [ -f "$REPO/scripts/sync_casaray_to_config.sh" ]; then
  DEPLOY_CMD="sh $REPO/scripts/sync_casaray_to_config.sh"
else
  log ERROR "no deploy process found (/config/deploy_casaray.sh or the repo sync script)"
  exit 2
fi
log INFO "deploy: $DEPLOY_CMD"

# Pass the resolved paths down. On a real host these are the defaults the
# child already uses, so nothing changes; off a host it is what makes the
# whole chain testable against a scratch directory instead of /config.
DEPLOY_OK=1
if REPO="$REPO" DEST="$LIVE_DIR" $DEPLOY_CMD >>"$LOG" 2>&1; then
  log INFO "deploy: command succeeded"
else
  DEPLOY_OK=0
  log ERROR "deploy: command FAILED"
fi

# --------------------------------------------------------------- post-flight
FAIL=""
[ "$DEPLOY_OK" -eq 1 ] || FAIL="deploy command returned non-zero"

if [ -z "$FAIL" ] && [ ! -f "$LIVE" ]; then
  FAIL="live dashboard missing after deploy"
fi

if [ -z "$FAIL" ] && have_python && ! yaml_parses "$LIVE"; then
  FAIL="live dashboard does not parse after deploy"
fi

if [ -z "$FAIL" ]; then
  if ha_core_check; then rc=0; else rc=$?; fi
  case "$rc" in
    0) log INFO "post-flight: ha core check passed" ;;
    1) FAIL="ha core check failed" ;;
    2) FAIL="ha core check unavailable; refusing an unverified deployment" ;;
  esac
fi

# ----------------------------------------------------------------- rollback
if [ -n "$FAIL" ]; then
  log ERROR "post-flight FAILED: $FAIL"
  if [ -n "$BACKUP" ] && [ -f "$BACKUP" ]; then
    cp "$BACKUP" "$LIVE"
    log INFO "rolled back: restored $(basename "$BACKUP")"
    if have_python && yaml_parses "$LIVE"; then
      log INFO "rollback verified: restored dashboard parses"
    else
      log ERROR "ROLLBACK DID NOT VERIFY. Restore by hand from $BACKUP_DIR"
    fi
  else
    log ERROR "no backup to roll back to; the live dashboard is as the deploy left it"
  fi
  log INFO "=== safe deploy finished: FAILED ==="
  exit 1
fi

# -------------------------------------------------------------------- prune
prune_backups
log INFO "backups retained: $(backup_count) (keep $BACKUP_KEEP)"
log INFO "=== safe deploy finished: OK ==="
exit 0
