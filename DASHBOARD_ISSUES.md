# Dashboard issue tracker

Authoritative regression and bug record for `dashboards/deez_smart_home.yaml`.
Check unresolved issues before planning a batch; fix high-severity
regressions before cosmetic work.

## Statuses

| Status | Meaning |
|---|---|
| `OPEN` | Identified, not yet worked on |
| `IN PROGRESS` | Being worked on now |
| `FIXED — AWAITING LIVE VERIFICATION` | Change committed and validated in the repository; the visible result has **not** been seen on the live dashboard |
| `VERIFIED` | Confirmed correct on the live Home Assistant frontend by the owner |

**A passing `ha_validate.sh` run never justifies `VERIFIED`.** This
environment cannot reach the instance, cannot check Lovelace schema and
cannot confirm an entity exists. Anything depending on the real frontend or
live entity data stays `FIXED — AWAITING LIVE VERIFICATION` until the owner
confirms it.

Severity: **S1** wrong/unsafe information · **S2** broken function or
navigation · **S3** layout or readability · **S4** polish.

ID series: `UI-` dashboard cards and views · `REG-` regressions and tracking
integrity · `BILL-` billing views and store · `DR-` design review ·
**`CFG-` Home Assistant configuration outside this repository** — a defect
seen on the live instance whose cause and fix live in HA's own config
(`.storage/`, an integration), not in any tracked file here. A `CFG-` item is
never fixed by a push to this branch, and never enters the verification
queue: the queue is for deployed changes awaiting a look, whereas a `CFG-`
item is awaiting a *diagnosis* the owner alone can perform.
**Closing a `CFG-` item still requires live verification.** The fix is
applied in Home Assistant by the owner rather than pushed from here, so the
close condition is the owner re-reading the affected surface and confirming
the corrected figure — never a plausible diagnosis, a matching arithmetic
model, or a passing `ha_validate.sh` run. When a `CFG-` fix is applied, add
its confirmation row to `LIVE_VERIFICATION_QUEUE.md` at that point, so the
close goes through the same gate as everything else.

---

## Open

| ID | Sev | View / component | Summary | Status |
|---|---|---|---|---|
| CFG-001 | S1 | Home Assistant **Energy dashboard configuration** (`.storage/energy`) — *not* `dashboards/deez_smart_home.yaml` | Energy → Totals reports Grid total **47.83 kWh** costing **A$437.60**, an implied **A$9.1491/kWh** and about **31.8×** the real tariff. Observed live by the owner 30 Aug 2026 while verifying `UI-011`. **Not a scaling bug — an accumulation read as a period total.** The one exposed monetary entity is named literally `sensor Cost` (`device_class: monetary`, `AUD`, no area) and read **451.1649** the same day; `451.1649 − 437.60 = 13.5649`, and A$13.5649 over 47.83 kWh is **0.2836 AUD/kWh** — an entirely ordinary rate, within 1.6% of the `SolarNet Grid import tariff` entity (0.2880 AUD/kWh) and 3.7% of the contracted peak rate (0.2734996 incl GST, per the `bill-electricity` view). So today's true cost is ≈A$13.56 sitting inside a wrong figure; the ≈A$437.60 on screen is the cost entity's accumulated total, not its increase across the selected period. That also explains why the factor is an odd 31.8× rather than a clean power of ten. **Leading hypothesis, stated as a hypothesis:** grid-consumption cost is set to *use an entity tracking the total costs*, pointed at a cumulative lifetime cost sensor whose statistic history effectively begins inside the current period, so its whole accumulated total was recorded as one jump and attributed to today. `451.16 ÷ 0.288 ≈ 1567 kWh` ≈ 33 days of import, consistent with a counter that started about a month ago. The sensor's name is itself a signal: HA auto-names a cost sensor `<source name> Cost`, so a bare `sensor Cost` means the source-name half resolved to nothing — consistent with a renamed source or a hand-made sensor. A `state_class: total` without `last_reset`, or a `total_increasing` sensor that reset, would produce similar symptoms by a different route. **Not diagnosable from here and deliberately not changed:** the cost source lives in `.storage/energy`, which this environment cannot read (`/config` unmounted, REST/WebSocket blocked — `DEPLOYMENT_BLOCKERS.md` Blockers 2/3), and the grid source entity itself is a Powerpal sensor, not exposed to Assist. Editing a production money figure blind is exactly what the owner's instruction ruled out. **Owner action to unblock:** Settings → Dashboards → Energy → Grid consumption → its cost setting. Report (1) which entity is the grid consumption source; (2) which cost option is selected — *do not track costs* / *static price* / *entity with the current price* / *entity tracking the total costs*; (3) if an entity is named, which one, plus its `state_class`, `device_class`, unit and current state from Developer Tools → States (≈451 if it is the `sensor Cost` above); (4) from Developer Tools → Statistics, whether that entity is flagged with a units/reset issue and when its history starts. **Nothing in this repository changes as part of the fix** — the Energy dashboard's configuration is not under version control here. Take a full backup first; HA backups are unavailable from this environment (`MAINTENANCE.md`). | OPEN — blocked on owner diagnosis |
| CFG-003 | S1 | **Deployment bridge / dashboard source of truth** — `/config/deploy_deez_dashboard.sh` and the storage-mode dashboard registry. *Not* `dashboards/deez_smart_home.yaml`, which is by all repository-side evidence correct | **Changes pushed to `ha-deploy` are not reaching the live dashboard.** Established 2026-08-30 after three consecutive `UI-032` attempts produced no visible change, the third being `UI-032 PROBE v1` — a card with **no condition of any kind**, whose absence therefore cannot be explained by any gate, template, entity or schema question. **The evidence that this is deployment, not YAML:** (1) every Home element the owner reports seeing — the `Home Systems` heading, its 7 cards, and the exact 5-chip row Media/Network/iPad/Status/Settings — has existed unchanged since merge `6c3fff5`; **nothing the owner has ever reported seeing is unique to any commit after it**, so every observation to date is equally consistent with the live dashboard being frozen at `6c3fff5`-era content. (2) **No change to `dashboards/deez_smart_home.yaml` has ever been independently confirmed live.** All three `VERIFIED` rows are something else: `UI-025` is a theme file plus a `/local/` image; `UI-026` was inferred from the background rendering, which is evidence about the theme, not this file; `UI-011` was read off Home Assistant's **native Energy panel**, a built-in page this Lovelace config does not produce. (3) **12 commits have touched the dashboard file since `26c3b14`**, the only deployment run on record — and that run was a no-op that wrote nothing, which is exactly `DEPLOYMENT_BLOCKERS.md` Blocker 1: the apply step has never been observed to write. **Confound that must be eliminated first, honestly stated:** the area the owner inspected — Energy, Lighting, Cameras, Security, Climate, People, Bills, Media, Network, iPad, Status, Settings — is `sections[5]`, `Home Systems`, at the **bottom** of the page. The probe is in `sections[1]`, the **second block from the top**, above `Today` and `Rooms`. The probe's location may not have been in view. This does not weaken points (1)–(3), but it is cheap to rule out and must be ruled out before the deployment bridge is touched. **Owner diagnosis, in order** — the first item is decisive on its own and bypasses rendering entirely: (a) open the dashboard's **Raw configuration editor** and search for the literal string `UI-032 PROBE v1`; absent = the deployed config is not at `2183177` and this is confirmed deployment failure; present = the config is current and the fault is rendering, not delivery. (b) Search the same raw config for `front_door_battery`. (c) Scroll `Home` to the block directly under the page header and say whether **any** alert card is there — `Solar producing` should be, its gate is `above: 100` and solar read 983 W. (d) Run `/config/deploy_deez_dashboard.sh` by hand and capture the full output, especially the candidate commit and whether it reports a write or a skip. (e) Settings → Dashboards: how many entries exist, their `url_path` values, whether any duplicate claims `deez-smart-home`, and which one the phone actually has open. **Do not modify the deployment bridge from here** — it is protected under `CLAUDE.md` and `MAINTENANCE.md` and requires an explicit instruction. | ✅ **RESOLVED 2026-09-05.** The owner deployed manually and observed **`UI-032 PROBE v1` rendering live** — the exact end-to-end criterion this entry set for the bridge ("the raw config should contain the literal string `UI-032 PROBE v1`, and the purple bug-icon card should appear"). Delivery is confirmed working in both directions since: `origin/ha-deploy` at `9cca3c4` reached the host clone at `/config/deez_repo`. *Prior state, retained: CONFIRMED 2026-08-30 — owner checked the live Raw Configuration Editor and `sensor.front_door_battery` was absent, which established the failure.* **Two follow-ups this does not cover:** (1) the host's `git push` still fails on GitHub authentication — worked around by pushing from the cloud session instead of fixing credentials, so the host only ever needs to `fetch`; (2) `/config/deploy_deez_dashboard.sh` syncs the legacy dashboard and has not been confirmed to sync `dashboards/casaray_v2.yaml`, which `docs/CASARAY_V2_DEPLOYMENT.md` step 4 checks explicitly. **`UI-032 PROBE v1` may now be removed** from the legacy dashboard whenever the owner wishes — it was retained solely as this bridge's test instrument and it has served that purpose. |
| CFG-002 | S4 | Fronius / SolarNet integration — *not* `dashboards/deez_smart_home.yaml` | The `SolarNet Grid import tariff` entity reads **0.2880 AUD/kWh** while the contracted Home 365 Solar peak rate shown on the `bill-electricity` view is **0.2734996 incl GST** — a 1.45 c/kWh gap, about 5% on every cost figure derived from the entity. Possibly a deliberate rounded-up estimate, possibly stale from a previous plan; the current contract began 31 Jul 2026, recently enough for a stale rate to be plausible. Lives in the integration, not in this repository, so there is nothing to change on this branch. **Logged separately so it is not mistaken for part of `CFG-001`** — it is a ~5% difference, not a 31.8× one, and correcting it would not move A$437.60 anywhere near A$13. | OPEN — owner decision |

