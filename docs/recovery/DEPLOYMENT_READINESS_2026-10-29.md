# CasaRay deployment readiness — 29/10/26 (Phase 1)

Branch `recovery/casaray-continuation`, cut from `d22ce8e` on the owner's
approval of 29/10/26. Companion to `CASARAY_RECOVERY_REPORT_2026-10-29.md`,
whose section numbers this file cites.

**Nothing has been deployed, restarted, reloaded or registered.** No
`/config` file, helper, credential, backup or Home Assistant setting was
touched. `ha-deploy` and the legacy dashboard are unchanged, and PR #12 is
left unmerged.

---

## 1. Recommendation

### **NO-GO today. GO for a dashboard-file sync once checks P1–P5 (section 6) come back as expected.**

The branch itself is sound. Every commit passed every gate (section 3), and
nothing was lost (section 4). The NO-GO is about the host. Three things that
decide whether a deploy works, sticks and is safe cannot be seen from here:

| # | Blocker | Why it blocks |
|---|---|---|
| **B1** | **CasaRay's registration is unknown.** It was re-registered on 30/09 and seen working on 05/10, then a Core update and reset came before 12/10. On 18/10 the recovery branch planned a fresh dashboard-only registration, which suggests it had been lost again [I] | If it is unregistered, a sync changes nothing on screen. Registering means editing `configuration.yaml` (a protected file) and restarting, which is a separate owner approval |
| **B2** | **The nightly auto-deploy may be armed.** If `packages/` loaded with the 30/09 block, `automation.casaray_nightly_safe_deploy` runs at 03:30 whenever `input_boolean.casaray_auto_deploy` is on. It runs `git reset --hard origin/ha-deploy` in `/config/deez_repo` and deploys `ha-deploy` | It would silently replace this candidate overnight with `ha-deploy`'s build, dropping Stage 2. It also hard-resets the host's clone. Neither the helper nor the automation is exposed to the connector, so its state is unknown |
| **B3** | **The kiosk-mode resource's state is unknown, and the legacy dashboard still carries `kiosk_mode`.** The repo copy of `deez_smart_home.yaml` hides the sidebar and header for every user | CasaRay no longer has the block (R0). The legacy dashboard is out of scope and was not touched, but if the resource is loaded the lockout risk survives there. Escape hatch: append `?disable_km` to the page address |

What does **not** block, but sets expectations:

- **Helpers and people are down** (section 5c). Bills, Bills details,
  People and the language toggle will read *No data* or stay in English.
  That is the dashboard telling the truth, not failing: the A2/A6 House
  health cards name the cause.
- **On the host shell, the sync script cannot check YAML.** With no
  `python3` (Terminal & SSH add-on), `sync_casaray_to_config.sh` prints
  `yaml parse: SKIPPED` and copies anyway. The parse guarantee is this
  branch's gate, which passed at every commit. Sync only from a commit that
  CI has passed.

---

## 2. What was built

- **Base:** `d22ce8e`, the last build the owner photographed running
  (recovery report §5).
- **Method:** `git cherry-pick -x`, one change at a time in the documented
  order. Each commit carries `(cherry picked from commit …)`,
  `Recovery-Step` and `Recovery-Class`. Original authors and dates are kept;
  combined commits name every original.
- **Combined, never applied alone** (each would leave a failing commit on its
  own):

  | Step | Commits | Why |
  |---|---|---|
  | R12 | `2016214` + `53f18e9` | `2016214` fails check 15e |
  | R14s | `5c106dc` + `86ec579` | the first names an orphaned hash |
  | R15 | `7309bd8` + `18a4e5d` + `3eff5e0` | crash, then a stale tail, then the fix |
  | A3 | `ef9c7e2` + `3edf53e` | **Deviation from the plan, which listed them as two commits:** `ef9c7e2`'s tests run `scripts/review_packet.py`, which `3edf53e` adds |

