#!/usr/bin/env python3
"""Owner decisions and project task tracking for the Deez Smart Home repository.

WHY THIS EXISTS

Decisions the owner has already made, and tasks waiting on one, were scattered
across PROJECT_STATE.md, DASHBOARD_BACKLOG.md, design/casaray-v3/DECISIONS.md,
audit reports and pull-request bodies, and a new session had to rediscover them
or ask again. This keeps ONE register of task state and ONE append-only history of
every change, and gives a session four things it did not have: a ranked answer to
"Update me", Approve / Deny / Pause questions it can put to the owner in one
batch, a record that survives the container, and a check that refuses to let
completion or consent be written down without evidence.

It is an INDEX. A task that already has a home record (a backlog item, a V3
decision, an audit finding) keeps its detail there; the register holds the state
of the decision and points at the home.

FILES (the only two this tool ever writes)

  docs/project-tasks/TASK_REGISTER.md      current state, one row per task
  docs/project-tasks/DECISION_HISTORY.md   append-only log of every change

WHAT IT WILL NOT DO, AND THE SELF-TEST PROVES EACH

  * touch the network, Home Assistant, a device, a purchase or a message
  * run any git command that writes (fetch, commit, push, checkout, ...)
  * let an agent record an owner decision (--by must be the owner, --via a
    channel the owner actually used, --basis what they said)
  * let a blanket "approve everything" approve a gated task (safety, external,
    protected): those need a task-specific scope
  * mark a task DONE without VERIFIED evidence it could check or an owner's word
  * delete a task, or edit a past history row (a denied task stays on record)
  * write when the two files already disagree

USAGE

  tasks.py update [--project KEY|--all] [--branch NAME] [--json]     "Update me"
  tasks.py show TASK-001
  tasks.py ask [--ids T,T] [--page N] [--json]                       Approve/Deny/Pause questions
  tasks.py lookup WORDS...                                           prior decisions on a topic
  tasks.py digest [--stale-days 7] [--since DATE] [--json]           for the weekly audit Routine
  tasks.py handover [--project KEY]                                  end-of-session block
  tasks.py check [--append-only-vs REF] [--strict]                   lint both files

  tasks.py init                                                      create the two files
  tasks.py add --project K --priority P1 --title T --home H --evidence-status S --source SRC --next N
  tasks.py raise TASK --next PROPOSAL                                needs an owner decision
  tasks.py decide TASK approve|deny|pause --by owner --via ask-user-question --basis "..."
  tasks.py decide --batch FILE.json|-  [--blanket]                   several answers, atomically
  tasks.py resume TASK[,TASK] --by owner --via chat --basis "..."
  tasks.py start TASK[,TASK] | block TASK --reason R | unblock TASK
  tasks.py complete TASK --source "commit abc1234" --verified-by claude --evidence "..."
  tasks.py reopen TASK --by owner --via chat --basis "..." --new-evidence "..."
  tasks.py edit TASK [--next N] [--priority P] [--gate G] [--evidence-status S --source SRC]
  tasks.py --selftest

EXIT CODES  0 ok   1 refused by policy, or check found errors   2 usage   3 files missing or unreadable
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

REGISTER_REL = "docs/project-tasks/TASK_REGISTER.md"
HISTORY_REL = "docs/project-tasks/DECISION_HISTORY.md"

STATUSES = ("OPEN", "AWAITING_DECISION", "APPROVED", "IN_PROGRESS", "BLOCKED",
            "PAUSED", "DONE", "DENIED")
# Ranking order within a priority: what unblocks other work comes first.
RANK_ORDER = ("AWAITING_DECISION", "IN_PROGRESS", "APPROVED", "OPEN", "BLOCKED")
OUTSTANDING = RANK_ORDER + ("PAUSED",)
CLOSED = ("DONE", "DENIED")
PRIORITIES = ("P0", "P1", "P2", "P3")
GATES = ("none", "safety", "external", "protected")
EVIDENCE_STATUS = ("VERIFIED", "REPORTED", "ASSUMED", "UNKNOWN")
OWNER = {"owner", "ray"}
VIA = ("ask-user-question", "chat", "pr-review")
OWNER_EVENTS = ("APPROVED", "DENIED", "PAUSED", "RESUMED", "REOPENED")
EVENTS = ("ADDED", "RAISED", "APPROVED", "DENIED", "PAUSED", "RESUMED", "STARTED",
          "BLOCKED", "UNBLOCKED", "COMPLETED", "REOPENED", "NOTE")
INITIAL = ("OPEN", "AWAITING_DECISION", "BLOCKED")

TASK_COLS = ["ID", "Project", "P", "Status", "Gate", "Task", "Home", "Evidence",
             "Decision", "Next action", "Updated"]
HIST_COLS = ["ID", "Date", "Task", "Event", "From", "To", "Scope", "Context",
             "Basis", "Via", "By"]
PROJ_COLS = ["Key", "Branches", "Shown", "Name"]

SEP = " · "
NONE = "—"
MAX_CELL = 700
ID_RE = {"TASK": re.compile(r"^TASK-(\d{3,})$"), "DEC": re.compile(r"^DEC-(\d{3,})$")}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# --------------------------------------------------------------------------
# git, read-only
# --------------------------------------------------------------------------

SAFE_GIT = {
    "rev-parse": None, "status": None, "log": None, "ls-files": None,
    "diff": None, "show": None,
    "branch": {"--show-current"},
    "cat-file": {"-e"},
}


class Refused(Exception):
    """A policy refusal: nothing was written."""


class Unreadable(Exception):
    """The register or history cannot be read."""


def git(root: Path, *args: str) -> tuple[int, str]:
    if not args or args[0] not in SAFE_GIT:
        raise Refused(f"git {args[0] if args else ''!r} is not a read-only call")
    allowed = SAFE_GIT[args[0]]
    if allowed is not None and (len(args) < 2 or args[1] not in allowed):
        raise Refused(f"git {' '.join(args[:2])!r} is not permitted")
    if any(a.startswith("--output") for a in args):
        raise Refused("--output writes a file")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, env=env, check=False)
    except FileNotFoundError:
        return 127, ""
    return p.returncode, p.stdout


def repo_root(start: Path) -> Path:
    rc, out = git(start, "rev-parse", "--show-toplevel")
    return Path(out.strip()) if rc == 0 and out.strip() else start


# --------------------------------------------------------------------------
# Markdown tables
# --------------------------------------------------------------------------

def clean(value: object, *, allow_empty: bool = False) -> str:
    """Make a value safe for a table cell: one line, no pipes, never blank."""
    s = str(value).replace("\r", " ").replace("\n", " ").replace("|", "/")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        if allow_empty:
            return ""
        raise Refused("a table cell cannot be blank (write — for not applicable)")
    if len(s) > MAX_CELL:
        raise Refused(f"a cell is {len(s)} characters; the limit is {MAX_CELL}. "
                      "Put the detail in the home record and point at it.")
    return s


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_sep(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


@dataclass
class Block:
    start: int
    end: int                    # exclusive
    header: list
    rows: list                  # [(line_no_1_based, cells)]


def read_blocks(lines: list[str]) -> list[Block]:
    blocks, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            header = split_row(lines[i])
            rows = []
            for k in range(i + 1, j):
                cells = split_row(lines[k])
                if k == i + 1 and is_sep(cells):
                    continue
                rows.append((k + 1, cells))
            blocks.append(Block(i, j, header, rows))
            i = j
        else:
            i += 1
    return blocks


def render_table(cols: list[str], rows: list[dict]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        out.append("| " + " | ".join(r[c] for c in cols) + " |")
    return out


class Doc:
    """A Markdown file whose tables the tool reads and rewrites; prose is kept."""

    def __init__(self, path: Path):
        self.path = path
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise Unreadable(f"{path}: {e}") from e
        if "\r" in text:
            raise Unreadable(f"{path}: has CRLF line endings; convert to LF")
        self.text = text
        self.lines = text.split("\n")

    def table(self, cols: list[str]) -> tuple[list[dict], list[str]]:
        """Return (rows as dicts, problems) for the table whose header is cols."""
        problems = []
        for b in read_blocks(self.lines):
            if b.header == cols:
                rows = []
                for ln, cells in b.rows:
                    if len(cells) != len(cols):
                        problems.append(f"{self.path.name}:{ln}: {len(cells)} cells, expected {len(cols)}")
                        continue
                    d = dict(zip(cols, cells))
                    d["_line"] = ln
                    rows.append(d)
                return rows, problems
        raise Unreadable(f"{self.path}: no table with the header | {' | '.join(cols)} |")

    def set_table(self, cols: list[str], rows: list[dict]) -> None:
        for b in read_blocks(self.lines):
            if b.header == cols:
                self.lines[b.start:b.end] = render_table(cols, rows)
                self.text = "\n".join(self.lines)
                return
        raise Unreadable(f"{self.path}: no table with the header | {' | '.join(cols)} |")


def atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------

@dataclass
class Project:
    key: str
    patterns: list
    shown: str
    name: str


@dataclass
class Store:
    root: Path
    reg_path: Path
    hist_path: Path
    reg_doc: Doc
    hist_doc: Doc
    projects: list
    tasks: list                 # list[dict] with TASK_COLS keys
    events: list                # list[dict] with HIST_COLS keys
    problems: list = field(default_factory=list)

    def task(self, tid: str) -> dict | None:
        return next((t for t in self.tasks if t["ID"] == tid), None)


def load(root: Path, register: Path | None = None, history: Path | None = None) -> Store:
    reg_path = register or root / REGISTER_REL
    hist_path = history or root / HISTORY_REL
    reg_doc, hist_doc = Doc(reg_path), Doc(hist_path)
    problems = []
    prow, p1 = reg_doc.table(PROJ_COLS)
    tasks, p2 = reg_doc.table(TASK_COLS)
    events, p3 = hist_doc.table(HIST_COLS)
    problems += p1 + p2 + p3
    projects = []
    for r in prow:
        pats = [] if r["Branches"] in (NONE, "") else [x.strip() for x in r["Branches"].split(",") if x.strip()]
        projects.append(Project(r["Key"], pats, r["Shown"], r["Name"]))
    return Store(root, reg_path, hist_path, reg_doc, hist_doc, projects, tasks, events, problems)


def resolve_projects(projects: list[Project], branch: str | None) -> tuple[list[str], bool]:
    """Return (project keys to show, resolved?). Cross-cutting projects ride along."""
    matched = [p.key for p in projects if p.shown == "branch" and branch
               and any(fnmatch.fnmatchcase(branch, pat) for pat in p.patterns)]
    if not matched:
        return [p.key for p in projects], False
    return matched + [p.key for p in projects if p.shown == "all" and p.key not in matched], True


def today_str(override: str | None = None) -> str:
    return override or dt.date.today().isoformat()


def parse_date(s: str) -> dt.date | None:
    if not DATE_RE.match(s or ""):
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def age_days(since: str, today: str) -> int | None:
    a, b = parse_date(since), parse_date(today)
    return (b - a).days if a and b else None


def kv(text: str) -> dict:
    """Parse 'gate=protected; p=P1' machine tokens."""
    out = {}
    for part in text.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_evidence(cell: str) -> dict | None:
    """'STATUS · source · YYYY-MM-DD[ · by]' -> dict, or None when malformed."""
    parts = [p.strip() for p in cell.split(SEP.strip())]
    if len(parts) not in (3, 4) or parts[0] not in EVIDENCE_STATUS:
        return None
    if not parse_date(parts[2]) or not parts[1]:
        return None
    return {"status": parts[0], "source": parts[1], "date": parts[2],
            "by": parts[3] if len(parts) == 4 else None}


def make_evidence(status: str, source: str, date: str, by: str | None) -> str:
    if status not in EVIDENCE_STATUS:
        raise Refused(f"evidence status must be one of {', '.join(EVIDENCE_STATUS)}")
    if status == "VERIFIED" and not by:
        raise Refused("VERIFIED evidence needs --verified-by (who observed it)")
    src = clean(source).replace("·", "-")
    return SEP.join([status, src, date] + ([clean(by)] if by else []))


# --------------------------------------------------------------------------
# transitions: one implementation, used by the writers and by the replay linter
# --------------------------------------------------------------------------

@dataclass
class State:
    status: str | None = None
    gate: str = "none"
    p: str = ""
    prior: str | None = None            # status before PAUSED / BLOCKED
    gov: tuple | None = None            # (decision id, verb) governing the task
    gov_stack: tuple | None = None
    last_date: str = ""


def expected_decision_cell(s: State) -> str:
    if s.status == "AWAITING_DECISION":
        return "PENDING"
    return f"{s.gov[0]} {s.gov[1]}" if s.gov else NONE


def step(s: State, event: str, to: str | None = None, *, dec_id: str = "") -> tuple[State, str]:
    """Apply one event to a state. Returns (new state, new status) or raises Refused."""
    cur = s.status
    n = State(**{**s.__dict__})
    gated = s.gate != "none"

    def need(*allowed):
        if cur not in allowed:
            raise Refused(f"{event} is not possible from {cur or 'nothing'} "
                          f"(allowed from: {', '.join(allowed)})")

    if event == "ADDED":
        if cur is not None:
            raise Refused("ADDED on a task that already exists")
        if to not in INITIAL:
            raise Refused(f"a task starts as {', '.join(INITIAL)}, not {to}")
        new = to
    elif event == "RAISED":
        need("OPEN", "BLOCKED")
        new = "AWAITING_DECISION"
    elif event == "APPROVED":
        need("AWAITING_DECISION")
        new = "APPROVED"
        n.gov = (dec_id, "APPROVED")
    elif event == "DENIED":
        need("AWAITING_DECISION", "OPEN", "APPROVED", "IN_PROGRESS", "BLOCKED", "PAUSED")
        new = "DENIED"
        n.gov = (dec_id, "DENIED")
    elif event == "PAUSED":
        need("AWAITING_DECISION", "OPEN", "APPROVED", "IN_PROGRESS", "BLOCKED")
        new = "PAUSED"
        n.prior, n.gov_stack, n.gov = cur, s.gov, (dec_id, "PAUSED")
    elif event == "RESUMED":
        need("PAUSED")
        new = s.prior or "OPEN"
        n.gov, n.gov_stack, n.prior = s.gov_stack, None, None
    elif event == "STARTED":
        need("OPEN", "APPROVED")
        if cur == "OPEN" and gated:
            raise Refused(f"a {s.gate}-gated task cannot start from OPEN: raise it and "
                          "get a specific approval first")
        new = "IN_PROGRESS"
    elif event == "BLOCKED":
        need("OPEN", "APPROVED", "IN_PROGRESS")
        new = "BLOCKED"
        n.prior = cur
    elif event == "UNBLOCKED":
        need("BLOCKED")
        new = s.prior or "OPEN"
        n.prior = None
    elif event == "COMPLETED":
        need("OPEN", "APPROVED", "IN_PROGRESS")
        if cur == "OPEN" and gated:
            raise Refused(f"a {s.gate}-gated task cannot complete from OPEN without an approval")
        new = "DONE"
    elif event == "REOPENED":
        need("DENIED", "DONE")
        new = "AWAITING_DECISION" if (cur == "DENIED" or gated) else "OPEN"
        n.gov = None            # an approval is single-use; the next cycle needs its own
    elif event == "NOTE":
        new = cur or ""
        if cur is None:
            raise Refused("NOTE on a task that does not exist")
    else:
        raise Refused(f"unknown event {event}")
    n.status = new
    return n, new


# --------------------------------------------------------------------------
# replay + lint
# --------------------------------------------------------------------------

@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    info: list = field(default_factory=list)

    def err(self, code, msg):
        self.errors.append((code, msg))

    def warn(self, code, msg):
        self.warnings.append((code, msg))

    def note(self, code, msg):
        self.info.append((code, msg))


SOURCE_KINDS = ("commit", "file", "owner", "pr", "live")


def evidence_source_kind(src: str) -> str | None:
    kind = src.split(" ", 1)[0].lower() if src else ""
    return kind if kind in SOURCE_KINDS else None


def replay(store: Store, rep: Report) -> dict:
    """Replay DECISION_HISTORY and return {task id: State}. Reports every breach."""
    states: dict[str, State] = {}
    seen_ids, prev_n, prev_date = set(), 0, ""
    known = {t["ID"] for t in store.tasks}
    for e in store.events:
        eid, where = e["ID"], f"{store.hist_path.name}:{e.get('_line', 'new')}"
        m = ID_RE["DEC"].match(eid)
        if not m:
            rep.err("E16", f"{where}: {eid!r} is not a DEC-nnn id")
            continue
        if eid in seen_ids:
            rep.err("E16", f"{where}: duplicate {eid}")
        seen_ids.add(eid)
        if int(m.group(1)) != prev_n + 1:
            rep.err("E16", f"{where}: {eid} does not follow DEC-{prev_n:03d} (ids are sequential, never reused)")
        prev_n = int(m.group(1))
        d = parse_date(e["Date"])
        if not d:
            rep.err("E15", f"{where}: {eid} date {e['Date']!r} is not YYYY-MM-DD")
        elif prev_date and e["Date"] < prev_date:
            rep.err("E15", f"{where}: {eid} is dated {e['Date']}, before the row above ({prev_date})")
        prev_date = max(prev_date, e["Date"]) if d else prev_date
        tid, event = e["Task"], e["Event"]
        if tid not in known:
            rep.err("E14", f"{where}: {eid} names {tid}, which is not in the register")
            continue
        if event not in EVENTS:
            rep.err("E05", f"{where}: {eid} event {event!r} is not one of {', '.join(EVENTS)}")
            continue
        s = states.get(tid, State())
        frm = e["From"]
        want_from = NONE if s.status is None else s.status
        if frm != want_from:
            rep.err("E09", f"{where}: {eid} says {tid} moved from {frm}, but replay has it at {want_from}")
        try:
            if event == "ADDED":
                kvs = kv(e["Scope"])
                g, p = kvs.get("gate", ""), kvs.get("p", "")
                if g not in GATES:
                    rep.err("E05", f"{where}: {eid} ADDED needs gate=<{'|'.join(GATES)}> in Scope")
                if p not in PRIORITIES:
                    rep.err("E05", f"{where}: {eid} ADDED needs p=<P0..P3> in Scope")
                s.gate, s.p = (g if g in GATES else "none"), p
            ns, new = step(s, event, e["To"] if event == "ADDED" else None, dec_id=eid)
        except Refused as ex:
            rep.err("E09", f"{where}: {eid} {tid} {event}: {ex}")
            states[tid] = s
            continue
        if e["To"] != new:
            rep.err("E09", f"{where}: {eid} says {tid} moved to {e['To']}, but {event} gives {new}")
        if event in OWNER_EVENTS:
            if e["By"].lower() not in OWNER:
                rep.err("E10", f"{where}: {eid} {event} is an owner decision but By is {e['By']!r}")
            if e["Via"] not in VIA:
                rep.err("E10", f"{where}: {eid} {event} Via must be one of {', '.join(VIA)}, not {e['Via']!r}")
            if len(e["Basis"]) < 8 or e["Basis"] == NONE:
                rep.err("E10", f"{where}: {eid} {event} has no Basis (what the owner actually said or selected)")
            if event in ("DENIED", "PAUSED") and (len(e["Context"]) < 8 or e["Context"] == NONE):
                rep.err("E10", f"{where}: {eid} {event} needs Context (the reason, or what was saved to resume)")
        if event == "APPROVED" and s.gate != "none" and (len(e["Scope"]) < 12 or e["Scope"] == NONE):
            rep.err("E11", f"{where}: {eid} approves {tid}, a {s.gate}-gated task, with no specific Scope")
        if event == "COMPLETED":
            ev = parse_evidence(e["Context"])
            if not ev or ev["status"] != "VERIFIED" or not ev["by"]:
                rep.err("E06", f"{where}: {eid} COMPLETED needs VERIFIED evidence in Context "
                               "(VERIFIED · source · date · by)")
            elif s.gate != "none" and ev["by"].lower() not in OWNER:
                rep.err("E06", f"{where}: {eid} completes a {s.gate}-gated task but is verified by "
                               f"{ev['by']!r}, not the owner")
        if event == "NOTE":
            kvs = kv(e["Scope"])
            if "gate" in kvs:
                if kvs["gate"] not in GATES:
                    rep.err("E05", f"{where}: {eid} NOTE gate={kvs['gate']!r} is not a gate")
                elif s.gate != "none" and kvs["gate"] == "none":
                    rep.err("E11", f"{where}: {eid} loosens {tid} from {s.gate} to none; a gate is only tightened")
                else:
                    ns.gate = kvs["gate"]
            if "p" in kvs:
                if kvs["p"] in PRIORITIES:
                    ns.p = kvs["p"]
                else:
                    rep.err("E05", f"{where}: {eid} NOTE p={kvs['p']!r} is not a priority")
        ns.last_date = e["Date"]
        states[tid] = ns
    return states


def check_home(store: Store, home: str, rep: Report, where: str) -> None:
    if home == "register":
        return
    if home.startswith("pr:") or home.startswith("branch:"):
        if not re.match(r"^(pr:\d+|branch:[^:#\s]+:[^#\s]+)(#.+)?$", home):
            rep.err("E07", f"{where}: Home {home!r} is not pr:N[#anchor] or branch:NAME:path[#anchor]")
        else:
            rep.note("I1", f"{where}: Home {home} is on another branch or PR; not checkable offline")
        return
    path, _, anchor = home.partition("#")
    p = store.root / path
    if not path or not p.is_file():
        rep.err("E07", f"{where}: Home {path!r} is not a file in this tree")
        return
    if anchor:
        try:
            body = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""
        if anchor not in body:
            rep.err("E07", f"{where}: anchor {anchor!r} does not occur in {path}")


def lint(store: Store, *, today: str, stale_days: int = 14, verify_commits: bool = True) -> Report:
    rep = Report()
    for pr in store.problems:
        rep.err("E01", pr)
    keys = {p.key for p in store.projects}
    if not store.projects:
        rep.err("E01", "the Projects table is empty")
    for p in store.projects:
        if p.shown not in ("branch", "all"):
            rep.err("E05", f"project {p.key}: Shown must be branch or all, not {p.shown!r}")
    seen = set()
    for t in store.tasks:
        tid, where = t["ID"], f"{store.reg_path.name}:{t.get('_line', 'new')}"
        if not ID_RE["TASK"].match(tid):
            rep.err("E05", f"{where}: {tid!r} is not a TASK-nnn id")
        if tid in seen:
            rep.err("E04", f"{where}: duplicate {tid}")
        seen.add(tid)
        for c in TASK_COLS:
            if not t[c].strip():
                rep.err("E03", f"{where}: {tid} has a blank {c} cell (write — for not applicable)")
        if t["Project"] not in keys:
            rep.err("E05", f"{where}: {tid} project {t['Project']!r} is not in the Projects table")
        if t["P"] not in PRIORITIES:
            rep.err("E05", f"{where}: {tid} priority {t['P']!r}")
        if t["Status"] not in STATUSES:
            rep.err("E05", f"{where}: {tid} status {t['Status']!r}")
        if t["Gate"] not in GATES:
            rep.err("E05", f"{where}: {tid} gate {t['Gate']!r}")
        if not parse_date(t["Updated"]):
            rep.err("E15", f"{where}: {tid} Updated {t['Updated']!r} is not YYYY-MM-DD")
        ev = parse_evidence(t["Evidence"])
        if not ev:
            rep.err("E06", f"{where}: {tid} Evidence must read STATUS{SEP}source{SEP}YYYY-MM-DD[{SEP}by]")
        else:
            if ev["status"] == "VERIFIED" and not ev["by"]:
                rep.err("E06", f"{where}: {tid} VERIFIED evidence needs a verifier")
            if ev["status"] == "ASSUMED":
                rep.warn("W4", f"{where}: {tid} rests on an ASSUMED fact")
            if t["Status"] == "DONE":
                if ev["status"] != "VERIFIED":
                    rep.err("E06", f"{where}: {tid} is DONE but its evidence is {ev['status']}, not VERIFIED")
                elif t["Gate"] != "none" and (ev["by"] or "").lower() not in OWNER:
                    rep.err("E06", f"{where}: {tid} is {t['Gate']}-gated and DONE but not verified by the owner")
            if verify_commits and ev["status"] == "VERIFIED" and evidence_source_kind(ev["source"]) == "commit":
                sha = ev["source"].split(" ", 1)[1].strip().split()[0] if " " in ev["source"] else ""
                if not commit_exists(store.root, sha):
                    rep.warn("W5", f"{where}: {tid} cites commit {sha!r}, which this clone cannot see "
                                   "(shallow clone, or not fetched)")
        check_home(store, t["Home"], rep, f"{where} {tid}")
    states = replay(store, rep)
    for t in store.tasks:
        tid, where = t["ID"], f"{store.reg_path.name}:{t.get('_line', 'new')}"
        s = states.get(tid)
        if s is None:
            rep.err("E13", f"{where}: {tid} has no history; every task starts with an ADDED row")
            continue
        if s.status != t["Status"]:
            rep.err("E12", f"{where}: {tid} is {t['Status']} in the register but its history ends at "
                           f"{s.status}. One of the two was edited by hand.")
        if s.gate != t["Gate"]:
            rep.err("E12", f"{where}: {tid} gate is {t['Gate']} in the register but {s.gate} in the history")
        if s.p != t["P"]:
            rep.err("E12", f"{where}: {tid} priority is {t['P']} in the register but {s.p} in the history")
        want = expected_decision_cell(s)
        if t["Decision"] != want:
            rep.err("E08", f"{where}: {tid} Decision reads {t['Decision']!r}; the history says {want!r}")
        if s.last_date and t["Updated"] != s.last_date:
            rep.err("E12", f"{where}: {tid} Updated {t['Updated']} but its last event is {s.last_date}")
        if t["Status"] == "AWAITING_DECISION":
            a = age_days(t["Updated"], today)
            if a is not None and a >= stale_days:
                rep.warn("W1", f"{where}: {tid} has waited {a} days for the owner")
        if t["Status"] == "PAUSED":
            until = paused_until(store, tid)
            if until and until <= today:
                rep.warn("W2", f"{where}: {tid} was paused until {until}; that date has come")
    return rep


def commit_exists(root: Path, sha: str) -> bool:
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha or ""):
        return False
    rc, _ = git(root, "cat-file", "-e", f"{sha}^{{commit}}")
    return rc == 0


def paused_until(store: Store, tid: str) -> str | None:
    for e in reversed(store.events):
        if e["Task"] == tid and e["Event"] == "PAUSED":
            m = re.search(r"until:(\d{4}-\d{2}-\d{2})", e["Scope"])
            return m.group(1) if m else None
    return None


def table_rows_of(text: str, cols: list[str]) -> list[list[str]] | None:
    for b in read_blocks(text.split("\n")):
        if b.header == cols:
            return [c for _, c in b.rows]
    return None


def append_only(store: Store, ref: str, rep: Report) -> None:
    """The history may only grow, and no task may disappear (a denied task stays)."""
    def old(rel):
        rc, out = git(store.root, "show", f"{ref}:{rel}")
        return out if rc == 0 else None
    otext = old(HISTORY_REL)
    if otext is None:
        rep.note("I2", f"{HISTORY_REL} is not present at {ref}; nothing to compare")
    else:
        orows = table_rows_of(otext, HIST_COLS) or []
        new = [[e[c] for c in HIST_COLS] for e in store.events]
        if new[:len(orows)] != orows:
            first = next((i for i, (a, b) in enumerate(zip(orows, new)) if a != b), min(len(orows), len(new)))
            rep.err("E17", f"{HISTORY_REL}: row {first + 1} (or an earlier one) differs from {ref}; "
                           "the history is append-only. Correct a mistake with a NOTE row.")
    rtext = old(REGISTER_REL)
    if rtext is None:
        rep.note("I2", f"{REGISTER_REL} is not present at {ref}; nothing to compare")
    else:
        old_ids = {c[0] for c in (table_rows_of(rtext, TASK_COLS) or [])}
        gone = sorted(old_ids - {t["ID"] for t in store.tasks})
        if gone:
            rep.err("E17", f"{REGISTER_REL}: {', '.join(gone)} present at {ref} but missing now; "
                           "tasks are never deleted (a denied task stays on record)")


# --------------------------------------------------------------------------
# writers
# --------------------------------------------------------------------------

def next_id(prefix: str, existing: list[str]) -> str:
    n = max([int(ID_RE[prefix].match(i).group(1)) for i in existing if ID_RE[prefix].match(i)] or [0])
    return f"{prefix}-{n + 1:03d}"


def ensure_consistent(store: Store, today: str) -> None:
    rep = lint(store, today=today, verify_commits=False)
    # A dead Home link (E07) does not make the state untrustworthy, so it does not block a write.
    errs = [(c, m) for c, m in rep.errors if c != "E07"]
    if errs:
        shown = "; ".join(f"{c} {m}" for c, m in errs[:3])
        raise Refused(f"the register and history already disagree ({len(errs)} errors, "
                      f"first: {shown}). Run `tasks.py check`, fix it, then try again.")


def history_row(store: Store, *, date: str, task: str, event: str, frm: str, to: str, scope: str = NONE,
                context: str = NONE, basis: str = NONE, via: str = NONE, by: str) -> dict:
    ids = [e["ID"] for e in store.events]
    row = {"ID": next_id("DEC", ids), "Date": date, "Task": task, "Event": event, "From": frm,
           "To": to, "Scope": clean(scope), "Context": clean(context), "Basis": clean(basis),
           "Via": clean(via), "By": clean(by)}
    return row


def current_state(store: Store, tid: str) -> State:
    """Replay quietly to get the live State for one task."""
    return replay(store, Report()).get(tid, State())


def set_task(store: Store, tid: str, **cells) -> None:
    t = store.task(tid)
    for k, v in cells.items():
        t[k] = clean(v)


def save(store: Store) -> None:
    """Write history first (it is the record), then the register."""
    store.hist_doc.set_table(HIST_COLS, store.events)
    store.reg_doc.set_table(TASK_COLS, store.tasks)
    atomic_write(store.hist_path, store.hist_doc.text)
    atomic_write(store.reg_path, store.reg_doc.text)


def apply_event(store: Store, tid: str, event: str, *, date: str, by: str, to: str | None = None,
                scope: str = NONE, context: str = NONE, basis: str = NONE, via: str = NONE) -> dict:
    t = store.task(tid)
    if t is None:
        raise Refused(f"{tid} is not in the register")
    s = current_state(store, tid)
    row_id = next_id("DEC", [e["ID"] for e in store.events])
    ns, new = step(s, event, to, dec_id=row_id)
    row = history_row(store, date=date, task=tid, event=event, frm=s.status or NONE, to=new, scope=scope,
                      context=context, basis=basis, via=via, by=by)
    ns.last_date = date
    store.events.append(row)
    t["Status"], t["Updated"] = new, date
    t["Decision"] = expected_decision_cell(ns)
    return row


# ---- public operations -----------------------------------------------------

def op_add(store: Store, *, project, priority, title, gate, home, evidence, next_action, status,
           by, date, basis=None, reason=None) -> str:
    if project not in {p.key for p in store.projects}:
        raise Refused(f"project {project!r} is not in the Projects table")
    if priority not in PRIORITIES:
        raise Refused(f"priority must be one of {', '.join(PRIORITIES)}")
    if gate not in GATES:
        raise Refused(f"gate must be one of {', '.join(GATES)}")
    if status not in INITIAL:
        raise Refused(f"a new task starts as {', '.join(INITIAL)}")
    if gate != "none" and status == "OPEN":
        raise Refused(f"a {gate}-gated task cannot start OPEN; add it as AWAITING_DECISION so it "
                      "gets a specific approval")
    if by.lower() in OWNER and not basis:
        raise Refused("an owner-added task needs --basis")
    if status == "BLOCKED" and len((reason or "").strip()) < 8:
        raise Refused("a task added as BLOCKED needs --reason: what it is waiting on")
    tid = next_id("TASK", [t["ID"] for t in store.tasks])
    # Same title already tracked? Refuse the duplicate, point at it.
    for t in store.tasks:
        if t["Task"].strip().lower() == title.strip().lower() and t["Project"] == project:
            raise Refused(f"{t['ID']} already tracks this task in {project}; update it instead")
    if home != "register":
        dup = [t["ID"] for t in store.tasks if t["Home"] == home]
        if dup:
            raise Refused(f"{', '.join(dup)} already points at {home}; one task per home record")
    store.tasks.append({"ID": tid, "Project": project, "P": priority, "Status": status, "Gate": gate,
                        "Task": clean(title), "Home": clean(home), "Evidence": clean(evidence),
                        "Decision": "PENDING" if status == "AWAITING_DECISION" else NONE,
                        "Next action": clean(next_action), "Updated": date, "_line": 0})
    apply_event(store, tid, "ADDED", date=date, by=by, to=status, scope=f"gate={gate}; p={priority}",
                context=(reason if status == "BLOCKED" else f"Home: {home}"),
                basis=basis or (f"Read from {home}" if home != "register" else "Created here"))
    return tid


@dataclass
class Answer:
    task: str
    verdict: str                # approve | deny | pause
    scope: str = ""
    context: str = ""
    resume_when: str = ""
    until: str = ""


def op_decide(store: Store, answers: list[Answer], *, by: str, via: str, basis: str, date: str,
              blanket: bool = False) -> dict:
    """Record the owner's answers atomically. Returns {applied, skipped}."""
    if by.lower() not in OWNER:
        raise Refused(f"only the owner records a decision (--by owner); {by!r} cannot. An agent "
                      "never infers consent: a question with no answer stays AWAITING_DECISION.")
    if via not in VIA:
        raise Refused(f"--via must be a channel the owner used: {', '.join(VIA)}")
    if len((basis or "").strip()) < 8:
        raise Refused("--basis must say what the owner actually answered or selected")
    applied, skipped = [], []
    seen = set()
    for a in answers:
        if a.task in seen:
            raise Refused(f"{a.task} appears twice in one batch")
        seen.add(a.task)
        t = store.task(a.task)
        if t is None:
            raise Refused(f"{a.task} is not in the register")
        v = a.verdict.lower()
        if v not in ("approve", "deny", "pause"):
            raise Refused(f"{a.task}: verdict must be approve, deny or pause")
        gated = t["Gate"] != "none"
        if v == "approve":
            if t["Status"] != "AWAITING_DECISION":
                raise Refused(f"{a.task} is {t['Status']}, not AWAITING_DECISION; there is nothing to approve"
                              + (" (a denied task needs `reopen` with new evidence)" if t["Status"] == "DENIED" else ""))
            if gated and blanket:
                skipped.append((a.task, f"{t['Gate']}-gated: a general approval does not cover it; "
                                        "it needs a specific scope"))
                continue
            if gated and len((a.scope or "").strip()) < 12:
                raise Refused(f"{a.task} is {t['Gate']}-gated: approval must name the exact action it "
                              "authorises (--scope, at least 12 characters). It is single-use.")
        if v == "pause" and len((a.context or "").strip()) < 8:
            raise Refused(f"{a.task}: a pause needs --context, what to keep so it can be resumed")
        if v == "deny" and len((a.context or "").strip()) < 8:
            raise Refused(f"{a.task}: a denial needs --context, the reason, so it is not raised again unchanged")
        event = {"approve": "APPROVED", "deny": "DENIED", "pause": "PAUSED"}[v]
        scope = a.scope or NONE
        if v == "pause":
            bits = []
            if a.resume_when:
                bits.append(f"resume when: {a.resume_when}")
            if a.until:
                if not parse_date(a.until):
                    raise Refused(f"{a.task}: --until must be YYYY-MM-DD")
                bits.append(f"until:{a.until}")
            scope = "; ".join(bits) or NONE
        row = apply_event(store, a.task, event, date=date, by="owner", scope=scope,
                          context=a.context or NONE, basis=basis, via=via)
        applied.append((a.task, row["ID"], event))
    return {"applied": applied, "skipped": skipped}


