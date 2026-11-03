"""Tests for scripts/recovery/backup_check.html (browser-local backup copy check).

    python3 -I scripts/recovery/tests/test_backup_check.py

Builds backups in the Supervisor's layout (outer tar, backup.json last, inner
gzip archives; /config stored under data/) and runs the page's own code:

  1. in Node, by evaluating the page's <script id="core"> unchanged;
  2. in real headless Chromium through Playwright, by opening the page from disk,
     choosing the file, pressing the buttons and saving the payload download.

Fixtures cover: a plain copy; a copy whose inner archives are opaque bytes with
backup.json protected (it stands in for an encrypted copy: SecureTar itself is
not used here); a copy cut short; one missing a listed archive; one with
corrupt gzip data; one with a bad outer header checksum; one with path
traversal, a symlink, a hard link and a device inside the two folders; one
written in GNU tar format with long names; and one whose backup.json
contradicts its contents. Canary secrets sit in secrets.yaml, .storage and a
config entry; none may reach the summary or the payload.

What this does NOT establish: behaviour on a real Home Assistant backup, on
SecureTar-encrypted data, on browsers other than this Chromium build, or on
files larger than these fixtures. Needs Node and Playwright; prints SKIP
without them.
"""
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PAGE = os.path.join(REPO, "scripts/recovery/backup_check.html")
NODE = shutil.which("node") or "/opt/node22/bin/node"
OLD = time.time() - 9 * 86400 + 0.25
CANARIES = ["SECRET-CANARY", "AUTH-CANARY", "TOKEN-CANARY", "USERNAME-CANARY"]
FAILS, PASSES = [], [0]

LONG = "custom_components/hacs/frontend/" + "/".join(["deeply_nested_folder_%02d" % i for i in range(6)]) + "/bundle.js"
FILES = {
    "configuration.yaml": b"default_config:\nfrontend:\n  themes: !include_dir_merge_named themes\n",
    "automations.yaml": b"- id: '1'\n  alias: a\n- id: '2'\n  alias: b\n- id: '3'\n  alias: c\n",
    "scripts.yaml": b"morning:\n  alias: m\nnight:\n  alias: n\n",
    "scenes.yaml": b"[]\n",
    "secrets.yaml": b"api_key: SECRET-CANARY\n",
    "home-assistant_v2.db": os.urandom(300000),
    ".storage/auth": json.dumps({"data": {"users": [{"name": "USERNAME-CANARY"}], "x": "AUTH-CANARY"}}).encode(),
    ".storage/core.config_entries": json.dumps({"data": {"entries": [{"domain": "hacs", "data": {"token": "TOKEN-CANARY"}}]}}).encode(),
    ".storage/hacs.repositories": json.dumps({"data": {
        "1": {"category": "integration", "full_name": "hacs/integration", "installed": True, "version_installed": "2.0.5"},
        "2": {"category": "plugin", "full_name": "thomasloven/lovelace-card-mod", "installed": True, "version_installed": "4.1.0"},
        "3": {"category": "plugin", "full_name": "someone/not-installed", "installed": False}}}).encode(),
    ".storage/lovelace_resources": json.dumps({"data": {"items": [
        {"id": "1", "type": "module", "url": "/hacsfiles/lovelace-card-mod/card-mod.js?hacstag=1"},
        {"id": "2", "type": "module", "url": "/hacsfiles/lovelace-mushroom/mushroom.js?hacstag=2"}]}}).encode(),
    "custom_components/hacs/manifest.json": json.dumps({"domain": "hacs", "name": "HACS", "version": "2.0.5"}).encode(),
    "custom_components/hacs/__init__.py": b"# hacs\n",
    "custom_components/hacs/bin/tool.sh": b"#!/bin/sh\necho hi\n",
    LONG: b"// long path\n" * 50,
    "custom_components/webrtc/manifest.json": json.dumps({"domain": "webrtc", "name": "WebRTC Camera", "version": "v3.6.1"}).encode(),
    "custom_components/webrtc/www/webrtc-camera.js": b"// webrtc\n",
    "www/community/lovelace-card-mod/card-mod.js": b"// card-mod\n",
    "www/community/lovelace-mushroom/mushroom.js": os.urandom(400000),
    "www/community/näme-with-ünicode/readme.txt": b"unicode path\n",
    "www/your_name_night_sky.jpg": b"jpg",
    "themes/deez_your_name.yaml": b"CasaRay:\n  a: b\n",
}
PAYLOAD_EXPECTED = sorted(p for p in FILES if p.startswith(("custom_components/", "www/community/")))


