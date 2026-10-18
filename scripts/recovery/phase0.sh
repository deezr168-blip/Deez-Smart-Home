#!/bin/sh
# CasaRay Phase 0 — READ-ONLY. Run at the Green's console after `login`.
# Changes nothing, restarts nothing, prints no password/token/key.
C=/mnt/data/supervisor/homeassistant
echo "== 1 clock, uptime, containers"; date -u; uptime
docker ps --format '{{.Names}}  {{.Status}}'
echo "== 2 disk"; df -h /mnt/data
du -sh $C $C/home-assistant_v2.db* $C/zigbee.db* $C/deez_repo /mnt/data/supervisor/addons/data /mnt/data/supervisor/backup /mnt/data/supervisor/share /mnt/data/supervisor/media 2>/dev/null
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
echo "== 3 ports 80/443/8123"; (ss -ltnp 2>/dev/null || netstat -ltnp) | grep -E ':(80|443|8123)[[:space:]]'
for p in 8123 80; do echo "-- :$p"; curl -s -o /dev/null -D - http://127.0.0.1:$p/ | grep -iE '^(HTTP|location|server)'; done
echo "== 4 config state (names, dates, booleans only)"
docker exec -i homeassistant python3 - <<'PY'
import json,os,re,time
S='/config/.storage'
def st(p):
    try: s=os.stat(p); return time.strftime('%Y-%m-%d %H:%M',time.gmtime(s.st_mtime))+'Z %dB'%s.st_size
    except FileNotFoundError: return 'MISSING'
def ld(n):
    try: return json.load(open(S+'/'+n)).get('data',{})
    except Exception: return None
for n in ['auth','auth_provider.homeassistant','onboarding','core.config','core.config_entries','core.entity_registry','core.device_registry','person','backup','cloud','lovelace_dashboards','input_boolean']: print('%-30s %s'%('.storage/'+n,st(S+'/'+n)))
for n in ['configuration.yaml','secrets.yaml','automations.yaml','scripts.yaml','scenes.yaml','home-assistant_v2.db','zigbee.db','dashboards/casaray_v2.yaml','dashboards/deez_smart_home.yaml','deploy_deez_dashboard.sh','casaray','packages','themes','custom_components']: print('%-30s %s'%(n,st('/config/'+n)))
o=ld('onboarding'); print('onboarding.done =',o and o.get('done'))
c=ld('core.config') or {}; print('time_zone =',c.get('time_zone'),'| location set =',bool(c.get('latitude')))
a=ld('auth')
if a:
    u=[x for x in a.get('users',[]) if not x.get('system_generated')]; cl=[x for x in a.get('refresh_tokens',[]) if 'claude' in (x.get('client_id') or '')]
    print('auth users =',len(u),'| owners =',sum(1 for x in u if x.get('is_owner')),'| claude tokens =',len(cl),'| claude last used =',max([x.get('last_used_at') or '' for x in cl] or ['none']))
p=ld('auth_provider.homeassistant'); print('login usernames =',p and [x.get('username') for x in p.get('users',[])])
b=ld('backup')
if b:
    k=b.get('config',{}); cb=k.get('create_backup',{})
    print('backup key stored =',bool(cb.get('password')),'| agents =',cb.get('agent_ids'),'| last auto =',k.get('last_completed_automatic_backup'))
e=ld('core.config_entries') or {}; d=sorted({x['domain'] for x in e.get('entries',[])})
print('integrations =',len(d),'| present =',[x for x in ['zha','matter','mcp_server','cloud','hue','tplink','tapo','fronius','powerpal','mobile_app','music_assistant','mqtt'] if x in d])
try: print('configuration.yaml keys =',re.findall(r'(?m)^([a-z_]+):',open('/config/configuration.yaml').read()))
except Exception as x: print('configuration.yaml unreadable:',type(x).__name__)
PY
echo "== 5 default-config / moved-aside evidence"
docker logs homeassistant 2>&1 | grep -iE 'Unable to find configuration|Creating default' | tail -3
ls -la $C/.storage | grep -viE ' (core\.|lovelace|http|person$|input_)' | tail -25
find /mnt/data -xdev \( -name 'auth_provider.homeassistant*' -o -name 'onboarding*' -o -name 'configuration.yaml*' \) 2>/dev/null | grep -vE '/deez_repo/|/addons/git/' | while read f; do stat -c '%y %s %n' "$f"; done
echo "== 6 backups and add-ons"; ha backups list; ha addons | grep -E 'name:|slug:|state:'
echo "== END"