---

## CFG-001 diagnostic protocol — awaiting owner evidence

**Status: open, evidence not yet supplied. Nothing in the Energy
configuration is to be guessed at or changed until it is** — the owner's
standing instruction, and consistent with `MAINTENANCE.md`, which places HA
configuration outside autonomous scope.

The owner will supply Energy Dashboard screenshots/details. When they arrive,
work these seven determinations in order and record each with the evidence it
rests on. Where evidence does not settle a point, say so — an unanswered
determination is a result, not a gap to fill with the model below.

| # | Determination | Where the evidence comes from |
|---|---|---|
| 1 | **Which entity HA uses as the Grid Consumption source** | Settings → Dashboards → Energy → Grid consumption. Expected to be a Powerpal sensor; it is not exposed to Assist, so it cannot be read from here |
| 2 | **Which cost option is selected** — *do not track costs* · *static price* · *entity with the current price* · *entity tracking the total costs* | Same panel, the cost row under that source |
| 3 | **Whether the cost entity is cumulative or period-based** | Its `state_class`: `total_increasing`/`total` = cumulative; `measurement` = instantaneous and wrong for this slot. A cumulative entity in the *current price* slot is a category error; a period entity in the *total costs* slot is another |
| 4 | **Its state, unit, `device_class` and `state_class`** | Developer Tools → States. Compare against the one monetary entity visible from here: name `sensor Cost`, `device_class: monetary`, `AUD`, **451.1649** on 30 Aug 2026. If the configured entity is that one, its state should now be somewhat above 451 |
| 5 | **Whether HA Statistics reports an issue on it** | Developer Tools → Statistics — look for a units-changed or "state class changed" flag, and for the *Fix issue* affordance |
| 6 | **Whether the entity's history/statistics start date explains A$437.60** | Developer Tools → Statistics → that entity's history, or the Energy dashboard stepped back day by day. **This is the decisive test of the standing hypothesis:** if the statistic's history begins on or near 30 Aug 2026 with a single jump of ≈A$437.60, the accumulation-read-as-period-total explanation is confirmed. If instead it has a month of ordinary ≈A$13/day steps, the hypothesis is **wrong** and the cause is elsewhere — report that plainly rather than reshaping the model to fit |
| 7 | **The safest correction that preserves historical Energy data** | Decided only after 1–6. Ranked below |

### Correction options, safest first

Not to be applied before determinations 1–6 are answered. Ranked by how much
history each preserves, which is the owner's stated priority:

1. **Repair the statistic in place.** If (6) shows one bogus jump in an
   otherwise sound series, Developer Tools → Statistics → *Fix issue* /
   *Adjust sum* on that single hour. Loses nothing but the bad delta, and
   keeps every real day before and after it. Try this first.
