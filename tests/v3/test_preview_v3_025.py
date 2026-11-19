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


# How a visibility condition on an entity the instance lacks is evaluated: in
# Home Assistant Core by newer frontends (the card is hidden — seen on the Green,
# 20/11/26), in the browser as 'unknown' by 20260826.7. Both must hold.
MODES = ("hide", "unknown")


def missing(states, *ents):
    """A state set without these entities: the instance does not have them."""
    return {k: v for k, v in states.items() if k not in ents}


def pairs(view, entity):
    """[the card shown while `entity` answers (its visibility condition names it),
    its self-hiding twin (show_empty: false; its template reads the entity)]."""
    main = [c for c in cards(view) if c.get("visibility") and c["visibility"][0].get("entity") == entity]
    twin = [c for c in cards(view) if c.get("show_empty") is False and f"states('{entity}')" in c.get("content", "")]
    assert len(main) == 1 and len(twin) == 1, (entity, len(main), len(twin))
    return main + twin


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
        cats = B.preview_catalogues({p.stem: B.load_yaml(p) for p in (B.SRC / "i18n").glob("*.yaml")})
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
        opened, silent = pairs(page("home"), DOOR)
        for mode in MODES:
            for state, want in (("on", (True, False)), ("off", (False, False)),
                                ("unavailable", (False, True)), ("unknown", (False, True)), (None, (False, True))):
                st = missing(self.normal, DOOR) if state is None else dict(self.normal, **{DOOR: state})
                self.assertEqual((L.visible(opened, st, mode), L.visible(silent, st, mode)), want, (mode, state))
        self.assertIn("[!WARNING]", opened["content"])        # amber, the theme's warning colour
        self.assertIn("前門感應器無回應", silent["content"])

    def test_unavailable_camera_gives_its_slot_to_an_offline_card(self):
        cam = cards(page("cameras"))
        for e in CAMS:
            pic, twin = pairs(page("cameras"), e)
            self.assertEqual(pic, next(c for c in cam if c["type"] == "picture-entity" and c["entity"] == e))
            st = dict(self.normal, **{e: "unavailable"})
            self.assertEqual((L.visible(pic, st), L.visible(twin, st)), (False, True), e)
            self.assertEqual((L.visible(pic, dict(st, **{e: "idle"})), L.visible(twin, dict(st, **{e: "idle"}))),
                             (True, False), e)
            out = render(twin["content"], st)
            self.assertIn("離線", out)
            self.assertIn("Offline", out)
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


    def test_timer_label_and_state_stay_on_their_own_lines(self):
        timer = next(c for c in cards(page("climate")) if "bedroom_parents_room_ac_timer" in c.get("content", ""))
        sw = "switch.bedroom_parents_room_ac_timer"
        for st in ("on", "off", "unavailable"):
            out = render(timer["content"], dict(self.normal, **{sw: st}))
            self.assertIn("</small>\n\n**", out, st)    # a paragraph break, not "Timer無資料"


class Catalogues(unittest.TestCase):
    def test_preview_strings_stay_out_of_the_working_catalogues(self):
        work = {c: B.load_yaml(B.SRC / "i18n" / f"{c}.yaml") for c in ("en", "yue", "km")}
        for c in ("en", "yue"):
            own = B.load_yaml(B.SRC / "preview" / "i18n" / f"{c}.yaml")
            self.assertFalse(set(own) & set(work[c]), c)
            self.assertTrue(all(k.startswith("pv.") for k in own), c)
        self.assertEqual(set(B.load_yaml(B.SRC / "preview" / "i18n" / "en.yaml")),
                         set(B.load_yaml(B.SRC / "preview" / "i18n" / "yue.yaml")))   # both languages, every key

    def test_a_key_in_both_is_refused(self):
        cats = {c: B.load_yaml(B.SRC / "i18n" / f"{c}.yaml") for c in ("en", "yue")}
        cats["en"]["pv.title"] = "re-worded"
        with self.assertRaises(SystemExit):
            B.preview_catalogues(cats)


