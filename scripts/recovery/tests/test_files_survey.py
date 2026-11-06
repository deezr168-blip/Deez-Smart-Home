"""Fixture tests for scripts/recovery/files_survey.py (read-only recovery survey).

    python3 -I scripts/recovery/tests/test_files_survey.py

Builds a simulated Green in a temporary folder: a live /config with the folders
that went missing, three backups in the Supervisor's own layout (outer tar,
backup.json last, homeassistant.tar.gz holding data/...): one plain, one
encrypted, one corrupt. A fake Supervisor and Core API answers on 127.0.0.1.
The script must never ask it for a backup download: the real Supervisor proxy
would hold a whole backup in memory.

Every run is wrapped in strace: the assertions cover every file the script
opened for writing and every file-changing system call, not only what it
printed. Every sensitive dummy value is a canary that must never reach the
output. Negative controls prove the canary check, the strace check and the
static check can each fail.

Needs strace. Prints SKIP and exits 0 without it.
"""
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(REPO, "scripts/recovery/files_survey.py")

TOKEN = "SUPERVISOR-TOKEN-CANARY-7f3a9c"
CANARIES = [TOKEN, "SECRET-CANARY", "TITLE-CANARY", "INSTANCE-CANARY",
            "DOCKER-CANARY", "USERNAME-CANARY", "HASH-CANARY", "AUTOMATION-CANARY"]
PLAIN, LOCKED, CLOUD = "a1b2c3d4", "9e00cb51", "c0c0c0c0"
NOW = time.time()
OLD = NOW - 5 * 86400

DEFAULT_CONFIG = """# Loads default set of integrations. Do not remove.
default_config:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
"""
THEME = "CasaRay V3:\n  primary-color: '#e0a14a'\n"
AUTOMATIONS = ("- id: '1'\n  alias: AUTOMATION-CANARY one\n  triggers: []\n"
               "- id: '2'\n  alias: two\n- id: '3'\n  alias: three\n")
FAILS = []
PASSES = [0]


def check(cond, msg):
    if cond:
        PASSES[0] += 1
    else:
        FAILS.append(msg)
        print("FAIL:", msg)


def storage(key, data):
    return json.dumps({"version": 1, "minor_version": 1, "key": key, "data": data})


def hacs_repos(entries):
    data = {}
    for i, (category, name, version, domain) in enumerate(entries):
        data[str(1000 + i)] = {"category": category, "full_name": name, "installed": True,
                               "version_installed": version, "domain": domain,
                               "authors": ["USERNAME-CANARY"]}
    data["999"] = {"category": "integration", "full_name": "someone/not-installed", "installed": False}
    return storage("hacs.repositories", data)


BACKUP_FILES = {
    "configuration.yaml": DEFAULT_CONFIG + "homeassistant:\n  packages: !include_dir_named packages\n",
    "automations.yaml": AUTOMATIONS,
    "scripts.yaml": "morning:\n  alias: m\nnight:\n  alias: n\n",
    "scenes.yaml": "[]\n",
    "secrets.yaml": "api_key: SECRET-CANARY\n",
    "home-assistant_v2.db": "x" * 4096,
    ".storage/auth": json.dumps({"data": {"users": [{"name": "USERNAME-CANARY"}],
                                          "refresh_tokens": [{"token": "SECRET-CANARY"}]}}),
    ".storage/auth_provider.homeassistant": json.dumps({"data": {"users": [
        {"username": "USERNAME-CANARY", "password": "HASH-CANARY"}]}}),
    ".storage/core.config_entries": storage("core.config_entries", {"entries": [
        {"domain": "hacs", "title": "TITLE-CANARY", "data": {"token": "SECRET-CANARY"}},
        {"domain": "webrtc", "title": "WebRTC TITLE-CANARY", "data": {}},
        {"domain": "zha", "title": "Zigbee", "data": {"device": "SECRET-CANARY"}},
        {"domain": "oldthing", "title": "gone", "data": {}}]}),
    ".storage/hacs.repositories": hacs_repos([
        ("integration", "hacs/integration", "2.0.5", "hacs"),
        ("integration", "AlexxIT/WebRTC", "v3.6.1", "webrtc"),
        ("plugin", "thomasloven/lovelace-card-mod", "4.1.0", "-"),
        ("plugin", "piitaya/lovelace-mushroom", "v4.5.0", "-")]),
    ".storage/lovelace_resources": storage("lovelace_resources", {"items": [
        {"id": "1", "type": "module", "url": "/hacsfiles/lovelace-card-mod/card-mod.js?hacstag=1"},
        {"id": "2", "type": "module", "url": "/hacsfiles/lovelace-mushroom/mushroom.js?hacstag=2"}]}),
    "custom_components/hacs/manifest.json": json.dumps({"domain": "hacs", "name": "HACS", "version": "2.0.5"}),
    "custom_components/hacs/__init__.py": "# hacs\n",
    "custom_components/webrtc/manifest.json": json.dumps({"domain": "webrtc", "name": "WebRTC Camera",
                                                          "version": "v3.6.1"}),
    "custom_components/webrtc/www/webrtc-camera.js": "// js\n",
    "www/community/lovelace-card-mod/card-mod.js": "// card-mod\n",
    "www/community/lovelace-mushroom/mushroom.js": "// mushroom\n",
    "www/your_name_night_sky.jpg": "jpg",
    "themes/deez_your_name.yaml": "CasaRay:\n  a: b\n",
    "dashboards/casaray_v2.yaml": "views: []\n",
    "packages/casaray_automation.yaml": "{}\n",
}


