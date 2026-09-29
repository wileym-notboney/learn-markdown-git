# tools/

Checker, selftest, review, and helper scripts. Python standard library only.

## Invariants

- A false green is worse than a false red. A learner reads a passing check
  as "move on", so a check that passes without the promised work misleads
  more than one that is too strict.
- Checks assert final state; lessons promise process. Tighten a check where
  Git history carries evidence of the process (per-path commits, both merge
  parents). Where history cannot carry it (for example, that a pull
  happened), the lesson labels the step as learner-verified instead of the
  check pretending to prove it.
- `review.py` findings drive curriculum edits. A metric the progress data
  does not support (learning time, abandonment) sends maintainers to rewrite
  the wrong lesson, so unsupported signals are not reported.
- Helpers that touch a learner's repository report state and stop on the
  first Git failure. They never reset, restore, or discard learner work.
- `tools/selftest.py` holds one regression per checker or helper defect,
  each building its own temporary course. A nonzero exit other than 1 from
  `check.py` is a harness error, not an expected exercise failure.

## Decision log

Code comments in `tools/*.py` and entries in `../CURRICULUM_CHANGELOG.md`
cite these IDs as `DL-nnn`.

### DL-002

Regression vehicle is selftest.py: one named function per finding that builds its own temporary course and asserts the specific check id outcome.

Reasoning: stdlib-only rule excludes pytest -> the shared happy-path Learner accumulates state so a negative case mid-walk would corrupt later lessons -> each regression gets a fresh setup(tmp) fixture and asserts on the check id line in stdout, not only the exit code.

### DL-003

Learner.check treats exit 1 as exercise failure and any other nonzero exit as a harness error.

Reasoning: check.py returns 2 for usage/operational errors and a traceback exits 1 only via uncaught exception text on stderr -> a crash currently reads as an expected fail -> regressions asserting fail would pass on a crash -> require returncode in (0,1) and empty stderr traceback before comparing.

### DL-004

setup_conflict.py refuses unless the index and all tracked files are clean (untracked files allowed); every git call is checked and the first failure stops with stderr and an inspect/recover hint; success is printed only after verifying branch tip content and that HEAD is back on main.

Reasoning: plain git commit takes the whole index (F1) -> path-scoped preflight is insufficient -> a whole-tree porcelain check excluding ?? lines is the smallest correct gate; ignored return codes produced false success (F2) -> fail-fast with no rollback keeps learner work untouched as the review requires.

### DL-005

merge_touching(path, both_sides=True) selects learner merge commits where the path differs from the merge base on both parents; Lesson 09 keeps the first-parent test.

Reasoning: a conflict exists only when both sides changed the path -> keeping main side leaves h^1 == h on that path so the first-parent test rejects a valid resolution (F3) -> comparing h^1 with h^2 is non-empty when only one side changed the path, so a conflict-free --no-ff merge would pass 06.merge.commit -> requiring base..h^1 and base..h^2 both non-empty holds for ours, theirs and combined and rejects one-sided merges -> the capstone merge changes CAP on the branch side only, so 09.merge.branch keeps the first-parent test via the default both_sides=False.

### DL-006

Lesson 04 scratch recovery teaches git rm --cached workspace/scratch.md then a commit; the checker rule is unchanged.

Reasoning: delete-and-commit leaves the file missing so 04.scratch.untracked can never pass (F8) -> rm --cached removes it from tracking while keeping the file on disk -> the literal steps reach exists+untracked+unstaged without destroying learner content and without loosening the check.

### DL-007

Separate-commit checks count learner commits that touch the target path and none of the sibling exercise paths; lesson 04 Exercise 4.1 Recovery is reworded so a bundled commit can still reach the checked state.

