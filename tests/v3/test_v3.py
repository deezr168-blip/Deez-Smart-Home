"""CasaRay V3 offline regression tests.  DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

No network, no Home Assistant. Each honesty test has a positive control, so a
check that silently stopped seeing anything would fail rather than pass.
"""
import copy
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import yaml  # noqa: E402

import build_dashboard as B  # noqa: E402
import components as C  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
EN = B.load_yaml(B.SRC / "i18n" / "en.yaml")


def dash(code="en"):
    loc = next(l for l in MAN["locales"] if l["code"] == code)
    return B.load_yaml(ROOT / loc["output"])


def view(d, path):
    return next(v for v in d["views"] if v["path"] == path)


def render(d, path, states, attrs=None):
    return "\n".join(R.render_view(view(d, path), states, attrs or {}))


class Build(unittest.TestCase):
    def test_reproducible(self):
        a, _, _ = B.build(write=False)
        b, _, stale = B.build(write=False)
        self.assertEqual(a, b, "two builds of the same sources differ")
        self.assertEqual(stale, [], f"committed outputs are stale: {stale}")

    def test_baseline_drift_refused(self):
        orig = B.load_yaml
        def fake(path, loader=B.DupKeyLoader):
            d = orig(path, loader)
            if Path(path).name == "manifest.yaml":
                d = copy.deepcopy(d)
                d["baseline"]["sha256"] = "0" * 64
            return d
        B.load_yaml = fake
        try:
            with self.assertRaises(SystemExit):
                B.build(write=False)
        finally:
            B.load_yaml = orig

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(yaml.YAMLError):
            yaml.load("a: 1\na: 2\n", Loader=B.DupKeyLoader)

    def test_outputs_marked_development_only(self):
        for loc in MAN["locales"]:
            head = (ROOT / loc["output"]).read_text(encoding="utf-8")[:600]
            self.assertIn("DEVELOPMENT ONLY — NOT DEPLOYED", head, loc["output"])


class Gate(unittest.TestCase):
    def test_validation_gate_passes(self):
        g = V.Gate()
        V.validate(g)
        self.assertEqual(g.fail, [], "\n".join(g.fail))
        self.assertGreater(len(g.passed), 100)

    def test_sentinel_pattern_bites(self):
        self.assertTrue(V.SENTINEL.search("{{ states('x') | float(0) }}"))
        self.assertFalse(V.SENTINEL.search("{{ states('x') | float }}"))

    def test_secret_patterns_bite(self):
        # Assembled at runtime so this file never contains a secret-shaped literal.
        samples = ["to" + "ken: " + "abcdefgh12345678", "http" + "://192.168." + "1.10:8123",
                   "ey" + "JhbGciOiJIUzI1NiJ9.ey" + "JzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop"]
        for s in samples:
            self.assertTrue(any(rx.search(s) for rx in V.SECRET_PATTERNS), s)


class Parity(unittest.TestCase):
    def test_every_v2_view_has_a_v3_home(self):
        v2 = yaml.safe_load((ROOT / MAN["baseline"]["file"]).read_text(encoding="utf-8"))
        for code in [l["code"] for l in MAN["locales"]]:
            paths = {v["path"] for v in dash(code)["views"]}
            for v in v2["views"]:
                self.assertIn(v["path"], paths, f"[{code}] V2 view {v['path']} lost")
            for n in MAN["native"]:
                self.assertIn(f"v2-{n}", paths, f"[{code}] classic copy of {n} missing")

    def test_carried_views_are_verbatim_apart_from_links_and_theme(self):
        v2 = yaml.safe_load((ROOT / MAN["baseline"]["file"]).read_text(encoding="utf-8"))
        d = dash("en")
        for v in v2["views"]:
            if v["path"] in MAN["native"]:
                continue
            want = B.rewrite_links(copy.deepcopy(v), "casaray-v2", "casaray-v3")
            want["theme"] = MAN["classic_theme"]
            self.assertEqual(view(d, v["path"]), want, v["path"])

    def test_navigation_resolves(self):
        for loc in MAN["locales"]:
            d = B.load_yaml(ROOT / loc["output"])
            paths = {v["path"] for v in d["views"]}
            for n in V.nav_paths(d):
                self.assertTrue(n.startswith(f"/{loc['url_base']}/"), n)
                self.assertIn(n.split("/")[2], paths, n)

    def test_native_home_reaches_every_top_level_board_in_one_tap(self):
        d = dash("en")
        targets = {n.split("/")[2] for n in V.nav_paths(view(d, "home"))}
        tops = {v["path"] for v in d["views"] if not v.get("subview")} - {"home"}
        self.assertEqual(tops - targets, set())


