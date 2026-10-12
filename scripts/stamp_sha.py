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

Only the Commit cell changes: every other byte, including CRLF line endings and
a missing final newline, is preserved, and the file is replaced atomically (temp
file + rename), so a failed write leaves the original intact.

It refuses (exit 1, file untouched) when: the SHA is not a commit in this
repository; the file cannot be read, is not UTF-8, or cannot be written; an ID
matches no row (one missing ID refuses the whole run); a row has no Commit
column, or a different number of cells than its header (an unescaped `|` shifts
the columns and would stamp the wrong cell); the Commit cell holds anything but
the pending placeholder or a bare SHA (an annotation would be destroyed); a row
already carries a different SHA and --restamp was not given; an ID would change
more than one row and --all-rows was not given (the CR-318 collision: two
batches under one number). Rows inside code fences are ignored. A cell that
already holds the same commit (any abbreviation length) is left alone, so a
second run is a no-op.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DOC = REPO / "LIVE_VERIFICATION_QUEUE.md"
PENDING = {"", "—", "-", "–"}
BARE_SHA = re.compile(r"[0-9a-fA-F]{7,40}")


class Refuse(Exception):
    """A controlled refusal: printed as `refused: ...`, exit 1, file untouched."""


def same_commit(a: str, b: str) -> bool:
    """Two SHA spellings of one commit: a bare-hex prefix of the other."""
    a, b = a.lower(), b.lower()
    return bool(BARE_SHA.fullmatch(a) and BARE_SHA.fullmatch(b)) and (
        a.startswith(b) or b.startswith(a))


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
    commit_col = header_len = None
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            commit_col = header_len = None
            continue
        if in_fence or not line.lstrip().startswith("|"):
            commit_col = header_len = None
            continue
        cells = split_row(line)
        if cells and cells[0] == "ID":
            commit_col = cells.index("Commit") if "Commit" in cells else None
            header_len = len(cells)
            continue
        if not cells or cells[0] not in ids:
            continue
        hit.add(cells[0])
        if commit_col is None or commit_col >= len(cells):
            problems.append(f"{cells[0]}: its table has no Commit column")
            continue
        if len(cells) != header_len:
            problems.append(f"{cells[0]}: line {i + 1} has {len(cells)} cells but "
                            f"its header has {header_len} (an unescaped `|`?); "
                            "fix the row by hand first")
            continue
        old = cells[commit_col].strip("` ")
        if old not in PENDING and not BARE_SHA.fullmatch(old):
            problems.append(f"{cells[0]}: Commit cell holds {cells[commit_col]!r}, "
                            "not a SHA or placeholder; edit it by hand")
            continue
        if old not in PENDING and same_commit(old, sha):
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


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")  # bytes: no newline translation
    except UnicodeDecodeError as e:
        raise Refuse(f"{path} is not UTF-8 ({e.reason} at byte {e.start})")
    except OSError as e:
        raise Refuse(f"cannot read {path}: {e.strerror}")


