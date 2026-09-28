#!/bin/sh
# CasaRay — Home Assistant login recovery (targeted, from an unencrypted backup)
#
#   sh /tmp/recover_login.sh run        ONE COMMAND: check -> stage -> fresh verified backup -> asks APPLY
#                                       -> dashboard+theme from ha-deploy -> repair -> restart -> verify
#   sh /tmp/recover_login.sh check      read-only: verify the backup and plan the repair (default)
#   sh /tmp/recover_login.sh prepare    NON-DISRUPTIVE: fresh full backup of the current install,
#                                       then stage the needed files under /config/_recovery/stage
#   sh /tmp/recover_login.sh apply      DISRUPTIVE (asks you to type APPLY): stops Core, adds the
#                                       missing files, validates config, starts Core, verifies;
#                                       rolls itself back if Core does not come up
#   sh /tmp/recover_login.sh verify     read-only: post-repair state
#   sh /tmp/recover_login.sh rollback   DISRUPTIVE (asks you to type ROLLBACK): back to pre-apply
#   sh /tmp/recover_login.sh dashboard  re-sync CasaRay dashboard + theme from ha-deploy (backs up first)
#   sh /tmp/recover_login.sh finish     after you have logged in: delete the staged secret copies
#
# Optional 2nd argument: backup tar (default e6cc88bd.tar).
# Never overwrites .storage/auth, never touches integrations, registries, Zigbee or Matter data,
# never restores a backup, never prints a password hash, token or key.
set -u
MODE="${1:-check}"
B="${2:-/mnt/data/supervisor/backup/e6cc88bd.tar}"
C="${RC_HOST_CONFIG:-/mnt/data/supervisor/homeassistant}"
R="$C/_recovery"
say() { echo "[recover] $*"; }
die() { echo "[recover] STOP: $*"; exit 1; }

