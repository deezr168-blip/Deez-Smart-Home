# CasaRay capability snapshot

**Audit date:** 2026-09-19T00:40:03Z
**Commit audited:** `a1a72d659a1d567f1916f64b697b9a2d2bcf5086` (`a1a72d6`)
**Branch:** `ha-deploy`, clean tree, identical to `origin/ha-deploy` and
`origin/claude/ha-dashboard-upgrades-wui7ig`
**Method:** implementation inspection plus execution where safe. Nothing below
is marked VERIFIED on the strength of documentation.

## Status vocabulary

| Label | Means |
|---|---|
| VERIFIED | Implementation exists and was executed successfully, in this audit or with cited evidence |
| IMPLEMENTED | Implementation exists and is coherent, but successful execution in its real target environment cannot be confirmed |
| PARTIAL | Some of the workflow exists; the complete path does not |
| PLANNED | Only documentation, notes or intent |
| MISSING | No implementation |
| OBSOLETE | Exists but superseded or no longer appropriate |

---

## 1. Executive summary

Claude can develop, validate, prove and publish CasaRay dashboard changes
**end to end inside the repository**, and cannot observe the result.

The authoring half of the workflow is strong and tested: structural YAML
editing, a 20-check validation pipeline, entity reconciliation against a
970-entity export, template rendering across live and dark states,
structural regression proof against any git ref, documentation, commit and
push to both branches. All of that ran successfully during this audit or
during the sessions that produced the commits above.

The observation half does not exist. This sandbox **cannot reach the Home
Assistant instance** — proven, not assumed: `homeassistant.local` does not
resolve and an HTTP request returns status `000`. There is no `/config`, no
`ha` CLI, and no supervisor. The only live channel is the Home Assistant MCP
connector, which offers **three read tools** and returns friendly names
without entity IDs.

**There is no `casaray-visual-audit` skill.** Two project skills exist:
`improve-system` and `automate`. No screenshot tooling is committed anywhere
in the repository, and no live screenshot is committed either — all eight
PNGs in `docs/mockups/` are design renders from 14–15 September. Every visual
correction so far has come from Ray photographing the wall iPad and Claude
reasoning over the image in conversation. That is image reasoning, not
computer vision, and the images are not persisted.

Measured against the seventeen-stage workflow in section 4, Claude covers
**10 of 17 stages (59%)** at VERIFIED or IMPLEMENTED.

The single largest gap is that nothing closes the loop between a change being
pushed and anyone knowing what it looks like.

---

## 2. Claude skill inventory

| Skill | Path | Purpose | Status | Invocation | Key dependencies |
|---|---|---|---|---|---|
| `improve-system` | `.claude/skills/improve-system/` | One autonomous improvement cycle: pick the highest-value safe change, verify entities live, implement, render templates, run gates, prove nothing lost, record, commit, push both branches | VERIFIED | `/improve-system`, or auto-trigger on dashboard/board/theme/gate work, live photos, "carry on" | `ha_validate.sh`, `preserve_check.py`, `render_cards.py`, HA MCP, git |
| `automate` | `.claude/skills/automate/` | Detect repeated manual workflows, score them deterministically, check existing tooling, build the strongest safe candidate, maintain the registry | VERIFIED | `/automate`, or auto-trigger on automation requests and self-noticed repetition | `procmem.py`, `inventory.py`, `.claude/process-memory.json` |

No `.claude/commands/`, no `.claude/agents/`, no subagent definitions.

### `improve-system` — detail

- **Inputs:** repository state, `docs/live/states_export_2026-09-05.txt`, HA
  MCP live state, `docs/mockups/`, owner photographs when supplied.
- **Outputs:** dashboard/theme/script edits, tracking-document rows, commits
  on both branches.
- **Modifies repository files:** yes. **Touches live HA:** read only, via MCP.
  **Git:** yes, including push. **Browser:** no. **Images:** consumes
  owner-supplied photographs and committed mockups; produces none.
- **Autonomous:** yes, within five stated stop conditions (approval boundary,
  unobtainable information, two materially different options, meaningful
  live-system risk, nothing worthwhile left).
- **Safety:** inherits `CLAUDE.md` and `MAINTENANCE.md` protected lists; never
  force-pushes; never modifies the legacy dashboard without instruction.
- **Maturity:** used to produce the last 6 commits. Its two bundled scripts
  both executed successfully in this audit.
- **Evidence:** commits `122852a`, `3fb9042`, `0d95183`, `d22ce8e`.

### `automate` — detail

- **Inputs:** observed command sequences, `.claude/process-memory.json`.
- **Outputs:** memory entries, ranked candidates with printed arithmetic,
  generated `AUTOMATION_REGISTRY.md`, and new tools when a candidate is HIGH
  and safe.
