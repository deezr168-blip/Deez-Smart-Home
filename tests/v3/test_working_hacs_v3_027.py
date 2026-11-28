"""V3-027: four of the V3-026 custom cards on the working dashboards.  DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

Owner decision 20/11/26 (V3-026): "Adopt cards in V3". The working dashboards
take four of the seven: WallPanel (dashboard level), Power Flow Card Plus and
ApexCharts on Energy, auto-entities on House health. Each sits in its own band
after the page's native readings with a note naming what it needs, so a card
that is not installed shows Home Assistant's error in that band only. Kiosk
Mode, Bubble Card and Advanced Camera Card stay off (V3-027 says why).

Offline: nothing here proves a card renders on a device or installs one.
"""
import copy
import sys
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
EXPORT = B.load_export(ROOT / MAN["entity_authority"])
LOCS = {l["code"]: l for l in MAN["locales"]}
SOLAR, GRID = "sensor.primo_5_0_1_1_ac_power", "sensor.powerpal_gateway_powerpal_power"
TEMP, DOOR = "sensor.bedroom_motion_sensor_temperature", "binary_sensor.f_contact_sensor_door"
BANDS = {"energy": "h.power_flow", "house-health": "h.not_answering"}   # the V3-027 band's heading key
PRODUCTS = {"energy": ["Power Flow Card Plus", "ApexCharts"], "house-health": ["auto-entities"]}
BLOCKED = {"custom:bubble-card", "custom:advanced-camera-card"}


def dash(code="en"):
    return B.load_yaml(ROOT / LOCS[code]["output"])


def view(path, code="en"):
    return next(v for v in dash(code)["views"] if v["path"] == path)


def band(path, code="en"):
    v = view(path, code)
    head = V.loc_t(LOCS[code], BANDS[path])
    return next(s for s in v["sections"] if s["cards"] and s["cards"][0].get("heading") == head)


def customs(node):
    return {c["type"] for c in V.walk_cards(node) if str(c.get("type", "")).startswith("custom:")}


_real_load = B.load_yaml


def _without_v3_027(path):
    """The same sources with the V3-027 additions taken out again."""
    data = _real_load(path)
    p = Path(path)
    if p.name == "manifest.yaml" and p.parent == B.SRC:
        data = copy.deepcopy(data)
        data.pop("working_root", None)
    elif p.parent.name == "views" and isinstance(data, dict) and data.get("path") in BANDS:
        data = copy.deepcopy(data)
        data["sections"] = [s for s in data["sections"] if s.get("heading") != BANDS[data["path"]]]
    return data


class Additive(unittest.TestCase):
    """Existing controls, readings and navigation are untouched."""

    @classmethod
    def setUpClass(cls):
        cls.with_, _, _ = B.build(write=False)
        with mock.patch.object(B, "load_yaml", side_effect=_without_v3_027):
            cls.without, _, _ = B.build(write=False)

    def test_other_views_identical_and_the_two_only_gain_one_band(self):
        for code, loc in LOCS.items():
            a, b = yaml.safe_load(self.with_[loc["output"]]), yaml.safe_load(self.without[loc["output"]])
            self.assertEqual(set(a) - set(b), {"wallpanel"}, code)
            self.assertEqual([v["path"] for v in a["views"]], [v["path"] for v in b["views"]], code)
            old = {v["path"]: v for v in b["views"]}
            for v in a["views"]:
                if v["path"] in BANDS:
                    extra = [s for s in v["sections"] if s not in old[v["path"]]["sections"]]
                    self.assertEqual(len(extra), 1, (code, v["path"]))
                    self.assertEqual([s for s in v["sections"] if s not in extra], old[v["path"]]["sections"],
                                     (code, v["path"], "the existing sections, in their order"))
                else:
                    self.assertEqual(v, old[v["path"]], (code, v["path"]))

    def test_the_preview_is_unchanged(self):
        out = MAN["preview"]["output"]
        self.assertEqual(self.with_[out], self.without[out])


