# Decision log

Decisions made autonomously, with the evidence that made them safe, so a later
reader can disagree with one on its merits. Newest last. Owner decisions are
marked **OWNER**.

## D-001 — Develop on `autonomous/casaray-dev`, not `ha-deploy` (2026-10-05, OWNER)

The owner asked for `ha-deploy` to be treated as protected and for work to
happen on a dedicated branch. Branch cut from `origin/ha-deploy` `18a4e5d`.
Nothing is pushed to `ha-deploy`; its PR is a draft. *Consequence:* CLAUDE.md's
"push both `ha-deploy` and `claude/ha-dashboard-upgrades-wui7ig`" is **not**
followed for this run; that rule predates the recovery.

## D-002 — Do not redo or touch authentication (2026-10-05, OWNER)

Owner login is restored and working. No script under `scripts/recovery/` is
run, copied or modified. `recovery/phase0-diagnostics` is treated as tooling
only, not a base to develop from.

## D-003 — Audit classes describe what the repository can know (2026-10-05)

`scripts/audit_casaray.py` classes entities as confirmed_broken, likely_broken,
live_check, working, stateless, obsolete from the 05/09 export, the `STALE`
map, twin detection and `packages/`. *Why not use the live MCP:* it returns
friendly names without entity IDs and includes stale registry twins, so a
name-keyed match would mislabel entities. `working` is deliberately weak
("nothing contradicts it"). *Result:* 0 confirmed broken, 0 likely broken, 148
live_check — of which 111 are helpers and 34 more feed the Bills board.

## D-004 — `ha-deploy` is production if auto-deploy is on (2026-10-05)

`scripts/casaray_safe_deploy.sh` runs `git reset --hard origin/ha-deploy` in
`/config/deez_repo` then deploys; `automation.casaray_nightly_safe_deploy`
calls it at 03:30 when `input_boolean.casaray_auto_deploy` is on. So a merge to
`ha-deploy` can reach the wall without anyone running the sync script — the
reverse of what CLAUDE.md's *Deployment* section says for CasaRay. Not changed
(it is the owner's deploy design). Mitigations done: the package comment that
claimed the helper defaults ON is corrected (it defaults OFF without
`initial:`), and OWNER_ACTION_QUEUE A6/A7 warn.

## D-005 — Entity gate now accepts IDs defined in `packages/` (2026-10-05)

`reconcile_entities.py` rejected any ID absent from the 05/09 export, so a
card for a helper that Git itself defines (created after the export) could
never pass. `package_defined()` unions IDs from `packages/*.yaml` (helper
blocks, scripts, template sensors by `name`, automations by `alias`). *This
widens the gate, so it is flagged:* it accepts only IDs a file in the repo
defines, and a unit test pins that. The audit still marks them `live_check`
because they exist only once `packages:` is loaded.

## D-006 — Setup status card on House health (2026-10-05)

After the 25/09 loss, every card that reads a lost helper says "No data"
without a cause. House health now has a **Setup status** card: answered/total
per helper group, three outcomes (answering / partly / not), pointing to
Settings → Helpers. The denominator is the list — here every helper is
*required*, so a silent one is the finding (the opposite of the sensor-fleet
rule, which is why the card says so in a comment). People are judged on
`unavailable` only; a person with no tracker is legitimately `unknown`. It
reads state only and acts on nothing. *Not verified:* wrapping on the iPad.

## D-007 — Did not rebuild the bills helpers (2026-10-05)

~110 helpers have no definition in Git on any branch (`git log -S` and
`git grep` across all refs). Writing YAML for them would mean inventing ranges
and could collide with surviving UI helpers (duplicate IDs become `_2`). Parked
behind OWNER_ACTION_QUEUE A1/A2.

## D-008 — Stopped at the validator edit (2026-10-05)

An attempt to delete the dead block in `scripts/ha_validate.sh` was refused by
the environment as removal of a security test. It was not retried by another
route. The defect is confirmed (`bash -n` fails; lines 182–316 are unreachable)
and recorded as OWNER_ACTION_QUEUE B1 with a test that tracks it.

## D-009 — Booleans proposed, everything else parked (2026-10-05)

Of the ~110 helpers with no definition in Git, only the seven `input_boolean`s
(language toggle, six paid flags) have no settings, so only they can be
written without inventing anything. They are in `proposals/`, outside the
path `package_defined()` reads, so they neither load nor legitimise any card.
Whether they should be installed depends on whether the originals were YAML or
UI helpers, which the repository cannot tell; the file's header gives the
owner a two-minute read-only check. A test pins that every key is an
`input_boolean` in the export, none is already in `packages/`, and no setting
is added. Number/date/text/select helpers stay parked on A1/A2.

## D-010 — The live connector is evidence, not an input (2026-10-05)

`docs/live/live_observations_2026-10-05.md` records what the MCP showed (the
language toggle and all three people `unavailable`; four Tapo streams down)
with its limits: no IDs, no helpers, stale twins. The audit does not consume
it. It contradicts CLAUDE.md's 19/09 note that the C420 streams recovered, so
camera availability is treated as unknown until a photograph says otherwise.
