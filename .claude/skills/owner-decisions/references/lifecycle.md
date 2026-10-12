# Lifecycle, gates and evidence

The full rules behind `scripts/tasks.py`. `tasks.py check` enforces everything in
this file; if the file and the tool disagree, the tool is right and this file is a
bug.

## What is tracked, and what is not

The register is an **index of decision state**, not a second backlog.

| If the task… | …its detail lives in | The register holds |
|---|---|---|
| is a V2 backlog item or issue | `DASHBOARD_BACKLOG.md`, `DASHBOARD_ISSUES.md` | state, priority, gate, next action, a pointer |
| is a V3 design decision or follow-up | `design/casaray-v3/DECISIONS.md` | the same |
| came from an audit or a PR | that report or PR | the same |
| originated in conversation | nowhere else: `Home` is `register` | the whole task |

Never copy a task's reasoning or evidence into the register. Point at it
(`Home`). A task has exactly one row, and one row has exactly one `Home`.

## Statuses

| Status | Means | Counts as outstanding |
|---|---|---|
| `OPEN` | known work, needs no owner decision | yes |
| `AWAITING_DECISION` | blocked on the owner: Approve / Deny / Pause | yes |
| `APPROVED` | the owner approved; not yet started | yes |
| `IN_PROGRESS` | being worked | yes |
| `BLOCKED` | cannot proceed for a stated reason that is not an owner decision | yes |
| `PAUSED` | the owner put it on hold; the context needed to resume is saved | yes, listed separately |
| `DONE` | finished, on VERIFIED evidence | no, but kept |
| `DENIED` | the owner said no, with a reason | no, but kept |

## Transitions

| Event | From | To | Who may record it |
|---|---|---|---|
| `ADDED` | none | `OPEN`, `AWAITING_DECISION` or `BLOCKED` | anyone |
| `RAISED` | `OPEN`, `BLOCKED` | `AWAITING_DECISION` | agent |
| `APPROVED` | `AWAITING_DECISION` | `APPROVED` | **owner only** |
| `DENIED` | `AWAITING_DECISION`, `OPEN`, `APPROVED`, `IN_PROGRESS`, `BLOCKED`, `PAUSED` | `DENIED` | **owner only** |
| `PAUSED` | `AWAITING_DECISION`, `OPEN`, `APPROVED`, `IN_PROGRESS`, `BLOCKED` | `PAUSED` | **owner only** |
| `RESUMED` | `PAUSED` | the status it was paused from | **owner only** |
| `STARTED` | `OPEN`, `APPROVED` | `IN_PROGRESS` | agent |
| `BLOCKED` / `UNBLOCKED` | `OPEN`, `APPROVED`, `IN_PROGRESS` / `BLOCKED` | `BLOCKED` / the status before | agent |
| `COMPLETED` | `OPEN`, `APPROVED`, `IN_PROGRESS` | `DONE` | the verifier named in the evidence |
| `REOPENED` | `DENIED`, `DONE` | `AWAITING_DECISION` (or `OPEN` for an ungated `DONE`) | **owner only**, with new evidence |
| `NOTE` | any | unchanged | anyone; changes priority, gate (tightening only) or next action, or corrects an earlier row |

Anything not in the table is refused. A denied task cannot be approved or
re-raised; it can only be reopened by the owner, with something new to say.

## Owner decisions

`APPROVED`, `DENIED`, `PAUSED`, `RESUMED` and `REOPENED` record **what the owner
actually answered**. Each row carries:

- `By` = `owner` (or `ray`); the tool refuses any other name.
- `Via` = the channel they used: `ask-user-question`, `chat` or `pr-review`.
  Never `routine`, `agent` or `inferred`.
- `Basis` = what they selected or said, in a few words.
- `Scope` (approvals) = exactly what was authorised.
- `Context` (denials and pauses) = the reason, or what must be kept to resume.

**No answer is not a decision.** A question the owner has not answered stays
`AWAITING_DECISION`. Silence, a general "go ahead", or an earlier approval of
something else is never recorded as consent
(root `CLAUDE.md`, *Context First*, item 10).

## Gates: general approval does not bypass safety

A task's `Gate` says what kind of consequence an approval would unlock.

| Gate | Covers |
|---|---|
| `none` | repository-only, reversible work |
| `safety` | anything that moves or disables a device, camera, lock, alarm or siren; the device-control guard; appliances; anything that lowers protection |
| `external` | a purchase, payment, message, email, upload, share or post: anything that leaves the household or the repository |
| `protected` | the live system and what protects it: deployment, authentication, tokens and secrets, backups, validation gates, instruction files, `MAINTENANCE.md`'s protected list, account-level automation (Routines, connectors) |

