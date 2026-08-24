# Deez-Smart-Home

Documentation, tooling and staged configuration for the Deez Smart Home
Home Assistant instance.

**This repository is not the smart home.** The live instance is the source of
truth; Home Assistant's own config files are not stored here and are not
readable from a Claude session. When this repository and the instance
disagree, the instance is right.

## Start here

| If you want to… | Read |
|---|---|
| Know how Claude reaches Home Assistant and GitHub | [`docs/access_verification.md`](docs/access_verification.md) |
| Know what devices exist, where, and what is healthy | [`docs/entity_inventory.md`](docs/entity_inventory.md) |
| See what is currently broken | [`docs/known_issues.md`](docs/known_issues.md) |
| Change dashboards, config or deployment | [`home-assistant/README.md`](home-assistant/README.md) |

## Layout

```
docs/                 Verified reference material
  access_verification.md   Which access paths work — protected infrastructure
  entity_inventory.md      Generated inventory of live entities
  known_issues.md          Dated findings from live captures
home-assistant/       Staged HA config + the architecture decisions
safework/             Site safety records (incidents, procedures, photos)
scripts/              Read-only tooling
CLAUDE.md             Operating rules for Claude in this repository
```

## Tooling

Both scripts are read-only. Neither contacts Home Assistant, and neither
modifies anything it inspects.

```bash
bash scripts/validate.sh       # run before committing config or deploying
```

Checks YAML syntax, duplicate keys, accidentally committed secrets, whitespace
and conflict markers, and broken relative links between docs. Exits non-zero on
failure.

Invoked via `bash` and `python3` rather than `./` because the scripts may arrive
without the executable bit — commits made through the GitHub API cannot set file
modes. `chmod +x scripts/*` locally if you prefer running them directly.

```bash
python3 scripts/build_entity_inventory.py <capture.txt> > docs/entity_inventory.md
```

Regenerates the entity inventory from a `GetLiveContext` capture. `docs/entity_inventory.md`
is generated — re-run this against a fresh capture rather than hand-editing it.

## Two things that are easy to get wrong

**Entity IDs are not in this repository, and cannot be guessed.** The access
path available to Claude reports friendly names, not `entity_id`s — and 24 of
those names are shared by more than one entity. Slugifying a name into an ID
will produce something wrong or ambiguous. Read the real ID from the entity
registry before anything references it.

**Deployment is manual on purpose.** The dashboard is storage mode, edited
through the Home Assistant UI, and automatic Git Pull deployment is
deliberately not used so that a person stays between a commit and the
appliances. The reasoning is in
[`home-assistant/README.md`](home-assistant/README.md) — please read it before
changing how config reaches the instance.

## Current state

Last live capture 2026-08-24: 431 exposed entities across 11 areas and 25
domains. 54 entities look genuinely offline and 11 look like orphaned
duplicates — see [`docs/known_issues.md`](docs/known_issues.md), where the
emergency buttons are the first item.
