# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- Commits made before the first `check.py` run are now recognised as the
  learner's own work. "Whose commit is this?" is decided by what a commit
  touches, not by when the checker was first run.
- The "Next:" line after a passing run points forward from the lesson just
  checked, and says so when every lesson is complete.
- Checks that need a missing file now report the missing file instead of
  describing its contents.

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