class Honesty(unittest.TestCase):
    states, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def test_dark_home_claims_nothing(self):
        out = render(dash("en"), "home", self.dark)
        self.assertNotIn("nothing needs attention", out)
        self.assertNotIn("**0**", out)
        self.assertIn("No data", out)
        self.assertIn("not reporting", out)

    def test_all_clear_only_when_every_check_answered(self):
        d = dash("en")
        ok = answering(self.states)  # every check, the unpaid-bills count included
        self.assertIn("nothing needs attention", render(d, "home", ok))   # positive control
        one_dark = dict(ok, **{"binary_sensor.lg_fridge_door": "unavailable"})
        out = render(d, "home", one_dark)
        self.assertNotIn("nothing needs attention", out)
        self.assertIn("1 not reporting", out)

    def test_counts_state_what_answered(self):
        s = dict(self.states, **{"person.raymond_du": "home", "person.vinh_du": "unavailable",
                                 "person.ai_q_huang": "not_home"})
        out = render(dash("en"), "home", s)
        self.assertIn("Home **1**", out)
        self.assertIn("2 of 3 reporting", out)

    def test_air_con_never_invents_a_mode_or_temperature(self):
        d = dash("en")
        for st, want in [("unavailable", "**Offline**"), ("unknown", "**State unknown**"),
                         ("cool", "Room No data"), ("weird_mode", "Current: weird_mode")]:
            out = render(d, "climate", dict(self.states, **{"climate.bedroom_parents_room_ac": st}))
            self.assertIn(want, out, st)
        out = render(d, "climate", self.states, {"climate.bedroom_parents_room_ac":
                                                   {"current_temperature": 23.3, "temperature": 22}})
        self.assertIn("Room 23.3° · Target 22.0°", out)

    def test_cameras_say_state_in_words(self):
        s = dict(self.states, **{"camera.front_door_live_view": "unknown",
                                 "camera.smart_pet_feeder": "unavailable",
                                 "camera.tapo_c425_north_wall_hd_stream_direct": "idle"})
        out = render(dash("en"), "cameras", s)
        self.assertIn("Front door — **State unknown**", out)
        self.assertIn("Pet feeder — **Offline**", out)
        self.assertIn("North wall — **Online**", out)

    def test_no_four_space_markdown_in_any_locale(self):
        for code in [l["code"] for l in MAN["locales"]]:
            d = dash(code)
            for p in MAN["native"]:
                for scen, (st, at) in R.scenarios().items():
                    for o in R.render_view(view(d, p), st, at):
                        self.assertFalse(o.startswith("    "), f"{code}/{p}/{scen}")


PAID_FLAGS = ["input_boolean.elec_bill_paid", "input_boolean.gas_bill_paid",
              "input_boolean.water_bill_paid", "input_boolean.council_rate_paid",
              "input_boolean.rego_paid", "input_boolean.car_insurance_paid"]


def answering(states):
    """Every Needs-attention check answering and clear (the positive control)."""
    ok = dict(states)
    ok.update({e: "off" for e in ok if e.startswith("binary_sensor.")})
    ok.update({e: "idle" for e in ok if e.startswith("camera.")})
    ok.update({e: "80" for e in ok if e.endswith("_battery")})
    ok.update({e: "on" for e in PAID_FLAGS})
    ok["binary_sensor.eero_wan_status"] = "on"
    ok["sensor.bills_unpaid_count"] = "0"
    return ok


class MigratedEntities(unittest.TestCase):
    """The 16 V2-home entities (and every other rebuilt view's) have a verified V3 place."""
    states, attrs = R.scenarios()["normal"]

    def test_bills_count_is_an_attention_item(self):
        d, ok = dash("en"), answering(self.states)
        self.assertIn("nothing needs attention", render(d, "home", ok))       # positive control
        self.assertIn("Unpaid bills: 2", render(d, "home", dict(ok, **{"sensor.bills_unpaid_count": "2"})))

    def test_bills_zero_is_not_an_answer_while_its_inputs_are_dark(self):
        d, ok = dash("en"), answering(self.states)
        for flag in PAID_FLAGS:
            out = render(d, "home", dict(ok, **{flag: "unavailable"}))
            self.assertNotIn("nothing needs attention", out, flag)
            self.assertIn("1 not reporting", out, flag)
        out = render(d, "home", dict(ok, **{"sensor.bills_unpaid_count": "unavailable"}))
        self.assertNotIn("nothing needs attention", out)
        self.assertIn("1 not reporting", out)

    def test_unpaid_bills_still_raised_when_the_flags_are_dark(self):
        s = dict(answering(self.states), **{"sensor.bills_unpaid_count": "3"},
                 **{f: "unavailable" for f in PAID_FLAGS})
        self.assertIn("Unpaid bills: 3", render(dash("en"), "home", s))

    def test_shade_battery_alert_names_the_room_it_is_in(self):
        s = dict(answering(self.states), **{"sensor.aqara_roller_shade_driver_e1_battery": "9"})
        out = render(dash("en"), "home", s)
        self.assertIn("Ray's room battery low (9%)", out)
        self.assertNotIn("Living room battery low", out)

    def test_monitored_total_sits_beside_its_circuits_read_only(self):
        tiles = [c for s in view(dash("en"), "energy")["sections"] for c in s["cards"]
                 if c.get("type") == "tile"]
        by = {c["entity"]: c for c in tiles}
        for e in ("sensor.casa_monitored_power", "sensor.g_monitor_freezer_p110m_current_consumption",
                  "sensor.r_energy_monitor_p110m_current_consumption"):
            self.assertIn(e, by)
        t = by["sensor.casa_monitored_power"]
        self.assertEqual(t["tap_action"], {"action": "more-info"})   # a sensor's details: history, no control
        self.assertEqual(t["icon_tap_action"], {"action": "none"})

    def test_every_v2_entity_of_a_rebuilt_view_is_accounted_for(self):
        _, rep, _ = B.build(write=False)
        rows = {r["path"]: r for r in rep["views"]}
        home = {m["entity"]: m for m in rows["home"]["migration"]}
        self.assertEqual(len(home), 16)
        # CR-V3-17: the six that were carried are native now, so all 16 are.
        self.assertEqual({m["status"] for m in home.values()}, {"native"})
        for e, m in home.items():
            self.assertIn(e, rows[m["to"]]["entities"], e)
            self.assertIn(e, rows["v2-home"]["entities"], e)   # classic copy keeps it

    def _build_with(self, mutate):
        orig = B.load_yaml

        def fake(path, loader=B.DupKeyLoader):
            d = orig(path, loader)
            if Path(path).name == "manifest.yaml":
                d = copy.deepcopy(d)
                mutate(d["migration"])
            return d
        B.load_yaml = fake
        try:
            B.build(write=False)
        finally:
            B.load_yaml = orig

    def test_false_or_missing_migration_rows_stop_the_build(self):
        bad = {
            "row removed": lambda m: m["home"].pop("sensor.casa_monitored_power"),
            "wrong view": lambda m: m["home"]["sensor.casa_monitored_power"].update(to="climate"),
            "wrong kind": lambda m: m["home"]["switch.g_printer_p100"].update(status="carried"),
            "unknown view": lambda m: m["home"]["switch.g_printer_p100"].update(to="appliances"),
            "stray key": lambda m: m["home"]["switch.g_printer_p100"].update({"read-only": None}),
            "retained, no reason": lambda m: m["home"]["switch.g_printer_p100"].update(status="retained", note=""),
            "stale row": lambda m: m["home"].update({"sensor.not_on_v2_home": {"to": "home", "status": "native"}}),
        }
        for name, mutate in bad.items():
            with self.assertRaises(SystemExit, msg=name):
                self._build_with(mutate)
        self._build_with(lambda m: None)  # positive control: the real map builds

