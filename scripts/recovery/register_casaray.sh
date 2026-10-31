#!/bin/sh
# CasaRay recovery -- register the CasaRay YAML dashboard, and nothing else (v1, 18/10/2026).
# Run in the Terminal & SSH add-on web terminal (BusyBox ash is enough; no python, git or docker):
#
#   sh /tmp/register_casaray.sh            same as 'check'
#   sh /tmp/register_casaray.sh check      read-only pre-flight; ends with READY or BLOCKED: <reasons>
#   sh /tmp/register_casaray.sh apply      check -> type APPLY -> full backup (verified) -> new run
#                                          folder with a byte-exact copy of configuration.yaml ->
#                                          theme (only if missing) -> append the registration block ->
#                                          'ha core check' -> restart -> wait for Core
#   sh /tmp/register_casaray.sh verify     read-only report: Core, registration, theme, last run
#   sh /tmp/register_casaray.sh rollback   type ROLLBACK -> undo the most recent register run -> restart
#
# /tmp does not survive an add-on restart or a reboot, so apply keeps a copy of this script in its
# run folder and prints that path for rollback.
#
# What it does. CasaRay (dashboards/casaray_v2.yaml, url_path casaray-v2) is a YAML dashboard. Its
# only registration lived in the configuration.yaml that was lost around 25/09; Home Assistant
# regenerated a default one. Core 2026.10.1 reads YAML dashboards once, at start-up, from
# 'lovelace: dashboards:' in configuration.yaml, so the fix is to append that one block and restart.
# The theme file is installed from the host's git clone first, if and only if it is missing and the
# clone's copy has the expected sha256, so one restart covers both.
#
# It puts everything back by itself (configuration.yaml byte-exact from the run folder; the theme
# file and themes/ folder only if this run created them) when: the backup cannot be made or
# verified (nothing has been changed at that point), 'ha core check' fails (no restart), a run-state
# write fails (no restart), it is stopped before the restart is requested (no restart), the restart
# cannot be confirmed (Supervisor refused it, or no sign of a new boot: the files go back so the
# change cannot load later, unwatched), Core does not answer after the restart, or Core comes back
# in recovery mode (both: restore, restart again). A restart counts as confirmed when 'ha core
# restart' exits 0, the probe saw Core go down, or the log shows a new container/Core start.
# 'ha core check' passes with a duplicate 'lovelace:' key, a missing dashboard file or a broken one,
# so those are pre-flight blockers or sha256 checks here, not left to the check. Any non-comment
# mention of 'lovelace' blocks, because a BOM, '? lovelace' or '!!str lovelace' is still the key.
# 'ha core check' output is never echoed or saved as-is (it can hold resolved !secret values):
# only where the errors are (integration, file, line, key).
#
# It never: adds 'homeassistant:' or 'packages:'; writes .storage (it only greps
# .storage/lovelace_dashboards for a UI dashboard already using /casaray-v2); opens secrets.yaml or
# any auth file; touches packages/, dashboards/, the legacy Deez Smart Home dashboard,
# automations/scripts/scenes, or deez_repo (the theme source is only read); overwrites an existing
# theme file; reads or writes anything under _recovery/casaray/ (the record of the 30/09 run) or an
# earlier run folder's copies; restores a backup; gives curl any credential. The liveness probe is
# GET /manifest.json, which Core serves without a login (in recovery mode too), so a probe is never
# logged as a failed login, never raises a 'Login attempt failed' notification and cannot get this
# terminal's IP banned. The Supervisor proxy is not used (this add-on has no Core API access).
#
# Supersedes deploy_casaray.sh (withdrawn), which (1) also appended 'homeassistant: packages:
# !include_dir_named packages' and so would have loaded packages/casaray_automation.yaml (12
# automations including a 03:30 self-deploy, 3 shell_commands); (2) overwrote
# _recovery/casaray/configuration.yaml.pre on every apply; (3) defaulted to a stale safety backup
# slug. Here the backup slug comes only from this run's own 'ha backups new' output, and every run
# gets a new folder _recovery/casaray-register-<YYYYMMDD-HHMMSS>/ (mode 700): configuration.yaml.pre,
# backup, manifest, state, run.log, check.log, register_casaray.sh (this script).
#
# Exit codes: 0 done / READY / verify OK; 1 blocked, refused or stopped with nothing changed;
# 2 usage; 3 apply failed and everything was put back; 4 needs attention (something could not be
# put back, a restart could not be confirmed, Core did not answer or came back in recovery mode
# after the last restart, or rollback found 'ha core check' failing and did not restart). Run
# state: prepared -> edited -> applied (manifest restart_confirmed=yes once a new boot is seen),
# or rolled-back / rollback-failed.
#
# Overrides (for tests): RC_HOST_CONFIG (config folder), RC_TTY (confirmation input, default
# /dev/tty), RC_POLL (seconds between Core probes, default 10), RC_WAIT_TRIES (probes, default 90),
# RC_MIN_FREE_KB (default 1048576 = 1 GB), TMPDIR (lock folder, default /tmp).

set -u
umask 077

H_DASH=77a4991626d6f8afcd9b78f235c34417d84d9f36c129549a386d8a66c324226c
H_THEME=ef7dc9fb2445a6baa2f597fc143927b6da2a60142aef2d0f76dc211f79fdb614
FIRST_LINE='# --- CasaRay registration (recovery 2026-10) ---------------------------'
# Any non-comment line that mentions lovelace. A narrower key pattern misses keys HA still reads as
# 'lovelace' (a UTF-8 BOM before it, '? lovelace', '!!str lovelace:'); the default file has none.
LOVELACE_RE='^[^#]*lovelace'
NL='
'
ESC=$(printf '\033')

