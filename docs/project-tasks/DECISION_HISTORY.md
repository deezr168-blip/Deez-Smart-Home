# Decision history

Append-only. One row for every change to a task's status: who did it, when, on
what basis, and for approvals, exactly what was authorised. A row is never edited
or removed; a mistake is corrected with a later `NOTE` row. Denied and paused
tasks stay here with their reasons and saved context.

`tasks.py check --append-only-vs <ref>` fails if an earlier row has changed.
Owner rows (`APPROVED`, `DENIED`, `PAUSED`, `RESUMED`, `REOPENED`) are written
only from what the owner actually answered; no answer means no decision.

| ID | Date | Task | Event | From | To | Scope | Context | Basis | Via | By |
|---|---|---|---|---|---|---|---|---|---|---|
| DEC-001 | 2026-10-12 | TASK-001 | ADDED | — | AWAITING_DECISION | gate=none; p=P2 | Home: WORKFLOW_AUDIT.md#**C5:** read | Read from WORKFLOW_AUDIT.md#**C5:** read | — | claude |
| DEC-002 | 2026-10-12 | TASK-002 | ADDED | — | AWAITING_DECISION | gate=none; p=P3 | Home: WORKFLOW_AUDIT.md#**C2:** should | Read from WORKFLOW_AUDIT.md#**C2:** should | — | claude |
| DEC-003 | 2026-10-12 | TASK-003 | ADDED | — | AWAITING_DECISION | gate=protected; p=P3 | Home: WORKFLOW_AUDIT.md#five-line precedence note | Read from WORKFLOW_AUDIT.md#five-line precedence note | — | claude |
| DEC-004 | 2026-10-12 | TASK-004 | ADDED | — | AWAITING_DECISION | gate=protected; p=P3 | Home: WORKFLOW_AUDIT.md#move the superseded blocks to `archive/` | Read from WORKFLOW_AUDIT.md#move the superseded blocks to `archive/` | — | claude |
| DEC-005 | 2026-10-12 | TASK-005 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: WORKFLOW_AUDIT.md#The pilot skills exist on | Read from WORKFLOW_AUDIT.md#The pilot skills exist on | — | claude |
| DEC-006 | 2026-10-12 | TASK-006 | ADDED | — | AWAITING_DECISION | gate=protected; p=P3 | Home: WORKFLOW_AUDIT.md#small, in existing files | Read from WORKFLOW_AUDIT.md#small, in existing files | — | claude |
| DEC-007 | 2026-10-12 | TASK-007 | ADDED | — | AWAITING_DECISION | gate=none; p=P2 | Home: WORKFLOW_AUDIT.md#add a regime check to `improve-system` step 1 | Read from WORKFLOW_AUDIT.md#add a regime check to `improve-system` step 1 | — | claude |
| DEC-008 | 2026-10-12 | TASK-008 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: SKILL_REGISTRY.md#automatically at session start | Read from SKILL_REGISTRY.md#automatically at session start | — | claude |
| DEC-009 | 2026-10-12 | TASK-009 | ADDED | — | AWAITING_DECISION | gate=safety; p=P1 | Home: pr:5#approval-4 | Read from pr:5#approval-4 | — | claude |
| DEC-010 | 2026-10-12 | TASK-010 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: pr:5#approval-1 | Read from pr:5#approval-1 | — | claude |
| DEC-011 | 2026-10-12 | TASK-011 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: pr:5#approval-2 | Read from pr:5#approval-2 | — | claude |
| DEC-012 | 2026-10-12 | TASK-012 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: .claude/skills/owner-decisions/references/weekly-routine.md#Proposed addendum to the Routine prompt | Read from .claude/skills/owner-decisions/references/weekly-routine.md#Proposed addendum to the Routine prompt | — | claude |
| DEC-013 | 2026-10-12 | TASK-013 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: pr:5#approval-3 | Read from pr:5#approval-3 | — | claude |
| DEC-014 | 2026-10-12 | TASK-014 | ADDED | — | AWAITING_DECISION | gate=none; p=P3 | Home: pr:5#approval-5 | Read from pr:5#approval-5 | — | claude |
| DEC-015 | 2026-10-12 | TASK-015 | ADDED | — | AWAITING_DECISION | gate=none; p=P2 | Home: register | Created here | — | claude |
| DEC-016 | 2026-10-12 | TASK-016 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: register | Created here | — | claude |
| DEC-017 | 2026-10-12 | TASK-017 | ADDED | — | AWAITING_DECISION | gate=none; p=P1 | Home: design/casaray-v3/DECISIONS.md#V3-003 | Read from design/casaray-v3/DECISIONS.md#V3-003 | — | claude |
| DEC-018 | 2026-10-12 | TASK-018 | ADDED | — | OPEN | gate=none; p=P1 | Home: design/casaray-v3/DECISIONS.md#review whether the Parents' room and Climate HVAC mode | Read from design/casaray-v3/DECISIONS.md#review whether the Parents' room and Climate HVAC mode | — | claude |
| DEC-019 | 2026-10-12 | TASK-019 | ADDED | — | AWAITING_DECISION | gate=none; p=P2 | Home: design/casaray-v3/DECISIONS.md#latent truthfulness fallbacks | Read from design/casaray-v3/DECISIONS.md#latent truthfulness fallbacks | — | claude |
| DEC-020 | 2026-10-12 | TASK-020 | ADDED | — | OPEN | gate=none; p=P3 | Home: design/casaray-v3/DECISIONS.md#the slight layout inconsistency of Lighting's | Read from design/casaray-v3/DECISIONS.md#the slight layout inconsistency of Lighting's | — | claude |
| DEC-021 | 2026-10-12 | TASK-021 | ADDED | — | AWAITING_DECISION | gate=protected; p=P1 | Home: DASHBOARD_BACKLOG.md#BILL-001 | Read from DASHBOARD_BACKLOG.md#BILL-001 | — | claude |
| DEC-022 | 2026-10-12 | TASK-022 | ADDED | — | AWAITING_DECISION | gate=protected; p=P2 | Home: DASHBOARD_BACKLOG.md#BILL-002 | Read from DASHBOARD_BACKLOG.md#BILL-002 | — | claude |
| DEC-023 | 2026-10-12 | TASK-023 | ADDED | — | BLOCKED | gate=protected; p=P1 | PR 3 is an unmerged draft against ha-deploy, so its OWNER_ACTION_QUEUE.md and DECISION_LOG.md are not on this branch to point at | Read from branch:autonomous/casaray-dev:docs/OWNER_ACTION_QUEUE.md | — | claude |
| DEC-024 | 2026-10-12 | TASK-024 | ADDED | — | AWAITING_DECISION | gate=protected; p=P1 | Home: register | Created here | — | claude |
| DEC-025 | 2026-10-12 | TASK-024 | APPROVED | AWAITING_DECISION | APPROVED | Write only: root CLAUDE.md, docs/project-tasks/TASK_REGISTER.md, docs/project-tasks/DECISION_HISTORY.md and the existing skills (named in the brief); plus the new .claude/skills/owner-decisions/ directory and SKILL_REGISTRY.md, which the agent infers from 'extend existing skills, no duplicate skills' and which the owner is asked to confirm in review. Open a draft PR into casaray-v3-design. Never merge, deploy or control a device. | Approval limited to the paths and actions in Scope | owner task brief in this session, 2026-10-12, target files listed | chat | owner |
| DEC-026 | 2026-10-12 | TASK-024 | STARTED | APPROVED | IN_PROGRESS | — | — | — | — | claude |
