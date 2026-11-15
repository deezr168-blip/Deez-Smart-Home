# Task Control Center V4 — conflict audit, 15/11/2026

**Status: PROPOSAL on `casaray-v3/agent-task-conflicts`, stacked on PR 8.** Not
merged, not deployed. Nothing here changes Home Assistant, a device, a Routine,
a schedule, a guard or any pull request. No earlier owner decision was edited or
removed: every change to the history is an appended row.

Sources read on 15/11/2026: the uploaded `casaray-task-control-v4.zip`
(`index.html`, `README.md`); `docs/project-tasks/TASK_REGISTER.md` and
`DECISION_HISTORY.md` at PR 8's head `0a653a9`; Issue #7 (owner-authored,
updated 12/10/2026 03:44 UTC); the repository's pull-request list (PRs 1 to 16,
heads as listed by GitHub on 15/11); the changed-file lists of PRs 10 and 13.

## 1. Conflict report

Severity: **High** — a paused or protected action could be approved, or a
decision lost. **Medium** — a wrong or stale record a person would act on.
**Low** — cosmetic or informational.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| C1 | High | **The canonical register never recorded Issue #7's pauses.** TASK-009, 010, 011, 013 and 014 (the work behind CR-T02, CR-T03, CR-T01 and CR-T04) were `AWAITING_DECISION` for 34 days after the owner paused them, so "Update me" and `ask` would have put paused work back to the owner as an open decision. | Issue #7 table and "All five tasks are PAUSED"; register at `0a653a9`, the five rows; history has no `PAUSED` row for them before DEC-075. |
| C2 | High | **V4 made paused work "free".** `TASK-009` (gate `free`, "Read-only audit": review the device-control guard gap) is CR-T02's own resume step ("inspect `scripts/deny_device_control.py`, `.claude/settings.json`…"). V4's *Approve all free* would have started paused work. | V4 `initial` row 6; Issue #7 CR-T02 resume text. |
| C3 | High | **V4 bulk-approved owner-gated tasks.** *Approve owner-input* ticks `V3-DEPLOY`, `TASK-009-APPROVE` and `CFG-005-LIVE` (and `TASK-026`) in one action. The handoff gives each the same generic sentence ("planning and review only"), not the exact single-use scope `tasks.py` requires for a gated task, and it approves `V3-DEPLOY` although that work is blocked on two unresolved tasks (C5). | V4 `bulkApprove('owner')` and `makeHandoff()`; V4 README "Changes" item 3. |
| C3a | High | **V4 turned an Approve on a paused task into a resume request.** Bulk skipped paused tasks, but a single Approve on CR-T01…05 was still selectable, and the handoff rendered it as "Request a fresh scoped resume review". Issue #7: "Do not perform any task until the owner explicitly resumes the relevant ID." | V4 `makeHandoff()`, the `gate==='paused'` branch. |
| C4 | High | **Duplicate `TASK-016`.** V4 rows 0 and 2 are identical; `new Map(...)` keeps the last silently. Worse, the ID collides with the canonical TASK-016 (*Allow docs/project-tasks/ as a permitted path on V3 branches*, protected), which TASK-026 depends on: a V4 decision handed over as "TASK-016" could have been recorded against the wrong task. V4's TASK-016 is the PR 16 review: canonical **TASK-028**. | V4 rows 0, 2; register TASK-016 and TASK-028 rows. |
| C5 | High | **Duplicate `V3-DEPLOY`, with two different states.** Row 1 "Awaiting decision", "Approve V3 camera/layout deployment"; row 3 "Awaiting scoped approval", "Approve camera/layout deployment". Which one survives depends on array order. Canonical: **TASK-029** (BLOCKED, protected), which depends on TASK-028 (merge review) and TASK-027 (which V3 version is live). V4 showed it as P0 awaiting a decision; it cannot be decided until both are resolved. | V4 rows 1, 3; register TASK-029, TASK-027, TASK-028. |
| C6 | High | **`TASK-009` and `TASK-009-APPROVE` split one task in two.** The approval half was `owner`-gated, the review half `free`; both are canonical TASK-009 (safety, now PAUSED by DEC-076). | V4 rows 6, 7; register TASK-009. |
| C7 | Medium | **V4 never read the register.** Its refresh fetched open PRs and issues only, so its own status words ("Review ready", "Read-only audit", "Paused by owner") never updated from `TASK_REGISTER.md` and could not show a decision Claude had recorded. | V4 `refresh()`; V4 README "Limitations" item 2. |
| C8 | Medium | **Selections never went stale.** V4 stored `{id: verdict}` in `casaray-decisions-v2` with nothing about the task's state, so a tick made before a pause was submitted after it. | V4 `localStorage` use. |
| C9 | Medium | **CR-T05's V4 title says "Review and merge weekly audit PR #5".** Issue #7 says "Review PR #5 for merging" and "no merge is authorised". CR-T05 had no canonical task at all: now **TASK-031** (protected, PAUSED). | V4 row 14; Issue #7 CR-T05 and "Evidence/constraints". |
| C10 | Medium | **PR 13 had no canonical task** (V4 `PR-13`, "free" read-only review). PR 13 is a V2 recovery continuation into `ha-deploy`: now **TASK-032** (protected). | V4 row 15; PR 13 base `ha-deploy`, draft. |
| C11 | Medium | **PR 10 and PR 13 overlap.** Both are CasaRay recovery work into `ha-deploy`; the only file both change is `PROJECT_STATE.md`, the V2 coordination record, so whichever merges second conflicts with the first. PR 10 is tracked by TASK-023 (BLOCKED, protected; V4's `CFG-005` and `CFG-005-LIVE`), PR 13 now by TASK-032. Recorded as `TASK-023 overlaps TASK-032`. PR 10 stays unmerged. | PR 10 (28 files) and PR 13 (22 files) file lists: one shared path. |
| C12 | Medium | **CR-T04 is two canonical tasks.** "Timezone and target branch" is TASK-013 (base branch) plus TASK-014 (timezone); TASK-012 is bundled with TASK-013. TASK-012's proposal was edited so it no longer carries TASK-013's line while that is paused. | Issue #7 CR-T04; register TASK-012, 013, 014. |
| C13 | Low | **V4 invented priorities** for CR-T01 to CR-T05 (P0 for CR-T02, P2 for the rest). Issue #7 sets none; the canonical priorities (TASK-009 P1, others P2/P3) stand. | V4 rows 10–14. |
| C14 | Low | **Open PRs with no task: 9, 11, 12, 14.** Three weekly-audit PRs into `main` and the Phase 0 recovery report into `ha-deploy`. Not added: what each should propose is the owner's call (see section 4). The V5 page lists them under Conflicts. | GitHub PR list, 15/11. |

## 2. Corrections made (proposal branch)

**Register and history**, through `tasks.py` only, append-only (`check
--append-only-vs origin/casaray-v3/agent-task-tracking`: 0 errors):

- TASK-031 (CR-T05) and TASK-032 (PR 13) added (DEC-067, DEC-068).
- The six pauses recorded as the owner's, `via github-issue`, each basis quoting
  Issue #7 (DEC-075 to DEC-080), each context keeping the issue's resume
  requirements. CR-T01 and CR-T02's earlier approvals were never in this register
  and were **not** back-filled as rows; the context says they were approved and
  then paused, "history, not authority".
- A **Links** table: Issue #7's five IDs as `alias-of`; V4's eight local IDs as
  `duplicate-of` their canonical task (V4:TASK-016 → TASK-028, both V3-DEPLOY rows
  → TASK-029, TASK-009 and TASK-009-APPROVE → TASK-009, CFG-005-LIVE → TASK-023,
  TASK-REGISTER → TASK-024, PR-13 → TASK-032, TASK-026 → TASK-026); `depends-on`,
  `bundled-with` and `overlaps` rows for C5, C11 and C12. Each link has a NOTE row
  on the task it touches (DEC-069 to DEC-074, DEC-081 to DEC-102).

**`tasks.py`** (owner-decisions skill):

- An approval is refused for a task paused in the register **or** in a linked
  record; a blanket batch skips it with the reason.
- A blanket approval needs `--live-checked` (what was re-read, when) and skips
  evidence older than 14 days, as well as every gated task.
- A resume names exactly one task, and its basis must name it or its alias.
- `--via github-issue` needs the issue number in the basis.
- `link` command; Links lint (duplicate link, unknown task, stale link, a
  pause another record holds that the register does not, near-duplicate titles).
- `update` pages five tasks at a time; `handover` lists pauses held elsewhere.

**Task Control Center V5** (`docs/project-tasks/control-center/`): replaces V4's
hand-written list with the register itself and enforces the same rules in the
browser. See its README.

## 3. Test results

| Suite | Result |
|---|---|
| `tasks.py --selftest` | 197 checks passed, 0 failed (section W: links, external pauses, bulk, pagination, stale evidence) |
| `tasks.py check` on the branch | 0 errors |
| `tasks.py check --append-only-vs origin/casaray-v3/agent-task-tracking` | 0 errors: no earlier row changed, no task removed |
| `test_control_center.cjs` | 83 checks passed, 0 failed: duplicate IDs, conflicts, paused-task protection, bulk safeguards, five-per-page pagination, priority sorting, Completed tab, GitHub refresh and fallback, stale-selection rejection, V4 migration, handoff accuracy, the handoff batch accepted by the real `tasks.py`, and no script error on any page |
| Mutation check | 8 safeguards broken one at a time in a copy of the page; each was caught by at least one test |
| Live replay | PR 8's branch, Issue #7 and the PR list as fetched on 15/11, served to the page: approval disabled on all five Issue #7 tasks; 9 errors and 5 warnings listed; no page error |

## 4. Outstanding owner decisions

1. **Confirm the six pause rows.** DEC-075 to DEC-080 are recorded as yours,
   from Issue #7, which you wrote. If any should not stand, say which; the
   correction is an appended row, never an edit.
2. **Confirm the V4 mappings**, above all V4 `TASK-016` → TASK-028 (the PR 16
   review) and both `V3-DEPLOY` rows → TASK-029.
3. **Land this proposal**: review it as a PR into PR 8's branch. Merging is yours.
4. **PRs 9, 11, 12 and 14** have no task. Add a task for each, or say they are
   superseded.
5. **TASK-032 (PR 13)**: keep or close the V2 recovery continuation. It overlaps
   PR 10 on `PROJECT_STATE.md`; PR 10 stays unmerged either way.
6. **Root `CLAUDE.md`** is protected, so it was not edited. Proposed addition
   to the bullets under *Standing Rule — Context First, Questions Last*: "**A
   pause outranks any approval**, including a general one given in the same
   message. A paused task is resumed only by the owner naming it." Apply only on
   your say-so.
