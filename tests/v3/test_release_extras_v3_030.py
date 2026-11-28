"""V3-030: PR #25's extras on PR #24's release preview, pinned.  DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

PR #24 (V3-024) is the release-preview base the owner kept (27/11/26). These
tests pin what was ported onto it from PR #25: PR #21's Home spacing and the
named air-con (HomeV3023, from PR #25's test_topbar_home_v3_023.py), and the
release scope -- Weather, Rubbish collection and the rubbish reminder stay
out, the four locales stay in step, and no camera surface acts (from PR #25's
test_preview_rc_v3_024.py). PR #24's own top-bar tests are
test_topbar_v3_024.py. No network, no Home Assistant.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import ha_layout as L  # noqa: E402
import render_check as R  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
CODES = [x["code"] for x in MAN["locales"]]
AC = "climate.bedroom_parents_room_ac"
DEFERRED = ("weather", "rubbish-collection")
EXPORT = {line.split("|")[0] for line in
          (ROOT / "docs/live/states_export_2026-09-05.txt").read_text(encoding="utf-8").splitlines() if "|" in line}
CAMS = ["camera.front_door_live_view", "camera.tapo_c425_north_wall_hd_stream_direct",
        "camera.tapo_c420_east_wall_hd_stream_direct", "camera.tapo_c420_south_wall_hd_stream_direct",
        "camera.tapo_c200_stockroom_hd_stream_direct", "camera.smart_pet_feeder"]


def dash(code="en"):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return B.load_yaml(ROOT / loc["output"])


def view(d, path):
    return next(v for v in d["views"] if v["path"] == path)


def catalogue(code):
    return B.load_yaml(B.SRC / "i18n" / f"{code}.yaml")


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


class HomeV3023(unittest.TestCase):
    normal, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def ac_cards(self, code="en"):
        return [c for s in view(dash(code), "home")["sections"] for c in s.get("cards", [])
                if c.get("type") == "markdown" and AC in c["content"] and "set s = states" in c["content"]]

    def test_one_tap_air_con_names_its_device_and_says_what_answered(self):
        one_tap = self.ac_cards()[0]
        env = R.env_for(dict(self.normal, **{AC: "cool"}), {AC: {"current_temperature": 23.3}})
        self.assertEqual(env.from_string(one_tap["content"]).render(),
                         "**Parents' air-con**<br>Cool · Room 23.3°")             # positive control
        for st, want in (("unavailable", "Offline · No data"), ("unknown", "State unknown · No data")):
            out = R.env_for(dict(self.normal, **{AC: st}), {AC: {"current_temperature": 23.3}}).from_string(
                one_tap["content"]).render()
            self.assertEqual(out, "**Parents' air-con**<br>" + want, st)       # a dark AC never shows a stale 23.3
        yue = R.env_for(self.dark, {}).from_string(self.ac_cards("yue")[0]["content"]).render()
        self.assertEqual(yue, "**爸媽房冷氣機**<br>離線 · 冇數據")

    def test_other_air_con_cards_are_unchanged(self):
        """Climate and Parents' room ask for neither option: same card as before."""
        for p in ("climate", "parents-room"):
            cards = [c for s in view(dash(), p)["sections"] for c in s.get("cards", [])
                     if c.get("type") == "markdown" and AC in c.get("content", "")
                     and "set s = states" in c["content"]]
            self.assertTrue(cards, p)
            for c in cards:
                self.assertNotIn(catalogue("en")["ac.parents_name"], c["content"], p)

    def test_monitored_footnote_sits_inside_the_card_it_qualifies(self):
        note = catalogue("en")["energy.monitored_note"]
        cards = [c for s in view(dash(), "home")["sections"] for c in s.get("cards", [])
                 if c.get("type") == "markdown" and note in c.get("content", "")]
        self.assertEqual(len(cards), 1)
        self.assertIn("sensor.casa_monitored_power", cards[0]["content"])

    def test_people_at_the_vertical_tile_minimum(self):
        people = [c for s in view(dash(), "home")["sections"] for c in s.get("cards", [])
                  if c.get("entity", "").startswith("person.")]
        self.assertEqual(len(people), 3)
        self.assertEqual({L.effective(c) for c in people}, {(4, 2)})

    def test_more_boards_four_across_on_the_wall_two_on_a_phone(self):
        """V3-024/V3-030: without the deferred Weather and Rubbish collection pages the
        band is eight cards, which fill whole rows at 6 units on both devices."""
        for code in CODES:
            band = view(dash(code), "home")["sections"][-1]
            buttons = [c for c in band["cards"] if c["type"] == "button"]
            self.assertEqual(len(buttons), 8, code)
            self.assertEqual({L.effective(c) for c in buttons}, {(6, 2)}, code)
            self.assertEqual(L.section_holes(band, 24), 0, code)
            self.assertEqual(L.section_holes(band, 12), 0, code)

    def test_new_strings_exist_in_every_catalogue(self):
        for code in CODES:
            for key in ("app.preview_banner", "ac.parents_name"):
                self.assertIn(key, catalogue(code), (code, key))
        self.assertEqual(catalogue("yue")["nav.climate"], "氣候")   # V3-022: was 冷氣同天氣



