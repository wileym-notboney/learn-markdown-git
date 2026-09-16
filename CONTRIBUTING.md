# Contributing to the Curriculum

## Ground rules

- Learner-owned files (`workspace/`, `.learning/`) are never touched by
  curriculum changes.
- Every change to a lesson, check, or reinforcement drill gets an entry in
  `CURRICULUM_CHANGELOG.md` **and** `CHANGELOG.md` (a commit hook enforces
  the second).
- Small changes. One concern per commit.

## Before you commit

```text
python tools/validate_curriculum.py    # structure, links, concept ordering
python tools/selftest.py               # simulates a learner; checker must pass
```

Both must exit 0.

## Changing an exercise

1. Find the evidence. Run `python tools/review.py` against real progress
   data if you have any, or write down the confusion you observed.
2. Decide what the likely cause is: missing prerequisite, unclear wording,
   check too strict, concept out of order, lesson too big.
3. Make the smallest change that addresses it.
4. If you change what a check expects, update `tools/check.py` and the
   lesson's **Check Your Work** section together, and extend
   `tools/selftest.py` so the new expectation is exercised.
5. Add the changelog entry. Mark whether it should be re-evaluated later.

## Adding a lesson

- Folder `lessons/NN-name/README.md`, numbered contiguously.
- Add it to `tools/curriculum.json` with `introduces` and `requires`.
  `validate_curriculum.py` refuses concepts used before they are introduced.
- Every `## Exercise` needs all nine sections (Goal, Why This Matters,
  Before You Start, Instructions, Check Your Work, What You Should Notice,
  Common Mistakes, Recovery, Reflection).
- Add its checks to `tools/check.py` and its walkthrough to `tools/selftest.py`.

## Writing style

Concise, friendly, direct. Explain the problem before the command. Every
command says where to run it, what to expect, and whether it modifies
anything. No decorative emoji, no gamification.
