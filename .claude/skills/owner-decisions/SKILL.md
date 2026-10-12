---
name: owner-decisions
description: Track tasks and owner decisions for the Deez Smart Home and CasaRay projects in one persistent register. Use when the user says Update me, what is outstanding, what needs my decision, pending approvals or open tasks; when you need the owner to approve, deny or pause something (put it as an Approve / Deny / Pause question, batched, and record the answer); when resuming a paused task or ending a session (handover); and before asking the owner anything that may already be decided. Ranks outstanding tasks by priority for the project the branch identifies, shows blockers and offers selectable next actions. Decisions are logged append-only with basis and scope; a general approval never covers a safety, external or protected action; a task is done only on verified evidence. Feeds the weekly audit Routine its items requiring approval. Not for improving dashboards (improve-system), branch rules (session-orient), faults (recovery-triage), equipment registers (provenance-register) or finding repeated work (automate).
metadata:
  version: "0.1.0"
  status: pilot
  origin: owner brief 2026-10-12 (Owner Decision and Project Task Tracking workflow)
---

# Owner decisions and task tracking

One register of what is outstanding, one append-only history of every decision, and
one command, **"Update me"**, so a new session picks up where the last one stopped
instead of asking again.

## Why this exists

Open decisions were scattered: `PROJECT_STATE.md`, `DASHBOARD_BACKLOG.md`,
`design/casaray-v3/DECISIONS.md`, audit reports, and the bodies of pull requests
that close when they merge. Each session rediscovered them or asked afresh, and a
"yes" given in one place was invisible in the next. The register is an **index**:
it holds the state of each decision and points at the record that holds the detail.
It does not copy those records and must not become a second backlog.

Files (the only two the tool writes):
`docs/project-tasks/TASK_REGISTER.md`, `docs/project-tasks/DECISION_HISTORY.md`.
The rules in full: `references/lifecycle.md`.

Everything runs through one script:
`python3 .claude/skills/owner-decisions/scripts/tasks.py <command>`
(read-only commands: `update show ask lookup digest handover check`).

## "Update me"

1. Run `tasks.py update`. Its first line names the project the branch identified.
   If it says the branch **did not identify a project**, ask which one, once; do
   not guess.
2. Tell the owner, in a few lines and in ranked order: what needs their decision,
   what is in progress, what is blocked and why, what is paused. Quote task ids.
   Do not paste the whole output unless asked.
3. Offer the next actions as a **selection**, not a prose question:
   `tasks.py update --select` prints a ready AskUserQuestion payload (multi-select:
   Decide / Work / Resume / Another project, and the top tasks). Pass its
   `questions` to AskUserQuestion unchanged.
4. Act on what they pick: *Decide* goes to the next section; *Work* is
   `tasks.py start TASK,TASK`; *Resume* is `tasks.py resume`; *Another project* is
   `tasks.py update --project KEY`.

## Putting a decision to the owner

Whenever owner input is genuinely required (an approval, a choice, a go-ahead):

1. **Look first.** `tasks.py lookup <words>`. A decision already recorded is
   reused, not re-asked. A `DENIED` task is not raised again unless something has
   changed, and then through `reopen`, with the new evidence stated.
   (Root `CLAUDE.md`, *Context First, Questions Last*, items 3 and 5.)
2. **Make it a task.** `tasks.py add ... --status AWAITING_DECISION`, or `raise`
   for an existing one. The `--next` text is the **proposal**: what happens if the
   owner approves. Choose the `--gate` honestly (`lifecycle.md`, *Gates*). If a
   task touches the live system, a device, a purchase or a message, it is not
   `none`.
3. **Ask as a selection.** `tasks.py ask --json` returns AskUserQuestion questions,
   at most four per call, each offering exactly **Approve / Deny / Pause**.
   Page with `--page 2`. Do not reword the options or add your own: the owner
   learns three words and the tool records three verdicts. All the questions for
   one session go in one batch (*Context First*, item 8).
