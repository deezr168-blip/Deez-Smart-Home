#!/bin/sh
#
# WITHDRAWN 2026-09-29 -- DO NOT RUN. Two defects: (1) calls runner.HassEventLoopPolicy,
# removed in 2026.9; (2) its reconstructed configuration.yaml registers the legacy dashboard
# as YAML at url_path deez-smart-home, which is a UI (storage) dashboard -- a conflict.
# Superseded by fix_owner_login.sh (login) and casaray_config_block.yaml (CasaRay).
# CasaRay — rebuild the missing Home Assistant password store, keeping every user ID.
#
# The 25 Sep backup has no .storage/auth_provider.homeassistant, and `ha auth reset` fails
# because that store is empty. The users and their login records (.storage/auth) survive,
# and at login Home Assistant looks up the EXISTING login record by normalised username
# (auth/providers/homeassistant.py: async_get_or_create_credentials). So re-adding each
# username to the password store -- with Home Assistant's own provider code, the same path
# as `hass --script auth add` -- reconnects every login to its existing user.
#
#   sh /tmp/repair_login.sh check      read-only report (default)
#   sh /tmp/repair_login.sh run        report -> set passwords (hidden) -> type APPLY ->
#                                      CasaRay dashboard+theme from ha-deploy -> stop Core ->
#                                      rebuild password store -> finish onboarding -> restore
#                                      config (validated) -> start Core -> verify
#   sh /tmp/repair_login.sh verify | rollback | dashboard | finish
#
# Never edits users, login records, tokens, integrations, registries, Zigbee, Matter or
# databases. Never prints a password, hash, token or key.
set -u
echo "[repair] WITHDRAWN: use fix_owner_login.sh and scripts/recovery/casaray_config_block.yaml"; exit 2
MODE="${1:-check}"
B="${2:-/mnt/data/supervisor/backup/e6cc88bd.tar}"   # optional: source of other missing files
SAFETY="${SAFETY:-b0206554}"
C="${RC_HOST_CONFIG:-/mnt/data/supervisor/homeassistant}"
R="$C/_recovery"
TTY="${RC_TTY:-/dev/tty}"
say() { echo "[repair] $*"; }
die() { echo "[repair] STOP: $*"; exit 1; }

