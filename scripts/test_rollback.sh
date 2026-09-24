#!/usr/bin/env bash
#
# Rollback drill — prove casaray_rollback.sh actually restores, and actually
# refuses, before anyone has to trust it on the live dashboard.
#
# WHY THIS EXISTS
#
# casaray_rollback.sh has never been executed. It is the last line of defence
# for every deployment, so "it looks correct" is not good enough: a rollback
# that silently does nothing is worse than no rollback, because the deploy
# script calls it on post-flight failure and reports success.
#
# Every path in casaray_common.sh is environment-overridable, deliberately so
# the suite can be exercised off a live host. This builds a throwaway /config
# tree in a temp directory and drives the real scripts against it. Nothing
# here touches a real Home Assistant, and the temp tree is removed on exit.
#
# WHAT IT PROVES
#   1. a deploy makes a backup
#   2. rollback restores the previous dashboard byte for byte
#   3. rollback refuses when there is nothing to restore
#   4. rollback refuses a backup that does not parse, rather than deploying it
#   5. rollback refuses a file that is not one of this suite's backups --
#      the sync script's .bak.*, Home Assistant's own backups, anything else
#   6. rollback saves the CURRENT dashboard before overwriting it, so a
#      rollback is itself reversible
#   7. --list reports what is available
#
# USAGE
#   bash scripts/test_rollback.sh          # run the drill
#   bash scripts/test_rollback.sh -v       # keep the temp tree and say where
#
# EXIT CODES
#   0  every assertion held
#   1  an assertion failed — the output says which

set -uo pipefail

REPO_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
KEEP=0
[ "${1:-}" = "-v" ] && KEEP=1

T=$(mktemp -d)
cleanup() { [ "$KEEP" -eq 1 ] && printf '\ntemp tree kept at %s\n' "$T" || rm -rf "$T"; }
trap cleanup EXIT

pass=0; fail=0
ok()  { printf '  \033[32mPASS\033[0m  %s\n' "$*"; pass=$((pass+1)); }
no()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; fail=$((fail+1)); }
note(){ printf '        %s\n' "$*"; }

# ------------------------------------------------------------- the fake host
mkdir -p "$T/deez_repo/dashboards" "$T/config/dashboards/backups" "$T/bin"
cp "$REPO_ROOT/scripts/casaray_common.sh"   "$T/bin/"
cp "$REPO_ROOT/scripts/casaray_rollback.sh" "$T/bin/"

export REPO="$T/deez_repo"
export LIVE_DIR="$T/config/dashboards"
export BACKUP_DIR="$T/config/dashboards/backups"
export CASARAY_LOG="$T/casaray_maintenance.log"
LIVE="$LIVE_DIR/casaray_v2.yaml"
BK="$BACKUP_DIR/casaray_v2.yaml.predeploy"

roll() { sh "$T/bin/casaray_rollback.sh" "$@" 2>&1; }

# Two recognisably different dashboards. Real YAML, since the script parses
# what it is about to restore.
printf 'views:\n- title: GOOD\n  path: home\n  cards: []\n' > "$T/good.yaml"
printf 'views:\n- title: BAD\n  path: home\n  cards: []\n'  > "$T/bad.yaml"

printf '\033[1mRollback drill\033[0m  (throwaway tree, nothing live is touched)\n\n'

printf '\033[1m[1] Nothing to restore\033[0m\n'
cp "$T/good.yaml" "$LIVE"
out=$(roll); rc=$?
[ "$rc" -eq 2 ] && ok "refuses with exit 2 when no backup exists" \
                || no "expected exit 2 with no backups, got $rc"
grep -qi 'no backup' <<<"$out" && ok "says why" || { no "did not say why"; note "$out"; }
grep -q 'GOOD' "$LIVE" && ok "left the live dashboard alone" \
                       || no "MODIFIED the live dashboard with nothing to restore"

printf '\n\033[1m[2] Restores the previous dashboard\033[0m\n'
# A deploy would make this backup; make it the same way, then "deploy" BAD.
cp "$LIVE" "$BK.20260924-120000"
cp "$T/bad.yaml" "$LIVE"
grep -q 'BAD' "$LIVE" && note "live is now BAD, backup holds GOOD"
out=$(roll); rc=$?
[ "$rc" -eq 0 ] && ok "exit 0" || { no "expected exit 0, got $rc"; note "$out"; }
cmp -s "$T/good.yaml" "$LIVE" && ok "live dashboard restored byte for byte" \
                              || no "live dashboard was NOT restored"