num() { case $1 in '' | *[!0-9]*) printf '%s\n' "$2" ;; *) printf '%s\n' "$1" ;; esac; }
MODE=${1:-check}
[ $# -le 1 ] || MODE=usage
TTY=${RC_TTY:-/dev/tty}
POLL=$(num "${RC_POLL:-}" 10)
TRIES=$(num "${RC_WAIT_TRIES:-}" 90)
MIN_FREE_KB=$(num "${RC_MIN_FREE_KB:-}" 1048576)
LOCK=${TMPDIR:-/tmp}/casaray_register.lock
STAMP=$(date +%Y%m%d-%H%M%S)

# ---------------------------------------------------------------- output
LOG=""   # set once a run folder exists; earlier lines wait in BUF
BUF=""
out() {
  printf '%s\n' "$1"
  if [ -n "$LOG" ]; then printf '%s\n' "$1" >>"$LOG" 2>/dev/null; else BUF=$BUF$1$NL; fi
}
say() { out "[casaray] $*"; }
row() { out "$(printf '  %-32s %s' "$1" "$2")"; }
out_lines() {  # text -> one out() per non-empty line, indented, colour codes stripped; no subshell
  ol=$(printf '%s\n' "$1" | sed -e "s/$ESC\[[0-9;]*m//g")
  ol_ifs=$IFS; IFS=$NL; set -f
  for l in $ol; do out "      $l"; done
  set +f; IFS=$ol_ifs
}
start_log() { LOG=$1; printf '%s' "$BUF" >>"$LOG" 2>/dev/null; BUF=""; }

# ---------------------------------------------------------------- exit and signals
HAVE_LOCK=0
DIRTY=0      # 1 while configuration.yaml or the theme may differ from before the run, unresolved
RESTARTED=0  # 1 once 'ha core restart' has been started
UNDO_CMD="sh /tmp/register_casaray.sh"   # the run folder's own copy once there is one
RUN=""
PHASE=start
on_exit() {
  rc=$?
  trap - EXIT
  if [ "$DIRTY" = 1 ] && [ -n "$RUN" ]; then
    DIRTY=0
    say "stopped part-way through ($PHASE, exit $rc): putting configuration.yaml and the theme back"
    if plan_undo "$RUN" && undo_files "$RUN"; then
      set_state "$RUN" rolled-back
      if [ "$RESTARTED" = 1 ]; then say "put back. Home Assistant still runs the changed file: run 'ha core restart'"
      else say "put back; Home Assistant was NOT restarted"; fi
      rc=3
    else
      set_state "$RUN" rollback-failed
      say "COULD NOT put everything back; the original is $(rel "$RUN")/configuration.yaml.pre"
      rc=4
    fi
  elif [ "$PHASE" = backup ]; then
    say "nothing changed (a backup that had started may still finish in Supervisor)"
  elif [ "$PHASE" = restart ] && [ "$RESTARTED" = 1 ] && [ "$rc" -ge 128 ]; then
    say "stopped after the restart was requested: configuration.yaml keeps the CasaRay block, and"
    say "the restart was not confirmed. Run '$UNDO_CMD verify'; '$UNDO_CMD rollback' undoes it"
  fi
  if [ "$HAVE_LOCK" = 1 ]; then rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null; fi
  exit "$rc"
}
trap on_exit EXIT
trap 'say "interrupted"; exit 130' INT
trap 'say "terminated"; exit 143' TERM

take_lock() {
  if mkdir "$LOCK" 2>/dev/null; then
    HAVE_LOCK=1
    printf '%s\n' "$$" >"$LOCK/pid"
    return 0
  fi
  lp=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$lp" ] && kill -0 "$lp" 2>/dev/null; then
    say "STOP: another register_casaray.sh run (pid $lp) is active; nothing changed"
  else
    say "STOP: lock $LOCK is left from a run that is no longer active. Run 'check' to see"
    say "      its state; if no other run is active: rm -r $LOCK   (nothing changed)"
  fi
  return 1
}

# ---------------------------------------------------------------- config folder
C=""
if [ -n "${RC_HOST_CONFIG:-}" ]; then
  [ -f "$RC_HOST_CONFIG/configuration.yaml" ] && C=$RC_HOST_CONFIG
else
  for d in /config /homeassistant; do
    if [ -f "$d/configuration.yaml" ]; then C=$d; break; fi
  done
fi
case $MODE in
  check | apply | verify | rollback) ;;
  *) echo "usage: sh register_casaray.sh [check|apply|verify|rollback]" >&2; trap - EXIT; exit 2 ;;
esac
if [ -z "$C" ]; then
  say "STOP: cannot find the Home Assistant config folder (no configuration.yaml in /config or /homeassistant)"
  exit 1
fi
r=$(readlink -f "$C" 2>/dev/null) && [ -n "$r" ] && C=$r
CFG=$C/configuration.yaml
DASH=$C/dashboards/casaray_v2.yaml
THEMES=$C/themes
THEME=$THEMES/deez_your_name.yaml
SRC=$C/deez_repo/themes/deez_your_name.yaml
STORE=$C/.storage/lovelace_dashboards
REC=$C/_recovery
EVID=$REC/casaray

# ---------------------------------------------------------------- helpers
rel() { printf '%s\n' "${1#"$C"/}"; }
regular() { [ -f "$1" ] && [ ! -L "$1" ]; }
sha() {  # sha256 of a regular file (symlinks are not followed), or nothing
  regular "$1" || return 1
  h=$(sha256sum "$1" 2>/dev/null) || return 1
  printf '%s\n' "${h%% *}"
}
yget() {  # top-level key of the ha CLI's YAML output, quotes stripped
  printf '%s\n' "$2" | sed -n "s/^$1:[[:space:]]*//p" | head -n 1 | tr -d '\r' \
    | sed -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/"
}
mf_set() {  # atomic: a full disk can fail it, but never leaves a cut-off line as the last value
  { cat "$1/manifest" && printf '%s=%s\n' "$2" "$3"; } >"$1/manifest.new" 2>/dev/null \
    && mv -f "$1/manifest.new" "$1/manifest" && return 0
  rm -f "$1/manifest.new"
  return 1
}
mf_get() { sed -n "s/^$2=//p" "$1/manifest" 2>/dev/null | tail -n 1; }
set_state() { printf '%s\n' "$2" >"$1/state.new" && mv -f "$1/state.new" "$1/state"; }
get_state() { st=""; [ -f "$1/state" ] && read -r st <"$1/state"; printf '%s\n' "$st"; }
is_run() { [ -d "$1" ] && [ ! -L "$1" ]; }   # for d in "$REC"/casaray-register-*: sorted = oldest first
ends_nl() { lc=$(tail -c 1 "$1"; printf x); lc=${lc%x}; [ "$lc" = "$NL" ]; }
lines() { wc -l <"$1" | tr -d ' '; }
free_kb() {  # statfs first: BusyBox df needs the path's mount in /proc/mounts, which it may not find
  fs=$(stat -f -c '%a %S' "$C" 2>/dev/null)
  if printf '%s\n' "$fs" | grep -qxE '[0-9]+ [0-9]+'; then
    printf '%s\n' "$((${fs% *} * ${fs#* } / 1024))"
    return 0
  fi
  df -P -k "$C" 2>/dev/null | awk 'END { print $4 }'
}

block() {
  printf '%s\n' \
    "$FIRST_LINE" \
    '# YAML dashboard only. The legacy "Deez Smart Home" dashboard is a UI' \
    '# (storage) dashboard and is deliberately NOT listed here.' \
    'lovelace:' \
    '  dashboards:' \
    '    casaray-v2:' \
    '      mode: yaml' \
    '      title: CasaRay' \
    '      icon: mdi:home-heart' \
    '      show_in_sidebar: true' \
    '      filename: dashboards/casaray_v2.yaml' \
    '# --- end CasaRay registration ------------------------------------------'
}

