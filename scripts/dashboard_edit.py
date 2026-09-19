#!/usr/bin/env python3
"""Locate and splice sections in a Lovelace dashboard, without hand-editing.

WHY THIS EXISTS

`dashboards/casaray_v2.yaml` is ~12,000 lines and carries comments that must
survive, so structural edits are done by parsing it, finding line offsets and
splicing — never by a YAML round-trip, which would strip every comment in the
file.

The finding-the-offsets part is the same twenty lines every time: parse the
document, locate each `- type: sections` header, find the `  - type: grid`
section starts inside one view, and walk BACK over the leading comment block
so a section's own explanation moves with it. That was written from scratch
eight times in one session (the top bar rollout, the chip strips on rooms and
on boards, the Bills restructure, the footers, the Rooms index, More boards,
the Energy bands). Once it was written slightly wrong — the section boundary
landed on the view's own header — and the edit had to be reverted.

Twenty lines of boilerplate repeated eight times, with one failure, is the
definition of something that should be a tool.

WHAT IT WILL NOT DO

Write YAML for you. `replace` and `insert` take a file whose contents are
spliced in verbatim, because deciding what a section should contain is the
part that needs judgement and the part where a generator would do damage. It
re-parses afterwards and refuses to write if the result does not parse or if
the view count changed.

USAGE

  dashboard_edit.py views
  dashboard_edit.py sections home
  dashboard_edit.py show home 3
  dashboard_edit.py show home 3 --lines            # with line numbers
  dashboard_edit.py replace home 3 --from new.yaml
  dashboard_edit.py insert home --at 4 --from new.yaml
  dashboard_edit.py delete home 7
  dashboard_edit.py span home 3 2                  # set column_span
  dashboard_edit.py grep "border-radius: 999px"    # which views/sections match

Every mutating command keeps a `.bak` beside the dashboard and prints what it
did. `--dry-run` shows the effect without writing.

EXIT STATUS

  0  ok
  1  refused — the edit would not parse, or the target does not exist
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(f"needs PyYAML: {exc}")

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT = "dashboards/casaray_v2.yaml"

VIEW_HEADER = "- type: sections"
SECTION_HEADER = "  - type: grid"


class Dashboard:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.lines = path.read_text(encoding="utf-8").split("\n")
        self.doc = yaml.safe_load("\n".join(self.lines))
        if not self.doc or "views" not in self.doc:
            sys.exit(f"{path} does not look like a dashboard")

    # ------------------------------------------------------------- locating
    def view_bounds(self):
        """[(path, start_line, end_line)] — half-open, 0-based."""
        starts = [i for i, l in enumerate(self.lines) if l == VIEW_HEADER]
        if len(starts) != len(self.doc["views"]):
            sys.exit(f"{len(starts)} '{VIEW_HEADER}' headers but "
                     f"{len(self.doc['views'])} parsed views — the file's shape "
                     f"is not what this tool assumes; edit it by hand")
        ends = starts[1:] + [len(self.lines)]
        return [(v.get("path"), s, e)
                for v, s, e in zip(self.doc["views"], starts, ends)]

    def find_view(self, name):
        for path, lo, hi in self.view_bounds():
            if path == name:
                return path, lo, hi
        sys.exit(f"no view with path {name!r}. Try: dashboard_edit.py views")

    def section_bounds(self, view_name):
        """[(index, start, end)] for one view, comment blocks included.

        A section's leading comments belong to it. Splicing without them
        leaves an explanation stranded above whatever replaced the section,
        which is worse than having no comment at all.
        """
        _, lo, hi = self.find_view(view_name)
        heads = [i for i in range(lo, hi)
                 if self.lines[i] == SECTION_HEADER
                 and self.lines[i + 1].lstrip().startswith("column_span:")]
        withc = []
        for h in heads:
            c = h
            while c - 1 > lo and (self.lines[c - 1].lstrip().startswith("#")
                                  or self.lines[c - 1].strip() == ""):
                c -= 1
            # Never swallow the view's own header block.
            withc.append(max(c, lo + 1))
        out = []
        for n, start in enumerate(withc):
            end = withc[n + 1] if n + 1 < len(withc) else hi
            # Trailing blank/comment lines before the next view belong to
            # neither section; leave them where they are.
            while end - 1 > start and self.lines[end - 1].strip() == "":
                end -= 1
            out.append((n, start, end))
        return out

    # -------------------------------------------------------------- writing
    def write(self, new_lines, dry_run, what):
        text = "\n".join(new_lines).rstrip("\n") + "\n"
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            sys.exit(f"REFUSED — the result does not parse:\n  {exc}")
        if not doc or "views" not in doc:
            sys.exit("REFUSED — the result has no views")
        before, after = len(self.doc["views"]), len(doc["views"])
        if before != after:
            sys.exit(f"REFUSED — view count changed {before} -> {after}")
        if dry_run:
            print(f"dry run: would {what}  "
                  f"({len(self.lines)} -> {len(new_lines)} lines)")
            return 0
        bak = self.path.with_suffix(self.path.suffix + ".bak")
        shutil.copy2(self.path, bak)
        self.path.write_text(text, encoding="utf-8")
        print(f"{what}  ({len(self.lines)} -> {len(new_lines)} lines)")
        print(f"backup: {bak.relative_to(REPO)}")
        return 0


def heading_of(doc_view, idx):
    try:
        cards = (doc_view.get("sections") or [])[idx].get("cards") or []
    except IndexError:
        return "-"
    for c in cards:
        if c.get("type") == "heading" and c.get("heading"):
            return c["heading"]
    return "-"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dashboard", default=DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("views")
    s = sub.add_parser("sections"); s.add_argument("view")
    sh = sub.add_parser("show"); sh.add_argument("view"); sh.add_argument("index", type=int)
    sh.add_argument("--lines", action="store_true")
    rp = sub.add_parser("replace"); rp.add_argument("view"); rp.add_argument("index", type=int)
    rp.add_argument("--from", dest="src", required=True)
    ins = sub.add_parser("insert"); ins.add_argument("view")
    ins.add_argument("--at", type=int, required=True); ins.add_argument("--from", dest="src", required=True)
    dl = sub.add_parser("delete"); dl.add_argument("view"); dl.add_argument("index", type=int)
    sp = sub.add_parser("span"); sp.add_argument("view"); sp.add_argument("index", type=int)
    sp.add_argument("value", type=int)
    gp = sub.add_parser("grep"); gp.add_argument("pattern")

    args = ap.parse_args()
    d = Dashboard(REPO / args.dashboard)

    if args.cmd == "views":
        for path, lo, hi in d.view_bounds():
            v = next(x for x in d.doc["views"] if x.get("path") == path)
            print(f"  {str(path):<20} {len(v.get('sections') or []):>2} sections  "
                  f"lines {lo + 1}-{hi}"
                  f"{'  [subview]' if v.get('subview') else ''}")
        return 0

    if args.cmd == "grep":
        pat = re.compile(args.pattern)
        for path, lo, hi in d.view_bounds():
            for n, start, end in d.section_bounds(path):
                body = "\n".join(d.lines[start:end])
                if pat.search(body):
                    v = next(x for x in d.doc["views"] if x.get("path") == path)
                    print(f"  {str(path):<20} section {n:<2} "
                          f"{heading_of(v, n):<28} lines {start + 1}-{end}")
        return 0

    if args.cmd == "sections":
        v = next(x for x in d.doc["views"] if x.get("path") == args.view)
        for n, start, end in d.section_bounds(args.view):
            sec = (v.get("sections") or [])[n] if n < len(v.get("sections") or []) else {}
            cards = sec.get("cards") or []
            cols = [c.get("grid_options", {}).get("columns") for c in cards]
            print(f"  [{n:>2}] span={sec.get('column_span')} "
                  f"{heading_of(v, n):<28} {len(cards):>2} cards  "
                  f"lines {start + 1}-{end}  cols={cols}")
        return 0

    if args.cmd == "show":
        b = d.section_bounds(args.view)
        if not 0 <= args.index < len(b):
            sys.exit(f"view {args.view!r} has {len(b)} sections (0-{len(b) - 1})")
        _, start, end = b[args.index]
        for i in range(start, end):
            print(f"{i + 1:>6}  {d.lines[i]}" if args.lines else d.lines[i])
        return 0

    # ----------------------------------------------------------- mutations
    b = d.section_bounds(args.view)
    lines = list(d.lines)

    if args.cmd in ("replace", "delete", "span"):
        if not 0 <= args.index < len(b):
            sys.exit(f"view {args.view!r} has {len(b)} sections (0-{len(b) - 1})")
        _, start, end = b[args.index]

    if args.cmd == "replace":
        new = pathlib.Path(args.src).read_text(encoding="utf-8").rstrip("\n").split("\n")
        lines[start:end] = new
        return d.write(lines, args.dry_run,
                       f"replaced {args.view} section {args.index} "
                       f"({end - start} lines -> {len(new)})")

    if args.cmd == "delete":
        lines[start:end] = []
        return d.write(lines, args.dry_run,
                       f"deleted {args.view} section {args.index} ({end - start} lines)")

    if args.cmd == "insert":
        if not 0 <= args.at <= len(b):
            sys.exit(f"--at must be 0-{len(b)} for view {args.view!r}")
        at = b[args.at][1] if args.at < len(b) else b[-1][2]
        new = pathlib.Path(args.src).read_text(encoding="utf-8").rstrip("\n").split("\n")
        lines[at:at] = new
        return d.write(lines, args.dry_run,
                       f"inserted {len(new)} lines into {args.view} at section {args.at}")

    if args.cmd == "span":
        for i in range(start, end):
            if lines[i].lstrip().startswith("column_span:"):
                indent = len(lines[i]) - len(lines[i].lstrip())
                old = lines[i].strip()
                lines[i] = " " * indent + f"column_span: {args.value}"
                return d.write(lines, args.dry_run,
                               f"{args.view} section {args.index}: {old} -> "
                               f"column_span: {args.value}")
        sys.exit(f"no column_span line in {args.view} section {args.index}")

    return 0


if __name__ == "__main__":
    # Dying quietly when the reader goes away is what `| head` expects; the
    # default is a traceback on every truncated listing.
    try:
        sys.exit(main())
    except BrokenPipeError:
        try:
            sys.stdout.close()
        finally:
            sys.exit(0)
