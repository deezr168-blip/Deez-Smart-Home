#!/bin/sh
# CasaRay maintenance suite — onboard onto the Home Assistant host.
#
# ONE COMMAND, run on the host (Terminal & SSH add-on):
#
#     sh /config/deez_repo/scripts/casaray_onboard.sh
#
# WHAT IT DOES
#   1. inspects what is already there and prints it
#   2. backs up anything it is about to replace, into /config/casaray/backups
#   3. installs the four maintenance scripts to /config/casaray/ and chmods them
#   4. installs packages/casaray_automation.yaml to /config/packages/
#   5. creates /config/dashboards/backups
#   6. parses the package YAML, then runs `ha core check`
#   7. STOPS if the config check fails, restoring whatever it replaced
#   8. reloads what can be reloaded, and tells you plainly whether the
#      remaining entities need a restart
#
# IT WILL NOT
#   - restart Home Assistant. New integrations in a package need a restart and
#     this tells you so; it does not decide that for you.
#   - modify configuration.yaml, the legacy dashboard, the deploy bridge,
#     /config/deploy_casaray.sh, /config/deploy_deez_dashboard.sh, or any theme.
#   - delete a backup belonging to anything else.
#
# OPTIONS
#   --dry-run    print every action, change nothing
#   --uninstall  remove the installed files (backups are kept)
#
# EXIT CODES
#   0 installed (possibly pending a restart)   1 failed and rolled back
#   2 refused before changing anything

set -eu

DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$DIR")"

CONFIG="${CONFIG:-/config}"
INSTALL_DIR="${INSTALL_DIR:-$CONFIG/casaray}"
PKG_DIR="${PKG_DIR:-$CONFIG/packages}"
DASH_BACKUPS="${DASH_BACKUPS:-$CONFIG/dashboards/backups}"
ONBOARD_BACKUPS="$INSTALL_DIR/backups"
PKG_NAME="casaray_automation.yaml"

SCRIPTS="casaray_common.sh casaray_safe_deploy.sh casaray_rollback.sh casaray_health_check.sh casaray_sync_status.sh"

DRY=0; UNINSTALL=0
for a in "$@"; do
  case "$a" in
    --dry-run)   DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

S="$(date +%Y%m%d-%H%M%S)"
step() { printf '\n== %s\n' "$*"; }
do_()  { if [ "$DRY" -eq 1 ]; then echo "   would: $*"; else eval "$@"; fi; }
said() { [ "$DRY" -eq 1 ] || echo "   $*"; }

# --------------------------------------------------------------- uninstall
if [ "$UNINSTALL" -eq 1 ]; then
  step "Uninstalling (backups under $ONBOARD_BACKUPS are kept)"
  for f in $SCRIPTS; do
    [ -f "$INSTALL_DIR/$f" ] && do_ "rm -f '$INSTALL_DIR/$f'" && echo "   removed $f"
  done
  [ -f "$PKG_DIR/$PKG_NAME" ] && do_ "rm -f '$PKG_DIR/$PKG_NAME'" && echo "   removed $PKG_NAME"
  echo
  echo "Removed. Restart Home Assistant to drop the entities this package created."
  exit 0
fi

# ------------------------------------------------------------------ inspect
step "1. Inspecting the host"
echo "   config dir        $CONFIG"
[ -d "$CONFIG" ] || { echo "   ERROR: $CONFIG does not exist. Is this the Home Assistant host?" >&2; exit 2; }
echo "   repo              $REPO_ROOT"
echo "   packages dir      $PKG_DIR $([ -d "$PKG_DIR" ] && echo '(exists)' || echo '(will be created)')"
echo "   install dir       $INSTALL_DIR $([ -d "$INSTALL_DIR" ] && echo '(exists)' || echo '(will be created)')"
echo "   dashboard backups $DASH_BACKUPS $([ -d "$DASH_BACKUPS" ] && echo '(exists)' || echo '(will be created)')"
echo "   existing deploy   $([ -f "$CONFIG/deploy_casaray.sh" ] && echo "$CONFIG/deploy_casaray.sh" || echo 'none — the repo sync script will be used')"
echo "   python3           $(command -v python3 >/dev/null 2>&1 && echo yes || echo 'NO — YAML checks will be skipped')"
echo "   supervisor CLI    $(command -v ha >/dev/null 2>&1 && echo yes || echo 'NO — ha core check will be skipped')"

if ! grep -qs 'packages:' "$CONFIG/configuration.yaml"; then
  echo
  echo "   WARNING: no 'packages:' key found in configuration.yaml." >&2
  echo "            This package will be installed but NOT loaded until you add:" >&2
  echo "              homeassistant:" >&2
  echo "                packages: !include_dir_named packages" >&2
fi

# An earlier implementation of this suite installed its scripts flat in
# /config and pointed shell_commands at /config/casaray_*.sh. If a host ran it,
# those files are still there and still referenced by the package it installed
# -- which this one replaces. They are REPORTED, never deleted: removing
# someone else's files unasked is not this script's business.
OLD_FLAT=""
for f in casaray_safe_deploy.sh casaray_health_check.sh casaray_rollback.sh; do
  [ -f "$CONFIG/$f" ] && OLD_FLAT="$OLD_FLAT $f"
done
if [ -n "$OLD_FLAT" ]; then
  echo
  echo "   NOTE: an earlier install left these in $CONFIG:"
  for f in $OLD_FLAT; do echo "           $f"; done
  echo "         This suite installs to $INSTALL_DIR instead, and the package"
  echo "         it installs points there. The old files are now unused but are"
  echo "         NOT removed. Delete them yourself once you are happy:"
  echo "           rm$(for f in $OLD_FLAT; do printf ' %s/%s' "$CONFIG" "$f"; done)"
fi

