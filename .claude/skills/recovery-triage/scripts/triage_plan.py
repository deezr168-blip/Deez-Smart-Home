#!/usr/bin/env python3
"""Turn a reported symptom into an ordered list of READ-ONLY checks, a list of
things not to do, and an incident-record skeleton.

WHY THIS EXISTS

This environment has no /config, no supervisor and no route to the Home
Assistant instance (MAINTENANCE.md). Every fact about a fault has to come from
the owner running a diagnostic on the host and pasting the output back. The
repository already has those diagnostics; what keeps being redone is working out
which one answers which question, in what order, and which tempting steps must
not be taken. The recovery work on the recovery branch also shows the same
safeguards being re-derived each time (references/recovery-safeguards.md).

THIS TOOL EXECUTES NOTHING

It prints text. It imports no process, file-writing or network module, and
`--selftest` proves that by walking its own syntax tree. HOST checks are for the
owner to run on the host. LIVE_READ checks use only the read-only Home Assistant
connector. Recovery steps are described, never run, and every one is marked as
needing the owner's approval.

USAGE

  triage_plan.py list
  triage_plan.py plan --symptom "wall iPad still shows the old dashboard"
  triage_plan.py plan --symptom "..." --sync-status out_of_sync
  triage_plan.py plan --symptom "..." --json
  triage_plan.py incident --symptom "..." [--date 2026-10-12]
  triage_plan.py --selftest

EXIT CODES  0 ok   1 self-test failed   2 usage error
"""

from __future__ import annotations

import argparse
import ast
import datetime
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO = Path(__file__).resolve().parents[4]
TEMPLATE = SKILL_DIR / "references" / "incident-template.md"

WHERE = ("REPO", "HOST", "LIVE_READ", "ASK")


@dataclass
class Check:
    where: str            # REPO | HOST | LIVE_READ | ASK
    what: str
    answers: str
    source: str           # repository file that documents it ("" for ASK)
    verify_path: str = "" # repo-relative path that must exist, or ""


@dataclass
class Symptom:
    id: str
    title: str
    keywords: list
    checks: list = field(default_factory=list)
    never: list = field(default_factory=list)
    reading: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    recovery: list = field(default_factory=list)   # described, never run; all need approval
    owner_only: bool = False
    route: str = ""       # non-empty: this is another skill's job


