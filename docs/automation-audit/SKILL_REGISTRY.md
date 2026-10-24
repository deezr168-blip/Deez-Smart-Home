# Skill Registry

Check this file before creating any skill (no duplicates; max one new skill per week).

Location of skills: `.claude/skills/<name>/SKILL.md` (frontmatter `name`, `description`).

| Skill | Purpose | Created | Evidence of need | Status |
|---|---|---|---|---|
| _(none)_ | | | | |

## Candidates (not approved, below the 3+ repetition threshold)
- `ha-entity-validate` (read-only): check entity IDs against `docs/entity_inventory.md`
  before use. Blocked until the inventory is populated and the need recurs.

## Skills that exist on other branches (read from git on 2026-10-24; not present on this branch)
Do not recreate these. Source: `SKILL_REGISTRY.md` on `origin/casaray-v3-design`; `owner-decisions` from PR #8 (unmerged).

| Skill | Branch / PR | Job |
|---|---|---|
| `automate` | `casaray-v3-design` | find and score repeated work |
| `improve-system` | `casaray-v3-design` | one dashboard improvement cycle |
| `session-orient` | `casaray-v3-design` | read-only start-of-session orientation |
| `recovery-triage` | `casaray-v3-design` | read-only recovery triage; executes nothing |
| `provenance-register` | `casaray-v3-design` | evidence-status registers and linter |
| `owner-decisions` | PR #8 | owner decision/task tracking |

Tooling (not a skill): `scripts/stamp_sha.py` (PR #5, unmerged).
