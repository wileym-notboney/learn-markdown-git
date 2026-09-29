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

## 2026-09-29 — Selftest tells a checker crash from an expected failure

- Observed problem: `Learner.check` treated any nonzero exit as "fail", so a regression that expects a failing check also passed when `check.py` crashed.
- Evidence: adversarial review of 2026-09-28: a `check.py` that raises at import makes every expected-fail assertion pass. `python tools/selftest.py` wall time at this commit: 7.0s.
- Hypothesis: Only exit codes 0 and 1 without a traceback on stderr mean pass or fail; everything else is the harness failing.
- Change made: `Learner.check` raises on other exit codes or a traceback; added `Learner.line` (output line for one check id) and `fresh_course` (one fixture per regression) for the regressions that follow.
- Expected improvement: a broken checker fails selftest loudly instead of looking like an exercise that has not been done yet.
- Re-evaluate: no
- Decisions: DL-002, DL-003 in tools/README.md.

## 2026-09-29 — Conflict helper no longer commits unrelated work or reports false success

- Observed problem: `tools/setup_conflict.py` ran a plain `git commit`, which commits the whole index, so anything the learner had staged landed on `conflict-practice`; and it ignored git's exit codes, so a failed commit still printed "Created branch".
- Evidence: adversarial review findings F1 and F2, reproduced by staging an unrelated file and by a pre-commit hook that exits 1. `python tools/selftest.py` wall time at this commit: 8.3s.
- Hypothesis: Preflight has to look at the whole working tree, not just favorites.md, and every git call has to be checked; a helper that fails should report where it stopped and leave the repository as it is.
- Change made: Whole-tree preflight (untracked files allowed), each git step return-code checked with the first failure reported, success printed only after the branch tip and current branch are verified. No reset or restore anywhere. Two selftest regressions.
- Expected improvement: a learner with unrelated staged work is told to commit or stash it instead of losing it into the practice branch; a failed helper never reads as success.
- Re-evaluate: no
- Decisions: DL-004 in tools/README.md.

## 2026-09-29 — Lesson 06 check accepts every valid conflict resolution

- Observed problem: `merge_touching` compared a merge commit with its first parent, so a learner who resolved the conflict by keeping the line already on `main` produced a merge identical to `main` on that path and `06.merge.commit` failed.
- Evidence: adversarial review finding F3: resolving with main's colour failed the check while purple passed. `python tools/selftest.py` wall time at this commit: 11.1s.
- Hypothesis: A conflict needs both sides to have changed the file since their merge base, so requiring both parents to differ from the base accepts ours, theirs and combined resolutions and rejects a merge only one side touched.
- Change made: `merge_touching(path, both_sides=True)` requires the path to differ from the merge base on both parents; 06.merge.commit uses it, the Lesson 09 check keeps the first-parent test. New selftest regression resolves the conflict three ways and requires 06.merge.commit to pass in each; a fast-forward and a no-conflict `--no-ff` merge still fail it.
- Expected improvement: a correct resolution is never rejected for the value the learner chose.
- Re-evaluate: no
- Decisions: DL-005 in tools/README.md.

## 2026-09-29 — Lesson 04.3: recovering a committed scratch file reaches the checked state
- Observed problem: Common Mistakes 4.3 told a learner who committed `scratch.md` to delete the file and commit the deletion; that leaves the file missing, and `04.scratch.untracked` requires it to exist and be untracked, so the check could never pass by following the text.
- Evidence: adversarial review finding F8: commit scratch.md, delete it and commit the deletion, and 04.scratch.untracked fails with "workspace/scratch.md not found". `python tools/selftest.py` wall time at this commit: 11.4s.
- Hypothesis: The recovery advice was written against the desired end state (untracked) without walking the steps to see whether they reach it.
- Change made: Common Mistakes 4.3 now says `git rm --cached workspace/scratch.md`, then commit; the different-scratch-file suggestion is removed; the check's Try text names the same command. The check rule is unchanged. New selftest regression follows the text literally.
- Expected improvement: a learner who committed the file by reflex can get to green without losing it.
- Re-evaluate: yes — when lesson 04 progress data exists
- Decisions: DL-006 in tools/README.md.