- **Modifies repository files:** yes. **Touches live HA:** no. **Git:** via
  the normal commit path. **Browser:** no. **Images:** no.
- **Autonomous:** yes for analysis and for building read-only/reversible
  tools; explicitly not for anything ending in a push, deployment, credentials,
  networks, or device actuation.
- **Has it generated another tool:** yes — `scripts/dashboard_edit.py`,
  from a HIGH candidate scoring 10 (8 occurrences).
- **Can it modify itself:** it is instructed to analyse itself and prune its
  own memory; it has not rewritten its own scripts.
- **Persistence:** `.claude/process-memory.json`, 6 workflows, secret-redacted
  on write (redaction tested — a bearer token, an HA token and a password all
  stored as `<redacted>` with no leakage into the signature).

---

## 3. Tool / script inventory

27 automation artefacts, grouped by capability rather than by file.

### 3.1 Validation pipeline — VERIFIED

`scripts/ha_validate.sh` (8 sections) → `scripts/dashboard_check.py`
(20 checks) + `scripts/yaml_check.py` + `scripts/reconcile_entities.py`.

Sections: YAML syntax and duplicate keys · dashboard structure, templates,
navigation, mass-damage · entity references against the export · protected
files · secrets and credentials · unexpected deletions · whitespace, conflict
markers, binaries · Home Assistant configuration validation.

**Executed in this audit: PASSED (8 sections), 2 advisory warnings.**
Section 8 SKIPs — no `hass` CLI, no `/config`, no reachable API.

Gates include four added in the last two days, each negative-tested: `15b`
badges, `15c` two-way `'on'` branches, `15d` footers, `15e` bilingual
vocabulary drift.

### 3.2 Entity reconciliation — VERIFIED

- `scripts/reconcile_entities.py` — every dashboard reference exists in the
  export, plus a `STALE` blocklist for IDs the export lists but that are
  known dead. Runs inside `ha_validate.sh` section 3. Current reading:
  casaray_v2 371 ok / 30 unknown / 29 unavailable.
- `scripts/audit_duplicate_entities.py` — 27 friendly names carrying two
  entity IDs; sorts into wrong / needs-Developer-Tools / no-action.
- `scripts/casaray_v2_entity_map.py` — legacy→v2 migration map. OBSOLETE for
  new work; historical reference.

### 3.3 Dashboard authoring — VERIFIED

`scripts/dashboard_edit.py` — `views`, `sections`, `show`, `grep`, `replace`,
`insert`, `delete`, `span`. Keeps `.bak`, supports `--dry-run`, refuses any
edit that would not re-parse or that changes the view count.

**Executed in this audit:** listed 28 views and Home's 12 sections, changed a
`column_span` and restored it, and refused an unparseable replacement leaving
no stray backup.

### 3.4 Template truthfulness — VERIFIED

`.claude/skills/improve-system/scripts/render_cards.py` — renders markdown
cards against a live-shaped state set and a fully dark one, both languages,
with optional width measurement against the observed wrap limit.

### 3.5 Regression proof — VERIFIED

`.claude/skills/improve-system/scripts/preserve_check.py` — structural diff
against any git ref (views, cards, entities, navigation, service calls), plus
one view card-for-card filtered by language.

### 3.6 Deployment chain — IMPLEMENTED (never executed on the real host)

`casaray_safe_deploy.sh` · `sync_casaray_to_config.sh` ·
`casaray_rollback.sh` · `casaray_health_check.sh` · `casaray_sync_status.sh` ·
`casaray_onboard.sh` · `casaray_kiosk_diagnose.sh` · `casaray_common.sh`.

All eleven `/config`-dependent scripts were exercised only against simulated
`/config` trees in a scratch directory. None has been observed running on the
Home Assistant host.

### 3.7 Git checkpointing — IMPLEMENTED, and stale

`scripts/checkpoint.sh` — append-only known-good record; `rollback-plan`
deliberately prints commands rather than running them.

Current state: known-good `68b76e3`, tagged `known-good/20260825-041406`,
**recorded 2026-08-25 — 25 commits ago — and marked
`deploy verified: UNVERIFIED`.**

### 3.8 Protected deployment auth — NOT INSPECTED BY POLICY

`deploy_env.sh`, `deploy_askpass.sh`, `deploy_diagnose.sh`, `DEPLOY_AUTH.md`.
`CLAUDE.md` forbids touching these without explicit instruction.

### 3.9 Home Assistant package — IMPLEMENTED