V2 = yaml.safe_load((ROOT / MAN["baseline"]["file"]).read_text(encoding="utf-8"))
V2_BY = {v["path"]: v for v in V2["views"]}
REBUILT_17 = ("security", "network", "ray-bedroom", "guest-room")
ROOMS_18 = ("rooms", "living-room", "kitchen", "dining", "parents-room", "garage")
CORE_19 = ("house-health", "alerts", "people")
REBUILT = REBUILT_17 + ROOMS_18 + CORE_19


def tiles(v):
    return [c for c in V.walk_cards(v) if c.get("type") == "tile"]


class NativeRebuilds(unittest.TestCase):
    """CR-V3-17: Security, Network, Ray's room and Guest room rebuilt natively."""
    states, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def test_rebuilt_views_are_native_and_keep_a_classic_copy(self):
        for p in REBUILT:
            self.assertIn(p, MAN["native"])
            for code in [l["code"] for l in MAN["locales"]]:
                d = dash(code)
                self.assertEqual(view(d, p)["theme"], MAN["theme"], (code, p))
                classic = view(d, "v2-" + p)
                want = B.rewrite_links(copy.deepcopy(V2_BY[p]), "casaray-v2", next(
                    l["url_base"] for l in MAN["locales"] if l["code"] == code))
                want.update(path="v2-" + p, subview=True, theme=MAN["classic_theme"],
                            title=f"{V2_BY[p].get('title', p)} (V2)")
                self.assertEqual(classic, want, f"{code}: classic v2-{p} must be the V2 view verbatim")

    def test_every_v2_entity_of_a_rebuilt_view_is_on_it(self):
        d = dash("en")
        for p in REBUILT:
            v2e = B.entities_in(V2_BY[p]) - {"input_boolean.chinese_dashboard"}
            moved = set(MAN.get("migration", {}).get(p, {}))   # e.g. zone.home -> People (carried)
            missing = v2e - B.entities_in(view(d, p)) - moved
            self.assertEqual(missing, set(), p)

    # ---- Security: safety behaviour unchanged
    def test_sirens_are_the_v2_tiles_byte_for_byte(self):
        want = [c for c in tiles(V2_BY["security"]) if c["entity"].startswith("siren.")]
        self.assertEqual(len(want), 3)
        for code in [l["code"] for l in MAN["locales"]]:
            got = [c for c in tiles(view(dash(code), "security")) if c["entity"].startswith("siren.")]
            self.assertEqual(got, want, code)
        for c in want:   # what that behaviour is: details on tap, nothing on the icon
            self.assertEqual(C.effective_tile_actions(c), ("more-info", "none"), c["entity"])

    def test_security_has_no_arming_disarming_or_emergency_action(self):
        sec = view(dash("en"), "security")
        self.assertEqual(list(V.actions(sec)), [])
        txt = yaml.safe_dump(sec)
        for dom in ("alarm_control_panel.", "lock.", "siren.turn_on", "siren.toggle", "button.press"):
            self.assertNotIn(dom, txt)

    def test_camera_switches_are_read_only_and_lead_to_the_classic_controls(self):
        sw = [c for c in tiles(view(dash("en"), "security")) if c["entity"].startswith("switch.")]
        self.assertEqual(len(sw), 12)
        for c in sw:
            self.assertEqual(c["icon_tap_action"], {"action": "none"}, c["entity"])
            self.assertEqual(c["tap_action"], {"action": "navigate", "navigation_path": "/casaray-v3/v2-security"})
        self.assertIn("switch.tapo_c425_north_wall_privacy", [c["entity"] for c in sw])

    def test_security_dark_claims_nothing(self):
        out = render(dash("en"), "security", self.dark)
        self.assertNotIn("nothing needs attention", out)
        self.assertNotIn("**0**", out)
        self.assertIn("Doors open **No data**", out)
        ok = dict(self.states, **{e: "off" for e in ("binary_sensor.f_contact_sensor_door",
                  "binary_sensor.m_contact_sensor_door", "binary_sensor.b_contact_sensor_door",
                  "siren.tapo_h200", "siren.tapo_c425_north_wall_siren", "siren.tapo_c200_stockroom_siren")},
                  **{e: "idle" for e in self.states if e.startswith("camera.")})
        self.assertIn("nothing needs attention", render(dash("en"), "security", ok))   # positive control
        out = render(dash("en"), "security", dict(ok, **{"siren.tapo_c425_north_wall_siren": "on"}))
        self.assertIn("North wall siren sounding", out)

    # ---- Network: connectivity in three states
    def test_network_states_online_offline_not_reporting(self):
        s = dict(self.states, **{"binary_sensor.g_printer_p100_cloud_connection": "on",
                                 "binary_sensor.k_coffee_p100_cloud_connection": "off",
                                 "binary_sensor.k_top_p100_cloud_connection": "unknown",
                                 "binary_sensor.k_bot_p100_cloud_connection": "unavailable",
                                 "sensor.g_printer_p100_signal_level": "3",
                                 "sensor.k_coffee_p100_signal_level": "unavailable"})
        out = render(dash("en"), "network", s)
        self.assertIn("G/Printer P100 — **Online** · signal 3", out)
        self.assertIn("K/Coffee P100 — **Offline**\n", out)          # no signal claimed from a dark sensor
        self.assertIn("K/Top P100 — **Not reporting**", out)
        self.assertIn("K/Bot P100 — **Not reporting**", out)
        self.assertRegex(out, r"\*\*\d+ online · \d+ offline · \d+ not reporting\*\*")

    def test_network_dark_says_nothing_answered(self):
        out = render(dash("en"), "network", self.dark)
        self.assertIn("No device is reporting", out)
        self.assertNotIn("0 online", out)
        self.assertNotIn("Online**", out)
        self.assertIn("Cameras **No data**", out)
        self.assertIn("Internet **No data**", out)

    def test_network_lines_do_not_run_together(self):
        out = render(dash("en"), "network", self.states)
        self.assertEqual(out.count("\n- "), 14 + 4, "14 devices and 4 groups, one per line")

    # ---- Rooms: original device assignments and controls
    def test_room_entities_match_v2_exactly(self):
        d = dash("en")
        for p in ("ray-bedroom", "guest-room"):
            v2e = B.entities_in(V2_BY[p]) - {"input_boolean.chinese_dashboard"}
            self.assertEqual(B.entities_in(view(d, p)), v2e, p)

    def test_tiles_behave_as_their_v2_tiles(self):
        """Every tile on a rebuilt view does what its V2 tile did, apart from the
        deliberate, gated departures: protected switches (camera privacy /
        detection / alerts, bulb power) lead to the classic controls instead."""
        d = dash("en")
        for p in REBUILT:
            v2t = {c["entity"]: c for c in tiles(V2_BY[p])}
            for c in tiles(view(d, p)):
                e = c["entity"]
                if V.protected_switch(e) or V.protected_setting(e):
                    self.assertEqual(C.effective_tile_actions(c), ("navigate", "none"), f"{p}: {e}")
                    goes = c["tap_action"]["navigation_path"].split("/")[2]
                    if e in v2t and C.effective_tile_actions(v2t[e]) == ("navigate", "none"):
                        # V2 already used it as a link only (Rooms index): same page as V2
                        self.assertEqual(goes, v2t[e]["tap_action"]["navigation_path"].split("/")[2], f"{p}: {e}")
                    else:
                        self.assertEqual(goes, "v2-" + p, f"{p}: {e} must open the classic controls")
                    continue
                if e not in v2t:
                    continue     # a reading V2 showed only inside a summary template
                self.assertIn(e, v2t, f"{p}: {e} was not a tile on V2")
                self.assertEqual(C.effective_tile_actions(c), C.effective_tile_actions(v2t[e]), f"{p}: {e}")
                want = [f["type"] for f in v2t[e].get("features", [])]
                got = [f["type"] for f in c.get("features", [])]
                self.assertEqual(got, want, f"{p}: {e} features")

    def test_scene_buttons_call_the_same_scenes(self):
        def scene_calls(v):
            return sorted(a["target"]["entity_id"] for a in V.actions(v) if a.get("perform_action") == "scene.turn_on")
        self.assertEqual(scene_calls(view(dash("en"), "ray-bedroom")), scene_calls(V2_BY["ray-bedroom"]))
        self.assertEqual(len(scene_calls(V2_BY["ray-bedroom"])), 6)

    def test_bulb_power_wall_switch_stays_read_only(self):
        c = next(c for c in tiles(view(dash("en"), "ray-bedroom")) if c["entity"] == "switch.bedroomlight_switch_1")
        self.assertEqual(c["icon_tap_action"], {"action": "none"})
        self.assertEqual(c["tap_action"]["action"], "navigate")

    def test_only_listed_switches_act_and_none_is_protected(self):
        # switches and helper toggles (gated alike since CR-V3-19)
        acting = {c["entity"] for p in MAN["native"] for c in tiles(view(dash("en"), p))
                  if c["entity"].split(".")[0] in ("switch", "input_boolean") and V.acting(c)}
        self.assertEqual(acting, set(MAN["controls"]))
        self.assertFalse(any(V.protected_switch(e) for e in MAN["controls"]))

    def test_rooms_navigation_reaches_the_rebuilt_rooms(self):
        d = dash("en")
        for src in ("home", "rooms"):
            targets = {n.split("/")[2] for n in V.nav_paths(view(d, src))}
            self.assertTrue({"ray-bedroom", "guest-room"} <= targets, src)
        for p in REBUILT:
            targets = {n.split("/")[2] for n in V.nav_paths(view(d, p))}
            self.assertIn("v2-" + p, targets, f"{p} links to its classic copy")
            self.assertIn("home", targets, f"{p} links Home")
            if p in ROOMS_18 and p != "rooms":
                self.assertIn("rooms", targets, f"{p} links back to All rooms")

    def test_rooms_dark_say_no_data(self):
        for p in ("ray-bedroom", "guest-room", "living-room", "kitchen", "dining", "parents-room", "garage"):
            out = render(dash("en"), p, self.dark)
            self.assertNotIn("**Normal**", out, p)
            self.assertNotIn("**Off**", out, p)
            self.assertIn("**Offline**", out, p)

    # ---- the gate's tile rules, shown biting on broken views
    def _safety(self, v):
        return V.tile_safety(v, V2_BY, MAN["controls"], "casaray-v2", "casaray-v3")

    def test_tile_safety_passes_the_real_views(self):
        for p in MAN["native"]:
            self.assertEqual(self._safety(view(dash("en"), p)), ([], []), p)

    def test_tile_safety_catches_unsafe_changes(self):
        d = dash("en")

        def mutated(p, entity, **change):
            v = copy.deepcopy(view(d, p))
            for c in V.walk_cards(v):
                if c.get("entity") == entity and c.get("type") == "tile":
                    c.update(change)
            return v
        cases = {
            "siren icon made to toggle": mutated("security", "siren.tapo_h200", icon_tap_action={"action": "toggle"}),
            "siren colour changed": mutated("security", "siren.tapo_h200", color="amber"),
            "privacy switch made a control": mutated("security", "switch.tapo_c425_north_wall_privacy",
                                                     tap_action={"action": "more-info"}, icon_tap_action={"action": "toggle"}),
            "bulb power made a control": mutated("ray-bedroom", "switch.bedroomlight_switch_1",
                                                 tap_action={"action": "more-info"}, icon_tap_action={"action": "toggle"}),
            "listed switch acting unlike V2": mutated("guest-room", "switch.g_printer_p100",
                                                      tap_action={"action": "toggle"}),
        }
        for name, v in cases.items():
            bad, prot = self._safety(v)
            self.assertTrue(bad or prot, name)
        unlisted = dict(MAN["controls"])
        unlisted.pop("switch.g_printer_p100")
        bad, _ = V.tile_safety(view(d, "guest-room"), V2_BY, unlisted, "casaray-v2", "casaray-v3")
        self.assertTrue(any("not in manifest controls" in b for b in bad))