PY=$(cat <<'EOF'
import sys, os, re, json, tarfile, time
MODE = os.environ.get('MODE', 'check'); CFG = os.environ.get('RCFG', '/config'); R = CFG + '/_recovery'
SAFE = ['auth_provider.homeassistant', 'core.config', 'backup', 'person', 'input_boolean', 'input_number',
        'input_select', 'input_text', 'input_datetime', 'input_button', 'counter', 'timer', 'schedule',
        'lovelace', 'lovelace_dashboards', 'lovelace_resources', 'core.area_registry', 'core.floor_registry',
        'core.label_registry']
DEFAULT_KEYS = {'default_config', 'frontend', 'automation', 'script', 'scene'}
keys = lambda y: re.findall(r'(?m)^([a-z_]+):', y)
def live(p): return os.path.exists(CFG + '/' + p)
def ljs(p):
    try: return json.load(open(CFG + '/' + p)).get('data', {})
    except Exception: return None
def rd(p):
    try: return open(CFG + '/' + p, encoding='utf-8', errors='replace').read()
    except Exception: return ''
def js(b):
    try: return json.loads(b).get('data', {})
    except Exception: return None

if MODE == 'verify':
    for n in ['auth', 'auth_provider.homeassistant', 'core.config', 'backup', 'onboarding', 'person']:
        print('  .storage/%-28s %s' % (n, 'present' if live('.storage/' + n) else 'MISSING'))
    p = ljs('.storage/auth_provider.homeassistant') or {}
    print('  login usernames with a password =', len(p.get('users', [])))
    print('  onboarding done =', (ljs('.storage/onboarding') or {}).get('done'))
    print('  time_zone =', (ljs('.storage/core.config') or {}).get('time_zone'))
    y = rd('configuration.yaml'); print('  configuration.yaml keys =', keys(y), '| casaray-v2 registered =', 'casaray-v2:' in y)
    sys.exit(0)

def norm(p):
    p = p[2:] if p.startswith('./') else p
    p = p[5:] if p.startswith('data/') else p
    return p[2:] if p.startswith('./') else p
WANT = set(['.storage/' + n for n in SAFE + ['onboarding']] + ['configuration.yaml', 'secrets.yaml'])
got, meta = {}, {}
try:
    outer = tarfile.open(fileobj=sys.stdin.buffer, mode='r|')
    for m in outer:
        n = norm(m.name)
        if n == 'backup.json': meta = json.load(outer.extractfile(m))
        elif n.startswith('homeassistant.tar'):
            inner = tarfile.open(fileobj=outer.extractfile(m), mode='r|gz' if n.endswith('gz') else 'r|')
            for im in inner:
                p = norm(im.name)
                if im.isfile() and p in WANT: got[p] = inner.extractfile(im).read()
except Exception as x:
    print('STOP: cannot read backup:', type(x).__name__, x); sys.exit(3)

fail, warn, plan = [], [], []
print('backup: %s | %s | protected=%s' % (meta.get('name'), meta.get('date'), meta.get('protected')))
if meta.get('protected'): fail.append('backup is encrypted; this workflow needs an unencrypted one')
la = ljs('.storage/auth')
prov = js(got.get('.storage/auth_provider.homeassistant', b''))
if not la: fail.append('live .storage/auth unreadable; refusing (the surviving user database is required)')
if live('.storage/auth_provider.homeassistant'): fail.append('live auth_provider.homeassistant already exists; not overwriting')
if prov is None: fail.append('backup has no auth_provider.homeassistant')
if la and prov is not None:
    users = {u.get('id'): u for u in la.get('users', [])}
    creds = [c for c in la.get('credentials', []) if c.get('auth_provider_type') == 'homeassistant']
    names = set(u.get('username') for u in prov.get('users', []))
    print('live users with a login = %d | usernames in backup = %d' % (len(creds), len(names)))
    owner_ok = False
    for c in creds:
        u = (c.get('data') or {}).get('username'); own = bool((users.get(c.get('user_id')) or {}).get('is_owner'))
        ok = u in names; owner_ok = owner_ok or (own and ok)
        print('  %-20s owner=%-5s password in backup=%s' % (u, own, ok))
        if not ok: warn.append('%s has no password in the backup; reset it after recovery' % u)
    if not owner_ok: fail.append('the owner username has no password in the backup')
for n in SAFE:
    p = '.storage/' + n
    if p in got and not live(p): plan.append(p)
bo = js(got.get('.storage/onboarding', b'')) or {}; lo = ljs('.storage/onboarding') or {}
bd, ld = set(bo.get('done') or []), set(lo.get('done') or [])
if bd and bd > ld: plan.append('.storage/onboarding')
print('onboarding: live %s -> backup %s' % (sorted(ld), sorted(bd)))
yb = got.get('configuration.yaml', b'').decode('utf-8', 'replace'); yl = rd('configuration.yaml')
if not yb: warn.append('backup has no configuration.yaml')
elif not set(keys(yb)) - DEFAULT_KEYS: warn.append('backup configuration.yaml is also default; config must be rebuilt later')
elif set(keys(yl)) - DEFAULT_KEYS: warn.append('live configuration.yaml is not default; leaving it alone')
else:
    missing = [t for t in re.findall(r'!include\s+(\S+)', yb) if not live(t)]
    refs = set(re.findall(r'!secret\s+(\w+)', yb)); ls = set(keys(rd('secrets.yaml')))
    bs = set(keys(got.get('secrets.yaml', b'').decode('utf-8', 'replace')))
    if missing: warn.append('configuration.yaml NOT restored: includes missing live: %s' % missing)
    elif refs - ls and not refs <= bs: warn.append('configuration.yaml NOT restored: secrets missing everywhere')
    else:
        plan.append('configuration.yaml')
        if refs - ls: plan.append('secrets.yaml')
print('config: live keys %s | backup keys %s' % (keys(yl), keys(yb)))
print('\nPLAN (%d files):' % len(plan))
for p in plan: print('  %-40s %s' % (p, 'replace (live copy saved first)' if live(p) else 'add (missing live)'))
for w in warn: print('WARN:', w)
for f in fail: print('FAIL:', f)
if fail: sys.exit(3)
if not any(p.endswith('auth_provider.homeassistant') for p in plan): print('FAIL: nothing to repair'); sys.exit(3)
if MODE == 'prepare':
    os.makedirs(R + '/stage', exist_ok=True); os.chmod(R, 0o700)
    for p in plan:
        d = R + '/stage/' + p; os.makedirs(os.path.dirname(d), exist_ok=True)
        with open(d, 'wb') as f: f.write(got[p])
        os.chmod(d, 0o600)
    open(R + '/plan.txt', 'w').write('\n'.join(plan) + '\n')
    open(R + '/PREPARED', 'w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
    print('staged %d files in /config/_recovery/stage (mode 600)' % len(plan))
print('OK')
EOF
)
pyrun() { docker exec -i -e MODE="$1" homeassistant python3 -c "$PY"; }
web() { curl -s -o /dev/null -w "$1" --max-time 5 -L --max-redirs 5 http://127.0.0.1:8123/ 2>/dev/null; }
# Core itself answers /api/ with 401 when it is really up; anything else is not proof.
api() { curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8123/api/ 2>/dev/null; }
running() { [ "$(docker inspect -f '{{.State.Running}}' homeassistant 2>/dev/null)" = true ]; }
cfgcheck() {
  ha core check && return 0
  say "ha core check failed or unavailable while Core is stopped; trying the Core image directly"
  IMG=$(docker inspect -f '{{.Config.Image}}' homeassistant 2>/dev/null) || return 1
  docker run --rm -v "$C:/config" --entrypoint python3 "$IMG" -m homeassistant --script check_config -c /config
}
# Latest CasaRay dashboard + theme from ha-deploy via the repo's own sync script, exported
# to a temp dir so the clone's working tree is never touched. Pre-copies feed rollback.
DASH="dashboards/casaray_v2.yaml themes/deez_your_name.yaml"
dash_sync() {
  mkdir -p "$R/pre"; touch "$R/placed.txt"
  for f in $DASH; do [ -e "$C/$f" ] && [ ! -e "$R/pre/$f" ] && mkdir -p "$(dirname "$R/pre/$f")" && cp -p "$C/$f" "$R/pre/$f"; done
  docker exec homeassistant sh -c 'set -e; X=/config/_recovery/export; rm -rf $X; mkdir -p $X/dashboards $X/themes; cd /config/deez_repo; [ -r /config/.deez_deploy.env ] && . /config/.deez_deploy.env; export DEEZ_GH_TOKEN GIT_ASKPASS=/config/deploy_askpass.sh GIT_TERMINAL_PROMPT=0; g() { git -c safe.directory="*" "$@"; }; g fetch -q origin ha-deploy; echo "[recover] ha-deploy is at $(g rev-parse --short FETCH_HEAD)"; g show FETCH_HEAD:dashboards/casaray_v2.yaml > $X/dashboards/casaray_v2.yaml; g show FETCH_HEAD:themes/deez_your_name.yaml > $X/themes/deez_your_name.yaml; g show FETCH_HEAD:scripts/sync_casaray_to_config.sh > $X/sync.sh; REPO=$X DEST=/config/dashboards THEME_DEST=/config/themes sh $X/sync.sh; rm -rf $X' || return 1
  for f in $DASH; do
    [ -e "$C/$f" ] || continue
    cmp -s "$C/$f" "$R/pre/$f" 2>/dev/null && continue
    grep -qx "$f" "$R/placed.txt" || echo "$f" >> "$R/placed.txt"
  done
}
do_prepare() {   # $1 = 1 when the python check already ran in prepare mode
  FREE=$(df -k /mnt/data | awk 'NR==2{print $4}'); [ "${FREE:-0}" -gt 2000000 ] || die "less than 2 GB free"
  say "checking the backup against the live install and staging the files (about 1 minute)"
  pyrun prepare < "$B" || die "check failed: NOTHING has changed. Photograph the lines above and send them."
  NAME="pre-login-repair-$(date +%Y%m%d-%H%M)"
  say "full backup of the CURRENT install: $NAME (unencrypted, a few minutes)"
  OUT=$(ha backups new --name "$NAME" 2>&1) || { echo "$OUT"; die "backup failed: nothing live has changed"; }
  SLUG=$(echo "$OUT" | sed -n 's/.*slug:[[:space:]]*\([0-9a-f]*\).*/\1/p')
  if [ -n "$SLUG" ] && ha backups info "$SLUG" >/dev/null 2>&1; then :
  elif ha backups list 2>/dev/null | grep -q "$NAME"; then SLUG="$NAME"
  else echo "$OUT"; die "backup not found after creation: nothing live has changed"; fi
  echo "$SLUG" > "$R/pre_backup_slug"; say "backup verified: $SLUG"
}
do_rollback() {
  [ -f "$R/placed.txt" ] || die "nothing recorded as placed"
  mkdir -p "$R/rolledback"
  ha core stop
  while read -r p; do
    [ -n "$p" ] || continue
    mkdir -p "$(dirname "$R/rolledback/$p")"; mv "$C/$p" "$R/rolledback/$p" 2>/dev/null && say "removed: $p"
    [ -e "$R/pre/$p" ] && cp -p "$R/pre/$p" "$C/$p" && say "restored pre-apply copy: $p"
  done < "$R/placed.txt"
  rm -f "$R/APPLIED" "$R/placed.txt"
  ha core start; say "rollback done: files are as they were before apply"
}

do_apply() {
  [ -f "$R/PREPARED" ] && [ -f "$R/plan.txt" ] || die "run prepare first"
  [ -e "$R/APPLIED" ] && die "already applied; use verify or rollback"
  say "will stop Core, then add/replace:"; sed 's/^/    /' "$R/plan.txt"
  say "and sync the CasaRay dashboard + theme from ha-deploy (live copies saved first)"
  printf '[recover] type APPLY to continue: '; read -r ANS; [ "$ANS" = APPLY ] || die "not confirmed; nothing changed"
  mkdir -p "$R/pre"; : > "$R/placed.txt"
  dash_sync || say "WARN: dashboard sync failed; login recovery continues (retry later: sh /tmp/recover_login.sh dashboard)"
  while read -r p; do [ -n "$p" ] && [ -e "$C/$p" ] && mkdir -p "$(dirname "$R/pre/$p")" && cp -p "$C/$p" "$R/pre/$p"; done < "$R/plan.txt"
  ha core stop || die "could not stop Core; nothing changed"
  touch "$R/APPLIED"
  while read -r p; do
    [ -n "$p" ] || continue
    cp -p "$R/stage/$p" "$C/$p" && echo "$p" >> "$R/placed.txt" && say "placed: $p"
  done < "$R/plan.txt"
  if ! cfgcheck; then
    say "config check FAILED: reverting configuration.yaml/secrets.yaml only; auth files stay"
    for p in configuration.yaml secrets.yaml; do
      grep -qx "$p" "$R/placed.txt" || continue
      if [ -e "$R/pre/$p" ]; then cp -p "$R/pre/$p" "$C/$p"; else rm -f "$C/$p"; fi
      grep -vx "$p" "$R/placed.txt" > "$R/placed.tmp"; mv "$R/placed.tmp" "$R/placed.txt"
    done
  fi
  ha core start
  say "waiting for Core (up to 15 minutes)"; i=0
  while [ "$(api)" != 401 ]; do
    i=$((i+1))
    if [ $i -gt 90 ]; then
      if running; then die "Core is running but its API is not answering yet. NOT rolling back. Wait 5 minutes, then: sh /tmp/recover_login.sh verify"; fi
      say "Core container is not running: rolling back automatically"; do_rollback; die "rolled back; send me a photo of: ha core logs | tail -40"
    fi
    sleep "${RC_POLL:-10}"
  done
  pyrun verify < /dev/null
  case "$(web '%{url_effective}')" in *onboarding*) say "WARNING: still redirecting to onboarding" ;; *) say "front page no longer redirects to onboarding" ;; esac
  say "DONE. Log in on the iPad with your usual owner username and password."
  say "If anything is wrong: sh /tmp/recover_login.sh rollback"
}

