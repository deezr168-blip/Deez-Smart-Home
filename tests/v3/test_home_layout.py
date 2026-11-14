"""V3-013: Home against the 14/09 wall render, and the layout rules behind it.
DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant. The layout tests check the arithmetic in
scripts/v3/ha_layout.py (read from frontend 20260826.7), not a device.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import ha_layout as L  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
SPEC = B.load_yaml(B.SRC / "views" / "home.yaml")
PLUGS = ["sensor.g_monitor_freezer_p110m_current_consumption", "sensor.r_energy_monitor_p110m_current_consumption"]
ATTRS = {"weather.forecast_home": {"temperature": 10.4},
         "sensor.casa_monitored_power": {"unit_of_measurement": "W"}}


def dash(code="en"):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return B.load_yaml(ROOT / loc["output"])


def home(code="en"):
    return next(v for v in dash(code)["views"] if v["path"] == "home")


def render(states, attrs=None, code="en"):
    return "\n".join(R.render_view(home(code), states, attrs or {}))


class FrontendRules(unittest.TestCase):
    """What the installed frontend does with a card's size (ha_layout.py)."""

    def test_columns_resolved_on_the_wall_ipad_and_a_phone(self):
        self.assertEqual(L.resolved_columns(1180, 2, [2, 1, 1]), 2)
        self.assertEqual(L.resolved_columns(390, 2, [2, 1, 1]), 1)

    def test_a_two_column_band_has_24_units(self):
        self.assertEqual(L.units(2, 2), 24)
        self.assertEqual(L.units(2, 1), 12)   # a phone clamps the span

    def test_card_minimums_override_the_yaml(self):
        tile = {"type": "tile", "entity": "sensor.x", "grid_options": {"columns": 3, "rows": "auto"}}
        self.assertEqual(L.effective(tile), (6, "auto"))
        named = {"type": "button", "name": "Bills", "icon": "mdi:x", "show_name": True,
                 "grid_options": {"columns": 3, "rows": 1}}
        self.assertEqual(L.effective(named), (3, 2))
        icon_only = dict(named, show_name=False)
        self.assertEqual(L.effective(icon_only), (3, 1))

    def test_a_twelve_column_heading_sits_beside_its_card_in_a_band(self):
        # the defect V3-013 fixes: 12 of 24 leaves room for the next card
        rows = L.place([(12, "auto"), (12, "auto")], 24)[0]
        self.assertEqual(rows[0][0], rows[1][0], "heading and card on the same row")
        rows = L.place([("full", "auto"), (12, "auto")], 24)[0]
        self.assertNotEqual(rows[0][0], rows[1][0])


class HomeBands(unittest.TestCase):
    def test_home_opts_in_and_passes_every_band_rule(self):
        self.assertEqual(SPEC.get("band_grid"), 24)
        heads, holes, clamps = V.band_problems(home(), SPEC)
        self.assertEqual((heads, holes, clamps), ([], [], []))

    def test_band_rules_bite(self):
        v = copy.deepcopy(home())
        sec = next(s for s in v["sections"] if s.get("column_span") == 2
                   and s["cards"][0].get("type") == "heading")
        sec["cards"][0]["grid_options"]["columns"] = 12
        self.assertTrue(V.band_problems(v, SPEC)[0], "a half-width band heading went unseen")
        v = copy.deepcopy(home())
        summary = next(c for s in v["sections"] for c in s["cards"]
                       if c.get("type") == "markdown" and "online" in c["content"] and "offline" in c["content"])
        summary["grid_options"]["rows"] = "auto"
        self.assertTrue(V.band_problems(v, SPEC)[1], "a hole beside the camera picture went unseen")
        v = copy.deepcopy(home())
        btn = next(c for s in v["sections"][1:] for c in s["cards"]   # [0] is the shared top bar
                   if c.get("type") == "button" and c.get("show_name"))
        btn["grid_options"]["rows"] = 1
        self.assertTrue(V.band_problems(v, SPEC)[2], "a silently clamped button went unseen")

    def test_other_views_are_untouched_by_the_option(self):
        for p in MAN["native"]:
            if p == "home":
                continue
            spec = B.load_yaml(B.SRC / "views" / f"{p}.yaml")
            self.assertNotIn("band_grid", spec, f"{p} opted in without a review of its own")