SYMPTOMS = [
    Symptom(
        id="stale-dashboard",
        title="The wall iPad or a browser shows an old or wrong dashboard after a change",
        keywords=["stale", "old dashboard", "not updating", "still showing", "still shows",
                  "out of sync", "out_of_sync", "not live", "after push", "after i pushed",
                  "ipad shows old", "wall ipad", "sync"],
        checks=[
            Check("LIVE_READ",
                  "Read sensor.casaray_sync_status through the read-only Home Assistant connector "
                  "(GetLiveContext). If the entity does not exist, say so and carry on.",
                  "What the host last reported. The sensor comes from packages/casaray_automation.yaml, "
                  "which is not in the 2026-09-05 export and may be deliberately inactive: a missing "
                  "sensor is NOT evidence of anything.",
                  "packages/casaray_automation.yaml", "packages/casaray_automation.yaml"),
            Check("HOST", "sh /config/casaray/casaray_sync_status.sh",
                  "One word: synced, out_of_sync, missing_repo or missing_live (byte comparison of the "
                  "repository copy and the live dashboard file).",
                  "scripts/casaray_sync_status.sh", "scripts/casaray_sync_status.sh"),
            Check("HOST", "sh /config/casaray/casaray_health_check.sh",
                  "Whether the delivery chain is sound; exits non-zero if a REQUIRED check fails.",
                  "scripts/casaray_health_check.sh", "scripts/casaray_health_check.sh"),
            Check("REPO", "git log --oneline -5",
                  "What has actually been committed. Committed is not live.",
                  "CLAUDE.md", "CLAUDE.md"),
            Check("ASK",
                  "Ask the owner: after the last push, did you run scripts/sync_casaray_to_config.sh on "
                  "the host, and did you refresh the browser?",
                  "Delivery of CasaRay is manual. A dashboard update needs a browser refresh, not a "
                  "restart.", "", ""),
        ],
        never=["Do not tell the owner a push is live. CLAUDE.md: committed in Git and live in Home "
               "Assistant are different things.",
               "Do not run or suggest running scripts/sync_casaray_to_config.sh on your own initiative. "
               "It puts a dashboard in front of people; it is the owner's step.",
               "Do not suggest restarting Home Assistant. A dashboard update does not need one."],
        reading=["CLAUDE.md, section Deployment", "docs/CASARAY_AUTOMATION.md, Out-of-sync detection"],
    ),
    Symptom(
        id="deploy-fetch-fails",
        title="The unattended deploy cannot fetch, or the apply step is not writing",
        keywords=["git fetch", "fetch fails", "could not read username", "deploy fails",
                  "deploy not applying", "apply step", "not writing", "403", "credential",
                  "unattended", "deploy log", "authentication failed"],
        checks=[
            Check("HOST",
                  "Run scripts/deploy_diagnose.sh THROUGH A HOME ASSISTANT shell_command, not from the "
                  "Studio Code Server terminal.",
                  "What differs between the failing context and the working one. The script's whole "
                  "point is where it is run. Output goes to the deploy log, with tokens in remote "
                  "URLs redacted.",
                  "scripts/deploy_diagnose.sh", "scripts/deploy_diagnose.sh"),
            Check("ASK",
                  "Ask the owner to paste the relevant part of the deploy log (it is sanitised). "
                  "Never ask for the token or the credential file.",
                  "The verdict the diagnosis reached.", "", ""),
            Check("REPO", "Read DEPLOY_AUTH.md steps 1 to 3 and match the verdict: credential, "
                          "environment, or SSH key.",
                  "Which fix applies.", "DEPLOY_AUTH.md", "DEPLOY_AUTH.md"),
        ],
        never=["Do not modify the deployment bridge (/config/deploy_deez_dashboard.sh, "
               "scripts/deploy_env.sh, scripts/deploy_askpass.sh, scripts/deploy_diagnose.sh, "
               "DEPLOY_AUTH.md). CLAUDE.md: not without an explicit instruction.",
               "Do not print, paste, store or commit a token, password or credential URL.",
               "Do not change authentication or accounts."],
        reading=["DEPLOY_AUTH.md", "DEPLOYMENT_BLOCKERS.md, the 2026-08-30 evidence that the apply "
                                   "step was not writing"],
        notes=["The fixes in DEPLOY_AUTH.md that involve a credential are the owner's to make."],
    ),
    Symptom(
        id="kiosk-header",
        title="Home Assistant's own header or sidebar still shows on the wall iPad",
        keywords=["kiosk", "header", "sidebar", "hide header", "kiosk_mode", "kiosk mode",
                  "toolbar"],
        checks=[
            Check("HOST", "sh /config/deez_repo/scripts/casaray_kiosk_diagnose.sh",
                  "Whether the kiosk-mode frontend resource is registered and present on this "
                  "instance. Read-only. This is the one question the build environment cannot answer.",
                  "scripts/casaray_kiosk_diagnose.sh", "scripts/casaray_kiosk_diagnose.sh"),
            Check("REPO", "Read DR-015 in DASHBOARD_ISSUES.md.", "The background and what was ruled out.",
                  "DASHBOARD_ISSUES.md", "DASHBOARD_ISSUES.md"),
        ],
        never=["Do not edit the dashboard YAML to work around a missing frontend resource. The question "
               "is what is installed on the instance.",
               "Read commit fc208cd (\"Remove CasaRay kiosk mode lockout configuration\") before "
               "re-adding any kiosk configuration, and do not re-add it without the owner's instruction.",
               "Do not install or remove frontend resources."],
        reading=["DASHBOARD_ISSUES.md, DR-015"],
    ),
    Symptom(
        id="disk-pressure",
        title="The disk is filling, or Home Assistant is slow because of storage",
        keywords=["disk", "storage", "full", "no space", "database size", "recorder", "out of space"],
        checks=[
            Check("HOST", "sh /config/casaray/casaray_disk_report.sh",
                  "What is consuming storage. Contains no rm, truncate, mv or VACUUM; safe to run "
                  "repeatedly and on a nearly full filesystem. Run it WITHOUT redirecting to a file "
                  "if the disk is nearly full.",
                  "scripts/casaray_disk_report.sh", "scripts/casaray_disk_report.sh"),
        ],
        never=["Do not delete, truncate, purge or VACUUM anything as part of triage. A cleanup has "
               "exactly one dangerous step (the report script's own header) and is a separate approval.",
               "Do not remove backups."],
        reading=["scripts/casaray_disk_report.sh header"],
    ),
    Symptom(
        id="bad-deploy-rollback",
        title="The dashboard is broken or blank after a deploy and the previous one is wanted",
        keywords=["roll back", "rollback", "broken after", "blank after", "previous version",
                  "restore dashboard", "undo deploy", "bad deploy", "revert"],
        checks=[
            Check("HOST", "sh /config/casaray/casaray_rollback.sh --list",
                  "Which pre-deploy backups exist, newest last. Read-only.",
                  "scripts/casaray_rollback.sh", "scripts/casaray_rollback.sh"),
            Check("HOST", "sh /config/casaray/casaray_health_check.sh",
                  "Whether the delivery chain is sound.",
                  "scripts/casaray_health_check.sh", "scripts/casaray_health_check.sh"),
            Check("REPO", "Read docs/CASARAY_AUTOMATION.md, Manual recovery, and docs/ROLLBACK_DRILL.md.",
                  "The rehearsed procedure.", "docs/ROLLBACK_DRILL.md", "docs/ROLLBACK_DRILL.md"),
        ],
        recovery=["sh /config/casaray/casaray_rollback.sh   (restores the newest backup; saves the "
                  "current file first; refuses a backup that does not parse; needs a browser refresh, "
                  "not a restart)  -- NOT RUN, NEEDS THE OWNER'S APPROVAL",
                  "script.casaray_rollback_previous   (the same action from inside Home Assistant)  "
                  "-- NOT RUN, NEEDS THE OWNER'S APPROVAL"],
        never=["Do not roll back with git reset or a force-push. In Git, rollback is git revert "
               "(MAINTENANCE.md).",
               "Do not run the rollback yourself. This environment has no /config, and the step "
               "changes what people see."],
        reading=["docs/CASARAY_AUTOMATION.md, Manual recovery", "docs/ROLLBACK_DRILL.md"],
    ),
    Symptom(
        id="lost-config-or-login",
        title="Locked out, login not working, configuration or dashboard registration lost, or "
              "helpers unavailable after a restore",
        keywords=["locked out", "lockout", "cannot log in", "can't log in", "login", "password",
                  "onboarding", "configuration.yaml", "config lost", "registration",
                  "dashboard missing", "unregistered", "restore from backup", "restored",
                  "helpers unavailable", "people unavailable"],
        owner_only=True,
        checks=[
            Check("ASK",
                  "Ask what the owner can still reach: the Home Assistant UI, the Supervisor UI, the "
                  "Terminal & SSH add-on, the Samba share.",
                  "Which paths exist at all. Do not choose a procedure before this is known.", "", ""),
            Check("REPO",
                  "Read the recovery branch (recovery/phase0-diagnostics). It is NOT in this checkout: "
                  "read it through the GitHub API or ask the owner to check it out.",
                  "The read-only Phase 0 diagnostic and the latest plan, which is marked \"planning "
                  "only, nothing run\".", "", ""),
            Check("HOST",
                  "If the owner chooses, run only the read-only Phase 0 diagnostic from that branch.",
                  "Clock, disk, listeners, file dates, onboarding steps, auth and user counts, "
                  "backup-key presence as true or false only.", "", ""),
        ],
        never=["STOP. Authentication, users, passwords, tokens, configuration.yaml, .storage/ and "
               "backup restores are on the owner-approval boundary (MAINTENANCE.md, Protected).",
               "You may PREPARE a plan, or review one against references/recovery-safeguards.md, "
               "marked NOT RUN, NEEDS APPROVAL. You may not run one, and nothing here could.",
               "Never ask for, print or store a password, hash, token or encryption key.",
               "Do not use a script the recovery branch has withdrawn (repair_login.sh now exits "
               "immediately)."],
        reading=["MAINTENANCE.md, Protected", "references/recovery-safeguards.md"],
        notes=["Backup identifiers and usernames stay out of the repository and out of incident "
               "records filed in it."],
    ),
    Symptom(
        id="ha-unreachable",
        title="Home Assistant will not start, or cannot be reached at all",
        keywords=["won't start", "wont start", "not starting", "unreachable", "cannot reach",
                  "can't reach", "502", "not responding", "no response", "blank page",
                  "won't load", "offline", "down"],
        checks=[
            Check("ASK",
                  "Ask what the browser shows (a Home Assistant page, a proxy error, a blank page, "
                  "nothing), whether other devices reach it, and what changed last (restart, update, "
                  "configuration edit, power event).",
                  "The only facts available. This environment cannot reach the instance.", "", ""),
            Check("HOST", "If any host shell is reachable: sh /config/casaray/casaray_health_check.sh",
                  "What it can report. Read-only.",
                  "scripts/casaray_health_check.sh", "scripts/casaray_health_check.sh"),
            Check("REPO", "Read MAINTENANCE.md, Blocked capabilities.",
                  "What this environment cannot see.", "MAINTENANCE.md", "MAINTENANCE.md"),
        ],
        never=["Do not invent Supervisor or operating-system commands that no repository file "
               "documents.",
               "Do not suggest a restart, reset or restore as a first step."],
        reading=["MAINTENANCE.md", "DEPLOYMENT_BLOCKERS.md"],
        notes=["Coverage is partial: no repository procedure handles an instance that is down. The "
               "closest is the Phase 0 diagnostic on the recovery branch. Say that plainly."],
    ),
    Symptom(
        id="card-renders-wrong",
        title="A card or view renders wrongly, truncates, or asserts something it cannot see",
        keywords=["card", "truncated", "wrapped", "wrong text", "tile", "chip", "renders",
                  "layout", "column", "pill", "label cut"],
        route="improve-system",
        notes=["This is a content or design fault, not an operational one."],
    ),
    Symptom(
        id="entity-unavailable",
        title="An entity is unavailable, missing, or shows no data",
        keywords=["unavailable", "entity missing", "no data", "unknown state", "dead entity",
                  "stale entity", "sensor dead"],
        route="improve-system",
        notes=["Use improve-system's references/evidence-rules.md and the read-only GetLiveContext. "
               "The export's availability column goes stale; do not conclude from it."],
    ),
    Symptom(
        id="gate-fails",
        title="A validation gate fails",
        keywords=["ha_validate", "validation failed", "gate fails", "dashboard_check",
                  "verify_change", "preserve_check", "check 15"],
        route="improve-system",
        notes=["Never weaken a gate to get past it. Note that `bash -n scripts/ha_validate.sh` reports "
               "a syntax error at line 182: a known latent defect in the gate's dead tail "
               "(WORKFLOW_AUDIT.md, D2), not the cause of a failing check."],
    ),
]

