# Live observations, 2026-10-05

What the Home Assistant MCP connector reported on 2026-10-05, read-only, from
an autonomous session. **Read this with three limits in mind:**

1. The connector exposes only the entities Assist is allowed to see. It does
   **not** expose helpers (`input_*`), scripts, automations or template
   sensors by default, so *absence from this list says nothing about them*.
2. It returns friendly names and states, **not entity IDs**, and the registry
   carries stale twins with identical names. Nothing here is matched to an ID
   automatically, which is why `scripts/audit_casaray.py` does not use it
   (DECISION_LOG D-003).
3. It is one moment. The owner's later statements supersede it: login works,
   CasaRay renders and navigates, some entities/helpers still read
   unavailable.

## The finding that matters

| Entity (by name) | State |
|---|---|
| Chinese Dashboard (`input_boolean`) | **unavailable** |
| Raymond Du., Vinh Du, Ai Q Huang (`person`) | **unavailable** (all three) |

Read twice, minutes apart, same result. A `person` with no tracker reads
`unknown`; `unavailable` means Home Assistant has the registry entry but
nothing providing it — consistent with the YAML that defined them being gone.
The new **House health → Setup status** card reports this on the dashboard.

## Not answering (unavailable), by name

- **Cameras (streams):** Tapo C420 East Wall HD Stream (Direct), Tapo C420 –
  South Wall HD Stream (Direct), Tapo C425 – North Wall HD Stream (Direct),
  Tapo C200 – Stockroom HD Stream (Direct)
- **Camera controls:** privacy switches and floodlights for the same four
  cameras; Stockroom auto-track and preset patrol
- **Lights:** Hue ambiance spots 1, 3, 4 (and a second "spot 1"), Living Room
  Inner/Outer Left/Right, Corridor 1 and 2, Dining Light Left/Right, Kogan Tv
- **Media:** Pogo; one Samsung Q9 speaker endpoint, one 55" QLED speaker
  endpoint (twins of working TV entries)
- **Sensors:** Presence Multi-Sensor FP300 occupancy; Tapo_C200_5C35 and
  Tapo_Camera motion; G/Monitor Freezer P110M Overheated; LPH-SE DCD9 (power,
  pump, pump cycling)
- **Plugs:** several P100/P110M entries — each has a working twin with the
  same name, i.e. the stale-registry pattern in `audit_duplicate_entities.py`

## Answering

Contact sensors (door entries reporting `off` alongside dead twins), Hue
motion sensors, eero WAN status, Front Door camera, Smart Pet Feeder camera,
Parents Room AC (off, 20.1 °C), living-room and bedroom scenes, Shopping list,
weather, the Genio and master-bedroom power points, TV media players.

## What changed in the repository because of this

- Setup status card (House health) — names the cause for the first table.
- OWNER_ACTION_QUEUE A1 — look at Settings → Helpers first.
- The four Tapo streams being down *now* contradicts CLAUDE.md's 19/09 note
  that the two C420 streams "had come back": treat camera availability as
  unknown and check the Cameras board after sync.