class RoomsBatch(unittest.TestCase):
    """CR-V3-18: Rooms index, Living room, Kitchen, Dining, Parents' room, Garage."""
    states, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]

    def acts(self, p, entity):
        c = next(c for c in tiles(view(dash("en"), p)) if c["entity"] == entity)
        return C.effective_tile_actions(c)

    def test_ordinary_settings_keep_v2_toggles(self):
        for p, e in [("kitchen", "switch.k_coffee_p100_led"), ("kitchen", "switch.lg_fridge_express_mode"),
                     ("garage", "switch.g_monitor_freezer_p110m_led"),
                     ("parents-room", "switch.master_bedroom_light_sensor_55_qled_4k_ai"),
                     ("dining", "switch.smart_pet_feeder_time_watermark")]:
            self.assertEqual(self.acts(p, e), ("more-info", "toggle"), e)
            self.assertIn(e, MAN["controls"])

    def test_sensitive_switches_and_settings_are_inert(self):
        inert = [("garage", "switch.g_monitor_freezer_p110m"), ("garage", "switch.g_monitor_freezer_p110m_auto_off_enabled"),
                 ("kitchen", "switch.k_coffee_p100"), ("kitchen", "switch.k_bot_p100_auto_off_enabled"),
                 ("living-room", "switch.genio_power_board_with_usb_livingroom_socket_3"),
                 ("living-room", "switch.genio_power_board_with_usb_livingroom_child_lock"),
                 ("living-room", "switch.living_room_living_hue_hue_sensor_motion_sensor_enabled"),
                 ("living-room", "number.front_door_volume"),
                 ("parents-room", "switch.master_bedroom_power_point_socket_5"),
                 ("parents-room", "switch.bedroom_parents_room_ac_climate_react"),
                 ("parents-room", "switch.bedroom_parents_room_ac_timer"),
                 ("parents-room", "switch.mainroomlight_switch_1"),
                 ("dining", "switch.dinning_light_switch_1"), ("dining", "switch.smart_pet_feeder_privacy_mode"),
                 ("dining", "select.smart_pet_feeder_night_vision"),
                 ("dining", "select.smart_pet_feeder_motion_detection_sensitivity")]
        for p, e in inert:
            self.assertEqual(self.acts(p, e), ("navigate", "none"), e)
            self.assertTrue(V.protected_switch(e) or V.protected_setting(e), f"{e} must be a gated class")
            self.assertNotIn(e, MAN["controls"])

    def test_ordinary_room_controls_unchanged_from_v2(self):
        # lights, fan, fridge setpoints, scenes, media: same entity, same features, same actions
        self.assertEqual(self.acts("living-room", "fan.living_room_air_purifier"), ("more-info", "toggle"))
        fan = next(c for c in tiles(view(dash("en"), "living-room")) if c["entity"] == "fan.living_room_air_purifier")
        self.assertEqual([f["type"] for f in fan["features"]], ["fan-speed"])
        for e in ("number.lg_fridge_fridge_temperature", "number.lg_fridge_freezer_temperature"):
            c = next(c for c in tiles(view(dash("en"), "kitchen")) if c["entity"] == e)
            self.assertEqual([f["type"] for f in c["features"]], ["numeric-input"])
        for p in ("living-room", "dining"):
            calls = lambda v: sorted(a["target"]["entity_id"] for a in V.actions(v) if a.get("perform_action") == "scene.turn_on")
            self.assertEqual(calls(view(dash("en"), p)), calls(V2_BY[p]), p)
        media = {p: [c["entity"] for c in V.walk_cards(view(dash("en"), p)) if c.get("type") == "media-control"]
                 for p in ("living-room", "parents-room")}
        self.assertEqual(media, {"living-room": ["media_player.living_room_tv_samsung_q9_series_65"],
                                 "parents-room": ["media_player.55_qled_4k_ai_qa55q7faawxxy"]})
        self.assertEqual([c["entity"] for c in V.walk_cards(view(dash("en"), "kitchen")) if c.get("type") == "todo-list"],
                         ["todo.shopping_list"])

    def test_rooms_index_tiles_open_the_same_pages_as_v2(self):
        want = {(c["entity"], c["tap_action"]["navigation_path"].split("/")[2]) for c in tiles(V2_BY["rooms"])}
        got = {(c["entity"], c["tap_action"]["navigation_path"].split("/")[2]) for c in tiles(view(dash("en"), "rooms"))}
        self.assertEqual(got, want)
        for c in tiles(view(dash("en"), "rooms")):
            self.assertEqual(c["icon_tap_action"], {"action": "none"})

    def test_zone_count_is_not_used_and_still_has_a_home(self):
        self.assertNotIn("zone.home", B.entities_in(view(dash("en"), "rooms")))
        row = MAN["migration"]["rooms"]["zone.home"]
        # CR-V3-18 left it on carried People; CR-V3-19 rebuilt People natively.
        self.assertEqual((row["to"], row["status"]), ("people", "native"))
        self.assertIn("zone.home", B.entities_in(view(dash("en"), "people")))
        out = render(dash("en"), "rooms", self.dark)
        self.assertIn("Home **No data**", out)

    def test_parents_air_con_read_only_with_one_tap_to_the_v2_controls(self):
        v = view(dash("en"), "parents-room")
        self.assertFalse([c for c in V.walk_cards(v) if c.get("type") == "thermostat"])
        self.assertFalse([a for a in V.actions(v) if "climate" in str(a)])
        targets = {n.split("/")[2] for n in V.nav_paths(v)}
        self.assertIn("v2-parents-room", targets)
        thermo = [c for c in V.walk_cards(view(dash("en"), "v2-parents-room")) if c.get("type") == "thermostat"]
        self.assertEqual([c["entity"] for c in thermo], ["climate.bedroom_parents_room_ac"])   # V2 controls intact

    def test_climate_controls_button_now_opens_the_classic_parents_room(self):
        for loc in MAN["locales"]:
            d = B.load_yaml(ROOT / loc["output"])
            btn = [c for c in V.walk_cards(view(d, "climate")) if c.get("type") == "button"
                   and "air-conditioner" in str(c.get("icon"))]
            self.assertEqual(len(btn), 1, loc["code"])
            self.assertEqual(btn[0]["tap_action"]["navigation_path"], f"/{loc['url_base']}/v2-parents-room")

    def test_filter_reset_asks_first_in_every_locale(self):
        v2b = next(c for s in V2_BY["parents-room"]["sections"] for c in s["cards"]
                   if c.get("entity") == "button.bedroom_parents_room_ac_reset_filter")
        for code in [l["code"] for l in MAN["locales"]]:
            presses = [a for a in V.actions(view(dash(code), "parents-room")) if a.get("perform_action") == "button.press"]
            self.assertEqual(len(presses), 1, code)
            a = presses[0]
            self.assertEqual((a["perform_action"], a["target"]),
                             (v2b["tap_action"]["perform_action"], v2b["tap_action"]["target"]), code)
            self.assertTrue(a["confirmation"]["text"], code)
        self.assertEqual(V.unconfirmed_presses(view(dash("en"), "parents-room")), [])
        bad = copy.deepcopy(view(dash("en"), "parents-room"))      # positive control
        for a in V.actions(bad):
            a.pop("confirmation", None)
        self.assertTrue(V.unconfirmed_presses(bad))

    def test_timer_end_only_while_the_timer_is_on(self):
        c = next(c for c in tiles(view(dash("en"), "parents-room"))
                 if c["entity"] == "sensor.bedroom_parents_room_ac_timer_end_time")
        v2c = next(c for s in V2_BY["parents-room"]["sections"] for c in s["cards"] if c.get("type") == "conditional")
        self.assertEqual(c["visibility"], v2c["conditions"])

    def test_freezer_line_says_only_what_the_sensors_say(self):
        d = dash("en")
        o, s = "binary_sensor.g_monitor_freezer_p110m_overloaded", "switch.g_monitor_freezer_p110m"
        for st, want in [({o: "on", s: "on"}, "freezer circuit is overloaded"),
                         ({o: "off", s: "on"}, "Freezer plug on · not overloaded."),
                         ({o: "off", s: "off"}, "The freezer plug is switched off."),
                         ({o: "unavailable", s: "on"}, "Freezer monitor is not reporting."),
                         ({o: "unavailable", s: "unavailable"}, "Freezer monitor is not reporting.")]:
            out = render(d, "garage", dict(self.states, **st))
            self.assertIn(want, out, st)
            self.assertNotIn("running normally", out)

    def test_room_conditions_never_call_a_dark_room_quiet(self):
        out = render(dash("en"), "rooms", self.dark)
        self.assertNotIn("quiet", out)
        self.assertNotRegex(out, r"\d+(\.\d)?°")
        s = dict(self.states, **{"sensor.living_room_living_room_temperature": "unknown",
                                 "binary_sensor.sensor_group_motion": "on"})
        self.assertIn("**Dining** temperature No data · movement", render(dash("en"), "rooms", s))

    def test_counts_state_what_answered(self):
        s = dict(self.states, **{"switch.k_coffee_p100": "on", "switch.k_top_p100": "unavailable", "switch.k_bot_p100": "off"})
        self.assertIn("Bench plugs on **1** <small>2 of 3 reporting</small>", render(dash("en"), "kitchen", s))
        dark = render(dash("en"), "kitchen", self.dark)
        self.assertIn("Bench plugs on **No data**", dark)
        self.assertNotIn("**0**", dark)

    def test_emergency_note_makes_no_live_claim(self):
        for code in [l["code"] for l in MAN["locales"]]:
            out = render(dash(code), "parents-room", self.states)
            self.assertNotIn("currently not reporting", out, code)
        self.assertIn("Do not treat this page alone as proof", render(dash("en"), "parents-room", self.states))

    def test_tile_safety_catches_unsafe_room_changes(self):
        d = dash("en")

        def mutated(p, entity):
            v = copy.deepcopy(view(d, p))
            for c in V.walk_cards(v):
                if c.get("entity") == entity and c.get("type") == "tile":
                    c.update(tap_action={"action": "more-info"}, icon_tap_action={"action": "toggle"})
            return v
        for p, e in [("garage", "switch.g_monitor_freezer_p110m"), ("kitchen", "switch.k_coffee_p100"),
                     ("living-room", "switch.genio_power_board_with_usb_livingroom_socket_1"),
                     ("parents-room", "switch.bedroom_parents_room_ac_timer"),
                     ("dining", "select.smart_pet_feeder_night_vision"),
                     ("living-room", "switch.living_room_living_hue_hue_sensor_light_sensor_enabled")]:
            bad, prot = V.tile_safety(mutated(p, e), V2_BY, MAN["controls"], "casaray-v2", "casaray-v3")
            self.assertTrue(prot, e)
        allow = dict(MAN["controls"], **{"switch.g_monitor_freezer_p110m": {"v2_view": "garage"}})
        bad, _ = V.tile_safety(mutated("garage", "switch.g_monitor_freezer_p110m"), V2_BY, allow, "casaray-v2", "casaray-v3")
        self.assertTrue(any("protected class" in b for b in bad), "an allowlist entry cannot unlock a protected load")


