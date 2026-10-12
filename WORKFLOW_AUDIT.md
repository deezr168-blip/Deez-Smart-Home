# Workflow audit

Repetition audit of the work reachable from this session: what is done by hand
more than once, what already has automation, and what is worth building next.

Audit date **2026-10-12**. Branch `casaray-v3-design`. Produced as a read-only
pass; no existing file was modified. Companion files: `SKILL_REGISTRY.md`
(what exists, what was added) and `SKILL_VALIDATION_REPORT.md` (what was tested).

## How to read this document

Every figure carries one of four labels. A number without a label is a defect.

| Label | Meaning |
|---|---|
| **[M]** | Measured from a source I could read: git history, GitHub API, file metadata, file sizes. A count, not an opinion. |
| **[R]** | Recorded by an earlier session in `.claude/process-memory.json`. Self-reported and unverified; it covers two dates only (2026-09-19, 2026-09-24). |
| **[A]** | Assumed by this audit. My estimate, stated so it can be argued with. Every *minute* in this document is [A] or [R]: **nothing accessible measures how long work took.** |
| **[N]** | No evidence reachable. Listed so the gap is visible, not filled in. |

## 1. Evidence base, and what it cannot support

| Source | How reached | Window | Used for | Limits |
|---|---|---|---|---|
| Git history, this repository | local `git log`; clone was shallow (59 commits), deepened with `git fetch --unshallow` (history only, no branch changed) | 2026-08-23 → 2026-10-12, **362 commits** [M] | frequencies, hot files, commit-type mix | project began 2026-08-22, so the 90-day expansion has nothing further to add |
| `.claude/process-memory.json` | read | 2026-09-19, 2026-09-24 | 12 recorded workflows | self-reported; two dates; minutes unverified |
| Tracked documents | read selectively (outlines, sizes, targeted sections) | current | instruction stack, conventions | `PROJECT_STATE.md` is 182,699 B [M] and was **not** read end to end |
| GitHub API (this repo only) | `list_pull_requests`, `list_commits` | all PRs; one branch since 2026-09-25 | PR flow, recovery effort | read-only; one extra branch (`recovery/phase0-diagnostics`) read by API, not checked out |
| Google Drive | `list_recent_files` (30 newest) and two title searches | newest 30 items; titles back to 2024 | shape of non-HA work | **metadata only. No document was opened.** Titles are deliberately not reproduced here; several look like confidential workplace matters |
| Claude session transcripts | `~/.claude/projects/` | this session only | none | no earlier transcripts are present in this container |
| ChatGPT conversation history | — | — | **none** | **Not accessible and not claimed.** No export or connector exists in this environment |
| Gmail, Calendar, Todoist, other repositories, local files outside the repo | — | — | none | available as connectors in some cases but hold personal data; **not examined**. Say so if you want any of them included |

### Coverage of the domains you named

| Domain | Evidence | Strength |
|---|---|---|
| CasaRay / Home Assistant | 362 commits, 35 automation artefacts (per `inventory.py`), 2 project skills, 12 recorded workflows | strong [M] |
| Troubleshooting and recovery | 6 distinct incident episodes in this checkout, plus a seventh on a recovery branch (9 commits, 2 sessions) [M] | strong |
| GitHub | 4 PRs, 31 remote heads (24 under `claude/*`) [M] | moderate |
| Workplace documentation | 30 newest Drive items: 8 folders, 16 Google Docs, 1 .docx, 5 PDFs; 16 carry a numbered-prefix naming scheme [M, metadata only] | weak: shape, not content |
| Structured reports | the numbered document packs above; repo status documents | indirect |
| Household projects | solar and battery quote documents in Drive; the HA project itself | indirect |
| Purchasing comparisons | three quote-request or quote files, 2024–2026; **no comparison document found** by title | **[N]** for comparisons |
| Equipment registers | two faulty-equipment *report forms*; **no register found** by title | **[N]** |

Where the evidence is [N], this audit does not invent a workflow. It names what
exemplar would unlock one (section 8).

