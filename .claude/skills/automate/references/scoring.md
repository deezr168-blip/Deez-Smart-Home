# Scoring, with worked examples from this repository

The arithmetic is in `scripts/procmem.py`; `score --explain <name>` prints it
for any recorded workflow. This is about how to read the answer.

## The dimensions, and why each is bounded

| Dimension | Range | Reasoning |
|---|---|---|
| frequency | 0–4 | Two occurrences scores 1. The brief this came from is explicit that twice is not a pattern, and the thresholds enforce it rather than relying on restraint. |
| steps | 0–3 | Under three steps scores nothing. A two-command sequence is not a workflow, it is two commands. |
| time saved | 0–3 | minutes × occurrences, capped. Uncapped, one confident self-reported number would justify anything. |
| error risk | 0–2 | +1 per recorded failure. A workflow that has actually gone wrong is worth more to automate than one that never has. |
| deterministic | 0–2 | Judgement-shaped work scores 0 **and** routes to a skill. This is not a penalty — it changes what gets built. |
| already automated | −3 | Big enough to push most solved things to LOW, not so big that a genuinely inadequate tool can never be flagged for extension. |

HIGH ≥ 7 · MEDIUM ≥ 4 · LOW below that.

## Worked example — HIGH, and worth it

```
parse views, locate a section, splice YAML

  frequency            +3     seen 8x
  steps                +2     6 steps
  time_saved           +3     8 min x 8
  error_risk           +0
  deterministic        +2
  already_automated    +0
  total                10  -> HIGH        recommendation: Python utility
```

This is the same twenty lines of boilerplate — parse the document, find the
`- type: sections` offsets, find the section starts inside a view, walk back
over the leading comment block — written from scratch eight times in one
session. Once it was written slightly wrong and the edit had to be reverted.

Note `error_risk` scored **0** even though it did fail once, because the
failure was not recorded at the time. That is a real limitation: score what
you actually saw, and pass `--failed` when something goes wrong, or the
dimension that should have made this obvious sooner stays empty.

Built as `scripts/dashboard_edit.py`.

## Worked example — LOW, built anyway

```
structural diff of the dashboard against a git ref

  frequency            +1     seen 2x
  steps                +1
  time_saved           +0
  deterministic        +2
  already_automated    -3
  total                 1  -> LOW
```

Two occurrences. By the rubric, record it and move on.

It was built anyway, as `preserve_check.py`, and that was the right call — but
it is worth being clear that the *score* did not justify it. What justified it
was consequence: both times it ran it caught a silent regression that every
other gate had passed, and the failure mode it guards against (a structural
edit quietly dropping a service call) is invisible until someone notices a
button does nothing.

**The rule this illustrates:** the score measures repetition and effort. It
does not measure what happens when the workflow is skipped. When the cost of
*not* doing something is high and the check is cheap, override the score —
deliberately, and say so. What is not allowed is overriding it because
building something felt satisfying.

## Worked example — HIGH, not built

```
validate, commit, push both branches

  frequency            +4     seen 16x
  steps                +2     5 steps
  time_saved           +3
  deterministic        +2
  total                11  -> HIGH        recommendation: shell script
```

The highest-scoring candidate in the memory, and deliberately left alone for
now. It ends in `git push`, and `scripts/checkpoint.sh` already occupies
adjacent ground. Both are reasons to bring it to the owner rather than build
it unprompted: the safety section puts anything ending in a push outside
autonomous territory, and the hierarchy says extend before adding.

A HIGH score is permission to *propose*, not always permission to build.

## Reading a score you disagree with

If the ranking looks wrong, the input is usually wrong rather than the
formula. Check:

- Were failures recorded? An unrecorded failure is two missing points.
- Is `minutes` the time for one run, or did it drift into total time?
- Is it really one workflow? Two things recorded under one name inflate
  frequency and flatten steps.
- Is it really deterministic? If the hard part is deciding what to do, it is
  not, and the recommendation should be a skill.
