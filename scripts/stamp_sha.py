#!/usr/bin/env python3
"""Stamp a commit SHA into the Commit column of tracking rows.

WHY

A commit cannot contain its own hash (CLAUDE.md, *Working rules*), so every
batch is two commits: the change with `—` in each row's Commit cell, then a
one-line `docs: stamp <sha> into the <IDs> rows`. That second edit was done by
hand in 13 commits between 2026-09-12 and 2026-09-24 (`git log --grep=stamp`),
and once went wrong enough to need `docs: re-stamp ... after a rebase changed
the hash` (86ec579).

    scripts/stamp_sha.py HEAD CR-324 CR-325            edit LIVE_VERIFICATION_QUEUE.md
    scripts/stamp_sha.py b96067e CR-324 --dry-run      show the diff, change nothing
    scripts/stamp_sha.py HEAD REG-016 --restamp        replace a stale SHA (after a rebase)
    scripts/stamp_sha.py --self-test                   fixture tests, incl. refusals

It edits the file and nothing else: no `git add`, no commit, no push. Commit
with the message it prints. Rows are matched on the first cell, and the target
column is found from the table's own header (`Commit`), because the queue has
six table shapes with the column in different places.

It refuses (exit 1, file untouched) when: the SHA is not a commit in this
repository; an ID matches no row; a row has no Commit column; a row already
carries a different SHA and --restamp was not given; an ID would change more
than one row and --all-rows was not given (the CR-318 collision: two batches
under one number).
"""
import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DOC = REPO / "LIVE_VERIFICATION_QUEUE.md"
PENDING = {"", "—", "-", "–"}


def split_row(line: str) -> list:
    """Cells of a markdown table row, respecting backslash-escaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def stamp(text: str, sha: str, ids: list, restamp: bool, all_rows: bool = False):
    """Return (new_text, problems). `problems` non-empty means do not write."""
    lines = text.split("\n")
    problems, hit, changed = [], set(), {}
    commit_col = None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            commit_col = None
            continue
        cells = split_row(line)
        if cells and cells[0] == "ID":
            commit_col = cells.index("Commit") if "Commit" in cells else None
            continue
        if not cells or cells[0] not in ids:
            continue
        hit.add(cells[0])
        if commit_col is None or commit_col >= len(cells):
            problems.append(f"{cells[0]}: its table has no Commit column")
            continue
        old = cells[commit_col].strip("` ")
        if old == sha:
            continue  # idempotent
        if old not in PENDING and not restamp:
            problems.append(f"{cells[0]}: already stamped `{old}`; "
                            "use --restamp only if a rebase changed the hash")
            continue
        # Splice by position so every other cell stays byte-identical.
        parts = re.split(r"(?<!\\)\|", line)
        offset = 1 if line.lstrip().startswith("|") else 0
        raw = parts[commit_col + offset]
        parts[commit_col + offset] = raw.replace(raw.strip(), f"`{sha}`", 1) \
            if raw.strip() else f" `{sha}` "
        lines[i] = "|".join(parts)
        changed.setdefault(cells[0], []).append(i + 1)
    for rid, at in changed.items():
        if len(at) > 1 and not all_rows:
            problems.append(f"{rid}: {len(at)} rows would be stamped (lines "
                            f"{', '.join(map(str, at))}). Two batches sharing an ID "
                            "is the CR-318 collision; if it is one batch, pass --all-rows")
    for missing in sorted(set(ids) - hit):
        problems.append(f"{missing}: no table row starts with this ID")
    return "\n".join(lines), problems


def resolve(rev: str):
    out = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--verify",
                          "--short=7", f"{rev}^{{commit}}"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


FIXTURE = """# Queue
| ID | What changed | Expected result | Commit | P | Result |
|---|---|---|---|---|---|
| CR-1 | a \\| b | ok | — | P1 | PENDING |
| CR-2 | two | ok | `aaaaaaa` | P1 | PENDING |
| CR-3 | three | ok | — | P2 | PENDING |
| CR-3 | three, second section | ok | — | P2 | PENDING |

| ID | Question | Why it is blocked |
|---|---|---|
| Q-1 | q | w |
"""


def self_test() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")

    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-3"], False)
    check("refuses one ID on two pending rows", len(p) == 1)
    new, p = stamp(FIXTURE, "bbbbbbb", ["CR-1", "CR-3"], False, True)
    check("--all-rows stamps pending rows", not p and new.count("`bbbbbbb`") == 3)
    check("escaped pipe and other cells untouched",
          "| a \\| b | ok | `bbbbbbb` | P1 | PENDING |" in new
          and "`aaaaaaa`" in new)
    check("only the Commit cell changed",
          len(new.split("\n")) == len(FIXTURE.split("\n"))
          and sum(a != b for a, b in zip(new.split("\n"),
                                         FIXTURE.split("\n"))) == 3)
    again, p = stamp(new, "bbbbbbb", ["CR-1", "CR-3"], False)
    check("idempotent", not p and again == new)
    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-2"], False)
    check("refuses a different existing SHA", len(p) == 1)
    new, p = stamp(FIXTURE, "bbbbbbb", ["CR-2"], True)
    check("--restamp replaces it", not p and "`aaaaaaa`" not in new)
    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-9"], False)
    check("refuses an unknown ID", len(p) == 1)
    _, p = stamp(FIXTURE, "bbbbbbb", ["Q-1"], False)
    check("refuses a table with no Commit column", len(p) == 1)
    check("rejects a non-commit rev", resolve("not-a-real-rev-xyz") is None)
    check("resolves HEAD", resolve("HEAD") is not None)
    print("self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("rev", nargs="?")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--file", type=pathlib.Path, default=DEFAULT_DOC)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--all-rows", action="store_true",
                    help="allow one ID to stamp several rows (one batch, several rows)")
    ap.add_argument("--restamp", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.rev or not a.ids:
        ap.error("need a rev and at least one ID")
    sha = resolve(a.rev)
    if not sha:
        print(f"refused: {a.rev!r} is not a commit here", file=sys.stderr)
        return 1
    text = a.file.read_text(encoding="utf-8")
    new, problems = stamp(text, sha, a.ids, a.restamp, a.all_rows)
    if problems:
        print("refused, file untouched:", *problems, sep="\n  ", file=sys.stderr)
        return 1
    if new == text:
        print("already stamped; nothing to do")
        return 0
    if a.dry_run:
        import difflib
        sys.stdout.writelines(difflib.unified_diff(
            text.splitlines(True), new.splitlines(True), "before", "after", n=0))
        print("(dry run: nothing written)")
        return 0
    a.file.write_text(new, encoding="utf-8")
    print(f"stamped {sha} into {', '.join(a.ids)}")
    print(f"commit message:\n  docs: stamp {sha} into the "
          f"{'/'.join(a.ids)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