## 2. Scoring method

Four dimensions, each 0–4, total 0–16. The repository's own `automate` skill
uses a different six-dimension rubric (`procmem.py score`); both are shown
where an item appears in both, and they disagree in places, for stated reasons.

| Dim | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| **F** frequency, occurrences in window | 0–1 | 2 | 3–4 | 5–9 | 10 or more |
| **T** time saved, weekly minutes [A] | under 5 | 5–14 | 15–29 | 30–59 | 60 or more |
| **S** simplicity | needs access I lack | large | moderate | small | trivial |
| **R** safety of automating it | crosses a hard boundary | touches live system, push, or external send | edits tracked project records | writes local files, reversible by git | read-only |

Bands: **High ≥ 12**, **Medium 8–11**, **Low ≤ 7**. Ties are broken by higher R,
then higher F, then ID. A score of R = 0 means *propose, never build*. Class G
("keep manual") overrides the score.

Classes: **A** skill · **B** script · **C** template · **D** hook ·
**E** scheduled automation · **F** improvement to an existing workflow · **G** keep manual.

## 3. Ranked opportunities

`Built` means built in this pass. 31 workflows were reviewed: 19 candidates
below (17 scored, 2 with no evidence), plus 12 already automated (section 6).

| Rank | ID | Workflow | Class | F | T | S | R | Score | Band | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | W06 | Pre-commit scope, secret and rule check on V3 branches | B → folded into skill | 4 | 2 | 4 | 4 | **14** | High | **Built**, as `session-orient --scope` |
| 2 | W03 | Session orientation and rule-regime resolution | A | 4 | 2 | 3 | 4 | **13** | High | **Built**: `session-orient` |
| 3 | W04 | Troubleshooting and recovery triage | A | 3 | 2 | 3 | 3 | **11** | Medium | **Built**: `recovery-triage` |
| 4 | W05 | Evidence-labelled registers, comparisons and reports | A | 3 | 2 | 3 | 3 | **11** | Medium | **Built**: `provenance-register` |
| 5 | W08 | Conflicting and duplicated standing instructions | F | 4 | 1 | 4 | 2 | 11 | Medium | Proposed; owner decision |
| 6 | W09 | `PROJECT_STATE.md` growth and its context cost | F | 4 | 2 | 3 | 2 | 11 | Medium | Proposed; owner approval |
| 7 | W02 | Validate, commit, push to the right branches | F | 4 | 2 | 4 | 1 | 11 | Medium | Risk mitigated by W03; script **not** proposed for build |
| 8 | W13 | Regenerating derived artefacts | B | 3 | 1 | 3 | 3 | 10 | Medium | Proposed script |
| 9 | W01 | Stamping a commit SHA into tracking rows | B | 4 | 1 | 3 | 2 | 10 | Medium | Proposed script; blocked on regime |
| 10 | W07 | Writing tracking records (queue, issues, progress) | G | 4 | 3 | 1 | 2 | 10 | Medium | **Keep manual** |
| 11 | W19 | Comparing a live render with the approved mockup | A | 2 | 2 | 1 | 4 | 9 | Medium | Not built: needs photographs |
| 12 | W14 | Two overlapping entity verifiers | F | 2 | 1 | 2 | 3 | 8 | Medium | Proposed consolidation |
| 13 | W15 | Defects in existing tooling | F | 1 | 0 | 4 | 3 | 8 | Medium | Reported, not fixed |
| 14 | W18 | Entity-inventory sync with live state | F | 2 | 1 | 1 | 3 | 7 | Low | Known gap, documented |
| 15 | W10 | Document-pack production (workplace documentation) | C | 1 | 2 | 2 | 2 | 7 | Low | Needs an exemplar |
| 16 | W16 | Session-branch sprawl on the remote | G | 2 | 0 | 3 | 1 | 6 | Low | Deleting needs approval |
| 17 | W17 | PR and branch flow | G | 1 | 0 | 3 | 1 | 5 | Low | Conflict reported (section 5) |
| — | W11 | Purchasing / quote comparison | — | — | — | — | — | unscored | — | **[N]**; reuse `operations:vendor-review` |
| — | W12 | Equipment register | — | — | — | — | — | unscored | — | **[N]** |

