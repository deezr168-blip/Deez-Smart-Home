#!/usr/bin/env python3
"""Build a render fixture from the entity export.

WHAT THIS IS FOR, AND THE BUG THAT PROMPTED IT

`render_cards.py` renders every markdown card twice: once "live" and once
"dark". Without a `--states` file the live pass has an EMPTY state map, so
every `states()` call returns `unknown` and the live pass is a second dark
pass wearing a different label. Every width measurement taken that way -- and
CR-311 and CR-312 in the verification queue were taken that way -- described
an instance where nothing was answering, while reporting itself as live.

This builds the missing half: a state map where the entities the export says
were ANSWERING carry a plausible typed value, and the ones it says were dark
carry `unavailable` or `unknown` exactly as recorded.

WHAT IT IS EMPHATICALLY NOT

**These are not real readings.** `docs/live/states_export_2026-09-05.txt`
deliberately carries no values -- that is what keeps addresses, coordinates
and consumption figures out of this repository, and it is not being undone
here. Every value below is invented by the table in `VALUES`, chosen for
shape and length rather than truth: a temperature that is two digits and a
decimal, a power figure that is four digits, a mode string that is as long as
a real one.

So the fixture answers "how does this card BEHAVE and how WIDE does it get
when its inputs are present" and it answers nothing at all about what the
house is doing. Never quote a number that came out of it as a fact about the
instance, and never let one reach a card.

Entity IDs are not invented: every key comes from the export, so the
never-invent rule is satisfied by construction.

USAGE

  scripts/build_render_fixture.py                 # write docs/live/fixture_states.json
  scripts/build_render_fixture.py --check         # fail if the file is stale
"""
import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EXPORT = REPO / "docs" / "live" / "states_export_2026-09-05.txt"
OUT = REPO / "docs" / "live" / "fixture_states.json"

# Matched in order, first hit wins. The key is a regex against the entity id.
# Values are picked for SHAPE: a card that renders `21.4` and a card that
# renders `7` wrap at different widths, and width is most of what this is for.
VALUES = [
    # --- binary sensors: the safe default is the quiet state -------------
    (r"^binary_sensor\..*(motion|occupancy|movement)", "off"),
    (r"^binary_sensor\..*(door|window|contact|opening)", "off"),
    (r"^binary_sensor\..*(problem|fault|tamper|smoke|gas|leak|moisture)", "off"),
    # A "connected"/"status" binary sensor reads `on` when things are WELL, so
    # defaulting it to `off` would have the fixture manufacture a critical
    # alert out of nothing -- which it did, until this line: the alerts chip
    # strip counts `!= 'on'` on eero_wan_status and the two emergency-button
    # cloud links, and reported `Critical 3` on a healthy fixture.
    (r"^binary_sensor\..*(connectivity|connection|online|reachable|running|"
     r"power|status|ok|healthy)", "on"),
    (r"^binary_sensor\.", "off"),

    # --- sensors, by what the name says they measure ---------------------
    (r"^sensor\..*_battery(_level)?$", "84"),
    (r"^sensor\..*(temperature|setpoint)", "21.4"),
    (r"^sensor\..*humidity", "58"),
    (r"^sensor\..*illuminance", "312"),
    (r"^sensor\..*(power|wattage)$", "1240"),
    (r"^sensor\..*(energy|consumption)", "18.62"),
    (r"^sensor\..*voltage", "241.3"),
    (r"^sensor\..*current", "5.2"),
    (r"^sensor\..*(count|_devices|_clients)", "7"),
    (r"^sensor\..*(percent|_level)$", "62"),
    (r"^sensor\..*(rssi|signal)", "-58"),
    (r"^sensor\..*(ssid|bssid)", "Casa-5G"),
    (r"^sensor\..*version", "2026.9.1"),
    (r"^sensor\..*(_at|_time|backup|synchronization)$", "2026-09-19T07:30:00+00:00"),
    (r"^sensor\..*(status|state|mode|type)$", "Normal"),
    (r"^sensor\..*(storage|volume|brightness|output)", "46"),
    (r"^sensor\.", "12.5"),

    # --- everything else, one plausible state per domain -----------------
    (r"^switch\.", "off"),
    (r"^light\.", "off"),
    (r"^fan\.", "off"),
    (r"^siren\.", "off"),
    (r"^automation\.", "on"),
    (r"^input_boolean\.", "off"),
    (r"^cover\.", "closed"),
    (r"^climate\.", "cool"),
    (r"^camera\.", "streaming"),
    (r"^media_player\.", "off"),
    (r"^person\.", "home"),
    (r"^device_tracker\.", "home"),
    (r"^weather\.", "partlycloudy"),
    (r"^sun\.", "above_horizon"),
    (r"^update\.", "off"),
    (r"^number\.|^input_number\.", "22"),
    (r"^select\.|^input_select\.", "Auto"),
    (r"^input_text\.", "Not entered"),
    (r"^input_datetime\.", "2026-09-19 07:30:00"),
    (r"^counter\.", "3"),
    (r"^todo\.", "4"),
    (r"^zone\.", "1"),
    (r"^time\.", "07:30:00"),

    # --- domains whose "state" is a timestamp, or genuinely nothing ------
    # Home Assistant gives scene, script, button and event entities the time
    # they last fired, and `unknown` until they have. The service domains
    # (conversation, tts, stt, notify, ai_task) really do sit at `unknown`
    # forever -- that is the right value, not a gap in this table.
    (r"^scene\.|^button\.|^event\.", "2026-09-19T07:30:00+00:00"),
    (r"^script\.", "off"),
    (r"^calendar\.|^remote\.", "off"),
    (r"^conversation\.|^tts\.|^stt\.|^notify\.|^ai_task\.", "unknown"),
]

