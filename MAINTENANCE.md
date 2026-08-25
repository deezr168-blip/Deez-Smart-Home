# Autonomous maintenance framework — `ha-deploy`

How Claude maintains this Home Assistant configuration, what it may change
without asking, what it may never change, and what it genuinely cannot verify.

Status: **PARTIAL.** The inspect → checkpoint → change → validate → commit →
deploy path is built and tested. The **verify** and **automatic rollback**
steps are not, because nothing in this environment can observe the live
instance. Detail in "Blocked capabilities" below. Nothing here is claimed as
working unless it was executed and its output checked.

---

## Verified environment

Audited 2026-08-25. Every line below was tested, not assumed.

| Capability | Status |
|---|---|
| Git read/write to `origin/ha-deploy` | **VERIFIED** — fetch and push both work |
| YAML parse, duplicate-key detection | **VERIFIED** — PyYAML 6.0.1 |
| Jinja template compilation | **VERIFIED** — Jinja2 3.1.6 |
| Live entity *state* (read-only) | **VERIFIED** — Assist connector, name-keyed |
| `/config` filesystem | **ABSENT** — not mounted |
| `.storage` | **ABSENT** — unreachable |
| `hass` / `ha` / supervisor CLI | **ABSENT** |
| HA config validation (`check_config`) | **UNAVAILABLE** |
| HA backup create/list | **UNAVAILABLE** — no supervisor access |
| HA restart / reload | **UNAVAILABLE** — and out of scope |
| REST / WebSocket to the instance | **BLOCKED** — egress policy denies the host |
| Deploy script `/config/deploy_deez_dashboard.sh` | **UNREADABLE** — not in repo, `/config` absent |
| Entity registry / real `entity_id` list | **UNAVAILABLE** |

### Credential exposure

The process environment holds a Nabu Casa remote URL and a JWT-shaped token
(`Name`, `Secret`), plus GitHub tokens. They are **not on disk in this
repository** and no tracked file contains them — verified by scan. The
validation gate fails the build if either ever appears in a tracked file.

`.gitignore` was tested against `secrets.yaml`, `.storage/`, the recorder
database, `backups/`, `id_rsa`, `*.token` and `.env`: **all correctly ignored.**

---

## Autonomous scope

Changed without asking, provided validation passes:

`dashboards/**` · theme files · dashboard styling, layout, navigation, text,
icons, translations · Mushroom cards · `card_mod` · Lovelace YAML · template
fixes · `/www` dashboard assets · non-destructive scripts and automations ·
documentation · deployment and validation scripts · helper references ·
entity-reference corrections **where the entity is verifiable** · duplicate
YAML keys · broken local resource paths · formatting and maintainability.

### Risk classes

- **LOW** — styling, icons, spacing, card text, theme variables, `card_mod`,
  documentation. Proceed.
- **MEDIUM** — automations, scripts, entity substitutions, deployment or
  validation scripts, config structure. Proceed only when a checkpoint exists,
  validation passes, and affected entities are verified.
- **HIGH** — requires explicit owner approval. See below.

## Protected — never modified autonomously

`secrets.yaml` · authentication and auth providers · users, passwords, API
tokens, long-lived tokens · SSH and Git credentials · backup encryption keys ·
Nabu Casa and remote-access credentials · router, DNS, firewall · HA OS and
supervisor-level operations · storage or device formatting · Zigbee coordinator
migration · Matter fabric credentials · deletion of integrations, devices or
entities · mass entity renaming · destructive database operations · anything
that could cause lockout or destroy Claude's own recovery path.

The validation gate **fails the build** if a protected path appears in the
diff. It is a check, not just a rule.

## Device control is prohibited, and enforced

Claude holds configuration-maintenance authority, not household-control
authority. It does not turn on lights, unlock doors, operate garage doors or
covers, activate alarms, switch appliances, run heating or cooling, operate
media, or trigger automations that could move a device.

This is enforced technically, not only by instruction:

- `.claude/settings.json` denies the device-control MCP tools by name, and
- a `PreToolUse` hook (`scripts/deny_device_control.py`) denies any tool whose
  name ends in a `Hass*` action verb, **matching on the tool name rather than
  the MCP server name** — the connector's server id has already changed once
  within this project, so a server-pinned rule would have silently stopped
  protecting anything.

