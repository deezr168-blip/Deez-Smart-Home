# CasaRay backlog revalidation — 2026-11-16

**Review proposal only.** Owner requested stale-task cleanup. This document changes no canonical status, decision history, device control, live Home Assistant, merge or deployment permission.

## Confirmed change
- PR #9 was closed without merging. Its successor PR #11 explicitly says it supersedes #9. This does not certify that the audit content was incorporated.

## Disposition matrix
| Record | Proposal | Required verification |
|---|---|---|
| TASK-002 | Complete decision-only | Approved decision recorded; no execution needed |
| TASK-015 | Complete decision-only | Register adoption and linked records confirmed |
| TASK-018 | Close review | Delivered HVAC review and Lovelace safeguards checked |
| TASK-025 | Supersede candidate | Hardening-1 fixes actually present/covered by tests; prototype relevance |
| TASK-020 | Retire candidate | Old prototype lighting card unused in active build |
| TASK-019 | Re-scope or retire | Confirm truthfulness fallbacks in current Lovelace build |
| PR #11 and PR #14 | Archive candidates | Preserve useful audit history; do not merge just to clear queue |
| PR #12 | Historical reference | Keep recovery report accessible, not active recovery |
| PR #13 / TASK-032 | Revalidate; no merge | Current host, auto-deploy and overlap with PR #10 independently checked |
| PR #10 / TASK-023 | Split/revalidate | V3 access restored as reported; HACS/custom components/streams require live verification |
| TASK-027 | Keep blocked | Compare live V3 revision read-only |
| TASK-030 | Keep diagnostics | Recheck Tapo streams on live HA |
| PR #16 / TASK-028-029 | Keep with separate gates | Review and merge distinct from deployment and live verification |
| PR #8 / #17 / TASK-024 | Keep | Central register and pause-protected control center needed |
| TASK-021 | Inspect and keep until checked | Determine whether V2 meter IDs still hardcoded |

## Explicit paused aliases
Issue #7 pauses CR-T01–CR-T05. V5 links them to TASK-011, TASK-009, TASK-010, TASK-013, TASK-014 and TASK-031. Keep all pauses, even if prior approvals exist. PR #5 remains draft and unmerged. This audit is NOT a resume instruction.

## Proposed operating policy (requires separate implementation and tests)
1. OPEN or APPROVED is not READY_TO_EXECUTE. A task needs current evidence, prerequisites, explicit scope and clearance of every safety/owner gate.
2. Add REVALIDATION_REQUIRED as a derived UI flag initially; do not add an unrecognised persistent status to the register.
3. Flag evidence older than 14 days or predating material recovery/merge/deployment. Never automatically close or resume anything.
4. Deduplicate by canonical task links, preserving original task history and distinct work scopes.
5. Before Approve, verify code/branch, live-system relevance if applicable, dependencies, duplicate/superseding work, and necessary authority.
6. Require exact files, rollback method and validation for write-capable tasks. Missing live evidence blocks execution.
7. Distinguish review complete, merge approved, merged, deploy approved, deployed and live verified.
8. Never let bulk actions approve a paused alias or accidentally lift a previous pause.
9. Actual status changes must be written through tasks.py and append-only DECISION_HISTORY.md, with selftests and register checks.
10. Show Backlog Cleanup as an owner-review queue of five at a time with keep, retire, complete and revalidate decisions. Do not make those controls direct production actions.

## Safe rollout
A. Review and integrate PR #17 into PR #8, preserving tested pause guards.
B. Implement UI cleanup tab and revalidation flags in a separate review PR, with tests.
C. Ask owner to select individual dispositions; retain uncertainty instead of guessing.
D. Update canonical records via tasks.py only, test, then close superseded PRs with clear reasons.
E. Expose only eligible work to Claude; no automatic merges or HA changes.

Sources: GitHub Issue #7, PRs #8–17, canonical TASK_REGISTER.md on casaray-v3/agent-task-conflicts, read 2026-11-16. Live HA claims are not independently confirmed in this audit.
