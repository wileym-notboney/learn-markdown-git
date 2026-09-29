# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Adversarial review of the tooling (`docs/adversarial-review-2026-09-28.md`)
  and the remediation plan that implements its findings
  (`docs/superpowers/plans/2026-09-29-adversarial-review-remediation.md`).

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
- Lesson 07 README formatting has been reverted from the previous commit to
  keep the focus on the Check Your Work change; extra emphasis/table
  alignment/indentation changes that were not part of the planned lesson edit
  have been removed.

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