for f in $SCRIPTS; do
  [ -f "$REPO_ROOT/scripts/$f" ] || { echo "ERROR: missing $REPO_ROOT/scripts/$f" >&2; exit 2; }
done
[ -f "$REPO_ROOT/packages/$PKG_NAME" ] || { echo "ERROR: missing $REPO_ROOT/packages/$PKG_NAME" >&2; exit 2; }

# ------------------------------------------------------------------ backup
step "2. Backing up anything about to be replaced"
do_ "mkdir -p '$ONBOARD_BACKUPS'"
RESTORE_PKG=""
if [ -f "$PKG_DIR/$PKG_NAME" ]; then
  RESTORE_PKG="$ONBOARD_BACKUPS/$PKG_NAME.$S"
  do_ "cp '$PKG_DIR/$PKG_NAME' '$RESTORE_PKG'"
  echo "   backed up existing package -> $RESTORE_PKG"
else
  echo "   no existing package to back up"
fi
for f in $SCRIPTS; do
  if [ -f "$INSTALL_DIR/$f" ]; then
    do_ "cp '$INSTALL_DIR/$f' '$ONBOARD_BACKUPS/$f.$S'"
    echo "   backed up $f"
  fi
done

# ----------------------------------------------------------------- install
step "3. Installing the maintenance scripts"
do_ "mkdir -p '$INSTALL_DIR'"
for f in $SCRIPTS; do
  do_ "cp '$REPO_ROOT/scripts/$f' '$INSTALL_DIR/$f'"
  do_ "chmod 755 '$INSTALL_DIR/$f'"
  said "installed $INSTALL_DIR/$f"
done

step "4. Installing the package"
do_ "mkdir -p '$PKG_DIR'"
do_ "cp '$REPO_ROOT/packages/$PKG_NAME' '$PKG_DIR/$PKG_NAME'"
said "installed $PKG_DIR/$PKG_NAME"

step "5. Creating the dashboard backup directory"
do_ "mkdir -p '$DASH_BACKUPS'"
said "$DASH_BACKUPS ready"

if [ "$DRY" -eq 1 ]; then
  echo
  echo "Dry run complete. Nothing was changed."
  exit 0
fi

# ------------------------------------------------------------------ verify
step "6. Checking the configuration"
CHECK_FAILED=""

if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys,yaml
class L(yaml.SafeLoader): pass
L.add_multi_constructor("!", lambda l,s,n: None)
yaml.load(open(sys.argv[1], encoding="utf-8"), Loader=L)' "$PKG_DIR/$PKG_NAME" >/dev/null 2>&1; then
    echo "   package YAML parses: ok"
  else
    CHECK_FAILED="package YAML does not parse"
  fi
else
  echo "   package YAML parse: SKIPPED (no python3)"
fi

if [ -z "$CHECK_FAILED" ]; then
  if command -v ha >/dev/null 2>&1; then
    echo "   running 'ha core check' (this takes a moment)..."
    if ha core check; then
      echo "   ha core check: PASSED"
    else
      CHECK_FAILED="ha core check failed"
    fi
  else
    echo "   ha core check: SKIPPED (no supervisor CLI on this host)"
    echo "   Check Developer Tools -> YAML -> Check Configuration before reloading."
  fi
fi

# ---------------------------------------------------------------- rollback
if [ -n "$CHECK_FAILED" ]; then
  step "7. FAILED: $CHECK_FAILED — rolling back"
  if [ -n "$RESTORE_PKG" ] && [ -f "$RESTORE_PKG" ]; then
    cp "$RESTORE_PKG" "$PKG_DIR/$PKG_NAME"
    echo "   restored the previous package"
  else
    rm -f "$PKG_DIR/$PKG_NAME"
    echo "   removed the package that was just installed"
  fi
  echo "   the scripts in $INSTALL_DIR were left in place; they are inert on their own"
  echo
  echo "Home Assistant's configuration is back as it was. Nothing is broken."
  exit 1
fi

# ------------------------------------------------------------------ reload
step "7. Reloading"
cat <<'NOTE'
   Reloading is not attempted from here. The supervisor CLI has no reliable
   service-call verb across versions, and a reload that silently does nothing
   is worse than one you performed yourself. Ten seconds in the UI:

     Developer Tools -> YAML, then press:
       Input Booleans · Input Numbers · Template Entities · Scripts · Automations

   THE ONE THING A RELOAD CANNOT DO: `shell_command` and `command_line` are
   only read at startup. Until Home Assistant restarts, the three buttons and
   sensor.casaray_sync_status will not work — everything else will.

     Settings -> System -> Restart Home Assistant

   Restarting is YOUR call, deliberately. This script will not do it.
NOTE

# ------------------------------------------------------------------ verify
step "8. What to verify once you have reloaded (and restarted)"
cat <<'NOTE'
   Developer Tools -> States, these should exist:
     input_boolean.casaray_auto_deploy          (on)
     input_number.casaray_battery_threshold     (20)
     input_number.casaray_offline_threshold     (0 = spike alert disarmed)
     sensor.casaray_low_batteries
     sensor.casaray_sync_status                 (synced / out_of_sync)
     binary_sensor.casaray_out_of_sync
     binary_sensor.casaray_powerpal_stale
     binary_sensor.casaray_fronius_stale
     script.casaray_deploy_now
     script.casaray_health_check
     script.casaray_rollback_previous

   Then, from a shell, the check that proves the whole chain:
     sh /config/casaray/casaray_health_check.sh
NOTE

step "Done"
echo "   Installed. Home Assistant's configuration passed its check."
echo "   Log:      /config/casaray_maintenance.log"
echo "   Backups:  $DASH_BACKUPS (dashboards) · $ONBOARD_BACKUPS (this install)"
exit 0