4. **Record exactly what they answered.** Write the answers to a file, then:

   ```
   tasks.py decide --batch answers.json --by owner --via ask-user-question \
       --basis "selected Approve for TASK-004, Pause for TASK-006"
   ```

   where each answer is `{"task", "verdict", "scope", "context", "resume_when", "until"}`:
   - **approve**: `scope` states the exact action authorised. Required for any
     gated task; it is single-use.
   - **deny**: `context` is the owner's reason.
   - **pause**: `context` is what must be kept to resume; `resume_when` is the
     condition; `until` is a date if they gave one.
   - free text typed under "Other" is the owner's own words: put it in `context`
     rather than choosing a verdict for them.

   Add `--blanket` only if the owner gave one general answer ("approve all").
   The tool then skips every gated task and says so.
5. **Unanswered means undecided.** If the question was dismissed or skipped, record
   nothing. Never infer consent from silence, from "looks fine", or from approval
   of something else.

## Working a task

- `start TASK` when work begins; `block TASK --reason` / `unblock TASK` for a
  blocker that is not an owner decision.
- `complete TASK --source "commit abc1234" --verified-by claude` is accepted only
  if the commit or file exists. Anything only the owner can see (the wall iPad,
  a device, an account) needs `--verified-by owner`. If it is deployed but not yet
  seen, the task stays `IN_PROGRESS` and says so in `--next`. **Never mark
  something done that has not been verified.**
- `edit TASK` changes priority, next action or evidence, and tightens a gate.
- A gated task's approval covers the action in its scope and nothing else. Whether
  the carrying-out session may perform that action is still decided by the rules
  that already govern it (root `CLAUDE.md`, the V3 hard boundaries,
  `MAINTENANCE.md`). The register records consent; it does not grant authority.

## End of a session

Run `tasks.py handover`. It lists what is in flight, waiting, paused and blocked,
and what was recorded today, and says whether the two files are committed. A
cloud container is reclaimed when the session ends: **uncommitted register changes
are lost.** Commit them with the work, to the branch `session-orient` names.

## The weekly audit Routine

`tasks.py digest` is the source of the Routine's **Items requiring approval**. The
Routine reads, reports and records; it never decides.
`references/weekly-routine.md` has the data flow, the proposed prompt addendum and
the caveat about which branch the Routine sees. The addendum changes a live
schedule, so it is a pending decision in the register and has not been applied.

## Hard rules

- Only the owner records an owner decision; `--by` must be `owner` and `--via` a
  channel they used. The tool refuses anything else.
- A general approval never approves a `safety`, `external` or `protected` task.
- No purchase, payment, message, upload or share, ever, on the strength of a
  register entry. Each needs its own explicit yes at the time.
- No live Home Assistant control, deploy, sync, reload or restart from here. The
  tool has no network and no write other than the two files.
- Never edit a past history row; correct it with a `NOTE`. Never delete a task.
- Never write a task as done, or a fact as `VERIFIED`, that was not observed.
- Do not put secrets, tokens, account identifiers or personal data in any cell.
- If `tasks.py check` fails, say so and fix the cause. Do not write around it; the
  tool refuses to write while the files disagree.

## Where it ends

| For… | Use |
|---|---|
| which rules and push target apply on this branch | `session-orient` (it also prints a one-line count from this register) |
| a card that renders wrongly, an unavailable entity, a failing gate | `improve-system` |
| something broken or lost on the live setup | `recovery-triage` |
| an equipment, quote or evidence register | `provenance-register` |
| finding repeated work | `automate` |
| design decisions *themselves* (what was chosen and why) | `design/casaray-v3/DECISIONS.md`; the register only tracks their state |

## Validation

`python3 .claude/skills/owner-decisions/scripts/tasks.py --selftest` builds
throwaway repositories and runs 160+ checks: Approve / Deny / Pause, resume,
"Update me", filtering, ranking, multi-task selection, atomic batches, append-only
history, persistence across a commit and a fresh clone, tamper detection, the
refusals above, and that the repository's device-control guard is untouched. Each
safety guard was also broken on purpose in a scratch copy to prove the self-test
notices. `tasks.py check` lints the real files; run it before committing them.

## Maintenance

The transition table and the lint are one implementation (`step()` and `replay()`
in `tasks.py`) used by both the writers and `check`, so they cannot drift. Change
a rule in the code, add a case to `--selftest`, then update
`references/lifecycle.md`. Never add a network call, a git call that writes, or a
write to any other file.
