# CasaRay recovery: missing custom integrations and front-end files (November 2026)

**PLANNING ONLY. NOTHING HAS BEEN RUN ON THE GREEN.** Updated 03/11/26. Every step
that writes is marked `NOT RUN, NEEDS APPROVAL`; read-only steps say so. No tool in
this plan has produced any real output from the Green yet.

Branch `recovery/phase0-diagnostics`. PR #10 stays unmerged. Backup identifiers and
usernames are deliberately not written here; backups are described by date and type.
Record: `CFG-005` in `PROJECT_STATE.md`.

## 1. What is established

### Live and session facts

| # | Fact | Status | Source |
|---|---|---|---|
| F1 | This session runs in Anthropic's cloud: the session record reads `anthropic_cloud`; host `vm`; no `/config`, `/backup`, Supervisor token or route to the Green; no computer attached through Remote Control; the Desktop Commander connector runs in the same VM (Linux, container `vm`) | VERIFIED | session checks, 02/11 and 03/11/26 |
| F2 | The Home Assistant connector reaches the household's instance (its `Parents Room AC` matches `climate.bedroom_parents_room_ac` in the states export). It reads exposed entity states only: no files, backups, integrations or logs | VERIFIED | connector, 02/11 and 03/11/26 |
| F3 | The four Tapo `HD Stream (Direct)` camera entities read `unavailable`; `Front Door Live view` and `Smart Pet Feeder` read `idle`. Sirens, door contacts and emergency buttons are not exposed to the connector. **The cause of the unavailability is not established** | VERIFIED (state only) | connector, 02/11/26 |
| F4 | `/config/custom_components` (including `hacs`) and `/config/www/community` are missing; `/config/www` exists; the HACS config entry shows "Not loaded" | REPORTED | owner, Studio Code Server, 02/11/26 |
| F5 | Core 2026.9.2. `configuration.yaml` and empty `automations.yaml`, `scripts.yaml`, `scenes.yaml` recently recreated; `ha core check` passed; owner login and Cloud login work after a password reset | REPORTED | owner, 01–02/11/26 |
| F6 | CasaRay V3 Preview imported at `/casaray-v3` (46 views). A recent backup was downloaded outside Home Assistant; which backup, and whether the copy is complete or encrypted, is not established | REPORTED | owner, 02/11/26 |
| F7 | An automatic backup dated 01/11/26, about 1.18 GB, encrypted. Others may exist | REPORTED | owner, 02/11/26 |
| F8 | `files_survey.py` at the pinned commit `b1eab57` has sha256 `956183884c9e19812a250acbd78a6e0229ec74b1efff1129754bb8fd6fe5660e`, both from git and from the pinned raw link | VERIFIED | 03/11/26 |

### From source code (each at the version named)

