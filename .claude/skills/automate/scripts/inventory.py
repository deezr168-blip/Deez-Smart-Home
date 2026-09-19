#!/usr/bin/env python3
"""What automation already exists in this repository, and what it is for.

WHY THIS EXISTS

The most common failure of an eager automation pass is a ninth script that
does most of what the third script already did. Before building anything, the
question is not "can I build this" but "what is already here, and can it be
extended". That question is tedious to answer by hand across scripts/, the
skills directory, Home Assistant packages, hooks and CI — so it is answered
here, in one command, with each tool's own first docstring line as its
description.

It also searches: `inventory.py --find "entity"` shows every existing tool
whose name, description or body mentions entities, which is the check to run
before writing an entity-related script.

USAGE

  inventory.py
  inventory.py --find validate
  inventory.py --find "sync to config"
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]

SURFACES = [
    ("shell scripts", "scripts", ("*.sh",)),
    ("python tools", "scripts", ("*.py",)),
    ("claude skills", ".claude/skills", ("*/SKILL.md",)),
    ("skill tooling", ".claude/skills", ("*/scripts/*.py", "*/scripts/*.sh")),
    ("home assistant packages", "packages", ("*.yaml",)),
    ("git hooks", ".git/hooks", ("*",)),
    ("ci workflows", ".github/workflows", ("*.yml", "*.yaml")),
]


def is_prose(line: str) -> bool:
    """A comment line that actually says something.

    Banner comments (`# ======`, `# ------`) are the commonest first comment in
    this repository's YAML and shell files, and taking one as a description
    produces an inventory row that reads `====================`.
    """
    stripped = line.strip().lstrip("#").strip()
    if len(stripped) < 8:
        return False
    letters = sum(ch.isalpha() for ch in stripped)
    return letters >= max(6, len(stripped) // 3)


def describe(path: pathlib.Path) -> str:
    """One line saying what a tool is for, taken from the tool itself."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "(unreadable)"

    if path.name == "SKILL.md":
        m = re.search(r"^description:\s*(.+)$", text, re.M)
        if m:
            return m.group(1).strip().split(". ")[0][:150]

    if path.suffix == ".py":
        m = re.search(r'^"""(.+?)$', text, re.M)
        if m:
            return m.group(1).strip()[:150]

    if path.suffix in (".sh", ""):
        for line in text.splitlines()[:16]:
            s = line.strip()
            if s.startswith("#") and not s.startswith("#!") and is_prose(s):
                return s.lstrip("# ").strip()[:150]

    if path.suffix in (".yaml", ".yml"):
        for line in text.splitlines()[:16]:
            s = line.strip()
            if s.startswith("#") and is_prose(s):
                return s.lstrip("# ").strip()[:150]
        # An HA package is best summarised by what it actually declares.
        kinds = [k for k in ("automation", "script", "shell_command", "sensor",
                             "template", "input_boolean", "input_number",
                             "command_line", "binary_sensor")
                 if re.search(rf"^\s*{k}:", text, re.M)]
        if kinds:
            return "declares " + ", ".join(kinds)
    return "(no description)"


def collect():
    found = []
    for label, rel, globs in SURFACES:
        base = REPO / rel
        if not base.exists():
            continue
        for g in globs:
            for p in sorted(base.glob(g)):
                if not p.is_file():
                    continue
                if p.name.endswith(".sample"):
                    continue
                found.append((label, p))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--find", help="only tools mentioning this term")
    args = ap.parse_args()

    items = collect()
    if args.find:
        term = args.find.lower()
        kept = []
        for label, p in items:
            try:
                body = p.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                body = ""
            if term in p.name.lower() or term in body:
                kept.append((label, p))
        items = kept
        print(f"tools mentioning {args.find!r}: {len(items)}\n")
    else:
        print(f"{len(items)} automation artefacts in {REPO.name}\n")

    by_label = {}
    for label, p in items:
        by_label.setdefault(label, []).append(p)

    for label, _, _ in SURFACES:
        group = by_label.get(label)
        if not group:
            continue
        print(f"--- {label} ({len(group)})")
        for p in group:
            rel = p.relative_to(REPO)
            print(f"  {str(rel):<56} {describe(p)}")
        print()

    if not items:
        print("  nothing matched — but check the term is the one the repository"
              "\n  actually uses before concluding there is no tool for this.")
    else:
        print("Prefer extending one of these over adding another. A tool that"
              "\nalready runs in the validation path is worth more than a new"
              "\none nobody remembers to call.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
