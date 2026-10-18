"""Fixture tests for scripts/recovery/casaray_evidence.sh.

    python3 -I scripts/recovery/tests/test_casaray_evidence.py

Each fixture is a throwaway chroot root holding only a static BusyBox (every
applet as a symlink), /dev/null, the script at /tmp/casaray_evidence_v1.2.sh
(the path the owner uses) and a dummy config tree. Each run is wrapped in
strace, so the assertions cover what the script opened and every write-class
syscall, not only what it printed. Every sensitive dummy file carries a canary
that must never reach the output.

Needs root (chroot, mknod), strace and a STATIC BusyBox (env BUSYBOX, or
'busybox' on PATH). Prints SKIP and exits 0 when any of them is missing.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CANDIDATE = os.path.join(REPO, "scripts/recovery/casaray_evidence.sh")
RUN_AS = "/tmp/casaray_evidence_v1.2.sh"

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
BLOCK = """
lovelace:
  dashboards:
    casaray-v2:
      mode: yaml
      title: CasaRay
      icon: mdi:home-heart
      show_in_sidebar: true
      filename: dashboards/casaray_v2.yaml
"""
ALLOW = """configuration.yaml
input_boolean.yaml
input_number.yaml
input_select.yaml
input_text.yaml
input_datetime.yaml
person.yaml
people.yaml
helpers.yaml
dashboards/casaray_v2.yaml
dashboards/deez_smart_home.yaml
themes/deez_your_name.yaml
deez_repo/dashboards/casaray_v2.yaml
deez_repo/themes/deez_your_name.yaml
_recovery/casaray/configuration.yaml.pre
.storage/lovelace_dashboards
.storage/lovelace_resources
.storage/repairs.issue_registry
.storage/person
.storage/input_boolean
.storage/input_number
.storage/input_select
.storage/input_text
.storage/input_datetime""".splitlines()

# Canary values. URLs are assembled at runtime so this file never contains a
# credential-shaped literal (scripts/ha_validate.sh scans tracked files for them).
CANARIES = ["CANARY_SECRETS_7d1", "CANARY_AUTH_19c", "CANARY_PROVIDER_44b", "CANARY_CLOUD_a02",
            "CANARY_ESP_5e9", "CANARY_DEPLOY_c31", "CANARY_OWNER_8f0", "CANARY_STAGE_2b7",
            "CANARY_PKG_e66", "CANARY_GIT_0aa", "CANARY_NOTREAD_91d", "CANARY_RESOURCE_3c4",
            "CANARY_QS_d58", "CANARY_OUTSIDE_6ab", "CANARY_ADDON_f12", "ba94d3a0"]
CRED_RESOURCE_URL = "https://user" + ":" + "CANARY_RESOURCE_3c4" + "@" + "cdn.example.com/x/y.js?token=CANARY_QS_d58"
CRED_GIT_URL = "https://x" + ":" + "CANARY_GIT_0aa" + "@" + "github.com/r"
DENIED_OPEN = re.compile(r"secret|auth|\.cloud|esphome|deez_deploy|askpass|/_recovery/(owner|stage|pre/)|"
                         r"packages/private|lovelace\.deez_smart_home|/\.git/|/outside/|^/config/")


def w(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def repo(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def storage_json(key, items):
    return json.dumps({"version": 1, "minor_version": 1, "key": key, "data": {"items": items}}, indent=2)


def make_root(roots, name, busybox):
    root = os.path.join(roots, name)
    for d in ("bin", "dev", "tmp"):
        os.makedirs(os.path.join(root, d))
    shutil.copy2(busybox, os.path.join(root, "bin/busybox"))
    applets = subprocess.run([busybox, "--list"], capture_output=True, text=True).stdout.split()
    for a in applets:
        if a != "busybox":
            os.symlink("busybox", os.path.join(root, "bin", a))
    os.mknod(os.path.join(root, "dev/null"), 0o20666, os.makedev(1, 3))
    shutil.copy2(CANDIDATE, root + RUN_AS)
    return root


def sensitive(cfg):
    """Credential-bearing files; none may be opened or echoed."""
    w(f"{cfg}/secrets.yaml", "wifi_password: CANARY_SECRETS_7d1\nchinese_dashboard: CANARY_SECRETS_7d1\n")
    w(f"{cfg}/.storage/auth", '{"data": {"refresh_tokens": [{"token": "CANARY_AUTH_19c"}]}}')
    w(f"{cfg}/.storage/auth_provider.homeassistant", '{"data": {"users": [{"password": "CANARY_PROVIDER_44b"}]}}')
    w(f"{cfg}/.storage/auth.corrupt.2026-10-12T03:01:02+00:00", "CANARY_AUTH_19c")
    w(f"{cfg}/.cloud/cloud.yaml", "token: CANARY_CLOUD_a02\n")
    w(f"{cfg}/esphome/secrets.yaml", "api_key: CANARY_ESP_5e9\n")
    w(f"{cfg}/esphome/node.yaml", "chinese_dashboard: CANARY_ESP_5e9\n")
    w(f"{cfg}/.deez_deploy.env", "DEEZ_GH_TOKEN=CANARY_DEPLOY_c31\n")
    w(f"{cfg}/_recovery/owner/auth_provider.homeassistant", "CANARY_OWNER_8f0")
    w(f"{cfg}/_recovery/stage/.storage/auth_provider.homeassistant", "CANARY_STAGE_2b7")
    w(f"{cfg}/deez_repo/.git/config", "[remote]\n url = " + CRED_GIT_URL + "\n")


def fx_post_loss(root):
    """The likely live shape: default config, legacy registration gone, content file survives."""
    cfg = f"{root}/homeassistant"
    sensitive(cfg)
    w(f"{cfg}/configuration.yaml", DEFAULT_CONFIG)
    w(f"{cfg}/.storage/lovelace_dashboards", storage_json("lovelace_dashboards", [
        {"id": "map", "icon": "mdi:map", "title": "Map", "url_path": "map", "mode": "storage",
         "require_admin": False, "show_in_sidebar": True},
        {"id": "lovelace", "mode": "storage", "url_path": "lovelace", "title": "Overview"}]))
    w(f"{cfg}/.storage/lovelace_dashboards.corrupt.2026-10-12T03:01:02.123456+00:00", "{broken")
    w(f"{cfg}/.storage/lovelace.deez_smart_home", '{"data": {"config": {"views": ["CANARY_NOTREAD_91d"]}}}')
    w(f"{cfg}/.storage/lovelace.map", '{"data": {"config": {"strategy": {"type": "map"}}}}')
    w(f"{cfg}/.storage/repairs.issue_registry", '{"data": {"issues": ['
      '{"domain": "homeassistant", "issue_id": "storage_corruption_lovelace_dashboards_2026-10-12T03:01:02"},'
      '{"domain": "homeassistant", "issue_id": "storage_corruption_auth_2026-10-12T03:01:02"},'
      '{"domain": "hacs", "issue_id": "restart_required"}]}}')
    w(f"{cfg}/.storage/lovelace_resources", storage_json("lovelace_resources", [
        {"id": "a", "type": "module", "url": "/hacsfiles/lovelace-card-mod/card-mod.js?hacstag=12345"},
        {"id": "b", "type": "module", "url": "/hacsfiles/kiosk-mode/kiosk-mode.js"},
        {"id": "c", "type": "module", "url": CRED_RESOURCE_URL}]))
    w(f"{cfg}/.storage/input_number", storage_json("input_number", [{"id": "gas_bill_mj", "name": "Gas Bill Usage MJ"}]))
    w(f"{cfg}/.storage/person", storage_json("person", [{"id": "someone_else", "name": "X"}]))
    w(f"{cfg}/people.yaml", "- name: Raymond Du.\n  id: raymond_du\n")
    w(f"{cfg}/packages/casaray_automation.yaml", repo("packages/casaray_automation.yaml"))
    w(f"{cfg}/packages/private.yaml", "chinese_dashboard:\n  name: CANARY_PKG_e66\n")
    w(f"{cfg}/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml"))
    w(f"{cfg}/dashboards/deez_smart_home.yaml", repo("dashboards/deez_smart_home.yaml"))
    w(f"{cfg}/deez_repo/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml"))
    w(f"{cfg}/deez_repo/themes/deez_your_name.yaml", repo("themes/deez_your_name.yaml"))
    w(f"{cfg}/_recovery/casaray/configuration.yaml.pre", DEFAULT_CONFIG)
    w(f"{cfg}/_recovery/casaray/backup_slug", "ba94d3a0\n")
    for d in ("custom_components/hacs", "custom_components/webrtc", "custom_components/tapo_control",
              "www/community/lovelace-card-mod", "www/community/kiosk-mode"):
        w(f"{cfg}/{d}/x", "")
    w(f"{cfg}/www/your_name_night_sky.jpg", "jpg")
    return {"exit": 0, "expect": [
        "config folder: /homeassistant",
        "only the generated default keys          yes",
        "top-level lovelace:                      no",
        "registers casaray-v2                     no",
        "loads the themes/ folder                 yes",
        "    map                            storage",
        "    lovelace                       storage",
        "lovelace.deez_smart_home",
        "lovelace_dashboards.corrupt.2026-10-12T03:01:02.123456+00:00",
        "storage_corruption_lovelace_dashboards_2026-10-12T03:01:02",
        "    lovelace-card-mod/card-mod.js",
        "    kiosk-mode/kiosk-mode.js",
        "    x/y.js",
        "themes/ folder                           MISSING",
        "MATCHES git",
        "/casaray-v2/ links in live dashboard     292",
        "chinese_dashboard  yaml: none   storage: none",
        "gas_bill_mj        yaml: none   storage: input_number",
        "raymond_du         yaml: people.yaml   storage: none",
        "    private.yaml",
        "  pre-copy registers casaray-v2          no",
        "APPLIED marker                           MISSING",
        "backup reference file                    present (content not read)",
        "    tapo_control", "    webrtc", "    lovelace-card-mod",
        "== END (read-only; nothing was changed)"],
        "forbid": ["storage_corruption_auth", "auth.corrupt", "restart_required", "DIFFERS"]}


def fx_registered(root):
    """Registered, themed, compact JSON, a stale dashboard file, helpers in YAML."""
    cfg = f"{root}/homeassistant"
    sensitive(cfg)
    w(f"{cfg}/configuration.yaml", DEFAULT_CONFIG + BLOCK + "input_select:\n  family_location:\n    options: [a]\n")
    w(f"{cfg}/input_boolean.yaml", "chinese_dashboard:\n  name: Chinese Dashboard\n")
    w(f"{cfg}/themes/deez_your_name.yaml", repo("themes/deez_your_name.yaml"))
    w(f"{cfg}/dashboards/casaray_v2.yaml", repo("dashboards/casaray_v2.yaml") + "# drift\n")
    w(f"{cfg}/.storage/lovelace_dashboards", '{"version":1,"key":"lovelace_dashboards","data":{"items":['
      '{"id":"deez_smart_home","url_path":"deez-smart-home","mode":"storage","title":"Deez"},'
      '{"id":"map","title":"Map","mode":"storage","url_path":"map"}]}}')
    w(f"{cfg}/.storage/repairs.issue_registry", '{"data":{"issues":[{"domain":"lovelace","issue_id":"yaml_mode_deprecated"}]}}')
    w(f"{cfg}/_recovery/casaray/configuration.yaml.pre", DEFAULT_CONFIG)
    w(f"{cfg}/_recovery/casaray/APPLIED", "")
    return {"exit": 0, "expect": [
        "only the generated default keys          no (2 other top-level keys)",
        "top-level lovelace:                      yes",
        "registers casaray-v2                     yes",
        "    deez-smart-home                storage",
        "    map                            storage",
        "    yaml_mode_deprecated",
        "    deez_your_name.yaml",
        "DIFFERS from git",
        "MATCHES git",
        "chinese_dashboard  yaml: input_boolean.yaml   storage: none",
        "family_location    yaml: configuration.yaml   storage: none",
        "APPLIED marker                           present",
        "backup reference file                    MISSING"],
        "forbid": ["auth.corrupt", "storage_corruption_auth"]}


def fx_dark(root):
    """Only an empty configuration.yaml; everything else absent."""
    w(f"{root}/homeassistant/configuration.yaml", "")
    return {"exit": 0, "expect": [
        "readable and non-empty                   no",
        "lovelace_dashboards                      MISSING",
        "    none",
        "dashboards/casaray_v2.yaml               MISSING",
        "packages/ folder                         MISSING",
        "_recovery/casaray/ folder                MISSING",
        "== END (read-only; nothing was changed)"], "forbid": ["MATCHES", "DIFFERS"]}


def fx_no_config(root):
    """No config folder at all."""
    os.makedirs(f"{root}/homeassistant", exist_ok=True)
    return {"exit": 1, "expect": ["config folder not found"], "forbid": ["== 1"]}


def fx_symlinks(root):
    """Allowlisted names that are symlinks to secrets or outside the config folder."""
    cfg = f"{root}/homeassistant"
    sensitive(cfg)
    w(f"{cfg}/configuration.yaml", DEFAULT_CONFIG)
    w(f"{root}/outside/secret.txt", "raymond_du:\n CANARY_OUTSIDE_6ab\n")
    os.symlink("secrets.yaml", f"{cfg}/people.yaml")
    os.makedirs(f"{cfg}/dashboards")
    os.symlink("/outside/secret.txt", f"{cfg}/dashboards/casaray_v2.yaml")
    os.makedirs(f"{cfg}/themes")
    os.symlink("../.storage/auth", f"{cfg}/themes/deez_your_name.yaml")
    os.symlink("../outside/secret.txt", f"{cfg}/person.yaml")
    return {"exit": 0, "expect": [
        "not read (refused: symlink outside the config folder or not a regular file)",
        "raymond_du         yaml: none   storage: none",
        "/casaray-v2/ links in live dashboard     0"], "forbid": ["MATCHES", "DIFFERS"]}


def fx_addon_config(root):
    """/config exists but is the add-on's own folder (no configuration.yaml)."""
    w(f"{root}/config/options.json", '{"password": "CANARY_ADDON_f12"}')
    w(f"{root}/config/x.yaml", "chinese_dashboard: CANARY_ADDON_f12\n")
    w(f"{root}/homeassistant/configuration.yaml", DEFAULT_CONFIG)
    return {"exit": 0, "expect": ["config folder: /homeassistant", "chinese_dashboard  yaml: none   storage: none"],
            "forbid": []}


