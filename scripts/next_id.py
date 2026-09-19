#!/usr/bin/env python3
"""The next free tracking ID, so a row is never numbered by eye.

WHY

`LIVE_VERIFICATION_QUEUE.md` and `DASHBOARD_ISSUES.md` are worked through by
ID: a person is told to go and look at `CR-322`. On 2026-09-19 two new rows
were numbered `CR-318` and `CR-319` because those looked like the next free
numbers, and both were already taken -- one by the entity audit, one by the
duplicate-entity script's row. Two unrelated rows under one number means one
of them gets checked and the other silently never does.

The mistake is not carelessness, it is that "the highest number I can see"
requires seeing twenty-five documents at once. So don't; ask.

    scripts/next_id.py CR        ->  CR-324
    scripts/next_id.py           ->  every prefix in use

WHY THERE IS NO GATE FOR THIS

A collision check was written first and then deleted, because it could not be
made to work. The obvious rule -- one ID must not carry rows with two
different commit SHAs -- misses the real case, since a freshly written row is
unstamped and so conflicts with nothing. The next rule -- rows sharing an ID
must sit in one section -- fails on `UI-031`, which correctly has two rows in
two sections because the queue is grouped by page and one batch fixed cards
on two of them.

There is no structural signal that separates "one batch, several things to
look at" from "two batches, same number". A gate that cannot tell them apart
would either pass the bug or fail on correct rows, and this repository's rule
is that a gate without a negative test does not get added. So this prevents
the mistake at the point of writing instead of catching it afterwards.
"""
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS = sorted(REPO.glob("*.md")) + sorted((REPO / "docs").glob("*.md"))
# Any MENTION counts, not just a table row. A number retired in a progress
# note is still spent, and handing it out again is the whole failure.
MENTION = re.compile(r"\b([A-Z]{2,5})-(\d{3})\b")


def used() -> dict:
    out = collections.defaultdict(set)
    for doc in DOCS:
        try:
            text = doc.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in MENTION.finditer(text):
            out[m.group(1)].add(int(m.group(2)))
    return out


def main() -> int:
    seen = used()
    if not seen:
        print("no tracking ids found", file=sys.stderr)
        return 1

    if len(sys.argv) > 1:
        prefix = sys.argv[1].upper().rstrip("-")
        if prefix not in seen:
            print(f"{prefix}-001")
            return 0
        print(f"{prefix}-{max(seen[prefix]) + 1:03d}")
        return 0

    width = max(len(p) for p in seen)
    for prefix in sorted(seen):
        nums = seen[prefix]
        print(f"  {prefix:<{width}}  next {prefix}-{max(nums) + 1:03d}"
              f"   ({len(nums)} used, highest {prefix}-{max(nums):03d})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
