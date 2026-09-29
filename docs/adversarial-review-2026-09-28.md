# Adversarial repository review and improvement plan

Date: 2026-09-28. Reviewed commit: `c9c0161`.

## Purpose and intended use

This repository is a self-paced course for people new to Markdown, Git, and terminals. The repository itself is the practice environment: learners read ten lessons, create documents under `workspace/`, build a Git history through commits and branches, practise conflict resolution and local remotes, then complete a documentation capstone.

The standard-library Python tooling provides two services: `check.py` checks exercise artifacts and records local progress; `review.py` aggregates that progress into proposed curriculum improvements. `validate_curriculum.py` checks curriculum structure and `selftest.py` simulates a learner in a temporary repository. It is an educational system, not a production application or a formal assessment of competence.

## Verdict and scope

The course has a coherent sequence, concrete exercises, and useful inspection-oriented feedback. The current implementation does not justify treating a green checker as proof that an exercise was completed correctly, or treating the generated curriculum findings as reliable evidence of learning difficulty. Repair mutation safety and assessment correctness before tuning the curriculum from those findings.

Reviewed the five Python tools, curriculum metadata, lesson and supporting documentation. Ran existing checks and targeted adversarial probes in temporary repositories. No learner files, actual repository branches, commits, remotes, or progress records were modified. Only this review document was added to the repository. This is a local behavioral and source review, not a cross-platform certification or an exhaustive security audit.

## Validation

Environment: Python 3.14.7; Git 2.55.0.

- `python3 tools/validate_curriculum.py`: passed; 10 lessons, 51 checks, zero reported problems.
- `python3 tools/selftest.py`: passed; all simulated lessons and the review-tool checks passed.
- Additional temporary-repository probes reproduced the failures below. Existing passing tests therefore do not cover these cases.

## Prioritized errors

### F1 — P1: Conflict setup captures unrelated staged work

Source: `tools/setup_conflict.py:34-35,46-53`.

The preflight checks only `workspace/favorites.md`, but plain `git commit` includes the entire index. With an unrelated file already staged, running the helper returned zero and committed both `workspace/favorites.md` and `workspace/unrelated.md` on `conflict-practice`. Returning to `main` removes that unrelated new file from the working tree because it now exists only on the practice branch. The lesson explicitly promises that the helper touches nothing else.

Fix: require a clean tracked working tree and index before mutation, allowing the intentional untracked scratch file; inspect the exact staged path set before committing. Refuse without mutation if unrelated staged work exists. Never automatically unstage, restore, or reset the user's work.

Acceptance: staged unrelated files, staged deletions, and partially staged edits retain identical index, working-tree, HEAD, and branch state after refusal.

### F2 — P1: Failed Git operations are reported as successful setup

Source: `tools/setup_conflict.py:46-57`.

The helper ignores the return codes from branch creation, staging, committing, and switching back. A temporary pre-commit hook that exits 1 caused the helper to return zero and print that it created a commit. HEAD was unchanged and `favorites.md` remained staged on `main`.

Fix: check each result and stop at the first failure; preserve stderr in the explanation; report the actual branch/index state and a recovery path. Verify final postconditions before printing success. Do not attempt destructive rollback.

Acceptance: injected failures at each mutation produce nonzero exit status, no false success message, and no execution of later mutation steps.

### F3 — P2: A valid conflict resolution fails Lesson 06

Source: `tools/check.py:77-81,345-349`; Lesson 06 explicitly permits either side of the conflict.

`merge_touching()` requires the result to differ from its first parent. Resolving a real conflict by keeping the version already on `main` produces a legitimate merge commit with no such difference. Reproduced: choose red from `main`, commit the resolution, delete the practice branch; checker says “no merge commit involving favorites.md.” The self-test always chooses a third color and misses this.

Fix: inspect both merge parents and the relevant path's history, and verify that the merge is reachable from the intended target branch. Accept ours, theirs, and a combined resolution without requiring a first-parent content change.

Acceptance: all three permitted resolutions pass; unfinished merges and commits containing conflict markers fail.

### F4 — P2: Progress collection creates misleading curriculum findings

Source: `tools/check.py:547-565,635-645`; `tools/review.py:58-87`.

Three reproduced counterexamples:

- Completing the work before the first checker run sets `started` and `completed` together; the review counts this as a “trivial pass” in under a minute. Time spent learning was never measured.
- A first-attempt pass followed by three failed rechecks is reported as four attempts before the first pass. The aggregate uses lifetime failures plus one.
- Checking all ten untouched lessons creates ten records; nine are subsequently counted as abandoned because a higher-numbered record exists. The implementation of `all` checks the entire curriculum despite README's “everything so far” description.

Prescribed partial checks and the Lesson 00 preview of Lesson 01 also create failures that do not necessarily indicate confusion.

Fix: distinguish previews, partial exercise checks, assessment attempts, and rechecks. Persist first-pass counters at first completion. Treat learning duration as unknown without an explicit start event; do not derive abandonment from record presence alone. Version the schema and preserve uncertainty for old records. Until corrected, suspend “trivial,” “abandoned,” and first-pass difficulty recommendations based on these measurements.

Acceptance: preview/all runs cannot manufacture abandonment; rechecks cannot change historical first-pass counts; absence of a start event cannot imply a short learning time.

### F5 — P2: Lesson 07 certifies a remote workflow that was not performed

Source: `tools/check.py:376-390`; Lesson 07's Check Your Work promises matching refs and a commit arriving from the remote.

The push check only requires `origin/main` to be an ancestor of `main`. The pull check merely counts commits touching the reading list. Reproduced: push a baseline to a real local bare remote, then make two reading-list commits locally, without cloning or pulling. All three Lesson 07 checks pass while `main` is ahead of `origin/main`.

Fix: align the lesson's completion-time equality requirement with the checker. Separate a one-time Lesson 07 assessment from later regression checks, since Lessons 08–09 legitimately advance `main` again. Ordinary final Git history alone does not prove which clone authored a commit or whether a pull command was used: add an explicit checkpoint if needed, or accurately label this part as learner verification rather than machine-certified provenance. Keep routine checking offline.

Acceptance: local-only edits cannot be described as proof of pull; ahead/behind/diverged states have accurate feedback; completing later lessons does not invalidate an already completed remote exercise solely because new local commits exist.

### F6 — P2: Commit counts do not enforce separate commits

Source: `tools/check.py:263-269,291-296`.

Lesson 03 checks total learner commit count rather than distinct commits for hello, profile, and notes. Reproduced: one bundled commit of all required files, plus an unrelated favorites commit and one empty commit, passes every Lesson 03 check. Lesson 04 similarly counts each path independently, so a combined edit commit can satisfy both path counts.

Fix: examine changed path sets and distinct commit IDs for the exercise outcomes. Exclude unrelated and empty commits from exercise-specific counts. Keep any pedagogical tolerance for accidental bundling explicit in both lesson and check behavior.

Acceptance: unrelated commits cannot satisfy the requirement; the prescribed separate-commit workflow passes; recovery instructions and acceptance rules agree.

### F7 — P2: Markdown checks count literal examples as rendered structures

Source: `tools/check.py:158-193,449-470`.

The regex checks run over raw text without respecting fenced code. Wrapping the entire valid profile fixture in a four-backtick text block still passes all 13 Lesson 01 checks. The document is one literal code block, not a profile with rendered headings, lists, emphasis, and links. This is especially relevant to learners who accidentally paste an outer example fence.

Fix: distinguish prose, inline code, and fenced blocks before checking structures. With the repository's standard-library-only constraint, support a clearly documented Markdown subset and explicitly require visual verification for unsupported syntax. Any third-party parser requires a separate dependency decision. Test valid alternatives as well as false positives; the bold patterns also demand more than one character.

Acceptance: a whole-profile code block fails structural checks; valid taught syntax passes; nested example fences do not confuse the checker.

### F8 — P2: Scratch-file recovery cannot reach the required state as written

Source: `lessons/04-everyday-git/README.md:322-330`; `tools/check.py:306-312`.

The lesson says that after accidentally committing scratch.md, deleting it and committing the deletion, or creating a different scratch file, lets the checker see the intended state. The checker requires the exact path `workspace/scratch.md` to exist and be untracked. Reproduced the deletion-and-commit path: it fails because the file is missing. A differently named scratch file cannot satisfy it either.

Fix: add the missing step to recreate the same path after committing its deletion, without staging it; alternatively teach a scoped removal from the index with a clear explanation. Keep recovery non-destructive to the contents the learner wants to preserve.

Acceptance: follow the recovery steps literally from a committed scratch file and get a passing check.

### F9 — P2: Malformed progress is silently replaced with empty history

