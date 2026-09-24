#!/usr/bin/env bash
#
# Verify a dashboard change before pushing it. Read-only: this script never
# writes to the repository, never commits and never pushes.
#
# WHY THIS EXISTS
#
# Three checks have to pass before a dashboard change is safe, and they catch
# different things:
#
#   ha_validate.sh      the gate — YAML, structure, entities, secrets, geometry
#   preserve_check.py   nothing was silently dropped — views, cards, entities,
#                       navigation targets, service calls
#   render_cards.py     what the cards SAY changed only where you meant it to
#
# The third is the one that gets skipped, because it needs a BEFORE to compare
# against and producing one by hand means remembering to render the old tree
# first. Over one session that produced render_all2.txt through
# render_all6.txt in a scratch directory, each one a baseline for the next,
# and one comparison made against the wrong file.
#
# This owns that bookkeeping: it renders the dashboard as it exists at a git
# ref, renders the working tree, and diffs them. There is no baseline file to
# keep, name or lose.
#
# A pure reorder should show a diff of section INDEXES in labels and no card
# content. A template change should show exactly the cards you touched. Any
# third thing is the bug this catches.
#
# USAGE
#
#   scripts/verify_change.sh              # against HEAD
#   scripts/verify_change.sh <ref>        # against any git ref
#   scripts/verify_change.sh --quick      # skip the render pass
#
# EXIT CODES
#
#   0  every check passed
#   1  a check failed — the output says which
#   2  could not run — bad ref, missing tool, nothing to compare

set -uo pipefail

REPO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO" || exit 2

REF="HEAD"
QUICK=0
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --help|-h) sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) printf 'unknown option: %s\n' "$arg" >&2; exit 2 ;;
    *) REF="$arg" ;;
  esac
done

git rev-parse --verify --quiet "$REF" >/dev/null || {
  printf 'not a git ref: %s\n' "$REF" >&2; exit 2; }

DASH="dashboards/casaray_v2.yaml"
RENDER=".claude/skills/improve-system/scripts/render_cards.py"
PRESERVE=".claude/skills/improve-system/scripts/preserve_check.py"

fails=0
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m    %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; fails=$((fails + 1)); }

printf '\033[1mVerifying the working tree against %s\033[0m\n' \
  "$(git rev-parse --short "$REF")"

# Nothing to verify is worth saying out loud rather than passing silently:
# a clean tree means the checks below are comparing a thing to itself.
if git diff --quiet "$REF" -- "$DASH" 2>/dev/null; then
  printf '\n  \033[33mNOTE\033[0m  %s is identical to %s — nothing to verify.\n' \
    "$DASH" "$REF"
fi

step "[1/3] Validation gate"
if bash scripts/ha_validate.sh >/tmp/vc_gate.$$ 2>&1; then
  ok "ha_validate.sh passed"
else
  bad "ha_validate.sh failed:"
  grep -E 'FAIL|WARN' /tmp/vc_gate.$$ | sed 's/^/        /'
fi
rm -f /tmp/vc_gate.$$

step "[2/3] Nothing lost"
if [ -f "$PRESERVE" ]; then
  if python3 "$PRESERVE" --ref "$REF" >/tmp/vc_pres.$$ 2>&1; then
    grep -E '^ +(views|entities|navs|services|cards)' /tmp/vc_pres.$$ | sed 's/^ */  /'
    ok "nothing lost against $REF"
  else
    bad "preserve_check reported a loss:"
    sed 's/^/        /' /tmp/vc_pres.$$
  fi
  rm -f /tmp/vc_pres.$$
else
  bad "preserve_check.py not found at $PRESERVE"
fi

step "[3/3] What the cards say"
if [ "$QUICK" -eq 1 ]; then
  printf '  \033[33mSKIP\033[0m  --quick: the render pass is the one that reads the cards.\n'
elif [ ! -f "$RENDER" ]; then
  bad "render_cards.py not found at $RENDER"
else
  # The whole point: the BEFORE comes from git, not from a file someone
  # remembered to make earlier.
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  if git show "$REF:$DASH" > "$tmp/before.yaml" 2>/dev/null; then
    python3 "$RENDER" --dashboard "$tmp/before.yaml" --all > "$tmp/before.txt" 2>&1
    python3 "$RENDER" --dashboard "$DASH"            --all > "$tmp/after.txt"  2>&1
    if grep -q 'RENDER FAILED' "$tmp/after.txt"; then
      bad "a template raised in the working tree:"
      grep -B2 'RENDER FAILED' "$tmp/after.txt" | sed 's/^/        /'
    fi
    if diff -q "$tmp/before.txt" "$tmp/after.txt" >/dev/null; then
      ok "every card renders exactly as it does at $REF"
    else
      n=$(diff "$tmp/before.txt" "$tmp/after.txt" | grep -c '^[<>]')
      printf '  \033[33mDIFF\033[0m  %s changed line(s) — read them:\n' "$n"
      diff "$tmp/before.txt" "$tmp/after.txt" | sed 's/^/        /'
      printf '\n        A reorder shows section INDEXES and no card text.\n'
      printf '        A template change shows only the cards you touched.\n'
      printf '        Anything else is the bug this pass exists to catch.\n'
    fi
  else
    bad "$DASH does not exist at $REF"
  fi
fi

printf '\n'
if [ "$fails" -eq 0 ]; then
  printf '\033[32mVERIFIED\033[0m — safe to commit. A render diff is for you to read,\n'
  printf 'not a failure; nothing here can see the live frontend.\n'
  exit 0
fi
printf '\033[31m%d CHECK(S) FAILED\033[0m — fix or revert before committing.\n' "$fails"
exit 1
