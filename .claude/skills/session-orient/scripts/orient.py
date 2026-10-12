#!/usr/bin/env python3
"""Orient a session in the Deez Smart Home repository, and check scope before a commit.

WHY THIS EXISTS

Two rule sets govern this repository and they disagree about where a push may
go. The root CLAUDE.md says to push to ha-deploy and
claude/ha-dashboard-upgrades-wui7ig. design/casaray-v3/CLAUDE.md says V3 work
pushes only to casaray-v3-design and never touches ha-deploy. Which one applies
depends on the branch. Working it out from memory, per session, is how a push
goes to the wrong place. This resolves the branch to a rule set and prints what
follows from it, so the answer is read rather than recalled.

READ-ONLY, AND PROVEN SO

No network. No write of any kind. Every git call goes through git(), which
accepts an allowlist of read-only subcommands and refuses everything else,
including `branch <name>`, `config`, `fetch`, `commit`, `push` and any
`--output` flag. `--selftest` demonstrates each refusal. Remote freshness is
therefore NOT checked; the report says so and prints the command to run.

USAGE

  orient.py                       orientation report
  orient.py --scope               also classify every changed path
  orient.py --scope --approved WORKFLOW_AUDIT.md --approved '.claude/skills/*/'
  orient.py --json                machine-readable
  orient.py --branch NAME         simulate a branch (fixtures, "what if")
  orient.py --selftest            prove the tool, in a throwaway repository

EXIT CODES

  0  ok            1  scope check found a path outside or blocked
  2  usage error   3  the rules for this branch are not settled: an unrecognised
                      branch, or one where the push target is not stated (ask the owner)

--approved is an assertion by the caller that the owner approved a path. This
tool cannot verify it, says so in its output, and it never overrides BLOCKED.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# git, read-only
# --------------------------------------------------------------------------

# subcommand -> None (any further arguments) or the set of permitted first
# arguments. Anything not listed here is refused.
SAFE_GIT = {
    "rev-parse": None,
    "status": None,
    "log": None,
    "rev-list": None,
    "diff": None,
    "ls-files": None,
    "branch": {"--show-current"},
}


class GitRefused(Exception):
    """Raised when something other than a read-only git call is attempted."""


def git(repo: Path, *args: str) -> tuple[int, str]:
    """Run an allowlisted read-only git command. Returns (returncode, stdout)."""
    if not args or args[0] not in SAFE_GIT:
        raise GitRefused(f"git {args[0] if args else ''!r} is not a read-only call")
    allowed_first = SAFE_GIT[args[0]]
    if allowed_first is not None and (len(args) < 2 or args[1] not in allowed_first):
        raise GitRefused(f"git {' '.join(args[:2])!r} is not permitted")
    if any(a.startswith("--output") for a in args):
        raise GitRefused("--output writes a file")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, env=env, check=False)
    return p.returncode, p.stdout


# --------------------------------------------------------------------------
# rule sets ("regimes")
# --------------------------------------------------------------------------

@dataclass
class Regime:
    key: str
    label: str
    branch_patterns: list
    # Path prefixes writes are confined to, or None when this tool does not
    # confine them (V2 work spans the repository; the protected list still applies).
    allowed_prefixes: list | None
    push_allowed: list
    push_forbidden: list
    gates: list
    notes: list
    must_read: list
    # (relative file, literal text) pairs this entry was written from. If the
    # text is no longer in the file, the rules may have moved: warn, do not trust.
    sources: list = field(default_factory=list)
    needs_confirmation: bool = False


V3_GATES = [
    "python3 design/casaray-v3/tools/verify_entities.py   (every entity ID exists in the export)",
    'NODE_PATH="$(npm root -g)" node design/casaray-v3/tools/test_and_capture.cjs   '
    "(needs Playwright + Chromium; run before design commits)",
    "bash scripts/ha_validate.sh   ONLY if anything outside design/casaray-v3/ was touched",
]
V3_FORBIDDEN = [
    "any commit, merge, rebase, push or pull request against ha-deploy",
    "claude/ha-dashboard-upgrades-wui7ig (the V2 mirror; not a V3 target)",
    "deploy, sync, reload or restart of Home Assistant; any device or config state change",
    "force-push or history rewrite (denied by .claude/settings.json)",
]
V3_SOURCES = [
    ("design/casaray-v3/CLAUDE.md", "Integration branch: `casaray-v3-design`"),
    ("design/casaray-v3/CLAUDE.md", "No changes to `ha-deploy`"),
    ("design/casaray-v3/CLAUDE.md", "casaray-v3/agent-*"),
    ("design/casaray-v3/CLAUDE.md", "explicit approval from Ray"),
]

REGIMES = [
    Regime(
        key="v3-integrator",
        label="CasaRay V3 design: integration branch",
        branch_patterns=["casaray-v3-design"],
        allowed_prefixes=["design/casaray-v3/"],
        push_allowed=["origin casaray-v3-design"],
        push_forbidden=V3_FORBIDDEN,
        gates=V3_GATES,
        notes=[
            "V3 is design and prototyping only; nothing here is deployed.",
            "Only the integrator commits to, merges into and pushes this branch; "
            "specialists push their own casaray-v3/agent-* branch.",
            "A change outside design/casaray-v3/ needs explicit approval from Ray.",
            "SHA stamping and the V2 tracking documents are not used from V3; "
            "record history in design/casaray-v3/DECISIONS.md.",
            "Show the owner a render or screenshot at each design milestone "
            "before building on it.",
        ],
        must_read=["CLAUDE.md", "design/casaray-v3/CLAUDE.md",
                   "design/casaray-v3/DECISIONS.md"],
        sources=V3_SOURCES,
    ),
    Regime(
        key="v3-specialist",
        label="CasaRay V3 design: specialist branch",
        branch_patterns=["casaray-v3/agent-*"],
        allowed_prefixes=["design/casaray-v3/"],
        push_allowed=["origin <this branch> (your own casaray-v3/agent-* branch only)"],
        push_forbidden=["casaray-v3-design (the integrator merges after review)"] + V3_FORBIDDEN,
        gates=V3_GATES,
        notes=[
            "Specialists never merge into casaray-v3-design.",
            "A change outside design/casaray-v3/ needs explicit approval from Ray.",
        ],
        must_read=["CLAUDE.md", "design/casaray-v3/CLAUDE.md",
                   "design/casaray-v3/DECISIONS.md"],
        sources=V3_SOURCES,
    ),
    Regime(
        key="v2-deploy",
        label="CasaRay V2: deployment branch",
        branch_patterns=["ha-deploy"],
        allowed_prefixes=None,
        push_allowed=["origin ha-deploy",
                      "origin ha-deploy:claude/ha-dashboard-upgrades-wui7ig  (both, every batch)"],
        push_forbidden=["any casaray-v3 branch", "force-push or history rewrite"],
        gates=["bash scripts/ha_validate.sh   (exit 0 or do not push)",
               "bash scripts/verify_change.sh   (structural diff and render diff against HEAD)"],
        notes=[
            "Fast-forward local ha-deploy before pushing, or the push reports "
            "'Everything up-to-date' and the commit never deploys.",
            "Committed in Git is not live in Home Assistant: the owner runs "
            "scripts/sync_casaray_to_config.sh.",
            "SHA stamping: commit with a placeholder, then a `docs: stamp` commit. "
            "Never amend. A rebase invalidates a stamp (see 86ec579).",
            "dashboards/deez_smart_home.yaml is the legacy baseline: do not modify.",
        ],
        must_read=["CLAUDE.md", "PROJECT_STATE.md"],
        sources=[("CLAUDE.md", "claude/ha-dashboard-upgrades-wui7ig"),
                 ("CLAUDE.md", "bash scripts/ha_validate.sh")],
    ),
    Regime(
        key="v2-session",
        label="Session branch (push target not stated)",
        branch_patterns=["claude/*"],
        allowed_prefixes=None,
        push_allowed=[],
        push_forbidden=["any casaray-v3 branch", "force-push or history rewrite"],
        gates=["bash scripts/ha_validate.sh   (exit 0 or do not push)"],
        notes=[
            "The root rules govern content. Their push rule names ha-deploy and "
            "claude/ha-dashboard-upgrades-wui7ig; this branch is neither.",
            "Confirm the push target with the owner before pushing.",
        ],
        must_read=["CLAUDE.md"],
        sources=[("CLAUDE.md", "claude/ha-dashboard-upgrades-wui7ig")],
        needs_confirmation=True,
    ),
    Regime(
        key="recovery",
        label="Recovery branch (owner-gated)",
        branch_patterns=["recovery/*"],
        allowed_prefixes=None,
        push_allowed=[],
        push_forbidden=["anything that touches the live instance without approval"],
        gates=[],
        notes=[
            "No rule file for this branch is checked out here. Its commit messages "
            "call it a temporary, non-deploy branch and mark every write step as "
            "needing approval. Treat every live-system step as owner-only.",
            "Use the recovery-triage skill.",
        ],
        must_read=["CLAUDE.md", "MAINTENANCE.md"],
        sources=[("MAINTENANCE.md", "anything that could cause lockout")],
        needs_confirmation=True,
    ),
]

UNKNOWN = Regime(
    key="unknown",
    label="No known rule set for this branch",
    branch_patterns=[],
    allowed_prefixes=None,
    push_allowed=[],
    push_forbidden=["pushing anywhere before the owner says which rules apply"],
    gates=[],
    notes=["Do not assume V2 or V3. Ask the owner which rules apply before the first write."],
    must_read=["CLAUDE.md"],
    needs_confirmation=True,
)


def resolve_regime(branch: str) -> Regime:
    for r in REGIMES:
        if any(fnmatch.fnmatchcase(branch, pat) for pat in r.branch_patterns):
            return r
    return UNKNOWN


# --------------------------------------------------------------------------
# protected paths
# --------------------------------------------------------------------------

# Home Assistant files the validation gate (scripts/ha_validate.sh, section 4)
# refuses to see modified, plus the secret-bearing names it refuses to see tracked.
#
# One deliberate difference: `.storage/` is blocked at any depth, not only at the
# repository root as in the gate. A copy of Home Assistant's registry under a
# subdirectory is no less sensitive.
PROTECTED_RE = re.compile(
    r"(^|/)(secrets\.ya?ml|configuration\.yaml|automations\.yaml|scripts\.yaml|"
    r"scenes\.yaml|known_devices\.yaml|ip_bans\.yaml|auth_provider\..*)$"
    r"|(^|/)\.storage/|(^|/)\.env"
)
SECRET_NAME_RE = re.compile(
    r"(^|/)(secrets\.ya?ml|\.env|id_rsa|id_ed25519|known_hosts|authorized_keys)$"
    r"|\.(pem|key|p12|pfx|token)$"
)
# CLAUDE.md "Do not touch without an explicit instruction".
DEPLOY_BRIDGE = {
    "scripts/deploy_env.sh", "scripts/deploy_askpass.sh", "scripts/deploy_diagnose.sh",
    "DEPLOY_AUTH.md",
}
# The device-control guard is part of the recovery path (MAINTENANCE.md).
GUARD_FILES = {".claude/settings.json", "scripts/deny_device_control.py"}
LEGACY = {"dashboards/deez_smart_home.yaml"}


def classify(path: str, regime: Regime, approved: list[str]) -> tuple[str, str]:
    """Return (verdict, reason). Verdicts: OK, APPROVED, OUTSIDE, BLOCKED."""
    is_example = path.endswith(".env.example")      # the gate allows this one name
    if not is_example and SECRET_NAME_RE.search(path):
        return "BLOCKED", "secret-bearing file name"
    if not is_example and PROTECTED_RE.search(path):
        return "BLOCKED", "protected Home Assistant path (MAINTENANCE.md)"
    if path in DEPLOY_BRIDGE:
        return "BLOCKED", "deployment bridge: do not touch without an explicit instruction"
    if path in GUARD_FILES:
        return "BLOCKED", "device-control guard: part of the recovery path"
    if path in LEGACY:
        return "BLOCKED", "legacy dashboard: do not modify without an explicit instruction"
    if regime.allowed_prefixes is None:
        return "OK", ""
    if any(path.startswith(p) for p in regime.allowed_prefixes):
        return "OK", ""
    for pat in approved:
        if fnmatch.fnmatchcase(path, pat) or (pat.endswith("/") and path.startswith(pat)):
            return "APPROVED", f"approval asserted by caller for {pat!r}; not verified"
    return "OUTSIDE", f"not under {', '.join(regime.allowed_prefixes)}"


# --------------------------------------------------------------------------
# changed files and added lines
# --------------------------------------------------------------------------

def parse_porcelain_z(raw: str) -> list[tuple[str, str]]:
    """Parse `git status --porcelain=v1 -z`. Returns [(source, path)]."""
    out: list[tuple[str, str]] = []
    tokens = raw.split("\0")
    i = 0
    while i < len(tokens):
        t = tokens[i]
        i += 1
        if len(t) < 4:
            continue
        x, y, path = t[0], t[1], t[3:]
        if x in "RC":          # the next token is the original path; skip it
            i += 1
        if x == "?" and y == "?":
            out.append(("untracked", path))
            continue
        if x not in " ?":
            out.append(("staged", path))
        if y not in " ?":
            out.append(("unstaged", path))
    return out


def valid_ref(repo: Path, ref: str) -> bool:
    if not ref or ref.startswith("-"):
        return False
    rc, _ = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return rc == 0


def upstream_of(repo: Path) -> str | None:
    rc, out = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return out.strip() if rc == 0 and out.strip() else None


def changed_files(repo: Path, base: str | None) -> dict[str, set[str]]:
    files: dict[str, set[str]] = {}
    rc, raw = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if rc == 0:
        for src, path in parse_porcelain_z(raw):
            files.setdefault(path, set()).add(src)
    if base:
        rc, raw = git(repo, "diff", "--name-only", "-z", f"{base}...HEAD")
        if rc == 0:
            for path in filter(None, raw.split("\0")):
                files.setdefault(path, set()).add("committed")
    return files


def added_lines(repo: Path, base: str | None, files: dict[str, set[str]]) -> dict[str, list[str]]:
    """Added lines per path, from the diffs and from untracked files."""
    result: dict[str, list[str]] = {}
    diffs = [["diff", "--cached", "-U0"], ["diff", "-U0"]]
    if base:
        diffs.append(["diff", "-U0", f"{base}...HEAD"])
    for args in diffs:
        rc, text = git(repo, *args)
        if rc != 0:
            continue
        current = None
        for line in text.splitlines():
            if line.startswith("+++ "):
                current = line[6:] if line.startswith("+++ b/") else None
            elif line.startswith("+") and current:
                result.setdefault(current, []).append(line[1:])
    for path, srcs in files.items():
        if "untracked" in srcs:
            p = repo / path
            try:
                if p.is_file() and p.stat().st_size <= 1_000_000:
                    result[path] = p.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                pass
    return result


# --------------------------------------------------------------------------
# minimal credential scan
# --------------------------------------------------------------------------

# Deliberately minimal and high-precision. It is NOT a substitute for section 5
# of scripts/ha_validate.sh, which scans the tracked tree; this looks only at
# lines you are about to add. The first three patterns mirror that gate.

# What follows a credential-looking key when it is NOT a credential: a reference
# (!secret, $VAR, {{ template }}), a placeholder, a bare number, or a call.
_NOT_A_VALUE = (r"(?![!<$({\[]|[\"']?(?:xxx|your|example|changeme|redacted|null|none|true|false)\b"
                r"|\d+[,\s]*$)")

SECRET_PATTERNS = [
    ("JWT-shaped token", re.compile(r"eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}")),
    ("private key header", re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b|github_pat_[A-Za-z0-9_]{30,}")),
    ("credential assignment", re.compile(
        # `key: value` (YAML, JSON), `key = "quoted literal"`, or `KEY=longbarevalue`.
        # Plain code such as `tokens = raw.split(...)` must not match.
        r"(?i)^\s*[\"']?[\w.-]*(?:password|passwd|secret|token|api[_-]?key)[\w.-]*[\"']?\s*(?:"
        r":\s*" + _NOT_A_VALUE + r"[\"']?[^\s'\"#,]{8,}"
        r"|=\s*[\"']" + _NOT_A_VALUE + r"[^\s'\"]{8,}[\"']"
        r"|=\s*" + _NOT_A_VALUE + r"[A-Za-z0-9_\-/+=]{16,}\s*$"
        r")")),
]


def scan_secrets(added: dict[str, list[str]]) -> list[tuple[str, int, str]]:
    """Return [(path, line_number, kind)]. The matched text is never returned."""
    hits = []
    for path, lines in sorted(added.items()):
        for n, line in enumerate(lines, 1):
            for kind, rx in SECRET_PATTERNS:
                if rx.search(line):
                    hits.append((path, n, kind))
                    break
    return hits


# --------------------------------------------------------------------------
# facts
# --------------------------------------------------------------------------

INSTRUCTION_FILES = ["CLAUDE.md", "design/casaray-v3/CLAUDE.md", "PROJECT_STATE.md",
                     "MAINTENANCE.md", "design/casaray-v3/DECISIONS.md"]


def read_text(repo: Path, rel: str) -> str | None:
    try:
        return (repo / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def heading_lines(text: str, wanted: list[str]) -> dict[str, int]:
    found = {}
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            for w in wanted:
                if w.lower() in line.lower() and w not in found:
                    found[w] = n
    return found


def _squash(s: str) -> str:
    """Collapse all whitespace so a phrase wrapped across lines still matches."""
    return " ".join(s.split())


def drift(repo: Path, regime: Regime) -> list[str]:
    missing = []
    cache: dict[str, str | None] = {}
    for rel, needle in regime.sources:
        if rel not in cache:
            text = read_text(repo, rel)
            cache[rel] = None if text is None else _squash(text)
            if text is None:
                missing.append(f"{rel} is not readable here")     # once per file
        text = cache[rel]
        if text is not None and _squash(needle) not in text:
            missing.append(f"{rel} no longer contains: {needle}")
    return missing


def conflicts(repo: Path, regime: Regime) -> list[dict]:
    root = read_text(repo, "CLAUDE.md") or ""
    v3 = read_text(repo, "design/casaray-v3/CLAUDE.md") or ""
    out = []
    if ("claude/ha-dashboard-upgrades-wui7ig" in root
            and "No changes to `ha-deploy`" in v3):
        if regime.key.startswith("v3"):
            status = ("Settled for this branch: follow the V3 file "
                      "('Relationship to the root rules'). Ignore the root push rule.")
        elif regime.key == "unknown":
            status = "Unsettled: the branch is unrecognised, so neither rule can be chosen."
        else:
            status = "Root rule applies on this branch; never push to a V3 branch from here."
        out.append({"id": "C1", "topic": "push target",
                    "text": "Root CLAUDE.md pushes to ha-deploy and a claude/ mirror; "
                            "the V3 file forbids touching ha-deploy.",
                    "status": status})
    if (re.search(r"PROJECT_STATE\.md`? in full", root) and "selectively" in root):
        out.append({"id": "C5", "topic": "reading PROJECT_STATE.md",
                    "text": "Root step 1 says read PROJECT_STATE.md in full; step 3 and the "
                            "file's own Context Loading Strategy say load selectively.",
                    "status": "Unsettled: the owner's call. This tool reports it and does not choose."})
    return out


def gather(repo: Path, branch_override: str | None) -> dict:
    rc, cur = git(repo, "branch", "--show-current")
    branch = branch_override if branch_override is not None else cur.strip()
    regime = resolve_regime(branch) if branch else UNKNOWN
    up = upstream_of(repo)
    ahead = behind = None
    if up:
        rc, out = git(repo, "rev-list", "--left-right", "--count", "@{u}...HEAD")
        if rc == 0 and len(out.split()) == 2:
            behind, ahead = (int(x) for x in out.split())
    rc, st = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = parse_porcelain_z(st) if rc == 0 else []
    rc, shallow = git(repo, "rev-parse", "--is-shallow-repository")
    rc2, count = git(repo, "rev-list", "--count", "HEAD")
    rc3, recent = git(repo, "log", "--oneline", "--no-decorate", "-n", "8")

    docs = []
    for rel in INSTRUCTION_FILES:
        p = repo / rel
        docs.append({"path": rel, "exists": p.is_file(),
                     "bytes": p.stat().st_size if p.is_file() else 0})
    ps = read_text(repo, "PROJECT_STATE.md") or ""
    settings = read_text(repo, ".claude/settings.json") or ""
    return {
        "repo": str(repo),
        "branch": branch or "(detached HEAD)",
        "simulated": branch_override is not None,
        "regime": {"key": regime.key, "label": regime.label,
                   "needs_confirmation": regime.needs_confirmation,
                   "allowed_prefixes": regime.allowed_prefixes,
                   "push_allowed": regime.push_allowed,
                   "push_forbidden": regime.push_forbidden,
                   "gates": regime.gates, "notes": regime.notes,
                   "must_read": regime.must_read},
        "upstream": up, "ahead": ahead, "behind": behind,
        "tree": {"changed_entries": len(entries),
                 "untracked": sum(1 for s, _ in entries if s == "untracked"),
                 "clean": not entries},
        "history": {"shallow": shallow.strip() == "true",
                    "commits_visible": int(count.strip()) if rc2 == 0 and count.strip() else None,
                    "recent": recent.strip().splitlines() if rc3 == 0 else []},
        "instruction_files": docs,
        "project_state_headings": heading_lines(
            ps, ["Context Loading Strategy", "Routine Startup Profiles", "Protected Areas"]),
        "conflicts": conflicts(repo, regime),
        "drift": drift(repo, regime),
        "device_guard_present": "deny_device_control.py" in settings,
    }


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def render(f: dict) -> str:
    r = f["regime"]
    L = ["SESSION ORIENTATION  (read-only: nothing was fetched, changed or pushed)", ""]
    sim = "   [SIMULATED branch name]" if f["simulated"] else ""
    if f["upstream"] and f["ahead"] is not None:
        up = f"  [{f['upstream']}: {f['ahead']} ahead, {f['behind']} behind, as of the last fetch]"
    else:
        up = "  [no upstream configured]"
    L.append(f"BRANCH     {f['branch']}{up}{sim}")
    L.append(f"RULES      {r['label']}  ({r['key']})")
    if r["needs_confirmation"]:
        L.append("           >> NOT SETTLED: ask the owner before the first write or any push.")
    t = f["tree"]
    L.append("TREE       " + ("clean" if t["clean"] else
                              f"{t['changed_entries']} changed entries, {t['untracked']} untracked"))
    h = f["history"]
    if h["shallow"]:
        L.append(f"HISTORY    SHALLOW CLONE: {h['commits_visible']} commits visible. Anything counted "
                 "from history undercounts.")
        L.append("           Deepen (history only): git fetch --unshallow origin <branch>   [not run]")
    else:
        L.append(f"HISTORY    {h['commits_visible']} commits visible (full history)")
    L.append("")
    if r["allowed_prefixes"]:
        L.append("MAY WRITE  " + ", ".join(p + "**" for p in r["allowed_prefixes"]))
        L.append("           anything else needs the owner's explicit approval")
    elif r["key"] in ("v2-deploy", "v2-session"):
        L.append("MAY WRITE  per root CLAUDE.md and MAINTENANCE.md; protected paths excepted")
    else:
        L.append("MAY WRITE  unknown: not settled for this branch")
    L.append("MAY PUSH   " + ("; ".join(r["push_allowed"]) if r["push_allowed"]
                              else "nothing is settled for this branch"))
    for i, item in enumerate(r["push_forbidden"]):
        L.append(("MUST NOT   " if i == 0 else "           ") + item)
    for i, item in enumerate(r["gates"]):
        L.append(("GATES      " if i == 0 else "           ") + item)
    L.append("")
    for i, item in enumerate(r["notes"]):
        L.append(("NOTES      " if i == 0 else "           ") + item)
    L.append("")
    L.append("READ       (sizes; tokens are bytes/4, an estimate)")
    for d in f["instruction_files"]:
        mark = "must read" if d["path"] in r["must_read"] else "reference"
        if d["exists"]:
            L.append(f"           {d['path']:<34} {d['bytes']:>8,} B  ~{d['bytes'] // 4:>6,} tokens  {mark}")
        elif d["path"] in r["must_read"]:
            L.append(f"           {d['path']:<34} MISSING (listed as must read)")
    ph = f["project_state_headings"]
    if ph:
        L.append("           PROJECT_STATE.md sections: " +
                 ", ".join(f"{k} (line {v})" for k, v in ph.items()))
    if f["conflicts"]:
        L.append("")
        L.append("CONTRADICTIONS BETWEEN INSTRUCTION FILES")
        for c in f["conflicts"]:
            L.append(f"  {c['id']}  {c['topic']}: {c['text']}")
            L.append(f"        {c['status']}")
    warn = []
    if f["drift"]:
        warn.append("RULE TABLE MAY BE STALE. This tool's rules were written from text that has changed:")
        warn += [f"  - {m}" for m in f["drift"]]
        warn.append("  Read the instruction files directly; do not rely on the lines above.")
    if not f["device_guard_present"]:
        warn.append("Device-control guard (deny_device_control.py) not found in .claude/settings.json.")
    if warn:
        L.append("")
        L.append("WARNINGS")
        L += [f"  {w}" if not w.startswith("  ") else w for w in warn]
    L.append("")
    L.append("NOT CHECKED  remote freshness (offline by design); live Home Assistant state;")
    L.append("             whether PROJECT_STATE.md changed since you last read it.")
    return "\n".join(L)


def render_scope(rows: list[dict], hits: list, base: str | None, regime: Regime) -> str:
    L = ["", f"SCOPE CHECK  rules: {regime.key}  base: {base or 'none (committed-but-unpushed changes NOT examined)'}"]
    if not rows:
        L.append("  no changed files found")
    for row in rows:
        L.append(f"  {row['verdict']:<9} {row['path']}   [{','.join(sorted(row['sources']))}]"
                 + (f"   {row['reason']}" if row["reason"] else ""))
    if hits:
        L.append("  CREDENTIAL-SHAPED TEXT in lines you are adding (value not shown):")
        for path, n, kind in hits:
            L.append(f"    {path}:{n}  {kind}")
    bad = [r for r in rows if r["verdict"] in ("OUTSIDE", "BLOCKED")]
    appr = [r for r in rows if r["verdict"] == "APPROVED"]
    if appr:
        L.append("  note: APPROVED rows rest on the caller's assertion; this tool cannot verify approval.")
    if bad or hits:
        n_out = sum(1 for r in bad if r["verdict"] == "OUTSIDE")
        n_blk = sum(1 for r in bad if r["verdict"] == "BLOCKED")
        L.append(f"RESULT  FAIL: {n_out} outside, {n_blk} blocked, {len(hits)} credential-shaped. "
                 "Do not commit until the owner has decided.")
    elif appr:
        L.append("RESULT  PASS: every changed path is in scope or covered by an approval the caller asserted; "
                 "nothing credential-shaped added.")
    else:
        L.append("RESULT  PASS: every changed path is within scope, nothing credential-shaped added.")
    L.append("        This is a scope and credential check only. It does not run the gates above.")
    return "\n".join(L)


def scope(repo: Path, regime: Regime, base: str | None, approved: list[str]):
    files = changed_files(repo, base)
    rows = []
    for path in sorted(files):
        verdict, reason = classify(path, regime, approved)
        rows.append({"path": path, "sources": sorted(files[path]),
                     "verdict": verdict, "reason": reason})
    hits = scan_secrets(added_lines(repo, base, files))
    failed = any(r["verdict"] in ("OUTSIDE", "BLOCKED") for r in rows) or bool(hits)
    return rows, hits, failed


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def _run(cwd: Path, *args: str) -> None:
    """Fixture setup only: a raw git call inside a throwaway repository."""
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    subprocess.run(["git", "-C", str(cwd), "-c", "commit.gpgsign=false", *args],
                   check=True, capture_output=True, env=env)


def selftest() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        results.append((name, bool(cond), detail))

    # 1. regime resolution
    for br, want in [("casaray-v3-design", "v3-integrator"), ("casaray-v3/agent-2-visual-ux", "v3-specialist"),
                     ("ha-deploy", "v2-deploy"), ("claude/determined-thompson-abc", "v2-session"),
                     ("recovery/phase0-diagnostics", "recovery"), ("main", "unknown"),
                     ("autonomous/casaray-dev", "unknown"), ("", "unknown")]:
        got = resolve_regime(br).key if br else UNKNOWN.key
        check(f"regime {br or '(detached)'!r} -> {want}", got == want, f"got {got}")

    # 2. classification
    v3 = resolve_regime("casaray-v3-design")
    v2 = resolve_regime("ha-deploy")
    cases = [("design/casaray-v3/README.md", v3, [], "OK"),
             ("WORKFLOW_AUDIT.md", v3, [], "OUTSIDE"),
             ("WORKFLOW_AUDIT.md", v3, ["WORKFLOW_AUDIT.md"], "APPROVED"),
             (".claude/skills/x/SKILL.md", v3, [".claude/skills/"], "APPROVED"),
             ("secrets.yaml", v3, ["secrets.yaml"], "BLOCKED"),
             ("config/.storage/auth", v3, [], "BLOCKED"),
             (".storage/auth", v2, [], "BLOCKED"),
             ("DEPLOY_AUTH.md", v2, [], "BLOCKED"),
             ("scripts/deploy_env.sh", v2, ["scripts/deploy_env.sh"], "BLOCKED"),
             (".claude/settings.json", v2, [], "BLOCKED"),
             ("dashboards/deez_smart_home.yaml", v2, [], "BLOCKED"),
             ("dashboards/casaray_v2.yaml", v2, [], "OK"),
             (".env.example", v2, [], "OK"),
             ("keys/server.pem", v2, [], "BLOCKED")]
    for path, reg, appr, want in cases:
        got = classify(path, reg, appr)[0]
        check(f"classify {path} under {reg.key} approved={appr} -> {want}", got == want, f"got {got}")

    # 3. porcelain parsing, including a rename and a path with a space
    raw = " M a.txt\0A  b b.txt\0R  new.txt\0old.txt\0?? c.txt\0"
    parsed = parse_porcelain_z(raw)
    check("porcelain parse", parsed == [("unstaged", "a.txt"), ("staged", "b b.txt"),
                                        ("staged", "new.txt"), ("untracked", "c.txt")], str(parsed))

    # 4. credential scan: positives are built at run time so this file holds no token
    jwt = "eyJ" + "a" * 20 + "." + "b" * 20
    ghp = "ghp_" + "A" * 36
    pk = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
    sample = {"x.md": [f"token: {jwt}", f"url https://x@{ghp}", pk, "password: hunter2hunter2",
                       "password: !secret ha_password", "token: <your token here>",
                       "the password is rotated monthly", "api_key: example", "ok line"]}
    hits = scan_secrets(sample)
    kinds = {(n, k) for _, n, k in hits}
    check("scan finds JWT", (1, "JWT-shaped token") in kinds, str(kinds))
    check("scan finds GitHub token", (2, "GitHub token") in kinds, str(kinds))
    check("scan finds private key header", (3, "private key header") in kinds, str(kinds))
    check("scan finds credential assignment", (4, "credential assignment") in kinds, str(kinds))
    check("scan ignores !secret refs, placeholders and prose", {n for n, _ in kinds} == {1, 2, 3, 4}, str(kinds))
    check("scan never returns the matched text", all(jwt not in str(h) and ghp not in str(h) for h in hits))
    # Forms that are credentials, and code that merely contains the words.
    # Built by joining parts so that no line of THIS file is itself assignment-shaped,
    # which would make the tool flag its own source.
    def S(*parts: str) -> str:
        return "".join(parts)

    pos = [S("API_KEY", "=", "k" * 24),
           S("password", " = ", '"', "q" * 12, '"'),
           S('  "token"', ": ", '"', "z" * 12, '"'),
           S("client_secret", ": ", "s" * 16)]
    neg = [S("tokens", " = ", 'raw.split("\\0")'),
           S("SECRET_NAME_RE", " = ", "re.compile("),
           S("token", " = ", "get_token()"),
           S("token_budget", ": ", "100000000"),
           S("password", ": ", "!secret ha_password"),
           S("token", ": ", '{{ states("x") }}'),
           S("secret", " = ", 'os.environ["X"]'),
           S("password", ": ", "${DB_PASSWORD}"),
           S("api_key", ": ", "null"),
           S("def check_token(self, ", "value):")]
    check("scan flags real credential forms",
          all(scan_secrets({"f": [s]}) for s in pos), str([s for s in pos if not scan_secrets({"f": [s]})]))
    check("scan ignores code that only contains the words",
          not any(scan_secrets({"f": [s]}) for s in neg), str([s for s in neg if scan_secrets({"f": [s]})]))
    wrapped = "needs explicit approval from\n    Ray first."
    check("drift squashes line wraps", _squash("explicit approval from Ray") in _squash(wrapped))

    # 5. the git wrapper refuses everything that writes
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "r"
        repo.mkdir()
        _run(repo, "init", "-q", "-b", "casaray-v3-design")
        (repo / "design/casaray-v3").mkdir(parents=True)
        (repo / "design/casaray-v3/a.md").write_text("one\n")
        # The text the V3 rule table was written from (see V3_SOURCES).
        (repo / "design/casaray-v3/CLAUDE.md").write_text(
            "Integration branch: `casaray-v3-design`\nNo changes to `ha-deploy`\n"
            "casaray-v3/agent-*\nexplicit approval from Ray\n")
        (repo / "CLAUDE.md").write_text("Read `PROJECT_STATE.md` in full. Load selectively. "
                                        "claude/ha-dashboard-upgrades-wui7ig bash scripts/ha_validate.sh\n")
        _run(repo, "add", "-A")
        _run(repo, "commit", "-q", "-m", "base")
        for args in [("push",), ("commit", "-m", "x"), ("fetch",), ("checkout", "-b", "z"),
                     ("reset", "--hard"), ("branch", "newbranch"), ("branch", "-D", "x"),
                     ("config", "user.name", "x"), ("remote", "add", "o", "u"),
                     ("diff", "--output=out.txt"), ("add", "-A"), ("stash",), ("tag", "t")]:
            try:
                git(repo, *args)
                check(f"git wrapper refuses {' '.join(args)}", False, "was allowed")
            except GitRefused:
                check(f"git wrapper refuses {' '.join(args)}", True)
        check("git wrapper allows branch --show-current",
              git(repo, "branch", "--show-current")[1].strip() == "casaray-v3-design")

        # 6. scope check end to end, and proof that nothing was written
        index_before = (repo / ".git/index").read_bytes()
        (repo / "design/casaray-v3/a.md").write_text("two\n")                     # in scope
        (repo / "notes.md").write_text("outside\n")                              # outside
        (repo / "secrets.yaml").write_text("x: 1\n")                             # blocked
        (repo / "design/casaray-v3/b.md").write_text(f"token: {jwt}\n")          # credential
        after_edit = _tree_state(repo)
        rows, hits, failed = scope(repo, v3, None, [])
        verdicts = {r["path"]: r["verdict"] for r in rows}
        check("scope: in-scope file is OK", verdicts.get("design/casaray-v3/a.md") == "OK", str(verdicts))
        check("scope: root file is OUTSIDE", verdicts.get("notes.md") == "OUTSIDE", str(verdicts))
        check("scope: secrets.yaml is BLOCKED", verdicts.get("secrets.yaml") == "BLOCKED", str(verdicts))
        check("scope: credential found in untracked file", ("design/casaray-v3/b.md", 1, "JWT-shaped token") in hits, str(hits))
        check("scope: overall FAIL", failed)
        check("scope wrote nothing to the worktree", _tree_state(repo) == after_edit)
        check("scope left the git index untouched", (repo / ".git/index").read_bytes() == index_before)
        rows, hits, failed = scope(repo, v3, None, ["notes.md"])
        check("scope: approval flag does not clear BLOCKED or credentials", failed)
        (repo / "notes.md").unlink()
        (repo / "secrets.yaml").unlink()
        (repo / "design/casaray-v3/b.md").unlink()
        rows, hits, failed = scope(repo, v3, None, [])
        check("scope: clean in-scope change passes", not failed, str(rows))
        facts = gather(repo, None)
        check("gather: regime from the real branch", facts["regime"]["key"] == "v3-integrator")
        check("gather: no drift when sources are present", facts["drift"] == [], str(facts["drift"]))
        check("gather: C5 detected", any(c["id"] == "C5" for c in facts["conflicts"]))
        facts = gather(repo, "ha-deploy")
        check("gather: simulated branch is flagged", facts["simulated"] and facts["regime"]["key"] == "v2-deploy")
        (repo / "design/casaray-v3/CLAUDE.md").unlink()
        gone = drift(repo, v3)
        check("drift: an unreadable source is reported once, not once per needle",
              gone == ["design/casaray-v3/CLAUDE.md is not readable here"], str(gone))
        (repo / "design/casaray-v3/CLAUDE.md").write_text(
            "Integration branch: `casaray-v3-design`\nNo changes to `ha-deploy`\n"
            "casaray-v3/agent-*\nexplicit approval from Ray\n")
        (repo / "design/casaray-v3/CLAUDE.md").write_text("rewritten\n")
        snap, index_snap = _tree_state(repo), (repo / ".git/index").read_bytes()
        facts = gather(repo, None)
        text = render(facts)
        check("drift: changed source text is reported", bool(facts["drift"]), str(facts["drift"]))
        check("render states the rules may be stale", "RULE TABLE MAY BE STALE" in text)
        check("orient wrote nothing to the worktree", _tree_state(repo) == snap)
        check("orient left the git index untouched", (repo / ".git/index").read_bytes() == index_snap)

    # 7. exit codes, through main() itself, for simulated branches (read-only on the real repo)
    import contextlib
    import io
    for br, want in [("casaray-v3-design", 0), ("casaray/agent-x", 3), ("casaray-v3/agent-x", 0),
                     ("ha-deploy", 0), ("main", 3), ("claude/abc", 3), ("recovery/x", 3)]:
        with contextlib.redirect_stdout(io.StringIO()):
            got = main(["--branch", br])
        check(f"exit code for branch {br!r} -> {want}", got == want, f"got {got}")
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        try:                                   # argparse refuses an option where a value is expected
            got = main(["--scope", "--base", "--evil"])
        except SystemExit as e:
            got = e.code
        check("--base followed by an option is refused (exit 2)", got == 2, f"got {got}")
        check("--base=-dash value is refused by the tool's own guard (exit 2)",
              main(["--scope", "--base=--evil"]) == 2)
        check("--base naming no commit is refused (exit 2)", main(["--scope", "--base", "no-such-ref-xyz"]) == 2)

    ok = all(c for _, c, _ in results)
    for name, cond, detail in results:
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if not cond and detail else ""))
    print(f"\n{sum(1 for _, c, _ in results if c)}/{len(results)} checks passed")
    return 0 if ok else 1


def _tree_state(repo: Path) -> dict:
    """Snapshot of file names, sizes and contents, excluding .git."""
    snap = {}
    for p in sorted(repo.rglob("*")):
        if ".git" in p.relative_to(repo).parts or not p.is_file():
            continue
        snap[str(p.relative_to(repo))] = p.read_bytes()
    return snap


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="repository root (default: from the current directory, "
                                   "else from this script's location)")
    ap.add_argument("--branch", help="simulate this branch name instead of reading it")
    ap.add_argument("--scope", action="store_true", help="classify every changed path")
    ap.add_argument("--base", help="compare committed work against this ref "
                                   "(default: the branch's upstream, if any)")
    ap.add_argument("--approved", action="append", default=[], metavar="PATH",
                    help="a path or glob the owner has approved (asserted, not verified)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--selftest", action="store_true", help="prove the tool in a throwaway repo")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.repo:
        repo = Path(args.repo).resolve()
    else:
        rc, out = git(Path.cwd(), "rev-parse", "--show-toplevel")
        repo = Path(out.strip()) if rc == 0 and out.strip() else Path(__file__).resolve().parents[4]
    rc, _ = git(repo, "rev-parse", "--git-dir")
    if rc != 0:
        print(f"error: {repo} is not a git repository", file=sys.stderr)
        return 2

    facts = gather(repo, args.branch)
    regime = resolve_regime(facts["branch"]) if facts["branch"] != "(detached HEAD)" else UNKNOWN

    payload = {"orientation": facts}
    text = render(facts)
    failed = False
    if args.scope:
        base = args.base
        if base is not None and not valid_ref(repo, base):
            print(f"error: --base {base!r} is not a commit in this repository", file=sys.stderr)
            return 2
        if base is None:
            base = upstream_of(repo)
        rows, hits, failed = scope(repo, regime, base, args.approved)
        payload["scope"] = {"base": base, "files": rows,
                            "credential_hits": [{"path": p, "line": n, "kind": k} for p, n, k in hits],
                            "failed": failed}
        text += "\n" + render_scope(rows, hits, base, regime)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(text)
    if args.scope and failed:
        return 1
    if regime.needs_confirmation:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
