#!/bin/sh
# CasaRay — restore the OWNER's login only, with Home Assistant's own tool.
#
# Why this works: the owner user and its login record survive in .storage/auth; only the
# password store (.storage/auth_provider.homeassistant) is gone. At login Home Assistant looks
# up the EXISTING login record by normalised username, so giving that username a password
# with the native tool
#     python3 -m homeassistant --script auth -c /config add <username> <password>
# reconnects it to the same user ID. Run inside the Core image while Core is stopped.
#
#   sh /tmp/fix_owner_login.sh check      read-only (default)
#   sh /tmp/fix_owner_login.sh run        hidden password twice -> type APPLY -> stop Core ->
#                                         native add + native validate -> start Core -> verify
#   sh /tmp/fix_owner_login.sh rollback   type ROLLBACK -> back to exactly the pre-repair files
#   sh /tmp/fix_owner_login.sh finish     after logging in: delete the pre-repair copies
#
# Touches ONE file: creates .storage/auth_provider.homeassistant. Users, login records, tokens,
# integrations, registries, onboarding, config, dashboards and databases are not edited; the
# user database and registries are fingerprinted before/after and restored if anything differs.
set -u
MODE="${1:-check}"
SAFETY="${SAFETY:-b0206554}"
C="${RC_HOST_CONFIG:-/mnt/data/supervisor/homeassistant}"
R="$C/_recovery/owner"
TTY="${RC_TTY:-/dev/tty}"
P=.storage/auth_provider.homeassistant
KEEP=".storage/auth .storage/core.config_entries .storage/core.device_registry .storage/core.entity_registry .storage/onboarding"
say() { echo "[owner] $*"; }
die() { echo "[owner] STOP: $*"; exit 1; }

# Read-only, plain JSON (no Home Assistant import): prints the owner's normalised username.
INFOPY=$(cat <<'EOF'
import json, os, sys
CFG = os.environ.get('RCFG', '/config')
try: a = json.load(open(CFG + '/.storage/auth'))['data']
except Exception as x: print('FAIL: cannot read .storage/auth:', type(x).__name__); sys.exit(3)
users = {u['id']: u for u in a.get('users', [])}
creds = [c for c in a.get('credentials', []) if c.get('auth_provider_type') == 'homeassistant']
people = [u for u in users.values() if not u.get('system_generated')]
print('users: %d (%d owner) | Home Assistant logins: %d' % (len(people), sum(1 for u in people if u.get('is_owner')), len(creds)), file=sys.stderr)
own = [c for c in creds if (users.get(c.get('user_id')) or {}).get('is_owner')]
if len(own) != 1: print('FAIL: expected exactly one owner login, found %d' % len(own)); sys.exit(3)
if os.path.exists(CFG + '/.storage/auth_provider.homeassistant'):
    print('FAIL: a password store already exists; this only rebuilds a missing one'); sys.exit(3)
print(own[0]['data']['username'].strip().casefold())
EOF
)
img() { docker inspect -f '{{.Config.Image}}' homeassistant 2>/dev/null; }
api() { curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8123/api/ 2>/dev/null; }
running() { [ "$(docker inspect -f '{{.State.Running}}' homeassistant 2>/dev/null)" = true ]; }
native() { docker run --rm -v "$C:/config" --entrypoint python3 "$IMG" -m homeassistant --script auth -c /config "$@"; }
fp() { for f in $KEEP; do [ -e "$C/$f" ] && sha256sum "$C/$f" | cut -c1-64 || echo missing; done; }
owner() { docker exec -i homeassistant python3 -c "$INFOPY"; }
restore_keep() {
  for f in $KEEP; do
    if [ -e "$R/pre/$f" ]; then cmp -s "$R/pre/$f" "$C/$f" || { cp -p "$R/pre/$f" "$C/$f"; say "restored $f"; }
    elif [ -e "$C/$f" ]; then mkdir -p "$R/rolledback"; mv "$C/$f" "$R/rolledback/"; say "removed newly created $f"; fi
  done
}
do_rollback() {
  [ -e "$R/APPLIED" ] || die "nothing applied"
  ha core stop
  mkdir -p "$R/rolledback"; [ -e "$C/$P" ] && mv "$C/$P" "$R/rolledback/" && say "removed rebuilt password store"
  restore_keep
  rm -f "$R/APPLIED"; ha core start; say "rollback done: files are exactly as before the repair"
}