`packages/casaray_automation.yaml` (572 lines) — helpers, shell commands,
command-line sensors, template sensors, scripts, 12 automations. Parses in
validation; never confirmed loaded on the instance.

### 3.10 Automation meta-tooling — VERIFIED

`.claude/skills/automate/scripts/procmem.py` and `inventory.py`. Both
executed in this audit.

### 3.11 CI / hooks / scheduled automation — MISSING

No `.github/`, no `Makefile`, no task runner, no git hooks, no cron. The only
scheduled automation is inside the HA package, which is unconfirmed on the
instance.

---

## 4. CasaRay end-to-end workflow matrix

| # | Stage | Status | Responsible tool |
|---|---|---|---|
| 1 | Inspect current dashboard | VERIFIED | `dashboard_edit.py`, Read/Grep |
| 2 | Understand target / mockup | VERIFIED | `docs/mockups/` (8 renders), `docs/CASARAY_MOCKUPS_2026-09-14.md` |
| 3 | Inspect entities | PARTIAL | export VERIFIED; live read lacks entity IDs |
| 4 | Edit dashboard YAML | VERIFIED | `dashboard_edit.py`, Edit |
| 5 | Validate changes | VERIFIED | `ha_validate.sh` (8 sections / 20 checks) |
| 6 | Reconcile entities | VERIFIED | `reconcile_entities.py`, `audit_duplicate_entities.py` |
| 7 | Sync / deploy | IMPLEMENTED | `casaray_safe_deploy.sh`, `sync_casaray_to_config.sh` — needs the host |
| 8 | Verify HA configuration | MISSING | `ha core check` — no supervisor here; section 8 SKIPs |
| 9 | View live result | MISSING | no route to the instance |
| 10 | Capture screenshot | MISSING | no screenshot tooling; instance unreachable |
| 11 | Compare screenshot vs mockup | PARTIAL | Claude image reasoning on owner-supplied photos only |
| 12 | Identify visual defects | PARTIAL | same — no deterministic tooling |
| 13 | Repair defects | VERIFIED | `improve-system` + `dashboard_edit.py` |
| 14 | Repeat verification | PARTIAL | requires Ray to re-photograph |
| 15 | Update issue / status docs | VERIFIED | tracking documents, manual by design |
| 16 | Git commit | VERIFIED | git |
| 17 | Git push | VERIFIED | git, both branches |

**Coverage:** VERIFIED 9 + IMPLEMENTED 1 = **10 / 17 = 59%**.
PARTIAL 4, MISSING 3.

The three MISSING stages are consecutive (8, 9, 10) and are the same root
cause: no path from this sandbox to the running instance.

---

## 5. Visual capability assessment

**There is no `casaray-visual-audit` skill.** Searched
`.claude/skills/` — only `automate` and `improve-system` exist. Searched the
whole repository for `screenshot|playwright|puppeteer|chromium|selenium` in
scripts and config: the sole match is `ha_validate.sh`, and only because it
excepts `docs/mockups/*.png` from its binary check.

| Capability | Status | Note |
|---|---|---|
| Locate CasaRay mockups | VERIFIED | 8 PNGs + 1 HTML in `docs/mockups/`, dated 14–15 Sep |
| Locate current screenshots | MISSING | none committed; owner photographs are not persisted |
| Analyse a screenshot | PARTIAL | Claude reads images pasted into conversation |
| Compare screenshot vs mockup | PARTIAL | reasoning only |
| Structural visual comparison | MISSING | no tooling |
| Detect effective column count | PARTIAL | inferred from YAML + photo; `check 15` gates half-empty rows structurally |
| Identify orphaned cards | VERIFIED (structural) | `dashboard_check.py` check 15, negative-tested |
| Identify excessive whitespace | PARTIAL | only the half-empty-row case is gated |
| Identify wrapping | PARTIAL | `render_cards.py --width` estimates against a limit read off one photograph; not measured |
| Card size differences | VERIFIED (structural) | check 14 requires declared geometry |
| Inspect theme differences | IMPLEMENTED | local Chromium rendering works (verified in this audit) |
| Correlate defect to YAML | VERIFIED | done repeatedly; e.g. the Sensibo "Entity not found" cards |
| Structured visual audit report | MISSING | no generator |
| Machine-readable visual report | MISSING | — |
| Auto-repair visual findings | PARTIAL | repair VERIFIED once a human identifies the defect |
| Capture a live screenshot | MISSING | proven unreachable |
| Repeat audit after repair | PARTIAL | requires a new photograph from Ray |

### Image reasoning vs computer vision — the distinction matters

