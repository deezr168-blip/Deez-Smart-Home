#!/bin/sh
# CasaRay disk report — what is consuming storage on this Home Assistant host?
#
# READ-ONLY. This script contains no rm, no truncate, no mv, no sqlite VACUUM
# and no delete of any kind. It measures and prints. Nothing it does can
# change a byte on disk, so it is safe to run on a nearly-full filesystem
# and safe to run repeatedly.
#
# It exists because a disk cleanup has exactly one dangerous step, and it is
# the first one: deciding what to delete before knowing what is there. This
# produces the evidence. The deciding happens afterwards, with a person.
#
# WHY A SCRIPT AND NOT A LIST OF COMMANDS
#
# The Home Assistant OS Terminal add-on is BusyBox ash, where half the usual
# incantations do not work: `find -printf` is GNU-only, `sort -h` is not
# reliably present, and `du --max-depth` is spelled `-d`. Everything here is
# POSIX sh and BusyBox-safe, and sizes are computed in kilobytes with `du -k`
# and formatted in awk rather than relying on `-h` and `sort -h`.
#
# USAGE (on the Home Assistant host, Terminal add-on or SSH)
#   sh /config/casaray/casaray_disk_report.sh
#   sh /config/casaray/casaray_disk_report.sh > /config/disk_report.txt
#
# Then paste the output back. Nothing is deleted until you say so.
#
# EXIT CODES
#   0  report produced
#   2  /config not found — this is not a Home Assistant host

set -u

CONFIG="${CONFIG:-/config}"
TOPN="${TOPN:-40}"

[ -d "$CONFIG" ] || {
  echo "ERROR: $CONFIG does not exist — is this a Home Assistant host?" >&2
  echo "       Override with: CONFIG=/path sh $0" >&2
  exit 2; }

hr()  { echo "------------------------------------------------------------"; }
sec() { echo; hr; echo "$*"; hr; }

# kb_of PATH... -- total kilobytes, 0 if nothing exists. Never fails.
kb_of() {
  _t=0
  for _p in "$@"; do
    [ -e "$_p" ] || continue
    _k=$(du -sk "$_p" 2>/dev/null | awk '{print $1}')
    [ -n "$_k" ] && _t=$((_t + _k))
  done
  echo "$_t"
}

# human KB -- 1048576 -> "1.0G"
human() {
  awk -v k="$1" 'BEGIN{
    if (k >= 1048576) printf "%.1fG", k/1048576;
    else if (k >= 1024) printf "%.0fM", k/1024;
    else printf "%dK", k;
  }'
}

# report LABEL PATH... -- one summary line, and remember it for the roll-up.
TOTALS=""
report() {
  _lab="$1"; shift
  _kb=$(kb_of "$@")
  printf '  %-34s %8s   %s\n' "$_lab" "$(human "$_kb")" "$1"
  TOTALS="$TOTALS$_kb $_lab
"
}

echo "CasaRay disk report"
echo "host date : $(date 2>/dev/null)"
echo "config    : $CONFIG"
echo "mode      : READ-ONLY (this script deletes nothing)"

sec "1. FILESYSTEM — total and free"
echo "(human)"
df -h 2>/dev/null | sed 's/^/  /'
echo
echo "(the filesystem holding $CONFIG)"
df -k "$CONFIG" 2>/dev/null | sed 's/^/  /'
echo
echo "NOTE: on Home Assistant OS the interesting mount is usually /mnt/data,"
echo "      with /config a bind mount inside it. If /config shows the same"
echo "      figures as /mnt/data or /, that is why."

