# Skill validation report

Validation of the three pilot skills added on 2026-10-12: `session-orient`,
`recovery-triage` and `provenance-register`. Companion files:
`WORKFLOW_AUDIT.md` (evidence and scoring) and `SKILL_REGISTRY.md` (what exists).

**Result: all checks that this environment can run pass.** 158 automated checks,
the installed validator on all three skills, and the repository's own gate. The
list of things that could **not** be tested is in section 5; read it before
relying on the pilots.

Environment: Python 3.13.16 · git 2.43.0 · PyYAML 6.0.1 · Claude Code 2.1.296.
Branch `casaray-v3-design`, HEAD `d4d6d42` when validated.

## 1. Results against the brief

| # | Requirement | Result | Evidence |
|---|---|---|---|
| 1 | Skill discovery and frontmatter against the installed specification | **Pass** | The installed validator (`skill-creator/scripts/quick_validate.py`) returns "Skill is valid!" for all three. Keys used: `name`, `description`, `metadata` only. Descriptions are 891, 980 and 912 of 1,024 characters, with no angle brackets and no `: ` that would break the YAML. **The harness listed each skill in its own live skill list as soon as the file existed** (`session-orient`, `recovery-triage`, `provenance-register`), and re-read `session-orient`'s description within the same session after an edit |
| 2 | Non-destructive tests with fixtures or dry-run | **Pass** | `orient.py --selftest` **74/74**, `triage_plan.py --selftest` **50/50**, `check_register.py --selftest` **34/34**. Fixtures are a throwaway git repository, 14 sample symptom reports, and five files of fictional register data. The refusal paths are tested, not just the happy ones (section 2) |
| 3 | No existing skill or instruction overwritten | **Pass** | `git diff` is empty; nothing staged; the only changes are **22 new untracked files** (this report included); HEAD still `d4d6d42` when checked. `.claude/settings.json`, `CLAUDE.md`, `MAINTENANCE.md`, `PROJECT_STATE.md`, `AUTOMATION_REGISTRY.md`, `process-memory.json`, `automate/`, `improve-system/`, all dashboards, themes, packages and deployment scripts are unmodified |
| 4 | No duplicate capability or conflicting trigger | **Pass after one fix** | 140 distinct skill names compared by shared phrases. One real collision found and fixed: "carry on" was claimed by both `session-orient` and `improve-system`. Section 3 |
| 5 | Output matches existing documentation conventions | **Pass** | ISO dates as in the other root documents; British spelling (the only US-spelled strings are a filename, `authorized_keys`, and a YAML key, `license`); tables and sentence-case headings as in `AUTOMATION_REGISTRY.md`; no emoji, tabs, CRLF or trailing whitespace; no private identifiers from the Drive or branch material read during discovery (searched for by pattern). `bash scripts/ha_validate.sh` exits 0 with the files present: no credential-shaped literals, no protected path touched |
| 6 | No live Home Assistant settings, credentials, branches or deployment scripts modified or executed | **Pass** | Section 4 lists every operation performed outside the repository |
| 7 | Successes, failures, limitations and remaining decisions recorded | **Done** | Sections 2 to 6 |

## 2. What each test suite proves

### `session-orient` · 74 checks

| Area | Checks | Proves |
|---|---|---|
| Rule-set resolution | 8 | the six branch shapes resolve correctly, including detached HEAD and `main` → unknown |
| Path classification | 14 | in-scope, outside, approved, and blocked paths; **an approval flag never clears BLOCKED** |
| Porcelain parsing | 1 | renames and paths with spaces |
| Credential scan | 8 | finds a JWT, a GitHub token, a private-key header, and a credential assignment; ignores `!secret` references, placeholders, prose, and code that only contains the words; **never returns the matched text** |
| Read-only wrapper | 14 | `push`, `commit`, `fetch`, `checkout`, `reset`, `branch <name>`, `branch -D`, `config`, `remote add`, `diff --output`, `add`, `stash` and `tag` are each **refused**; `branch --show-current` is allowed |
| Scope, end to end | 7 | in a real temporary repository: a verdict per file, a credential found in an untracked file, overall fail, an approval flag that does not clear BLOCKED or credentials, then a pass once the bad files are removed |
| No side effects | 4 | the worktree is byte-identical and the **git index is untouched** after both scope and orientation runs |
| Orientation report | 5 | the regime is read from the real branch, a simulated branch is flagged as simulated, the push-rule and `PROJECT_STATE.md` contradictions are detected, and stale rules are announced in the text |
| Drift detection | 3 | changed source text is reported; an unreadable source is reported once; line-wrapped phrases still match |
| Exit codes | 10 | through `main()`: 0 for settled branches, 3 for unsettled ones, 2 for bad `--base` |

