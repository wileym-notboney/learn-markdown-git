# Learnings from the 2026-09-29 remediation session

A retrospective on taking nine adversarial-review findings from "documented"
to "fixed, reviewed and gated" using a planner skill and a subagent workflow.
Written for whoever runs the next pass, human or model.

## What happened

1. Both existing gates (`validate_curriculum.py`, `selftest.py`) were green at
   `c9c0161` while all nine findings in
   `docs/adversarial-review-2026-09-28.md` remained reproducible.
2. The planner skill produced a nine-milestone plan through architect,
   developer and technical-writer agents, each followed by parallel
   quality-reviewer gates. The design phase needed two fix rounds, the code
   phase two, the docs phase one.
3. A Workflow ran one specialised implementer per milestone with a
   code-reviewer gate after each. It stopped once (M-007) and a second run
   finished M-008, M-009 and a close-out milestone.
4. Result: eleven commits on `feature/adversarial-review-remediation`, all
   gates green, one named regression per finding, decision log in
   `tools/README.md`.

Rough cost: about 1.6M subagent tokens for planning and 1.2M for the two
workflow runs, roughly three hours wall clock.

## What worked

- **Plan-level review caught what code review cannot.** The reviewers found
  that Lessons 03 and 04 told learners bundling commits was fine, which the
  tightened check would then fail with no recovery path. That contradiction
  spans a lesson file and a checker function; a diff reviewer looking at one
  milestone would never see it.
- **Reviewers on a different agent type than implementers.** No milestone was
  graded by its own author. The M-007 reviewer caught a whole-file formatter
  run that the implementer reported as a clean change.
- **The breaker.** When a fix round left a finding open, the loop stopped
  instead of stacking two more milestones on a rejected base. The cost was one
  extra workflow launch, not a corrupted branch.
- **Scoped re-review.** The M-007 fix round removed the formatter noise but
  added a CHANGELOG bullet describing its own revert. Reviewing only the fix
  diff is what surfaced that.
- **One regression per finding, each with its own fixture.** The selftest
  now prints a line per finding, so a future reader can see exactly which
  behaviour each commit pinned.

## What went wrong

- **Stacked diffs are brittle.** The plan carried exact diffs per milestone.
  One reviewer-requested change to a selftest print line invalidated the
  context of every later selftest hunk and cost a full fix round. Prefer
  intent plus acceptance criteria for later milestones, and let the
  implementer generate the diff against the real tree.
- **Implementers reached for formatters.** Two agents reformatted whole lesson
  files. The house rule against whitespace-only changes was in CLAUDE.md, but
  the dispatch prompt did not repeat it. Name the rule that matters most in
  the prompt, not just the file that contains it.
- **An unowned plan artifact.** The plan defined `tools/README.md` in a
  trailing section that no milestone's file list included. Seven changelog
  entries and every `(ref: DL-nnn)` comment pointed at a file that did not
  exist until a close-out milestone was added by hand. Every artifact a plan
  defines needs a milestone that owns it.
- **A bug in the orchestration script.** After the first milestone the script
  set the review base to the literal string `HEAD`, so every later reviewer
  was told to diff `HEAD..HEAD`. All of them noticed and reviewed `HEAD~1`
  instead, which happened to be right for single-commit milestones but would
  have hidden a multi-commit one. Record concrete SHAs, never symbolic refs.
- **Reviewer noise.** Several reviewers flagged the commit trailer model name
  as wrong based on stale guidance. Harmless, but it appeared in a third of
  the review outputs and had to be filtered by hand.
- **One self-amend.** The M-004 implementer amended its own just-created
  commit to fix a placeholder. Nothing earlier was touched, but the repo rule
  says no history rewriting, and "no amend, add a commit" should be in the
  dispatch prompt explicitly.
- **A flake nobody explained.** `review.py --selfcheck` returned exit 2 once
  each in two different agents' runs and never again. Both agents reran it
  and moved on. It is still unexplained and worth a look.

## Learnings to carry forward

1. A green test suite is evidence about the suite, not the code. When a
   review lists reproductions the suite cannot reach, fix the suite's reach
   first (M-001 here) before trusting any later green.
2. Review the plan as hard as the code. The cheapest defects to fix were the
   ones caught before a single line landed.
3. Give each milestone intent, acceptance criteria and a file list. Give it
   exact diffs only for the first milestone touching a file.
4. Put the three rules most likely to be broken in the dispatch prompt: no
   formatting-only changes, no amend or rebase, stage `CHANGELOG.md`.
5. Track review bases as SHAs the moment a commit exists.
6. Let the breaker stop the run. Restart from the recorded base with the
   remaining milestones rather than forcing a fourth fix round.
7. When a plan defines a document, assign it to a milestone in the same
   pass.
8. Filter reviewer output for known-stale guidance before treating a Minor
   as a task.

## Still open

- Progress schema v2 and migration, remote-evidence caching and Git history
  caching were deliberately deferred until real learner data exists.
- The branch is unmerged and unpushed. Squashing the M-007 fix-up and the
  M-004 self-amend is optional and needs a maintainer's decision.
- The unexplained `review.py --selfcheck` exit 2.