# ---------------------------------------------------------------- Supervisor and Core
CORE_VERSION=""; CORE_PORT=8123; CORE_SSL=false; EXCL_DB=""
core_info() {
  ci=$(ha core info 2>/dev/null) || return 1
  CORE_VERSION=$(yget version "$ci")
  p=$(yget port "$ci"); case $p in '' | *[!0-9]*) ;; *) CORE_PORT=$p ;; esac
  [ "$(yget ssl "$ci")" = true ] && CORE_SSL=true
  EXCL_DB=$(yget backups_exclude_database "$ci")
  [ -n "$CORE_VERSION" ]
}
UP_HOW=""
core_up() {
  # Liveness probe of Core itself, with no credential: /manifest.json needs no login (the frontend
  # serves it, in recovery mode too; Core's HTTP server starts only once the frontend is set up).
  # Not /api/: its 401 is logged as a failed login, raises a 'Login attempt failed' notification
  # and, with http: login_attempts_threshold set, bans this terminal's IP. With ssl on, the
  # certificate is issued for the public name, not 'homeassistant', hence -k. -q: no ~/.curlrc.
  if [ "$CORE_SSL" = true ]; then
    code=$(curl -q -s -k -o /dev/null -w '%{http_code}' --max-time 5 "https://homeassistant:$CORE_PORT/manifest.json" 2>/dev/null)
  else
    code=$(curl -q -s -o /dev/null -w '%{http_code}' --max-time 5 "http://homeassistant:$CORE_PORT/manifest.json" 2>/dev/null)
  fi
  case $code in
    200) UP_HOW="homeassistant:$CORE_PORT/manifest.json, HTTP 200"; return 0 ;;
    403) UP_HOW="HTTP 403: Core has banned this terminal's IP (ip_bans.yaml)"; return 1 ;;
  esac
  UP_HOW="no answer (HTTP ${code:-none})"
  return 1
}
WC_DOWN=0    # 1 when the last wait_core saw Core not answering at least once
wait_core() {
  w=0; WC_DOWN=0
  while [ "$w" -lt "$TRIES" ]; do
    if core_up; then return 0; fi
    WC_DOWN=1
    w=$((w + 1))
    sleep "$POLL"
  done
  return 1
}
# -n 2, not -n 1: the CLI turns -n 1 into 'Range: entries=:0:', which the journal gateway reads as
# "from the head", so it would stream the whole retained journal (up to 500 MB) before the restart.
log_marker() { ha core logs -n 2 2>/dev/null | tr -d '\r' | sed '/^[[:space:]]*$/d' | tail -n 1; }
# recovery_after <marker>: 0 = Core logged recovery mode after the marker line, 1 = it did not,
# 2 = unknown (no marker, the marker is no longer in the log window, or nothing after it: a restart
# always logs new lines, so an empty tail means the log could not be read, e.g. an error body)
POSTLOG=""
recovery_after() {
  POSTLOG=""
  [ -n "$1" ] || return 2
  all=$(ha core logs -n 1000 2>/dev/null | tr -d '\r') || return 2
  POSTLOG=$(printf '%s\n' "$all" | MARK=$1 awk 'BEGIN { m = ENVIRON["MARK"] }
    { l[NR] = $0 } $0 == m { n = NR }
    END { if (!n) exit 3; for (i = n + 1; i <= NR; i++) print l[i] }') || { POSTLOG=""; return 2; }
  printf '%s\n' "$POSTLOG" | grep -q '[^[:space:]]' || return 2
  printf '%s\n' "$POSTLOG" | grep -qiE 'activating recovery mode|starting in recovery mode' && return 0
  return 1
}
# A new boot in the log after the marker: the s6 init of the Core container, or Core's own start.
BOOT_RE='s6-rc: info: service legacy-services successfully started|home assistant initialized in|activating recovery mode|starting in recovery mode'
# restart_core <marker>: request a restart and wait for Core. 0 = Core answers and a new boot is
# confirmed; 1 = Core does not answer; 2 = Core answers but nothing shows that it restarted (e.g.
# Supervisor refused: an offline database migration, another Core job). Sets RS_RC, RS_ERR, RECM
# (recovery_after's result) and UP_HOW.
RS_RC=0; RS_ERR=""; RECM=2
restart_core() {
  RESTARTED=1
  rs_out=$(ha core restart 2>&1)
  RS_RC=$?
  [ -n "$LOG" ] && printf '%s\n' "$rs_out" >>"$LOG" 2>/dev/null
  RS_ERR=$(printf '%s\n' "$rs_out" | sed -e "s/$ESC\[[0-9;]*m//g" | tr -d '\r' | grep '[^[:space:]]' | tail -n 1 | cut -c1-200)
  [ "$RS_RC" -eq 0 ] || say "WARN 'ha core restart' returned $RS_RC: ${RS_ERR:-no message} (waiting anyway)"
  RECM=2
  wait_core || return 1
  say "    Core answers ($UP_HOW)"
  recovery_after "$1"
  RECM=$?
  if [ "$RS_RC" -eq 0 ] || [ "$WC_DOWN" = 1 ] || printf '%s\n' "$POSTLOG" | grep -qiE "$BOOT_RE"; then return 0; fi
  return 2
}
# check_where: 'ha core check' output on stdin -> where the errors are (integration, file, line,
# key), one line each. Never a value: messages and dumps can hold resolved !secret values.
Q="'"
check_where() {
  sed -e "s/$ESC\[[0-9;]*m//g" -e 's/\r$//' -e 's/^[[:space:]]*//' -e 's/^- //' | sed -n \
    -e "s/^\(Invalid config for ${Q}[^${Q}]*${Q} at [^,]*, line [0-9]*\).* for dictionary value \(${Q}[^${Q}]*${Q}\).*/\1 (key \2)/p" \
    -e "t" \
    -e "s/^\(Invalid config for ${Q}[^${Q}]*${Q} at [^,]*, line [0-9]*\).*/\1/p" \
    -e "t" \
    -e "s/^\(Invalid config for ${Q}[^${Q}]*${Q}\).*/\1/p" \
    -e "t" \
    -e 's/^\(Fatal error while loading config\).*\(Secret [A-Za-z0-9_]* not defined\).*/\1: \2/p' \
    -e "t" \
    -e 's/^\(Fatal error while loading config\).*/\1/p' \
    -e "t" \
    -e 's/^\(Secret [A-Za-z0-9_]* not defined\)$/\1/p' \
    -e "t" \
    -e 's/^in "\([^"]*\)", \(line [0-9]*, column [0-9]*\)$/in \1, \2/p' \
    -e "t" \
    -e 's/^\(Integration error: [A-Za-z0-9_.]*\).*/\1/p' \
    -e "t" \
    -e "s/^\(Platform error ${Q}[A-Za-z0-9_.]*${Q}\).*/\1/p" \
    | awk '!seen[$0]++' | head -n 8
}
CHECK_WHERE=""
run_check() {  # <log file> -> 0 = passed; the log gets check_where's lines, never the raw output
  ck=$(ha core check 2>&1)
  ckrc=$?
  CHECK_WHERE=$(printf '%s\n' "$ck" | check_where)
  ck=""
  { printf 'ha core check exit %s\n' "$ckrc"
    if [ "$ckrc" -ne 0 ]; then
      printf '%s\n' "${CHECK_WHERE:-no error location found in the output}"
      printf '%s\n' "(values are left out: run 'ha core check' for the full text; it can show values from secrets.yaml)"
    fi; } >"$1" 2>/dev/null
  return "$ckrc"
}

# ---------------------------------------------------------------- undo
UNDO_CFG=""; UNDO_THEME=""; UNDO_DIR=""; UNDO_WHY=""
plan_undo() {  # run folder -> sets UNDO_*; 1 = cannot be undone safely
  pre=$1/configuration.yaml.pre
  want_pre=$(mf_get "$1" cfg_sha256_before)
  want_new=$(mf_get "$1" cfg_sha256_after)
  cur=$(sha "$CFG")
  UNDO_WHY=""
  # The file being byte-identical to what this run built is stronger evidence than the state word,
  # so it is tested first: a state write can fail (a full disk) after the file was replaced.
  if [ -n "$want_pre" ] && [ "$cur" = "$want_pre" ]; then
    UNDO_CFG=none
  elif [ -n "$want_new" ] && [ "$cur" = "$want_new" ]; then
    if [ "$(sha "$pre")" = "$want_pre" ]; then UNDO_CFG=restore
    else UNDO_CFG=refuse; UNDO_WHY="the saved copy $(rel "$pre") does not match its recorded sha256"; fi
  elif [ "$(get_state "$1")" = prepared ]; then
    UNDO_CFG=untouched      # 'edited' is recorded (checked) before the replace, so this run never wrote it
  else
    UNDO_CFG=refuse
    UNDO_WHY="configuration.yaml has changed since this run wrote it; restoring the copy would discard those changes (remove the CasaRay block by hand instead)"
  fi
  case $(mf_get "$1" theme_created) in
    yes)
      if regular "$THEME" && [ "$(sha "$THEME")" = "$H_THEME" ]; then UNDO_THEME=remove
      elif [ -e "$THEME" ] || [ -L "$THEME" ]; then UNDO_THEME=keep-differs
      else UNDO_THEME=none; fi ;;
    pending)  # intent only: remove it only if it is this run's own file (theme.new is its hard link)
      if regular "$THEME" && [ -e "$1/theme.new" ] && [ "$THEME" -ef "$1/theme.new" ]; then UNDO_THEME=remove
      elif [ -e "$THEME" ] || [ -L "$THEME" ]; then UNDO_THEME=keep-other
      else UNDO_THEME=none; fi ;;
    *) UNDO_THEME=none ;;
  esac
  case $(mf_get "$1" themes_dir_created) in
    yes | pending) if [ -d "$THEMES" ] && [ ! -L "$THEMES" ]; then UNDO_DIR=remove; else UNDO_DIR=none; fi ;;
    *) UNDO_DIR=none ;;
  esac
  [ "$UNDO_CFG" != refuse ]
}
undo_files() {  # run folder; follows plan_undo; 0 = configuration.yaml and theme are as before the run
  uf=0
  case $UNDO_CFG in
    none) say "  configuration.yaml: already as before the run" ;;
    untouched) say "  configuration.yaml: never replaced by this run; left as it is" ;;
    restore)
      if cp -p "$1/configuration.yaml.pre" "$1/configuration.yaml.restore" \
        && mv -f "$1/configuration.yaml.restore" "$CFG" && cmp -s "$1/configuration.yaml.pre" "$CFG"; then
        say "  configuration.yaml: restored byte-exact from $(rel "$1")/configuration.yaml.pre"
      else
        say "  configuration.yaml: RESTORE FAILED"; uf=1
      fi ;;
    *) say "  configuration.yaml: NOT restored: $UNDO_WHY"; uf=1 ;;
  esac
  case $UNDO_THEME in
    remove)
      if rm -f "$THEME" && [ ! -e "$THEME" ]; then say "  themes/deez_your_name.yaml: removed (this run installed it)"
      else say "  themes/deez_your_name.yaml: could NOT be removed"; uf=1; fi ;;
    keep-differs) say "  WARN themes/deez_your_name.yaml differs from what this run installed: left alone" ;;
    keep-other) say "  WARN themes/deez_your_name.yaml was not installed by this run (it stopped first): left alone" ;;
  esac
  [ -e "$1/theme.new" ] && rm -f "$1/theme.new"
  if [ "$UNDO_DIR" = remove ]; then
    if rmdir "$THEMES" 2>/dev/null; then say "  themes/: removed (this run created it)"
    else say "  themes/: not empty, left in place"; fi
  fi
  return "$uf"
}

