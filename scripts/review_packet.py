#!/usr/bin/env python3
"""Build an independent-review packet for a branch. READ-ONLY.

Prints one markdown document a second reviewer (Codex, or a person) can read
without access to the author's session: what changed, what the gates said,
what the structural diff lost, which protected paths were touched, and what
the author claims was and was not verified live.

It never writes to the repository, never contacts Home Assistant and never
pushes. The author's *claims* come from the PR body; this packet supplies the
*evidence*, so the reviewer can tell them apart.

    python3 scripts/review_packet.py [--base origin/ha-deploy] [--no-gates]
"""

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTECTED = re.compile(
    r"^(dashboards/deez_smart_home\.yaml|scripts/deploy_(env|askpass|diagnose)\.sh|"
    r"DEPLOY_AUTH\.md|MAINTENANCE\.md|configuration\.yaml|secrets\.ya?ml|"
    r"\.storage/.*|\.env.*|scripts/ha_validate\.sh|scripts/dashboard_check\.py|"
    r"scripts/reconcile_entities\.py)$")
# Not protected from edits, but a reviewer should look hardest at them: they are
# the gates, and weakening one makes every later change easier to ship.
GATES = {"scripts/ha_validate.sh", "scripts/dashboard_check.py",
         "scripts/reconcile_entities.py", ".github/workflows/ci.yml",
         "tests/test_casaray.py"}


def sh(*cmd, timeout=300):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).rstrip()


def block(title, body, lang=""):
    return f"### {title}\n\n```{lang}\n{body}\n```\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/ha-deploy")
    ap.add_argument("--no-gates", action="store_true",
                    help="skip running the gates (faster; packet says so)")
    args = ap.parse_args()

    rc, _ = sh("git", "rev-parse", "--verify", args.base)
    if rc:
        print(f"unknown base {args.base}", file=sys.stderr)
        return 2
    _, head = sh("git", "rev-parse", "--short", "HEAD")
    _, base = sh("git", "rev-parse", "--short", args.base)
    _, branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD")
    _, names = sh("git", "diff", "--name-only", f"{args.base}...HEAD")
    files = [f for f in names.split("\n") if f]

    out = [f"# Review packet: `{branch}` ({head}) against `{args.base}` ({base})\n"]
    out.append("**Reviewer, read this first.** This packet is evidence, not "
               "argument. `Committed` is not `deployed`: nothing here has been "
               "seen on the running Home Assistant. Reject any claim of live "
               "verification that is not backed by a screenshot or states read "
               "from the API.\n")

    _, log = sh("git", "log", "--format=%h %an: %s", f"{args.base}..HEAD")
    out.append(block("Commits", log or "(none)"))
    _, stat = sh("git", "diff", "--stat", f"{args.base}...HEAD")
    out.append(block("Files changed", stat or "(none)"))

    prot = [f for f in files if PROTECTED.match(f)]
    gate = [f for f in files if f in GATES]
    flags = []
    if prot:
        flags.append("PROTECTED paths touched (needs owner approval):\n  "
                     + "\n  ".join(prot))
    if gate:
        flags.append("GATE files touched -- check none was weakened:\n  "
                     + "\n  ".join(gate))
    out.append(block("Flags", "\n\n".join(flags) or "none"))

    rc, text = sh(sys.executable,
                  ".claude/skills/improve-system/scripts/preserve_check.py",
                  "--ref", args.base) if os.path.exists(os.path.join(
                      ROOT, ".claude/skills/improve-system/scripts/preserve_check.py")) \
        else (0, "preserve_check.py not present")
    out.append(block(f"Nothing lost? (preserve_check, exit {rc})",
                     text[-3000:]))

    if args.no_gates:
        out.append("### Gates\n\nNOT RUN (--no-gates). The reviewer must run "
                   "`bash scripts/ha_validate.sh` and "
                   "`python3 -m unittest discover -s tests`.\n")
    else:
        rc, text = sh("bash", "scripts/ha_validate.sh")
        text = re.sub(r"\x1b\[[0-9;]*m", "", text)
        out.append(block(f"ha_validate.sh (exit {rc})", text[-2500:]))
        rc, text = sh(sys.executable, "-m", "unittest", "discover", "-s",
                      "tests")
        out.append(block(f"tests (exit {rc})", text[-1500:]))
        rc, text = sh(sys.executable, "scripts/audit_casaray.py", "--check",
                      "--strict")
        out.append(block(f"audit report (exit {rc})", text))

    out.append("## What the reviewer should answer\n\n"
               "1. Does any change reference an entity the export or "
               "`packages/` does not define?\n"
               "2. Does any card now assert a state it cannot see "
               "(Closed / Clear / Normal / 0) without a third branch?\n"
               "3. Was any gate, test or check weakened, skipped or removed?\n"
               "4. Does anything act on the physical house, reduce a security "
               "protection, or touch authentication or secrets?\n"
               "5. Are the author's *verified live* claims backed by evidence?\n"
               "6. Is every change small enough to revert alone?\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
