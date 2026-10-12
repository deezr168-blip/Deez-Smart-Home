# Weekly automation audit — 2026-10-12

**Evidence limits.** Only git history (`ha-deploy`, 91 commits since 2026-09-12; `casaray-v3-design`; PRs #1–#4) and `.claude/process-memory.json` were available. No session transcripts, task logs or ChatGPT conversations. `ha-deploy` had **0 commits in the last 7 days**; the week's activity was V3 design/docs work on other branches, from which no repeated manual procedure could be identified. Time figures below are the repository's own `process-memory.json` estimates, not measurements.

1. **Repeated tasks.** (a) Stamping a SHA into tracking rows: 13 `stamp` commits on `ha-deploy` (verifiable in git), 5x in process-memory. (b) Validate, commit, push to both branches: 16x (self-reported, 2026-09-19). (c) Compare live render to mockup: 3x, ~40 min each (self-reported).
2. **Highest priority.** (a): `procmem.py score` = 9 HIGH, deterministic, low risk, verifiable against history. (b) is higher count but ends in a push (external action); (c) needs judgement and live access.
3. **Improved.** `improve-system` skill extended with `scripts/stamp_sha.py` (no new skill; `automate` and `improve-system` already exist).
4. **Manual inputs eliminated.** Per batch: hand-locating rows, editing the Commit cell(s), writing the stamp message (≈3 steps) → 1 command.
5. **Weekly minutes saved.** Not measurable this week (no `ha-deploy` batches). process-memory estimates 4 min per stamp; at the 13 stamps seen in the prior 30 days that is ≈52 min/month, ≈12 min/week *if* the pace repeats. Estimate only.
6. **Validation.** `stamp_sha.py --self-test`: 11/11, incl. refusals. Replayed 4 historical stamp commits against their parents: 3 byte-identical to the hand edit; the 4th (`bd49f14`, CR-318/319) was refused because those IDs sit on two rows — the real ID collision the hand edit worked around. `ha_validate.sh` fails section 2 (`jinja2` not installed in this sandbox) **identically with and without these changes**; not caused by this PR.
7. **Files.** `scripts/stamp_sha.py` (new), `.claude/skills/improve-system/SKILL.md`, `.claude/process-memory.json`, `AUTOMATION_REGISTRY.md`, `docs/automation-audit/*`. `CLAUDE.md` unchanged.
8. **PR.** See the draft PR into `ha-deploy` (never merged automatically).
9. **Needs approval.** Whether to automate the push-to-both-branches step (16x, external action; `CLAUDE.md` says push to `ha-deploy` and `claude/ha-dashboard-upgrades-wui7ig`). Whether to add `stamp_sha.py --self-test` to `verify_change.sh`. Install `jinja2` in the routine environment so `ha_validate.sh` can run.

**Routine.** This run is itself a scheduled firing, so a weekly schedule already exists; I did not create another. No Home Assistant access or deployment was used.
