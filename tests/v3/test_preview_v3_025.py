"""V3-025: the bilingual design preview, a separate dashboard. DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant. Wording is an offline Jinja render
(render_check.py); geometry is ha_layout.py's arithmetic. Neither proves how
a device draws a card.
"""
import copy
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402
import ha_layout as L  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
PV = MAN["preview"]
EXPORT = B.load_export(ROOT / MAN["entity_authority"])
DOOR = "binary_sensor.f_contact_sensor_door"
CAMS = ["camera.front_door_live_view", "camera.tapo_c425_north_wall_hd_stream_direct",
        "camera.tapo_c420_east_wall_hd_stream_direct", "camera.tapo_c420_south_wall_hd_stream_direct",
        "camera.tapo_c200_stockroom_hd_stream_direct", "camera.smart_pet_feeder"]


def preview():
    return B.load_yaml(ROOT / PV["output"])


def page(path):
    return next(v for v in preview()["views"] if v["path"] == path)


def spec(path):
    return B.load_yaml(B.SRC / "preview" / f"{path}.yaml")


def working_paths():
    wloc = next(l for l in MAN["locales"] if l["url_base"] == PV["working_url_base"])
    return {v["path"] for v in B.load_yaml(ROOT / wloc["output"])["views"]}


def problems(view, path=None):
    return V.preview_problems(view, spec(path or view["path"]), EXPORT, set(PV["views"]), PV["url_base"],
                              working_paths(), PV["working_url_base"], PV["tabs"])


def cards(view):
    return [c for s in view["sections"] for c in s.get("cards", [])]


def render(content, states, attrs=None):
    return R.env_for(states, attrs or {}).from_string(content).render()


class Separate(unittest.TestCase):
    def test_working_dashboards_do_not_depend_on_the_preview(self):
        with_pv, _, _ = B.build(write=False)
        with mock.patch.object(B, "build_preview", return_value=None):
            without, _, _ = B.build(write=False)
        for loc in MAN["locales"]:
            self.assertEqual(with_pv[loc["output"]], without[loc["output"]], loc["code"])
        self.assertIn(PV["output"], with_pv)
        self.assertNotIn(PV["output"], without)

    def test_own_file_and_url_path(self):
        self.assertNotIn(PV["output"], [l["output"] for l in MAN["locales"]])
        self.assertNotIn(PV["url_base"], [l["url_base"] for l in MAN["locales"]])
        head = (ROOT / PV["output"]).read_text(encoding="utf-8")[:700]
        self.assertIn("DESIGN PREVIEW — NOT DEPLOYED", head)
        self.assertIn("SEPARATE dashboard", head)


class Bilingual(unittest.TestCase):
    def ctx(self):
        locs = {l["code"]: l for l in MAN["locales"]}
        cats = {p.stem: B.load_yaml(p) for p in (B.SRC / "i18n").glob("*.yaml")}
        return B.BiCtx(locs["yue"], locs["en"], cats, EXPORT, PV["url_base"], PV["views"],
                       PV["working_url_base"], PV.get("vocabulary"))

    def test_context_joins_both_languages_and_links_by_page(self):
        c = self.ctx()
        self.assertEqual(c.t("nav.home"), "主頁 Home")
        self.assertEqual(c.pair("s.no_data"), ("無資料", "No data"))   # the mockups' word, by alias
        self.assertIn("' ' ~", c.jt("chip.reporting", n="1", m="2"))    # a live value said in both
        self.assertEqual(c.link("rooms"), f"/{PV['url_base']}/rooms")
        self.assertEqual(c.link("energy"), f"/{PV['working_url_base']}/energy")

    def test_every_page_title_heading_and_tab_says_both(self):
        for v in preview()["views"]:
            self.assertTrue(V.bilingual(v["title"]), v["title"])
            for c in cards(v) + v["footer"]["card"]["cards"]:
                label = c.get("heading") if c["type"] == "heading" else c.get("name") if c["type"] == "button" else None
                if label is not None:
                    self.assertTrue(V.bilingual(label), (v["path"], label))

    def test_header_time_above_ddmmyy_date_with_weekday(self):
        for v in preview()["views"]:
            head = v["sections"][0]["cards"][0]["content"]
            self.assertLess(head.index("strftime('%H:%M')"), head.index("strftime('%d/%m/%y')"), v["path"])
            self.assertNotIn("%Y", head)
            self.assertIn("now().weekday()", head)
            self.assertIn("設計預覽 · 未部署", head)
            self.assertNotIn("示例數據", head)   # live readings on a device are not "sample data"


