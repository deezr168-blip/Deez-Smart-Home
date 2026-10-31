"""Fixture tests for scripts/recovery/register_casaray.sh.

    python3 -I scripts/recovery/tests/test_register_casaray.py

Every scenario builds a throwaway Home Assistant config folder under a temp
directory (never under the repo) from the real repo dashboard and theme files
and the HA 2026.10.1 default configuration.yaml, plus dummy secrets.yaml,
.storage/auth, packages/, deez_repo/ and a 30/09 evidence folder
_recovery/casaray/. The script runs under BusyBox sh with a PATH that holds
ONLY BusyBox applet symlinks plus a fake 'ha' and a fake 'curl' written here.
The fake ha logs every call and implements 'core check' with Home Assistant's
REAL check_config (HA 2026.10.1 venv) against the fixture; the fake curl
answers the Core liveness probe as configured.

Each run is wrapped in strace -f. Assertions cover every file the script
opened (read allowlist), every write-class syscall (write allowlist per mode),
every exec, the token never reaching a command line, canaries never reaching
the output or the run record, the evidence folder staying byte-identical, and
a full before/after snapshot of the fixture. Events of the fake tools and
their children (the check_config process) are excluded from the file
assertions: on the device those run inside Supervisor, not in this script.
Interruptions are simulated by the fake ha (SIGTERM or SIGKILL to the script
during 'core check'); a concurrent edit by strace delaying the theme step's
link() while a harness thread edits configuration.yaml.

Needs strace and BusyBox (env BUSYBOX, else 'busybox' on PATH). Prints SKIP
and exits 0 when either is missing. Optional: dash and shellcheck for the
syntax checks; env HA_CHECK_PYTHON for the check_config interpreter (a Python
with homeassistant 2026.10.1 installed; without it a marker-based fake check is
used and the run says so); env REGISTER_SCRIPT to test another copy; env
ONLY=name,name to run a subset. The disk-full sweep needs root (tmpfs mount)
and prints SKIP without it.
"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# REGISTER_SCRIPT tests another copy (e.g. a deliberately broken one, to prove the assertions bite).
SCRIPT = os.environ.get("REGISTER_SCRIPT") or os.path.join(REPO, "scripts/recovery/register_casaray.sh")

H_DASH = "77a4991626d6f8afcd9b78f235c34417d84d9f36c129549a386d8a66c324226c"
H_THEME = "ef7dc9fb2445a6baa2f597fc143927b6da2a60142aef2d0f76dc211f79fdb614"

# homeassistant.config.DEFAULT_CONFIG in Core 2026.10.1 (literal; HA is not imported here).
DEFAULT_CONFIG = """
# Loads default set of integrations. Do not remove.
default_config:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
"""
# The block the script must append, byte for byte (the spec's text).
BLOCK = """# --- CasaRay registration (recovery 2026-10) ---------------------------
# YAML dashboard only. The legacy "Deez Smart Home" dashboard is a UI
# (storage) dashboard and is deliberately NOT listed here.
lovelace:
  dashboards:
    casaray-v2:
      mode: yaml
      title: CasaRay
      icon: mdi:home-heart
      show_in_sidebar: true
      filename: dashboards/casaray_v2.yaml
