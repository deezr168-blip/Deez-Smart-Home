#!/usr/bin/env python3
"""CasaRay recovery: restore ONLY /config/custom_components and /config/www/community.
v1.0, 03/11/2026. Written for the Studio Code Server terminal on the Green.

    python3 -I -B restore_files.py plan SOURCE      read-only: what would be created, and every refusal
    python3 -I -B restore_files.py stage SOURCE     writes only under /share/casaray-restore/<stamp>/
    python3 -I -B restore_files.py apply STAGE      creates the two folders; you type APPLY
    python3 -I -B restore_files.py rollback STAGE   removes only what apply created; you type ROLLBACK
    python3 -I -B restore_files.py status STAGE     read-only

SOURCE is one of:
  * a Home Assistant backup .tar whose archives are NOT encrypted (an unencrypted backup,
    or a copy Home Assistant decrypted on download);
  * casaray_payload.tar, saved by backup_check.html, whose manifest is verified file by file.

What it will and will not do:
  * It reads only data/custom_components/** and data/www/community/** from a backup, plus the
    safe fields of backup.json. Nothing else in the backup is extracted or printed.
  * It refuses links, devices, absolute or ".." paths, duplicates and oversized entries, and
    it refuses an encrypted backup.
  * apply refuses if either destination exists, so nothing is overwritten. Every file is
    created exclusively (O_EXCL). The two folders are built under temporary names and renamed
    into place. apply undoes itself if anything fails, or if a protected file changes while
    it runs.
  * Never written: .storage/, any authentication file, configuration.yaml, automations.yaml,
    scripts.yaml, scenes.yaml, secrets.yaml, themes/, dashboards.
  * rollback removes only the files apply recorded, and only while they are unchanged. It
    removes a folder only once it is empty. Anything else is listed and kept.
  * It restarts, reloads, restores and downloads nothing.
"""
import gzip
import hashlib
import json
import os
import re
import stat
import sys
import tarfile
import time

VERSION = "1.0"
ROOT = os.environ.get("CASARAY_RESTORE_ROOT", "")          # test harness only: prefixes /config and /share
TESTING = bool(ROOT) and os.environ.get("CASARAY_RESTORE_TESTING") == "1"
FAULT = os.environ.get("CASARAY_RESTORE_FAULT", "") if TESTING else ""
CONFIG = ROOT + "/config"
STAGE_BASE = ROOT + "/share/casaray-restore"
ROOTS = ("custom_components", "www/community")
PROTECTED = ("configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml", "secrets.yaml")
# Files Home Assistant does not rewrite in normal running. .storage/auth is left out on
# purpose: Core rewrites it whenever a login token is refreshed, which would abort a correct
# apply. This tool never opens it either way.
PROTECTED_STORAGE = ("auth_provider.homeassistant", "onboarding", "lovelace_dashboards", "lovelace_resources")
MAX_FILE = int(os.environ.get("CASARAY_RESTORE_MAX_FILE", 512 << 20)) if TESTING else 512 << 20
MAX_TOTAL = int(os.environ.get("CASARAY_RESTORE_MAX_TOTAL", 3 << 30)) if TESTING else 3 << 30
MAX_ENTRIES = 200000
RESERVE = 256 << 20
TMP_PREFIX = ".casaray_restore_tmp_"
O_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


class Refused(Exception):
    pass


def out(*parts):
    text = " ".join(str(p) for p in parts)
    sys.stdout.write(re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "?", text) + "\n")
    sys.stdout.flush()


def _remove_own(paths):
    """Remove paths this run created, newest first: files, then folders once empty."""
    for p in reversed(paths):
        try:
            st = os.lstat(p)
        except OSError:
            continue
        if stat.S_ISDIR(st.st_mode):
            try:
                os.rmdir(p)
            except OSError:
                pass
        else:
            os.unlink(p)


def _clear_temp(temp):
    """Empty and remove a temporary folder this run created with mkdir. Everything in it was
    created by this run (exclusive creation inside a folder made a moment before)."""
    leftovers = []
    if not os.path.lexists(temp) or not is_real_dir(temp):
        return leftovers
    for folder, dirs, files in os.walk(temp, topdown=False, followlinks=False):
        for name in files:
            os.unlink(os.path.join(folder, name))
        for name in dirs:
            p = os.path.join(folder, name)
            if os.path.islink(p):
                os.unlink(p)
            else:
                try:
                    os.rmdir(p)
                except OSError:
                    leftovers.append(p)
    try:
        os.rmdir(temp)
    except OSError:
        leftovers.append(temp)
    return leftovers


