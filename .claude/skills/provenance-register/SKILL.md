---
name: provenance-register
description: Build, update or check a register, inventory, evidence log, quote or purchase comparison, or structured report so that every fact carries a status and a source and nothing is invented. Use when creating or maintaining an equipment register, asset or entity inventory, evidence and verification register, comparison of quotes or products, or any report stating ownership, model, serial number, rating, measurement, price or date. Each row is VERIFIED, REPORTED, ASSUMED or UNKNOWN; missing data is written as UNKNOWN and never guessed; ownership and measurements are never inferred; a bundled linter fails blank cells, unsourced verified rows, duplicate IDs and unsourced values in ownership, measurement and price columns. Produces local drafts only; uploading, sharing, emailing or buying needs explicit confirmation. Not for verifying Home Assistant entity IDs inside the dashboard repository (improve-system).
metadata:
  version: "0.1.0"
  status: pilot
  origin: WORKFLOW_AUDIT.md W05
---

# Provenance register

A register is only as good as its worst guessed cell. This skill keeps every fact
attached to where it came from, and makes a gap say so.

## The rule

Every row has a **Status** and a **Source**. The status is one of five words:

| | |
|---|---|
| **VERIFIED** | observed directly: has a Source, a date and a person |
| **REPORTED** | stated by a named person or document: has a Source |
| **ASSUMED** | a flagged working assumption: never allowed in ownership, identifier, rating, measurement or price |
| **UNKNOWN** | not established: the word is written in the cell |
| **N/A** | does not apply: the reason is in Notes |

A blank cell is an error. Full definitions and the mapping to the repository's own
vocabulary are in `references/status-vocabulary.md`.

## Procedure

1. **Find the register, if there is one.** If the owner has an existing register,
   read it and keep its columns exactly as they are: do not reorder, rename or
   "tidy" them. Add `Status`, `Source`, `Verified on`, `Verified by` only if they
   are missing, and say you did. Otherwise start from a template:
   `check_register.py --template equipment|evidence|quotes`.
2. **Fill only from what you have been given or can read.** The owner's message,
   files in the project, documents they have pointed you at. Nothing from
   memory, from a typical value, or from what such an item usually is.
3. **For each cell decide which status it earns.**
   - You can point at the line, label, page or reading: **VERIFIED** (or
     **REPORTED** if a person or document says it and you could not check).
   - You think you know but cannot show it: write **UNKNOWN**. Put your
     suspicion in Notes, as a candidate, marked unverified. Do not put it in the cell.
4. **Ownership and measurements are the sharpest edge.** Who owns, holds or is
   assigned an item; its model, serial number, rating, capacity, dimensions,
   voltage, power; its price. None of these is ever inferred. If the Source is not
   in front of you, the cell says UNKNOWN.
5. **Comparisons.** Prices come from the document. Put the basis beside each (tax,
   unit, term, inclusions). If two are not on the same basis, the comparison is
   UNKNOWN, not a converted guess. Show any arithmetic. Never rank across an
   UNKNOWN; say the ranking is withheld and what is missing. Keep the
   recommendation separate and labelled as opinion.
6. **Run the linter** and fix every error:
   `python3 .claude/skills/provenance-register/scripts/check_register.py FILE`
   (`--strict` makes warnings fail; `--table N` picks a Markdown table). Do not
   edit the linter or loosen its patterns to get a pass.
7. **Report in this shape:**
   ```
   Register: <file>   Rows: 12   VERIFIED 5 · REPORTED 3 · UNKNOWN 4
   Linter: PASS (0 errors, 1 warning)
   Open questions (what would turn each UNKNOWN into a fact):
     - EQ-004 Owner: who holds the purchase record?
   Not done: nothing uploaded, shared, sent or bought.
   ```
   Count by status, never as a fraction ("9 of 14" reads as five failures when
   they are five gaps).

## Confirm before you do any of these

Uploading to Drive or anywhere else, sharing, emailing, posting, ordering or
paying. Each needs the owner's explicit yes, every time. Say what will be sent and
to whom. Approval for one send is not approval for the next.

Write drafts only where the owner says, or in the session's scratch area. **Do not
commit a register to a repository unless asked.**

## Confidential or personal matters

For personnel, representation or similar records, register that an item **exists
and where it is held**, not what it says. Use an ID or initials, not a name. Do not
copy statements into a register, a summary, a commit message or a repository file.

## What the linter does and does not tell you

It checks that the register is well formed and honest about its gaps: blank cells,
bad statuses, duplicate IDs, unsourced VERIFIED or REPORTED rows, missing dates,
and values in ownership, measurement or price columns on rows that have not earned
them. **A pass does not mean any value is true.** It means none was passed off as
more certain than it is. Only a person with the source can say a value is right.

Its sensitive-column list is a pattern on headers. A register that names such a
column differently (a "Wattage" or "Colour" column that matters) needs
`--also-sensitive 'wattage|colour'`. Say so when you notice one.

## Where it ends

- Entity verification inside the Home Assistant repository belongs to
  `improve-system` (`references/evidence-rules.md`). This skill is for everything else.
- A vendor comparison with total cost of ownership and negotiation points belongs
  to `operations:vendor-review`; use this skill afterwards to check its figures.
- It does not know what equipment, bills or documents the owner has. It will not
  guess. If you have nothing to fill a register from, the right output is a
  template and a list of what you need.

## Validation

`python3 .claude/skills/provenance-register/scripts/check_register.py --selftest`
(34 checks) runs five fixtures of fictional data, the three templates, the
rule that an assumed owner is refused, and proof that linting changes nothing.
Last result is in `SKILL_VALIDATION_REPORT.md`.

## Maintenance

Templates are in `assets/templates/` and must lint clean (the self-test checks
it). Fixtures in `tests/fixtures/` are fictional and labelled so; never add real
data to them. If a new kind of register needs a different column rule, add a case
to the fixtures first, then change the linter.