Reasoning: total-count check passes one bundled commit plus unrelated commits (F6) -> per-path exclusive commits encode one thing per commit directly -> git log -- path already drops empty commits and unrelated paths -> Lesson 03 needs one exclusive commit each for hello/profile/notes; Lesson 04 needs two exclusive commits each for profile.md and notes/README.md relative to each other -> current 4.1 Recovery (Committed both together? do the next exercise commits separately) leaves only one exclusive commit per file (lesson 04 has only Exercises 4.1-4.3, none adding more), so 04.commits.two-more could never pass; likewise 3.2 Recovery (committed both together is acceptable, move on) leaves 03.commit.separate unpassable -> both Recovery texts must tell the learner to make one further small edit to each file and commit each on its own.

### DL-008

Markdown structural checks run over prose with top-level fenced blocks removed and inline code spans blanked; code-block checks run over the extracted top-level fences; backtick and tilde fences and unclosed fences follow CommonMark; indented (4-space) code blocks are outside the taught subset and not treated as code.

Reasoning: regexes over raw text count a fenced example as rendered structure (F7) -> a line scanner that tracks fence char (backtick or tilde) and length (CommonMark closing rule: same char and >= opening length) handles nested four-backtick examples in ~20 stdlib lines -> CommonMark runs an unclosed fence to end of document, so the scanner treats everything after an unclosed opener as code (no false green from a forgotten closer) -> lessons teach only fenced code blocks, and indented-block detection needs list/paragraph context the scanner does not model, so indented blocks are explicitly excluded (their text counts as prose; accepted false-red risk, consistent with false red over false green) -> no parser dependency needed -> inline code blanked so backticked **x** is not bold.

### DL-009

Lesson 07 checks are stateless: pushed = origin/main exists and is an ancestor of main with distinct ahead/behind/diverged messages; pulled = origin/main carries at least two learner commits touching reading-list.md and main contains origin/main.

Reasoning: requiring main == origin/main would fail after Lessons 08-09 advance main and would need progress coupling -> requiring the second reading-list commit to be on origin/main rejects unpushed local edits (F5 repro) while surviving later lessons -> which clone authored a commit is unprovable from history -> lesson text labels provenance as learner self-verification.

### DL-010

load_progress distinguishes missing (default record) from unreadable/malformed/wrong-shape (print path + reason + recovery; main returns 2 without writing); save_progress writes a sibling temp file then os.replace.

Reasoning: malformed JSON is silently replaced by empty history on next save (F9) -> refusing to proceed preserves the file for recovery -> same-directory temp + os.replace is atomic on POSIX and Windows -> review.load applies the same shape validation and skips bad records with a named reason.

### DL-011

Metrics fix without schema version: check.py all is read-only; failing runs after completion increment rechecks only; first completion freezes fails_before_pass; review.py drops trivial and abandoned signals and computes hard-to-pass only from fails_before_pass.

Reasoning: started/completed timestamps cannot measure learning time and record presence cannot prove abandonment (F4) -> deleting the unsupported signals is smaller and more honest than a v2 schema -> additive keys read with .get keep v1 files valid -> records lacking fails_before_pass are excluded from attempts, i.e. unknown rather than guessed.

### DL-012

No selftest runtime threshold is set; each milestone commit records the measured python tools/selftest.py wall time in its CURRICULUM_CHANGELOG.md evidence line, and runtime work is deferred unless a maintainer reports it as a problem.

Reasoning: no user instruction or project doc sets a runtime budget and docs/error-remediation-plan.md defers runtime optimization -> inventing a ~60s threshold would be an unbacked policy default -> fresh fixtures accumulate across M-002..M-009, so a single M-001 measurement is only a baseline -> recording the measured time at every milestone makes growth visible without a threshold.

### DL-014

CURRICULUM_REVIEW.md is added to the scope of M-009 to remove the timestamp-derived signal rows.

Reasoning: CURRICULUM_REVIEW.md documents the trivial/abandoned signals that DL-011 deletes from review.py -> leaving them would describe metrics the tool no longer produces and steer maintainers to rewrite lessons from non-existent data -> CONTRIBUTING.md requires checks and their docs to change together -> the task_spec scope list omitted this file only because it was not in the adversarial-review entry points, so extending scope by one doc file is the minimal consistent fix.
