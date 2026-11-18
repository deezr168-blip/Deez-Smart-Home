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