class Gate(unittest.TestCase):
    def test_every_page_passes(self):
        for v in preview()["views"]:
            self.assertEqual({k: x for k, x in problems(v).items() if x}, {}, v["path"])

    def test_gate_bites(self):
        home = page("home")
        bad = copy.deepcopy(home)
        cards(bad)[1]["tap_action"] = {"action": "perform-action", "perform_action": "switch.turn_on",
                                       "target": {"entity_id": "switch.g_printer_p100"}}
        self.assertTrue(problems(bad)["actions"])
        bad = copy.deepcopy(home)
        cards(bad)[1]["tap_action"] = {"action": "navigate", "navigation_path": f"/{PV['working_url_base']}/home"}
        self.assertTrue(problems(bad)["links"], "a working link that shares a preview page's name")
        bad = copy.deepcopy(home)
        bad["footer"]["card"]["cards"][0].pop("color")
        self.assertTrue(problems(bad)["tabs"], "an unmarked current tab")
        bad = copy.deepcopy(home)
        next(c for c in cards(bad) if c["type"] == "heading")["heading"] = "Room lights"
        self.assertTrue(problems(bad)["bilingual"], "an English-only heading")
        bad = copy.deepcopy(home)
        cards(bad)[1]["content"] = "**客廳** Living room · 已關 Off"
        self.assertTrue(problems(bad)["dark"], "a reassurance that is shown whatever answers")
        bad = copy.deepcopy(page("rooms"))
        bad["sections"][1]["cards"].append(dict(bad["sections"][1]["cards"][0],
                                                content="{{ states('sensor.not_a_real_entity') }}"))
        self.assertTrue(problems(bad, "rooms")["entities"])


class Honest(unittest.TestCase):
    normal, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def test_door_banner_open_silent_closed(self):
        opened, silent = [c for c in cards(page("home")) if c.get("visibility")
                          and c["visibility"][0].get("entity") == DOOR]
        for state, want in (("on", (True, False)), ("off", (False, False)),
                            ("unavailable", (False, True)), ("unknown", (False, True))):
            st = dict(self.normal, **{DOOR: state})
            self.assertEqual((L.visible(opened, st), L.visible(silent, st)), want, state)
        self.assertIn("[!WARNING]", opened["content"])        # amber, the theme's warning colour
        self.assertIn("前門感應器無回應", silent["content"])

    def test_unavailable_camera_gives_its_slot_to_an_offline_card(self):
        cam = cards(page("cameras"))
        for e in CAMS:
            pic = next(c for c in cam if c["type"] == "picture-entity" and c["entity"] == e)
            twin = next(c for c in cam if c["type"] == "markdown" and c.get("visibility")
                        and c["visibility"][0]["entity"] == e)
            st = dict(self.normal, **{e: "unavailable"})
            self.assertEqual((L.visible(pic, st), L.visible(twin, st)), (False, True), e)
            self.assertEqual((L.visible(pic, dict(st, **{e: "idle"})), L.visible(twin, dict(st, **{e: "idle"}))),
                             (True, False), e)
            self.assertIn("離線 Offline", render(twin["content"], st))
            self.assertEqual(L.effective(pic), L.effective(twin), e)   # same size: the grid keeps its shape

    def test_rooms_say_no_data_when_dark(self):
        rows = [c for c in cards(page("rooms")) if c["type"] == "markdown" and "›" in c["content"]]
        self.assertEqual(len(rows), 7)
        for c in rows:
            out = render(c["content"], self.dark)
            self.assertIn("無資料", out)
            for word in ("已開", "已關", "暫無動作", "°C"):
                self.assertNotIn(word, out)

    def test_air_con_is_read_only_and_climate_lives_under_more(self):
        clim = page("climate")
        self.assertEqual(list(V.actions(clim)), [])
        tinted = [b for b in clim["footer"]["card"]["cards"] if b.get("color")]
        self.assertEqual(len(tinted), 1)
        self.assertTrue(tinted[0]["tap_action"]["navigation_path"].endswith("/more"))
        status = next(c for c in cards(clim) if "climate.bedroom_parents_room_ac" in c.get("content", "")
                      and "## " in c.get("content", ""))
        self.assertIn("離線", render(status["content"], dict(self.normal, **{"climate.bedroom_parents_room_ac": "unavailable"})))
        on = render(status["content"], dict(self.normal, **{"climate.bedroom_parents_room_ac": "cool"}))
        self.assertIn("運行中", on)
        self.assertIn("只供查看", on)

    def test_mockup_controls_without_an_entity_are_inert_and_say_so(self):
        modes = [c for c in cards(page("lighting")) if "情境" not in c.get("heading", "") and
                 ("日常模式" in c.get("content", "") or "日間模式" in c.get("content", ""))]
        self.assertEqual(len(modes), 2)
        for c in modes:
            self.assertNotIn("tap_action", c)
            self.assertIn("未設定", c["content"])
        night = next(c for c in cards(page("lighting")) if "晚間模式" in c.get("content", ""))
        self.assertEqual(night["tap_action"]["perform_action"], "light.turn_on")   # the existing Night action
        self.assertEqual(night["tap_action"]["data"], {"brightness_pct": 10})

    def test_filter_and_timer_never_need_a_default_they_lack(self):
        clim = page("climate")
        for c in cards(clim):
            if c["type"] == "markdown":
                render(c["content"], self.dark)      # raises if as_datetime/as_timestamp has no default
                render(c["content"], self.normal, self.attrs)


class SampleData(unittest.TestCase):
    def test_sample_file_is_labelled_and_reads_only_verified_entities(self):
        sm = B.load_yaml(ROOT / "design/casaray-v3/preview_samples/mockup_2026-11-19.yaml")
        self.assertIn("示例數據", sm["label"])
        self.assertIn("SIMULATED", sm["label"])
        for e in list(sm["states"]) + list(sm["attrs"]) + list(sm["pictures"]["crops"]):
            self.assertIn(e, EXPORT, e)
        self.assertIn("示例圖片", sm["pictures"]["badge"])
        self.assertTrue((ROOT / sm["pictures"]["source"]).is_file())


if __name__ == "__main__":
    unittest.main()
