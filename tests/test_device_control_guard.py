#!/usr/bin/env python3
"""CR-T02: offline tests for the Home Assistant PreToolUse guard. No device calls."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "deny_device_control.py"
SETTINGS = ROOT / ".claude" / "settings.json"

class DeviceControlGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        cls.matcher = re.compile(cls.settings["hooks"]["PreToolUse"][0]["matcher"])

    def decision(self, name):
        p = subprocess.run([sys.executable, str(GUARD)], input=json.dumps({"tool_name": name}),
                           capture_output=True, text=True, check=True, timeout=5)
        return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else "allow"

    def test_play_media_is_denied_and_hook_activated(self):
        for name in ("mcp__Home_Assistant__media_player__play_media",
                     "mcp__changed_server_id__media_player__play_media",
                     "media_player__play_media"):
            with self.subTest(name=name):
                self.assertIsNotNone(self.matcher.search(name))
                self.assertEqual(self.decision(name), "deny")

    def test_existing_hass_controls_remain_denied(self):
        names = ("HassTurnOn", "HassTurnOff", "HassLightSet", "HassClimateSetTemperature",
                 "HassFanSetSpeed", "HassSetPosition", "HassStopMoving",
                 "HassSetVolume", "HassSetVolumeRelative", "HassMediaPause",
                 "HassMediaUnpause", "HassMediaNext", "HassMediaPrevious",
                 "HassMediaSearchAndPlay", "HassMediaPlayerMute", "HassMediaPlayerUnmute",
                 "HassBroadcast", "HassCancelAllTimers", "HassListAddItem",
                 "HassListCompleteItem", "HassListRemoveItem")
        for action in names:
            name = "mcp__Home_Assistant__" + action
            with self.subTest(name=name):
                self.assertIsNotNone(self.matcher.search(name))
                self.assertEqual(self.decision(name), "deny")

    def test_read_only_and_near_miss_names_not_denied(self):
        for name in ("mcp__Home_Assistant__HassGetLiveContext",
                     "mcp__Home_Assistant__HassGetDateTime",
                     "mcp__Home_Assistant__todo_get_items",
                     "mcp__Home_Assistant__media_player__play_media_get",
                     "mcp__Home_Assistant__media_player__play_media_extra",
                     "mcp__Other__play_media", "mcp__Other__unrelated"):
            with self.subTest(name=name):
                self.assertEqual(self.decision(name), "allow")

    def test_other_permissions_untouched(self):
        deny = self.settings["permissions"]["deny"]
        self.assertEqual(len(deny), 27)
        self.assertIn("Bash(git push --force*)", deny)

if __name__ == "__main__":
    unittest.main()