META = {
    "_meta": {
        "what": "Synthetic render fixture. NOT real Home Assistant readings.",
        "why": "render_cards.py's live pass is a second dark pass without one.",
        "values": "invented for shape and length; see scripts/build_render_fixture.py",
        "availability": "real -- taken from the export's fourth column",
        "source": "docs/live/states_export_2026-09-05.txt",
    }
}


UNMATCHED: list = []


def value_for(entity_id: str) -> str:
    for pattern, value in VALUES:
        if re.match(pattern, entity_id):
            return value
    # An entity the table does not cover becomes `unknown`, which reads as a
    # dark entity. That is a silent way to shrink the answering set, so it is
    # reported rather than absorbed.
    UNMATCHED.append(entity_id)
    return "unknown"


def build() -> dict:
    if not EXPORT.exists():
        sys.exit(f"export not found: {EXPORT}")
    out = dict(META)
    rows = 0
    for line in EXPORT.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        entity_id, availability = parts[0].strip(), parts[3].strip()
        # Availability is the one thing here that is real, so it is taken
        # verbatim rather than guessed at.
        if availability in ("unavailable", "unknown"):
            out[entity_id] = availability
        else:
            out[entity_id] = value_for(entity_id)
        rows += 1
    out["_meta"]["entities"] = rows
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed fixture is stale")
    args = ap.parse_args()

    built = build()
    text = json.dumps(built, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    if args.check:
        if not OUT.exists():
            print(f"FAIL  {OUT.relative_to(REPO)} does not exist")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"FAIL  {OUT.relative_to(REPO)} is stale — re-run without --check")
            return 1
        print(f"ok    {OUT.relative_to(REPO)} matches the export "
              f"({built['_meta']['entities']} entities)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    answering = sum(1 for k, v in built.items()
                    if not k.startswith("_") and v not in ("unavailable", "unknown"))
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {built['_meta']['entities']} entities, "
          f"{answering} answering, "
          f"{built['_meta']['entities'] - answering} dark")
    if UNMATCHED:
        print(f"  {len(UNMATCHED)} answering entity/entities matched no rule "
              f"and were written as `unknown`:")
        for e in UNMATCHED[:10]:
            print(f"    {e}")
        if len(UNMATCHED) > 10:
            print(f"    ... and {len(UNMATCHED) - 10} more")
        print("  Add a rule to VALUES rather than leaving them dark.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
