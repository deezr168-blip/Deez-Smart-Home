#!/usr/bin/env python3
"""CasaRay recovery: READ-ONLY survey of the files missing from /config, and of
the backups that may still hold them.  v1.0, 02/11/2026.

Run in the Studio Code Server terminal on the Green, after checking its hash:

    python3 -I -B files_survey.py survey
    python3 -I -B files_survey.py contents SLUG [SLUG ...]

survey    Fast. Environment; proof that this /config is the one Core writes;
          which folders are missing; what the running Core has loaded; what
          HACS recorded as installed; every backup with its date, protection
          and Home Assistant version.
contents  Slow (minutes per backup). Reads an UNENCRYPTED local backup from
          /backup as a stream and lists, by name, the custom integrations, the
          www/community folders and the other items it holds.

Encrypted backups are not opened. Core's own decrypted download cannot be used
from an add-on for a backup this size: the Supervisor's Core API proxy reads a
non-event-stream response whole into memory before passing it on. See
FILES_RECOVERY_PLAN_2026-11.md, G2.

It writes nothing, extracts nothing to disk, and restarts, reloads, restores or
deletes nothing. It prints names, dates, sizes, counts, versions and yes/no
flags. It never prints a token, key or password, a username or config-entry
title, or the contents of any file, except these fields: manifest.json
domain/name/version, dashboard resource URLs and dashboard URL paths,
configuration.yaml top-level keys, HACS repository names and versions, and
entity IDs of unavailable security devices.
"""
import hashlib
import json
import os
import platform
import re
import socket
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.0"

# Test harness only: ROOT prefixes every absolute path, and the Supervisor URL
# may point at a local fake. Anything else is refused below, because every
# request carries the Supervisor token.
ROOT = os.environ.get("CASARAY_SURVEY_ROOT", "")
SUP = os.environ.get("CASARAY_SUPERVISOR_URL", "http://supervisor").rstrip("/")
TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
SECRETS = [TOKEN] if TOKEN else []
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never via a proxy

KEY_DIRS = ["custom_components", "custom_components/hacs", "www", "www/community", "themes",
            "dashboards", "packages", "blueprints", "deez_repo", "casaray", "_recovery", "esphome"]
KEY_FILES = ["configuration.yaml", "automations.yaml", "scripts.yaml", "scenes.yaml",
             "secrets.yaml", "home-assistant_v2.db"]
SECURITY_DOMAINS = ("camera", "siren", "lock", "alarm_control_panel")
SECURITY_CLASSES = {"door", "window", "opening", "garage_door", "lock", "smoke", "gas",
                    "moisture", "safety", "tamper"}
COPY_NAMES = {"custom_components", "hacs", "community", "lovelace-card-mod", "lovelace-mushroom",
              "kiosk-mode", "webrtc", "tapo_control"}
ARCHIVE_SUFFIXES = (".tar", ".tar.gz", ".tgz", ".zip", ".7z")


def P(path):
    return ROOT + path


def out(*parts):
    text = " ".join(str(p) for p in parts)
    for secret in SECRETS:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def clean(value, limit=60):
    text = re.sub(r"[\x00-\x1f\x7f]", "?", str(value))
    return text if len(text) <= limit else text[: limit - 1] + "~"


def ts(epoch):
    if not epoch:
        return "-"
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(epoch)) + "Z"


def mb(nbytes):
    return "%.1f MB" % (nbytes / 1048576.0)


def section(label, title):
    out("")
    out("== %s %s" % (label, title))


# --------------------------------------------------------------------- API ---
def _get(path, timeout=30, cap=64 << 20):
    if not TOKEN:
        return None, "SUPERVISOR_TOKEN not set"
    request = urllib.request.Request(SUP + path, headers={"Authorization": "Bearer " + TOKEN})
    try:
        with OPENER.open(request, timeout=timeout) as reply:
            return json.loads(reply.read(cap) or b"null"), None
    except urllib.error.HTTPError as err:
        return None, "HTTP %d" % err.code
    except Exception as err:  # noqa: BLE001 - only the type is ever printed
        return None, type(err).__name__


def sup(path):
    data, err = _get(path)
    if err:
        return None, err
    if not isinstance(data, dict) or data.get("result") != "ok":
        return None, "unexpected reply"
    return data.get("data") or {}, None


def core(path):
    return _get("/core" + path)


# ---------------------------------------------------------------- helpers ---
def stat(path):
    try:
        return os.stat(path)
    except OSError:
        return None