def mb(n):
    return "%.1f MB" % (n / 1048576.0)


def utc(t=None):
    return time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(t if t is not None else time.time()))


def sha_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def free_bytes(path):
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


def inside(folder, base):
    """Second line of defence after check_rel: the resolved folder must sit inside base."""
    real, real_base = os.path.realpath(folder), os.path.realpath(base)
    if real != real_base and not real.startswith(real_base + os.sep):
        raise Refused("a path resolves outside %s" % os.path.basename(base))


def is_real_dir(path):
    try:
        return stat.S_ISDIR(os.lstat(path).st_mode)
    except OSError:
        return False


def confirm(word):
    prompt = "Type %s to continue, anything else to stop: " % word
    if TESTING:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        answer = sys.stdin.readline()
    else:
        try:
            with open("/dev/tty", "r+") as tty:
                tty.write(prompt)
                tty.flush()
                answer = tty.readline()
        except OSError:
            out("REFUSED: this step must be run in an interactive terminal.")
            return False
    return answer.strip() == word


# ------------------------------------------------------------------- reading a source ---
class HashingReader:
    """Wraps a binary file and hashes every byte read through it."""

    def __init__(self, handle):
        self.handle = handle
        self.digest = hashlib.sha256()
        self.count = 0

    def read(self, n=-1):
        data = self.handle.read(n)
        self.digest.update(data)
        self.count += len(data)
        return data


def check_rel(rel):
    """Return a refusal reason for an unsafe relative path, or None."""
    if not rel or "\x00" in rel or "\\" in rel or rel.startswith("/"):
        return "unsafe path"
    parts = rel.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return "unsafe path"
    if len(rel.encode("utf-8", "surrogateescape")) > 1024 or len(parts) > 32 or \
            any(len(p.encode("utf-8", "surrogateescape")) > 255 for p in parts):
        return "path too long"
    return None


def under_roots(rel):
    return any(rel == r or rel.startswith(r + "/") for r in ROOTS)


def normal(name):
    while name.startswith("./"):
        name = name[2:]
    return name.rstrip("/")


class Collector:
    """Validates every entry under the two roots; optionally writes them into a tree."""

    def __init__(self, tree=None):
        self.tree = tree
        self.files = {}
        self.dirs = set()
        self.refusals = []
        self.skipped_pycache = 0
        self.total = 0
        self.entries = 0
        self.created = []

    def refuse(self, rel, why):
        if len(self.refusals) < 200:
            self.refusals.append((rel, why))

    def add(self, rel, member, archive):
        self.entries += 1
        if self.entries > MAX_ENTRIES:
            raise Refused("more than %d entries under the two folders" % MAX_ENTRIES)
        why = check_rel(rel)
        if why:
            self.refuse(rel, why)
            return
        if "/__pycache__/" in "/" + rel + "/":
            self.skipped_pycache += 1
            return
        if rel in self.files or rel in self.dirs:
            self.refuse(rel, "appears twice")
            return
        if member.isdir():
            self.dirs.add(rel)
            if self.tree:
                self._mkdirs(rel)
            return
        if not (member.isreg() or member.type == tarfile.CONTTYPE):
            kind = ("symbolic link" if member.issym() else "hard link" if member.islnk() else
                    "device" if member.isdev() else "type %r" % member.type)
            self.refuse(rel, kind)
            return
        if member.size > MAX_FILE:
            self.refuse(rel, "larger than %s" % mb(MAX_FILE))
            return
        if self.total + member.size > MAX_TOTAL:
            raise Refused("the two folders exceed %s" % mb(MAX_TOTAL))
        self.total += member.size
        parent = rel.rsplit("/", 1)[0] if "/" in rel else ""
        for i, part in enumerate(parent.split("/") if parent else []):
            prefix = "/".join(parent.split("/")[: i + 1])
            if prefix in self.files:
                self.refuse(rel, "a file is in the way of its folder")
                return
        mode = 0o755 if member.mode & 0o111 else 0o644
        source = archive.extractfile(member)
        if self.tree is None:
            digest, size = self._hash(source)
        else:
            if free_bytes(self.tree) < member.size + RESERVE:
                raise Refused("not enough free space for staging")
            if parent:
                self._mkdirs(parent)
            digest, size = self._write(os.path.join(self.tree, rel), source, mode, member.mtime)
        if size != member.size:
            raise Refused("%s is cut short in the source" % rel)
        self.files[rel] = {"size": size, "sha256": digest, "mode": "%04o" % mode}

    def _hash(self, source):
        digest, size = hashlib.sha256(), 0
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
            size += len(block)
        return digest.hexdigest(), size

    def _mkdirs(self, rel):
        path = self.tree
        for part in rel.split("/"):
            path = os.path.join(path, part)
            if os.path.relpath(path, self.tree) not in ("www",):
                inside(path, self._root_of(path))
            if not os.path.lexists(path):
                os.mkdir(path, 0o755)
                self.created.append(path)
            elif not is_real_dir(path):
                raise Refused("a file is in the way of folder %s" % rel)

    def _root_of(self, path):
        rel = os.path.relpath(path, self.tree)
        root = next((r for r in ROOTS if rel == r or rel.startswith(r + "/")), None)
        if root is None:
            raise Refused("a path falls outside the two folders")
        return os.path.join(self.tree, root)

    def _write(self, path, source, mode, mtime):
        inside(os.path.dirname(path), self._root_of(path))
        digest, size = hashlib.sha256(), 0
        fd = os.open(path, O_FLAGS, 0o600)
        self.created.append(path)
        with os.fdopen(fd, "wb") as handle:
            for block in iter(lambda: source.read(1 << 20), b""):
                handle.write(block)
                digest.update(block)
                size += len(block)
            os.fchmod(handle.fileno(), mode)
        os.utime(path, (mtime, mtime), follow_symlinks=False)
        return digest.hexdigest(), size