def write_atomic(path: pathlib.Path, text: str) -> None:
    """All-or-nothing replace: temp file beside the target, fsync, rename."""
    target = path.resolve()  # a symlink is followed, not replaced by a file
    if not os.access(target, os.W_OK):
        raise Refuse(f"{path} is not writable")
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.",
                                   suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(text.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        shutil.copymode(target, tmp)
        os.replace(tmp, target)
        tmp = None
    except OSError as e:
        raise Refuse(f"cannot write {path}: {e.strerror}; the original is untouched")
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


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


def run_cli(*argv):
    """main() with a fake argv; returns (exit code, stdout, stderr)."""
    import contextlib
    import io
    out, err, old = io.StringIO(), io.StringIO(), sys.argv
    sys.argv = ["stamp_sha.py", *map(str, argv)]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main()
            except SystemExit as e:  # argparse usage errors
                code = e.code
    finally:
        sys.argv = old
    return code, out.getvalue(), err.getvalue()


def self_test() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")

    # -- the stamping rules (pure text in, text out) --
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
    again, p = stamp(new, "b" * 7 + "c" * 33, ["CR-1", "CR-3"], False)
    check("idempotent across SHA abbreviation lengths", not p and again == new)
    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-2"], False)
    check("refuses a different existing SHA", len(p) == 1)
    new, p = stamp(FIXTURE, "bbbbbbb", ["CR-2"], True)
    check("--restamp replaces it", not p and "`aaaaaaa`" not in new)
    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-9"], False)
    check("refuses an unknown ID", len(p) == 1)
    _, p = stamp(FIXTURE, "bbbbbbb", ["CR-1", "CR-9"], False)
    check("one missing ID refuses the whole run", len(p) == 1)
    _, p = stamp(FIXTURE, "bbbbbbb", ["Q-1"], False)
    check("refuses a table with no Commit column", len(p) == 1)
    shifted = "| ID | Note | Commit | P |\n|---|---|---|---|\n| CR-1 | a|— | — | P1 |\n"
    new, p = stamp(shifted, "bbbbbbb", ["CR-1"], False)
    check("refuses a row whose cell count differs from its header",
          len(p) == 1 and new == shifted)
    fenced = "```\n| ID | Commit |\n|---|---|\n| CR-1 | — |\n```\n"
    new, p = stamp(fenced, "bbbbbbb", ["CR-1"], False)
    check("ignores a table inside a code fence", len(p) == 1 and new == fenced)
    note = FIXTURE.replace("`aaaaaaa`", "`aaaaaaa` (rebased)")
    new, p = stamp(note, "bbbbbbb", ["CR-2"], True)
    check("refuses to overwrite an annotated cell, even with --restamp",
          len(p) == 1 and new == note)
    check("rejects a non-commit rev", resolve("not-a-real-rev-xyz") is None)
    check("resolves HEAD", resolve("HEAD") is not None)

    # -- the file handling, on throwaway files --
    import hashlib
    import time
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)

        def digest(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()

        f = d / "q.md"
        f.write_text(FIXTURE, encoding="utf-8")
        before = digest(f)
        mtime = f.stat().st_mtime_ns
        time.sleep(0.01)
        code, out, _ = run_cli("HEAD", "CR-1", "--dry-run", "--file", f)
        check("--dry-run writes nothing (bytes and mtime unchanged)",
              code == 0 and "dry run" in out and digest(f) == before
              and f.stat().st_mtime_ns == mtime)
        dup = d / "dup.md"
        dup.write_text(FIXTURE, encoding="utf-8")
        code, out, _ = run_cli("HEAD", "CR-1", "CR-1", "--file", dup)
        sha = out.split()[1] if out.startswith("stamped ") else "?"
        check("a repeated ID on the command line is stamped and named once",
              code == 0 and "CR-1/CR-1" not in out and "into CR-1\n" in out
              and dup.read_text().count(f"`{sha}`") == 1)
        code, _, _ = run_cli("HEAD", "CR-1", "CR-9", "--file", f)
        check("a refused run leaves the file byte-identical", code == 1 and digest(f) == before)
        code, _, _ = run_cli("HEAD", "CR-1", "--file", f)
        stamped = digest(f)
        code2, out2, _ = run_cli("HEAD", "CR-1", "--file", f)
        check("second run is a no-op", code == 0 and code2 == 0
              and "nothing to do" in out2 and digest(f) == stamped)
        crlf = d / "crlf.md"
        crlf.write_bytes(FIXTURE.replace("\n", "\r\n").encode())
        code, _, _ = run_cli("HEAD", "CR-1", "--file", crlf)
        raw = crlf.read_bytes()
        check("CRLF line endings preserved", code == 0
              and raw.count(b"\n") == raw.count(b"\r\n") == FIXTURE.count("\n"))
        nofinal = d / "nofinal.md"
        nofinal.write_text(FIXTURE.rstrip("\n"), encoding="utf-8")
        run_cli("HEAD", "CR-1", "--file", nofinal)
        check("a missing final newline stays missing", not nofinal.read_text().endswith("\n"))
        bad = d / "bad.md"
        bad.write_bytes(b"| ID | Commit |\n|---|---|\n| CR-1 | \xff\xfe |\n")
        badsum = digest(bad)
        code, _, err = run_cli("HEAD", "CR-1", "--file", bad)
        check("non-UTF-8 input is refused cleanly", code == 1 and "UTF-8" in err
              and "Traceback" not in err and digest(bad) == badsum)
        code, _, err = run_cli("HEAD", "CR-1", "--file", d / "nope.md")
        check("a missing file is refused cleanly", code == 1 and "cannot read" in err)
        code, _, err = run_cli("HEAD", "CR-1", "--file", d)
        check("a directory is refused cleanly", code == 1 and "cannot read" in err)
        empty = d / "empty.md"
        empty.write_text("", encoding="utf-8")
        code, _, _ = run_cli("HEAD", "CR-1", "--file", empty)
        check("an empty file is refused", code == 1 and empty.read_text() == "")
        # a write that fails at the last step must leave the original intact
        g = d / "atomic.md"
        g.write_text(FIXTURE, encoding="utf-8")
        gsum = digest(g)
        real_replace = os.replace

        def boom(*a, **k):
            raise OSError(5, "simulated crash")
        os.replace = boom
        try:
            code, _, err = run_cli("HEAD", "CR-1", "--file", g)
        finally:
            os.replace = real_replace
        check("a failed write leaves the original intact and no temp file",
              code == 1 and "untouched" in err and digest(g) == gsum
              and not [x for x in d.iterdir() if x.name.startswith(".atomic")])
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
    ids = list(dict.fromkeys(a.ids))
    try:
        sha = resolve(a.rev)
        if not sha:
            raise Refuse(f"{a.rev!r} is not a commit here")
        text = read_text(a.file)
        new, problems = stamp(text, sha, ids, a.restamp, a.all_rows)
        if problems:
            raise Refuse("file untouched", *problems)
        if new == text:
            print("already stamped; nothing to do")
            return 0
        if a.dry_run:
            import difflib
            sys.stdout.writelines(difflib.unified_diff(
                text.splitlines(True), new.splitlines(True), "before", "after", n=0))
            print("(dry run: nothing written)")
            return 0
        write_atomic(a.file, new)
    except Refuse as e:
        print("refused:", *e.args, sep="\n  " if len(e.args) > 1 else " ", file=sys.stderr)
        return 1
    print(f"stamped {sha} into {', '.join(ids)}")
    print(f"commit message:\n  docs: stamp {sha} into the "
          f"{'/'.join(ids)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
