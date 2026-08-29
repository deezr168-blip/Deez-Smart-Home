# Deez Smart Home — project rules

Permanent rules and architecture for this repository. Read this, then
`DASHBOARD_PROGRESS.md` and `DASHBOARD_ISSUES.md`, at the start of every
session. Resume from that recorded state; do not re-audit from scratch.

## What this repository is

`ha-deploy` is the deployment branch for one live Home Assistant dashboard.
`dashboards/deez_smart_home.yaml` **is production** — a push to `ha-deploy`
reaches the live dashboard within 15 minutes via
`/config/deploy_deez_dashboard.sh`. Treat every pushed batch as live.

Dashboard identity: url_path `deez-smart-home`, title **Deez Smart Home**,
36 views (16 subviews), Mushroom + card_mod + kiosk_mode, five per-view
themes, an English/Chinese toggle on `input_boolean.chinese_dashboard`.

## Session start

1. Read `CLAUDE.md`, `DASHBOARD_PROGRESS.md`, `DASHBOARD_ISSUES.md`.
2. `git log --oneline -15 ha-deploy` and confirm the tree is clean.
3. Check unresolved issues **before** planning new work. High-severity
   regressions come before cosmetic improvement.

## Working rules

- Small, controlled batches. One meaningful improvement per batch.
- Inspect the current YAML before changing it. Never edit blind.
- **Never invent entity IDs.** Use only entities the file already
  references, or ones verified through the read-only Home Assistant
  connector. If no entity exists, say so on the card rather than faking
  status — the established convention is a grey icon and an honest
  secondary ("no status entity", "Wi-Fi module not integrated yet").
- Preserve: entity IDs, navigation paths, `/deez-smart-home/` links, the
  language toggle, kiosk mode, subviews, camera functionality, energy
  calculations, room controls, themes, popups.
- Never `| float(0)`, `| float(100)` or `| float(9999)` as a fallback for a
  missing reading. A sentinel renders as a real measurement. Guard with an
  explicit `unavailable / unknown / none` branch, or test `is number`.
- Never let a card assert a reassuring state it cannot see. "Closed",
  "Clear", "Normal", "Up to date" all need a third branch.
- Run `bash scripts/ha_validate.sh` after every batch. Exit 0 or do not push.
- If validation fails, fix or revert before pushing. Never force-push, never
  rewrite published history.
- Push to `ha-deploy` **and** `claude/ha-dashboard-upgrades-wui7ig`. Local
  `ha-deploy` must be fast-forwarded before pushing it, or the push reports
  "Everything up-to-date" and the commit silently never deploys.
- Commit tracking-document updates together with the dashboard change they
  describe.
- A commit cannot contain its own hash. Write the batch's dashboard change
  and its tracking entries in one commit with the SHA left as a placeholder,
  then stamp the real SHA in a one-line `docs: stamp` commit immediately
  after. Do not amend to insert it — amending changes the hash again.

## Do not touch without an explicit instruction

The deployment bridge and its authentication: `/config/deploy_deez_dashboard.sh`,
`scripts/deploy_env.sh`, `scripts/deploy_askpass.sh`, `scripts/deploy_diagnose.sh`,
`DEPLOY_AUTH.md`, the deployment automation, Git remote configuration and
onboarding infrastructure. See `MAINTENANCE.md` for the wider protected list
(secrets, auth, users, tokens, network gear, supervisor operations) and for
the prohibition on device control.

No passwords, tokens, credentials or private Home Assistant URLs in any
tracked file, tracking documents included. The validation gate fails the
build if one appears.

## Design direction

**CasaRay × Your Name.** Cinematic, calm, premium, midnight-blue, slightly
translucent, and still native to Home Assistant. The background is the Your
Name night-sky frame at `/local/your_name_night_sky.jpg`, fixed and covering
the viewport; the palette is sampled from that image (see
`themes/deez_your_name.yaml`). Cards are frosted glass over the sky —
translucent, light-bordered, no heavy shadows.

Global first: put surface treatment in the theme so future cards inherit it,
rather than adding a `card_mod` block per card. Reach for a native Tile or
Section treatment before custom CSS.

**iPad landscape renders about two usable columns.** Design for two,
whatever `max_columns` says. Do not cram four narrow columns onto the iPad.

Still true from the previous direction: calm, minimal, Apple-like.
Sections layout with `grid_options`, not nested `grid` cards. One `heading`
card per section; the single `mushroom-title-card` is the page title and
comes first. Restrained amber for active state. Consistent 18px radius glass
surface. iPad landscape is the primary target — `max_columns` must match the
width a view actually fills, and no label should truncate.

## What cannot be verified from here

The build environment has no `/config`, no supervisor, no route to the
instance. YAML parsing, templates, navigation and structure are checkable;
Lovelace schema, entity existence and anything visual are not. A passing
validation run never means a card renders. See `DEPLOYMENT_BLOCKERS.md`.
