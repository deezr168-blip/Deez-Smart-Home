#!/bin/sh
# One word on stdout: synced | out_of_sync | missing_repo | missing_live
#
# Backs sensor.casaray_sync_status. Deliberately trivial and side-effect free:
# a command_line sensor runs this every five minutes, so it must never write,
# never block and never depend on the network.
set -eu
DIR="$(dirname "$0")"
# shellcheck source=casaray_common.sh
. "$DIR/casaray_common.sh"
sync_status
