wrote AUTOMATION_REGISTRY.md  (6 in place, 1 candidates)
ate/scripts/procmem.py registry`.
Do not hand-edit — record the workflow and re-run instead, or the next
regeneration silently discards whatever was written here.

Last generated 2026-09-19 from `.claude/process-memory.json`.

## In place

| Automation | Type | Replaces | Trigger | Recorded from |
|---|---|---|---|---|
| `.claude/skills/improve-system/SKILL.md` | claude skill | add a gate to dashboard_check and negative-test it (6 steps) | manual | seen 4x, 2026-09-19–2026-09-19 |
| `scripts/casaray_capture.sh` | shell script | obtain a screenshot of a live CasaRay view (5 steps) | manual | seen 2x, 2026-09-19–2026-09-19 |
| `scripts/dashboard_edit.py` | python utility | parse views, locate a section, splice YAML (6 steps) | manual | seen 8x, 2026-09-19–2026-09-19 |
| `.claude/skills/improve-system/scripts/render_cards.py` | skill tooling | render a card across live and dark states (5 steps) | manual | seen 6x, 2026-09-19–2026-09-19 |
| `.claude/skills/improve-system/scripts/preserve_check.py` | skill tooling | structural diff of the dashboard against a git ref (4 steps) | manual | seen 2x, 2026-09-19–2026-09-19 |
| `scripts/audit_duplicate_entities.py + scripts/reconcile_entities.py` | python utility | verify an entity against live before using it (4 steps) | manual | seen 5x, 2026-09-19–2026-09-19 |

## Candidates

| Workflow | Score | Seen | Suggested form |
|---|---|---|---|
| validate, commit, push both branches | HIGH (11) | 16x | shell script |
