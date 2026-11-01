# CasaRay V3 Preview — deployment runbook

**Status: NOT DEPLOYED.** Ray approved deploying V3 as a separate preview beside V2
(01/11/26). The attempt stopped at step 2, live access, because the session that
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

Screens, in order. Each is reported back before the next one is given.

| # | Screen | Changes anything? |
|---|---|---|
| A | Profile → Theme list; Settings → Dashboards (list, default, `/casaray-v3` free?, V2 present?); ⋮ → Resources (`card-mod`, `webrtc-camera`) | no |
| B | Settings → System → Backups → create, wait, download (recommended before the first change) | adds a backup only |
| C | Settings → Dashboards → Add dashboard → from scratch: `CasaRay V3 Preview`, URL `casaray-v3`, not default | adds one dashboard |
| D | open it → Edit → Raw configuration editor → replace all with the pinned dashboard file → Save | that dashboard only |
| E | theme, only if a browser file editor add-on is already installed (File editor or Studio Code Server): new file `/config/themes/casaray_v3.yaml` from the pinned theme file, then Developer tools → Actions → `frontend.reload_themes` | one file plus a theme reload; no restart. Skipped if no editor is installed: no add-on is installed for this |
| F | verify: load, rail and More boards, each "Classic V2 view" button, carried pages, missing-card or template errors; protected tiles looked at, not tapped | no |

The native views work without the theme, in the default look. The carried and
`v2-*` views need `card-mod`, `webrtc-camera` and theme `CasaRay` to look and
behave as V2 does.

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
   - run the `frontend.reload_themes` action (no restart).
   - The default `configuration.yaml` already has
     `frontend: themes: !include_dir_merge_named themes`. If it does not, the
     theme cannot load without a configuration change and a restart: report
     that instead of making it.
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
| Backup (name, date, size; downloaded to laptop) | |
| Default dashboard unchanged | |
| V2 status before / after | |
| Defects found and fixed | |
| Device checks still outstanding | wall iPad and iPhone rendering, live entity availability, camera streams |