printf '\n\033[1m[3] The rollback is itself reversible\033[0m\n'
# Step 2 should have saved BAD before overwriting it.
if grep -rql 'BAD' "$BACKUP_DIR" >/dev/null 2>&1; then
  ok "the overwritten dashboard was saved first"
  note "$(grep -rl 'BAD' "$BACKUP_DIR" | xargs -n1 basename | tr '\n' ' ')"
else
  no "the overwritten dashboard was LOST — a rollback cannot be undone"
fi

printf '\n\033[1m[4] Refuses a backup that does not parse\033[0m\n'
# The backup dir is cleared first so the corrupt file is unambiguously the
# newest. Without this, step 2's backup carries a REAL timestamp and sorts
# above any hand-written one, the script correctly restores that instead, and
# the assertion fails for a reason that has nothing to do with the script.
rm -f "$BACKUP_DIR"/*
printf 'views:\n  - [unclosed\n' > "$BK.20260924-130000"
cp "$T/good.yaml" "$LIVE"
out=$(roll); rc=$?
[ "$rc" -eq 2 ] && ok "refuses with exit 2" || { no "expected exit 2, got $rc"; note "$out"; }
cmp -s "$T/good.yaml" "$LIVE" && ok "live dashboard untouched" \
                              || no "OVERWROTE the live dashboard with a corrupt backup"
grep -qi 'does not parse' <<<"$out" && ok "names the reason" || no "reason not given"
rm -f "$BK.20260924-130000"

printf '\n\033[1m[5] Refuses files that are not this suite'"'"'s backups\033[0m\n'
# The sync script leaves .bak.* files in LIVE_DIR. Home Assistant has its own
# backups. Neither may be restored by name, and nor may anything outside.
printf 'views: []\n' > "$LIVE_DIR/casaray_v2.yaml.bak.20260924-140000"
printf 'views: []\n' > "$T/elsewhere.yaml"
for bad in "casaray_v2.yaml.bak.20260924-140000" "$T/elsewhere.yaml" "/etc/hostname"; do
  out=$(roll "$bad"); rc=$?
  if [ "$rc" -eq 2 ] && grep -qi 'refusing' <<<"$out"; then
    ok "refuses $(basename "$bad")"
  else
    no "ACCEPTED $bad (exit $rc)"; note "$out"
  fi
done
cmp -s "$T/good.yaml" "$LIVE" && ok "live dashboard untouched by all three" \
                              || no "live dashboard was modified"

printf '\n\033[1m[6] --list reports what is available\033[0m\n'
# Self-contained, like every block should be: step 4 clears the backup
# directory, and a block that silently depends on an earlier one's leftovers
# fails for reasons that have nothing to do with what it is asserting.
cp "$T/good.yaml" "$BK.20260924-150000"
out=$(roll --list); rc=$?
[ "$rc" -eq 0 ] && ok "exit 0" || no "expected exit 0, got $rc"
grep -q 'predeploy' <<<"$out" && ok "lists the backups" || { no "listed nothing"; note "$out"; }
grep -q 'bak\.' <<<"$out" && no "LISTED a sync .bak file it must not restore" \
                          || ok "does not list files it would refuse"

printf '\n\033[1m[7] Restores a named backup, not just the newest\033[0m\n'
cp "$T/bad.yaml" "$LIVE"
cp "$T/good.yaml" "$BK.20260924-100000"
printf 'views:\n- title: OLDEST\n  path: home\n  cards: []\n' > "$BK.20260924-090000"
out=$(roll "casaray_v2.yaml.predeploy.20260924-090000"); rc=$?
[ "$rc" -eq 0 ] && grep -q 'OLDEST' "$LIVE" \
  && ok "restored the one that was asked for" \
  || { no "did not restore the named backup (exit $rc)"; note "$out"; }

printf '\n'
printf 'ran %d assertion(s): \033[32m%d passed\033[0m' $((pass+fail)) "$pass"
[ "$fail" -gt 0 ] && printf ', \033[31m%d FAILED\033[0m\n' "$fail" || printf '\n'
[ "$fail" -eq 0 ] || exit 1
printf '\nThis proves the LOGIC. It does not prove the paths on your host are\n'
printf 'right — for that, run the drill in docs/ROLLBACK_DRILL.md once.\n'