case "$MODE" in
check)
  running || die "Core must be running for the check"
  ha backups info "$SAFETY" >/dev/null 2>&1 && say "safety backup $SAFETY: present" || say "WARN: safety backup $SAFETY not found"
  O=$(owner) || die "$O"; say "owner login to repair: $O"
  say "Core image: $(img)"; say "OK: nothing changed" ;;
run)
  running || die "Core must be running to start"
  [ -e "$R/APPLIED" ] && die "already applied; use rollback or finish"
  ha backups info "$SAFETY" >/dev/null 2>&1 || die "safety backup $SAFETY not found; nothing changed"
  say "safety backup $SAFETY: present"
  O=$(owner) || die "$O"; IMG=$(img); [ -n "$IMG" ] || die "cannot identify the Core image"
  say "owner login to repair: $O"
  while :; do
    printf '[owner] new password for %s (your old one is fine): ' "$O"; stty -echo 2>/dev/null <"$TTY"; read -r PW <"$TTY"; stty echo 2>/dev/null <"$TTY"; echo
    [ -n "$PW" ] || die "no password entered; nothing changed"
    case "$PW" in -*) say "a password may not start with '-'; try again"; continue ;; esac
    printf '[owner] again: '; stty -echo 2>/dev/null <"$TTY"; read -r PW2 <"$TTY"; stty echo 2>/dev/null <"$TTY"; echo
    [ "$PW" = "$PW2" ] && break; say "did not match, try again"
  done; PW2=
  say "ready: stop Core, create the owner's password with Home Assistant's own auth tool, start Core."
  printf '[owner] type APPLY to continue: '; read -r ANS <"$TTY"; [ "$ANS" = APPLY ] || { PW=; die "not confirmed; nothing changed"; }
  rm -rf "$R/pre"; mkdir -p "$R/pre/.storage"; chmod 700 "$C/_recovery" "$R" 2>/dev/null
  for f in $KEEP; do [ -e "$C/$f" ] && cp -p "$C/$f" "$R/pre/$f"; done
  BEFORE=$(fp)
  ha core stop || { PW=; die "could not stop Core; nothing changed"; }
  touch "$R/APPLIED"
  OUT=$(native add "$O" "$PW" 2>&1); echo "$OUT" | grep -E "Auth created|already exists|Error|error" | head -3
  VAL=$(native validate "$O" "$PW" 2>&1); PW=
  echo "$VAL" | grep -q "Auth valid" || { say "native validate did not confirm the password: rolling back"; do_rollback; die "rolled back; photograph the lines above"; }
  say "native validate: Auth valid"
  if [ "$(fp)" != "$BEFORE" ]; then
    say "a protected file changed during the tool run; restoring the pre-repair copies"
    restore_keep
  else say "users, login records, tokens, registries and onboarding: unchanged"; fi
  chmod 600 "$C/$P" 2>/dev/null
  ha core start
  say "waiting for Core (up to 15 minutes)"; i=0
  while [ "$(api)" != 401 ]; do
    i=$((i+1))
    if [ $i -gt 90 ]; then
      running && die "Core is running but not answering yet. NOT rolling back. Wait 5 minutes and try logging in."
      say "Core container is not running: rolling back automatically"; do_rollback; die "rolled back; photograph: ha core logs | tail -40"
    fi
    sleep "${RC_POLL:-10}"
  done
  say "DONE. Core is up. On the iPad, log in as '$O' with the password you just set."
  say "If the onboarding screen appears, it should now let you log in and finish its remaining steps."
  say "Anything wrong: sh /tmp/fix_owner_login.sh rollback" ;;
rollback)
  printf '[owner] type ROLLBACK to stop Core and undo the repair: '; read -r ANS <"$TTY"
  [ "$ANS" = ROLLBACK ] || die "not confirmed"; do_rollback ;;
finish)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  rm -rf "$R/pre" "$R/rolledback" && rm -f "$R/APPLIED" && say "pre-repair copies deleted (they contained login tokens)" ;;
*) die "unknown mode: $MODE" ;;
esac
