# Incident record: {{symptom}}

Status: OPEN · Opened: {{date}} · Decision belongs to: the owner
Prepared by: Claude, triage only. **Nothing was executed.**

**Rule for this record.** Every line has a status, using the same four as the
`provenance-register` skill:

- **VERIFIED**: observed directly, with its source and time
- **REPORTED**: stated by a named person or document, not independently checked
- **ASSUMED**: inferred, with what it was inferred from
- **UNKNOWN**: not established. Write the word. A blank is a defect.

Keep usernames, backup identifiers, tokens, hashes and keys out of this record,
especially if it will be filed in the repository.

## 1. Symptom

- As reported: {{symptom}}
- First noticed: UNKNOWN
- Who or what is affected: UNKNOWN
- Are the cameras, alarms and door sensors still working meanwhile: UNKNOWN. Ask before anything else.

## 2. Last known good

- Last change before the fault (restart, update, configuration edit, deploy, power event): UNKNOWN
- Commit or backup that was last known good: UNKNOWN

## 3. Evidence

| # | Evidence | Status | Source | Time |
|---|---|---|---|---|
| E1 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 4. Hypotheses

Rank them. Each needs the check that would **disprove** it.

| # | Hypothesis | Supported by | Check that would disprove it | State |
|---|---|---|---|---|
| H1 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 5. Checks run (all read-only)

| # | Check | Run by | Result | Reading |
|---|---|---|---|---|
| C1 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

Run by is *owner on host*, *connector (read-only)* or *repository*. Claude runs
only the last two.

## 6. Decision needed from the owner

UNKNOWN. State the decision as a question with the options and what each risks.

## 7. Proposed recovery (NOT RUN, NEEDS APPROVAL)

UNKNOWN. If a recovery is proposed, every step below must be written down, and
every write step carries `NOT RUN, NEEDS APPROVAL`. Check the plan against
`references/recovery-safeguards.md` (R1 to R13) and say which safeguards it meets.

| Step | Reads or writes | Needs approval | Safeguards met |
|---|---|---|---|
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 8. Rollback of the recovery

UNKNOWN. How the recovery itself is undone if it goes wrong, and what is verified
before it begins.

## 9. Verification after

UNKNOWN. What will be checked, by whom, to call this fixed. "Looks fine" is not a check.

## 10. Unknowns and what would resolve each

| Unknown | Who or what can answer it |
|---|---|
| UNKNOWN | UNKNOWN |
