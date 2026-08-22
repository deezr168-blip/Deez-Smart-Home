#!/usr/bin/env python3
"""Tests for the snapshot tooling. Run: python3 scripts/test_snapshot_tools.py

Uses plain asserts and unittest so it runs with no third-party dependencies.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import diff_snapshots  # noqa: E402
from ha_snapshot import load, load_context, parse  # noqa: E402

SNAPSHOT = REPO / "snapshots" / "2026-08-23-assist-context.json"

SAMPLE = """Live Context: An overview of the areas and the devices in this smart home:
- names: Kitchen Lamp
  domain: light
  state: 'on'
  areas: Kitchen
  attributes:
    brightness: '73'
- names: Freezer Plug
  domain: switch
  state: unavailable
  areas: Garage
- names: Odd &quot;Quoted&quot; Name
  domain: sensor
  state: '12.5'
  areas: Garage
  attributes:
    unit_of_measurement: kWh
    device_class: energy
- names: Orphan
  domain: sensor
  state: unknown
"""


def write(tmp: Path, name: str, context: str) -> Path:
    path = tmp / name
    path.write_text(json.dumps({"success": True, "result": context}), encoding="utf-8")
    return path


class TestParse(unittest.TestCase):
    def test_parses_fields_attributes_and_entities_without_area(self):
        entities = parse(SAMPLE)
        self.assertEqual(len(entities), 4)

        lamp, plug, odd, orphan = entities
        self.assertEqual(lamp["name"], "Kitchen Lamp")
        self.assertEqual(lamp["domain"], "light")
        self.assertEqual(lamp["state"], "on", "surrounding quotes must be stripped")
        self.assertEqual(lamp["area"], "Kitchen")
        self.assertEqual(lamp["attrs"]["brightness"], "73")

        self.assertEqual(plug["state"], "unavailable")
        self.assertEqual(odd["name"], 'Odd "Quoted" Name', "HTML entities decoded")
        self.assertEqual(odd["attrs"]["device_class"], "energy")
        self.assertEqual(orphan["area"], "", "missing area becomes empty string")
        self.assertEqual(orphan["attrs"], {})

    def test_accepts_plain_text_and_wrapped_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            wrapped = write(tmp, "wrapped.json", SAMPLE)
            plain = tmp / "plain.txt"
            plain.write_text(SAMPLE, encoding="utf-8")
            self.assertEqual(load_context(wrapped), load_context(plain))

    def test_rejects_a_failed_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(json.dumps({"success": False}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                load_context(path)

    def test_rejects_a_snapshot_with_no_entities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write(Path(tmpdir), "empty.json", "Live Context: nothing here\n")
            with self.assertRaises(SystemExit):
                load(path)


class TestDiff(unittest.TestCase):
    def run_diff(self, before: str, after: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            args = [str(write(tmp, "a.json", before)), str(write(tmp, "b.json", after))]
            import io
            import contextlib
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = diff_snapshots.main(args)
            return code, buffer.getvalue()

    def test_no_changes_between_identical_snapshots(self):
        code, out = self.run_diff(SAMPLE, SAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("Became unavailable (0)", out)
        self.assertIn("Recovered (0)", out)

    def test_newly_unavailable_entity_is_reported_and_fails(self):
        after = SAMPLE.replace("  state: 'on'\n  areas: Kitchen",
                               "  state: unavailable\n  areas: Kitchen")
        code, out = self.run_diff(SAMPLE, after)
        self.assertEqual(code, 1, "a regression must be a non-zero exit")
        self.assertIn("Became unavailable (1)", out)
        self.assertIn("Kitchen Lamp", out)

    def test_recovery_is_reported_and_passes(self):
        after = SAMPLE.replace("  state: unavailable\n  areas: Garage",
                               "  state: 'off'\n  areas: Garage")
        code, out = self.run_diff(SAMPLE, after)
        self.assertEqual(code, 0)
        self.assertIn("Recovered (1)", out)
        self.assertIn("Freezer Plug", out)

    def test_disappeared_entity_fails_but_new_entity_does_not(self):
        trimmed = SAMPLE.replace("- names: Orphan\n  domain: sensor\n  state: unknown\n", "")
        code, out = self.run_diff(SAMPLE, trimmed)
        self.assertEqual(code, 1)
        self.assertIn("Disappeared (1)", out)

        code, out = self.run_diff(trimmed, SAMPLE)
        self.assertEqual(code, 0, "a new entity is not a regression")
        self.assertIn("New entities (1)", out)

    def test_ordinary_state_change_is_hidden_by_default(self):
        after = SAMPLE.replace("  state: '12.5'", "  state: '99.9'")
        code, out = self.run_diff(after, SAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("1 ordinary state changes hidden", out)

    def test_duplicate_names_are_tracked_independently(self):
        """Duplicate friendly names are real here (health report finding 3).

        One copy going unavailable must be detected even though the other copy
        keeps the same identity key.
        """
        dup = SAMPLE + (
            "- names: Kitchen Lamp\n  domain: light\n  state: 'on'\n  areas: Kitchen\n"
        )
        after = dup.replace(
            "- names: Kitchen Lamp\n  domain: light\n  state: 'on'\n  areas: Kitchen\n",
            "- names: Kitchen Lamp\n  domain: light\n  state: unavailable\n  areas: Kitchen\n",
            1,
        )
        code, out = self.run_diff(dup, after)
        self.assertEqual(code, 1)
        self.assertIn("Became unavailable (1)", out)


class TestAgainstRealSnapshot(unittest.TestCase):
    def test_committed_snapshot_matches_the_documented_figures(self):
        entities = load(SNAPSHOT)
        self.assertEqual(len(entities), 431)
        unavailable = sum(1 for e in entities if e["state"] == "unavailable")
        self.assertEqual(unavailable, 76)

    def test_inventory_regenerates_identically(self):
        """docs/entity_inventory.md must match what the generator produces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "inventory.md"
            subprocess.run(
                [sys.executable, str(SCRIPTS / "build_entity_inventory.py"),
                 str(SNAPSHOT), "-o", str(out)],
                check=True, capture_output=True, cwd=REPO,
            )
            committed = (REPO / "docs" / "entity_inventory.md").read_text(encoding="utf-8")
            self.assertEqual(out.read_text(encoding="utf-8"), committed,
                             "docs/entity_inventory.md is stale — regenerate it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