def count_tree(path, cap=200000):
    files = size = 0
    for base, dirs, names in os.walk(path):
        dirs.sort()
        for name in names:
            files += 1
            st = stat(os.path.join(base, name))
            size += st.st_size if st else 0
            if files >= cap:
                return files, size, True
    return files, size, False


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def list_entries(text):
    """Top-level YAML list items (automations.yaml, scenes.yaml)."""
    stripped = text.strip()
    if stripped in ("", "[]"):
        return 0
    return len(re.findall(r"(?m)^- ", text))


def map_entries(text):
    """Top-level YAML mapping keys (scripts.yaml)."""
    stripped = text.strip()
    if stripped in ("", "{}"):
        return 0
    return len(re.findall(r"(?m)^[^\s#\-][^:\n]*:", text))


def top_keys(text):
    return re.findall(r"(?m)^([a-z_]+):", text)


COUNTERS = {"automations.yaml": list_entries, "scenes.yaml": list_entries,
            "scripts.yaml": map_entries}


def storage_data(raw):
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data.get("data") if isinstance(data, dict) else None


def hacs_installed(raw):
    data = storage_data(raw)
    rows = []
    if isinstance(data, dict):
        for repo in data.values():
            if isinstance(repo, dict) and repo.get("installed"):
                version = repo.get("version_installed") or (repo.get("installed_commit") or "")[:7]
                rows.append((clean(repo.get("category", "?"), 14), clean(repo.get("full_name", "?"), 50),
                             clean(version or "?", 20), clean(repo.get("domain") or "-", 30)))
    return sorted(rows)


def resource_urls(raw):
    data = storage_data(raw)
    items = data.get("items", []) if isinstance(data, dict) else []
    return [(clean(i.get("type", "?"), 10), clean(i.get("url", "?"), 90)) for i in items if isinstance(i, dict)]


def dashboard_paths(raw):
    data = storage_data(raw)
    items = data.get("items", []) if isinstance(data, dict) else []
    return [(clean(i.get("url_path", "?"), 40), clean(i.get("mode", "?"), 10))
            for i in items if isinstance(i, dict)]


def entry_domains(raw):
    data = storage_data(raw)
    entries = data.get("entries", []) if isinstance(data, dict) else []
    return sorted({clean(e.get("domain", "?"), 40) for e in entries if isinstance(e, dict)})


STORAGE_READERS = {".storage/hacs.repositories": hacs_installed,
                   ".storage/lovelace_resources": resource_urls,
                   ".storage/lovelace_dashboards": dashboard_paths,
                   ".storage/core.config_entries": entry_domains}


def live_storage(name):
    """Read one allow-listed live .storage file, returning only its safe fields."""
    path = P("/config/") + name
    reader = STORAGE_READERS.get(name)
    if reader is None or not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        return reader(handle.read(32 << 20))


def safe_meta(raw):
    try:
        meta = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(meta, dict):
        return None
    ha = meta.get("homeassistant") or {}
    apps = meta.get("addons") or meta.get("apps") or []
    extra = meta.get("extra") if isinstance(meta.get("extra"), dict) else {}
    return {
        "slug": clean(meta.get("slug", "?"), 20), "name": clean(meta.get("name", "?"), 50),
        "date": clean(meta.get("date", "?"), 32), "type": clean(meta.get("type", "?"), 10),
        "protected": bool(meta.get("protected")), "compressed": meta.get("compressed", True),
        "ha_version": clean(ha.get("version", "-") if isinstance(ha, dict) else "-", 20),
        "exclude_db": bool(ha.get("exclude_database")) if isinstance(ha, dict) else None,
        "folders": [clean(f, 20) for f in meta.get("folders") or []],
        "apps": len(apps) if isinstance(apps, list) else 0,
        "automatic": extra.get("with_automatic_settings"),
    }


def local_backups():
    """Every *.tar in /backup, with the safe fields of its backup.json."""
    found = {}
    folder = P("/backup")
    if not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".tar"):
            continue
        path = os.path.join(folder, name)
        meta, err = None, None
        try:
            with tarfile.open(path, "r:") as archive:
                member = None
                for candidate in ("./backup.json", "backup.json"):
                    try:
                        member = archive.getmember(candidate)
                        break
                    except KeyError:
                        continue
                if member is None:
                    err = "no backup.json"
                else:
                    meta = safe_meta(archive.extractfile(member).read(1 << 20))
        except Exception as error:  # noqa: BLE001
            err = type(error).__name__
        found[name] = (path, stat(path), meta, err)
    return found