class CoreBoards(unittest.TestCase):
    """CR-V3-19: House health, Alerts and People."""
    states, attrs = R.scenarios()["normal"]
    dark = R.scenarios()["dark"][0]
    P = ["person.raymond_du", "person.vinh_du", "person.ai_q_huang"]

    def people_out(self, **st):
        return render(dash("en"), "people", dict(self.states, **st))

    # ---- People: occupancy uncertainty
    def test_nobody_home_only_when_everyone_answered(self):
        a, b, c = self.P
        self.assertIn("**At home** Nobody is home", self.people_out(**{a: "not_home", b: "not_home", c: "not_home"}))
        out = self.people_out(**{a: "not_home", b: "unavailable", c: "unknown"})
        self.assertNotIn("Nobody is home", out)
        self.assertIn("Nobody confirmed at home", out)
        self.assertIn("2 not reporting a location", out)
        out = render(dash("en"), "people", self.dark)
        self.assertIn("Nobody is reporting a location", out)
        self.assertNotIn("Nobody is home", out)

    def test_silent_person_is_never_counted_away(self):
        a, b, c = self.P
        out = self.people_out(**{a: "home", b: "unavailable", c: "Work"})
        self.assertIn("**At home** Raymond", out)
        self.assertIn("**Away** Ai Q · 1 not reporting a location", out)
        self.assertNotIn("Vinh", out.split("**Away**")[1].split("\n")[0])

    def test_zone_zero_not_claimed_while_people_are_dark(self):
        a, b, c = self.P
        out = self.people_out(**{"zone.home": "0", a: "not_home", b: "unavailable", c: "not_home"})
        self.assertIn("**In the home zone** Not confirmed <small>1 of 3 people not reporting</small>", out)
        out = self.people_out(**{"zone.home": "0", a: "not_home", b: "not_home", c: "not_home"})   # positive control
        self.assertIn("**In the home zone** 0\n", out)
        self.assertIn("**In the home zone** No data", render(dash("en"), "people", self.dark))
        out = self.people_out(**{"zone.home": "2", a: "home", b: "unavailable", c: "unavailable"})
        self.assertNotIn("differs", out)        # no comparison while people are dark

    def test_zone_home_has_moved_to_native_people(self):
        row = MAN["migration"]["rooms"]["zone.home"]
        self.assertEqual((row["to"], row["status"]), ("people", "native"))
        self.assertIn("zone.home", B.entities_in(view(dash("en"), "people")))
        self.assertNotIn("zone.home", [c.get("entity") for c in tiles(view(dash("en"), "people"))],
                         "no raw zone tile: a bare tile would show a zero the people cannot back")

    def test_guest_mode_keeps_v2_toggle_only_through_the_allowlist(self):
        c = next(c for c in tiles(view(dash("en"), "people")) if c["entity"] == "input_boolean.guest_mode")
        self.assertEqual(C.effective_tile_actions(c), ("more-info", "toggle"))
        self.assertIn("input_boolean.guest_mode", MAN["controls"])
        unlisted = {k: v for k, v in MAN["controls"].items() if k != "input_boolean.guest_mode"}
        bad, _ = V.tile_safety(view(dash("en"), "people"), V2_BY, unlisted, "casaray-v2", "casaray-v3")
        self.assertTrue(any("guest_mode" in b and "not in manifest controls" in b for b in bad))

    # ---- Alerts
    def alerts(self, **st):
        outs = R.render_view(view(dash("en"), "alerts"), dict(self.states, **st), self.attrs)
        return outs

    def test_strip_and_lists_agree(self):
        W, D, M = ("binary_sensor.eero_wan_status", "binary_sensor.emergency_button_dad_cloud_connection",
                   "binary_sensor.emergency_button_mum_cloud_connection")
        scenarios = [{}, {W: "off", D: "weird", M: "unavailable", "sensor.front_door_battery": "9"},
                     {"binary_sensor.lph_se_dcd9_pump": "on", "binary_sensor.lg_fridge_door": "on"}]
        for st in scenarios + [None]:
            outs = R.render_view(view(dash("en"), "alerts"), self.dark if st is None else dict(self.states, **st), self.attrs)
            strip, lists = outs[2], outs[3:6]
            counts = [int(x) if x.isdigit() else None for x in re.findall(r"\*\*(\d+|No data)\*\*", strip)]
            self.assertEqual(len(counts), 3, strip)
            for n, body in zip(counts, lists):
                bullets = body.count("\n- **")
                self.assertEqual(bullets, n or 0, (st, strip, body))

    def test_emergency_buttons_are_never_cleared_by_silence_or_an_odd_state(self):
        D, M = "binary_sensor.emergency_button_dad_cloud_connection", "binary_sensor.emergency_button_mum_cloud_connection"
        crit = lambda **st: self.alerts(**st)[3]
        self.assertIn("Dad's emergency button cannot be confirmed", crit(**{D: "unavailable"}))
        self.assertIn("Dad's emergency button cannot be confirmed", crit(**{D: "weird"}))
        self.assertIn("Mum's emergency button is not connected", crit(**{M: "off"}))
        out = crit(**{D: "on", M: "on", "binary_sensor.eero_wan_status": "on",
                      "binary_sensor.g_monitor_freezer_p110m_overloaded": "off"})
        self.assertIn("nothing needs attention", out)                      # positive control
        self.assertNotIn("nothing needs attention", render(dash("en"), "alerts", self.dark))

    def test_alerts_has_no_state_changing_action(self):
        v = view(dash("en"), "alerts")
        self.assertEqual(list(V.actions(v)), [])
        self.assertEqual(tiles(v), [])

    # ---- House health
    def test_unverified_summary_sensors_are_retained_not_shown(self):
        rows = MAN["migration"]["house-health"]
        hh = B.entities_in(view(dash("en"), "house-health"))
        for e in ("sensor.house_status", "sensor.active_rooms_count", "sensor.house_lights_on"):
            self.assertEqual(rows[e]["status"], "retained")
            self.assertIn("CR-213", rows[e]["note"])
            self.assertNotIn(e, hh)
            self.assertIn(e, B.entities_in(view(dash("en"), "v2-house-health")))

    def test_system_updates_inert_air_con_firmware_as_v2(self):
        hh = {c["entity"]: c for c in tiles(view(dash("en"), "house-health"))}
        for e in ("update.home_assistant_core_update", "update.home_assistant_supervisor_update",
                  "update.home_assistant_operating_system_update"):
            self.assertEqual(C.effective_tile_actions(hh[e]), ("navigate", "none"), e)
            self.assertTrue(V.protected_setting(e))
        self.assertEqual(C.effective_tile_actions(hh["update.bedroom_parents_room_ac_firmware"]), ("more-info", "none"))

    def test_batteries_low_list_and_dark(self):
        out = render(dash("en"), "house-health", dict(self.states, **{"sensor.front_door_battery": "12",
                     "sensor.tapo_c425_north_wall_battery": "29", "sensor.gas_meter_pulse_sensor_battery": "unknown"}))
        self.assertIn("**Lowest: 12% (Front door)** · 14 of 15 reporting", out)
        self.assertIn("**Under 30%:** Front door, North wall", out)
        dark = render(dash("en"), "house-health", self.dark)
        self.assertIn("No battery is reporting a level.", dark)
        self.assertNotIn("**0**", dark)
        self.assertIn("Lights on **No data**", dark)

    def test_wiring_notes_render_as_a_list(self):
        md = [c["content"] for c in V.walk_cards(view(dash("en"), "house-health"))
              if c.get("type") == "markdown" and "Brightness average" in c.get("content", "")]
        self.assertEqual(len(md), 1)
        self.assertFalse(md[0].startswith("<small>"))
        self.assertEqual(md[0].count("\n- ") + md[0].startswith("- "), 4)

    # ---- confirmation coverage, every native view
    def test_every_native_button_press_asks_first(self):
        for code in [l["code"] for l in MAN["locales"]]:
            for p in MAN["native"]:
                self.assertEqual(V.unconfirmed_presses(view(dash(code), p)), [], f"{code}/{p}")
        bad = copy.deepcopy(view(dash("en"), "people"))         # positive control: a planted bare press
        bad["sections"][1]["cards"].append({"type": "button", "tap_action": {
            "action": "perform-action", "perform_action": "button.press", "target": {"entity_id": "button.x"}}})
        self.assertTrue(V.unconfirmed_presses(bad))


