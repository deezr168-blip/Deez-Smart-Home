#!/usr/bin/env python3
"""Compare two Home Assistant Assist snapshots and report what changed.

Answers the questions that matter between captures: what broke, what came back,
what appeared, and what vanished. Routine state churn (a light switching off, a
temperature moving) is ignored unless --all-changes is passed.

Usage:
    python3 scripts/diff_snapshots.py snapshots/<older> snapshots/<newer>

Exits 1 if any entity newly became unavailable or disappeared, so this can gate
a check. Exits 0 otherwise.
"""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ha_snapshot import key, load  # noqa: E402

DEAD = "unavailable"


def index(entities: list[dict]) -> dict[tuple[str, str, str], list[str]]:
    """Map entity identity to the list of states seen under it.

    Duplicate friendly names are real in this system, so an identity can carry
    several states; they are compared as a sorted multiset.
    """
    grouped: dict[tuple[str, str, str], list[str]] = collections.defaultdict(list)
    for entity in entities:
        grouped[key(entity)].append(entity["state"])
    return {k: sorted(v) for k, v in grouped.items()}


def describe(identity: tuple[str, str, str]) -> str:
    name, domain, area = identity
    return f"[{domain}] {name} ({area or 'no area'})"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="older snapshot")
    parser.add_argument("after", type=Path, help="newer snapshot")
    parser.add_argument("--all-changes", action="store_true",
                        help="also list ordinary state changes")
    args = parser.parse_args(argv)

    before = index(load(args.before))
    after = index(load(args.after))

    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))

    broke, recovered, changed = [], [], []
    for identity in sorted(set(before) & set(after)):
        old, new = before[identity], after[identity]
        if old == new:
            continue
        old_dead, new_dead = old.count(DEAD), new.count(DEAD)
        if new_dead > old_dead:
            broke.append((identity, old, new))
        elif new_dead < old_dead:
            recovered.append((identity, old, new))
        else:
            changed.append((identity, old, new))

    def section(title: str, rows: list, transitions: bool = False) -> None:
        print(f"\n## {title} ({len(rows)})")
        if not rows:
            print("  none")
            return
        for row in rows:
            if transitions:
                identity, old, new = row
                print(f"  {describe(identity)}: {', '.join(old)} -> {', '.join(new)}")
            else:
                print(f"  {describe(row)}")

    print(f"Comparing {args.before.name} -> {args.after.name}")
    print(f"  entities: {sum(len(v) for v in before.values())} -> "
          f"{sum(len(v) for v in after.values())}")
    print(f"  unavailable: {sum(v.count(DEAD) for v in before.values())} -> "
          f"{sum(v.count(DEAD) for v in after.values())}")

    section("Became unavailable", broke, transitions=True)
    section("Recovered", recovered, transitions=True)
    section("New entities", added)
    section("Disappeared", removed)
    if args.all_changes:
        section("Other state changes", changed, transitions=True)
    else:
        print(f"\n({len(changed)} ordinary state changes hidden; "
              f"pass --all-changes to list them)")

    return 1 if broke or removed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