# ------------------------------------------------------------------ survey ---
def survey():
    out("CasaRay files survey v%s - READ-ONLY: nothing is written, extracted, restarted or reloaded."
        % VERSION)
    section("1", "environment")
    out("python", platform.python_version(), "| host", clean(socket.gethostname(), 40),
        "| add-on container:", "yes" if os.path.exists(P("/data/options.json")) else "no",
        "| SUPERVISOR_TOKEN:", "set" if TOKEN else "NOT SET")
    info, err = sup("/core/info")
    out("Supervisor /core/info:", err or "version %s | machine %s" % (
        clean(info.get("version")), clean(info.get("machine"))))
    supinfo, err2 = sup("/supervisor/info")
    out("Supervisor version:", err2 or clean(supinfo.get("version")))
    cfg, err3 = core("/api/config")
    comps = []
    if err3 or not isinstance(cfg, dict):
        out("Core /api/config:", err3 or "unexpected reply")
        cfg = {}
    else:
        comps = cfg.get("components") or []
        out("Core /api/config: version %s | config_dir %s | state %s | recovery_mode %s | "
            "components loaded %d | hacs loaded: %s" % (
                clean(cfg.get("version")), clean(cfg.get("config_dir")), clean(cfg.get("state")),
                clean(cfg.get("recovery_mode", cfg.get("safe_mode"))), len(comps),
                "yes" if "hacs" in comps else "no"))

    section("2", "is this /config the folder Core writes?")
    config = P("/config")
    out("/config:", "present" if os.path.isdir(config) else "MISSING")
    try:
        out("/homeassistant ->", clean(os.readlink(P("/homeassistant"))))
    except OSError:
        out("/homeassistant: not a symlink" if os.path.exists(P("/homeassistant")) else "/homeassistant: absent")
    mounts = P("/proc/mounts") if os.path.exists(P("/proc/mounts")) else "/proc/mounts"
    line = ""
    try:
        with open(mounts) as handle:
            line = next((l for l in handle if l.split()[1:2] == ["/config"]), "")
    except OSError:
        pass
    out("mount:", "device %s, type %s" % tuple(line.split()[0:3:2]) if line else "no /config line in /proc/mounts")
    ha_version = ""
    try:
        with open(os.path.join(config, ".HA_VERSION")) as handle:
            ha_version = re.sub(r"[^0-9A-Za-z.]", "", handle.read(40))
    except OSError:
        pass
    out(".HA_VERSION:", ha_version or "MISSING", "| Core reports:", clean(cfg.get("version", "-")))
    now = time.time()
    ages = {}
    for name in ("core.restore_state", "core.entity_registry", "core.config_entries"):
        st = stat(os.path.join(config, ".storage", name))
        ages[name] = (now - st.st_mtime) / 60 if st else None
        out("  .storage/%-22s %s" % (name, "modified %.0f min ago" % ages[name] if st else "MISSING"))
    live = ha_version and ha_version == cfg.get("version") and ages["core.restore_state"] is not None \
        and ages["core.restore_state"] < 20
    out("VERDICT:", "LIVE - this /config is the folder the running Core writes" if live else
        "NOT PROVEN - .HA_VERSION must match Core and core.restore_state must be under 20 min old"
        " (Core rewrites it every 15 min)")

    section("3", "folders and files in /config now (names, counts, sizes)")
    names = sorted(os.listdir(config)) if os.path.isdir(config) else []
    out("top level (%d):" % len(names), ", ".join(
        n + ("/" if os.path.isdir(os.path.join(config, n)) else "") for n in names))
    for rel in KEY_DIRS:
        path = os.path.join(config, rel)
        if os.path.isdir(path):
            files, size, cut = count_tree(path)
            out("  %-24s present  %d files%s, %s" % (rel, files, "+" if cut else "", mb(size)))
        else:
            out("  %-24s MISSING" % rel)
    for rel in KEY_FILES:
        st = stat(os.path.join(config, rel))
        if not st:
            out("  %-24s MISSING" % rel)
            continue
        note = ""
        if rel in COUNTERS:
            with open(os.path.join(config, rel), encoding="utf-8", errors="replace") as handle:
                note = " | entries %d" % COUNTERS[rel](handle.read(8 << 20))
        elif rel == "configuration.yaml":
            with open(os.path.join(config, rel), encoding="utf-8", errors="replace") as handle:
                note = " | keys %s" % ",".join(top_keys(handle.read(1 << 20)))
        out("  %-24s %d bytes, modified %s%s" % (rel, st.st_size, ts(st.st_mtime), note))
    themes = os.path.join(config, "themes")
    if os.path.isdir(themes):
        for base, _, files in os.walk(themes):
            for name in sorted(files):
                full = os.path.join(base, name)
                out("  theme file %-30s %s" % (clean(os.path.relpath(full, config), 40), sha256(full)))
    www = os.path.join(config, "www")
    if os.path.isdir(www):
        out("  www holds:", ", ".join(sorted(os.listdir(www))) or "(empty)")

    section("4", "what the running Core has loaded (Core API, read-only)")
    states, err = core("/api/states")
    if err or not isinstance(states, list):
        out("states:", err or "unexpected reply")
    else:
        unavailable = [s for s in states if s.get("state") == "unavailable"]
        out("entities %d | unavailable %d" % (len(states), len(unavailable)))
        for domain in ("automation", "script", "scene"):
            rows = [s for s in states if str(s.get("entity_id", "")).startswith(domain + ".")]
            out("  %-10s loaded %d (unavailable %d)" % (domain, len(rows),
                sum(1 for s in rows if s.get("state") == "unavailable")))
        risky = sorted(str(s.get("entity_id")) for s in unavailable
                       if str(s.get("entity_id", "")).split(".")[0] in SECURITY_DOMAINS
                       or (str(s.get("entity_id", "")).startswith("binary_sensor.")
                           and (s.get("attributes") or {}).get("device_class") in SECURITY_CLASSES))
        out("  security devices unavailable (%d):" % len(risky), ", ".join(risky[:60]) or "none")
    entries, err = core("/api/config/config_entries/entry")
    if err or not isinstance(entries, list):
        out("config entries:", err or "unexpected reply")
    else:
        by_state = {}
        for e in entries:
            by_state[clean(e.get("state"), 20)] = by_state.get(clean(e.get("state"), 20), 0) + 1
        out("config entries %d | by state %s" % (len(entries), by_state))
        for e in sorted(entries, key=lambda x: str(x.get("domain"))):
            if e.get("state") != "loaded":
                out("  not loaded: %-28s state %-18s disabled_by %s" % (
                    clean(e.get("domain"), 28), clean(e.get("state"), 18), clean(e.get("disabled_by") or "-", 12)))
        out("  configured domains:", ", ".join(sorted({clean(e.get("domain"), 40) for e in entries})))

    section("5", "what was recorded as installed (live .storage, selected fields only)")
    hacs = live_storage(".storage/hacs.repositories")
    if hacs is None:
        out("  .storage/hacs.repositories: MISSING")
    else:
        out("  HACS records %d installed repositories:" % len(hacs))
        for category, name, version, domain in hacs:
            out("    %-12s %-46s %-18s domain %s" % (category, name, version, domain))
    resources = live_storage(".storage/lovelace_resources")
    out("  dashboard resources registered:", "file MISSING" if resources is None else len(resources))
    for kind, url in resources or []:
        out("    %-8s %s" % (kind, url))
    dashboards = live_storage(".storage/lovelace_dashboards")
    out("  storage dashboards:", "file MISSING" if dashboards is None else
        ", ".join("%s (%s)" % row for row in dashboards) or "none")

    section("6", "backups (Supervisor API and the /backup folder)")
    listing, err = sup("/backups")
    rows = (listing or {}).get("backups") or []
    if err:
        out("  Supervisor /backups:", err)
    for b in sorted(rows, key=lambda x: str(x.get("date"))):
        slug = clean(b.get("slug"), 20)
        detail, derr = sup("/backups/%s/info" % urllib.parse.quote(str(b.get("slug")), safe=""))
        detail = detail or {}
        extra = detail.get("extra") if isinstance(detail.get("extra"), dict) else {}
        content = b.get("content") or {}
        size = b.get("size_bytes") or (b.get("size") or 0) * 1048576
        out("  %-10s %-25s %-8s %10s protected=%-5s HA=%-10s automatic=%-5s db_excluded=%-5s "
            "locations=%s folders=%s apps=%d name=%s%s" % (
                slug, clean(b.get("date"), 25), clean(b.get("type"), 8), mb(size),
                bool(b.get("protected")), clean(detail.get("homeassistant") or "-", 10),
                clean(extra.get("with_automatic_settings", "-"), 5),
                clean(detail.get("homeassistant_exclude_database", "-"), 5),
                clean(b.get("locations", [b.get("location")]), 40), clean(content.get("folders") or [], 50),
                len(content.get("addons") or content.get("apps") or []), clean(b.get("name"), 40),
                " (info: %s)" % derr if derr else ""))
    local = local_backups()
    out("  /backup holds %d .tar files:" % len(local))
    for name, (path, st, meta, err) in local.items():
        out("    %-56s %10s %s slug=%s protected=%s HA=%s%s" % (
            clean(name, 56), mb(st.st_size) if st else "?", ts(st.st_mtime) if st else "-",
            meta["slug"] if meta else "?", meta["protected"] if meta else "?",
            meta["ha_version"] if meta else "?", " (%s)" % err if err else ""))
    plain = [m["slug"] for _, (_, _, m, _) in local.items() if m and not m["protected"]]
    locked = [m["slug"] for _, (_, _, m, _) in local.items() if m and m["protected"]]
    out("  unencrypted local backups:", ", ".join(plain) or "none")
    out("  encrypted local backups:", ", ".join(locked) or "none")

    section("7", "other local copies (folder and archive names only)")
    hits = 0
    for top in ("/share", "/media", "/addon_configs", "/addons", "/backup", "/config"):
        base = P(top)
        if not os.path.isdir(base):
            continue
        seen = 0
        for folder, dirs, files in os.walk(base):
            depth = folder[len(base):].count(os.sep)
            dirs[:] = sorted(d for d in dirs if depth < 4 and not (top == "/config" and d == ".storage"))
            seen += len(dirs) + len(files)
            for d in dirs:
                if d in COPY_NAMES:
                    hits += 1
                    out("  folder  %s" % clean(top + folder[len(base):] + "/" + d, 100))
            for f in sorted(files):
                if f.endswith(ARCHIVE_SUFFIXES) and not (top == "/backup" and folder == base):
                    st = stat(os.path.join(folder, f))
                    hits += 1
                    out("  archive %s %s %s" % (clean(top + folder[len(base):] + "/" + f, 100),
                                                mb(st.st_size) if st else "?", ts(st.st_mtime) if st else "-"))
            if seen > 200000 or hits > 100:
                out("  (search stopped early under %s)" % top)
                break
    out("  matches:", hits)
    out("")
    out("== END survey (read-only; nothing was changed)")
    return 0