- **Approved integration corrections** (recovery report §12):
  1. **A3:** `KNOWN_SYNTAX_ISSUES` emptied (R15 had already fixed
     `ha_validate.sh`); OWNER_ACTION_QUEUE B1 marked resolved, with its
     finding kept.
  2. **`CLAUDE.md`:** reconciled with R0 (no kiosk mode), R7 (alerts
     `columns: 12`) and R9 (More boards two across), plus D-001's push rule.
  3. **`PROJECT_STATE.md`:** a dated recovery note. **`DECISION_LOG`:**
     D-011. **`AUTONOMOUS_BACKLOG`:** B1 struck.

The full commit map, with every new SHA and its original, is in Appendix A.

---

## 3. Validation

**After each of the 42 commits before this report,** by the replay driver: the validation
gate; `sh -n`/`bash -n` on every `scripts/*.sh`; a loss check against the
commit before it; a render of every markdown card in English and 中文
against a populated fixture and an all-dark state set, diffed against the
commit before it; the test suite and the audit check from the point each
exists; and a clean tree. **Every check passed on every commit.**

| Step | Render diff lines | Cards | Step | Render diff lines | Cards |
|---|---|---|---|---|---|
| R0 | 0 | 1235 | R15 | 0 | 1238 |
| R1 | 58 | 1235 | A1 | 0 | 1238 |
| R2 | 114 | 1238 | A2 | 46 | 1241 |
| R3 ×7 | 0 | 1238 | A3 | 0 | 1241 |
| R4 | 8, 0, 0, 0 | 1238 | A4 | 30, 0 | 1241 |
| R5 | 8, 0 | 1238 | A5 | 0 | 1241 |
| R6 | 2, 0 | 1238 | A6 | 14 | 1242 |
| R7–R11 | 0 | 1238 | A7 | 0 | 1242 |
| R12 | 82 | 1238 | A8 | 16 | 1242 |
| R12s–R14s | 0 | 1238 | A9 | 0, 0 | 1242 |

Every render diff matches its commit's stated intent; the recovery report
§10 records what each one says. R7–R10 change geometry and tile names, which
the render pass does not read.

Notes from the run:

- At A1, the audit check found no report to compare against. That is the
  source branch's own order: the tool arrives at A1 and its report at A2.
  The check runs from A2 on and passes.
- **R15 changes no gate behaviour:** with Python present, the validator's
  output before and after is identical. With Python absent it prints
  `VALIDATION PARTIAL` and exits 0, which is the 25/09 owner design. No
  deploy script relies on that exit code: `casaray_safe_deploy.sh` refuses
  outright without `python3`.

**Final run on the branch head** (what CI runs, plus the rest):

| Check | Result |
|---|---|
| `bash scripts/ha_validate.sh` | **VALIDATION PASSED** (8 sections), exit 0 |
| `sh -n` / `bash -n`, every `scripts/*.sh` | **19 / 19** parse |
| `python3 -m unittest discover -s tests` | **51 / 51 OK** |
| `python3 scripts/audit_casaray.py --check --strict` | **up to date, clean** |
| `render_cards.py --all` | **0 render failures** |
| `bash scripts/test_rollback.sh` | **18 / 18** |
| `py_compile`, every repo Python script | **OK** |
| CI `protected-paths` rule against `ha-deploy` | **no protected path changed** |

Not verifiable from here: Lovelace schema, anything visual, the live
frontend. `hass check_config` is **SKIP** (no `hass`, no `/config`).

---

## 4. Preservation

| Compared with | Views | Entity refs | Nav targets | Service calls | Cards |
|---|---|---|---|---|---|
| `d22ce8e` (baseline) | 28 → 28 | 405 → 405 | 28 → 28 | 7 → 7 | 1,235 → 1,242 (+7) |
| `18a4e5d` (`ha-deploy`) | 28 → 28 | 405 → 405 | 28 → 28 | 7 → 7 | 1,238 → 1,242 (+4) |
| `autonomous/casaray-dev` | 28 → 28 | 405 → 405 | 28 → 28 | 7 → 7 | 1,242 → 1,242 |

