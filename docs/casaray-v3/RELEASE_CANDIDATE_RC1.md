# CasaRay V3 — preview release candidate 1 (18/11/26)

**Status: NOT RELEASED, NOT DEPLOYED.** This is a tested candidate for the
existing `/casaray-v3` preview dashboard. Nothing here has been seen in Home
Assistant or on a device. It does not authorise a merge, a write to Home
Assistant, a theme reload, an automation, or a restart. A merge needs a
separate owner approval; a deploy needs the preflight below and a further
approval. Decision record: `design/casaray-v3/DECISIONS.md` **V3-024**.

## Candidate

| Item | Value |
|---|---|
| Branch | `feature/casaray-v3-preview-rc1`, from `feature/casaray-v3-build` at `116c043` |
| Generated outputs as of | commit `edad5e076e05cd3e66410dc86b1ea6fa97a980a6`. Later commits on the branch change documentation only: `git diff edad5e0 HEAD -- dashboards/ src/ scripts/` is empty |
| Views per locale | 46, the same paths in the same order as `116c043` |
| Theme | unchanged: `src/casaray_v3/themes/casaray_v3.yaml` sha256 `17a51b9015d115e56ce7da7801625f1d1183da781059063c1641d9f40a574e21`, the runbook's pinned file. No theme install or reload is needed |

| Locale | File | Bytes | sha256 (file) | sha256 (parsed config, canonical JSON) |
|---|---|---|---|---|
| en (the preview) | `dashboards/casaray_v3.yaml` | 1,001,171 | `6ac3c7b0df4bcbf4ec187bf651a8c6df0d0857178b5ae8d16385d2ccea7a26e3` | `93420be1e11667417db13fc3d03c4d0f4562b6b4d6199a7914ad56746cfb109f` |
| yue | `dashboards/casaray_v3/dist/casaray_v3_yue.yaml` | 1,002,512 | `29d92a236073a82a64895413478985ac3b8f738a1cb54b4e70bbc79c12359295` | `467a1638fbd7616f69bc634c0777b4860e1ca71b31f9559e6e0cbad483dd90ec` |
| zh-Hans | `dashboards/casaray_v3/dist/casaray_v3_zh-hans.yaml` | 1,002,845 | `c93e5576d34d60904bca80e59a1e1f2f4b56bb0257d0610a2781113a2d780246` | `f85350a802d86512f467ed3dfda52f834d4601951e10925b443483e402bf30bb` |
| km (draft) | `dashboards/casaray_v3/dist/casaray_v3_km.yaml` | 1,053,751 | `66f12f16878ce0e701eafada41699539bb76fd5f8adf851014d8d6062af2be4e` | `ce1ded6c3c427a437afd726751614f7449bbe41bee1187b506a84928cffa51e4` |

Canonical JSON is `json.dumps(yaml.safe_load(f), sort_keys=True, ensure_ascii=False,
separators=(",",":"))`, as in `PREVIEW_DEPLOYMENT.md`; storage mode does not keep YAML
formatting, so a readback is compared on this, not on the file hash.

Pinned raw link (English), once the branch is pushed:
`https://raw.githubusercontent.com/deezr168-blip/Deez-Smart-Home/edad5e076e05cd3e66410dc86b1ea6fa97a980a6/dashboards/casaray_v3.yaml`

## What is in it

| From | Feature |
|---|---|
| PR #16 (V3-014) | Cameras: two across on the wall iPad, one on a phone, Front door first |
| PR #16 | Each camera slot is a picture or a **same-size card that says Offline in words**, with "No stream from Home Assistant" and the battery reading or "No battery reading" |
| PR #16 | A tap opens **Home Assistant's own camera dialog** (live view, full screen from its video); the six V2 stream pages stay one tap away under More boards |
| PR #16 | Privacy and detection tiles named by camera, read-only; Home's front-door camera with the same tap and Offline card |
| PR #21 (V3-022/023) | **Named, readable navigation** on every native view: header cell plus six named buttons, one row on the wall, two on a phone, every cell one height, current page inert and tinted |
| PR #21 | Home: One tap air-con names its device; people at two rows; footnote inside the plugs card; Solar expected today in Energy now; Climate now shows all four room temperatures; Shopping list at five rows |
| PR #21 | Cantonese: 氣候 for Climate (was 冷氣同天氣); 爸媽房冷氣機 for the parents' air-con |
| V3-024 | The camera card also covers `unknown` and says "State unknown"; the header marker says "Preview" |

## What is deferred

- PR #21's **Weather** and **Rubbish collection** pages, their More boards links, the
  `new_views` generator key and `header_title`.
- PR #21's **rubbish reminder automation**: not in this branch, not installed, not
  activated. `tests/v3/test_preview_rc_v3_024.py` fails if any of these arrive.
- PR #21's six-across More boards (it needed the two deferred pages).
- PR #16's equal room heights and compact icon-only top bar (superseded; V3-024 point 3).

## Evidence (offline)