# --- end CasaRay registration ------------------------------------------
"""
# Canaries. Credential-shaped values are assembled at runtime so this tracked
# file never contains one (scripts/ha_validate.sh scans for them).
SECRET_CANARY = "CANARY_SECRETS_" + "5f1c"
AUTH_CANARY = "CANARY_AUTH_" + "a77e"
OWNER_CANARY = "CANARY_OWNER_" + "08c2"
PKG_CANARY = "CANARY_PKG_" + "e661"
TOKEN = "CANARYTOKEN" + "-sup-" + "3b9d0c71e5"
CRED_GIT_URL = "https://x" + ":" + "CANARY_GIT_" + "0aa" + "@" + "github.com/r"
CANARIES = [SECRET_CANARY, AUTH_CANARY, OWNER_CANARY, PKG_CANARY, "CANARY_GIT_0aa"]

TRACE = ("open,openat,openat2,creat,unlink,unlinkat,rename,renameat,renameat2,mkdir,mkdirat,rmdir,"
         "chmod,fchmodat,truncate,symlink,symlinkat,link,linkat,utimensat,chown,fchownat,lchown,"
         "execve,execveat,clone,clone3,fork,vfork")
MUTATING = {"creat", "unlink", "unlinkat", "rename", "renameat", "renameat2", "mkdir", "mkdirat", "rmdir",
            "chmod", "fchmodat", "truncate", "symlink", "symlinkat", "link", "linkat", "utimensat", "chown",
            "fchownat", "lchown"}
LINE_RE = re.compile(r"^(\d+)\s+(\w+)\((.*)\)\s+=\s+(-?\d+|\?)")
STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
WRITE_FLAGS = re.compile(r"O_WRONLY|O_RDWR|O_CREAT|O_TRUNC|O_APPEND")


# ------------------------------------------------------------------ fake tools
FAKE_HA = r'''#!{py} -I
import json, os, re, signal, subprocess, sys
ST = os.environ["FAKE_STATE"]
def jload(n, d):
    try:
        with open(os.path.join(ST, n)) as f:
            return json.load(f)
    except FileNotFoundError:
        return d
def jsave(n, v):
    with open(os.path.join(ST, n), "w") as f:
        json.dump(v, f)
def main_shell():
    # The script's top shell: walk up from this process through the shells (argv[0] .../sh) that
    # started it; the first non-shell ancestor is strace or the harness. Only our own ancestors.
    p, top = os.getppid(), None
    while p > 1:
        try:
            a = open("/proc/%d/cmdline" % p, "rb").read().split(b"\0")
            q = int(open("/proc/%d/stat" % p).read().rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            break
        if not a[0].endswith(b"/sh"):
            break
        top, p = p, q
    return top
def signal_script(sig):
    p = main_shell()
    if p:
        os.kill(p, sig)
ctl = jload("control.json", {{}})
state = jload("state.json", {{"restarts": 0, "backups": {{"b0206554": "before_auth_repair"}}, "logs": [], "seq": 0}})
argv = [a for a in sys.argv[1:] if a not in ("--no-progress",)]
with open(os.path.join(ST, "ha_calls.jsonl"), "a") as f:
    f.write(json.dumps({{"argv": argv, "token_present": bool(os.environ.get("SUPERVISOR_TOKEN"))}}) + "\n")
def logline(level, logger, text):
    state["seq"] += 1
    state["logs"].append("2026-10-18 19:%02d:%02d.%03d %s (MainThread) [%s] %s #%d" % (
        state["seq"] // 60 % 60, state["seq"] % 60, state["seq"] % 1000, level, logger, text, state["seq"]))
if not state["logs"]:
    for i in range(6):
        logline("WARNING", "homeassistant.loader", "custom integration webrtc has not been tested")
def done(rc, out="", err=""):
    jsave("state.json", state)
    if out:
        sys.stdout.write(out)
    if err:
        sys.stderr.write(err)
    sys.exit(rc)
if argv == ["core", "info"]:
    done(0, "arch: aarch64\naudio_input: null\naudio_output: null\nbackups_exclude_database: false\n"
            "boot: true\nduplicate_log_file: false\nimage: ghcr.io/home-assistant/green-homeassistant\n"
            "ip_address: 172.30.32.1\nmachine: green\nport: 8123\nssl: %s\nupdate_available: false\n"
            "version: 2026.10.1\nversion_latest: 2026.10.1\nwatchdog: true\n" % ("true" if ctl.get("core_ssl") else "false"))
if argv[:2] == ["backups", "new"]:
    name = None
    rest = argv[2:]
    for i, a in enumerate(rest):
        if a == "--name" and i + 1 < len(rest):
            name = rest[i + 1]
        elif a.startswith("--name="):
            name = a.split("=", 1)[1]
    if ctl.get("backup") == "fail" or not name:
        done(1, err="Error: Backup was canceled: not enough free space on the data disk\n")
    slug = ctl.get("slug", "9f3c1a2b")
    state["backups"][slug] = name
    if ctl.get("fill_leave_pages") is not None:   # the backup lands on the same data partition
        fp = ctl["fill_path"]
        stv = os.statvfs(os.path.dirname(fp))
        with open(fp, "wb") as fh:
            fh.write(b"0" * max(stv.f_bavail * stv.f_frsize - int(ctl["fill_leave_pages"]) * stv.f_frsize, 0))
    if ctl.get("backup_side_effect"):           # someone edits configuration.yaml during the backup
        with open(os.path.join(os.environ["FAKE_HA_CONFIG"], "configuration.yaml"), "a") as f:
            f.write(ctl["backup_side_effect"])
    shown = '"%s"' % slug if re.fullmatch(r"[0-9]+|0e[0-9]+", slug) else slug
    if ctl.get("backup") == "noslug":
        done(0, "job_id: 0123456789abcdef0123456789abcdef\n")
    if ctl.get("backup") == "stale":
        del state["backups"][slug]
        done(0, "job_id: 0123456789abcdef0123456789abcdef\nslug: b0206554\n")
    done(0, "job_id: 0123456789abcdef0123456789abcdef\nslug: %s\n" % shown)
if argv[:2] == ["backups", "info"] and len(argv) == 3:
    slug = argv[2]
    if ctl.get("backup_info") == "fail" or slug not in state["backups"]:
        done(1, err="Error: Backup does not exist\n")
    shown = '"%s"' % slug if re.fullmatch(r"[0-9]+|0e[0-9]+", slug) else slug
    done(0, "addons:\n- name: Terminal & SSH\n  size: 0.1\n  slug: core_ssh\n  version: 10.5.0\n"
            "compressed: true\ndate: \"2026-10-18T19:00:00.000000+00:00\"\nextra: {{}}\n"
            "folders:\n- share\n- ssl\n- media\n- addons/local\nhomeassistant: 2026.10.1\n"
            "homeassistant_exclude_database: false\nlocation: null\nlocation_attributes:\n"
            "  .local:\n    protected: false\n    size_bytes: 891564032\nlocations:\n- null\n"
            "name: %s\nprotected: false\nrepositories: []\nsize: 850.3\nsize_bytes: 891564032\n"
            "slug: %s\nsupervisor_version: 2026.10.0\ntype: %s\n" % (state["backups"][slug], shown,
                                                                   ctl.get("backup_type", "full")))
if argv == ["core", "check"]:
    if ctl.get("check") == "real":
        p = subprocess.run([ctl["ha_python"], "-I", "-m", "homeassistant", "--script", "check_config",
                            "-c", os.environ["FAKE_HA_CONFIG"]], capture_output=True, text=True, cwd=ST,
                           env={{"PATH": "/usr/bin:/bin", "HOME": ST, "LANG": "C.UTF-8"}})
        rc, log = p.returncode, p.stdout + p.stderr
    else:
        rc = 1 if os.path.exists(os.path.join(ST, "check_fail_marker")) else 0
        log = "fake check (no HA python): " + ("marker present -> invalid" if rc else "valid") + "\n"
    with open(os.path.join(ST, "check_runs.log"), "a") as f:
        f.write("rc=%d\n%s\n" % (rc, log))
    if ctl.get("check_interrupt"):
        signal_script(signal.SIGTERM)
    if ctl.get("check_kill"):
        signal_script(signal.SIGKILL)
    if rc == 0:
        done(0, "Command completed successfully.\n")
    done(1, err="Error: Testing configuration at /config\n" + log)
if argv == ["core", "restart"]:
    if ctl.get("restart_refused"):        # Supervisor: APIDBMigrationInProgress / GROUP_REJECT; no restart
        done(1, err="Error: Offline database migration in progress, try again after it has completed\n")
    state["restarts"] += 1
    k = state["restarts"]
    state["logs"].append("s6-rc: info: service legacy-services: stopping")
    state["logs"].append("s6-rc: info: service s6rc-oneshot-runner: starting")
    state["logs"].append("s6-rc: info: service legacy-services successfully started")
    logline("WARNING", "homeassistant.loader", "boot %d: custom integration webrtc has not been tested" % k)
    if k in ctl.get("recovery_after_restart", []):
        logline("ERROR", "homeassistant.bootstrap", "Detected that frontend did not load. Activating recovery mode")
    logline("WARNING", "homeassistant.components.http", "boot %d: http server started" % k)
    if ctl.get("restart_interrupt"):      # Ctrl-C while the restart is in progress
        jsave("state.json", state)
        signal_script(signal.SIGINT)
    done(int(ctl.get("restart_rc", 0)), "Command completed successfully.\n" if not ctl.get("restart_rc") else "",
         "Error: timeout\n" if ctl.get("restart_rc") else "")
if argv[:2] == ["core", "logs"]:
    n = 100
    rest = argv[2:]
    for i, a in enumerate(rest):
        if a in ("-n", "--lines") and i + 1 < len(rest):
            n = int(rest[i + 1])
        elif a.startswith("--lines="):
            n = int(a.split("=", 1)[1])
    if ctl.get("logs_error"):             # the CLI prints an HTTP error body and still exits 0
        done(0, "No systemd-journal-gatewayd Unix socket available")
    if ctl.get("marker_interrupt") and n == 2:
        signal_script(signal.SIGINT)      # Ctrl-C while the marker is read, before the restart
    if n == 1:                            # real CLI: 'Range: entries=:0:' = from the journal's head
        done(0, "".join(l + "\n" for l in state["logs"]))
    done(0, "".join(l + "\n" for l in state["logs"][-n:]))
done(1, err="Error: unknown command \"%s\" for \"ha\"\n" % " ".join(argv))
'''

FAKE_CURL = r'''#!{py} -I
import json, os, sys
from urllib.parse import urlsplit
ST = os.environ["FAKE_STATE"]
def jload(n, d):
    try:
        with open(os.path.join(ST, n)) as f:
            return json.load(f)
    except FileNotFoundError:
        return d
ctl = jload("control.json", {{}})
state = jload("state.json", {{"restarts": 0}})
args = sys.argv[1:]
url = next((a for a in args if a.startswith(("http://", "https://"))), "")
CRED = ("-K", "--config", "-H", "--header", "-u", "--user", "--oauth2-bearer", "-b", "--cookie", "-E", "--cert")
via_stdin, header_ok = False, False
if "-K" in args and args[args.index("-K") + 1:args.index("-K") + 2] == ["-"]:
    via_stdin = True
    cfgtext = sys.stdin.read()
    tok = os.environ.get("SUPERVISOR_TOKEN", "")
    header_ok = bool(tok) and ('header = "Authorization: Bearer %s"' % tok) in cfgtext
tok = os.environ.get("SUPERVISOR_TOKEN") or "\x00"
rec = {{"url": url, "auth_via_stdin": via_stdin, "header_ok": header_ok,
       "token_in_argv": any(tok in a for a in args), "insecure": "-k" in args,
       "sends_credential": via_stdin or any(a in CRED or a.startswith(tuple(c + "=" for c in CRED if c.startswith("--")))
                                            for a in args),
       "first_q": bool(args) and args[0] == "-q", "failed_login": False}}
mode = ctl.get("curl", "up")
k = state.get("restarts", 0)
up = (mode == "up" or (mode == "down_after_first_restart" and k != 1)
      or (mode == "down_after_restart" and k == 0))
u = urlsplit(url)
rc = 0
if "://supervisor/core/api" in url:
    code = "401" if up else "502"         # this add-on has no homeassistant_api: always refused, and logged
elif u.hostname == "homeassistant":
    if not up:
        code = "000"
    elif ctl.get("banned"):
        code = "403"                      # ip_bans.yaml: Core answers 403 to everything from this IP
    elif (u.scheme == "https") != bool(ctl.get("core_ssl")):
        code = "000"
    elif u.scheme == "https" and "-k" not in args:
        code, rc = "000", 60              # the certificate is for the public name, not 'homeassistant'
    elif u.path == "/manifest.json":
        code = "200"                      # requires_auth = False
    elif u.path.startswith("/api"):
        code = "401"                      # HTTPUnauthorized -> ban.process_wrong_login: WARNING + notification
        rec["failed_login"] = True
    else:
        code = "404"
else:
    code = "000"
rec["code"] = code
with open(os.path.join(ST, "curl_calls.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\n")
if "-w" in args:
    sys.stdout.write(code)
sys.exit(rc or (7 if code == "000" else 0))
'''


# ------------------------------------------------------------------ fixture helpers
def w(path, text="", mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    if mode is not None:
        os.chmod(path, mode)


def repo(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8", newline="") as f:
        return f.read()


def rd(path, binary=False):
    with open(path, "rb" if binary else "r", **({} if binary else {"encoding": "utf-8", "newline": ""})) as f:
        return f.read()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def sha_file(path):
    return hashlib.sha256(rd(path, True)).hexdigest()


def storage_json(key, items):
    return json.dumps({"version": 1, "minor_version": 1, "key": key, "data": {"items": items}}, indent=2)


def base_fixture(cfg):
    w(f"{cfg}/configuration.yaml", DEFAULT_CONFIG)
    w(f"{cfg}/automations.yaml", "[]\n")
    w(f"{cfg}/scripts.yaml", "")
    w(f"{cfg}/scenes.yaml", "")
    w(f"{cfg}/secrets.yaml", f"wifi_password: {SECRET_CANARY}\nlatitude: {SECRET_CANARY}\n")
    w(f"{cfg}/.storage/auth", json.dumps({"data": {"refresh_tokens": [{"token": AUTH_CANARY}]}}))
    w(f"{cfg}/.storage/auth_provider.homeassistant", json.dumps({"data": {"users": [{"password": AUTH_CANARY}]}}))
    w(f"{cfg}/.storage/core.config", json.dumps({"data": {"time_zone": "Australia/Sydney"}}))
    w(f"{cfg}/.storage/lovelace_dashboards", storage_json("lovelace_dashboards", [
        {"id": "map", "icon": "mdi:map", "title": "Map", "url_path": "map", "mode": "storage",
         "require_admin": False, "show_in_sidebar": True}]))
    w(f"{cfg}/.storage/lovelace.deez_smart_home", '{"data": {"config": {"views": []}}}')
    w(f"{cfg}/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml"))
    w(f"{cfg}/dashboards/deez_smart_home.yaml", repo("dashboards/deez_smart_home.yaml"))
    w(f"{cfg}/packages/casaray_automation.yaml", repo("packages/casaray_automation.yaml"))
    w(f"{cfg}/packages/private.yaml", f"input_boolean:\n  chinese_dashboard:\n    name: {PKG_CANARY}\n")
    w(f"{cfg}/deez_repo/themes/deez_your_name.yaml", repo("themes/deez_your_name.yaml"))
    w(f"{cfg}/deez_repo/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml"))
    w(f"{cfg}/deez_repo/.git/config", "[remote]\n url = " + CRED_GIT_URL + "\n")
    w(f"{cfg}/_recovery/casaray/configuration.yaml.pre", DEFAULT_CONFIG)
    w(f"{cfg}/_recovery/casaray/backup_slug", "ba94d3a0\n")
    w(f"{cfg}/_recovery/owner/auth_provider.homeassistant", OWNER_CANARY)
    os.chmod(f"{cfg}/_recovery", 0o700)


def snapshot(root):
    snap = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for n in dirnames + filenames:
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, root)
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode):
                snap[rel] = ("l", os.readlink(p), 0)
            elif stat.S_ISDIR(st.st_mode):
                snap[rel] = ("d", "", stat.S_IMODE(st.st_mode))
            else:
                snap[rel] = ("f", sha_file(p), stat.S_IMODE(st.st_mode))
    return snap


def diff(a, b):
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return added, removed, changed


RUN_DIR_RE = re.compile(r"^_recovery/casaray-register-\d{8}-\d{6}(/|$)")


def outside_runs(paths):
    return [p for p in paths if not RUN_DIR_RE.match(p)]


def run_dirs(cfg):
    base = os.path.join(cfg, "_recovery")
    return sorted(os.path.join(base, d) for d in os.listdir(base) if re.fullmatch(r"casaray-register-\d{8}-\d{6}", d))


def manifest(run):
    m = {}
    for line in rd(os.path.join(run, "manifest")).splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            m[k] = v
    return m


def state_of(run):
    p = os.path.join(run, "state")
    return rd(p).strip() if os.path.exists(p) else ""


# ------------------------------------------------------------------ trace analysis
def joined_trace(path):
    lines, pending = [], {}
    with open(path, errors="replace") as f:
        for l in f.read().splitlines():
            pid = l.split(" ", 1)[0]
            if l.endswith("<unfinished ...>"):
                pending[pid] = l[: -len("<unfinished ...>")]
                continue
            m = re.match(r"^(\d+)\s+<\.\.\. \w+ resumed>(.*)$", l)
            if m and m.group(1) in pending:
                l = pending.pop(m.group(1)) + m.group(2)
            lines.append(l)
    return lines


def unescape(s):
    return s.encode("latin-1", "backslashreplace").decode("unicode_escape")


def parse_events(lines):
    ev = []
    for i, l in enumerate(lines):
        m = LINE_RE.match(l)
        if not m:
            continue
        pid, call, args, res = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        ev.append({"i": i, "pid": pid, "call": call, "args": args,
                   "res": int(res) if res.lstrip("-").isdigit() else None,
                   "strs": [unescape(s) for s in STR_RE.findall(args)], "line": l})
    return ev


def tool_filter(events, tool_paths):
    """Split events into (script, tool): tool = a fake tool after its exec, or anything it forked."""
    parent, fork_at, exec_at = {}, {}, {}
    for e in events:
        if e["call"] in ("clone", "clone3", "fork", "vfork") and e["res"] and e["res"] > 0:
            parent[e["res"]] = e["pid"]
            fork_at[e["res"]] = e["i"]
        if e["call"] in ("execve", "execveat") and e["res"] == 0 and e["strs"] and e["strs"][0] in tool_paths:
            exec_at.setdefault(e["pid"], e["i"])

    memo = {}

    def descendant(pid):
        if pid in memo:
            return memo[pid]
        q = parent.get(pid)
        r = False
        if q is not None:
            r = (q in exec_at and exec_at[q] < fork_at[pid]) or descendant(q)
        memo[pid] = r
        return r

    script, tool = [], []
    for e in events:
        is_tool = (e["pid"] in exec_at and e["i"] >= exec_at[e["pid"]]) or descendant(e["pid"])
        (tool if is_tool else script).append(e)
    return script, tool


# ------------------------------------------------------------------ the world
class World:
    def __init__(self, base, name, bindir, ha_python, strace_cmd):
        self.name = name
        self.strace_cmd = strace_cmd
        self.dir = os.path.join(base, name)
        self.cfg = os.path.join(self.dir, "config")
        self.tmp = os.path.join(self.dir, "tmp")
        self.st = os.path.join(self.dir, "fake")
        self.tty = os.path.join(self.dir, "tty")
        self.bindir = bindir
        for d in (self.cfg, self.tmp, self.st):
            os.makedirs(d)
        base_fixture(self.cfg)
        self.control = {"check": "real" if ha_python else "marker", "ha_python": ha_python or ""}
        self.env_extra = {}
        self.runs = []
        self.extra_strace = []

    def set_control(self, **kw):
        self.control.update(kw)
        w(os.path.join(self.st, "control.json"), json.dumps(self.control))

    def calls(self, kind):
        p = os.path.join(self.st, kind)
        if not os.path.exists(p):
            return []
        return [json.loads(l) for l in rd(p).splitlines() if l.strip()]

    def run(self, mode, tty_text, script=None, trace=True):
        """trace=False: no strace (fast sweeps); the syscall assertions are then skipped."""
        script = script or SCRIPT
        w(os.path.join(self.st, "control.json"), json.dumps(self.control))
        w(self.tty, tty_text if tty_text is not None else "")
        before = snapshot(self.cfg)
        ha_before, curl_before = len(self.calls("ha_calls.jsonl")), len(self.calls("curl_calls.jsonl"))
        trace_on = trace
        trace = os.path.join(self.dir, f"run{len(self.runs)}.strace")
        env = {"PATH": self.bindir, "RC_HOST_CONFIG": self.cfg, "RC_TTY": self.tty, "RC_POLL": "0",
               "RC_WAIT_TRIES": "3", "TMPDIR": self.tmp, "SUPERVISOR_TOKEN": TOKEN,
               "FAKE_STATE": self.st, "FAKE_HA_CONFIG": self.cfg}
        env.update(self.env_extra)
        cmd = self.strace_cmd + ["-f", "-qq", "-s", "4096", "-e", f"trace={TRACE}"] + self.extra_strace + [
            "-o", trace, os.path.join(self.bindir, "sh"), script]
        if not trace_on:
            cmd, trace = [os.path.join(self.bindir, "sh"), script], None
        if mode is not None:
            cmd.append(mode)
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
        after = snapshot(self.cfg)
        r = {"mode": mode or "check", "rc": p.returncode, "out": p.stdout, "err": p.stderr,
             "before": before, "after": after, "trace": trace, "script": script,
             "ha": self.calls("ha_calls.jsonl")[ha_before:], "curl": self.calls("curl_calls.jsonl")[curl_before:]}
        r["generic"] = generic_checks(self, r)
        self.runs.append(r)
        return r


def generic_checks(world, r):
    """Assertions that hold for every run of every scenario."""
    fails = []
    cfg = world.cfg
    out = r["out"] + r["err"]
    for c in CANARIES + [TOKEN]:
        if c in out:
            fails.append(f"canary in output: {c[:14]}...")
    for d in run_dirs(cfg):
        for n in os.listdir(d):
            t = rd(os.path.join(d, n), True)
            for c in CANARIES + [TOKEN]:
                if c.encode() in t:
                    fails.append(f"canary in run record {n}: {c[:14]}...")
    # The 30/09 evidence folder: byte-identical, every file.
    ev_b = {k: v for k, v in r["before"].items() if k.startswith("_recovery/casaray/") or k == "_recovery/casaray"}
    ev_a = {k: v for k, v in r["after"].items() if k.startswith("_recovery/casaray/") or k == "_recovery/casaray"}
    if ev_b != ev_a or not ev_b:
        fails.append("_recovery/casaray/ changed")
    for c in r["ha"]:
        if not c["token_present"]:
            fails.append("ha called without SUPERVISOR_TOKEN in its environment")
    for c in r["curl"]:
        if c["token_in_argv"]:
            fails.append("Supervisor token on curl's command line")
        if c.get("sends_credential") or c["auth_via_stdin"] or c["header_ok"]:
            fails.append(f"curl was given a credential: {c['url']}")
        if "://supervisor/" in c["url"]:
            fails.append("Supervisor proxy probed (this add-on has no Core API access; Supervisor logs every try)")
        if c.get("failed_login"):
            fails.append(f"probe that Core logs as a failed login ('Login attempt failed'): {c['url']}")
        if not c.get("first_q"):
            fails.append("curl run without -q first (a ~/.curlrc could add options)")
    for c in r["ha"]:
        a = c["argv"]
        if a[:2] == ["core", "logs"] and "-n" in a and a[a.index("-n") + 1:a.index("-n") + 2] == ["1"]:
            fails.append("'ha core logs -n 1' (the CLI sends entries=:0:, which streams the whole journal from its head)")
    if r["trace"] is None:
        return fails

    lines = joined_trace(r["trace"])
    events = parse_events(lines)
    tool_paths = {os.path.join(world.bindir, "ha"), os.path.join(world.bindir, "curl")}
    script_ev, _ = tool_filter(events, tool_paths)
    for l in lines:
        if TOKEN in l:
            fails.append("Supervisor token appears in the syscall trace (command line or path)")
            break
    mode = r["mode"]
    pre_runs = {k for k in r["before"] if RUN_DIR_RE.match(k)}
    lock = os.path.join(world.tmp, "casaray_register.lock")

    def under(p, base):
        return p == base or p.startswith(base + "/")

    def write_ok(p):
        if not p.startswith("/"):
            return False
        p = os.path.normpath(p)
        if p == "/dev/null":
            return True
        if mode in ("check", "verify"):
            return False
        if under(p, lock):
            return True
        if p == f"{cfg}/configuration.yaml" or under(p, f"{cfg}/themes"):
            return True
        rel = os.path.relpath(p, cfg)
        if RUN_DIR_RE.match(rel):
            top = rel.split("/")[:2]
            top = "/".join(top)
            if mode == "apply":
                return top not in pre_runs           # only the folder this run created
            if mode == "rollback":
                return top in pre_runs               # only the run being rolled back
        return False

    read_ok_exact = {SCRIPT, r["script"], world.tty, "/dev/null", "/etc/localtime", f"{cfg}/configuration.yaml",
                     f"{cfg}/.storage/lovelace_dashboards", f"{cfg}/dashboards/casaray_v2.yaml",
                     f"{cfg}/themes/deez_your_name.yaml", f"{cfg}/deez_repo/themes/deez_your_name.yaml"}
    dir_ok = {f"{cfg}/_recovery"}
    denied = re.compile(r"secrets\.yaml|/\.storage/(?!lovelace_dashboards$)|/_recovery/casaray(/|$)|/_recovery/owner|"
                        r"/packages(/|$)|/deez_repo/(?!themes/deez_your_name\.yaml$)|deez_smart_home|"
                        r"automations\.yaml|scripts\.yaml|scenes\.yaml")
    n_writes = 0
    execs = set()
    for e in script_ev:
        call = e["call"]
        if call in ("open", "openat", "openat2", "creat"):
            if not e["strs"]:
                continue
            path = e["strs"][0]
            if call != "open" and not e["args"].startswith(("AT_FDCWD", '"')) and not path.startswith("/"):
                fails.append(f"dirfd-relative open: {e['line'][:160]}")
                continue
            flags = e["args"]
            writing = call == "creat" or bool(WRITE_FLAGS.search(flags))
            if denied.search(path):
                if not (path == f"{cfg}/.storage/lovelace_dashboards" and not writing):
                    fails.append(f"denied path opened: {path} ({'write' if writing else 'read'})")
            if writing:
                if path != "/dev/null":
                    n_writes += 1
                if not write_ok(path):
                    fails.append(f"write-mode open outside the allowlist ({mode}): {path}")
            elif e["res"] is not None and e["res"] >= 0:
                if "O_DIRECTORY" in flags:
                    if os.path.normpath(path) not in dir_ok:
                        fails.append(f"directory listed: {path}")
                elif not (path in read_ok_exact or path.startswith("/proc/") or under(path, lock)
                          or RUN_DIR_RE.match(os.path.relpath(path, cfg))):
                    fails.append(f"file read outside the allowlist: {path}")
        elif call in MUTATING:
            paths = e["strs"] or ["<fd>"]
            if call == "utimensat" and not e["strs"]:
                continue
            n_writes += 1
            for path in paths:
                if denied.search(path) or not write_ok(path):
                    fails.append(f"{call} outside the allowlist ({mode}): {path}")
        elif call in ("execve", "execveat") and e["res"] == 0 and e["strs"]:
            execs.add(e["strs"][0])
            if not (e["strs"][0].startswith(world.bindir + "/") or e["strs"][0] == "/proc/self/exe"):
                fails.append(f"exec outside the test PATH: {e['strs'][0]}")
    r["n_writes"] = n_writes
    r["execs"] = execs
    if mode in ("check", "verify") and n_writes:
        fails.append(f"{mode} made {n_writes} write-class syscall(s)")
    return fails


# ------------------------------------------------------------------ scenario helpers
def calls_of(r, *prefix):
    return [c for c in r["ha"] if c["argv"][:len(prefix)] == list(prefix)]


def expect(cond, msg, fails):
    if not cond:
        fails.append(msg)


def unchanged(r, fails, label=""):
    a, rm, ch = diff(r["before"], r["after"])
    if a or rm or ch:
        fails.append(f"{label}fixture changed: added={a[:4]} removed={rm[:4]} changed={ch[:4]}")


def no_mutating_ha(r, fails):
    bad = [c["argv"] for c in r["ha"] if c["argv"][:2] in (["backups", "new"], ["core", "restart"], ["core", "check"])]
    expect(not bad, f"mutating ha calls: {bad}", fails)


def last_line(r, prefix):
    return any(l.startswith(prefix) for l in r["out"].splitlines())


def real_check(world, ha_python):
    if not ha_python:
        return True, "skipped (no HA python)"
    p = subprocess.run([ha_python, "-I", "-m", "homeassistant", "--script", "check_config", "-c", world.cfg],
                       capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "HOME": world.st})
    return p.returncode == 0, f"rc={p.returncode}"


# ------------------------------------------------------------------ scenarios
def sc_check_ready(wd, S):
    r = S.run("check", None)
    f = []
    expect(r["rc"] == 0, f"exit {r['rc']} != 0", f)
    expect(last_line(r, "READY"), "no READY line", f)
    expect("BLOCKED" not in r["out"], "BLOCKED present", f)
    expect("will be installed" in r["out"], "theme install not announced", f)
    unchanged(r, f)
    no_mutating_ha(r, f)
    expect(r["n_writes"] == 0, f"{r['n_writes']} writes (check must make none)", f)
    expect(not os.path.exists(os.path.join(S.tmp, "casaray_register.lock")), "check created a lock", f)
    expect(r["curl"] and all(c["url"] == "http://homeassistant:8123/manifest.json" and not c["insecure"]
                             for c in r["curl"]), f"liveness probe is not GET /manifest.json: {r['curl']}", f)
    return f, "READY, 0 writes, probe /manifest.json with no credential"


def blocked(setup, needle):
    def sc(wd, S):
        setup(S)
        r = S.run("check", None)
        f = []
        expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
        bl = [l for l in r["out"].splitlines() if l.startswith("BLOCKED:")]
        expect(bl and needle in bl[0], f"BLOCKED line lacks {needle!r}: {bl}", f)
        expect(not last_line(r, "READY"), "READY printed", f)
        unchanged(r, f)
        no_mutating_ha(r, f)
        r2 = S.run("apply", "APPLY\n")
        expect(r2["rc"] == 1, f"apply exit {r2['rc']} != 1", f)
        expect(not calls_of(r2, "backups", "new"), "apply made a backup although blocked", f)
        unchanged(r2, f, "apply: ")
        no_mutating_ha(r2, f)
        return f, f"BLOCKED ({needle}); apply refused"
    return sc


def setup_lovelace(S):
    w(f"{S.cfg}/configuration.yaml", DEFAULT_CONFIG + "\nlovelace:\n  resource_mode: yaml\n")


def setup_storage(S):
    w(f"{S.cfg}/.storage/lovelace_dashboards", storage_json("lovelace_dashboards", [
        {"id": "map", "title": "Map", "url_path": "map", "mode": "storage"},
        {"id": "casaray_v2", "title": "CasaRay", "url_path": "casaray-v2", "mode": "storage"}]))


def setup_dash_missing(S):
    os.remove(f"{S.cfg}/dashboards/casaray_v2.yaml")


def setup_theme_unverifiable(S):
    w(f"{S.cfg}/deez_repo/themes/deez_your_name.yaml", repo("themes/deez_your_name.yaml") + "# local edit\n")


def setup_registered(S):
    w(f"{S.cfg}/configuration.yaml", DEFAULT_CONFIG + BLOCK)


def setup_cfg_symlink(S):
    w(f"{S.cfg}/configuration.real.yaml", DEFAULT_CONFIG)
    os.remove(f"{S.cfg}/configuration.yaml")
    os.symlink("configuration.real.yaml", f"{S.cfg}/configuration.yaml")


def setup_low_space(S):
    S.env_extra["RC_MIN_FREE_KB"] = str(10 ** 15)


def setup_probe_down(S):
    S.set_control(curl="down")


def sc_warn_dash(wd, S):
    w(f"{S.cfg}/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml") + "# drift\n")
    r = S.run("check", None)
    f = []
    expect(r["rc"] == 0, f"exit {r['rc']} != 0", f)
    expect(last_line(r, "READY"), "no READY line", f)
    expect(any(l.startswith("WARN: dashboards/casaray_v2.yaml differs from git") for l in r["out"].splitlines()),
           "no dashboard WARN line", f)
    unchanged(r, f)
    return f, "READY with WARN"


def assert_applied(wd, S, r, f, original, theme_installed=True, slug="9f3c1a2b"):
    expect(r["rc"] == 0, f"apply exit {r['rc']} != 0", f)
    expect("DONE. CasaRay is registered" in r["out"], "no DONE line", f)
    expected = original + ("" if original.endswith("\n") or not original else "\n") + BLOCK
    got = rd(f"{S.cfg}/configuration.yaml")
    expect(got == expected, "configuration.yaml is not original + block byte-exact", f)
    ok, why = real_check(S, wd.ha_python)
    expect(ok, f"real check_config fails on the result ({why})", f)
    runs = run_dirs(S.cfg)
    expect(len(runs) == 1, f"{len(runs)} run folders", f)
    if not runs:
        return None
    run = runs[0]
    m = manifest(run)
    expect(stat.S_IMODE(os.stat(run).st_mode) == 0o700, "run folder not mode 700", f)
    expect(rd(f"{run}/configuration.yaml.pre") == original, "configuration.yaml.pre not byte-exact", f)
    expect(m.get("cfg_sha256_before") == sha_text(original), "manifest sha before", f)
    expect(m.get("cfg_sha256_after") == sha_text(expected), "manifest sha after", f)
    expect(m.get("backup_slug") == slug, f"manifest backup_slug {m.get('backup_slug')} != {slug}", f)
    expect(re.fullmatch(r"casaray-pre-register-\d{8}-\d{4}", m.get("backup_name", "")) is not None,
           f"backup name {m.get('backup_name')}", f)
    expect(state_of(run) == "applied", f"state {state_of(run)} != applied", f)
    expect(m.get("restart_confirmed") == "yes", "manifest lacks restart_confirmed=yes", f)
    expect(set(os.listdir(run)) == {"configuration.yaml.pre", "backup", "manifest", "state", "run.log", "check.log",
                                    "register_casaray.sh"}, f"run folder holds {sorted(os.listdir(run))}", f)
    copy = os.path.join(run, "register_casaray.sh")
    expect(os.path.exists(copy) and rd(copy, True) == rd(SCRIPT, True), "run folder lacks a byte-exact copy of the script", f)
    expect(f"undo:   sh {copy} rollback" in r["out"], "the undo line does not point at the run folder's copy", f)
    expect(len(calls_of(r, "core", "restart")) == 1, f"{len(calls_of(r, 'core', 'restart'))} restarts != 1", f)
    expect(len(calls_of(r, "backups", "new")) == 1, "backup not made exactly once", f)
    seq = [" ".join(c["argv"][:2]) for c in r["ha"] if c["argv"][:2] != ["core", "info"]]
    want = ["backups new", "backups info", "core check", "core logs", "core restart", "core logs"]
    expect(seq == want, f"ha call order {seq}", f)
    theme = f"{S.cfg}/themes/deez_your_name.yaml"
    if theme_installed:
        expect(os.path.isfile(theme) and sha_file(theme) == H_THEME, "theme not installed with the right hash", f)
        expect(stat.S_IMODE(os.stat(theme).st_mode) == 0o644, "theme not mode 644", f)
        expect(stat.S_IMODE(os.stat(f"{S.cfg}/themes").st_mode) == 0o755, "themes/ not mode 755", f)
        expect(m.get("theme_created") == "yes" and m.get("themes_dir_created") == "yes", "manifest theme flags", f)
    a, rm, ch = diff(r["before"], r["after"])
    want_added = ["themes", "themes/deez_your_name.yaml"] if theme_installed else []
    expect(outside_runs(a) == want_added, f"added outside run folder: {outside_runs(a)}", f)
    expect(rm == [], f"removed: {rm}", f)
    expect(outside_runs(ch) == ["configuration.yaml"], f"changed: {outside_runs(ch)}", f)
    return run


def sc_apply_success(wd, S):
    f = []
    r = S.run("apply", "APPLY\n")
    run = assert_applied(wd, S, r, f, DEFAULT_CONFIG)
    r2 = S.run("check", None)
    expect(r2["rc"] == 1 and "still marked 'applied'" in r2["out"], "check after apply is not BLOCKED by the run", f)
    unchanged(r2, f, "check after apply: ")
    return f, f"applied; run {os.path.basename(run) if run else '?'}; check afterwards BLOCKED"


def sc_apply_noeol(wd, S):
    f = []
    original = DEFAULT_CONFIG.rstrip("\n")
    w(f"{S.cfg}/configuration.yaml", original)
    r = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r, f, original)
    return f, "file without a final newline: one newline added before the block"


def sc_wrong_confirmation(wd, S):
    r = S.run("apply", "apply\n")
    f = []
    expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
    expect("not confirmed; nothing changed" in r["out"], "no 'not confirmed' line", f)
    unchanged(r, f)
    no_mutating_ha(r, f)
    expect(not os.path.exists(os.path.join(S.tmp, "casaray_register.lock")), "lock left behind", f)
    return f, "typed 'apply': refused, no backup"


def sc_backup_fails(kind):
    def sc(wd, S):
        S.set_control(**{"fail": {"backup": "fail"}, "info": {"backup_info": "fail"}, "noslug": {"backup": "noslug"},
                         "stale": {"backup": "stale"}, "partial": {"backup_type": "partial"}}[kind])
        r = S.run("apply", "APPLY\n")
        f = []
        expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
        expect("nothing changed" in r["out"], "no 'nothing changed'", f)
        unchanged(r, f)
        expect(len(calls_of(r, "backups", "new")) == 1, "backup not attempted once", f)
        expect(not calls_of(r, "core", "check") and not calls_of(r, "core", "restart"), "check/restart called", f)
        return f, f"backup {kind}: stopped, fixture byte-identical"
    return sc


def assert_rolled_back(S, r, f, original, restarts, rc=3):
    expect(r["rc"] == rc, f"exit {r['rc']} != {rc}", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == original, "configuration.yaml not byte-identical to before", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "themes/ left behind", f)
    n = len(calls_of(r, "core", "restart"))
    expect(n == restarts, f"{n} restarts != {restarts}", f)
    runs = run_dirs(S.cfg)
    expect(len(runs) == 1 and state_of(runs[0]) == "rolled-back", f"run state {[state_of(x) for x in runs]}", f)
    a, rm, ch = diff(r["before"], r["after"])
    expect(outside_runs(a) == [] and rm == [] and outside_runs(ch) == [],
           f"outside run folder: added={outside_runs(a)} removed={rm} changed={outside_runs(ch)}", f)
    if runs:
        left = {"configuration.yaml.new", "configuration.yaml.restore", "theme.new", "manifest.new",
                "state.new"} & set(os.listdir(runs[0]))
        expect(not left, f"temp files left in the run folder: {left}", f)


def sc_check_fails(wd, S):
    original = DEFAULT_CONFIG + "homeassistant:\n  unit_system: bogus\n"
    w(f"{S.cfg}/configuration.yaml", original)
    w(os.path.join(S.st, "check_fail_marker"), "x")   # used only by the fallback fake check
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, original, restarts=0)
    expect(len(calls_of(r, "core", "check")) == 1, "core check not called once", f)
    expect("configuration check FAILED" in r["out"], "failure not reported", f)
    runs = run_dirs(S.cfg)
    if runs and S.control["check"] == "real":
        expect("unit_system" in rd(f"{runs[0]}/check.log"), "check.log lacks the real error", f)
    expect("theme" in r["out"] and "removed (this run installed it)" in r["out"], "theme removal not reported", f)
    return f, "real check failed: restored, theme removed, no restart"


def sc_never_up(wd, S):
    S.set_control(curl="down_after_first_restart")
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=2)
    expect("did not answer" in r["out"], "no 'did not answer'", f)
    return f, "Core never up: restored, restarted twice, rolled-back"


def sc_recovery_mode(wd, S):
    S.set_control(recovery_after_restart=[1])
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=2)
    expect("RECOVERY MODE" in r["out"], "recovery mode not reported", f)
    return f, "recovery mode after restart: restored, restarted twice"


def sc_interrupted(wd, S):
    S.set_control(check_interrupt=True)
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=0)
    expect("terminated" in r["out"], "termination not reported", f)
    return f, "SIGTERM during check: EXIT trap restored everything, no restart"


def sc_theme_differs(wd, S):
    own = "# the owner's own theme\nOwnTheme:\n  primary-color: \"#ff0000\"\n"
    w(f"{S.cfg}/themes/deez_your_name.yaml", own)
    S.set_control(slug="12345678")
    f = []
    r0 = S.run("check", None)
    expect(r0["rc"] == 0 and any(l.startswith("WARN: themes/deez_your_name.yaml differs") for l in r0["out"].splitlines()),
           "check: no theme WARN or not READY", f)
    r = S.run("apply", "APPLY\n")
    run = assert_applied(wd, S, r, f, DEFAULT_CONFIG, theme_installed=False, slug="12345678")
    expect(rd(f"{S.cfg}/themes/deez_your_name.yaml") == own, "existing theme was modified", f)
    if run:
        expect(manifest(run).get("theme_created") == "no", "manifest claims the theme was created", f)
    return f, "different theme left byte-identical; quoted numeric slug parsed"


def sc_rollback_after_success(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    mode_before = stat.S_IMODE(os.stat(f"{S.cfg}/configuration.yaml").st_mode)
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 0, f"rollback exit {r2['rc']} != 0", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not byte-identical to pre-apply", f)
    expect(stat.S_IMODE(os.stat(f"{S.cfg}/configuration.yaml").st_mode) == mode_before, "mode changed", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "theme/themes not removed", f)
    expect(len(calls_of(r2, "core", "restart")) == 1, "rollback did not restart once", f)
    expect(len(calls_of(r2, "core", "check")) == 1, "rollback did not run core check", f)
    runs = run_dirs(S.cfg)
    expect(runs and state_of(runs[0]) == "rolled-back", "run not marked rolled-back", f)
    a, rm, ch = diff(r1["before"], r2["after"])
    expect(outside_runs(a) == [] and rm == [] and outside_runs(ch) == [],
           f"vs pre-apply: added={outside_runs(a)} removed={rm} changed={outside_runs(ch)}", f)
    r3 = S.run("check", None)
    expect(r3["rc"] == 0 and last_line(r3, "READY"), "check after rollback is not READY", f)
    return f, "rollback: byte-identical config, theme and themes/ removed, 1 restart; READY again"


def sc_rollback_edited_theme(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    theme = f"{S.cfg}/themes/deez_your_name.yaml"
    edited = rd(theme) + "# owner tweak after the apply\n"
    w(theme, edited)
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 0, f"rollback exit {r2['rc']} != 0", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not restored", f)
    expect(os.path.exists(theme) and rd(theme) == edited, "the edited theme was removed or changed", f)
    expect("differs from what this run installed: left alone" in r2["out"], "theme kept without a WARN", f)
    expect(len(calls_of(r2, "core", "restart")) == 1, "rollback did not restart once", f)
    return f, "theme edited after apply: rollback restores config, keeps the theme"


def sc_rollback_nothing(wd, S):
    r = S.run("rollback", "ROLLBACK\n")
    f = []
    expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
    expect("nothing to roll back" in r["out"], "no 'nothing to roll back'", f)
    unchanged(r, f)
    expect(not r["ha"], f"ha called: {[c['argv'] for c in r['ha']]}", f)
    return f, "refused, no ha call, fixture byte-identical"


def sc_rollback_changed(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    edited = rd(f"{S.cfg}/configuration.yaml") + "# owner edit after the apply\n"
    w(f"{S.cfg}/configuration.yaml", edited)
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 1, f"rollback exit {r2['rc']} != 1", f)
    expect("has changed since this run wrote it" in r2["out"], "reason not given", f)
    unchanged(r2, f)
    no_mutating_ha(r2, f)
    return f, "config edited after apply: rollback refused, nothing changed"


def sc_lock_held(wd, S):
    lock = os.path.join(S.tmp, "casaray_register.lock")
    w(os.path.join(lock, "pid"), f"{os.getpid()}\n")
    r = S.run("apply", "APPLY\n")
    f = []
    expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
    expect("another register_casaray.sh run" in r["out"], "lock not reported", f)
    expect(os.path.exists(os.path.join(lock, "pid")), "a lock it did not hold was removed", f)
    unchanged(r, f)
    expect(not r["ha"], "ha called while locked out", f)
    return f, "live lock: refused, lock kept"


def sc_verify(wd, S):
    f = []
    r0 = S.run("verify", None)
    expect(r0["rc"] == 1 and "ABSENT" in r0["out"], "verify before apply does not report ABSENT", f)
    unchanged(r0, f, "verify before: ")
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    r2 = S.run("verify", None)
    expect(r2["rc"] == 0 and last_line(r2, "VERIFY: OK"), f"verify after apply: exit {r2['rc']}", f)
    expect("present, exact" in r2["out"], "registration not reported exact", f)
    expect(": applied (backup 9f3c1a2b)" in r2["out"], "latest run not reported", f)
    unchanged(r2, f, "verify after: ")
    no_mutating_ha(r2, f)
    return f, "verify: 0 writes before and after apply"


def sc_restart_rc(wd, S):
    S.set_control(restart_rc=1)
    f = []
    r = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r, f, DEFAULT_CONFIG)
    expect("WARN 'ha core restart' returned 1" in r["out"], "non-zero restart rc not reported", f)
    return f, "restart rc 1 but Core answers: applied, with a WARN"


def sc_rollback_wrong(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    r2 = S.run("rollback", "rollback\n")
    expect(r2["rc"] == 1 and "not confirmed; nothing changed" in r2["out"], f"rollback exit {r2['rc']}", f)
    unchanged(r2, f)
    no_mutating_ha(r2, f)
    return f, "typed 'rollback': refused, nothing changed"


def sc_killed(wd, S):
    """SIGKILL mid-check: no trap can run. Then check, the owner clears the stale lock, rollback."""
    S.set_control(check_kill=True)
    f = []
    r1 = S.run("apply", "APPLY\n")
    expect(r1["rc"] != 0, "killed apply exited 0", f)
    runs = run_dirs(S.cfg)
    expect(len(runs) == 1 and state_of(runs[0]) == "edited", f"state after kill {[state_of(x) for x in runs]}", f)
    S.set_control(check_kill=False)
    rv = S.run("verify", None)
    expect(rv["rc"] == 1 and "ATTENTION" in rv["out"] and "stopped before restarting" in rv["out"],
           f"verify after the kill: exit {rv['rc']}, not ATTENTION for the unfinished run", f)
    unchanged(rv, f, "verify after kill: ")
    r2 = S.run("check", None)
    expect(r2["rc"] == 1 and "still marked 'edited'" in r2["out"], "check does not block on the unfinished run", f)
    expect("WARN: lock" in r2["out"], "stale lock not reported by check", f)
    r3 = S.run("rollback", "ROLLBACK\n")
    expect(r3["rc"] == 1 and "no longer active" in r3["out"], "stale lock not refused", f)
    unchanged(r3, f, "rollback with stale lock: ")
    lock = os.path.join(S.tmp, "casaray_register.lock")
    os.remove(os.path.join(lock, "pid"))
    os.rmdir(lock)                                   # what the STOP message tells the owner to do
    r4 = S.run("rollback", "ROLLBACK\n")
    expect(r4["rc"] == 0, f"rollback exit {r4['rc']} != 0", f)
    expect("no restart" in r4["out"] and not calls_of(r4, "core", "restart"), "restarted although never restarted", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not restored", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "theme not removed", f)
    expect(runs and state_of(runs[0]) == "rolled-back", "run not rolled-back", f)
    a, rm, ch = diff(r1["before"], r4["after"])
    expect(outside_runs(a) == [] and rm == [] and outside_runs(ch) == [], "fixture not back to pre-apply", f)
    return f, "SIGKILL mid-check -> check BLOCKED, stale lock refused, rollback restores without restart"


def sc_changed_during_backup(wd, S):
    S.set_control(backup_side_effect="lovelace:\n  resource_mode: yaml\n")
    r = S.run("apply", "APPLY\n")
    f = []
    expect(r["rc"] == 1, f"exit {r['rc']} != 1", f)
    expect("while the backup ran" in r["out"], "change during the backup not reported", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG + "lovelace:\n  resource_mode: yaml\n",
           "configuration.yaml was touched by the script", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "theme installed", f)
    expect(not calls_of(r, "core", "check") and not calls_of(r, "core", "restart"), "check/restart called", f)
    a, rm, ch = diff(r["before"], r["after"])
    expect(outside_runs(a) == [] and rm == [] and outside_runs(ch) == ["configuration.yaml"],
           f"outside run folder: added={outside_runs(a)} changed={outside_runs(ch)}", f)
    return f, "lovelace: added during the backup: stopped before any edit"


def sc_changed_before_replace(wd, S):
    """configuration.yaml changes after the pre-copy, before the replace. strace delays the theme
    step's link() by 1.5 s; a harness thread (another actor) appends a line once the run folder's
    theme.new exists, i.e. inside that window, before the script compares and replaces."""
    import threading
    import time
    S.extra_strace = ["-e", "inject=link,linkat:delay_enter=1500000"]
    edit = "# edited by someone else while the run was in progress\n"

    def actor():
        deadline = time.time() + 120
        while time.time() < deadline:
            for d in (run_dirs(S.cfg) if os.path.isdir(f"{S.cfg}/_recovery") else []):
                if os.path.exists(os.path.join(d, "theme.new")):
                    time.sleep(0.2)
                    with open(f"{S.cfg}/configuration.yaml", "a") as c:
                        c.write(edit)
                    return
            time.sleep(0.005)
    t = threading.Thread(target=actor, daemon=True)
    t.start()
    r = S.run("apply", "APPLY\n")
    t.join(5)
    f = []
    expect(r["rc"] == 3, f"exit {r['rc']} != 3", f)
    expect("changed while this ran; not replaced" in r["out"], "concurrent edit not detected", f)
    expect("never replaced by this run; left as it is" in r["out"], "config not left alone", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG + edit, "configuration.yaml is not the other actor's version", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "theme or themes/ left behind", f)
    runs = run_dirs(S.cfg)
    expect(runs and state_of(runs[0]) == "rolled-back", f"state {[state_of(x) for x in runs]}", f)
    expect(not calls_of(r, "core", "check") and not calls_of(r, "core", "restart"), "check/restart called", f)
    return f, "edit after the pre-copy: not replaced, theme removed, rolled-back, the other edit kept"


def sc_usage(wd, S):
    r = S.run("bogus", None)
    f = []
    expect(r["rc"] == 2, f"exit {r['rc']} != 2", f)
    unchanged(r, f)
    expect(not r["ha"], "ha called", f)
    return f, "unknown mode: exit 2"


# ---- review round 1 (18/10/2026): state machine, platform, scope -------------------------------
def setup_lovelace_bom(S):        # a Windows editor's BOM before a first-line key: still 'lovelace' to HA
    w(f"{S.cfg}/configuration.yaml", "﻿lovelace:\n  dashboards:\n    owner-board:\n      mode: yaml\n"
      "      title: Owner\n      filename: dashboards/casaray_v2.yaml\n" + DEFAULT_CONFIG)


def setup_lovelace_complex(S):    # '? lovelace' complex key
    w(f"{S.cfg}/configuration.yaml", DEFAULT_CONFIG + "? lovelace\n: {resource_mode: yaml}\n")


def setup_lovelace_tagged(S):     # '!!str lovelace:' tagged key
    w(f"{S.cfg}/configuration.yaml", DEFAULT_CONFIG + "!!str lovelace:\n  resource_mode: yaml\n")


def setup_banned(S):
    S.set_control(banned=True)


def sc_check_commented_lovelace(wd, S):
    w(f"{S.cfg}/configuration.yaml", DEFAULT_CONFIG + "# lovelace:\n#   resource_mode: yaml\n")
    r = S.run("check", None)
    f = []
    expect(r["rc"] == 0 and last_line(r, "READY"), f"commented-out lovelace blocks: exit {r['rc']}", f)
    unchanged(r, f)
    return f, "a commented-out lovelace block does not block"


def sc_check_ssl(wd, S):
    S.set_control(core_ssl=True)
    r = S.run("check", None)
    f = []
    expect(r["rc"] == 0 and last_line(r, "READY"), f"exit {r['rc']}, not READY with ssl", f)
    expect(r["curl"] and all(c["url"] == "https://homeassistant:8123/manifest.json" and c["insecure"]
                             for c in r["curl"]), f"ssl probe is not https + -k to /manifest.json: {r['curl']}", f)
    unchanged(r, f)
    return f, "ssl: https://homeassistant:8123/manifest.json with -k, no credential"


def sc_check_fails_secret(wd, S):
    """A pre-existing error in a section that uses !secret: the raw check output then holds the
    resolved value. Only where the error is may reach the terminal or the run record (the generic
    canary assertions cover both)."""
    original = DEFAULT_CONFIG + "homeassistant:\n  name: Home\n  latitude: !secret latitude\n  unit_system: bogus\n"
    w(f"{S.cfg}/configuration.yaml", original)
    w(os.path.join(S.st, "check_fail_marker"), "x")
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, original, restarts=0)
    if S.control["check"] == "real":
        expect(SECRET_CANARY in rd(os.path.join(S.st, "check_runs.log")),
               "vacuous: the raw check output holds no resolved secret", f)
        expect("Invalid config for 'homeassistant' at secrets.yaml, line" in r["out"], "error location not shown", f)
    return f, "check fails in a !secret section: location shown, value nowhere"


def sc_rollback_check_fails(wd, S):
    """Rollback finds 'ha core check' failing on the restored file (an unrelated, later break):
    no restart, state kept so rollback can be re-run; after the fix it only checks and restarts."""
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    w(f"{S.cfg}/scenes.yaml", "- name: [unclosed\n")
    marker = os.path.join(S.st, "check_fail_marker")
    w(marker, "x")
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 4, f"rollback exit {r2['rc']} != 4", f)
    expect(not calls_of(r2, "core", "restart"), "restarted although the check failed", f)
    expect("NOT restarting" in r2["out"], "no 'NOT restarting'", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not restored", f)
    expect(not os.path.exists(f"{S.cfg}/themes"), "theme or themes/ left", f)
    runs = run_dirs(S.cfg)
    expect(runs and state_of(runs[0]) == "applied", f"state {[state_of(x) for x in runs]} != applied", f)
    if S.control["check"] == "real":
        expect("scenes.yaml, line 1" in r2["out"], "error location not shown", f)
    w(f"{S.cfg}/scenes.yaml", "")
    os.remove(marker)
    r3 = S.run("rollback", "ROLLBACK\n")
    expect(r3["rc"] == 0 and "rollback done" in r3["out"], f"second rollback exit {r3['rc']}", f)
    expect(len(calls_of(r3, "core", "restart")) == 1, "second rollback did not restart once", f)
    expect(runs and state_of(runs[0]) == "rolled-back", "not rolled-back after the second rollback", f)
    a, rm, ch = diff(r1["before"], r3["after"])
    expect(outside_runs(a) == [] and rm == [] and outside_runs(ch) == [], "fixture not back to pre-apply", f)
    return f, "rollback with a failing check: no restart, exit 4; re-run after the fix restarts once"


def sc_rollback_recovery(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    S.set_control(recovery_after_restart=[2])
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 4, f"rollback exit {r2['rc']} != 4", f)
    expect("RECOVERY MODE" in r2["out"] and "rollback done" not in r2["out"], "recovery mode not reported", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not restored", f)
    expect(len(calls_of(r2, "core", "restart")) == 1, "rollback did not restart once", f)
    return f, "rollback lands in recovery mode: exit 4, not 'rollback done'"


def sc_recovery_both(wd, S):
    S.set_control(recovery_after_restart=[1, 2])
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=2, rc=4)
    expect("RECOVERY MODE again" in r["out"], "second recovery mode not reported", f)
    return f, "recovery mode on both boots: restored, exit 4"


def sc_restart_refused(wd, S):
    """Supervisor refuses the restart; the old Core keeps answering. The files go back (no restart),
    so the block cannot load later, unwatched."""
    S.set_control(restart_refused=True)
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=1, rc=4)
    st = json.loads(rd(os.path.join(S.st, "state.json")))
    expect(st["restarts"] == 0, "the fake restarted", f)
    expect("DONE" not in r["out"], "DONE although Core never restarted", f)
    expect("Offline database migration" in r["out"], "Supervisor's reason not shown", f)
    runs = run_dirs(S.cfg)
    expect(runs and manifest(runs[0]).get("restart_confirmed") != "yes", "restart_confirmed recorded", f)
    return f, "restart refused: files back, exit 4, no DONE"


def sc_rollback_restart_refused(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    S.set_control(restart_refused=True)
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 4, f"rollback exit {r2['rc']} != 4", f)
    expect("rollback done" not in r2["out"] and "could not be confirmed" in r2["out"], "refused restart not reported", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml not restored", f)
    return f, "rollback restart refused: files back, exit 4"


def sc_interrupted_before_restart(wd, S):
    """Ctrl-C while the log marker is read, after 'check passed' and before the restart request."""
    S.set_control(marker_interrupt=True)
    r = S.run("apply", "APPLY\n")
    f = []
    assert_rolled_back(S, r, f, DEFAULT_CONFIG, restarts=0)
    expect("interrupted" in r["out"] and "restart was requested" not in r["out"], "wrong interrupt message", f)
    return f, "SIGINT before the restart request: everything back, no restart"


def sc_interrupted_during_restart(wd, S):
    S.set_control(restart_interrupt=True)
    f = []
    r1 = S.run("apply", "APPLY\n")
    expect(r1["rc"] == 130, f"exit {r1['rc']} != 130", f)
    expect("restart was requested" in r1["out"] and "not confirmed" in r1["out"], "interrupt message", f)
    runs = run_dirs(S.cfg)
    expect(runs and state_of(runs[0]) == "applied" and manifest(runs[0]).get("restart_confirmed") != "yes",
           "state after the interrupt", f)
    S.set_control(restart_interrupt=False)
    rv = S.run("verify", None)
    expect(rv["rc"] == 1 and "NOT confirmed" in rv["out"], f"verify exit {rv['rc']}: not ATTENTION", f)
    r3 = S.run("rollback", "ROLLBACK\n")
    expect(r3["rc"] == 0 and rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, f"rollback exit {r3['rc']}", f)
    return f, "SIGINT during the restart: exit 130, verify ATTENTION, rollback works"


def sc_logs_unreadable(wd, S):
    """The logs endpoint prints an error body with exit 0: recovery mode is unknown, so WARN."""
    S.set_control(logs_error=True, recovery_after_restart=[1])
    f = []
    r = S.run("apply", "APPLY\n")
    assert_applied(wd, S, r, f, DEFAULT_CONFIG)
    expect("could not isolate the log" in r["out"], "no WARN although the log could not be read", f)
    return f, "unreadable log: applied with the recovery-mode WARN"


def kill_script_tree(S):
    """SIGKILL this world's script (its top shell) and everything under it; never strace, the
    harness or another world's processes (matched by this world's FAKE_STATE)."""
    import signal
    ppid, sh, ours = {}, set(), set()
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            a = rd(f"/proc/{d}/cmdline", True).split(b"\0")
            ppid[int(d)] = int(rd(f"/proc/{d}/stat").rsplit(")", 1)[1].split()[1])
            env = rd(f"/proc/{d}/environ", True).split(b"\0")
        except (OSError, IndexError, ValueError):
            continue
        if ("FAKE_STATE=" + S.st).encode() in env:
            ours.add(int(d))
            if a[0].endswith(b"/sh"):
                sh.add(int(d))
    tree = {p for p in sh if ppid.get(p) not in sh}          # the top shell(s)
    grew = True
    while grew:
        more = {p for p, q in ppid.items() if q in tree and p in ours} - tree
        grew = bool(more)
        tree |= more
    for p in tree:
        try:
            os.kill(p, signal.SIGKILL)
        except OSError:
            pass
    return sorted(tree)


def sc_killed_before_link(wd, S):
    """SIGKILL between 'theme_created=pending' and the theme's link(); the owner then installs the
    theme by hand. Rollback must keep that file: 'pending' only records intent."""
    import threading
    import time
    S.extra_strace = ["-e", "inject=link,linkat:delay_enter=1500000"]
    got = {}

    def actor():
        deadline = time.time() + 120
        while time.time() < deadline:
            for d in (run_dirs(S.cfg) if os.path.isdir(f"{S.cfg}/_recovery") else []):
                try:
                    pend = manifest(d).get("theme_created") == "pending"
                except OSError:
                    continue
                if pend and os.path.exists(os.path.join(d, "theme.new")):
                    time.sleep(0.3)               # inside ln's delayed link()
                    got["pids"] = kill_script_tree(S)
                    return
            time.sleep(0.005)
    t = threading.Thread(target=actor, daemon=True)
    t.start()
    r1 = S.run("apply", "APPLY\n")
    t.join(5)
    f = []
    theme = f"{S.cfg}/themes/deez_your_name.yaml"
    runs = run_dirs(S.cfg)
    expect(r1["rc"] != 0 and got.get("pids"), f"apply was not killed (exit {r1['rc']})", f)
    expect(not os.path.exists(theme), "vacuous: the theme was linked before the kill", f)
    expect(runs and manifest(runs[0]).get("theme_created") == "pending", "theme_created is not 'pending'", f)
    shutil.copyfile(f"{S.cfg}/deez_repo/themes/deez_your_name.yaml", theme)     # the owner, by hand
    lock = os.path.join(S.tmp, "casaray_register.lock")
    shutil.rmtree(lock, ignore_errors=True)                                       # as the STOP message says
    r2 = S.run("rollback", "ROLLBACK\n")
    expect(r2["rc"] == 0, f"rollback exit {r2['rc']} != 0", f)
    expect(os.path.isfile(theme) and sha_file(theme) == H_THEME, "the hand-installed theme was removed", f)
    expect("stopped before installing it" in r2["out"], "kept without saying why", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG, "configuration.yaml changed", f)
    expect(runs and state_of(runs[0]) == "rolled-back", "not rolled-back", f)
    return f, "killed before the theme link: rollback keeps the owner's hand-installed theme"


def sc_rollback_from_copy(wd, S):
    f = []
    r1 = S.run("apply", "APPLY\n")
    run = assert_applied(wd, S, r1, f, DEFAULT_CONFIG)
    if not run:
        return f, ""
    r2 = S.run("rollback", "ROLLBACK\n", script=os.path.join(run, "register_casaray.sh"))
    expect(r2["rc"] == 0, f"rollback from the run folder's copy: exit {r2['rc']}", f)
    expect(rd(f"{S.cfg}/configuration.yaml") == DEFAULT_CONFIG and not os.path.exists(f"{S.cfg}/themes"),
           "not restored", f)
    return f, "rollback from the run folder's copy (no /tmp needed)"


def owner_recovers(T):
    """What the owner does after a run: check; clear a stale lock as told; rollback if a run blocks."""
    seq = [T.run("check", None, trace=False)]
    shutil.rmtree(os.path.join(T.tmp, "casaray_register.lock"), ignore_errors=True)
    if "still marked" in seq[0]["out"]:
        seq.append(T.run("rollback", "ROLLBACK\n", trace=False))
    return seq


CLAIMS_BACK = ("everything is back as before", "put back; Home Assistant was NOT restarted", "rollback done",
               "rolled back; no restart needed", "files put back", "rolled back; Core restarted")


def sc_disk_full_sweep(wd, S):
    """The full backup lands on the same data partition. For K = 0, 1, 2 ... free 4 KiB pages left
    after it (config folder on a tmpfs), with the check passing and failing: every 'back as before'
    claim must be true when made, DONE only with state 'applied', no restart when the check fails,
    and after the owner's recovery (free space, check, clear lock, rollback) the files are as before."""
    if os.geteuid() != 0 or not shutil.which("mount"):
        return None, "needs root and mount (tmpfs)"
    f = []
    seen, k_ok = {}, None
    for check_fails in (False, True):
        k, ok_streak = 0, 0
        while True:
            tag = f"k{k}{'cf' if check_fails else 'ok'}"
            T = World(S.dir, tag, S.bindir, None, S.strace_cmd)
            mnt = os.path.join(T.dir, "fs")
            os.makedirs(mnt)
            if subprocess.run(["mount", "-t", "tmpfs", "-o", "size=8m,mode=755", "tmpfs", mnt],
                              capture_output=True).returncode != 0:
                return None, "cannot mount a tmpfs"
            try:
                shutil.copytree(T.cfg, os.path.join(mnt, "config"), symlinks=True)
                T.cfg = os.path.join(mnt, "config")
                os.chmod(os.path.join(T.cfg, "_recovery"), 0o700)
                original = rd(f"{T.cfg}/configuration.yaml")
                filler = os.path.join(mnt, "filler")
                T.env_extra["RC_MIN_FREE_KB"] = "0"
                T.control.update(fill_leave_pages=k, fill_path=filler)
                if check_fails:
                    w(os.path.join(T.st, "check_fail_marker"), "x")
                r = T.run("apply", "APPLY\n", trace=False)
                runs = run_dirs(T.cfg)
                after_apply = [(state_of(x), manifest(x).get("restart_confirmed")
                                if os.path.exists(os.path.join(x, "manifest")) else None) for x in runs]
                T.control.pop("fill_leave_pages")
                if os.path.exists(filler):
                    os.remove(filler)                                      # the owner frees space
                seq = [r] + owner_recovers(T)
                v = []
                for q in seq:
                    v += [f"{q['mode']}: {x}" for x in q["generic"]]
                    restored = (q["after"].get("configuration.yaml", ("", ""))[1] == sha_text(original)
                                and "themes" not in q["after"])
                    for c in CLAIMS_BACK:
                        if c in q["out"] and not restored:
                            v.append(f"{q['mode']} exit {q['rc']} says '{c}' but the files are not as before")
                    if check_fails and calls_of(q, "core", "restart"):
                        v.append(f"{q['mode']} restarted although the check fails")
                if r["rc"] == 0 and after_apply != [("applied", "yes")]:
                    v.append(f"apply exit 0 but (state, restart_confirmed) = {after_apply}")
                if r["rc"] not in (0, 1, 3, 4):
                    v.append(f"apply exit {r['rc']}")
                if rd(f"{T.cfg}/configuration.yaml") != original or os.path.exists(f"{T.cfg}/themes"):
                    v.append("after the owner's recovery the files are NOT as before: "
                             f"{[(q['mode'], q['rc']) for q in seq]}")
                seen[(check_fails, r["rc"])] = seen.get((check_fails, r["rc"]), 0) + 1
                f += [f"K={k} {'check fails' if check_fails else 'check passes'}: {x}" for x in v]
                ok_streak = ok_streak + 1 if r["rc"] == (3 if check_fails else 0) else 0
            finally:
                subprocess.run(["umount", "-l", mnt], capture_output=True)
            k += 1
            if not check_fails and ok_streak >= 2:
                k_ok = k
                break
            if check_fails and k >= (k_ok or 0) + 1:
                break
            if k > 96:
                f.append(f"no success within 96 free pages ({'check fails' if check_fails else 'check passes'})")
                break
    n = sum(seen.values())
    return f, f"{n} worlds, K=0..{(k_ok or 0)}: " + ", ".join(
        f"{'cf' if c else 'ok'} exit {rc} x{m}" for (c, rc), m in sorted(seen.items()))


