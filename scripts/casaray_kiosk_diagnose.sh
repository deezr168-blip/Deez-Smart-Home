#!/bin/sh
# Why is Home Assistant's own header still showing on the CasaRay wall iPad?
#
# READ-ONLY. This script changes nothing. It answers one question the build
# environment cannot: is the kiosk-mode frontend resource actually registered
# and present on this instance?
#
# BACKGROUND (DR-015)
#
# `kiosk_mode:` in a dashboard YAML is not a Home Assistant feature. It is
# configuration read by kiosk-mode, a custom frontend module that must be
# loaded as a Lovelace RESOURCE. With no resource, the block is inert and the
# header renders normally -- which is exactly what the 19/09 photographs show.
#
# The dashboard's own block is not the problem: `hide_sidebar` and
# `hide_header` are both valid options per the module's README, and both are
# set. (`ignore_per_user`, which sat beside them until 19/09, is not a
# kiosk-mode option at all -- but an unknown key is ignored, it does not
# disable the valid ones.)
#
# Two other custom resources DO work on this instance -- card-mod paints every
# glass surface and the chip strip's pill radius, and custom:webrtc-camera
# renders the camera subviews -- so resource loading itself is fine. That is
# what narrows this to kiosk-mode specifically.
#
# USAGE (Home Assistant host, Terminal & SSH add-on)
#     sh /config/deez_repo/scripts/casaray_kiosk_diagnose.sh

set -eu
CONFIG="${CONFIG:-/config}"

say() { printf '%s\n' "$*"; }
hr()  { say "------------------------------------------------------------"; }

say "CasaRay kiosk-mode diagnosis"
say "config root: $CONFIG"
hr

# ---------------------------------------------------------------- 1. the file
say "1. Is the kiosk-mode module on disk?"
found=0
for p in "$CONFIG/www/kiosk-mode.js" \
         "$CONFIG/www/community/kiosk-mode/kiosk-mode.js" \
         "$CONFIG/www/community/kiosk-mode/kiosk-mode.js.gz"; do
  if [ -f "$p" ]; then say "   FOUND  $p"; found=1; fi
done
[ "$found" -eq 1 ] || say "   NOT FOUND in any usual location — this alone explains the header."
hr

# --------------------------------------------------------- 2. the registration
# Storage mode keeps resources in .storage/lovelace_resources. We only ever
# READ it, and only print resource URLs -- it holds no credentials.
say "2. Is it registered as a Lovelace resource?"
RES="$CONFIG/.storage/lovelace_resources"
if [ -f "$RES" ]; then
  say "   $RES exists. Registered URLs:"
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$RES" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception as exc:
    print(f"     could not parse: {exc}"); raise SystemExit
items = (data.get("data") or {}).get("items") or []
if not items:
    print("     (none registered)")
for it in items:
    print(f"     {it.get('url')}")
print()
urls = " ".join(str(i.get("url", "")) for i in items)
for name, why in (("kiosk-mode", "THE ONE IN QUESTION"),
                  ("card-mod", "known working — proves resources load"),
                  ("webrtc", "known working — proves resources load")):
    print(f"     {name:<12} {'registered' if name in urls else 'NOT registered':<15} {why}")
PY
  else
    say "     (no python3; grep instead)"
    grep -o '"url": *"[^"]*"' "$RES" || say "     (none)"
  fi
else
  say "   No $RES — this instance is not using UI-managed resources."
  say "   That means YAML mode, and resources must be declared in"
  say "   configuration.yaml under lovelace: resources: — see step 3."
fi
hr

# ------------------------------------------------------------- 3. YAML mode
say "3. Does configuration.yaml declare lovelace resources?"
CFG="$CONFIG/configuration.yaml"
if [ -f "$CFG" ]; then
  # Print only the lovelace block's shape, never the whole file: it can hold
  # tokens and internal hostnames and this output may be pasted into a chat.
  if grep -qE '^lovelace:' "$CFG"; then
    say "   A lovelace: block was found. Keys directly under it:"
    awk '/^lovelace:/{f=1;next} f&&/^[^[:space:]]/{f=0} f&&/^  [a-z_]+:/{print "     " $1}' "$CFG"
    # `resources:` only MATTERS in YAML mode. Reporting it as missing while
    # the instance is in storage mode would point at the wrong thing: there
    # the UI resource manager is authoritative and step 2 already answered.
    if grep -qE '^  mode: *yaml' "$CFG"; then
      if grep -qE '^  resources:' "$CFG"; then
        say "   Mode is YAML and resources: IS declared — look for kiosk-mode in it."
      else
        say "   Mode is YAML and resources: is NOT declared. In YAML mode that"
        say "   means NO custom frontend module loads at all — but card-mod is"
        say "   demonstrably working on the wall iPad, so re-read step 2 before"
        say "   acting on this line."
      fi
    else
      say "   Top-level mode is storage (or unset, which defaults to storage),"
      say "   so resources are UI-managed and step 2 is the authoritative answer."
      say "   A per-dashboard 'mode: yaml' under dashboards: does not change"
      say "   that — resources stay global."
    fi
  else
    say "   No top-level lovelace: block — storage mode, so step 2 is the answer."
  fi
else
  say "   $CFG not readable from here."
fi
hr

say "WHAT TO DO WITH THE ANSWER"
say ""
say "  Not on disk and not registered"
say "    -> kiosk-mode was never installed. Install it from HACS (Frontend ->"
say "       Kiosk Mode), then hard-refresh the iPad. This is the likely case:"
say "       the dashboards have carried a kiosk_mode: block since the first"
say "       build on the assumption the module was there, and nothing in the"
say "       repository ever recorded installing or verifying it."
say ""
say "  On disk but not registered"
say "    -> add the resource. Storage mode: Settings -> Dashboards -> Resources"
say "       -> Add, /local/community/kiosk-mode/kiosk-mode.js, JavaScript"
say "       module. YAML mode: add it under lovelace: resources: instead."
say ""
say "  Registered and still showing the header"
say "    -> the module is loading but not acting. Check its version against"
say "       this Home Assistant version; kiosk-mode has broken before when the"
say "       frontend's header markup changed. Report the two version numbers."
say ""
say "Nothing was modified by this script."