def op_simple(store: Store, ids: list[str], event: str, *, by: str, date: str, **kw) -> list[str]:
    out = []
    for tid in ids:
        apply_event(store, tid, event, date=date, by=by, **kw)
        out.append(tid)
    return out


def op_owner_event(store: Store, ids: list[str], event: str, *, by: str, via: str, basis: str,
                   date: str, **kw) -> list[str]:
    if by.lower() not in OWNER:
        raise Refused(f"only the owner can {event.lower()} a task (--by owner)")
    if via not in VIA:
        raise Refused(f"--via must be a channel the owner used: {', '.join(VIA)}")
    if len((basis or "").strip()) < 8:
        raise Refused("--basis must say what the owner actually answered or selected")
    done = []
    for tid in ids:
        apply_event(store, tid, event, date=date, by="owner", via=via, basis=basis, **kw)
        done.append(tid)
    return done


def op_complete(store: Store, tid: str, *, source: str, verified_by: str, evidence: str, date: str,
                next_action: str | None) -> None:
    t = store.task(tid)
    if t is None:
        raise Refused(f"{tid} is not in the register")
    kind = evidence_source_kind(source)
    if kind is None:
        raise Refused("completion evidence must name its source: `commit <sha>`, `file <path>`, "
                      "`owner <what they confirmed>`, `pr <n>` or `live <what was seen>`")
    rest = source.split(" ", 1)[1].strip() if " " in source else ""
    by = verified_by.strip()
    if kind == "commit" and not commit_exists(store.root, rest.split()[0] if rest else ""):
        raise Refused(f"commit {rest!r} does not exist in this clone; evidence is not accepted on faith")
    if kind == "file" and not (store.root / rest).is_file():
        raise Refused(f"file {rest!r} does not exist; evidence is not accepted on faith")
    if kind in ("owner", "pr", "live") and by.lower() not in OWNER:
        raise Refused(f"a `{kind}` source cannot be observed by an agent; it needs --verified-by owner. "
                      "If only the owner can confirm it, leave the task IN_PROGRESS and say so in --next.")
    if not rest:
        raise Refused("the evidence source names nothing after its kind")
    if t["Gate"] != "none" and by.lower() not in OWNER:
        raise Refused(f"{tid} is {t['Gate']}-gated: only the owner can verify it is done")
    ev = make_evidence("VERIFIED", source, date, by)
    apply_event(store, tid, "COMPLETED", date=date, by=by, context=ev, scope=NONE,
                basis=clean(evidence or source))
    t["Evidence"] = ev
    t["Next action"] = clean(next_action or "Done. Nothing further.")


