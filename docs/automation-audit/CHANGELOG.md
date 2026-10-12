# Automation audit changelog

## 2026-10-12 (first audit)
- Added `scripts/stamp_sha.py` and documented it in `improve-system/SKILL.md`. No new skill (existing `improve-system` extended, per the no-duplicate rule).
- `procmem.py resolve` + `registry` run: `.claude/process-memory.json`, `AUTOMATION_REGISTRY.md` updated.
- Created `docs/automation-audit/` (this directory).

## 2026-10-12 (revision 1, after independent review)
- `scripts/stamp_sha.py` hardened: CRLF-exact, atomic write, cell-count and code-fence guards, annotated-cell guard, SHA-abbreviation-tolerant idempotence, controlled refusals. Self-test 11 to 27 checks. Independent suite 20/30 to 30/30.
- Added `requirements-dev.txt` (jinja2, PyYAML); removed the unreachable 135-line tail of `scripts/ha_validate.sh` (output identical in four environments).
- Corrected the first report: 13 stamps is 8, 91 commits is 49, the first Routine run was creation-time not scheduled, and the missing dependency is jinja2 *and* PyYAML.
- `REPETITION_HISTORY.json` is now version 2: owner input and agent effort are separate fields, each tagged measured / self_reported / estimate.
- Recorded Routine schedule evidence (UTC cron, next fire, attached connectors, base-branch gap).
- Reconciled with the root `SKILL_REGISTRY.md` that landed on `casaray-v3-design` during this revision: this directory's registry now defers to it when present, to avoid two skill indexes disagreeing.