| Gate | Result |
|---|---|
| `python3 scripts/v3/build_dashboard.py --check` | outputs up to date; 46 views × 4 locales, 0 missing keys |
| `python3 scripts/v3/validate_dashboard.py` | **1509 passed, 0 failed**, 30 notes (baseline `116c043`: 1425 / 0) |
| `python3 -m unittest discover -s tests/v3` | **123 tests, 0 failures** at `edad5e0` (baseline `116c043`: 93 / 0). New: `test_cameras_layout` (PR #16, adapted), `test_topbar_home_v3_023` (PR #21, adapted), `test_preview_rc_v3_024` |
| `bash scripts/ha_validate.sh` | **PASSED** (8 sections); section 8 the standing SKIP (no `hass`, no instance); 470 warnings, 4 more than the baseline, all "Camera health" in the per-locale heading class |
| Camera safety | the six verified camera IDs, Front door first, in every locale; no camera surface performs an action; every camera switch's icon does nothing |
| Missing-data honesty | Offline / State unknown in words; no 0 % battery from a dark sensor; a dark air-con reads "Offline · No data", never a stale temperature |
| Entity audit vs `116c043` | no view or entity removed or substituted; one added on Home (`sensor.presence_multi_sensor_fp300_temperature`, in the export) |
| Layout, simulated | every native view resolves 2 columns at 1180 × 820 and 1 at 390 × 844 in all four locales; Home and Cameras: no clipped label, no overflowing card |

The layout numbers come from `scripts/v3/preview_view.py --shots`: the frontend's
own grid geometry (20260826.7), approximated card interiors, fixture data. **They
are not screenshots of Home Assistant**, and nothing was checked on a device.

### Which views change on the Green

Against both recorded live revisions (`8f1ec33`, imported 02/11; `7f16e79`, the
V3-013 update approved 14/11, applied state unconfirmed) **18 of 46 views change**:
the 18 native views. The 28 carried and classic views are byte-identical. Apart from
Home and Cameras, the native views differ only in the top bar, plus the Cantonese
Climate rename where it appears.

## Known open items

- **Khmer (draft):** on a phone the Living room and Parents' room titles wrap the
  header cell (the same two PR #21 reported). Needs a native speaker's shorter titles.
- **Already on the baseline, unchanged:** "Concentrate" (Lighting scenes) and
  "Entertainment" (More boards on three room pages) clip on an English phone; Khmer
  "Bills" clips on Energy.
- **Band holes, wall iPad, simulated:** Home 21 · 31 · 11 px in Cantonese
  (43 · 31 · 32 px in English); Cameras 1 px (23 px in Cantonese).
- Native card text (tile states, "Add item", weather words) follows the Home Assistant
  user's profile language, not this build.
- The front-door camera on **Living room** and the pet-feeder camera on **Dining** still
  open their V2 stream page (`custom:webrtc-camera`) on a tap, not the native dialog;
  those views were outside this release's scope. Where WebRTC Camera is missing on the
  Green, that page shows a card error. Cameras and Home are not affected.

## Preflight on the Green — before any deploy (owner, by hand)

The steps are PR #23's gates and the runbook's own (`PREVIEW_DEPLOYMENT.md`,
*Update 14/11/26*, U1–U4). They cannot be done from an offline build.

1. **U1, read only:** the Green is reachable; `CasaRay V3 Preview` is still at
   `casaray-v3` and is **not** the default; V2 is still available; storage free space
   and the newest backup's date and size.
2. **Identify what is live:** Raw configuration editor → select all → copy to a
   timestamped text file outside the Green → close **without saving**. Compare its
   canonical JSON with `7f16e79` (`10550f25…`) and `8f1ec33` (`d92ec791…`). If it is
   neither, the owner's own edits are live: **stop** and diff before anything else.
3. **U2:** that text file is the rollback copy. Take a backup sized to the free space
   U1 reports (the 03/11 figures — about 0.6 GB free against a 1.18 GB backup — are
   historical, not today's).
4. **Resources:** whether `card-mod` and `webrtc-camera` are listed. The native views
   need neither; carried and classic views do.
5. **Cameras, read only:** each camera's state; never infer a working stream from
   `idle`. Press nothing.
6. Confirm the candidate commit and the hashes above against the file being pasted.

**Stop** on a missing rollback copy, a live config that is not understood, too little
storage, an unreachable Green, a failing gate, or a hash that does not match.

## Deploy and rollback (unchanged procedure)

- **U3:** Raw configuration editor → select all → paste the English file above → Save.
  This changes that one dashboard only. No restart, no theme reload.
- **U4:** on the wall iPad, then the iPhone: Home, the named rail on several views,
  Cameras (two across / one across, Front door first, Offline words on the dark
  cameras), a camera tap opening the native dialog, More boards, Rooms, Energy. Look
  only: no One tap button, siren, switch or helper is pressed.
- **Rollback, restart-free, exactly as the runbook says:** the same Raw configuration
  editor → select all → paste the step 2 text file → Save. The backup is the last
  resort only.
