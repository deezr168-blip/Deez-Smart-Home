#!/usr/bin/env bash
#
# Known-good checkpoint record for the Deez Smart Home maintenance framework.
#
#   scripts/checkpoint.sh show                 print the current known-good state
#   scripts/checkpoint.sh record "why"         mark HEAD known-good (tag + record)
#   scripts/checkpoint.sh rollback-plan        print the exact recovery commands
#
# History is append-only. `record` adds a git tag and appends to the history
# array in .maintenance/known_good.json; it never rewrites or deletes an
# earlier checkpoint. Tags are additive and are never force-moved.
#
# `rollback-plan` deliberately PRINTS commands rather than running them. Reverting
# a deployed dashboard is a production change and stays a decision, not a side
# effect of running a script.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
STATE=.maintenance/known_good.json

show() {
  [ -f "$STATE" ] || { echo "no checkpoint recorded yet"; return 1; }
  python3 - "$STATE" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
c = d["current"]
print(f"  known-good commit : {c['commit']}")
print(f"  tag               : {c['tag']}")
print(f"  recorded          : {c['recorded_utc']}")
print(f"  deploy verified   : {c['deploy_verified']}")
print(f"  note              : {c['note']}")
print(f"  history entries   : {len(d['history'])}")
PY
}

record() {
  local note="${1:-routine checkpoint}"
  local sha ts tag
  sha=$(git rev-parse HEAD)
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  tag="known-good/$(date -u +%Y%m%d-%H%M%S)"
  git tag -a "$tag" -m "known-good: $note" "$sha" || return 1
  python3 - "$STATE" "$sha" "$ts" "$tag" "$note" <<'PY'
import json, os, sys
state, sha, ts, tag, note = sys.argv[1:6]
d = {"current": None, "history": []}
if os.path.exists(state):
    d = json.load(open(state))
entry = {"commit": sha, "tag": tag, "recorded_utc": ts, "note": note,
         # Honest by default: nothing here can observe the live instance, so a
         # checkpoint is "committed and validated", not "confirmed live".
         "deploy_verified": "UNVERIFIED — no live-instance observation available"}
if d.get("current"):
    d["history"].append(d["current"])
d["current"] = entry
json.dump(d, open(state, "w"), indent=2)
print(f"  recorded {sha[:12]} as {tag}")
PY
}

rollback_plan() {
  [ -f "$STATE" ] || { echo "no checkpoint recorded — cannot build a plan"; return 1; }
  local good; good=$(python3 -c "import json;print(json.load(open('$STATE'))['current']['commit'])")
  cat <<EOF
  Recovery plan (review before running — these are production changes)

  Last known-good commit: $good
  Current HEAD          : $(git rev-parse HEAD)

  1. See what changed since the known-good state:
       git diff $good..HEAD -- dashboards/

  2. Revert the offending commit(s) — never force-push, never reset a
     published branch:
       git revert --no-edit <bad-sha>

  3. Re-validate before pushing:
       bash scripts/ha_validate.sh

  4. Push. The deploy script picks the revert up like any other commit:
       git push origin ha-deploy

  5. Verify in the browser. If the deploy pipeline is not running, apply
     the known-good dashboard by hand instead:
       git show $good:dashboards/deez_smart_home.yaml
     then paste into Settings -> Dashboards -> Raw configuration editor.
EOF
}

case "${1:-show}" in
  show)          show ;;
  record)        record "${2:-}" ;;
  rollback-plan) rollback_plan ;;
  *) echo "usage: $0 {show|record \"note\"|rollback-plan}"; exit 2 ;;
esac