FIXTURES = [("post_loss", fx_post_loss), ("registered", fx_registered), ("dark", fx_dark),
            ("no_config", fx_no_config), ("symlinks", fx_symlinks), ("addon_config", fx_addon_config)]
TRACE = "open,openat,creat,execve,chroot,unlink,unlinkat,rename,renameat,renameat2,mkdir,mkdirat,rmdir," \
        "link,linkat,symlink,symlinkat,chmod,fchmodat,fchmod,truncate,ftruncate,utimensat,chown,fchownat"
OPEN_RE = re.compile(r'open(?:at)?\((?:AT_FDCWD, )?"([^"]*)", ([A-Z_|0-9]+)')
EXEC_RE = re.compile(r'execve\("([^"]*)"')
MUTATE_RE = re.compile(r"\b(creat|unlink|unlinkat|rename|renameat2?|mkdir|mkdirat|rmdir|link|linkat|symlink|"
                       r"symlinkat|chmod|fchmodat|fchmod|truncate|ftruncate|utimensat|chown|fchownat)\(")


def joined_trace(path):
    """Rejoin strace -f's split '<unfinished ...>' / '<... resumed>' lines."""
    lines, pending = [], {}
    with open(path) as f:
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


def tools():
    busybox = os.environ.get("BUSYBOX") or shutil.which("busybox")
    strace, chroot = shutil.which("strace"), shutil.which("chroot")
    missing = [n for n, v in (("busybox", busybox), ("strace", strace), ("chroot", chroot)) if not v]
    if os.geteuid() != 0:
        missing.append("root")
    return busybox, strace, chroot, missing