**Why the most-repeated item is not first.** W01 is the largest repetition by
count (70 of 362 commits, 19% [M]) but it is cheap per occurrence (about 3–4
minutes [R]) and bursty: 48 of the 70 landed on two days, 2026-08-29 and
2026-08-30 [M]. Thirteen fall in the last 30 days [M]. Count alone would
overstate it.

**Where the two rubrics disagree.** `procmem.py` scores W01 HIGH (9) and W02
HIGH (11); this rubric scores both Medium. The difference is the safety
dimension: both end in a commit or push that the repository's own rules put
behind the owner.

### Top 10 by opportunity

1. **W06** pre-commit scope and secret check on V3 branches (14)
2. **W03** session orientation and rule-regime resolution (13)
3. **W04** troubleshooting and recovery triage (11)
4. **W05** evidence-labelled registers and comparisons (11)
5. **W08** conflicting standing instructions (11)
6. **W09** `PROJECT_STATE.md` growth (11)
7. **W02** validate, commit and push to the right branches (11)
8. **W13** regenerating derived artefacts (10)
9. **W01** stamping SHAs into tracking rows (10)
10. **W07** writing tracking records (10, **keep manual**)

## 4. Workflow detail

### W06 · Pre-commit scope, secret and rule check (V3) · Class B, folded into a skill · 14 · P1
- **Project and evidence:** `design/casaray-v3/CLAUDE.md`, *Workflow* step 3, lists five things to confirm before each commit: entity IDs, themes and languages and widths, **no file changed outside `design/casaray-v3/`**, no secrets, correct branch. Two are scripted (`verify_entities.py`, the Playwright harness); the rest are by eye. 16 non-merge commits on this branch since 2026-09-25 [M].
- **Frequency:** 16 in 17 days, about 6–7 per week while the sprint is active [M].
- **Manual steps:** `git branch --show-current`; `git status`; `git diff --name-only` and compare to the allowed path by eye; scan the diff for credentials by eye; recall the push target.
- **Effort:** about 3 minutes per commit [A].
- **Automation:** `orient.py --scope` classifies every changed path against the branch's regime, names anything outside, flags protected paths, and runs a minimal credential scan on added lines. Read-only.
- **Savings:** about 20 min/week while V3 is active [A].
- **Error risk if skipped:** high. A write outside the V3 tree is a hard-boundary breach, and the V3 rules require the owner's approval for it.
- **Complexity:** low.

### W03 · Session orientation and rule-regime resolution · Class A · 13 · P1
- **Project and evidence:** root `CLAUDE.md` (21,080 B), `design/casaray-v3/CLAUDE.md` (21,147 B), `PROJECT_STATE.md` (182,699 B), `MAINTENANCE.md` (9,126 B) [M]. The V3 file contains a section, *Relationship to the root rules*, that exists only to say which of two contradictory push rules applies. Commit `58c7fdb` ("allow isolated specialist agent branches") shows the rules moving.
- **Frequency:** at least 21 distinct commit-producing sessions: 19 on this branch across 6 of the last 8 ISO weeks, 2 more on the recovery branch [M, lower bound: a read-only session leaves no trailer].
- **Manual steps:** fetch; branch; status; log; locate the right `CLAUDE.md` files; decide which push rule applies; decide which gate applies; note protected paths; note whether the clone is shallow.
- **Effort:** about 6 minutes of commands and reading per session [A].
- **Automation:** `session-orient` skill plus `orient.py` (read-only, no network). It resolves branch → regime → push targets, forbidden targets, gate, protected paths, and reports instruction-file sizes and contradictions it can see.
- **Savings:** about 16 min/week [A] (6 min × the measured 2.6 sessions/week lower bound).
- **Error risk if skipped:** high. The two rule sets disagree on where a push may go.
- **Complexity:** moderate.
- **What it deliberately does not do:** it does not decide whether `PROJECT_STATE.md` is read in full. That is contradicted inside the repository's own rules (section 5, C5), so it is reported, not resolved.

