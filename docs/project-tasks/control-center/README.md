# CasaRay Task Control Center — V5

One HTML file the owner opens in a browser to see the task register and select
Approve / Deny / Pause. **It decides nothing and writes nothing.** It prepares a
handoff that Claude Code records with the owner-decisions tool, and it calls a
decision recorded only when GitHub shows the owner's row in the history.

| File | What it is |
|---|---|
| `index.html` | the page; no build step, no dependencies, no server |
| `build.py` | embeds the register and history in the page as the offline snapshot |
| `test_control_center.cjs` | browser tests (Playwright, headless Chromium); GitHub mocked |

## Where its data comes from

The only task list is the canonical one:
`docs/project-tasks/TASK_REGISTER.md` and `DECISION_HISTORY.md`, read from the
branch named under **Source** (default `casaray-v3/agent-task-conflicts`, PR 17's
pause-safe review branch). On open, and every 15 minutes while visible, it reads that branch's
commit and then both files **at that commit**, plus Issue #7 and the PR list.
If GitHub cannot be reached it keeps the last GitHub read, or falls back to the
snapshot `build.py` embedded, and says which in the header. V4's hand-written
`initial` array is gone: a task that is not in the register is not on the page.

## Rules it enforces (the same ones `tasks.py` enforces)

- **A pause outranks everything.** Approve is disabled on a `PAUSED` task and on
  a task whose alias another record has paused (Issue #7's CR-T01 to CR-T05, via
  the register's Links table). The page has no Resume button: the owner resumes
  one task, by name, in Claude Code.
- **Approve only what awaits a decision.** `OPEN`, `BLOCKED`, `IN_PROGRESS`,
  `APPROVED`, `DONE` and `DENIED` tasks cannot be approved. Deny and Pause follow
  the tool's own transition table.
- **A gated task needs its own exact scope** (12+ characters, single use), and
  every approval says whether it covers *read-only review / preparation* or
  *implementation on a branch*. There is no deployment option.
- **Bulk approval** covers only ungated tasks awaiting a decision, with evidence
  at most 14 days old, no unfinished dependency and no conflict, and only for
  review / preparation. Every skipped task is listed with its reason in the
  confirmation.
- **A reused task ID** disables every decision on that ID until one record
  remains.
- **Selections are remembered, and re-checked.** Each one stores the task's
  status, updated date, decision, gate, priority and last history row. If any
  of them changes on refresh, the selection is held back until the owner
  confirms it again. V4 selections are mapped through the Links table and must be
  confirmed again; a V4 ID with no canonical task is reported and dropped.
- **Submit records nothing.** It needs the confirmation box and a second
  confirmation, then prints the handoff: each decision with its scope, what it
  does not authorise, its blockers, the commit it was prepared against, the
  exact `tasks.py decide --batch` command, and the batch JSON. Items that are
  not valid are listed under *Not in this handoff*.

## Tabs

- **Queue**: open tasks, five a page, highest priority first (then awaiting a
  decision, in progress, approved, open, blocked, paused). Filters: all,
  needs a decision, no decision needed, paused, blocked; and by priority.
- **Conflicts**: duplicate IDs, unreadable rows, duplicate or dangling links,
  a pause another record holds that the register has not recorded, Issue #7
  changing since it was checked, Issue #7 IDs with no task, open PRs no task
  covers, tasks with the same title, overlaps and bundles, stale evidence, V4
  selections, and any selection that needs revalidating.
- **Completed**: `DONE` and `DENIED` tasks, kept on record.
- **Backlog Cleanup**: five flagged records per page, priority-ordered. Uses age of the recorded evidence (14-day warning), blocked/paused state, and explicit review recommendations to propose Keep, Complete, Retire, or Revalidate. This is a **non-mutating triage surface**: it does not change Approve/Deny/Pause selections, mutate GitHub, or authorise execution. Paused tasks can only be marked Keep or Revalidate; never Complete or Retire through this tab. A confirmation prepares a separate plain-English owner-review handoff that still requires validation via tasks.py before any status change. The recommendations are dated hypotheses, not proof of completion.

## Maintaining it

After changing the register or history, run
`python3 docs/project-tasks/control-center/build.py` so the offline snapshot
matches, and `--check` to confirm. Then
`node docs/project-tasks/control-center/test_control_center.cjs` (existing 83 checks plus cleanup regression cases;
the last group runs the page's handoff through the real `tasks.py` on a
throwaway copy of the tree).

It is a local file. Opening it does not publish it, and nothing in it is a
credential: GitHub is read anonymously. A refresh makes three GitHub API
requests (the branch's commit, Issue #7, the PR list; the two files come from
raw.githubusercontent.com), and the anonymous API limit is 60 an hour, so about
twenty refreshes an hour. Past that, or if the repository is ever made private,
the page says GitHub is unreachable and shows the last read or the snapshot.

Until the Links table reaches PR 8's branch, the page applies the links in its
snapshot (and says so under Conflicts), so Issue #7's pauses are enforced either
way. To read PR 8's original register instead, set **Source** to
`casaray-v3/agent-task-tracking`. The cleanup recommendations are a review layer; the register and append-only history remain authoritative. As of 16 November 2026, the browser suite is **not executed** in this GitHub-only editing session (JavaScript syntax validated), so review and the full test run are required before merging.
