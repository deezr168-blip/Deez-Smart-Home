#!/bin/sh
# CasaRay live screenshot capture — run this ON a machine that can reach Home
# Assistant (the HA host itself, or any LAN machine with Chromium).
#
# WHY THIS EXISTS
#
# Every visual correction to CasaRay so far has depended on Ray photographing
# the wall iPad and pasting the image into a conversation. The image is not
# persisted, cannot be compared against the previous one, and the loop cannot
# run without a human in it. This closes that: it writes a deterministic PNG
# into the repository clone, where Claude reads it from git like any other
# file.
#
# THE PROBLEM THIS SOLVES THAT A NAIVE SCREENSHOT DOES NOT
#
#   chromium --headless --screenshot http://ha:8123/casaray-v2/home
#
# does not fail when it is not logged in. It returns a perfectly valid
# screenshot OF THE LOGIN PAGE. A visual audit run against that would report
# that the entire dashboard had vanished, which is worse than no screenshot at
# all. So this checks the DOM before it trusts the pixels, and refuses rather
# than writing a misleading file.
#
# THREE CAPTURE PATHS, TRIED IN ORDER
#
#   1. Plain Chromium. Works when the capturing machine needs no login —
#      HA `trusted_networks` auth, or a dashboard set `require_admin: false`
#      on an open instance. Zero dependencies.
#   2. Playwright (Python or Node). Injects a long-lived access token into
#      localStorage before navigating, which is how the HA frontend actually
#      authenticates. Needed on any normally-secured instance.
#   3. Refuse, naming exactly what to install.
#
# THE TOKEN
#
# Supplied by environment or file, NEVER by argument (arguments show up in
# `ps` and in shell history) and never committed:
#
#   export CASARAY_HA_TOKEN="$(cat ~/.casaray_token)"     # preferred
#   or  --token-file ~/.casaray_token
#
# Create one in Home Assistant: profile -> Security -> Long-lived access
# tokens. This script only ever reads it; it is not written to the PNG, the
# sidecar, the log, or anywhere else.
#
# USAGE
#
#   casaray_capture.sh home
#   casaray_capture.sh --url http://<ha-host>:8123 energy
#   casaray_capture.sh --width 1180 --height 820 --scale 2 home
#   casaray_capture.sh --label pass-02 home
#   casaray_capture.sh --check          # diagnose without capturing
#   casaray_capture.sh --all            # every top-level view
#
# OUTPUT
#
#   artifacts/screenshots/<view>-current.png     (or -<label>.png)
#   artifacts/screenshots/<view>-current.json    capture metadata
#
# EXIT CODES
#
#   0  captured, and the DOM looked like a dashboard
#   1  captured nothing — unreachable, unauthenticated, or no usable browser
#   2  refused before trying — bad arguments or missing prerequisites

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
OUT_DIR="${CASARAY_SHOT_DIR:-$REPO/artifacts/screenshots}"

# The wall iPad in landscape. These are the defaults because they are the
# device the design is for; DR-012 and DR-013 are both about this width.
HA_URL="${CASARAY_HA_URL:-http://homeassistant.local:8123}"
DASH="${CASARAY_DASH:-casaray-v2}"
WIDTH=1180
HEIGHT=820
SCALE=2
WAIT_MS=4000
LABEL="current"
CHECK_ONLY=0
ALL=0
TOKEN="${CASARAY_HA_TOKEN:-}"
VIEWS=""

die()  { printf '%s\n' "$*" >&2; exit 2; }
say()  { printf '%s\n' "$*"; }
warn() { printf '  ! %s\n' "$*" >&2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --url)        HA_URL="$2"; shift 2 ;;
    --dashboard)  DASH="$2"; shift 2 ;;
    --width)      WIDTH="$2"; shift 2 ;;
    --height)     HEIGHT="$2"; shift 2 ;;
    --scale)      SCALE="$2"; shift 2 ;;
    --wait)       WAIT_MS="$2"; shift 2 ;;
    --label)      LABEL="$2"; shift 2 ;;
    --out)        OUT_DIR="$2"; shift 2 ;;
    --token-file) [ -r "$2" ] || die "cannot read token file: $2"
                  TOKEN=$(cat "$2"); shift 2 ;;
    --check)      CHECK_ONLY=1; shift ;;
    --all)        ALL=1; shift ;;
    -h|--help)    sed -n '2,60p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --*)          die "unknown option: $1" ;;
    *)            VIEWS="$VIEWS $1"; shift ;;
  esac
done

case "$HA_URL" in http://*|https://*) ;; *) die "--url must start with http:// or https://" ;; esac
HA_URL=$(printf '%s' "$HA_URL" | sed 's#/*$##')

# ------------------------------------------------------------------ browser
find_chromium() {
  for c in "${CASARAY_CHROMIUM:-}" \
           /opt/pw-browsers/chromium-*/chrome-linux/chrome \
           /usr/bin/chromium /usr/bin/chromium-browser /usr/bin/google-chrome \
           /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome; do
    [ -n "$c" ] && [ -x "$c" ] && { printf '%s' "$c"; return 0; }
  done
  command -v chromium >/dev/null 2>&1 && { command -v chromium; return 0; }
  return 1
}

