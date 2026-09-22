# Curriculum Changelog

Every change to a lesson, exercise, check, or reinforcement drill is
recorded here with its reasoning. Software-level changes go in
`CHANGELOG.md`.

Entry template:

```text
## YYYY-MM-DD — short title
- Observed problem:
- Evidence:
- Hypothesis:
- Change made:
- Expected improvement:
- Re-evaluate: yes/no — when
```

## 2026-09-21 — Lesson 07: pre-existing `origin` and bare-repo default branch

- Observed problem: learners who clone the course already have a remote
  named `origin`; and a bare repo created without `-b main` clones as an
  empty folder with a confusing warning.
- Evidence: author walkthrough in a fresh clone; selftest reproduced the
  empty clone.
- Hypothesis: both are environment surprises the lesson text did not
  anticipate.
- Change made: Before You Start renames a pre-existing `origin`; step 1
  uses `git init --bare -b main`; Common Mistakes covers the warning.
- Expected improvement: fewer failed 07.remote.* checks on first attempt.
- Re-evaluate: yes — once 07 progress data exists.

## 2026-09-16 — Initial curriculum

- Observed problem: none yet; first release.
- Evidence: author walkthrough via `tools/selftest.py` (lessons 00–09 simulated).
- Hypothesis: ten lessons, each pairing one Markdown skill with the Git
  action that naturally follows editing, will keep cognitive load low.
- Change made: created lessons 00–09, checker, progress tracking, review tooling.
- Expected improvement: n/a (baseline).
- Re-evaluate: yes — after the first five real progress files are collected.
