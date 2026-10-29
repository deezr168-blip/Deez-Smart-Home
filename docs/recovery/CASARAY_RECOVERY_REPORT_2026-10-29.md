# CasaRay historical recovery report — 29/10/26

**Phase 0 only. Nothing has been implemented.** This report is investigation
and a recommendation. No dashboard file, theme, package or Home Assistant
setting was changed to produce it, and no branch was moved, rewritten or
deleted. The recovery branch it proposes does not exist yet. It waits for the
owner's approval of the recovery point (section 12).

Dates are UTC unless marked AEST/AEDT. Commits authored under the owner's
account carry a `+1000` offset and no session trailer, so they are labelled
**owner-account** below. That records whose account made them, not which tool
did.

Evidence labels used throughout:

| Label | Meaning |
|---|---|
| **[O]** | Owner-observed: a photograph or a statement from the owner, recorded in the repository |
| **[V]** | Validated in this session, offline, by a command whose output is summarised here |
| **[R]** | Recorded in a repository document or commit message, not re-checked here |
| **[I]** | Inferred. Stated as an inference, never as a fact |

---

## 1. Summary

1. **The CasaRay dashboard YAML was never the broken part.** The problems
   that began on 24–25/09 were in the Home Assistant installation around it:
   a kiosk-mode lockout, and then the loss of `configuration.yaml`,
   the password store and `core.config` during a recovery attempt. CasaRay's
   file survived and its lineage is unbroken. Every later version keeps the
   same 28 views, 405 entities, 28 navigation targets and 7 service calls,
   and nothing was lost at any step [V].
2. **Recommended recovery point: `d22ce8e`** (18/09 17:23). It is the last
   build with direct owner evidence of running on the live instance: six
   iPhone photographs show its exact wording [O]. It passes today's
   validation gate, and every template renders in both languages [V].
3. **It carries one latent defect, the `kiosk_mode` block.** That block hides
   Home Assistant's sidebar and header for every user, admins included. It
   was inert when photographed (`DR-015`), and the owner later removed it as a
   "lockout configuration" (`fc208cd`). The recovery branch must take that
   removal **first**, before anything else.
4. **Every later change was replayed onto the baseline, in order, in a
   throwaway worktree:** 25 steps, with the gate, a loss check and a render
   diff after each one. All 25 pass and none loses anything [V]. The result
   matches `ha-deploy`'s dashboard, theme and package byte for byte, plus one
   validator repair. A second stage adds the six truthfulness fixes, the test
   suite and the CI workflow from `autonomous/casaray-dev`.
5. **No change after `d22ce8e` has been seen working on its own on the live
   instance.** They are all class B: useful, gated, but unverified. The only
   later live evidence is the owner's 05/10 statement that CasaRay "is
   visible and navigates", and which file was on disk at the time is unknown.
6. **What blocks a working CasaRay today is the environment, not the YAML.**
   On 29/10, `input_boolean.chinese_dashboard` and all three `person`
   entities read `unavailable`, and four of the six cameras are down [V].
   122 of the dashboard's 405 references are helpers, people, scripts and
   automations, the class that lived in or depended on the lost
   configuration. The live connector exposes only one of those helpers, and
   it is `unavailable`. Whether CasaRay is still registered after the October
   Core update is unknown.

---

## 2. What was examined

| Source | Coverage |
|---|---|
| Git | The clone was shallow (50 commits) and was unshallowed. That gives **441 commits on 35 remote branches**, two root histories, and **344 commits on `ha-deploy`** |
| Branches read in full | `ha-deploy`, `recovery/phase0-diagnostics`, `autonomous/casaray-dev`, `casaray-v3-design`, `casaray-v3/hardening-1`, `casaray-v3/agent-2-visual-ux`, `casaray-v3/agent-task-tracking`, `claude/inspiring-lamport-0pfu43`, `claude/node-version-check-e9n225`, `claude/ha-dashboard-upgrades-wui7ig` |
| Branches inventoried by tip and topology | The other 25 (Appendix A) |
| Documents | `CLAUDE.md`, `PROJECT_STATE.md` (selectively), `DASHBOARD_ISSUES.md` (open section and visual audit), `LIVE_VERIFICATION_QUEUE.md` (results and late-September sections), the recovery records `RECOVERY_2026-09.md` and `RESTORE_PLAN_2026-10.md`, the V3 `README.md`, `DECISIONS.md` and `FEATURE_INVENTORY.md`, and `autonomous/casaray-dev`'s `DECISION_LOG.md`, `OWNER_ACTION_QUEUE.md` and `live_observations_2026-10-05.md` |
| Visual references | The seven 14/09 mockups and the 15/09 network render in `docs/mockups/` (the owner-approved design target). No live screenshot is committed anywhere: `artifacts/screenshots/` holds only its README. The owner photographs are known only through their transcriptions in the tracking files |
| Live Home Assistant | A read-only `GetLiveContext` on 29/10 12:49 AEDT (section 9). It returns friendly names, not entity IDs, and only Assist-exposed entities |
| Not reachable from here | `/config`, the supervisor, backups, logs, `.storage`, the Lovelace dashboard list |

---

## 3. Development timeline

### 3a. Before CasaRay v2 (21/08 – 04/09)