def check(cond, msg):
    if cond:
        PASSES[0] += 1
    else:
        FAILS.append(msg)
        print("FAIL:", msg)


def inner(files, fmt=tarfile.PAX_FORMAT, extra=None, empty_dirs=("custom_components/hacs/emptydir",)):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=fmt) as tar:
        meta = b'{"version": "2026.9.2"}'
        ti = tarfile.TarInfo("./homeassistant.json")
        ti.size, ti.mtime = len(meta), OLD
        tar.addfile(ti, io.BytesIO(meta))
        root = tarfile.TarInfo("data")
        root.type, root.mtime, root.mode = tarfile.DIRTYPE, OLD, 0o755
        tar.addfile(root)
        for d in empty_dirs:
            ti = tarfile.TarInfo("data/" + d)
            ti.type, ti.mtime, ti.mode = tarfile.DIRTYPE, OLD, 0o755
            tar.addfile(ti)
        for rel, body in sorted(files.items()):
            ti = tarfile.TarInfo("data/" + rel)
            ti.size, ti.mtime = len(body), OLD
            ti.mode = 0o755 if rel.endswith(".sh") else 0o644
            tar.addfile(ti, io.BytesIO(body))
        for ti in extra or []:
            tar.addfile(ti, io.BytesIO(b"x" * ti.size) if ti.size else None)
    return gzip.compress(raw.getvalue())


def small_archive(label):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        body = label.encode()
        ti = tarfile.TarInfo("./" + label + ".txt")
        ti.size, ti.mtime = len(body), OLD
        tar.addfile(ti, io.BytesIO(body))
    return gzip.compress(raw.getvalue())


def outer(members, protected=False, folders=("share", "addons/local"), apps=("a0d7b954_vscode",)):
    meta = json.dumps({"slug": "1a2b3c4d", "name": "Test backup", "date": "2026-11-01T04:45:00+11:00",
                       "type": "full", "protected": protected, "compressed": True,
                       "homeassistant": {"version": "2026.9.2", "exclude_database": False},
                       "folders": list(folders), "addons": [{"slug": a, "name": a, "version": "1"} for a in apps],
                       "docker": {"registries": {"x": {"password": "SECRET-CANARY"}}}}).encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, body in list(members) + [("./backup.json", meta)]:
            ti = tarfile.TarInfo(name)
            ti.size, ti.mtime = len(body), int(OLD)
            tar.addfile(ti, io.BytesIO(body))
    return raw.getvalue()


def standard_members(ha_bytes):
    return [("./homeassistant.tar.gz", ha_bytes), ("./share.tar.gz", small_archive("share")),
            ("./addons_local.tar.gz", small_archive("local")), ("./a0d7b954_vscode.tar.gz", small_archive("vscode"))]


def unsafe_extra():
    out = []
    t = tarfile.TarInfo("data/custom_components/evil/../../secrets_copy.yaml")
    t.size, t.mtime = 5, OLD
    out.append(t)
    t = tarfile.TarInfo("data/custom_components/hacs/link")
    t.type, t.linkname, t.mtime = tarfile.SYMTYPE, "/config/.storage/auth", OLD
    out.append(t)
    t = tarfile.TarInfo("data/www/community/lovelace-card-mod/hard")
    t.type, t.linkname, t.mtime = tarfile.LNKTYPE, "data/secrets.yaml", OLD
    out.append(t)
    t = tarfile.TarInfo("data/custom_components/hacs/dev")
    t.type, t.devmajor, t.devminor, t.mtime = tarfile.CHRTYPE, 1, 3, OLD
    out.append(t)
    return out


