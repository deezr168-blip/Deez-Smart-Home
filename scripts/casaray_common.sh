#!/bin/sh
# CasaRay maintenance — shared paths and helpers.
#
# Sourced by casaray_safe_deploy.sh, casaray_rollback.sh,
# casaray_health_check.sh and casaray_sync_status.sh. Not executable on its
# own; it defines and never acts.
#
# POSIX sh throughout: the Home Assistant OS Terminal add-on is BusyBox ash,
# not bash. No arrays, no [[ ]], no ${x^^}.
#
# Every path can be overridden from the environment so the suite can be
# exercised somewhere other than a live host:
#   REPO=/tmp/clone LIVE_DIR=/tmp/live sh scripts/casaray_health_check.sh

REPO="${REPO:-/config/deez_repo}"
LIVE_DIR="${LIVE_DIR:-/config/dashboards}"
NAME="${NAME:-casaray_v2.yaml}"

SRC="$REPO/dashboards/$NAME"
LIVE="$LIVE_DIR/$NAME"

# Our own backups live in their own directory with their own filename shape.
# The sync script's `.bak.<timestamp>` files sit directly in $LIVE_DIR and are
# NEVER touched by anything here -- pruning only ever looks inside $BACKUP_DIR,
# and only at the two prefixes below.
BACKUP_DIR="${BACKUP_DIR:-$LIVE_DIR/backups}"
BACKUP_PREFIX="casaray_v2.yaml.predeploy."
# A parallel implementation that reached ha-deploy first named its backups
# casaray_v2_predeploy_<ts>.yaml. A host that ran it has real backups under
# that name; they are counted, listed and pruned alongside ours so neither
# scheme can grow without limit. Anything NOT matching one of these two
# patterns -- the sync script's .bak.*, Home Assistant's own backups -- is
# still untouchable.
BACKUP_PREFIX_ALT="casaray_v2_predeploy_"
BACKUP_KEEP="${BACKUP_KEEP:-30}"

LOG="${CASARAY_LOG:-/config/casaray_maintenance.log}"

# Where the onboarding script installs these scripts on the host.
INSTALL_DIR="${INSTALL_DIR:-/config/casaray}"

ts()  { date +%Y%m%d-%H%M%S; }
now() { date '+%Y-%m-%d %H:%M:%S'; }

# log LEVEL MESSAGE... -- to stdout and, if the log is writable, to the log.
log() {
  _lvl="$1"; shift
  _line="$(now) [$_lvl] $*"
  echo "$_line"
  if [ -w "$(dirname "$LOG")" ] 2>/dev/null || [ -w "$LOG" ] 2>/dev/null; then
    echo "$_line" >> "$LOG" 2>/dev/null || true
  fi
}

# yaml_parses FILE -- true if python3 can load it. If there is no python3 the
# check is skipped rather than failed: refusing to deploy because the host
# lacks a checker would be worse than deploying an already-validated file.
yaml_parses() {
  [ -f "$1" ] || return 1
  if ! command -v python3 >/dev/null 2>&1; then
    return 0
  fi
  python3 -c 'import sys,yaml
class L(yaml.SafeLoader): pass
def _op(loader, suffix, node): return None
L.add_multi_constructor("!", _op)
yaml.load(open(sys.argv[1], encoding="utf-8"), Loader=L)' "$1" >/dev/null 2>&1
}

# have_python -- whether the YAML checks above are real or skipped.
have_python() { command -v python3 >/dev/null 2>&1; }

# ha_core_check -- 0 pass, 1 fail, 2 unavailable (no supervisor CLI here).
ha_core_check() {
  command -v ha >/dev/null 2>&1 || return 2
  ha core check >/dev/null 2>&1
}

# backup_count -- how many of OUR pre-deploy backups exist.
backup_count() {
  [ -d "$BACKUP_DIR" ] || { echo 0; return; }
  find "$BACKUP_DIR" -maxdepth 1 -type f \
       \( -name "$BACKUP_PREFIX*" -o -name "$BACKUP_PREFIX_ALT*" \) 2>/dev/null \
    | wc -l | tr -d ' '
}

# latest_backup -- newest pre-deploy backup path, or empty.
#
# The two naming schemes CANNOT be compared by sorting their filenames
# together, for the same reason prune_backups() handles them separately: `.`
# sorts before `_`, so every casaray_v2.yaml.predeploy.* file sorts below
# every casaray_v2_predeploy_* file regardless of date. A plain
# `sort | tail -1` across both therefore returns the newest file of the OLD
# scheme even when a far newer one exists under the new name -- which on a
# host carrying both means a bare `casaray_rollback.sh` silently restores a
# months-old dashboard. Found 2026-09-24 by casaray_disk_report.sh, against a
# fixture holding five September backups and one from August; it picked the
# August one.
#
# So: sort on the TIMESTAMP, not the filename. Every digit in the name is
# part of the timestamp in both schemes; the new scheme gives 14 of them
# (YYYYMMDD-HHMMSS) and the old gives 8 (YYYYMMDD), so the short ones are
# padded to 14 before comparing. That makes 20260815 read as 20260815000000,
# which is right: a backup dated only to the day is treated as its earliest
# moment.
latest_backup() {
  [ -d "$BACKUP_DIR" ] || return 0
  find "$BACKUP_DIR" -maxdepth 1 -type f \
       \( -name "$BACKUP_PREFIX*" -o -name "$BACKUP_PREFIX_ALT*" \) 2>/dev/null \
    | while read -r _f; do
        _digits=$(basename "$_f" | tr -cd '0-9')
        [ -n "$_digits" ] || continue
        # Pad right to 14 so schemes of different precision compare correctly.
        while [ "${#_digits}" -lt 14 ]; do _digits="${_digits}0"; done
        printf '%s\t%s\n' "$(echo "$_digits" | cut -c1-14)" "$_f"
      done \
    | sort | tail -1 | cut -f2-
}

# prune_backups -- keep the newest $BACKUP_KEEP of each naming scheme.
#
# Each scheme is pruned on its own rather than as one merged list: the two
# names sort lexically by prefix, not by time, so a merged sort would delete
# every file of one scheme before touching the other regardless of age. Within
# a scheme the timestamps are zero-padded, so a plain sort IS chronological.
#
# The patterns are anchored inside $BACKUP_DIR, so the sync script's .bak.*
# files and Home Assistant's own backups cannot be reached even if someone
# points BACKUP_DIR somewhere careless.
prune_backups() {
  [ -d "$BACKUP_DIR" ] || return 0
  for _pat in "$BACKUP_PREFIX" "$BACKUP_PREFIX_ALT"; do
    _n="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name "$_pat*" 2>/dev/null | wc -l | tr -d ' ')"
    [ "$_n" -gt "$BACKUP_KEEP" ] || continue
    _drop=$((_n - BACKUP_KEEP))
    find "$BACKUP_DIR" -maxdepth 1 -type f -name "$_pat*" 2>/dev/null \
      | sort | head -n "$_drop" \
      | while read -r _f; do
          rm -f "$_f" && log INFO "pruned old backup: $(basename "$_f")"
        done
  done
}

# sync_status -- synced | out_of_sync | missing_repo | missing_live
sync_status() {
  if [ ! -f "$SRC" ];  then echo missing_repo; return; fi
  if [ ! -f "$LIVE" ]; then echo missing_live; return; fi
  if cmp -s "$SRC" "$LIVE"; then echo synced; else echo out_of_sync; fi
}
