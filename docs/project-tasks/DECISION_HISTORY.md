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
| DEC-027 | 2026-11-08 | TASK-017 | APPROVED | AWAITING_DECISION | APPROVED | Proceed on the default: the Energy board shows grid export and whole-house consumption as 'no source entity' until the meter fact is supplied. Nothing is built by this. | Approval is of the default only. The fact itself (Fronius Smart Meter fitted, or Powerpal net meter) was not supplied and is still needed. | selected Approve in the AskUserQuestion prompt for TASK-017, 2026-11-08 | ask-user-question | owner |
| DEC-028 | 2026-11-08 | TASK-017 | NOTE | APPROVED | APPROVED | — | Owner approved the default on 2026-11-08; the underlying fact was not supplied, so the task stays open (APPROVED, not DONE). | — | — | claude |
| DEC-029 | 2026-11-08 | TASK-009 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: exact edit, verified offline | — | — | claude |
| DEC-030 | 2026-11-08 | TASK-003 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: the audit never drafted the wording | — | — | claude |
| DEC-031 | 2026-11-08 | TASK-004 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: V3 rules bar editing PROJECT_STATE.md | — | — | claude |
| DEC-032 | 2026-11-08 | TASK-008 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: exact hook | — | — | claude |
| DEC-033 | 2026-11-08 | TASK-011 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: agent's recommended list | — | — | claude |
| DEC-034 | 2026-11-08 | TASK-012 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: exact action | — | — | claude |
| DEC-035 | 2026-11-08 | TASK-013 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Proposal made concrete before asking the owner, 2026-11-08: default named | — | — | claude |
| DEC-036 | 2026-11-08 | TASK-009 | NOTE | AWAITING_DECISION | AWAITING_DECISION | — | Correction (2026-11-08): the previous proposal text showed the regex alternation as '/' because the register turns a pipe into '/'; reworded without a pipe | — | — | claude |
| DEC-037 | 2026-11-08 | TASK-001 | APPROVED | AWAITING_DECISION | APPROVED | Policy adopted: sessions load PROJECT_STATE.md selectively by its own Context Loading Strategy. Does NOT authorise editing root CLAUDE.md step 1: that is a protected instruction file and needs its own specific approval. | Blanket 'Approve all': applied to ungated tasks only | owner replied 'Approve all' in chat on 2026-11-08, a blanket answer, after the Update me list of pending decisions | chat | owner |
| DEC-038 | 2026-11-08 | TASK-002 | APPROVED | AWAITING_DECISION | APPROVED | The integration branch may open a PR to main only when the owner asks for one. Pull requests from specialist branches need no answer. | Blanket 'Approve all': applied to ungated tasks only | owner replied 'Approve all' in chat on 2026-11-08, a blanket answer, after the Update me list of pending decisions | chat | owner |
| DEC-039 | 2026-11-08 | TASK-007 | APPROVED | AWAITING_DECISION | APPROVED | Approved in principle: add the one-line regime check to improve-system step 1. Does NOT authorise the edit itself: it is outside design/casaray-v3/ and needs its own specific go-ahead. | Blanket 'Approve all': applied to ungated tasks only | owner replied 'Approve all' in chat on 2026-11-08, a blanket answer, after the Update me list of pending decisions | chat | owner |
| DEC-040 | 2026-11-08 | TASK-015 | APPROVED | AWAITING_DECISION | APPROVED | Adopted: the register stays an index; PR 3's queue and log stay the detailed home of recovery items; PR 5's approvals are recorded here. Nothing from PR 3 or PR 5 is copied. | Blanket 'Approve all': applied to ungated tasks only | owner replied 'Approve all' in chat on 2026-11-08, a blanket answer, after the Update me list of pending decisions | chat | owner |
| DEC-041 | 2026-11-08 | TASK-019 | APPROVED | AWAITING_DECISION | APPROVED | Authorise the three prototype fixes (elapsed time, brightness, cover position), each with its own regression check, on a specialist branch for integrator review. Does not authorise merging. | Blanket 'Approve all': applied to ungated tasks only | owner replied 'Approve all' in chat on 2026-11-08, a blanket answer, after the Update me list of pending decisions | chat | owner |
| DEC-042 | 2026-11-08 | TASK-001 | NOTE | APPROVED | APPROVED | — | Next action updated after the owner's blanket approval, 2026-11-08 | — | — | claude |
| DEC-043 | 2026-11-08 | TASK-002 | NOTE | APPROVED | APPROVED | — | Next action updated after the owner's blanket approval, 2026-11-08 | — | — | claude |
| DEC-044 | 2026-11-08 | TASK-007 | NOTE | APPROVED | APPROVED | — | Next action updated after the owner's blanket approval, 2026-11-08 | — | — | claude |
| DEC-045 | 2026-11-08 | TASK-015 | NOTE | APPROVED | APPROVED | — | Next action updated after the owner's blanket approval, 2026-11-08 | — | — | claude |
| DEC-046 | 2026-11-08 | TASK-019 | NOTE | APPROVED | APPROVED | — | Next action updated after the owner's blanket approval, 2026-11-08 | — | — | claude |
| DEC-047 | 2026-11-08 | TASK-018 | RAISED | OPEN | AWAITING_DECISION | — | Run the read-only review: check the Parents' room AC card and the Climate board against Home's safeguards (V3-007, hardening 2-5, items 9-11). Report findings; change no code, no entity, no doc under design/casaray-v3/. It does not unblock any build. | — | — | claude |
| DEC-048 | 2026-11-08 | TASK-018 | APPROVED | AWAITING_DECISION | APPROVED | Run the read-only review and report the findings. Changes no code, entity or design document; unblocks no build. | Approval is for the review only | owner replied 'Approve 018' in chat, 2026-11-08 | chat | owner |
| DEC-049 | 2026-11-08 | TASK-018 | STARTED | APPROVED | IN_PROGRESS | — | — | — | — | claude |
| DEC-050 | 2026-11-08 | TASK-018 | NOTE | IN_PROGRESS | IN_PROGRESS | — | Review run after the owner approved it (DEC-048); findings recorded here, not filed in DECISIONS.md | — | — | claude |
| DEC-051 | 2026-11-08 | TASK-025 | ADDED | — | AWAITING_DECISION | gate=none; p=P1 | Home: design/casaray-v3/DECISIONS.md#*HVAC safeguards.* Home has | Read from design/casaray-v3/DECISIONS.md#*HVAC safeguards.* Home has | — | claude |
| DEC-052 | 2026-11-09 | TASK-023 | NOTE | BLOCKED | BLOCKED | — | Pointer corrected 2026-11-09: the newer recovery record is on recovery/phase0-diagnostics (PR 10), not PR 3's queue of 5 Oct | — | — | claude |
