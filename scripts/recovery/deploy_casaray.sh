#!/bin/sh
# CasaRay — re-register the dashboard, from the Home Assistant Web Terminal (Terminal & SSH add-on).
#
# Root cause: CasaRay is a YAML-mode dashboard (url_path casaray-v2) registered in
# configuration.yaml. That file was lost and Home Assistant regenerated a default one, which
# registers nothing and no longer loads /config/packages (helpers + people -> unavailable).
# The dashboard file itself survives. This puts back exactly those two lines of config:
# scripts/recovery/casaray_config_block.yaml.
#
#   sh /tmp/deploy_casaray.sh check     read-only report (default)
#   sh /tmp/deploy_casaray.sh apply     fresh verified backup -> type APPLY -> append block ->
#                                       `ha core check` -> restart -> health check;
#                                       automatic rollback if the check fails or Core does not return
#   sh /tmp/deploy_casaray.sh verify    read-only health check
#   sh /tmp/deploy_casaray.sh rollback  type ROLLBACK -> previous configuration.yaml -> restart
#
# Needs only BusyBox sh, `ha`, `curl` and `grep` (no docker, no python). Never touches
# authentication, .storage, integrations, the legacy (UI) dashboard or the dashboard files.
set -u
MODE="${1:-check}"
SAFETY="${SAFETY:-b0206554}"
TTY="${RC_TTY:-/dev/tty}"
say() { echo "[casaray] $*"; }
die() { echo "[casaray] STOP: $*"; exit 1; }

C="${RC_HOST_CONFIG:-}"
if [ -z "$C" ]; then for d in /config /homeassistant; do [ -f "$d/configuration.yaml" ] && [ -d "$d/.storage" ] && { C=$d; break; }; done; fi
[ -n "$C" ] || die "cannot find the Home Assistant config folder (/config or /homeassistant)"
CFG="$C/configuration.yaml"; R="$C/_recovery/casaray"
DASH="$C/dashboards/casaray_v2.yaml"; THEME="$C/themes/deez_your_name.yaml"

BLOCK='
# --- CasaRay recovery (2026-09-29) ---------------------------------------
# Restores the two things the lost configuration.yaml provided for CasaRay.
# The legacy "Deez Smart Home" dashboard is a UI (storage) dashboard and is
# deliberately NOT listed here.
homeassistant:
  packages: !include_dir_named packages

lovelace:
  dashboards:
    casaray-v2:
      mode: yaml
      title: CasaRay
      icon: mdi:home-heart
      show_in_sidebar: true
      filename: dashboards/casaray_v2.yaml
# --- end CasaRay recovery -------------------------------------------------'

