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
REBUILT = ("security", "network", "ray-bedroom", "guest-room")


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
            missing = v2e - B.entities_in(view(d, p))
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
                if V.protected_switch(e):
                    self.assertEqual(C.effective_tile_actions(c), ("navigate", "none"), f"{p}: {e}")
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
        acting = {c["entity"] for p in MAN["native"] for c in tiles(view(dash("en"), p))
                  if c["entity"].startswith("switch.") and V.acting(c)}
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

    def test_rooms_dark_say_no_data(self):
        for p in ("ray-bedroom", "guest-room"):
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