# ---------------------------------------------------------------- pre-flight (read-only)
BLOCKERS=""; WARNS=""; THEME_ACTION=""
blocker() { BLOCKERS=${BLOCKERS:+$BLOCKERS; }$1; }
warn() { WARNS=$WARNS$1$NL; }
preflight() {
  if ! command -v ha >/dev/null 2>&1; then
    row "Supervisor CLI" "MISSING"; blocker "the 'ha' command is missing (run this in the Terminal & SSH add-on)"
  elif core_info; then
    row "Home Assistant Core" "$CORE_VERSION (port $CORE_PORT, ssl $CORE_SSL, backups exclude database: ${EXCL_DB:-?})"
  else
    row "Home Assistant Core" "'ha core info' did not answer"; blocker "the Supervisor CLI does not answer ('ha core info')"
  fi

  if [ -L "$CFG" ] || ! regular "$CFG"; then
    row "configuration.yaml" "NOT a regular file"; blocker "configuration.yaml is a symlink or not a regular file"
  else
    row "configuration.yaml" "$(wc -c <"$CFG" | tr -d ' ') bytes, $(lines "$CFG") lines, sha256 $(sha "$CFG" | cut -c1-12)..."
    if grep -qE "$LOVELACE_RE" "$CFG"; then
      row "  lovelace (outside comments)" "PRESENT"; blocker "configuration.yaml mentions lovelace outside a comment, so it may already have a top-level 'lovelace:' key (a second one would silently win; merge by hand)"
    else row "  lovelace (outside comments)" "no"; fi
    if grep -q 'casaray-v2' "$CFG"; then
      row "  casaray-v2" "ALREADY MENTIONED"; blocker "configuration.yaml already mentions casaray-v2 (run 'verify')"
    else row "  casaray-v2" "not registered"; fi
    if grep -qE '^[[:space:]]+themes:[[:space:]]*!include_dir_merge_named[[:space:]]+themes/?[[:space:]]*$' "$CFG"; then
      row "  themes/ loaded" "yes"
    else row "  themes/ loaded" "NO"; warn "configuration.yaml does not load 'themes: !include_dir_merge_named themes'; the theme file will not be read (not changed by this script)"; fi
    if grep -qE '^[[:space:]]+packages:' "$CFG"; then
      warn "configuration.yaml loads packages; a package could also define lovelace: (not checked here)"
    fi
  fi

  if [ -L "$STORE" ] || { [ -e "$STORE" ] && [ ! -f "$STORE" ]; }; then
    row ".storage/lovelace_dashboards" "NOT a regular file (not read)"
    blocker ".storage/lovelace_dashboards is a symlink or not a regular file; cannot rule out a UI dashboard at /casaray-v2"
  elif [ -e "$STORE" ]; then
    grep -qE '"url_path"[[:space:]]*:[[:space:]]*"casaray-v2"' "$STORE" 2>/dev/null
    case $? in
      0) row ".storage/lovelace_dashboards" "a UI dashboard USES /casaray-v2"
         blocker "a UI (storage) dashboard already uses url_path casaray-v2 (delete it in Settings > Dashboards first)" ;;
      1) row ".storage/lovelace_dashboards" "casaray-v2 not used" ;;
      *) row ".storage/lovelace_dashboards" "could not be read"
         blocker ".storage/lovelace_dashboards could not be read; cannot rule out a UI dashboard at /casaray-v2" ;;
    esac
  else row ".storage/lovelace_dashboards" "not present"; fi

  if regular "$DASH" && [ -s "$DASH" ]; then
    if [ "$(sha "$DASH")" = "$H_DASH" ]; then row "dashboards/casaray_v2.yaml" "present, sha256 MATCHES git"
    else row "dashboards/casaray_v2.yaml" "present, sha256 DIFFERS from git"
      warn "dashboards/casaray_v2.yaml differs from git (sha256 $(sha "$DASH" | cut -c1-12)...); CasaRay renders whatever is on disk"; fi
  else
    row "dashboards/casaray_v2.yaml" "MISSING (or empty, or a symlink)"; blocker "dashboards/casaray_v2.yaml is missing, empty or a symlink"
  fi

  if [ -e "$THEMES" ] && { [ -L "$THEMES" ] || [ ! -d "$THEMES" ]; }; then
    row "themes/" "NOT a folder"; blocker "themes exists but is not a plain folder"; THEME_ACTION=none
  elif [ -e "$THEME" ] || [ -L "$THEME" ]; then
    if regular "$THEME" && [ "$(sha "$THEME")" = "$H_THEME" ]; then
      row "themes/deez_your_name.yaml" "present, sha256 MATCHES git"; THEME_ACTION=keep
    else
      row "themes/deez_your_name.yaml" "present, DIFFERS from git (left alone)"; THEME_ACTION=keep
      warn "themes/deez_your_name.yaml differs from git; it is left alone, never overwritten"
    fi
  elif regular "$SRC" && [ "$(sha "$SRC")" = "$H_THEME" ]; then
    row "themes/deez_your_name.yaml" "MISSING; deez_repo copy verified, will be installed"; THEME_ACTION=install
  else
    row "themes/deez_your_name.yaml" "MISSING; no verified source"; THEME_ACTION=none
    blocker "themes/deez_your_name.yaml is missing and deez_repo/themes/deez_your_name.yaml is missing or has the wrong sha256"
  fi

  kb=$(free_kb)
  case $kb in
    '' | *[!0-9]*) row "free space" "unknown"; blocker "could not read the free space of the config folder" ;;
    *) row "free space" "$((kb / 1024)) MB"
       [ "$kb" -ge "$MIN_FREE_KB" ] || blocker "less than $((MIN_FREE_KB / 1024)) MB free for the backup" ;;
  esac

  if ! command -v curl >/dev/null 2>&1; then
    row "Core liveness probe" "curl MISSING"; blocker "curl is missing"
  elif core_up; then row "Core liveness probe" "answers ($UP_HOW)"
  else
    row "Core liveness probe" "$UP_HOW"
    blocker "Core does not answer the liveness probe from this terminal ($UP_HOW), so a restart could not be verified"
  fi

  nruns=0
  for d in "$REC"/casaray-register-*; do
    is_run "$d" || continue
    nruns=$((nruns + 1))
    s=$(get_state "$d")
    row "earlier run ${d##*/}" "${s:-no state}"
    case $s in
      rolled-back) ;;
      prepared | edited | applied | rollback-failed)
        blocker "earlier register run ${d##*/} is still marked '$s' (run 'verify', or 'rollback' to undo it)" ;;
      *) warn "run folder ${d##*/} has no state (it stopped before changing anything)" ;;
    esac
  done
  [ "$nruns" -gt 0 ] || row "earlier register runs" "none"
  if [ -d "$EVID" ]; then row "_recovery/casaray/ (30/09)" "present; never read or changed here"; fi
  if [ "$HAVE_LOCK" = 0 ] && [ -d "$LOCK" ]; then warn "lock $LOCK exists: another run may be active"; fi
}
finish_report() {  # prints WARN lines and READY / BLOCKED; 0 = READY
  fr_ifs=$IFS; IFS=$NL; set -f
  for l in $WARNS; do out "WARN: $l"; done
  set +f; IFS=$fr_ifs
  if [ -n "$BLOCKERS" ]; then out "BLOCKED: $BLOCKERS"; return 1; fi
  out "READY"
  return 0
}

