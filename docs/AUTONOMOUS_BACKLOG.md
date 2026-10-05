# Autonomous backlog

Work the agent can do without asking. Owner-required items are **not** here —
they are in `docs/OWNER_ACTION_QUEUE.md`. Decisions are in
`docs/DECISION_LOG.md`. Every item says what finishing it looks like, so it can
be checked rather than argued.

*As of 2026-10-05, branch `autonomous/casaray-dev`, draft PR into `ha-deploy`.*

## Done this run

| Batch | Commit | What |
|---|---|---|
| 1 | `eb630df` | `scripts/audit_casaray.py` + generated `docs/CASARAY_AUDIT.md`; entity gate accepts IDs `packages/` defines |
| 2 | `3e46561` | House health **Setup status** card: answered/total per helper group |
| 3 | `ef9c7e2` | Regression suite and `.github/workflows/ci.yml` |
| 4 | `3edf53e` | Review packet, Codex protocol, PR template, decision log |
| 5 | `693e743` | **Bills fix**: no longer claims "Nothing is waiting to be paid" / "Not set up" when helpers are silent |
| 6 | `4c83642` | Helper-boolean proposal (inert), live observations, bills tests |
| 7 | `8d16497` | Security-control test: sirens, locks, camera privacy never actuate on a bare tap |
| 8 | `a9456a3` | House health **Dashboard delivery** status from the maintenance package |
| 9 | this batch | Package-template parse test, PROJECT_STATE pointer, backlog |

## Findings from the audit (all classes)

| Class | Count | Meaning |
|---|---|---|
| confirmed broken | 0 | no card references an entity that cannot exist |
| likely broken | 0 | no card uses the dead half of a stale twin pair |
| live check | see `CASARAY_AUDIT.md` | needs the running instance: ~110 helpers lost with `configuration.yaml`, ~30 offline devices |
| obsolete | 15 | dead twins and `STALE` IDs, listed so nobody adopts one by name |
| unknown | 0 | every reference has a class |

**Working vs working-on-the-iPad are different claims.** Nothing here has seen the wall.

## Backlog, in priority order

### P1 — reliability

- **AB-01 Mixed-state render tests.** The dark pass tests "nothing answers"; the
  real instance is *partly* answering. Add fixtures with the helpers dark and
  everything else live (the actual state today), and with one sensor of each
  fleet dark, and assert the chip strips never print a zero they did not
  measure. *Done when:* `DarkInstance` has a `Partial` sibling that fails against
  a deliberately broken strip.
- **AB-02 Promote the reassurance phrases into `dashboard_check.py` (check 17).**
  Today they live only in `tests/test_casaray.py`, so `ha_validate.sh` cannot
  see them. Editing the gate is permitted but is the sort of change the
  environment's guard has blocked once (D-008) — do it as an *addition* in its
  own commit and expect to ask. *Done when:* a negative test makes the gate
  name the card.
- **AB-03 Render the package's own templates.** `test_every_package_template_parses`
  checks syntax only. The battery roll-up and stale-data sensors branch on
  `unavailable`; a mock `states` object would prove the three branches.
  *Done when:* a test runs the low-battery template against fake states.
- **AB-04 Audit the 12 package automations for unavailable triggers.** Reviewed
  by reading only. Check each trigger's `to:` vs `unavailable`, each
  `for:`, and that every one is `mode:`-set (the test pins mode; not the
  triggers). Reload-safety on restart: `casaray_startup_health_check` runs a
  shell command two minutes after every start.

### P2 — usability and consistency

- **AB-05 Pet feeder tiles.** `switch.smart_pet_feeder_privacy_mode` and
  `_motion_alarm` toggle on a bare tap (Dining, Camera Pet Feeder, 3 places).
  Every other privacy/siren tile is more-info only. Low risk (indoor camera);
  *decision, not a fix:* make them match, or confirm the tap is intended.
- **AB-06 Give the two allow-lists their reasons in one place.**
  `ALLOWED_HALF_ROWS` (1 entry) and `ALLOWED_SENSES` (4 entries) in
  `dashboard_check.py` carry their reasons in comments far from the sets.
  Cosmetic; do it only when the file is already being edited.
- **AB-07 View-by-view mockup comparison** for Energy, Security, Cameras,
  Climate, Network. Needs photographs of the live iPad (OWNER_ACTION_QUEUE C).
  Offline, only entity and truthfulness checks are possible and those are done.
- **AB-08 `docs/CASARAY_V2_ENTITY_MAP.md` and `NETWORK_BOARD_DESIGN.md`**
  predate the recovery; regenerate the entity map from the audit.

### P3 — tooling

- **AB-09 `audit_casaray.py --live FILE`**: accept a Developer Tools template
  dump (ID|state), so one owner paste upgrades `live_check` to a real answer
  for every entity, including helpers the MCP cannot see. *Blocked on* the
  owner running the template once (draft in `docs/B1_STATES_EXPORT.md`).
- **AB-10 Fold `review_packet.py` into a PR comment workflow** once branch
  protection exists (OWNER_ACTION_QUEUE B2).

## Not here, and why

- Rebuilding the ~110 lost helpers — settings are not in Git (A1/A2).
- Any change to authentication, secrets, `.storage`, `configuration.yaml`,
  `scripts/recovery/*`, the deploy bridge, or router/network gear.
- Deleting the dead block in `ha_validate.sh` — owner approval (B1).
- Deploying anything, restarting or reloading Home Assistant.
