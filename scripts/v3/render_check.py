"""Offline Jinja render of V3 markdown templates.  DEVELOPMENT ONLY.

A small shim of Home Assistant's template environment (states, state_attr,
is_state, now, is_number, float, round, int, count) good enough to execute
every template V3-native views emit, against two state sets:

  normal  docs/live/fixture_states.json (synthetic, shaped on the 05/09 export)
  dark    every entity 'unavailable'

It proves templates compile and run and what they SAY in the dark case. It
does not prove Home Assistant renders the card — nothing offline can.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import jinja2

ROOT = Path(__file__).resolve().parents[2]
FIXED_NOW = dt.datetime(2026, 11, 1, 20, 30)


def _is_number(v):
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    try:
        float(str(v))
        return str(v).strip().lower() not in ("nan", "inf", "-inf", "")
    except (TypeError, ValueError):
        return False


def _float(v, *default):
    try:
        return float(v)
    except (TypeError, ValueError):
        if default:
            return default[0]
        raise ValueError(f"float filter got {v!r} with no default (HA would error)")


def env_for(states: dict, attrs: dict | None = None):
    attrs = attrs or {}
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, extensions=["jinja2.ext.loopcontrols"])
    env.filters["is_number"] = _is_number
    env.filters["float"] = _float
    env.tests["number"] = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    g = env.globals
    g["states"] = lambda e: states.get(e, "unknown")
    g["is_state"] = lambda e, s: states.get(e, "unknown") == s
    g["state_attr"] = lambda e, a: attrs.get(e, {}).get(a)
    g["now"] = lambda: FIXED_NOW
    return env


def load_fixture():
    d = json.loads((ROOT / "docs/live/fixture_states.json").read_text(encoding="utf-8"))
    return {k: v for k, v in d.items() if k != "_meta"}


def scenarios():
    normal = load_fixture()
    dark = {k: "unavailable" for k in normal}
    attrs = {  # demo attributes for the normal pass only; never read from a device
        "sensor.powerpal_gateway_powerpal_power": {"unit_of_measurement": "W"},
        "sensor.primo_5_0_1_1_ac_power": {"unit_of_measurement": "W"},
        "sensor.living_room_living_hue_hue_sensor_temperature": {"unit_of_measurement": "°C"},
        "sensor.bedroom_motion_sensor_temperature": {"unit_of_measurement": "°C"},
    }
    return {"normal": (normal, attrs), "dark": (dark, {})}


def markdowns(view):
    for s in view.get("sections", []):
        for c in s.get("cards", []):
            if c.get("type") == "markdown":
                yield c["content"]


def render_view(view, states, attrs):
    env = env_for(states, attrs)
    return [env.from_string(m).render() for m in markdowns(view)]