# ---------------------------------------------------------------- confirmation
confirm() {
  if ! { : <"$TTY"; } 2>/dev/null; then
    say "STOP: cannot read a confirmation from $TTY; nothing changed"
    return 1
  fi
  printf '[casaray] type %s to continue (anything else stops): ' "$1"
  ans=""
  read -r ans <"$TTY"
  printf '\n'
  if [ "$ans" = "$1" ]; then say "confirmed ($1)"; return 0; fi
  say "not confirmed; nothing changed"
  return 1
}

# ---------------------------------------------------------------- apply
fail_apply() {  # reason -- before any restart; puts everything back
  say "STOP: $1"
  say "putting everything back:"
  if plan_undo "$RUN" && undo_files "$RUN"; then
    DIRTY=0
    set_state "$RUN" rolled-back
    say "everything is back as before. Home Assistant was NOT restarted. Backup: $SLUG"
    exit 3
  fi
  DIRTY=0
  set_state "$RUN" rollback-failed
  say "NOT everything could be put back; the original is $(rel "$RUN")/configuration.yaml.pre"
  exit 4
}
do_apply() {
  take_lock || exit 1
  out "CasaRay register v1 (apply)   config folder: $C"
  preflight
  if ! finish_report; then say "nothing changed"; exit 1; fi
  BNAME=casaray-pre-register-${STAMP%??}
  RUN=$REC/casaray-register-$STAMP
  say "PLAN -- nothing has changed yet. After you type APPLY:"
  say "  1. full backup '$BNAME', verified with 'ha backups info' (several minutes)"
  say "  2. new folder $(rel "$RUN")/ with a byte-exact copy of configuration.yaml"
  if [ "$THEME_ACTION" = install ]; then
    say "  3. install themes/deez_your_name.yaml from deez_repo (sha256 verified)"
  else say "  3. themes/deez_your_name.yaml is already there: not touched"; fi
  if ends_nl "$CFG" || [ ! -s "$CFG" ]; then say "  4. append these 12 lines to configuration.yaml:"
  else say "  4. append a newline and these 12 lines to configuration.yaml:"; fi
  out_lines "$(block)"
  say "  5. 'ha core check'; if it fails: put everything back and stop WITHOUT restarting"
  say "  6. 'ha core restart', then probe Core up to $TRIES times, $POLL s apart. If the restart cannot be"
  say "     confirmed (e.g. Supervisor refuses it): put everything back, no restart. If Core does not"
  say "     come back, or comes back in recovery mode: put everything back and restart again"
  say "  This page disconnects while Home Assistant restarts. The script keeps running: reopen the"
  say "  Terminal panel to see the result (it is also saved in the run folder's run.log)."
  confirm APPLY || exit 1
  trap '' HUP

  PHASE=backup
  say "1/6 full backup '$BNAME' (Supervisor is busy until it finishes)"
  bout=$(ha backups new --name "$BNAME" 2>&1)
  brc=$?
  SLUG=$(printf '%s\n' "$bout" | sed -n 's/^slug:[[:space:]]*//p' | tail -n 1 | tr -d "\"' \r")
  if [ "$brc" -ne 0 ] || ! printf '%s\n' "$SLUG" | grep -qxE '[0-9a-f]{8}'; then
    out_lines "$(printf '%s\n' "$bout" | tail -n 8)"
    say "STOP: the backup did not complete (ha exit $brc, slug '${SLUG:-none}'); nothing changed"
    PHASE=stopped; exit 1
  fi
  binfo=$(ha backups info "$SLUG" 2>&1)
  irc=$?
  b_slug=$(yget slug "$binfo"); b_type=$(yget type "$binfo"); b_name=$(yget name "$binfo")
  b_core=$(yget homeassistant "$binfo"); b_bytes=$(yget size_bytes "$binfo"); b_mb=$(yget size "$binfo")
  b_date=$(yget date "$binfo"); b_prot=$(yget protected "$binfo"); b_xdb=$(yget homeassistant_exclude_database "$binfo")
  bad=""
  [ "$irc" -eq 0 ] || bad="$bad 'ha backups info' failed;"
  [ "$b_slug" = "$SLUG" ] || bad="$bad slug;"
  [ "$b_type" = full ] || bad="$bad type '$b_type' is not full;"
  [ "$b_name" = "$BNAME" ] || bad="$bad name;"
  case $b_core in '' | null) bad="$bad no Home Assistant config in it;" ;; esac
  case $b_bytes in
    *[!0-9]* | '') printf '%s\n' "$b_mb" | grep -qE '^[0-9]*\.?[0-9]*$' && printf '%s\n' "$b_mb" | grep -q '[1-9]' \
                     || bad="$bad no size;" ;;
    *[1-9]*) ;;
    *) bad="$bad size 0;" ;;
  esac
  if [ -n "$bad" ]; then
    say "STOP: backup $SLUG could not be verified:$bad nothing changed"
    PHASE=stopped; exit 1
  fi
  if [ -n "$b_bytes" ]; then b_sz="$b_bytes bytes"; else b_sz="$b_mb MB"; fi
  say "    backup $SLUG verified: full, Core $b_core, $b_sz, protected $b_prot, database excluded ${b_xdb:-?}"

  PHASE=folder
  say "2/6 run folder $(rel "$RUN")/"
  if [ ! -d "$REC" ] && ! mkdir -m 700 "$REC"; then
    say "STOP: cannot create $(rel "$REC")/; nothing changed (backup $SLUG was made)"; exit 1
  fi
  if ! mkdir -m 700 "$RUN"; then
    say "STOP: cannot create $(rel "$RUN")/; nothing changed (backup $SLUG was made)"; exit 1
  fi
  start_log "$RUN/run.log"
  PRE=$RUN/configuration.yaml.pre
  if ! { cp -p "$CFG" "$PRE" && cmp -s "$CFG" "$PRE"; }; then
    say "STOP: could not make a verified copy of configuration.yaml; nothing changed (backup $SLUG was made)"; exit 1
  fi
  sha_pre=$(sha "$PRE")
  if grep -qE "$LOVELACE_RE" "$PRE" || grep -q 'casaray-v2' "$PRE"; then   # the backup takes minutes
    say "STOP: configuration.yaml gained a lovelace: key or casaray-v2 while the backup ran;"
    say "      nothing changed (backup $SLUG was made). Run 'check' again."
    exit 1
  fi
  if ! { printf 'slug=%s\nname=%s\ntype=%s\ndate=%s\nhomeassistant=%s\nsize_bytes=%s\nprotected=%s\nexclude_database=%s\n' \
           "$SLUG" "$BNAME" "$b_type" "$b_date" "$b_core" "$b_bytes" "$b_prot" "$b_xdb" >"$RUN/backup" \
         && printf 'run=%s\nscript=register_casaray.sh v1\nconfig=%s\ncreated=%s/\nbackup_slug=%s\nbackup_name=%s\ncfg_sha256_before=%s\nlines_before=%s\ntheme_created=no\nthemes_dir_created=no\n' \
           "${RUN##*/}" "$C" "$(rel "$RUN")" "$SLUG" "$BNAME" "$sha_pre" "$(lines "$PRE")" >"$RUN/manifest" \
         && set_state "$RUN" prepared; }; then
    say "STOP: could not write the run record; nothing changed (backup $SLUG was made)"; exit 1
  fi
  say "    configuration.yaml copied byte-exact (sha256 $(printf '%s' "$sha_pre" | cut -c1-12)...)"
  # /tmp is gone after an add-on restart or a reboot: keep the tool that reads this record with it.
  if regular "$0" && cp "$0" "$RUN/register_casaray.sh" 2>/dev/null && cmp -s "$0" "$RUN/register_casaray.sh"; then
    UNDO_CMD="sh $RUN/register_casaray.sh"
    mf_set "$RUN" script_copy "register_casaray.sh sha256 $(sha "$RUN/register_casaray.sh")"
  else
    rm -f "$RUN/register_casaray.sh"
    say "    WARN could not keep a copy of this script in the run folder (to undo later, use the git copy)"
  fi

  PHASE=theme
  DIRTY=1
  if [ "$THEME_ACTION" = install ]; then
    say "3/6 installing themes/deez_your_name.yaml from deez_repo"
    if [ ! -d "$THEMES" ]; then
      mf_set "$RUN" themes_dir_created pending || fail_apply "could not record the run state; themes/ not created"
      if ! mkdir -m 755 "$THEMES"; then
        mf_set "$RUN" themes_dir_created no
        fail_apply "could not create themes/"
      fi
      mf_set "$RUN" themes_dir_created yes
      mf_set "$RUN" created themes/
    fi
    if ! { cp "$SRC" "$RUN/theme.new" && chmod 644 "$RUN/theme.new" && [ "$(sha "$RUN/theme.new")" = "$H_THEME" ]; }; then
      fail_apply "could not make a verified copy of the deez_repo theme"
    fi
    mf_set "$RUN" theme_created pending || fail_apply "could not record the run state; the theme was not installed"
    if ! ln "$RUN/theme.new" "$THEME"; then
      mf_set "$RUN" theme_created no
      fail_apply "themes/deez_your_name.yaml appeared while this ran; not overwritten"
    fi
    mf_set "$RUN" theme_created yes || fail_apply "could not record the run state"   # theme.new still links it
    mf_set "$RUN" created themes/deez_your_name.yaml
    rm -f "$RUN/theme.new"
    [ "$(sha "$THEME")" = "$H_THEME" ] || fail_apply "the installed theme does not have the expected sha256"
    say "    installed, sha256 verified"
  else
    say "3/6 theme already present: not touched"
  fi

  PHASE=edit
  say "4/6 appending the CasaRay block to configuration.yaml"
  NEW=$RUN/configuration.yaml.new
  lead=""
  if [ -s "$PRE" ] && ! ends_nl "$PRE"; then lead=$NL; fi
  if ! { cp -p "$PRE" "$NEW" && printf '%s' "$lead" >>"$NEW" && block >>"$NEW"; }; then
    fail_apply "could not write the new configuration.yaml"
  fi
  if ! { cat "$PRE"; printf '%s' "$lead"; block; } | cmp -s - "$NEW"; then
    fail_apply "the new configuration.yaml is not exactly the original plus the block"
  fi
  sha_new=$(sha "$NEW")
  mf_set "$RUN" cfg_sha256_after "$sha_new" || fail_apply "could not record the run state; configuration.yaml not replaced"
  cmp -s "$CFG" "$PRE" || fail_apply "configuration.yaml changed while this ran; not replaced"
  set_state "$RUN" edited || fail_apply "could not record the run state; configuration.yaml not replaced"
  mv -f "$NEW" "$CFG" || fail_apply "could not replace configuration.yaml"
  [ "$(sha "$CFG")" = "$sha_new" ] || fail_apply "configuration.yaml does not read back as written"
  mf_set "$RUN" modified configuration.yaml
  BLK="$(($(lines "$CFG") - 11))-$(lines "$CFG")"
  mf_set "$RUN" block_lines "$BLK"
  say "    done: lines $BLK of configuration.yaml are the CasaRay block"

  PHASE=check
  say "5/6 ha core check (Home Assistant's own validator; can take a few minutes)"
  if ! run_check "$RUN/check.log"; then
    say "the configuration check FAILED (ha exit $ckrc). Where (values are left out; for the full text"
    say "run 'ha core check' yourself, it can show values from secrets.yaml):"
    out_lines "${CHECK_WHERE:-no error location found in the output}"
    say "(the CasaRay block is lines $BLK; an error elsewhere was already in the file or in a file it includes)"
    fail_apply "configuration check failed"
  fi
  say "    check passed"

  PHASE='pre-restart'   # still DIRTY: stopped here, everything goes back and nothing restarts
  say "6/6 restarting Home Assistant. THIS PAGE WILL DISCONNECT: reopen the Terminal in a minute or two."
  mark=$(log_marker)
  set_state "$RUN" applied || fail_apply "could not record the run state; not restarting"
  mf_set "$RUN" restarted yes      # requested; restart_confirmed=yes follows once a new boot is seen
  PHASE=restart
  DIRTY=0
  restart_core "$mark"
  rs=$?
  failed=""
  if [ "$rs" -eq 0 ]; then
    mf_set "$RUN" restart_confirmed yes
    if [ "$RECM" -eq 0 ]; then failed="Core came back in RECOVERY MODE"
    elif [ "$RECM" -eq 2 ]; then
      say "WARN could not isolate the log since the restart: check Settings > System > Repairs that"
      say "     Home Assistant is not in recovery mode"
    else
      n=$(printf '%s\n' "$POSTLOG" | grep -ciE "lovelace.*(error|invalid|not unique)|(error|invalid).*lovelace")
      [ "$n" -eq 0 ] || say "WARN $n lovelace error line(s) in the log since the restart: Settings > System > Logs"
    fi
  elif [ "$rs" -eq 1 ]; then
    failed="Core did not answer after $TRIES probes $POLL s apart ($UP_HOW)"
  else
    PHASE='undo-unconfirmed'
    say "could not confirm that Home Assistant restarted: 'ha core restart' returned $RS_RC, Core kept"
    say "answering and its log shows no new boot. Putting the files back, so the change cannot load at"
    say "a later, unwatched restart:"
    DIRTY=1
    if plan_undo "$RUN" && undo_files "$RUN"; then
      DIRTY=0
      set_state "$RUN" rolled-back
      say "files put back. Home Assistant was most likely NOT restarted${RS_ERR:+ (Supervisor said: $RS_ERR)};"
      say "if it was, it shows CasaRay until its next restart. Run apply again later. Backup: $SLUG"
      exit 4
    fi
    DIRTY=0
    set_state "$RUN" rollback-failed
    say "NOT everything could be put back; the original is $(rel "$RUN")/configuration.yaml.pre"
    exit 4
  fi
  if [ -n "$failed" ]; then
    PHASE=undo-after-restart
    say "$failed: putting everything back and restarting again"
    DIRTY=1
    if plan_undo "$RUN" && undo_files "$RUN"; then
      DIRTY=0
      set_state "$RUN" rolled-back
      say "restarting Home Assistant again"
      mark=$(log_marker)
      restart_core "$mark"
      rs=$?
      if [ "$rs" -eq 0 ] && [ "$RECM" -eq 0 ]; then
        say "rolled back, but Core came back in RECOVERY MODE again, without the CasaRay block: the cause"
        say "is elsewhere. See Settings > System > Repairs and: ha core logs | tail -40. Backup: $SLUG"
        exit 4
      elif [ "$rs" -eq 0 ]; then
        [ "$RECM" -eq 2 ] && say "WARN could not isolate the log since that restart: check Settings > System > Repairs"
        say "rolled back; Core restarted and answers again ($UP_HOW). Backup taken before the change: $SLUG"
        say "send a screenshot of: ha core logs | tail -40"
        exit 3
      elif [ "$rs" -eq 1 ]; then
        say "rolled back, but Core is still not answering. Backup taken before the change: $SLUG"
        exit 4
      fi
      say "rolled back, but the second restart could not be confirmed${RS_ERR:+ (Supervisor said: $RS_ERR)}:"
      say "run 'ha core restart'. Backup taken before the change: $SLUG"
      exit 4
    fi
    DIRTY=0
    set_state "$RUN" rollback-failed
    say "NOT everything could be put back; the original is $(rel "$RUN")/configuration.yaml.pre"
    exit 4
  fi

  PHASE=finished
  say "DONE. CasaRay is registered (lines $BLK of configuration.yaml) and Core restarted with it."
  say "check by hand:"
  say "  [ ] the wall iPad opens /casaray-v2/home (sidebar: CasaRay) and it renders"
  say "  [ ] Settings > Dashboards lists CasaRay as a YAML dashboard"
  say "  [ ] Profile > Theme offers CasaRay"
  say "backup taken before the change: $SLUG ($BNAME)"
  say "record: $(rel "$RUN")/"
  say "undo:   $UNDO_CMD rollback"
  exit 0
}

