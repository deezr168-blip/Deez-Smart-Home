# CasaRay V3 Preview — deployment runbook

**Status: NOT DEPLOYED** (01/11/26). Ray has repaired `configuration.yaml`. The
pre-V3 backup is requested but not yet confirmed. The theme is not loaded and the
dashboard has not been created. Live state and the restart answer are in the two
sections after the browser-only path.

Ray approved deploying V3 as a separate preview beside V2
(01/11/26). The first attempt stopped at step 2, live access, because the session that
picked it up runs in Anthropic's cloud, not on Ray's laptop:

- The session record reads `environment_kind: anthropic_cloud`.
- The container has no `/config`, no `ha` command, no SSH client and no route to
  the home network.
- No computer is connected to that session through Remote Control.
- Its Home Assistant connector is the voice-assistant API, which reads entity
  states and runs intents. It cannot create backups, list or register
  dashboards, write files or reload themes.

Nothing on the Green was read for configuration or changed.

**Superseded 01/11/26 by the browser-only path below; kept for the record.** To proceed:
run Claude Code on the laptop itself, in this repository at the
candidate below, on the same network as the Green and with an existing
authorised credential available to it. Alternatively, connect the laptop to the
cloud session through Remote Control. Steps 3–9 are written for that session,
and for Ray to follow by hand if preferred.

## Browser-only path (chosen 01/11/26: the laptop cannot run Claude Code)

Ray performs every step in the Home Assistant web UI. Claude guides one screen
at a time and records what Ray reports. Deployment is claimed only after Ray
confirms the live result.

Direct downloads, pinned to the verified commit. Both were checked
byte-identical to the commit on 01/11/26:

| File | Pinned raw link | sha256 |
|---|---|---|
| Dashboard (English) | https://raw.githubusercontent.com/deezr168-blip/Deez-Smart-Home/8f1ec337e28e1cdd86154668175e1b9f903f22c4/dashboards/casaray_v3.yaml | `04a214e4783d3dec8498edc340c51009cc54d6df096a70b94a99ef1cc4bbf25d` |
| Theme `CasaRay V3` | https://raw.githubusercontent.com/deezr168-blip/Deez-Smart-Home/8f1ec337e28e1cdd86154668175e1b9f903f22c4/src/casaray_v3/themes/casaray_v3.yaml | `17a51b9015d115e56ce7da7801625f1d1183da781059063c1641d9f40a574e21` |

Screens, in the order now being followed. Each is reported back before the next one is
given. The theme and dependency screens (E1–E3) come before the dashboard (C, D),
because they decide whether the theme can be loaded without losing anything.

| # | Screen | Changes anything? | Status 01/11/26 |
|---|---|---|---|
| A | Settings → Dashboards: list, default, `/casaray-v3` free?, V2 present? Its theme and resource checks moved to E1 | no | given; results not yet reported. Needed before C |
| B | Settings → System → Backups: confirm `config-repaired-pre-v3` completed, then download it to a place outside the Green | no (download only) | backup requested; completion not confirmed |
| E1 | Read-only: themes loaded now (Profile) against theme files on disk; resource URLs (⋮ → Resources) against the folders that serve them | no | next, after B |
| E2 | Studio Code Server (installed and in use): upload the pinned theme as `/config/themes/casaray_v3.yaml`, then check its sha256 in the terminal | one new file | after E1 |
| E3 | Developer tools → Actions → `frontend.reload_themes`, **only if E1 shows every theme loaded now has its file on disk** | theme reload; no restart | after E2 |
| C | Settings → Dashboards → Add dashboard → from scratch: `CasaRay V3 Preview`, URL `casaray-v3`, not default | adds one dashboard | not started |
| D | open it → Edit → Raw configuration editor → replace all with the pinned dashboard file → Save | that dashboard only | not started |
| F | verify: load, rail and More boards, each "Classic V2 view" button, carried pages, missing-card or template errors; protected tiles looked at, not tapped | no | not started |

The native views work without the theme, in the default look. The carried and
`v2-*` views need `card-mod`, `webrtc-camera` and theme `CasaRay` to look and
behave as V2 does.

## Live state, 01/11/26 — reported by Ray, not seen by Claude

The session's tools run in Anthropic's cloud. Everything in this table comes from Ray's
report.

| Item | State |
|---|---|
| `/config` before the repair | held only hidden folders, with no `configuration.yaml` |
| `configuration.yaml` | recreated by Ray: `default_config:`, `frontend: themes: !include_dir_merge_named themes`, `automation:` / `script:` / `scene:` includes. This is Home Assistant's own default file (`DEFAULT_CONFIG` in `homeassistant/config.py`, 2026.10.1) |
| Include files | were missing; Ray created them. Their contents are not recorded here |
| `/config/themes/` | exists. What it contains is checked at E1 |
| `ha core check` | passed twice |
| Core | **not restarted** |
| Backup `config-repaired-pre-v3` | requested; completion not confirmed |
| V3 | not deployed. No theme file, no dashboard |