SYNC_MEANING = {
    "synced": "The repository copy and the live dashboard file are byte-identical. The fault is not "
              "delivery; look at the browser (refresh), the cache, or the card itself.",
    "out_of_sync": "The live file differs from the repository copy. After any push this is EXPECTED "
                   "until the owner runs scripts/sync_casaray_to_config.sh. It is a fault only if the "
                   "owner says that step was done.",
    "missing_repo": "The repository dashboard file is absent from the host clone. The delivery chain "
                    "is broken at the source: run the health check and read DEPLOY_AUTH.md.",
    "missing_live": "The live dashboard file /config/dashboards/casaray_v2.yaml is absent. The "
                    "dashboard is not installed there, or was lost. Treat as lost-config-or-login "
                    "until the owner says otherwise: owner-only.",
}

UNCLASSIFIED = Symptom(
    id="unclassified",
    title="No known symptom matched",
    keywords=[],
    checks=[Check("ASK",
                  "Ask the owner: what exactly is wrong, where they see it, when it started, what "
                  "changed just before, and whether the house's security (cameras, alarms) still works.",
                  "Enough to classify the fault. Do not guess a procedure.", "", "")],
    never=["Do not invent a diagnostic. If no repository file documents a step, say so."],
)

_KW_NORMALISE = str.maketrans({"’": "'", "‘": "'"})