def sc_guard_scripts(wd, S):
    """The withdrawn and disabled modes of the sibling scripts stay refused, and change nothing."""
    f = []
    fx = os.path.join(S.dir, "login")
    cfg = os.path.join(fx, "config")
    calls = os.path.join(fx, "calls.log")
    stub = os.path.join(fx, "bin")
    os.makedirs(stub)
    for a in os.listdir(S.bindir):
        if a not in ("ha", "curl", "docker", "python3"):
            os.symlink(os.path.join(S.bindir, a), os.path.join(stub, a))
    for n in ("ha", "docker", "curl", "python3"):
        w(os.path.join(stub, n), f"#!{S.bindir}/sh\necho \"{n} $*\" >>{calls}\n"
          + ("printf 401\n" if n == "curl" else "") + "exit 0\n", 0o755)
    w(f"{cfg}/.storage/auth_provider.homeassistant", '{"data": {"users": [{"username": "owner", "password": "LIVE"}]}}\n')
    w(f"{cfg}/.storage/auth", json.dumps({"data": {"users": [], "credentials": []}}))
    w(f"{cfg}/_recovery/PREPARED", "2026-10-01T00:00:00Z\n")
    w(f"{cfg}/_recovery/plan.txt", ".storage/auth_provider.homeassistant\n")
    w(f"{cfg}/_recovery/stage/.storage/auth_provider.homeassistant",
      '{"data": {"users": [{"username": "owner", "password": "OLD-STAGED"}]}}\n')
    w(f"{cfg}/_recovery/owner/pre/.storage/auth", "{}\n")
    before = snapshot(cfg)
    cases = [("recover_login.sh", "apply", 1, "apply is disabled"),
             ("recover_login.sh", "rollback", 1, "rollback is disabled"),
             ("fix_owner_login.sh", "rollback", 1, "rollback is disabled"),
             ("deploy_casaray.sh", "apply", 2, "WITHDRAWN")]
    for script, mode, want, needle in cases:
        p = subprocess.run([os.path.join(S.bindir, "sh"), os.path.join(REPO, "scripts/recovery", script), mode],
                           input="APPLY\nROLLBACK\n", capture_output=True, text=True, timeout=120,
                           env={"PATH": stub, "RC_HOST_CONFIG": cfg, "RC_POLL": "0", "RC_TTY": os.devnull})
        expect(p.returncode == want and needle in p.stdout + p.stderr,
               f"{script} {mode}: exit {p.returncode} (want {want}), {(p.stdout + p.stderr).strip()[-120:]!r}", f)
    a, rm, ch = diff(before, snapshot(cfg))
    expect(not (a or rm or ch), f"a guarded mode changed the fixture: {a + rm + ch}", f)
    expect(not os.path.exists(calls), f"a guarded mode called a tool: {rd(calls) if os.path.exists(calls) else ''}", f)
    return f, "recover_login apply/rollback, fix_owner_login rollback refused; deploy_casaray withdrawn"