PLANPY=$(cat <<'EOF'
import sys, os, re, json, tarfile
MODE = os.environ.get('MODE', 'plan'); CFG = os.environ.get('RCFG', '/config'); R = CFG + '/_recovery'
live = lambda p: os.path.exists(CFG + '/' + p)
def ljs(p):
    try: return json.load(open(CFG + '/' + p))
    except Exception: return None
def rd(p):
    try: return open(CFG + '/' + p, encoding='utf-8', errors='replace').read()
    except Exception: return ''
keys = lambda y: re.findall(r'(?m)^([a-z_]+):', y)
norm = lambda u: u.strip().casefold()
DEFAULT_KEYS = {'default_config', 'frontend', 'automation', 'script', 'scene'}

if MODE == 'verify':
    p = (ljs('.storage/auth_provider.homeassistant') or {}).get('data', {})
    print('  password store: %s, %d username(s)' % ('present' if p else 'MISSING', len(p.get('users', []))))
    print('  onboarding done =', ((ljs('.storage/onboarding') or {}).get('data') or {}).get('done'))
    print('  time_zone =', ((ljs('.storage/core.config') or {}).get('data') or {}).get('time_zone', 'not set (core.config missing)'))
    y = rd('configuration.yaml'); print('  configuration.yaml keys =', keys(y), '| casaray-v2 registered =', 'casaray-v2:' in y)
    sys.exit(0)

fail, warn, plan = [], [], []
a = (ljs('.storage/auth') or {}).get('data')
if not a: fail.append('.storage/auth unreadable: refusing (the surviving user database is required)')
if live('.storage/auth_provider.homeassistant'): fail.append('a password store already exists; this repair only rebuilds a MISSING one')
users_out = []
if a:
    users = {u['id']: u for u in a.get('users', [])}
    creds = [c for c in a.get('credentials', []) if c.get('auth_provider_type') == 'homeassistant']
    seen = {}
    print('login records (Home Assistant logins):')
    for c in creds:
        u = users.get(c.get('user_id'))
        name = (c.get('data') or {}).get('username', '')
        if u is None: warn.append('login %r points at a missing user; skipped' % name); continue
        n = norm(name)
        if n in seen: fail.append('two login records normalise to the same username %r' % n); continue
        seen[n] = 1
        own = bool(u.get('is_owner')); act = u.get('is_active', True)
        print('  %-24s owner=%-5s active=%-5s person=%s' % (n, own, act, u.get('name')))
        users_out.append('%s %s' % (n, 'owner' if own else 'user'))
    if not any(l.endswith(' owner') for l in users_out): fail.append('no owner login record found')
lo = ((ljs('.storage/onboarding') or {}).get('data') or {}).get('done')
print('onboarding done =', lo, '(will be completed)')
got = {}
if os.environ.get('HAVE_BACKUP') == '1':
    SAFE = ['core.config', 'backup', 'person', 'input_boolean', 'input_number', 'input_select', 'input_text',
            'input_datetime', 'input_button', 'counter', 'timer', 'schedule', 'lovelace', 'lovelace_dashboards',
            'lovelace_resources', 'core.area_registry', 'core.floor_registry', 'core.label_registry']
    want = set(['.storage/' + n for n in SAFE] + ['configuration.yaml'])
    try:
        outer = tarfile.open(fileobj=sys.stdin.buffer, mode='r|')
        for m in outer:
            n = m.name[2:] if m.name.startswith('./') else m.name
            if n.startswith('homeassistant.tar'):
                inner = tarfile.open(fileobj=outer.extractfile(m), mode='r|gz' if n.endswith('gz') else 'r|')
                for im in inner:
                    p = im.name
                    for pre in ('./', 'data/', './'):
                        p = p[len(pre):] if p.startswith(pre) else p
                    if im.isfile() and p in want: got[p] = inner.extractfile(im).read()
    except Exception as x:
        warn.append('backup not readable (%s); continuing without it' % type(x).__name__)
    for p in sorted(got):
        if p.startswith('.storage/') and not live(p): plan.append(p)
    print('from backup, missing live:', [p for p in plan] or 'none')
yl = rd('configuration.yaml')
cands = []
if set(keys(yl)) - DEFAULT_KEYS:
    print('configuration.yaml: already customised; left alone')
else:
    yb = got.get('configuration.yaml', b'').decode('utf-8', 'replace')
    if yb and set(keys(yb)) - DEFAULT_KEYS and not [t for t in re.findall(r'!include\s+(\S+)', yb) if not live(t)]:
        cands.append(('original from backup', yb))
    dash = ''
    for key, title, icon, fn in [('deez-smart-home', 'Deez Smart Home', 'mdi:home-assistant', 'dashboards/deez_smart_home.yaml'),
                                 ('casaray-v2', 'CasaRay', 'mdi:home-heart', 'dashboards/casaray_v2.yaml')]:
        if live(fn):
            dash += '    %s:\n      mode: yaml\n      title: %s\n      icon: %s\n      show_in_sidebar: true\n      filename: %s\n' % (key, title, icon, fn)
    pk = [f for f in os.listdir(CFG + '/packages') if f.endswith('.yaml')] if os.path.isdir(CFG + '/packages') else []
    base = yl.rstrip() + '\n\n# Restored by CasaRay recovery (scripts/recovery/repair_login.sh)\n'
    lov = ('lovelace:\n  dashboards:\n' + dash) if dash else ''
    if pk and lov: cands.append(('default + packages + dashboards', base + 'homeassistant:\n  packages: !include_dir_named packages\n' + lov))
    if pk and not lov: cands.append(('default + packages', base + 'homeassistant:\n  packages: !include_dir_named packages\n'))
    if lov: cands.append(('default + dashboards', base + lov))
    print('packages/*.yaml =', len(pk), '| dashboards present =', [k for k in ('deez_smart_home.yaml', 'casaray_v2.yaml') if live('dashboards/' + k)])
    defs = ' '.join(rd('packages/' + f) for f in pk)
    print('helpers defined in packages: chinese_dashboard=%s' % ('chinese_dashboard:' in defs))
    print('config candidates (tried in order, first that validates wins):', [c[0] for c in cands] or 'none')
for w in warn: print('WARN:', w)
for f in fail: print('FAIL:', f)
if fail: sys.exit(3)
if MODE == 'plan' and os.environ.get('STAGE') == '1':
    os.makedirs(R + '/stage/.storage', exist_ok=True); os.chmod(R, 0o700)
    for p in plan:
        with open(R + '/stage/' + p, 'wb') as f: f.write(got[p])
        os.chmod(R + '/stage/' + p, 0o600)
    for i, (label, text) in enumerate(cands):
        open(R + '/stage/cand%d.yaml' % i, 'w').write(text)
    open(R + '/plan.txt', 'w').write(''.join(p + '\n' for p in plan))
    open(R + '/cands.txt', 'w').write(''.join('cand%d.yaml %s\n' % (i, c[0]) for i, c in enumerate(cands)))
    open(R + '/users.txt', 'w').write(''.join(l + '\n' for l in users_out))
print('OK')
EOF
)

