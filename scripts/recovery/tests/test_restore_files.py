"""Tests for scripts/recovery/restore_files.py (selective restore of two folders).

    python3 -I scripts/recovery/tests/test_restore_files.py

A simulated Green is built in a temporary folder: /config without
custom_components or www/community (and with canaries in secrets.yaml, .storage
and the login store), an empty /share, and sources in /backup:

  * backups in the Supervisor's layout: plain; with opaque (encrypted-style)
    archives; cut short; with a wrong gzip CRC; with path traversal, a symlink,
    a hard link, a device, a duplicate entry and a file in a folder's way; one
    without custom_components/hacs;
  * payloads: one produced by backup_check.html's own code in Node, and
    Python-made ones that are tampered, carry an unlisted file, lack a listed
    file, or hold a file outside the two folders.

Every command runs under strace, and the test fails on any write-class system
call outside the paths that step is allowed to touch. Snapshots prove nothing
else in /config changed, hashes prove the protected files did not, and every
output is scanned for the canaries.

What this establishes is limited to the paths and conditions exercised here. It
does not establish behaviour on the real Green, its filesystem, a real backup,
or Python versions other than the one running this test. Needs strace; Node for
the browser-payload case (skipped without it).
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
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TOOL = os.path.join(REPO, "scripts/recovery/restore_files.py")
PAGE = os.path.join(REPO, "scripts/recovery/backup_check.html")
NODE = shutil.which("node") or "/opt/node22/bin/node"
OLD = time.time() - 9 * 86400
CANARIES = ["SECRET-CANARY", "AUTH-CANARY", "HASH-CANARY", "TOKEN-CANARY"]
FAILS, PASSES = [], [0]

TREE = {
    "custom_components/hacs/manifest.json": json.dumps({"domain": "hacs", "version": "2.0.5"}).encode(),
    "custom_components/hacs/__init__.py": b"# hacs\n",
    "custom_components/hacs/bin/tool.sh": b"#!/bin/sh\n",
    "custom_components/hacs/frontend/" + "/".join("level_%02d_folder_name" % i for i in range(6)) + "/x.js": b"x" * 900,
    "custom_components/webrtc/manifest.json": json.dumps({"domain": "webrtc", "version": "v3.6.1"}).encode(),
    "custom_components/webrtc/www/webrtc-camera.js": os.urandom(250000),
    "www/community/lovelace-card-mod/card-mod.js": b"// card-mod\n",
    "www/community/lovelace-mushroom/mushroom.js": os.urandom(300000),
}
OTHER = {
    "configuration.yaml": b"default_config:\n",
    "automations.yaml": b"- id: '1'\n  alias: a\n",
    "secrets.yaml": b"k: SECRET-CANARY\n",
    ".storage/auth": b'{"data": {"t": "AUTH-CANARY"}}',
    ".storage/core.config_entries": b'{"data": {"entries": [{"domain": "hacs", "data": {"token": "TOKEN-CANARY"}}]}}',
    "home-assistant_v2.db": os.urandom(200000),
    "www/your_name_night_sky.jpg": b"jpg",
}


def check(cond, msg):
    if cond:
        PASSES[0] += 1
    else:
        FAILS.append(msg)
        print("FAIL:", msg)


def ti(name, size=0, kind=tarfile.REGTYPE, mode=0o644, link=""):
    t = tarfile.TarInfo(name)
    t.size, t.type, t.mode, t.mtime, t.linkname = size, kind, mode, OLD, link
    return t


def inner(files, extra=(), drop=()):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        tar.addfile(ti("./homeassistant.json", 2), io.BytesIO(b"{}"))
        tar.addfile(ti("data", kind=tarfile.DIRTYPE, mode=0o755))
        tar.addfile(ti("data/custom_components/hacs/__pycache__", kind=tarfile.DIRTYPE, mode=0o755))
        for rel, body in sorted(files.items()):
            if rel in drop:
                continue
            tar.addfile(ti("data/" + rel, len(body), mode=0o755 if rel.endswith(".sh") else 0o644), io.BytesIO(body))
        for t, body in extra:
            tar.addfile(t, io.BytesIO(body) if body is not None else None)
    return gzip.compress(raw.getvalue())


def outer(ha, protected=False):
    meta = json.dumps({"slug": "1a2b3c4d", "name": "x", "date": "2026-11-01T04:45:00+11:00", "type": "full",
                       "protected": protected, "compressed": True,
                       "homeassistant": {"version": "2026.9.2"}, "folders": [], "addons": [],
                       "docker": {"registries": {"r": {"password": "SECRET-CANARY"}}}}).encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, body in (("./homeassistant.tar.gz", ha), ("./backup.json", meta)):
            tar.addfile(ti(name, len(body)), io.BytesIO(body))
    return raw.getvalue()


def payload(files, manifest_files=None, first="manifest", extra=()):
    listed = manifest_files if manifest_files is not None else [
        {"path": p, "size": len(b), "sha256": hashlib.sha256(b).hexdigest(), "mode": "0644"} for p, b in files.items()]
    manifest = json.dumps({"format": "casaray-payload/1", "tool": "test", "roots": ["custom_components", "www/community"],
                           "source": {"backup_date": "2026-11-01", "ha_version": "2026.9.2"}, "dirs": [],
                           "files": listed}).encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        entries = [("casaray_payload_manifest.json", manifest)] + sorted(files.items()) + list(extra)
        if first != "manifest":
            entries = entries[1:] + entries[:1]
        for name, body in entries:
            tar.addfile(ti(name, len(body)), io.BytesIO(body))
    return raw.getvalue()


def write(path, data, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    if mtime:
        os.utime(path, (mtime, mtime))


def build_world(root):
    cfg = root + "/config"
    for rel, body in [("configuration.yaml", b"default_config:\n"), ("automations.yaml", b"[]\n"),
                      ("scripts.yaml", b""), ("scenes.yaml", b""), ("secrets.yaml", b"k: SECRET-CANARY\n"),
                      (".HA_VERSION", b"2026.9.2"), (".storage/auth", b'{"t": "AUTH-CANARY"}'),
                      (".storage/auth_provider.homeassistant", b'{"h": "HASH-CANARY"}'),
                      (".storage/onboarding", b"{}"), (".storage/lovelace_dashboards", b"{}"),
                      (".storage/lovelace_resources", b'{"data": {"items": []}}'),
                      (".storage/core.config_entries", b'{"t": "TOKEN-CANARY"}'),
                      ("themes/casaray_v3.yaml", b"CasaRay V3:\n  a: b\n"), ("www/existing.txt", b"keep me")]:
        write(os.path.join(cfg, rel), body, OLD)
    os.makedirs(root + "/share", exist_ok=True)
    src = root + "/backup"
    os.makedirs(src, exist_ok=True)
    allfiles = dict(TREE, **OTHER)
    plain = outer(inner(allfiles))
    sources = {"plain": plain}
    sources["opaque"] = outer(b"SIMULATED-OPAQUE" + os.urandom(5000), protected=True)
    sources["truncated"] = plain[: len(plain) * 2 // 3]
    ha = bytearray(inner(allfiles))
    ha[-8] ^= 0xFF
    sources["badcrc"] = outer(bytes(ha))
    sources["unsafe"] = outer(inner(allfiles, extra=[
        (ti("data/custom_components/evil/../../secrets_copy.yaml", 4), b"evil"),
        (ti("data/custom_components/hacs/link", kind=tarfile.SYMTYPE, link="/config/.storage/auth"), None),
        (ti("data/www/community/lovelace-card-mod/hard", kind=tarfile.LNKTYPE, link="data/secrets.yaml"), None),
        (ti("data/custom_components/hacs/dev", kind=tarfile.CHRTYPE), None),
    ]))
    sources["duplicate"] = outer(inner(allfiles, extra=[(ti("data/custom_components/hacs/__init__.py", 3), b"dup")]))
    sources["inway"] = outer(inner(allfiles, extra=[(ti("data/custom_components/blocker", 1), b"f"),
                                                    (ti("data/custom_components/blocker/inside.py", 1), b"g")]))
    sources["nohacs"] = outer(inner(allfiles, drop=[p for p in TREE if p.startswith("custom_components/hacs/")]))
    body = TREE["custom_components/hacs/__init__.py"]
    good = {p: b for p, b in TREE.items()}
    sources["payload_py"] = payload(good)
    tampered = [{"path": p, "size": len(b), "sha256": hashlib.sha256(b).hexdigest()} for p, b in good.items()]
    tampered[0] = dict(tampered[0], sha256="0" * 64)
    sources["payload_tampered"] = payload(good, manifest_files=tampered)
    sources["payload_unlisted"] = payload(good, extra=[("custom_components/hacs/unlisted.py", b"u")])
    listed = [{"path": p, "size": len(b), "sha256": hashlib.sha256(b).hexdigest()} for p, b in good.items()]
    listed.append({"path": "custom_components/hacs/missing.py", "size": 1, "sha256": "1" * 64})
    sources["payload_missing"] = payload(good, manifest_files=listed)
    sources["payload_outside"] = payload(good, extra=[(".storage/auth", b"AUTH-CANARY")])
    sources["payload_order"] = payload(good, first="last")
    paths = {}
    for name, data in sources.items():
        paths[name] = os.path.join(src, name + ".tar")
        write(paths[name], data)
    return paths


TRACED = "trace=openat,open,creat,unlink,unlinkat,rename,renameat,renameat2,mkdir,mkdirat,rmdir,utimensat,truncate"
WRITE_FLAGS = re.compile(r"O_(WRONLY|RDWR|CREAT|TRUNC|APPEND)")


def write_targets(trace_text):
    paths = []
    for line in trace_text.splitlines():
        m = re.match(r"(?:\d+\s+)?(\w+)\((.*)", line)
        if not m or "= -1" in line:
            continue
        call, rest = m.groups()
        quoted = re.findall(r'"((?:[^"\\]|\\.)*)"', rest)
        if call in ("openat", "open", "creat"):
            if call != "creat" and not WRITE_FLAGS.search(rest):
                continue
            if quoted:
                paths.append((call, quoted[0]))
        elif quoted:
            for q in quoted:
                paths.append((call, q))
    return paths


def run(root, args, stdin="", env_extra=None, traces=None):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
           "CASARAY_RESTORE_ROOT": root, "CASARAY_RESTORE_TESTING": "1"}
    env.update(env_extra or {})
    trace = os.path.join(traces, "t%d" % len(os.listdir(traces)))
    cmd = ["strace", "-f", "-qq", "-o", trace, "-e", TRACED, sys.executable, "-I", "-B", TOOL] + args
    proc = subprocess.run(cmd, env=env, input=stdin, capture_output=True, text=True, timeout=300)
    with open(trace) as handle:
        writes = write_targets(handle.read())
    return proc.returncode, proc.stdout + proc.stderr, writes


def outside(writes, allowed):
    bad = []
    for call, p in writes:
        if p in ("/dev/tty", "/dev/null"):
            continue
        if not any(p == a or p.startswith(a.rstrip("/") + "/") for a in allowed):
            bad.append("%s %s" % (call, p))
    return bad


def snapshot(base, skip=()):
    state = {}
    for folder, dirs, files in os.walk(base):
        rel_folder = os.path.relpath(folder, base)
        if any(rel_folder == s or rel_folder.startswith(s + "/") for s in skip):
            dirs[:] = []
            continue
        for name in dirs + files:
            rel = os.path.normpath(os.path.join(rel_folder, name))
            if any(rel == s or rel.startswith(s + "/") for s in skip):
                continue
            st = os.lstat(os.path.join(folder, name))
            # A folder's own mtime changes whenever an entry inside it is added or removed, so
            # folders are compared by type and mode; files by mtime, size and mode.
            state[rel] = ("dir", st.st_mode) if os.path.isdir(os.path.join(folder, name)) and \
                not os.path.islink(os.path.join(folder, name)) else (st.st_mtime_ns, st.st_size, st.st_mode)
    return state


def protected_hashes(cfg):
    out = {}
    for rel in ("configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml", "secrets.yaml",
                ".storage/auth", ".storage/auth_provider.homeassistant", ".storage/core.config_entries",
                "themes/casaray_v3.yaml"):
        with open(os.path.join(cfg, rel), "rb") as handle:
            out[rel] = hashlib.sha256(handle.read()).hexdigest()
    return out


def stage_dir_from(output, root):
    m = re.search(r"STAGED: (\S+)", output)
    return (root + m.group(1)) if m else None


def browser_payload(work, source, dest):
    runner = os.path.join(work, "mkpayload.js")
    with open(runner, "w") as handle:
        handle.write(r"""