def sc_header_references(wd, S):
    """Every file the recovery scripts' headers point to exists."""
    f = []
    n_refs = 0
    for n in ("register_casaray.sh", "fix_owner_login.sh", "recover_login.sh", "deploy_casaray.sh"):
        hdr = "\n".join(l for l in rd(os.path.join(REPO, "scripts/recovery", n)).splitlines()[:60] if l.startswith("#"))
        for ref in re.findall(r"scripts/recovery/[A-Za-z0-9_.-]+|\b[A-Za-z0-9_-]+\.md\b", hdr):
            ref = ref.rstrip(".")
            n_refs += 1
            path = os.path.join(REPO, ref) if ref.startswith("scripts/") else os.path.join(REPO, "scripts/recovery", ref)
            expect(os.path.exists(path), f"{n} names {ref}, which does not exist", f)
    return f, f"{n_refs} references checked"


SCENARIOS = [
    ("check-ready", sc_check_ready),
    ("blocked-existing-lovelace", blocked(setup_lovelace, "top-level 'lovelace:'")),
    ("blocked-storage-casaray-v2", blocked(setup_storage, "UI (storage) dashboard already uses url_path casaray-v2")),
    ("blocked-dashboard-missing", blocked(setup_dash_missing, "dashboards/casaray_v2.yaml is missing")),
    ("blocked-theme-unverifiable", blocked(setup_theme_unverifiable, "themes/deez_your_name.yaml is missing and deez_repo")),
    ("blocked-config-symlink", blocked(setup_cfg_symlink, "configuration.yaml is a symlink")),
    ("blocked-low-free-space", blocked(setup_low_space, "MB free for the backup")),
    ("blocked-probe-down", blocked(setup_probe_down, "liveness probe")),
    ("warn-dashboard-hash-differs", sc_warn_dash),
    ("apply-success", sc_apply_success),
    ("apply-no-final-newline", sc_apply_noeol),
    ("apply-wrong-confirmation", sc_wrong_confirmation),
    ("apply-backup-fails", sc_backup_fails("fail")),
    ("apply-backup-unverified", sc_backup_fails("info")),
    ("apply-backup-no-slug", sc_backup_fails("noslug")),
    ("apply-backup-stale-slug", sc_backup_fails("stale")),
    ("apply-backup-partial", sc_backup_fails("partial")),
    ("apply-restart-rc-nonzero", sc_restart_rc),
    ("apply-config-changed-during-backup", sc_changed_during_backup),
    ("apply-config-changed-before-replace", sc_changed_before_replace),
    ("apply-check-fails", sc_check_fails),
    ("apply-core-never-up", sc_never_up),
    ("apply-recovery-mode", sc_recovery_mode),
    ("apply-interrupted-during-check", sc_interrupted),
    ("apply-when-already-registered", blocked(setup_registered, "already mentions casaray-v2")),
    ("theme-already-present-differs", sc_theme_differs),
    ("rollback-after-success", sc_rollback_after_success),
    ("rollback-keeps-edited-theme", sc_rollback_edited_theme),
    ("rollback-with-nothing-applied", sc_rollback_nothing),
    ("rollback-refuses-edited-config", sc_rollback_changed),
    ("rollback-wrong-confirmation", sc_rollback_wrong),
    ("apply-killed-then-rollback", sc_killed),
    ("apply-lock-held", sc_lock_held),
    ("verify-readonly", sc_verify),
    ("usage-unknown-mode", sc_usage),
    ("blocked-lovelace-after-bom", blocked(setup_lovelace_bom, "top-level 'lovelace:'")),
    ("blocked-lovelace-complex-key", blocked(setup_lovelace_complex, "top-level 'lovelace:'")),
    ("blocked-lovelace-tagged-key", blocked(setup_lovelace_tagged, "top-level 'lovelace:'")),
    ("check-ready-commented-lovelace", sc_check_commented_lovelace),
    ("check-ready-ssl", sc_check_ssl),
    ("blocked-ip-banned", blocked(setup_banned, "ip_bans.yaml")),
    ("apply-check-fails-secret-section", sc_check_fails_secret),
    ("apply-restart-refused", sc_restart_refused),
    ("apply-interrupted-before-restart", sc_interrupted_before_restart),
    ("apply-interrupted-during-restart", sc_interrupted_during_restart),
    ("apply-recovery-mode-both-boots", sc_recovery_both),
    ("apply-log-unreadable", sc_logs_unreadable),
    ("apply-killed-before-theme-link", sc_killed_before_link),
    ("rollback-check-fails-no-restart", sc_rollback_check_fails),
    ("rollback-recovery-mode", sc_rollback_recovery),
    ("rollback-restart-refused", sc_rollback_restart_refused),
    ("rollback-from-run-folder-copy", sc_rollback_from_copy),
    ("apply-disk-full-sweep", sc_disk_full_sweep),
    ("guard-sibling-scripts", sc_guard_scripts),
    ("header-references-exist", sc_header_references),
]


