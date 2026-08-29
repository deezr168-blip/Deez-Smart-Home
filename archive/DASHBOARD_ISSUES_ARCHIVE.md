# Dashboard issues archive

Full evidence for **resolved** findings, moved out of `DASHBOARD_ISSUES.md`
to keep the recurring read cheap. Every finding here is fixed and its current
status is tracked in `DASHBOARD_ISSUES.md`.

**No unresolved regression's evidence is archived.** Read this file only when
investigating a recurrence of one of these findings.

---

## Regression audit — 2026-08-29

Scheduled regression audit against `ha-deploy` HEAD `7f304ad`. Reviewed the 12
commits since the last recorded batch (`ae89134`..`f04a59f`: camera dedup,
iPad column retuning, glass-to-theme migration, Mushroom→Tile conversions,
the iPad Command Center rebuild, the last nested-`grid` dissolution, the
media-player dedup, and the three-commit bilingual pass) against the current
`dashboards/deez_smart_home.yaml`, plus a full-file sweep for the standing
regression categories (navigation, duplicate controls, reassuring false
status, unguarded numeric fallbacks, language-toggle consistency, iPad
layout). No previous `REG-` audit exists in this file, so this is the
baseline.

**Clean:** all 130 `navigate` targets resolve to one of the 36 declared view
paths; zero same-view duplicate entity controls; zero nested `grid` cards
remain (9b28fdb's dissolution is complete); all ~50 converted Tile cards
carry the features their Mushroom predecessors had (color-temp, cover
position); all 38 `float(0)` casts are properly guarded by a prior
unavailable/unknown/none check, and no `float(100)`/`float(9999)` sentinel
exists anywhere; every `max_columns` in the file is ≤2; the iPad Command
Center's 4-section structure matches its commit message with no drift; all
6 camera back-chips are bilingual; no inverted or scope-leaking `cn`
template variable found anywhere.

**Findings** (severity per task scale: CRITICAL / HIGH / MEDIUM / LOW):

| ID | Sev | View / component | Evidence | Suspected commit | Recommended action | Status |
|---|---|---|---|---|---|---|
| REG-001 | MEDIUM | `security` — 3 door cards (Living Room Door, Main/Parents Door, Back Door) | Lines 2192, 2200, 2208: `{{ ''Open'' if v == ''on'' else ''Closed'' }}` is bare English inside a template whose own "Sensor offline" fallback, one clause earlier in the same string, IS bilingual. Identical door-state logic elsewhere in the file (lines 647, 1059, 3694, 3705, 3716) already reads `''开启'' if cn else ''Open''` / `''关闭'' if cn else ''Closed''`. | `fa286de` (UI-028) — that commit's own message lists Open/Closed among the words it translated, but these three cards were missed. | Wrap the Open/Closed clause the same way as the other five instances in the file. | FIXED — AWAITING LIVE VERIFICATION |
| REG-002 | MEDIUM | `lights` quick-status chip + `cameras` quick-status chip ("Motion"/"Quiet") | Lines 3020-3027 (`lights`) and 1611-1620 (`cameras`): both aggregate several `binary_sensor.*_motion` entities with `select('eq','on') | count > 0`, no unavailable/unknown branch, and bare English text. If every watched sensor goes unavailable, `count` is 0 and the chip confidently shows "Quiet" — the exact reassuring-false-state anti-pattern this project's own process note calls out (root cause of UI-002/005/006/008/018/020). Also untranslated regardless of the Chinese toggle. | Predates tracked batch history — from the `61273b1` baseline sync (2026-08-25), before `d01e813` established tracking. Not introduced by the 12 audited commits, but never caught by the UI-006 guard pass or the three bilingual passes that touched nearly every other status chip in the file. | Add a `bad = [unavailable, unknown, none]` branch (grey/"—") ahead of the count check, and bilingual text, matching the treatment already used on the sibling per-sensor motion cards a few lines above line 3025. | FIXED — AWAITING LIVE VERIFICATION |
| REG-003 | MEDIUM | `home` — Network nav chip | Lines 547-548: `icon_color: '{{ ''green'' if is_state(''binary_sensor.eero_wan_status'',''on'') else ''red'' }}'` — two-branch only, no unavailable guard, so a dropped WAN sensor shows confident red rather than an unknown state. The dedicated `network` view fixed this exact pattern (`a5dc914`); this duplicate summary chip on `home` was missed. | Predates tracked batch history (`61273b1` baseline). Not fixed by `a5dc914`, which only touched the `network` view itself. | Add a third `grey` branch for unavailable/unknown, mirroring `a5dc914`'s treatment on the Network view. | FIXED — AWAITING LIVE VERIFICATION |
| REG-004 | LOW | `people-locations` — per-person markdown loop | Line 2872: the "at home" (🟢) branch renders the bare English word `home` regardless of the toggle, while the "away" branches on the same line are properly bilingual (`距家 {{ d }} 公里` / `{{ d }} km away`). | `f04a59f` — the commit whose stated purpose was closing exactly this class of gap (number/fragment-glued bilingual text) touched this template and missed the most common case. | Wrap as `{{ ''在家'' if cn else ''home'' }}`. | FIXED — AWAITING LIVE VERIFICATION |
| REG-005 | LOW | `ipad-command-center` — WAN chip | Line 3662: the unavailable-state fallback renders literal `WAN —` in both languages, while the sibling Online/Offline branches on the same line are bilingual, and an equivalent unavailable case elsewhere in the file (~line 1623, "网络无数据") is translated. | `fa286de` | Matched the sibling unavailable-case wording elsewhere in the file rather than translating the dash literally: now reads `{{ ''网络无数据'' if cn else ''WAN not reporting'' }}`, same phrase as line ~1623. English text changes from "WAN —" to "WAN not reporting" as a result — flag if the owner wanted the dash kept. | FIXED — AWAITING LIVE VERIFICATION |
| REG-006 | LOW | `home` — Energy tile secondary | Line 450: bare lowercase `offline` fallback sits untranslated next to `''太阳能'' if cn else ''Solar''` in the same template. | Originally introduced `a49ca72` (2026-08-25, pre-tracked-history); `f04a59f` edited this exact line for an unrelated word and left `offline` untouched. | Wrap as `{{ ''离线'' if cn else ''offline'' }}`. | FIXED — AWAITING LIVE VERIFICATION |

No CRITICAL or HIGH findings. No broken navigation, no lost functionality,
no duplicate controls, no invalid subview references, no card-config or
grid-structure regressions, and no unguarded numeric sentinels were found in
the audited commits or the file as a whole.

---
