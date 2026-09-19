---
name: improve-system
description: Run one autonomous improvement cycle on the Deez Smart Home Home Assistant dashboards — pick the highest-value safe change, verify every entity against the live instance, implement it, render the templates, run the validation gates, prove nothing was lost, record it, commit and push both branches. Use this whenever the user asks to improve, fix, polish, converge, audit, review or continue work on CasaRay, the dashboard, a view or board (Home, Rooms, Energy, Bills, Security, Cameras, Network, Lighting, Climate, People, Alerts, House health), the theme, the chip strips, an automation or a validation gate — and also when they paste live-render photographs, report a broken card, say "carry on", "next", "keep going", or hand over an open-ended improvement brief with no specific target. Prefer this skill over ad-hoc editing for ANY change to dashboards/casaray_v2.yaml, themes/, scripts/ or packages/, because the failure modes here are invisible to a passing validation run and this cycle is what catches them.
---

# Improve the system — one cycle

This repository deploys two Home Assistant dashboards to a wall iPad. The work
is a loop: find the highest-value safe improvement, make it, prove it, record
it, push it, go again. This skill is that loop.

Read `CLAUDE.md` and `PROJECT_STATE.md` first — they are the architecture and
the recorded state, and this skill does not repeat them. What follows is the
*method*: how to be sure a change is right before it reaches a wall-mounted
screen that someone's parents use to check whether the front door is shut.

## The one idea behind all of it

**A passing validation run never means a card renders, and never means a card
tells the truth.** The gates here check that YAML parses, templates compile,
entities appear in an export and geometry is declared. They cannot see a pill
that wraps, a header that was never hidden, or a card confidently reporting
"All clear" about three sensors that are not answering. Every rule below
exists because one of those shipped.

So the cycle is built around *evidence*: prefer live data to exported data,
rendered output to inspected source, a structural diff to a careful read.

## The cycle

1. **Orient.** `git fetch origin ha-deploy`, confirm the tree is clean and the
   branch current. Read `PROJECT_STATE.md`. Check `LIVE_VERIFICATION_QUEUE.md`
   and `DASHBOARD_ISSUES.md` for open regressions — those come before anything
   cosmetic.

2. **Choose one improvement.** Priority order: broken configuration → broken
   cards or dead entity references → safety and reliability → automation
   reliability → iPad usability → performance → energy accuracy → security and
   cameras → lighting and climate → duplicate or obsolete configuration → UI
   consistency → new automations → documentation. One meaningful change per
   batch; a batch that does three things cannot be reverted cleanly.

3. **Verify every entity before you use it.** See
   `references/evidence-rules.md`. This is the step most likely to be skipped
   and most likely to be the reason something breaks.

4. **Inspect the current YAML, then edit.** Never edit blind. For structural
   work, parse and splice with a script rather than hand-editing — the file is
   ~12k lines and carries comments that must survive.

5. **Render what you changed.** If the change touches a template, run
   `scripts/render_cards.py` across a populated state and a fully dark one,
   in both languages, and *read the output*. This catches the one class of bug
   nothing else here can: a card asserting something it did not measure.
   The populated pass comes from `docs/live/fixture_states.json` by default
   and is labelled `fixture`, not `live` — real availability, invented
   values. If a pass is labelled `empty`, the fixture was missing or
   `--no-fixture` was passed, and that run measured a dark instance twice.

6. **Run the gates.** `bash scripts/ha_validate.sh`. Exit 0 or do not push. If
   it fails, fix or revert — never weaken a gate to get past it.

7. **Prove nothing was lost.** `scripts/preserve_check.py` against the commit
   you started from. Entity, navigation, service and view counts should be
   unchanged unless you are deliberately fixing a broken reference, and it
   will tell you exactly which ones moved.

8. **Review your own diff adversarially.** Ask what a reviewer would catch.
   This session's own worst two defects were self-inflicted and found here: a
   rebuild that silently flattened every button from `rows: 2` to `rows: 1`,
   and one that rewrote the language toggle into a different service call.

9. **Gate the class, not the instance.** If you found a defect that could
   recur, add a check to `scripts/dashboard_check.py` — then *negative-test
   it* by reintroducing the defect and confirming the build fails, naming the
   view. A gate nobody proved can fail is decoration. See
   `references/gates.md`.

10. **Record it.** A row in `LIVE_VERIFICATION_QUEUE.md` for anything only a
    human at the iPad can confirm; a `DR-` entry in `DASHBOARD_ISSUES.md` for
    a design finding; a rule in `CLAUDE.md` if it changes how future work is
    done. Tracking updates go in the *same commit* as the change they describe.

11. **Commit and push both branches.** See *Commit protocol* below.

12. **Go again**, unless a stop condition below is met.

## Where truth lives

| Question | Authority |
|---|---|
| Does this entity exist right now? | The live Home Assistant MCP (`GetLiveContext`) |
| What is its exact entity_id? | `docs/live/states_export_2026-09-05.txt`, **cross-checked live** |
| Is this ID known dead? | The `STALE` map in `scripts/reconcile_entities.py` |
| What should this look like? | `docs/mockups/` — the renders win over any prose |
| How wide does this actually render? | Only a photograph. Nothing here can measure it. |
| Is it live? | Only after `scripts/sync_casaray_to_config.sh` runs on the host |

