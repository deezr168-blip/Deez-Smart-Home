# artifacts/screenshots

Captures of the **live** CasaRay dashboard, produced on the Home Assistant host
by `scripts/casaray_capture.sh`. This is the only path by which a rendered page
reaches this repository, and therefore the only way a build can be compared
against the approved renders in `docs/mockups/`.

Two things must stay true of everything in this directory, because a file here
is trusted as evidence:

1. **It is a capture of the real instance.** Never commit a render of a mock, a
   stand-in, or a local preview here. If it did not come off the wall iPad's
   Home Assistant, it does not belong in this directory.
2. **Its sidecar travels with it.** Each `<view>-<label>.png` has a
   `<view>-<label>.json` recording the viewport, the settle time, the capture
   method, the repository commit and the UTC timestamp. Without it a screenshot
   cannot be tied to a version of the dashboard and is worth very little.

`scripts/ha_validate.sh` section 7 excepts `*.png` here from the
no-binaries rule. Nothing else in this directory is excepted, so do not park
exports, backups or databases here.

## Capturing

On the Home Assistant host (not in a build sandbox — it has no route to the
instance):

    export CASARAY_HA_TOKEN="$(cat ~/.casaray_token)"   # only if not already signed in
    sh scripts/casaray_capture.sh --label 2026-09-20 home energy bills

Then commit the PNGs and their sidecars so they can be read back here.