Source: `tools/check.py:532-544`; `tools/review.py:26-38,47-54`.

`load_progress()` treats malformed JSON the same as a missing file. The next save overwrites it with a fresh record. Reproduced a malformed progress file followed by load/save: it became the default empty history without a warning. Writes also truncate the destination in place, and decoded data is not schema-validated.

Fix: distinguish absent, unreadable, malformed, and unsupported-schema data. Preserve existing invalid data and explain recovery. Write a validated new record to a sibling temporary file and atomically replace the target. Validate imported report records before aggregation; do not silently accept arbitrary JSON shapes.

Acceptance: malformed or incompatible files remain available for recovery; simulated interrupted writes retain the previous valid record; bad report inputs receive actionable errors.

## Error correction plan

| Order | Work package | Completion gate |
|---|---|---|
| 1 | Helper safety: F1 and F2 | No unrelated changes; fail-fast behavior and truthful postconditions under injected Git errors |
| 2 | Learner blockers: F3 and F8 | Every documented conflict choice and scratch recovery passes in an isolated fixture |
| 3 | Assessment correctness: F5–F7 | Tests reject the demonstrated incomplete work while accepting documented valid work; later lessons remain compatible |
| 4 | Progress integrity: F9 | Schema validation, preserved malformed files, atomic writes, and tested migration behavior |
| 5 | Evidence quality: F4 | Explicit first-pass metrics and check intent; old data labeled insufficient where necessary |
| 6 | Documentation alignment | Match every Check Your Work claim to an implemented assertion or clearly identified manual reflection |

Make focused changes and update both changelogs for curriculum changes, as required by CONTRIBUTING.md. Avoid invalidating the active learner's exercise; use additive changes or queue incompatible ones. Run both existing validation commands after each coherent change. Add targeted regressions, not another copy of the same happy-path walkthrough.

## Optimization plan

### Strengthen test evidence first

- Test individual check IDs with both accepted and rejected cases. The current pre-exercise failure proves only that at least one check failed, not that every check detects its intended defect.
- Distinguish checker exit 1 from setup/usage errors and crashes: `selftest.py:50-54` currently treats every nonzero exit as an expected exercise failure.
- Isolate Git configuration in tests, including hooks, signing, branch defaults, and pull strategy. Test a clone-based installation as well as the synthetic `git init` setup.
- Add a lightweight CI job for the standard-library suite, including the declared minimum Python version and a current version. Windows/Linux execution was not validated in this review.

### Reduce repeated history work after correctness is fixed

`learner_commits()` repeatedly walks history and invokes `git show` once per candidate to classify it; multiple checks repeat those queries. Cache immutable commit metadata within one checker process or collect changed paths in a batch. Measure subprocess count and runtime on a representative longer learning history first; no speedup is claimed here. Do not add persistent cache invalidation machinery for a ten-lesson course without measured need.

### Improve the curriculum feedback loop

- Compare normalized rates and sample sizes, not raw fail totals across lessons with different numbers of checks and prescribed intermediate runs.
- Keep classifier causes as hypotheses. “No hints means a strict check” and “many checks means an oversized lesson” are weak proxies, even after the underlying counters are repaired.
- Preserve reports with timestamps or run IDs and record curriculum revision/schema version. `review.py:231-234` currently overwrites a same-day report, undermining before/after comparison.
- Add an explicit manual reflection/preview gate for understanding and document quality. Static artifacts cannot establish independent competence or prove the learner actually performed every transient action.

### Clarify operating assumptions

- Define clone/setup instructions, expected branch, and minimum Git capability rather than assuming any existing main branch identifies this course.
- Narrow blanket claims that abort/restore operations can never lose work; include clean-state preconditions for drills and recovery instructions.
- Use Git plumbing to locate merge state instead of assuming `.git` is a directory, if linked-worktree support is intended.
- Define a stable course baseline. Classifying every commit touching a curriculum directory as “maintainer” also hides accidental learner edits once committed; a docs-only maintainer commit outside those directories can be classified as learner work.
- Audit the remaining completion assertions: Lesson 08 only requires two Markdown files although its steps request README, usage/install, and changelog; the capstone branch check tests unmerged branches rather than deletion of the completed branch; a glossary commit does not prove that a term was added.

These are follow-up opportunities identified by source inspection. The numbered findings above carry the direct adversarial reproduction evidence.