# ---------------------------------------------------------------- contents ---
def read_member(archive, member, cap):
    handle = archive.extractfile(member)
    return handle.read(cap) if handle else b""


def scan(archive, member, rep):
    name = member.name
    while name.startswith("./"):
        name = name[2:]
    if not name.startswith("data/") or name == "data/":
        return
    rel = name[5:]
    parts = rel.split("/")
    top = parts[0]
    rep["members"] += 1
    if rep["members"] % 20000 == 0:
        out("  ... %d entries read" % rep["members"])
    item = rep["top"].setdefault(top, [0, 0])
    if member.isfile():
        item[0] += 1
        item[1] += member.size
        if not rel.startswith(".storage/") and not rel.startswith("home-assistant_v2.db"):
            rep["newest"] = max(rep["newest"], member.mtime)
    if top == "custom_components" and len(parts) >= 2 and parts[1]:
        comp = rep["cc"].setdefault(parts[1], {"files": 0, "bytes": 0, "newest": 0, "manifest": None})
        if member.isfile():
            comp["files"] += 1
            comp["bytes"] += member.size
            comp["newest"] = max(comp["newest"], member.mtime)
            if len(parts) == 3 and parts[2] == "manifest.json" and member.size < 262144:
                try:
                    manifest = json.loads(read_member(archive, member, 262144))
                    comp["manifest"] = (clean(manifest.get("domain", "?"), 30),
                                        clean(manifest.get("version", "?"), 20),
                                        clean(manifest.get("name", "?"), 40))
                except ValueError:
                    comp["manifest"] = ("unreadable", "-", "-")
    elif top == "www" and len(parts) >= 2 and parts[1]:
        if parts[1] == "community":
            if len(parts) >= 3 and parts[2]:
                d = rep["community"].setdefault(parts[2], {"files": 0, "bytes": 0, "newest": 0})
                if member.isfile():
                    d["files"] += 1
                    d["bytes"] += member.size
                    d["newest"] = max(d["newest"], member.mtime)
        else:
            rep["www"].add(parts[1])
    if rel in KEY_FILES and member.isfile():
        entry = {"size": member.size, "mtime": member.mtime}
        if rel in COUNTERS:
            entry["entries"] = COUNTERS[rel](read_member(archive, member, 8 << 20).decode("utf-8", "replace"))
        elif rel == "configuration.yaml":
            entry["keys"] = top_keys(read_member(archive, member, 1 << 20).decode("utf-8", "replace"))
        rep["keyfiles"][rel] = entry
    if top in ("themes", "dashboards", "packages") and member.isfile():
        rep["lists"].setdefault(top, []).append(clean("/".join(parts[1:]), 60))
    if rel in STORAGE_READERS and member.isfile():
        rep["storage"][rel] = STORAGE_READERS[rel](read_member(archive, member, 32 << 20))