class Safety(unittest.TestCase):
    def test_no_device_action_on_climate_switch_or_siren(self):
        for p in MAN["native"]:
            for a in V.actions(view(dash("en"), p)):
                tgt = str(a.get("target")) + str(a.get("perform_action"))
                self.assertNotRegex(tgt, r"climate\.|switch\.|siren\.|camera\.", p)

    def test_all_lights_off_does_not_cut_bulb_power(self):
        acts = [a for a in V.actions(view(dash("en"), "home")) if a.get("perform_action") == "light.turn_off"]
        self.assertTrue(acts)
        for a in acts:
            self.assertNotIn("switch.", str(a["target"]))


class Locales(unittest.TestCase):
    def test_catalogues_are_subsets_with_matching_placeholders(self):
        for p in sorted((B.SRC / "i18n").glob("*.yaml")):
            cat = B.load_yaml(p)
            for k, v in cat.items():
                self.assertIn(k, EN, f"{p.name}: {k} not in en")
                ph = lambda s: sorted(re.findall(r"\{(\w+)\}", str(s)))
                self.assertEqual(ph(v), ph(EN[k]), f"{p.name}: {k} placeholders differ")

    def test_cantonese_and_khmer_are_complete(self):
        for code in ("yue", "km"):
            missing = set(EN) - set(B.load_yaml(B.SRC / "i18n" / f"{code}.yaml"))
            self.assertEqual(missing, set(), f"{code} missing {sorted(missing)}")

    def test_date_format_is_dd_mm_yy(self):
        text = (ROOT / "dashboards/casaray_v3.yaml").read_text(encoding="utf-8")
        native = "\n".join(yaml.safe_dump(view(dash('en'), p), allow_unicode=True) for p in MAN["native"])
        self.assertIn("%d/%m/%y", native)
        self.assertNotIn("%d/%m/%Y", native)
        self.assertTrue(text)


class Theme(unittest.TestCase):
    @staticmethod
    def lum(hexc):
        h = hexc.lstrip("#")
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    def ratio(self, a, b):
        la, lb = sorted([self.lum(a), self.lum(b)], reverse=True)
        return (la + 0.05) / (lb + 0.05)

    def test_wcag_aa_text_on_cards_both_modes(self):
        th = B.load_yaml(B.SRC / "themes" / "casaray_v3.yaml")["CasaRay V3"]["modes"]
        for mode, t in th.items():
            for fg in ("v3-text", "v3-text-2", "v3-accent", "v3-ok", "v3-alert", "v3-muted"):
                for bg in ("v3-card", "v3-page", "v3-elevated"):
                    r = self.ratio(t[fg], t[bg])
                    self.assertGreaterEqual(r, 4.5, f"{mode}: {fg} on {bg} = {r:.2f}")

    def test_native_views_use_the_v3_theme(self):
        for p in MAN["native"]:
            self.assertEqual(view(dash("en"), p)["theme"], MAN["theme"])


if __name__ == "__main__":
    unittest.main()