The +7 cards are R2 (+3, Rooms conditions) and A2/A6 (+4, House health
setup and delivery status). **The dashboard, theme and package are
byte-identical to `autonomous/casaray-dev`.** The whole branch differs from
it only by the validator's deleted tail, `requirements-dev.txt`, the A3
correction and the documentation.

**No unresolved high-severity regression was found.** Open items that are
not regressions:

- CVA-001…014 (layout against the mobile mockup), all pre-existing.
- R7, R9 and R10 change Home's widths and heights, and nothing here can see
  them. **Needs a wall-iPad look** (P6).
- With `kiosk_mode` gone, Home Assistant's own header and sidebar show,
  which may change the resolved column count (CLAUDE.md, DR-013 note).
- The Bills-details subview shows the account and policy number helpers as
  tiles. That is the established BILL-001 design, since the first v2 build;
  it is noted here only because a wall display shows it.

---

## 5. Read-only inventory of the live deployment

### 5a. What could be inspected, and what could not

| Source | Used | Limits |
|---|---|---|
| Home Assistant connector (`GetLiveContext`), 29/10 | Yes, read-only | Friendly names, not IDs; only Assist-exposed entities; registry twins share names |
| `/config`, `configuration.yaml`, `.storage`, the dashboard list, Supervisor, logs, backups | **No** | No route from this environment. Each gap is recorded as a blocker or an owner check, not guessed |
| Repository deployment config | Yes | `packages/casaray_automation.yaml`, `scripts/casaray_safe_deploy.sh`, `scripts/sync_casaray_to_config.sh`, and the dashboard-only block `scripts/recovery/casaray_config_block.yaml` (`recovery/phase0-diagnostics` `e835fc5`) |

### 5b. Dashboard registration: **unknown (B1)**

| When | Evidence | Label |
|---|---|---|
| ~25/09 | Registration lost with `configuration.yaml` | [R] |
| 30/09 | `deploy_casaray.sh` appended the registration block, `packages:` included | [R] |
| 05/10 | Owner: "CasaRay is visible and navigates" | [O] via [R] |
| before 12/10 | Core update, then restart or reset; login failed | [O] via [R] |
| 18/10 | Restore plan superseded by "a dashboard-only registration" | [R]; whether it is currently registered: [I] not |
| 29/10 | Nothing named *CasaRay* is exposed to the connector | proves nothing about a dashboard |

### 5c. Missing helpers and people

The dashboard reads **118 helper, script and automation IDs that have no
definition in Git**, plus 3 that `packages/` defines and 3 `person`
entities (counts from `scripts/audit_casaray.py`):

| Kind | Count | Boards that read them | Live, 29/10 |
|---|---|---|---|
| `input_number` | 59 | `bills-details`, `bills`, `house-health` | *Gas Bill Usage MJ* (`input_number.gas_bill_mj`): `unavailable` |
| `input_datetime` | 26 | same | not exposed |
| `input_text` | 15 | `bills-details` | not exposed |
| `input_boolean` | 8 | the language toggle on every board; six bill-paid flags; `guest_mode` (People) | *Chinese Dashboard*: `unavailable` |
| `input_select` | 1 | `bills-details` | not exposed. (*Family Location*, `input_select.input_select_family_location_selected`, which no board reads, is `unavailable`) |
| `script` | 6 | `bills`, `bills-details` (record-a-payment) | not exposed |
| `automation` | 3 | `automations` | not exposed |
| `person` | 3 | `home`, `people`, `house-health` | **all three `unavailable`** |
| Defined in `packages/` | 3 helpers + `sensor.casaray_sync_status`, `sensor.casaray_backup_count`, `binary_sensor.casaray_live_file_present` | `house-health` | none exposed; present only if `packages:` loads |

References per board: `bills-details` 111, `bills` 34, `house-health` 22,
`automations` 4, `people` 2, and every other board 1 (the language toggle).

