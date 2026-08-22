# Deployment & Change Workflow

This document defines the required workflow for making any change to
production Home Assistant configuration through this repository —
dashboards, automations, scripts, or themes — once real config exists
here to change. It exists so that "clean up the dashboard" never turns
into "the family's dashboard is broken until someone fixes it."

## The current production dashboard is production-stable

The live dashboard works today. It is not a draft. Nothing in this repo
should treat it as something to be freely rewritten for the sake of a
cleaner architecture. See `CLAUDE.md` rule 7.

## Required workflow for any production dashboard/automation/script change

```
Current production
      |
      v
Backup / rollback checkpoint
      |
      v
Small, targeted edit
      |
      v
Syntax / config validation
      |
      v
Entity validation
      |
      v
Review diff
      |
      v
Deploy
      |
      v
Verify live behaviour
      |
      v
Commit + changelog
```

### Step by step

1. **Current production.** Confirm what's actually running before
   touching anything — read the current file(s) in this repo (or, if not
   yet imported, the live system) rather than assuming.

2. **Backup / rollback checkpoint.** Before any edit that could break
   something working, create a clearly identified checkpoint: a copy of
   the file (e.g. `home.yaml` → `home.yaml.bak-2026-08-22`), a backup
   branch/tag, or — at minimum — note the exact prior content in the
   commit that makes the change, so it can be reverted without guessing.
   This is non-negotiable for anything beyond a trivial addition.

3. **Small, targeted edit.** Change only what was actually asked for.
   Don't reformat, reorder, rename, or "improve" surrounding config as a
   side effect (`CLAUDE.md` rule 8). If a larger redesign is genuinely
   worthwhile, build it as a separate candidate file/branch instead of
   editing the working one in place (`CLAUDE.md` rule 7).

4. **Syntax / config validation.** Any YAML touched must be checked for
   valid syntax before it's committed (`CLAUDE.md` rule 9) — e.g. a YAML
   linter or parser, not just "it looks right."

5. **Entity validation.** Every entity referenced in the change must be
   confirmed against the live connector or `docs/entity_inventory.md`
   (`CLAUDE.md` rules 3–4). Remember this connector doesn't expose real
   `entity_id` values — a friendly name match is not sufficient
   confirmation that the exact `entity_id` used in YAML is correct.

6. **Review diff.** Look at the actual diff before committing, not just
   the intended change — confirm the blast radius matches what was
   planned and nothing unrelated crept in.

7. **Deploy.** Apply the change to the live instance through whatever
   mechanism is in use (this depends on how HA is set up to consume this
   repo's config — not yet established; see `docs/live_ha_blockers.md`).
   Never treat "committed to git" as equivalent to "deployed" unless
   there's an actual sync/deploy mechanism connecting the two — call out
   explicitly which one just happened.

8. **Verify live behaviour.** After deploying, check that the change
   actually works as intended on the live system — and that nothing else
   broke. For anything involving alarms, locks, security, heating/
   cooling, appliances, or high-power loads, this verification step gets
   extra scrutiny (`CLAUDE.md` rule 19).

9. **Commit + changelog.** Commit with a clear, scoped message (see Git
   discipline below) and add an entry to `CHANGELOG.md` describing what
   changed and — per `CLAUDE.md` rule 14 — whether it's been verified live
   or only exists in the repo so far.

## Git discipline

For each meaningful stage of work:

- Inspect current repository state before starting (`git status`,
  `git diff`).
- Make only the relevant changes for that stage — don't bundle unrelated
  work into one commit.
- Review the diff before committing.
- Check for accidentally-included credentials/secrets before staging,
  especially in any file that might reference `secrets.yaml`, tokens, or
  webhook URLs — even in a filename that looks innocuous.
- Commit with a descriptive, conventional message, e.g.:

  ```
  docs: populate verified HA entity inventory
  docs: document live connector capabilities
  chore: strengthen CLAUDE.md production safeguards
  dashboards: add backed-up Home dashboard baseline
  automations: add parents room lighting automation
  ```

## Rollback

If a deployed change causes a problem: restore from the checkpoint created
in step 2, redeploy, verify, and record what happened in `CHANGELOG.md`
(and, if it reveals a gap in this workflow, update this document too).
Never leave production in a broken state while investigating — restore
first, diagnose after.
