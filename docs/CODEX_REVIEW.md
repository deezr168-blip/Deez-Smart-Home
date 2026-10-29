# Independent review workflow (Claude develops, Codex reviews)

Claude and the reviewer are different identities. Neither approves its own
work. This is the protocol, and the prompt to hand the reviewer.

## Roles

| | Does | Never does |
|---|---|---|
| **Claude (author)** | Develops on `autonomous/**` branches, runs the gates, opens a draft PR into `ha-deploy` with the template filled in | Merges, approves, pushes to `ha-deploy`, edits protected paths, weakens a gate |
| **Codex (reviewer)** | Reads the review packet and diff, runs the gates itself, approves or requests changes | Pushes to the author's branch, merges |
| **Owner** | Merges, and is the only person who can approve anything on the owner queue | — |

## Flow

1. Author finishes a batch, then runs
   `python3 scripts/review_packet.py > /tmp/packet.md` and opens a **draft** PR
   into `ha-deploy`. The PR template's *Verified live / NOT verified* sections
   are mandatory.
2. CI (`.github/workflows/ci.yml`) runs the gate, the tests, the audit check and
   a full card render. Red CI is the author's to fix; a reviewer does not look at
   red CI.
3. The reviewer receives the packet plus the PR link and answers the six
   questions at the foot of the packet, in writing.
4. Request-changes goes back to the author. Approve goes to the owner, who
   merges. A new push **dismisses** the approval (branch protection setting,
   owner action B2), so an approval never covers code it did not see.
5. After merge: nothing is live until `scripts/sync_casaray_to_config.sh` runs on
   the host — or until 03:30 if `casaray_auto_deploy` is on (DECISION_LOG D-004).

## Reviewer prompt

> You are the independent reviewer for a Home Assistant dashboard repository
> that drives a wall-mounted iPad in a family home. You did not write this
> change and you cannot see the running system. Read `CLAUDE.md`, then the
> review packet, then the diff.
>
> Reject — do not "note" — any of the following: an entity ID not present in
> `docs/live/states_export_2026-09-05.txt` or defined under `packages/`; a card
> that states "closed", "clear", "normal", "all off" or a zero count with no
> branch for unavailable/unknown inputs; `| float(0)` (or 100 / 9999) used as a
> fallback; a badge block in `casaray_v2.yaml`; `max_columns` above 2; any
> weakened, skipped or deleted check or test; any action that unlocks, opens,
> disarms, disables a camera, restarts Home Assistant, or touches
> authentication, secrets or `.storage`; any claim of live verification without
> a screenshot or API-read states.
>
> Run `bash scripts/ha_validate.sh` and
> `python3 -m unittest discover -s tests` yourself. Answer the six numbered
> questions in the packet. End with exactly one of: `APPROVE`,
> `REQUEST CHANGES: <list>`, or `BLOCKED: <what you need>`.

## Limits

The reviewer sees what the author sees: files. Neither can render the dashboard
or read the host. "Approved" therefore means *consistent and safe by the
repository's own rules*, never *works on the iPad*.