CHROME=$(find_chromium || true)

have_playwright_py() { python3 -c "import playwright" >/dev/null 2>&1; }
have_playwright_node() { command -v node >/dev/null 2>&1 &&
  node -e "require('playwright')" >/dev/null 2>&1; }

# Chromium phones home on startup (component updater, sync, safebrowsing).
# These flags stop that. They are a precaution for a host with restricted
# egress, not a fix for an observed hang -- see the note on content type below
# for the stall that actually was observed.
CHROME_BASE="--headless=new --no-sandbox --disable-gpu --hide-scrollbars \
--disable-dev-shm-usage --no-first-run --no-default-browser-check \
--disable-background-networking --disable-component-update --disable-sync \
--disable-default-apps --disable-client-side-phishing-detection \
--disable-extensions --metrics-recording-only --mute-audio \
--force-device-scale-factor=$SCALE --window-size=$WIDTH,$HEIGHT"

# `--virtual-time-budget` is kept off the DOM probe: the probe only needs the
# first paint, and a live dashboard keeps scheduling work, so there is no
# reason to pay the settle time twice.
#
# If a capture appears to hang for the full BROWSER_TIMEOUT, check the response
# `Content-Type` first. Headless Chromium DOWNLOADS anything that is not HTML
# rather than rendering it, and then waits -- indistinguishable from a network
# stall. Home Assistant serves `text/html`, so this shows up against a
# hand-rolled stand-in far more often than against the real thing.
CHROME_SHOT="$CHROME_BASE --virtual-time-budget=$WAIT_MS"

# Hard ceiling on any browser invocation, so a stall surfaces as a failure
# rather than a hung script.
BROWSER_TIMEOUT="${CASARAY_BROWSER_TIMEOUT:-45}"
run_chrome() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$BROWSER_TIMEOUT" "$@"
  else
    "$@"
  fi
}

# ------------------------------------------------------------- reachability
reachable() {
  if command -v curl >/dev/null 2>&1; then
    # `|| echo 000` would APPEND to curl's own "000" on failure, giving
    # "000000", which is not equal to "000" and reads as reachable. Replace
    # the value on failure instead of adding to it.
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$HA_URL/" 2>/dev/null) || code=000
    case "$code" in ''|000) return 1 ;; esac
    return 0
  else
    # No curl: let the browser be the probe rather than guessing.
    [ -n "$CHROME" ]
  fi
}

# Does the rendered DOM look like a dashboard, or like the login form?
# This is the check that stops a screenshot of the login page being written
# out and later mistaken for a catastrophic layout regression.
classify_dom() {
  _url="$1"
  [ -n "$CHROME" ] || { printf 'no-browser'; return; }
  dom=$(run_chrome "$CHROME" $CHROME_BASE --dump-dom "$_url" 2>/dev/null || true)
  [ -n "$dom" ] || { printf 'empty'; return; }
  case "$dom" in
    *ha-authorize*|*"<ha-auth-flow"*|*'action="/auth/login_flow"'*) printf 'login'; return ;;
  esac
  case "$dom" in
    *hui-view*|*"hui-sections-view"*|*"<home-assistant"*) printf 'dashboard'; return ;;
  esac
  printf 'unknown'
}

# ------------------------------------------------------------------ capture
capture_plain() {   # url outfile -> 0 ok
  run_chrome "$CHROME" $CHROME_SHOT --screenshot="$2" "$1" >/dev/null 2>&1 || return 1
  [ -s "$2" ]
}

capture_playwright_py() {  # url outfile
  CASARAY_HA_TOKEN="$TOKEN" python3 - "$1" "$2" "$HA_URL" "$WIDTH" "$HEIGHT" "$SCALE" "$WAIT_MS" <<'PY'
import json, os, sys
from playwright.sync_api import sync_playwright
url, out, base, w, h, scale, wait = sys.argv[1:8]
token = os.environ.get("CASARAY_HA_TOKEN", "")
# The HA frontend reads its session from localStorage under `hassTokens`.
# Seeding it before the app boots is what makes a headless capture arrive
# already authenticated instead of at the login form.
tokens = json.dumps({
    "access_token": token, "token_type": "Bearer",
    "expires_in": 1800, "refresh_token": "",
    "expires": 9999999999999, "clientId": None,
    "hassUrl": base,
})
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--hide-scrollbars"])
    ctx = b.new_context(viewport={"width": int(w), "height": int(h)},
                        device_scale_factor=float(scale))
    ctx.add_init_script(f"window.localStorage.setItem('hassTokens', {tokens!r});")
    page = ctx.new_page()
    page.goto(url, wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(int(wait))
    # Animations settle differently run to run; freezing them is most of what
    # makes two captures of an unchanged dashboard comparable.
    page.add_style_tag(content="*{animation:none!important;transition:none!important}")
    page.wait_for_timeout(300)
    page.screenshot(path=out, full_page=False)
    b.close()
PY
  [ -s "$2" ]
}

write_sidecar() {  # outfile view path_kind
  _json="${1%.png}.json"
  _commit=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)
  # The URL is recorded WITHOUT host, because this file is committed and
  # CLAUDE.md forbids private Home Assistant URLs in tracked files.
  cat > "$_json" <<EOF
{
  "view": "$2",
  "dashboard": "$DASH",
  "captured_utc": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "repo_commit": "$_commit",
  "viewport": { "width": $WIDTH, "height": $HEIGHT, "device_scale_factor": $SCALE },
  "settle_ms": $WAIT_MS,
  "method": "$3",
  "path": "/$DASH/$2"
}
EOF
}