# ---------------------------------------------------------------- rollback
do_rollback() {
  take_lock || exit 1
  out "CasaRay register v1 (rollback)   config folder: $C"
  T=""
  for d in "$REC"/casaray-register-*; do
    is_run "$d" || continue
    case $(get_state "$d") in applied | edited | prepared | rollback-failed) T=$d ;; esac
  done
  if [ -z "$T" ]; then
    say "STOP: nothing to roll back: no register run is marked applied (or unfinished); nothing changed"
    exit 1
  fi
  RUN=$T
  [ -f "$T/register_casaray.sh" ] && UNDO_CMD="sh $T/register_casaray.sh"
  tstate=$(get_state "$T")
  say "run:    $(rel "$T")/  (state: $tstate, backup $(mf_get "$T" backup_slug))"
  if ! plan_undo "$T"; then
    say "STOP: $UNDO_WHY; nothing changed"
    exit 1
  fi
  need_restart=no
  if [ "$tstate" = applied ] || [ "$(mf_get "$T" restarted)" = yes ]; then need_restart=yes; fi
  case $UNDO_CFG in
    restore) say "will:   restore configuration.yaml byte-exact from $(rel "$T")/configuration.yaml.pre" ;;
    none) say "will:   leave configuration.yaml (already as before the run)" ;;
    untouched) say "will:   leave configuration.yaml (that run never replaced it)" ;;
  esac
  case $UNDO_THEME in
    remove) say "        remove themes/deez_your_name.yaml (that run installed it; unchanged since)" ;;
    keep-differs) say "        leave themes/deez_your_name.yaml (it changed since that run installed it)" ;;
    keep-other) say "        leave themes/deez_your_name.yaml (that run stopped before installing it)" ;;
  esac
  [ "$UNDO_DIR" = remove ] && say "        remove themes/ if it is empty (that run created it)"
  if [ "$need_restart" = yes ]; then say "        'ha core check' (if it fails: stop, no restart), then restart Home Assistant (this page disconnects)"
  else say "        no restart (that run never restarted Home Assistant)"; fi
  confirm ROLLBACK || exit 1
  trap '' HUP
  start_log "$T/rollback-$STAMP.log"
  PHASE=rollback
  if ! undo_files "$T"; then
    set_state "$T" rollback-failed
    say "NOT everything could be put back; nothing was restarted"
    exit 4
  fi
  if [ "$need_restart" = no ]; then
    set_state "$T" rolled-back
    say "rolled back; no restart needed"
    exit 0
  fi
  if run_check "$T/rollback-check-$STAMP.log"; then say "ha core check: passed"
  else
    # The block is gone from the file, so the error is elsewhere; a restart would load it (possibly
    # recovery mode, house-wide). Core keeps running what it loaded at its last start.
    say "STOP: 'ha core check' fails on the restored configuration (ha exit $ckrc). The CasaRay block is"
    say "      no longer in the file, so the error is elsewhere. Where (values are left out; for the full"
    say "      text run 'ha core check' yourself, it can show values from secrets.yaml):"
    out_lines "${CHECK_WHERE:-no error location found in the output}"
    say "NOT restarting: a restart would load that error. Home Assistant keeps running its current"
    say "configuration (with CasaRay) until it restarts. The files above are already put back."
    say "Fix the error, then run '$UNDO_CMD rollback' again: it will only check and restart."
    exit 4
  fi
  say "restarting Home Assistant (this page will disconnect; reopen the Terminal in a minute or two)"
  mark=$(log_marker)
  restart_core "$mark"
  rs=$?
  set_state "$T" rolled-back
  if [ "$rs" -eq 0 ] && [ "$RECM" -eq 0 ]; then
    say "files rolled back, but Core came back in RECOVERY MODE, without the CasaRay block: the cause"
    say "is elsewhere. See Settings > System > Repairs and: ha core logs | tail -40"
    exit 4
  elif [ "$rs" -eq 0 ]; then
    [ "$RECM" -eq 2 ] && say "WARN could not isolate the log since the restart: check Settings > System > Repairs that Home Assistant is not in recovery mode"
    say "rollback done: Core restarted and answers ($UP_HOW). The backup $(mf_get "$T" backup_slug) is untouched."
    exit 0
  elif [ "$rs" -eq 1 ]; then
    say "files rolled back, but Core is not answering yet ($UP_HOW); wait, then run 'verify'"
    exit 4
  fi
  say "files rolled back, but the restart could not be confirmed${RS_ERR:+ (Supervisor said: $RS_ERR)}:"
  say "Home Assistant keeps CasaRay until it restarts. Run 'ha core restart' when possible, then 'verify'"
  exit 4
}