**Inference [I]:** every helper the connector can see is `unavailable`
rather than `unknown`, and so are the people. That is the pattern of
YAML-defined entities whose definitions went with `configuration.yaml`.
UI-made helpers would have survived in `.storage`. **P3 settles it.**

**What Git can restore:** the 7 on/off helpers, from
`proposals/casaray_helper_booleans.proposed.yaml` (arrived with A4; an
input_boolean has no settings to invent). It is **not installed**: loading it
needs `packages:` and the P3 answer. The other 102 helper IDs have no
settings in Git (ranges, options, initial values), so rebuilding them would
mean inventing values. Settings come from a pre-25/09 backup (the key was
lost; see the emergency kit, ENV-05) or from the owner. The 3 `person`
entities need the owner, in Settings → People.

Full ID list: Appendix B.

### 5d. Auto-deploy (B2)

| Item | Definition in Git | Live |
|---|---|---|
| `input_boolean.casaray_auto_deploy` | `packages/casaray_automation.yaml`, no `initial:`, so OFF on first load; a restored state wins after that | unknown, not exposed |
| `automation.casaray_nightly_safe_deploy` | 03:30 daily, conditioned on the helper being on | unknown |
| `shell_command.casaray_safe_deploy` → `/config/casaray/casaray_safe_deploy.sh` | `git fetch` + `git reset --hard origin/ha-deploy` in `/config/deez_repo`, then deploy; needs `python3` (present in Core's container) | unknown whether `/config/casaray/` is installed (`casaray_onboard.sh`) |
| 11 more `casaray_*` automations, 3 scripts, 3 command-line sensors | startup health check, out-of-sync, battery, internet, energy-stale and offline-spike notices | none exposed |

**Do not arm it.** Nothing here activates it, and P2 makes sure it is off
before any sync.

### 5e. Other deployment facts

- **Legacy dashboard:** a storage-mode dashboard at `deez-smart-home`. Its
  registration survived the 25/09 loss. It must never be added to
  `configuration.yaml` (url_path collision). Not touched.
- **Legacy deploy bridge:** the `shell_command` that ran
  `/config/deploy_deez_dashboard.sh` lived in the lost `configuration.yaml`.
  It is a protected area and was not touched.
- **Themes:** HA's regenerated default `configuration.yaml` includes
  `frontend: themes: !include_dir_merge_named themes`, and the sync copies
  `themes/deez_your_name.yaml`. The theme is unchanged since `63dc2b8`
  (15/09).
- **Resources:** `card-mod` and `webrtc-camera` are storage-mode Lovelace
  resources. They were not among the files lost on 25/09
  (`RECOVERY_2026-09.md`) [R], and CasaRay rendered on 05/10 [O].
  CasaRay no longer needs kiosk-mode.

---

## 6. Owner checks before any deploy (read-only, about 5 minutes)

| # | Check | Expected for GO | If not |
|---|---|---|---|
| **P1** | Open `/casaray-v2/home` | It loads (registered) | Unregistered: GO becomes a registration decision (section 7b), not a sync |
| **P2** | Settings → Entities, search `casaray_auto_deploy` | Absent, or present and **off** | If on, turn it off first. Otherwise 03:30 overwrites the candidate and resets the clone |
| **P3** | Settings → Devices & services → Helpers | Tells us whether *Chinese Dashboard* and the bill helpers are listed (UI helpers) or "not provided" (lost YAML helpers) | Decides whether the boolean proposal applies; it does not block the sync |
| **P4** | HACS → Frontend: is kiosk-mode installed? | Either is fine for CasaRay | If installed, the **legacy** dashboard can lock navigation; `?disable_km` bypasses it |
| **P5** | Settings → System → Backups: take a full backup and download it | Done | Do not deploy without it |
| P6 | After deploy: photograph Home on the wall iPad and the phone | No half-empty rows; alerts full width; More boards two across; Rooms rows open their room | `FAIL` rows to the verification queue; roll back if unusable |

---

## 7. Deployment (owner-run, after P1–P5)

### 7a. CasaRay is registered: dashboard-file sync, no restart

From the Terminal & SSH add-on. This never resets the host's clone:

```sh
cd /config/deez_repo
git fetch origin recovery/casaray-continuation
rm -rf /tmp/casaray_rc && mkdir -p /tmp/casaray_rc
git archive FETCH_HEAD | tar -x -C /tmp/casaray_rc
REPO=/tmp/casaray_rc sh /tmp/casaray_rc/scripts/sync_casaray_to_config.sh
```

Then hard-refresh the browser and the iPad. The sync writes only
`/config/dashboards/casaray_v2.yaml` and `/config/themes/deez_your_name.yaml`,
keeping a timestamped copy of each. On this shell it will say
`yaml parse: SKIPPED`; the branch's gate is the parse guarantee.

### 7b. CasaRay is unregistered: a separate decision

That needs `configuration.yaml` (protected) plus `ha core check` and a
restart. Use only the **dashboard-only** block, `casaray_config_block.yaml`
at `e835fc5`. Never use `deploy_casaray.sh` (withdrawn), and do not add
`packages:` in the same step: that would load the auto-deploy. Not
prepared further here, because it is a restart and needs its own approval.

### 7c. Not part of deploying

Installing the helper proposal, loading `packages/`, arming auto-deploy,
merging into `ha-deploy`, and changes to authentication or backups. Each is
its own owner decision.

---

## 8. Rollback

| What | How | Restores |
|---|---|---|
| Dashboard and theme | Copy back the sync's timestamped `.bak` copies in `/config/dashboards/` and `/config/themes/`, or run section 7a with `ha-deploy` instead of `recovery/casaray-continuation` | the previous file, or `18a4e5d` |
| With the maintenance suite installed | `sh /config/casaray/casaray_rollback.sh --list`, then restore by name (REG-016 fixed; 18/18 tests) | the named backup |
| Registration (only if 7b was done) | Remove the block, `ha core check`, restart | unregistered |
| Legacy dashboard | Nothing to do; never touched | — |
| Git | Nothing to do; this branch is additive, and `ha-deploy` and every source branch are unchanged | — |
| Whole instance (last resort, owner only) | The P5 backup, Home Assistant component only | the state before the deploy |

---

## 9. Still open (owner)

ENV-01…07 in the recovery report §11. In short: confirm registration (P1);
decide on the helpers (P3) and the people; passwords for the other three
users; a new backup key and emergency kit; the legacy kiosk block; the
legacy deploy bridge; and reading Core 2026.10's breaking changes before
any further update.

---

## Appendix A — commit map

`Recovery-Step` → new commit → original commit(s). Everything after
`d22ce8e` on this branch:

| Step | New | Original | Subject |
|---|---|---|---|
| R0 | `06ef9c2` | `fc208cd` | Remove CasaRay kiosk mode lockout configuration |
| R1 | `597d865` | `0d95183` | fix(P1): the Home chip strip fits one line; measure all 22 against the limit |
| R2 | `a8108c7` | `3fb9042` | ui(P2): lighter footers, plainer Lighting, compact Rooms conditions |
| R3 (1/7) | `762d5d2` | `d3b4fad` | skill: /improve-system — the improvement cycle, with its two missing tools |
| R3 (2/7) | `b9dcfd9` | `122852a` | audit: the export's availability column has expired, and a tool to notice |
| R3 (3/7) | `cc97979` | `a1a72d6` | skill: /automate — find repeated work, score it, build the strongest case |
| R3 (4/7) | `8080f83` | `9e6235b` | docs: evidence-based capability snapshot at a1a72d6 |
| R3 (5/7) | `7bfb41c` | `55631a1` | tooling: live screenshot capture for CasaRay views |
| R3 (6/7) | `b6b8d8c` | `f7856d9` | docs: stamp 55631a1 into the CAP-001..003 verification rows |
| R3 (7/7) | `5213d55` | `6accad8` | tooling: render fixture — the live pass was a second dark pass |
| R4 (1/4) | `f0bb648` | `2d42e1a` | fix: two cards that under-reported, found by rendering with data present |
| R4 (2/4) | `60232d8` | `bd49f14` | docs: stamp 2d42e1a into the CR-318/CR-319 verification rows |
| R4 (3/4) | `9b39c08` | `6ec8f20` | docs: renumber the new queue rows to CR-322/CR-323 |
| R4 (4/4) | `271bc4b` | `2fecd89` | tooling: next_id.py — stop numbering tracking rows by eye |
| R5 (1/2) | `831a0ba` | `b96067e` | fix(home): name what the attention count is made of; two truncating tiles |
| R5 (2/2) | `f7c0102` | `d182251` | docs: stamp b96067e into the CR-324/CR-325 verification rows |
| R6 (1/2) | `50401c9` | `fa816a1` | ui(home): One tap and Rooms move directly under Needs attention |
| R6 (2/2) | `1b6fdc2` | `cb9c684` | docs: stamp fa816a1 into the CVA-004 verification row |
| R7 | `1630022` | `8b2f91b` | Make Home attention alerts full width (CVA-005) |
| R8 | `78b40a5` | `1c90090` | Correct misleading Home room tile labels (CVA-012) |
| R9 | `0018040` | `4d40250` | Make More Boards labels readable on wall iPad |
| R10 | `4cde3eb` | `34ee88d` | Reduce One Tap card height on wall iPad |
| R11 | `c7fc7ee` | `8ce9721` | tooling: verify_change.sh — one pass, and git supplies the BEFORE |
| R12 | `7b4fc9c` | `2016214`, `53f18e9` | recovery(R12): owner CVA-013 room-centric Home summaries, with the REG-015 bilin |
| R12s | `35628ec` | `7f8e07c` | docs: stamp 53f18e9 into the REG-015 row |
| R13 (1/2) | `c29c2ed` | `9fbdbcb` | tooling: prove rollback works — 17 assertions, and a host drill |
| R13 (2/2) | `a928200` | `de84740` | docs: stamp 9fbdbcb into the CAP-004/CAP-005 rows |
| R14 | `8ceb202` | `032a705` | tooling: read-only disk report — and an S1 rollback bug it found |
| R14s | `76f53d1` | `5c106dc`, `86ec579` | recovery(R14s): CFG-004/REG-016 stamp and its correction |
| R15 | `8cdd804` | `7309bd8`, `18a4e5d`, `3eff5e0` | recovery(R15): validator tolerates a Python-less host shell, without the stale t |
| A1 | `3381c1a` | `eb630df` | tooling: whole-dashboard audit; entity gate accepts IDs Git defines |
| A2 | `b06404c` | `3e46561` | feat(house-health): Setup status card names why helpers read No data |
| A3 | `364aa49` | `ef9c7e2`, `3edf53e` | recovery(A3): regression suite, CI gate and independent-review workflow |
| A4 (1/2) | `d5e6ac3` | `693e743` | fix(bills): stop claiming nothing is owed when the helpers are not answering |
| A4 (2/2) | `8fb6a5d` | `4c83642` | test+docs: pin the bills fix; propose the seven helper booleans; live notes |
| A5 | `84e7f3a` | `8d16497` | test: pin that sirens, locks and camera privacy never actuate on a bare tap |
| A6 | `2b63dfb` | `a9456a3` | feat(house-health): dashboard delivery status from the maintenance package |
| A7 | `974d6b7` | `a414bec` | docs+test: autonomous backlog, project-state pointer, package template parse tes |
| A8 | `7971225` | `9f73e33` | fix(people): print no zeros when nobody is reporting a location |
| A9 (1/2) | `6825c18` | `5ffbe74` | fix(bills): one silent bill blocks the all-clear (review finding) |
| A9 (2/2) | `077c430` | `ac10385` | docs: correct helper counts to the audit's own numbers; backlog batches 10-11 |
| docs | `c2903bd` |  | docs(recovery): reconcile CLAUDE.md and PROJECT_STATE.md with the recovered bran |

## Appendix B — the 118 dashboard references with no definition in Git

From `python3 scripts/audit_casaray.py --json`, key `helpers_external`.

| Domain | Count | IDs (without the domain prefix) |
|---|---|---|
| `automation` | 3 | `bills_reset_ytd_totals`, `deploy_deez_dashboard_updates`, `gas_meter_pulse_counter` |
| `input_boolean` | 8 | `car_insurance_paid`, `chinese_dashboard`, `council_rate_paid`, `elec_bill_paid`, `gas_bill_paid`, `guest_mode`, `rego_paid`, `water_bill_paid` |
| `input_datetime` | 26 | `bill_history_car_insurance_due_date`, `bill_history_car_insurance_paid_date`, `bill_history_council_rates_due_date`, `bill_history_council_rates_paid_date`, `bill_history_electricity_due_date`, `bill_history_electricity_paid_date`, `bill_history_gas_due_date`, `bill_history_gas_paid_date`, `bill_history_rego_due_date`, `bill_history_rego_paid_date`, `bill_history_water_due_date`, `bill_history_water_paid_date`, `car_insurance_due`, `car_insurance_period_en`, `car_insurance_period_start`, `council_rate_due`, `council_rate_period_end`, `council_rate_period_start`, `elec_bill_due`, `elec_bill_period_start`, `gas_bill_due`, `gas_bill_period_start`, `rego_due`, `water_bill_due`, `water_bill_period_end`, `water_bill_period_start` |
| `input_number` | 59 | `bill_history_car_insurance_discount`, `bill_history_car_insurance_payment`, `bill_history_car_insurance_saving`, `bill_history_council_rates_discount`, `bill_history_council_rates_payment`, `bill_history_council_rates_saving`, `bill_history_electricity_discount`, `bill_history_electricity_payment`, `bill_history_electricity_saving`, `bill_history_gas_discount`, `bill_history_gas_payment`, `bill_history_gas_saving`, `bill_history_rego_discount`, `bill_history_rego_payment`, `bill_history_rego_saving`, `bill_history_water_discount`, `bill_history_water_payment`, `bill_history_water_saving`, `bills_original_ytd`, `bills_paid_ytd`, `bills_saved_ytd`, `car_insurance_actual_paid`, `car_insurance_amount`, `car_insurance_bill_before_discount`, `car_insurance_discount_percent`, `car_insurance_last_amount`, `car_insurance_saving`, `council_rate_amount`, `council_rate_last_amount`, `council_rates_actual_paid`, `council_rates_bill_before_discount`, `council_rates_discount_percent`, `council_rates_saving`, `elec_bill_amount`, `elec_last_bill_amount`, `electricity_actual_paid`, `electricity_bill_before_discount`, `electricity_discount_percent`, `electricity_saving`, `gas_actual_paid`, `gas_bill_amount`, `gas_bill_before_discount`, `gas_bill_mj`, `gas_discount_percent`, `gas_last_bill_amount`, `gas_saving`, `rego_actual_paid`, `rego_amount`, `rego_bill_before_discount`, `rego_discount_percent`, `rego_last_amount`, `rego_saving`, `water_actual_paid`, `water_bill_amount`, `water_bill_before_discount`, `water_bill_usage_kl`, `water_discount_percent`, `water_last_bill_amount`, `water_saving` |
| `input_select` | 1 | `bill_history_company` |
| `input_text` | 15 | `car_insurance_policy_number`, `car_insurance_provider`, `car_insurance_registration`, `car_insurance_vehicle`, `council_rate_assessment_number`, `council_rate_council`, `council_rate_property`, `elec_account_number`, `gas_account_number`, `rego_customer_number`, `rego_plate`, `rego_vehicle`, `water_account_number`, `water_property`, `water_provider` |
| `script` | 6 | `record_car_insurance_bill_payment`, `record_council_rates_bill_payment`, `record_electricity_bill_payment`, `record_gas_bill_payment`, `record_rego_bill_payment`, `record_water_bill_payment` |
