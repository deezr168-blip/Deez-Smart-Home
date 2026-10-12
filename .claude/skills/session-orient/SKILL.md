---
name: session-orient
description: Orient at the start of any session in the Deez Smart Home repository, and check scope before committing. Resolves which rule set governs the current branch (CasaRay V2 on ha-deploy, CasaRay V3 design on casaray-v3-design or casaray-v3/agent branches, a recovery branch, or unrecognised), then states where a push may and may not go, which gate to run, which paths are protected, and where the instruction files contradict each other, from one read-only command. Use at the start of every session, when the user says orient, where are we, resume a session, which rules apply, or where do I push, before the first write on a branch not yet checked, and before a commit to confirm nothing changed outside the permitted paths. Not for improving dashboards (improve-system), for faults (recovery-triage) or for finding repeated work (automate). Read-only, never fetches, commits, pushes or edits.
metadata:
  version: "0.1.0"
  status: pilot
  origin: WORKFLOW_AUDIT.md W03 and W06
---

# Session orient

One read-only command that answers *which rules am I under?*, so the answer is
read rather than recalled.

## Why this exists

Two instruction sets govern this repository and they disagree about where a
push may go. Root `CLAUDE.md` says push to `ha-deploy` and
`claude/ha-dashboard-upgrades-wui7ig`. `design/casaray-v3/CLAUDE.md` says V3
work pushes only to `casaray-v3-design` and never touches `ha-deploy`. Which
applies depends on the branch, and the second file exists largely to settle that.
Working it out from memory each session is how a commit ends up in the wrong place.

## Procedure

1. Run `python3 .claude/skills/session-orient/scripts/orient.py`
2. Read it top to bottom and act on what it says:
   - **`NOT SETTLED` or exit 3**: stop and ask the owner which rules apply. Do
     not default to V2 or to V3.
   - **`RULE TABLE MAY BE STALE`**: an instruction file this tool was written
     from has changed. Read `CLAUDE.md` and `design/casaray-v3/CLAUDE.md`
     directly instead of trusting the summary, and tell the owner so the rule
     table can be updated.
   - **`SHALLOW CLONE`**: say so before quoting any number taken from history.
   - **Contradictions**: C1 (push target) is settled for V3 branches; follow the
     V3 file. C5 (read `PROJECT_STATE.md` in full, or selectively?) is the
     owner's call. Follow the repository's rule literally, flag C5 once, and do
     not resolve it yourself.
3. Read the files marked *must read*. This skill tells you which files matter;
   it does not replace reading them.
4. Tell the user in at most six lines: branch, rules, where you may push, which
   gates apply, and anything unsettled or stale. Then get on with the task.
5. **Before every commit** run `orient.py --scope`. Exit 1 means do not commit:
   put the OUTSIDE, BLOCKED and credential-shaped lines in front of the owner.
6. Run the gates it lists. `--scope` checks paths and credentials only; it does
   not run them.

## Running before other skills

The `improve-system` skill is written for the V2 line only. It never mentions V3,
and its first and last steps fetch `ha-deploy` and push to `ha-deploy` and
`claude/ha-dashboard-upgrades-wui7ig`, which the V3 rules forbid. So when the user
says "carry on", "next" or "keep going" (triggers `improve-system` owns), **run this
first.** If the rules turn out to be V2, continue with `improve-system`. If they are
V3 or unsettled, do not follow its push steps; say why and ask.

## Rules for using the output

- **It is not an approval.** `--approved PATH` records that the owner approved a
  path; use it only for a path the owner approved in so many words, and say who
  and when. It never overrides `BLOCKED`, and it cannot make a credential-shaped
  line acceptable.
- **It cannot see the remote.** Freshness is not checked (offline by design). Run
  `git fetch origin <branch>` yourself when it matters; the repository's rules
  allow that.
- **It does not settle the pull-request rule.** The repository files do not say
  whether the integration branch may open a PR. V3 PRs run specialist branch to
  `casaray-v3-design`, and no V3 branch may target `ha-deploy`. If the session
  harness tells you to open one, ask the owner first.
- **Nothing it prints is a fact about the live house.** It reads git and the
  instruction files only.

## What it prints

```
BRANCH     casaray-v3-design  [origin/casaray-v3-design: 0 ahead, 0 behind, as of the last fetch]
RULES      CasaRay V3 design: integration branch  (v3-integrator)
TREE       clean
HISTORY    362 commits visible (full history)

MAY WRITE  design/casaray-v3/**
MAY PUSH   origin casaray-v3-design
MUST NOT   any commit, merge, rebase, push or pull request against ha-deploy
GATES      python3 design/casaray-v3/tools/verify_entities.py ...
CONTRADICTIONS BETWEEN INSTRUCTION FILES
  C1  push target: ...   Settled for this branch: follow the V3 file.
  C5  reading PROJECT_STATE.md: ...   Unsettled: the owner's call.
NOT CHECKED  remote freshness (offline by design); live Home Assistant state ...
```

`--json` gives the same facts for a script. `--branch NAME` simulates a branch,
which is how the self-test and any "what would apply on X" question are answered.

## Safeguards

- **No write of any kind, no network.** Every git call passes an allowlist
  (`rev-parse`, `status`, `log`, `rev-list`, `diff`, `ls-files`,
  `branch --show-current`). `fetch`, `commit`, `push`, `checkout`, `reset`,
  `config`, `remote`, `tag`, `stash`, `add`, `branch <name>` and `--output` are
  refused, and `--selftest` proves each refusal.
- **Idempotent.** Run it as often as you like; the worktree and the git index are
  byte-identical afterwards (also tested).
- **The credential scan is minimal and looks only at lines you are about to add.**
  It never prints the matched text. It is not a substitute for section 5 of
  `scripts/ha_validate.sh`, which scans the tracked tree.

## Validation

`python3 .claude/skills/session-orient/scripts/orient.py --selftest` builds a
throwaway repository and checks 74 behaviours, including the refusals above. It
needs only Python 3 and git. Last result is in `SKILL_VALIDATION_REPORT.md`.

## Maintenance

The rule table is the `REGIMES` list in `scripts/orient.py` together with
`references/regimes.md`; change them in the same commit. Each rule set records
the text it was written from, and the tool warns when that text changes. When you
add a rule set, add a branch case and a classification case to `--selftest`.
Never add a network call or a write.
