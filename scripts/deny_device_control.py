#!/usr/bin/env python3
"""PreToolUse guard: refuse Home Assistant tools that physically act on the house.

Claude has configuration-maintenance authority over this repository, not
household-control authority. Read-only tools (GetLiveContext, GetDateTime,
todo_get_items) are needed to verify entities and are allowed; anything that
moves a real device is denied here.

Enforcement is by TOOL NAME, deliberately, not by MCP server name. The Home
Assistant connector's server id has already changed once within a single
project ("Home_Assistant" -> a UUID), so a rule pinned to a server name would
silently stop protecting anything. Matching the Hass* action verb survives
that.

Reads the hook payload on stdin, prints a deny decision when the tool is a
device actuator, and stays silent otherwise (silence = allow).
"""

import json
import re
import sys

# Every Hass* tool that changes physical state. Anchored so GetLiveContext,
# GetDateTime and todo_get_items are unaffected.
BLOCKED = re.compile(
    r"(?:^|__)("
    r"HassTurnOn|HassTurnOff"
    r"|HassLightSet"
    r"|HassClimateSetTemperature"
    r"|HassFanSetSpeed"
    r"|HassSetPosition|HassStopMoving"
    r"|HassSetVolume|HassSetVolumeRelative"
    r"|HassMediaPause|HassMediaUnpause|HassMediaNext|HassMediaPrevious"
    r"|HassMediaSearchAndPlay|HassMediaPlayerMute|HassMediaPlayerUnmute"
    r"|HassBroadcast"
    r"|HassCancelAllTimers"
    r"|HassListAddItem|HassListCompleteItem|HassListRemoveItem"
    r")$"
)

REASON = (
    "Blocked by the Deez Smart Home maintenance framework: this tool physically "
    "operates a device in the house. Claude holds configuration-maintenance "
    "authority here, not household-control authority. Ask the owner to perform "
    "or approve this action. (scripts/deny_device_control.py)"
)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Never fail open on a malformed payload we cannot classify, but also
        # never wedge the session: say nothing and let normal permissions apply.
        return 0

    tool = str(payload.get("tool_name", ""))
    if BLOCKED.search(tool):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