def keyword_hits(text: str, keywords: list) -> list:
    t = " " + re.sub(r"\s+", " ", text.lower().translate(_KW_NORMALISE)) + " "
    hits = []
    for k in keywords:
        pat = r"(?<![a-z0-9_])" + re.escape(k.lower()) + r"(?![a-z0-9_])"
        if re.search(pat, t):
            hits.append(k)
    return hits


def classify(text: str) -> list:
    """Return [(score, symptom, hits)] best first; empty when nothing matched."""
    scored = []
    for s in SYMPTOMS:
        hits = keyword_hits(text, s.keywords)
        if hits:
            scored.append((sum(1 + h.count(" ") for h in hits), s, hits))
    scored.sort(key=lambda x: (-x[0], x[1].id))
    return scored


def build_plan(symptom_text: str, sync_status: str | None = None) -> dict:
    if sync_status is not None and sync_status not in SYNC_MEANING:
        raise ValueError(f"--sync-status must be one of {', '.join(SYNC_MEANING)}")
    ranked = classify(symptom_text)
    if not ranked:
        chosen, hits, alt = UNCLASSIFIED, [], []
    else:
        _, chosen, hits = ranked[0]
        alt = [s.id for sc, s, _ in ranked[1:] if sc >= ranked[0][0] - 1]
    plan = {"symptom_text": symptom_text, "matched": chosen.id, "title": chosen.title,
            "matched_keywords": hits, "also_possible": alt,
            "owner_only": chosen.owner_only, "route": chosen.route,
            "checks": [asdict(c) for c in chosen.checks], "never": chosen.never,
            "reading": chosen.reading, "notes": chosen.notes, "recovery": chosen.recovery,
            "sync_status": None}
    if sync_status:
        plan["sync_status"] = {"value": sync_status, "meaning": SYNC_MEANING[sync_status]}
        if sync_status == "missing_live" and chosen.id != "lost-config-or-login":
            plan["also_possible"] = sorted(set(plan["also_possible"]) | {"lost-config-or-login"})
    return plan