## Restarts and reloads — Home Assistant 2026.10.1 source

Read from `homeassistant/components/frontend/__init__.py`, `homeassistant/bootstrap.py`,
`homeassistant/config.py` and `homeassistant/components/config/view.py` at tag `2026.10.1`.

**Loading a theme: reload, no restart.**

- `frontend` is in Core's `DEFAULT_INTEGRATIONS`. It is set up at every start except in
  recovery mode, whatever `configuration.yaml` says, so its `reload_themes` action already
  exists in the running Core.
- `frontend.reload_themes` re-reads `configuration.yaml` from disk and takes
  `frontend: themes:` from it. So the `themes:` line Ray has just written takes effect on a
  reload, even though Core was started without it.
- **The reload replaces the set of loaded themes; it does not add to it.**
  - A theme that is loaded now but has no file in `/config/themes` disappears from the
    running Core.
  - If the backend default theme (`frontend.set_theme`) is not in the new set, it falls back
    to `default`.
  - E1 rules both out before E3 is run.
- If a theme fails validation, the reload fails and changes nothing.

**Read only when Core starts, so a change needs a restart.** The preview needs none of these:

- `default_config:` and the integrations it brings in;
- `frontend: extra_module_url`;
- YAML-mode `lovelace: dashboards:`. The preview is a storage-mode dashboard created in the
  UI, so it needs no restart.

**`automation:`, `script:` and `scene:` includes.**

- Core reads them at start-up, and again when each one's own reload action runs.
- The UI editors read the file, change one entry, write the whole file back, then reload.
- The include files were recreated just now. Whether they hold what the running Core
  loaded is unknown.
- Until the recovery track settles that, during this preview:
  - run no automation, script or scene reload;
  - run no "All YAML configuration" reload;
  - save nothing in those three editors.

**Restart hazard (recovery track, not part of the preview).** A Core restart now would start
from what is on disk. Anything the running Core loaded from files that have since gone
missing would not come back.

## Candidate

| Item | Value |
|---|---|
| Source commit | `8f1ec337e28e1cdd86154668175e1b9f903f22c4` (`feature/casaray-v3-build`) |
| Dashboard to deploy (English) | `dashboards/casaray_v3.yaml`, sha256 `04a214e4783d3dec8498edc340c51009cc54d6df096a70b94a99ef1cc4bbf25d`, 46 views |
| Parsed config, canonical JSON | sha256 prefix `d92ec791c7f5bd02` (`json.dumps(yaml.safe_load(f), sort_keys=True, ensure_ascii=False, separators=(",",":"))`) — compare a readback against this, since storage mode does not keep YAML formatting |
| V3 theme | `src/casaray_v3/themes/casaray_v3.yaml`, sha256 `17a51b9015d115e56ce7da7801625f1d1183da781059063c1641d9f40a574e21`, theme `CasaRay V3` (dark, light) |
| V2 theme (carried and classic views) | `themes/deez_your_name.yaml`, sha256 `ef7dc9fb2445a6baa2f597fc143927b6da2a60142aef2d0f76dc211f79fdb614`, theme `CasaRay` |
| Other locales (not part of the preview unless asked) | `dashboards/casaray_v3/dist/casaray_v3_{yue,km,zh-hans}.yaml`, at `/casaray-v3-yue`, `/casaray-v3-km`, `/casaray-v3-zh` |

**The preview URL must be `casaray-v3`.** Every internal link in the English
build is `/casaray-v3/<view>`. A different URL needs a rebuild with a different
`url_base` in `src/casaray_v3/manifest.yaml`.

**Dependencies:**

- The 18 native views use native cards only.
- The carried views and the `v2-*` fallback views use `card_mod` (216 uses in the English build),
  `custom:webrtc-camera` (the six camera stream pages) and the V2 theme
  `CasaRay`.
- Without those, the native views still work; the carried and fallback views
  show card errors or default styling.

## 1. Read-only pre-checks (record each result)

1. **Version:** Settings → About shows the Home Assistant Core version (V3 was
   written against frontend `20260930.3` / Core 2026.10.1).
2. **Dashboards:** Settings → Dashboards. Confirm that `/casaray-v3` is **not
   in use**. Record which dashboard is the default, and whether CasaRay V2
   (`/casaray-v2`) is registered and opens. On 30/10 it was not registered;
   see `scripts/recovery/RUNBOOK_2026-10-30.md` on `recovery/phase0-diagnostics`.
3. **Resources:** Settings → Dashboards → ⋮ → Resources. Note whether
   `card-mod` and `webrtc-camera` are listed.
4. **Themes:** Profile → Theme lists the installed themes. Note whether
   `CasaRay` and `CasaRay V3` are present.

Stop if `/casaray-v3` is already taken. That is not a preview-scope decision.

## 2. Backup (before any change)

Settings → System → Backups → **Create backup** (full, including the
database). Wait until it shows as completed, then **download** it to the
laptop, separately from the Cloud copy. Record only its name, date and size
here, never its contents or the encryption key.