| Date | Event | Ref | Evidence |
|---|---|---|---|
| 21–23/08 | Repository and entity inventory created; `ha-deploy` created as the safe deployment branch; the production (legacy) dashboard imported | `2d4b295`, `a62d49e` | [R] |
| 23/08 | First "CasaRay-native" dashboard attempt, on a separate history, never merged | `44ec55f` (`claude/ha-dashboard-upgrade-8v0377`) | [R] |
| 24–30/08 | Hardening of the legacy dashboard (UI-/REG- series); CasaRay × Your Name theme | `88be895` | [R] |
| 29–30/08 | `CFG-003`: `ha-deploy` history replaced, so pushes stopped reaching the host. Root cause found 30/08; work paused | `ec10656` | [R] |
| 01/09 | Owner freezes **CasaRay Design v1** (mockups and Master Design Briefing) and lifts the pause; Batch 1 clock built on the legacy dashboard | `b6e76f5`, `5ad2bce` | [O] via [R] |

### 3b. CasaRay v2 development (05/09 – 24/09)

| Date | Event | Ref | Evidence |
|---|---|---|---|
| 05/09 | `CFG-003` resolved. 970-entity B1 export. **CasaRay v2 rebuilt from scratch**, and the owner names `casaray_v2.yaml` the canonical target. Bilingual layer and headings; `/casaray-v2` url_path migration; nine feature batches (Bills, Climate, Energy, House Health, People, Security, Entertainment) | `5dc6f50` → `0d2b58a` | [R] |
| 06/09 | **First live render.** Owner screenshots of `home`, `rooms`, `living-room`, `kitchen`, `dining`; six verification rows PASS (CR-100, 110, 113, 120, 133, 141); two layout defects fixed the same day | `3683782` | **[O]** |
| 06–08/09 | Correctness from live data (Bills contradiction, a 1000× Wh/kWh error, off-by-one due dates); mockup fidelity; area sweep | `81e7c8e` → `28752c3` | [R] |
| 13/09 | Every card declares its geometry (gated) | `677c6ea` → `26ae662` | [R] |
| 14/09 | Seven owner renders adopted as the visual target: sentence case, CR-232 colour system, chip strips, tinted alerts | `93e66b8` → `31eac4a` | [O] (renders) |
| 15/09 | Network board. Home rebuilt against the wall render, then **corrected twice against the live iPad** (DR-012, DR-013, so `max_columns: 2`). CSS background theme (DR-014) | `262d59d`, `b5e8522`, `e39b2bb`, `63dc2b8` | **[O]** |
| 15–16/09 | Maintenance suite: safe deploy, health checks, the automation package with a 03:30 self-deploy | `7c58cc8`, `0ebde71`, `9c4dce0` | [R] |
| 18/09 | Chip strip on all 28 views; badge gate (DR-011); footers; i18n gates; deploy pre-flight hardening | `5f74285` → `5aa567f`, `23b04e3`, `3c40913` | [R] |
| 18/09 17:23 | **`d22ce8e`**: dead Sensibo entities fixed (from the 19/09 AEST wall-iPad photographs), `STALE` blocklist gate, `DR-015` kiosk diagnosis | `d22ce8e` | **[O]** for the defect it fixed |
| 19–20/09 | **Six iPhone photographs of the live build. Their wording is `d22ce8e` exactly**, so nothing from `0d95183` onward was live. Visual audit CVA-001…014 against the mobile mockup. Theme and background PASS; Cameras 6/6; kiosk_mode does nothing | `DASHBOARD_ISSUES.md` (visual audit) | **[O]** |
| 18–20/09 | Chip compaction, plainer Lighting, render-fixture truthfulness pass, attention-count wording; tooling (improve-system, automate, capture, fixture) | `0d95183` → `d182251` | [R], unseen live |
| 24/09 08:57 | CVA-004: One tap and Rooms moved under Needs attention | `fa816a1` | [R], unseen live |

### 3c. The incident window (24/09 – 25/09)