def render_plan(p: dict) -> str:
    L = ["TRIAGE  " + p["matched"] + "  -  " + p["title"], "",
         "THIS TOOL EXECUTES NOTHING. HOST checks are for the owner to run on the host and paste back;",
         "this environment has no /config. LIVE_READ uses only the read-only Home Assistant connector.", ""]
    if p["matched_keywords"]:
        L.append("MATCHED ON  " + ", ".join(p["matched_keywords"]))
    if p["also_possible"]:
        L.append("ALSO POSSIBLE  " + ", ".join(p["also_possible"]) + "  (ask a question that tells them apart)")
    if p["route"]:
        L += ["", f"ROUTE  This is not an operational fault. Use the `{p['route']}` skill instead.",
              "       Triage stops here."]
        for n in p["notes"]:
            L.append("       " + n)
        return "\n".join(L)
    if p["owner_only"]:
        L += ["", ">> OWNER-ONLY. STOP before any action. Authentication, configuration, .storage and",
              "   backup restores are on the approval boundary. Gather facts and prepare; do not act."]
    if p["sync_status"]:
        L += ["", f"SYNC STATUS  {p['sync_status']['value']}", "  " + p["sync_status"]["meaning"]]
    L += ["", "CHECKS  read-only, in order; stop when one answers the question"]
    for i, c in enumerate(p["checks"], 1):
        L.append(f"  {i}. [{c['where']}] {c['what']}")
        L.append(f"       answers: {c['answers']}")
        if c["source"]:
            L.append(f"       source:  {c['source']}")
    L += ["", "DO NOT"] + [f"  - {x}" for x in p["never"]]
    if p["reading"]:
        L += ["", "READ FIRST"] + [f"  - {x}" for x in p["reading"]]
    if p["notes"]:
        L += ["", "NOTES"] + [f"  - {x}" for x in p["notes"]]
    if p["recovery"]:
        L += ["", "IF A RECOVERY IS NEEDED  (described, never run; each needs the owner's approval)"]
        L += [f"  - {x}" for x in p["recovery"]]
    L += ["", "AFTER THE OWNER PASTES OUTPUT",
          "  Quote the line each conclusion rests on. Keep VERIFIED, REPORTED and ASSUMED apart.",
          "  Anything not established stays UNKNOWN. Then: triage_plan.py incident --symptom \"...\""]
    return "\n".join(L)


def render_incident(symptom: str, date: str) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    return text.replace("{{symptom}}", symptom).replace("{{date}}", date)


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

