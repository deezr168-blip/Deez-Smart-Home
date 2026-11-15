#!/usr/bin/env python3
"""Embed the canonical task register in the Task Control Center page.

    python3 docs/project-tasks/control-center/build.py            # write the snapshot
    python3 docs/project-tasks/control-center/build.py --check    # exit 1 if it is stale

The page reads GitHub when it can. When it cannot (offline, rate-limited, a
file opened from disk) it falls back to the snapshot this script embeds: the
register and decision history exactly as committed, with the commit they came
from, so the page never shows a task list of its own making. There is no
hand-written task list anywhere in the page.

Reads the two files from the working tree. The commit recorded is the last one
that changed either file, so a snapshot built after committing them names the
commit they came from (a commit cannot name itself: commit the files, then run
this and commit the page). If either file has uncommitted changes the snapshot
says so with "dirty": true. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGE = HERE / "index.html"
FILES = {"register": "docs/project-tasks/TASK_REGISTER.md", "history": "docs/project-tasks/DECISION_HISTORY.md"}
SNAP_RE = re.compile(r'(<script type="application/json" id="snapshot">)(.*?)(</script>)', re.S)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout.strip()


def snapshot() -> dict:
    sha = git("log", "-1", "--format=%H", "--", *FILES.values()) or "unknown"
    dirty = bool(git("status", "--porcelain", "--", *FILES.values()))
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    snap = {name: (ROOT / rel).read_text(encoding="utf-8") for name, rel in FILES.items()}
    snap.update(sha=sha, dirty=dirty, ref=branch,
                built_at=dt.date.today().isoformat() if dirty else (git("log", "-1", "--format=%cs", sha) or "unknown"))
    return snap


def embed(snap: dict) -> str:
    # "</" inside a <script> element would end it early; "<\/" is the same JSON string.
    return json.dumps(snap, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")


def current(html: str) -> dict:
    m = SNAP_RE.search(html)
    if not m:
        raise SystemExit("index.html has no snapshot <script> element")
    return json.loads(m.group(2) or "{}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the embedded register or history differs from the files")
    a = ap.parse_args()
    html = PAGE.read_text(encoding="utf-8")
    snap = snapshot()
    if a.check:
        have = current(html)
        stale = [k for k in FILES if have.get(k) != snap[k]]
        if stale:
            print("STALE: the page embeds an old " + " and ".join(stale) + ". Run build.py.")
            return 1
        print(f"OK: snapshot matches the register and history ({have.get('sha', '?')[:12]}"
              + (", built from uncommitted files" if have.get("dirty") else "") + ").")
        return 0
    new = SNAP_RE.sub(lambda m: m.group(1) + embed(snap) + m.group(3), html, count=1)
    PAGE.write_text(new, encoding="utf-8")
    state = "UNCOMMITTED changes on top of " if snap["dirty"] else ""
    print(f"Embedded {FILES['register']} and {FILES['history']}: {state}{snap['sha'][:12]} ({snap['ref']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
