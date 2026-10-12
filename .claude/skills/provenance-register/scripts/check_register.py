#!/usr/bin/env python3
"""Lint a register, inventory, evidence log or quote comparison for provenance.

WHY THIS EXISTS

A register fails quietly: a plausible value goes into a cell because the cell
looked empty, and from then on nobody can tell it from a measured one. The rule
this enforces is simple. Every row carries a Status and a Source; a value is
VERIFIED, REPORTED, ASSUMED or UNKNOWN; a gap is the literal word UNKNOWN; and
the columns where a wrong value does the most damage (ownership, identifiers,
ratings, measurements, prices) may only hold a value on a row that is VERIFIED
or REPORTED. The same discipline the Home Assistant work here applies to entity
IDs ("never invent one") and to cards ("never assert a state you cannot see").

WHAT IT CHECKS

  E0  the table is malformed (no table found, or a row with the wrong cell count)
  E1  a required column is missing (default: ID, Status, Source)
  E2  a Status that is not VERIFIED, REPORTED, ASSUMED, UNKNOWN or N/A
  E3  a blank cell. A gap must say UNKNOWN (or N/A)
  E4  a duplicate ID
  E5  a VERIFIED or REPORTED row whose Source is blank, UNKNOWN or N/A
  E6  a VERIFIED row whose "Verified on" is not a date (when that column exists)
  E7  a value in an ownership/measurement/price column on a row that is not
      VERIFIED or REPORTED
  W1  a vague placeholder (TBC, approx, probably, ?) where UNKNOWN belongs
  W2  the recommended columns "Verified on" / "Verified by" are absent
  W3  ASSUMED rows exist (reported so they are not forgotten)

It reads a file and prints. It never writes, uploads, shares or sends.

USAGE

  check_register.py FILE                  .md (first pipe table) or .csv
  check_register.py FILE --table 2        the second table in a Markdown file
  check_register.py FILE --strict         warnings count as errors
  check_register.py FILE --json
  check_register.py FILE --require id,status,source,verified on
  check_register.py FILE --also-sensitive 'wattage|colour'
  check_register.py --template equipment  print a blank register (equipment, evidence, quotes)
  check_register.py --selftest

EXIT CODES  0 clean   1 errors (or warnings with --strict)   2 usage or unreadable file
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "assets" / "templates"
FIXTURES = SKILL_DIR / "tests" / "fixtures"

STATUSES = ("VERIFIED", "REPORTED", "ASSUMED", "UNKNOWN", "N/A")
GROUNDED = ("VERIFIED", "REPORTED")           # statuses that may carry a sensitive value
REQUIRED_DEFAULT = ("id", "status", "source")
RECOMMENDED = ("verified on", "verified by")

# Columns where a wrong value is worst. A header matching this may only hold a
# value on a VERIFIED or REPORTED row. Replace with --sensitive, extend with
# --also-sensitive.
SENSITIVE_DEFAULT = (
    r"owner|assigned|custodian|serial|asset[ _-]?(tag|no|number)|model|manufacturer|"
    r"rating|capacity|weight|dimension|voltage|current|power|energy|\bkw\b|\bkwh\b|"
    r"\bamps?\b|\bmm\b|\bcm\b|\bkg\b|price|cost|amount|total"
)
# Words that stand in for UNKNOWN. "about" and "likely" are left out on purpose:
# they are ordinary prose in a Notes column and would bury the real warnings.
VAGUE = re.compile(r"^\s*(tbc|tbd|to be confirmed|to be determined|n/k|unsure|\?+)\s*$"
                   r"|\b(approx\.?|approximately|roughly|circa|probably)\b|~|\?", re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{1,2}/\d{1,2}/\d{2,4}$")


# --------------------------------------------------------------------------
# reading tables
# --------------------------------------------------------------------------

def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-+:?", c.strip()) for c in cells)


def markdown_tables(text: str) -> list[list[tuple[int, list[str]]]]:
    """All pipe tables outside fenced code blocks, as [(line_number, cells)]."""
    tables, current, in_fence = [], [], False
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            if current:
                tables.append(current)
                current = []
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("|"):
            current.append((n, split_row(line)))
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    out = []
    for t in tables:
        if len(t) >= 2 and is_separator(t[1][1]):
            out.append([t[0]] + t[2:])        # header, then data rows (separator dropped)
    return out


def read_table(path: Path, table_no: int = 1) -> tuple[list[str], list[tuple[int, list[str]]]]:
    """Return (header cells, [(line_number, cells)]). Raises ValueError."""
    try:
        # utf-8-sig: spreadsheet exports often start with a byte-order mark, which
        # would otherwise turn the first header into "﻿ID" and fail E1.
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"cannot read {path}: {e}") from e
    suffix = path.suffix.lower()
    if suffix == ".csv":
        rows = list(csv.reader(io.StringIO(text)))
        rows = [r for r in rows if any(c.strip() for c in r)]
        if not rows:
            raise ValueError("E0: the CSV file is empty")
        return [c.strip() for c in rows[0]], [(i + 2, [c.strip() for c in r])
                                              for i, r in enumerate(rows[1:])]
    if suffix in (".md", ".markdown"):
        tables = markdown_tables(text)
        if not tables:
            raise ValueError("E0: no pipe table found")
        if table_no < 1 or table_no > len(tables):
            raise ValueError(f"E0: --table {table_no} requested but the file has {len(tables)}")
        t = tables[table_no - 1]
        return t[0][1], t[1:]
    raise ValueError(f"unsupported file type {suffix!r}; use .md or .csv")


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def is_gap(v: str) -> bool:
    return v.strip().upper() in ("UNKNOWN", "N/A")


def lint(header: list[str], rows: list[tuple[int, list[str]]], *,
         required=REQUIRED_DEFAULT, sensitive: str = SENSITIVE_DEFAULT,
         also_sensitive: str | None = None) -> dict:
    errors: list[dict] = []
    warns: list[dict] = []

    def err(code, msg, line=None):
        errors.append({"code": code, "line": line, "message": msg})

    def warn(code, msg, line=None):
        warns.append({"code": code, "line": line, "message": msg})

    names = [h.strip().casefold() for h in header]
    idx = {n: i for i, n in enumerate(names)}
    missing = [r for r in required if r.casefold() not in idx]
    if missing:
        err("E1", "required column(s) missing: " + ", ".join(missing))
    pat = re.compile(sensitive + (("|" + also_sensitive) if also_sensitive else ""), re.I)
    sens_cols = [i for i, h in enumerate(header) if pat.search(h)]
    for r in RECOMMENDED:
        if r not in idx:
            warn("W2", f"recommended column '{r}' is absent")

    id_i, st_i, src_i = idx.get("id"), idx.get("status"), idx.get("source")
    on_i = idx.get("verified on")
    seen: dict[str, int] = {}
    counts = {s: 0 for s in STATUSES}
    counts["INVALID"] = 0              # a row whose Status is not one of the five words
    unknown_in_sensitive = 0

    for line, cells in rows:
        if len(cells) != len(header):
            err("E0", f"row has {len(cells)} cells, header has {len(header)}", line)
            continue
        for i, c in enumerate(cells):
            if not c.strip():
                err("E3", f"blank cell in column '{header[i]}': write UNKNOWN or N/A", line)
            elif VAGUE.search(c) and not is_gap(c):
                warn("W1", f"vague wording in '{header[i]}' ({c!r}): write UNKNOWN", line)
        status = None
        if st_i is not None:
            status = cells[st_i].strip().upper()
            if status and status not in STATUSES:
                err("E2", f"status {cells[st_i]!r} is not one of {', '.join(STATUSES)}", line)
                counts["INVALID"] += 1
                status = None
            elif status:
                counts[status] += 1
        if id_i is not None:
            key = cells[id_i].strip().casefold()
            if key and key in seen:
                err("E4", f"duplicate ID {cells[id_i]!r} (first at line {seen[key]})", line)
            elif key:
                seen[key] = line
        if status in GROUNDED and src_i is not None and (not cells[src_i].strip() or is_gap(cells[src_i])):
            err("E5", f"{status} row has no Source", line)
        if status == "VERIFIED" and on_i is not None and not DATE.match(cells[on_i].strip()):
            err("E6", f"VERIFIED row has no valid 'Verified on' date ({cells[on_i]!r})", line)
        for i in sens_cols:
            v = cells[i].strip()
            if not v:
                continue
            if is_gap(v):
                if v.upper() == "UNKNOWN":      # N/A is not an open question
                    unknown_in_sensitive += 1
            elif status not in GROUNDED:
                err("E7", f"'{header[i]}' holds a value but the row is {status or 'unstatused'}; "
                          "only a VERIFIED or REPORTED row may carry it. Write UNKNOWN", line)

    if counts["ASSUMED"]:
        warn("W3", f"{counts['ASSUMED']} ASSUMED row(s): confirm or turn them into UNKNOWN before this is final")
    return {"rows": len(rows), "columns": header, "sensitive_columns": [header[i] for i in sens_cols],
            "status_counts": counts, "unknown_in_sensitive_columns": unknown_in_sensitive,
            "errors": errors, "warnings": warns}


def render(path: str, rep: dict, strict: bool) -> str:
    L = [f"REGISTER  {path}", f"  rows {rep['rows']}   " +
         " · ".join(f"{k} {v}" for k, v in rep["status_counts"].items() if v)]
    L.append("  sensitive columns (value only on VERIFIED or REPORTED rows): " +
             (", ".join(rep["sensitive_columns"]) or "none matched"))
    for e in rep["errors"]:
        L.append(f"  ERROR {e['code']}" + (f"  line {e['line']}" if e["line"] else "") + f"  {e['message']}")
    for w in rep["warnings"]:
        L.append(f"  warn  {w['code']}" + (f"  line {w['line']}" if w["line"] else "") + f"  {w['message']}")
    bad = len(rep["errors"]) + (len(rep["warnings"]) if strict else 0)
    L.append(f"RESULT  {'FAIL' if bad else 'PASS'}: {len(rep['errors'])} error(s), "
             f"{len(rep['warnings'])} warning(s)" + (" (strict)" if strict else ""))
    if rep["unknown_in_sensitive_columns"]:
        L.append(f"  open questions: {rep['unknown_in_sensitive_columns']} ownership/measurement/price "
                 "cell(s) are UNKNOWN. Each needs a source before it can be filled.")
    L.append("  A pass means the register is well-formed and honest about its gaps. "
             "It does not mean any value is true.")
    return "\n".join(L)


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def run_file(p: Path, **kw):
    header, rows = read_table(p, kw.pop("table", 1))
    return lint(header, rows, **kw)


def selftest() -> int:
    res: list = []

    def check(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    def codes(rep, kind="errors"):
        return {e["code"] for e in rep[kind]}

    # parsing
    check("split_row handles escaped pipes and edges", split_row("| a \\| b | c |") == ["a | b", "c"])
    md = "intro\n```\n| x | y |\n|---|---|\n| 1 | 2 |\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n| c |\n|---|\n| 9 |\n"
    ts = markdown_tables(md)
    check("fenced tables are skipped, real tables found", len(ts) == 2 and ts[0][0][1] == ["a", "b"], str(ts))
    check("date pattern", all(DATE.match(d) for d in ("2026-10-12", "12/10/26")) and not DATE.match("soon"))

    # fixtures
    expect = {
        "good_equipment.md": (set(), set()),
        "bad_equipment.md": ({"E2", "E3", "E4", "E5", "E6", "E7"}, {"W1"}),
        "good_quotes.csv": (set(), set()),
        "bad_quotes.csv": ({"E0", "E3", "E7"}, set()),
        "bad_columns.csv": ({"E1"}, {"W2"}),
    }
    for name, (want_err, want_warn) in expect.items():
        f = FIXTURES / name
        if not f.is_file():
            check(f"fixture {name} exists", False)
            continue
        rep = run_file(f)
        check(f"{name}: errors {sorted(want_err) or 'none'}", codes(rep) == want_err, str(sorted(codes(rep))))
        check(f"{name}: warnings include {sorted(want_warn) or 'none'}", want_warn <= codes(rep, "warnings"),
              str(sorted(codes(rep, "warnings"))))

    # the specific rule the owner cares about: an inferred ownership or rating is refused
    h = ["ID", "Owner", "Rating (kW)", "Status", "Source"]
    rep = lint(h, [(2, ["A-1", "Alex", "UNKNOWN", "ASSUMED", "UNKNOWN"])])
    check("an ASSUMED owner is refused (E7)", "E7" in codes(rep))
    rep = lint(h, [(2, ["A-1", "UNKNOWN", "UNKNOWN", "ASSUMED", "UNKNOWN"])])
    check("the same row with UNKNOWN passes", not rep["errors"], str(rep["errors"]))
    rep = lint(h, [(2, ["A-1", "Alex", "2.2", "REPORTED", "label photo"])])
    check("a REPORTED value with a source is allowed", not rep["errors"], str(rep["errors"]))
    rep = lint(h, [(2, ["A-1", "Alex", "2.2", "REPORTED", "UNKNOWN"])])
    check("a REPORTED value without a source is refused (E5)", "E5" in codes(rep))
    rep = lint(h, [(2, ["A-1", "UNKNOWN", "UNKNOWN", "unknown", "unknown"])])
    check("status and gap words are case-insensitive", not rep["errors"], str(rep["errors"]))
    rep = lint(h, [(2, ["A-1", "UNKNOWN", "about 2", "UNKNOWN", "UNKNOWN"])])
    check("'about 2' in a rating cell is refused as a value (E7)", "E7" in codes(rep))
    rep = lint(["ID", "Status", "Source", "Note"], [(2, ["A", "VERIFIED", "doc", "tbc"])])
    check("a vague word warns (W1)", "W1" in codes(rep, "warnings"))

    # strict mode, counting, output
    rep = lint(["ID", "Status", "Source"], [(2, ["A", "ASSUMED", "UNKNOWN"])])
    check("ASSUMED rows warn (W3) but do not error", "W3" in codes(rep, "warnings") and not rep["errors"])
    check("strict turns that warning into a failure", render("x", rep, True).count("FAIL") == 1
          and "PASS" in render("x", rep, False))
    check("report says a pass does not mean a value is true", "does not mean any value is true" in render("x", rep, False))
    rep = lint(["ID", "Status", "Source"], [(2, ["A", "VERIFIED", "doc"]), (3, ["a", "VERIFIED", "doc"])])
    check("duplicate IDs are caught case-insensitively", "E4" in codes(rep))
    check("json round-trips", json.loads(json.dumps(rep))["rows"] == 2)

    # templates lint clean, and are what --template prints
    for t in ("equipment", "evidence", "quotes"):
        f = TEMPLATES / f"{t}.md"
        ok = f.is_file()
        check(f"template {t} exists", ok)
        if ok:
            rep = run_file(f)
            check(f"template {t} lints clean (no errors, no warnings)",
                  not rep["errors"] and not rep["warnings"], str(rep["errors"] + rep["warnings"]))

    # reading is all it does: a temp file is unchanged and nothing is created beside it
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "r.md"
        p.write_text("| ID | Status | Source |\n|---|---|---|\n| A | UNKNOWN | UNKNOWN |\n", encoding="utf-8")
        before = (p.read_bytes(), sorted(x.name for x in Path(tmp).iterdir()))
        run_file(p)
        check("linting changes nothing", (p.read_bytes(), sorted(x.name for x in Path(tmp).iterdir())) == before)
        try:
            read_table(Path(tmp) / "r.txt")
            check("unsupported file type is refused", False)
        except ValueError:
            check("unsupported file type is refused", True)
        bom = Path(tmp) / "bom.csv"
        bom.write_bytes(b"\xef\xbb\xbfID,Status,Source\r\nA,UNKNOWN,UNKNOWN\r\n")
        rep = run_file(bom)
        check("a spreadsheet CSV with a byte-order mark and CRLF lints clean",
              not rep["errors"] and rep["columns"][0] == "ID", str(rep["errors"] + [rep["columns"]]))

    for name, cond, detail in res:
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if not cond and detail else ""))
    print(f"\n{sum(1 for _, c, _ in res if c)}/{len(res)} checks passed")
    return 0 if all(c for _, c, _ in res) else 1


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="a .md (first pipe table) or .csv register")
    ap.add_argument("--table", type=int, default=1, help="which Markdown table (1-based)")
    ap.add_argument("--strict", action="store_true", help="warnings count as errors")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--require", help="comma-separated required columns "
                                      f"(default {','.join(REQUIRED_DEFAULT)})")
    ap.add_argument("--sensitive", help="regex replacing the default sensitive-column pattern")
    ap.add_argument("--also-sensitive", help="regex added to the sensitive-column pattern")
    ap.add_argument("--template", choices=["equipment", "evidence", "quotes"],
                    help="print a blank register")
    ap.add_argument("--selftest", action="store_true", help="prove the tool against its fixtures")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.template:
        print((TEMPLATES / f"{a.template}.md").read_text(encoding="utf-8"), end="")
        return 0
    if not a.file:
        ap.print_help()
        return 2
    required = tuple(x.strip().casefold() for x in a.require.split(",")) if a.require else REQUIRED_DEFAULT
    try:
        header, rows = read_table(Path(a.file), a.table)
        rep = lint(header, rows, required=required,
                   sensitive=a.sensitive or SENSITIVE_DEFAULT, also_sensitive=a.also_sensitive)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except re.error as e:
        print(f"error: bad pattern: {e}", file=sys.stderr)
        return 2
    print(json.dumps(rep, indent=2) if a.json else render(a.file, rep, a.strict))
    return 1 if rep["errors"] or (a.strict and rep["warnings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
