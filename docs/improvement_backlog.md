# Improvement Backlog

Work identified from the live system but **not yet implemented**, with the
reason it is still pending. Findings referenced as "H*n*" are sections of
[`docs/health_report.md`](health_report.md).

Nothing in this list has been written into Home Assistant.

## Blocked: entity IDs are unavailable to this repository

Every automation and dashboard item below is blocked on the same thing.

The Home Assistant MCP bridge exposes the **Assist live context**, which reports
friendly names, domains, areas and states — but **not canonical
`domain.object_id` entity IDs**. The bridge's only other resource,
`homeassistant://assist/context-snapshot`, returns the same data. No filesystem
or REST access to the Home Assistant instance is available from this
environment.

`CLAUDE.md` requires that no entity ID is ever invented, so no YAML referencing
entities can be written until real IDs are obtained. Any of the following would
unblock the whole list:

1. A `configuration.yaml` / `automations.yaml` / dashboard YAML export committed
   to `home-assistant/`.
2. A long-lived access token plus base URL, so tooling can read
   `/api/states` directly. **Do not commit the token** — it belongs in the
   environment, and `.gitignore` already excludes `.env`.
3. A paste of Developer Tools → States, or the download from
   **Settings → Devices & Services → Entities** (the export includes entity IDs).

Option 1 is the most useful long-term: it puts the configuration under version
control, which is what this repository is for.

---

## Owner actions (approval-boundary — see health report)

Ordered by priority. None of these can be performed autonomously under
`CLAUDE.md`; they touch live registry data, security hardware, or entity
deletion.

| # | Action | Finding |
| --- | --- | --- |
| 1 | Restore both emergency buttons (test, replace cells, re-pair) | H1 |
| 2 | Confirm whether the `Tapo H200` hub is retired; remove its config entry if so | H2 |
| 3 | Restore the Backyard freezer P110M power monitor | H4 |
| 4 | Charge/replace: Tapo C425 North Wall (24 %), Front Door (24 %), RingRing (28 %) | H8 |
| 5 | Remove the duplicate TP-Link/Tapo config entry and its 26 orphaned entities | H3, H5 |
| 6 | Recover or retire the Presence Multi-Sensor FP300 | H12 |
| 7 | Delete orphaned Hue bulb entities once confirmed in daylight | H7 |
| 8 | Fix `Parents Room Motion Sensor Battery voltage` unit (`V` → `mV`) | H9 |
| 9 | Name or remove the malformed `sensor Cost` entity | H10 |
| 10 | Reassign areas: split TV, cameras out of `Network`, the 72 unassigned entities | H11 |

## Proposed automations

Each is deliberately conservative and unwritten pending entity IDs. Trigger
behaviour, conditions and execution mode are specified so they can be reviewed
before anything is built.

### A. Freezer failure alert

**Why:** Two freezers (Garage, Backyard) hold food with no failure alerting
today, and the Backyard monitor is currently offline entirely (H4).

- **Trigger:** freezer plug power draw stays below a threshold for 2 hours, or
  the plug becomes `unavailable` for 30 minutes.
- **Conditions:** skip if the plug has been unavailable since Home Assistant
  started (avoids a restart-storm notification).
- **Mode:** `single`, with the long `for:` duration providing debounce.
- **Care needed:** a freezer compressor cycles — the Garage unit reads `1.7 W`
  while resting. The threshold must be based on *sustained* low draw, not an
  instantaneous reading, or it will fire every cycle.
- **Action:** notify only. It must never switch the plug.

### B. Low-battery digest

**Why:** three security-relevant devices are already at or below 28 % (H8) and
nothing reports it.

- **Trigger:** daily at a fixed morning time.
- **Condition:** at least one battery entity below 25 %.
- **Mode:** `single`.
- **Action:** one grouped notification listing every low device. A per-entity
  automation would produce repeated alerts for the same device daily; a digest
  will not.

### C. Offline-device watchdog

**Why:** the emergency buttons (H1) and the FP300 (H12) failed silently. Nothing
in the system reports a device going away.

- **Trigger:** a watched critical entity is `unavailable` for 1 hour.
- **Conditions:** must ignore the known-normal overnight solar dropout (H6) and
  must not fire during the first few minutes after a Home Assistant restart,
  when everything is briefly unavailable.
- **Mode:** `single` per device, with a daily re-notify cap.
- **Watch list:** emergency buttons, freezer plugs, contact sensors, cameras.

### D. Front-door battery warning

Front Door is at 24 % with no alert. Folds into automation B rather than being
separate.

## Dashboard work

Also blocked on entity IDs, and additionally on knowing which custom cards are
actually installed — `CLAUDE.md` requires confirming a custom card exists before
depending on it, and HACS inventory is not visible from here.

Groundwork that the inventory already provides:

- **Areas are the natural card grouping**, but they need the H11 cleanup first.
  Six cameras filed under `Network` and 72 unassigned entities mean an
  area-driven dashboard would currently misplace a large fraction of the system.
- **`input_boolean` "Chinese Dashboard"** exists and is `off`. Any dashboard work
  must preserve this English/Chinese switching behaviour.
- **`input_select` "Family Location"** and three `person` entities support a
  presence card.
- **Energy** has healthy Solcast forecast entities and `input_number` "Gas Bill
  Usage MJ" to build against, but the Fronius production side needs H6 resolved
  before an energy dashboard would show real data.

## Verification still outstanding

- **Midday snapshot** to settle H6 (solar) and H7 (Hue). Capture into
  `snapshots/` and rerun `scripts/build_entity_inventory.py`; the two findings
  resolve to either "normal overnight behaviour" or "genuinely broken" with no
  further investigation needed.