# Runs in the Core IMAGE while Core is stopped. Credentials arrive on stdin as
# username/password line pairs and are never printed.
AUTHPY=$(cat <<'EOF'
import sys, os, json, asyncio
from homeassistant import runner
from homeassistant.auth import auth_manager_from_config
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.components.onboarding import OnboardingStorage, STORAGE_KEY, STORAGE_VERSION
from homeassistant.components.onboarding.const import STEPS
CFG = os.environ.get('RCFG', '/config')
raw = sys.stdin.read().split('\n')
pairs = [(raw[i].strip().casefold(), raw[i + 1]) for i in range(0, len(raw) - 1, 2) if raw[i].strip()]
def core():
    d = json.load(open(CFG + '/.storage/auth'))['data']
    return json.dumps([d.get('users'), d.get('credentials')], sort_keys=True)
async def main():
    before = core()
    hass = HomeAssistant(CFG)
    await asyncio.gather(dr.async_load(hass), er.async_load(hass))
    hass.auth = await auth_manager_from_config(hass, [{'type': 'homeassistant'}], [])
    prov = hass.auth.auth_providers[0]
    await prov.async_initialize()
    if prov.data.users: print('FAIL: password store is not empty; refusing'); sys.exit(4)
    known = {prov.data.normalize_username(c.data['username']): c for c in await prov.async_credentials()}
    for u, p in pairs:
        if u not in known: print('FAIL: no login record for', u); sys.exit(4)
        if len(p) < 1: print('FAIL: empty password for', u); sys.exit(4)
        prov.data.add_auth(u, p)
    await prov.data.async_save()
    for u, p in pairs:
        prov.data.validate_login(u, p)
        c = await prov.async_get_or_create_credentials({'username': u})
        if c.id != known[u].id or c.is_new: print('FAIL: login for', u, 'would not map to its existing user'); sys.exit(4)
        print('  password set and verified for %s -> existing user kept' % u)
    store = OnboardingStorage(hass, STORAGE_VERSION, STORAGE_KEY, private=True)
    data = await store.async_load() or {'done': []}
    data['done'] = [s for s in STEPS if s in data['done']] + [s for s in STEPS if s not in data['done']]
    await store.async_save(data)
    print('  onboarding marked complete:', data['done'])
    await hass.async_stop()
    if core() != before: print('FAIL: users or login records changed unexpectedly'); sys.exit(5)
    print('  users and login records unchanged: OK')
asyncio.set_event_loop_policy(runner.HassEventLoopPolicy(False))
asyncio.run(main())
EOF
)

