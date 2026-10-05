"""Regression tests for the CasaRay repository.

Offline, stdlib `unittest` plus PyYAML and Jinja2 (what the gates already
need). Run with:

    python3 -m unittest discover -s tests -v

These are not a second copy of `scripts/ha_validate.sh`. The gates answer "is
this change safe to push"; these pin the behaviour of the tooling and the
properties the project decided it must never lose -- so a change to a gate, to
the audit, or to the dashboard cannot quietly weaken one of them.

Nothing here can see the running Home Assistant. A green run means the
repository is internally consistent, not that a card renders.
"""

import ast
import glob
import json
import os
import re
import subprocess
import sys
import unittest

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import audit_casaray as audit  # noqa: E402
import reconcile_entities as rec  # noqa: E402

DASH = os.path.join(ROOT, "dashboards", "casaray_v2.yaml")
RENDER = os.path.join(ROOT, ".claude", "skills", "improve-system", "scripts",
                      "render_cards.py")


def run(*cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def load():
    with open(DASH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


class DashboardStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dash = load()
        cls.views = cls.dash["views"]

    def test_view_paths_unique_and_present(self):
        paths = [v.get("path") for v in self.views]
        self.assertTrue(all(paths), "every view needs a path")
        self.assertEqual(len(paths), len(set(paths)), "duplicate view path")
        for must in ("home", "rooms", "security", "energy", "bills",
                     "cameras", "network", "house-health", "alerts"):
            self.assertIn(must, paths)

    def test_no_badges_block(self):
        # DR-011: badges render above the top bar. check 15b gates it too.
        for v in self.views:
            self.assertNotIn("badges", v, f"{v['path']} has a badges block")

    def test_every_view_is_two_columns_or_fewer(self):
        # DR-013: the wall iPad resolves two. Do not raise without a photo.
        for v in self.views:
            self.assertLessEqual(v.get("max_columns", 1), 2, v["path"])

    def test_navigation_targets_exist(self):
        ids = {v["path"] for v in self.views}
        bad = []

        def scan(n):
            for k in ("navigation_path", "path"):
                val = n.get(k)
                if isinstance(val, str):
                    m = re.match(r"/casaray-v2/([a-z0-9-]+)", val)
                    if m and m.group(1) not in ids:
                        bad.append(val)
        walk(self.views, scan)
        self.assertEqual(bad, [])

    def test_only_one_custom_card_type(self):
        custom = set()

        def scan(n):
            t = n.get("type")
            if isinstance(t, str) and t.startswith("custom:"):
                custom.add(t)
        walk(self.views, scan)
        self.assertEqual(custom, {"custom:webrtc-camera"})

    def test_language_toggle_is_the_only_bilingual_switch(self):
        # Every visibility condition on the dashboard keys off one helper or
        # another entity -- but the *language* conditions must use this one.
        conds = []

        def scan(n):
            for c in n.get("visibility") or []:
                if isinstance(c, dict) and c.get("condition") == "state":
                    conds.append(c.get("entity"))
        walk(self.views, scan)
        self.assertGreater(len(conds), 100)
        self.assertIn("input_boolean.chinese_dashboard", set(conds))

    def test_english_headings_survive_a_dead_toggle(self):
        # The English card uses state_not 'on', so it still shows when the
        # helper is unavailable (as it is after the 25/09 loss).
        for v in self.views:
            def scan(n, v=v):
                if n.get("type") != "heading":
                    return
                for c in n.get("visibility") or []:
                    if c.get("entity") != "input_boolean.chinese_dashboard":
                        continue
                    text = str(n.get("heading", ""))
                    if re.search(r"[一-鿿]", text):
                        self.assertEqual(c.get("state"), "on", (v["path"], text))
                    else:
                        self.assertEqual(c.get("state_not"), "on", (v["path"], text))
            walk(v, scan)

    def test_house_health_reports_setup_status(self):
        hh = next(v for v in self.views if v["path"] == "house-health")
        text = yaml.safe_dump(hh, allow_unicode=True)
        self.assertIn("Setup status", text)
        self.assertIn("设置状态", text)
        self.assertIn("input_boolean.casaray_auto_deploy", text)

    def test_no_sentinel_float_fallbacks(self):
        raw = open(DASH, encoding="utf-8").read()
        body = "\n".join(l for l in raw.split("\n")
                         if not l.lstrip().startswith("#"))
        self.assertIsNone(re.search(r"float\((0|100|9999)\)", body),
                          "a sentinel renders as a real measurement")


class Gates(unittest.TestCase):
    def test_dashboard_check_passes(self):
        r = run(sys.executable, "scripts/dashboard_check.py",
                "dashboards/casaray_v2.yaml")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_entity_reconciliation_passes(self):
        r = run(sys.executable, "scripts/reconcile_entities.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fixture_matches_export(self):
        r = run(sys.executable, "scripts/build_render_fixture.py", "--check")
        self.assertIn(r.returncode, (0, 2), r.stdout + r.stderr)


class Audit(unittest.TestCase):
    def setUp(self):
        self.live = {
            "switch.a": ("Plug", "Kitchen", "ok"),
            "switch.a_2": ("Plug", "Kitchen", "unavailable"),
            "switch.b": ("Heater", "", "unavailable"),
            "scene.s": ("Scene", "", "unknown"),
            "sensor.u": ("Thing", "", "unknown"),
            "input_boolean.h": ("Helper", "", "ok"),
            "input_boolean.h_unk": ("Helper2", "", "unknown"),
        }
        self.groups = audit.twins(self.live)

    def c(self, eid, defined=()):
        return audit.classify(eid, self.live, self.groups, set(defined))[0]

    def test_missing_entity_is_confirmed_broken(self):
        self.assertEqual(self.c("switch.nope"), "confirmed_broken")

    def test_stale_map_is_confirmed_broken(self):
        stale = next(iter(rec.STALE))
        live = dict(self.live)
        live[stale] = ("X", "", "ok")
        self.assertEqual(audit.classify(stale, live, audit.twins(live), set())[0],
                         "confirmed_broken")

    def test_dead_twin_is_likely_broken(self):
        self.assertEqual(self.c("switch.a_2"), "likely_broken")

    def test_live_twin_is_working(self):
        self.assertEqual(self.c("switch.a"), "working")

    def test_unavailable_without_twin_needs_a_live_check(self):
        self.assertEqual(self.c("switch.b"), "live_check")

    def test_unknown_scene_is_stateless_not_a_problem(self):
        self.assertEqual(self.c("scene.s"), "stateless")

    def test_unknown_sensor_needs_a_live_check(self):
        self.assertEqual(self.c("sensor.u"), "live_check")

    def test_helper_not_defined_in_git_needs_a_live_check(self):
        self.assertEqual(self.c("input_boolean.h"), "live_check")

    def test_helper_defined_in_git_is_working(self):
        self.assertEqual(self.c("input_boolean.h", {"input_boolean.h"}),
                         "working")

    def test_git_defined_entity_missing_from_export_is_not_broken(self):
        self.assertEqual(
            self.c("input_boolean.new", {"input_boolean.new"}), "live_check")

    def test_repository_has_no_confirmed_broken_references(self):
        a = audit.audit()
        broken = [e for e, i in a["entities"].items()
                  if i["class"] == "confirmed_broken"]
        self.assertEqual(broken, [])
        self.assertEqual(a["bad_nav"], [])
        self.assertEqual(a["unreachable_views"], [])
        self.assertIs(a["theme_declared"], True)

    def test_committed_report_is_current(self):
        r = run(sys.executable, "scripts/audit_casaray.py", "--check")
        self.assertEqual(r.returncode, 0,
                         "run python3 scripts/audit_casaray.py\n" + r.stderr)


class Packages(unittest.TestCase):
    # Actions an unattended automation in this repository must never take.
    FORBIDDEN = re.compile(
        r"\b(lock\.(unlock|open)|cover\.(open|close)_cover|"
        r"alarm_control_panel\.alarm_(disarm|arm)\w*|"
        r"homeassistant\.(restart|stop)|hassio\.(host|addon)_\w+|"
        r"camera\.(turn_off|disable_motion_detection)|"
        r"switch\.turn_off)\b")

    @classmethod
    def setUpClass(cls):
        cls.files = sorted(glob.glob(os.path.join(ROOT, "packages", "*.yaml")))

    def load(self, path):
        with open(path, encoding="utf-8") as fh:
            return yaml.load(fh, Loader=rec._Loose)

    def test_packages_parse(self):
        self.assertTrue(self.files)
        for f in self.files:
            self.assertIsInstance(self.load(f), dict, f)

    def test_package_defined_entities(self):
        d = rec.package_defined()
        self.assertIn("input_boolean.casaray_auto_deploy", d)
        self.assertIn("sensor.casaray_low_batteries", d)

    def test_every_automation_has_alias_and_mode(self):
        for f in self.files:
            for a in self.load(f).get("automation") or []:
                self.assertIn("alias", a, f)
                self.assertIn("mode", a, a.get("alias"))

    def test_no_automation_takes_a_physical_or_security_action(self):
        for f in self.files:
            body = "\n".join(l for l in open(f, encoding="utf-8")
                             if not l.lstrip().startswith("#"))
            self.assertIsNone(self.FORBIDDEN.search(body), f)

    def test_nothing_restarts_home_assistant(self):
        for f in self.files:
            body = open(f, encoding="utf-8").read()
            self.assertNotRegex(body, r"(?m)^\s*-?\s*action:\s*homeassistant\.restart")


class Proposals(unittest.TestCase):
    """proposals/ holds changes that are written but deliberately inert."""
    PATH = os.path.join(ROOT, "proposals", "casaray_helper_booleans.proposed.yaml")

    def test_boolean_proposal_matches_the_export_and_packages(self):
        with open(self.PATH, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        live = rec.load_export(rec.EXPORT)
        defined = rec.package_defined()
        self.assertEqual(set(doc), {"input_boolean"}, "booleans only: no "
                         "other helper type has settings we can know")
        for key, cfg in doc["input_boolean"].items():
            eid = f"input_boolean.{key}"
            self.assertIn(eid, live, eid)
            self.assertNotIn(eid, defined, f"{eid} already defined in packages/")
            self.assertEqual(set(cfg), {"name"}, f"{key}: no invented settings")

    def test_proposals_are_not_on_the_gates_path(self):
        # package_defined reads packages/ only; a proposal there would be
        # counted as defined and silently legitimise cards that read it.
        self.assertNotIn("input_boolean.chinese_dashboard",
                         rec.package_defined())
        self.assertFalse(os.path.exists(os.path.join(
            ROOT, "packages", os.path.basename(self.PATH))))


class Scripts(unittest.TestCase):
    # Scripts known to fail `sh -n`, each tracked in docs/OWNER_ACTION_QUEUE.md.
    # ha_validate.sh carries a dead, duplicated copy of its own body after its
    # final `exit 1` (lines 182-316 on 18a4e5d). It runs correctly because bash
    # parses lazily and exits first, but `bash -n` rejects it.
    KNOWN_SYNTAX_ISSUES = {"ha_validate.sh"}

    def _parses(self, f):
        with open(f, encoding="utf-8") as fh:
            first = fh.readline()
        sh = "bash" if "bash" in first else "sh"
        return subprocess.run([sh, "-n", f], capture_output=True, text=True)

    def test_shell_scripts_parse(self):
        for f in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.sh"))):
            if os.path.basename(f) in self.KNOWN_SYNTAX_ISSUES:
                continue
            r = self._parses(f)
            self.assertEqual(r.returncode, 0, f"{f}: {r.stderr}")

    def test_known_syntax_issues_are_still_tracked(self):
        # If a known issue is fixed, delete it from KNOWN_SYNTAX_ISSUES. If it
        # is still broken it must stay on the owner's queue, not be forgotten.
        queue = open(os.path.join(ROOT, "docs", "OWNER_ACTION_QUEUE.md"),
                     encoding="utf-8").read()
        for name in self.KNOWN_SYNTAX_ISSUES:
            f = os.path.join(ROOT, "scripts", name)
            if self._parses(f).returncode != 0:
                self.assertIn(name, queue, f"{name} is broken and untracked")
            else:
                self.fail(f"{name} now parses -- remove it from "
                          "KNOWN_SYNTAX_ISSUES")

    def test_python_scripts_compile(self):
        files = glob.glob(os.path.join(ROOT, "scripts", "*.py")) + glob.glob(
            os.path.join(ROOT, "tests", "*.py"))
        for f in sorted(files):
            with open(f, encoding="utf-8") as fh:
                ast.parse(fh.read(), f)

    def test_no_secret_shaped_literals_in_tracked_text(self):
        pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{30,}\.|"
                         r"-----BEGIN [A-Z ]*PRIVATE KEY-----)")
        tracked = run("git", "ls-files").stdout.split("\n")
        for f in tracked:
            p = os.path.join(ROOT, f)
            if not f or not os.path.isfile(p) or f.endswith((".png", ".jpg")):
                continue
            try:
                text = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            self.assertIsNone(pat.search(text), f)


class ReviewPacket(unittest.TestCase):
    def test_packet_builds_and_asks_the_six_questions(self):
        r = run(sys.executable, "scripts/review_packet.py", "--no-gates",
                "--base", "HEAD")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("evidence, not argument", r.stdout)
        self.assertIn("Was any gate, test or check weakened", r.stdout)
        self.assertIn("NOT RUN", r.stdout)

    def test_unknown_base_is_refused(self):
        r = run(sys.executable, "scripts/review_packet.py", "--base", "no/such")
        self.assertEqual(r.returncode, 2)


class Ci(unittest.TestCase):
    def test_workflow_parses_and_runs_the_gates(self):
        wf = yaml.safe_load(open(os.path.join(
            ROOT, ".github", "workflows", "ci.yml"), encoding="utf-8"))
        text = yaml.safe_dump(wf)
        for needle in ("ha_validate.sh", "unittest discover",
                       "audit_casaray.py --check --strict", "render_cards.py"):
            self.assertIn(needle, text)
        self.assertEqual(wf["permissions"], {"contents": "read"})

    def test_ci_requirements_pinned_to_what_the_tools_import(self):
        reqs = open(os.path.join(ROOT, "requirements-ci.txt")).read().lower()
        self.assertIn("pyyaml", reqs)
        self.assertIn("jinja2", reqs)


@unittest.skipUnless(os.path.exists(RENDER), "render_cards.py not present")
class DarkInstance(unittest.TestCase):
    """What the markdown cards say when nothing is answering."""

    @classmethod
    def setUpClass(cls):
        r = run(sys.executable, RENDER, "--all")
        cls.rc, cls.out = r.returncode, r.stdout + r.stderr

    def test_every_card_renders(self):
        self.assertEqual(self.rc, 0, self.out[-2000:])
        self.assertNotRegex(self.out, r"Traceback|TemplateError|UndefinedError")

    def test_dark_pass_never_reassures(self):
        # CLAUDE.md: never let a card assert a state it cannot see. These are
        # whole-card phrases a dark instance must not produce.
        # "Nothing is waiting to be paid" and "Not set up" were both rendered
        # for six unavailable bill helpers (found 2026-10-05): the first
        # claims a measurement nobody made, the second blames the owner for
        # a helper that is simply not answering.
        bad = re.compile(r"\b(all clear|all closed|all secure|everything is "
                         r"(fine|normal|ok)|no problems|up to date|"
                         r"nothing is waiting to be paid|not set up|"
                         r"no amount entered)\b", re.I)
        offenders = []
        block = ""
        for line in self.out.split("\n"):
            if line.startswith("=== "):
                block = line
            if "dark/EN" in line and bad.search(line):
                offenders.append((block, line.strip()[:120]))
        self.assertEqual(offenders, [])

    def test_setup_status_names_the_cause_when_helpers_are_dark(self):
        self.assertRegex(self.out, r"dark/EN\s+\d of \d helper groups are not "
                                   r"fully answering")
        self.assertIn("没有完全响应", self.out)


if __name__ == "__main__":
    unittest.main()