DANGEROUS = re.compile(
    r"\b(rm|mv|cp|chmod|chown|reset|restore|restart|delete|purge|vacuum|truncate|kill)\b"
    r"|ha core (restart|stop)|backups restore|git (push|commit|checkout|merge|rebase)"
    r"|sync_casaray_to_config|casaray_safe_deploy|casaray_onboard"
    r"|casaray_rollback\.sh(?! --list)", re.I)


def selftest() -> int:
    res: list = []

    def check(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    cases = [
        ("The wall iPad still shows the old dashboard after I pushed", "stale-dashboard"),
        ("dashboard is out of sync", "stale-dashboard"),
        ("git fetch says could not read Username when the deploy runs", "deploy-fetch-fails"),
        ("the kiosk header is still showing on the iPad", "kiosk-header"),
        ("the disk is almost full", "disk-pressure"),
        ("I want to roll back the last deploy", "bad-deploy-rollback"),
        ("the dashboard is broken after deploy, I need a rollback", "bad-deploy-rollback"),
        ("I’m locked out and can’t log in after the restore", "lost-config-or-login"),
        ("configuration.yaml was lost and the dashboard is unregistered", "lost-config-or-login"),
        ("Home Assistant won't start", "ha-unreachable"),
        ("the Energy card text is truncated", "card-renders-wrong"),
        ("the sensor is unavailable and shows no data", "entity-unavailable"),
        ("ha_validate failed on check 15e", "gate-fails"),
        ("completely unrelated words here", "unclassified"),
    ]
    for text, want in cases:
        got = build_plan(text)["matched"]
        check(f"classify {text!r} -> {want}", got == want, f"got {got}")

    # structure
    ids = [s.id for s in SYMPTOMS]
    check("symptom ids are unique", len(ids) == len(set(ids)))
    check("every check has a valid location",
          all(c.where in WHERE for s in SYMPTOMS + [UNCLASSIFIED] for c in s.checks))
    actionable = [c for s in SYMPTOMS + [UNCLASSIFIED] for c in s.checks if c.where != "ASK"]
    check("no check anyone would run contains a mutating verb or a deploy/restore script",
          not [c.what for c in actionable if DANGEROUS.search(c.what)],
          str([c.what for c in actionable if DANGEROUS.search(c.what)]))
    check("ASK checks are phrased as questions for the owner",
          all(c.what.startswith("Ask") for s in SYMPTOMS + [UNCLASSIFIED] for c in s.checks if c.where == "ASK"))
    check("recovery steps are all marked as needing approval",
          all("NEEDS THE OWNER'S APPROVAL" in r for s in SYMPTOMS for r in s.recovery))
    check("routed symptoms carry no checks of their own",
          all(not s.checks for s in SYMPTOMS if s.route))
    check("owner-only symptoms open with STOP",
          all(s.never and s.never[0].startswith("STOP") for s in SYMPTOMS if s.owner_only))
    check("every operational symptom says what not to do", all(s.never for s in SYMPTOMS if not s.route))
    check("every host check names a source file", all(c.source for s in SYMPTOMS for c in s.checks
                                                       if c.where == "HOST" and "recovery branch" not in c.what
                                                       and "Phase 0" not in c.what))

    # the repository files the data cites still exist
    if (REPO / "CLAUDE.md").is_file():
        missing = sorted({c.verify_path for s in SYMPTOMS for c in s.checks
                          if c.verify_path and not (REPO / c.verify_path).is_file()})
        check("every cited repository file exists", not missing, str(missing))
        for ref in ("incident-template.md", "recovery-safeguards.md", "symptoms.md"):
            check(f"references/{ref} exists", (SKILL_DIR / "references" / ref).is_file())
    else:
        print("  skip  repository path checks (not running inside the repository)")

    # sync status
    check("all four sync words are explained", set(SYNC_MEANING) == {"synced", "out_of_sync",
                                                                      "missing_repo", "missing_live"})
    try:
        build_plan("x", "bogus")
        check("bad --sync-status is refused", False)
    except ValueError:
        check("bad --sync-status is refused", True)
    p = build_plan("dashboard out of sync", "out_of_sync")
    check("out_of_sync is described as expected after a push", "EXPECTED" in p["sync_status"]["meaning"])
    p = build_plan("dashboard out of sync", "missing_live")
    check("missing_live points at the owner-only symptom", "lost-config-or-login" in p["also_possible"])

    # rendering
    text = render_plan(build_plan("locked out and cannot log in"))
    check("owner-only plan says STOP", "OWNER-ONLY. STOP" in text)
    text = render_plan(build_plan("the Energy card text is truncated"))
    check("routed plan names the other skill and stops", "improve-system" in text and "Triage stops here" in text)
    text = render_plan(build_plan("rollback please"))
    check("rollback plan lists the restore as not run", "NOT RUN, NEEDS THE OWNER'S APPROVAL" in text)
    check("plan states it executes nothing", "EXECUTES NOTHING" in render_plan(build_plan("disk full")))

    # incident template
    if TEMPLATE.is_file():
        inc = render_incident("wall iPad shows old dashboard", "2026-10-12")
        for h in ("Symptom", "Last known good", "Evidence", "Hypotheses", "Checks run",
                  "Decision needed", "Proposed recovery", "Rollback", "Verification", "Unknowns"):
            check(f"incident template has a '{h}' section", re.search(rf"^## \d+\. {h}", inc, re.M) is not None)
        check("incident template substitutes symptom and date",
              "wall iPad shows old dashboard" in inc and "2026-10-12" in inc and "{{" not in inc)
        check("incident template defaults to UNKNOWN", inc.count("UNKNOWN") >= 10)
        check("incident template marks the recovery as not run", "NOT RUN, NEEDS APPROVAL" in inc)

    # this tool cannot act: no process, file-writing or network capability anywhere outside the test
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    banned_imports = {"subprocess", "shutil", "socket", "urllib", "http", "requests", "ftplib", "smtplib"}
    # `replace` is deliberately absent: str.replace is used to fill the template.
    banned_calls = {"system", "popen", "Popen", "run", "write_text", "write_bytes", "unlink", "rmdir",
                    "mkdir", "rename", "remove", "touch"}
    problems = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "selftest":
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Import):
                problems += [a.name for a in sub.names if a.name.split(".")[0] in banned_imports]
            elif isinstance(sub, ast.ImportFrom) and (sub.module or "").split(".")[0] in banned_imports:
                problems.append(sub.module)
            elif isinstance(sub, ast.Attribute) and sub.attr in banned_calls:
                problems.append("." + sub.attr)
            elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "open":
                mode = sub.args[1].value if len(sub.args) > 1 and isinstance(sub.args[1], ast.Constant) else "r"
                if any(ch in str(mode) for ch in "wax+"):
                    problems.append("open(..., write)")
    check("syntax-tree scan: no process, network or file-writing capability", not problems, str(problems))

    # and it leaves no trace when used
    with tempfile.TemporaryDirectory() as tmp:
        import os
        before = sorted(os.listdir(tmp))
        render_plan(build_plan("disk full"))
        check("running a plan creates no files", sorted(os.listdir(tmp)) == before)

    for name, cond, detail in res:
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if not cond and detail else ""))
    print(f"\n{sum(1 for _, c, _ in res if c)}/{len(res)} checks passed")
    return 0 if all(c for _, c, _ in res) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="prove the tool")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list", help="list known symptoms")
    p = sub.add_parser("plan", help="checks and cautions for a symptom")
    p.add_argument("--symptom", required=True, help="the owner's words")
    p.add_argument("--sync-status", choices=list(SYNC_MEANING), help="result of casaray_sync_status.sh")
    p.add_argument("--json", action="store_true")
    i = sub.add_parser("incident", help="print a blank incident record")
    i.add_argument("--symptom", required=True)
    i.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.cmd == "list":
        for s in SYMPTOMS:
            kind = f"-> {s.route}" if s.route else ("owner-only" if s.owner_only else "triage")
            print(f"  {s.id:<22} {kind:<16} {s.title}")
        return 0
    if args.cmd == "plan":
        plan = build_plan(args.symptom, args.sync_status)
        print(json.dumps(plan, indent=2) if args.json else render_plan(plan))
        return 0
    if args.cmd == "incident":
        date = args.date or datetime.date.today().isoformat()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            print("error: --date must be YYYY-MM-DD", file=sys.stderr)
            return 2
        print(render_incident(args.symptom, date))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