### `recovery-triage` · 50 checks

| Area | Checks | Proves |
|---|---|---|
| Classification | 14 | each symptom class is recognised from realistic wording, including a curly apostrophe; unrelated text lands in `unclassified` rather than being forced into a class |
| Structure | 9 | symptom IDs are unique; every check has a valid location; **no check anyone would run contains a mutating verb or a deploy, sync, restore or onboarding script**; ASK checks are phrased as questions; recovery steps are all marked as needing approval; owner-only symptoms open with STOP; routed symptoms carry no checks of their own; every operational symptom says what not to do; every host check names a source file |
| Cited files | 4 | every repository file the data cites exists, and the three reference documents exist, so the symptom table cannot quietly rot |
| Sync-status words | 4 | all four words explained; a bogus word refused; `out_of_sync` described as expected after a push; `missing_live` points at the owner-only symptom |
| Rendering | 4 | owner-only plans say STOP; routed plans name the other skill and stop; the rollback is listed as not run; every plan says it executes nothing |
| Incident template | 13 | ten required sections, substitution of symptom and date, `UNKNOWN` defaults, "NOT RUN, NEEDS APPROVAL" |
| **Cannot act** | 2 | a walk of the script's own syntax tree finds **no process, network or file-writing capability** outside the test function; running a plan creates no files |

### `provenance-register` · 34 checks

| Area | Checks | Proves |
|---|---|---|
| Parsing | 3 | escaped pipes; tables inside code fences are skipped; date formats |
| Fixtures | 10 | the good files pass with no findings; each bad file produces exactly its expected error codes (E0 to E7) and no others |
| The owner's rule | 7 | **an ASSUMED owner or rating is refused (E7)**; the same row with `UNKNOWN` passes; a REPORTED value with a source is allowed; a REPORTED value without one is refused; "about 2" in a rating cell is refused |
| Reporting | 5 | ASSUMED rows warn but do not error, strict mode turns that into a failure, duplicate IDs are caught case-insensitively, JSON round-trips, and the report says "a pass does not mean any value is true" |
| Templates | 6 | all three templates exist and lint with no errors and no warnings |
| No side effects | 3 | linting changes nothing; an unsupported file type is refused; **a spreadsheet CSV with a byte-order mark and CRLF line endings lints clean** |

Additional runs outside the suites, all passing: five representative commands,
each run twice, give byte-identical output and leave the worktree unchanged
(idempotence); each tool runs correctly from a directory that is not a
repository; the `--template` output of every template, written to a file, lints
clean; and seven negative command-line cases each exit 2 with a clear message.

## 3. Trigger and capability overlap

**Method.** The descriptions of all 140 distinct skill names on this machine (the
project, the account-synced skills and the plugin skills) were compared for shared
two- and three-word phrases, and 16 realistic requests were scored against every
description with TF-IDF cosine similarity. The scripts lived in the session
scratch area and are not committed.

**Findings.**

1. **"carry on" collided.** `improve-system` lists it as a trigger, and my first
   draft of `session-orient` claimed it as well. Removed from `session-orient`, and
   a hand-off section added: run `session-orient` first, then continue with
   `improve-system` only if the rules turn out to be V2.
2. **`improve-system` has no notion of V3** (finding D5 in the audit). Not edited,
   because it is an existing skill. This is the more important result: it is why
   the hand-off matters.