Everything in the "visual" column so far is **Claude reasoning over an image
Ray pasted into the conversation**. There is no deterministic pixel
comparison, no layout extraction, no diffing. The one quantitative visual
measurement in the codebase — `render_cards.py`'s wrap budget — is calibrated
from a single number estimated off a photograph (≈45 characters at 1.0em) and
the script says so in its own header.

### What the environment can actually do

Chromium **is** present at `/opt/pw-browsers/chromium-1194` and renders local
HTML headlessly — verified in this audit by producing a PNG. The Playwright
Python package is **not** installed. So local rendering of the theme or a
hand-built HTML replica is possible; rendering the real dashboard is not,
because the dashboard needs a running Home Assistant.

---

## 6. Entity / state capability assessment

| Capability | Status | Tool |
|---|---|---|
| Extract all dashboard entity references | VERIFIED | `reconcile_entities.py`, `preserve_check.py` |
| Compare refs against the export | VERIFIED | `ha_validate.sh` section 3 |
| Identify entities missing from the export | VERIFIED | fails the build |
| Detect `unknown` state | VERIFIED (export) | 30 unknown in casaray_v2 |
| Detect `unavailable` state | VERIFIED (export) | 29 unavailable |
| Detect duplicate friendly names | VERIFIED | `audit_duplicate_entities.py` — 27 found |
| Identify renamed entities | PARTIAL | pattern-based; the Sensibo rename was found only because Ray photographed the failure |
| Suggest replacement entities | PARTIAL | requires judgement; no automatic mapping |
| Query live HA state | IMPLEMENTED | `GetLiveContext` — exposed entities only, **no entity IDs** |
| Distinguish "not exposed" from "does not exist" | **MISSING** | an empty result is ambiguous; documented in `evidence-rules.md` |
| Compare historical export vs live | PARTIAL | done by hand this week; no tool |
| Produce reconciliation reports | VERIFIED | both scripts print structured output |
| Safely apply reconciliations | PARTIAL | edits are safe and gated; deciding the mapping is human |

### Hard limits on live visibility

1. **`GetLiveContext` returns friendly names, not entity IDs.** Where two
   entities share a name — 27 such names exist — it cannot say which is which.
   Evidence from this audit: the `light` domain returns "Dining", "Living
   room", "NightLight" and "Hue ambiance spot 1" each **twice**, with no
   identifier to tell them apart.
2. **Exposure is domain-dependent, not uniformly reduced.** `light` returns
   26 entities and the export also holds 26 — complete. The `update` domain
   returns "No exposed entities found". So absence from `GetLiveContext` is
   *not* evidence of non-existence.
3. **The export's availability column goes stale.** Confirmed 19/09: three
   contact sensors, two camera streams and a privacy switch had all recovered
   while the 05/09 export still called them `unavailable`. Recorded in
   `CLAUDE.md`.
4. **No read access at all** to HA configuration, automations, scripts,
   dashboards, the device/area registry, or any file on the host.

---

## 7. Deployment capability assessment

| Operation | Status | Runs how |
|---|---|---|
| Edit canonical CasaRay source | VERIFIED | autonomous |
| Validate YAML | VERIFIED | autonomous |
| Validate navigation | VERIFIED | autonomous — 261 targets, 0 broken |
| Validate entity refs | VERIFIED | autonomous |
| Make a checkpoint / backup | IMPLEMENTED | `checkpoint.sh`; last record 25 commits old |
| Sync source into `/config` | IMPLEMENTED | **Ray runs it on the host** |
| Execute `ha core check` | MISSING here | no supervisor; pre-flight inside `casaray_safe_deploy.sh` |
| Reload / restart anything | MISSING / blocked | deliberately never automated |
| Verify dashboard deployment | MISSING | no route |
| Detect deployment failure | IMPLEMENTED | post-flight in `casaray_safe_deploy.sh`, host-side |
| Rollback | IMPLEMENTED | `casaray_rollback.sh`, host-side |
| Restore known-good | IMPLEMENTED | `checkpoint.sh rollback-plan` prints, never executes |
| Commit source | VERIFIED | autonomous |
| Push branches | VERIFIED | autonomous |

**Committed ≠ live.** CasaRay reaches `/config/dashboards/` only when Ray runs
`scripts/sync_casaray_to_config.sh`. `/config/deploy_deez_dashboard.sh` syncs
the legacy dashboard only.

**Known prior failure:** `casaray_safe_deploy.sh` originally decided the
supervisor-CLI check in post-flight, so a host without `ha` would deploy then
immediately revert, nightly, forever. Fixed in `3c40913` by moving it to
pre-flight with a `--no-core-check` opt-out. Never re-tested on the host.

---

## 8. Git capability assessment

