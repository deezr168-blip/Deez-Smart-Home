# CasaRay recovery: missing custom integrations and front-end files (November 2026)

**PLANNING ONLY. NOTHING RUN.** Every step that writes is marked
`NOT RUN, NEEDS APPROVAL`. The read-only survey (G1, G2) may be run by the owner
whenever convenient; nothing else may be run without the owner's approval.

Branch `recovery/phase0-diagnostics`. PR #10 stays unmerged. Backup identifiers
and usernames are deliberately not written here; backups are described by date
and type.

## 1. What is established (02/11/26)

| # | Fact | Status | Source |
|---|---|---|---|
| F1 | Claude's tools run in Anthropic's cloud: host `vm`, no `/config`, no `/backup`, no Supervisor token, `supervisor` does not resolve, no computer attached through Remote Control | VERIFIED | session checks, 02/11/26 |
| F2 | The Home Assistant connector reaches the household's instance (its `Parents Room AC` matches `climate.bedroom_parents_room_ac` in the states export). It reads exposed entity states only: no files, backups, integrations or logs | VERIFIED | connector, 02/11/26 |
| F3 | Exposed cameras: the four Tapo `HD Stream (Direct)` cameras are `unavailable`; `Front Door Live view` and `Smart Pet Feeder` are `idle`. Sirens, door contacts and emergency buttons are not exposed to the connector | VERIFIED (cause UNKNOWN) | connector, 02/11/26 |
| F4 | `/config/custom_components` (including `hacs`) and `/config/www/community` are missing; `/config/www` exists; the HACS config entry shows "Not loaded" | REPORTED | owner, Studio Code Server, 02/11/26 |
| F5 | Core 2026.9.2. `configuration.yaml` and empty `automations.yaml`, `scripts.yaml`, `scenes.yaml` recently recreated; `ha core check` passed; owner login and Cloud login work after a password reset | REPORTED | owner, 01–02/11/26 |
| F6 | CasaRay V3 Preview imported at `/casaray-v3` (46 views). A recent backup was downloaded outside Home Assistant | REPORTED | owner, 02/11/26 |
| F7 | An automatic backup dated 01/11/26, about 1.18 GB, encrypted. Others may exist | REPORTED | owner, 02/11/26 |

From source code, read 02/11/26 (each at the version named):

| # | Fact | Source |
|---|---|---|
| S1 | Studio Code Server maps the Home Assistant configuration at `/config` and the backups at `/backup`, both read-write. Its image has Python 3.13, `curl`, `openssl` and the `ha` CLI | `hassio-addons/addon-vscode` `config.yaml`, `Dockerfile` (main) |
| S2 | A backup is a plain outer tar. Inside it, `homeassistant.tar.gz` stores `/config` under `data/`. It excludes `__pycache__`, `*.log`, `tts/` and `.cache/`. `backup.json` is written last | Supervisor `homeassistant/module.py`, `backups/backup.py` (main) |
| S3 | Retention deletes **automatic** backups only (both the copies limit and the days limit). It runs daily and after **every** backup is created, manual ones included | Core 2026.9.2 `backup/config.py`, `backup/manager.py` |
| S4 | Core can itself stream a decrypted copy of a local encrypted backup: `GET /api/backup/download/{id}?agent_id=hassio.local&password=…` (admin only). It decrypts with `securetar==2026.4.1` | Core 2026.9.2 `backup/http.py`, `backup/util.py`, `backup/manifest.json` |
| S5 | When authentication fails, Core logs the requested URL, query string included (`Requested URL: '…'`) | Core 2026.9.2 `http/ban.py` |
| S6 | Custom integrations load only when Core starts. `/local/` is registered at start only if `/config/www` exists then | Core 2026.9.2 `frontend/__init__.py` |
| S7 | **The Supervisor's Core API proxy reads any response that is not an event stream whole into memory before passing it on.** So S4 is unusable from an add-on for a backup of this size: about 1.2 GB would sit in the Supervisor's memory on a Green | Supervisor `api/proxy.py` `api()`, `await client.read()` (main) |
| S8 | The current Studio Code Server image installs `esphome==2026.10.1`, which requires `cryptography==50.0.2`. The installed add-on's own version is UNKNOWN | add-on `requirements.txt` (main), PyPI metadata |

