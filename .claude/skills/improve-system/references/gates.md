# The gates

`bash scripts/ha_validate.sh` runs eight sections. Section 2 calls
`scripts/dashboard_check.py`, which holds the structural checks. Section 3
calls `scripts/reconcile_entities.py` for entity existence.

## Current catalogue

`dashboard_check.py`:

| # | What it refuses |
|---|---|
| 1 | a template that does not compile |
| 2 | a navigation path to a view that does not exist |
| 3 | a card property the card type ignores |
| 4 | a markdown card that renders as an indented code block |
| 5 | a folded scalar with accidentally more-indented lines |
| 6 | a `/local/` resource reference |
| 7 | a Fronius Wh sensor read as kWh |
| 8 | day-difference arithmetic that rounds instead of ceiling |
| 9 | `on`/`off` tested on a domain that never reports it |
| 10 | a stateless entity shown as a stateful tile |
| 11 | CJK text broken across a YAML fold |
| 12 | an unpaired bilingual heading |
| 13 | a markdown line emitting one to three leading spaces |
| 14 | a card in `casaray_v2.yaml` with no `grid_options` |
| 15 | a section leaving a half-empty row (`ALLOWED_HALF_ROWS`) |
| 15b | a `badges:` block in `casaray_v2.yaml` |
| 15c | `{% if ...'on' %}A{% else %}B{% endif %}` — no third branch |
| 15d | a view with no footer, an ungated footer label, or no way Home |
| 15e | one English term rendered two ways in Chinese (`ALLOWED_SENSES`) |
| 16 | mass damage — a large unexplained diff against HEAD |

`reconcile_entities.py`: an ID absent from the export, **and** an ID present in
the export but known dead (the `STALE` map).

## When to add one

Add a gate when you have just fixed a defect that could recur — not for a
one-off. The test is whether the same mistake is available to the next person
in a different file or a different view. Every `15x` check above exists because
a defect was found in several places at once, which is exactly the signal.

Two of them are worth studying as models:

- **15c** catches a *shape*, not a string: a two-way branch on a three-state
  entity. It found one survivor after a hand audit had already been done.
- **15e** compares the whole bilingual vocabulary against itself. It caught six
  collisions created by a later batch that shortened English labels — a class
  of mistake nobody would have thought to look for.

## How to add one

Follow the existing pattern in `dashboard_check.py`:

1. Scope it. Most checks are `if path.endswith("casaray_v2.yaml")` — the legacy
   dashboard predates the rules and is the rollback baseline.
2. Write a comment block above the check saying **what it refuses and why it
   exists**, naming the defect that motivated it. Six months from now the
   reason is the only thing that makes the check maintainable.
3. Append to `fails` with a message naming the view and *what to do about it*,
   not just what is wrong.
4. Print a one-line count even when it passes — a silent check is one nobody
   trusts.
5. If exceptions are legitimate, use a named constant (`ALLOWED_HALF_ROWS`,
   `ALLOWED_SENSES`) with a comment giving the reason for each entry. Adding an
   exception should require writing down why.

## Negative-test it, always

A gate nobody has seen fail is decoration. Before committing:

```sh
cp dashboards/casaray_v2.yaml "$SCRATCH/cr.bak"
# reintroduce the defect — one line is enough
python3 scripts/dashboard_check.py dashboards/casaray_v2.yaml   # expect FAIL naming the view
cp "$SCRATCH/cr.bak" dashboards/casaray_v2.yaml
python3 scripts/dashboard_check.py dashboards/casaray_v2.yaml   # expect PASS
```

Say in the commit message that it was negative-tested and what the failure
message said. That is the evidence the gate works.

## Never weaken a gate to get past it

If a gate fires on your change, it is telling you something. Fix the change,
or — if the gate is genuinely wrong — fix the gate *and say so explicitly in
the commit*, with the reasoning. Widening an allowlist to make a batch pass is
how a check quietly stops meaning anything.