| Capability | Status | Evidence |
|---|---|---|
| status / diff / log | VERIFIED | used throughout |
| Branch inspection | VERIFIED | — |
| Commit | VERIFIED | 8 commits in the audited range |
| **Push** | **VERIFIED** | `HEAD`, `origin/ha-deploy` and `origin/claude/ha-dashboard-upgrades-wui7ig` all resolve to `a1a72d6` |
| Fetch / pull | VERIFIED | `git fetch origin ha-deploy` |
| Branch synchronisation | VERIFIED | both-branch push is the standing convention |
| Backup branches | IMPLEMENTED | tags via `checkpoint.sh` |
| Rollback / checkpointing | IMPLEMENTED | prints a plan; never executes |
| Handling dirty unrelated files | VERIFIED | validation section 6 catches unexpected deletions |
| Commit SHA stamping | IMPLEMENTED | `CLAUDE.md` two-commit convention; used inconsistently |
| Avoiding destructive operations | VERIFIED | `--force`, `-f`, `reset --hard origin/*` denied in settings |

**Push credentials are not a limitation.** Pushing works from this
environment, to both branches, over HTTPS to
`github.com/deezr168-blip/Deez-Smart-Home`.

---

## 9. Home Assistant access / control assessment

### Read — 3 tools

| Tool | Returns |
|---|---|
| `GetLiveContext` | entity states by domain/area/name: friendly name, domain, state, area, a few attributes. **No entity IDs.** Exposed entities only. |
| `todo__get_items` | Shopping list items |
| `llm__GetDateTime` | instance date/time |

No read access to configuration, automations, scripts, dashboards, the
registry, or files.

### Write / control — ~21 tools, all blocked

`HassTurnOn/Off`, `HassLightSet`, `HassClimateSetTemperature`,
`HassFanSetSpeed`, `HassSetPosition`, `HassStopMoving`, volume and media
tools, `HassBroadcast`, `HassCancelAllTimers`, and the three todo mutators.

No tool exists for editing HA files, reloading, restarting, or deploying a
dashboard.

### Safeguards — VERIFIED

`scripts/deny_device_control.py`, wired as a `PreToolUse` hook on matcher
`.*Hass.*`. Matches by tool **name**, anchored `(?:^|__)…$`, deliberately not
by server name — the connector's server id has already changed once.

**Tested in this audit, 7/7 correct:**

```
DENY   mcp__Home_Assistant__intent__HassTurnOn
DENY   mcp__Home_Assistant__light__HassLightSet
DENY   mcp__Home_Assistant__todo__HassListAddItem
allow  mcp__Home_Assistant__homeassistant__GetLiveContext
allow  mcp__Home_Assistant__llm__GetDateTime
allow  mcp__Home_Assistant__todo__get_items
allow  Bash
```

Malformed payload → silent, exit 0 (does not wedge the session).

### Finding: the `permissions.deny` list does not match real tool names

`.claude/settings.json` denies `mcp__Home_Assistant__HassTurnOn`. The actual
tool is `mcp__Home_Assistant__intent__HassTurnOn` — the sub-namespace
(`intent__`, `light__`, `climate__`, `todo__`, `media_player__`,
`assist_satellite__`, `fan__`) is missing from every one of those 21 entries.

The hook is therefore doing the protecting, alone. This is a **defence-in-depth
gap, not an open hole** — the hook was verified above and covers every case.
Recommended: update the deny entries to the real names, or to
`mcp__Home_Assistant__*__Hass*`. Not changed during this audit, because the
brief says not to loosen or alter safeguards while auditing.

---

## 10. Autonomous operation boundaries

### SAFE AUTONOMOUS
Reading anything in the repository · `dashboard_edit.py` (all subcommands,
backed up and refusing bad parses) · `ha_validate.sh` and every gate ·
`reconcile_entities.py` · `audit_duplicate_entities.py` · `render_cards.py` ·
`preserve_check.py` · `procmem.py`, `inventory.py` · local Chromium rendering ·
`GetLiveContext`, `get_items`, `GetDateTime` · editing tracking documents ·
`git status/diff/log/fetch`.

### AUTONOMOUS WITH GUARDRAILS
Editing `dashboards/casaray_v2.yaml`, `themes/`, `scripts/`, `packages/` —
requires a passing `ha_validate.sh` and a clean `preserve_check.py` ·
adding a gate — requires a negative test · `git commit` and `git push` to the
two designated branches · creating new tooling — requires the `automate`
inventory check first.

### HUMAN INPUT REQUIRED (Ray)
Running `sync_casaray_to_config.sh` on the host · anything needing a
screenshot of the live dashboard · running `casaray_kiosk_diagnose.sh`
(`DR-015` is blocked on this) · confirming which twin of a duplicated entity
name is real (`CR-320`, needs Developer Tools) · `ha core check` and any
reload · choosing between materially different design options (`CR-312`) ·
legacy-dashboard changes (`CR-321`).

