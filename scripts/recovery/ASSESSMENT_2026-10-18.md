# CasaRay recovery assessment — 18 Oct 2026 (tooling updated 30 Oct)

Branch `recovery/phase0-diagnostics`. Read-only assessment: nothing on the Green was changed by
this work. CR-T01 and CR-T02 stay paused. Supersedes `RESTORE_PLAN_2026-10.md`.

## Bottom line

CasaRay V2 is missing because its only registration was a `lovelace: dashboards:` entry in the
`configuration.yaml` lost around 25/09. Home Assistant regenerated the default, which registers
nothing. **No accessible backup holds that entry.** Every one was taken after 25/09. The 30/09 one
was taken by `deploy_casaray.sh` at step 1/5, before it appended anything. So a restore would roll
back logins, tokens and history without bringing CasaRay back. The minimum fix is the 12-line
dashboard-only block (`casaray_config_block.yaml`), the theme file, and one restart. It passes
Home Assistant 2026.10.1's own `check_config` offline.

Two faults are separate, and the registration does not fix them:

- the legacy *Deez Smart Home* UI dashboard is gone from `.storage/lovelace_dashboards`;
- the helpers and people CasaRay reads are `unavailable`.

## Verified (18/10, by these means)

| Finding | How |
|---|---|
| The live instance is the expected install, and its time zone survived the 29/09 repair (AEDT) | Home Assistant MCP connection, read-only calls only |
| `input_boolean.chinese_dashboard`, `person.raymond_du`, `person.ai_q_huang`, `person.vinh_du`, Family Location, `input_number.gas_bill_mj` and the four Tapo "(Direct)" streams are `unavailable`; Hue scenes and two other cameras work | same |
| None of those helpers or people is defined anywhere in git; `packages/casaray_automation.yaml` defines none of them | repo search, all branches |
| `dashboards/casaray_v2.yaml`, `themes/deez_your_name.yaml` and the package are byte-identical on `ha-deploy`, this branch and `casaray-v3-design` | git blob ids |
| `.storage` missing from Studio Code Server's Explorer proves nothing: the add-on hides it by default (`files.exclude`); it does not hide `themes/` | add-on source |
| Core 2026.10.1 still accepts `lovelace: dashboards: <slug>: mode: yaml`; only top-level `lovelace: mode: yaml` is deprecated. Its migrations only add dashboards (`lovelace`, and `map` at onboarding), never remove them; a corrupt `lovelace_dashboards` is renamed `.corrupt.<time>` and the list starts empty | Core 2026.10.1 source |
| The block passes `check_config` 2026.10.1; a deliberately broken one fails at the right line | offline, real HA 2026.10.1 |

## Live check, 30/10 (read-only)

The owner approved the v1.3 evidence workflow on 30/10. Its published copy was verified from the
cloud session: an anonymous HTTPS fetch of `17fbd86` gave `fetch_casaray_tools.sh` `060734bb…`.
That helper then verified `casaray_evidence.sh` `4da47bc1…` and `register_casaray.sh`
`56dea19d…`.

**The evidence script has still not run on the Green.** The cloud session has no route there:
- no Remote Control computer is connected;
- Desktop Commander runs inside the cloud container;
- the Home Assistant connection can read entity states, but has no file or shell access.

So the file-level questions stay open until the owner runs it. The connection does show this,
and every entity below was `ok` in the 05/09 export:

| Entity | 30/10 |
|---|---|
| `input_boolean.chinese_dashboard` (the language toggle; 503 references in CasaRay) | unavailable |
| `input_number.gas_bill_mj` | unavailable |
| `input_select.input_select_family_location_selected` (not used by CasaRay) | unavailable |
| `person.raymond_du`, `person.vinh_du`, `person.ai_q_huang` | unavailable |
| a zone named Home: `zone.home` or `zone.home_2` (both are named Home, and the connection gives no IDs) | unavailable |
| `todo.shopping_list`, Hue scenes and lights, mobile-app trackers | working |

The connection sees only entities exposed to Assist, so the other bill helpers cannot be seen
from here. CasaRay reads 114 distinct helper, person, zone and to-do IDs, and all 114 are in the
05/09 export.

What this adds to H3: every storage-collection type CasaRay reads is down together, while
config-entry integrations work. That covers people, `input_*`, and possibly the zone. Two causes
fit:
- (a) those collections' `.storage` files were lost while the entity registry survived;
- (b) the integrations are not loaded at all, as happens when `configuration.yaml` lacks
  `default_config:`.

Evidence section 5 tells them apart. If `chinese_dashboard`, `gas_bill_mj` and `raymond_du` are
still in `.storage`, the cause is (b).

## Root causes

| # | Hypothesis | Confidence |
|---|---|---|
| H1 | CasaRay: registration missing from `configuration.yaml` (lost ~25/09). Why the 30/09 `apply` did not leave it is unknown: `_recovery/casaray/` will tell | high |
| H2 | Legacy dashboard: registration missing from `.storage/lovelace_dashboards`. Its content file `lovelace.deez_smart_home` may survive | medium; cause unknown |
| H3 | Helpers and people: their YAML or `.storage` definitions are not loaded | high (symptom); source unknown |
| H4 | `/config/themes/` absent | medium |
| H5 | card-mod, WebRTC or Tapo degraded after the update | low–medium; rendering only |
| H6 | 2026.10 broke YAML dashboards | ruled out |
| H7 | the login problem caused CasaRay's loss | unlikely; it came weeks later |

## Backups