## 2. Safety meanwhile

- **Cameras.** Four Tapo camera streams are unavailable now (F3).
  - Whether that is because their integration is a missing custom one is
    UNKNOWN. The survey's section 4 lists every unavailable security device.
- **Sirens, door contacts and emergency buttons** cannot be seen from here.
  - Check them on the house's own security pages before relying on them.
- If any of them belongs to a custom integration, it stays down until the
  integration's files are back and Core has been restarted once.

## 3. Unknown, and what answers it

| Unknown | Answered by |
|---|---|
| Which backups exist, their dates, encryption, Home Assistant version, and whether each is automatic | G1, section 6 |
| Which backups still hold `custom_components/hacs` and `www/community`, and which versions | G2 |
| Whether the running Core holds automations, scripts or scenes that exist only in memory | G1, sections 3 and 4 (loaded counts against on-disk entry counts) |
| Which custom integrations were configured, and which are now not loaded | G1, section 4; G2, C6 |
| What HACS recorded as installed, and the dashboard resources registered then and now | G1, section 5; G2, C6 |
| When and how the files went missing | not established; the newest file dates in each backup (G2, C1) bound it |

## 4. Read-only gates

### G1: survey (fast, read-only)

The tool is `scripts/recovery/files_survey.py`, sha256
`956183884c9e19812a250acbd78a6e0229ec74b1efff1129754bb8fd6fe5660e`.

1. Download it from the pinned link in the delivery record (section 9).
2. Drag it into Studio Code Server's Explorer, onto `config`.
3. In the Studio Code Server terminal, check the hash; it must match the one above:

```sh
sha256sum /config/files_survey.py
```

4. Run the survey:

```sh
python3 -I -B /config/files_survey.py survey
```

**What it reads:**

- the folder names, counts and sizes in `/config`;
- the dates of three `.storage` files;
- the entry counts of the three include files;
- `configuration.yaml`'s top-level keys;
- the `themes/` hashes;
- selected fields of `.storage/hacs.repositories`, `lovelace_resources` and
  `lovelace_dashboards`;
- the Supervisor and Core APIs, through GET requests only;
- each `/backup/*.tar`'s `backup.json`;
- folder and archive names under `/share`, `/media`, `/addon_configs`, `/addons`
  and `/config`.

**What it never opens or prints:** `secrets.yaml`, `.storage/auth*`, any token,
key, password, username or config-entry title.

The file can stay in `/config`; Home Assistant ignores it.

### G2: contents of candidate backups (slow, read-only)

**G2a: unencrypted local backups.** Start with the newest that G1 lists:

```sh
python3 -I -B /config/files_survey.py contents SLUG
```

- It reads the file in `/backup` directly, as a stream. It never goes through the
  Supervisor's proxy.
- Each backup takes several minutes on a Green: all of its `homeassistant.tar.gz` is
  read, the database included. Run it at a quiet time.
- A read that ends `INCOMPLETE` lists nothing. An incomplete read is no evidence of
  what a backup lacks.

**G2b: encrypted backups, for example the automatic one dated 01/11.**

The tool does not open these. A first version streamed Core's decrypted download
(S4) through the Supervisor's proxy. It was removed before it was ever shipped,
because the proxy would hold the whole backup in memory (S7).

| Option | What it involves | Risk | Needs |
|---|---|---|---|
| A. Not needed | an unencrypted backup in G2a already qualifies under G3 | none | nothing |
| B. Core's own library, on the Green | a temporary, isolated Python environment under `/tmp` in Studio Code Server, holding `securetar==2026.4.1` (the version Core pins, S4), hash-pinned. The key is typed hidden; names only are read; nothing is extracted. The environment lives only in the add-on container's `/tmp`, outside `/config`, the add-on's `/data` and every backup, and is removed by deleting that one folder | installs a package in the add-on container, against the 01/11 instruction "no development dependencies on the Green" | owner approval, then a tested tool |
| C. A decrypted download in the laptop's browser | the decrypted backup then sits on the laptop in plain form, with every credential in it | high: all secrets in plaintext outside the Green | not recommended |

