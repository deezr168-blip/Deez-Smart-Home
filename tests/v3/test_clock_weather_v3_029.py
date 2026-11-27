"""V3-029: Clock Weather Card is Home's Weather band.  DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

Owner, 21/11/26: "switch weather band to clock weather". The card is installed
on the instance (docs/casaray-v3/HACS_INSTALLED.md). Its options come from its
own README at pkissling/clock-weather-card (3.1.0): the v3 `sections` schema,
with its default header rows and two patterns set (time HH:mm over date
dd/MM/yy). The hourly strip and daily list stay the card's defaults.

Offline: nothing here proves the card renders on a device. Nothing here proves
weather.forecast_home is the entity that answers, either; the owner confirms
that in an isolated preview on Home Assistant.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import components as C  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
EXPORT = B.load_export(ROOT / MAN["entity_authority"])
LOCS = {l["code"]: l for l in MAN["locales"]}
W = "weather.forecast_home"
CWC = "custom:clock-weather-card"
LOCALE = {"en": "en-au", "yue": "zh-hant", "zh-Hans": "zh-hans", "km": "km"}


def dash(code="en"):
    return B.load_yaml(ROOT / LOCS[code]["output"])


def view(path, code="en"):
    return next(v for v in dash(code)["views"] if v["path"] == path)


def band_at(v, code="en"):
    head = V.loc_t(LOCS[code], "h.weather")
    return next(i for i, s in enumerate(v["sections"]) if s["cards"] and s["cards"][0].get("heading") == head)


def card(v):
    return next(c for c in V.walk_cards(v) if c.get("type") == CWC)


def segments(c, kind):
    return [(i, seg) for i, row in enumerate(c["sections"]["header"]["rows"])
            for seg in row["segments"] if seg["type"] == kind]


class ClockWeather(unittest.TestCase):
    def test_one_card_on_the_entity_home_already_reads(self):
        self.assertIn(W, EXPORT)
        for code in LOCS:
            v = view("home", code)
            sec = v["sections"][band_at(v, code)]
            self.assertEqual([c["type"] for c in sec["cards"]], ["heading", CWC, "markdown"], code)
            self.assertEqual(sec["column_span"], 2)
            self.assertEqual(card(v)["entity"], W)
            types = [c.get("type") for c in V.walk_cards(v)]
            self.assertEqual(types.count(CWC), 1, code)
            self.assertNotIn("weather-forecast", types, "the native forecasts it replaced are gone")

    def test_time_over_dd_mm_yy(self):
        c = card(view("home"))
        (t_row, t), = segments(c, "time")
        (d_row, d), = segments(c, "date")
        self.assertLess(t_row, d_row, "the time sits above the date")
        self.assertEqual(t["time_pattern"], "HH:mm")
        self.assertEqual(d["date_pattern"], "dd/MM/yy")

    def test_header_keeps_the_cards_default_rows(self):
        rows = card(view("home"))["sections"]["header"]["rows"]
        self.assertEqual([[s["type"] for s in r["segments"]] for r in rows],
                         [["icon", "weather", "spacer", "weather"], ["time"], ["icon", "date"]])
        self.assertEqual((rows[1]["font_size"], rows[1]["alignment"], rows[2]["alignment"]),
                         ("4rem", "center", "center"))

    def test_locale_follows_the_dashboard(self):
        for code, tag in LOCALE.items():
            self.assertEqual(card(view("home", code))["locale"], tag, code)

    def test_only_reviewed_options_and_the_default_forecasts(self):
        c = card(view("home"))
        self.assertEqual(set(c), {"type", "entity", "locale", "sections", "grid_options"})
        self.assertEqual(set(c["sections"]), {"header"}, "strip and list stay the card's defaults")
        self.assertNotIn("tap_action", c, "the default opens more-info; nothing acts")

    def test_note_names_the_card_in_every_locale(self):
        for code in LOCS:
            v = view("home", code)
            note = v["sections"][band_at(v, code)]["cards"][2]["content"]
            self.assertIn("Clock Weather Card", note, code)

    def test_native_outside_reading_answers_above_it(self):
        for code in LOCS:
            v = view("home", code)
            chips = v["sections"][1]["cards"][0]
            self.assertEqual(chips["type"], "markdown")
            self.assertIn(W, chips["content"])
            self.assertIn(V.loc_t(LOCS[code], "chip.outside"), chips["content"])
            self.assertLess(1, band_at(v, code))

    def test_only_on_home(self):
        for code in LOCS:
            for v in dash(code)["views"]:
                if v["path"] != "home":
                    self.assertNotIn(CWC, {c.get("type") for c in V.walk_cards(v)}, (code, v["path"]))

    def test_home_passes_the_working_gate(self):
        for code in LOCS:
            self.assertEqual(V.working_custom_problems(view("home", code)), [], code)


class GateBites(unittest.TestCase):
    """Each rule fails on the shape it exists to stop."""

    def setUp(self):
        self.v = copy.deepcopy(view("home"))
        self.c = card(self.v)

    def problems(self):
        return V.working_custom_problems(self.v)

    def test_a_four_digit_year(self):
        segments(self.c, "date")[0][1]["date_pattern"] = "dd/MM/yyyy"
        self.assertTrue(any("DD/MM/YY" in p for p in self.problems()))

    def test_a_twelve_hour_clock(self):
        segments(self.c, "time")[0][1]["time_pattern"] = "h:mm a"
        self.assertTrue(any("HH:mm" in p for p in self.problems()))

    def test_an_unreviewed_option(self):
        self.c["tap_action"] = {"action": "navigate", "navigation_path": "/config"}
        self.assertTrue(any("unreviewed options" in p for p in self.problems()))

    def test_a_forecast_section_set_by_hand(self):
        self.c["sections"]["forecast_strip"] = {"type": "daily"}
        self.assertTrue(any("defaults" in p for p in self.problems()))

    def test_an_unreviewed_segment(self):
        self.c["sections"]["header"]["rows"][0]["segments"].append({"type": "sensor", "entity": "sensor.x"})
        self.assertTrue(any("segment" in p for p in self.problems()))

    def test_a_locale_nobody_reviewed(self):
        self.c["locale"] = "fr"
        self.assertTrue(any("locale" in p for p in self.problems()))

    def test_without_its_note(self):
        sec = self.v["sections"][band_at(self.v)]
        sec["cards"] = [c for c in sec["cards"] if c.get("type") != "markdown"]
        self.assertTrue(any("no note naming" in p for p in self.problems()))

    def test_on_another_page(self):
        e = copy.deepcopy(view("energy"))
        e["sections"][2]["cards"].append(copy.deepcopy(self.c))
        self.assertTrue(any("not allowed" in p for p in V.working_custom_problems(e)))

    def test_the_component_refuses_a_non_weather_entity(self):
        with self.assertRaises(SystemExit):
            C.clock_weather(None, "sensor.bedroom_motion_sensor_temperature")


if __name__ == "__main__":
    unittest.main()