For a gated task:

1. It cannot be `OPEN` and cannot start without an approval.
2. The approval must carry a **specific `Scope`** naming the exact action
   (12 characters minimum is the mechanical floor, not the standard). It is
   **single-use**: reopening a finished gated task needs a fresh decision.
3. A **blanket** answer ("approve everything pending") skips it. The tool applies
   the ungated tasks, leaves the gated ones `AWAITING_DECISION`, and says which.
   Denying or pausing under a blanket answer is allowed, since both reduce risk.
4. Only the owner can verify it is `DONE`.
5. A gate is only ever **tightened**. Loosening one is a new owner decision.

The gate records the *kind* of approval needed. It does not replace the
repository's own rules: the *Do not touch* list in root `CLAUDE.md`, the V3 hard
boundaries, and `MAINTENANCE.md` still apply to whoever carries the action out.
Approving a task in this register never authorises a deploy, a restart, a device
action, a purchase or a message by itself; the action has to be one the rules
let the carrying-out session do.

## Evidence

The `Evidence` cell reads `STATUS · source · date · by`.

| Status | Means | Needs |
|---|---|---|
| `VERIFIED` | observed directly | source, date and who observed it |
| `REPORTED` | stated by a record or a person, not re-checked | source and date |
| `ASSUMED` | a working assumption | flagged; the tool warns |
| `UNKNOWN` | not established | the word, never a blank |

This is `provenance-register`'s vocabulary. A row seeded from another record is
`REPORTED`: its status is as that record stated it on that date.

**`DONE` needs `VERIFIED` evidence, and the source must be one of:**

| Source | Accepted when |
|---|---|
| `commit <sha>` | the commit exists in this clone (the tool checks) |
| `file <path>` | the file exists in this tree (the tool checks) |
| `owner <what they confirmed>` | the verifier is the owner |
| `pr <n>` | the verifier is the owner |
| `live <what was seen>` | the verifier is the owner |

An agent cannot verify what only the owner can see. Work that is deployed but not
yet seen on the wall iPad stays `IN_PROGRESS` with that as its next action; it
becomes `DONE` when the owner says it passed
(`PROJECT_STATE.md`, *Verification States*: `LIVE_VERIFIED`).

## Priority

The same four levels as `PROJECT_STATE.md`'s *Priority Model*.

| P | Covers |
|---|---|
| `P0` | broken functionality, validation failures, data-loss, security or privacy exposure |
| `P1` | major usability or navigation problems, significant incorrect state, safety findings |
| `P2` | meaningful architecture or feature improvement, decisions that unblock several things |
| `P3` | polish and housekeeping |

## Ranking in "Update me"

Priority first. Within a priority: `AWAITING_DECISION` (it unblocks other work),
then `IN_PROGRESS`, `APPROVED`, `OPEN`, `BLOCKED`; then the task that has waited
longest. `PAUSED` tasks are listed in their own section. `DONE` and `DENIED`
stay on record and are counted, but are not listed unless asked for.

## Home pointers

`Home` is one of:

| Form | Checked |
|---|---|
| `register` | the task has no other home |
| `path/to/file.md` or `path/to/file.md#literal text` | the file exists in this tree and the text occurs in it |
| `pr:N` or `pr:N#text` | not checkable offline; reported as a note |
| `branch:NAME:path#text` | not checkable offline; reported as a note |

## Projects

The `Projects` table in the register maps a branch to the project it belongs to,
so "Update me" can identify the current project without asking. A project marked
`all` is cross-cutting and shown whatever the branch. A branch that matches no
project shows everything and says so; say which project you are on rather than
guessing.

## The two files, and keeping them honest

- `docs/project-tasks/TASK_REGISTER.md`: current state.
- `docs/project-tasks/DECISION_HISTORY.md`: append-only. A row is never edited or
  removed; a mistake is corrected with a `NOTE` row.

`tasks.py check` replays the history and compares the result with the register:
status, gate, priority, the `Decision` cell and the `Updated` date must all agree.
It also fails on a task missing from the history, a decision id reused or out of
sequence, an owner row written by anyone else, a gated approval with no scope,
and a `DONE` task without `VERIFIED` evidence.
`tasks.py check --append-only-vs <ref>` additionally fails if any earlier history
row differs from that ref or any task has disappeared.

The tool refuses to write while the two files already disagree, so one hand edit
cannot quietly compound.

Both files must be committed to survive the session. A cloud container is
reclaimed when the session ends; `tasks.py handover` says whether they are saved.
