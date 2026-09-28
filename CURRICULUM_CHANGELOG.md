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

## 2026-09-28 — Three faults found by hand-walking lessons 04–09

- Observed problem: (1) a learner who completed lesson 03 and only then ran
  the checker was told "no commit of yours touches workspace/hello.md" for
  work they had just committed; (2) passing lesson 04 printed
  "Next: lessons/00-orientation"; (3) a check whose file was missing
  reported "README.md does not link to another file".
- Evidence: author hand-walk of lessons 04–09 in a fresh clone, doing each
  lesson's work the way its text describes rather than the way the
  simulation did. The simulation always ran the checker before committing,
  so it could not reach fault (1) at all.
- Hypothesis: "the learner's commits" had been defined by *time* (a baseline
  recorded on first run), and time is the one thing a learner controls
  freely. Defining it by *content* — a commit touching learner files and not
  curriculum files — removes the ordering assumption entirely and also
  survives pulling curriculum updates.
- Change made: replaced the stored baseline with `is_maintainer()` /
  `learner_commits()` in `tools/check.py`; rewrote the next-step line;
  made both link checks report a missing file first. Added three regression
  checks to `selftest.py`, including one that commits before ever running
  the checker.
- Expected improvement: no learner is ever told their committed work does
  not exist; the checker's closing line always points somewhere useful.
- Re-evaluate: no — the ordering assumption is gone rather than tuned, and
  the selftest now covers the sequence that exposed it.

## 2026-09-28 — Review findings now carry a diagnosis

- Observed problem: every finding said "Likely cause: unclassified", so the
  report named friction but pointed nowhere; step 3 of the loop (classify)
  was left entirely to a human reading raw signals.
- Evidence: author run against real progress data — four findings for one
  lesson, all with the same empty diagnosis, three of them restating the
  same concept.
- Hypothesis: each signal can be split by a second piece of evidence
  already in the data (hints used, where the concept was introduced, how
  many checks the lesson has), which is enough for a defensible first
  guess without pretending to certainty.
- Change made: implemented `classify_cause` with documented rules and an
  assert-based `--selfcheck`; grouped findings by concept; both wired into
  `selftest.py`. Rules that cannot find their second piece of evidence
  still return `unclassified`.
- Expected improvement: a maintainer opening a review report has a starting
  hypothesis and a concrete suggested change per finding.
- Re-evaluate: yes — after the first reports from real learners, check
  whether the diagnoses matched what the fix turned out to be.

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