# ---------------------------------------------------------------- verify (read-only)
do_verify() {
  out "CasaRay register v1 (verify, read-only)   config folder: $C"
  attn=""
  if command -v ha >/dev/null 2>&1 && core_info; then row "Home Assistant Core" "$CORE_VERSION"
  else row "Home Assistant Core" "'ha core info' did not answer"; attn="$attn Supervisor CLI;"; fi
  if core_up; then row "Core API" "answers ($UP_HOW)"; else row "Core API" "$UP_HOW"; attn="$attn Core not answering;"; fi
  if regular "$CFG"; then
    if [ "$(tail -n 12 "$CFG" | sha256sum | cut -d' ' -f1)" = "$(block | sha256sum | cut -d' ' -f1)" ]; then
      row "registration block" "present, exact, at the end of configuration.yaml"
    elif grep -qxF "$FIRST_LINE" "$CFG"; then row "registration block" "present but edited or not at the end"
    elif grep -q 'casaray-v2' "$CFG"; then row "registration block" "not this script's; casaray-v2 is mentioned"
    else row "registration block" "ABSENT"; attn="$attn not registered;"; fi
  else row "configuration.yaml" "not a regular file"; attn="$attn configuration.yaml;"; fi
  if regular "$DASH"; then
    if [ "$(sha "$DASH")" = "$H_DASH" ]; then row "dashboards/casaray_v2.yaml" "present, MATCHES git"
    else row "dashboards/casaray_v2.yaml" "present, DIFFERS from git"; fi
  else row "dashboards/casaray_v2.yaml" "MISSING"; attn="$attn dashboard file;"; fi
  if regular "$THEME"; then
    if [ "$(sha "$THEME")" = "$H_THEME" ]; then row "themes/deez_your_name.yaml" "present, MATCHES git"
    else row "themes/deez_your_name.yaml" "present, DIFFERS from git"; fi
  else row "themes/deez_your_name.yaml" "MISSING"; attn="$attn theme;"; fi
  last=""
  for d in "$REC"/casaray-register-*; do is_run "$d" && last=$d; done
  if [ -n "$last" ]; then
    lst=$(get_state "$last")
    row "latest register run" "${last##*/}: ${lst:-no state} (backup $(mf_get "$last" backup_slug))"
    case $lst in
      prepared | edited)
        row "" "that run stopped before restarting Home Assistant: CasaRay is NOT loaded"
        attn="$attn latest run unfinished (run rollback: no restart is needed);" ;;
      rollback-failed)
        attn="$attn latest run could not be rolled back;" ;;
      applied)
        if [ "$(mf_get "$last" restart_confirmed)" != yes ]; then
          row "" "the restart after the change was NOT confirmed"
          attn="$attn restart after the change not confirmed (after 'ha core restart', check /casaray-v2/home; or rollback);"
        fi ;;
    esac
  else row "latest register run" "none"; fi
  if command -v ha >/dev/null 2>&1; then
    if ha core logs -n 300 2>/dev/null | grep -qiE 'activating recovery mode|starting in recovery mode'; then
      row "recovery mode (last 300 log lines)" "YES"; attn="$attn recovery mode logged;"
    else row "recovery mode (last 300 log lines)" "no"; fi
  fi
  if [ -n "$attn" ]; then out "VERIFY: ATTENTION:$attn"; exit 1; fi
  out "VERIFY: OK"
  exit 0
}

case $MODE in
  check)
    out "CasaRay register v1 (check, read-only)   config folder: $C"
    preflight
    if finish_report; then say "nothing changed. Next: sh /tmp/register_casaray.sh apply"; exit 0; fi
    say "nothing changed"
    exit 1 ;;
  apply) do_apply ;;
  verify) do_verify ;;
  rollback) do_rollback ;;
esac