2. **Correct the wiring, leave the data.** If (2)/(3) show a category error —
   a cumulative total sitting in the *current price* slot, say — repointing
   the cost option fixes future periods without touching recorded history.
   Past periods stay wrong and should be noted as such rather than silently
   left to look correct.
3. **Repoint at a price entity or a static price.** `SolarNet Grid import
   tariff` (0.2880 AUD/kWh) is the obvious candidate for *entity with the
   current price*, **but see `CFG-002`** — that entity's own rate is unconfirmed
   and 5% above the contracted one, so this option should not be taken until
   `CFG-002` is settled, or it trades a 31.8× error for a 5% one.
4. **Clear and re-record the cost statistic.** Discards history. Last resort,
   and only with the owner's explicit agreement on what is being lost.

In every case: full backup first — HA backups are unavailable from this
environment (`MAINTENANCE.md`) — and the close is the owner re-reading
Energy → Totals and confirming a plausible daily cost (≈A$13–15 for a
47.83 kWh day), per the live-verification rule above.

### What is already established, and what is only a model

Keeping these apart matters, because determination 6 can falsify the second
column and nothing in the first.

| Established (read-only, 30 Aug 2026) | Hypothesis only |
|---|---|
| Energy → Totals showed 47.83 kWh at A$437.60 → A$9.1491/kWh implied | That the cost option is *entity tracking the total costs* |
| Exactly one monetary entity is exposed, named literally `sensor Cost`, `device_class: monetary`, AUD, state 451.1649 | That its statistic history begins inside the current period |
| `451.1649 − 437.60 = 13.5649`, and A$13.5649 ÷ 47.83 kWh = **0.2836 AUD/kWh** — an ordinary rate | That the whole accumulated total was recorded as one jump |
| `SolarNet Grid import tariff` = 0.2880 AUD/kWh; contracted peak 0.2734996 incl GST | That `451.16 ÷ 0.288 ≈ 1567 kWh ≈ 33 days` reflects when the counter started |
| The grid source entity is not exposed to Assist and cannot be read from here | That the bare name `sensor Cost` indicates a renamed or hand-made source |

## CFG-002 — change gate

`SolarNet Grid import tariff` reads 0.2880 AUD/kWh; the `bill-electricity`
view's contracted Home 365 Solar peak rate is 0.2734996 incl GST.

**Do not change the configured tariff on the strength of that gap alone.**
Confirm the actual EnergyAustralia rate *structure* first — the dashboard
records a single peak rate, but the discrepancy would be explained just as
well by a rate this record does not capture: a time-of-use or demand
component, a shoulder/off-peak band, the 24% guaranteed discount applying to
usage rather than the total, or a rate that changed after the 31 Jul 2026
contract start. 0.2880 may be a deliberate rounded-up estimate rather than an
error.

Only once the correct structure is confirmed against the bill or the
retailer's rate sheet does a change become correct — and it is applied in the
Fronius/SolarNet integration, not on this branch. Close on live confirmation,
never on the arithmetic alone.

---

## UI-032 — battery health had no surface at all

**Status: BLOCKED on `CFG-003`.** Three attempts (`a183d5f`, `0fec9bb`,
`2183177`) produced no visible change. The third was an unconditional card,
so the cause is no longer plausibly in this file's logic — see `CFG-003`.
**No further `UI-032` logic change until the source-of-truth question is
settled**, per the owner's instruction. The 12 conditionals and the probe
stay in place; the probe is now the deployment test instrument. Sev S2: not a false statement, but a maintenance condition the
household could not see. Front Door and RingRing are entry devices and the
C425 is an outdoor camera; all three run flat without warning.

### What was wrong

The dashboard surfaced 2 of roughly a dozen live battery entities. Nothing
showed **Front Door 20%**, **RingRing 21%** or **Tapo C425 North Wall 28%**.
The `cameras` view's chip read "6/6 online", which was true and said nothing
about charge — a camera at 28% is still online right up until it isn't.

### What was added

Conditional cards in the `home` view's **Active Now** strip (after the Bills
alert, before the Rooms grid), following the strip's existing pattern —
`grid_options` + `conditions` + a bilingual `custom:mushroom-template-card`.
The first attempt used one consolidated card; see the rework section below for
why it is now one card per entity per situation.

It is **contextual, not a panel**: the card does not exist on screen at all
unless a battery is genuinely below 30% or genuinely not reporting. With every
battery healthy the Active Now strip looks exactly as it did before.

| Property | Behaviour |
|---|---|
| Low | "Front Door 20%" / "Battery low", icon `red` |
| Unreadable | "Front Door not reporting" / "Battery not reporting", icon `orange` |
| Healthy | "Front Door 100%" / "Battery OK", icon `green` — reachable only if the state changes after the gate fires |
| Tap | Navigates to `/deez-smart-home/cameras` |
| Language | Full bilingual pair on every branch, per the toggle convention |

### Entities bound — all six owner-verified, none inferred

`sensor.front_door_battery` · `sensor.living_room_ringring_battery` ·
`sensor.tapo_c425_north_wall_battery` · `sensor.tapo_c420_south_wall_battery` ·
`sensor.tapo_c420_east_wall_battery` · `sensor.tapo_camera_bcca_battery`

**`sensor.tapo_c420_south_wall_battery_2` is deliberately NOT bound** — the
owner identified it as a stale duplicate that reads `unavailable` forever.
Binding it would have manufactured a permanent false alarm. Verified absent
from the file by grep.

### How a missing reading is handled

Two independent guards, because the gate and the text can disagree:

1. **The visibility gate** fires on `numeric_state below: 30` *or*
   `state: unavailable`, per entity. `numeric_state` is false for a
   non-numeric state, so an unreadable sensor can never satisfy the *low*
   branch.
2. **The card text** re-checks every entity itself: `unavailable`/`unknown`/
   `none`, *and* `is_number` for anything else non-numeric. Only a value that
   passes both is compared against 30 or rendered as a percentage.

A missing reading therefore renders as **"not reporting"** and colours
`orange`. It is never shown as 0%, never counted as low, never counted as
healthy, and never silently dropped from the tally — the failure mode
`REG-007..011` were filed for.

### Verified by rendering, not by inspection

The primary and `icon_color` templates were rendered against six scenarios
before the file was touched: the live states; all healthy; all unavailable;
all six low; a mixed `unknown`/`none`/non-numeric-string case; and the
29/30 boundary. Every branch produced correct text, correct colour and a
bounded length (12–72 chars). The 30 boundary is exclusive in both the gate
and the text, so they cannot disagree about it.