# ------------------------------------------------------------------ main
class WD:
    pass


def tools():
    busybox = os.environ.get("BUSYBOX") or shutil.which("busybox")
    strace = shutil.which("strace")
    ha_python = os.environ.get("HA_CHECK_PYTHON")
    return busybox, strace, ha_python


def make_bin(base, busybox):
    bindir = os.path.join(base, "bin")
    os.makedirs(bindir)
    applets = subprocess.run([busybox, "--list"], capture_output=True, text=True).stdout.split()
    bb = os.path.join(bindir, "busybox")
    shutil.copy2(busybox, bb)
    for a in applets:
        if a not in ("busybox", "ha", "curl"):
            os.symlink("busybox", os.path.join(bindir, a))
    for name, src in (("ha", FAKE_HA), ("curl", FAKE_CURL)):
        w(os.path.join(bindir, name), src.format(py=sys.executable), 0o755)
    return bindir


def syntax_checks(busybox):
    res = []
    for label, cmd in (("busybox ash -n", [busybox, "ash", "-n", SCRIPT]),
                       ("dash -n", ["dash", "-n", SCRIPT] if shutil.which("dash") else None),
                       ("shellcheck -s sh -S warning", ["shellcheck", "-s", "sh", "-S", "warning", SCRIPT]
                        if shutil.which("shellcheck") else None)):
        if cmd is None:
            res.append((label, "SKIP", "not installed"))
            continue
        p = subprocess.run(cmd, capture_output=True, text=True)
        res.append((label, "PASS" if p.returncode == 0 else "FAIL", (p.stdout + p.stderr).strip()[:400]))
    return res