pyrun() { docker exec -i -e MODE="$1" -e STAGE="${STAGE:-0}" -e HAVE_BACKUP="${HAVE_BACKUP:-0}" homeassistant python3 -c "$PLANPY"; }
img() { docker inspect -f '{{.Config.Image}}' homeassistant 2>/dev/null; }
api() { curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8123/api/ 2>/dev/null; }
running() { [ "$(docker inspect -f '{{.State.Running}}' homeassistant 2>/dev/null)" = true ]; }
cfgcheck() {
  ha core check && return 0
  docker run --rm -v "$C:/config" --entrypoint python3 "$(img)" -m homeassistant --script check_config -c /config
}
DASH="dashboards/casaray_v2.yaml themes/deez_your_name.yaml"
precopy() { for f in "$@"; do [ -e "$C/$f" ] && [ ! -e "$R/pre/$f" ] && mkdir -p "$(dirname "$R/pre/$f")" && cp -p "$C/$f" "$R/pre/$f"; done; return 0; }
mark() { grep -qx "$1" "$R/placed.txt" 2>/dev/null || echo "$1" >> "$R/placed.txt"; }
dash_sync() {
  mkdir -p "$R/pre"; touch "$R/placed.txt"; precopy $DASH
  docker exec homeassistant sh -c 'set -e; X=/config/_recovery/export; rm -rf $X; mkdir -p $X/dashboards $X/themes; cd /config/deez_repo; [ -r /config/.deez_deploy.env ] && . /config/.deez_deploy.env; export DEEZ_GH_TOKEN GIT_ASKPASS=/config/deploy_askpass.sh GIT_TERMINAL_PROMPT=0; g() { git -c safe.directory="*" "$@"; }; g fetch -q origin ha-deploy; echo "[repair] ha-deploy is at $(g rev-parse --short FETCH_HEAD)"; g show FETCH_HEAD:dashboards/casaray_v2.yaml > $X/dashboards/casaray_v2.yaml; g show FETCH_HEAD:themes/deez_your_name.yaml > $X/themes/deez_your_name.yaml; g show FETCH_HEAD:scripts/sync_casaray_to_config.sh > $X/sync.sh; REPO=$X DEST=/config/dashboards THEME_DEST=/config/themes sh $X/sync.sh; rm -rf $X' || return 1
  for f in $DASH; do [ -e "$C/$f" ] && ! cmp -s "$C/$f" "$R/pre/$f" 2>/dev/null && mark "$f"; done; return 0
}
do_rollback() {
  [ -f "$R/placed.txt" ] || die "nothing recorded as changed"
  mkdir -p "$R/rolledback"; ha core stop
  while read -r p; do
    [ -n "$p" ] || continue
    mkdir -p "$(dirname "$R/rolledback/$p")"; mv "$C/$p" "$R/rolledback/$p" 2>/dev/null && say "removed: $p"
    [ -e "$R/pre/$p" ] && cp -p "$R/pre/$p" "$C/$p" && say "restored pre-repair copy: $p"
  done < "$R/placed.txt"
  rm -f "$R/APPLIED" "$R/placed.txt"; ha core start; say "rollback done: files are as they were before the repair"
}
askpw() {  # $1 username -> sets PW (hidden input, typed twice)
  while :; do
    printf '[repair] new password for %s: ' "$1"; stty -echo 2>/dev/null; read -r PW; stty echo 2>/dev/null; echo
    [ -n "$PW" ] || return 1
    printf '[repair] again: '; stty -echo 2>/dev/null; read -r PW2; stty echo 2>/dev/null; echo
    [ "$PW" = "$PW2" ] && { PW2=; return 0; }; say "did not match, try again"
  done
}

case "$MODE" in
check)
  running || die "Core must be running for the read-only check"
  if [ -f "$B" ]; then HAVE_BACKUP=1 pyrun plan < "$B"; else pyrun plan < /dev/null; fi ;;
run)
  running || die "Core must be running to start"
  [ -e "$R/APPLIED" ] && die "a repair is already applied; use verify or rollback"
  ha backups info "$SAFETY" >/dev/null 2>&1 || die "safety backup $SAFETY not found (set SAFETY=<slug> if it has another ID)"
  say "safety backup $SAFETY is present"
  FREE=$(df -k /mnt/data | awk 'NR==2{print $4}'); [ "${FREE:-0}" -gt 1000000 ] || die "less than 1 GB free"
  rm -rf "$R/stage" "$R/plan.txt" "$R/cands.txt"; mkdir -p "$R"
  if [ -f "$B" ]; then STAGE=1 HAVE_BACKUP=1 pyrun plan < "$B"; else STAGE=1 pyrun plan < /dev/null; fi || die "check failed: NOTHING has changed. Photograph the lines above."
  CREDS=""; OWNER=""
  while read -r U ROLE; do
    [ -n "$U" ] || continue
    if [ "$ROLE" = owner ]; then
      say "owner login: $U  (your old password is fine, or choose a new one)"
      askpw "$U" <"$TTY" || die "owner password is required; nothing changed"; OWNER="$U"
    else
      say "user login: $U  (Enter to skip; a skipped user cannot log in until this is re-run)"
      askpw "$U" <"$TTY" || { say "skipped $U"; continue; }
    fi
    CREDS="$CREDS$U