### DO NOT AUTONOMOUSLY EXECUTE
Any Hass\* actuator (hook-blocked) · force-push or history rewrite
(settings-denied) · `rm -rf /config*` (settings-denied) · editing
`secrets.yaml` or `.storage/**` (settings-denied) · the deployment-auth files ·
HA restart/reload · credential, network or firewall changes · deleting live
entities, devices or integrations.

---

## 11. Current orchestration capability

`improve-system` is the orchestrator. It coordinates inspect → modify →
validate → verify-no-loss → document → commit → push, and explicitly stops
where evidence runs out.

Against the section-4 stage list it drives **10 of 17 stages (59%)**:

| Bucket | Stages | Count |
|---|---|---|
| VERIFIED | 1, 2, 4, 5, 6, 13, 15, 16, 17 | 9 |
| IMPLEMENTED | 7 | 1 |
| PARTIAL | 3, 11, 12, 14 | 4 |
| MISSING | 8, 9, 10 | 3 |

It does **not** orchestrate deploy → verify → visual-repair, because stages
8–10 have no implementation. Its own documentation states this rather than
claiming the loop is closed.

---

## 12. Repeated-process automation capability

**`automate`**, at `.claude/skills/automate/`. VERIFIED.

- **Observes** repeated work: `procmem.py observe` groups piped commands by
  normalised shape (literals, numbers, git revisions and filenames collapse).
- **Records**: `.claude/process-memory.json`, 6 workflows, with occurrences,
  dates, files, minutes, failures, determinism.
- **Scores**: deterministic, six bounded dimensions, `--explain` prints the
  arithmetic. Two occurrences cannot reach HIGH.
- **Checks existing tooling first**: `inventory.py` across scripts, skills, HA
  packages, hooks and CI — 27 artefacts, each described from its own source.
- **Creates tools**: yes — `scripts/dashboard_edit.py` came from a HIGH
  candidate scoring 10 on 8 occurrences.
- **Registry**: `AUTOMATION_REGISTRY.md`, generated, 5 in place / 1 candidate.
- **Self-modification**: instructed to analyse and prune itself; has not
  rewritten its own scripts.
- **Safeguards**: secret redaction (tested); explicit refusal to autonomously
  automate pushes, deployment, credentials, networks or device control.

**Validation evidence:** seeded from real session history, the scorer
independently rediscovered the tools already built for those workflows —
`render_cards.py` HIGH on 6 occurrences, `preserve_check.py` LOW on 2. The
LOW is documented as a score correctly overridden on consequence.

**Outstanding candidate:** "validate, commit, push both branches" scores 11
(16 occurrences) and is deliberately unbuilt — it ends in a push.

---

## 13. Known limitations

1. **Cannot reach the Home Assistant instance.** Proven: `homeassistant.local`
   does not resolve; HTTP returns `000`. No `/config`, no `ha` CLI.
2. **Cannot capture a live screenshot.** No tooling, and no route if there
   were. Chromium renders local HTML only.
3. **No `casaray-visual-audit` skill exists**, and no visual audit report
   format exists.
4. **Visual comparison is reasoning, not measurement.** Owner photographs
   pasted into conversation; not persisted; no pixel or layout diffing.
5. **`GetLiveContext` returns no entity IDs**, so 27 duplicated friendly names
   cannot be resolved live.
6. **Absence from `GetLiveContext` is ambiguous** — not exposed vs does not
   exist.
7. **The export is 14 days old** and its availability column is demonstrably
   stale; it remains authoritative only for which IDs exist and their names.
8. **The whole deployment chain is unexecuted on the real host.** It has one
   known prior failure mode, fixed but unretested.
9. **The known-good checkpoint is 25 commits stale** and marked
   `deploy verified: UNVERIFIED`.
10. **`ha core check` cannot run here**; validation section 8 always SKIPs.
11. **No CI, no git hooks, no task runner.** Every gate depends on someone
    remembering to run `ha_validate.sh`.
12. **The `permissions.deny` HA entries do not match real tool names**; the
    PreToolUse hook is the only effective device-control guard (it is
    verified, but the second layer is inert).
13. **Two open items are blocked on Ray:** `DR-015` (kiosk-mode host
    diagnosis) and `CR-312` (chip-strip wrapping decision).
14. **Playwright Python is not installed**, though Chromium binaries are.

---

## 14. Three highest-value next improvements

Ranked on manual work removed, reliability gained, and how close existing
tooling already is.

