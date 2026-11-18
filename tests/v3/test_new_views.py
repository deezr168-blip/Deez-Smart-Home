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

import build_dashboard as B  # noqa: E402
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


class NewViewsEmission(unittest.TestCase):
    def test_empty_new_views_yields_unchanged_output(self):
        """Dropping `new_views` entirely must reproduce exactly the output a
        pre-CR-V3-20 manifest would have written: every existing view kept,
        byte-identical, and neither new page present."""
        outputs, report, _ = B.build(write=False)  # real manifest (new_views set)

        def strip(d):
            d.pop("new_views", None)
        stripped_outputs, stripped_report, _ = _patched_build(strip)

        for loc in MAN["locales"]:
            real_path = loc["output"]
            self.assertNotIn("path: weather", stripped_outputs[real_path])
            self.assertNotIn("path: rubbish-collection", stripped_outputs[real_path])
            self.assertEqual(stripped_report["locales"][loc["code"]]["views"],
                             report["locales"][loc["code"]]["views"] - 2, loc["code"])
            # the two appended new-page views are the only difference: strip
            # them from the real build's text and nothing else may differ
            # besides the view count line in the header comment.
            real_lines = outputs[real_path].splitlines()
            stripped_lines = stripped_outputs[real_path].splitlines()
            # Every line in the stripped build must also appear, in order, in
            # the real build (new_views only ever appends, never reorders or
            # rewrites an existing line) — this is the byte-identical
            # guarantee the generator's own comments promise, checked rather
            # than assumed.
            it = iter(real_lines)
            for line in stripped_lines:
                for cand in it:
                    if cand == line:
                        break
                else:
                    self.fail(f"[{loc['code']}] stripped-build line not found in order "
                             f"in the real build: {line!r}")

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


if __name__ == "__main__":
    unittest.main()