def analyse(stream):
    rep = {"meta": None, "inner": None, "inner_done": False, "error": None, "members": 0,
           "top": {}, "cc": {}, "community": {}, "www": set(), "keyfiles": {}, "lists": {},
           "storage": {}, "newest": 0}
    try:
        outer = tarfile.open(fileobj=stream, mode="r|")
        for member in outer:
            name = member.name
            while name.startswith("./"):
                name = name[2:]
            if name == "backup.json" and member.isfile():
                rep["meta"] = safe_meta(read_member(outer, member, 1 << 20))
            elif name in ("homeassistant.tar.gz", "homeassistant.tar") and member.isfile():
                rep["inner"] = name
                inner = tarfile.open(fileobj=outer.extractfile(member),
                                     mode="r|gz" if name.endswith(".gz") else "r|")
                for item in inner:
                    scan(inner, item, rep)
                rep["inner_done"] = True
    except Exception as err:  # noqa: BLE001 - only the type is printed
        rep["error"] = type(err).__name__
    return rep


def report(label, rep, started):
    live_cfg = P("/config")
    hacs_rows = live_storage(".storage/hacs.repositories") or []
    hacs_live = {row[3]: row for row in hacs_rows if row[3] != "-"}
    hacs_by_name = {row[1]: row for row in hacs_rows}
    entries, _ = core("/api/config/config_entries/entry")
    entry_state = {}
    for e in entries if isinstance(entries, list) else []:
        entry_state.setdefault(clean(e.get("domain"), 40), clean(e.get("state"), 18))
    meta = rep["meta"] or {}
    section("C1", "backup %s" % label)
    out("  metadata: slug %s | date %s | type %s | HA %s | protected %s | db excluded %s | folders %s"
        % (meta.get("slug", "?"), meta.get("date", "?"), meta.get("type", "?"), meta.get("ha_version", "?"),
           meta.get("protected", "?"), meta.get("exclude_db", "?"), meta.get("folders", "?")))
    complete = rep["inner_done"] and not rep["error"]
    out("  read: %s | archive entries read %d | newest config file (not .storage, not db) %s | %.0f s"
        % ("COMPLETE" if complete else "INCOMPLETE (%s)" % (rep["error"] or "no homeassistant archive"),
           rep["members"], ts(rep["newest"]), time.time() - started))
    if not complete:
        out("  An incomplete read proves nothing about what the backup holds or lacks, so no contents"
            " are listed. Usual causes: a wrong key, an unsupported format, or an interrupted stream."
            " Nothing was written.")
        out("")
        out("== END contents %s (INCOMPLETE; read-only; nothing was written)" % label)
        return 5

    live_cc = os.path.isdir(os.path.join(live_cfg, "custom_components"))
    section("C2", "custom_components: %d integrations in the backup | live folder %s"
            % (len(rep["cc"]), "present" if live_cc else "MISSING"))
    for comp, d in sorted(rep["cc"].items()):
        domain, version, name = d["manifest"] or ("no manifest", "-", "-")
        live = hacs_live.get(domain)
        out("  %-24s %4d files %9s newest %s | manifest %s %s | HACS live record %s | entry %s | live %s"
            % (clean(comp, 24), d["files"], mb(d["bytes"]), ts(d["newest"]), domain, version,
               live[2] if live else "-", entry_state.get(domain, "-"),
               "present" if os.path.isdir(os.path.join(live_cfg, "custom_components", comp)) else "MISSING"))

    live_comm = os.path.isdir(os.path.join(live_cfg, "www", "community"))
    section("C3", "www/community: %d folders in the backup | live folder %s"
            % (len(rep["community"]), "present" if live_comm else "MISSING"))
    for folder, d in sorted(rep["community"].items()):
        out("  %-32s %4d files %9s newest %s" % (clean(folder, 32), d["files"], mb(d["bytes"]), ts(d["newest"])))
    out("  www, other top-level items:", ", ".join(sorted(clean(n, 40) for n in rep["www"])) or "none")

    section("C4", "top-level items in the backup, against /config now")
    for top, (files, size) in sorted(rep["top"].items()):
        out("  %-28s %6d files %10s | live %s" % (clean(top, 28), files, mb(size),
            "present" if os.path.exists(os.path.join(live_cfg, top)) else "MISSING"))

    section("C5", "key files: size, date, entry counts (contents not printed)")
    for rel in KEY_FILES:
        b = rep["keyfiles"].get(rel)
        st = stat(os.path.join(live_cfg, rel))
        note = ""
        if b and "entries" in b:
            note = " | entries %d" % b["entries"]
        if b and "keys" in b:
            note = " | keys %s" % ",".join(b["keys"])
        out("  %-22s backup %s | live %s" % (rel, ("%d bytes %s%s" % (b["size"], ts(b["mtime"]), note)) if b
                                            else "ABSENT", ("%d bytes %s" % (st.st_size, ts(st.st_mtime))) if st
                                            else "MISSING"))
    for top in ("themes", "dashboards", "packages"):
        if top in rep["lists"]:
            out("  %s/: %s" % (top, ", ".join(sorted(rep["lists"][top])[:40])))

    section("C6", "selected .storage records in the backup (names and versions only)")
    hacs = rep["storage"].get(".storage/hacs.repositories")
    out("  HACS installed then:", "not in backup" if hacs is None else len(hacs))
    for category, name, version, domain in hacs or []:
        live = hacs_by_name.get(name)
        out("    %-12s %-46s %-18s | live record %s" % (category, name, version, live[2] if live else "-"))
    resources = rep["storage"].get(".storage/lovelace_resources")
    out("  dashboard resources then:", "not in backup" if resources is None else len(resources))
    for kind, url in resources or []:
        out("    %-8s %s" % (kind, url))
    then = rep["storage"].get(".storage/core.config_entries")
    if then is not None and isinstance(entries, list):
        now = {clean(e.get("domain"), 40) for e in entries}
        out("  config-entry domains in the backup but not live:", ", ".join(sorted(set(then) - now)) or "none")
        out("  config-entry domains live but not in the backup:", ", ".join(sorted(now - set(then))) or "none")
    out("")
    out("== END contents %s (read-only; nothing was written)" % label)
    return 0 if complete else 5