const fs = require("fs"), vm = require("vm"), path = require("path");
vm.runInThisContext(fs.readFileSync(process.argv[2], "utf8").match(/<script id="core">([\s\S]*?)<\/script>/)[1]);
(async () => {
  const blob = await fs.openAsBlob(process.argv[3]);
  const rep = await BackupCheck.analyse({ name: path.basename(process.argv[3]), size: blob.size, stream: () => blob.stream() });
  if (!rep.verdict.payloadOk) { console.error(JSON.stringify(rep.verdict)); process.exit(3); }
  const { parts } = BackupCheck.buildPayload(rep, 1700000000);
  fs.writeFileSync(process.argv[4], Buffer.concat(parts.map((p) => Buffer.from(p.buffer, p.byteOffset, p.byteLength))));
})().catch((e) => { console.error(String(e)); process.exit(1); });
""")
    return subprocess.run([NODE, runner, PAGE, source, dest], capture_output=True, text=True, timeout=300, cwd=work)


def main():
    if not shutil.which("strace"):
        print("SKIP: strace not available")
        return 0
    base = tempfile.mkdtemp(prefix="rf_")
    traces = tempfile.mkdtemp(prefix="rf_trace_")
    outputs = []
    try:
        root = os.path.join(base, "green")
        os.makedirs(root)
        paths = build_world(root)
        cfg, share = root + "/config", root + "/share"
        stage_base = share + "/casaray-restore"
        pristine = snapshot(cfg)
        hashes = protected_hashes(cfg)

        # ---- plan: read-only
        rc, out, writes = run(root, ["plan", paths["plain"]], traces=traces)
        outputs.append(out)
        check(rc == 0 and "READY" in out, "plan of a plain backup is READY (rc %d)" % rc)
        check(re.search(r"custom_components\s+\d+ files .*2 folders: hacs, webrtc", out), "plan lists the integrations")
        check(re.search(r"www/community\s+\d+ files .*lovelace-card-mod, lovelace-mushroom", out), "plan lists community")
        check("skipped 1 __pycache__" in out, "plan skips __pycache__")
        check(not outside(writes, []), "plan writes nothing %s" % outside(writes, [])[:3])

        refusals = {"opaque": "encrypted", "truncated": "cut short", "badcrc": "corrupt", "nohacs": None}
        for name, word in refusals.items():
            rc, out, writes = run(root, ["plan", paths[name]], traces=traces)
            outputs.append(out)
            if name == "nohacs":
                check(rc == 0, "plan of a backup without hacs reads (stage will refuse)")
            else:
                check(rc == 3 and "REFUSED" in out and word in out, "plan refuses %s (%s)" % (name, out[-200:]))
            check(not outside(writes, []), "plan of %s writes nothing" % name)
        rc, out, _ = run(root, ["plan", paths["unsafe"]], traces=traces)
        outputs.append(out)
        check(rc == 3 and out.count(" - ") >= 4 and "unsafe path" in out and "symbolic link" in out and
              "hard link" in out and "device" in out, "plan lists traversal, symlink, hard link and device")
        rc, out, _ = run(root, ["plan", paths["duplicate"]], traces=traces)
        outputs.append(out)
        check(rc == 3 and "appears twice" in out, "plan refuses a duplicate entry")
        rc, out, _ = run(root, ["plan", paths["inway"]], traces=traces)
        outputs.append(out)
        check(rc == 3 and "in the way" in out, "plan refuses a file in a folder's way")
        rc, out, _ = run(root, ["plan", paths["plain"]], env_extra={"CASARAY_RESTORE_MAX_FILE": "100000"}, traces=traces)
        outputs.append(out)
        check(rc == 3 and "larger than" in out, "plan refuses an oversized file")
        for name, word in (("payload_tampered", "does not match"), ("payload_unlisted", "does not list"),
                           ("payload_missing", "lacks"), ("payload_outside", "outside"), ("payload_order", "first entry")):
            rc, out, _ = run(root, ["plan", paths[name]], traces=traces)
            outputs.append(out)
            check(rc == 3 and word in out, "plan refuses %s (%s)" % (name, out.strip().splitlines()[-2:]))
        rc, out, _ = run(root, ["plan", paths["payload_py"]], traces=traces)
        outputs.append(out)
        check(rc == 0 and "verified file by file" in out, "plan accepts a valid payload")
        check(run(root, ["plan", os.path.join(cfg, "configuration.yaml")], traces=traces)[0] == 2,
              "a source inside /config is refused")
        check(snapshot(cfg) == pristine, "no plan changed /config")

        # ---- stage: writes only under /share/casaray-restore
        rc, out, writes = run(root, ["stage", paths["nohacs"]], traces=traces)
        outputs.append(out)
        check(rc == 3 and "no custom_components/hacs" in out, "stage refuses a backup without hacs")
        check(not os.listdir(stage_base), "the refused staging folder was removed")
        rc, out, writes = run(root, ["stage", paths["unsafe"]], traces=traces)
        outputs.append(out)
        check(rc == 3 and not os.listdir(stage_base), "stage refuses unsafe entries and leaves nothing")
        check(not outside(writes, [share]), "refused stage wrote only under /share %s" % outside(writes, [share])[:3])
        rc, out, writes = run(root, ["stage", paths["plain"]], traces=traces)
        outputs.append(out)
        stage = stage_dir_from(out, root)
        check(rc == 0 and stage and os.path.isfile(os.path.join(stage, "stage.json")), "stage of the plain backup")
        check(not outside(writes, [stage_base]), "stage writes only under /share/casaray-restore %s"
              % outside(writes, [stage_base])[:3])
        staged = {}
        for folder, _, files in os.walk(os.path.join(stage, "tree")):
            for name in files:
                rel = os.path.relpath(os.path.join(folder, name), os.path.join(stage, "tree"))
                with open(os.path.join(folder, name), "rb") as handle:
                    staged[rel] = handle.read()
        check(staged == TREE, "staged tree is exactly the two folders' files")
        check(os.stat(os.path.join(stage, "tree/custom_components/hacs/bin/tool.sh")).st_mode & 0o777 == 0o755,
              "executable mode kept")
        check(snapshot(cfg) == pristine, "stage did not change /config")

        # ---- apply: wrong word, then a destination that exists, then for real
        rc, out, writes = run(root, ["apply", stage], stdin="apply\n", traces=traces)
        outputs.append(out)
        check(rc == 2 and "Nothing was changed" in out and snapshot(cfg) == pristine, "a wrong confirmation changes nothing")
        os.mkdir(os.path.join(cfg, "www/community"))
        rc, out, _ = run(root, ["apply", stage], stdin="APPLY\n", traces=traces)
        outputs.append(out)
        check(rc == 3 and "already exists" in out, "apply refuses when a destination exists")
        os.rmdir(os.path.join(cfg, "www/community"))
        check(snapshot(cfg) == pristine, "refused apply changed nothing")

        rc, out, writes = run(root, ["apply", stage], stdin="APPLY\n", env_extra={"CASARAY_RESTORE_FAULT": "after_first_root"},
                              traces=traces)
        outputs.append(out)
        check(rc == 5 and "Undone" in out, "a fault after the first folder is undone (rc %d)" % rc)
        check(snapshot(cfg) == pristine, "after the fault /config is exactly as before")
        applied = json.load(open(os.path.join(stage, "applied.json")))
        check(applied["state"] == "undone", "the record says undone")
        os.unlink(os.path.join(stage, "applied.json"))

        rc, out, writes = run(root, ["apply", stage], stdin="APPLY\n", env_extra={"CASARAY_RESTORE_FAULT": "touch_protected"},
                              traces=traces)
        outputs.append(out)
        check(rc == 5 and "protected files changed" in out and "configuration.yaml" in out,
              "a protected file changing during apply undoes it")
        check(not os.path.lexists(os.path.join(cfg, "custom_components")) and
              not os.path.lexists(os.path.join(cfg, "www/community")), "nothing left after that undo")
        with open(os.path.join(cfg, "configuration.yaml"), "wb") as handle:
            handle.write(b"default_config:\n")
        os.utime(os.path.join(cfg, "configuration.yaml"), (OLD, OLD))
        os.unlink(os.path.join(stage, "applied.json"))
        check(snapshot(cfg) == pristine, "test world reset")

        rc, out, writes = run(root, ["apply", stage], stdin="APPLY\n", traces=traces)
        outputs.append(out)
        check(rc == 0 and "APPLIED" in out, "apply succeeds (rc %d %s)" % (rc, out[-300:]))
        allowed = [cfg + "/custom_components", cfg + "/www/community", cfg + "/.casaray_restore_tmp_",
                   cfg + "/www/.casaray_restore_tmp_", stage]
        stray = [w for w in outside(writes, [stage]) if not any(w.split(" ", 1)[1].startswith(a) for a in allowed)]
        check(not stray, "apply writes only the two folders, its temporary names and its record %s" % stray[:3])
        live = {}
        for top in ("custom_components", "www/community"):
            for folder, _, files in os.walk(os.path.join(cfg, top)):
                for name in files:
                    p = os.path.join(folder, name)
                    with open(p, "rb") as handle:
                        live[os.path.relpath(p, cfg)] = handle.read()
        check(live == TREE, "the two folders now hold exactly the restored files")
        check(snapshot(cfg, skip=("custom_components", "www/community")) == pristine,
              "nothing else in /config changed")
        check(protected_hashes(cfg) == hashes, "protected files unchanged")
        check(not [n for n in os.listdir(cfg) + os.listdir(cfg + "/www") if n.startswith(".casaray_restore_tmp_")],
              "no temporary folder left")
        rc, out, _ = run(root, ["apply", stage], stdin="APPLY\n", traces=traces)
        outputs.append(out)
        check(rc == 3 and "already been applied" in out, "a second apply is refused")
        rc, out, writes = run(root, ["status", stage], traces=traces)
        outputs.append(out)
        check(rc == 0 and "%d unchanged, 0 changed, 0 gone" % len(TREE) in out, "status reports every file unchanged")
        check(not outside(writes, []), "status writes nothing")

        # ---- rollback after Home Assistant has written into the folders
        write(os.path.join(cfg, "custom_components/hacs/__pycache__/__init__.cpython-313.pyc"), b"pyc")
        write(os.path.join(cfg, "custom_components/webrtc/runtime_cache.json"), b"{}")
        with open(os.path.join(cfg, "www/community/lovelace-card-mod/card-mod.js"), "ab") as handle:
            handle.write(b"// edited later\n")
        rc, out, writes = run(root, ["rollback", stage], stdin="no\n", traces=traces)
        outputs.append(out)
        check(rc == 2 and os.path.isdir(os.path.join(cfg, "custom_components")), "a wrong word stops rollback")
        rc, out, writes = run(root, ["rollback", stage, "--pycache"], stdin="ROLLBACK\n", traces=traces)
        outputs.append(out)
        check(rc == 4 and "ROLLBACK INCOMPLETE" in out, "rollback keeps folders holding files it did not create")
        check(os.path.isfile(os.path.join(cfg, "custom_components/webrtc/runtime_cache.json")) and
              os.path.isfile(os.path.join(cfg, "www/community/lovelace-card-mod/card-mod.js")),
              "a foreign file and a changed file are kept")
        check(not os.path.exists(os.path.join(cfg, "custom_components/hacs")), "unchanged restored files are removed")
        check(not os.path.exists(os.path.join(cfg, "custom_components/hacs/__pycache__")), "--pycache removes caches")
        check("memory-only configuration lost at a restart is NOT brought back" in out, "rollback states its limit")
        removable = [cfg + "/custom_components", cfg + "/www/community", stage]
        check(not outside(writes, removable), "rollback touches only the two folders and its record %s"
              % outside(writes, removable)[:3])
        os.unlink(os.path.join(cfg, "custom_components/webrtc/runtime_cache.json"))
        os.unlink(os.path.join(cfg, "www/community/lovelace-card-mod/card-mod.js"))
        rc, out, _ = run(root, ["rollback", stage], stdin="ROLLBACK\n", traces=traces)
        outputs.append(out)
        check(rc == 0 and "ROLLED BACK" in out, "rollback completes once the extra files are gone (rc %d)" % rc)
        check(not os.path.lexists(os.path.join(cfg, "custom_components")) and
              not os.path.lexists(os.path.join(cfg, "www/community")), "both folders are gone")
        check(snapshot(cfg, skip=("www",)) == {k: v for k, v in pristine.items() if not k.startswith("www")} and
              os.listdir(cfg + "/www") == ["existing.txt"], "/config is back to its starting contents")
        check(protected_hashes(cfg) == hashes, "protected files still unchanged")

        # ---- the payload that backup_check.html makes, end to end
        if os.path.exists(NODE):
            made = os.path.join(base, "casaray_payload.tar")
            proc = browser_payload(base, paths["plain"], made)
            check(proc.returncode == 0 and os.path.isfile(made), "backup_check.html made a payload: %s" % proc.stderr[-300:])
            shutil.copy(made, root + "/share/casaray_payload.tar")
            rc, out, _ = run(root, ["stage", root + "/share/casaray_payload.tar"], traces=traces)
            outputs.append(out)
            stage2 = stage_dir_from(out, root)
            check(rc == 0 and stage2, "the browser payload stages (rc %d %s)" % (rc, out[-300:]))
            if stage2:
                rc, out, _ = run(root, ["apply", stage2], stdin="APPLY\n", traces=traces)
                outputs.append(out)
                check(rc == 0, "the browser payload applies")
                ok = all(open(os.path.join(cfg, p), "rb").read() == b for p, b in TREE.items())
                check(ok, "files restored from the browser payload match the source")
                rc, out, _ = run(root, ["rollback", stage2], stdin="ROLLBACK\n", traces=traces)
                outputs.append(out)
                check(rc == 0 and protected_hashes(cfg) == hashes, "and roll back cleanly")
        else:
            print("SKIP: node not available for the browser-payload case")

        joined = "\n".join(outputs)
        check(not [c for c in CANARIES if c in joined], "no canary in any output %s" % [c for c in CANARIES if c in joined])
    finally:
        shutil.rmtree(base, ignore_errors=True)
        shutil.rmtree(traces, ignore_errors=True)
    print("%d passed, %d failed" % (PASSES[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