case "$MODE" in
run)
  [ -f "$B" ] || die "backup not found: $B"
  [ -e "$R/APPLIED" ] && die "a repair is already applied; use verify or rollback"
  do_prepare
  do_apply ;;
check)
  [ -f "$B" ] || die "backup not found: $B"; df -h /mnt/data | tail -1
  pyrun check < "$B" ;;
prepare)
  [ -f "$B" ] || die "backup not found: $B"
  [ -e "$R/APPLIED" ] && die "a repair is already applied; use verify or rollback"
  do_prepare
  say "prepared. Nothing live has changed. Next, with approval: sh /tmp/recover_login.sh apply" ;;
apply)
  do_apply ;;
verify)
  pyrun verify < /dev/null; say "Core API: $(api) (401 = up) | front page -> $(web '%{url_effective}')" ;;
dashboard)
  running || die "Core is not running"
  dash_sync || die "dashboard sync failed"
  say "done: refresh the CasaRay page on the iPad (a changed theme needs Developer Tools -> YAML -> Reload themes)" ;;
rollback)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  printf '[recover] type ROLLBACK to stop Core and undo the repair: '; read -r ANS
  [ "$ANS" = ROLLBACK ] || die "not confirmed"; do_rollback ;;
finish)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  rm -rf "$R/stage" && say "staged copies deleted; pre-apply copies kept in $R/pre" ;;
*) die "unknown mode: $MODE" ;;
esac