| # | Fact | Source |
|---|---|---|
| S1 | Studio Code Server maps the configuration at `/config` and the backups at `/backup`, both read-write. Its image has Python 3.13, `curl`, `openssl` and the `ha` CLI, and its terminal runs `zsh` | `hassio-addons/addon-vscode` `config.yaml`, `Dockerfile` (main) |
| S2 | A backup is a plain outer tar. Inside it, `homeassistant.tar.gz` stores `/config` under `data/`, without `__pycache__`, logs, `tts/` or `.cache/`. `backup.json` is written last | Supervisor `homeassistant/module.py`, `backups/backup.py` (main) |
| S3 | Retention deletes **automatic** backups only, by count and by age. It runs daily and after **every** new backup, manual ones included | Core 2026.9.2 `backup/config.py`, `backup/manager.py` |
| S4 | Core can stream a decrypted copy of a local encrypted backup itself: `GET /api/backup/download/{id}?agent_id=hassio.local&password=…` (admin only), using `securetar==2026.4.1` | Core 2026.9.2 `backup/http.py`, `backup/util.py`, `backup/manifest.json` |
| S5 | When authentication fails, Core logs the requested URL, query string included | Core 2026.9.2 `http/ban.py` |
| S6 | Custom integrations load only when Core starts. `/local/` is registered at start only if `/config/www` exists then | Core 2026.9.2 `frontend/__init__.py` |
| S7 | The Supervisor's Core API proxy, the path an add-on must use, reads any response that is not an event stream whole into memory. So S4 through an add-on would hold a whole backup in the Supervisor's memory. **Not used** | Supervisor `api/proxy.py` `api()` (main) |
| S8 | The current Studio Code Server image installs `esphome==2026.10.1`, which requires `cryptography`. The installed add-on's version is UNKNOWN | add-on `requirements.txt` (main), PyPI metadata |
| S9 | **The UI's Download button may save a decrypted copy.** For an encrypted backup it saves a **decrypted** copy when the stored key decrypts it, with no prompt. When the key differs it asks for the backup's key, offering "download the backup encrypted". When Core cannot decrypt the backup it saves it encrypted. **So a laptop copy's encryption must be read from the file itself** | frontend 20260826.7 `backup/helper/download_backup.ts`, `dialog-download-decrypted-backup.ts`, English strings |
| S10 | That download goes from the browser to Core's own web server with a signed URL, and Core decrypts it as a stream (S4). The Supervisor's proxy (S7) is not on that path. If decryption fails part-way the stream ends early, and a browser can report a finished download of a truncated file | frontend 20260826.7 `getSignedPath` and `fileDownload`; Core 2026.9.2 `backup/http.py`, `util.py` |
| S11 | The admin WebSocket commands `automation/config` and `script/config` return an automation's or script's configuration **as the running Core holds it in memory** | Core 2026.9.2 `automation/__init__.py`, `script/__init__.py` |
| S12 | Python's `tarfile` stream mode `r|gz` never checks the gzip CRC; `gzip.GzipFile` checks it at the end of the stream | CPython 3.13 `tarfile.py` (`_init_read_gz`, `_read`) |

## 2. Safety meanwhile

- **Cameras.** Four Tapo camera streams were unavailable on 02/11 (F3). The cause is
  not established. A missing custom integration is one possibility, not a finding. The
  survey's section 4 lists every unavailable security device.
- **Sirens, door contacts and emergency buttons** cannot be seen from here. Check them on
  the house's own security pages before relying on them.

## 3. Unknown, and what answers it

| Unknown | Answered by |
|---|---|
| Whether a complete laptop copy of the 01/11 automatic backup exists, and whether it is encrypted | G0 (`backup_check.html`) |
| Which backups exist, their dates, encryption, Home Assistant version, and which are automatic | G1, section 6 |
| Which backups hold `custom_components/hacs` and `www/community`, at which versions | G0 (laptop copy), G2 |
| Automations, scripts or scenes held only in Core's memory | G1, sections 3 and 4; G5 |
| The custom integrations configured, and which are now not loaded | G1, section 4 |
| What HACS recorded as installed, and the dashboard resources registered then and now | G1, section 5; G0 or G2 |
| When and how the files went missing | not established. The newest file dates inside each backup bound it |

## 4. Gates

### G0: preserve the 01/11 automatic backup before any new backup

The step itself is read-only on the Green; it downloads a file.

1. **On the laptop:** look for a copy of *that* backup. Home Assistant names a download
   after the backup's name and date. A copy of the pre-V3 backup is a different backup.
2. **If there is none:** Settings → System → Backups → the automatic backup dated
   1 November → Download.
   - If Home Assistant asks for an encryption key, it is that backup's own key (S9).
   - Typing it gives a decrypted copy; "download the backup encrypted" keeps it encrypted.
3. **Check the copy with `backup_check.html`,** opened from disk in a desktop browser.
   Nothing is uploaded: the page's security policy forbids network requests. It reports:
   - whether the copy is complete, including every inner archive's gzip integrity;
   - whether the copy is encrypted;
   - for a plain copy, which integrations and community folders it holds.
