#!/usr/bin/env python3
"""Parse Home Assistant YAML and report duplicate keys.

Read-only. Never contacts Home Assistant and never writes to the files it
checks. Exits non-zero if any file fails.

PyYAML silently accepts duplicate mapping keys, keeping the last one — a
mistake that is easy to make when merging dashboard views and invisible until
a card quietly disappears. This adds an explicit duplicate check on top of the
normal parse.

Home Assistant's YAML tags (!include, !secret, ...) are not understood by
PyYAML and would otherwise be reported as errors. They are registered below as
opaque values so that a file using them still parses structurally.

This is a text-level check only. It cannot confirm that an entity exists, that
a service call is valid, or that an automation is safe. Home Assistant's own
"Check Configuration" remains the authority.
"""

import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")


HA_TAGS = [
    "!include",
    "!include_dir_list",
    "!include_dir_merge_list",
    "!include_dir_merge_named",
    "!include_dir_named",
    "!secret",
    "!env_var",
    "!input",
]


class DuplicateKeyError(Exception):
    pass


class HALoader(yaml.SafeLoader):
    """SafeLoader that tolerates HA tags and rejects duplicate mapping keys."""


def _opaque(loader, node):
    """Accept an HA tag without trying to resolve what it points at."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


for tag in HA_TAGS:
    HALoader.add_constructor(tag, _opaque)


MERGE_TAG = "tag:yaml.org,2002:merge"


def _no_duplicates(loader, node, deep=False):
    """Build a mapping, rejecting keys written twice in the same block.

    Duplicate detection runs over the keys literally present in this mapping,
    BEFORE merge keys are flattened. That ordering matters: `<<: *anchor` is
    valid YAML that Home Assistant supports and community themes rely on, and
    flatten_mapping prepends the anchor's pairs to node.value. Checking after
    the flatten would report every deliberate override of an inherited value
    as a duplicate — e.g. a theme that inherits a base and then sets its own
    accent colour.
    """
    seen = set()
    for key_node, _ in node.value:
        if key_node.tag == MERGE_TAG:
            continue
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
        except TypeError:  # unhashable key — let PyYAML handle it normally
            duplicate = False
            key = str(key)
        if duplicate:
            mark = key_node.start_mark
            raise DuplicateKeyError(
                f"line {mark.line + 1}, column {mark.column + 1}: "
                f"duplicate key {key!r}"
            )
        seen.add(key)

    # Resolve `<<` into node.value. PyYAML places inherited pairs first, so
    # iterating in order below gives explicit keys the final say, which is
    # correct merge semantics.
    loader.flatten_mapping(node)

    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError:
            key = str(key)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


HALoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates
)


def check(path):
    """Return None if the file is fine, else a human-readable problem string."""
    try:
        with open(path, encoding="utf-8") as handle:
            # load_all: HA config files may contain multiple documents.
            for _ in yaml.load_all(handle, Loader=HALoader):
                pass
    except DuplicateKeyError as exc:
        return f"duplicate key — {exc}"
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f"line {mark.line + 1}, column {mark.column + 1}: " if mark else ""
        return f"parse error — {where}{getattr(exc, 'problem', exc)}"
    except OSError as exc:
        return f"unreadable — {exc}"
    return None


def main():
    paths = sys.argv[1:]
    if not paths:
        print("no YAML files to check")
        return 0

    failures = 0
    for path in paths:
        problem = check(path)
        if problem:
            failures += 1
            print(f"  FAIL  {path}: {problem}")
        else:
            print(f"  ok    {path}")

    if failures:
        print(f"\n{failures} of {len(paths)} file(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
