# Recovery safeguards

A checklist for **reviewing or preparing** a recovery plan. It is not a licence
to run one: nothing in this environment can reach `/config`, and the steps that
matter are on the owner-approval boundary.

These were not invented for this skill. They are the safeguards that recur in
the recovery branch's commit messages (`recovery/phase0-diagnostics`, nine
commits in two sessions, 2026-09-26 to 2026-10-12, read through the GitHub API),
plus `MAINTENANCE.md`. Short hashes are given so each can be checked. Backup
identifiers and usernames are deliberately not copied here.

| # | Safeguard | Why, and where it came from |
|---|---|---|
| R1 | **Plan before action, and label it.** A plan says "planning only, nothing run"; every write step says it needs approval. | `1458c0d`. A plan that reads like a procedure gets run. |
| R2 | **Read-only gates first.** Establish facts with steps that cannot change anything before any step that can. State what each gate reads. | `aa78292`, `835ca7f`: a Phase 0 diagnostic and a backup inspection, each with "no rm/mv/write redirects, no restart". |
| R3 | **Backup before change, and verify the backup before touching anything.** "Verified" means something was read back, for example `ha backups info`, not that the command exited 0. | `59c3b92`, `3dc2365`. |
| R4 | **Typed confirmation for the destructive step.** The word `APPLY` or `ROLLBACK` typed in full, not a `y` that Enter can supply. | `0a2c638`, `efe9430`, `cc8e049`, `3dc2365` (4 of the 9 commits). |
| R5 | **Fingerprint what must not change.** Hash the user database, config entries, registries and onboarding state before and after; restore automatically if they differ. | `cc8e049`. |
| R6 | **Roll back automatically if the system does not return, but define "return" carefully.** "Something answers on port 8123" counted as up and let verification run too early on a host that redirects that port. Use the application's own API answering, and roll back only if the container has *stopped*, not merely started slowly. | `3dc2365`, a correction found by audit. |
| R7 | **Nothing secret in any output.** No hash, token, key or password; passwords read hidden and passed on stdin, never as arguments; key presence reported as true or false. | 7 of the 9 commits. |
| R8 | **Test before offering, including a test that must fail.** Run against a simulated host and, where possible, the platform's own `check_config`. A deliberately corrupted config proves the check inspects it. State what was **not** tested and where it has not yet run. | `490afac`, `59c3b92`, `cc8e049`, `efe9430`, `3dc2365` (6 of the 9). |
| R9 | **Call the platform's own tool; do not reimplement it.** A reimplementation broke on the next release. | `cc8e049` replaced `efe9430`'s approach after `repair_login.sh` failed on a new version. |
| R10 | **Withdraw wrong tooling out loud.** When a script is found to be wrong, make it exit immediately and say why in the commit. | `490afac`: `repair_login.sh` withdrawn. |
| R11 | **Check every step against the standing constraints.** The prepared registration block also loaded a package that had to stay inactive, so the one-command apply "must not be used as written". | `1458c0d`, the R3/R9 collision it records. |
| R12 | **One change at a time, verified after each**, with a post-restore checklist written before the first change. | `1458c0d`. |
| R13 | **Stay inside the protected list.** Authentication, users, tokens, `secrets.yaml`, `.storage/`, backups, network gear, restarts and anything that could cause lockout are the owner's. A plan may be *prepared*; it is never *run* without approval. | `MAINTENANCE.md`, *Protected*; the standing preferences' approval boundary. |

## Using this when you review a plan

For each safeguard, write one of: **met** (point at the line), **not met**
(say what is missing), or **not applicable** (say why). Do not leave one
unanswered. A plan that meets fewer than all of R1, R3, R4, R6, R7 and R8 is not
ready to put to the owner.

## What this list does not cover

It does not say *how to recover a particular fault*. For that the repository has
only what `symptoms.md` cites. Where it has nothing, say so; do not supply a
procedure from memory for a system you cannot see.