### 1 — Close the observation loop: get a live screenshot into the repository

**Removes:** the only genuinely manual step in every visual cycle. Today Ray
photographs the wall iPad, pastes it into chat, and the image is lost when the
conversation ends. It unblocks stages 9, 10, 11, 12 and 14.

**Gains:** visual regressions become comparable across commits instead of
across memories.

**Closeness:** moderate. Chromium is present and works; what is missing is a
route to Home Assistant and a credential. The realistic first version is
host-side — a small script Ray runs on the HA host (or a HA automation) that
captures `/casaray-v2/<view>` and writes a PNG into the repository clone, so
Claude reads it from git rather than from a conversation. That reuses the
existing `deez_repo` clone and the existing sync convention.

### 2 — A CI check, or a pre-commit hook, running `ha_validate.sh`

**Removes:** the possibility of pushing an unvalidated dashboard. Currently
every gate depends on discipline.

**Gains:** the 20 structural checks and 4 honesty gates become unskippable
rather than customary. Note the gates exist *because* four classes of defect
reached the wall; nothing currently forces them to run.

**Closeness:** very close. `ha_validate.sh` already exits non-zero correctly
and has no host dependencies for 7 of its 8 sections. This is a small file,
and it is the cheapest reliability gain available.

### 3 — A live-state snapshot tool that captures entity IDs

**Removes:** the hand reconciliation that consumed most of the 19/09 audit,
and unblocks `CR-320` permanently.

**Gains:** kills limitations 5, 6 and 7 at once. A fresh export with real
availability would have made the Sensibo failure visible before it reached the
wall, rather than two weeks after.

**Closeness:** moderate, and it is host-side rather than sandbox-side —
`GetLiveContext` structurally cannot provide IDs. The existing B1 export
process already produces exactly the right format; what is missing is a way to
regenerate it on a schedule and land it in the repository, which is the same
delivery problem as improvement 1 and could share its mechanism.

---

## 15. Audit provenance

- **Date:** 2026-09-19T00:40:03Z
- **Commit:** `a1a72d659a1d567f1916f64b697b9a2d2bcf5086`
- **Validation at audit time:** `ha_validate.sh` → PASSED (8 sections), 2
  advisory warnings, section 8 SKIPPED (no host).
- **Executed during this audit:** `ha_validate.sh`, `dashboard_edit.py`
  (`views`, `sections`, `grep`, `span`, `replace --dry-run`, refusal path),
  `deny_device_control.py` (7 cases + malformed), `procmem.py`,
  `inventory.py`, `checkpoint.sh show`, `GetLiveContext` (light domain),
  Chromium headless render, DNS and HTTP reachability probes.
- **Not executed:** every `/config`-dependent script (11), `ha core check`,
  the HA package.

### Key files another AI should know about

| File | Role |
|---|---|
| `dashboards/casaray_v2.yaml` | canonical dashboard, 14,054 lines, 28 views |
| `dashboards/deez_smart_home.yaml` | legacy baseline — do not modify |
| `themes/deez_your_name.yaml` | CasaRay theme and `--casaray-*` tokens |
| `packages/casaray_automation.yaml` | HA-side maintenance package |
| `docs/live/states_export_2026-09-05.txt` | 970-entity authority for IDs and names |
| `docs/mockups/` | 8 design renders — the visual target |
| `CLAUDE.md` | permanent rules and architecture |
| `PROJECT_STATE.md` | coordination state, 2,739 lines |
| `LIVE_VERIFICATION_QUEUE.md` | CR-### rows awaiting live confirmation |
| `DASHBOARD_ISSUES.md` | DR-### design findings |
| `DEPLOYMENT_BLOCKERS.md` | what cannot be verified from the build environment |
| `MAINTENANCE.md` | protected paths |
| `AUTOMATION_REGISTRY.md` | generated automation registry |
| `.claude/settings.json` | permissions and the PreToolUse hook |
| `.claude/process-memory.json` | workflow repetition memory |
| `scripts/ha_validate.sh` | the gate that decides whether a change may ship |

---

## MEMORY UPDATE SUMMARY

*Paste-ready state summary. Current as of commit `a1a72d6`, 2026-09-19.*

**Architecture.** `Deez-Smart-Home`, branch `ha-deploy`, mirrored to
`claude/ha-dashboard-upgrades-wui7ig`. Two Lovelace dashboards:
`dashboards/casaray_v2.yaml` is canonical (14,054 lines, 28 views, url_path
`casaray-v2`, two-column baseline, bilingual on
`input_boolean.chinese_dashboard`, native-first with one custom card type);
`dashboards/deez_smart_home.yaml` is the legacy rollback baseline and must not
be modified. Theme `themes/deez_your_name.yaml` holds all `--casaray-*`
colour tokens; the dashboard carries no hardcoded colour. Design target is
eight owner renders in `docs/mockups/`.