**"Committed in Git" and "live in Home Assistant" are different things.**
CasaRay reaches `/config/dashboards/` only when the owner runs the sync
script. Never report a push as a deployment.

## Hard rules, and why

These are not style preferences. Each one is a defect that reached the wall.

- **Never invent an entity ID.** Name similarity is not proof — this instance
  carries stale registry rows that look right and are dead.
- **Never let a card assert a state it cannot see.** "Closed", "Clear",
  "Normal", "All off", "0 overdue" each need a third branch for the case where
  the inputs are silent. Two outcomes for three states is the bug.
- **A denominator is what answered**, not the length of the list. `9/14` when
  five sensors are unavailable reads as five dead devices.
- **Never `| float(0)`** as a fallback for a missing reading — a sentinel
  renders as a real measurement. Guard explicitly, or test `is number`.
- **A markdown card must not emit four leading spaces** — CommonMark turns the
  whole card into a grey code block. End preamble tags with `-%}`.
- **Do not raise `max_columns` above 2** without a photograph proving the
  extra column resolves. The arithmetic here has been wrong twice and the
  failure is silent.
- **Never force-push, never rewrite published history**, never modify
  `dashboards/deez_smart_home.yaml` or anything in `MAINTENANCE.md`'s
  protected list without an explicit instruction.

## Bilingual work

Every user-facing string is a pair. Headings and button labels use two cards
with opposite `visibility`, because neither can be templated. Chinese is
Simplified; grep the legacy dashboard for an existing term before inventing
one; enumerations take `、`.

One English term gets one Chinese word — `check 15e` enforces this. When you
shorten an English label, check you have not collapsed it onto a word that
already means something else; that check caught six such collisions in a
single batch. Where the Chinese is more precise than the English, move the
English to meet it rather than blunting the Chinese.

## Commit protocol

Write the message for someone reading `git log` in six months with no memory
of the session. State what was wrong, what changed, *why that fix and not
another*, and what was verified — including the things you could not verify.
Record judgement calls and anything you left undone.

Push to **both** `ha-deploy` and `claude/ha-dashboard-upgrades-wui7ig`. Local
`ha-deploy` must be fast-forwarded first or the push reports "Everything
up-to-date" and the commit silently never deploys.

A commit cannot contain its own hash: write the change and its tracking rows
together with the SHA left as a placeholder, then stamp the real SHA in a
one-line `docs: stamp` commit. Do not amend — that changes the hash again.

## Stop and ask

Keep going autonomously through ordinary engineering decisions. Stop only for:

1. Anything on the approval boundary — deleting live entities or integrations,
   auth, secrets, network gear, device control, anything that reduces physical
   security, anything irreversible.
2. Information that genuinely cannot be obtained here — most often "how wide
   does this render", which needs a photograph.
3. Two materially different options with real consequences and no safe
   inference between them. Present the measurement and the options; do not
   quietly pick one. Example: four chip strips that cannot fit one line at a
   legible size — cut a reading, split the pill, or accept two lines is the
   owner's call, not yours.
4. A live-system change with meaningful risk.
5. No worthwhile safe improvement left.

## Reporting

After several meaningful changes, or at the end of a run: what was completed,
what is in flight, validation status, important findings, blockers needing the
owner, and what is planned next. Keep it short and concrete. Say plainly what
was *not* verified — for this repository that always includes anything visual.

## Bundled scripts

- `scripts/render_cards.py` — render a view's markdown cards against a
  populated state set and a fully dark one, in both languages, with an
  optional width measurement. Six ad-hoc variants of this were written in one
  session before it was bundled; use it rather than writing a seventh.
  Its populated pass defaults to `docs/live/fixture_states.json`, built by
  `scripts/build_render_fixture.py` from the entity export. Before that
  default existed the pass ran with an empty state map, so it was a second
  dark pass calling itself live, and every width taken that way described an
  instance where nothing was answering. `ha_validate.sh` fails the build if
  the fixture has drifted from the export.
- `scripts/next_id.py` — the next free `CR-`/`UI-`/`DR-` number, scanned
  across every tracking document. Use it before writing a queue or issue row;
  numbering by eye put two unrelated rows under `CR-318` and `CR-319` on
  2026-09-19, and one of a colliding pair silently never gets checked.
- `scripts/preserve_check.py` — structural diff against any git ref: views,
  cards, entities, navigation targets, service calls, with the added and
  removed items named.

Both are standalone (`python3`, `PyYAML`, `Jinja2`) and print human-readable
output. Run either with `--help`.

## References

- `references/evidence-rules.md` — how to verify an entity, why the export
  lies, and what the live MCP can and cannot tell you. Read before step 3.
- `references/gates.md` — the current gate catalogue, how to add one, and how
  to negative-test it. Read at step 9.