### W04 · Troubleshooting and recovery triage · Class A · 11 · P1
- **Project and evidence:** six distinct episodes in this checkout [M]: deploy `git fetch` failing under automation (`DEPLOY_AUTH.md`); the apply step not writing (`DEPLOYMENT_BLOCKERS.md`, 2026-08-30); `kiosk_mode` having no effect (`DR-015`, `d22ce8e`); the core-check running after deploy rather than before (`3c40913`); a rollback bug found by the disk report (`032a705`); and a kiosk lockout whose configuration was removed (`fc208cd`; "lockout" is the commit's own word, the incident itself is inferred). The seventh episode, loss of configuration, is on the recovery branch below. A keyword filter matches 90 of 362 commits, but that is an upper bound because it includes feature commits that merely mention kiosk mode.
- **The recovery branch** (`recovery/phase0-diagnostics`, read by API): 9 commits in 2 sessions, 2026-09-26 → 2026-10-12 [M]. Counting the 9 commit messages, the same safeguards recur: a backup before anything changes (5 of 9), typed confirmation before apply (4 of 9), automatic rollback if Core does not return (5 of 9), no hash, token, key or password in output (7 of 9), and testing against a simulated host or Home Assistant's own `check_config` (6 of 9). One script was **withdrawn** after it was found to be wrong. The latest commit is a plan marked "planning only, nothing run". Backup identifiers are deliberately omitted from this document.
- **Frequency:** 7 episodes in 7.3 weeks, about one per week [M].
- **Manual steps:** decide which host-side diagnostic answers the question; ask the owner to run it (this environment cannot reach `/config`); interpret the pasted output; decide whether the next step is read-only; draft a recovery plan with approval points; write up the incident.
- **Effort:** about 20 minutes per episode [A].
- **Automation:** `recovery-triage` skill plus `triage_plan.py`: symptom → ordered read-only checks (existing scripts, run by the owner on the host), a list of what must *not* be done, and an incident record skeleton. It plans and never executes.
- **Savings:** about 20 min/week, bursty [A].
- **Error risk if done badly:** the highest of any item. Recovery scripts here have touched authentication and the configuration file, both on the approval boundary.
- **Complexity:** moderate.

### W05 · Evidence-labelled registers, comparisons and reports · Class A · 11 · P1
- **Project and evidence:** in the repo, `docs/entity_inventory.md` (6 commits), `design/casaray-v3/ENTITY_MAPPING.md` (5), `LIVE_VERIFICATION_QUEUE.md` (78) [M]; the repo already forbids inventing an entity ID and requires `no source entity` where none exists. In Drive, the 2026-10-09 pack alone contains four register-type documents (evidence and verification; case; decision and accountability; commitments and follow-up), and its 11 numbered documents were created within 21 minutes; an earlier numbered PDF pack dates from 2026-10-07 [M, metadata only]. Your brief states the same discipline: never infer equipment ownership or measurements, use placeholders and explicit unknowns.
- **Frequency:** F is capped at 3 although 15 events match: 11 are HA documents that already have conventions, and the non-HA side is metadata only.
- **Manual steps:** build a table; fill what is known; decide for each cell whether it is observed, reported, assumed or unknown; chase the source; avoid filling blanks with plausible values.
- **Effort:** about 10 minutes per register session, 2 per week [A, weakest estimate in this document].
- **Automation:** `provenance-register` skill plus `check_register.py`, a linter for Markdown and CSV registers that fails on blank cells, unsourced "verified" rows, duplicate IDs, and non-`UNKNOWN` values in ownership or measurement columns that lack a verified or reported source.
- **Savings:** about 20 min/week [A].
- **Error risk if skipped:** a plausible invented measurement in a report.
- **Complexity:** moderate.
- **Reuse, not duplication:** `improve-system/references/evidence-rules.md` covers *entity* verification; this skill covers everything else and points back to it.

### W08 · Conflicting and duplicated standing instructions · Class F · 11 · P2
See section 5 for the seven conflicts and four duplications. Proposed fix is a
five-line precedence note in the root `CLAUDE.md`; **not applied**, because it
edits a protected instruction file.

### W09 · `PROJECT_STATE.md` growth · Class F · 11 · P2
- **Evidence [M]:** 182,699 B, the largest file in the repository; touched by 106 non-merge commits of 362 (29%), 97 of them in August; it holds 8 `### Superseded` blocks, all stacked from line 2582 onward. The root rules require reading it at the start of every session.
- **Proposal:** move the superseded blocks to `archive/`, which `CLAUDE.md` already tells sessions not to read end to end. **Not applied:** it edits a coordination file other routines depend on, and the V3 rules say not to edit it from V3.
- **Estimated effect:** roughly 45k tokens per session if the file is read in full [A: 4 bytes per token]. The saving is unknown until the archive is cut, so it is not counted in section 7.

### W02 · Validate, commit, push to the right branches · Class F · 11 · P2
- **Evidence:** 16 occurrences recorded on one day [R]; 61 commits mention `ha_validate` in the body [M]. `CLAUDE.md` documents the failure mode of forgetting the second branch.
- **Not proposed for build.** It ends in `git push`, which the `automate` skill already classes as behind the owner, and under the V3 rules the push target is a *different* single branch. The hazard it addressed (pushing to the wrong place) is what W03 now reports at session start. No script is proposed.

### W13 · Regenerating derived artefacts · Class B · 10 · P3
- **Evidence [M]:** five generators, each run by hand: `gen_entity_table.py` (ENTITY_MAPPING, 5 commits), `capture_comparison.cjs` (COMPARISON, 2), `test_and_capture.cjs` (`test_results.json`, 5), `procmem.py registry` (5), `build_render_fixture.py` (2). Only the fixture has a drift check (`ha_validate.sh`).
- **Proposal:** one read-only `--check` that reports which derived files are older than their sources. Not built.

### W01 · Stamping a commit SHA into tracking rows · Class B · 10 · P3
- **Evidence [M]:** 70 `docs: stamp` commits of 362; 13 in the last 30 days; each is one file, one line (`+1/-1`); one correction commit (`86ec579`) after a rebase changed the hash, which is the documented failure.
- **The placeholder is not a token.** Sampled stamp diffs replace a bare `—` in a *commit* cell with the backticked SHA (`cb9c684`, `d182251`, `7f8e07c`). `—` appears everywhere, so a script must locate the row by its ID (for example `CVA-004`) and the column by header.
- **Specification, not built.** `scripts/stamp_sha.py --rows CVA-004,CR-318 [--sha SHA] [--apply]`: dry-run by default and prints the diff; refuses unless `git merge-base --is-ancestor SHA HEAD` (this alone catches the rebase trap); refuses if a named row is missing or its commit cell is not exactly `—`; edits only the tracking documents named in `CLAUDE.md`; never commits.
- **Blocked on regime:** the V3 rules say tracking documents are not edited from V3. It is useful only on the `ha-deploy` line.

### W07 · Writing tracking records · Class G · 10 · keep manual
`LIVE_VERIFICATION_QUEUE.md` 78 commits, `DASHBOARD_ISSUES.md` 57, `DASHBOARD_PROGRESS.md` 49 [M]. This is the largest manual effort in the repository and is **deliberately kept manual**: `automate/references/patterns.md` §8 argues the value is the judgement about what is worth recording, and a generated row would be filler. I agree. Only the numbering is mechanical, and `scripts/next_id.py` already covers it.

### W19 · Comparing a live render with the approved mockup · Class A · 9 · not built
Recorded 3 times at 40 minutes each [R], the largest per-occurrence cost in the process memory. It needs photographs of the live iPad, which this environment cannot obtain, so a skill could not be tested here. Left as a candidate.

### W14 · Two overlapping entity verifiers · Class F · 8
`scripts/reconcile_entities.py` (dashboards against the export) and `design/casaray-v3/tools/verify_entities.py` (V3 prototype and mapping against the same export) answer the same question for different inputs. Consolidating them touches two existing tools; proposed, not done.

### W15 · Defects in existing tooling · Class F · 8
Five findings (D1 to D5); see section 5. None fixed. D5, `improve-system` having no notion of V3, is the one with consequences.

### W18 · Entity-inventory sync with live state · Class F · 7
The `automate` patterns file already records this as a known gap: the live connector returns friendly names, the export returns IDs, and nothing bridges entities that share a name. Not solvable by a new script.

### W10 · Document-pack production · Class C · 7 · needs an exemplar
Two numbered packs in nine days [M, metadata only], with a consistent scheme: a number prefix, a status suffix such as "Draft v0.1" or "Ready to Use", and a Google Doc plus a .docx copy of at least one item in different folders. Two occurrences is not a pattern under this repository's own bar. **To build a template I need one finished pack to read, with your permission, and your say on which parts are reusable.** Existing skills (`docx`, `doc-coauthoring`, `operations:process-doc`) cover the mechanics.

### W16 · Session-branch sprawl · Class G · 6
24 `claude/*` heads on the remote, plus 7 others (`ha-deploy`, `main`, the V3 branches, `autonomous/casaray-dev`, `recovery/phase0-diagnostics`) [M]. Deleting remote branches is irreversible and outside this brief. Reported only.

### W17 · PR and branch flow · Class G · 5
Four PRs ever [M]. #1 (closed) and #3 (open draft) target `ha-deploy`; #2 (closed) targeted `main`; #4 went from a specialist branch into this branch, which is the V3 pattern. See conflict C2 for the open question about opening a PR from this branch.

### W11 · Purchasing / quote comparison · [N]
Three quote-related files in Drive (two quote-request documents, one PDF quote) [M, titles only]. No comparison was found. The existing `operations:vendor-review` skill already does cost and recommendation work; use it. `provenance-register` adds the guard against inventing figures. No new skill.

### W12 · Equipment register · [N]
No register found. The closest items are two faulty-equipment report **forms** (templates). I have not inferred what equipment exists, who owns it, or any rating. `provenance-register` ships a register template with `UNKNOWN` as the default for every ownership and measurement cell.

## 5. Instruction stack: duplication, conflicts, and defects

Seven layers shape a session here: your standing preferences; root `CLAUDE.md`;
`design/casaray-v3/CLAUDE.md`; `PROJECT_STATE.md`; `MAINTENANCE.md`; the
`improve-system` skill; and the session harness. The four repository documents
alone totalled about 234 KB [M] when measured (21,080 + 182,699 + 21,147 + 9,126
bytes). Root `CLAUDE.md` has since grown to 22,717 B with the standing rule
below (C8), so about 236 KB; every other figure in this document was measured
before that merge.

### Conflicts

| # | Topic | The sources say | Status |
|---|---|---|---|
| C1 | Push target | Root: push to `ha-deploy` **and** `claude/ha-dashboard-upgrades-wui7ig`. V3: `casaray-v3-design` only, never `ha-deploy`. Session: develop on `casaray-v3-design`. | **Settled** by the V3 file's *Relationship to the root rules*; `session-orient` prints the answer. |
| C2 | Opening a PR after a push | Your preferences: do not open one unless useful or requested. The session harness: always open a draft PR. V3: PRs run specialist branch → `casaray-v3-design`; the integrator controls this branch. | **Unsettled.** I did not open a PR from the integration branch to `main` and say so in the summary. |
| C3 | Tracking documents | Preferences and root: keep inventory and tracking documents current, stamp SHAs. V3: V3 records history in `DECISIONS.md` and does not edit them. | Settled for V3; root applies on V2 branches. |
| C4 | Reload or restart of Home Assistant | Preferences: prefer reload over restart after validating. V3: no deploy, sync, reload or restart. `MAINTENANCE.md`: reload and restart are out of scope. | Most restrictive wins. |
| C5 | Reading `PROJECT_STATE.md` | Root step 1: read in full. Root step 3 and the file's own *Context Loading Strategy* (line 250): load selectively. | **Unsettled, and your decision.** Full read is about 45k tokens [A]. |
| C6 | Autonomy | Preferences: continue without asking. V3: show the owner a render and get approval at each design milestone. | Settled for V3. |
| C7 | Files outside the V3 tree | V3: needs Ray's explicit approval. This task names three new root files and new skill directories. | Treated as that approval for those named files only; nothing else outside the tree was touched. |
| C8 | When to ask the owner a question | Root `CLAUDE.md`, *Standing Rule: Context First, Questions Last*, added by PR #6 and **merged while this audit was in progress** (2026-10-12): search the records first, ask only for what is genuinely missing or needs authorisation, and a conflict between governing instructions is *not* a safe ambiguity. | **Consistent** with how the pilots treat C2 and C5 (report, do not resolve). It changed two things in the pilots, made in a follow-up commit: `recovery-triage` no longer asks where to file a record, and `provenance-register` maps its statuses onto the rule's *confirmed, estimated, outdated, unknown* and gained `--max-age-days` so "outdated" can be told apart from "confirmed". |

### Duplications

The rule *never invent an entity ID* appears in four places (preferences, root, V3, `improve-system`). *Draw unavailable, never hide it; keep a third branch* appears in three. *Push to both branches* appears in three (root, `improve-system`, process memory). The protected-path list appears in three (`MAINTENANCE.md`, the preferences' approval boundary, V3's hard boundaries). Some duplication is deliberate, since each file is read in a different context. The harmful kind is the kind that diverges, which is C1, C2 and C5.

### Defects in existing tooling

None of these was fixed, because each is an existing production file.

| # | File | Finding | Impact |
|---|---|---|---|
| D1 | `AUTOMATION_REGISTRY.md` | First ~64 bytes are corrupted in four of its five committed revisions (every one since `55631a1`): line 1 reads `wrote AUTOMATION_REGISTRY.md  (9 in place, 3 candidates)` and the header is truncated. Cause: the registry was generated with the command's stdout redirected into the file it writes; `cmd_registry` writes the file, then its own `print()` overwrites the start through the shell's descriptor. | Cosmetic; the generated header and title are lost. Fix: print the status line to stderr, or refuse when stdout is the target. |
| D2 | `scripts/ha_validate.sh` | Lines 182–316 are a truncated second copy of the preamble and eight sections, beginning mid-statement with ` || true)`. `bash -n` exits 2. Present since the validator-preamble commits of 2026-09-25 (`7309bd8`, `18a4e5d`); I did not bisect further. | Latent. The gate runs because the first copy always reaches an `exit`. Any edit that removes or moves that `exit` exposes a syntax error in the validation gate. |
| D3 | `scripts/next_id.py` | `--help` is read as an ID prefix and prints `--HELP-001`. | Minor; the output looks like a valid ID. |
| D4 | session start | Every fresh clone is shallow: 59 of 362 commits were visible until `--unshallow`. | Any frequency analysis from a fresh clone undercounts by 6×. `session-orient` flags it. |
| D5 | `.claude/skills/improve-system/` | The skill never mentions V3 (0 matches across its `SKILL.md` and references, and in `automate`). Its step 1 fetches `ha-deploy` and its commit protocol pushes to `ha-deploy` **and** `claude/ha-dashboard-upgrades-wui7ig`. Its triggers include "carry on", "next" and "keep going". | **A hazard on this branch.** Followed literally on `casaray-v3-design`, the skill directs a push the V3 rules forbid. `session-orient` now says to run it first and prints the forbidden targets, but that depends on being run first. Proposed fix: a one-line regime check in `improve-system` step 1. **Not applied**, because it edits an existing skill. |

## 6. Already automated, reviewed and reused

| ID | Workflow | Covered by | Notes |
|---|---|---|---|
| A01 | Splice dashboard sections | `scripts/dashboard_edit.py` | recorded 8× |
| A02 | Render cards, populated and dark | `improve-system/scripts/render_cards.py` | recorded 6× |
| A03 | Structural diff against a git ref | `improve-system/scripts/preserve_check.py` | recorded 2× |
| A04 | Verify a change before pushing | `scripts/verify_change.sh` | recorded 5× |
| A05 | Build a render fixture | `scripts/build_render_fixture.py` | recorded 3×, 3 failures |
| A06 | Live screenshot capture | `scripts/casaray_capture.sh` | recorded 2×; must run where the instance is reachable |
| A07 | Next free tracking ID | `scripts/next_id.py` | see D3 |
| A08 | Entity existence and duplicates | `reconcile_entities.py`, `audit_duplicate_entities.py` | see W14 |
| A09 | Add a gate and negative-test it | `improve-system` skill | recorded 4× |
| A10 | Deploy with rollback | `casaray_safe_deploy.sh`, `casaray_rollback.sh` | host-side; off-limits to new automation |
| A11 | Validation gate | `scripts/ha_validate.sh` | see D2 |
| A12 | Device-control guard | `scripts/deny_device_control.py`, PreToolUse hook in `.claude/settings.json` | enforced by tool name |

The `automate` skill already provides the discovery, scoring and registry
mechanism you asked for. **This audit did not create a competing one.** What
it adds is cross-source evidence (git history, GitHub, Drive metadata), the
A–G classification, and the instruction-stack review. Folding the
classification into `automate` would be an improvement to an existing skill
and needs your approval.

## 7. Time saved per week

**Measured: zero minutes.** Nothing accessible records how long work took.
What is measured is the *count* of repetitions, and every minute figure below
is an assumption multiplied by one.

| Skill | Measured input [M] | Assumed minutes saved per use [A] | Assumed weekly saving [A] |
|---|---|---|---|
| `session-orient` | ≥ 2.6 commit-producing sessions per week (19 in 7.3 weeks) | 6 | about 16 min |
| `session-orient --scope` | about 6.6 V3 commits per week while the sprint runs | 3 | about 20 min while V3 is active, 0 otherwise |
| `recovery-triage` | about 1 incident episode per week (7 in 7.3 weeks) | 20 | about 20 min, bursty |
| `provenance-register` | none directly (Drive evidence is metadata only) | 10 × 2 per week | about 20 min, **weakest estimate** |
| **Total** | | | **about 56–76 min/week, assumed** |

Proposed but unbuilt items would add roughly: W01 about 9 min/week (13 stamps
in 30 days × 3 min [A]); W13 about 5 min/week [A].

## 8. What would unlock the next layer

| To cover | I need |
|---|---|
| Workplace documentation | one finished document pack, read with your permission, and which parts repeat |
| Equipment registers | an existing register (or a column list) and what counts as verified |
| Purchasing comparisons | one past comparison, and the criteria you weigh |
| Household projects | which project folders or repos are in scope |
| ChatGPT-derived repetition | an export file placed where I can read it, or a connector |
| A true time baseline | a week of rough timestamps, or permission to treat the commit rate as the clock |

## 9. Decisions for you

1. **C5:** read `PROJECT_STATE.md` in full each session, or by its own loading strategy?
2. **C2:** should the integration branch ever open a PR to `main`, or never?
3. Approve a precedence note for the root `CLAUDE.md` (W08).
4. Approve archiving the superseded blocks of `PROJECT_STATE.md` (W09).
5. The pilot skills exist on `casaray-v3-design` only. The V3 rules forbid merging into `ha-deploy`, so sessions on that line will not see them. Copy them across, or leave them V3-only?
6. Fix D1–D3 (small, in existing files), or leave?
7. **D5:** add a regime check to `improve-system` step 1 so it cannot direct a V3 session to push to `ha-deploy`? Until then, run `session-orient` first.