3. The remaining phrase overlaps are boundary statements ("not for ... finding
   repeated work"), which point *away* from each other. They are intended.
4. `provenance-register` shares no trigger phrase with any other skill. It sits
   next to `operations:vendor-review` for quote comparison; the registry says to
   use the vendor skill first and this one to check the figures.

**Routing probes: 16 of 16 correct in substance** (15 on the exact name; the 16th
resolved to `vendor-review`, the un-prefixed name of `operations:vendor-review`).
Three probes were aimed at `session-orient`, five at `recovery-triage`, two at
`improve-system`, three at `provenance-register` (one also acceptable to the
vendor skill), and one each at `automate`, `ha-dashboard-design` and
`operations:vendor-review`. Similarity scores were low in absolute terms (0.09 to
0.47), so the ranking is the evidence, not the margin. `session-orient` ranked
second, behind `automate`, for "what do I keep doing by hand", which is the right
order.

**This is a lexical proxy, not Claude's real selection.** It shows the
descriptions do not contradict each other. It does not show that Claude will pick
the right skill on a live request. See section 5.

## 4. Operations performed outside the repository

Everything that touched anything, so the claim in row 6 can be checked:

| Operation | Effect |
|---|---|
| `git fetch --unshallow origin casaray-v3-design` | deepened local history from 59 to 362 commits; **no branch moved, no ref changed**; the only state change is the clone's shallow marker |
| `git ls-remote` (four invocations) | read-only |
| Google Drive: one `list_recent_files` (30 items) and two title searches | **metadata only. No document was opened.** Nothing created, modified, shared or trashed. Titles are not reproduced in any committed file |
| GitHub API: `list_pull_requests`, `list_commits` ×2 | read-only; one extra branch read by API, not checked out |
| `bash scripts/ha_validate.sh` | the repository's validation gate, which its header describes as read-only. Run once. It is not a deployment script; it ran no sync, deploy or restart |
| Home Assistant | **no `Home_Assistant` tool was called at all**, read or write |
| Credentials | `~/.claude/.credentials.json` was never opened. No token, password or key was printed, stored or committed |
| Deployment scripts, recovery scripts, automations | none executed. Of the host scripts (`scripts/casaray_*`, `deploy_*`), none was run; they were only read |
| Files written | the 22 new files in the repository; scratch scripts in the session scratch directory. A `__pycache__` folder created inside one skill by a validation import was removed |

## 5. Defects found in my own work

Found by running the tools against real data and the installed validator, not by
reading. Each is fixed and now covered by a test.

| # | Defect | Found by | Fix |
|---|---|---|---|
| 1 | `orient.py` warned that the V3 rules were stale when they were not: the phrase it looked for wraps across two lines in the source file | running it on the real repository | whitespace-insensitive matching; test added |
| 2 | The credential rule flagged ordinary code (`tokens = raw.split(...)`) | same run | rule narrowed to `key: value`, quoted literals and long bare values; 14 positive and negative cases |
| 3 | The tool flagged its own test fixtures | same run | fixtures built by concatenation so no source line is assignment-shaped |
| 4 | An unreadable source file was reported once per needle | self-test | once per file; test added |
| 5 | Branches needing confirmation (`claude/*`, `recovery/*`) printed "NOT SETTLED" but exited 0 | review of the exit-code design | exit 3; 10 exit-code tests |
| 6 | `.storage/` was blocked only at the repository root | review | blocked at any depth (deliberately stricter than the gate) |
| 7 | `check_register.py` crashed on Python 3.13: a second `(?i)` flag mid-pattern | first run | single flag |
| 8 | Vague-word warnings fired on "about" and "likely", ordinary prose | reading the output | removed from the list |
| 9 | A row with an invalid status was not counted anywhere (7 rows, 6 counted) | reading the output | `INVALID` counter |
| 10 | `N/A` cells were counted as open questions | reading the output | only `UNKNOWN` counts |
| 11 | A spreadsheet CSV with a byte-order mark failed with a false "missing ID column" | reviewing likely inputs | `utf-8-sig`; **negative test proved the old behaviour failed on the same file** |
| 12 | `provenance-register`'s `description` contained `only: uploading`, which is invalid YAML and would stop the skill loading | the installed validator | reworded |
| 13 | "carry on" claimed by two skills | the overlap scan | section 3 |
| 14 | Wording differed between the plan footer (OBSERVED, INFERRED) and the incident template (VERIFIED, ASSUMED) | reading both | aligned to one vocabulary |
| 15 | Four of my test assertions were wrong: a fixture missing a file, a check that asserted nothing, a drift test that passed for the wrong reason, and a dangerous-verb scan that flagged questions | self-test failures and review | each made a real assertion |

Items 12 and 7 are the instructive ones: a reader could not have seen either, and
both would have broken the skill silently for the next person to use it.

## 6. Limitations: what was not tested

1. **Real triggering.** Whether Claude selects the right skill on a live request is
   unmeasured. The harness did list all three, and the lexical probes agree, but
   neither is the selector. `skill-creator` ships a description-optimisation loop
   (`run_loop.py`) that would measure this with model calls; I did not run it
   because it spends model calls and was not asked for.
2. **No end-to-end use.** No person has yet used these skills on a real task.
3. **The host scripts were not run, by constraint.** `recovery-triage` cites
   `sh /config/casaray/...` paths taken from `docs/CASARAY_AUTOMATION.md` and the
   scripts' own headers; the host may differ. Whether `sensor.casaray_sync_status`
   currently exists is unknown (no Home Assistant call was made); the plan says so
   and treats a missing sensor as no information.
4. **The rule table is a snapshot of 2026-10-12.** The drift check watches four to
   five phrases per rule set, not every rule.
5. **`orient.py` sees git-visible state only.** It cannot see the remote, ignored
   files, or the live house. `--approved` is the caller's assertion and cannot be
   verified. The credential scan is minimal and covers only lines about to be added.
6. **`check_register.py` is heuristic.** Sensitive columns are found by an English
   header pattern; one table at a time; no multi-line cells; spreadsheets must be
   exported to CSV; `.xlsx` is unsupported. No real register was available to
   test against.
7. **Platform coverage:** Python 3.13.16 and git 2.43.0 on Linux only.
8. **Time saved is assumed.** Nothing accessible records how long work took
   (`WORKFLOW_AUDIT.md`, section 7).
9. **Non-HA domains rest on metadata.** Drive was read for titles and dates only.
   Workplace documentation, equipment registers, purchasing comparisons and
   household projects therefore have no dedicated skill; `provenance-register` is
   the generic guard for them, and it needs an exemplar before it can be tuned.

## 7. Remaining manual decisions

From `WORKFLOW_AUDIT.md`, section 9, plus those this validation raised:

1. **C5:** read `PROJECT_STATE.md` in full each session, or selectively?
2. **C2:** may the integration branch open a PR to `main`? (None was opened here.)
3. Approve a precedence note for the root `CLAUDE.md` (W08).
4. Approve archiving the superseded blocks of `PROJECT_STATE.md` (W09).
5. **Where the pilots live.** They exist on `casaray-v3-design` only; the V3 rules
   forbid merging into `ha-deploy`, so sessions on that line will not see them.
6. Fix D1 to D3 in the existing tooling, or leave.
7. **D5:** add a regime check to `improve-system` step 1. Until then, run
   `session-orient` first.
8. Wire `orient.py` as a `SessionStart` hook (edits `.claude/settings.json`).
9. Run the description-optimisation loop to measure real triggering.
10. Provide an exemplar document pack, register or comparison so the non-HA
    workflows can be built from evidence instead of metadata.

## 8. How to reproduce

```sh
QV=$(echo ~/.claude/skills/synced/*/skill-creator/scripts/quick_validate.py)
for s in session-orient recovery-triage provenance-register; do
  python3 -I "$QV" .claude/skills/$s
done
python3 -I .claude/skills/session-orient/scripts/orient.py --selftest
python3 -I .claude/skills/recovery-triage/scripts/triage_plan.py --selftest
python3 -I .claude/skills/provenance-register/scripts/check_register.py --selftest
bash scripts/ha_validate.sh        # the repository's gate; read-only
python3 -I .claude/skills/session-orient/scripts/orient.py --scope
```

`quick_validate.py` is from the account-synced `skill-creator` skill, not the
repository. The routing and overlap scripts are not committed. If you want them
kept, they would belong in `scripts/`, and that is a decision for you.
