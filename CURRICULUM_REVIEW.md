# Curriculum Review

How this course evaluates itself. The process is real, not aspirational:
`tools/review.py` produces the evidence, this file holds the rubric and the
loop, `CURRICULUM_CHANGELOG.md` records the outcomes.

## Signals

`tools/check.py` writes local, anonymous progress data to
`.learning/progress.json`. Per lesson it records: started/completed time,
attempts, passes, fails, hints requested, and how many times each individual
check failed. Nothing about the person is stored.

`tools/review.py` reads one or more progress files and derives:

| Signal | Derived from | What it usually means |
|--------|--------------|-----------------------|
| High fail count before first pass | `attempts` at first pass | Instructions unclear, or check too strict |
| Same check failing repeatedly | `failed_checks[id]` | The concept behind that check is not landing |
| Hints requested | `hints_used` | Lesson text alone is insufficient |
| Started, never completed, then a later lesson started | timestamps | Learner abandoned it; possible difficulty cliff or check bug |
| Passed on first attempt in under a minute | timestamps | Possibly trivial; may not demonstrate understanding |
| Fail spike in lesson N after clean N-1 | attempts across lessons | Difficulty jump or missing prerequisite |

Run it:

```text
python tools/review.py                       # this repo's .learning/progress.json
python tools/review.py path/to/dir           # every *.json in a folder (many learners)
python tools/review.py --selfcheck           # assert the classification rules still hold
```

Each finding carries a **likely cause** — the tool's own step-3 guess, made
by splitting a signal on a second piece of evidence (were hints used? was
the concept introduced in this lesson or an earlier one? how many checks
does the lesson have?). A rule that cannot find that second piece returns
`unclassified` rather than guessing. The diagnosis is a starting hypothesis,
never the decision: the decision goes in `CURRICULUM_CHANGELOG.md`.

It writes `docs/review-<date>.md` and prints findings with severity.

## Rubric

Evaluate each lesson against these. Record findings as
**evidence → finding → severity → suggested change**, not as scores.

| Category | Questions |
|----------|-----------|
| Beginner accessibility | Does every command say where to run it and what to expect? Is anything assumed about the terminal or editor? |
| Conceptual clarity | Is the problem explained before the syntax? Is there a mental model before the terminology? |
| Progressive difficulty | Does the lesson use only concepts from `curriculum.json` `requires`? Is hand-holding reduced gradually? |
| Practical relevance | Does the exercise change a real file in the repo for a plausible reason? |
| Command safety | Are `reset`, `checkout`, `clean`, `rebase`, force push absent or explicitly warned? Is `switch`/`restore` used over `checkout`? |
| Exercise quality | Does the check test what the lesson taught? Could a learner pass by pasting without understanding? |
| Recovery quality | Can the learner get back to a known-good state from every likely mistake without losing committed work? |
| Reinforcement | Is the concept used again in a later lesson? Is there a `reinforcement/` drill for it? |
| Consistency | Same term for the same thing everywhere? Same exercise section order? |
| Independence | By lesson 08, is the learner choosing commands rather than copying them? |
| Markdown quality | Do examples render? Are they readable as raw text? |
| Git accuracy | Is the expected output still what current Git prints? |
| Maintainability | Is each check exercised by `selftest.py`? Are lesson expectations in one place? |

## Optimisation loop

1. **Gather** — collect `.learning/progress.json` files (your own, or
   volunteers' — they contain no personal data) into a folder.
2. **Identify** — `python tools/review.py <folder>`. Read the findings.
3. **Classify** — for each finding, decide the likely cause:
   unclear wording / missing prerequisite / check too strict / check buggy /
   concept out of order / lesson too big / lesson too small / trivial pass.
4. **Propose** — write the smallest change that addresses the cause.
5. **Apply** — edit the lesson and/or `tools/check.py`. Keep it to one
   concern.
6. **Validate** — `python tools/validate_curriculum.py` and
   `python tools/selftest.py` must pass.
7. **Compare** — after the change has been used, run `review.py` again and
   compare the same signal against `docs/review-<earlier date>.md`.
8. **Record** — add a `CURRICULUM_CHANGELOG.md` entry.

## Guardrails

- Never optimise for completion rate alone. A check that everyone passes
  instantly is a finding ("trivial pass"), not a win.
- Never change the lesson a learner is currently on (`current_lesson` in
  their progress file) in a way that invalidates their in-progress work.
- Changes are ordinary Git commits: reviewable, revertable.
- Automated tooling proposes; a human commits.

## Review cadence

Run the loop whenever you have new progress data, after any change to
`tools/check.py`, and after a Git release that changes command output.