def read_source(path, collector):
    """Stream SOURCE once. Returns facts about it; fills the collector."""
    facts = {"kind": None, "meta": None, "manifest": None, "size": os.path.getsize(path)}
    with open(path, "rb") as raw:
        hashing = HashingReader(raw)
        try:
            outer = tarfile.open(fileobj=hashing, mode="r|")
            first = True
            for member in outer:
                name = normal(member.name)
                if first:
                    facts["kind"] = "payload" if name == "casaray_payload_manifest.json" else "backup"
                    first = False
                if facts["kind"] == "payload":
                    _payload_member(name, member, outer, facts, collector)
                    continue
                if name == "casaray_payload_manifest.json":
                    raise Refused("the payload's first entry must be its manifest")
                if name == "backup.json" and member.isfile():
                    facts["meta"] = safe_meta(outer.extractfile(member).read(1 << 20))
                elif name in ("homeassistant.tar.gz", "homeassistant.tar") and member.isfile():
                    try:
                        source = outer.extractfile(member)
                        # GzipFile, not tarfile's own "r|gz", because only GzipFile checks the CRC
                        # and length at the end of the stream; it is drained below to force that.
                        stream = gzip.GzipFile(fileobj=source, mode="rb") if name.endswith(".gz") else source
                        inner = tarfile.open(fileobj=stream, mode="r|")
                        for item in inner:
                            rel = normal(item.name)
                            if not rel.startswith("data/"):
                                continue
                            rel = rel[5:]
                            if under_roots(rel):
                                collector.add(rel, item, inner)
                        for _ in iter(lambda: stream.read(1 << 20), b""):
                            pass
                    except (tarfile.ReadError, OSError, EOFError) as err:
                        if not collector.files and not collector.dirs:
                            raise Refused("the Home Assistant archive is not readable: it is encrypted, or not a"
                                          " backup this tool takes (%s)" % type(err).__name__) from None
                        raise Refused("the Home Assistant archive is corrupt or cut short (%s)"
                                      % type(err).__name__) from None
                    facts["inner"] = True
            for _ in iter(lambda: hashing.read(1 << 20), b""):
                pass
        except Refused:
            raise
        except (tarfile.TarError, OSError, EOFError) as err:
            raise Refused("the source is not a readable tar file (%s)" % type(err).__name__) from None
    facts["sha256"] = hashing.digest.hexdigest()
    if facts["kind"] == "backup":
        if not facts.get("inner"):
            raise Refused("the source holds no Home Assistant archive")
        if facts["meta"] and facts["meta"]["protected"]:
            raise Refused("backup.json says this backup is encrypted")
    if facts["kind"] == "payload":
        listed = {f["path"] for f in facts["manifest"]["files"]}
        missing = sorted(listed - set(collector.files))
        if missing:
            raise Refused("the payload lacks %d files its manifest lists, e.g. %s" % (len(missing), missing[0]))
    return facts