sec "2. TOP-LEVEL — what is under $CONFIG"
du -sk "$CONFIG"/* "$CONFIG"/.[!.]* 2>/dev/null | sort -rn | head -30 \
  | while read -r k p; do printf '  %8s  %s\n' "$(human "$k")" "$p"; done
echo
printf '  %8s  %s\n' "$(human "$(kb_of "$CONFIG")")" "TOTAL $CONFIG"

sec "3. LARGEST $TOPN FILES under $CONFIG"
# `du -ak` lists files as well as directories; keep only regular files so a
# directory total is not mistaken for one big file.
du -ak "$CONFIG" 2>/dev/null | sort -rn | head -300 \
  | while read -r k p; do
      [ -f "$p" ] || continue
      printf '  %8s  %s\n' "$(human "$k")" "$p"
    done | head -"$TOPN"

sec "4. DATABASE — recorder"
report "home-assistant_v2.db"      "$CONFIG/home-assistant_v2.db"
report "  .db-wal (write-ahead)"   "$CONFIG/home-assistant_v2.db-wal"
report "  .db-shm (shared memory)" "$CONFIG/home-assistant_v2.db-shm"
echo
echo "  Other .db files:"
find "$CONFIG" -maxdepth 2 -name '*.db' -o -maxdepth 2 -name '*.db-*' 2>/dev/null \
  | while read -r f; do
      [ -f "$f" ] || continue
      printf '    %8s  %s\n' "$(human "$(kb_of "$f")")" "$f"
    done
echo
echo "  recorder: configuration (purge_keep_days is the lever here)"
if [ -f "$CONFIG/configuration.yaml" ]; then
  awk '/^recorder:/{f=1} f&&/^[a-z_]+:/&&!/^recorder:/{f=0} f' \
      "$CONFIG/configuration.yaml" 2>/dev/null | sed 's/^/    /'
  grep -rn 'purge_keep_days' "$CONFIG"/*.yaml "$CONFIG"/packages/*.yaml 2>/dev/null \
    | sed 's/^/    /' | head -5
else
  echo "    (configuration.yaml not readable from here)"
fi
echo
command -v sqlite3 >/dev/null 2>&1 \
  && echo "  sqlite3 IS available — a VACUUM could reclaim free pages in place" \
  || echo "  sqlite3 not present — a VACUUM would need the recorder service instead"

sec "5. LOGS"
report "home-assistant.log"        "$CONFIG/home-assistant.log"
report "home-assistant.log.1"      "$CONFIG/home-assistant.log.1"
report "home-assistant.log.fault"  "$CONFIG/home-assistant.log.fault"
report "casaray_maintenance.log"   "$CONFIG/casaray_maintenance.log"
echo
echo "  Every *.log over 1M under $CONFIG:"
du -ak "$CONFIG" 2>/dev/null | sort -rn \
  | while read -r k p; do
      [ "$k" -ge 1024 ] || continue
      case "$p" in *.log|*.log.*|*.txt) [ -f "$p" ] && printf '    %8s  %s\n' "$(human "$k")" "$p" ;; esac
    done | head -20

sec "6. BACKUPS"
report "/backup (Home Assistant's own)" "/backup"
report "$CONFIG/backups"                "$CONFIG/backups"
echo
echo "  Individual backup archives (newest last):"
for d in /backup "$CONFIG/backups"; do
  [ -d "$d" ] || continue
  ls -l "$d" 2>/dev/null | tail -n +2 | sed "s|^|    |" | head -20
done

sec "7. MEDIA, CAMERA SNAPSHOTS, WWW"
report "/media"                 "/media"
report "$CONFIG/media"          "$CONFIG/media"
report "$CONFIG/www"            "$CONFIG/www"
report "  www/snapshots"        "$CONFIG/www/snapshots"
report "  www/images"           "$CONFIG/www/images"
report "$CONFIG/image"          "$CONFIG/image"
report "/share"                 "/share"
echo
echo "  Image/video files over 1M:"
du -ak "$CONFIG" /media /share 2>/dev/null | sort -rn \
  | while read -r k p; do
      [ "$k" -ge 1024 ] || continue
      case "$p" in *.jpg|*.jpeg|*.png|*.mp4|*.mkv|*.mov|*.gif)
        [ -f "$p" ] && printf '    %8s  %s\n' "$(human "$k")" "$p" ;;
      esac
    done | head -20

sec "8. CACHE, TEMP, BUILD ARTEFACTS"
report "$CONFIG/.storage"       "$CONFIG/.storage"
report "$CONFIG/deps"           "$CONFIG/deps"
report "$CONFIG/tts"            "$CONFIG/tts"
report "$CONFIG/tmp"            "$CONFIG/tmp"
report "/tmp"                   "/tmp"
report "$CONFIG/.cloud"         "$CONFIG/.cloud"
echo
echo "  __pycache__ directories:"
_pc=$(find "$CONFIG" -type d -name '__pycache__' 2>/dev/null | wc -l | tr -d ' ')
echo "    count: $_pc"
[ "$_pc" -gt 0 ] && printf '    %8s  total\n' \
  "$(human "$(find "$CONFIG" -type d -name '__pycache__' 2>/dev/null | while read -r d; do du -sk "$d" 2>/dev/null; done | awk '{s+=$1} END{print s+0}')")"

sec "9. CASARAY DEPLOYMENT BACKUPS"
BK="$CONFIG/dashboards/backups"
report "dashboards/ (whole dir)"  "$CONFIG/dashboards"
report "  backups/"               "$BK"
echo
if [ -d "$BK" ]; then
  for pat in "casaray_v2.yaml.predeploy." "casaray_v2_predeploy_"; do
    n=$(find "$BK" -maxdepth 1 -type f -name "$pat*" 2>/dev/null | wc -l | tr -d ' ')
    k=$(find "$BK" -maxdepth 1 -type f -name "$pat*" 2>/dev/null | while read -r f; do du -sk "$f" 2>/dev/null; done | awk '{s+=$1} END{print s+0}')
    printf '  %-34s %8s   %s file(s)\n' "$pat*" "$(human "${k:-0}")" "$n"
  done
  echo
  echo "  NEWEST backup (this one must survive any cleanup):"
  # By TIMESTAMP, not filename: `.` sorts before `_`, so a plain sort across
  # both schemes returns the newest file of the OLD scheme whatever the dates
  # are. Same defect this script found in casaray_common.sh's latest_backup().
  find "$BK" -maxdepth 1 -type f \
       \( -name "casaray_v2.yaml.predeploy.*" -o -name "casaray_v2_predeploy_*" \) 2>/dev/null \
    | while read -r f; do
        d=$(basename "$f" | tr -cd '0-9')
        [ -n "$d" ] || continue
        while [ "${#d}" -lt 14 ]; do d="${d}0"; done
        printf '%s\t%s\n' "$(echo "$d" | cut -c1-14)" "$f"
      done \
    | sort | tail -1 | cut -f2- | sed 's/^/    /'
else
  echo "  (no backups directory — nothing has ever been deployed by the suite)"
fi
echo
echo "  Sync script .bak files sitting in dashboards/ itself:"
n=$(find "$CONFIG/dashboards" -maxdepth 1 -type f -name '*.bak.*' 2>/dev/null | wc -l | tr -d ' ')
k=$(find "$CONFIG/dashboards" -maxdepth 1 -type f -name '*.bak.*' 2>/dev/null | while read -r f; do du -sk "$f" 2>/dev/null; done | awk '{s+=$1} END{print s+0}')
printf '    %8s  %s file(s)\n' "$(human "${k:-0}")" "$n"

sec "10. GIT CLONE — $CONFIG/deez_repo"
report "deez_repo (whole)"  "$CONFIG/deez_repo"
report "  .git"             "$CONFIG/deez_repo/.git"
report "  working tree"     "$CONFIG/deez_repo/dashboards" "$CONFIG/deez_repo/docs" "$CONFIG/deez_repo/scripts"
echo
if [ -d "$CONFIG/deez_repo/.git" ]; then
  echo "  Is the clone clean? (uncommitted work would be LOST by a reclone)"
  ( cd "$CONFIG/deez_repo" && git status --short 2>/dev/null | head -10 | sed 's/^/    /' ) || true
  ( cd "$CONFIG/deez_repo" && git status --short 2>/dev/null | wc -l \
      | awk '{print ($1==0) ? "    clean — nothing uncommitted" : "    " $1 " uncommitted change(s) — do NOT reclone until these are saved"}' )
fi

sec "SUMMARY — largest consumers measured above"
printf '%s' "$TOTALS" | sort -rn | head -15 \
  | while read -r k lab; do
      [ "${k:-0}" -gt 0 ] || continue
      printf '  %8s  %s\n' "$(human "$k")" "$lab"
    done

hr
echo "Nothing was deleted. Nothing was modified."
echo
echo "Paste this whole output back and you will get a categorised proposal"
echo "with a size and a risk for each item, and nothing happens without a"
echo "decision from you."
exit 0