**Claude skills (both new, both verified).**
`improve-system` — one autonomous improvement cycle: choose the highest-value
safe change, verify entities against the live instance, edit, render
templates across live and dark states, run the gates, prove nothing was lost,
record, commit, push both branches. Bundles `render_cards.py` and
`preserve_check.py`.
`automate` — detects repeated manual workflows, scores them deterministically,
checks existing tooling before building, maintains `AUTOMATION_REGISTRY.md`.
Bundles `procmem.py` and `inventory.py`, persists to
`.claude/process-memory.json`.
**No `casaray-visual-audit` skill exists.**

**Newly automated.** `scripts/dashboard_edit.py` (locate/splice dashboard
sections; backs up, dry-runs, refuses edits that would not re-parse) —
generated by `automate` from a HIGH candidate. `scripts/audit_duplicate_entities.py`
(27 duplicated friendly names). Four validation gates added and
negative-tested: badges, two-way `'on'` branches, footers, bilingual
vocabulary drift. `dashboard_check.py` now carries 20 checks;
`ha_validate.sh` has 8 sections.

**Live access.** Home Assistant MCP only: `GetLiveContext`, `todo get_items`,
`GetDateTime`. **The sandbox cannot reach the instance** —
`homeassistant.local` does not resolve, HTTP returns 000, there is no
`/config` and no `ha` CLI. `GetLiveContext` returns friendly names **without
entity IDs**, so 27 duplicated names cannot be resolved live; exposure is
domain-dependent, so absence is not proof of non-existence. The 05/09 export
is authoritative for IDs and names but its availability column is stale —
three contact sensors, two camera streams and a privacy switch had recovered
by 19/09 while the export still called them unavailable.

**Visual audit.** Reasoning only. Claude reads photographs Ray pastes into
conversation; those images are not persisted and no live screenshot is
committed. No pixel or layout diffing, no report format, no capture ability.
Chromium is available for rendering local HTML (verified) but cannot render
the real dashboard. The one quantitative visual figure — the chip-strip wrap
budget — is estimated from a single photograph, not measured.

**Deployment.** Claude edits, validates and pushes; it does not deploy.
CasaRay reaches `/config/dashboards/` only when Ray runs
`scripts/sync_casaray_to_config.sh` on the host. `casaray_safe_deploy.sh`,
`casaray_rollback.sh`, `casaray_health_check.sh`, `casaray_onboard.sh` and
`casaray_kiosk_diagnose.sh` are implemented and were tested only against
simulated `/config` trees — never on the real host. `ha core check` cannot run
here; validation section 8 always skips. **Committed is not live.**

**Safeguards.** `scripts/deny_device_control.py` runs as a `PreToolUse` hook
on `.*Hass.*` and denies every device actuator by tool name; verified 7/7
this audit, fails safe on malformed input. Settings deny force-push,
`reset --hard origin/*`, `rm -rf /config*`, and edits to `secrets.yaml` and
`.storage/**`. Note: the HA entries in `permissions.deny` omit the tool
sub-namespace (`intent__`, `light__`, …) and therefore do not match real tool
names — the hook is the only effective guard, and updating those entries is a
small outstanding fix.

**Git.** Commit and push are VERIFIED; credentials are not a limitation. HEAD
and both remote branches are identical at `a1a72d6`. The known-good
checkpoint is stale — `68b76e3`, 2026-08-25, marked `deploy verified:
UNVERIFIED`.

**Workflow coverage.** 10 of 17 end-to-end stages at VERIFIED or IMPLEMENTED
(59%). Missing: verify HA configuration, view live result, capture
screenshot — all three the same root cause. Partial: live entity inspection,
screenshot-vs-mockup comparison, visual defect identification, repeat
verification.

**Blocked on Ray.** `DR-015` — run `scripts/casaray_kiosk_diagnose.sh` on the
host to find why HA's header still renders beside CasaRay's nav rail.
`CR-312` — choose how four over-width chip strips should behave. `CR-320` —
confirm in Developer Tools which twin of seven duplicated entity names is
real. `CR-321` — the legacy dashboard references a dead entity twin.

**Immediate next tooling priority.** Get a live screenshot into the
repository, host-side, so visual comparison stops depending on a conversation.
Then a CI check or pre-commit hook running `ha_validate.sh`, which is close to
free and makes the gates unskippable. Then a scheduled live-state export
carrying real entity IDs, which would retire the staleness and duplicate-twin
limitations together.