def main():
    busybox, strace, chroot, missing = tools()
    if missing:
        print(f"SKIP: needs {', '.join(missing)} (set BUSYBOX to a static BusyBox binary)")
        return 0
    roots = tempfile.mkdtemp(prefix="casaray_evidence_")
    total = 0
    try:
        for name, build in FIXTURES:
            root = make_root(roots, name, busybox)
            spec = build(root)
            trace = os.path.join(roots, f"{name}.strace")
            p = subprocess.run([strace, "-f", "-qq", "-e", f"trace={TRACE}", "-o", trace,
                                chroot, root, "/bin/sh", RUN_AS],
                               capture_output=True, text=True, env={"PATH": "/bin"})
            out, err = p.stdout, p.stderr
            events = joined_trace(trace)
            events = events[next(i for i, l in enumerate(events) if "chroot(" in l) + 1:]
            fails = []
            if p.returncode != spec["exit"]:
                fails.append(f"exit {p.returncode} != {spec['exit']}")
            if err.strip():
                fails.append(f"stderr not empty: {err.strip()[:200]}")
            fails += [f"canary leaked: {c}" for c in CANARIES if c in out or c in err]
            fails += [f"missing expected: {e!r}" for e in spec["expect"] if e not in out]
            fails += [f"forbidden text present: {t!r}" for t in spec["forbid"] if t in out]
            opened, writes, execs = set(), set(), set()
            for l in events:
                m = OPEN_RE.search(l)
                if m and not l.rstrip().endswith("ENOENT (No such file or directory)"):
                    path, flags = m.groups()
                    if "O_DIRECTORY" not in flags:
                        opened.add(path)
                    if re.search(r"O_WRONLY|O_RDWR|O_CREAT|O_TRUNC|O_APPEND", flags) and path != "/dev/null":
                        writes.add(path)
                    if DENIED_OPEN.search(path):
                        fails.append(f"denied path opened: {path} {flags}")
                if MUTATE_RE.search(l):
                    fails.append(f"mutating syscall: {l.strip()[:160]}")
                x = EXEC_RE.search(l)
                if x and l.rstrip().endswith("= 0"):
                    execs.add(x.group(1))
                    if not x.group(1).startswith("/bin/"):
                        fails.append(f"exec outside /bin: {x.group(1)}")
            # /etc/localtime: the read-only time-zone file stat opens to format %y.
            allowed = {"/dev/null", "/etc/localtime", RUN_AS} | {f"/homeassistant/{a}" for a in ALLOW}
            fails += [f"opened file not in allowlist: {f}" for f in sorted(opened - allowed)]
            if writes:
                fails.append(f"write-mode opens: {sorted(writes)}")
            total += len(fails)
            print(f"[{'PASS' if not fails else 'FAIL'}] {name:13s} exit={p.returncode} files_opened={len(opened)} "
                  f"write_opens={len(writes)} execs={','.join(sorted(execs))}")
            for f in fails:
                print("        !!", f)
    finally:
        shutil.rmtree(roots, ignore_errors=True)
    print(f"TOTAL FAILURES: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
