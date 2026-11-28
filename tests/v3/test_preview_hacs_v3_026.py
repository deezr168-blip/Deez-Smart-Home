"""V3-026: the owner-approved custom cards in the bilingual preview. DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

Owner decision 20/11/26: Kiosk Mode, Bubble Card, Advanced Camera Card,
auto-entities, ApexCharts, Power Flow Card Plus and WallPanel may be used in the
preview. These tests pin what each one is allowed to do there and prove the
gate catches anything else. Offline: nothing proves a card renders on a device,
and nothing here installs one.
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
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
PV = MAN["preview"]
EXPORT = B.load_export(ROOT / MAN["entity_authority"])
SOLAR, GRID = "sensor.primo_5_0_1_1_ac_power", "sensor.powerpal_gateway_powerpal_power"
CAMS = ["camera.front_door_live_view", "camera.tapo_c425_north_wall_hd_stream_direct",
        "camera.tapo_c420_east_wall_hd_stream_direct", "camera.tapo_c420_south_wall_hd_stream_direct",
        "camera.tapo_c200_stockroom_hd_stream_direct", "camera.smart_pet_feeder"]


def dash():
    return B.load_yaml(ROOT / PV["output"])


def page(path):
    return next(v for v in dash()["views"] if v["path"] == path)


def cards(view):
    return list(V.walk_cards(view))


def of(view, t):
    return [c for c in cards(view) if c.get("type") == t]


def problems(view):
    spec = B.load_yaml(B.SRC / "preview" / f"{view['path']}.yaml")
    wloc = next(l for l in MAN["locales"] if l["url_base"] == PV["working_url_base"])
    wpaths = {v["path"] for v in B.load_yaml(ROOT / wloc["output"])["views"]}
    return V.preview_problems(view, spec, EXPORT, set(PV["views"]), PV["url_base"], wpaths,
                              PV["working_url_base"], PV["tabs"])


class Approved(unittest.TestCase):
    def test_only_the_approved_custom_cards_and_all_of_them(self):
        used = {c["type"] for v in dash()["views"] for c in cards(v) if c["type"].startswith("custom:")}
        self.assertEqual(used, C.PREVIEW_CUSTOM)
        self.assertEqual(C.PREVIEW_CUSTOM, {"custom:bubble-card", "custom:advanced-camera-card",
                                            "custom:auto-entities", "custom:apexcharts-card",
                                            "custom:power-flow-card-plus"})
        self.assertIn("kiosk_mode", dash())
        self.assertIn("wallpanel", dash())

    def test_every_page_passes_the_gate(self):
        for v in dash()["views"]:
            p = problems(v)
            self.assertFalse(any(p.values()), (v["path"], {k: x for k, x in p.items() if x}))
        self.assertEqual(V.root_problems(dash(), EXPORT), [])

    def test_working_dashboards_carry_only_the_v3_027_four(self):
        """V3-026 kept the working dashboards free of these cards. V3-027 (owner
        brief, 21/11/26) adopts four there: Power Flow Card Plus, ApexCharts,
        auto-entities and WallPanel. Bubble Card, Advanced Camera Card and Kiosk
        Mode still never reach a working dashboard."""
        adopted = set().union(*C.WORKING_CUSTOM.values())
        self.assertEqual(adopted, {"custom:power-flow-card-plus", "custom:apexcharts-card", "custom:auto-entities"})
        for loc in MAN["locales"]:
            text = (ROOT / loc["output"]).read_text(encoding="utf-8")
            for t in C.PREVIEW_CUSTOM - adopted:
                self.assertNotIn(t, text, loc["code"])
            self.assertNotIn("kiosk_mode:", text, loc["code"])


class DashboardLevel(unittest.TestCase):
    def test_kiosk_mode_is_the_legacy_dashboards_settings(self):
        legacy = B.load_yaml(ROOT / "dashboards/deez_smart_home.yaml")["kiosk_mode"]
        self.assertEqual(dash()["kiosk_mode"], {"hide_header": True, "hide_sidebar": True})
        self.assertTrue(legacy["hide_header"] and legacy["hide_sidebar"])

    def test_wallpanel_screensaver_leaves_chrome_to_kiosk_mode(self):
        wp = dash()["wallpanel"]
        self.assertTrue(wp["enabled"])
        self.assertFalse(wp["hide_toolbar"] or wp["hide_sidebar"])
        self.assertTrue(wp["image_url"].startswith("media-source://"))
        normal, attrs = R.scenarios()["normal"]
        dark = R.scenarios()["dark"][0]
        clock = wp["cards"][0]["content"]
        self.assertIn("%d/%m/%y", clock)
        for c in wp["cards"]:
            self.assertEqual(c["type"], "markdown")
            out = R.env_for(normal, attrs).from_string(c["content"]).render()
            self.assertTrue(V.bilingual(out), out)
            dout = R.env_for(dark, {}).from_string(c["content"]).render()
            for word in ("已關", "Closed"):   # never a closed door when nothing answers
                self.assertNotIn(word, dout)
        door = wp["cards"][2]["content"]
        self.assertIn("無資料", R.env_for(dark, {}).from_string(door).render())


class Bubble(unittest.TestCase):
    def test_room_rows_open_their_pop_ups_and_every_pop_up_is_reachable(self):
        rooms = page("rooms")
        hashes = {c["hash"] for c in of(rooms, "custom:bubble-card") if c.get("card_type") == "pop-up"}
        self.assertEqual(hashes, {"#living-room", "#dining", "#ray-room"})
        self.assertEqual({n for n in V.nav_paths(rooms) if n.startswith("#")}, hashes)

    def test_sliders_are_lights_and_readings_only_read(self):
        for c in of(page("rooms"), "custom:bubble-card"):
            if c.get("card_type") == "pop-up":
                self.assertTrue(V.bilingual(c["name"]))
                continue
            self.assertIn(c["entity"], EXPORT)
            if c["button_type"] == "slider":
                self.assertTrue(c["entity"].startswith("light."), c["entity"])
            else:
                self.assertEqual(c["button_type"], "state")
                self.assertEqual(c["tap_action"], {"action": "more-info"})
                self.assertEqual(c["button_action"], {"tap_action": {"action": "more-info"}})

    def test_closed_pop_ups_take_no_space(self):
        rooms = page("rooms")
        pop = next(s for s in rooms["sections"] if any(c.get("card_type") == "pop-up" for c in s["cards"]))
        normal = R.scenarios()["normal"][0]
        self.assertEqual([c for c in pop["cards"] if L.visible(c, normal)], [])


class Cameras(unittest.TestCase):
    def test_one_grid_card_over_the_six_cameras(self):
        acc = of(page("cameras"), "custom:advanced-camera-card")
        self.assertEqual(len(acc), 1)
        self.assertEqual([c["camera_entity"] for c in acc[0]["cameras"]], CAMS)
        self.assertEqual(acc[0]["live"]["display"]["mode"], "grid")
        for c in acc[0]["cameras"]:
            self.assertTrue(c["always_error_if_entity_unavailable"])
            self.assertTrue(V.bilingual(c["title"]))
        self.assertNotIn("menu", acc[0])   # the card's own menu defaults; no PTZ or microphone settings


class Energy(unittest.TestCase):
    def test_flow_and_chart_read_the_two_measured_sensors(self):
        e = page("energy")
        pf = of(e, "custom:power-flow-card-plus")[0]["entities"]
        self.assertEqual((pf["solar"]["entity"], pf["grid"]["entity"]), (SOLAR, GRID))
        self.assertNotIn("entity", pf["home"])   # no consumption sensor exists: Home is the card's sum
        ap = of(e, "custom:apexcharts-card")[0]
        self.assertEqual([s["entity"] for s in ap["series"]], [SOLAR, GRID])
        self.assertEqual({s["type"] for s in ap["series"]}, {"area"})
        self.assertEqual((ap["graph_span"], ap["span"]), ("24h", {"start": "day"}))
        for x in (SOLAR, GRID):
            self.assertIn(x, EXPORT)

    def test_the_home_caveat_is_on_the_page_in_both_languages(self):
        text = " ".join(c.get("content", "") for c in of(page("energy"), "markdown"))
        self.assertIn("偏高", text)
        self.assertIn("reads high while the panels export", text)


class HouseHealth(unittest.TestCase):
    def test_lists_are_filters_not_hand_kept_ids(self):
        lists = of(page("house-health"), "custom:auto-entities")
        domains = set()
        for c in lists:
            for rule in c["filter"]["include"]:
                self.assertEqual(set(rule), {"domain", "state"})
                self.assertEqual(rule["state"], "unavailable")
                domains.add(rule["domain"])
            self.assertEqual(c["card"]["type"], "entities")
            self.assertTrue(V.bilingual(c["else"]["content"]))
        self.assertEqual(domains, {"light", "switch", "camera", "sensor", "binary_sensor"})

    def test_more_opens_the_preview_pages_and_no_link_shares_their_names(self):
        links = set(V.nav_paths(page("more")))
        self.assertIn(f"/{PV['url_base']}/energy", links)
        self.assertIn(f"/{PV['url_base']}/house-health", links)
        for v in dash()["views"]:
            for n in V.nav_paths(v):
                self.assertNotIn(n, (f"/{PV['working_url_base']}/energy", f"/{PV['working_url_base']}/house-health"))


class GateBites(unittest.TestCase):
    def test_a_switch_slider_an_unknown_card_and_an_orphan_hash_are_caught(self):
        rooms = page("rooms")
        bad = copy.deepcopy(rooms)
        pop = next(c for c in V.walk_cards(bad) if c.get("card_type") == "pop-up")
        pop["cards"].append({"type": "custom:bubble-card", "card_type": "button", "button_type": "slider",
                             "entity": "switch.g_printer_p100", "name": "打印機 Printer"})
        self.assertTrue(problems(bad)["custom"])
        bad = copy.deepcopy(rooms)
        bad["sections"][-1]["cards"].append({"type": "custom:button-card", "grid_options": {"columns": 12}})
        self.assertIn("custom:button-card", problems(bad)["types"])
        bad = copy.deepcopy(rooms)
        bad["sections"][-1]["cards"][0]["hash"] = "#lounge"
        self.assertTrue(problems(bad)["links"])
        bad = copy.deepcopy(rooms)
        reading = next(c for c in V.walk_cards(bad) if c.get("button_type") == "state")
        reading["button_action"] = {"tap_action": {"action": "toggle"}}
        self.assertTrue(problems(bad)["custom"])

    def test_dashboard_level_settings_are_held_to_what_was_reviewed(self):
        d = copy.deepcopy(dash())
        d["kiosk_mode"]["block_mouse"] = True
        self.assertTrue(V.root_problems(d, EXPORT))
        d = copy.deepcopy(dash())
        d["wallpanel"]["hide_toolbar"] = True
        self.assertTrue(V.root_problems(d, EXPORT))


if __name__ == "__main__":
    unittest.main()
