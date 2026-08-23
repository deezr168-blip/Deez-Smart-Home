#!/usr/bin/env bash
# Non-destructive validation checks for this repository's Home Assistant
# deployment content (ha-config/) and general repo hygiene.
#
# Safe to run at any time: it only reads files and runs `git diff`/`git
# grep`/`git ls-files` — it never writes, deletes, restarts anything, or
# touches a live Home Assistant instance.
#
# Usage: scripts/validate_ha_config.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

OVERALL_FAIL=0
section() { echo; echo "== $1 =="; }

# ---------------------------------------------------------------------------
# 1. YAML syntax validation (+ duplicate-key detection) for all tracked YAML
# ---------------------------------------------------------------------------
section "YAML syntax + duplicate-key validation"
mapfile -t YAML_FILES < <(git ls-files '*.yaml' '*.yml')
if [ "${#YAML_FILES[@]}" -eq 0 ]; then
  echo "No tracked YAML files found — nothing to validate yet."
elif ! command -v python3 >/dev/null 2>&1; then
  echo "SKIP: python3 not available in this environment."
  OVERALL_FAIL=1
else
  if python3 - "${YAML_FILES[@]}" <<'PYEOF'
import sys
try:
    import yaml
except ImportError:
    print("SKIP: PyYAML is not installed in this environment; cannot validate YAML syntax.")
    sys.exit(1)

class DupKeyLoader(yaml.SafeLoader):
    pass

def construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key!r}", key_node.start_mark
            )
        value = loader.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping

DupKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)

failed = False
for path in sys.argv[1:]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            list(yaml.load_all(f, Loader=DupKeyLoader))
        print(f"OK   {path}")
    except yaml.YAMLError as e:
        print(f"FAIL {path}: {e}")
        failed = True
sys.exit(1 if failed else 0)
PYEOF
  then
    :
  else
    OVERALL_FAIL=1
  fi
fi

# ---------------------------------------------------------------------------
# 2. git diff --check (whitespace errors / leftover conflict markers)
# ---------------------------------------------------------------------------
section "git diff --check (whitespace / conflict markers)"
DIFF_ISSUES=0
if ! git diff --check; then DIFF_ISSUES=1; fi
if ! git diff --cached --check; then DIFF_ISSUES=1; fi
if [ "$DIFF_ISSUES" -eq 0 ]; then
  echo "OK   no whitespace errors or leftover conflict markers in working tree or staged changes."
else
  OVERALL_FAIL=1
fi

# ---------------------------------------------------------------------------
# 3. Forbidden secret-file / protected-path detection
# ---------------------------------------------------------------------------
section "Forbidden secret / protected path detection"
FORBIDDEN_PATTERNS=(
  "secrets.yaml"
  ".storage"
)
FOUND=0
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  matches=$(git ls-files | grep -F "$pattern" || true)
  if [ -n "$matches" ]; then
    echo "FAIL: forbidden path tracked in git (matches '$pattern'):"
    echo "$matches" | sed 's/^/  /'
    FOUND=1
  fi
done
if [ "$FOUND" -eq 0 ]; then
  echo "OK   no secrets.yaml or .storage/ path is tracked in git."
else
  OVERALL_FAIL=1
fi

# ---------------------------------------------------------------------------
# 4. Private key material detection
# ---------------------------------------------------------------------------
section "Private key material detection"
KEY_HITS=$(git grep -lIE "BEGIN (RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY" -- . 2>/dev/null || true)
if [ -n "$KEY_HITS" ]; then
  echo "FAIL: possible private key material found in:"
  echo "$KEY_HITS" | sed 's/^/  /'
  OVERALL_FAIL=1
else
  echo "OK   no private key headers found in tracked files."
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
section "Summary"
if [ "$OVERALL_FAIL" -eq 0 ]; then
  echo "All checks passed."
else
  echo "One or more checks FAILED — see above."
fi

echo
echo "NOT RUN — unavailable or intentionally skipped in this environment:"
echo "  - Home Assistant's own config check ('hass --script check_config' /"
echo "    the Supervisor 'Check Configuration' action): Home Assistant core"
echo "    is not installed in this repo's environment, and this script does"
echo "    not attempt to install it or reach the live instance."
echo "  - yamllint: not installed here. Duplicate-key and syntax checks above"
echo "    use PyYAML instead, which is already available, per this repo's"
echo "    instruction not to add dependencies without documenting why."

exit "$OVERALL_FAIL"