class SampleData(unittest.TestCase):
    def test_sample_file_is_labelled_and_reads_only_verified_entities(self):
        sm = B.load_yaml(ROOT / "design/casaray-v3/preview_samples/mockup_2026-11-19.yaml")
        self.assertIn("示例數據", sm["label"])
        self.assertIn("SIMULATED", sm["label"])
        for e in list(sm["states"]) + list(sm["attrs"]) + list(sm["pictures"]["crops"]):
            self.assertIn(e, EXPORT, e)
        self.assertIn("示例圖片", sm["pictures"]["badge"])
        self.assertTrue((ROOT / sm["pictures"]["source"]).is_file())




class Trial(unittest.TestCase):
    """The 20/11/26 live trial (V3-025 item 12): missing light tiles, uneven
    camera slots, footer clearance. Offline arithmetic and renders only."""
    normal, attrs = R.scenarios()["normal"]
    LIGHTS = {"home": ["light.living_room", "light.dining", "light.bedroom_bedroom"],
              "lighting": ["light.living_room", "light.dining", "light.bedroom_bedroom", "light.bedroom_nightlight"]}
    READINGS = {"home": "sensor.bedroom_motion_sensor_temperature",
                "climate": "sensor.living_room_living_hue_hue_sensor_temperature"}

    def _one_shows(self, a, b, st, mode="hide"):
        return (L.visible(a, st, mode), L.visible(b, st, mode))

    def test_no_data_offline_and_silent_cards_never_hang_on_a_condition(self):
        """The 20/11 photos: Core hides a card whose condition names an entity it
        does not have, so a card that must say No data / Offline / not reporting
        cannot be gated by one. It hides itself while its template is empty."""
        for path in PV["views"]:
            for c in cards(page(path)):
                for cond in c.get("visibility") or []:
                    want = cond.get("state")
                    want = want if isinstance(want, list) else [want]
                    self.assertFalse({"unknown", "unavailable"} & {str(w) for w in want}, (path, c.get("type")))
                    self.assertNotIn("state_not", cond if c.get("type") == "markdown" else {}, path)
            hiding = [c for c in cards(page(path)) if c.get("show_empty") is False]
            for c in hiding:
                self.assertNotIn("visibility", c, path)
                self.assertTrue(c["content"].startswith("{%- if"), path)   # empty unless the case holds

    def test_every_camera_one_slot_one_size_in_every_state(self):
        slots = [(page("cameras"), e) for e in CAMS] + [(page("home"), CAMS[0])]
        for view, e in slots:
            pic, twin = pairs(view, e)
            self.assertEqual((pic["type"], twin["type"]), ("picture-entity", "markdown"), e)
            self.assertEqual(L.effective(pic), L.effective(twin), e)
            for mode in MODES:
                for state, want in (("idle", (True, False)), ("streaming", (True, False)),
                                    ("recording", (True, False)), ("unavailable", (False, True)),
                                    ("unknown", (False, True))):
                    self.assertEqual(self._one_shows(pic, twin, dict(self.normal, **{e: state}), mode), want,
                                     (e, state, mode))
                gone = missing(self.normal, e)
                self.assertEqual(self._one_shows(pic, twin, gone, mode), (False, True), (e, mode))   # never vanishes
            off = render(twin["content"], dict(self.normal, **{e: "unavailable"}))
            unk = render(twin["content"], dict(self.normal, **{e: "unknown"}))
            self.assertEqual(unk, render(twin["content"], gone))
            for word in ("離線", "Offline"):
                self.assertIn(word, off)
            for word in ("狀態未知", "State unknown"):
                self.assertIn(word, unk)
            self.assertEqual(render(twin["content"], dict(self.normal, **{e: "idle"})), "")   # hides itself
            for text in (off, unk, pic["name"]):   # an idle entity is not proof its stream plays
                self.assertNotIn("Online", text)
                self.assertNotIn("在線", text)
        names = [c for c in cards(page("cameras")) if c["type"] == "markdown" and "mdi:video-outline" in c["content"]]
        self.assertEqual(names, [])   # 2914b09's separate 4-unit name cells are gone

    def test_mixed_camera_states_pack_with_no_holes(self):
        cam = next(s for s in page("cameras")["sections"] if any(c.get("type") == "picture-entity" for c in s["cards"]))
        mix = dict(self.normal, **dict(zip(CAMS, ["idle", "unavailable", "unknown", "streaming", "idle", "unavailable"])))
        photo = missing(mix, *CAMS[1:4], CAMS[5])   # the 20/11 photos: four camera IDs not on the instance
        for st in (mix, missing(mix, CAMS[1], CAMS[3]), photo, R.scenarios()["dark"][0]):
            shown = [c for c in cam["cards"] if L.visible(c, st)]
            self.assertEqual(len(shown), len(CAMS))
            self.assertEqual({L.effective(c) for c in shown}, {(12, 3)})
            for where, resolved in (("wall iPad", 2), ("phone", 1)):
                self.assertEqual(L.section_holes(cam, L.units(cam.get("column_span", 1), resolved), st), 0, where)

    def test_light_and_reading_tiles_give_way_to_a_named_no_data_card(self):
        names = {"light.living_room": ("客廳", "Living room"), "light.dining": ("飯廳", "Dining"),
                 "light.bedroom_bedroom": ("Ray 房", "Ray room"), "light.bedroom_nightlight": ("夜燈", "Nightlight")}
        cases = [(p, e) for p, es in self.LIGHTS.items() for e in es] + list(self.READINGS.items())
        for path, e in cases:
            tile, nd = pairs(page(path), e)
            self.assertEqual((tile["type"], nd["type"]), ("tile", "markdown"), (path, e))
            self.assertEqual(L.effective(tile), L.effective(nd), (path, e))
            ok = "on" if e.startswith("light.") else "23"
            self.assertEqual(self._one_shows(tile, nd, dict(self.normal, **{e: ok})), (True, False), (path, e))
            for st in (dict(self.normal, **{e: "unavailable"}), dict(self.normal, **{e: "unknown"}),
                       missing(self.normal, e)):
                for mode in MODES:
                    self.assertEqual(self._one_shows(tile, nd, st, mode), (False, True), (path, e, mode))
                out = render(nd["content"], st)
                for word in ("無資料", "No data"):
                    self.assertIn(word, out, (path, e))
                if e in names:
                    for word in names[e]:
                        self.assertIn(word, out, (path, e))
            if L.effective(nd)[1] == 1:   # one 56 px row: one line, no icon
                out = render(nd["content"], missing(self.normal, e))
                self.assertNotIn("<br>", out)
                self.assertNotIn("\n", out)
                self.assertNotIn("ha-icon", out)
        # the Lighting tiles keep V3 Lighting's own controls; Home's stay read-only
        for e in self.LIGHTS["lighting"]:
            self.assertEqual(pairs(page("lighting"), e)[0]["features"], [{"type": "light-brightness"}])
        for e in self.LIGHTS["home"]:
            t = pairs(page("home"), e)[0]
            self.assertEqual((t["icon_tap_action"], t["hold_action"]), ({"action": "none"}, {"action": "none"}))

    def test_weather_card_names_itself_when_it_has_no_data(self):
        w = "weather.forecast_home"
        card = next(c for c in cards(page("home")) if c["type"] == "markdown" and "pv.cond" not in c["content"]
                    and w in c["content"] and "## " in c["content"])
        for st in (missing(self.normal, w), dict(self.normal, **{w: "unavailable"})):
            out = render(card["content"], st)
            for word in ("天氣", "Weather", "無資料", "No data"):
                self.assertIn(word, out)
        out = render(card["content"], dict(self.normal, **{w: "partlycloudy"}), {w: {"temperature": 21}})
        self.assertIn("21°C", out)
        self.assertIn("多雲間晴", out)
        self.assertNotIn("無資料", out)

    def test_night_targets_are_unchanged_until_verified_live(self):
        night = next(c for c in cards(page("lighting")) if "晚間模式" in c.get("content", ""))
        self.assertEqual(night["tap_action"]["target"]["entity_id"],
                         ["light.living_room", "light.bedroom_bedroom", "light.dining"])
        self.assertEqual(night["tap_action"]["data"], {"brightness_pct": 10})

    def test_trial_sample_is_labelled_and_names_only_verified_ids(self):
        sm = B.load_yaml(ROOT / "design/casaray-v3/preview_samples/trial_2026-11-20.yaml")
        self.assertIn("SIMULATED", sm["label"])
        for e in sm["missing"] + list(sm["states"]) + list(sm["attrs"]) + list(sm["pictures"]["crops"]):
            self.assertIn(e, EXPORT, e)   # "missing" means absent on the instance, never an invented ID
        self.assertFalse(set(sm["missing"]) & set(sm["states"]))


if __name__ == "__main__":
    unittest.main()