def _payload_member(name, member, archive, facts, collector):
    if name == "casaray_payload_manifest.json":
        if facts["manifest"] is not None:
            raise Refused("the payload holds two manifests")
        try:
            manifest = json.loads(archive.extractfile(member).read(64 << 20))
        except ValueError:
            raise Refused("the payload manifest is unreadable") from None
        if manifest.get("format") != "casaray-payload/1" or sorted(manifest.get("roots", [])) != sorted(ROOTS):
            raise Refused("the payload manifest is not one this tool knows")
        files = manifest.get("files")
        if not isinstance(files, list) or not all(isinstance(f, dict) and {"path", "size", "sha256"} <= set(f)
                                                  for f in files):
            raise Refused("the payload manifest has no valid file list")
        facts["manifest"] = manifest
        facts["listed"] = {f["path"]: f for f in files}
        return
    if facts["manifest"] is None:
        raise Refused("the payload's first entry must be its manifest")
    if not under_roots(name):
        raise Refused("the payload holds %s, outside the two folders" % name)
    if not member.isdir():
        listed = facts["listed"].get(name)
        if listed is None:
            raise Refused("the payload holds %s, which its manifest does not list" % name)
    collector.add(name, member, archive)
    if not member.isdir() and name in collector.files:
        got, want = collector.files[name], facts["listed"][name]
        if got["sha256"] != want["sha256"] or got["size"] != want["size"]:
            raise Refused("%s does not match the payload manifest" % name)


def safe_meta(raw):
    try:
        meta = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(meta, dict):
        return None
    ha = meta.get("homeassistant") if isinstance(meta.get("homeassistant"), dict) else {}
    return {"date": str(meta.get("date", "?"))[:32], "type": str(meta.get("type", "?"))[:10],
            "protected": meta.get("protected") is True, "ha": str(ha.get("version", "-"))[:20]}


def describe(collector):
    lines = []
    for root in ROOTS:
        names = sorted({rel[len(root) + 1:].split("/")[0] for rel in list(collector.files) + list(collector.dirs)
                        if rel.startswith(root + "/")})
        size = sum(f["size"] for rel, f in collector.files.items() if rel.startswith(root + "/"))
        count = sum(1 for rel in collector.files if rel.startswith(root + "/"))
        lines.append("  %-18s %5d files %10s | %d folders: %s" % (root, count, mb(size), len(names),
                                                                  ", ".join(names[:40]) or "none"))
    return lines


def destinations():
    rows = []
    for root in ROOTS:
        path = os.path.join(CONFIG, root)
        rows.append((root, "EXISTS" if os.path.lexists(path) else "absent"))
    return rows


# --------------------------------------------------------------------------- commands ---
def cmd_plan(source):
    out("CasaRay restore_files v%s - plan (read-only; nothing is written)" % VERSION)
    collector = Collector()
    try:
        facts = read_source(source, collector)
    except Refused as err:
        out("REFUSED:", err)
        _print_refusals(collector)
        return 3
    _print_facts(facts, collector)
    blockers = _apply_blockers(collector.total)
    for b in blockers:
        out("  apply would refuse:", b)
    out("  would create only: /config/custom_components and /config/www/community")
    ok = not collector.refusals and not blockers
    out("== END plan:", "READY (stage next)" if ok else "NOT READY")
    return 0 if ok else 3