def inner_archive(files, mtime):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        meta = json.dumps({"version": "2026.9.2"}).encode()
        info = tarfile.TarInfo("./homeassistant.json")
        info.size, info.mtime = len(meta), mtime
        tar.addfile(info, io.BytesIO(meta))
        root = tarfile.TarInfo("data")
        root.type, root.mtime = tarfile.DIRTYPE, mtime
        tar.addfile(root)
        for rel, text in sorted(files.items()):
            body = text.encode()
            info = tarfile.TarInfo("data/" + rel)
            info.size, info.mtime = len(body), mtime
            tar.addfile(info, io.BytesIO(body))
    return gzip.compress(raw.getvalue())


def backup_json(slug, protected, automatic):
    return json.dumps({
        "slug": slug, "name": "Backup %s" % slug, "date": "2026-11-01T04:45:00+11:00", "type": "full",
        "protected": protected, "compressed": True, "crypto": "aes128" if protected else None,
        "homeassistant": {"version": "2026.9.2", "exclude_database": False},
        "folders": ["share", "ssl"], "addons": [{"slug": "a0d7b954_vscode", "name": "Studio Code Server"}],
        "docker": {"registries": {"ghcr.io": {"username": "USERNAME-CANARY", "password": "DOCKER-CANARY"}}},
        "extra": {"instance_id": "INSTANCE-CANARY", "with_automatic_settings": automatic},
    }).encode()


def outer_archive(slug, protected, inner, automatic=False):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, body in (("./homeassistant.tar.gz", inner), ("./share.tar.gz", gzip.compress(b"share")),
                           ("./backup.json", backup_json(slug, protected, automatic))):
            info = tarfile.TarInfo(name)
            info.size, info.mtime = len(body), OLD
            tar.addfile(info, io.BytesIO(body))
    return raw.getvalue()


def write(path, text, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)
    if mtime:
        os.utime(path, (mtime, mtime))


