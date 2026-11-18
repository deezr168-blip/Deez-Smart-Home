"""V3-024: one shared, named top bar on every native view, and More boards
labels that fit a phone.  DEVELOPMENT ONLY — NOT DEPLOYED.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant. These check the generated YAML against the
pinned frontend's grid rules (ha_layout.py) and the gate that guards it
(validate_dashboard.topbar_problems), in all four locales. Whether a label
fits on the device is measured offline with preview_view.py --shots and
proven only on the wall iPad and a phone.
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
LOCALES = [x["code"] for x in MAN["locales"]]
RAIL = [p for p, _, _ in C.RAIL]


def views(code):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return B.load_yaml(ROOT / loc["output"])["views"]


def native(code):
    return [v for v in views(code) if v["path"] in MAN["native"]]


def view(path, code="en"):
    return next(v for v in views(code) if v["path"] == path)


def catalogue(code):
    return B.load_yaml(B.SRC / "i18n" / f"{code}.yaml")


class SharedTopBar(unittest.TestCase):
    def test_every_native_view_in_every_locale_passes_the_gate(self):
        for code in LOCALES:
            vs = native(code)
            self.assertGreaterEqual(len(vs), 18, code)
            for v in vs:
                self.assertEqual(V.topbar_problems(v), [], (code, v["path"]))

    def test_one_bar_everywhere_home_and_cameras_included(self):
        """Home sits in the same place on every page: the bar's shape is the
        same on every native view; only the title and the marked page differ."""
        def shape(v):
            return [(c["type"], L.effective(c), c.get("icon")) for c in v["sections"][0]["cards"]]
        for code in LOCALES:
            shapes = {v["path"]: shape(v) for v in native(code)}
            self.assertEqual(len({str(s) for s in shapes.values()}), 1, code)

    def test_every_rail_button_is_named_from_its_own_catalogue(self):
        for code in LOCALES:
            cat, en = catalogue(code), catalogue("en")
            for v in native(code):
                btns = [c for c in v["sections"][0]["cards"] if c["type"] == "button"]
                for (path, key, _), b in zip(C.RAIL, btns):
                    self.assertIsNot(b.get("show_name"), False, (code, v["path"], path))
                    self.assertEqual(b["name"], cat.get(key, en[key]), (code, path))

    def test_the_current_page_is_inert_and_amber_and_only_it(self):
        for path in ("home", "cameras", "lighting", "energy"):
            btns = [c for c in view(path)["sections"][0]["cards"] if c["type"] == "button"]
            marked = [RAIL[i] for i, b in enumerate(btns) if b.get("color")]
            inert = [RAIL[i] for i, b in enumerate(btns) if b["tap_action"] == {"action": "none"}]
            self.assertEqual(marked, [path])
            self.assertEqual(inert, [path])
            self.assertEqual(btns[RAIL.index(path)]["color"], "accent")
        # a page that is not a rail destination marks nothing
        btns = [c for c in view("rooms")["sections"][0]["cards"] if c["type"] == "button"]
        self.assertFalse(any(b.get("color") for b in btns))
        self.assertTrue(all(b["tap_action"]["action"] == "navigate" for b in btns))

    def test_one_height_whole_rows_on_wall_and_phone(self):
        cards = view("home")["sections"][0]["cards"]
        sizes = [L.effective(c) for c in cards]
        self.assertEqual({r for _, r in sizes}, {C.TOPBAR_BUTTON[1]})
        wall, phone = L.place(sizes, 24), L.place(sizes, 12)
        self.assertEqual((wall[1], wall[2]), (2, 0), "one row of buttons (two grid rows) on the wall iPad")
        self.assertEqual((phone[1], phone[2]), (4, 0), "two rows of buttons (four grid rows) on a phone")
        self.assertTrue(all(c >= 3 for c, _ in sizes if isinstance(c, int)))

    def test_header_has_time_over_dd_mm_yy_and_the_preview_marker(self):
        for code in LOCALES:
            head = view("cameras", code)["sections"][0]["cards"][0]
            self.assertTrue(head.get("text_only"))
            body = head["content"]
            self.assertIn("**{{ now().strftime('%H:%M') }}**<br>", body)
            self.assertLess(body.index("%H:%M"), body.index("%d/%m/%y"))
            self.assertNotIn("%Y", body)
            self.assertIn(catalogue(code)["app.preview_banner"], body)
            self.assertTrue(body.startswith("## "), "never four leading spaces")


class GateRejectsEarlierBars(unittest.TestCase):
    """Each earlier design, planted on a real view, is caught."""

    def planted(self, cards):
        v = copy.deepcopy(view("home"))
        v["sections"][0]["cards"] = cards
        return V.topbar_problems(v)

    def header(self):
        return copy.deepcopy(view("home")["sections"][0]["cards"][0])

    def test_v3_014_icon_only_bar(self):
        ctx_cards = [self.header()]
        for p in RAIL:
            b = copy.deepcopy(view("home")["sections"][0]["cards"][1 + RAIL.index(p)])
            b["show_name"] = False
            b["grid_options"] = {"columns": 2, "rows": 1}
            ctx_cards.append(b)
        bad = self.planted(ctx_cards)
        self.assertTrue(any("not named" in x for x in bad), bad)
        self.assertTrue(any("under 3" in x for x in bad), bad)

    def test_older_bar_named_only_on_the_current_page(self):
        cards = [self.header()]
        for i, p in enumerate(RAIL):
            b = copy.deepcopy(view("home")["sections"][0]["cards"][1 + i])
            b["show_name"] = p == "home"
            b["grid_options"] = {"columns": 2, "rows": 1}
            cards.append(b)
        bad = self.planted(cards)
        self.assertTrue(any("different heights" in x for x in bad), bad)
        self.assertTrue(any("not named" in x for x in bad), bad)

    def test_an_unmarked_current_page(self):
        cards = copy.deepcopy(view("home")["sections"][0]["cards"])
        del cards[1]["color"]
        self.assertTrue(any("inert and tinted" in x for x in self.planted(cards)))

    def test_a_button_that_goes_to_the_wrong_page(self):
        cards = copy.deepcopy(view("home")["sections"][0]["cards"])
        cards[2]["tap_action"]["navigation_path"] = cards[3]["tap_action"]["navigation_path"]
        self.assertTrue(any("does not navigate to its own page" in x for x in self.planted(cards)))

    def test_a_clock_without_the_two_digit_year(self):
        cards = copy.deepcopy(view("home")["sections"][0]["cards"])
        cards[0]["content"] = cards[0]["content"].replace("%d/%m/%y", "%d/%m/%Y")
        self.assertTrue(any("DD/MM/YY" in x for x in self.planted(cards)))


class MoreBoards(unittest.TestCase):
    @staticmethod
    def more(v, code):
        title = catalogue(code).get("h.more", catalogue("en")["h.more"])
        return next(s for s in v["sections"] if any(c.get("type") == "heading" and c["heading"] == title
                                                    for c in s["cards"]))

    def test_named_and_four_units_off_the_band_views(self):
        for code in LOCALES:
            for v in native(code):
                btns = [c for c in self.more(v, code)["cards"] if c["type"] == "button"]
                self.assertTrue(all(b["tap_action"]["action"] == "navigate" for b in btns), v["path"])
                self.assertTrue(all(b.get("show_name", True) and b["name"] for b in btns), v["path"])
                want = (6, 2) if v["path"] in ("home", "cameras") else (4, 2)
                self.assertEqual({L.effective(b) for b in btns}, {want}, (code, v["path"]))
                self.assertEqual({L.configured(b) for b in btns}, {want}, "drawn at the size written")


if __name__ == "__main__":
    unittest.main()