On 01/11/26 the backup is `config-repaired-pre-v3`, requested after the
`configuration.yaml` repair. Before E2 it must be confirmed in the list with:

- a completion date and time;
- a size, not a few KB;
- its locations;
- its contents: Home Assistant settings and history, and which add-ons and folders.

Downloading it to the laptop, plus a second copy kept off the laptop, completes this step.

**This backup holds the repaired state.** It is the rollback point for the preview. It is not
a copy of the files that went missing from `/config`. The older backups are what might hold
those, so keep them. Automatic backups can be rotated out by the retention setting. A
downloaded copy is the safe one; do not change the setting for this.

## 3. Deploy — restart-free

A UI-created (storage-mode) dashboard needs no restart. A YAML-mode
registration in `configuration.yaml` would; do not use it for the preview.

1. Settings → Dashboards → **Add dashboard** → *New dashboard from scratch*.
   - Title: `CasaRay V3 Preview`
   - URL: `casaray-v3`
   - Icon: `mdi:home-heart`
   - Show in sidebar: on
   - Admin only: Ray's choice
   - **Do not set it as the default.**
2. Open it → ⋮ → **Edit dashboard** → ⋮ → **Raw configuration editor**.
   Replace everything with the full contents of `dashboards/casaray_v3.yaml`
   (about 990 KB) and save.
3. Install the theme, recommended for the look but not needed for function:
   - copy `src/casaray_v3/themes/casaray_v3.yaml` to `/config/themes/casaray_v3.yaml`
     (Studio Code Server or the Terminal & SSH add-on);
   - run the `frontend.reload_themes` action (no restart). It re-reads
     `configuration.yaml`, so a `themes:` line added since Core started is
     honoured. It **replaces** the loaded themes, so first confirm that every
     theme loaded now has its file in `/config/themes` (screen E1).
   - The default `configuration.yaml` has
     `frontend: themes: !include_dir_merge_named themes`. Ray reports it present
     on 01/11/26. If it were missing, adding it would be a configuration change:
     report that instead of making it.
4. **Optional:** if the `CasaRay` theme is missing, it comes from
   `themes/deez_your_name.yaml`, verified by the hash above. It is the same
   hash that `register_casaray.sh` on `recovery/phase0-diagnostics` pins and installs.

A scripted session may do steps 1–2 over the WebSocket API
(`lovelace/dashboards/create`, then `lovelace/config/save` with
`url_path: casaray-v3`). Check the message fields against the installed version
before sending.

## 4. Verify (no device is switched, no siren, button or helper is touched)

- `/casaray-v3/home` opens. Open each native view from the rail and More
  boards: home, lighting, climate, cameras, energy, security, network, rooms,
  living-room, kitchen, dining, parents-room, ray-bedroom, garage, guest-room,
  house-health, alerts, people.
- On each native view, follow its "Classic V2 view" button and confirm the
  `v2-<path>` page opens. Follow the carried pages: bills, bills-details,
  automations, entertainment, and the six camera stream pages.
- Look for red "Custom element doesn't exist" or "Configuration error" cards,
  and template errors in Settings → System → Logs. Expected only where a
  resource above is missing, and only on carried / classic views.
- **Read only, do not tap:** confirm that the protected tiles do not offer a
  toggle. These are: the camera privacy, detection and alert switches; the
  socket strips; the freezer and kitchen plugs; the sensing switches; the
  bulb-power wall switches; the air-con; and the Core, Supervisor and OS
  updates. The filter reset must ask before acting, so do not confirm it.
- **Readback:** fetch the saved config and compare its canonical JSON hash
  with the one above.
- Check that `/casaray-v2`, if registered, and the default dashboard still open
  as before.
- Viewport checks (iPad 1180 × 820, iPhone 390 × 844) in a desktop browser are
  simulations. Say so, and do not report them as device checks.

## 5. Rollback (exact)

1. Settings → Dashboards → `CasaRay V3 Preview` → **Delete**. This removes only
   that dashboard and its own stored config. V2, the legacy dashboard and the
   default are not touched.
2. If the theme was installed: delete `/config/themes/casaray_v3.yaml`, then
   run `frontend.reload_themes`.
3. No restart is needed for either step. The backup from step 2 is the last
   resort, and is not needed for a preview rollback.

## 6. Deployment record (fill in when done)

| Field | Value |
|---|---|
| Deployed at (local time) | |
| Deployed by (session) | |
| Home Assistant Core / frontend version | |
| URL | `/casaray-v3` |
| Source commit | |
| Readback canonical-JSON sha256 matches candidate | |
| Theme installed (`CasaRay V3`) | |
| Backup (name, date, size; downloaded to laptop) | `config-repaired-pre-v3`, requested 01/11/26. Completion, size and download not yet confirmed |
| Default dashboard unchanged | |
| V2 status before / after | |
| Defects found and fixed | |
| Device checks still outstanding | wall iPad and iPhone rendering, live entity availability, camera streams |