Read-only `GetLiveContext`, `GetDateTime` and `todo_get_items` stay allowed;
entity verification depends on them. Both paths were pipe-tested: actuators
denied, read-only tools allowed.

---

## Validation pipeline

`bash scripts/ha_validate.sh` — read-only, exit 0 = safe to deploy.

| # | Check | Status |
|---|---|---|
| 1 | YAML parsing | **VERIFIED** |
| 2 | Duplicate-key detection | **VERIFIED** — strict loader |
| 3 | Template syntax (all Jinja compiles) | **VERIFIED** |
| 4 | Navigation integrity | **VERIFIED** — every `navigation_path` resolves |
| 5 | Card-property mismatches | **VERIFIED** — e.g. `color` on a Mushroom card |
| 6 | `/local/` resource existence | **PARTIAL** — checks when `www/` is in the repo; skipped and labelled otherwise |
| 7 | Protected-file modification | **VERIFIED** |
| 8 | Secret / credential scan | **VERIFIED** |
| 9 | Unexpected deletions | **VERIFIED** |
| 10 | Mass-damage detection | **VERIFIED** — truncation, view loss, entity loss vs HEAD |
| 11 | Whitespace, conflict markers, binaries | **VERIFIED** |
| 12 | **Home Assistant config validation** | **UNAVAILABLE** — reported as SKIP, never silently passed |
| 13 | Entity existence | **UNAVAILABLE** — registry unreachable |

Every check was negative-tested: a deliberately truncated dashboard, a staged
`secrets.yaml`, and a deleted file each failed the gate as intended.

**A pass means well-formed and internally consistent. It does not mean a card
renders or an entity exists.** The browser check after deploy is not optional.

---

## Recovery

**Git.** Every change is a commit with a descriptive message and a reviewable
diff. History is never rewritten; rollback is `git revert`, never force-push or
reset of a published branch.

**Checkpoints.** `scripts/checkpoint.sh`:

- `show` — current known-good commit
- `record "why"` — tag HEAD and append to `.maintenance/known_good.json`
- `rollback-plan` — print the exact recovery commands

History is append-only: tags are additive, never force-moved, and an earlier
checkpoint is pushed onto a history array rather than overwritten. The plan
prints commands rather than running them — reverting a deployed dashboard is a
production change, not a script side effect.

> **Tags are local-only here.** `git push --tags` reports "Everything
> up-to-date" while the remote keeps zero tags — the git proxy in this
> environment does not accept tag refs. Since the container is ephemeral, a
> tag-only checkpoint would not survive it. That is why the authoritative
> record is `.maintenance/known_good.json`, which is a committed, pushed file.
> The tag is a local convenience; **the JSON is the recovery artifact.**

**Home Assistant backups: UNAVAILABLE.** No supervisor access. Take a full
backup manually before any substantial change.

## Deployment

Unchanged: push to `origin/ha-deploy`; `/config/deploy_deez_dashboard.sh`
fetches, validates, skips when unchanged, and applies. That mechanism was not
modified. Git Pull remains unused and must not be pointed at this branch.

## Blocked capabilities

Honest list of what this framework does **not** do.

1. **Post-deploy verification.** Nothing here can reach the instance, so
   "did the change load?" cannot be answered from this environment.
2. **Automatic rollback on failure.** It depends on (1). A rollback *plan* is
   generated; executing it is a human decision.
3. **HA schema validation.** Valid YAML is not valid Lovelace config.
4. **Entity existence.** Several referenced sensors are not exposed to Assist
   and cannot be confirmed at all.
5. **HA backups.**
6. **Reading the deploy script**, so its internal safety behaviour is unknown
   and must not be relied on.

### Minimum additional access to close each

| To unblock | Minimum needed |
|---|---|
| 1, 2, 3, 5, 6 | File-level `/config` access (Studio Code Server, Samba or SSH add-on) — or commit `deploy_deez_dashboard.sh` and a config snapshot to this branch |
| 4 | Export Developer Tools → States and commit the entity list |

Nothing broader than that is required. Do not grant more.