def contents(args):
    if not args:
        out("usage: contents SLUG [SLUG ...]")
        return 2
    local = local_backups()
    by_slug = {m["slug"]: name for name, (_, _, m, _) in local.items() if m}
    rc = 0
    for arg in args:
        name = arg if arg in local else by_slug.get(arg)
        if name is None:
            out("\n== backup %s: no local file in /backup (it may be stored only in Home Assistant Cloud)"
                % clean(arg, 40))
            rc = rc or 3
            continue
        path, st, meta, err = local[name]
        if meta and meta["protected"]:
            out("\n== backup %s is ENCRYPTED. This tool does not open encrypted backups; see"
                " FILES_RECOVERY_PLAN_2026-11.md, G2. Nothing was read." % meta["slug"])
            rc = rc or 3
            continue
        out("\n== reading %s (%s) as a stream; nothing is written. This takes a few minutes."
            % (clean(name, 60), mb(st.st_size) if st else "?"))
        started = time.time()
        with open(path, "rb") as handle:
            rep = analyse(handle)
        rc = report(meta["slug"] if meta else clean(name, 40), rep, started) or rc
    return rc


def main(argv):
    if not re.fullmatch(r"http://supervisor|http://(?:127\.0\.0\.1|localhost):\d{1,5}", SUP):
        out("REFUSED: the Supervisor URL may only be http://supervisor, or a local test harness.")
        return 4
    mode = argv[1] if len(argv) > 1 else "survey"
    if mode == "survey":
        return survey()
    if mode == "contents":
        return contents(argv[2:])
    out(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