A restore of any kind is excluded.

### G3: choose the source backup (decision, no change)

The source is **the newest backup whose read is `COMPLETE`**, and which also:

- holds `custom_components/hacs` and `www/community`;
- has a Home Assistant version of 2026.9.2, or the closest below it.

Record its date, type, version, and the list of integrations and community folders,
**without its identifier**.

### G4: keep the source safe (download only)

**Download the source backup off the Green before any change.**

- An automatic backup is deleted by retention as newer automatic ones arrive (S3).
- **Creating any backup**, the safety backup in step 1 included, can trigger that
  deletion.
- Changing the retention or schedule settings is the owner's decision, and is not
  part of this plan.

### G5: restart-risk check (read-only)

Compare G1 section 4 (automations, scripts and scenes **loaded** in the running Core)
with section 3 (entries **on disk**).

- If more are loaded than are on disk, a restart removes them.
- **Stop.** Those files are on the owner's do-not-overwrite list, so this is a
  separate decision.

## 5. Proposed changes — NOT RUN, NEEDS APPROVAL

Only **two folders are created**; nothing that exists today is changed:

| Created | From | Contents |
|---|---|---|
| `/config/custom_components/` | the source backup's `data/custom_components/` | every integration in it, as listed in G2 C2 |
| `/config/www/community/` | the source backup's `data/www/community/` | every folder in it, as listed in G2 C3 |

**Not touched:** `.storage/`, any authentication file, `configuration.yaml`,
`automations.yaml`, `scripts.yaml`, `scenes.yaml`, `secrets.yaml`, `themes/`, the
V3 dashboard and every other existing file. Nothing is deleted.

**Not included, each a separate decision:**

- `packages/` and `dashboards/` (the CasaRay V2 YAML file);
- `themes/deez_your_name.yaml` and `www/your_name_night_sky.jpg`;
- the contents of the include files;
- re-registering dashboard resources;
- `deez_repo` and the deployment bridge.

| Step | Reads or writes | Needs approval |
|---|---|---|
| 1. Safety backup (manual), verified by reading its info back | adds one backup. Retention may then delete surplus automatic backups (G4 first) | yes |
| 2. Stage: stream the source backup and extract **only** `data/custom_components/` and `data/www/community/` into `/share/casaray-restore-<date>/`, outside `/config`. An encrypted source is staged only by the method G2b settled on. Compare file counts and manifest versions with G2 | writes in `/share` only | yes |
| 3. Apply: copy the two staged folders into place, only if both targets are still absent, after typing `APPLY` | creates the two folders | yes |
| 4. One Core restart, only after G5 has passed | restart | yes, at that moment |
| 5. Verify (section 7), then rerun G1 | read-only | no |
| 6. If the Resources list is still empty once HACS has loaded, add back the resources the backup recorded (G2 C6), one at a time, in Settings → Dashboards → Resources | Home Assistant writes `.storage` itself | yes, each |

Before and after step 3, fingerprint the following, and print only `unchanged: yes/no`
(R5, R7):

- `.storage/core.config_entries`;
- the `.storage/auth*` files;
- `configuration.yaml` and the three include files.

The staging and apply tooling is written and tested only once G3 has named the
source (R12). Its form depends on whether the source is encrypted.

## 6. Restart: needed once. Risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Configuration held only in memory | automations, scripts or scenes the running Core has but the files do not are gone after the restart | G5 stops the plan first |
| A restored integration fails on 2026.9.2 | its entry shows an error. Rarely, start-up is delayed | rollback (section 8). The source backup's own version (G3) makes this unlikely |
| Recovery mode | Core starts with a minimal configuration | rollback |
| Outage | cameras, automations and dashboards drop for the restart, typically 1–3 minutes on a Green | choose the time |
| Versions older than HACS's records | HACS may offer updates | do not update during recovery (no reinstall) |
| Dashboard resources still empty | card-mod, Mushroom, kiosk-mode and webrtc-camera still do not load on the dashboards that use them | step 6 |
| Not affected | logins (`.storage/auth*` untouched), the V3 preview (storage mode), `/config/themes` (loaded at start) | none needed |

## 7. Verification after

