#!/usr/bin/env python3
"""Process memory: what workflows keep getting repeated, and which are worth
automating.

WHY THIS EXISTS

Noticing repetition is not the hard part — remembering it across sessions is.
A workflow performed three times in one afternoon is obvious; the same
workflow performed once a week for a month is invisible, and it is the more
expensive one. This keeps a small durable record so the second kind gets
caught too.

The scoring is deterministic and lives here rather than in the skill prose
for one reason: a judgement made the same way every time can be argued with.
`score --explain` shows the arithmetic for any candidate, so when it says
something is worth automating you can check whether you agree.

WHAT IT DELIBERATELY DOES NOT STORE

Command *output*, environment variables, anything matching a secret-shaped
pattern, and full paths outside the repository. What is stored is the SHAPE of
a workflow: normalised commands, which files it touched, how often, how long.
Anything secret-shaped is replaced with <redacted> on the way in, but the real
protection is not putting it there: record the SHAPE of a command, not a
command that had a credential in it.

NORMALISATION

`grep entity_id dashboards/casaray_v2.yaml` and
`grep sensor. dashboards/deez_smart_home.yaml` are the same workflow wearing
different clothes. Before anything is compared, commands are reduced to a
shape: literals become <str>, numbers <n>, git revisions <rev>, and a path
keeps its directory but loses its specific basename. Without this the memory
fills with thousands of unique one-offs and finds nothing.

USAGE

  procmem.py record --name "validate and push" \\
      --step "bash scripts/ha_validate.sh" --step "git add -A" \\
      --step "git commit -F -" --step "git push origin ha-deploy" \\
      --file dashboards/casaray_v2.yaml --minutes 4
  procmem.py observe < commands.txt      # bulk, one command per line
  procmem.py list
  procmem.py score                       # ranked candidates
  procmem.py score --explain "validate and push"
  procmem.py resolve "validate and push" --automated-by scripts/checkpoint.sh
  procmem.py registry                    # regenerate AUTOMATION_REGISTRY.md
  procmem.py prune --older-than 180

EXIT STATUS

  0  ran
  1  `score` found at least one HIGH-value candidate with no automation yet
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
MEMORY = REPO / ".claude" / "process-memory.json"
REGISTRY = REPO / "AUTOMATION_REGISTRY.md"
TODAY = _dt.date.today().isoformat()

# Anything matching these never reaches the file, whatever it was attached to.
# The memory is committed to a public-ish repository and read by future
# sessions; a token in it would outlive the mistake that put it there.
SECRET = re.compile(
    r"(?i)(token|passwd|password|secret|api[-_ ]?key|bearer|authorization"
    r"|ssh-rsa|BEGIN [A-Z ]*PRIVATE KEY|[A-Za-z0-9_\-]{32,}\.[A-Za-z0-9_\-]{6,})")


# --------------------------------------------------------------- normalisation
def normalise(command: str) -> str:
    """Reduce a command to its shape so near-identical runs compare equal."""
    c = command.strip()
    c = re.sub(r"<<'?[A-Z_]+'?[\s\S]*", "<<heredoc", c)          # heredoc bodies
    c = re.sub(r'"[^"]*"', "<str>", c)
    c = re.sub(r"'[^']*'", "<str>", c)
    c = re.sub(r"\b[0-9a-f]{7,40}\b", "<rev>", c)                # git revisions
    c = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "<date>", c)
    c = re.sub(r"(?<![\w.])\d+(?![\w])", "<n>", c)
    # A path keeps its directory and extension but loses the specific file:
    # dashboards/casaray_v2.yaml -> dashboards/*.yaml
    c = re.sub(r"([\w./-]*/)([\w.-]+)\.(\w+)", lambda m: f"{m.group(1)}*.{m.group(3)}", c)
    c = re.sub(r"\s+", " ", c)
    return c.strip()


def redact(text: str) -> str:
    return "<redacted>" if SECRET.search(text or "") else text


def shape(steps) -> str:
    """A stable identity for a sequence of steps, order preserved."""
    return " ; ".join(normalise(s) for s in steps)


# ---------------------------------------------------------------------- store
def load() -> dict:
    if MEMORY.exists():
        try:
            return json.loads(MEMORY.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            sys.exit(f"{MEMORY} is not valid JSON: {exc}")
    return {"version": 1, "workflows": []}


def save(db: dict) -> None:
    MEMORY.parent.mkdir(parents=True, exist_ok=True)
    MEMORY.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")


def find(db, name=None, sig=None):
    for w in db["workflows"]:
        if name and w["name"] == name:
            return w
        if sig and w["signature"] == sig:
            return w
    return None


# -------------------------------------------------------------------- scoring
# Each dimension is small and bounded so no single one can carry a candidate on
# its own. The thresholds are set so that "happened twice" never reaches HIGH:
# the brief this came from is explicit that twice is not a pattern.
def score(w: dict) -> dict:
    n = w.get("occurrences", 1)
    freq = 0 if n < 2 else 1 if n < 3 else 2 if n < 5 else 3 if n < 10 else 4

    s = len(w.get("steps", []))
    steps = 0 if s < 3 else 1 if s < 5 else 2 if s < 8 else 3

    # Minutes saved per run, across every run we expect. Capped because a big
    # self-reported number should not by itself justify building something.
    saved = min(3, int((w.get("minutes", 0) * max(n, 1)) / 15))

    risk = min(2, w.get("failures", 0))
    det = 2 if w.get("deterministic", True) else 0
    penalty = 3 if w.get("automated_by") else 0

    total = freq + steps + saved + risk + det - penalty
    band = "HIGH" if total >= 7 else "MEDIUM" if total >= 4 else "LOW"
    return {"total": total, "band": band, "parts": {
        "frequency": freq, "steps": steps, "time_saved": saved,
        "error_risk": risk, "deterministic": det, "already_automated": -penalty}}


def recommend(w: dict) -> str:
    """The simplest thing that could work, per the automation hierarchy.

    The important case is the last one: reaching for a Claude skill when a
    shell script would do produces something slower, less predictable and
    harder to test. A skill earns its place only where judgement is needed.
    """
    if w.get("automated_by"):
        return f"already: {w['automated_by']} — extend it rather than duplicating"
    if not w.get("deterministic", True):
        return "Claude skill — needs interpretation or judgement"
    if w.get("schedule"):
        return "scheduled task (HA automation or cron)"
    if w.get("gate_on") == "commit":
        return "git hook"
    if w.get("gate_on") == "push":
        return "CI check"
    if w.get("data_processing"):
        return "Python utility"
    return "shell script"


# ------------------------------------------------------------------- commands
def cmd_record(args, db):
    steps = [redact(s) for s in args.step]
    sig = shape(steps)
    w = find(db, name=args.name) or find(db, sig=sig)
    if w:
        w["occurrences"] = w.get("occurrences", 1) + 1
        w["last_seen"] = TODAY
        if args.failed:
            w["failures"] = w.get("failures", 0) + 1
        for f in args.file:
            if f not in w["files"]:
                w["files"].append(f)
        if args.minutes:
            w["minutes"] = max(w.get("minutes", 0), args.minutes)
        print(f"updated {w['name']!r}: {w['occurrences']} occurrence(s)")
    else:
        db["workflows"].append({
            "name": args.name,
            "signature": sig,
            "steps": steps,
            "files": list(args.file),
            "occurrences": 1,
            "first_seen": TODAY,
            "last_seen": TODAY,
            "minutes": args.minutes or 0,
            "failures": 1 if args.failed else 0,
            "deterministic": not args.judgement,
            "data_processing": args.data,
            "schedule": args.schedule,
            "gate_on": args.gate_on,
            "automated_by": args.automated_by,
            "notes": redact(args.note or ""),
        })
        print(f"recorded {args.name!r} ({len(steps)} steps)")
    save(db)
    return 0


def cmd_observe(args, db):
    """Group a stream of commands by normalised shape.

    This is the cheap path: pipe in whatever was run, see what recurs. It does
    not create workflows — a run of similar commands is evidence, not a
    workflow, and naming one is a judgement worth making deliberately.
    """
    lines = [l.strip() for l in sys.stdin if l.strip() and not l.startswith("#")]
    counts = collections.Counter(normalise(l) for l in lines)
    repeated = [(s, n) for s, n in counts.most_common() if n >= args.min_count]
    print(f"{len(lines)} commands, {len(counts)} distinct shapes, "
          f"{len(repeated)} repeated {args.min_count}+ times\n")
    for s, n in repeated:
        known = any(normalise(st) == s for w in db["workflows"] for st in w["steps"])
        print(f"  {n:>3}x  {'[known]' if known else '       '}  {s[:110]}")
    if repeated:
        print("\nName the ones that belong together with `record`; a shape that"
              "\nrecurs is evidence, not yet a workflow.")
    return 0


def cmd_list(args, db):
    if not db["workflows"]:
        print("nothing recorded yet")
        return 0
    for w in sorted(db["workflows"], key=lambda x: -x.get("occurrences", 0)):
        sc = score(w)
        auto = w.get("automated_by") or "-"
        print(f"  {sc['band']:<6} {sc['total']:>2}  {w['occurrences']:>3}x  "
              f"{w['name']:<38} {auto}")
    return 0


def cmd_score(args, db):
    if args.explain:
        w = find(db, name=args.explain)
        if not w:
            sys.exit(f"no workflow named {args.explain!r}")
        sc = score(w)
        print(f"{w['name']}\n")
        for k, v in sc["parts"].items():
            print(f"  {k:<20} {v:+d}")
        print(f"  {'':<20} ----")
        print(f"  {'total':<20} {sc['total']:>2}   -> {sc['band']}")
        print(f"\n  seen {w['occurrences']}x, first {w['first_seen']}, "
              f"last {w['last_seen']}, {len(w['steps'])} steps")
        print(f"  recommendation: {recommend(w)}")
        return 0

    ranked = sorted(db["workflows"], key=lambda w: -score(w)["total"])
    hot = []
    for band in ("HIGH", "MEDIUM", "LOW"):
        rows = [w for w in ranked if score(w)["band"] == band]
        if not rows:
            continue
        print(f"--- {band}")
        for w in rows:
            sc = score(w)
            print(f"  {sc['total']:>2}  {w['name']:<38} {w['occurrences']:>3}x  "
                  f"{recommend(w)}")
            if band == "HIGH" and not w.get("automated_by"):
                hot.append(w["name"])
        print()
    if hot:
        print("HIGH value and not yet automated:")
        for n in hot:
            print(f"  - {n}")
        print("\nBuild the strongest one. Check `inventory.py` first — extending"
              "\nsomething that exists beats adding a ninth script.")
    return 1 if hot else 0


def cmd_resolve(args, db):
    w = find(db, name=args.name)
    if not w:
        sys.exit(f"no workflow named {args.name!r}")
    w["automated_by"] = args.automated_by
    w["automated_on"] = TODAY
    save(db)
    print(f"{w['name']!r} -> {args.automated_by}")
    return 0


def cmd_prune(args, db):
    cutoff = (_dt.date.today() - _dt.timedelta(days=args.older_than)).isoformat()
    keep, drop = [], []
    for w in db["workflows"]:
        # An automated workflow is kept regardless of age: it is the record of
        # WHY the automation exists, which is the part that gets forgotten.
        stale = w["last_seen"] < cutoff and w.get("occurrences", 0) < 3 \
            and not w.get("automated_by")
        (drop if stale else keep).append(w)
    for w in drop:
        print(f"  dropping {w['name']!r} (last seen {w['last_seen']}, "
              f"{w['occurrences']}x, never automated)")
    if not args.dry_run:
        db["workflows"] = keep
        save(db)
    print(f"{len(keep)} kept, {len(drop)} {'would be ' if args.dry_run else ''}dropped")
    return 0


def artefact_type(path: str) -> str:
    """What a resolved automation actually IS, from its path.

    `recommend()` answers "what should this become", which for a solved
    workflow is "already: <path>" — useless as a Type column. This answers
    "what is it".
    """
    first = (path or "").split(" +")[0].strip()
    if "/skills/" in first and first.endswith("SKILL.md"):
        return "claude skill"
    if "/skills/" in first:
        return "skill tooling"
    if first.endswith(".sh"):
        return "shell script"
    if first.endswith(".py"):
        return "python utility"
    if "packages/" in first:
        return "home assistant"
    if ".github/" in first:
        return "ci check"
    if "hooks/" in first:
        return "git hook"
    return "tool"


def cmd_registry(args, db):
    done = [w for w in db["workflows"] if w.get("automated_by")]
    todo = [w for w in db["workflows"]
            if not w.get("automated_by") and score(w)["band"] != "LOW"]
    lines = [
        "# Automation registry",
        "",
        "Generated by `.claude/skills/automate/scripts/procmem.py registry`.",
        "Do not hand-edit — record the workflow and re-run instead, or the next",
        "regeneration silently discards whatever was written here.",
        "",
        f"Last generated {TODAY} from `.claude/process-memory.json`.",
        "",
        "## In place",
        "",
        "| Automation | Type | Replaces | Trigger | Recorded from |",
        "|---|---|---|---|---|",
    ]
    for w in sorted(done, key=lambda x: x["name"]):
        trig = w.get("schedule") or w.get("gate_on") or "manual"
        lines.append(f"| `{w['automated_by']}` | {artefact_type(w['automated_by'])} "
                     f"| {w['name']} ({len(w['steps'])} steps) | {trig} "
                     f"| seen {w['occurrences']}x, {w['first_seen']}–{w['last_seen']} |")
    if not done:
        lines.append("| _(none yet)_ | | | | |")
    lines += ["", "## Candidates", "",
              "| Workflow | Score | Seen | Suggested form |", "|---|---|---|---|"]
    for w in sorted(todo, key=lambda x: -score(x)["total"]):
        sc = score(w)
        lines.append(f"| {w['name']} | {sc['band']} ({sc['total']}) "
                     f"| {w['occurrences']}x | {recommend(w)} |")
    if not todo:
        lines.append("| _(none above LOW)_ | | | |")
    lines.append("")
    REGISTRY.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REGISTRY.relative_to(REPO)}  "
          f"({len(done)} in place, {len(todo)} candidates)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="record or re-observe a workflow")
    r.add_argument("--name", required=True)
    r.add_argument("--step", action="append", default=[], required=True)
    r.add_argument("--file", action="append", default=[])
    r.add_argument("--minutes", type=int, default=0)
    r.add_argument("--failed", action="store_true")
    r.add_argument("--judgement", action="store_true",
                   help="needs interpretation — routes to a skill, not a script")
    r.add_argument("--data", action="store_true", help="data processing")
    r.add_argument("--schedule", help="cron-ish description if it should run on one")
    r.add_argument("--gate-on", choices=("commit", "push"))
    r.add_argument("--automated-by")
    r.add_argument("--note")

    o = sub.add_parser("observe", help="group piped commands by shape")
    o.add_argument("--min-count", type=int, default=2)

    sub.add_parser("list", help="everything recorded")

    s = sub.add_parser("score", help="rank candidates")
    s.add_argument("--explain", help="show the arithmetic for one workflow")

    v = sub.add_parser("resolve", help="mark a workflow as automated")
    v.add_argument("name")
    v.add_argument("--automated-by", required=True)

    p = sub.add_parser("prune", help="drop stale one-offs")
    p.add_argument("--older-than", type=int, default=180)
    p.add_argument("--dry-run", action="store_true")

    sub.add_parser("registry", help="regenerate AUTOMATION_REGISTRY.md")

    args = ap.parse_args()
    db = load()
    return {"record": cmd_record, "observe": cmd_observe, "list": cmd_list,
            "score": cmd_score, "resolve": cmd_resolve, "prune": cmd_prune,
            "registry": cmd_registry}[args.cmd](args, db)


if __name__ == "__main__":
    sys.exit(main())