4. **A plain (decrypted) copy holds every credential of the install in plain form.**
   - Keep it on the laptop's own disk, not in a synced folder.
   - Remove it once the recovery is closed. That is the owner's decision.
5. **For an encrypted copy, compare its SHA-256 with the Green's file** (read-only):
   ```sh
   sha256sum "/backup/<file name from survey section 6>"
   ```

### G1: survey (read-only)

The pinned link is in section 9.

1. Download the file to the laptop.
2. Drag it onto `config` in Studio Code Server's file panel. **This creates one file,
   `/config/files_survey.py`.** The survey itself writes nothing, and Home Assistant
   ignores the file.
3. Run it, hash-gated: `&&` stops the survey if the hash does not match.

```sh
echo "956183884c9e19812a250acbd78a6e0229ec74b1efff1129754bb8fd6fe5660e  /config/files_survey.py" | sha256sum -c - && python3 -I -B /config/files_survey.py survey
```

### G2: contents of candidate backups (read-only)

- **G2a, unencrypted local backups,** newest first:
  `python3 -I -B /config/files_survey.py contents SLUG`.
  - Stop at the first `COMPLETE` read that holds both folders.
  - Each read takes minutes on a Green.
  - An `INCOMPLETE` read lists nothing and is no evidence.
- **G2b, encrypted backups only.** Compared on what each would need:

| Option | How | New software on the Green | Disk on the Green | Memory | Where decrypted data exists | Assessment |
|---|---|---|---|---|---|---|
| **L1** laptop copy and two-folder payload | G0 gives a complete plain copy → `backup_check.html` "Save `casaray_payload.tar`" (only the two folders and a manifest) → drag it onto `share` in Studio Code Server → `restore_files.py` | none (Python standard library) | the payload plus one staged copy: tens of MB each, expected | browser: the two folders only; Green: streaming | the full plain copy on the laptop (already there if the UI decrypted on download); only the two folders reach the Green | **recommended** when G0 succeeds |
| **L2** upload the whole plain copy | upload the ~1.2 GB plain copy to `/share`, then `restore_files.py` | none | ~1.2 GB in `/share` until removed. A later backup that includes `share` would carry it, under that backup's own encryption | the browser upload of a large file may be slow or fail | the full plain copy on the laptop **and** in `/share` | workable, heavier |
| **G1** Core's own library on the Green | a temporary environment in `/tmp` holding `securetar==2026.4.1`, pinned and hashed. The key is typed hidden; it stream-decrypts and stages only the two folders | **installs a package**: needs approval, against the 01/11 "no development dependencies" instruction | the staged folders only | streaming; small | only the two folders are written | needs approval and a new tested tool |
| S4 through the Supervisor's proxy | removed | — | — | whole backup in the Supervisor's memory (S7) | — | **not used** |

### G3: choose the source (a decision; no change)

The source is the newest copy whose read is complete and which:

- holds `custom_components/hacs` and `www/community`;
- has a Home Assistant version of 2026.9.2, or the closest below it.

Record its date, type, version and contents, without its identifier.

### G4: keep the source safe

The source must have a copy off the Green before any change. An automatic backup is
deleted by retention as newer ones arrive, and any new backup triggers that clean-up
(S3). Changing the retention settings is the owner's decision.

### G5: memory-only configuration, checked and preserved before any restart

- G1 section 4 counts the automations, scripts and scenes **loaded** in the running Core;
  section 3 counts the entries **on disk**.
- If more are loaded than are on disk, a restart loses the difference, and **no rollback
  brings it back.** Before a restart can be proposed:
  - export them read-only from the running Core with `automation/config` and
    `script/config` (S11), to a file in `/share`, not `/config`;
  - scenes have no read-back command checked so far. Their states can be recorded from
    the entity attributes only partially.
- The exporter is written and tested only if G1 shows the need.
- Writing anything back into `automations.yaml` or `scripts.yaml` changes protected
  files, and is a separate owner decision.

