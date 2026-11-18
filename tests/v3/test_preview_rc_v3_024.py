"""V3-024: the scope of the preview release candidate, pinned.  DEVELOPMENT ONLY.

    python3 -m unittest discover -s tests/v3 -v

PR #16 (cameras and layout) and the Home and navigation parts of PR #21 are
integrated; PR #21's Weather and Rubbish collection pages and its rubbish
reminder automation are not. These tests fail if a deferred page, a link to
one or the automation reaches this release, if a locale drifts from the
others, or if the camera surfaces gain a control. No network, no Home
Assistant.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import build_dashboard as B  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")
CODES = [x["code"] for x in MAN["locales"]]
DEFERRED = ("weather", "rubbish-collection")
EXPORT = {line.split("|")[0] for line in
          (ROOT / "docs/live/states_export_2026-09-05.txt").read_text(encoding="utf-8").splitlines() if "|" in line}
CAMS = ["camera.front_door_live_view", "camera.tapo_c425_north_wall_hd_stream_direct",
        "camera.tapo_c420_east_wall_hd_stream_direct", "camera.tapo_c420_south_wall_hd_stream_direct",
        "camera.tapo_c200_stockroom_hd_stream_direct", "camera.smart_pet_feeder"]


def dash(code):
    loc = next(x for x in MAN["locales"] if x["code"] == code)
    return B.load_yaml(ROOT / loc["output"])


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def view(d, path):
    return next(v for v in d["views"] if v["path"] == path)


class DeferredScope(unittest.TestCase):
    def test_weather_and_rubbish_pages_are_not_in_this_release(self):
        self.assertFalse(MAN.get("new_views"), "new_views belongs to PR #21's deferred pages")
        for p in DEFERRED:
            self.assertFalse((B.SRC / "views" / f"{p}.yaml").exists(), p)
        for code in CODES:
            d = dash(code)
            paths = [v["path"] for v in d["views"]]
            for p in DEFERRED:
                self.assertNotIn(p, paths, code)
            links = [n.get("navigation_path", "") for n in walk(d)]
            for p in DEFERRED:
                self.assertFalse([x for x in links if x.rstrip("/").endswith("/" + p)], (code, p))

    def test_rubbish_reminder_automation_is_not_installed(self):
        self.assertFalse((ROOT / "docs/casaray-v3/proposals/rubbish_reminder_automation.yaml").exists())
        for f in (ROOT / "packages").glob("**/*.yaml"):
            self.assertNotRegex(f.read_text(encoding="utf-8").lower(), r"rubbish|bin collection",
                                f"{f.relative_to(ROOT)} must not carry the deferred reminder")


class FourLocales(unittest.TestCase):
    def test_every_locale_has_the_same_views_and_the_same_entities(self):
        pat = re.compile(r"\b[a-z_]+\.[a-z0-9_]+\b")
        ref = dash("en")
        ref_paths = [v["path"] for v in ref["views"]]
        ref_ents = {v["path"]: {m for m in pat.findall(str(v)) if m in EXPORT} for v in ref["views"]}
        for code in CODES:
            d = dash(code)
            self.assertEqual([v["path"] for v in d["views"]], ref_paths, code)
            for v in d["views"]:
                self.assertEqual({m for m in pat.findall(str(v)) if m in EXPORT}, ref_ents[v["path"]],
                                 (code, v["path"]))


class CameraSafety(unittest.TestCase):
    def test_camera_ids_are_the_verified_six(self):
        for code in CODES:
            d = dash(code)
            used = {n["entity"] for n in walk(d) if str(n.get("entity", "")).startswith("camera.")}
            self.assertTrue(used <= EXPORT, (code, sorted(used - EXPORT)))
            pics = [n["entity"] for n in walk(view(d, "cameras")) if n.get("type") == "picture-entity"]
            self.assertEqual(pics, CAMS, code)

    def test_camera_surfaces_change_nothing(self):
        """Cameras and Home's front-door slot: a tap opens the camera's own
        dialog or navigates; nothing performs an action, and every switch on
        Cameras is read-only (its icon does nothing)."""
        for code in CODES:
            d = dash(code)
            cams = view(d, "cameras")
            for n in walk(cams):
                for key in ("tap_action", "hold_action", "double_tap_action", "icon_tap_action"):
                    act = (n.get(key) or {}).get("action")
                    self.assertIn(act, (None, "none", "more-info", "navigate"), (code, n.get("entity"), key))
                if str(n.get("entity", "")).startswith("switch."):
                    self.assertEqual((n.get("icon_tap_action") or {}).get("action"), "none", (code, n["entity"]))
            for n in walk(view(d, "home")):
                if n.get("type") == "picture-entity":
                    self.assertEqual(n["tap_action"], {"action": "more-info"}, code)
                    self.assertEqual(n["hold_action"], {"action": "none"}, code)


if __name__ == "__main__":
    unittest.main()
