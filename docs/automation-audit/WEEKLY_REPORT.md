# Weekly automation audit — 2026-10-12 (revision 1, after independent review)

**Evidence limits.** Only git history, the GitHub PR list and `.claude/process-memory.json` are available to this routine. No session transcripts, task logs or ChatGPT conversations. Each figure below is tagged **measured** (re-derivable from git or the Routines API, command given), **self-reported** (process-memory, not re-derivable), or **estimate**. `ha-deploy` has **0 commits in the last 7 days** (last: 2026-09-25); the week's activity was V3 design work on other branches.

**Corrections to the first version of this report**

| First version said | Re-derived | Command |
|---|---|---|
| 13 `stamp` commits | **8** (`docs: stamp` / `re-stamp`); 4 more commits merely mention the word in their body | `git log origin/ha-deploy --format='%h %s' \| grep -E ' docs: (re-)?stamp'` |
| 91 `ha-deploy` commits since 2026-09-12 | **49**: the branch's whole history, 2026-09-18 to 2026-09-25 | `git rev-list --count origin/ha-deploy` |
| "This run is itself a scheduled firing" | It was a **creation-time** run (fired 20 s after the Routine was created, on a Monday; the cron is Saturday). The cron path has not fired yet. | Routine `last_fired_at` vs `created_at` |
| `jinja2` is the missing dependency | A clean environment is also missing **PyYAML**; the first sandbox just had it | clean-venv run, below |

1. **Repeated tasks.**
   (a) Stamping a SHA into tracking rows: 8 commits, all 2026-09-18 to 2026-09-25 (measured). (b) Validate, commit, push both branches: 16x (self-reported, not re-derivable). (c) Compare a live render to the mockup: 3x, ~40 min each (self-reported). (d) **New:** the validator cannot run in the sandbox it is given. Two owner-authored commits on 2026-09-25 (`7309bd8` Python-less shells, `18a4e5d` shell preamble; measured) and this week's routine sandbox missing `jinja2` (reported by the first run; reproduced here by hiding the module). Same class, three occurrences.
2. **Highest priority.** The first version chose (a) because `procmem.py score` rated it 9 HIGH. That score is driven by the `minutes` field, which is **agent effort**, not owner input (see 4). Ranked by owner input, (d) is first: it has measured owner cost and one owner action removes the class. (a) remains a reliability and agent-effort improvement.
3. **Improved.** `improve-system` (no new skill): `scripts/stamp_sha.py` hardened and documented; `requirements-dev.txt` added; `scripts/ha_validate.sh` unreachable tail removed.
4. **Owner-input events eliminated** *(measured separately from 5)*.
   - `stamp_sha.py`: **0.** All 8 stamp commits are authored by `Claude`; the owner never typed one (`git log --format='%an'`). The tool removes agent steps, not owner input.
   - `requirements-dev.txt`: **0 so far.** It becomes real only when the owner adds the setup-script line (see 9). Cost it targets: 2 owner-authored validator-environment commits (measured).
   - **Net verified this week: 0 events.** One owner action requested.
5. **Agent effort saved** *(estimate, kept apart from 4)*.
   - `stamp_sha.py`: 6 recorded steps become 1 command. Minutes: process-memory's **4 min per stamp is self-reported**. Observed stamps in the last 7 days: **0**, so **0 min** observed. Busiest observed week (2026-09-18 to 09-25): 8 stamps, at most ~32 min if the 4 min is right. It only recurs if V2 work on `ha-deploy` resumes: `casaray-v3-design` has no stamp commits and no stamp-able table.
   - Reliability: 1 of 8 stamps needed a re-stamp (`86ec579`, after a rebase). The tool does not prevent that; it makes it one flag.
6. **Validation.**
   - `stamp_sha.py --self-test`: **27/27** (was 11). Ten guard mutations (e.g. remove the cell-count guard, write in place, de-dup off) are each caught by at least one check.
   - Independent adversarial suite (not committed), 30 checks over idempotence, duplicate IDs, missing IDs, malformed input and dry-run safety: **20/30 on the first version, 30/30 now** (1 SKIP: file-mode check is meaningless as root).
   - Replay of **all 8** historical stamp commits against their parents: 7 byte-identical to the hand edit with default flags. The 8th (`bd49f14`) is refused: CR-318 sits on two unrelated rows and the human stamped one of them. `--all-rows` would over-stamp; no flag picks one of two, so the refusal is correct (known limit).
   - `ha_validate.sh`: exit 0 with `jinja2` + `PyYAML`; exit 1 with `jinja2` hidden, **identically on base and this branch**; clean venv: exit 1 (2 problems) before `pip install -r requirements-dev.txt`, exit 0 after. Output and exit code are byte-identical before and after the tail removal in four environments (normal, `jinja2` hidden, no Python, clean venv). `bash -n` now passes (it did not on `ha-deploy`).
   - Note: no Python at all gives exit 0 `VALIDATION PARTIAL`, while a missing module gives exit 1. Deliberate (commit `7309bd8`), but a pass-by-absence the routine should not treat as a full pass.
