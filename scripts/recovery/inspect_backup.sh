#!/bin/sh
# CasaRay recovery — READ-ONLY inspection of an unencrypted HA backup.
#   sh /tmp/inspect_backup.sh [backup.tar]   (default: e6cc88bd.tar)
# Streams the backup into Python inside the homeassistant container and
# compares it with the live /config. Writes nothing, extracts nothing to
# disk, restarts nothing. Prints names, dates, sizes, counts, usernames
# and true/false flags only -- never a password hash, token or key.
B="${1:-/mnt/data/supervisor/backup/e6cc88bd.tar}"
[ -f "$B" ] || { echo "backup not found: $B"; exit 2; }
echo "== backup file"; ls -la "$B"
PY=$(cat <<'EOF'
import sys, tarfile, json, os, re, time
CFG = os.environ.get('RCFG', '/config')
T = lambda t: time.strftime('%Y-%m-%d %H:%M', time.gmtime(t)) + 'Z' if t else '-'
WANT = ['.storage/auth_provider.homeassistant', '.storage/core.config', '.storage/backup',
        '.storage/onboarding', '.storage/auth', '.storage/person', '.storage/core.config_entries',
        'configuration.yaml', 'secrets.yaml']
found, bstore, meta, addons, inner_name = {}, set(), None, [], None
tops = {'packages': 0, 'themes': 0, 'dashboards': 0, 'casaray': 0, 'custom_components': 0}
def norm(p):
    p = p[2:] if p.startswith('./') else p
    p = p[5:] if p.startswith('data/') else p
    return p[2:] if p.startswith('./') else p
outer = tarfile.open(fileobj=sys.stdin.buffer, mode='r|')
for m in outer:
    n = norm(m.name)
    if n == 'backup.json':
        meta = json.load(outer.extractfile(m)); continue
    if n.startswith('homeassistant.tar'):
        inner_name = n
        try:
            inner = tarfile.open(fileobj=outer.extractfile(m), mode='r|gz' if n.endswith('gz') else 'r|')
            for im in inner:
                p = norm(im.name)
                if not im.isfile(): continue
                if p.startswith('.storage/'): bstore.add(p[9:])
                t = p.split('/')[0]
                if t in tops: tops[t] += 1
                if p in WANT: found[p] = (im.mtime, im.size, inner.extractfile(im).read())
        except Exception as x:
            print('!! cannot read', n, '->', type(x).__name__, x)
        continue
    if m.isfile(): addons.append('%s (%dMB)' % (n, m.size // 1048576))

def cur(p):
    try: s = os.stat(CFG + '/' + p); return (s.st_mtime, s.st_size)
    except FileNotFoundError: return None
def js(b):
    try: return json.loads(b).get('data', {})
    except Exception: return None
def curjs(p):
    try: return json.load(open(CFG + '/' + p)).get('data', {})
    except Exception: return None

print('\n== 1 backup metadata')
if meta:
    ha = meta.get('homeassistant') or {}
    print('name =', meta.get('name'), '| date =', meta.get('date'), '| type =', meta.get('type'), '| protected =', meta.get('protected'))
    print('HA version =', ha.get('version'), '| database excluded =', ha.get('exclude_database'))
    print('folders =', meta.get('folders'), '| addons =', [a.get('slug') for a in meta.get('addons', [])])
print('inner archive =', inner_name, '| add-on archives =', addons)

print('\n== 2 key files: backup vs live')
print('%-38s %-28s %s' % ('file', 'in backup', 'live now'))
for p in WANT:
    b, c = found.get(p), cur(p)
    print('%-38s %-28s %s' % (p, ('PRESENT %s %dB' % (T(b[0]), b[1])) if b else 'ABSENT',
                               ('%s %dB' % (T(c[0]), c[1])) if c else 'MISSING'))
print('backup dir file counts =', tops)
print('live   dir file counts =', {k: sum(len(f) for _, _, f in os.walk(CFG + '/' + k)) for k in tops})

print('\n== 3 .storage differences (names only)')
live = set(os.listdir(CFG + '/.storage'))
print('in backup, missing live =', sorted(bstore - live))
print('live only (newer)       =', sorted(live - bstore))

print('\n== 4 auth compatibility (usernames and counts only)')
la, bp = curjs('.storage/auth'), js(found.get('.storage/auth_provider.homeassistant', (0, 0, b''))[2])
ba = js(found.get('.storage/auth', (0, 0, b''))[2])
if la:
    lu = [u for u in la.get('users', []) if not u.get('system_generated')]
    lcred = [c for c in la.get('credentials', []) if c.get('auth_provider_type') == 'homeassistant']
    print('live users =', len(lu), '| owners =', sum(1 for u in lu if u.get('is_owner')), '| HA-login credentials =', len(lcred))
    names = set(x.get('username') for x in (bp or {}).get('users', []))
    for c in lcred:
        u = (c.get('data') or {}).get('username')
        owner = any(x.get('is_owner') for x in lu if x.get('id') == c.get('user_id'))
        print('  login %-20s owner=%-5s in backup provider=%s' % (u, owner, u in names))
    if bp is not None: print('backup provider usernames =', sorted(names))
    if ba:
        lid = set(u.get('id') for u in la.get('users', [])); bid = set(u.get('id') for u in ba.get('users', []))
        print('user IDs: live', len(lid), '| backup', len(bid), '| same', len(lid & bid), '| live-only', len(lid - bid))
        lc = set(c.get('id') for c in lcred); bc = set(c.get('id') for c in ba.get('credentials', []))
        print('HA-login credential IDs identical in backup =', lc <= bc)
else:
    print('live .storage/auth unreadable or missing')

print('\n== 5 onboarding / core.config / backup-store (no secrets)')
bo = js(found.get('.storage/onboarding', (0, 0, b''))[2]); lo = curjs('.storage/onboarding')
print('onboarding done: backup =', bo and bo.get('done'), '| live =', lo and lo.get('done'))
bc = js(found.get('.storage/core.config', (0, 0, b''))[2])
if bc: print('backup core.config: time_zone =', bc.get('time_zone'), '| country =', bc.get('country'), '| location set =', bool(bc.get('latitude')))
bb = js(found.get('.storage/backup', (0, 0, b''))[2])
if bb:
    cb = (bb.get('config') or {}).get('create_backup') or {}
    print('backup store: encryption key present =', bool(cb.get('password')), '| agents =', cb.get('agent_ids'),
          '| last auto =', (bb.get('config') or {}).get('last_completed_automatic_backup'))

print('\n== 6 configuration.yaml in backup')
y = found.get('configuration.yaml', (0, 0, b''))[2].decode('utf-8', 'replace')
if y:
    print('top-level keys =', re.findall(r'(?m)^([a-z_]+):', y))
    print('registers casaray-v2 =', 'casaray-v2:' in y, '| legacy dashboard =', 'deez-smart-home' in y,
          '| packages =', bool(re.search(r'packages:\s*!include', y)), '| !secret refs =', len(re.findall(r'!secret\s', y)))
    for kind, tgt in sorted(set(re.findall(r'!(include(?:_dir_\w+)?)\s+(\S+)', y))):
        print('  %-26s %-32s exists live = %s' % (kind, tgt, os.path.exists(CFG + '/' + tgt)))
    print('secrets.yaml live =', os.path.exists(CFG + '/secrets.yaml'))
try: print('live configuration.yaml keys =', re.findall(r'(?m)^([a-z_]+):', open(CFG + '/configuration.yaml').read()))
except Exception as x: print('live configuration.yaml unreadable:', type(x).__name__)
print('\n== END (read-only; nothing was changed)')
EOF
)
echo "== streaming backup into container python (about 1 minute)"
docker exec -i homeassistant python3 -c "$PY" < "$B"