- G1 again: HACS and the other custom-integration entries `loaded`, and the counts
  in section 4 unchanged or better.
- Settings → Devices & services: no new errors.
- The four Tapo camera streams, the sirens and the door sensors report.
- `/deez-smart-home` and `/casaray-v3` open. Note any red card.
- Settings → Dashboards → Resources: compared with G2 C6.

## 8. Rollback — NOT RUN, NEEDS APPROVAL

- **Before the restart:** remove the two folders step 3 created, after typing
  `ROLLBACK`. Neither existed before, and nothing else was changed.
- **After the restart:** remove the same two folders and restart once more. Home
  Assistant then returns to today's state, with the custom integrations not loaded.
- **Last resort:** the step-1 backup. Restoring it also restores `.storage`, which the
  owner has excluded, so it is the owner's decision.

## 9. Delivery record

| Item | Value |
|---|---|
| Survey tool | `scripts/recovery/files_survey.py` |
| sha256 | `956183884c9e19812a250acbd78a6e0229ec74b1efff1129754bb8fd6fe5660e` |
| Pinned link | https://raw.githubusercontent.com/deezr168-blip/Deez-Smart-Home/b1eab5724a469116e6caeab85085c933fb71b60f/scripts/recovery/files_survey.py |
| Tests | `python3 -I scripts/recovery/tests/test_files_survey.py`: 54 passed, 0 failed, 03/11/26 |

**What the tests cover.** They run against a simulated Green:

- a live `/config` missing both folders;
- plain, encrypted and corrupt backups in the Supervisor's layout;
- a fake Supervisor and Core API.

**How they check it.**

- Every run is traced with `strace`. There were no write-class system calls, and the
  simulated Green was unchanged afterwards.
- Canaries were planted in `secrets.yaml`, `.storage/auth`, config-entry titles and
  data, `backup.json`'s Docker credentials, add-on options and the token. None reached
  the output.
- Behaviour checks:
  - an encrypted backup is refused unread;
  - a corrupt one ends `INCOMPLETE` and lists nothing;
  - no backup download is requested through the Supervisor's proxy;
  - a foreign Supervisor URL is refused, and nothing is sent;
  - a proxy in the environment is bypassed.
- Every request was a GET.

**Negative controls.** Three deliberately broken copies each failed the suite:

- one printed the token: the canary check failed;
- one wrote a file: both the `strace` check and the snapshot failed;
- one requested a backup download: the proxy check failed.

The static check is a coarse lint; the `strace` check is the guarantee.

**Not tested:** a real Green, a real Supervisor and Core, a real backup, and
Supervisor API versions other than the two field layouts simulated (`addons` and
`apps`).

## 10. Safeguards review (references/recovery-safeguards.md)

| # | Status |
|---|---|
| R1 plan labelled | met. Header and every write step |
| R2 read-only gates first | met. G1–G5 precede every write, and each says what it reads |
| R3 backup before change, verified | met. Step 1 reads the backup's info back; G4 downloads the source first |
| R4 typed confirmation | met in the plan (`APPLY`, `ROLLBACK`); the tooling is yet to be written (section 5) |
| R5 fingerprint what must not change | met in the plan; tooling yet to be written |
| R6 automatic rollback, defined carefully | **not met yet.** The apply tooling does not exist; when written, "returned" must mean Core's API answering, not a port |
| R7 nothing secret in output | met for the survey (canary tests). No key is asked for anywhere in this version |
| R8 tested, including tests that must fail | met for the survey (section 9). The apply tooling is still to be tested |
| R9 the platform's own tools | met. The Supervisor and Core APIs, and Supervisor's backup layout read as is. No reimplemented decryption; option B would use Core's own library |
| R10 withdraw wrong tooling | met. The decrypted-download mode was removed before it shipped, and the reason is recorded in G2b and S7 |
| R11 checked against standing constraints | met. No restart, restore, reinstall, deletion or integration reload is run; the protected files are not written |
| R12 one change at a time | met. Steps 1–6, each verified |
| R13 inside the protected list | met. Backups, `.storage` and the restart are all owner-approved steps |

The plan is **ready for the read-only gates**. It is **not ready to apply**. R4, R5,
R6 and R8 need the apply tooling, which waits for G3.
