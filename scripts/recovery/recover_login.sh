#!/bin/sh
# CasaRay — Home Assistant login recovery (targeted, from an unencrypted backup)
#
#   sh /tmp/recover_login.sh check      read-only: verify the backup and plan the repair (default)
#   sh /tmp/recover_login.sh prepare    NON-DISRUPTIVE: fresh full backup of the current install,
#                                       then stage the needed files under /config/_recovery/stage
#   sh /tmp/recover_login.sh apply      DISRUPTIVE (asks you to type APPLY): stops Core, adds the
#                                       missing files, validates config, starts Core, verifies;
#                                       rolls itself back if Core does not come up
#   sh /tmp/recover_login.sh verify     read-only: post-repair state
#   sh /tmp/recover_login.sh rollback   DISRUPTIVE (asks you to type ROLLBACK): back to pre-apply
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
cfgcheck() {
  ha core check && return 0
  say "ha core check failed or unavailable while Core is stopped; trying the Core image directly"
  IMG=$(docker inspect -f '{{.Config.Image}}' homeassistant 2>/dev/null) || return 1
  docker run --rm -v "$C:/config" --entrypoint python3 "$IMG" -m homeassistant --script check_config -c /config
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

case "$MODE" in
check)
  [ -f "$B" ] || die "backup not found: $B"; df -h /mnt/data | tail -1
  pyrun check < "$B" ;;
prepare)
  [ -f "$B" ] || die "backup not found: $B"
  [ -e "$R/APPLIED" ] && die "a repair is already applied; use verify or rollback"
  FREE=$(df -k /mnt/data | awk 'NR==2{print $4}'); [ "${FREE:-0}" -gt 2000000 ] || die "less than 2 GB free"
  pyrun check < "$B" > /dev/null || die "backup check failed; run: sh /tmp/recover_login.sh check"
  say "1/2 full backup of the CURRENT install (unencrypted, a few minutes)"
  OUT=$(ha backups new --name "pre-login-repair-$(date +%Y%m%d-%H%M)" 2>&1) || { echo "$OUT"; die "backup failed"; }
  echo "$OUT" | grep -i slug; mkdir -p "$R"; echo "$OUT" | sed -n 's/.*slug:[[:space:]]*\([0-9a-f]*\).*/\1/p' > "$R/pre_backup_slug"
  say "2/2 staging files from $(basename "$B")"
  pyrun prepare < "$B" || die "staging failed"
  say "prepared. Nothing live has changed. Next, with approval: sh /tmp/recover_login.sh apply" ;;
apply)
  [ -f "$R/PREPARED" ] && [ -f "$R/plan.txt" ] || die "run prepare first"
  [ -e "$R/APPLIED" ] && die "already applied; use verify or rollback"
  say "will stop Core, then add/replace:"; sed 's/^/    /' "$R/plan.txt"
  printf '[recover] type APPLY to continue: '; read -r ANS; [ "$ANS" = APPLY ] || die "not confirmed; nothing changed"
  mkdir -p "$R/pre"; : > "$R/placed.txt"
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
  say "waiting for Core (up to 10 minutes)"; i=0
  while [ "$(web '%{http_code}')" = 000 ] || [ -z "$(web '%{http_code}')" ]; do
    i=$((i+1)); [ $i -gt 60 ] && { say "Core did not come up: rolling back automatically"; do_rollback; die "rolled back; send me: ha core logs | tail -50"; }
    sleep 10
  done
  pyrun verify < /dev/null
  case "$(web '%{url_effective}')" in *onboarding*) say "WARNING: still redirecting to onboarding" ;; *) say "front page no longer redirects to onboarding" ;; esac
  say "DONE. Log in on the iPad with your usual owner username and password."
  say "If anything is wrong: sh /tmp/recover_login.sh rollback" ;;
verify)
  pyrun verify < /dev/null; say "front page -> $(web '%{url_effective}') ($(web '%{http_code}'))" ;;
rollback)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  printf '[recover] type ROLLBACK to stop Core and undo the repair: '; read -r ANS
  [ "$ANS" = ROLLBACK ] || die "not confirmed"; do_rollback ;;
finish)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  rm -rf "$R/stage" && say "staged copies deleted; pre-apply copies kept in $R/pre" ;;
*) die "unknown mode: $MODE" ;;
esac
