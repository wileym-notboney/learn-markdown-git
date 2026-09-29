# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `LEARNINGS.md`: retrospective on the 2026-09-29 remediation session.
- Adversarial review of the tooling (`docs/adversarial-review-2026-09-28.md`)
  and the remediation plan that implements its findings
  (`docs/superpowers/plans/2026-09-29-adversarial-review-remediation.md`).
- `tools/README.md` records the tooling invariants and the decision log
  (DL-nnn) cited by code comments and `CURRICULUM_CHANGELOG.md`.

### Fixed

- Commits made before the first `check.py` run are now recognised as the
  learner's own work. "Whose commit is this?" is decided by what a commit
  touches, not by when the checker was first run.
- The "Next:" line after a passing run points forward from the lesson just
  checked, and says so when every lesson is complete.
- Checks that need a missing file now report the missing file instead of
  describing its contents.
- `selftest.py` reports a checker crash as a harness error instead of an
  expected exercise failure.
- `setup_conflict.py` refuses to run while any tracked file is modified or
  any change is staged, and stops at the first failing git command instead of
  printing success.
- `06.merge.commit` accepts a conflict resolved by keeping either side, or
  by combining them, not only the resolutions that change the main line.
- Lesson 04 Exercise 4.3 recovery for a committed `scratch.md` now ends in
  the state `04.scratch.untracked` checks for.
- `03.commit.separate` and `04.commits.two-more` require commits that touch
  only their own file or folder, not just enough commits overall. Recovery
  text in Exercises 3.2 and 4.1 now tells a learner who bundled the files how
  to reach the checked state.
- The Lesson 01 and Lesson 09 Markdown checks ignore fenced code blocks and
  inline code spans, so Markdown shown as an example no longer counts as
  Markdown used. Code-block rules test the fenced blocks themselves.
- `07.remote.pulled` requires the second `reading-list.md` commit to be on
  `origin/main` and contained in `main`; `07.remote.pushed` reports "behind"
  and "diverged" separately. Lesson 07 Check Your Work says what the checker
  can and cannot verify.
- `check.py` refuses to run on a progress file it cannot read (exit 2, file
  untouched) instead of replacing it with an empty history, and saves
  progress through a temporary file and `os.replace`. `review.py` skips
  files that are not progress records and says which.
- `check.py all` no longer records progress. A failing run after a lesson
  is complete counts as a recheck and leaves `fails` and `failed_checks`
  alone; the first completion stores `fails_before_pass`.
- `review.py` no longer reports "abandoned" or "trivial pass", which were
  derived from timestamps that only show when the checker ran. "Hard to pass"
  uses `fails_before_pass` and ignores records that lack it.

### Added

- `review.py` classifies each finding's likely cause instead of reporting
  `unclassified`, with `python tools/review.py --selfcheck` asserting the rules.
- Findings group by concept rather than by individual check.

- Checker collapses repeated identical failures into one explanation.

- Ten-lesson curriculum teaching Markdown and Git by editing this repository.
- `tools/check.py`: educational checks with local progress tracking.
- `tools/validate_curriculum.py`: structural tests and concept-ordering validation.
- `tools/review.py`: friction report from progress data.
- `tools/setup_conflict.py`: creates the controlled merge conflict for Lesson 06.
- `tools/selftest.py`: simulates a learner through every lesson to prove the checker.
