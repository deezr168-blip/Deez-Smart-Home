#!/bin/sh
# Fetch one recovery script from the recovery branch into /tmp (tmpfs),
# then print its SHA-256 to compare before running it.
#   sh /tmp/get.sh inspect_backup.sh
# Uses the Green's existing deploy credential through the existing askpass
# helper; never prints it. Writes only /tmp/<name> and git objects inside
# /config/deez_repo/.git. The working tree and checked-out branch are untouched.
F="$1"
case "$F" in ''|*[!a-z0-9_.]*) echo "usage: sh /tmp/get.sh <script-name>"; exit 2 ;; esac
docker exec homeassistant sh -c 'cd /config/deez_repo; [ -r /config/.deez_deploy.env ] && . /config/.deez_deploy.env; export DEEZ_GH_TOKEN GIT_ASKPASS=/config/deploy_askpass.sh GIT_TERMINAL_PROMPT=0; git -c safe.directory="*" fetch -q origin recovery/phase0-diagnostics && git -c safe.directory="*" show FETCH_HEAD:scripts/recovery/'"$F" > "/tmp/$F" \
  && sha256sum "/tmp/$F" || { echo "fetch failed"; rm -f "/tmp/$F"; exit 1; }
