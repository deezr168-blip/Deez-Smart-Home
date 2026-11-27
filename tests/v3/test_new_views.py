"""CasaRay V3 — regression tests for CR-V3-20 (new_views: pages with no V2
equivalent). DEVELOPMENT ONLY — NOT DEPLOYED.

    python3 -m unittest discover -s tests/v3 -v

Covers exactly what the owner's authorisation asked to be proven:
  - unchanged output when `new_views` is unconfigured (byte-identical to a
    build that never had the manifest key);
  - the two new pages emit exactly once per locale;
  - a duplicate path, a path with no source file, and a path colliding with
    an existing V2 view each fail the build clearly;
  - navigation into the new pages uses the right locale url_base.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v3"))

import yaml  # noqa: E402

import build_dashboard as B  # noqa: E402
import render_check as R  # noqa: E402
import validate_dashboard as V  # noqa: E402

MAN = B.load_yaml(B.SRC / "manifest.yaml")


def _patched_build(mutate):
    """Build once with `mutate(manifest_dict)` applied, manifest.yaml
    otherwise untouched on disk. Mirrors test_v3.py's own
    test_baseline_drift_refused pattern."""
    orig = B.load_yaml
    def fake(path, loader=B.DupKeyLoader):
        d = orig(path, loader)
        if Path(path).name == "manifest.yaml":
            d = copy.deepcopy(d)
            mutate(d)
        return d
    B.load_yaml = fake
    try:
        return B.build(write=False)
    finally:
        B.load_yaml = orig


def _views_by_path(parsed_dash):
    return {v["path"]: v for v in parsed_dash["views"]}


def _assert_same_views(case, got_by_path, want_by_path, msg_prefix=""):
    """Exact structural equality, one view at a time — not a text or
    line-subsequence comparison. A subsequence check (the original version
    of this test, before CR-V3-20 PR review) can pass even when a card was
    duplicated or an extra one inserted, because every original line is
    still present *somewhere*, just with extras interleaved; dict equality
    on the parsed structure cannot be fooled that way, since an inserted or
    duplicated card changes the `cards` list itself.
    `test_exact_comparison_rejects_duplicated_or_inserted_card` below proves
    this by running the same helper against a deliberately corrupted copy
    and showing it fails."""
    case.assertEqual(set(got_by_path), set(want_by_path), f"{msg_prefix}view set differs")
    for path in want_by_path:
        case.assertEqual(got_by_path[path], want_by_path[path], f"{msg_prefix}{path}")


class NewViewsEmission(unittest.TestCase):
    def test_empty_new_views_yields_unchanged_output(self):
        """Dropping `new_views` entirely must reproduce exactly what a
        pre-CR-V3-20 build would have written for every existing path: not
        merely 'every old line appears somewhere in the new output' (a
        subsequence check, which an inserted or duplicated card can defeat —
        see test_exact_comparison_rejects_duplicated_or_inserted_card below),
        but exact structural equality, view by view."""
        # Independently-derived expected view count for the non-new paths,
        # from the source inputs themselves rather than from running the
        # generator a second time: v2's own view list, plus one classic
        # (`v2-<path>`) copy per native rebuild. This is the count the
        # generator had before CR-V3-20 could exist at all.
        v2 = B.yaml.safe_load((ROOT / MAN["baseline"]["file"]).read_bytes())
        expected_count_without_new = len(v2["views"]) + len(MAN["native"])

        def strip(d):
            d.pop("new_views", None)
        stripped_outputs, stripped_report, _ = _patched_build(strip)

        for loc in MAN["locales"]:
            stripped_dash = B.yaml.safe_load(stripped_outputs[loc["output"]])
            self.assertEqual(len(stripped_dash["views"]), expected_count_without_new, loc["code"])
            paths = {v["path"] for v in stripped_dash["views"]}
            self.assertNotIn("weather", paths, loc["code"])
            self.assertNotIn("rubbish-collection", paths, loc["code"])
            self.assertEqual(stripped_report["locales"][loc["code"]]["views"],
                             expected_count_without_new, loc["code"])

        # Now the exact-equality half: every view the real (new_views-set)
        # build produces for a NON-new path must be byte-for-byte the same
        # parsed structure as the stripped build's — the two new pages are
        # the only permitted difference.
        real_outputs, _, _ = B.build(write=False)
        for loc in MAN["locales"]:
            stripped_dash = B.yaml.safe_load(stripped_outputs[loc["output"]])
            real_dash = B.yaml.safe_load(real_outputs[loc["output"]])
            want = _views_by_path(stripped_dash)
            got = {p: v for p, v in _views_by_path(real_dash).items()
                   if p not in ("weather", "rubbish-collection")}
            _assert_same_views(self, got, want, msg_prefix=f"[{loc['code']}] ")

    def test_exact_comparison_rejects_duplicated_or_inserted_card(self):
        """Proves the helper above has teeth: feed it a view with one card
        duplicated (the exact shape of bug CR-V3-20's review asked this
        suite to be able to catch) and confirm it fails, rather than passing
        because every original line still appears somewhere."""
        outputs, _, _ = B.build(write=False)
        dash = B.yaml.safe_load(outputs[MAN["locales"][0]["output"]])
        clean = _views_by_path(dash)
        home = copy.deepcopy(clean["home"])
        # Duplicate the first card of the first card-bearing section — a
        # stand-in for the exact bug class under review: an extra or
        # repeated card silently appended into an existing view.
        for sec in home["sections"]:
            if sec.get("cards"):
                sec["cards"] = [sec["cards"][0]] + sec["cards"]
                break
        else:
            self.fail("home view has no card-bearing section to corrupt")
        corrupted = dict(clean)
        corrupted["home"] = home
        with self.assertRaises(AssertionError):
            _assert_same_views(self, corrupted, clean)

    def test_new_pages_emit_exactly_once_per_locale(self):
        outputs, report, _ = B.build(write=False)
        for loc in MAN["locales"]:
            text = outputs[loc["output"]]
            for p in ("weather", "rubbish-collection"):
                self.assertEqual(text.count(f"path: {p}\n"), 1,
                                 f"[{loc['code']}] {p} should appear exactly once")

    def test_new_views_rows_marked_kind_new(self):
        _, report, _ = B.build(write=False)
        rows = {r["path"]: r for r in report["views"]}
        for p in ("weather", "rubbish-collection"):
            self.assertEqual(rows[p]["kind"], "new", p)
            self.assertIsNone(rows[p]["v2_equivalent"], p)


class NewViewsValidation(unittest.TestCase):
    def test_duplicate_new_views_path_rejected(self):
        with self.assertRaises(SystemExit) as c:
            _patched_build(lambda d: d.__setitem__("new_views", ["weather", "weather"]))
        self.assertIn("duplicate", str(c.exception))

    def test_new_views_missing_source_rejected(self):
        with self.assertRaises(SystemExit) as c:
            _patched_build(lambda d: d.__setitem__("new_views", ["no-such-page"]))
        self.assertIn("no source", str(c.exception))

    def test_new_views_collision_with_v2_path_rejected(self):
        with self.assertRaises(SystemExit) as c:
            _patched_build(lambda d: d.__setitem__("new_views", ["home"]))
        self.assertIn("collides", str(c.exception))

    def test_new_views_cannot_also_be_native(self):
        with self.assertRaises(SystemExit) as c:
            def mutate(d):
                # "home" is already in native:; forcing it into new_views
                # alongside (rather than instead of) must still be refused,
                # even though the v2-path collision check above would also
                # catch it — this exercises the native/new_views exclusivity
                # check specifically, in case one check is ever loosened.
                d["new_views"] = list(d.get("new_views", [])) + ["home"]
            _patched_build(mutate)
        self.assertTrue("collides" in str(c.exception) or "also listed in" in str(c.exception))


class NewViewsNavigation(unittest.TestCase):
    def test_new_page_links_resolve_to_locale_url_base(self):
        for loc in MAN["locales"]:
            d = B.load_yaml(ROOT / loc["output"])
            paths = {v["path"] for v in d["views"]}
            self.assertIn("weather", paths, loc["code"])
            self.assertIn("rubbish-collection", paths, loc["code"])
            for n in V.nav_paths(d):
                self.assertTrue(n.startswith(f"/{loc['url_base']}/"), n)
                self.assertIn(n.split("/")[2], paths, n)

    def test_home_more_boards_links_to_both_new_pages(self):
        d = B.load_yaml(ROOT / MAN["locales"][0]["output"])
        home = next(v for v in d["views"] if v["path"] == "home")
        targets = set()
        for s in home["sections"]:
            for c in s.get("cards", []):
                nav = c.get("tap_action", {}).get("navigation_path", "")
                if nav:
                    targets.add(nav.rsplit("/", 1)[-1])
        self.assertIn("weather", targets)
        self.assertIn("rubbish-collection", targets)


EN = B.load_yaml(B.SRC / "i18n" / "en.yaml")


def _weather_markdown(dash_dict):
    weather = next(v for v in dash_dict["views"] if v["path"] == "weather")
    for sec in weather["sections"]:
        for c in sec.get("cards", []):
            if c.get("type") == "markdown" and "weather.forecast_home" in c["content"]:
                return c["content"]
    return None


class WeatherHonesty(unittest.TestCase):
    def test_weather_detail_suppresses_stale_attributes_when_entity_dark(self):
        """CR-V3-20 (ChatGPT review on PR #21): weather_detail() used to read
        temperature/humidity straight off the entity's attributes, trusting
        that Home Assistant always clears them when the entity itself goes
        unavailable/unknown. That isn't guaranteed. This is the regression
        case: the entity's overall state is 'unavailable', but its
        attributes still carry plausible, valid-looking numbers — the card
        must show "No data" for both readings, never the stale figures,
        exactly as it already does for the condition word."""
        dash, _, _ = B.build(write=False)
        content = _weather_markdown(yaml.safe_load(dash[MAN["locales"][0]["output"]]))
        self.assertIsNotNone(content, "weather_detail's markdown card not found")
        env = R.env_for({"weather.forecast_home": "unavailable"},
                        {"weather.forecast_home": {"temperature": 21.3, "humidity": 55}})
        rendered = env.from_string(content).render()
        no_data = EN["s.no_data"]
        self.assertEqual(rendered.count(no_data), 2,
                         f"expected 'No data' for both temperature and humidity: {rendered!r}")
        self.assertNotIn("21.3", rendered)
        self.assertNotIn("55%", rendered)

    def test_weather_detail_shows_real_readings_when_available(self):
        """Positive control for the test above: with the entity genuinely
        reporting, the same two readings must show their real values, so the
        unavailable-case test is proving suppression, not a card that never
        shows numbers at all."""
        dash, _, _ = B.build(write=False)
        content = _weather_markdown(yaml.safe_load(dash[MAN["locales"][0]["output"]]))
        env = R.env_for({"weather.forecast_home": "sunny"},
                        {"weather.forecast_home": {"temperature": 21.3, "humidity": 55}})
        rendered = env.from_string(content).render()
        self.assertIn("21.3", rendered)
        self.assertIn("55%", rendered)
        self.assertNotIn(EN["s.no_data"], rendered)


if __name__ == "__main__":
    unittest.main()
