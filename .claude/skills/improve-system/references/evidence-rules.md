# What counts as proof here

Read this before writing any entity ID into a card.

## The export is historical evidence, not live truth

`docs/live/states_export_2026-09-05.txt` lists 970 entities with IDs, friendly
names, areas and availability. `ha_validate.sh` section 3 fails the build on an
ID that is not in it. That makes it feel authoritative. It is not.

**It is a snapshot of an entity *registry*, and a registry keeps rows for
devices that have been renamed.** Both identities appear, both marked `ok`, and
only one of them answers.

This is not hypothetical. The Sensibo air conditioner was renamed to "Parents
Room AC" at some point before the export was taken. The export carries all ten
`*_parents_room_ac_*` entities **and** three `master_bedroom_sensibo_sky_plus*`
rows. The dashboard used the second set. The gate passed them for two weeks.
The wall iPad rendered three orange "Entity not found" cards on Climate and a
fourth on Parents Room, and nobody knew until someone photographed it.

`CLAUDE.md` already warns that "name similarity is not proof" — that is the
same trap from the other direction, where the *dead* ID is the one that looks
authoritative because the export vouches for it.

## The verification ladder

Work down this list and stop at the first rung that answers:

1. **Live Home Assistant MCP** — `GetLiveContext`, filtered by `domain`,
   `area` or `name`. This is the instance answering about itself. Best
   available evidence.
2. **A photograph from the owner.** Direct observation of the rendered page.
   Beats any inference.
3. **The export**, for the exact `entity_id` string — the MCP returns friendly
   names, not IDs, so the two are used together: the MCP says *what exists*,
   the export says *what it is called*.
4. **Another dashboard's usage.** `dashboards/deez_smart_home.yaml` is a
   reference for confirmed-working IDs, since it is the running system.

### What the live MCP cannot tell you

- **Anything not exposed to the assistant.** `GetLiveContext` returns exposed
  entities only. An empty result means "not exposed", *not* "does not exist" —
  do not conclude an entity is dead from its absence alone.
- **Entity IDs.** It returns friendly names. Pair it with the export.
- **Anything about the frontend** — resources, themes, whether a card renders,
  how wide anything is.

## When an entity turns out to be dead

1. Add it to the `STALE` map in `scripts/reconcile_entities.py` with the
   evidence and the replacement. This is what stops it being re-added by
   someone who checks the export and finds it listed as `ok`.
2. Look for the *same* ID elsewhere with grep before fixing only the card you
   were told about. The Sensibo switch had a fourth reference on a page the
   photographs did not cover.
3. Prefer remapping the **section's purpose** over swapping tile for tile. If
   three dead tiles were "the advanced controls for this device", the fix is
   this device's actual advanced controls — not three unrelated entities that
   happen to exist.
4. If nothing unambiguous replaces it, say so on the card or remove it. An
   honest grey "no status entity" is better than a card that looks live.

## Never fake a reading

If no entity exists for something a design asks for, the established
convention is a grey icon and an honest secondary — "no status entity",
"Wi-Fi module not integrated yet", "Needs UPnP". The Network board's "Not
measured yet" group is the model: it keeps its place in the layout, draws an
em dash, and names the integration that would fill it.

This is also why summary sensors are treated with suspicion.
`sensor.open_doors_count` reads `0` while all three contact sensors are
`unavailable` — a sentinel wearing a number's clothes. It is deliberately on
no board. When you need such a figure, compute it from the underlying entities
with an explicit "none of them answered" branch, which is what the chip strips
do.