def build_world(root):
    cfg = root + "/config"
    write(cfg + "/configuration.yaml", DEFAULT_CONFIG)
    for name in ("automations.yaml",):
        write(cfg + "/" + name, "[]\n")
    for name in ("scripts.yaml", "scenes.yaml"):
        write(cfg + "/" + name, "")
    write(cfg + "/secrets.yaml", "api_key: SECRET-CANARY\n")
    write(cfg + "/.HA_VERSION", "2026.9.2")
    write(cfg + "/themes/casaray_v3.yaml", THEME)
    os.makedirs(cfg + "/www", exist_ok=True)
    write(cfg + "/.storage/core.restore_state", "{}", NOW - 120)
    write(cfg + "/.storage/core.entity_registry", "{}", NOW - 3600)
    write(cfg + "/.storage/core.config_entries", BACKUP_FILES[".storage/core.config_entries"])
    write(cfg + "/.storage/auth", BACKUP_FILES[".storage/auth"])
    write(cfg + "/.storage/hacs.repositories", hacs_repos([
        ("integration", "hacs/integration", "2.0.6", "hacs"),
        ("integration", "AlexxIT/WebRTC", "v3.6.1", "webrtc"),
        ("plugin", "thomasloven/lovelace-card-mod", "4.1.0", "-")]))
    write(cfg + "/.storage/lovelace_resources", storage("lovelace_resources", {"items": []}))
    write(cfg + "/.storage/lovelace_dashboards", storage("lovelace_dashboards", {"items": [
        {"id": "d1", "url_path": "deez-smart-home", "mode": "storage", "title": "TITLE-CANARY"},
        {"id": "d2", "url_path": "casaray-v3", "mode": "storage", "title": "CasaRay V3 Preview"}]}))
    write(root + "/data/options.json", json.dumps({"init_commands": ["SECRET-CANARY"]}))
    os.symlink("/config", root + "/homeassistant")
    write(root + "/proc/mounts", "/dev/mmcblk0p8 /config ext4 rw,relatime 0 0\n")
    write(root + "/share/old_copy/custom_components/hacs/manifest.json", "{}")
    write(root + "/share/manual_export.zip", "zip")
    os.makedirs(root + "/backup", exist_ok=True)
    plain = outer_archive(PLAIN, False, inner_archive(BACKUP_FILES, OLD))
    locked = outer_archive(LOCKED, True, os.urandom(4096), automatic=True)
    for name, body in (("plain_backup.tar", plain), ("Automatic_backup_2026.9.2.tar", locked),
                       ("corrupt.tar", plain[: len(plain) // 3])):
        with open(root + "/backup/" + name, "wb") as handle:
            handle.write(body)


class Fake:
    requests = []
    methods = []
    paths = []


def make_handler():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):  # never used by a read-only script
            Fake.methods.append(self.command)
            Fake.requests.append((self.command, self.path))
            self.reply({"result": "error"}, 405)

        do_DELETE = do_PUT = do_POST

        def do_GET(self):
            Fake.methods.append("GET")
            Fake.paths.append(self.path)
            Fake.requests.append(("GET", self.path))
            if self.headers.get("Authorization") != "Bearer " + TOKEN:
                return self.reply({"result": "error", "message": "unauthorized"}, 401)
            url = urlparse(self.path)
            ok = lambda data: self.reply({"result": "ok", "data": data})
            backups = {
                PLAIN: {"slug": PLAIN, "name": "Backup plain", "date": "2026-10-30T09:00:00+11:00",
                        "type": "full", "size": 0.01, "size_bytes": 10240, "location": None,
                        "locations": [None], "protected": False, "compressed": True,
                        "content": {"homeassistant": True, "addons": ["a0d7b954_vscode"], "folders": ["share"]}},
                LOCKED: {"slug": LOCKED, "name": "Automatic backup 2026.9.2", "date": "2026-11-01T04:45:00+11:00",
                         "type": "full", "size": 1180.0, "size_bytes": 1237319680, "location": None,
                         "locations": [None], "protected": True, "compressed": True,
                         "content": {"homeassistant": True, "apps": [], "folders": ["share", "ssl"]}},
                CLOUD: {"slug": CLOUD, "name": "Cloud only", "date": "2026-10-20T04:45:00+11:00",
                        "type": "full", "size": 900.0, "location": ".cloud_backup",
                        "locations": [".cloud_backup"], "protected": True, "compressed": True,
                        "content": {"homeassistant": True, "addons": [], "folders": []}},
            }
            path = url.path
            if path == "/core/info":
                return ok({"version": "2026.9.2", "machine": "green", "ip_address": "SECRET-CANARY"})
            if path == "/supervisor/info":
                return ok({"version": "2026.10.2"})
            if path == "/core/api/config":
                return self.reply({"version": "2026.9.2", "config_dir": "/config", "state": "RUNNING",
                                   "recovery_mode": False, "components": ["zha", "frontend", "backup"],
                                   "latitude": "SECRET-CANARY"})
            if path == "/core/api/states":
                return self.reply([
                    {"entity_id": "automation.one", "state": "on", "attributes": {}},
                    {"entity_id": "automation.two", "state": "unavailable", "attributes": {}},
                    {"entity_id": "script.night", "state": "off", "attributes": {}},
                    {"entity_id": "camera.tapo_c425_north_wall_hd_stream_direct", "state": "unavailable",
                     "attributes": {"friendly_name": "SECRET-CANARY"}},
                    {"entity_id": "binary_sensor.f_contact_sensor_door", "state": "unavailable",
                     "attributes": {"device_class": "door"}},
                    {"entity_id": "binary_sensor.kitchen_motion", "state": "unavailable",
                     "attributes": {"device_class": "motion"}},
                    {"entity_id": "sensor.temp", "state": "unavailable", "attributes": {}}])
            if path == "/core/api/config/config_entries/entry":
                return self.reply([
                    {"entry_id": "e1", "domain": "hacs", "title": "TITLE-CANARY", "state": "not_loaded",
                     "disabled_by": None, "reason": "SECRET-CANARY"},
                    {"entry_id": "e2", "domain": "webrtc", "title": "TITLE-CANARY", "state": "not_loaded",
                     "disabled_by": None},
                    {"entry_id": "e3", "domain": "zha", "title": "TITLE-CANARY", "state": "loaded",
                     "disabled_by": None},
                    {"entry_id": "e4", "domain": "cloud", "title": "TITLE-CANARY", "state": "loaded",
                     "disabled_by": None}])
            if path == "/backups":
                return ok({"backups": list(backups.values())})
            m = re.fullmatch(r"/backups/([0-9a-f]+)/info", path)
            if m and m.group(1) in backups:
                b = dict(backups[m.group(1)])
                b.update({"homeassistant": "2026.9.2", "homeassistant_exclude_database": False,
                          "supervisor_version": "2026.10.2",
                          "extra": {"instance_id": "INSTANCE-CANARY",
                                    "with_automatic_settings": m.group(1) == LOCKED},
                          "repositories": ["https://example.invalid/SECRET-CANARY"]})
                return ok(b)
            return self.reply({"result": "error"}, 404)
    return Handler


TRACE_WRITE_FLAGS = re.compile(r"O_(WRONLY|RDWR|CREAT|TRUNC|APPEND)")
MUTATING = ("unlink", "unlinkat", "rename", "renameat", "renameat2", "mkdir", "mkdirat", "rmdir",
            "truncate", "ftruncate", "chmod", "fchmod", "fchmodat", "chown", "fchown", "fchownat",
            "lchown", "symlink", "symlinkat", "link", "linkat", "utime", "utimes", "utimensat",
            "creat", "mknod", "mknodat")


def trace_violations(trace_text):
    bad = []
    for line in trace_text.splitlines():
        call = re.match(r"(?:\[pid\s+\d+\]\s+|\d+\s+)?(\w+)\(", line)
        if not call:
            continue
        name = call.group(1)
        if name in ("open", "openat", "openat2") and TRACE_WRITE_FLAGS.search(line):
            target = re.search(r'"([^"]*)"', line)
            if target and target.group(1) in ("/dev/tty", "/dev/null"):
                continue
            if "= -1" in line:
                continue
            bad.append(line.strip())
        elif name in MUTATING and "= -1" not in line:
            bad.append(line.strip())
    return bad


def run(env, args, stdin_text=None, tmp=None):
    trace = os.path.join(tmp, "trace.%d" % len(os.listdir(tmp)))
    cmd = ["strace", "-f", "-qq", "-o", trace, "-e",
           "trace=open,openat,openat2,creat," + ",".join(MUTATING),
           sys.executable, "-I", "-B", SCRIPT] + args
    proc = subprocess.run(cmd, env=env, input=stdin_text, capture_output=True, text=True, timeout=300)
    with open(trace) as handle:
        traced = handle.read()
    return proc.returncode, proc.stdout + proc.stderr, traced


def snapshot(root):
    state = {}
    for folder, dirs, files in os.walk(root):
        for name in dirs + files:
            path = os.path.join(folder, name)
            st = os.lstat(path)
            state[path] = (st.st_mtime_ns, st.st_size, st.st_mode)
    return state


def leaks(text):
    return [c for c in CANARIES if c in text]


FORBIDDEN_STATIC = [r"\bos\.(remove|unlink|rename|replace|rmdir|mkdir|makedirs|chmod|chown|symlink|link|"
                    r"truncate|utime|system|popen|spawn\w*|exec\w*)\(",
                    r"\bshutil\b", r"\bsubprocess\b", r"\.extractall\(", r"\.extract\(",
                    r"open\([^)]*[\"'][wax+][bt+]?[\"']", r"Request\([^)]*\b(data|method)\s*="]


def static_violations(source):
    return [p for p in FORBIDDEN_STATIC if re.search(p, source)]


def main():
    if not shutil.which("strace"):
        print("SKIP: strace not available")
        return 0
    tmp = tempfile.mkdtemp(prefix="files_survey_")
    traces = tempfile.mkdtemp(prefix="files_survey_trace_")
    try:
        root = os.path.join(tmp, "green")
        os.makedirs(root)
        build_world(root)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler())
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
               "CASARAY_SURVEY_ROOT": root, "CASARAY_SUPERVISOR_URL": "http://127.0.0.1:%d" % port,
               "SUPERVISOR_TOKEN": TOKEN, "CASARAY_SURVEY_TESTING": "1",
               # A proxy that answers nothing: requests reach the fake only if the script bypasses proxies.
               "http_proxy": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9",
               "no_proxy": "", "NO_PROXY": ""}
        before = snapshot(root)
        all_output = []

        rc, out, trace = run(env, ["survey"], tmp=traces)
        all_output.append(out)
        check(rc == 0, "survey exits 0 (got %d)" % rc)
        check("VERDICT: LIVE" in out, "survey proves the live /config")
        check(re.search(r"custom_components\s+MISSING", out), "survey reports custom_components MISSING")
        check(re.search(r"www/community\s+MISSING", out), "survey reports www/community MISSING")
        check(re.search(r"(?m)^\s+www\s+present", out), "survey reports www present")
        check(re.search(r"automations\.yaml\s+\d+ bytes.*entries 0", out), "live automations.yaml has 0 entries")
        check(re.search(r"automation\s+loaded 2 \(unavailable 1\)", out), "running automations counted")
        check("camera.tapo_c425_north_wall_hd_stream_direct" in out and
              "binary_sensor.f_contact_sensor_door" in out, "unavailable security devices listed")
        check("binary_sensor.kitchen_motion" not in out and "sensor.temp" not in out,
              "non-security entities are not listed")
        check(re.search(r"not loaded: hacs\s+state not_loaded", out), "hacs entry shown not loaded")
        check("hacs loaded: no" in out, "hacs not among loaded components")
        check("hacs/integration" in out and "2.0.6" in out, "live HACS records listed")
        check("dashboard resources registered: 0" in out, "empty live resources reported")
        check("casaray-v3 (storage)" in out, "V3 preview dashboard listed by URL path")
        check(hashlib.sha256(THEME.encode()).hexdigest() in out, "theme file hash printed in full")
        check(re.search(r"%s .*protected=False HA=2026\.9\.2" % PLAIN, out), "plain backup listed")
        check(re.search(r"%s .*protected=True .*automatic=True" % LOCKED, out), "encrypted automatic backup listed")
        check(CLOUD in out, "cloud-only backup listed")
        check("unencrypted local backups: %s" % PLAIN in out, "unencrypted local backups identified")
        check("encrypted local backups: %s" % LOCKED in out, "encrypted local backups identified")
        check(re.search(r"corrupt\.tar .*\((ReadError|EOFError|no backup\.json)", out) or
              re.search(r"corrupt\.tar .*slug=\?", out), "corrupt backup flagged")
        check("/share/old_copy/custom_components" in out, "other local copy found")
        check("/share/manual_export.zip" in out, "local archive found")
        check(not trace_violations(trace), "survey: no write-class syscalls %s" % trace_violations(trace)[:3])

        rc, out, trace = run(env, ["contents", PLAIN], tmp=traces)
        all_output.append(out)
        check(rc == 0, "contents (plain) exits 0 (got %d)" % rc)
        check("read: COMPLETE" in out, "plain backup read completely")
        check(re.search(r"hacs\s+\d+ files .*manifest hacs 2\.0\.5 \| HACS live record 2\.0\.6 \| entry not_loaded \| live MISSING", out),
              "hacs component with manifest, live record and entry state")
        check(re.search(r"webrtc\s+\d+ files .*manifest webrtc v3\.6\.1", out), "webrtc component listed")
        check(re.search(r"lovelace-card-mod\s+1 files", out) and "lovelace-mushroom" in out, "community folders listed")
        check("your_name_night_sky.jpg" in out, "other www items listed")
        check(re.search(r"automations\.yaml\s+backup \d+ bytes .* entries 3", out), "backup automations counted")
        check(re.search(r"scripts\.yaml\s+backup \d+ bytes .* entries 2", out), "backup scripts counted")
        check(re.search(r"configuration\.yaml\s+backup .*keys .*homeassistant", out), "backup config keys listed")
        check(re.search(r"secrets\.yaml\s+backup \d+ bytes", out), "secrets.yaml reported by size only")
        check("/hacsfiles/lovelace-card-mod/card-mod.js" in out, "backup resources listed")
        check(re.search(r"domains in the backup but not live: oldthing", out), "entry-domain difference shown")
        check(re.search(r"packages\s+\d+ files .*\| live MISSING", out), "top-level comparison shown")
        check(not trace_violations(trace), "contents: no write-class syscalls %s" % trace_violations(trace)[:3])

        rc, out, _ = run(env, ["contents", LOCKED], tmp=traces)
        all_output.append(out)
        check(rc == 3 and "is ENCRYPTED" in out and "does not open encrypted backups" in out
              and "Nothing was read" in out, "contents refuses an encrypted backup without reading it")

        rc, out, _ = run(env, ["contents", "corrupt.tar"], tmp=traces)
        all_output.append(out)
        check(rc == 5 and "INCOMPLETE" in out, "corrupt backup read reported INCOMPLETE (rc %d)" % rc)
        check("proves nothing" in out, "incomplete read is not taken as evidence")
        check("== C2" not in out and "integrations in the backup" not in out,
              "an incomplete read lists no contents")

        rc, out, _ = run(env, ["contents", "deadbeef"], tmp=traces)
        all_output.append(out)
        check(rc == 3 and "no local file" in out, "unknown slug reported")

        Fake.requests.clear()
        bad = dict(env, CASARAY_SUPERVISOR_URL="http://supervisor.evil.example")
        rc, out, _ = run(bad, ["survey"], tmp=traces)
        all_output.append(out)
        check(rc == 4 and "REFUSED" in out and not Fake.requests, "foreign Supervisor URL refused, nothing sent")

        notoken = {k: v for k, v in env.items() if k != "SUPERVISOR_TOKEN"}
        rc, out, _ = run(notoken, ["survey"], tmp=traces)
        all_output.append(out)
        check(rc == 0 and "SUPERVISOR_TOKEN: NOT SET" in out and "NOT PROVEN" in out,
              "without a token the survey still runs and proves nothing")

        check(Fake.methods and set(Fake.methods) == {"GET"}, "every request was a GET %s" % set(Fake.methods))
        check(Fake.paths and not any("/backup/download" in p or "password=" in p for p in Fake.paths),
              "no backup download was requested through the Supervisor proxy")
        joined = "\n".join(all_output)
        check(not leaks(joined), "no canary in any output: %s" % leaks(joined))
        after = snapshot(root)
        check(before == after, "simulated Green unchanged (no file added, removed or modified)")

        # Negative controls: each check above must be able to fail.
        check(leaks("x " + TOKEN + " y") == [TOKEN], "control: canary check catches a leak")
        probe_file = os.path.join(tmp, "control.txt")
        trace_path = os.path.join(traces, "control.trace")
        subprocess.run(["strace", "-f", "-qq", "-o", trace_path, "-e", "trace=open,openat,openat2",
                        sys.executable, "-I", "-B", "-c", "open(%r, 'w').write('1')" % probe_file],
                       capture_output=True, timeout=60)
        with open(trace_path) as handle:
            check(trace_violations(handle.read()), "control: strace check catches a write")
        with open(SCRIPT) as handle:
            source = handle.read()
        check(not static_violations(source), "static: no forbidden call in the script %s" % static_violations(source))
        check(static_violations(source + "\nopen(p, 'w')\n"), "control: static check catches open(..., 'w')")
        check(static_violations(source + "\nos.remove(p)\n"), "control: static check catches os.remove")
        server.shutdown()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(traces, ignore_errors=True)
    print("%d passed, %d failed" % (PASSES[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