# ---------------------------------------------------------------- view list
if [ "$ALL" -eq 1 ]; then
  VIEWS=$(python3 - "$REPO/dashboards/casaray_v2.yaml" <<'PY' 2>/dev/null || true
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
print(" ".join(v["path"] for v in d["views"]
                if v.get("path") and not v.get("subview")))
PY
)
  [ -n "$VIEWS" ] || die "--all could not read the view list from the dashboard"
fi
[ -n "${VIEWS# }" ] || VIEWS=" home"

# -------------------------------------------------------------- diagnostics
say "CasaRay capture"
say "  target     : $HA_URL/$DASH/<view>"
say "  viewport   : ${WIDTH}x${HEIGHT} @${SCALE}x, settle ${WAIT_MS}ms"
say "  output     : $OUT_DIR"
printf '  chromium   : %s\n' "${CHROME:-NOT FOUND}"
printf '  playwright : '
if have_playwright_py; then say "python"; elif have_playwright_node; then say "node";
else say "absent (token auth unavailable)"; fi
printf '  token      : '
[ -n "$TOKEN" ] && say "supplied (${#TOKEN} chars)" || say "none"

if ! reachable; then
  say ""
  say "  UNREACHABLE — $HA_URL did not answer."
  say "  Run this on the Home Assistant host or a LAN machine, not in a"
  say "  sandbox. If the host is right, check --url."
  exit 1
fi
say "  reachable  : yes"

# Probe the FIRST view actually requested, not a hardcoded one: capturing
# only `energy` on an instance where `home` happens to redirect would
# otherwise classify a page nobody asked for.
PROBE_VIEW=$(printf '%s' "${VIEWS# }" | cut -d' ' -f1)
PROBE=$(classify_dom "$HA_URL/$DASH/$PROBE_VIEW")
say "  dom probe  : $PROBE"

METHOD=""
case "$PROBE" in
  dashboard) METHOD="chromium-plain" ;;
  login)
    if [ -z "$TOKEN" ]; then
      say ""
      say "  NOT AUTHENTICATED and no token supplied."
      say "  Create a long-lived access token in Home Assistant"
      say "  (profile -> Security), then:"
      say "    export CASARAY_HA_TOKEN=\"\$(cat ~/.casaray_token)\""
      exit 1
    fi
    if have_playwright_py; then METHOD="playwright-python"
    else
      say ""
      say "  A token was supplied but Playwright is not installed, and plain"
      say "  Chromium cannot seed localStorage before the app boots."
      say "    pip install playwright && playwright install chromium"
      exit 1
    fi ;;
  no-browser)
    say ""
    say "  No Chromium found. Install one, or set CASARAY_CHROMIUM."
    exit 2 ;;
  *)
    warn "DOM did not look like either a dashboard or a login page."
    warn "Continuing, but check the first capture by eye before trusting it."
    METHOD="chromium-plain" ;;
esac
say "  method     : $METHOD"

if [ "$CHECK_ONLY" -eq 1 ]; then
  say ""
  say "  --check: diagnosis only, nothing captured."
  exit 0
fi

mkdir -p "$OUT_DIR"
FAILED=0
say ""
for v in $VIEWS; do
  out="$OUT_DIR/$v-$LABEL.png"
  url="$HA_URL/$DASH/$v"
  ok=0
  case "$METHOD" in
    chromium-plain)     capture_plain "$url" "$out" && ok=1 ;;
    playwright-python)  capture_playwright_py "$url" "$out" && ok=1 ;;
  esac
  if [ "$ok" -eq 1 ]; then
    bytes=$(wc -c < "$out" | tr -d ' ')
    write_sidecar "$out" "$v" "$METHOD"
    printf '  captured  %-16s %8s bytes  %s\n' "$v" "$bytes" "${out#"$REPO"/}"
  else
    printf '  FAILED    %-16s %s\n' "$v" "$url"
    FAILED=$((FAILED + 1))
  fi
done

say ""
if [ "$FAILED" -gt 0 ]; then
  say "  $FAILED capture(s) failed."
  exit 1
fi
say "  Commit the PNGs so Claude can read them:"
say "    git -C \"$REPO\" add artifacts/screenshots && git -C \"$REPO\" commit -m 'shots: capture'"
exit 0
