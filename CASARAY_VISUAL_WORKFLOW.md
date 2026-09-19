# CasaRay visual workflow — capability state

The pipeline that turns "the dashboard is committed" into "the dashboard looks
right", stage by stage, with what actually covers each one. Owner-supplied
framing, 2026-09-19; statuses below are set from implementation or execution
evidence, not from intent.

**Vocabulary.** `VERIFIED` — executed here and observed to work.
`IMPLEMENTED` — written and syntax-clean, not yet executed against the real
thing. `PARTIAL` — works for part of the stage. `PLANNED` — agreed, not
written. `MISSING` — nothing covers it.

## The fourteen stages

| # | Stage | Status | What covers it |
|---|---|---|---|
| 1 | Author dashboard YAML | VERIFIED | `dashboards/casaray_v2.yaml`, `scripts/dashboard_edit.py` |
| 2 | Validate structure and entities | VERIFIED | `scripts/ha_validate.sh` (8 sections), `dashboard_check.py` (20 checks), `reconcile_entities.py` |
| 3 | Predict what a card will SAY | VERIFIED | `.claude/skills/improve-system/scripts/render_cards.py` — live, dark and both languages |
| 4 | Prove an edit lost nothing | VERIFIED | `preserve_check.py` — views, cards, entities, nav targets, service calls |
| 5 | Commit and push | VERIFIED | `ha-deploy` + `claude/ha-dashboard-upgrades-wui7ig` |
| 6 | Reach the host clone | VERIFIED | `CFG-003` resolved; pushes land in `/config/deez_repo` |
| 7 | Sync into `/config/dashboards/` | PARTIAL | `scripts/sync_casaray_to_config.sh` — exists, **owner runs it manually** |
| 8 | Reload / restart safely | IMPLEMENTED | `scripts/casaray_safe_deploy.sh` — never executed from here |
| 9 | Confirm HA accepted the config | IMPLEMENTED | `casaray_health_check.sh`, `casaray_sync_status.sh` |
| 10 | **Capture the rendered page** | IMPLEMENTED | `scripts/casaray_capture.sh` — every path exercised against a stand-in; never yet run against the instance |
| 11 | Read the capture back | VERIFIED | a committed PNG is read from the repository like any other file |
| 12 | Compare against the approved render | PARTIAL | by eye, against `docs/mockups/` + `docs/CASARAY_MOCKUPS_2026-09-14.md`. No automated diff |
| 13 | Record the defect | VERIFIED | `DASHBOARD_ISSUES.md`, `LIVE_VERIFICATION_QUEUE.md` |
| 14 | Close the loop without a human | MISSING | stage 7 is manual and stage 10 needs a machine on the LAN |

## Where the loop actually breaks

Until 2026-09-19 the bottleneck was **stage 10**. Every visual correction this
project has made — the 14/09 mockup transcription, the 15/09 geometry
corrections, the 19/09 live render review — began with Ray photographing the
wall iPad. That image is not persisted, cannot be diffed against the previous
one, and the loop cannot advance while he is asleep.

`scripts/casaray_capture.sh` closes it from the other side: a PNG in
`artifacts/screenshots/`, with a sidecar recording the viewport, settle time,
method and repository commit, committed like any other file and read back
here. What it cannot do is run itself — see below.

The bottleneck is now **stages 7 and 10 together**, and both are the same
problem: this build environment has no route to the instance. It is not a
missing tool.

## What was verified, and how

Against a local stand-in that serves the HA markers (`serve.py`, scratch —
`hui-sections-view` for a dashboard, `ha-auth-flow` for the login form):

| Behaviour | Result |
|---|---|
| Authenticated dashboard → capture | PNG written, 2360×1640 at 1180×820 @2x, read back and legible |
| Login page → refuse | exit 1, token instructions printed, **no PNG written** |
| Unreachable host → refuse | exit 1, "UNREACHABLE", nothing attempted |
| `--check` | diagnosis only, exit 0, writes nothing |
| Multiple views + `--label` | three PNGs and three sidecars, correctly named |
| `--all` view enumeration | 21 top-level views, subviews correctly excluded |
| Sidecar contents | no host, no token, no credential-shaped string |
| `ha_validate.sh` binary exception | a PNG in `artifacts/screenshots/` passes; a PNG anywhere else still fails |

Two defects were found and fixed during that run, both of which would have
misled on the real host:

- **The reachability probe reported an unreachable host as reachable.** `curl`
  prints its own `000` on failure *and* exits non-zero, so `|| echo 000`
  appended a second one; `000000` is not equal to `000`, so the check passed.
  The script would have gone on to probe and screenshot a host that was not
  answering.
- **A "Chromium hangs on restricted egress" diagnosis was wrong.** The stall
  was the stand-in serving `application/octet-stream`: headless Chromium
  *downloads* anything that is not HTML and then waits, which is
  indistinguishable from a network stall. Home Assistant serves `text/html`,
  so this would never have bitten on the real instance — but the comment
  justifying a set of flags by a hang that was never observed from that cause
  has been corrected rather than left standing.

## What is still not verified, and cannot be from here

`homeassistant.local` does not resolve in this environment and HTTP returns
`000`. There is no `/config`, no supervisor, no `ha` CLI. So:

- the script has never authenticated against a real Home Assistant,
- the `localStorage`/`hassTokens` seeding has never been exercised against the
  real frontend,
- 4000 ms has never been shown to be long enough for CasaRay to settle,
- and no capture of the actual dashboard exists.

**One host-side run closes all four.** On any LAN machine with Chromium:

    sh scripts/casaray_capture.sh --url http://<ha-host>:8123 --check
    sh scripts/casaray_capture.sh --url http://<ha-host>:8123 --label first home

Then commit `artifacts/screenshots/`. Recorded as `CAP-001`–`CAP-003` in
`LIVE_VERIFICATION_QUEUE.md`.

## Build order for the rest

| Priority | Item | State |
|---|---|---|
| 1 | `casaray_capture` | built; awaiting one host-side run |
| 2 | Automated mockup diff (stage 12) | not started — needs a real capture first, since the comparison basis is unknown until one exists |
| 3 | Capture on a schedule | blocked on priority 1 |
| 4 | Sync automation (stage 7) | **owner decision** — it changes what is on the wall, so it is not an autonomous build |
| 5 | Regression alarm on visual drift | blocked on priority 2 |
| 6 | CasaRay controller tying 1–5 together | last, deliberately |

Priorities 2 and 5 are deferred for a reason worth stating: an image diff
built against a stand-in would encode the stand-in's layout, and the first
real capture is likely to change what "comparable" means (device pixel ratio,
scrollbar width, whether the iPad's rendering matches a desktop Chromium at
the same viewport). Building it now would be building it twice.