class HomeSaysWhatAnswered(unittest.TestCase):
    states, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def test_two_plug_total_is_labelled_and_only_shown_while_both_plugs_answer(self):
        s = dict(self.states, **{"sensor.casa_monitored_power": "147.9", PLUGS[0]: "113.8", PLUGS[1]: "34.1"})
        out = render(s, ATTRS)
        self.assertIn("Two monitored plugs **147.9 W**", out)              # positive control
        self.assertIn("147.9 W · garage freezer and Ray's desk", out)
        out = render(dict(s, **{PLUGS[1]: "unavailable"}), ATTRS)
        self.assertIn("Two monitored plugs **No data** <small>1 of 2 reporting</small>", out)
        self.assertNotIn("147.9", out)
        strip = next(o for o in R.render_view(home(), self.dark, {}) if o.startswith("Outside"))
        self.assertTrue(strip.endswith("Two monitored plugs **No data**"), strip)   # nothing answered: no count

    def test_outside_reads_the_weather_entity_and_says_no_data_when_dark(self):
        self.assertIn("Outside **10°**", render(self.states, ATTRS))
        self.assertIn("Outside **No data**", render(self.dark))

    def test_room_lines_count_what_did_not_answer(self):
        s = dict(self.states, **{"light.living_room": "on",
                                 "sensor.living_room_living_hue_hue_sensor_temperature": "19.7",
                                 "binary_sensor.living_room_living_hue_hue_sensor_motion": "off"})
        self.assertIn("**Living room**\nLights on · 19.7° · Quiet", render(s))   # positive control
        out = render(dict(s, **{"binary_sensor.living_room_living_hue_hue_sensor_motion": "unavailable"}))
        self.assertIn("**Living room**\nLights on · 19.7° · 1 not reporting", out)
        self.assertNotIn("19.7° · Quiet", out)

    def test_dark_rooms_claim_nothing(self):
        out = render(self.dark)
        for room in ("Living room", "Dining", "Kitchen", "Parents' room", "Ray's room", "Garage", "Guest room"):
            self.assertIn(f"**{room}**\nNo data", out, room)
        for word in ("Quiet", "Lights off", "Fridge closed", "Normal", "Not occupied", "Blind closed"):
            self.assertNotIn(word, out, word)

    def test_an_idle_camera_counts_as_online(self):
        s = dict(self.states, **{"camera.tapo_c425_north_wall_hd_stream_direct": "idle",
                                 "camera.front_door_live_view": "idle"})
        out = render(s)
        self.assertIn("North wall — **Online**", out)
        self.assertIn("Front door — **Online**", out)
        self.assertNotIn("North wall camera offline", out)

    def test_chinese_room_line_uses_v2_vocabulary(self):
        s = dict(self.states, **{"light.dining": "off", "binary_sensor.sensor_group_motion": "off"})
        out = render(s, code="zh-Hans")
        self.assertIn("**餐厅**\n灯光已关 · ", out)
        self.assertIn("安静", out)


class HomeBehaviourKept(unittest.TestCase):
    def actions(self):
        return sorted((a["perform_action"], str(a.get("target")), str(a.get("data")))
                      for a in V.actions(home()))

    def test_only_the_three_lighting_actions_act(self):
        self.assertEqual(self.actions(), sorted([
            ("light.turn_on", "{'entity_id': 'light.living_room'}", "{'brightness_pct': 55}"),
            ("light.turn_on", "{'entity_id': ['light.living_room', 'light.bedroom_bedroom', 'light.dining']}",
             "{'brightness_pct': 10}"),
            ("light.turn_off", "{'entity_id': ['light.living_room', 'light.dining', 'light.bedroom_bedroom']}", "None"),
        ]))

    def test_every_room_tile_opens_its_room(self):
        want = {"living-room", "dining", "kitchen", "parents-room", "ray-bedroom", "garage", "guest-room", "rooms"}
        got = {c["tap_action"]["navigation_path"].split("/")[2] for s in home()["sections"] for c in s["cards"]
               if c.get("type") == "markdown" and (c.get("tap_action") or {}).get("action") == "navigate"}
        self.assertTrue(want <= got, want - got)

    def test_no_tile_on_home_can_toggle(self):
        for s in home()["sections"]:
            for c in s["cards"]:
                if c.get("type") == "tile":
                    tap, icon = V.C.effective_tile_actions(c)
                    self.assertIn(tap, ("navigate", "more-info", "none"), c["entity"])
                    self.assertEqual(icon, "none", c["entity"])


class ReassuranceCheck(unittest.TestCase):
    def test_stem_is_the_distinctive_part(self):
        en = B.load_yaml(B.SRC / "i18n" / "en.yaml")
        stem = V.reassurance_stem(en["att.all_clear"])
        self.assertNotEqual(stem, "All")
        self.assertNotIn(stem, "**All rooms**")
        rendered = en["att.all_clear"].replace("{n}", "17")
        self.assertIn(stem, rendered, "the check no longer sees the sentence it guards")


if __name__ == "__main__":
    unittest.main()