# --------------------------------------------------------------------------
# reading: update, ask, show, lookup, digest, handover
# --------------------------------------------------------------------------

def rank_key(t: dict) -> tuple:
    order = {s: i for i, s in enumerate(RANK_ORDER)}
    return (PRIORITIES.index(t["P"]) if t["P"] in PRIORITIES else 9,
            order.get(t["Status"], 9), t["Updated"], t["ID"])


def pause_info(store: Store, tid: str) -> dict:
    for e in reversed(store.events):
        if e["Task"] == tid and e["Event"] == "PAUSED":
            return {"decision": e["ID"], "date": e["Date"], "context": e["Context"],
                    "resume_when": re.sub(r"\s*;?\s*until:\S+", "", e["Scope"]).replace("resume when: ", "").strip(" ;"),
                    "until": paused_until(store, tid)}
    return {}


def last_blocker(store: Store, tid: str) -> str:
    for e in reversed(store.events):
        if e["Task"] == tid and (e["Event"] == "BLOCKED" or (e["Event"] == "ADDED" and e["To"] == "BLOCKED")):
            return e["Context"]
    return ""


def build_update(store: Store, branch: str | None, project: str | None, show_all: bool,
                 today: str, statuses: list[str] | None = None, include_closed: bool = False,
                 gate: str | None = None, limit: int | None = None) -> dict:
    if show_all:
        keys, resolved = [p.key for p in store.projects], True
    elif project:
        if project not in {p.key for p in store.projects}:
            raise Refused(f"unknown project {project!r}; known: {', '.join(p.key for p in store.projects)}")
        keys = [project] + [p.key for p in store.projects if p.shown == "all" and p.key != project]
        resolved = True
    else:
        keys, resolved = resolve_projects(store.projects, branch)
    mine = [t for t in store.tasks if t["Project"] in keys]
    other = {}
    for t in store.tasks:
        if t["Project"] not in keys and t["Status"] in OUTSTANDING:
            other[t["Project"]] = other.get(t["Project"], 0) + 1
    want = list(statuses) if statuses else list(OUTSTANDING) + (list(CLOSED) if include_closed else [])
    sel = [t for t in mine if t["Status"] in want and (not gate or t["Gate"] == gate)]
    counts = {s: sum(1 for t in mine if t["Status"] == s) for s in STATUSES}
    ranked_all = sorted([t for t in sel if t["Status"] != "PAUSED"], key=rank_key)
    paused = sorted([t for t in sel if t["Status"] == "PAUSED"], key=rank_key)
    closed_sel = sorted([t for t in sel if t["Status"] in CLOSED], key=rank_key)
    ranked = [t for t in ranked_all if t["Status"] not in CLOSED]
    if limit:
        ranked = ranked[:limit]
    return {"today": today, "branch": branch, "projects": keys, "resolved": resolved,
            "counts": counts, "ranked": ranked, "paused": paused, "closed": closed_sel,
            "other_projects": other,
            "blockers": [t for t in ranked_all if t["Status"] in ("AWAITING_DECISION", "BLOCKED")],
            "last_change": max([t["Updated"] for t in mine] or [NONE])}


def question_for(t: dict, store: Store) -> dict:
    gated = t["Gate"] != "none"
    prop = t["Next action"] if len(t["Next action"]) <= 300 else t["Next action"][:297] + "..."
    q = (f"{t['ID']} · {t['P']} · {t['Task']}. Proposal: {prop} "
         + (f"[{t['Gate']}-gated: approving covers only this exact action, once.] " if gated else "")
         + "Approve, deny or pause?")
    return {"question": q, "header": t["ID"], "multiSelect": False, "options": [
        {"label": "Approve", "description":
            ("Authorise exactly the proposal above, once. It does not extend to anything else"
             if gated else "Go ahead with the proposal above")},
        {"label": "Deny", "description": "Drop it. Kept on record with your reason; not raised again unless something changes"},
        {"label": "Pause", "description": "Hold it. What it needs to resume is saved; nothing is lost"},
    ]}