class Cards(unittest.TestCase):
    def test_energy_band_is_power_flow_and_apexcharts_on_two_verified_sensors(self):
        for code in LOCS:
            b = band("energy", code)
            types = [c["type"] for c in b["cards"]]
            self.assertEqual(types, ["heading", "custom:power-flow-card-plus", "custom:apexcharts-card",
                                     "markdown", "markdown"], code)
            flow, apex = b["cards"][1], b["cards"][2]
            self.assertEqual(flow["entities"]["solar"]["entity"], SOLAR)
            self.assertEqual(flow["entities"]["grid"]["entity"], GRID)
            self.assertNotIn("entity", flow["entities"]["home"], "Home is the card's sum; no consumption sensor exists")
            self.assertEqual([s["entity"] for s in apex["series"]], [SOLAR, GRID])
            for e in (SOLAR, GRID):
                self.assertIn(e, EXPORT)
            notes = " ".join(c["content"] for c in b["cards"] if c["type"] == "markdown")
            self.assertIn(V.loc_t(LOCS[code], "energy.flow_caveat"), notes)

    def test_house_health_band_is_four_auto_entities_lists(self):
        for code in LOCS:
            b = band("house-health", code)
            lists = [c for c in b["cards"] if c["type"] == "custom:auto-entities"]
            self.assertEqual([[r["domain"] for r in c["filter"]["include"]] for c in lists],
                             [["light"], ["camera"], ["switch"], ["sensor", "binary_sensor"]], code)
            for c in lists:
                self.assertTrue(all(set(r) == {"domain", "state"} and r["state"] == "unavailable"
                                    for r in c["filter"]["include"]))
                self.assertEqual(c["card"]["type"], "entities")
                self.assertIn(V.loc_t(LOCS[code], "hh.list_none"), c["else"]["content"])

    def test_each_band_names_what_it_needs_in_every_locale(self):
        for code in LOCS:
            for path, products in PRODUCTS.items():
                notes = " ".join(c["content"] for c in band(path, code)["cards"] if c["type"] == "markdown")
                for p in products:
                    self.assertIn(p, notes, (code, path))

    def test_bands_come_after_every_native_reading_and_pass_the_reviewed_checks(self):
        for code in LOCS:
            for path in BANDS:
                self.assertEqual(V.working_custom_problems(view(path, code)), [], (code, path))

    def test_custom_cards_only_where_reviewed(self):
        for code in LOCS:
            d = dash(code)
            self.assertNotIn("kiosk_mode", d)
            self.assertFalse(customs(d) & BLOCKED, code)
            for v in d["views"]:
                found = customs(v) - {V.NAVBAR}   # V3-028's navbar is on every native page
                if v["path"] in BANDS:
                    self.assertEqual(found, V.WORKING_CUSTOM[v["path"]], (code, v["path"]))
                elif v["path"] in MAN["native"]:   # V3-029: Clock Weather Card on Home
                    self.assertEqual(found, V.WORKING_CUSTOM.get(v["path"], set()), (code, v["path"]))
                else:   # carried and classic V2 views keep V2's one custom card
                    self.assertLessEqual(found, V.ALLOWED_CUSTOM, (code, v["path"]))