def main():
    busybox, strace_bin, ha_python = tools()
    missing = [n for n, v in (("busybox", busybox), ("strace", strace_bin)) if not v]
    if missing:
        print(f"SKIP: needs {', '.join(missing)} (set BUSYBOX to a BusyBox binary)")
        return 0
    strace_cmd = [strace_bin]
    if subprocess.run([strace_bin, "-f", "--seccomp-bpf", "-qq", "-e", "trace=openat", "-o", os.devnull, "true"],
                      capture_output=True).returncode == 0:
        strace_cmd.append("--seccomp-bpf")
    print(f"script  {SCRIPT}  sha256 {sha_file(SCRIPT)}")
    print(f"busybox {busybox}")
    if ha_python:
        print(f"core check: REAL check_config via {ha_python}")
    else:
        print("core check: FAKE (no HA python found): fails only when a marker file exists")
    if repo("scripts/recovery/casaray_config_block.yaml").lstrip("\n") != BLOCK:
        print("[FAIL] block-matches-repo: casaray_config_block.yaml differs from the expected block")
        return 1
    if sha_text(repo("dashboards/casaray_v2.yaml")) != H_DASH or sha_text(repo("themes/deez_your_name.yaml")) != H_THEME:
        print("[FAIL] repo-sources: the repo dashboard or theme no longer has the expected sha256")
        return 1
    if ha_python:   # the literal above must still be what this Core writes (asked in its own process)
        p = subprocess.run([ha_python, "-I", "-c", "import sys; from homeassistant.config import DEFAULT_CONFIG; "
                            "sys.stdout.write(DEFAULT_CONFIG)"], capture_output=True, text=True)
        if p.returncode != 0 or p.stdout != DEFAULT_CONFIG:
            print("[FAIL] default-config-literal: DEFAULT_CONFIG differs from the HA venv's")
            return 1
        print("[PASS] default-config-literal: matches homeassistant.config.DEFAULT_CONFIG of the HA venv")
    base = tempfile.mkdtemp(prefix="register_casaray_")
    wd = WD()
    wd.ha_python = ha_python
    total = 0
    evidence_ok, n_runs = True, 0
    try:
        bindir = make_bin(base, busybox)
        only = [x for x in os.environ.get("ONLY", "").split(",") if x]   # ONLY=a,b runs a subset
        for name, fn in [sc for sc in SCENARIOS if not only or sc[0] in only]:
            S = World(base, name, bindir, ha_python, strace_cmd)
            try:
                fails, detail = fn(wd, S)
            except Exception as exc:  # a harness or fixture error is a failure, not a crash
                fails, detail = [f"harness error: {type(exc).__name__}: {exc}"], ""
            if fails is None:
                print(f"[SKIP] {name}: {detail}")
                continue
            for r in S.runs:
                n_runs += 1
                g = r["generic"]
                if any("_recovery/casaray/ changed" in x for x in g):
                    evidence_ok = False
                fails += [f"[{r['mode']} run] {x}" for x in g]
            total += 1 if fails else 0
            print(f"[{'PASS' if not fails else 'FAIL'}] {name}: {detail}"
                  + "".join(f"\n        !! {x}" for x in fails[:12]))
            if fails:
                for r in S.runs:
                    print(f"        --- {r['mode']} exit {r['rc']} output tail:")
                    for l in (r["out"] + r["err"]).splitlines()[-12:]:
                        print(f"        | {l}")
        print(f"[{'PASS' if evidence_ok else 'FAIL'}] evidence-folder-untouched: "
              f"_recovery/casaray/ byte-identical across all {n_runs} runs")
        total += 0 if evidence_ok else 1
        for label, verdict, txt in syntax_checks(busybox):
            print(f"[{verdict}] syntax: {label}" + (f"\n        {txt}" if verdict == "FAIL" else ""))
            total += 1 if verdict == "FAIL" else 0
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"TOTAL FAILURES: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