registered() { grep -q '^[[:space:]]*casaray-v2:' "$CFG"; }
# Core API: via the Supervisor proxy when the add-on has it, else the plain port (401 = up).
core_up() {
  if [ -n "${SUPERVISOR_TOKEN:-}" ]; then
    [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 -H "Authorization: Bearer $SUPERVISOR_TOKEN" http://supervisor/core/api/ 2>/dev/null)" = 200 ] && return 0
  fi
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://homeassistant:8123/api/ 2>/dev/null)
  [ "$c" = 401 ] || [ "$c" = 200 ]
}
state() {  # entity -> state via the Supervisor proxy, or "?" if not available here
  [ -n "${SUPERVISOR_TOKEN:-}" ] || { echo "?"; return; }
  curl -s --max-time 5 -H "Authorization: Bearer $SUPERVISOR_TOKEN" "http://supervisor/core/api/states/$1" 2>/dev/null \
    | sed -n 's/.*"state"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1 | grep . || echo "?"
}
health() {
  say "health:"
  for e in input_boolean.chinese_dashboard person.raymond_du person.ai_q_huang person.vinh_du input_boolean.elec_bill_paid; do
    printf '[casaray]   %-36s %s\n' "$e" "$(state "$e")"
  done
  say "  ('?' = not readable from this terminal; Claude will verify through its Home Assistant connection)"
}
report() {
  say "config folder: $C"
  say "Home Assistant: $(ha core info 2>/dev/null | grep -m1 '^version:' | sed 's/version: //')"
  say "configuration.yaml top-level keys: $(grep -oE '^[a-z_]+:' "$CFG" | tr -d ':' | tr '\n' ' ')"
  if registered; then say "casaray-v2 registration: PRESENT"; else say "casaray-v2 registration: missing  <- the cause"; fi
  [ -f "$DASH" ] && say "dashboard file: present ($(wc -c < "$DASH") bytes, $(grep -c '/casaray-v2/' "$DASH") internal links)" || say "dashboard file: MISSING"
  [ -f "$THEME" ] && say "theme file: present" || say "WARN theme file missing: CasaRay will render unthemed"
  n=$(ls "$C"/packages/*.yaml 2>/dev/null | wc -l); say "packages/*.yaml: $n file(s)"
  if [ "$n" -gt 0 ]; then
    grep -qs '^[[:space:]]*chinese_dashboard:' "$C"/packages/*.yaml && say "  chinese_dashboard is defined in packages -> language toggle will return" \
      || say "  WARN chinese_dashboard NOT found in packages -> it was in the lost config; needs rebuilding after this"
  fi
  ha backups info "$SAFETY" >/dev/null 2>&1 && say "safety backup $SAFETY: present" || say "WARN safety backup $SAFETY not found"
  say "free space: $(df -h "$C" | awk 'NR==2{print $4}')"
}
blockers() {
  B=""
  grep -qE '^homeassistant:' "$CFG" && B="$B configuration.yaml already has a top-level 'homeassistant:' key;"
  grep -qE '^lovelace:' "$CFG" && B="$B configuration.yaml already has a top-level 'lovelace:' key;"
  grep -qs '"url_path"[[:space:]]*:[[:space:]]*"casaray-v2"' "$C/.storage/lovelace_dashboards" && B="$B a UI dashboard already uses /casaray-v2;"
  [ -f "$DASH" ] || B="$B dashboards/casaray_v2.yaml is missing;"
  echo "$B"
}
restore_cfg() { cp -p "$R/configuration.yaml.pre" "$CFG" && say "configuration.yaml restored to the pre-deploy copy"; }
wait_core() {
  i=0; while ! core_up; do i=$((i+1)); [ $i -gt 90 ] && return 1; sleep "${RC_POLL:-10}"; done; return 0
}

case "$MODE" in
check)
  report
  B=$(blockers)
  if registered; then say "already registered: nothing to deploy (run: sh /tmp/deploy_casaray.sh verify)"
  elif [ -n "$B" ]; then say "BLOCKED (needs a manual merge, nothing changed):$B"
  else say "READY: 'apply' will append $(printf '%s\n' "$BLOCK" | wc -l) lines to configuration.yaml and restart Home Assistant."; fi
  say "OK: nothing changed" ;;
apply)
  report
  registered && die "casaray-v2 is already registered; nothing to do"
  B=$(blockers); [ -z "$B" ] || die "blocked:$B nothing changed"
  printf '[casaray] this will back up, add CasaRay to configuration.yaml and RESTART Home Assistant.\n[casaray] type APPLY to continue: '
  read -r ANS <"$TTY"; [ "$ANS" = APPLY ] || die "not confirmed; nothing changed"
  NAME="casaray-pre-registration-$(date +%Y%m%d-%H%M)"
  say "1/5 full backup: $NAME (a few minutes)"
  OUT=$(ha backups new --name "$NAME" 2>&1) || { echo "$OUT"; die "backup failed; nothing changed"; }
  SLUG=$(echo "$OUT" | sed -n 's/.*slug:[[:space:]]*\([0-9a-f]*\).*/\1/p' | head -1)
  { [ -n "$SLUG" ] && ha backups info "$SLUG" >/dev/null 2>&1; } || ha backups list 2>/dev/null | grep -q "$NAME" || { echo "$OUT"; die "backup not verified; nothing changed"; }
  say "    backup verified: ${SLUG:-$NAME}"
  mkdir -p "$R" && chmod 700 "$R"; cp -p "$CFG" "$R/configuration.yaml.pre"; echo "${SLUG:-$NAME}" > "$R/backup_slug"
  say "2/5 adding the CasaRay block to configuration.yaml"
  printf '%s\n' "$BLOCK" >> "$CFG"
  say "3/5 ha core check"
  if ! ha core check; then restore_cfg; die "configuration check failed: rolled back, Home Assistant was NOT restarted"; fi
  touch "$R/APPLIED"
  say "4/5 restarting Home Assistant (1-5 minutes)"
  ha core restart || say "WARN restart command returned an error; waiting anyway"
  if ! wait_core; then
    say "Core did not come back: rolling back and restarting"
    restore_cfg; rm -f "$R/APPLIED"; ha core restart; die "rolled back; send a screenshot of: ha core logs | tail -40"
  fi
  say "5/5 Core is up"; health
  say "DONE. Open CasaRay from the sidebar on the iPad (address /casaray-v2/home) and try the language toggle."
  say "Undo: sh /tmp/deploy_casaray.sh rollback" ;;
verify)
  core_up && say "Core API: up" || say "Core API: not answering"
  registered && say "casaray-v2 registration: PRESENT" || say "casaray-v2 registration: missing"
  health ;;
rollback)
  [ -f "$R/configuration.yaml.pre" ] || die "no pre-deploy copy found in $R"
  printf '[casaray] type ROLLBACK to restore the previous configuration.yaml and restart: '; read -r ANS <"$TTY"
  [ "$ANS" = ROLLBACK ] || die "not confirmed"
  restore_cfg; rm -f "$R/APPLIED"; ha core check || say "WARN check reported a problem with the restored file"
  ha core restart; wait_core && say "rollback done: Core is up" || say "Core not answering yet; wait and run verify" ;;
*) die "unknown mode: $MODE" ;;
esac