## 5. Proposed changes — NOT RUN, NEEDS APPROVAL

**Only two folders are created**, from the source chosen at G3:
`/config/custom_components/` and `/config/www/community/`. Nothing that exists today is
changed or deleted.

**Not touched:** `.storage/`, any authentication file, `configuration.yaml`,
`automations.yaml`, `scripts.yaml`, `scenes.yaml`, `secrets.yaml`, `themes/`, the V3
dashboard, and every other existing file.

**Not included, each a separate decision:** `packages/`, `dashboards/`, the legacy theme
and background image, the include files' contents, dashboard resources, `deez_repo` and
the deployment bridge.

The tool is `scripts/recovery/restore_files.py` (section 9).

| Step | Command | Writes | Needs approval |
|---|---|---|---|
| 1 | `python3 -I -B restore_files.py plan SOURCE` | nothing | no |
| 2 | a manual safety backup, after G0 and G4 | adds a backup; retention may then delete surplus automatic ones (S3) | yes |
| 3 | `python3 -I -B restore_files.py stage SOURCE` | only `/share/casaray-restore/<stamp>/` | yes |
| 4 | `python3 -I -B restore_files.py apply /share/casaray-restore/<stamp>`, after typing `APPLY` | creates the two folders | yes |
| 5 | one Core restart, only after G5 is cleared | restart | yes, at that moment |
| 6 | verify (section 7), then run the survey again | nothing | no |
| 7 | if Resources is still empty once HACS loads, add back the resources the backup recorded, one at a time | Home Assistant writes `.storage` itself | yes, each |

**How `restore_files.py` is built, and what was tested.**

- **Sources:** an unencrypted backup, a decrypted copy, or the payload (whose manifest it
  checks file by file). It refuses an encrypted backup.
- **Paths:** it refuses links, devices, absolute and `..` paths, duplicates, and oversized
  or truncated entries.
  - A second check confirms that every resolved path sits inside its own folder. That
    check alone stopped three traversal shapes with the first check disabled.
  - It verifies the gzip CRC (S12).
- **Apply:**
  - It refuses if either destination exists, and creates every file exclusively.
  - It builds each folder under a temporary name and renames it into place.
  - It undoes itself on any failure, and if a protected file changes while it runs. The
    protected files are fingerprinted; `.storage/auth` is left out, because Core rewrites
    it whenever a login token refreshes.

## 6. Restart: needed once. Risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Configuration held only in memory | lost at the restart; **rollback does not bring it back** | G5 first |
| A restored integration fails on 2026.9.2 | its entry shows an error; rarely, start-up is delayed | rollback, then another restart. A source on the same version (G3) lowers the chance |
| Recovery mode | Core starts with a minimal configuration | rollback, then restart |
| Outage | cameras, automations and dashboards drop for the restart. Expected 1–3 minutes; not measured on this Green | choose the time |
| Versions older than HACS's records | HACS may offer updates | do not update during recovery |
| Dashboard resources still empty | the cards they provide still fail | step 7 |
| Logins and dashboards | the change touches neither, but a restart reloads everything. That they stay as they are is **expected, not guaranteed** | check them after (section 7) |

## 7. Verification after

- Rerun G1: HACS and the custom entries `loaded`; section 4's counts no worse.
- Settings → Devices & services: no new errors.
- The Tapo camera streams, sirens and door sensors report. If a camera is still
  unavailable, its cause is still to be established.
- Owner login, `/deez-smart-home` and `/casaray-v3` open. Note any red card.
- Settings → Dashboards → Resources, compared with what the backup recorded.

## 8. Rollback — NOT RUN, NEEDS APPROVAL

- **Command:** `python3 -I -B restore_files.py rollback /share/casaray-restore/<stamp>`,
  after typing `ROLLBACK`.
  - It removes only the files `apply` recorded, each only while unchanged, and then
    their folders once empty.
  - Anything else is listed and kept.
  - `--pycache` also removes the Python caches Home Assistant creates when it imports the
    restored code.
