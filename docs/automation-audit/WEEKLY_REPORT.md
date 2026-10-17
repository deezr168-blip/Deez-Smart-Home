# Weekly Automation Audit

Newest entry first. Evidence is limited to what is accessible from this repository
(git history, files). No ChatGPT conversations, Home Assistant sessions or local
shell history are accessible, and none are assumed.

## 2026-10-17 (baseline, audit #1)

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