### Live FAIL on the first attempt, and the rework

**Observed 2026-08-30 (owner):** no battery alert appeared on Home at all,
with Front Door at 20%, RingRing at 21% and C425 North Wall at 28%. The card
did not render.

**Cause: `condition: or`.** It was the single construct in `a183d5f` that
did not already exist anywhere in this dashboard, it was flagged at the time
as the thing to check first if the card failed to appear, and it is the only
part of the change that governs whether the card renders at all — the
templates cannot suppress a card, they only fill one in. Confirmed by
elimination rather than by observation: Lovelace schema still cannot be
checked from this environment.

**The lesson is the one the repository already had written down.** A
construct with no precedent in the file cannot be validated here, so
introducing one puts the whole change on a single unverifiable bet. The
existing strip had a working pattern and it should have been used first.

**Rework (`0fec9bb`): one conditional card per entity per situation, each
with a single flat condition** — exactly the shape the Active Now strip's
Solar, Bills, Climate and Media alerts already use, and which the live
dashboard therefore demonstrably renders. Twelve cards, six entities × two
gates:

| Gate | Condition | Fires when |
|---|---|---|
| Low | `condition: numeric_state` · `below: 30` | The reading is numeric and under 30 |
| Not reporting | `condition: state` · `state: unavailable` | The entity is unavailable |

No `conditions:` list has more than one entry and none is nested, so nothing
in the new structure depends on a construct this file has not already proven.
Verified by parsing the committed YAML: 12 cards, 6 distinct entities, zero
nested condition blocks.

