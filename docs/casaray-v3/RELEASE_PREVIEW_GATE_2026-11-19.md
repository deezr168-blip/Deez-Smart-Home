# CasaRay V3 — controlled preview release gate (19 November 2026)

**Status: NOT RELEASED.** Preparation only; this record does not authorise merging a feature PR, writing to Home Assistant, reloading themes, starting automations, or restarting Core.

## Release scope and selection

- Target: existing separate storage-mode `/casaray-v3` preview (not the default dashboard). Preserve V2 and its configuration.
- Baseline: `feature/casaray-v3-build`, merge `116c0430e636a739506db9754043cf755fd38a4e`; repository CI success `44371209448`. This is offline CI, not proof of the current HA Green.
- **Camera/layout candidate:** PR [#16](https://github.com/deezr168-blip/Deez-Smart-Home/pull/16), head `97e9bceccaf8737f68638f3725a87bd2750071e8`. Draft, 20 changed files, clean reported merge as inspected 19 November. Not approved for merge or deployment.
- **Defer:** PR [#21](https://github.com/deezr168-blip/Deez-Smart-Home/pull/21), head `900555a372f3e4fb006bbc556b0508a9b5f1ccb8`: new Weather and Rubbish Collection pages/reminder proposal, plus V3-023 Home/navigation changes. This release does **not** install the reminder or depend on a rubbish schedule.
- PR #16 and #21 overlap in 15 paths, notably `scripts/v3/components.py`, `src/casaray_v3/views/home.yaml`, translations, validation, and generated dashboards. **Do not merge both independently** or copy an entire generated file from one on top of the other.

## Camera-first integration brief (next coding task; not implemented by this document)

1. On an isolated integration branch from the current V3 build, bring in PR #16's camera-only improvements and reconciled Home/layout components. Preserve the camera entity IDs; never substitute an answering battery-only device for a camera.
2. Required camera behaviour: a stable 2-up iPad / 1-up phone grid; Front door first; offline/unavailable presented **in words**; picture and offline placeholder of matching size; safe native more-info/full-screen tap; no privacy, detection or recording controls.
3. **Resolve the conflicting navigation proposal deliberately:** PR #16 uses 6 icon-only 2-unit rail buttons and a 56px iPad row. PR #21 uses 6 named 3-unit buttons and a roughly 120px row, with a header cell. The proposed release preference is **named, readable navigation** while retaining the camera layout, but do not transplant PR #21's Home/new-view changes in bulk. Run measured iPad/phone layouts and accessibility checks before accepting the final rail. A brief design review of the combined result is required.
4. Preserve V3 safety invariants: HVAC read-only, dangerous camera switches inert, missing readings never reassuring, explicit owner approval on state-changing controls, all four locale outputs. Review Cantonese and Khmer wraps rather than silently suppressing labels.
5. Regenerate all output via the V3 generator, not hand-edited YAML. Require reproducible `--check`, `validate_dashboard.py`, all `tests/v3`, `scripts/ha_validate.sh`, and camera/layout tests at the **new combined head**. Merge only after a separate approval.

## Hard preflight gates — must be observed on HA Green

These facts **cannot be established by an offline repository build**. Do not assume the previous November import is still the current dashboard.

- [ ] HA Green reachable and stable at its current local IP; no rescue/recovery operation pending.
- [ ] Settings → Dashboards: identify the current `CasaRay V3 Preview` URL/path, confirm it is **not default**, and confirm V2 remains available. Record its current number of views.
- [ ] In V3 **Raw configuration editor**, select all and save an **external, timestamped rollback copy** **without saving** changes. If the existing config differs from the expected pinned baseline, inspect/diff it and preserve owner edits.
- [ ] Confirm latest completed full backup: date, size, whether readable/exported outside Green; confirm storage has enough free capacity for the chosen backup method. The old November runbook notes an earlier ~0.6 GB free versus ~1.18 GB backup. These numbers are **historical**, not a claim about today's free space.
- [ ] Confirm dashboard resources (HACS / `card-mod` / `webrtc-camera`) and `/config/themes` status. Their old missing state is **historical** and must be rechecked, especially for carried/V2 camera views.
- [ ] Review current camera entity availability and supported native camera dialogs; never infer stream operation from state `idle`. No controls are pressed during preflight.
- [ ] Confirm the exact candidate commit, generated file SHA-256 and validation run link **after** integration; record the matching rollback SHA-256.

**STOP:** missing rollback copy, dashboard mismatch not understood, insufficient storage, inaccessible HA, failing validation, or unverified candidate SHA. Never restart Core merely to apply a storage-mode dashboard update.

## Preview deployment, only after separate explicit owner approval

1. Recheck the exact pinned candidate and live rollback file hashes.
2. Update **only** the existing `/casaray-v3` dashboard in the HA UI; do not alter V2, `ha-deploy`, configuration includes, resources, automation or Core state.
3. On wall iPad landscape and iPhone, visually verify Home, Cameras, six camera slots, offline words, More boards, navigation labels, Rooms, Energy, dark/unavailable readings and language display. Do not toggle sensitive tiles.
4. Record pass/fail for each, observed live candidate hash/revision where determinable, and screenshots. A failure triggers **dashboard-only** rollback by replacing raw config from the saved copy (not a Core restart).
5. Close release gate only when the owner confirms the on-device acceptance results. Offline tests or an old runbook statement do not prove deployment.

## Current disposition

**No live verification has been performed by this review.** PR #16 and PR #21 are still unmerged drafts; the Task Control Center remains a shelved side project. This file is a deployment **preflight and integration contract**, not a deployable release candidate.

## Integration result — candidate for review (18 November 2026, V3-024)

**Status: NOT RELEASED. NOT DEPLOYED. NOT MERGED.** This section records the offline integration that the brief above asked for. Merging needs a separate owner approval, and so does deploying. Nothing was written to Home Assistant, no device was operated, nothing was reloaded or restarted, and the Task Control Center was not touched.

### What the branch holds

Branch `feature/casaray-v3-release-preview`, from `feature/casaray-v3-build` at `116c043`:

| Commit | What |
|---|---|
| `5407cd2` | merge of PR #16 head `97e9bce`, whole (camera slots, Offline cards, native full-screen tap, Cameras and Home sizing) — clean, no overlapping file |
| `32dd163` | merge of PR #23 head `e413aaa` (this document) |
| `b53eaa1` | cherry-pick of PR #21's `fd0b3df` only: the preview's button and markdown metrics from the pinned frontend (tooling; no output change) |
| `c97db94` | **V3-024**: one named, readable top bar on every native view; More boards at 4 units off the band views; `topbar_problems` gate; tests. Generates the candidate outputs below |

**Not integrated from PR #21:** the Weather and Rubbish Collection pages, the reminder proposal, `header_title`, its Home changes and the new-page generator.

### Brief items 1–5, as done

1. Camera entity IDs unchanged: Front door, North wall, East wall, South wall, Stockroom, Pet feeder, in that order (`test_front_door_first_and_no_camera_remapped`). No battery-only device stands in for a camera.
2. Two across on the wall iPad and one on a phone; Front door first. A camera that is `unavailable` shows a same-size card that says **Offline**, "No stream from Home Assistant" and the battery reading. A tap opens Home Assistant's own camera dialog. No privacy, detection or recording control is on the page; those tiles stay read-only.
3. Navigation: the **named** rail. A header (title, the time over `DD/MM/YY`, "Preview") and six named icon buttons at 3 units × 2 rows: one 120 px row on the wall iPad, two on a phone, the same bar on all 18 native views. The current page is inert and its icon amber. Measured offline in 18 views × 4 locales × 2 devices: no rail label clipped or wrapped, no header overflow, no tap target under 44 px. The cost is +64 px on the wall and +128 px on a phone for Home and Cameras. Full table: `design/casaray-v3/DECISIONS.md` V3-024. **The design review of the combined result (item 3) is still the owner's.**
4. Safety invariants unchanged and gated in all four locales. HVAC is read-only. Camera and protected switches are inert. Dark readings are never reassuring (rendered against a fully dark fixture). Every native button press asks first.
5. All outputs regenerated by the generator. Results are in the next section.

### Validation at `c97db94`

| Gate | Result |
|---|---|
| Fresh build in a clean worktree vs committed outputs | byte-identical, all four locales (reproducible) |
| `python3 scripts/v3/build_dashboard.py --check` | outputs up to date |
| `python3 scripts/v3/validate_dashboard.py` | **1509 passed, 0 failed**, 30 notes (the notes are the export's dark entities, unchanged) |
| `python3 -m unittest discover -s tests/v3` | **114 tests, 0 failures, exit 0** (533 s): the 105 at the merge, less PR #16's 3 icon-only top-bar tests, plus 12 for V3-024 |
| `bash scripts/ha_validate.sh` | **PASSED**, 8 sections; 470 warnings, the identical set to the pre-change merge (per-locale heading notes) |
| Scope, by script | 28 of 46 views byte-identical in every locale. On the 18 native views, only the top bar changed, plus More boards `grid_options` on 16 of them |
| V2, legacy, V2 themes, packages, V3 theme | unchanged |

### Candidate files (deploy only the English file; the others are for the locale dashboards if asked)

| File | sha256 | Canonical-JSON sha256 prefix | Views |
|---|---|---|---|
| `dashboards/casaray_v3.yaml` (English, `/casaray-v3`) | `f6c9c3077e8b05a5278e7f2c23dab156da836ab17bc9afc40fe445697e38c3f5` | `397be34aa8be45a1` | 46 |
| `dashboards/casaray_v3/dist/casaray_v3_yue.yaml` | `9d561831b0880bb1095e26af3b1436a06bf117d5cdce82649bbc225f1db3e7e9` | `8a5bbb67675aae4d` | 46 |
| `dashboards/casaray_v3/dist/casaray_v3_km.yaml` | `745ad272718a658cc281fdcf6e645c84e4d96ea04062df80c9c0c05a06cc16b5` | `437604df02f29e03` | 46 |
| `dashboards/casaray_v3/dist/casaray_v3_zh-hans.yaml` | `96c6823dde97ab8f8056c3adb5175f890d00a019224c4ebdacb6c2a2f199939a` | `cdfc5036832ef77e` | 46 |
| `src/casaray_v3/themes/casaray_v3.yaml` (unchanged) | `17a51b9015d115e56ce7da7801625f1d1183da781059063c1641d9f40a574e21` | — | — |

Generated by `c97db94`, and unchanged by any later documentation commit on this branch. Pin a raw link to `c97db94` or to the pull request's head; both serve these bytes. The canonical-JSON prefix is `sha256(json.dumps(yaml.safe_load(f), sort_keys=True, ensure_ascii=False, separators=(",",":")))`. Storage mode does not keep YAML formatting, so a readback is compared on this hash, not on the file's.

### Known revisions of `/casaray-v3` — what the live one might be

These are references only. **The live revision is unknown.** Ray reported the 02/11 import. The 14/11 V3-013 update was approved, and whether it was applied is not recorded.

| Revision | sha256 (English file) | Canonical-JSON prefix |
|---|---|---|
| `8f1ec33`, imported 02/11/26 (reported by Ray) | `04a214e4783d3dec8498edc340c51009cc54d6df096a70b94a99ef1cc4bbf25d` | `d92ec791c7f5bd02` |
| `7f16e79` = `116c043` build base, V3-013, approved 14/11/26, application unconfirmed | `dff3399dc5ecdc6b68766bea48e45b63273e16a6faaa9ee2ec91fac6576b2ab7` | `10550f25b91e1edc` |
| `97e9bce`, PR #16 head (never approved for deployment) | `3740755b3e2b5c14c15c53749e8a28df8d10ae7502aa149fc18ca3bd8dbf955d` | `f2635dd9380ed608` |

If the preflight copy's canonical hash matches none of these, the live dashboard holds edits made on the Green. **Stop**, diff the copy against the nearest revision, and carry the owner's edits forward before any update. Never overwrite them.

### Rollback (exact; dashboard only; no restart, no theme reload)

1. **Before any update** (preflight, read-only): open `/casaray-v3` → Edit dashboard → Raw configuration editor → select all → copy into a timestamped file **outside** the Green → close **without saving**. Then hash it:
   `python3 -c "import sys,json,yaml,hashlib;print(hashlib.sha256(json.dumps(yaml.safe_load(open(sys.argv[1],encoding='utf-8')),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:16])" COPY.yaml`
   Record the prefix and the view count beside the table above.
2. **To roll back:** the same Raw configuration editor → select all → paste the saved copy → Save. This changes that one dashboard only. Reload the page and check the view count and the title against the copy.
3. **Only if the saved copy is lost:** paste the pinned file of the revision that step 1 identified (table above). Never paste a revision that step 1 did not identify.
4. **Not part of a dashboard rollback:** V2, the default dashboard, the theme (this candidate leaves it unchanged), resources, configuration includes, Core. The full backup is the last resort, and restoring it is a separate owner-approved operation.
5. **Repository:** nothing to undo until a merge. After a merge, undo it with `git revert -m 1 <merge commit>` on `feature/casaray-v3-build`, through a pull request (never a force-push). Then run `build_dashboard.py --check`. The English output returns to `dff3399d…`.

### Live state read for this record (read-only connector, 18/11/26; states only, never playback)

| Camera (connector name) | State |
|---|---|
| Front Door Live view | idle |
| Tapo C420 East Wall HD Stream (Direct) | idle |
| Tapo C420 South Wall HD Stream (Direct) | idle |
| Tapo C200 - Stockroom HD Stream (Direct) | idle |
| Smart Pet Feeder | **unavailable**: its slot would show the Offline card |
| Tapo C425 North Wall | not exposed to the connector, so unread |

`idle` does not prove that a stream plays. That is an on-device check.

### Remaining blockers before a release

- [ ] **Owner design review** of the combined result (brief item 3). Two questions: the phone top bar is 248 px; and the clock is now bold body text under the title, smaller than PR #16's heading-size clock.
- [ ] **Owner approval to merge** this integration pull request. A separate approval is needed to deploy.
- [ ] **Every HA Green preflight gate above.** None can be done from a cloud session. The Home Assistant connector reads states only, and no computer is attached through Remote Control. In particular, the live `/casaray-v3` revision is unknown, and free space and the latest backup are historical figures only.
- [ ] Dashboard resources: `webrtc-camera` is needed only by the six V2 camera pages under More boards. The native camera tap does not need it. It was missing on 02/11 and has not been rechecked.
- [ ] Theme: the installed file's hash was never received (PREVIEW_DEPLOYMENT E2). Without the `CasaRay V3` theme, the current-page mark uses Home Assistant's default accent colour, so it is still marked.
- [ ] On-device acceptance on the wall iPad and the iPhone, per the deployment steps above.
- [ ] Native review of the Cantonese and Khmer strings. The rail labels fit in the simulation; the wording itself is still a draft.
- Not blocking, outside navigation: on a phone, Lighting's scene button "Concentrate" clips and five scene names wrap. "Classic V2 view" wraps at a word boundary.
