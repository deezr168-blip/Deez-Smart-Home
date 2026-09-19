# Workflow families in this repository

Repetition here is conceptual, not textual. These are the families the work
actually falls into, what covers each today, and where the gaps are. Read this
before recording a "new" workflow — it is usually a member of one of these.

## 1. Entity reconciliation

Checking whether an entity exists, what it is called, whether it is answering,
and whether it has a stale twin. Presents as five separate-looking activities
— grep the export, query live state, compare friendly names, look for
duplicates, update a note — which is why it kept being done by hand.

- `scripts/reconcile_entities.py` — every dashboard reference exists in the
  export, plus a `STALE` blocklist for IDs known dead despite being listed.
- `scripts/audit_duplicate_entities.py` — friendly names carrying two entity
  IDs, and which twin each dashboard uses.
- The live Home Assistant MCP (`GetLiveContext`) — what is answering *now*.

**Known gap.** Nothing reconciles the export against live in one pass, because
`GetLiveContext` returns friendly names and the export returns IDs, and
nothing available here bridges them for entities that share a name. That is a
real limitation, not a missing script.

## 2. Dashboard structural editing

Parse, locate a view, locate a section, splice, re-parse, assert the shape.

- `scripts/dashboard_edit.py` — `views`, `sections`, `show`, `grep`,
  `replace`, `insert`, `delete`, `span`. Keeps a backup, supports
  `--dry-run`, and refuses any edit that would not re-parse.

Use it rather than writing the offset-finding loop again. If it cannot do what
you need, extend it — that is cheaper than a ninth one-off and the refusal
logic comes for free.

## 3. Template truthfulness

Rendering a card against live and dark states, in both languages, to catch a
card asserting something it did not measure.

- `.claude/skills/improve-system/scripts/render_cards.py` — including
  `--width` against the observed wrap limit.

## 4. Change verification

Proving a structural edit lost nothing.

- `.claude/skills/improve-system/scripts/preserve_check.py` — views, cards,
  entities, navigation targets, service calls, and one view card-for-card
  filtered by language.

## 5. Validation gates

- `scripts/ha_validate.sh` — the eight-section gate; the only thing that
  decides whether a change may be pushed.
- `scripts/dashboard_check.py` — the structural checks inside it.
- `scripts/yaml_check.py` — duplicate keys.

Adding a check is covered by `improve-system`'s `references/gates.md`,
including the negative-test step. Do not add a gate without one.

## 6. Deployment and its verification

- `scripts/casaray_safe_deploy.sh` — refresh, pre-flight, backup, deploy,
  post-flight, rollback, prune.
- `scripts/sync_casaray_to_config.sh` — the manual bridge to `/config`.
- `scripts/casaray_sync_status.sh`, `casaray_health_check.sh`,
  `casaray_rollback.sh`, `casaray_kiosk_diagnose.sh`.

All of these touch what people see. New automation around them is a
conversation with the owner, not an autonomous build.

## 7. Git workflow

Validate, commit, push to **both** branches. `scripts/checkpoint.sh` records
known-good states; nothing wraps the full sequence, and the failure mode —
forgetting the second branch, so the commit never deploys — is documented in
`CLAUDE.md` because it has happened.

Scored HIGH and deliberately not built. See `scoring.md`.

## 8. Reporting and tracking

Rows in `LIVE_VERIFICATION_QUEUE.md`, `DR-` entries in
`DASHBOARD_ISSUES.md`, rules in `CLAUDE.md`. Consistently repeated, and
deliberately **not** automated: the value is in the judgement about what is
worth recording and how to say it, and a generated row would be filler. If
this ever becomes mechanical, that is a sign the entries have stopped being
worth writing.

---

## Where a new workflow probably belongs

| If it is about… | Look first at |
|---|---|
| whether an entity exists or is answering | family 1 |
| moving, adding or resizing dashboard sections | `dashboard_edit.py` |
| what a card *says* in a given state | `render_cards.py` |
| whether an edit dropped something | `preserve_check.py` |
| refusing a class of mistake for good | a gate in `dashboard_check.py` |
| getting a change onto the wall | family 6 — ask before automating |
| writing down what happened | family 8 — probably leave it manual |
