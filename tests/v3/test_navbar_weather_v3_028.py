"""V3-028: a Navbar card on every native page, and weather with forecasts on Home.
DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

Owner, 21/11/26: "Add in navbar for navigation, i want weather card and forecast
cards in home page". Navbar Card is installed on the instance (the owner's card
picker lists it); its options are from its own docs. The forecasts were native
weather-forecast cards on the entity Home already reads; V3-029 (owner, 21/11/26)
replaced them with Clock Weather Card, tested in test_clock_weather_v3_029.py.
Offline: nothing here proves either renders on a device.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import components as C  # noqa: E402
import ha_layout as L  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
LOCS = {l["code"]: l for l in MAN["locales"]}
W = "weather.forecast_home"


def dash(code="en"):
    return B.load_yaml(ROOT / LOCS[code]["output"])


def view(path, code="en"):
    return next(v for v in dash(code)["views"] if v["path"] == path)


def navbars(node):
    return [c for c in V.walk_cards(node) if c.get("type") == C.NAVBAR]


class Navbar(unittest.TestCase):
    def test_one_navbar_last_on_every_native_page_and_nowhere_else(self):
        for code, loc in LOCS.items():
            d = dash(code)
            paths = [v["path"] for v in d["views"]]
            for v in d["views"]:
                if v["path"] in MAN["native"]:
                    self.assertEqual(V.navbar_problems(v, loc["url_base"], paths), [], (code, v["path"]))
                else:
                    self.assertEqual(navbars(v), [], (code, v["path"], "carried and classic V2 views stay V2"))

    def test_routes_follow_the_v3_order_with_labels_from_the_catalogue(self):
        for code, loc in LOCS.items():
            nb = navbars(view("home", code))[0]
            main, more = nb["routes"][:-1], nb["routes"][-1]
            self.assertEqual([r["url"] for r in main],
                             [f"/{loc['url_base']}/{p}" for p in ("home", "rooms", "energy", "cameras")])
            self.assertEqual([r["label"] for r in main],
                             [V.loc_t(loc, k) for k in ("nav.home", "nav.rooms", "nav.energy", "nav.cameras")])
            self.assertEqual(more["label"], V.loc_t(loc, "nav.more"))
            self.assertEqual(more["tap_action"], {"action": "open-popup"})
            self.assertEqual([i["url"].split("/")[-1] for i in more["popup"]],
                             ["security", "lighting", "climate", "network", "house-health", "alerts", "bills"])

    def test_current_destination_marked_and_labels_shown(self):
        nb = navbars(view("home"))[0]
        self.assertEqual(nb["layout"], {"reflect_child_state": True})   # More lit while one of its pages is open
        self.assertEqual(nb["desktop"], {"show_labels": True})
        self.assertEqual(nb["mobile"], {"show_labels": True, "safe_area": True})

    def test_native_top_bar_stays_as_the_fallback(self):
        for code in LOCS:
            for p in MAN["native"]:
                self.assertEqual(V.topbar_problems(view(p, code)), [], (code, p))

    def test_layout_model_gives_it_no_grid_space(self):
        self.assertFalse(L.visible(navbars(view("home"))[0], {}))


class NavbarGateBites(unittest.TestCase):
    def setUp(self):
        self.loc = LOCS["en"]
        self.v = copy.deepcopy(view("energy"))
        self.paths = [v["path"] for v in dash()["views"]]
        self.nb = navbars(self.v)[0]

    def problems(self):
        return V.navbar_problems(self.v, self.loc["url_base"], self.paths)

    def test_a_route_to_a_page_that_does_not_exist(self):
        self.nb["routes"][1]["url"] = f"/{self.loc['url_base']}/nowhere"
        self.assertTrue(self.problems())

    def test_an_undocumented_option(self):
        self.nb["styles"] = "ha-card { display: none }"
        self.assertTrue(self.problems())

    def test_no_home_route(self):
        self.nb["routes"].pop(0)
        self.assertIn("no Home route", self.problems())

    def test_not_the_last_card(self):
        self.v["sections"][-1]["cards"].append({"type": "markdown", "content": "x", "grid_options": {"columns": 12}})
        self.assertIn("the navbar is not the page's last card", self.problems())

    def test_a_route_that_acts(self):
        self.nb["routes"][0]["tap_action"] = {"action": "toggle-menu"}
        self.assertTrue(self.problems())


class HomeWeather(unittest.TestCase):
    def band(self, code="en"):
        head = V.loc_t(LOCS[code], "h.weather")
        return next(s for s in view("home", code)["sections"] if s["cards"] and s["cards"][0].get("heading") == head)

    def test_full_width_band_that_packs(self):
        for code in LOCS:
            self.assertEqual(self.band(code)["column_span"], 2)
        spec = B.load_yaml(B.SRC / "views" / "home.yaml")
        self.assertEqual(V.band_problems(view("home"), spec), ([], [], []))

    def test_who_is_home_re_measured(self):
        sec = next(s for s in view("home")["sections"]
                   if any(c.get("entity", "").startswith("person.") for c in s["cards"]))
        rows = [c["grid_options"]["rows"] for c in sec["cards"] if c.get("type") == "tile"]
        self.assertEqual(rows, [2, 2, 2, 2])

    def test_only_the_frontends_forecast_types(self):
        with self.assertRaises(SystemExit):
            C.weather(None, W, forecast=True, forecast_type="weekly")


if __name__ == "__main__":
    unittest.main()
