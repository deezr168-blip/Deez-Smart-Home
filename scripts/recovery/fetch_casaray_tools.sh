#!/bin/sh
# CasaRay recovery -- fetch the two recovery scripts from GitHub, verified (v1, 30/10/2026).
# Run in the Terminal & SSH add-on:   sh /tmp/fetch_casaray_tools.sh
#
# Fetches branch recovery/phase0-diagnostics of the PUBLIC repository anonymously into a
# temporary bare git repository, checks casaray_evidence.sh and register_casaray.sh against the
# sha256 values pinned below, and only if BOTH match puts them at /tmp/casaray_evidence.sh and
# /tmp/register_casaray.sh. On any mismatch or failure it writes neither and exits 1.
#
# Never: runs what it fetches; sends or reads a credential (no deploy token, no
# /config/.deez_deploy.env, no askpass helper, no git credential helper, no ~/.gitconfig);
# touches /config, /homeassistant or the host clone deez_repo; restarts or changes anything in
# Home Assistant. It writes only under /tmp: the temporary repository (removed on exit) and
# the two verified files. Undo: rm /tmp/casaray_evidence.sh /tmp/register_casaray.sh
#
# Overrides (for tests): CASARAY_REPO_URL, CASARAY_OUT (default /tmp).

set -u
umask 077
URL=${CASARAY_REPO_URL:-https://github.com/deezr168-blip/Deez-Smart-Home.git}
BRANCH=recovery/phase0-diagnostics
OUT=${CASARAY_OUT:-/tmp}
H_EVIDENCE=4da47bc1a9d540bf064eefaabd5e866682c4b6dfd0907e896b3e6014ae11bd1f
H_REGISTER=56dea19d6603f76fa8f6827c76b08f4afda05cacb8042c2937872470f57ef251

say() { echo "[fetch] $*"; }
die() { echo "[fetch] STOP: $*"; exit 1; }
# git with no credential source at all: no system or global config, no prompt, no askpass,
# no helper, and none of the token variables a shell here might carry.
g() {
  env -u DEEZ_GH_TOKEN -u GITHUB_TOKEN -u GH_TOKEN -u GIT_ASKPASS -u SSH_ASKPASS \
    GIT_TERMINAL_PROMPT=0 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
    git -c credential.helper= -c core.askPass= --git-dir="$T" "$@"
}

command -v git >/dev/null 2>&1 || die "git is not available here; nothing changed"
[ -d "$OUT" ] || die "$OUT does not exist; nothing changed"
T=$(mktemp -d "$OUT/casaray_fetch.XXXXXX") || die "cannot create a temporary folder in $OUT; nothing changed"
case "$T" in "$OUT"/casaray_fetch.??????) ;; *) die "unexpected temporary path; nothing changed" ;; esac
trap 'rm -rf "$T"' EXIT
trap 'exit 1' INT TERM HUP

say "fetching $BRANCH from $URL (anonymous, read-only)"
g init -q --bare >/dev/null 2>&1 || die "git init failed; nothing changed"
g fetch -q --no-tags --depth=1 "$URL" "refs/heads/$BRANCH" 2>"$T/fetch.err" \
  || { sed 's/^/[fetch]   /' "$T/fetch.err" | tail -n 3; die "fetch failed; nothing changed"; }
COMMIT=$(g rev-parse FETCH_HEAD) || die "no commit fetched; nothing changed"
say "commit $COMMIT"

ok=0
for pair in "casaray_evidence.sh $H_EVIDENCE" "register_casaray.sh $H_REGISTER"; do
  f=${pair% *}; want=${pair#* }
  if ! g show "FETCH_HEAD:scripts/recovery/$f" >"$T/$f" 2>/dev/null; then
    say "$f: not in that commit"; continue
  fi
  got=$(sha256sum "$T/$f" | cut -d' ' -f1)
  if [ "$got" = "$want" ]; then say "$f: sha256 $got  VERIFIED"; ok=$((ok + 1))
  else say "$f: sha256 $got  DOES NOT MATCH the pinned $want"; fi
done
[ "$ok" -eq 2 ] || die "not both files verified; neither was written (the branch may have moved on: ask for an updated fetch script)"

for f in casaray_evidence.sh register_casaray.sh; do
  mv -f "$T/$f" "$OUT/$f" || die "could not place $OUT/$f; check $OUT"
done
say "written: $OUT/casaray_evidence.sh and $OUT/register_casaray.sh (nothing was run)"
say "next, each only with its own approval:  sh $OUT/casaray_evidence.sh   |   sh $OUT/register_casaray.sh check"