## 2026-09-29 — Separate-commit checks require a commit per file
- Observed problem: `03.commit.separate` counted learner commits (three or more) and `04.commits.two-more` counted commits touching each file, so one bundled commit plus unrelated or empty commits passed, and one combined edit passed as two. The old Recovery text also said bundling was acceptable, which would have made the stricter check unpassable.
- Evidence: adversarial review finding F6: one commit holding hello, profile and notes, then a favorites commit and an empty commit, passed `03.commit.separate`. Selftest now walks both Recovery texts literally. `python tools/selftest.py` wall time at this commit: 14.1s.
- Hypothesis: The lessons promise "one commit per thing"; the check should look at what each commit touched, since history carries that evidence, and the recovery path must lead to a state the check accepts.
- Change made: `exclusive_commits(path, *others)` in `tools/check.py`; lesson 03 needs a commit of its own for each of hello, profile and notes, lesson 04 needs two for profile.md and two for notes/README.md relative to each other. Exercise 3.2 and 4.1 Recovery now say to make one more small edit to each file and commit each alone. Four selftest regressions.
- Expected improvement: a learner who bundled files is told exactly what to do instead of being told it is fine, and false green from padding commits is gone.
- Re-evaluate: yes — when lesson 03 and 04 progress data exists
- Decisions: DL-007 in tools/README.md.

## 2026-09-29 — Markdown checks stop counting text inside code fences
- Observed problem: The lesson 01 and 09 checks ran regular expressions over the raw file, so a profile wrapped in a code fence (shown as text, rendering none of it) passed all thirteen checks, and `**x**` in backticks counted as bold.
- Evidence: adversarial review finding F7: the PROFILE fixture wrapped in a four-backtick fence passed every 01 check. `python tools/selftest.py` wall time at this commit: 15.5s.
- Hypothesis: Structure only counts if it renders; a small line scanner following the CommonMark fence rules is enough for the subset the lessons teach, without a parser dependency.
- Change made: `split_fences` (backtick and tilde fences, closing fence at least as long, unclosed fence runs to end of file) and `strip_inline_code` in `tools/check.py`; code-block rules test the extracted blocks, and the Lesson 09 rule requires an info string. Indented code blocks are not detected (outside the taught subset). Three selftest cases: fenced, unclosed tilde, and a nested example fence.
- Expected improvement: a learner cannot reach green by pasting the exercise inside a code block; rendered-preview checking remains the learner's job.
- Re-evaluate: yes — when lesson 01 and 09 progress data exists
- Decisions: DL-008 in tools/README.md.

## 2026-09-29 — Lesson 07 no longer accepts unpushed local edits as a pull

- Observed problem: `07.remote.pulled` counted reading-list commits on local `main`, so two local commits and no pull passed; `07.remote.pushed` passed whenever `main` was ahead of `origin/main` and gave one message for two different problems.
- Evidence: adversarial review finding F5: push a baseline, make two local reading-list commits, never pull, and lesson 07 passed. `python tools/selftest.py` wall time at this commit: 15.5s.
- Hypothesis: Which folder authored a commit cannot be proven from history, but whether the remote has the commit and whether main contains it can. The rest is learner self-verification and the lesson should say so.
- Change made: `07.remote.pushed`: distinct behind and diverged messages. `07.remote.pulled`: origin/main must carry two learner reading-list commits and main must contain origin/main (stateless, so it survives lessons 08-09 advancing main). `learner_commits` takes a `rev`. Check Your Work states what is checked and points to `git log` for provenance. One selftest regression.
- Expected improvement: a learner who never pulled is sent to the clone, and the lesson does not claim more than the checker verifies.
- Re-evaluate: yes — when lesson 07 progress data exists
- Decisions: DL-009 in tools/README.md.

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
- Hypothesis: "the learner's commits" had been defined by _time_ (a baseline
  recorded on first run), and time is the one thing a learner controls
  freely. Defining it by _content_ — a commit touching learner files and not
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