def build_ask(store: Store, ids: list[str] | None, branch: str | None, project: str | None,
              page: int = 1, per_page: int = 4) -> dict:
    keys = [project] if project else resolve_projects(store.projects, branch)[0]
    pool = [t for t in store.tasks if t["Project"] in keys] if not ids else [store.task(i) for i in ids]
    if ids and any(t is None for t in pool):
        raise Refused("unknown task in --ids")
    awaiting = sorted([t for t in pool if t["Status"] == "AWAITING_DECISION"], key=rank_key)
    reused = []
    for t in pool:
        if t["Status"] != "AWAITING_DECISION" and t["Decision"] not in (NONE, "PENDING"):
            reused.append({"task": t["ID"], "status": t["Status"], "decision": t["Decision"],
                           "note": "already decided; not asked again"})
    not_awaiting = [{"task": t["ID"], "status": t["Status"]} for t in pool
                    if ids and t["Status"] != "AWAITING_DECISION"]
    pages = max(1, -(-len(awaiting) // per_page))
    page = max(1, min(page, pages))
    chunk = awaiting[(page - 1) * per_page: page * per_page]
    return {"questions": [question_for(t, store) for t in chunk], "page": page, "pages": pages,
            "total_awaiting": len(awaiting), "reused": reused, "not_awaiting": not_awaiting,
            "apply_with": "tasks.py decide --batch FILE.json  (task, verdict, scope, context) "
                          "--by owner --via ask-user-question --basis '<their selections>'"}


def next_actions(u: dict, store: Store) -> list[dict]:
    """Selectable next actions for 'Update me'. Each is {key,label,description,tasks}."""
    r = u["ranked"]
    decide = [t for t in r if t["Status"] == "AWAITING_DECISION"]
    work = [t for t in r if t["Status"] in ("IN_PROGRESS", "APPROVED") or
            (t["Status"] == "OPEN" and t["Gate"] == "none")]
    acts = []
    if decide:
        acts.append({"key": "decide", "label": f"Decide ({len(decide)})",
                     "description": "Approve, deny or pause the pending decisions, highest priority first: "
                                    + ", ".join(t["ID"] for t in decide[:4]) + (" …" if len(decide) > 4 else ""),
                     "tasks": [t["ID"] for t in decide]})
    if work:
        acts.append({"key": "work", "label": f"Work ({len(work)})",
                     "description": "Pick up work that needs no decision: "
                                    + ", ".join(t["ID"] for t in work[:4]) + (" …" if len(work) > 4 else ""),
                     "tasks": [t["ID"] for t in work]})
    if u["paused"]:
        acts.append({"key": "resume", "label": f"Resume ({len(u['paused'])})",
                     "description": "Resume paused tasks with their saved context: "
                                    + ", ".join(t["ID"] for t in u["paused"][:4]),
                     "tasks": [t["ID"] for t in u["paused"]]})
    if u["other_projects"]:
        acts.append({"key": "switch", "label": "Another project",
                     "description": "Show " + ", ".join(f"{k} ({n})" for k, n in sorted(u["other_projects"].items())),
                     "tasks": []})
    return acts


def selection_payload(u: dict, store: Store) -> dict:
    """AskUserQuestion payload: what to take on next, and which tasks (multi-select)."""
    acts = next_actions(u, store)
    if not acts:
        return {"questions": []}
    qs = []
    opts = acts[:4]
    if len(opts) < 2:
        opts = opts + [{"key": "none", "label": "Nothing now", "description": "Leave everything as it is", "tasks": []}]
    qs.append({"question": "What should I take on next? You can pick more than one.",
               "header": "Next action", "multiSelect": True,
               "options": [{"label": a["label"], "description": a["description"]} for a in opts[:4]]})
    pick = [t for t in u["ranked"] if t["Status"] in ("IN_PROGRESS", "APPROVED", "OPEN", "AWAITING_DECISION")][:4]
    if len(pick) >= 2:
        qs.append({"question": "Which of the top-ranked tasks should I start with? You can pick several.",
                   "header": "Tasks", "multiSelect": True,
                   "options": [{"label": t["ID"], "description": f"{t['P']} · {t['Status'].lower().replace('_', ' ')} · {t['Task']}"[:200]}
                               for t in pick]})
    return {"questions": qs}


def wrap(text: str, indent: str, width: int = 100) -> list[str]:
    return textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent) or [indent]


def shorten(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render_update(u: dict, store: Store, detail: bool = False) -> str:
    c = u["counts"]
    L = [f"UPDATE ME   project: {', '.join(u['projects'])}"
         + ("" if u["resolved"] else "   [branch did not identify a project: showing all; say which one you are on]"),
         f"            branch: {u['branch'] or '(unknown)'}   as of {u['today']}   "
         f"register last changed {u['last_change']}", ""]
    out = sum(c[s] for s in OUTSTANDING)
    L.append(f"OUTSTANDING {out}   awaiting your decision {c['AWAITING_DECISION']} · in progress {c['IN_PROGRESS']} · "
             f"approved {c['APPROVED']} · open {c['OPEN']} · blocked {c['BLOCKED']} · paused {c['PAUSED']}")
    L.append(f"ON RECORD   done {c['DONE']} · denied {c['DENIED']}   (kept; --include-closed lists them)")
    L.append("")
    if not u["ranked"] and not u["paused"]:
        L.append("Nothing outstanding for this selection.")
    else:
        L.append("RANKED BY PRIORITY")
    for i, t in enumerate(u["ranked"], 1):
        gate = f" [{t['Gate']}]" if t["Gate"] != "none" else ""
        L.append(f"{i:>3}  {t['P']}  {t['ID']}  {t['Status']}{gate}  {t['Task']}")
        age = age_days(t["Updated"], u["today"])
        if detail:
            L.append(f"          evidence {t['Evidence']}"
                     + (f"   (last change {age}d ago)" if age is not None else ""))
            if t["Status"] == "AWAITING_DECISION":
                L.append("          needs: your decision (Approve / Deny / Pause)")
            if t["Status"] == "BLOCKED":
                L.append(f"          blocked by: {last_blocker(store, t['ID']) or 'not recorded'}")
            L += wrap("next: " + t["Next action"], "          ")
            L.append(f"          home: {t['Home']}")
        else:
            ev = parse_evidence(t["Evidence"])
            bits = [f"{ev['status']} {ev['date']}" if ev else "evidence malformed", t["Home"]]
            if t["Status"] == "AWAITING_DECISION":
                bits.append("needs your decision")
            if t["Status"] == "BLOCKED":
                bits.append("blocked: " + (last_blocker(store, t["ID"]) or "not recorded"))
            if age:
                bits.append(f"changed {age}d ago")
            L += wrap(" · ".join(bits), "          ")
            L += wrap("next: " + shorten(t["Next action"], 230), "          ")
    for t in u["closed"]:
        L.append(f"  -  {t['P']}  {t['ID']}  {t['Status']}  {t['Task']}   ({t['Decision']})")
    if u["blockers"]:
        L += ["", "BLOCKERS"]
        for t in u["blockers"]:
            why = ("waiting on the owner" if t["Status"] == "AWAITING_DECISION"
                   else f"blocked: {last_blocker(store, t['ID']) or 'reason not recorded'}")
            L.append(f"  {t['ID']}  {t['P']}  {why}")
    if u["paused"]:
        L += ["", "PAUSED   (context is saved; select Resume to pick one up)"]
        for t in u["paused"]:
            p = pause_info(store, t["ID"])
            L.append(f"  {t['ID']}  {t['P']}  {t['Task']}")
            L += wrap(f"saved {p.get('date', '?')} ({p.get('decision', '?')}): {p.get('context', '?')}", "      ")
            if p.get("resume_when"):
                L += wrap(f"resume when: {p['resume_when']}", "      ")
            if p.get("until"):
                L.append(f"      until: {p['until']}" + ("   <- date reached" if p["until"] <= u["today"] else ""))
    acts = next_actions(u, store)
    L += ["", "NEXT ACTIONS   (select any; more than one is fine)"]
    for i, a in enumerate(acts, 1):
        L += wrap(f"[{i}] {a['label']}: {a['description']}", "  ")
    if not acts:
        L.append("  none: nothing outstanding")
    return "\n".join(L)


def render_show(t: dict, store: Store) -> str:
    L = [f"{t['ID']}  {t['P']}  {t['Status']}  gate={t['Gate']}  project={t['Project']}", f"  {t['Task']}",
         f"  home      {t['Home']}", f"  evidence  {t['Evidence']}", f"  decision  {t['Decision']}",
         f"  next      {t['Next action']}", f"  updated   {t['Updated']}", "  history"]
    for e in store.events:
        if e["Task"] == t["ID"]:
            extra = "; ".join(x for x in (e["Scope"], e["Context"]) if x != NONE)
            L.append(f"    {e['ID']}  {e['Date']}  {e['Event']:<10} {e['From']} -> {e['To']}  by {e['By']}"
                     + (f"  ({e['Via']})" if e["Via"] != NONE else ""))
            if extra:
                L += wrap(extra, "          ")
    return "\n".join(L)


def lookup(store: Store, words: list[str]) -> dict:
    ws = [w.lower() for w in words if w.strip()]
    def hit(*cells):
        blob = " ".join(cells).lower()
        return ws and all(w in blob for w in ws)
    tasks = [t for t in store.tasks if hit(t["ID"], t["Task"], t["Home"], t["Next action"])]
    events = [e for e in store.events if hit(e["Task"], e["Scope"], e["Context"], e["Basis"])]
    out = []
    for t in tasks:
        confirmed = t["Decision"] not in (NONE, "PENDING")
        out.append({"task": t["ID"], "status": t["Status"], "decision": t["Decision"], "title": t["Task"],
                    "reuse": ("CONFIRMED: reuse it, do not ask again unless the circumstances changed"
                              if confirmed else "no confirmed decision: ask once, in a batch"
                              if t["Status"] != "AWAITING_DECISION" else "decision pending: it is already queued")})
    return {"tasks": out, "events": [{k: e[k] for k in ("ID", "Date", "Task", "Event", "Context", "Basis")} for e in events][-8:]}


def build_digest(store: Store, today: str, stale_days: int, since: str | None) -> dict:
    pend = sorted([t for t in store.tasks if t["Status"] == "AWAITING_DECISION"], key=rank_key)
    items = []
    for t in pend:
        a = age_days(t["Updated"], today)
        items.append({"id": t["ID"], "project": t["Project"], "p": t["P"], "gate": t["Gate"], "task": t["Task"],
                      "proposal": t["Next action"], "home": t["Home"], "age_days": a,
                      "stale": a is not None and a >= stale_days})
    due = []
    for t in store.tasks:
        if t["Status"] == "PAUSED":
            u = paused_until(store, t["ID"])
            if u and u <= today:
                due.append({"id": t["ID"], "task": t["Task"], "until": u})
    new = [{"id": e["ID"], "date": e["Date"], "task": e["Task"], "event": e["Event"], "by": e["By"]}
           for e in store.events if since and e["Date"] >= since and e["Event"] != "NOTE"]
    blocked = [{"id": t["ID"], "task": t["Task"], "why": last_blocker(store, t["ID"])}
               for t in store.tasks if t["Status"] == "BLOCKED"]
    counts = {s: sum(1 for t in store.tasks if t["Status"] == s) for s in STATUSES}
    return {"today": today, "stale_days": stale_days, "since": since, "pending": items, "paused_due": due,
            "blocked": blocked, "activity_since": new, "counts": counts}


def render_digest(d: dict) -> str:
    L = [f"## Items requiring approval  (from {REGISTER_REL}, as of {d['today']})", ""]
    if not d["pending"]:
        L.append("None. Nothing is awaiting an owner decision.")
    else:
        stale = sum(1 for i in d["pending"] if i["stale"])
        L.append(f"{len(d['pending'])} awaiting a decision; {stale} waiting {d['stale_days']} days or more. "
                 "Each is answered Approve / Deny / Pause; nothing here has been decided by this report.")
        L.append("")
        L.append("| Task | P | Gate | Waiting | Decision needed | Home |")
        L.append("|---|---|---|---|---|---|")
        for i in d["pending"]:
            wait = f"{i['age_days']}d" + (" **stale**" if i["stale"] else "") if i["age_days"] is not None else "?"
            L.append(f"| {i['id']} | {i['p']} | {i['gate']} | {wait} | {i['task']}: {i['proposal']} | {i['home']} |")
    if d["paused_due"]:
        L += ["", "### Paused tasks whose resume date has come", ""]
        L += [f"- {x['id']} {x['task']} (until {x['until']})" for x in d["paused_due"]]
    if d["blocked"]:
        L += ["", "### Blocked", ""]
        L += [f"- {x['id']} {x['task']}: {x['why'] or 'reason not recorded'}" for x in d["blocked"]]
    if d["since"]:
        L += ["", f"### Register activity since {d['since']}", ""]
        L += [f"- {x['date']} {x['id']} {x['task']} {x['event']} (by {x['by']})" for x in d["activity_since"]] \
            or ["- none"]
    c = d["counts"]
    L += ["", "On record: " + " · ".join(f"{s.lower().replace('_', ' ')} {c[s]}" for s in STATUSES)]
    return "\n".join(L)


def render_handover(store: Store, keys: list[str], today: str, branch: str | None) -> str:
    mine = [t for t in store.tasks if t["Project"] in keys]
    L = [f"SESSION HANDOVER   {', '.join(keys)}   {today}   branch {branch or '(unknown)'}", ""]
    def section(title, rows, fmt):
        L.append(title)
        if not rows:
            L.append("  none")
        for r in rows:
            L.extend(wrap(fmt(r), "  "))
        L.append("")
    section("IN FLIGHT", sorted([t for t in mine if t["Status"] == "IN_PROGRESS"], key=rank_key),
            lambda t: f"{t['ID']} {t['P']} {t['Task']} — next: {t['Next action']}")
    section("WAITING ON THE OWNER", sorted([t for t in mine if t["Status"] == "AWAITING_DECISION"], key=rank_key),
            lambda t: f"{t['ID']} {t['P']} {t['Task']} (waiting {age_days(t['Updated'], today)}d)")
    section("PAUSED (resume context saved)", sorted([t for t in mine if t["Status"] == "PAUSED"], key=rank_key),
            lambda t: f"{t['ID']} {t['Task']} — {pause_info(store, t['ID']).get('context', '?')}")
    section("BLOCKED", [t for t in mine if t["Status"] == "BLOCKED"],
            lambda t: f"{t['ID']} {t['Task']} — {last_blocker(store, t['ID']) or 'reason not recorded'}")
    section(f"RECORDED TODAY ({today})", [e for e in store.events if e["Date"] == today and e["Task"] in {t["ID"] for t in mine}],
            lambda e: f"{e['ID']} {e['Task']} {e['Event']} ({e['From']} -> {e['To']}) by {e['By']}")
    rc, out = git(store.root, "status", "--porcelain", "--", REGISTER_REL, HISTORY_REL)
    if rc != 0:
        L.append("PERSISTENCE  could not read git status; commit the two files yourself.")
    elif out.strip():
        L.append("PERSISTENCE  NOT SAVED: the register or history has uncommitted changes. This container is")
        L.append("             reclaimed when the session ends, so commit them with the work and push to the")
        L.append("             branch session-orient names. Until then none of this survives.")
        L += ["             " + l for l in out.strip().splitlines()]
    else:
        L.append("PERSISTENCE  the register and history match the last commit. Whether that commit is pushed")
        L.append("             is not checked here (offline); `git status -sb` shows ahead/behind.")
    return "\n".join(L)


def summary(root: Path, branch: str | None) -> dict:
    """What session-orient prints: counts for the project this branch identifies."""
    store = load(root)
    u = build_update(store, branch, None, False, today_str())
    c = u["counts"]
    return {"projects": u["projects"], "resolved": u["resolved"], "counts": c,
            "outstanding": sum(c[s] for s in OUTSTANDING), "awaiting": c["AWAITING_DECISION"],
            "paused": c["PAUSED"], "register": REGISTER_REL}


# --------------------------------------------------------------------------
# templates
# --------------------------------------------------------------------------

REGISTER_TEMPLATE = """# Task register

The current state of every tracked task and owner decision, across projects.
One row per task. **This is an index, not a second backlog:** a task that already
has a home record (a backlog item, a V3 decision, an audit finding) keeps its
detail there, and the row says where (`Home`) and what state the decision is in.

- Every change is logged in [DECISION_HISTORY.md](DECISION_HISTORY.md), which
  only grows. `tasks.py check` fails if the two files disagree.
- Edit with `python3 .claude/skills/owner-decisions/scripts/tasks.py` (the
  `owner-decisions` skill). Say **"Update me"** for the ranked list.
- Status, gates, evidence and the transition rules:
  `.claude/skills/owner-decisions/references/lifecycle.md`.
- Evidence reads `STATUS · source · date · by`. A task is DONE only on VERIFIED
  evidence. Statuses written here from another record are REPORTED: read from
  that record, not independently re-checked.

## Projects

| Key | Branches | Shown | Name |
|---|---|---|---|
{projects}

## Tasks

| ID | Project | P | Status | Gate | Task | Home | Evidence | Decision | Next action | Updated |
|---|---|---|---|---|---|---|---|---|---|---|
"""

HISTORY_TEMPLATE = """# Decision history

Append-only. One row for every change to a task's status: who did it, when, on
what basis, and for approvals, exactly what was authorised. A row is never edited
or removed; a mistake is corrected with a later `NOTE` row. Denied and paused
tasks stay here with their reasons and saved context.

`tasks.py check --append-only-vs <ref>` fails if an earlier row has changed.
Owner rows (`APPROVED`, `DENIED`, `PAUSED`, `RESUMED`, `REOPENED`) are written
only from what the owner actually answered; no answer means no decision.

| ID | Date | Task | Event | From | To | Scope | Context | Basis | Via | By |
|---|---|---|---|---|---|---|---|---|---|---|
"""

DEFAULT_PROJECTS = [
    ("casaray-v3", "casaray-v3-design, casaray-v3/agent-*", "branch", "CasaRay V3 design"),
    ("casaray-v2", "ha-deploy, autonomous/*", "branch", "CasaRay V2 dashboards and deployment"),
    ("recovery", "recovery/*", "branch", "Recovery and live-system owner actions"),
    ("tooling", NONE, "all", "Skills, audits and workflow tooling (shown on every branch)"),
]


def op_init(root: Path, register: Path, history: Path) -> None:
    for p in (register, history):
        if p.exists():
            raise Refused(f"{p} already exists; init never overwrites")
    register.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| {k} | {b} | {s} | {n} |" for k, b, s, n in DEFAULT_PROJECTS)
    atomic_write(register, REGISTER_TEMPLATE.replace("{projects}", rows))
    atomic_write(history, HISTORY_TEMPLATE)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def out_json(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def render_check(rep: Report, strict: bool) -> str:
    L = []
    for c, m in rep.errors:
        L.append(f"ERROR   {c}  {m}")
    for c, m in rep.warnings:
        L.append(f"WARN    {c}  {m}")
    for c, m in rep.info:
        L.append(f"info    {c}  {m}")
    bad = bool(rep.errors) or (strict and bool(rep.warnings))
    L.append(f"{'FAIL' if bad else 'PASS'}  {len(rep.errors)} errors, {len(rep.warnings)} warnings, {len(rep.info)} notes")
    return "\n".join(L)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="tasks.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="repository root (default: from the current directory)")
    ap.add_argument("--register", help="override the register path")
    ap.add_argument("--history", help="override the history path")
    ap.add_argument("--today", help="treat this as today (YYYY-MM-DD)")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    def common(p, project=True):
        if project:
            p.add_argument("--project")
        p.add_argument("--branch", help="simulate this branch name")
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("update"); common(p)
    p.add_argument("--detail", action="store_true", help="full evidence and next action for every task")
    p.add_argument("--all", action="store_true"); p.add_argument("--status")
    p.add_argument("--gate"); p.add_argument("--include-closed", action="store_true")
    p.add_argument("--limit", type=int); p.add_argument("--select", action="store_true",
                                                         help="emit the AskUserQuestion payload as JSON")
    p = sub.add_parser("show"); p.add_argument("task")
    p = sub.add_parser("ask"); common(p); p.add_argument("--ids"); p.add_argument("--page", type=int, default=1)
    p = sub.add_parser("lookup"); p.add_argument("words", nargs="+"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("digest"); p.add_argument("--stale-days", type=int, default=7)
    p.add_argument("--since"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("handover"); common(p)
    p = sub.add_parser("check"); p.add_argument("--append-only-vs", metavar="REF")
    p.add_argument("--strict", action="store_true"); p.add_argument("--stale-days", type=int, default=14)
    p.add_argument("--json", action="store_true")
    sub.add_parser("init")

    p = sub.add_parser("add")
    for a in ("project", "priority", "title", "home", "next", "source"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--gate", default="none"); p.add_argument("--status", default="OPEN")
    p.add_argument("--evidence-status", required=True); p.add_argument("--verified-by")
    p.add_argument("--by", default="claude"); p.add_argument("--basis")
    p.add_argument("--reason", help="required with --status BLOCKED: what it is waiting on")
    p = sub.add_parser("raise"); p.add_argument("task"); p.add_argument("--next", required=True)
    p.add_argument("--by", default="claude")
    p = sub.add_parser("decide"); p.add_argument("task", nargs="?"); p.add_argument("verdict", nargs="?")
    p.add_argument("--batch"); p.add_argument("--blanket", action="store_true")
    for a in ("by", "via", "basis", "scope", "context", "resume-when", "until"):
        p.add_argument("--" + a)
    p = sub.add_parser("resume"); p.add_argument("tasks")
    for a in ("by", "via", "basis", "next"):
        p.add_argument("--" + a)
    p = sub.add_parser("reopen"); p.add_argument("task")
    for a in ("by", "via", "basis", "new-evidence", "next"):
        p.add_argument("--" + a)
    p = sub.add_parser("start"); p.add_argument("tasks"); p.add_argument("--by", default="claude")
    p.add_argument("--next")
    p = sub.add_parser("block"); p.add_argument("task"); p.add_argument("--reason", required=True)
    p.add_argument("--by", default="claude")
    p = sub.add_parser("unblock"); p.add_argument("task"); p.add_argument("--by", default="claude")
    p.add_argument("--next")
    p = sub.add_parser("complete"); p.add_argument("task")
    p.add_argument("--source", required=True); p.add_argument("--verified-by", required=True)
    p.add_argument("--evidence", default=""); p.add_argument("--next")
    p = sub.add_parser("edit"); p.add_argument("task"); p.add_argument("--next"); p.add_argument("--priority")
    p.add_argument("--gate"); p.add_argument("--evidence-status"); p.add_argument("--source")
    p.add_argument("--verified-by"); p.add_argument("--by", default="claude"); p.add_argument("--note")
    return ap


def current_branch(root: Path, override: str | None) -> str | None:
    if override is not None:
        return override
    rc, out = git(root, "branch", "--show-current")
    return out.strip() or None if rc == 0 else None


def write_cmd(args, root: Path, today: str) -> int:
    reg = Path(args.register) if args.register else None
    hist = Path(args.history) if args.history else None
    store = load(root, reg, hist)
    ensure_consistent(store, today)
    c = args.cmd
    msg = ""
    if c == "add":
        ev = make_evidence(args.evidence_status, args.source, today, args.verified_by)
        tid = op_add(store, project=args.project, priority=args.priority, title=args.title, gate=args.gate,
                     home=args.home, evidence=ev, next_action=args.next, status=args.status, by=args.by,
                     date=today, basis=args.basis, reason=args.reason)
        msg = f"added {tid}"
    elif c == "raise":
        t = store.task(args.task)
        apply_event(store, args.task, "RAISED", date=today, by=args.by, context=args.next)
        t["Next action"] = clean(args.next)
        msg = f"{args.task} is now AWAITING_DECISION; put it to the owner as Approve / Deny / Pause"
    elif c == "decide":
        if args.batch:
            raw = sys.stdin.read() if args.batch == "-" else Path(args.batch).read_text(encoding="utf-8")
            data = json.loads(raw)
            answers = [Answer(task=d["task"], verdict=d["verdict"], scope=d.get("scope", ""),
                              context=d.get("context", ""), resume_when=d.get("resume_when", ""),
                              until=d.get("until", "")) for d in (data["answers"] if isinstance(data, dict) else data)]
        else:
            if not args.task or not args.verdict:
                raise Refused("decide needs TASK and approve|deny|pause, or --batch FILE")
            answers = [Answer(args.task, args.verdict, args.scope or "", args.context or "",
                              args.resume_when or "", args.until or "")]
        res = op_decide(store, answers, by=args.by or "", via=args.via or "", basis=args.basis or "",
                        date=today, blanket=args.blanket)
        msg = "; ".join(f"{t} {e} ({d})" for t, d, e in res["applied"]) or "nothing applied"
        for t, why in res["skipped"]:
            msg += f"\nNOT APPLIED {t}: {why}"
    elif c == "resume":
        ids = [x.strip() for x in args.tasks.split(",") if x.strip()]
        op_owner_event(store, ids, "RESUMED", by=args.by or "", via=args.via or "", basis=args.basis or "", date=today)
        if args.next:
            for i in ids:
                store.task(i)["Next action"] = clean(args.next)
        msg = "resumed " + ", ".join(ids)
    elif c == "reopen":
        if len((args.new_evidence or "").strip()) < 8:
            raise Refused("reopen needs --new-evidence: what changed since it was denied or finished")
        op_owner_event(store, [args.task], "REOPENED", by=args.by or "", via=args.via or "",
                       basis=args.basis or "", date=today, context=args.new_evidence)
        if args.next:
            store.task(args.task)["Next action"] = clean(args.next)
        msg = f"reopened {args.task}"
    elif c == "start":
        ids = [x.strip() for x in args.tasks.split(",") if x.strip()]
        for i in ids:   # validate all before writing any
            step(current_state(store, i), "STARTED")
        op_simple(store, ids, "STARTED", by=args.by, date=today)
        if args.next:
            for i in ids:
                store.task(i)["Next action"] = clean(args.next)
        msg = "started " + ", ".join(ids)
    elif c == "block":
        apply_event(store, args.task, "BLOCKED", date=today, by=args.by, context=args.reason)
        store.task(args.task)["Next action"] = clean(f"Blocked: {args.reason}")
        msg = f"{args.task} blocked"
    elif c == "unblock":
        apply_event(store, args.task, "UNBLOCKED", date=today, by=args.by)
        if args.next:
            store.task(args.task)["Next action"] = clean(args.next)
        msg = f"{args.task} unblocked"
    elif c == "complete":
        op_complete(store, args.task, source=args.source, verified_by=args.verified_by,
                    evidence=args.evidence, date=today, next_action=args.next)
        msg = f"{args.task} DONE on VERIFIED evidence"
    elif c == "edit":
        t = store.task(args.task)
        if t is None:
            raise Refused(f"{args.task} is not in the register")
        scope_bits = []
        if args.priority:
            if args.priority not in PRIORITIES:
                raise Refused("priority must be P0..P3")
            scope_bits.append(f"p={args.priority}")
        if args.gate:
            if args.gate not in GATES:
                raise Refused(f"gate must be one of {', '.join(GATES)}")
            if t["Gate"] != "none" and args.gate == "none":
                raise Refused("a gate is only tightened; loosening one is the owner's call and a new decision")
            scope_bits.append(f"gate={args.gate}")
        if args.source or args.evidence_status:
            if not (args.source and args.evidence_status):
                raise Refused("--evidence-status and --source go together")
            if t["Status"] == "DONE" and args.evidence_status != "VERIFIED":
                raise Refused("a DONE task keeps VERIFIED evidence")
            t["Evidence"] = make_evidence(args.evidence_status, args.source, today, args.verified_by)
        if not (scope_bits or args.next or args.source or args.note):
            raise Refused("edit needs --next, --priority, --gate, --evidence-status/--source or --note")
        apply_event(store, args.task, "NOTE", date=today, by=args.by, scope="; ".join(scope_bits) or NONE,
                    context=args.note or args.next or "evidence updated")
        if args.priority:
            t["P"] = args.priority
        if args.gate:
            t["Gate"] = args.gate
        if args.next:
            t["Next action"] = clean(args.next)
        msg = f"edited {args.task}"
    save(store)
    print(msg)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if args.selftest:
        return selftest()
    if not args.cmd:
        ap.print_usage(sys.stderr)
        return 2
    root = Path(args.root).resolve() if args.root else repo_root(Path.cwd())
    today = today_str(args.today)
    reg = Path(args.register) if args.register else None
    hist = Path(args.history) if args.history else None
    try:
        if args.cmd == "init":
            op_init(root, reg or root / REGISTER_REL, hist or root / HISTORY_REL)
            print("created the register and the history")
            return 0
        if args.cmd in ("add", "raise", "decide", "resume", "reopen", "start", "block", "unblock",
                        "complete", "edit"):
            return write_cmd(args, root, today)
        store = load(root, reg, hist)
        branch = current_branch(root, getattr(args, "branch", None))
        if args.cmd == "update":
            u = build_update(store, branch, args.project, args.all, today,
                             [s.strip().upper() for s in args.status.split(",")] if args.status else None,
                             args.include_closed, args.gate, args.limit)
            if args.select:
                out_json(selection_payload(u, store))
            elif args.json:
                out_json({**{k: v for k, v in u.items() if k not in ("ranked", "paused", "closed", "blockers")},
                          "ranked": u["ranked"], "paused": u["paused"], "closed": u["closed"],
                          "blockers": [t["ID"] for t in u["blockers"]],
                          "next_actions": next_actions(u, store), "selection": selection_payload(u, store)})
            else:
                print(render_update(u, store, args.detail))
        elif args.cmd == "show":
            t = store.task(args.task)
            if t is None:
                raise Refused(f"{args.task} is not in the register")
            print(render_show(t, store))
        elif args.cmd == "ask":
            ids = [x.strip() for x in args.ids.split(",")] if args.ids else None
            payload = build_ask(store, ids, branch, args.project, args.page)
            if args.json:
                out_json(payload)
            else:
                print(f"{payload['total_awaiting']} awaiting; page {payload['page']} of {payload['pages']}; "
                      f"{len(payload['questions'])} question(s) below. Use --json for the AskUserQuestion payload.")
                for q in payload["questions"]:
                    print(f"\n[{q['header']}] {q['question']}\n  options: " + " / ".join(o["label"] for o in q["options"]))
                for r in payload["reused"]:
                    print(f"\nREUSED {r['task']}: {r['decision']} ({r['status']}); not asked again")
        elif args.cmd == "lookup":
            res = lookup(store, args.words)
            if args.json:
                out_json(res)
            else:
                for t in res["tasks"]:
                    print(f"{t['task']}  {t['status']}  {t['decision']}  {t['title']}\n    {t['reuse']}")
                for e in res["events"]:
                    print(f"{e['ID']} {e['Date']} {e['Task']} {e['Event']}: {e['Context']}")
                if not res["tasks"] and not res["events"]:
                    print("no record of this: it is genuinely new, so ask (once, batched with the others)")
        elif args.cmd == "digest":
            d = build_digest(store, today, args.stale_days, args.since)
            out_json(d) if args.json else print(render_digest(d))
        elif args.cmd == "handover":
            keys = [args.project] if args.project else resolve_projects(store.projects, branch)[0]
            print(render_handover(store, keys, today, branch))
        elif args.cmd == "check":
            rep = lint(store, today=today, stale_days=args.stale_days)
            if args.append_only_vs:
                append_only(store, args.append_only_vs, rep)
            if args.json:
                out_json({"errors": rep.errors, "warnings": rep.warnings, "info": rep.info})
            else:
                print(render_check(rep, args.strict))
            return 1 if rep.errors or (args.strict and rep.warnings) else 0
        return 0
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    except Unreadable as e:
        print(f"UNREADABLE: {e}", file=sys.stderr)
        if not (reg or root / REGISTER_REL).exists():
            print("hint: there is no register here. `tasks.py init` creates one, if this repository "
                  "is meant to have one.", file=sys.stderr)
        return 3
    except (KeyError, json.JSONDecodeError) as e:
        print(f"USAGE: bad input ({e})", file=sys.stderr)
        return 2


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def selftest() -> int:
    """Prove the tool in throwaway repositories. Needs only Python 3 and git."""
    import hashlib
    import shutil

    SELF = Path(__file__).resolve()
    results: list[tuple[str, bool, str]] = []

    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    base = Path(tempfile.mkdtemp(prefix="tasks-selftest-"))

    def sh(cwd, *a):
        p = subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"{a}: {p.stderr}")
        return p.stdout

    def mkrepo(name):
        r = base / name
        r.mkdir()
        sh(r, "git", "init", "-q", "-b", "casaray-v3-design")
        sh(r, "git", "config", "user.email", "selftest@example.invalid")
        sh(r, "git", "config", "user.name", "selftest")
        (r / "docs").mkdir()
        (r / "docs" / "x.md").write_text("# fixture\nalpha anchor\nbravo anchor\n", encoding="utf-8")
        return r

    def cli(root, *a, today="2026-10-12", stdin=None):
        p = subprocess.run([sys.executable, str(SELF), "--root", str(root), "--today", today, *a],
                           capture_output=True, text=True, input=stdin)
        return p.returncode, p.stdout, p.stderr

    def snap(root):
        out = {}
        for p in sorted(root.rglob("*")):
            if p.is_file() and ".git" not in p.relative_to(root).parts:
                out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
        return out

    def commit(root, msg):
        sh(root, "git", "add", "-A")
        # "nothing to commit" is not a harness failure: a broken guard may have written nothing
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(root), capture_output=True, text=True)

    OWN = ["--by", "owner", "--via", "ask-user-question", "--basis", "selected in the AskUserQuestion prompt"]
    class _Ids(dict):
        """Task ids by fixture key; a missing one yields a name that fails its check, not a crash."""
        def __missing__(self, key):
            return "TASK-MISSING"

    ids = _Ids()

    def add(root, key, title, project="casaray-v3", p="P2", gate="none", status="OPEN",
            home="register", today="2026-10-01"):
        extra = ["--reason", "waiting on a fixture part"] if status == "BLOCKED" else []
        rc, o, e = cli(root, "add", "--project", project, "--priority", p, "--title", title, "--gate", gate,
                       "--status", status, "--home", home, "--evidence-status", "REPORTED",
                       "--source", "fixture record", "--next", f"Next step for {title}", *extra, today=today)
        m = re.search(r"added (TASK-\d+)", o)
        if m:
            ids[key] = m.group(1)
        return rc, o, e

    def row(root, tid):
        t = load(root).task(tid)
        return t if t is not None else {c: "<no such task>" for c in TASK_COLS}

    try:
        # ---------------------------------------------------------------- A. static safety
        src = SELF.read_text(encoding="utf-8")
        body = src.split("def selftest()")[0]
        for tok in ("import socket", "urllib", "http.client", "import requests", "smtplib", "ftplib",
                    "webbrowser", "os.system", "shell=True"):
            check(f"A1 no `{tok}` in the tool", tok not in body)
        check("A2 subprocess is used only by the read-only git wrapper",
              body.count("subprocess.run(") == 1)
        check("A3 the git allowlist names no verb that writes",
              not set(SAFE_GIT) & {"fetch", "pull", "push", "commit", "checkout", "reset", "config", "remote",
                                   "tag", "stash", "add", "rm", "merge", "rebase", "clean", "apply", "am"})
        probe = mkrepo("probe")
        for verb in ("fetch", "pull", "push", "commit", "checkout", "reset", "config", "remote", "tag",
                     "stash", "add", "rm", "merge", "rebase", "clean"):
            try:
                git(probe, verb)
                check(f"A4 git {verb} is refused", False)
            except Refused:
                check(f"A4 git {verb} is refused", True)
        for args in (("branch", "newname"), ("show", "--output=x", "HEAD"), ("cat-file", "-p", "HEAD")):
            try:
                git(probe, *args)
                check(f"A5 git {' '.join(args)} is refused", False)
            except Refused:
                check(f"A5 git {' '.join(args)} is refused", True)

        # ---------------------------------------------------------------- B. init
        r = mkrepo("main")
        rc, o, e = cli(r, "init")
        check("B1 init creates the register and the history",
              rc == 0 and (r / REGISTER_REL).is_file() and (r / HISTORY_REL).is_file(), e)
        rc, o, e = cli(r, "init")
        check("B2 init never overwrites", rc == 1 and "already exists" in e)
        rc, o, e = cli(r, "check")
        check("B3 an empty register passes check", rc == 0 and "PASS" in o, o)
        commit(r, "baseline")

        # ---------------------------------------------------------------- C. add
        rc, o, e = add(r, "A", "Alpha job", p="P1", home="docs/x.md#alpha")
        check("C1 add creates TASK-001 as OPEN", rc == 0 and ids["A"] == "TASK-001", e)
        rc, o, e = add(r, "x", "Gated starts open", gate="protected")
        check("C2 a gated task cannot start OPEN", rc == 1 and "cannot start OPEN" in e, e)
        rc, o, e = add(r, "x", "Alpha job")
        check("C3 a duplicate title is refused and points at the original", rc == 1 and "TASK-001" in e, e)
        rc, o, e = add(r, "x", "Other job", home="docs/x.md#alpha")
        check("C4 a second task on the same home record is refused", rc == 1 and "one task per home" in e, e)
        rc, o, e = add(r, "x", "Bad project", project="nope")
        check("C5 an unknown project is refused", rc == 1 and "not in the Projects table" in e, e)
        rc, o, e = add(r, "x", "Bad priority", p="P9")
        check("C6 an unknown priority is refused", rc == 1, e)
        add(r, "B", "Bravo decision", p="P1", status="AWAITING_DECISION", home="docs/x.md#bravo")
        add(r, "C", "Charlie gated", p="P0", gate="protected", status="AWAITING_DECISION")
        add(r, "D", "Delta", p="P2", status="AWAITING_DECISION")
        add(r, "E", "Echo", project="tooling", p="P3", status="AWAITING_DECISION")
        add(r, "F", "Foxtrot", project="casaray-v2", p="P1")
        add(r, "G", "Golf safety", p="P3", gate="safety", status="AWAITING_DECISION")
        add(r, "H", "Hotel", p="P2", status="AWAITING_DECISION")
        rc, o, e = cli(r, "add", "--project", "casaray-v3", "--priority", "P3", "--title", "No reason", "--status", "BLOCKED",
                       "--home", "register", "--evidence-status", "REPORTED", "--source", "fixture", "--next", "x", today="2026-10-01")
        check("C6b a task added as BLOCKED must say what it waits on", rc == 1 and "--reason" in e, e)
        add(r, "I", "India blocked", p="P3", status="BLOCKED")
        check("C7 nine tasks, sequential ids", [ids[k] for k in "ABCDEFGHI"] == [f"TASK-{i:03d}" for i in range(1, 10)])
        rc, o, e = cli(r, "check")
        check("C8 the register passes check after the adds", rc == 0, o)
        check("C9 the Decision cell is PENDING for AWAITING_DECISION and — otherwise",
              row(r, ids["B"])["Decision"] == "PENDING" and row(r, ids["A"])["Decision"] == NONE)
        commit(r, "after adds")
        t0 = snap(r)

        # ---------------------------------------------------------------- D. approve / deny / pause
        D5 = "2026-10-05"
        def decide(*a, today=D5, owner=True):
            return cli(r, "decide", *a, *(OWN if owner else []), today=today)
        rc, o, e = cli(r, "decide", ids["B"], "approve", "--by", "claude", "--via", "chat",
                       "--basis", "the agent decided", today=D5)
        check("D1 an agent cannot record an owner decision", rc == 1 and "only the owner" in e, e)
        rc, o, e = cli(r, "decide", ids["B"], "approve", "--by", "owner", "--via", "routine",
                       "--basis", "weekly routine", today=D5)
        check("D2 a routine is not a channel the owner used", rc == 1 and "--via" in e, e)
        rc, o, e = cli(r, "decide", ids["B"], "approve", "--by", "owner", "--via", "chat", "--basis", "ok", today=D5)
        check("D3 a decision with no real basis is refused", rc == 1 and "--basis" in e, e)
        rc, o, e = decide(ids["B"], "maybe")
        check("D4 only approve, deny or pause are verdicts", rc == 1, e)
        check("D5 nothing was written by the refusals", snap(r) == t0)
        rc, o, e = decide(ids["B"], "approve")
        b = row(r, ids["B"])
        check("D6 approve moves AWAITING_DECISION to APPROVED", rc == 0 and b["Status"] == "APPROVED", e)
        check("D7 the Decision cell names the decision", re.fullmatch(r"DEC-\d+ APPROVED", b["Decision"]) is not None, b["Decision"])
        rc, o, e = decide(ids["C"], "approve")
        check("D8 a protected task needs a specific scope", rc == 1 and "exact action" in e, e)
        rc, o, e = decide(ids["C"], "approve", "--scope", "Run the fix script once on the host")
        c = row(r, ids["C"])
        check("D9 a specific scope is accepted and recorded", rc == 0 and c["Status"] == "APPROVED", e)
        hist = load(r).events
        check("D10 the history row carries the scope, basis, channel and actor",
              any(h["Task"] == ids["C"] and h["Event"] == "APPROVED" and "Run the fix script" in h["Scope"]
                  and h["Via"] == "ask-user-question" and h["By"] == "owner" for h in hist))
        rc, o, e = decide(ids["E"], "deny")
        check("D11 a denial needs a reason", rc == 1 and "reason" in e, e)
        rc, o, e = decide(ids["E"], "deny", "--context", "Not wanted: the household does not use it")
        check("D12 deny moves to DENIED and keeps the reason",
              rc == 0 and row(r, ids["E"])["Status"] == "DENIED"
              and any(h["Task"] == ids["E"] and "household does not use" in h["Context"] for h in load(r).events))
        rc, o, e = decide(ids["E"], "approve")
        check("D13 a denied task cannot simply be approved", rc == 1 and "reopen" in e, e)
        rc, o, e = cli(r, "raise", ids["E"], "--next", "Ask again", today=D5)
        check("D14 a denied task is not silently re-raised", rc == 1, e)
        rc, o, e = decide(ids["D"], "pause")
        check("D15 a pause needs the context to resume from", rc == 1 and "--context" in e, e)
        rc, o, e = decide(ids["H"], "pause", "--context", "Waiting on the Powerpal meter reading",
                          "--resume-when", "the owner has checked the meter", "--until", "2026-10-10")
        check("D16 pause moves to PAUSED", rc == 0 and row(r, ids["H"])["Status"] == "PAUSED", e)
        rc, o, e = decide(ids["B"], "approve")
        check("D17 an already-approved task is not approved twice", rc == 1, e)
        rc, o, e = cli(r, "check")
        check("D18 check passes after decisions", rc == 0, o)

        # ---------------------------------------------------------------- E. multi-task selection
        before = snap(r)
        rc, o, e = cli(r, "decide", "--batch", "-", *OWN, today=D5, stdin=json.dumps(
            [{"task": ids["D"], "verdict": "approve"},
             {"task": ids["G"], "verdict": "approve"}]))
        check("E1 a batch with one invalid answer writes nothing (atomic)",
              rc == 1 and snap(r) == before and row(r, ids["D"])["Status"] == "AWAITING_DECISION", e)
        rc, o, e = cli(r, "decide", "--batch", "-", "--blanket", *OWN, today=D5, stdin=json.dumps(
            [{"task": ids["D"], "verdict": "approve"},
             {"task": ids["G"], "verdict": "approve"}]))
        check("E2 a blanket approval applies to the ungated task", rc == 0 and row(r, ids["D"])["Status"] == "APPROVED", o + e)
        check("E3 a blanket approval does NOT approve a safety-gated task",
              row(r, ids["G"])["Status"] == "AWAITING_DECISION" and "NOT APPLIED" in o and "safety-gated" in o, o)
        rc, o, e = cli(r, "decide", "--batch", "-", *OWN, today=D5, stdin=json.dumps(
            {"answers": [{"task": ids["G"], "verdict": "approve", "scope": "Test the siren once, 10 seconds, with the owner present"},
                         {"task": ids["F"], "verdict": "deny", "context": "Superseded by the V3 rebuild"}]}))
        check("E4 a specific batch applies several different answers at once",
              rc == 0 and row(r, ids["G"])["Status"] == "APPROVED" and row(r, ids["F"])["Status"] == "DENIED", o + e)
        add(r, "K", "Kilo", p="P3", status="AWAITING_DECISION", today=D5)
        before = snap(r)
        rc, o, e = cli(r, "decide", "--batch", "-", *OWN, today=D5, stdin=json.dumps(
            [{"task": ids["K"], "verdict": "approve"}, {"task": ids["K"], "verdict": "deny", "context": "changed my mind"}]))
        check("E5 the same task twice in one batch is refused and writes nothing",
              rc == 1 and "twice" in e and snap(r) == before, e)
        rc, o, e = cli(r, "start", f"{ids['D']},{ids['B']}", today=D5)
        check("E6 several approved tasks can be started together",
              rc == 0 and row(r, ids["D"])["Status"] == "IN_PROGRESS" and row(r, ids["B"])["Status"] == "IN_PROGRESS", e)
        before = snap(r)
        rc, o, e = cli(r, "start", f"{ids['A']},{ids['D']}", today=D5)
        check("E7 starting a set where one cannot start changes none of them",
              rc == 1 and snap(r) == before and row(r, ids["A"])["Status"] == "OPEN", e)

        # ---------------------------------------------------------------- F. resume
        rc, o, e = cli(r, "resume", ids["H"], "--by", "claude", "--via", "chat", "--basis", "agent says resume", today="2026-10-12")
        check("F1 only the owner resumes a paused task", rc == 1 and "owner" in e, e)
        rc, o, e = cli(r, "update", "--project", "casaray-v3", today="2026-10-12")
        check("F2 Update me shows the saved pause context and the resume condition",
              "Waiting on the Powerpal meter reading" in o and "the owner has checked the meter" in o
              and "date reached" in o, o)
        rc, o, e = cli(r, "resume", ids["H"], *OWN, today="2026-10-12")
        h = row(r, ids["H"])
        check("F3 resume returns the task to the status it was paused from (AWAITING_DECISION)",
              rc == 0 and h["Status"] == "AWAITING_DECISION" and h["Decision"] == "PENDING", e)
        rc, o, e = cli(r, "resume", ids["H"], *OWN, today="2026-10-12")
        check("F4 resuming a task that is not paused is refused", rc == 1 and "PAUSED" in e, e)
        rc, o, e = cli(r, "decide", ids["D"], "pause", *OWN, "--context", "Hold until the hardware arrives", today="2026-10-12")
        d = row(r, ids["D"])
        check("F5 an IN_PROGRESS task can be paused", rc == 0 and d["Status"] == "PAUSED", e)
        rc, o, e = cli(r, "resume", ids["D"], *OWN, today="2026-10-12")
        d = row(r, ids["D"])
        check("F6 resume restores IN_PROGRESS and the approval that governed it",
              rc == 0 and d["Status"] == "IN_PROGRESS" and re.fullmatch(r"DEC-\d+ APPROVED", d["Decision"]) is not None, d["Decision"])
        rc, o, e = cli(r, "check", today="2026-10-12")
        check("F7 check passes after pause and resume", rc == 0, o)

        # ---------------------------------------------------------------- G. completion needs evidence
        T12 = "2026-10-12"
        rc, o, e = cli(r, "start", ids["A"], today=T12)
        rc, o, e = cli(r, "complete", ids["A"], "--source", "tests passed", "--verified-by", "claude", today=T12)
        check("G1 completion with no checkable source is refused", rc == 1 and "must name its source" in e, e)
        rc, o, e = cli(r, "complete", ids["A"], "--source", "commit deadbeefdead", "--verified-by", "claude", today=T12)
        check("G2 a commit that does not exist is not accepted on faith", rc == 1 and "does not exist" in e, e)
        rc, o, e = cli(r, "complete", ids["A"], "--source", "file docs/nope.md", "--verified-by", "claude", today=T12)
        check("G3 a file that does not exist is not accepted on faith", rc == 1, e)
        rc, o, e = cli(r, "complete", ids["A"], "--source", "owner saw it on the iPad", "--verified-by", "claude", today=T12)
        check("G4 an agent cannot verify what only the owner can see", rc == 1 and "verified-by owner" in e.replace("--verified-by owner", "verified-by owner"), e)
        check("G5 none of those completed it", row(r, ids["A"])["Status"] == "IN_PROGRESS")
        head = sh(r, "git", "rev-parse", "HEAD").strip()
        rc, o, e = cli(r, "complete", ids["A"], "--source", f"commit {head[:10]}", "--verified-by", "claude", today=T12)
        a = row(r, ids["A"])
        check("G6 a real commit is accepted: DONE with VERIFIED evidence",
              rc == 0 and a["Status"] == "DONE" and a["Evidence"].startswith("VERIFIED"), e)
        rc, o, e = cli(r, "complete", ids["C"], "--source", "file docs/x.md", "--verified-by", "claude", today=T12)
        check("G7 a protected task cannot be marked done by an agent", rc == 1 and "only the owner" in e, e)
        cli(r, "start", ids["C"], today=T12)
        rc, o, e = cli(r, "complete", ids["C"], "--source", "owner confirmed the script ran", "--verified-by", "owner", today=T12)
        check("G8 the owner can verify a gated task", rc == 0 and row(r, ids["C"])["Status"] == "DONE", e)
        rc, o, e = cli(r, "check", today=T12)
        check("G9 check passes with completed tasks", rc == 0, o)

        # ---------------------------------------------------------------- H. edit
        add(r, "J", "Juliet", p="P2", today=T12)
        rc, o, e = cli(r, "edit", ids["J"], "--gate", "safety", today=T12)
        check("H1 a gate can be tightened", rc == 0 and row(r, ids["J"])["Gate"] == "safety", e)
        rc, o, e = cli(r, "edit", ids["J"], "--gate", "none", today=T12)
        check("H2 a gate cannot be loosened", rc == 1 and "only tightened" in e, e)
        rc, o, e = cli(r, "start", ids["J"], today=T12)
        check("H3 a task tightened while OPEN cannot start without an approval", rc == 1, e)
        rc, o, e = cli(r, "edit", ids["J"], "--priority", "P1", "--next", "Raise it", today=T12)
        check("H4 priority and next action can change", rc == 0 and row(r, ids["J"])["P"] == "P1", e)
        rc, o, e = cli(r, "raise", ids["J"], "--next", "Approve a one-off test of the thing", today=T12)
        check("H5 an OPEN task is raised for a decision", rc == 0 and row(r, ids["J"])["Status"] == "AWAITING_DECISION", e)
        rc, o, e = cli(r, "block", ids["I"], "--reason", "Needs the router credentials", today=T12)
        check("H6 a BLOCKED task cannot be blocked again", rc == 1, e)
        rc, o, e = cli(r, "unblock", ids["I"], "--next", "Carry on", today=T12)
        check("H7 unblock returns a task to where it was", rc == 0 and row(r, ids["I"])["Status"] == "BLOCKED" or row(r, ids["I"])["Status"] == "OPEN", e)
        rc, o, e = cli(r, "check", today=T12)
        check("H8 check passes", rc == 0, o)
        commit(r, "after workflow")

        # ---------------------------------------------------------------- I. reopen
        rc, o, e = cli(r, "reopen", ids["E"], "--by", "claude", "--via", "chat", "--basis", "agent wants it back",
                       "--new-evidence", "Something changed", today=T12)
        check("I1 only the owner reopens a denied task", rc == 1, e)
        rc, o, e = cli(r, "reopen", ids["E"], *OWN, today=T12)
        check("I2 reopening needs new evidence", rc == 1 and "new-evidence" in e, e)
        rc, o, e = cli(r, "reopen", ids["E"], *OWN, "--new-evidence", "The household now uses it daily", today=T12)
        check("I3 a denied task reopens as AWAITING_DECISION", rc == 0 and row(r, ids["E"])["Status"] == "AWAITING_DECISION", e)
        rc, o, e = cli(r, "reopen", ids["C"], *OWN, "--new-evidence", "It must be run again after the rebuild", today=T12)
        check("I4 a finished gated task reopens as AWAITING_DECISION: its approval was single-use",
              rc == 0 and row(r, ids["C"])["Status"] == "AWAITING_DECISION" and row(r, ids["C"])["Decision"] == "PENDING", e)
        rc, o, e = cli(r, "reopen", ids["A"], *OWN, "--new-evidence", "Regressed after the next merge", today=T12)
        check("I5 a finished ungated task reopens as OPEN", rc == 0 and row(r, ids["A"])["Status"] == "OPEN", e)

        add(r, "L", "Lima", p="P2", status="AWAITING_DECISION", today=T12)
        cli(r, "decide", ids["L"], "approve", *OWN, today=T12)
        cli(r, "start", ids["L"], today=T12)
        cli(r, "complete", ids["L"], "--source", "file docs/x.md", "--verified-by", "claude", today=T12)
        check("I6 an approved ungated task shows its approval once done",
              re.fullmatch(r"DEC-\d+ APPROVED", row(r, ids["L"])["Decision"]) is not None)
        cli(r, "reopen", ids["L"], *OWN, "--new-evidence", "Regressed after a later change", today=T12)
        check("I7 reopening clears the old approval: a stale one is not shown as current",
              row(r, ids["L"])["Status"] == "OPEN" and row(r, ids["L"])["Decision"] == NONE, row(r, ids["L"])["Decision"])

        # ---------------------------------------------------------------- J. persistent history / tamper
        reg_p, his_p = r / REGISTER_REL, r / HISTORY_REL
        reg0, his0 = reg_p.read_text(encoding="utf-8"), his_p.read_text(encoding="utf-8")
        def restore():
            reg_p.write_text(reg0, encoding="utf-8")
            his_p.write_text(his0, encoding="utf-8")
        rc, o, e = cli(r, "check", "--append-only-vs", "HEAD", today=T12)
        check("J1 appending to the history is allowed", rc == 0, o)
        # edit an old history row
        his_p.write_text(his0.replace("selected in the AskUserQuestion prompt", "rewritten basis", 1), encoding="utf-8")
        rc, o, e = cli(r, "check", "--append-only-vs", "HEAD", today=T12)
        check("J2 editing a past history row is caught (E17)", rc == 1 and "E17" in o, o)
        restore()
        # delete a task row (the denied one)
        reg_p.write_text("\n".join(l for l in reg0.split("\n") if not l.startswith(f"| {ids['F']} |")), encoding="utf-8")
        rc, o, e = cli(r, "check", "--append-only-vs", "HEAD", today=T12)
        check("J3 deleting a denied task is caught (E17)", rc == 1 and "E17" in o and ids["F"] in o, o)
        restore()
        # hand-mark done
        reg_p.write_text(reg0.replace(f"| {ids['B']} | casaray-v3 | P1 | IN_PROGRESS", f"| {ids['B']} | casaray-v3 | P1 | DONE"), encoding="utf-8")
        rc, o, e = cli(r, "check", today=T12)
        check("J4 hand-marking a task DONE without evidence is caught", rc == 1 and ("E12" in o and "E06" in o), o)
        rc2, o2, e2 = cli(r, "decide", ids["H"], "deny", *OWN, "--context", "writing while inconsistent", today=T12)
        check("J5 writes are refused while the files disagree", rc2 == 1 and "already disagree" in e2, e2)
        restore()
        # loosen a gate by hand
        reg_p.write_text(reg0.replace(f"| {ids['G']} | casaray-v3 | P3 | APPROVED | safety", f"| {ids['G']} | casaray-v3 | P3 | APPROVED | none"), encoding="utf-8")
        rc, o, e = cli(r, "check", today=T12)
        check("J6 loosening a gate by hand is caught", rc == 1 and "gate" in o and "E12" in o, o)
        restore()
        # an agent forging an owner approval in the history
        forged = his0.rstrip("\n") + (f"\n| DEC-{len(load(r).events) + 1:03d} | {T12} | {ids['H']} | APPROVED | AWAITING_DECISION | APPROVED | — | — | looks fine | chat | claude |\n")
        his_p.write_text(forged, encoding="utf-8")
        reg_p.write_text(reg0.replace(f"| {ids['H']} | casaray-v3 | P2 | AWAITING_DECISION", f"| {ids['H']} | casaray-v3 | P2 | APPROVED"), encoding="utf-8")
        rc, o, e = cli(r, "check", today=T12)
        check("J7 a forged approval attributed to the agent is caught (E10)", rc == 1 and "E10" in o, o)
        restore()
        # reused decision id
        his_p.write_text(his0.replace("DEC-003", "DEC-002", 1), encoding="utf-8")
        rc, o, e = cli(r, "check", today=T12)
        check("J8 a reused or out-of-sequence decision id is caught (E16)", rc == 1 and "E16" in o, o)
        restore()
        rc, o, e = cli(r, "check", today=T12)
        check("J9 after restoring, check passes again", rc == 0, o)
        check("J10 no temporary files are left behind", not list((r / "docs" / "project-tasks").glob("*.tmp")))

        # ---------------------------------------------------------------- K. persistence across sessions
        commit(r, "session end")
        clone = base / "clone"
        sh(base, "git", "clone", "-q", str(r), str(clone))
        rc1, o1, _ = cli(r, "update", "--branch", "casaray-v3-design", today=T12)
        rc2, o2, _ = cli(clone, "update", "--branch", "casaray-v3-design", today=T12)
        check("K1 a fresh clone shows the identical Update me", rc1 == 0 and rc2 == 0 and o1 == o2)
        rc, o, e = cli(clone, "check", "--append-only-vs", "HEAD~1", today=T12)
        check("K2 the clone passes check and append-only against its own history", rc == 0, o)
        rc, o, e = cli(clone, "show", ids["E"], today=T12)
        check("K3 a denied-then-reopened task keeps its whole history in the clone",
              rc == 0 and "DENIED" in o and "REOPENED" in o and "household does not use" in o, o)
        rc, o, e = cli(clone, "decide", ids["J"], "approve", *OWN, "--scope", "Run the one-off test, once", today="2026-10-13")
        check("K4 a decision can be recorded in the clone and carries on from the same ids",
              rc == 0 and "DEC-" in o, o + e)

        # ---------------------------------------------------------------- L. Update me on a controlled set
        u = mkrepo("update")
        cli(u, "init")
        def uadd(key, title, **kw):
            return add(u, key, title, **kw)
        uadd("U1", "Zulu older P2 decision", p="P2", status="AWAITING_DECISION", today="2026-10-01")
        uadd("U2", "Open P1 job", p="P1", today="2026-10-01")
        uadd("U3a", "P1 decision (waiting longest)", p="P1", status="AWAITING_DECISION", today="2026-10-02")
        uadd("U3", "P1 decision (newer)", p="P1", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U4", "P0 blocked", p="P0", status="BLOCKED", today="2026-10-03")
        uadd("U5", "P1 in progress", p="P1", today="2026-10-03")
        uadd("U6", "P3 decision", p="P3", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U7", "P1 approved", p="P1", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U8", "P1 to pause", p="P1", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U9", "V2 P0 decision", project="casaray-v2", p="P0", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U10", "Tooling P2 open", project="tooling", p="P2", today="2026-10-03")
        uadd("U11", "P1 to finish", p="P1", today="2026-10-03")
        uadd("U12", "P1 to deny", p="P1", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U13", "P3 decision two", p="P3", status="AWAITING_DECISION", today="2026-10-03")
        uadd("U14", "P3 decision three", p="P3", status="AWAITING_DECISION", today="2026-10-03")
        UO = ["--by", "owner", "--via", "chat", "--basis", "told me in the chat window"]
        cli(u, "decide", ids["U7"], "approve", *UO, today="2026-10-04")
        cli(u, "decide", ids["U8"], "pause", *UO, "--context", "Needs the new sensor first", "--resume-when", "the sensor is installed", today="2026-10-04")
        cli(u, "decide", ids["U12"], "deny", *UO, "--context", "Not needed any more", today="2026-10-04")
        cli(u, "start", ids["U5"], today="2026-10-04")
        cli(u, "block", ids["U4"].replace(ids["U4"], ids["U4"]) , "--reason", "x", today="2026-10-04")  # already BLOCKED: refused
        cli(u, "start", ids["U11"], today="2026-10-04")
        cli(u, "complete", ids["U11"], "--source", "file docs/x.md", "--verified-by", "claude", today="2026-10-05")
        rc, o, e = cli(u, "check", today="2026-10-12")
        check("L0 the controlled set passes check", rc == 0, o)
        rc, o, e = cli(u, "update", "--branch", "casaray-v3-design", today="2026-10-12")
        order = re.findall(r"^\s*\d+\s+P\d\s+(TASK-\d+)", o, re.M)
        want = [ids[k] for k in ("U4", "U3a", "U3", "U5", "U7", "U2", "U1", "U10", "U6", "U13", "U14")]
        check("L1 ranked by priority, then decisions, in progress, approved, open, blocked, then oldest",
              order == want, f"got {order}\nwant {want}")
        check("L2 the V3 branch shows casaray-v3 plus the cross-cutting tooling project",
              "project: casaray-v3, tooling" in o)
        check("L3 a task from another project is not listed, but counted as another project",
              ids["U9"] not in o and "casaray-v2 (1)" in o)
        check("L4 DONE and DENIED are not listed but remain counted", ids["U11"] not in o.split("PAUSED")[0]
              and "done 1 · denied 1" in o)
        check("L5 the paused task is in its own section with its saved context",
              "Needs the new sensor first" in o and "the sensor is installed" in o and ids["U8"] in o.split("PAUSED")[1])
        check("L6 BLOCKERS lists the owner decisions and the blocked task with its reason",
              "BLOCKERS" in o and f"{ids['U4']}  P0  blocked: waiting on a fixture part" in o
              and f"{ids['U3a']}  P1  waiting on the owner" in o)
        check("L7 the counts line states what is outstanding by status",
              "awaiting your decision 6 · in progress 1 · approved 1 · open 2 · blocked 1 · paused 1" in o, o.split("\n")[3])
        check("L8 NEXT ACTIONS offers Decide, Work, Resume and Another project",
              all(k in o for k in ("Decide (6)", "Work (", "Resume (1)", "Another project")))
        rc, o2, e = cli(u, "update", "--branch", "claude/some-session", today="2026-10-12")
        check("L9 a branch that identifies no project shows everything and says so",
              "did not identify a project" in o2 and ids["U9"] in o2)
        rc, o3, e = cli(u, "update", "--branch", "ha-deploy", today="2026-10-12")
        check("L10 ha-deploy resolves to the V2 project (plus tooling)",
              "project: casaray-v2, tooling" in o3 and ids["U9"] in o3 and ids["U1"] not in o3)
        rc, o3, e = cli(u, "update", "--branch", "casaray-v3/agent-x", today="2026-10-12")
        check("L11 a specialist branch resolves to V3", "project: casaray-v3, tooling" in o3)
        rc, o4, e = cli(u, "update", "--branch", "casaray-v3-design", "--status", "AWAITING_DECISION", today="2026-10-12")
        order4 = re.findall(r"^\s*\d+\s+P\d\s+(TASK-\d+)", o4, re.M)
        check("L12 --status filters to the decisions only", order4 == [ids[k] for k in ("U3a", "U3", "U1", "U6", "U13", "U14")], str(order4))
        rc, o5, e = cli(u, "update", "--branch", "casaray-v3-design", "--include-closed", today="2026-10-12")
        check("L13 --include-closed lists done and denied tasks, marked", ids["U11"] in o5 and ids["U12"] in o5 and "DENIED" in o5)
        rc, o6, e = cli(u, "update", "--project", "casaray-v2", today="2026-10-12")
        check("L14 --project overrides the branch", ids["U9"] in o6 and ids["U3"] not in o6)
        rc, o7, e = cli(u, "update", "--all", today="2026-10-12")
        check("L15 --all shows every project", ids["U9"] in o7 and ids["U3"] in o7)
        rc, o8, e = cli(u, "update", "--branch", "casaray-v3-design", "--json", today="2026-10-12")
        try:
            j = json.loads(o8)
            ok = j["counts"]["AWAITING_DECISION"] == 6 and len(j["ranked"]) == 11 and "selection" in j
        except Exception as ex:      # noqa
            ok = False
        check("L16 --json is valid and complete", ok)
        rc, o9, e = cli(u, "update", "--project", "nope", today="2026-10-12")
        check("L17 an unknown project is refused with the known ones", rc == 1 and "casaray-v3" in e)
        rc, oa, e = cli(u, "update", "--branch", "casaray-v3-design", "--gate", "protected", today="2026-10-12")
        check("L18 --gate filters", rc == 0 and "Nothing outstanding" in oa)

        # selection payload
        rc, o, e = cli(u, "update", "--branch", "casaray-v3-design", "--select", today="2026-10-12")
        try:
            sel = json.loads(o)
            qs = sel["questions"]
            shape = all(2 <= len(q["options"]) <= 4 and q["multiSelect"] is True and len(q["header"]) <= 12
                        for q in qs) and len(qs) == 2
        except Exception:
            shape = False
        check("L19 the selection payload is a valid multi-select AskUserQuestion payload", shape, o[:300])

        # ---------------------------------------------------------------- M. ask: Approve / Deny / Pause
        rc, o, e = cli(u, "ask", "--branch", "casaray-v3-design", "--json", today="2026-10-12")
        p1 = json.loads(o)
        check("M1 six decisions are asked four at a time", len(p1["questions"]) == 4 and p1["pages"] == 2 and p1["total_awaiting"] == 6)
        check("M2 every question offers exactly Approve, Deny, Pause as a single choice",
              all([x["label"] for x in q["options"]] == ["Approve", "Deny", "Pause"] and q["multiSelect"] is False
                  for q in p1["questions"]))
        check("M3 headers fit 12 characters and questions end with a question mark",
              all(len(q["header"]) <= 12 and q["question"].endswith("?") for q in p1["questions"]))
        check("M4 the highest-priority decision is asked first", p1["questions"][0]["header"] == ids["U3a"])
        check("M5 a task already decided is reused, not asked again",
              any(x["task"] == ids["U7"] for x in p1["reused"]) and
              ids["U7"] not in [q["header"] for q in p1["questions"]])
        rc, o, e = cli(u, "ask", "--branch", "casaray-v3-design", "--json", "--page", "2", today="2026-10-12")
        p2 = json.loads(o)
        check("M6 page two carries the remaining two", len(p2["questions"]) == 2 and p2["page"] == 2)
        rc, o, e = cli(u, "ask", "--ids", f"{ids['U2']},{ids['U3']}", "--json", today="2026-10-12")
        p3 = json.loads(o)
        check("M7 --ids asks only the named decisions and reports ones that are not awaiting",
              [q["header"] for q in p3["questions"]] == [ids["U3"]] and p3["not_awaiting"][0]["task"] == ids["U2"])
        uadd("U15", "Protected question", p="P1", gate="protected", status="AWAITING_DECISION", today="2026-10-06")
        rc, o, e = cli(u, "ask", "--ids", ids["U15"], "--json", today="2026-10-12")
        q = json.loads(o)["questions"][0]
        check("M8 a gated question says approval covers only the exact action, once",
              "protected-gated" in q["question"] and "once" in q["question"] and "once" in q["options"][0]["description"])

        # ---------------------------------------------------------------- N. lookup / reuse
        rc, o, e = cli(u, "lookup", "P1", "approved", today="2026-10-12")
        check("N1 lookup finds a confirmed decision and says to reuse it", "CONFIRMED" in o and ids["U7"] in o, o)
        rc, o, e = cli(u, "lookup", "nonexistent", "topic", today="2026-10-12")
        check("N2 lookup of something new says to ask once, batched", "genuinely new" in o)
        rc, o, e = cli(u, "lookup", "to", "deny", today="2026-10-12")
        check("N3 lookup of a denied task reports the denial", "DEC-" in o and "DENIED" in o, o)

        # ---------------------------------------------------------------- O. digest for the weekly routine
        rc, o, e = cli(u, "digest", "--stale-days", "7", "--since", "2026-10-05", today="2026-10-12")
        check("O1 digest lists every pending decision with its gate and age",
              "Items requiring approval" in o and ids["U15"] in o and "protected" in o and "**stale**" in o, o)
        check("O2 digest says nothing here has been decided", "nothing here has been decided" in o)
        rc, o2, e = cli(u, "digest", "--json", "--stale-days", "30", today="2026-10-12")
        dj = json.loads(o2)
        check("O3 digest --json counts the pending decisions and flags none stale at 30 days",
              len(dj["pending"]) == 8 and not any(i["stale"] for i in dj["pending"]), str(len(dj["pending"])))
        check("O4 the highest priority pending decision leads the digest (P0, then P1)",
              [i["p"] for i in dj["pending"]] == sorted(i["p"] for i in dj["pending"]) and dj["pending"][0]["p"] == "P0")
        check("O5 --since lists register activity from that date",
              "Register activity since 2026-10-05" in cli(u, "digest", "--since", "2026-10-05", today="2026-10-12")[1])

        # ---------------------------------------------------------------- P. handover and persistence reporting
        rc, o, e = cli(u, "handover", "--branch", "casaray-v3-design", today="2026-10-12")
        check("P1 handover warns when the register is not committed",
              "NOT SAVED" in o and "IN FLIGHT" in o and "WAITING ON THE OWNER" in o and ids["U8"] in o, o)
        commit(u, "register state")
        rc, o, e = cli(u, "handover", "--branch", "casaray-v3-design", today="2026-10-12")
        check("P2 after committing, handover says the files match the last commit", "match the last commit" in o)

        # ---------------------------------------------------------------- Q. read-only commands change nothing
        before = snap(u)
        for args in (("update",), ("update", "--all"), ("update", "--select"), ("show", ids["U7"]), ("ask",), ("ask", "--json"),
                     ("lookup", "P1"), ("digest",), ("digest", "--json"), ("handover",), ("check",),
                     ("check", "--append-only-vs", "HEAD")):
            cli(u, *args, today="2026-10-12")
        check("Q1 update, show, ask, lookup, digest, handover and check leave every file untouched", snap(u) == before)
        sh(u, "git", "status", "--porcelain")
        check("Q2 and leave the git working tree clean", sh(u, "git", "status", "--porcelain").strip() == "")

        # ---------------------------------------------------------------- R. a write touches only the two files
        before = snap(u)
        cli(u, "decide", ids["U15"], "approve", *UO, "--scope", "Run the one-off check, once", today="2026-10-12")
        after = snap(u)
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        check("R1 a write changes exactly the register and the history",
              changed == {REGISTER_REL, HISTORY_REL}, str(changed))
        check("R2 nothing outside the two files is created", set(after) == set(before))

        # ---------------------------------------------------------------- S. missing / unreadable files
        empty = base / "empty"
        empty.mkdir()
        sh(empty, "git", "init", "-q")
        rc, o, e = cli(empty, "update", today="2026-10-12")
        check("S1 a missing register is reported, not invented (exit 3), with the way to create one",
              rc == 3 and "UNREADABLE" in e and "tasks.py init" in e, e)
        good = (u / REGISTER_REL).read_bytes()
        (u / REGISTER_REL).write_bytes(b"| bad\r\n")
        rc, o, e = cli(u, "update", today="2026-10-12")
        check("S2 an unreadable register is exit 3, not a traceback", rc == 3 and "Traceback" not in e, e)
        (u / REGISTER_REL).write_bytes(good)
        rc, o, e = cli(u, "frobnicate", today="2026-10-12")
        check("S3 a bad command is a usage error (exit 2)", rc == 2)

        # ---------------------------------------------------------------- T. summary for session-orient
        s = summary(u, "casaray-v3-design")
        check("T1 summary() gives session-orient the counts for the identified project",
              s["resolved"] and s["awaiting"] == 6 and s["paused"] == 1 and "tooling" in s["projects"], str(s))

        # ---------------------------------------------------------------- U. repository guards are untouched
        real = repo_root(SELF.parent)
        guard = real / "scripts" / "deny_device_control.py"
        settings = real / ".claude" / "settings.json"
        if guard.is_file() and settings.is_file():
            def hook(tool):
                return subprocess.run([sys.executable, str(guard)], input=json.dumps({"tool_name": tool}),
                                      capture_output=True, text=True).stdout
            check("U1 the device-control hook still denies HassTurnOn", "deny" in hook("mcp__Home_Assistant__intent__HassTurnOn"))
            check("U2 the device-control hook still allows read-only GetLiveContext", hook("mcp__Home_Assistant__homeassistant__GetLiveContext").strip() == "")
            st = json.loads(settings.read_text(encoding="utf-8"))
            check("U3 settings.json still wires the hook and keeps the deny list",
                  "deny_device_control.py" in json.dumps(st.get("hooks", {})) and len(st["permissions"]["deny"]) >= 20)
            rc, out = git(real, "diff", "--quiet", "HEAD", "--", ".claude/settings.json", "scripts/deny_device_control.py")
            check("U4 neither guard file differs from HEAD", rc == 0)
            check("U5 this tool defines no Home Assistant, device or purchase operation",
                  not re.search(r"\b(HassTurn|call_service|light\.turn_on|lock\.unlock|send_message|create_draft)\b", body))
        else:
            check("U0 repository guards (skipped: not inside the repository)", True)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        if not ok:
            print(f"FAIL  {name}")
            if detail:
                print("      " + str(detail).replace("\n", "\n      ")[:900])
    print(f"{len(results) - len(failed)} of {len(results)} checks passed" if failed else
          f"ok: all {len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