def cmd_stage(source):
    out("CasaRay restore_files v%s - stage (writes only under %s)" % (VERSION, "/share/casaray-restore"))
    os.makedirs(STAGE_BASE, mode=0o700, exist_ok=True)
    now = time.time_ns()
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime(now / 1e9)) + "-%06d" % (now // 1000 % 1000000)
    stage = os.path.join(STAGE_BASE, stamp)
    os.mkdir(stage, 0o700)
    tree = os.path.join(stage, "tree")
    os.mkdir(tree, 0o755)
    collector = Collector(tree)
    try:
        facts = read_source(source, collector)
        if collector.refusals:
            raise Refused("%d entries were refused" % len(collector.refusals))
        if "custom_components/hacs" not in collector.dirs and \
                not any(r.startswith("custom_components/hacs/") for r in collector.files):
            raise Refused("the source holds no custom_components/hacs")
        if not any(r.startswith("www/community/") for r in collector.files):
            raise Refused("the source holds nothing under www/community")
    except Refused as err:
        _remove_own([stage, tree] + collector.created)
        out("REFUSED:", err)
        _print_refusals(collector)
        out("The partial staging folder was removed. Nothing in /config was touched.")
        return 3
    record = {"tool": "restore_files.py", "version": VERSION, "created_utc": utc(),
              "source": {"kind": facts["kind"], "name": os.path.basename(source), "size": facts["size"],
                         "sha256": facts["sha256"], "meta": facts["meta"]},
              "roots": list(ROOTS), "dirs": sorted(collector.dirs), "files": collector.files,
              "skipped_pycache": collector.skipped_pycache}
    tmp = os.path.join(stage, "stage.json.tmp")
    with open(tmp, "x") as handle:
        json.dump(record, handle, indent=1, sort_keys=True)
    os.rename(tmp, os.path.join(stage, "stage.json"))
    _print_facts(facts, collector)
    out("STAGED:", stage.replace(ROOT, "", 1) if ROOT else stage)
    out("== END stage (nothing in /config was touched; apply is a separate step)")
    return 0


def _print_facts(facts, collector):
    meta = facts.get("meta") or {}
    out("  source: %s, %d bytes, sha256 %s" % (facts["kind"], facts["size"], facts["sha256"]))
    if meta:
        out("  backup.json: date %s | type %s | HA %s | protected %s" % (meta["date"], meta["type"], meta["ha"],
                                                                      meta["protected"]))
    if facts["kind"] == "payload":
        src = facts["manifest"].get("source", {})
        out("  payload manifest: %d files, made by %s from a backup dated %s (HA %s), verified file by file" % (
            len(facts["manifest"]["files"]), str(facts["manifest"].get("tool"))[:40], str(src.get("backup_date"))[:32],
            str(src.get("ha_version"))[:20]))
    for line in describe(collector):
        out(line)
    if collector.skipped_pycache:
        out("  skipped %d __pycache__ entries (rebuilt by Python)" % collector.skipped_pycache)
    for root, state in destinations():
        out("  destination /config/%s: %s" % (root, state))
    _print_refusals(collector)


def _print_refusals(collector):
    if collector.refusals:
        out("  refused entries (%d):" % len(collector.refusals))
        for rel, why in collector.refusals[:50]:
            out("    %s - %s" % (rel[:160], why))


def _apply_blockers(total):
    blockers = []
    if not os.path.isfile(os.path.join(CONFIG, ".HA_VERSION")):
        blockers.append("/config/.HA_VERSION is missing; this is not a Home Assistant config folder")
    if not is_real_dir(os.path.join(CONFIG, "www")):
        blockers.append("/config/www is missing or not a plain folder; creating it is not part of this plan")
    for root, state in destinations():
        if state == "EXISTS":
            blockers.append("/config/%s already exists; nothing is merged or overwritten" % root)
    for parent in (CONFIG, os.path.join(CONFIG, "www")):
        if os.path.isdir(parent) and any(n.startswith(TMP_PREFIX) for n in os.listdir(parent)):
            blockers.append("a temporary folder from an earlier run is in %s; run status first" %
                            parent.replace(ROOT, "", 1))
    if os.path.isdir(CONFIG) and free_bytes(CONFIG) < total + RESERVE:
        blockers.append("not enough free space on /config")
    return blockers


def _load_stage(stage):
    path = os.path.join(stage, "stage.json")
    if not os.path.isfile(path):
        raise Refused("%s is not a completed staging folder (no stage.json)" % stage)
    with open(path) as handle:
        record = json.load(handle)
    if record.get("roots") != list(ROOTS) or not isinstance(record.get("files"), dict):
        raise Refused("stage.json is not one this tool wrote")
    tree = os.path.join(stage, "tree")
    for rel in list(record["files"]) + record["dirs"]:
        if check_rel(rel) or not under_roots(rel):
            raise Refused("stage.json lists an unsafe path")
    for rel, f in record["files"].items():
        p = os.path.join(tree, rel)
        st = os.lstat(p) if os.path.lexists(p) else None
        if not st or not stat.S_ISREG(st.st_mode) or st.st_size != f["size"] or sha_file(p) != f["sha256"]:
            raise Refused("staged file %s is missing or changed since staging" % rel)
    return record, tree


def protected_fingerprint():
    found = {}
    for name in PROTECTED:
        p = os.path.join(CONFIG, name)
        found[name] = sha_file(p) if os.path.isfile(p) else None
    for name in PROTECTED_STORAGE:
        p = os.path.join(CONFIG, ".storage", name)
        found[".storage/" + name] = sha_file(p) if os.path.isfile(p) else None
    themes = os.path.join(CONFIG, "themes")
    if os.path.isdir(themes):
        for base, _, files in os.walk(themes):
            for name in files:
                p = os.path.join(base, name)
                found[os.path.relpath(p, CONFIG)] = sha_file(p)
    return found


def _write_record(stage, applied):
    tmp = os.path.join(stage, "applied.json.tmp")
    with open(tmp, "w") as handle:
        json.dump(applied, handle, indent=1, sort_keys=True)
    os.replace(tmp, os.path.join(stage, "applied.json"))


def cmd_apply(stage):
    out("CasaRay restore_files v%s - apply" % VERSION)
    try:
        record, tree = _load_stage(stage)
    except Refused as err:
        out("REFUSED:", err)
        return 3
    if os.path.exists(os.path.join(stage, "applied.json")):
        out("REFUSED: this staging folder has already been applied; use status or rollback")
        return 3
    total = sum(f["size"] for f in record["files"].values())
    blockers = _apply_blockers(total)
    if blockers:
        for b in blockers:
            out("REFUSED:", b)
        return 3
    out("  will create /config/custom_components and /config/www/community: %d files, %s, from %s (%s)" % (
        len(record["files"]), mb(total), record["source"]["kind"], record["source"]["name"][:60]))
    out("  will not touch .storage, authentication, configuration.yaml, include files, secrets, themes, dashboards")
    if not confirm("APPLY"):
        out("Stopped. Nothing was changed.")
        return 2
    before = protected_fingerprint()
    stamp = os.path.basename(os.path.normpath(stage))
    applied = {"state": "in-progress", "started_utc": utc(), "files": {}, "dirs": [], "targets": [], "temps": []}
    _write_record(stage, applied)
    try:
        for root in ROOTS:
            parent_rel, _, leaf = root.rpartition("/")
            parent = os.path.join(CONFIG, parent_rel) if parent_rel else CONFIG
            temp = os.path.join(parent, "%s%s_%s" % (TMP_PREFIX, stamp, leaf))
            os.mkdir(temp, 0o755)
            applied["temps"].append(os.path.relpath(temp, CONFIG))
            _write_record(stage, applied)
            for rel in sorted(d for d in record["dirs"] if d.startswith(root + "/")):
                _mkdirs_under(temp, rel[len(root) + 1:], applied, os.path.relpath(temp, CONFIG))
            for rel, f in sorted(record["files"].items()):
                if not rel.startswith(root + "/"):
                    continue
                sub = rel[len(root) + 1:]
                if "/" in sub:
                    _mkdirs_under(temp, sub.rsplit("/", 1)[0], applied, os.path.relpath(temp, CONFIG))
                dest = os.path.join(temp, sub)
                inside(os.path.dirname(dest), temp)
                digest = _copy_exclusive(os.path.join(tree, rel), dest, int(f["mode"], 8))
                if digest != f["sha256"]:
                    raise Refused("copy of %s does not match the staged file" % rel)
                applied["files"][rel] = f["sha256"]
            _write_record(stage, applied)
            target = os.path.join(CONFIG, root)
            if os.path.lexists(target):
                raise Refused("/config/%s appeared while apply ran" % root)
            os.rename(temp, target)
            applied["temps"].remove(os.path.relpath(temp, CONFIG))
            applied["targets"].append(root)
            applied["dirs"] = [d.replace(os.path.relpath(temp, CONFIG), root, 1) for d in applied["dirs"]]
            _write_record(stage, applied)
            if FAULT == "after_first_root":
                raise RuntimeError("test fault after the first folder")
            if FAULT == "touch_protected" and root == ROOTS[0]:
                with open(os.path.join(CONFIG, "configuration.yaml"), "a") as handle:
                    handle.write("# changed by the test harness\n")
        problems = _verify_created(applied)
        if problems:
            raise Refused("verification failed: %s" % problems[0])
        after = protected_fingerprint()
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if changed:
            raise Refused("protected files changed while apply ran: %s" % ", ".join(changed))
    except BaseException as err:  # noqa: BLE001 - every failure is undone, then reported
        reason = str(err) if isinstance(err, Refused) else "%s: %s" % (type(err).__name__, err)
        leftovers = _undo(applied)
        applied["state"] = "undone" if not leftovers else "undo-incomplete"
        applied["error"] = reason
        applied["leftovers"] = leftovers
        applied["ended_utc"] = utc()
        _write_record(stage, applied)
        out("FAILED:", reason)
        if leftovers:
            out("UNDO INCOMPLETE. Still present (created by this run):")
            for p in leftovers[:40]:
                out("  ", p)
            return 6
        out("Undone: everything this run created was removed. /config is as it was before apply.")
        return 5
    applied["state"] = "applied"
    applied["ended_utc"] = utc()
    _write_record(stage, applied)
    out("APPLIED: created /config/custom_components and /config/www/community (%d files)." % len(applied["files"]))
    out("Protected files unchanged: yes. Nothing is loaded until Home Assistant Core restarts; that restart is a"
        " separate decision.")
    return 0


def _mkdirs_under(base, rel, applied, base_rel):
    path = base
    for part in rel.split("/"):
        path = os.path.join(path, part)
        if not os.path.lexists(path):
            os.mkdir(path, 0o755)
            applied["dirs"].append(os.path.relpath(path, CONFIG))
        elif not is_real_dir(path):
            raise Refused("something other than a folder is at %s" % os.path.relpath(path, CONFIG))


def _copy_exclusive(src, dest, mode):
    digest = hashlib.sha256()
    fd = os.open(dest, O_FLAGS, 0o600)
    with os.fdopen(fd, "wb") as handle, open(src, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            handle.write(block)
            digest.update(block)
        os.fchmod(handle.fileno(), mode)
    st = os.stat(src)
    os.utime(dest, (st.st_mtime, st.st_mtime), follow_symlinks=False)
    return digest.hexdigest()


def _created_path(rel, applied):
    root = next(r for r in ROOTS if rel.startswith(r + "/"))
    if root in applied["targets"]:
        return os.path.join(CONFIG, rel)
    parent_rel, _, leaf = root.rpartition("/")
    temp = next((t for t in applied["temps"] if t.endswith("_" + leaf) and
                 (os.path.dirname(t) == parent_rel)), None)
    return os.path.join(CONFIG, temp, rel[len(root) + 1:]) if temp else None


def _verify_created(applied):
    problems = []
    for rel, digest in applied["files"].items():
        p = _created_path(rel, applied)
        if not p or not os.path.isfile(p) or os.path.islink(p) or sha_file(p) != digest:
            problems.append(rel)
    for root in applied["targets"]:
        listed = {r for r in applied["files"] if r.startswith(root + "/")}
        for base, dirs, files in os.walk(os.path.join(CONFIG, root)):
            for name in files:
                rel = os.path.relpath(os.path.join(base, name), CONFIG)
                if rel not in listed:
                    problems.append("unexpected %s" % rel)
    return problems


def _undo(applied):
    """Remove what this apply created. Returns what could not be removed.

    Temporary folders are emptied whole (everything in them is this run's). In a folder that
    was already renamed into place, only files whose content still matches the record are
    removed, and a folder only once empty."""
    leftovers = []
    for temp in list(applied["temps"]):
        leftovers += [os.path.relpath(p, CONFIG) for p in _clear_temp(os.path.join(CONFIG, temp))]
    for root in applied["targets"]:
        for rel, digest in sorted(applied["files"].items(), reverse=True):
            if not rel.startswith(root + "/"):
                continue
            p = os.path.join(CONFIG, rel)
            if os.path.lexists(p):
                if os.path.isfile(p) and not os.path.islink(p) and sha_file(p) == digest:
                    os.unlink(p)
                else:
                    leftovers.append(rel)
        base = os.path.join(CONFIG, root)
        if os.path.lexists(base):
            for folder, dirs, files in os.walk(base, topdown=False, followlinks=False):
                for name in files:
                    rel = os.path.relpath(os.path.join(folder, name), CONFIG)
                    if rel not in leftovers:
                        leftovers.append(rel)
                try:
                    os.rmdir(folder)
                except OSError:
                    pass
    applied["targets"] = [r for r in applied["targets"] if os.path.lexists(os.path.join(CONFIG, r))]
    applied["temps"] = [t for t in applied["temps"] if os.path.lexists(os.path.join(CONFIG, t))]
    return leftovers


def cmd_rollback(stage, pycache=False):
    out("CasaRay restore_files v%s - rollback" % VERSION)
    path = os.path.join(stage, "applied.json")
    if not os.path.isfile(path):
        out("REFUSED: nothing was applied from this staging folder")
        return 3
    with open(path) as handle:
        applied = json.load(handle)
    if applied.get("state") not in ("applied", "in-progress", "undo-incomplete", "rollback-incomplete"):
        out("REFUSED: this run is recorded as %s; there is nothing to roll back" % applied.get("state"))
        return 3
    out("  removes only the %d files this apply created, each only while unchanged, then their folders if empty"
        % len(applied["files"]))
    if pycache:
        out("  also removes __pycache__ folders inside those folders that hold only .pyc files")
    out("  memory-only configuration lost at a restart is NOT brought back by this")
    if not confirm("ROLLBACK"):
        out("Stopped. Nothing was changed.")
        return 2
    kept, removed, changed = [], 0, set()
    for temp in list(applied["temps"]):
        for p in _clear_temp(os.path.join(CONFIG, temp)):
            kept.append(os.path.relpath(p, CONFIG) + " (could not be removed)")
    for rel, digest in sorted(applied["files"].items(), reverse=True):
        if not any(rel.startswith(r + "/") for r in applied["targets"]):
            continue
        p = os.path.join(CONFIG, rel)
        if not os.path.lexists(p):
            continue
        if os.path.isfile(p) and not os.path.islink(p) and sha_file(p) == digest:
            os.unlink(p)
            removed += 1
        else:
            kept.append(rel + " (changed since apply; kept)")
            changed.add(rel)
    bases = [os.path.join(CONFIG, r) for r in applied["targets"]]
    for base in bases:
        if not os.path.lexists(base):
            continue
        for folder, dirs, files in os.walk(base, topdown=False, followlinks=False):
            if pycache and os.path.basename(folder) == "__pycache__" and files and \
                    all(f.endswith(".pyc") for f in files) and not dirs:
                for name in files:
                    os.unlink(os.path.join(folder, name))
                    out("  removed cache", os.path.relpath(os.path.join(folder, name), CONFIG))
                files = []
            for name in files:
                rel = os.path.relpath(os.path.join(folder, name), CONFIG)
                if rel not in changed:
                    kept.append(rel + " (not created by apply; kept)")
            try:
                os.rmdir(folder)
            except OSError:
                pass
    applied["targets"] = [r for r in applied["targets"] if os.path.lexists(os.path.join(CONFIG, r))]
    applied["temps"] = [t for t in applied["temps"] if os.path.lexists(os.path.join(CONFIG, t))]
    applied["state"] = "rolled-back" if not (applied["targets"] or applied["temps"]) else "rollback-incomplete"
    applied["rolled_back_utc"] = utc()
    applied["kept"] = kept
    _write_record(stage, applied)
    out("Removed %d files." % removed)
    for k in kept[:60]:
        out("  kept:", k)
    if applied["state"] == "rolled-back":
        out("ROLLED BACK: both folders are gone. A restart is needed before Home Assistant stops using code it"
            " already loaded; that restart is a separate decision.")
        return 0
    out("ROLLBACK INCOMPLETE: the folders above still exist because of the kept entries.")
    return 4


def cmd_status(stage):
    out("CasaRay restore_files v%s - status (read-only)" % VERSION)
    try:
        record, tree = _load_stage(stage)
        out("  staging folder: complete, %d files, every one matches stage.json" % len(record["files"]))
    except Refused as err:
        out("  staging folder:", err)
        record = None
    path = os.path.join(stage, "applied.json")
    if not os.path.isfile(path):
        out("  apply: not run")
    else:
        with open(path) as handle:
            applied = json.load(handle)
        out("  apply: %s (started %s)" % (applied.get("state"), applied.get("started_utc")))
        same = changed = missing = 0
        for rel, digest in applied.get("files", {}).items():
            p = _created_path(rel, applied)
            if not p or not os.path.lexists(p):
                missing += 1
            elif os.path.isfile(p) and sha_file(p) == digest:
                same += 1
            else:
                changed += 1
        out("  files created by apply: %d unchanged, %d changed, %d gone" % (same, changed, missing))
        extra = []
        for root in applied.get("targets", []):
            for base, dirs, files in os.walk(os.path.join(CONFIG, root)):
                for name in files:
                    rel = os.path.relpath(os.path.join(base, name), CONFIG)
                    if rel not in applied["files"]:
                        extra.append(rel)
        out("  files not created by apply inside the two folders: %d%s" % (len(extra), (": " + ", ".join(extra[:20]))
                                                                            if extra else ""))
    for root, state in destinations():
        out("  /config/%s: %s" % (root, state))
    return 0


def main(argv):
    if len(argv) < 3 or argv[1] not in ("plan", "stage", "apply", "rollback", "status"):
        out(__doc__)
        return 2
    mode, target = argv[1], argv[2]
    if mode in ("plan", "stage"):
        if not os.path.isfile(target):
            out("REFUSED: %s is not a file" % target)
            return 2
        if os.path.realpath(target).startswith(os.path.realpath(CONFIG) + os.sep):
            out("REFUSED: keep the source outside /config (for example in /share or /backup)")
            return 2
        return cmd_plan(target) if mode == "plan" else cmd_stage(target)
    stage = os.path.realpath(target)
    if not stage.startswith(os.path.realpath(STAGE_BASE) + os.sep):
        out("REFUSED: %s is not a staging folder under /share/casaray-restore" % target)
        return 2
    if mode == "apply":
        return cmd_apply(stage)
    if mode == "rollback":
        return cmd_rollback(stage, pycache="--pycache" in argv[3:])
    return cmd_status(stage)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
