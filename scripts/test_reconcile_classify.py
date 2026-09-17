#!/usr/bin/env python3
"""Regression test for reconcile_entities.classify().

The classifier decides which references are faults and which are noise, so a
mistake here does not break the build -- it makes the build lie. The one that
matters most is BENIGN_UNKNOWN_DOMAINS: `unknown` is the resting state for a
`scene` or a `button`, and a fault everywhere else. If that set ever widens to
a domain carrying a reading, real faults start reporting as healthy and this
tool stops being worth running.

Exits non-zero on any failure. Run directly, or via ha_validate.sh.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reconcile_entities as R  # noqa: E402

# Domains that carry a reading, a position or a power state. `unknown` in any
# of these means a card is about to render a blank where a value belongs.
STATE_BEARING = [
    "sensor", "binary_sensor", "light", "switch", "media_player", "camera",
    "climate", "cover", "fan", "lock", "number", "select", "input_text",
    "input_boolean", "input_number", "vacuum", "update", "person",
    "device_tracker", "weather", "remote",
]

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def bucket(domain, avail, obs=None):
    eid = f"{domain}.probe"
    exp = {eid: (f"Probe {domain}", "Area", avail)}
    return R.classify(eid, exp, obs or {}, R.duplicate_names(exp))


# 1. `unknown` is benign ONLY for scene and button.
for d in ("scene", "button"):
    check(bucket(d, "unknown") == "benign_unknown",
          f"{d}: unknown should be benign_unknown, got {bucket(d, 'unknown')}")

for d in STATE_BEARING:
    got = bucket(d, "unknown")
    check(got == "unresolved",
          f"{d}: unknown MUST stay a fault, got {got!r} — "
          f"BENIGN_UNKNOWN_DOMAINS has been widened and is hiding faults")

# 2. `unavailable` is never benign, not even for scene and button.
for d in ("scene", "button", "sensor", "light"):
    got = bucket(d, "unavailable")
    check(got == "unavailable",
          f"{d}: unavailable must stay unavailable, got {got!r}")

# 3. The benign set itself must not drift.
check(R.BENIGN_UNKNOWN_DOMAINS == {"scene", "button"},
      f"BENIGN_UNKNOWN_DOMAINS changed to {R.BENIGN_UNKNOWN_DOMAINS!r}; "
      f"widening it hides real faults — see the comment on the constant")

# 4. A same-domain name collision is ambiguous; a cross-domain one is not.
#    One appliance legitimately spans domains (a TV is media_player + remote).
same = {"binary_sensor.a": ("Door", "Hall", "ok"),
        "binary_sensor.b": ("Door", "Hall", "ok")}
check(R.classify("binary_sensor.a", same, {}, R.duplicate_names(same))
      == "ambiguous", "same-domain duplicate name should be ambiguous")

cross = {"media_player.tv": ("Telly", "Lounge", "ok"),
         "remote.tv": ("Telly", "Lounge", "ok")}
check(R.classify("media_player.tv", cross, {}, R.duplicate_names(cross))
      == "live", "cross-domain name sharing is normal, not ambiguous")

# 5. The overlay promotes unavailable -> recovered, and never demotes `ok`.
exp = {"light.x": ("X", "A", "unavailable")}
check(R.classify("light.x", exp, {"light.x": ("on", "recovered")},
                 R.duplicate_names(exp)) == "recovered",
      "overlay `recovered` should override an export `unavailable`")

exp_ok = {"light.y": ("Y", "A", "ok")}
check(R.classify("light.y", exp_ok, {"light.y": ("on", "recovered")},
                 R.duplicate_names(exp_ok)) == "live",
      "an export-`ok` entity is already live and must not be recounted")

# 6. An absent overlay must not change any verdict.
check(bucket("light", "unavailable") == "unavailable",
      "with no overlay, unavailable must stay unavailable")

if failures:
    print(f"  FAIL  {len(failures)} classifier regression(s):")
    for f in failures:
        print(f"        {f}")
    sys.exit(1)

print(f"  classifier: {len(STATE_BEARING)} state-bearing domains still fault "
      f"on `unknown`; benign set = {sorted(R.BENIGN_UNKNOWN_DOMAINS)}")
sys.exit(0)