class WallPanel(unittest.TestCase):
    def test_reviewed_options_and_no_chrome_hiding(self):
        for code in LOCS:
            wp = dash(code)["wallpanel"]
            self.assertEqual({k: v for k, v in wp.items() if k != "cards"},
                             {"enabled": True, "hide_toolbar": False, "hide_sidebar": False, "fullscreen": False,
                              "idle_time": 120, "image_url": "media-source://media_source/"}, code)
            self.assertEqual([c["type"] for c in wp["cards"]], ["markdown"] * 3)
            self.assertEqual(V.root_problems(dash(code), EXPORT, label_ok=V.nonempty,
                                             forbidden=[V.loc_t(LOCS[code], "s.open"), V.loc_t(LOCS[code], "s.closed")],
                                             reviewed={"wallpanel": V.PREVIEW_ROOT["wallpanel"]}), [], code)

    def render(self, code, states):
        env = R.env_for(states, {})
        return [env.from_string(c["content"]).render() for c in dash(code)["wallpanel"]["cards"]]

    def test_info_box_says_what_answered(self):
        for code in ("en", "yue"):
            t = lambda k: V.loc_t(LOCS[code], k)  # noqa: E731
            clock, temp, door = self.render(code, {TEMP: "21.4", DOOR: "on"})
            face = dash(code)["wallpanel"]["cards"][0]["content"]
            self.assertLess(face.index("%H:%M"), face.index("%d/%m/%y"), "the time sits above the date")
            self.assertNotIn("%Y", face)
            self.assertIn("21.4°", temp)
            self.assertIn(t("s.open"), door)
            self.assertIn(t("s.closed"), self.render(code, {TEMP: "21.4", DOOR: "off"})[2])
            _, temp, door = self.render(code, {TEMP: "unavailable", DOOR: "unavailable"})
            self.assertIn(t("s.no_data"), temp)
            self.assertIn(t("s.offline"), door)
            self.assertNotIn(t("s.closed"), door)


class GateBites(unittest.TestCase):
    """Each rule fails on the shape it exists to stop."""

    def test_a_card_that_is_not_reviewed_for_the_page_is_caught(self):
        v = copy.deepcopy(view("energy"))
        band_i = next(i for i, s in enumerate(v["sections"]) if customs(s))
        v["sections"][band_i]["cards"].append({"type": "custom:bubble-card", "card_type": "button",
                                               "button_type": "state", "entity": SOLAR, "name": "x"})
        self.assertTrue(any("not allowed" in p for p in V.working_custom_problems(v)))
        h = copy.deepcopy(view("home"))
        h["sections"][1]["cards"].append(copy.deepcopy(band("energy")["cards"][1]))
        self.assertTrue(V.working_custom_problems(h))

    def test_a_band_above_native_readings_is_caught(self):
        v = copy.deepcopy(view("house-health"))
        band_i = next(i for i, s in enumerate(v["sections"]) if customs(s))
        sec = v["sections"].pop(band_i)
        v["sections"].insert(2, sec)
        self.assertTrue(any("come after" in p for p in V.working_custom_problems(v)))

    def test_a_band_without_its_note_is_caught(self):
        v = copy.deepcopy(view("energy"))
        band_i = next(i for i, s in enumerate(v["sections"]) if customs(s))
        v["sections"][band_i]["cards"] = [c for c in v["sections"][band_i]["cards"]
                                          if "ApexCharts" not in c.get("content", "")]
        self.assertTrue(any("no note naming" in p for p in V.working_custom_problems(v)))

    def test_an_unreviewed_filter_is_caught(self):
        v = copy.deepcopy(view("house-health"))
        lst = next(c for c in V.walk_cards(v) if c.get("type") == "custom:auto-entities")
        lst["filter"]["include"][0]["name"] = "*door*"
        self.assertTrue(V.working_custom_problems(v))

    def test_kiosk_mode_is_refused_on_the_working_dashboards(self):
        def with_kiosk(path):
            data = _real_load(path)
            if Path(path).name == "manifest.yaml" and Path(path).parent == B.SRC:
                data = copy.deepcopy(data)
                data["working_root"] = dict(data["working_root"], kiosk_mode={"hide_header": True, "hide_sidebar": True})
            return data
        with mock.patch.object(B, "load_yaml", side_effect=with_kiosk):
            with self.assertRaises(SystemExit) as cm:
                B.build(write=False)
        self.assertIn("kiosk_mode", str(cm.exception))

    def test_a_reassuring_door_word_when_dark_is_caught(self):
        d = copy.deepcopy(dash())
        d["wallpanel"]["cards"][2]["content"] = "**Front door**\n## Closed"
        self.assertTrue(V.root_problems(d, EXPORT, label_ok=V.nonempty, forbidden=["Open", "Closed"],
                                        reviewed={"wallpanel": V.PREVIEW_ROOT["wallpanel"]}))


if __name__ == "__main__":
    unittest.main()