7. **Files.** `scripts/stamp_sha.py`, `.claude/skills/improve-system/SKILL.md`, `.claude/process-memory.json`, `AUTOMATION_REGISTRY.md`, `requirements-dev.txt` (new), `scripts/ha_validate.sh` (-135 lines), `docs/automation-audit/*`. `CLAUDE.md` unchanged.
8. **PR.** [PR #5](https://github.com/deezr168-blip/Deez-Smart-Home/pull/5), draft, never merged automatically.
9. **Needs approval (owner).**
   1. Add `python3 -m pip install -r requirements-dev.txt` to the cloud environment's **Setup script** (environment menu, Edit). Without it the next routine run fails section 2 again.
   2. Detach unneeded connectors from the Routine (it needs none to audit a repository; see below). The Routines API this session can edit name, schedule and prompt, not connectors.
   3. Add a base-branch line to the Routine prompt (see below). Not edited here: it is a live schedule.
   4. Extend `scripts/deny_device_control.py` to cover `media_player__play_media` (see below).
   5. Unchanged from the first version: automating push-to-both-branches (external action); adding `stamp_sha.py --self-test` to `verify_change.sh`.

**Routine evidence** (Routines API, read-only, 2026-10-12)

| | |
|---|---|
| Routine | `trig_01F4irXHwaazWvbsKKZLhWdr`, "isolated automation-audit branch" |
| Schedule | cron `0 22 * * 6`, **no `CRON_TZ` prefix, so UTC**: Saturday 22:00 UTC |
| Next fire | 2026-10-17 22:01:54 UTC (a Saturday; the ~2 min offset is server-side) |
| Enabled | yes. It is the **only** enabled recurring routine (the four older ones listed are disabled) |
| Last run | 2026-10-12 02:16:17 UTC, succeeded, created PR #5. A creation-time run, not a cron run |
| Session | fresh session per fire (`persist_session: false`) |
| Local time | Household zone is **not recorded** in the repo or the Routine. Australia is **inferred** (NMI/MIRN billing terms, A$), not confirmed. If so, 22:00 UTC Saturday is Sunday 09:00 AEDT (NSW/VIC/ACT/TAS), 08:30 ACDT (SA), 08:00 AEST (QLD), 07:30 ACST (NT), 06:00 AWST (WA). Fixed UTC means the local hour moves by one at daylight-saving changes (next: April 2027) |

- **Not yet proven:** the cron path has never fired. The first cron-driven run is 2026-10-17 22:01 UTC; check it ran (a new PR or a "no evidence" report) before relying on the schedule.
- **Connectors.** Nine are attached (Claude Docs, Context7, Gmail, Google Calendar, Google Drive, Home Assistant, Spotify, Todoist, visualize) and none lists a tool restriction (`permitted_tools` is empty; what empty means is not documented where I could read). A repository audit needs none. The repo's guard (`scripts/deny_device_control.py`, hook matcher `.*Hass.*`) blocks 20 of the 21 side-effecting Home Assistant tools exposed this session; the gap is `media_player__play_media`, which has no `Hass` in its name so the hook never runs. The 21 explicit `mcp__Home_Assistant__*` deny entries in `.claude/settings.json` match no live tool name (they omit the `intent__`/`light__`-style segment) and are inert; the hook is the real guard.
- **Future PRs default to `ha-deploy`.** The Routine prompt names no base branch, so each weekly PR will need retargeting by hand: repeated owner input. The base is the owner's call; once chosen, a line such as `Open the PR against <branch>; do not push to any other branch.` ends the retargeting. PR #5 itself needed retargeting from `ha-deploy` to `casaray-v3-design`, done on the owner's instruction.

This revision did not contact Home Assistant or deploy anything.
