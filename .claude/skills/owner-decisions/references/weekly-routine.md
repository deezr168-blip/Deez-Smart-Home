# Pending decisions and the weekly audit Routine

The weekly Routine ("isolated automation-audit branch", cron `0 22 * * 6`, UTC)
ends every report with **Items requiring approval** (its validation item 9). Until
now that list lived only in prose, in a PR body that is closed when the PR is
merged. This makes the register the source of that section.

## What the Routine does with the register

```
  register ──digest──▶ "Items requiring approval" in the weekly report
     ▲                                   │
     └── add / raise ◀── new approval needs found this week
```

1. **Read.** `python3 .claude/skills/owner-decisions/scripts/tasks.py digest --since <date of the last weekly report>`
   prints every task awaiting a decision, ranked, with its gate, how long it has
   waited, what approving it would do and where its detail lives; flags those
   waiting a week or more as **stale**; lists paused tasks whose resume date has
   come and blocked tasks; and lists register activity since that date. `--json`
   gives the same for a script.
2. **Report.** The digest goes into the report verbatim, as section 9. Counts, ages
   and gates are not summarised away.
3. **Record.** A new approval need found this week is added with
   `tasks.py add ... --status AWAITING_DECISION` (or `raise` for an existing task),
   so it is still there after the PR is merged. The weekly report cites the task
   id instead of restating the case.
4. **Never decide.** `tasks.py decide`, `resume` and `reopen` accept only the
   owner, speaking through `ask-user-question`, `chat` or `pr-review`. A Routine
   has none of those channels and records none. A pending item is flagged, never
   acted on.
5. **Never repair.** If the register is missing or `tasks.py check` fails, the
   report says so and the Routine carries on. It does not edit history.

The Routine is not interactive, so it cannot ask. It reports; the owner answers in
a session ("Update me"), and that session records the answer.

## Proposed addendum to the Routine prompt

Append this to the stored prompt (it changes a live schedule, so it is a decision
in the register, `Gate: protected`, and has **not** been applied by the change that
introduced it):

```
[PENDING OWNER DECISIONS]
Before step 6, run:
  python3 .claude/skills/owner-decisions/scripts/tasks.py digest --since <date of the last weekly report>
Put its output, unabridged, under "Items requiring approval" in the report and in
the PR description. Record every new approval need with tasks.py add (or raise) so
it survives the PR. Never run tasks.py decide, resume or reopen: only the owner
decides. Flag a decision waiting 7 days or more as stale; do not act on it. If the
register is missing or `tasks.py check` fails, say so and continue.
```

It is deliberately silent about which branch the Routine's PR opens against. That
is a separate decision (PR #5, approval 3), and it is the owner's to name.

## What reaches the Routine without any prompt change

The Routine already reads root `CLAUDE.md` and `.claude/skills/`. Once the
*Owner Decisions and Task Tracking* standing rule and this skill are on the branch
the Routine checks out, it will find them. That is why the rule is written to be
followable without the prompt addendum, and why the addendum is a belt to that
braces rather than a requirement.

**One caveat the owner should know.** This work is on a V3 branch. The Routine
works from whichever branch its checkout lands on; the V3 rules forbid merging V3
branches into `ha-deploy`. If the Routine runs on `ha-deploy`, none of this is
visible to it until the files are brought there by a route the owner approves
(the same question as the pilot skills, `WORKFLOW_AUDIT.md` section 9, item 5).

## Staleness

`digest --stale-days N` (default 7) flags a decision that has waited N days.
`check` warns at 14. A stale decision is a reason to ask the owner once, in the
next "Update me", batched with the others (root `CLAUDE.md`, *Context First*,
item 8), not a reason to ask in a notification.