Each card is `columns: 6` (the strip's own half-width default) rather than the
first attempt's `columns: 12`, because each now carries one short line
("Front Door 20%") instead of a combined sentence.

**The card body is identical for both gates**, and still carries the full
guard: it re-derives the state itself and re-checks `unavailable`/`unknown`/
`none` and `is_number` before rendering a percentage or comparing against 30.
So whichever gate fires, the card reports the entity's *current* truth — an
entity that goes unreadable between gate evaluation and render says "not
reporting" in orange, never a stale percentage and never red "low".

With four alerts able to appear at once the strip is busier than the single
consolidated card would have been. That is the deliberate trade: the
consolidated version cannot be expressed without `or`, and a card that
renders beats a tidier one that does not.

### Second live FAIL, and what it eliminated

**Observed 2026-08-30 (owner):** still nothing, after `0fec9bb`. Other Home
cards (Energy, Lighting, Cameras, Security, Climate, People, Bills) render
normally, so the view itself is fine.

I was wrong about the cause the first time. `condition: or` was a real
unproven construct and removing it was correct on its own terms, but it was
**not** what stopped the cards rendering, because the flat replacement fails
identically. Recording that plainly: the first diagnosis was reasoning by
elimination presented with more confidence than one unverified variable
deserved.

**What the repository can now positively rule out**, by parsing the committed
YAML rather than by argument:

| Checked | Result |
|---|---|
| Are the cards inside the rendered Home container? | **Yes.** Home → `sections[1]`, the Active Now strip, alongside the 5 pre-existing conditionals |
| Is `grid_options` valid at that nesting level? | **Same level as the working Solar card**, which renders |
| Is the section structure dropping them? | Section 1 is `type: grid`, `column_span: 2`, no `visibility` key anywhere in the file |
| Is my card shape different from a working one? | **No.** Key-for-key identical to the Solar alert: `type` / `grid_options.columns` / `conditions[0]{condition,entity,below\|above}` / `card{type,primary,secondary,icon,icon_color,tap_action}`. The only difference is `below` vs `above`, both valid `numeric_state` operators |
| Any section- or view-level condition suppressing the block? | None exists |

So the structure is not the problem, and two structural rewrites have now
failed. The two remaining candidates cannot be settled from this environment
at all: **the entity IDs**, and **whether the deployed dashboard is actually
at the stamped commit**.

### Probe shipped instead of a third rewrite

`UI-032 PROBE v1` — one **unconditional** `custom:mushroom-template-card`, the
first card of the same section 1, `columns: 12`, purple bug icon. No condition
of any kind, so it renders if and only if that container renders.

It reads out the raw `states()` of all six entity IDs and counts how many
satisfy the exact test the gates use. Its three possible outcomes are mutually
exclusive and each names a different root cause:

| What the owner sees | Root cause |
|---|---|
| `FD 20 · RR 21 · NW 28 · SW 100 · EW unavailable · BC 100` and "3 of 6 read under 30" | IDs and deploy are both fine → the fault is in `numeric_state` evaluation itself, and the fix is to drop the conditional wrapper and gate inside the template |
| `FD unknown · RR unknown · …` and "0 of 6" | **The entity IDs do not resolve on this instance.** Every gate is false, so nothing ever renders — and this would explain both failures exactly |
| **No purple probe card at all** | The container is not rendering, or the deployed dashboard is not at the stamped commit — a deployment problem, not a YAML one |

The 12 conditional cards are left in place. If the IDs are good they cost
nothing, and if the probe shows real values while they stay hidden, that
isolates the gate precisely.

### Still to confirm live

- The probe outcome above, which decides the actual fix.
- That the four expected cards then appear at all.

- That the four expected cards now appear at all. This is the whole point of
  the rework.
- Per the owner: close `UI-032` only once all three verified low batteries
  display correctly **and clear correctly when no longer low**. The clearing
  half cannot be observed from here at all.

### Not covered

Only these six entities. Other live battery entities (the Hue sensors, the
contact sensors, the Aqara shade, the Powerpal gateway) have not been
owner-verified as entity IDs, and the never-invent rule still applies to them.

---

## CFG-003 root cause — the branch history was replaced and the host's clone was left behind

**Confirmed, not hypothesised.** The owner's Raw Configuration Editor check
settled the delivery question: `sensor.front_door_battery` is absent from the
live config. Git then settled the cause.

### The proof

`26c3b14` is the candidate commit the deployment script itself reported
resolving. It is **not reachable from the current branch at all**:

```
$ git merge-base 26c3b14 HEAD
(no output — unrelated histories)
```

Three commits the repository's own documentation refers to are all outside the
current history: `26c3b14` (the deploy log's candidate), `1bdd704` (the
README's landing-check marker) and `5608b5f`. None is an ancestor of `HEAD`.

The reason is visible in the roots:

| History | Root commit | Tip | Contains |
|---|---|---|---|
| **Old** — what the host cloned | `2d4b295`, 2026-08-23 | `5608b5f`, 2026-08-25 | `26c3b14`, `1bdd704` |
| **Current** — what we push to | `6c3fff5`, **2026-08-29** | `376f3d8`+ | every commit since |

`6c3fff5` is **a root commit with no parents**, despite its message reading
"Merge remote-tracking branch 'origin/ha-deploy'". So on **2026-08-29 the
`ha-deploy` branch on GitHub was replaced with an unrelated history.** A
non-fast-forward update on that ref was directly observed from this
environment (`+ 5608b5f...ca1fa32 ha-deploy -> origin/ha-deploy (forced
update)`).

### Why that stops propagation, exactly

The Home Assistant host cloned before 2026-08-29 and its working branch still
sits on the old history. From there:

- `git fetch` succeeds and downloads the new objects, but
- **nothing can fast-forward a branch across disjoint roots.** `merge`/`pull`
  either refuses ("unrelated histories") or is a no-op, so the checked-out
  commit never advances.

Which is precisely the log on record:

```
Fetching origin/ha-deploy...
Repository already current          <- cannot advance, not "nothing to do"
Candidate commit: 26c3b148…         <- still the old history's commit
No dashboard content change.        <- content compares equal, so…
                                    <- …the apply step never runs
```

**The exact point where repo YAML stops propagating is the host's local
clone**, between `origin/ha-deploy` on GitHub and the file the script reads.
Every stage downstream — validate, compare, apply — is behaving correctly
given the stale input it is handed. The apply step is not broken; **it is
never reached**, because the content never changes, because the commit never
advances.

This also explains why `DEPLOYMENT_BLOCKERS.md` could only ever record a
no-op run: there has never been a run with anything new to apply.

### Two independent faults, and the order to fix them

1. **This one — the clone is orphaned from its branch.** Fix first; nothing
   else can work until it is.
2. **`DEPLOY_AUTH.md`'s credential fault** — the scheduled `git fetch` under
   HA's `shell_command` has no git credentials for a private repo. Independent
   of (1) and still outstanding. Fixing (1) alone may leave *manual* deploys
   working and *scheduled* ones still failing.

### Owner recovery, on the host, in the clone the script uses

Find the clone with `grep -n 'cd \|git ' /config/deploy_deez_dashboard.sh`,
then, in that directory:

```sh
git rev-parse --short HEAD                    # expect an old-history commit
git fetch origin ha-deploy
git merge-base HEAD origin/ha-deploy          # EMPTY confirms the split
git status --short                            # must be clean
git log --oneline origin/ha-deploy..HEAD      # MUST be empty — see warning
```

**Check that last command before going further.** If it lists commits, the
host clone carries work that exists nowhere else — captured live UI changes,
per `README.md` "Capturing a live UI change back into Git". Save those first
(`git bundle create /config/host-clone-backup.bundle --all`) and say so;
do not discard them.

Only once it is empty:

```sh
git checkout ha-deploy 2>/dev/null || git checkout -b ha-deploy
git reset --hard origin/ha-deploy
git rev-parse --short HEAD                    # expect 376f3d8 or later
```

Then run `/config/deploy_deez_dashboard.sh` by hand and capture the output.
The candidate commit should no longer be `26c3b14`, and the run should report
a content change and an apply rather than a skip.

**Not done from here.** The deployment bridge and its clone are protected
under `CLAUDE.md` and `MAINTENANCE.md`; this section is a procedure for the
owner, not a change.

### How the bridge gets verified afterwards

`UI-032 PROBE v1` is deliberately left in place as the test instrument. Once
delivery is fixed, it verifies the whole chain end to end in one look: the raw
config should contain the literal string `UI-032 PROBE v1`, and the purple
bug-icon card should appear in the block directly under the Home page header.
The probe is removed only after that, and `UI-032`'s own conditionals can then
be judged on their merits for the first time.

## Fixed — tracking only (no live dashboard component)

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-012 | MED | `LIVE_VERIFICATION_QUEUE.md` (tracking, not the dashboard YAML) | Verification-queue upkeep fell behind the REG-007..011 / UI-030 batch, in two ways: (1) `691689a` (UI-030) never added a queue row for the LetPot Grow Light guard; (2) the queue's own "N checks pending" footer undercounted its table. By the time this was reconciled, a later batch (`ccfb0c8`) had already corrected the footer arithmetic (39→42, matching the table) as a side effect of adding its own two rows, but the underlying `UI-030` row itself was still genuinely missing — grepping the queue for `LetPot`/`ray-bedroom`/`UI-030` still returned nothing. **Corrective action taken:** added the missing `UI-030` row to `LIVE_VERIFICATION_QUEUE.md` (Bills & rooms section) citing commit `691689a`, and updated the footer to 43. No dashboard YAML touched. | Daily Project Coordinator, this run | FIXED — no live check needed; the queue row's own presence is directly verifiable by inspection, not a rendered-dashboard question |
| REG-014 | LOW | `DASHBOARD_ISSUES.md` (tracking, not the dashboard YAML) | This file's own header describes it as "the authoritative regression and bug record for `dashboards/deez_smart_home.yaml`", but two genuine bug-class fixes to that file by the Billing routine were absent from it entirely: `BILL-001`'s account-number de-hardcoding (`23c0301`) and `BILL-004`'s raw-interpolation guard (`d570a82`). Both were already correctly tracked in `DASHBOARD_BACKLOG.md` and `LIVE_VERIFICATION_QUEUE.md` — this was a completeness gap in this file only, not a lost fix. **Corrective action taken:** added both as rows in "Fixed — awaiting live verification" below (without reproducing the NMI/MIRN digit values, which remain correctly `BLOCKED`). | Billing Dashboard Upgrade, this run | FIXED — no live check needed; both cited commits are already deployed and separately queued for verification under their own IDs |

---

## False-safe-state sweep — 2026-08-30

A narrow re-sweep for the recurring false-safe-state class (see Process note)
beyond the REG-001..006 baseline, targeting cards that aggregate multiple
sensors — the per-sensor guards already fixed under REG-001..003 don't
automatically cover an aggregate that silently drops an unavailable sensor
from its count instead of flagging it. This was the exact same
three-door-sensor list (`m_contact_sensor_door`, `f_contact_sensor_door`,
`b_contact_sensor_door`) copy-pasted into five separate cards across three
views, of which only REG-003 (a different chip on the same list) had ever
been guarded. All five instances found and fixed; grepping the raw sensor
list afterward confirms none remain.

**Correction:** REG-008 was first logged against `ipad-command-center`. The
chip is actually on the `cameras` view's status chip row (line ~1590) — the
`ipad-command-center` view starts later in the file, at a different chip row
entirely (which turned out to have its own, distinct instance of the same
bug — see REG-011). Corrected below; `LIVE_VERIFICATION_QUEUE.md` was moved
to the right page section in the same commit as REG-009..011.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-007 | MED | `home` — House Pulse hero card | The door-open count and its icon_color silently dropped any door sensor reporting `unavailable`/`unknown`/`none` from the tally instead of flagging it, so all three sensors going offline showed a confident "0 open" and (with WAN up) a green icon — the same false-safe pattern REG-003 fixed on the sibling Network nav chip two cards away. Now surfaces "N door sensor(s) offline" / "N 个门传感器离线" and the icon falls back to grey rather than green when any door state is unknown. | `b058006` | FIXED — AWAITING LIVE VERIFICATION |
| REG-008 | MED | `cameras` — status chip row Doors chip | Same root cause as REG-007, worse: the chip had no unavailable guard at all and was still bare English ("N open"), unlike its two siblings in the same chip row (Motion, WAN) which were already guarded. All three door sensors offline showed "0 open" / green. Now matches the Motion chip's own guard convention: all-unknown → "Sensor offline" / grey, bilingual. **View corrected from an initial mislog against `ipad-command-center` — see note above.** | `b058006` | FIXED — AWAITING LIVE VERIFICATION |
| REG-009 | MED | `home` — quick-control chip row Doors chip | Same unguarded template as REG-008, also still bare English, on the `home` view's own quick-control chip row (separate card from the House Pulse hero). Fixed to the same guarded/bilingual convention. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |
| REG-010 | MED | `home` — Rooms section Security card | The "N doors open • motion monitoring" summary silently dropped unavailable door sensors from its count/colour. Now appends "N unknown" / "N 离线" when any door sensor is unavailable and the icon falls back to grey instead of a confident green. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |
| REG-011 | MED | `ipad-command-center` — Home Pulse chip row Doors chip | The genuine `ipad-command-center` instance (see correction note): unguarded and still bare English, sitting beside an already-guarded WAN chip (REG-005) in the same row. Fixed to the same guarded/bilingual convention as REG-008/009. | `d592692` | FIXED — AWAITING LIVE VERIFICATION |

---

## False-safe + raw-interpolation sweep — 2026-08-30 (person chip, Climate summary, Roller Shade, Lighting Modes)

A fresh pass over the areas the previous run's `LIVE_VERIFICATION_QUEUE.md`
note flagged as next-plausible (raw-interpolation class beyond `ray-bedroom`).
The six `camera-*` subviews themselves turned out clean — each is just a back
chip plus a `webrtc-camera` card, no template content to guard. Widening the
grep for raw `{{ states(...) }}` interpolation elsewhere in the file (outside
Billing's `bill-*` views, which are out of scope) turned up three unguarded
instances, plus one genuine false-safe finding caught while checking the
same `lighting-modes` view.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-031 | S4 | `home` quick-control chip row (Person); `home` Rooms grid (Climate card); `light-ray-bedroom` (Roller Shade card) | Same raw-interpolation class as UI-006/UI-030: three cards printed a raw `states(...)` value with no guard and no bilingual text — the `home` view's Person chip showed the literal `person.raymond_du` state string (`home`/`not_home`, or `unavailable` verbatim) instead of the distance-based bilingual convention already used on `people-locations` and `ipad-command-center`; the `home` Rooms-grid Climate card printed the raw lowercase HVAC mode (or `unavailable`) instead of the guarded/title-cased convention already used two cards away (Parents Room, line ~375); the Roller Shade card on `light-ray-bedroom` printed the raw cover state and an unguarded battery percentage that would render `unavailable%` exactly like the Powerpal battery card UI-020 already fixed. All three now use the guards/bilingual conventions already established elsewhere in the same file for the same entities. | `ccfb0c8` | FIXED — AWAITING LIVE VERIFICATION |
| REG-013 | MED | `lighting-modes` — Current State section (Living Room, Ray Bedroom, Dining cards) | The recurring false-safe-state class: each card read `'Off' if is_state(light,'off') else (<percent> if brightness is not none else 'On')`. An `unavailable`/`unknown` light is neither `off` nor has a brightness attribute, so it fell into the final `else` and confidently asserted **"On"** — the exact same class CLAUDE.md's process note warns about ("never let a card assert a reassuring state it cannot see"), just for a light instead of a door/motion sensor. Now shows bilingual "Offline"/"离线" when the light is unavailable/unknown, ahead of the existing off/percentage branches. Icon colour was already safe (defaults to grey unless confirmed `on`) — text was the only false-safe surface. | `ccfb0c8` | FIXED — AWAITING LIVE VERIFICATION |

---

## Regression audit — 2026-08-29

Baseline audit against `ha-deploy` HEAD `7f304ad`, covering the 12 commits
`ae89134`..`f04a59f` plus a full-file sweep for the standing regression
categories. **All six findings are now fixed.** Full evidence, per-finding
suspected commits and recommended actions are preserved in
`archive/DASHBOARD_ISSUES_ARCHIVE.md`.

Clean at audit time: all 130 `navigate` targets resolved; no same-view
duplicate entity controls; no nested `grid` cards; converted Tile cards kept
their Mushroom features; all 38 `float(0)` casts guarded and no
`float(100)`/`float(9999)` sentinel anywhere; every `max_columns` ≤2; all six
camera back-chips bilingual.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| REG-001 | MED | `security` — 3 door cards | Bare-English `Open`/`Closed` inside an otherwise-bilingual template. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-002 | MED | `lights` + `cameras` motion chips | Motion-aggregate chips showed a confident "Quiet" when every watched sensor was unavailable — the project's recurring false-safe-state class. Also untranslated. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-003 | MED | `home` — Network nav chip | Two-branch green/red with no unavailable guard, so a dropped WAN sensor showed confident red. | `b5eee22` | FIXED — AWAITING LIVE VERIFICATION |
| REG-004 | LOW | `people-locations` | The "at home" branch rendered bare English `home` while its sibling away-branches were bilingual. | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| REG-005 | LOW | `ipad-command-center` — WAN chip | Unavailable fallback rendered literal `WAN —` in both languages. Fix also changed the English text to "WAN not reporting" to match an equivalent case elsewhere — **owner may want the dash kept; not decided.** | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| REG-006 | LOW | `home` — Energy tile | Bare lowercase `offline` fallback beside an already-bilingual "Solar"/"太阳能". | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |

## Fixed — awaiting live verification

Every entry below is committed, validated and pushed to `ha-deploy`. None has
been seen rendered.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-001 | S3 | `home` | Nested 3/4-column grids inside a ~280px section made tiles 60-85px wide; lights/doors/solar each duplicated four times; two tiles navigated to the page they were already on. | `119e1cd` | FIXED — AWAITING LIVE VERIFICATION |
| UI-002 | S1 | `home` room tiles | Three tiles showed static text that never changed; three interpolated unguarded sensors ("unknown °C", "Freezer unavailable W"). | `018610b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-003 | S3 | 16 views | Two different section-header treatments (46 heading cards vs 35 Mushroom title cards) mixed within single views. | `b85949e` | FIXED — AWAITING LIVE VERIFICATION |
| UI-004 | S3 | 23 views | `max_columns` exceeded the section count, leaving empty grid tracks; seven views used a quarter of the iPad screen. | `94a9b42` | FIXED — AWAITING LIVE VERIFICATION |
| UI-005 | S1 | `security` doors | `'Open' if is_state(...) else 'Closed'` — an unavailable contact sensor reported a confident green "Closed" on the security page. | `b1ef565` | FIXED — AWAITING LIVE VERIFICATION |
| UI-006 | S1 | 20 cards across 8 views | Same class as UI-005: "Clear", "Normal", "Door Closed", "Up to date" asserted on dropout, incl. the three iPad Command Center door cards. Nine raw interpolations printed state names mid-sentence. | `315323f` | FIXED — AWAITING LIVE VERIFICATION |
| UI-007 | S3 | `climate`, `status` | Flat single-column pages; Climate lacked the full thermostat for the house's only climate device. | `bb05c7c` | FIXED — AWAITING LIVE VERIFICATION |
| UI-008 | S1 | `status` backups, Home hero, weather | Raw ISO timestamps ("Last success 2026-08-25T04:00:12+00:00"); House Pulse rendered "None°C" and an unrounded temperature; conditions read "Partlycloudy". | `bb05c7c` | FIXED — AWAITING LIVE VERIFICATION |
| UI-009 | S2 | six `camera-*` subviews | No back link. `kiosk_mode` hides the header, so a full-screen camera had no exit. | `e06d0ce` | FIXED — AWAITING LIVE VERIFICATION |
| UI-010 | S3 | 4 lighting views | Section heading card placed before the page title, so each page opened with a section label. | `e06d0ce` | FIXED — AWAITING LIVE VERIFICATION |
| UI-017 | S2 | 16 of 19 top-level views | No route back to Home under kiosk mode; tapping a room stranded you there. | `34a92e7` | FIXED — AWAITING LIVE VERIFICATION |
| UI-018 | S1 | `people-locations`, `people-locations-distance`, `ipad-command-center` | `distance(...) \| float(9999)` rendered "9999.0 km from home" in red for anyone without a GPS fix. Eight occurrences. | `76da19b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-019 | S3 | `people-locations` | Each of three people listed four times on one page; person cards ~83px wide in a nested 3-column grid. | `76da19b` | FIXED — AWAITING LIVE VERIFICATION |
| UI-020 | S1 | `energy` | Total Solar was a bare unguarded `states()` with no unit; Powerpal battery read "Battery unavailable%" and its `\| float(100)` sentinel painted it green when silent. | `df457e3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-021 | S3 | `energy` | 14 cards in one column; the four native energy cards squeezed into half a page. | `df457e3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-022 | S1 | `network` | Three Infrastructure cards with no entity, no state and no tap action rendered identically to real status cards, so three of five could never say anything but "fine". | `a5dc914` | FIXED — AWAITING LIVE VERIFICATION |
| UI-023 | S3 | room pages | Seven "nothing here yet" markdown placeholders under their own headings, filling two of Ray Bedroom's four columns. Moved to `README.md`. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |
| UI-014 | S3 | `cameras` | Front Door rendered twice (picture-entity plus a template card doing the same navigation); five per-camera chips duplicated the tiles above them; the "All Cameras" heading sat over a grid excluding Front Door; a 2-up nested grid in a third-width section gave ~185px previews. | `ae89134` | FIXED — AWAITING LIVE VERIFICATION |
| UI-015 | S3 | `ipad-command-center` | 52 cards, three nested grids inside half-width sections, and a six-chip camera status row sitting directly above the six camera tiles it described. Two load chips were unguarded. | `99a77b4` | FIXED — AWAITING LIVE VERIFICATION |
| UI-016 | S3 | `bills`, `light-living-room`, `lighting-modes` | The last four nested `grid` cards sizing themselves inside half-width sections. Dissolved into native `grid_options`; the dashboard now has none. The six bill subviews are reviewed and need no layout change — one section, one column each. | `9b28fdb` | FIXED — AWAITING LIVE VERIFICATION |
| UI-013 | S4 | `parents-room`, `guest-room` | Each stacked a Mushroom media card and a native `media-control` for the same player. The native card is a superset — artwork, transport, volume and power — so the Mushroom card was removed from both. The four Mushroom media cards that are the ONLY card for their player were left alone. The parents-room climate pair was also left: there the compact card is half of a deliberate 2-up summary row, not a duplicate. | `56c7656` | FIXED — AWAITING LIVE VERIFICATION |
| UI-012 | S4 | all 36 views | Only Home, Cameras and Lighting Studio responded to the language toggle; switching to Chinese left 33 views in English. The navigation-level chrome — 23 page titles, 26 subtitles, 55 section headings, 10 entities-card titles and the six camera back chips — is now bilingual. Every view responds. Device names and per-card status text are deliberately still English; see UI-028. | `f4e7ec3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-028 | S4 | status text across all views | 57 guarded templates now carry bilingual status text — Offline, Sensor offline, Open/Closed, Motion/Clear, Occupied/Empty, Clean required, Up to date, Paid/Payment Outstanding and the rest. Number-glued fragments ("{{ d }} km away", "N of 6 offline", "W • measured") are deliberately still English; see UI-029. | `fa286de` | FIXED — AWAITING LIVE VERIFICATION |
| UI-029 | S4 | ~34 templates | Number- and unit-glued status fragments. The position-stable ones ("Fridge {{ t }}°C", "W • measured", "Paid • $") were fragment-swapped; the four that Chinese genuinely reorders ("{{ d }} km away", "km from home", "N of 6 offline", the offline-camera join) were rewritten as whole per-language clauses. | `f04a59f` | FIXED — AWAITING LIVE VERIFICATION |
| UI-024 | S4 | `kitchen` | Third smart plug had no `name` (rendered its entity ID) and a one-off `brightness(200%)` pink/yellow card_mod unlike its two neighbours. | `3048e54` | FIXED — AWAITING LIVE VERIFICATION |
| UI-027 | S3 | 52 native `heading` cards; `themes/deez_your_name.yaml` | Heading cards render with no `ha-card` wrapper, so `card-mod-card` never reached them — the 52 of them sat directly on the photograph with no text-shadow, unlike the 69 title/chip cards `cbec78b` already covered. Added a theme-level `card-mod-card-heading` rule (card-mod's per-card-type key) targeting `:host` with the same `text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` — one rule, not 52 per-card blocks, per the global-first design direction. | `9926233` | FIXED — AWAITING LIVE VERIFICATION |
| BILING-RESID | S4 | `people-locations`, `ipad-command-center`, `home` Energy tile | Closes REG-004/005/006: the "at home" branch of the per-person markdown loop, the WAN chip's unavailable fallback, and the Energy tile's offline fallback were the last three bare-English fragments left over from the UI-012 -> UI-028 -> UI-029 bilingual sequence. | `dff00f3` | FIXED — AWAITING LIVE VERIFICATION |
| UI-030 | S4 | `ray-bedroom` — LetPot Grow Light card | Raw `states()` interpolation for `select.lph_se_dcd9_light_mode` / `..._light_brightness` printed the literal string "unavailable" mid-sentence with no guard at all — the same raw-interpolation class UI-006 fixed elsewhere. Found while widening the REG-007..011 aggregate sweep to `climate`/`network`/`status`/room views (that sweep itself found no new false-safe instances — clean). Now falls back to an em dash per field, or bilingual "Offline"/"离线" when both underlying selects are unavailable. | `691689a` | FIXED — AWAITING LIVE VERIFICATION |
| BILL-001 | S1 | `bill-electricity`, `bill-gas` — plan-details markdown | Hardcoded literal account numbers in the plan-details card replaced with guarded `input_text.elec_account_number` / `..._gas_account_number` references (falls back to "Not entered" when the helper is empty) — closes the account-number half of a P1 privacy exposure. **NMI/MIRN literals are unchanged** — no helper entity exists for either and one must not be invented; that portion stays `BLOCKED` in `DASHBOARD_BACKLOG.md` pending an owner decision. | `23c0301` | FIXED — AWAITING LIVE VERIFICATION (account-number portion only; NMI/MIRN out of scope, see `BILL-001` in backlog) |
| BILL-004 | S4 | `bills` landing tiles (Electricity, Gas, Car Insurance, Council Rates, South East Water, VicRoads Rego) + status cards on `bill-car-insurance`/`bill-water`/`bill-council-rates`/`bill-rego` | Ten `custom:mushroom-template-card` secondary fields printed a raw `states(...)` value with no guard — the same raw-interpolation class UI-006/UI-030/UI-031 fixed elsewhere, never previously swept here because `bills`/`bill-*` is Billing-owned and out of scope for Main. Guarded all ten against `unavailable`/`unknown`/`none`, reusing only already-referenced entities and the existing "Not entered" / bilingual-fallback conventions. | `d570a82` | FIXED — AWAITING LIVE VERIFICATION |
| BILL-005 | S3 | `bill-car-insurance`, `bill-water`, `bill-council-rates`, `bill-rego` — page title cards | These four `mushroom-title-card`s were the only 4 of 29 in the whole dashboard with no `card_mod` text-shadow treatment, unlike every other title card including `bills`, `bill-electricity` and `bill-gas` — found by grepping every `mushroom-title-card` instance for the standard `text-shadow: 0 1px 3px rgba(4, 10, 20, 0.55)` block. Over the CasaRay night-sky photo background this means these four titles were the only ones dashboard-wide with no shadow guaranteeing contrast/readability. Added the identical block already used by the other 25 title cards (no new CSS invented). | `73813e8` | FIXED — AWAITING LIVE VERIFICATION |

---

## Verified

Confirmed by the owner on the live dashboard.

| ID | Sev | View / component | Summary | Fixed in | Status |
|---|---|---|---|---|---|
| UI-025 | S2 | theme / background asset | Your Name background installed at `/local/your_name_night_sky.jpg` and the six-theme file at `/config/themes/`. | `88be895` | VERIFIED |
| UI-026 | S3 | all views | Per-card glass retired in favour of the theme surface. Precondition met — the background renders, which is only possible with the theme installed, so cards are drawing on the themed surface rather than the default opaque one. | `0f620f2` | VERIFIED |
| UI-011 | S3 | `energy` — Total Solar | Wh→kWh conversion confirmed correct. Owner read the native HA Energy dashboard live on 30 Aug 2026: Solar 16 kWh, Grid 47.83 kWh, Home consumption 63.83 kWh — `16 + 47.83 = 63.83` exactly — with the Solar production chart and the Energy Distribution card independently showing 16 kWh, so the figure held across three renderings of the same statistic rather than one card's formatting. Corroborated from this environment the same day by a read-only entity query: `Primo 5.0-1 (1) Energy day` = **16558 Wh** (`unit_of_measurement: Wh`) = 16.56 kWh, matching. The sibling `Total energy` sensor reads 48425900 Wh, which the card's `/1000` renders as 48425.9 kWh — the same order of magnitude as `Energy year` (4588108 Wh → 4588.1 kWh) and larger than it, as a lifetime counter must be. The feared 1000×-low reading does not occur. **Scope, stated precisely:** the owner's evidence is from the **native HA Energy dashboard**. It settles the Wh→kWh question this issue was about, and the entity read above independently confirms the card's own arithmetic. It does **not** close `UI-020`, a different check on the same card (that the readout carries a unit, and that the Powerpal battery is guarded), which stays `PENDING` in the queue. | `df457e3` | VERIFIED |


---

## Process note

Recurring root cause across UI-002, UI-005, UI-006, UI-008, UI-018 and
UI-020: a numeric or boolean fallback used as a sentinel — `| float(0)`,
`| float(100)`, `| float(9999)`, or a two-branch `if is_state(...)` — which
renders a missing reading as a real, plausible, usually reassuring value.
Grep for these before adding any new card.