| Time (UTC) | AEST | Event | Ref |
|---|---|---|---|
| 24/09 15:12–15:49 | 25/09 01:12–01:49 | Five owner-account commits: CVA-005 alerts full width, CVA-012 honest tile labels, More boards, One tap height, CVA-013 room summaries. **The last one leaves the gate failing** (four check-15e bilingual collisions) | `8b2f91b` → `2016214` |
| 24/09 15:58–17:49 | 25/09 01:58–03:49 | `verify_change.sh`; REG-015 fix (gate green again); rollback test suite and host drill | `8ce9721`, `53f18e9`, `9fbdbcb` |
| 24/09 18:24 | 25/09 04:24 | **Owner-account commit "Remove CasaRay kiosk mode lockout configuration"**: the `kiosk_mode:` block is deleted. *That a lockout happened is inferred from this commit title; no incident record exists* [I] | `fc208cd` |
| 24/09 18:43 | 25/09 04:43 | Read-only disk report for the host (CFG-004); it found an S1 rollback bug (REG-016), which was fixed | `032a705` |
| 24/09 19:22–19:24 | 25/09 05:22–05:24 | Owner-account validator changes "for Python-less HA environments" (the host's Terminal add-on). The first one breaks the validator; the second restores it but leaves a stale duplicate tail | `7309bd8`, `18a4e5d` |
| ~25/09 | | **During a CasaRay recovery attempt, files under `/config` were removed while Home Assistant was running.** It regenerated a default `configuration.yaml`. Lost: the CasaRay registration, the `packages:` include (so helpers and people went `unavailable`), `.storage/auth_provider.homeassistant` (so every password login was rejected), `core.config` (time zone fell back to UTC) and the backup key | `RECOVERY_2026-09.md` [R] |

### 3d. After the incident (25/09 – 29/10)

| Date | Event | Ref | Evidence |
|---|---|---|---|
| 25/09 | V3 design workspace (an HTML prototype) cut from `18a4e5d`. Its live check that day already shows all three `person` entities `unavailable` | `casaray-v3-design` `fb6dd8e` | [R] |
| 26–29/09 | Recovery tooling. Owner login rebuilt with Home Assistant's native auth tool, keeping user IDs; time zone restored through onboarding | `recovery/phase0-diagnostics` `aa78292` → `59c3b92` | [O] via [R] |
| 30/09 | `deploy_casaray.sh` run on the host, appending the registration block with `packages:` | `e835fc5` message | [R] |
| 05/10 | **Owner: login works; CasaRay is visible and navigates; some helpers read No data.** The owner directs that `ha-deploy` is protected and work goes on dedicated branches (D-001). `autonomous/casaray-dev`: 12 commits. V3-005 confirmed by the owner for the prototype | `DECISION_LOG.md`, `OWNER_ACTION_QUEUE.md` | **[O]** via [R] |
| before 12/10 | Core update, then a restart or reset; login fails again | `RESTORE_PLAN_2026-10.md` | [O] via [R] |
| 11–12/10 | V3 PR #4 merged into `casaray-v3-design`; V3 hardening; workflow skills; restore-from-backup plan (planning only) | `3eed6ca`, `1458c0d` | [R] |
| 18/10 | Login works again. Restore plan superseded; `deploy_casaray.sh` withdrawn; registration block reduced to the dashboard alone; read-only evidence script approved but not run | `e835fc5`, `4923ad4` | [O] via [R] |
| 17/10, 24/10 | Weekly automation audits, on the pre-29/08 history | `claude/inspiring-lamport-0g1pf6`, `-qmyt8v` | [R] |
| 29/10 | This report. Live: helpers and people still `unavailable`; four Tapo camera streams and the pet feeder camera down | section 9 | [V] |

---

## 4. The problem chain

Two different kinds of "problem" appear in the history. Only the second is the
one this recovery is about.

**Ordinary development defects (05/09 – 20/09).** Found and closed in the
normal loop: Bills contradictions, the Wh/kWh error, layout geometry
(DR-012, DR-013), dead Sensibo IDs, and the CVA visual mismatches. None of them
made CasaRay inoperable, and the build stayed live and was photographed
throughout.

**The operational incident (24/09 onward).**

1. **Kiosk-mode lockout [I].** `kiosk_mode:` with `hide_sidebar: true` and
   `hide_header: true` had been in the dashboard since the first build, with
   no admin exemption. It did nothing for as long as the kiosk-mode frontend
   resource was not loaded (`DR-015`, and the 20/09 photographs). `d22ce8e`
   replaced a non-existent option with `ignore_entity_settings: true`. Once
   the resource loads, that block hides Home Assistant's own navigation on
   every CasaRay view for every user. The owner's 25/09 04:24 AEST commit
   calls it a "lockout configuration". When the resource first loaded is not
   recorded.
2. **Gate left red overnight.** `2016214` (owner-account) failed check 15e.
   It was caught and fixed in `53f18e9` about 15 minutes later. Whether that
   red build was ever synced to the host is unknown.
3. **Validator broken on the branch tip.** `7309bd8` truncated a line and
   spliced a script body into it (exit 2). `18a4e5d` restored it, but left a
   stale copy of the body after `exit 1`, so `bash -n` rejects the file. It
   still runs, because bash executes line by line.
4. **Configuration loss (~25/09).** This is what took CasaRay down: files
   deleted under a running Home Assistant. Its effects (registration,
   packages, helpers, people, logins, time zone, backup key) are listed in
   3c. They are all **outside** `dashboards/casaray_v2.yaml`.
5. **Second login failure (before 12/10)** after a Core update. Resolved by
   18/10.

---

## 5. Last known-good: the candidates

| Candidate | Date | Live evidence | Gate today [V] | For | Against |
|---|---|---|---|---|---|
| `3683782` | 06/09 | **[O]** six PASS rows | not re-run | First confirmed render | Discards two weeks of work that was itself live and photographed by 20/09 |
| `e39b2bb` / `63dc2b8` | 15/09 | **[O]** live iPad corrections | not re-run | Home geometry proven on the wall | Same objection; `d22ce8e` contains it |
| **`d22ce8e`** | **18/09** | **[O] the 19–20/09 iPhone photographs show this build's exact text** | **PASS** | Last build seen running; includes every live-proven fix | Carries the latent kiosk block; 14 CVA mismatches open |
| `cb9c684` | 24/09 08:57 | none | PASS | Last coherent state before the incident window | Never seen live |
| `86ec579` | 24/09 18:44 | none | PASS | Includes the kiosk removal; validator intact | Never seen live; mixes in the incident-window commits |
| `18a4e5d` (`ha-deploy` tip) | 25/09 05:24 AEST | **indirect only**: on 05/10 the owner said CasaRay "is visible and navigates", but which file was on disk is unverified | PASS at runtime; **`bash -n` fails** | Most complete; the recovery record says Home Assistant's own `check_config` passed it with the registration block | Not proven to be the version that rendered; contains the broken-then-patched validator |

**Recommendation: `d22ce8e`**, entering the recovery branch with the kiosk
removal (`fc208cd`) applied as its first commit.

The oldest confirmed build is not the best one: the 06/09 builds were
superseded by work that was also live. The latest build is not the best one
either: nothing after `d22ce8e` was seen before the incident, and the tip's
05/10 evidence cannot be tied to a commit.

### Evidence that `d22ce8e` was operational

| # | Evidence | Source | Label |
|---|---|---|---|
| 1 | Six iPhone photographs of the live dashboard. The Home chip strip reads `Inside 24.0°` and `At home 1 of 3`, which is `d22ce8e`'s wording exactly; "nothing from `0d95183` onward was live" | `DASHBOARD_ISSUES.md`, visual audit 2026-09-20; `LIVE_VERIFICATION_QUEUE.md`, iPhone live render | **[O]** |
| 2 | In the same photographs, theme and background match the approved renders: flat near-black page, translucent cards, 16–18 px radius, no photographic background, no hardcoded colour | same | **[O]** |
| 3 | `Cameras 6/6`: all six cameras answering | same | **[O]** |
| 4 | The defect the previous build showed live (three "Entity not found" cards on Climate) is fixed in this commit | `d22ce8e` message | **[O]** + [R] |
| 5 | `bash scripts/ha_validate.sh`: VALIDATION PASSED, 8 sections, exit 0 | this session | [V] |
| 6 | Every markdown template renders in English and Chinese, against a populated fixture and an all-dark state set, with no render failure | `verify_change.sh` render pass, this session | [V] |
| 7 | 28 views (7 subviews), 1,235 cards, 405 entity references, all present in the 05/09 export; 28 navigation targets, 0 broken; 7 service calls | `preserve_check.py`, gate check 3, this session | [V] |
| 8 | **Known at the time:** `kiosk_mode` inert; CVA-001…014 open; CVA-012 (S1) tiles named for rooms but wired to the freezer and printer plugs | `DR-015`, visual audit | **[O]** |

---

## 6. Git comparison between versions

Structural counts, from `preserve_check.py` [V]:

| | `d22ce8e` | `cb9c684` | `53f18e9` | `18a4e5d` | `autonomous/casaray-dev` |
|---|---|---|---|---|---|
| Views | 28 | 28 | 28 | 28 | 28 |
| Cards | 1,235 | 1,238 | 1,238 | 1,238 | 1,242 (with stage 2 in the replay) |
| Entity references | 405 | 405 | 405 | 405 | 405 |
| Navigation targets | 28 | 28 | 28 | 28 | 28 |
| Service calls | 7 | 7 | 7 | 7 | 7 |
| Lines in `casaray_v2.yaml` | 12,114 | | | 14,101 | +143 / −24 on `18a4e5d` |
| Validation gate | PASS | PASS | PASS | PASS (runtime) | PASS; 51/51 tests |

`d22ce8e` → `18a4e5d` is 33 commits: `+2,322 / −335` in the dashboard, no
change to `themes/` or `packages/`, and nothing removed. The commit that
introduced the gate failure, `2016214`, fails on its own [V]:
`'Fridge closed' is rendered 2 different ways in Chinese` and the same for
`'Motion'`. `7309bd8` exits 2 [V].

Branch topology: everything CasaRay descends from `ha-deploy` `18a4e5d`.
Nothing was ever merged back, and no branch has moved `ha-deploy` since
25/09. The branches hanging off it are `recovery/phase0-diagnostics`,
`autonomous/casaray-dev`, the four `casaray-v3*` branches and
`claude/inspiring-lamport-0pfu43`. The older root (`main` and 20 `claude/*`
branches, including October's weekly audit branches) is a separate history
and holds no CasaRay v2 work.

---

## 7. Classification of every change after the baseline

**A: verified working.** None after `d22ce8e`. No later change has its own
live observation. Everything up to and including `d22ce8e` is class A and
is the baseline.

**B: useful but unverified.** All validated offline; none seen live.

| Step | Commits | What | Notes |
|---|---|---|---|
| R0 | `fc208cd` | Remove the `kiosk_mode` block | **Mandatory, first.** Owner-account. Removes the lockout ingredient; nothing depended on it, since it never worked (`DR-015`). Home Assistant's own header shows afterwards; that is accepted |
| R1 | `0d95183` | Home chip strip fits one line | Deliberate compaction: `Inside 21.4°` → `21°`, `3 of 3` → `3/3`, Climate drops its `(3/3)` denominator, Bills drops the next-due bill name |
| R2 | `3fb9042` | Lighter footers, plainer Lighting, compact Rooms conditions | +3 cards; detail moved to House health, nothing dropped |
| R3 | `d3b4fad` `122852a` `a1a72d6` `9e6235b` `55631a1` `f7856d9` `6accad8` | Tooling: improve-system and automate skills, export-staleness audit, capability snapshot, screenshot capture, render fixture | No dashboard change |
| R4 | `2d42e1a` `bd49f14` `6ec8f20` `2fecd89` | Two under-reporting cards (Network `0/0`, update count); `next_id.py` | Truthfulness |
| R5 | `b96067e` `d182251` | Needs attention names what it counts; two truncating tiles renamed | From the 20/09 photos |
| R6 | `fa816a1` `cb9c684` | CVA-004 band reorder | Pure reorder; render diff is two index lines |
| R7 | `8b2f91b` | CVA-005: alert cards `columns: 12` | Owner-account. **Supersedes `CLAUDE.md`'s band table** ("alert cards at `columns: 6`"). Needs reconciling in `CLAUDE.md` when integrated |
| R8 | `1c90090` | CVA-012: `Garage freezer`, `Guest Room printer` | Owner-account. Closes an S1 honesty defect |
| R9 | `4d40250` | More boards: `columns: 6, rows: 1` | Owner-account. Changes More boards from four across to two across. `CLAUDE.md` describes the four-across shape; needs reconciling |
| R10 | `34ee88d` | One tap: `rows: 2` | Owner-account |
| R11 | `8ce9721` | `verify_change.sh` | Tooling |
| R12 | `2016214` + `53f18e9` + `7f8e07c` | CVA-013 room-centric Home summaries, with the REG-015 bilingual fix | **Only as a pair.** Markdown rows with `tap_action: navigate`; the markdown card supports `tap_action` per current Home Assistant docs. Needs a live tap test |
| R13 | `9fbdbcb` `de84740` | Rollback test suite and host drill | 18/18 assertions after R14 [V] |
| R14 | `032a705` `5c106dc` `86ec579` | Disk report (CFG-004); REG-016 rollback fix | `5c106dc` stamped an orphaned hash, and `86ec579` corrects it, so they go together |
| R15 | `7309bd8` + `18a4e5d` + `3eff5e0` | Validator tolerates a Python-less host shell, then the stale tail is removed | `3eff5e0` is from `claude/inspiring-lamport-0pfu43`. Only the trio is sound |
| A1 | `eb630df` | Whole-dashboard audit; the entity gate accepts IDs defined in `packages/` | `autonomous/casaray-dev` |
| A2 | `3e46561` | House health → Setup status card (why helpers read No data) | +3 cards |
| A3 | `ef9c7e2` `3edf53e` | Regression suite (51 tests) and GitHub Actions gate; review workflow docs | The workflow triggers on pushes to `recovery/**`, so it runs on this branch from A3 onward; read-only permissions |
| A4 | `693e743` `4c83642` | Bills: no "nothing owed" while the helpers are silent | Truthfulness |
| A5 | `8d16497` | Test: sirens, locks and camera privacy never actuate on a bare tap | Safety pin |
| A6 | `a9456a3` | House health: dashboard delivery status | +1 card; reads `packages/` sensors, so it shows No data until they load |
| A7 | `a414bec` | Backlog, project-state pointer, package template parse test | |
| A8 | `9f73e33` | People: no zeros when nobody reports a location | Truthfulness |
| A9 | `5ffbe74` `ac10385` | Bills: one silent bill blocks the all-clear | Truthfulness |
| — | `claude/inspiring-lamport-0pfu43` (rest) | `stamp_sha.py`, `requirements-dev.txt`, audit reports | Tooling; optional, after stage 2 |

**C: known defective.** Never integrated as they stand.

| Change | Defect | Disposition |
|---|---|---|
| `kiosk_mode` block (`5dc6f50` … `53f18e9`) | Hides Home Assistant's navigation for every user once the resource loads; the lockout | Removed by R0 |
| `2016214` alone | Fails the gate (check 15e) | Only with `53f18e9` (R12) |
| `7309bd8` alone | Validator exits 2 | Only within R15 |
| `18a4e5d` alone | Validator fails `bash -n` (stale tail after `exit 1`) | Only within R15 |
| `5c106dc` alone | Tracking row names a commit not on the branch | Only with `86ec579` (R14) |
| `claude/ha-dashboard-upgrades-wui7ig` `ef27115`, `626b507` | Pre-rebase duplicates of `032a705` and its stamp | Excluded; the mirror is stale (6 behind, 2 divergent) |
| `scripts/recovery/repair_login.sh`, `deploy_casaray.sh` | Withdrawn by their own authors: an API removed in 2026.9; registering the legacy url_path; loading the automation package as a side effect | Excluded; reference only |
| `rollback` modes of `fix_owner_login.sh` and `recover_login.sh` | Would move the live password store aside and lock every user out | Excluded; disabled on that branch |
| The ~25/09 deletion of files under a running `/config` | Caused the configuration loss | Not a commit; recorded here so it is never repeated (section 11) |

**D: unclear impact.** Kept as reference and not integrated without a
decision.

| Change | Why it is D |
|---|---|
| CasaRay V3 prototype (`casaray-v3-design` and three agent branches) | A different product: an HTML/JS prototype on demo data, with Concept D as the design base (V3-005, owner-confirmed 05/10). It is not Home Assistant YAML and replaces CasaRay's visual system rather than continuing it. Its *decisions* are valuable inputs (V3-007: no HVAC toggle on Home, Home ≤ ~2 screens, an all-clear only when every check answered, 44 px touch targets). Its *code* is not a recovery source |
| V3 workflow skills (`session-orient`, `recovery-triage`, `provenance-register`) | Useful tooling, unvalidated against this branch's rules |
| `claude/node-version-check-e9n225` | Entity-reconciliation classifier and visual smoke test cut from `23b04e3`; diverged 53 commits behind; overlaps the `STALE` gate |
| `packages/casaray_automation.yaml` 03:30 self-deploy | Live status unknown. If the 30/09 run loaded `packages/` and `input_boolean.casaray_auto_deploy` is on, the host resets its clone to `origin/ha-deploy` nightly and redeploys, which would overwrite any manually synced candidate (D-004) |
| `recovery/phase0-diagnostics` evidence script (CR-REC-25 v1.2) | Approved, tested in chroots, never run on the host. A read-only tool, not a dashboard change |
| Pre-29/08 history (`main`, 21 `claude/*` branches) | Bootstrap scaffolding and "blocked" routine logs; superseded |

---

## 8. Recovered features register

What the recovery candidate carries, board by board. The "Live" column
records the strongest evidence that board has. The Dependency column says
what in Home Assistant must answer for the board to say anything useful
today.

| Board / view | Content | Live | Dependency today |
|---|---|---|---|
| `home` | Top bar, chip strip, Needs attention, One tap, Rooms \| Shopping list, Right now \| Who's home, Security, Energy now \| Recent activity, More boards | **[O]** 06/09, 15/09, 19–20/09 | People (`unavailable`), bills helpers |
| `rooms` + 7 room pages | Conditions, lights, scenes, plugs, sensors, device settings | **[O]** 06/09 (`rooms`, `living-room`, `kitchen`, `dining`) | Hue lights partly down |
| `lighting` | Groups, wall switches, Hue spots, scene studio | not individually | Hue spots `unavailable` |
| `climate` | Parents Room AC (thermostat), room readings, 24 h, Advanced | **[O]** 19/09 wall iPad (defect then fixed) | AC answering |
| `energy` | Solar, metered circuits, trend, grid, inverter health, forecast, carbon | not individually; UI-011 on the native panel only | Inverter and forecast answering; `CFG-001`/`CFG-002` open |
| `bills` + `bills-details` | Unpaid/paid, upcoming, savings, YTD, history | not individually | **All 34 references are helpers.** The connector cannot see them; the owner reported helpers reading No data on 05/10 |
| `security` | Doors, motion, camera health, detection settings (display-only), sirens (half-width by design) | not individually | Contacts answering |
| `cameras` + 6 `camera-*` subviews | Batteries, floodlights, `custom:webrtc-camera` streams | "Cameras 6/6" **[O]** 20/09 | **Four Tapo streams and the pet feeder `unavailable` on 29/10** |
| `people` | Household, devices, whereabouts, guest mode | not individually | **All three `person` entities `unavailable`** |
| `entertainment` | Four TVs and speakers, room lighting | not individually | TVs answering; Pogo down |
| `house-health` | Overall, batteries, network, offline count, backups and updates | not individually | |
| `network` | WAN, Wi-Fi link quality, monitored devices | not individually | eero WAN answering |
| `automations`, `alerts` | Household behaviours, Hue Bridge automations; Critical / Warnings / Info | not individually | |
| Cross-cutting | Bilingual EN/中文 on `input_boolean.chinese_dashboard` (503 references); `DD/MM/YY` clock; chip strip on 28 views; footer navigation; theme tokens; offline drawn, never hidden | **[O]** clock 06/09, theme 20/09 | **The toggle is `unavailable`, so English shows by design (`state_not: 'on'`)** |

---

## 9. Live Home Assistant, 29/10 12:49 AEDT

Read-only `GetLiveContext`. **Limits:** the connector returns friendly names,
not entity IDs, and only Assist-exposed entities. The registry carries stale
twins with identical names, so absence or a twin's state proves nothing about
a specific ID.

| Answering | Not answering |
|---|---|
| Fronius Primo inverter (1,675 W AC, 8,575 Wh today); SolarNet; Solcast forecast; Electricity Maps | `input_boolean.chinese_dashboard` ("Chinese Dashboard") |
| Front, master and back door contacts (each with a dead twin); LG fridge door | `person` Raymond Du., Vinh Du, Ai Q Huang |
| Parents Room AC (off, 19.6 °C), its Climate React, Timer and occupancy | Tapo C420 East, C420 South, C425 North and C200 Stockroom streams; Smart Pet Feeder camera |
| Front Door camera, ding and motion events, battery 68% | Hue ambiance spots, Living Room inner/outer, Corridor 1/2, Dining Left/Right |
| Weather (Forecast Home, partly cloudy, 16.4 °C; it was `unavailable` on 25/09) | Hue motion sensors (Bedroom, Living); Presence FP300 (one of its twins answers) |
| eero WAN; Shopping list; Hue scenes; light groups; roller shade; TVs; Tapo plugs | Air purifier; Genio power board; master bedroom power point; Pogo |
| | "Solar Power Display" (`sensor.solar_power_display` in the export; not referenced by CasaRay) |

Compared with earlier reads: the weather was `unavailable` on 25/09 and has
answered since 05/10. Cameras were 6/6 on 20/09. Four Tapo streams were
already down on 05/10, and the pet feeder camera, which answered on 05/10,
is now down too.

---

## 10. Validation against the eleven criteria

| # | Criterion | Status | How |
|---|---|---|---|
| 1 | Original approved visual design | Theme and background **matched** on 20/09 [O]; layout mismatches CVA-001…014 partly addressed by R5–R12; no live photo since | 14/09 mockups |
| 2 | Last known-good functionality | **Preserved**: 28 views, 405 entities, 28 navigation targets and 7 services at every step | `preserve_check` [V] |
| 3 | Completed later features | All 16 stage-1 steps and 9 stage-2 steps replay cleanly | dry run [V] |
| 4 | Current Home Assistant compatibility | Gate PASS. Home Assistant's `check_config` passed the registration block: on 2026.2.3 with this dashboard, theme and package on disk, and on 2026.10.1 against the default configuration [R]. `check_config` does not validate Lovelace card schema. Markdown `tap_action` is supported per current docs [V]. No `hass` here | |
| 5 | Current entity availability | Section 9. **Helpers, people and four cameras down** | live [V] |
| 6 | Dashboard navigation | 28 targets resolve, 0 broken; on-device taps not testable here | gate [V] |
| 7 | Tablet/mobile rendering | **Cannot be measured here.** DR-012/DR-013 rules hold; R7 and R9 change widths and need a wall-iPad photo | owner |
| 8 | Cameras | Subviews and `webrtc-camera` unchanged since baseline; four streams currently down (environment) | live [V] |
| 9 | Energy | Wh/kWh gates PASS; inverter answering; CR-326 unit mismatch is an owner setting | gate [V], live [V] |
| 10 | Language support | Bilingual gates PASS; render EN and 中文 with no errors; toggle currently `unavailable` | render [V] |
| 11 | Security and climate controls | Sirens and detection settings display-only or guarded; A5 pins no bare-tap actuation; AC uses the native thermostat; V3-007's HVAC caution noted for later work | gate and tests [V] |

**Regressions found by the step-by-step replay** (gate · loss · render diff
lines, each step against the one before):

| Step | Gate | Lost | Render diff | Step | Gate | Lost | Render diff |
|---|---|---|---|---|---|---|---|
| R0 | pass | none | 0 | R13 | pass | none | 0 |
| R1 | pass | none | 58 | R14 | pass | none | 0 |
| R2 | pass | none | 114 | R15 | pass | none | 0 |
| R3 | pass | none | 0 | A1 | pass | none | 0 |
| R4 | pass | none | 8 | A2 | pass | none | 46 |
| R5 | pass | none | 8 | A3 | pass | none | 0 |
| R6 | pass | none | 2 | A4 | pass | none | 30 |
| R7 | pass | none | 0 | A5 | pass | none | 0 |
| R8 | pass | none | 0 | A6 | pass | none | 14 |
| R9 | pass | none | 0 | A7 | pass | none | 0 |
| R10 | pass | none | 0 | A8 | pass | none | 16 |
| R11 | pass | none | 0 | A9 | pass | none | 0 |
| R12 | pass | none | 82 | | | | |

R7–R10 change geometry and tile names, which the render pass does not read;
those need the wall-iPad check in section 13.

Each render diff was read and is what its commit says it does. After R15,
`test_rollback.sh` passes 18/18. After A9 the suite runs 51 tests with one
failure: `test_known_syntax_issues_are_still_tracked`. That is a ratchet
test, and it fails *because* R15 fixed the validator. The fix is to delete
one entry from `KNOWN_SYNTAX_ISSUES` at integration time. On
`autonomous/casaray-dev` itself the suite passes 51/51.

**No regression was found at gate level.** What the replay cannot find is
anything visual or on-device, and that is what criteria 6, 7 and 8 still
need.

---

## 11. Known defects register

| ID | Defect | Where | State |
|---|---|---|---|
| KD-01 | `kiosk_mode` block: lockout once the resource loads | baseline | Fixed by R0 |
| KD-02 | CVA-001…014 mismatches with the mobile mockup (one layout serves phone and wall) | baseline | Partly addressed (CVA-004, 005, 009, 012, 013); CVA-001 needs an architecture decision |
| KD-03 | CVA-012 (S1): room-named tiles report one appliance | baseline | Fixed by R8 |
| KD-04 | REG-015: gate red after `2016214` | incident window | Fixed by R12 pairing |
| KD-05 | Validator: crash, then stale tail | incident window | Fixed by R15 |
| KD-06 | REG-016: rollback picked the oldest backup | tooling | Fixed by R14, 18/18 |
| KD-07 | Bills could claim "nothing owed" while its helpers were silent | `18a4e5d` | Fixed by A4, A9 |
| KD-08 | People printed zeros with nobody reporting | `18a4e5d` | Fixed by A8 |
| KD-09 | Home Assistant's loader warns about a duplicate `ha-card-border-color` in the theme | theme, pre-existing | Open, cosmetic [R] |
| KD-10 | CR-326: `Solar today` in Wh beside `Used today` in kWh | HA entity setting | Owner action |
| KD-11 | `CLAUDE.md` contradicts R7 and R9 (alert and More boards widths) | docs | Reconcile at integration |
| ENV-01 | CasaRay registration status after the October Core update unknown | host | Owner check |
| ENV-02 | The language toggle and all 3 people `unavailable`. The dashboard reads 109 helper IDs whose definitions are not in Git; they were most likely in the lost `configuration.yaml` [I] | host | `proposals/casaray_helper_booleans.proposed.yaml` (arrives with A4) covers the 7 booleans; the owner checks Settings → Helpers first |
| ENV-03 | Four camera streams and the pet feeder down | host / devices | Owner |
| ENV-04 | Hue lights and motion sensors, air purifier, Genio and master bedroom power points down | devices | Owner |
| ENV-05 | Other users' passwords not restored; backup key lost | host | Owner (open since 29/09) |
| ENV-06 | Auto-deploy package status unknown | host | Owner check before any sync |
| ENV-07 | Deploy-bridge `shell_command` lost with `configuration.yaml` | host, protected | Only on explicit instruction |

**Never repeat:** deleting or moving files under `/config` while Home
Assistant is running. That one act caused ENV-01, ENV-02 and ENV-05.

---

## 12. Proposed recovery branch and plan (not created yet)

| Item | Proposal |
|---|---|
| Branch | `recovery/casaray-continuation`, cut from **`d22ce8e`** |
| Method | `git cherry-pick -x`, one step per commit, in the order R0 → R15, then A1 → A9. `-x` records each original SHA, so every step stays traceable to `ha-deploy` |
| Each step | `bash scripts/ha_validate.sh` (exit 0) · loss check against the previous step · render diff read · commit message carries its class from section 7 · stop on any failure |
| Integration edits | At A3, delete the one `KNOWN_SYNTAX_ISSUES` entry that R15 made obsolete; reconcile `CLAUDE.md` with R7/R9; record the branch in `PROJECT_STATE.md` |
| Protected | `ha-deploy` (D-001), `dashboards/deez_smart_home.yaml`, every other branch. Nothing is rebased, reset, force-pushed or deleted |
| Result | **Stage 1** (R0–R15): dashboard, theme and package byte-identical to `18a4e5d`, validator clean. **Stage 2** (A1–A9): plus the truthfulness fixes, tests and CI. Both proven by the dry run |
| After | Live verification by the owner (section 13). Only then does new development start, on top of this branch |

---

## 13. Deployment and rollback (owner-run, after approval)

Nothing below has been run. Each step is the owner's.

**Before anything (read-only):**

1. Open `/casaray-v2/home`. Does it load (registered), or say it cannot be
   found (unregistered)?
2. Settings → Devices & services → Helpers. Is *Chinese Dashboard* listed?
   This decides ENV-02's fix (see the proposal file's own instructions).
3. HACS → Frontend. Is kiosk-mode installed? If it is, the legacy dashboard
   can hide navigation too. Appending `?disable_km` to the page address
   bypasses kiosk-mode on that page.
4. Is `input_boolean.casaray_auto_deploy` present and **on**? If so, turn it
   off first. Otherwise 03:30 resets the host's clone to `ha-deploy` and
   overwrites the candidate.
5. Take a full backup (Settings → System → Backups) and download it.

**Deploy the candidate.** This syncs the dashboard and theme only and never
resets the host's clone:

```sh
cd /config/deez_repo
git fetch origin recovery/casaray-continuation
rm -rf /tmp/casaray_rc && mkdir -p /tmp/casaray_rc
git archive FETCH_HEAD | tar -x -C /tmp/casaray_rc
REPO=/tmp/casaray_rc sh /tmp/casaray_rc/scripts/sync_casaray_to_config.sh
```

Then hard-refresh the browser or iPad (CAP-005 asks whether a soft refresh is
enough). The sync script refuses a file that does not parse, and keeps a
timestamped copy of what it replaces.

**If CasaRay is unregistered:** registration is a `configuration.yaml`
change (a protected file) plus a restart. Use the **dashboard-only** block,
`scripts/recovery/casaray_config_block.yaml` at `e835fc5` on
`recovery/phase0-diagnostics`. Do not use `deploy_casaray.sh`, and do not add
`packages:` in the same step. Run `ha core check` before restarting.

**Verify:** the six icon-rail destinations open and return; Home on the wall
iPad has no half-empty rows (R7 and R9 changed widths); Rooms rows navigate
(R12); one camera subview streams; English/中文 once the toggle exists.

**Rollback:**

- *Dashboard:* restore the sync script's timestamped copy in
  `/config/dashboards/`, or run the same five lines with `ha-deploy` in place
  of `recovery/casaray-continuation` to return to `18a4e5d`.
- *Registration:* remove the block, `ha core check`, restart.
- *Legacy dashboard:* never touched. It stays available at
  `/deez-smart-home/` throughout.
- *Git:* the recovery branch is additive, and `ha-deploy` does not move.

---

## 14. Decisions needed from the owner

1. **Approve `d22ce8e` as the recovery point** (the recommendation). The
   alternative is to cut from `18a4e5d` directly. The resulting tree is the
   same, but the history would no longer re-certify each change.
2. **Stage 2.** Include the `autonomous/casaray-dev` improvements (A1–A9),
   which add a GitHub Actions workflow? Recommended.
3. **Naming.** The brief calls the outcome "CasaRay V3 development candidate".
   "V3" already names the HTML prototype redesign (Concept D, V3-005).
   Recommended: call this the **CasaRay v2 recovery candidate**, keep url_path
   `casaray-v2`, and keep the V3 prototype as reference only. Or say which
   meaning "V3" should have.
4. **V3 decisions.** Port the V3-007 rules (no HVAC toggle on Home, a grey
   all-clear while any check is unanswered) into v2 as later work? Proposed
   as new development, after recovery is verified.

---

## Appendix A — branch inventory

| Branch | Tip | Relation to `ha-deploy` | Class |
|---|---|---|---|
| `ha-deploy` | `18a4e5d` 25/09 | — | production record; protected |
| `recovery/phase0-diagnostics` | `4923ad4` 18/10 | +11 on tip | C/D reference: recovery tooling |
| `autonomous/casaray-dev` | `ac10385` 05/10 | +12 on tip | B: stage 2 |
| `casaray-v3-design` | `27f3fed` 12/10 | +22 on tip | D: V3 prototype |
| `casaray-v3/hardening-1` | `fda930e` 11/10 | +20 on tip | D |
| `casaray-v3/agent-2-visual-ux` | `e1d7848` 11/10 | +16 on tip | D (merged into V3 via PR #4) |
| `casaray-v3/agent-task-tracking` | `f774991` 12/10 | +24 on tip | D |
| `claude/inspiring-lamport-0pfu43` | `a7b2581` 12/10 | +7 on tip | B: tooling (R15 takes `3eff5e0`) |
| `claude/ha-dashboard-upgrades-wui7ig` | `626b507` 24/09 | 6 behind, 2 divergent | C: stale mirror |
| `claude/node-version-check-e9n225` | `ac43239` 17/09 | 53 behind, +4 | D |
| `claude/elegant-mendel-3ilvv0`, `-dbdgpx`, `claude/ecstatic-lovelace-j2oo40`, `claude/ha-deploy-setup-vb0hxa` | August | merged ancestors (+0, or +1 doc) | historical |
| `main` and 20 `claude/*` branches on the older root | 21/08 – 24/10 | unrelated history | historical / audit reports |

## Appendix B — reproducing this report's checks

```sh
git fetch --unshallow origin    # the session clone was shallow
bash scripts/ha_validate.sh                     # at any candidate commit
bash scripts/verify_change.sh d22ce8e           # from an 18a4e5d checkout
python3 .claude/skills/improve-system/scripts/preserve_check.py --ref <prev>
bash scripts/test_rollback.sh                   # 18/18 after R14
python3 -m unittest discover -s tests           # after stage 2
```

The dry run used throwaway worktrees outside the repository. Its commits are
on no branch and were not pushed.
