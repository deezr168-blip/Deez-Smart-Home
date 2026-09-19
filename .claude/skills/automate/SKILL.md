---
name: automate
description: Spot work that keeps being repeated by hand and turn the strongest cases into reusable automation — a shell script, a Python utility, a Claude skill, a validator, a git hook, a Home Assistant automation or a scheduled task. Use this whenever the user asks to automate something, find repeated work, reduce manual steps, build a tool or command, tidy up a workflow, or asks "haven't we done this before" — and also when YOU notice you are writing the same script, running the same command sequence, or following the same multi-step procedure for the third time. Run it at natural checkpoints in longer sessions, after a batch of work is committed, so repetition that only shows up across a whole session gets caught. Prefer this over building a one-off helper, because the first question it answers is whether a tool for this already exists and can be extended instead.
---

# Automate repeated work

Noticing repetition is easy in the moment and impossible across weeks. This
turns "I think I have done this before" into a record that survives sessions,
a score that can be argued with, and — when a candidate is strong enough —
something built, tested and committed.

**The bar is deliberately high.** Something happening twice is not a pattern,
and a repository full of tiny single-purpose scripts is worse than one where
the work stayed manual. The scoring below never reaches HIGH on two
occurrences, on purpose.

## The loop

1. **Observe without derailing.** Finish the work the user asked for first.
   Repetition is noticed in passing, not hunted mid-task.
2. **Record it.** `procmem.py record` when you recognise a workflow, or pipe a
   batch of commands through `procmem.py observe` to see what recurs by shape.
3. **Score.** `procmem.py score` ranks everything and says what form each
   candidate should take. `--explain <name>` shows the arithmetic.
4. **Check what exists — always, before building.** `inventory.py` lists every
   script, skill, HA package, hook and CI workflow with its own description;
   `inventory.py --find <term>` searches them. Extending something that
   already runs in the validation path is worth more than a new tool nobody
   remembers to call.
5. **Build the strongest candidate** if it is HIGH and safe. Smallest thing
   that works, per the hierarchy below.
6. **Test it, including the refusal path.** A tool that cannot demonstrate it
   refuses bad input has not been tested.
7. **Run it against the work that motivated it** and compare to the manual
   result. If it does not reproduce what you did by hand, it is not finished.
8. **Record the resolution** — `procmem.py resolve <name> --automated-by <path>` —
   then `procmem.py registry` to regenerate `AUTOMATION_REGISTRY.md`.
9. **Commit**, following the repository's own conventions.

## What form it should take

Reach for the simplest reliable thing. The order matters more than it looks:
reaching for a Claude skill when a shell script would do produces something
slower, less predictable and harder to test.

| Situation | Form |
|---|---|
| A tool already does most of it | extend that tool |
| Deterministic, a handful of commands | shell script |
| Deterministic, parsing or comparing data | Python utility |
| Needs judgement, interpretation, diagnosis | Claude skill |
| Must not be skippable before a commit | git hook |
| Must run on every push | CI check |
| Must happen on a clock | HA automation or cron |

`procmem.py` suggests one of these from what you recorded — `--judgement`
routes to a skill, `--data` to a Python utility, `--gate-on` to a hook or CI.

**A skill is for judgement, a script is for procedure.** If you can write down
the steps completely, write a script. If the hard part is deciding *which*
steps, write a skill — and give it scripts for the mechanical parts, which is
what `improve-system` does.

## Scoring

Six bounded dimensions, so no single one carries a candidate alone:

```
frequency   0-4   2 occurrences is 1 point; 10+ is 4
steps       0-3   under 3 steps scores nothing
time saved  0-3   minutes x occurrences, capped
error risk  0-2   +1 per recorded failure
deterministic 0-2 judgement-shaped work scores 0 here and routes to a skill
already automated  -3

HIGH >= 7    build it, if safe
MEDIUM >= 4  build it only if it materially simplifies the workflow
LOW          record and leave alone
```

A LOW score is a real answer. Most recorded workflows should stay LOW forever.

Worked examples from this repository are in `references/scoring.md` — including
two that scored HIGH and were worth building, and one that scored LOW and was
built anyway on judgement, which is allowed but should be deliberate.

## Safety

Run autonomously: validation, read-only analysis, reporting, formatting,
comparison, linting, generating derived files. These are safe because they are
reversible and observable.

**Do not build or run autonomously**, without asking first: deleting files,
destructive git operations (force-push, history rewrite, hard reset on work
that is not yours), rewriting large parts of a configuration, production
deployment, credential or auth changes, network or firewall changes, package
upgrades that reach production, database modification, anything that
physically actuates the house.

In this repository specifically: `scripts/sync_casaray_to_config.sh` puts a
dashboard in front of people, `packages/casaray_automation.yaml` can act on
the house, and `MAINTENANCE.md` lists paths that are off-limits without an
instruction. Wrapping any of those in new automation is a decision to bring to
the owner, not one to make.

**Make it idempotent.** Running it twice should be safe and should say so.
Mutating tools keep a backup and support `--dry-run`; that is the pattern
`dashboard_edit.py` follows and the one to copy.

## Recording what you build

`AUTOMATION_REGISTRY.md` is generated — record the workflow and re-run
`procmem.py registry` rather than editing it, or the next regeneration
silently discards what you wrote.

`.claude/process-memory.json` stores the *shape* of workflows: normalised
commands, files touched, counts, dates. Never command output, environment
variables, or anything secret-shaped — `procmem.py` redacts on the way in, but
the real protection is not putting it there.

## Repetition is conceptual, not textual

`grep entity_id dashboards/casaray_v2.yaml` and
`grep sensor. dashboards/deez_smart_home.yaml` are the same workflow.
`procmem.py` normalises before comparing — literals, numbers, git revisions
and specific filenames all collapse — so near-identical runs group together
instead of filling the memory with unique one-offs.

Look for the larger shape too. Checking unavailable entities, comparing them
against the export, looking for duplicate friendly names, querying live state
and updating a reconciliation note are not five workflows; they are one, and
it should become one tool rather than five. Likewise *edit → validate → sync →
verify → report → commit* is one deployment workflow wearing six hats.

## Reporting

When you act on a candidate, say so in one line and move on:

```
AUTOMATION: dashboard section splicing was hand-written 8 times this session,
once incorrectly. Built scripts/dashboard_edit.py — locate, show, replace,
insert, delete, span. Refuses any edit that would not re-parse.
```

Then, once: what was created, what manual steps it replaces, how it was
tested, and what it does not cover. Do not interrupt work for a MEDIUM or LOW
candidate — record it and mention it at the next checkpoint.

## Improving this skill itself

The same rules apply here. If the discovery or scoring process is being done
by hand each time, that is a candidate like any other. Periodically:
merge workflows that turned out to be the same thing, `prune` stale one-offs,
and check whether automation that was built is actually being used — an
unused tool is a maintenance cost, and the honest move is to delete it and
record why.

Do not rewrite stable automation without evidence it needs changing.

## Bundled scripts

- `scripts/procmem.py` — record, observe, score, explain, resolve, prune,
  registry. The scoring lives here rather than in this file so it is
  reproducible and can be disagreed with.
- `scripts/inventory.py` — every automation artefact in the repository with
  its own description; `--find <term>` before building anything.

## References

- `references/scoring.md` — the rubric with worked examples from this
  repository, including a candidate that scored LOW and a judgement call that
  overrode it.
- `references/patterns.md` — the workflow families this repository actually
  has, and which tool covers each.