- **After a restart,** another restart is needed before Home Assistant stops using code it
  has already loaded.
- **What it cannot do:**
  - restore memory-only configuration lost at a restart;
  - undo resources added in step 7;
  - undo anything Home Assistant did while the restored integrations ran.
- **Last resort:** the step-2 backup. It restores `.storage` too, so it is the owner's
  decision.

## 9. Delivery and test record

| Tool | sha256 | Pinned link | Tests, 03/11/26 |
|---|---|---|---|
| `files_survey.py` | `956183884c9e19812a250acbd78a6e0229ec74b1efff1129754bb8fd6fe5660e` | https://raw.githubusercontent.com/deezr168-blip/Deez-Smart-Home/b1eab5724a469116e6caeab85085c933fb71b60f/scripts/recovery/files_survey.py | `tests/test_files_survey.py`: 54 passed |
| `backup_check.html` | `f59c7716fbf02618d2511a8ae2817341bf9a8e120dff8acd68cd3a666e6d2c36` | (stamped after commit) | `tests/test_backup_check.py`: 64 passed, in Node and in real headless Chromium |
| `restore_files.py` | `cb6b9cbb5884121a45040ebde7449384ea690198014e42e2e7ef7fb17f21a6be` | (stamped after commit) | `tests/test_restore_files.py`: 69 passed |

**What the tests establish:**

- **Write tracing:** every run was traced with `strace`. On the paths and conditions these
  tests exercised, no write-class system call fell outside the paths that step may touch.
  Snapshots showed nothing else changing. **That is evidence about those runs, not a
  guarantee** for every input, filesystem, Python version or browser.
- **Canaries:** fake secrets were planted in `secrets.yaml`, `.storage`, config entries,
  backup metadata, the token and add-on options. None appeared in any output.
- **Deliberately broken copies.** Each failed its suite:
  - for the survey: printing the token, writing a file, calling the download route;
  - for the page: a payload offered for an encrypted copy, `.storage` taken into the
    payload;
  - for the restore tool: path checks disabled, the existing-destination refusal removed,
    rollback deleting everything, the CRC drain removed, the protected-file comparison
    removed.

**Not tested:**

- a real Green, a real Home Assistant backup, real SecureTar data;
- browsers other than this Chromium build;
- Supervisor API versions beyond the two field layouts simulated;
- files larger than the fixtures.

## 10. Safeguards review (references/recovery-safeguards.md)

| # | Status |
|---|---|
| R1 plan labelled | met. Header and every write step |
| R2 read-only gates first | met. G0 to G5 come before every write, and each says what it reads |
| R3 backup before change, verified | met in the plan: G0 and G4 preserve the source; step 2 is read back |
| R4 typed confirmation | met: `APPLY`, `ROLLBACK`; a wrong word is tested to change nothing |
| R5 fingerprint what must not change | met for the stable protected files, with a tested automatic undo. `.storage/auth` is excluded, and why is recorded |
| R6 automatic rollback, defined carefully | met for `apply`: any failure undoes what it created, and an injected fault is tested. The tool restarts nothing, so "returned" is not its question |
| R7 nothing secret in output | met in the tests (canaries). No key is asked for anywhere in these tools |
| R8 tested, including tests that must fail | met within the limits in section 9 |
| R9 the platform's own tools | met. The Supervisor and Core APIs; Core decrypts in L1 and L2 (S9, S10); option G1 would use Core's own library |
| R10 withdraw wrong tooling | met. The decrypted download through the Supervisor's proxy was removed before shipping (S7) |
| R11 checked against standing constraints | met. No restore, install, restart, deletion or integration reload is run; protected files are not written |
| R12 one change at a time | met. Steps 1 to 7, each verified |
| R13 inside the protected list | met. Backups, `.storage` and the restart are all owner-approved steps |

**Ready for:** G0 and G1, both read-only. **Not ready to apply:** no source has been
chosen, and no real Green evidence exists.
