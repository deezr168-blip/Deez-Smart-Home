# HACS — installed inventory (owner screenshots)

**What this is.** A source reference for agents planning dashboard upgrades:
what Ray's HACS **Installed** list showed on his iPhone. Transcribed from six
owner-supplied screenshots in `docs/mockups/hacs_installed/`
(`hacs_installed_1of6.png` … `6of6.png`). Added 21/11/26.

**What this is not.**
- **Not an approval to use any of it.** V3-native views are native cards only,
  no `card_mod`, no HACS (`docs/casaray-v3/ARCHITECTURE.md` → Dependencies).
  `validate_dashboard.py` enforces `ALLOWED_CUSTOM = {"custom:webrtc-camera"}`.
  Using anything below in a view needs an owner decision recorded in
  `design/casaray-v3/DECISIONS.md` and a gate change in the same commit.
- **Not proof it works.** "Installed" in HACS means the download is present. It
  does not prove a frontend card is registered as a Lovelace resource, loads on
  the wall iPad, or that an integration is configured and its entities exist.
  Entity IDs still come only from `docs/live/states_export_2026-09-05.txt`
  (never invent one) and must be re-checked live.
- **Not dated.** The screenshots show a clock (9:40–9:42) but no date and no
  HA instance. Treat the list as the owner's report, unverified from this
  environment.

## Conflicts with earlier records (flagged, not resolved)

- `docs/casaray-v3/PREVIEW_DEPLOYMENT.md` records Ray reporting
  `/config/custom_components` (HACS included) and `/config/www/community`
  **missing** on 02/11/26. These screenshots show a working HACS with 40 items
  installed, so either the files were restored since, or the screenshots are
  from a different instance. Re-confirm before relying on either.
- `docs/CASARAY_MAPPING_PACK.md` blocker **B4** says `auto-entities` is not
  installed. The list below shows it installed. B4 is outdated if this list is
  current.

## Installed (green tick) — 40 rows visible

Names truncated by HACS are shown as seen, with `…`. Type is HACS's own label
(truncated in places). Stars/downloads are omitted: they change daily.

**Dashboard cards and card helpers** (HACS "Dashboard")

| Name | Notes |
|---|---|
| Mushroom | V2/legacy dashboards use it; V3 does not |
| Bubble Card | |
| button-card | |
| card-mod | V2 (217 uses) and carried views use it; not V3-native |
| auto-entities | dynamic lists |
| ha-floorplan | |
| Battery State Card / Entity… | |
| Power Flow Card Plus | energy flow |
| Advanced Camera Card | |
| Vertical Stack In Card | |
| Multiple Entity Row | |
| Clock Weather Card | |
| Navbar card | |
| Thermostat Dark Card | |
| Horizon Card | |
| Mushroom Dashboard Str… | name truncated |
| Your HA Digital Twin floor… | name truncated |
| Timer Bar Card | |
| Weather Radar Card | |
| Better Thermostat UI | |
| Platinum Weather Card Pl… | name truncated |
| Weather Station Card | |
| Weather Card (Liquid Glass) | |

**Themes**

| Name |
|---|
| Frosted Glass Theme |
| iOS Themes – Dark Mode a… (name truncated) |

**Integrations**

| Name | Notes |
|---|---|
| HA-MCP — Manage Home … | name truncated; gives an assistant access to HA, so treat as a security-relevant component |
| Local Tuya | |
| Adaptive Lighting | |
| Waste Collection Schedule | candidate source for the Rubbish Collection page (CR-V3-20); **not** verified configured, no entity known |
| Passive BLE monitor integ… | name truncated |
| WebRTC Camera | provides `custom:webrtc-camera`, the one custom card V2 and the carried camera views use |
| Tapo: Cameras Control | |
| Tapo Controller | |
| Alexa Media Player | |
| Powercalc | |
| SmartThinQ LGE Sensors | |
| govee | |
| Smart M-Air (Mitsubishi W…) | name truncated |
| Card Builder | HACS labels it Integration |
| tuya_cloud_ha_bridge | |

## Seen in the "New" section — NOT installed

These have no green tick. Do not assume they are available.

- Smart Heating Control (Integration)
- **Energy Horizon Card** (Dashboard)
- GivEnergy EVC OCPP (Integration)
- Eisenberg (Arlo) (Integration; name partly cut off)

## Gaps in the screenshots

- The list continues past the last row in each screenshot; neighbouring
  screenshots overlap at one row, but **an unseen row may sit between 1of6 and
  2of6 (after "Passive BLE monitor integ…") and between 4of6 and 5of6 (after
  "Your HA Digital Twin floor…")**. Treat the inventory as possibly missing a
  row or two there.
- The "New" section is cut off after Eisenberg (Arlo); more items may follow.
- Repository names and exact `custom:` card type strings are not visible.
  Look each up from the card's own repo before writing YAML; never guess a
  type string.

## Using this for a dashboard upgrade

1. Check the V3 rule above first. For V3-native views the answer is the
   native card unless the owner has approved otherwise.
2. If a card here would genuinely help (Power Flow Card Plus for Energy, Weather
   Station / Radar for Weather, Advanced Camera Card for Cameras), propose it as
   a decision, not a build: name the card, what native card it replaces, and
   what breaks if the resource is not loaded.
3. Before depending on it, get live confirmation that the resource is
   registered and loads on the wall iPad (one view, one card, PASS/FAIL).
4. Entities for any new card come from the states export and a live check.
