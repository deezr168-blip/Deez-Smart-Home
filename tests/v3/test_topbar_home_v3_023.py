"""V3-023: the shared top bar, and Home's compaction and alignment pass.
DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant. Geometry is ha_layout.py's arithmetic (read
from frontend 20260826.7); wording is an offline Jinja render
(render_check.py). Neither is proof of how a device draws the card.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import components as C  # noqa: E402
import ha_layout as L  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
CODES = [x["code"] for x in MAN["locales"]]
PAGES = list(MAN["native"]) + list(MAN.get("new_views") or [])
RAIL = {p for p, _, _ in C.RAIL}
AC = "climate.bedroom_parents_room_ac"


def dash(code="en"):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return B.load_yaml(ROOT / loc["output"])


def view(d, path):
    return next(v for v in d["views"] if v["path"] == path)


def spec(path):
    return B.load_yaml(B.SRC / "views" / f"{path}.yaml")


def catalogue(code):
    return B.load_yaml(B.SRC / "i18n" / f"{code}.yaml")


class TopBar(unittest.TestCase):
    def test_every_page_in_every_locale_passes_the_gate(self):
        for code in CODES:
            d = dash(code)
            for p in PAGES:
                self.assertEqual(V.topbar_problems(view(d, p), spec(p), RAIL), [], (code, p))

    def test_gate_catches_the_bar_it_replaces(self):
        """69b5164's bar: auto-height wordmark and clock beside two-row named
        buttons at 2 units, the current one inert but not marked."""
        old = [{"type": "markdown", "content": "## CasaRay", "grid_options": {"columns": 6, "rows": "auto"}},
               {"type": "markdown", "content": "## 20:30", "grid_options": {"columns": 6, "rows": "auto"}}]
        for path, _, icon in C.RAIL:
            old.append({"type": "button", "name": path, "icon": icon, "show_name": True, "show_icon": True,
                        "tap_action": {"action": "none"} if path == "home" else
                        {"action": "navigate", "navigation_path": "/x/" + path},
                        "grid_options": {"columns": 2, "rows": 2}})
        v = {"path": "home", "sections": [{"type": "grid", "column_span": 2, "cards": old}]}
        found = " | ".join(V.topbar_problems(v, {"sections": [{"topbar": True}]}, RAIL))
        self.assertIn("more than one height", found)
        self.assertIn("is 2 units (labels need 3)", found)
        self.assertIn("1 inert and 0 tinted", found)

    def test_one_row_on_the_wall_two_on_a_phone(self):
        bar = view(dash(), "home")["sections"][0]
        sizes = [L.effective(c) for c in bar["cards"]]
        self.assertEqual(L.place(sizes, 24)[1:], (2, 0))   # one 2-row band, no holes
        self.assertEqual(L.place(sizes, 12)[1:], (4, 0))   # two of them on a phone

    def test_header_keeps_time_above_a_ddmmyy_date_and_the_marker(self):
        for code in CODES:
            head = view(dash(code), "home")["sections"][0]["cards"][0]["content"]
            self.assertLess(head.index("strftime('%H:%M')"), head.index("strftime('%d/%m/%y')"), code)
            self.assertNotIn("%Y", head, code)
            self.assertIn(catalogue(code)["app.dev_short"], head, code)

    def test_current_destination_is_marked_on_rail_pages_only(self):
        for code in CODES:
            d = dash(code)
            for p in PAGES:
                buttons = [c for c in view(d, p)["sections"][0]["cards"] if c["type"] == "button"]
                marked = [b for b in buttons if b.get("color") == "accent"]
                self.assertEqual(len(marked), 1 if p in RAIL else 0, (code, p))
                for b in marked:
                    self.assertEqual(b["tap_action"], {"action": "none"}, (code, p))

    def test_header_title_shortens_only_the_header(self):
        en = catalogue("en")
        page = view(dash(), "rubbish-collection")
        self.assertEqual(page["title"], en["nav.rubbish"])                       # the page keeps its name
        head = page["sections"][0]["cards"][0]["content"]
        self.assertTrue(head.startswith("## " + en["nav.rubbish_short"] + "\n"), head)
        self.assertEqual(view(dash(), "weather")["sections"][0]["cards"][0]["content"].split("\n")[0],
                         "## " + en["nav.weather"])                              # no key, no change


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

    def test_more_boards_six_across_on_the_wall_three_on_a_phone(self):
        band = view(dash(), "home")["sections"][-1]
        buttons = [c for c in band["cards"] if c["type"] == "button"]
        self.assertEqual(len(buttons), 12)
        self.assertEqual({L.effective(c) for c in buttons}, {(4, 2)})
        self.assertEqual(L.section_holes(band, 24), 0)
        self.assertEqual(L.section_holes(band, 12), 0)

    def test_new_strings_exist_in_every_written_catalogue(self):
        for code in ("en", "yue", "km"):
            for key in ("app.dev_short", "ac.parents_name", "nav.rubbish_short"):
                self.assertIn(key, catalogue(code), (code, key))
        # the short marker is part of each locale's own banner: no new vocabulary
        for code in CODES:
            c = catalogue(code)
            if "app.dev_short" in c:
                self.assertIn(c["app.dev_short"].lower(), c["app.dev_banner"].lower(), code)


if __name__ == "__main__":
    unittest.main()