| Backup | Has CasaRay's registration? | Note |
|---|---|---|
| `casaray_pre_registration_20260930_0229` (~850 MB) | **no, by construction** | taken before the block; best place to check (names only) whether the legacy registration existed on 30/09 |
| `casaray_before_auth_recovery` (~586 MB) | no, if taken after 25/09 | date unverified |
| `before_auth_repair` (~51 MB, partial) | no, if taken after 25/09 | if dated before 25/09 it could hold the original config and the old backup key |
| automatic 18/09 (encrypted) | **the only one likely to** | key lost with `.storage/backup`; needs the emergency kit |

A larger backup is not a better candidate here. None of the archives were opened from the cloud
session: the only way to read them there streams secrets into the conversation.

## Plan and tools

1. **Evidence (v1.3, needs re-approval; never run):** `casaray_evidence.sh`, sha256
   `4da47bc1a9d540bf064eefaabd5e866682c4b6dfd0907e896b3e6014ae11bd1f`. CR-REC-25 approved v1.2
   (`168a2216…ad9ec`). v1.3 closes a gap a Codex review found: `rd()` now also requires a
   symlink's resolved target to be on the allowlist. Before, an allowlisted name linked to, say, a
   package file would have been read. It is read-only and reads a fixed allowlist of 24 files. It makes no API calls, reads no logs and prints no slugs. It needs
   to run on the Green, and the cloud session has no route there. In the Terminal & SSH add-on,
   paste it into `/tmp/casaray_evidence.sh`, then run it only if the hash matches:
   `[ "$(sha256sum /tmp/casaray_evidence.sh | cut -d' ' -f1)" = <hash above> ] && sh /tmp/casaray_evidence.sh`.
   (`get.sh` is no shortcut here: it uses `docker exec`, so it works only at the host console,
   where there is no `/config` for the script to read.)
2. **Registration (needs separate owner approval):** `register_casaray.sh check`, then `apply`. It
   takes a verified full backup, writes a dated run folder (never `_recovery/casaray/`), installs the
   theme only if missing and hash-verified, appends the dashboard-only block atomically and gates
   on `ha core check`. It restarts, confirms a new boot, and undoes itself on a failed check,
   unconfirmed restart, dead Core or recovery mode. The web terminal disconnects during the restart;
   the script keeps running (reopen the Terminal panel). Undo: the `rollback` printed at the end.
3. **Look:** open `/casaray-v2/home` on the iPad. See *Theme* below.

**Getting the scripts onto the Green: resolved 30/10, see `RUNBOOK_2026-10-30.md`, Step 0.** The
repository is public, so delivery is an anonymous Git fetch into the add-on's `/tmp`. It uses no
credential and does not touch the host clone or `/config`. `fetch_casaray_tools.sh` writes both
scripts only if both match their pinned SHA-256 values. Nothing needs pasting.

| Script | Status |
|---|---|
| `casaray_evidence.sh` | v1.3, read-only, awaiting re-approval (v1.2 was approved); 7/7 chroot fixtures, and the new symlink fixture fails on v1.2 |
| `register_casaray.sh` | ready for review; 55 scenarios / 85 runs pass, including a disk-full sweep; 3 independent reviews (15 findings, all fixed); 8 regression mutants caught |
| `casaray_config_block.yaml` | dashboard-only; identical to the block `register_casaray.sh` appends |
| `deploy_casaray.sh` | **withdrawn** (packages side effect; overwrote the 30/09 evidence; stale slug) |
| `fix_owner_login.sh`, `recover_login.sh` | `rollback` disabled; `recover_login.sh apply` refuses while a password store exists |
| `inspect_backup.sh`, `phase0.sh`, `get.sh` | unchanged |

## Platform facts behind the tools (from primary sources)

- Terminal & SSH mounts the config at `/homeassistant`, and `/config` is a symlink to it.
  Everything is BusyBox (Alpine), plus `bash`, `curl`, `git` and `jq`. There is **no python3**.
- The Supervisor proxy to the Core API returns **401** for this add-on, so liveness is probed with
  an unauthenticated `GET /manifest.json`. A probe of `/api/` would be logged as a failed login.
- `ha core check` exits non-zero on invalid config, but it **misses** a duplicate `lovelace:` key
  and a missing or broken dashboard file. Supervisor does not check config before a restart.
- With a bad config Core can boot into **recovery mode while `ha core restart` still exits 0**.
- `ha backups new` blocks until done and prints `slug: <8 hex>`, sometimes quoted. The bare
  `--homeassistant-exclude-database` flag does *not* exclude the database.

## Theme (confirmed against the frontend source)

In frontend `20260930.3` a dashboard-level `theme:` is accepted and ignored. Only a per-view
`theme:` is applied. The `theme: CasaRay` at the top of `casaray_v2.yaml` therefore does nothing:
CasaRay renders in each viewer's profile theme. Options are (a) add `theme: CasaRay` to each of the 28
views, an `ha-deploy` change that also changes the dashboard sha256 both scripts pin; (b) choose
CasaRay under Profile → Theme on the wall iPad; or (c) set a backend default theme. (b) and (c) are
live changes. For (a), the change is prepared as `theme/casaray_per_view_theme.patch` against
`ha-deploy` `18a4e5d`. It is additive only, validated, and reverses cleanly; the procedure is in
`RUNBOOK_2026-10-30.md`, Step 3.

## Not fixed by registration

- Helpers and people (H3): their definitions are not in the repo. Restore them from wherever the
  evidence pass finds them, or rebuild them (their settings are unknown).
- Legacy dashboard (H2): re-adding a UI dashboard at `deez-smart-home` re-attaches
  `lovelace.deez_smart_home` if it survives. Never *delete* a storage dashboard to undo: that
  deletes its content file. The fallback is git's `dashboards/deez_smart_home.yaml`.
- From 29/09, still open: the other three users' passwords, a new backup encryption key and
  emergency kit, and the deploy bridge `shell_command`.
