# Weekly Automation Audit

Newest entry first. Evidence is limited to what is accessible from this repository
(git history, files). No ChatGPT conversations, Home Assistant sessions or local
shell history are accessible, and none are assumed.

## 2026-10-24 (audit #2)

**Correction to audit #1.** It inspected the checked-out branch (`main`) only and concluded "0 commits". `git log --all` shows 54 non-merge commits (all authored `Claude`) in the 30 days from 2026-09-24, mostly on other branches. The 10-12 audit in PR #5 already used that wider scope. Audit #1's "evidence insufficient" was a scope error, not a finding.

**Evidence window:** 7 days = 2026-10-17..10-24; 30 days = 2026-09-24..10-24. Sources: git history on all remote branches, PR list. No task logs, session transcripts, shell history or ChatGPT conversations are accessible.

1. **Repeated tasks identified.** Last 7 days: 3 commits, one being audit #1 and two being `recovery:` commits (live recovery family, out of scope). Nothing repeats 3+ times. 30-day: SHA stamping x8 (2026-09-18..09-25, none since; already covered by `scripts/stamp_sha.py` in PR #5); `recovery:` x11 (excluded); weekly-audit PR base branch retargeted/mis-targeted x2 (below threshold).
2. **Highest-priority improvement.** None to build. The one recurring owner input is the PR base branch for these weekly PRs; the fix is a one-line Routine prompt change that needs the owner (not edited here: it changes a live schedule).
3. **Skill created or improved.** None. Five skills plus `owner-decisions` (PR #8) already exist on other branches; see `SKILL_REGISTRY.md`. A new one would be speculative.
4. **Manual inputs eliminated.** 0 (nothing implemented).
5. **Weekly minutes saved.** 0 (no measurement basis).
6. **Validation.** `REPETITION_HISTORY.json` parses; commit counts re-derivable with `git log --all --since=<date> --no-merges`. No skill to dry-run.
7. **Files modified.** `docs/automation-audit/{WEEKLY_REPORT.md,SKILL_REGISTRY.md,REPETITION_HISTORY.json,CHANGELOG.md}`. `CLAUDE.md` unchanged. Home Assistant, deploys and recovery branches untouched.
8. **PR.** Draft, not merged. It contains PR #9's baseline commit plus this audit, so it supersedes #9.
9. **Needs the owner.** (a) Which branch should audit PRs target (`main` vs `casaray-v3-design`)? Then add a base-branch line to the Routine prompt. (b) Merge or close #9 and #5 so audit trails live in one place. (c) PR #5's open approvals (setup-script `pip install`, connector detach, device-control guard gap for `media_player__play_media`) remain unresolved. (d) Which off-git repeated work (HA UI edits, ChatGPT, terminal) should be ranked? Without it this routine cannot see it.

**Scheduling.** This run is a scheduled cloud routine, so weekly scheduling exists. GitHub Actions fallback only if the owner approves: `on: schedule` weekly cron plus `workflow_dispatch`, running Claude Code on a non-main branch and opening a draft PR.

---

## 2026-10-17 (baseline, audit #1) — superseded: scope error, see correction above

**Evidence window:** 7 days = 2026-10-10..2026-10-17; 30 days = 2026-09-17..2026-10-17.

| Window | Commits found |
|---|---|
| Last 7 days | 0 |
| Last 30 days | 0 |
| All history | 5 (2026-08-21 .. 2026-08-23) |

All five commits are repository scaffolding (initial commit, CLAUDE.md, folder
scaffold, .gitignore + entity inventory template, one merged PR).

1. **Repeated tasks identified:** none. No task occurs 3+ times in the evidence.
2. **Highest-priority improvement:** none justified. Evidence insufficient.
3. **Skill created or improved:** none (registry is empty; creating one now would be speculative).
4. **Manual inputs eliminated:** 0 (not measured; nothing implemented).
5. **Weekly minutes saved:** 0 (no measurement basis; none invented).
6. **Validation:** audit files parse (`REPETITION_HISTORY.json` checked with a JSON parser). No skill to dry-run.
7. **Files modified:** all four files under `docs/automation-audit/` (new).
8. **PR:** draft PR on branch `claude/inspiring-lamport-0g1pf6` for review; not merged.
9. **Items requiring approval:** merging this PR; see "Open questions" below.

### Observations (not yet repetition evidence)
- `docs/entity_inventory.md` is an unpopulated template waiting on verified Home
  Assistant read access. Once populated, "validate an entity ID before using it"
  is a likely candidate for a read-only skill, but only if it recurs 3+ times.
- `CLAUDE.md` holds no verified project context yet, so there is nothing to reuse.
  Once facts are verified (HA URL, access method, conventions), add them there.

### Open questions for the owner
- Which work happens outside git (HA UI edits, ChatGPT, terminal) that you repeat weekly?
  Telling me those task names would give real evidence to rank.
- Should this routine be pointed at other repos where activity actually occurs?

### Scheduling
This run was itself fired by a scheduled cloud routine, so weekly scheduling already
exists. Fallback if it is ever unavailable: a GitHub Actions workflow with
`on: schedule` (weekly cron) plus `workflow_dispatch` that runs Claude Code on a
non-main branch and opens a draft PR. It should be added only with your approval.
