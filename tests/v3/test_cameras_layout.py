"""V3-014: camera slots and bands that pack with visibility applied; the top
bar on the band-grid views.  DEVELOPMENT ONLY.

V3-024 (preview release candidate): V3-014's compact, icon-only top bar is
superseded by V3-023's named bar on every view, so CompactTopBar became
SharedTopBar; and the Offline card also covers `unknown`, where it says
"State unknown" instead.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant: these check the generated YAML and what its
templates say, not whether a stream plays.
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
CAMS = ["camera.front_door_live_view", "camera.tapo_c425_north_wall_hd_stream_direct",
        "camera.tapo_c420_east_wall_hd_stream_direct", "camera.tapo_c420_south_wall_hd_stream_direct",
        "camera.tapo_c200_stockroom_hd_stream_direct", "camera.smart_pet_feeder"]


def view(path, code="en"):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return next(v for v in B.load_yaml(ROOT / loc["output"])["views"] if v["path"] == path)


def cards(v, kind=None):
    return [c for s in v["sections"] for c in s.get("cards", []) if kind is None or c.get("type") == kind]


def grid_section(v):
    return next(s for s in v["sections"] if any(c.get("type") == "picture-entity" for c in s["cards"]))


class CameraSlots(unittest.TestCase):
    states = R.scenarios()["normal"][0]

    def test_front_door_first_and_no_camera_remapped(self):
        pics = [c["entity"] for c in cards(view("cameras"), "picture-entity")]
        self.assertEqual(pics, CAMS)

    def test_every_slot_is_a_picture_and_an_offline_card_of_one_size(self):
        for path in ("cameras", "home"):
            sec = grid_section(view(path))
            pics = [c for c in sec["cards"] if c["type"] == "picture-entity"]
            for pic in pics:
                e = pic["entity"]
                i = sec["cards"].index(pic)
                twin = sec["cards"][i + 1]
                self.assertEqual(twin["type"], "markdown", e)
                self.assertEqual(pic["visibility"], [{"condition": "state", "entity": e,
                                                      "state_not": ["unavailable", "unknown"]}])
                self.assertEqual(twin["visibility"], [{"condition": "state", "entity": e,
                                                       "state": ["unavailable", "unknown"]}])
                self.assertEqual(L.effective(pic), L.effective(twin), e)

    def test_exactly_one_of_each_pair_shows(self):
        sec = grid_section(view("cameras"))
        for st in ("idle", "streaming", "unknown", "unavailable"):
            shown = [c for c in sec["cards"] if c["type"] in ("picture-entity", "markdown")
                     and c.get("visibility") and L.visible(c, {e: st for e in CAMS})]
            self.assertEqual(len(shown), 6, st)
        idle = {e: "idle" for e in CAMS}
        self.assertTrue(all(c["type"] == "picture-entity" for c in sec["cards"]
                            if c.get("visibility") and L.visible(c, idle)), "an idle camera is available")
        for st in ("unavailable", "unknown"):
            dark = {e: st for e in CAMS}
            self.assertTrue(all(c["type"] == "markdown" for c in sec["cards"]
                                if c.get("visibility") and L.visible(c, dark)), f"a {st} camera shows words")
        # a camera entity that does not exist reads `unknown` in the frontend
        # (validate-condition.ts): its slot shows words, not an empty frame
        shown = [c for c in sec["cards"] if c.get("visibility") and L.visible(c, {})]
        self.assertEqual(len(shown), 6)
        self.assertTrue(all(c["type"] == "markdown" for c in shown))

    def test_unknown_camera_says_state_unknown_not_offline(self):
        """V3-024: offline and unknown are different states with different
        words (V3 rule: four camera states, never colour alone)."""
        E = "camera.tapo_c200_stockroom_hd_stream_direct"
        for code, word, wrong in (("en", "State unknown", "Offline"), ("yue", "狀態未知", "離線"),
                                  ("zh-Hans", "状态未知", "离线"), ("km", "មិនដឹងស្ថានភាព", "ដាច់បណ្ដាញ")):
            twin = next(c for c in grid_section(view("cameras", code))["cards"]
                        if c["type"] == "markdown" and c.get("visibility") and E in str(c["visibility"]))
            out = R.env_for(dict(self.states, **{E: "unknown"}), {}).from_string(twin["content"]).render()
            self.assertIn("· **" + word + "**", out, code)
            self.assertNotIn(wrong, out, code)
            out = R.env_for(dict(self.states, **{E: "unavailable"}), {}).from_string(twin["content"]).render()
            self.assertIn("· **" + wrong + "**", out, code)

    def test_a_tap_opens_the_native_live_view(self):
        for path in ("cameras", "home"):
            for pic in cards(view(path), "picture-entity"):
                self.assertEqual(pic["tap_action"], {"action": "more-info"}, pic["entity"])
                self.assertEqual(pic["hold_action"], {"action": "none"})

    def test_the_v2_camera_pages_stay_one_tap_away(self):
        targets = {n.split("/")[2] for n in V.nav_paths(view("cameras"))}
        for p in ("camera-front-door", "camera-north-wall", "camera-east-wall", "camera-south-wall",
                  "camera-stockroom", "camera-pet-feeder"):
            self.assertIn(p, targets)

    def test_offline_card_says_offline_and_what_the_battery_says(self):
        s = dict(self.states, **{"camera.tapo_c420_east_wall_hd_stream_direct": "unavailable",
                                 "sensor.tapo_camera_bcca_battery": "100"})
        out = "\n".join(R.render_view(view("cameras"), s, {}))
        self.assertIn("**East wall** · **Offline**\nNo stream from Home Assistant · Battery 100%", out)
        out = "\n".join(R.render_view(view("cameras"), R.scenarios()["dark"][0], {}))
        self.assertIn("**East wall** · **Offline**\nNo stream from Home Assistant · No battery reading", out)
        self.assertIn("**Stockroom** · **Offline**\nNo stream from Home Assistant", out)
        self.assertNotIn("Battery 0%", out)

    def test_privacy_tiles_are_named_and_read_only(self):
        tiles = [c for c in cards(view("cameras"), "tile") if c["entity"].startswith("switch.")]
        self.assertEqual(len(tiles), 6)
        for t in tiles:
            self.assertTrue(t.get("name"), t["entity"])
            self.assertLess(len(t["name"]), 30, t["name"])
            self.assertEqual(V.C.effective_tile_actions(t)[1], "none", t["entity"])


class SharedTopBar(unittest.TestCase):
    """V3-024: the band-grid views (Home, Cameras) carry the same named top bar
    as every other view: one row on the wall iPad, two on a phone, every cell
    one height, the current page inert and tinted."""

    def test_band_views_get_the_named_one_height_top_bar(self):
        for path in ("home", "cameras"):
            top = view(path)["sections"][0]
            btn = [c for c in top["cards"] if c["type"] == "button"]
            self.assertEqual(len(btn), 6)
            self.assertTrue(all(c.get("show_name", True) for c in btn), path)
            self.assertEqual({L.effective(c)[1] for c in top["cards"]}, {2}, path)
            current = [c for c in btn if c["tap_action"] == {"action": "none"}]
            self.assertEqual(len(current), 1, "the current page is inert")
            self.assertEqual(current[0].get("color"), "accent", "and marked")
            for units in (24, 12):
                self.assertEqual(L.place([L.effective(c) for c in top["cards"]], units)[2], 0, (path, units))

    def test_every_view_has_the_same_bar_shape(self):
        shape = lambda p: [(c["type"], L.effective(c)) for c in view(p)["sections"][0]["cards"]]
        for p in MAN["native"]:
            self.assertEqual(shape(p), shape("home"), p)
        self.assertFalse(any(c.get("text_only") for p in MAN["native"] for c in view(p)["sections"][0]["cards"]))

    def test_clock_keeps_dd_mm_yy_under_the_time(self):
        head = view("home")["sections"][0]["cards"][0]["content"]
        self.assertIn("%H:%M') }}**<br>", head)
        self.assertIn("%d/%m/%y", head)
        self.assertNotIn("%Y", head)


class BandsWithVisibility(unittest.TestCase):
    def test_cameras_passes_every_band_rule(self):
        spec = B.load_yaml(B.SRC / "views" / "cameras.yaml")
        self.assertEqual(spec.get("band_grid"), 24)
        self.assertEqual(V.band_problems(view("cameras"), spec), ([], [], []))

    def test_a_twin_of_another_size_is_caught(self):
        spec = B.load_yaml(B.SRC / "views" / "cameras.yaml")
        v = copy.deepcopy(view("cameras"))
        twin = next(c for c in grid_section(v)["cards"] if c["type"] == "markdown" and c.get("visibility"))
        twin["grid_options"]["columns"] = 6
        self.assertTrue(V.band_problems(v, spec)[1], "a half-size Offline card went unseen")


if __name__ == "__main__":
    unittest.main()
