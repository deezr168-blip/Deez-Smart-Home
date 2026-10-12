# Status vocabulary

Five words. Every row of a register carries exactly one in its `Status` column.
`scripts/check_register.py` enforces this file.

| Status | Means | Must have |
|---|---|---|
| **VERIFIED** | Observed directly: read off a data plate, seen in an export, measured, confirmed on the live system | `Source` (what, where, which page or line), `Verified on` (a date), and `Verified by` (who) |
| **REPORTED** | Stated by a named person or a document, not independently checked | `Source`: who or which document |
| **ASSUMED** | A working assumption, flagged so it is not mistaken for either of the above | the reason, in `Notes`. **Never allowed in an ownership, identifier, rating, measurement or price column.** Resolve it or turn it into UNKNOWN before the register is final |
| **UNKNOWN** | Not established. The word is written in the cell | nothing; but say in `Notes` what would resolve it |
| **N/A** | Does not apply to this row, with the reason in `Notes` | the reason |

A blank cell is not a status. It is an error (E3), because a blank cannot be told
apart from a value somebody forgot to fill in, or one that was deleted.

## The columns that matter most

The linter treats any column whose header looks like ownership, an identifier, a
rating, a measurement or a price as **sensitive**: owner, assigned, custodian,
serial, asset tag, model, manufacturer, rating, capacity, weight, dimension,
voltage, current, power, energy, kW, kWh, amps, mm, cm, kg, price, cost, amount,
total. A sensitive cell may hold a value only on a **VERIFIED** or **REPORTED**
row. That is the mechanical form of the rule *never infer unverified equipment
ownership or technical measurements*.

Replace the pattern with `--sensitive REGEX`, or extend it with
`--also-sensitive REGEX`, when a register uses other words.

## How this relates to the vocabulary already in the repository

These describe different things, so they are mapped, not merged.

| Repository term | Where | In a register |
|---|---|---|
| An entity ID is present in `docs/live/states_export_2026-09-05.txt` | root `CLAUDE.md` | **VERIFIED** for *existence*, Source = the export and line |
| That export's availability column | root `CLAUDE.md`: "a snapshot, and it goes stale" | **REPORTED**, dated 2026-09-05, never VERIFIED as current |
| `no source entity` | `design/casaray-v3/ENTITY_MAPPING.md` | **UNKNOWN**, with `no source entity` in Notes |
| `unavailable`, `unknown`, `offline`, `no data` on a card | root and V3 `CLAUDE.md` | a *runtime* reading, not a register status; do not copy it into a register as if it were a finding |
| `LIVE_VERIFIED` (owner confirmed on the live frontend) | `PROJECT_STATE.md`, *Verification States* | **VERIFIED**, `Verified by` = the owner |
| `CODE_VALID`, `PUSHED`, `DEPLOYED`, `LIVE_VERIFICATION_REQUIRED` | same | not provenance. They describe a *change's* journey, not a fact's evidence |

For entity checks inside the Home Assistant repository use `improve-system`'s
`references/evidence-rules.md`. This vocabulary is for everything else.

## The repository's standing rule: confirmed, estimated, outdated, unknown

Root `CLAUDE.md` (*Standing Rule: Context First, Questions Last*, item 11) says to
distinguish **confirmed, estimated, outdated and unknown** information. The
register's words map onto those, with one deliberate omission:

| Standing rule | In a register | Note |
|---|---|---|
| confirmed | **VERIFIED** | with a Source, a date and a person |
| estimated | **ASSUMED** | flagged, and never in an ownership, identifier, rating, measurement or price column |
| unknown | **UNKNOWN** | the word is written |
| outdated | **VERIFIED, with an old `Verified on` date** | there is no sixth status: staleness is a property of the *date*, not of the fact. `--max-age-days N` warns (W4) when a VERIFIED date is older than N days or in the future. When you know a value is superseded, write `outdated since <date>` in Notes |
| (no counterpart) | **REPORTED** | a named source's claim that nobody here has checked. Treat it as unconfirmed until it is |

The same item 9 asks that verified facts be recorded **with source and date**.
That is what `Source`, `Verified on` and `Verified by` are for.

## Counting

Say what answered, not the length of the list. Report `VERIFIED 9, UNKNOWN 5`,
never "9 of 14" or "64%": a fraction invites reading the five as failures when
they are gaps. This is the rule the dashboards already follow
("a denominator is what ANSWERED").

## Comparisons

- Prices come from the quote document, never from memory or a typical figure.
- Put the basis beside every price: tax included or not, unit, term, inclusions.
- Two quotes on different bases are **not comparable**. The comparison cell is
  UNKNOWN, not a converted guess. If you convert, show the arithmetic, name each
  input and its Source, and mark the result REPORTED at best.
- Never rank across an UNKNOWN. Say the ranking is withheld and what is missing.
- A recommendation is an opinion. Put it in its own row or paragraph, labelled as
  one, and keep it out of the data columns.

## Confidential or personal matters

For personnel, representation or other confidential records: register **that an
item exists and where it is held**, not what it says. Use an ID or initials rather
than a name. Do not copy statements into a register, a commit message or a file in
a repository. A register is a finding aid, not a copy.