$PW
"; PW=
  done < "$R/users.txt"
  say "ready: stop Core, rebuild the password store, complete onboarding, restore configuration,"
  say "and sync the CasaRay dashboard + theme from ha-deploy. Live copies are saved first."
  printf '[repair] type APPLY to continue: '; read -r ANS <"$TTY"; [ "$ANS" = APPLY ] || { CREDS=; die "not confirmed; nothing changed"; }
  mkdir -p "$R/pre"; : > "$R/placed.txt"
  precopy .storage/auth .storage/onboarding configuration.yaml
  while read -r p; do precopy "$p"; done < "$R/plan.txt"
  dash_sync || say "WARN: dashboard sync failed; login repair continues (later: sh /tmp/repair_login.sh dashboard)"
  IMG=$(img); [ -n "$IMG" ] || die "cannot identify the Core image; nothing changed"
  ha core stop || die "could not stop Core; only the dashboard files may have changed (rollback restores them)"
  touch "$R/APPLIED"
  while read -r p; do [ -n "$p" ] && cp -p "$R/stage/$p" "$C/$p" && mark "$p" && say "restored from backup: $p"; done < "$R/plan.txt"
  mark .storage/auth_provider.homeassistant; mark .storage/onboarding
  if ! printf '%s' "$CREDS" | docker run --rm -i -v "$C:/config" --entrypoint python3 "$IMG" -c "$AUTHPY"; then
    CREDS=; say "password rebuild FAILED: rolling back"; do_rollback; die "rolled back; photograph the lines above"
  fi
  CREDS=
  if ! cmp -s "$C/.storage/auth" "$R/pre/.storage/auth"; then say "note: Home Assistant rewrote .storage/auth (users and login records verified identical)"; fi
  if [ -s "$R/cands.txt" ]; then
    OK=""
    while read -r F LABEL; do
      cp -p "$R/stage/$F" "$C/configuration.yaml"; mark configuration.yaml
      say "validating configuration: $LABEL"
      if cfgcheck >/dev/null 2>&1; then OK="$LABEL"; break; fi
    done < "$R/cands.txt"
    if [ -n "$OK" ]; then say "configuration restored: $OK"; else cp -p "$R/pre/configuration.yaml" "$C/configuration.yaml"; say "WARN: no candidate validated; default configuration kept (login still repaired)"; fi
  fi
  ha core start
  say "waiting for Core (up to 15 minutes)"; i=0
  while [ "$(api)" != 401 ]; do
    i=$((i+1))
    if [ $i -gt 90 ]; then
      running && die "Core is running but its API is not answering yet. NOT rolling back. Wait 5 minutes, then: sh /tmp/repair_login.sh verify"
      say "Core container is not running: rolling back automatically"; do_rollback; die "rolled back; photograph: ha core logs | tail -40"
    fi
    sleep "${RC_POLL:-10}"
  done
  pyrun verify < /dev/null
  say "DONE. On the iPad, log in as '$OWNER' with the password you just set."
  say "Set Time zone and Location in Settings > System > General if they show defaults."
  say "Anything wrong: sh /tmp/repair_login.sh rollback" ;;
verify)
  pyrun verify < /dev/null; say "Core API: $(api) (401 = up)" ;;
dashboard)
  running || die "Core is not running"; dash_sync || die "dashboard sync failed"
  say "done: refresh CasaRay on the iPad" ;;
rollback)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  printf '[repair] type ROLLBACK to stop Core and undo the repair: '; read -r ANS <"$TTY"
  [ "$ANS" = ROLLBACK ] || die "not confirmed"; do_rollback ;;
finish)
  [ -e "$R/APPLIED" ] || die "nothing applied"
  rm -rf "$R/stage" "$R/users.txt" && say "staged copies deleted; pre-repair copies kept in $R/pre" ;;
*) die "unknown mode: $MODE" ;;
esac