def build(folder):
    ha = inner(FILES)
    plain = outer(standard_members(ha))
    fx = {"plain": plain}
    opaque = [(n, b"SIMULATED-OPAQUE" + os.urandom(len(b) + 32)) for n, b in standard_members(ha)]
    fx["encrypted"] = outer(opaque, protected=True)
    fx["truncated"] = plain[: len(plain) // 2]
    fx["missing"] = outer([m for m in standard_members(ha) if m[0] != "./share.tar.gz"])
    bad = bytearray(ha)
    mid = len(bad) // 2
    for i in range(mid, mid + 64):
        bad[i] ^= 0x5A
    fx["corrupt"] = outer(standard_members(bytes(bad)))
    hdr = bytearray(plain)
    hdr[10] ^= 0x01
    fx["badheader"] = bytes(hdr)
    fx["unsafe"] = outer(standard_members(inner(FILES, extra=unsafe_extra())))
    fx["gnu"] = outer(standard_members(inner(FILES, fmt=tarfile.GNU_FORMAT)))
    fx["inconsistent"] = outer(standard_members(ha), protected=True)
    paths = {}
    for name, body in fx.items():
        d = os.path.join(folder, name)
        os.makedirs(d)
        paths[name] = os.path.join(d, name + ".tar")
        with open(paths[name], "wb") as handle:
            handle.write(body)
    return paths


NODE_RUNNER = r"""
const fs = require("fs"), vm = require("vm"), path = require("path"), crypto = require("crypto");
const html = fs.readFileSync(process.argv[2], "utf8");
const core = html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
vm.runInThisContext(core);
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
  const out = {};
  for (const job of jobs) {
    const blob = await fs.openAsBlob(job.path);
    const file = { name: path.basename(job.path), size: blob.size, stream: () => blob.stream() };
    const rep = await BackupCheck.analyse(file);
    const r = { verdict: rep.verdict, summary: BackupCheck.summary(rep), sha256: rep.sha256, archives: rep.archives,
                cc: rep.ha ? Object.fromEntries(Object.entries(rep.ha.cc).map(([k, v]) => [k, v.manifest])) : null,
                community: rep.ha ? Object.keys(rep.ha.community).sort() : null,
                unsafe: rep.ha ? rep.ha.unsafe : null,
                payloadPaths: rep.ha ? rep.ha.payload.map((p) => p.path).sort() : null };
    if (rep.verdict.payloadOk) {
      const { parts, manifest } = BackupCheck.buildPayload(rep, 1700000000);
      fs.writeFileSync(job.payload, Buffer.concat(parts.map((p) => Buffer.from(p.buffer, p.byteOffset, p.byteLength))));
      r.manifestFiles = manifest.files.length;
    }
    out[job.id] = r;
  }
  const vec = [];
  for (const n of [0, 1, 55, 56, 63, 64, 65, 119, 120, 128, 1000003]) {
    const d = crypto.randomBytes(n);
    const whole = new BackupCheck.Sha256().update(new Uint8Array(d)).hex();
    const h = new BackupCheck.Sha256();
    for (let i = 0; i < n; i += 37) h.update(new Uint8Array(d.subarray(i, Math.min(n, i + 37))));
    const want = crypto.createHash("sha256").update(d).digest("hex");
    vec.push([n, whole === want, h.hex() === want]);
  }
  out.sha = vec;
  process.stdout.write(JSON.stringify(out));
})().catch((e) => { console.error(String(e && e.stack || e)); process.exit(1); });
"""

BROWSER_RUNNER = r"""
const { chromium } = require("playwright");
const [page_path, plain, enc, saveTo] = process.argv.slice(2);
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ acceptDownloads: true });
  const page = await ctx.newPage();
  const requests = [], errors = [];
  page.on("request", (r) => requests.push(r.url()));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto("file://" + page_path);
  const wait = async (name) => page.waitForFunction((n) => document.getElementById("summary").value.includes(n), name,
                                                    { timeout: 120000 });
  await page.setInputFiles("#file", plain);
  await page.click("#run");
  await wait("plain.tar");
  const summaryPlain = await page.inputValue("#summary");
  const payloadShown = await page.isVisible("#payloadBox");
  const careShown = (await page.textContent("#facts")).includes("Handle with care");
  const [download] = await Promise.all([page.waitForEvent("download"), page.click("#save")]);
  await download.saveAs(saveTo);
  await page.setInputFiles("#file", enc);
  await page.click("#run");
  await wait("encrypted.tar");
  const summaryEnc = await page.inputValue("#summary");
  const payloadShownEnc = await page.isVisible("#payloadBox");
  await browser.close();
  process.stdout.write(JSON.stringify({ summaryPlain, payloadShown, careShown, summaryEnc, payloadShownEnc,
                                        requests, errors, download: download.suggestedFilename() }));
})().catch((e) => { console.error(String(e && e.stack || e)); process.exit(1); });
"""


def verify_payload(path, label):
    with tarfile.open(path, "r:") as tar:
        names = tar.getnames()
        check(names[0] == "casaray_payload_manifest.json", "%s: manifest comes first" % label)
        manifest = json.load(tar.extractfile("casaray_payload_manifest.json"))
        files = sorted(m.name for m in tar.getmembers() if m.isfile() and m.name != "casaray_payload_manifest.json")
        check(files == PAYLOAD_EXPECTED, "%s: payload holds exactly the two folders' files (%s)" % (label, files[:3]))
        check(all(n == "casaray_payload_manifest.json" or n.startswith(("custom_components", "www/community"))
                  for n in names), "%s: nothing outside the two roots" % label)
        check(not any(m.issym() or m.islnk() or m.isdev() for m in tar.getmembers()), "%s: no links or devices" % label)
        byname = {f["path"]: f for f in manifest["files"]}
        ok = all(byname[p]["sha256"] == hashlib.sha256(FILES[p]).hexdigest() and byname[p]["size"] == len(FILES[p])
                 for p in PAYLOAD_EXPECTED)
        check(ok and len(byname) == len(PAYLOAD_EXPECTED), "%s: manifest sizes and SHA-256 match the source" % label)
        ok = all(tar.extractfile(p).read() == FILES[p] for p in PAYLOAD_EXPECTED)
        check(ok, "%s: payload file contents match the source" % label)
        check(tar.getmember("custom_components/hacs/bin/tool.sh").mode & 0o111 and
              byname["custom_components/hacs/bin/tool.sh"]["mode"] == "0755", "%s: executable bit kept" % label)
        check(LONG in names, "%s: long path preserved" % label)
        check("custom_components/hacs/emptydir" in manifest["dirs"], "%s: empty folder recorded" % label)
        check("www" not in manifest["dirs"], "%s: www itself is not a payload folder" % label)
        check(manifest["source"]["copy"] == "not encrypted" and manifest["source"]["ha_version"] == "2026.9.2",
              "%s: manifest records the source" % label)
        raw = open(path, "rb").read()
        check(not [c for c in CANARIES if c.encode() in raw], "%s: no canary in the payload" % label)


def main():
    if not os.path.exists(NODE):
        print("SKIP: node not available")
        return 0
    data = tempfile.mkdtemp(prefix="bc_data_")
    work = tempfile.mkdtemp(prefix="bc_work_")
    try:
        paths = build(data)
        jobs = [{"id": k, "path": v, "payload": os.path.join(work, k + "_payload.tar")} for k, v in paths.items()]
        with open(os.path.join(work, "jobs.json"), "w") as handle:
            json.dump(jobs, handle)
        runner = os.path.join(work, "runner.js")
        with open(runner, "w") as handle:
            handle.write(NODE_RUNNER)
        proc = subprocess.run([NODE, runner, PAGE, os.path.join(work, "jobs.json")], capture_output=True, text=True,
                              timeout=600, cwd=work)
        check(proc.returncode == 0, "node runner exits 0: %s" % proc.stderr[-400:])
        res = json.loads(proc.stdout or "{}")

        for n, whole, chunked in res.get("sha", []):
            check(whole and chunked, "SHA-256 matches hashlib for %d bytes (whole and chunked)" % n)

        p = res["plain"]
        v = p["verdict"]
        check(v["complete"] and v["encryption"] == "not encrypted", "plain: complete and not encrypted %s" % v)
        check(p["sha256"] == hashlib.sha256(open(paths["plain"], "rb").read()).hexdigest(), "plain: file SHA-256 matches")
        check(p["cc"]["hacs"]["version"] == "2.0.5" and p["cc"]["webrtc"]["version"] == "v3.6.1", "plain: manifests read")
        check(p["community"] == sorted(["lovelace-card-mod", "lovelace-mushroom", "näme-with-ünicode"]),
              "plain: community folders, unicode name included")
        check(v["payloadOk"] and p["payloadPaths"] == PAYLOAD_EXPECTED, "plain: payload offered with exactly the files")
        s = p["summary"]
        check("entries 3" in s and "dashboard resources recorded: 2" in s and "HACS recorded installed: 2" in s,
              "plain: key files, resources and HACS records in the summary")
        check("complete: YES" in s and "encryption: NOT ENCRYPTED" in s, "plain: verdict lines")
        check(all(a["ok"] for a in p["archives"].values()), "plain: every inner archive verified")
        check(not [c for c in CANARIES if c in json.dumps(res)], "no canary in any result or summary")
        verify_payload(os.path.join(work, "plain_payload.tar"), "node payload")

        e = res["encrypted"]["verdict"]
        check(e["encryption"] == "encrypted" and e["complete"] and not e["payloadOk"],
              "encrypted: recognised, structure complete, no payload %s" % e)
        check(res["encrypted"]["sha256"] == hashlib.sha256(open(paths["encrypted"], "rb").read()).hexdigest(),
              "encrypted: file SHA-256 matches (for comparison with the Green's copy)")
        t = res["truncated"]
        check(not t["verdict"]["complete"] and not t["verdict"]["payloadOk"] and t["sha256"] is None,
              "truncated: incomplete, no payload, no SHA-256 %s" % t["verdict"]["completeWhy"])
        m = res["missing"]["verdict"]
        check(not m["complete"] and any("share.tar.gz" in w for w in m["completeWhy"]), "missing: names the archive")
        c = res["corrupt"]["verdict"]
        check(not c["complete"] and not c["payloadOk"], "corrupt gzip: incomplete, no payload %s" % c["completeWhy"])
        b = res["badheader"]["verdict"]
        check(not b["complete"] and any("checksum" in w for w in b["completeWhy"]), "bad header: checksum named")
        u = res["unsafe"]
        check(not u["verdict"]["payloadOk"] and len(u["unsafe"]) == 4, "unsafe: 4 entries flagged, no payload %s" % u["unsafe"])
        check(not any(".." in x or x.endswith(("link", "hard", "dev")) for x in u["payloadPaths"]),
              "unsafe: none of them collected")
        g = res["gnu"]
        check(g["verdict"]["complete"] and g["payloadPaths"] == PAYLOAD_EXPECTED, "GNU format: long names read")
        i = res["inconsistent"]["verdict"]
        check(i["encryption"] == "inconsistent" and not i["payloadOk"], "inconsistent backup.json flagged")

        browser = os.path.join(work, "browser.js")
        with open(browser, "w") as handle:
            handle.write(BROWSER_RUNNER)
        saved = os.path.join(work, "browser_payload.tar")
        proc = subprocess.run([NODE, browser, PAGE, paths["plain"], paths["encrypted"], saved], capture_output=True,
                              text=True, timeout=600, cwd=work)
        check(proc.returncode == 0, "browser runner exits 0: %s" % proc.stderr[-600:])
        r = json.loads(proc.stdout or "{}")
        check("complete: YES" in r.get("summaryPlain", "") and "NOT ENCRYPTED" in r.get("summaryPlain", ""),
              "Chromium: plain copy verified")
        check(r.get("payloadShown") and r.get("careShown"), "Chromium: payload offered and care warning shown")
        check("encryption: ENCRYPTED" in r.get("summaryEnc", "") and not r.get("payloadShownEnc"),
              "Chromium: encrypted copy recognised, no payload offered (%s | payload shown %s)"
              % ([l for l in r.get("summaryEnc", "").splitlines() if l.startswith("encryption")], r.get("payloadShownEnc")))
        check(r.get("requests") == ["file://" + PAGE], "Chromium: the page made no request but its own load %s"
              % r.get("requests"))
        check(not r.get("errors"), "Chromium: no console or page errors %s" % r.get("errors"))
        check(r.get("download") == "casaray_payload.tar", "Chromium: download named casaray_payload.tar")
        if os.path.exists(saved):
            verify_payload(saved, "Chromium payload")
        else:
            check(False, "Chromium payload saved")

        with open(PAGE) as handle:
            page = handle.read()
        check("default-src 'none'" in page, "page carries a Content-Security-Policy that forbids network access")
        check(not any(w in page for w in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "<img src=\"http",
                                          "src=\"http", "href=\"http")), "page source has no network call")
    finally:
        shutil.rmtree(data, ignore_errors=True)
        shutil.rmtree(work, ignore_errors=True)
    print("%d passed, %d failed" % (PASSES[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
