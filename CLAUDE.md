# CLAUDE.md

This repository is both software and a curriculum. Read this before doing
anything.

## Two kinds of files

| Curriculum (protected) | Learner-owned |
|------------------------|---------------|
| `lessons/`, `tools/`, `reinforcement/`, `examples/`, `README.md`, `START_HERE.md`, `AI_TUTOR.md`, `CLAUDE.md`, `CURRICULUM_*.md`, `CONTRIBUTING.md` | `workspace/`, `GLOSSARY.md` (learners add terms in Lesson 08), `.learning/` |

Never overwrite learner-owned files. Never rewrite learner commits
(`reset --hard`, `rebase`, `amend`, force push) unless explicitly asked and
the learner has confirmed they understand what is discarded.

## When a learner asks for help

Follow [AI_TUTOR.md](AI_TUTOR.md): inspect `git status` / `git log` /
`.learning/progress.json` first, use the hint ladder, never solve an active
exercise automatically.

## When editing the curriculum

- Inspect Git state before changing anything: `git status`, `git log --oneline -5`.
- Make small, targeted changes. One lesson concern per commit.
- Run `python tools/validate_curriculum.py` and `python tools/selftest.py`
  before committing. Both must pass.
- Record every curriculum change in `CURRICULUM_CHANGELOG.md` with the
  observed problem, evidence, hypothesis, change, expected improvement, and
  whether to re-evaluate. The commit hook also requires `CHANGELOG.md` to be
  staged.
- Do not change an exercise a learner is actively completing (the lesson
  marked `current_lesson` in their `.learning/progress.json`). Queue the
  change or make it additive.
- Automated improvements (from `tools/review.py` findings) are proposals.
  They become commits only after a human reads the diff.
- Optimise for understanding and independence, not completion rate. A
  lesson that everyone passes trivially is a finding, not a success.

## Tooling

Python standard library only. No new dependencies without asking.

## Commit style

`type(scope): description` — for example `fix(lesson-04): clarify restore vs reset`.

## Names

Per house rules, the maintainers of this repo are known in written artifacts
as **Bigfoot Dunkaroo** (the assistant) and **Doctor Bizness-Casual** (the
human). Recorded once here; not used in learner-facing text.