class DeferredScope(unittest.TestCase):
    def test_weather_and_rubbish_pages_are_not_in_this_release(self):
        self.assertFalse(MAN.get("new_views"), "new_views belongs to PR #21's deferred pages")
        for p in DEFERRED:
            self.assertFalse((B.SRC / "views" / f"{p}.yaml").exists(), p)
        for code in CODES:
            d = dash(code)
            paths = [v["path"] for v in d["views"]]
            for p in DEFERRED:
                self.assertNotIn(p, paths, code)
            links = [n.get("navigation_path", "") for n in walk(d)]
            for p in DEFERRED:
                self.assertFalse([x for x in links if x.rstrip("/").endswith("/" + p)], (code, p))

    def test_rubbish_reminder_automation_is_not_installed(self):
        self.assertFalse((ROOT / "docs/casaray-v3/proposals/rubbish_reminder_automation.yaml").exists())
        for f in (ROOT / "packages").glob("**/*.yaml"):
            self.assertNotRegex(f.read_text(encoding="utf-8").lower(), r"rubbish|bin collection",
                                f"{f.relative_to(ROOT)} must not carry the deferred reminder")


class FourLocales(unittest.TestCase):
    def test_every_locale_has_the_same_views_and_the_same_entities(self):
        pat = re.compile(r"\b[a-z_]+\.[a-z0-9_]+\b")
        ref = dash("en")
        ref_paths = [v["path"] for v in ref["views"]]
        ref_ents = {v["path"]: {m for m in pat.findall(str(v)) if m in EXPORT} for v in ref["views"]}
        for code in CODES:
            d = dash(code)
            self.assertEqual([v["path"] for v in d["views"]], ref_paths, code)
            for v in d["views"]:
                self.assertEqual({m for m in pat.findall(str(v)) if m in EXPORT}, ref_ents[v["path"]],
                                 (code, v["path"]))


class CameraSafety(unittest.TestCase):
    def test_camera_ids_are_the_verified_six(self):
        for code in CODES:
            d = dash(code)
            used = {n["entity"] for n in walk(d) if str(n.get("entity", "")).startswith("camera.")}
            self.assertTrue(used <= EXPORT, (code, sorted(used - EXPORT)))
            pics = [n["entity"] for n in walk(view(d, "cameras")) if n.get("type") == "picture-entity"]
            self.assertEqual(pics, CAMS, code)

    def test_camera_surfaces_change_nothing(self):
        """Cameras and Home's front-door slot: a tap opens the camera's own
        dialog or navigates; nothing performs an action, and every switch on
        Cameras is read-only (its icon does nothing)."""
        for code in CODES:
            d = dash(code)
            cams = view(d, "cameras")
            for n in walk(cams):
                for key in ("tap_action", "hold_action", "double_tap_action", "icon_tap_action"):
                    act = (n.get(key) or {}).get("action")
                    if act == "open-popup":
                        # V3-028's Navbar card "More" route: allowed only as a popup of
                        # plain navigation entries (url, icon, label), nothing that acts
                        self.assertTrue(n.get("popup"), (code, n))
                        for item in n["popup"]:
                            self.assertLessEqual(set(item), {"url", "icon", "label"}, (code, item))
                            self.assertTrue(str(item["url"]).startswith("/"), (code, item))
                        continue
                    self.assertIn(act, (None, "none", "more-info", "navigate"), (code, n.get("entity"), key))
                if str(n.get("entity", "")).startswith("switch."):
                    self.assertEqual((n.get("icon_tap_action") or {}).get("action"), "none", (code, n["entity"]))
            for n in walk(view(d, "home")):
                if n.get("type") == "picture-entity":
                    self.assertEqual(n["tap_action"], {"action": "more-info"}, code)
                    self.assertEqual(n["hold_action"], {"action": "none"}, code)



if __name__ == "__main__":
    unittest.main()
