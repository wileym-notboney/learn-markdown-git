# Plan

## Overview

check.py reports green for work the lessons promise but the learner did not do (F3 inverse, F5, F6, F7), the conflict helper can commit unrelated learner work and report false success (F1, F2), lesson 04 recovery text cannot reach the checked state (F8), progress.json is silently replaced when malformed (F9), and review.py derives trivial/abandoned/first-pass findings from data that cannot support them (F4). Both gates pass at c9c0161 because selftest only walks the happy path and treats any nonzero checker exit as an expected fail.

**Approach**: Nine sequential milestones, one finding-concern each and one commit each. M-001 hardens the selftest harness so every later regression fails on a crash rather than masquerading as an expected fail. Each later milestone adds one targeted selftest regression in its own temporary course, then the smallest code or lesson-text change that makes it pass, then entries in CHANGELOG.md and CURRICULUM_CHANGELOG.md. Checks are tightened where Git history carries evidence (separate commits, fences, remote contents, merge parents) and relabelled as learner self-verification where it cannot (clone provenance). No schema version, no caching, no new dependencies.

## Planning Context

### Decision Log

| ID | Decision | Reasoning Chain |
|---|---|---|
| DL-001 | Nine sequential milestones; one finding-concern per milestone and per commit; files may repeat across milestones | CLAUDE.md requires one lesson concern per commit and gates before every commit -> check.py hosts six of the nine findings -> a file-disjoint split would bundle unrelated fixes into one unreviewable commit -> sequential milestones sharing check.py/selftest.py/changelogs with one gate run each |
| DL-002 | Regression vehicle is selftest.py: one named function per finding that builds its own temporary course and asserts the specific check id outcome | stdlib-only rule excludes pytest -> the shared happy-path Learner accumulates state so a negative case mid-walk would corrupt later lessons -> each regression gets a fresh setup(tmp) fixture and asserts on the check id line in stdout, not only the exit code |
| DL-003 | Learner.check treats exit 1 as exercise failure and any other nonzero exit as a harness error | check.py returns 2 for usage/operational errors and a traceback exits 1 only via uncaught exception text on stderr -> a crash currently reads as an expected fail -> regressions asserting fail would pass on a crash -> require returncode in (0,1) and empty stderr traceback before comparing |
| DL-004 | setup_conflict.py refuses unless the index and all tracked files are clean (untracked files allowed); every git call is checked and the first failure stops with stderr and an inspect/recover hint; success is printed only after verifying branch tip content and that HEAD is back on main | plain git commit takes the whole index (F1) -> path-scoped preflight is insufficient -> a whole-tree porcelain check excluding ?? lines is the smallest correct gate; ignored return codes produced false success (F2) -> fail-fast with no rollback keeps learner work untouched as the review requires |
| DL-005 | merge_touching(path, both_sides=True) selects learner merge commits where the path differs from the merge base on both parents; Lesson 09 keeps the first-parent test | a conflict exists only when both sides changed the path -> keeping main side leaves h^1 == h on that path so the first-parent test rejects a valid resolution (F3) -> comparing h^1 with h^2 is non-empty when only one side changed the path, so a conflict-free --no-ff merge would pass 06.merge.commit -> requiring base..h^1 and base..h^2 both non-empty holds for ours, theirs and combined and rejects one-sided merges -> the capstone merge changes CAP on the branch side only, so 09.merge.branch keeps the first-parent test via the default both_sides=False |
| DL-006 | Lesson 04 scratch recovery teaches git rm --cached workspace/scratch.md then a commit; the checker rule is unchanged | delete-and-commit leaves the file missing so 04.scratch.untracked can never pass (F8) -> rm --cached removes it from tracking while keeping the file on disk -> the literal steps reach exists+untracked+unstaged without destroying learner content and without loosening the check |
| DL-007 | Separate-commit checks count learner commits that touch the target path and none of the sibling exercise paths; lesson 04 Exercise 4.1 Recovery is reworded so a bundled commit can still reach the checked state | total-count check passes one bundled commit plus unrelated commits (F6) -> per-path exclusive commits encode one thing per commit directly -> git log -- path already drops empty commits and unrelated paths -> Lesson 03 needs one exclusive commit each for hello/profile/notes; Lesson 04 needs two exclusive commits each for profile.md and notes/README.md relative to each other -> current 4.1 Recovery (Committed both together? do the next exercise commits separately) leaves only one exclusive commit per file (lesson 04 has only Exercises 4.1-4.3, none adding more), so 04.commits.two-more could never pass; likewise 3.2 Recovery (committed both together is acceptable, move on) leaves 03.commit.separate unpassable -> both Recovery texts must tell the learner to make one further small edit to each file and commit each on its own |
| DL-008 | Markdown structural checks run over prose with top-level fenced blocks removed and inline code spans blanked; code-block checks run over the extracted top-level fences; backtick and tilde fences and unclosed fences follow CommonMark; indented (4-space) code blocks are outside the taught subset and not treated as code | regexes over raw text count a fenced example as rendered structure (F7) -> a line scanner that tracks fence char (backtick or tilde) and length (CommonMark closing rule: same char and >= opening length) handles nested four-backtick examples in ~20 stdlib lines -> CommonMark runs an unclosed fence to end of document, so the scanner treats everything after an unclosed opener as code (no false green from a forgotten closer) -> lessons teach only fenced code blocks, and indented-block detection needs list/paragraph context the scanner does not model, so indented blocks are explicitly excluded (their text counts as prose; accepted false-red risk, consistent with false red over false green) -> no parser dependency needed -> inline code blanked so backticked **x** is not bold |
| DL-009 | Lesson 07 checks are stateless: pushed = origin/main exists and is an ancestor of main with distinct ahead/behind/diverged messages; pulled = origin/main carries at least two learner commits touching reading-list.md and main contains origin/main | requiring main == origin/main would fail after Lessons 08-09 advance main and would need progress coupling -> requiring the second reading-list commit to be on origin/main rejects unpushed local edits (F5 repro) while surviving later lessons -> which clone authored a commit is unprovable from history -> lesson text labels provenance as learner self-verification |
| DL-010 | load_progress distinguishes missing (default record) from unreadable/malformed/wrong-shape (print path + reason + recovery; main returns 2 without writing); save_progress writes a sibling temp file then os.replace | malformed JSON is silently replaced by empty history on next save (F9) -> refusing to proceed preserves the file for recovery -> same-directory temp + os.replace is atomic on POSIX and Windows -> review.load applies the same shape validation and skips bad records with a named reason |
| DL-011 | Metrics fix without schema version: check.py all is read-only; failing runs after completion increment rechecks only; first completion freezes fails_before_pass; review.py drops trivial and abandoned signals and computes hard-to-pass only from fails_before_pass | started/completed timestamps cannot measure learning time and record presence cannot prove abandonment (F4) -> deleting the unsupported signals is smaller and more honest than a v2 schema -> additive keys read with .get keep v1 files valid -> records lacking fails_before_pass are excluded from attempts, i.e. unknown rather than guessed |
| DL-012 | No selftest runtime threshold is set; each milestone commit records the measured python tools/selftest.py wall time in its CURRICULUM_CHANGELOG.md evidence line, and runtime work is deferred unless a maintainer reports it as a problem | no user instruction or project doc sets a runtime budget and docs/error-remediation-plan.md defers runtime optimization -> inventing a ~60s threshold would be an unbacked policy default -> fresh fixtures accumulate across M-002..M-009, so a single M-001 measurement is only a baseline -> recording the measured time at every milestone makes growth visible without a threshold |
| DL-013 | Planning assumptions are recorded with evidence: A1 selftest fixtures as test vehicle (backed by CLAUDE.md stdlib-only rule, DL-002); A2 lesson 07 stateless rule (DL-009, RA-003); A3 deleting trivial/abandoned instead of schema versioning (DL-011, RA-001, adversarial-review F4); A4 no active learner - verified 2026-09-29 that .learning/ is empty, and M-004, M-005, M-007 each re-verify it as their first step | CLAUDE.md forbids changing an exercise a learner is actively completing (current_lesson in .learning/progress.json) -> M-004, M-005 and M-007 change lesson 04 and 07 exercises and checks -> the assumption held at planning time (.learning/ empty) but can change before execution -> each of those milestones starts by reading .learning/progress.json and stops (queue the change) if current_lesson is 04 or 07 |
| DL-014 | CURRICULUM_REVIEW.md is added to the scope of M-009 to remove the timestamp-derived signal rows | CURRICULUM_REVIEW.md documents the trivial/abandoned signals that DL-011 deletes from review.py -> leaving them would describe metrics the tool no longer produces and steer maintainers to rewrite lessons from non-existent data -> CONTRIBUTING.md requires checks and their docs to change together -> the task_spec scope list omitted this file only because it was not in the adversarial-review entry points, so extending scope by one doc file is the minimal consistent fix |

### Rejected Alternatives

| Alternative | Why Rejected |
|---|---|
| Execute the 30-task docs/error-remediation-plan.md including progress schema v2 and migration | No learner data exists to migrate; additive .get-read keys plus deleting unsupported signals meet F4/F9 acceptance with far less code (ref: DL-011) |
| Third-party Markdown parser for F7 | Violates stdlib-only rule; a fence/inline-span scanner covers the taught subset (ref: DL-008) |
| Require main == origin/main for lesson 07, remembered via progress once completed | Couples a pure check to progress state and breaks check all after lessons 08-09; the origin/main-carries-second-commit rule rejects the repro statelessly (ref: DL-009) |
| Prove pull provenance via reflog or commit author | Reflog is local and expirable; learners use one identity in both folders; history cannot prove which clone authored a commit (ref: DL-009) |
| Loosen 04.scratch.untracked to accept a missing or differently named scratch file | Weakens the unstaging concept check; fixing the lesson text with git rm --cached keeps the rule and preserves file contents (ref: DL-006) |
| setup_conflict.py rolls back (reset/restore) after a failed step | Destructive recovery on learner state is forbidden by CLAUDE.md; report state and stop instead (ref: DL-004) |
| Scope setup_conflict commit with git commit -- workspace/favorites.md instead of refusing | Still switches branches with unrelated staged/modified work in the tree, and a partially staged favorites.md would be committed differently than the learner staged; refusing is simpler and never surprises (ref: DL-004) |

### Constraints

- C-001 (technical, doc-derived): Python standard library only
- C-002 (organizational, doc-derived): Never touch learner-owned workspace/, GLOSSARY.md, .learning/ of the real checkout; all mutation happens in selftest temp fixtures
- C-003 (organizational, doc-derived): python tools/validate_curriculum.py and python tools/selftest.py exit 0 before each commit
- C-004 (organizational, doc-derived): Each commit stages CHANGELOG.md and adds a CURRICULUM_CHANGELOG.md entry; commit style type(scope): description; one concern per commit
- C-005 (organizational, doc-derived): No history rewriting; helpers never reset/restore/unstage learner work
- C-006 (organizational, doc-derived): Do not change an exercise that is current_lesson in .learning/progress.json; M-004, M-005, M-007 verify this first (.learning/ verified empty 2026-09-29; DL-013)

### Known Risks

- **git rev-parse ranges in merge_touching error on root/octopus merges**: git() already returns empty on failure, so such commits are simply not counted
- **Per-regression fresh fixtures lengthen selftest runtime (each setup copies the course and commits)**: No runtime threshold (no user or doc budget; DL-012). Every milestone commit, M-001 through M-009, records measured selftest wall time in its CURRICULUM_CHANGELOG.md evidence line so growth from accumulating fixtures is visible; runtime work is deferred unless a maintainer reports it
- **Pre-commit hook fixture is POSIX-specific**: Hook case skips on os.name == nt with a printed note; other F2 steps still covered on POSIX CI-less runs
- **Stripping fences changes 01/09 outcomes for learners whose files relied on raw-text matches**: Only literal examples lose credit; valid taught syntax passes; changelog entry names the behaviour change
- **Lesson 00 still previews lesson 01 with a recorded check run (prescribed partial checks remain in progress data)**: Out of scope here; rechecks no longer inflate fails after completion and review no longer derives abandonment, so the residual effect is a few pre-pass fails in lesson 01 counts

## Invisible Knowledge

### System

check.py registers (lesson, id, concept, desc, fn) checks; fn returns None or a (problem, look, try) triple. review.py maps failed check ids to concepts and turns progress.json counters into curriculum findings. selftest.py walks every lesson in a temp copy.

### Invariants

- A green check means the lesson's promised outcome is visible in files or history; anything history cannot prove is labelled learner-verified in the lesson text
- Helpers and checks never reset, restore, unstage or rewrite learner work; on failure they report state and stop
- Every check function is pure over the repository state: no reads of progress.json
- Learner commits are identified by content (touch learner paths, not curriculum paths), never by time
- Progress data that cannot be validated is never overwritten

### Tradeoffs

- False red is preferred over false green: learners read green as move on
- Stateless lesson 07 rule accepts a learner who pushes two local commits then pulls nothing; provenance is explicitly learner-verified instead of pretending to prove it
- Markdown scanner supports only the taught subset; full CommonMark and rendered-preview judgement stay manual
- F4 fixed by removing unsupported metrics rather than versioning the schema; old records lacking fails_before_pass count as unknown

## Milestones

### Milestone 1: Selftest distinguishes checker failure from checker crash

**Files**: tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- Learner.check raises on exit codes other than 0 and 1
- Learner.check raises when stderr contains a Python traceback
- a helper returns the stdout line for one check id so regressions assert on a specific id
- measured selftest wall time is recorded in each milestone CURRICULUM_CHANGELOG.md entry (DL-012)

**Acceptance Criteria**:

- python tools/selftest.py exits 0
- temporarily making check.py raise at import makes selftest fail with a harness error instead of an expected fail

**Tests**:

- selftest.py harness self-assertion

#### Code Intent

- **CI-M-001-001** `tools/selftest.py::Learner.check`: Run check.py; if returncode not in (0, 1) or 'Traceback' in stderr raise RuntimeError('checker crashed') with stdout+stderr; else compare pass/fail with expect as before. Add Learner.line(out, cid) returning the stdout line whose second token is cid (ok/-- status) so regressions assert per check id. Add a fresh_course(tmp, name) helper that runs setup() into tmp/name so each regression owns its fixture; setup() takes the target root. (refs: DL-002, DL-003)
- **CI-M-001-002** `CHANGELOG.md`: Unreleased/Fixed entry: selftest reports a checker crash as a harness error instead of an expected exercise failure. CURRICULUM_CHANGELOG.md gets a matching entry (observed problem, evidence, hypothesis, change, expected improvement, re-evaluate) for every milestone; each milestone adds one entry to both changelogs, and each CURRICULUM_CHANGELOG.md evidence line records the measured wall time of python tools/selftest.py for that commit (no threshold). (refs: DL-001, DL-012)

#### Code Changes

**CC-M-001-001** (tools/selftest.py) - implements CI-M-001-001

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -49,15 +49,21 @@
 
     def check(self, lesson, expect):
         r = subprocess.run([PY, "tools/check.py", lesson], cwd=self.root, capture_output=True, text=True)
+        if r.returncode not in (0, 1) or "Traceback" in r.stderr:
+            raise RuntimeError(f"checker crashed on lesson {lesson}:\n{r.stdout}{r.stderr}")
         got = "pass" if r.returncode == 0 else "fail"
         if got != expect:
             raise AssertionError(f"lesson {lesson}: expected {expect}, got {got}\n{r.stdout}{r.stderr}")
         print(f"  lesson {lesson}: {expect} as expected")
         return r.stdout
 
-
-def setup(tmp):
-    root = os.path.join(tmp, "course")
+    @staticmethod
+    def line(out, cid):
+        """The check.py output line for one check id; its first word is 'ok' or '--'."""
+        return next(ln for ln in out.splitlines() if ln.split()[1:2] == [cid])
+
+
+def setup(root):
     shutil.copytree(SRC, root, ignore=shutil.ignore_patterns(".git", ".learning", "docs", "__pycache__"))
     l = Learner(root)
     l.git("init", "-q")
@@ -69,6 +75,11 @@
     l.append("lessons/00-orientation/README.md", "\n<!-- maintainer edit after release -->\n")
     l.commit("fix(lesson-00): maintainer edit that must not count as learner work", "lessons/00-orientation/README.md")
     return l
+
+
+def fresh_course(tmp, name):
+    """A new course in tmp/name, so a regression owns its fixture."""
+    return setup(os.path.join(tmp, name))
 
 
 PROFILE = """# Ada
@@ -320,7 +331,7 @@
 def main():
     with tempfile.TemporaryDirectory() as tmp:
         print("Simulating a learner in a temporary copy...")
-        l = setup(tmp)
+        l = setup(os.path.join(tmp, "course"))
         protected_files(l)
         commits_before_first_check(l)
         next_step_moves_forward(l)

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -51,2 +51,5 @@
         r = subprocess.run([PY, "tools/check.py", lesson], cwd=self.root, capture_output=True, text=True)
+        # check.py exits 1 for an unmet exercise and 2 for an operational error. Any other
+        # status, or a traceback, is a harness fault: reading a crash as an expected fail
+        # would let a regression pass on it. (ref: DL-003)
         if r.returncode not in (0, 1) or "Traceback" in r.stderr:

```

> **Developer notes**: Apply changes in order within the milestone; diffs were generated from a sequential scratch copy and tools/selftest.py plus validate_curriculum.py passed after each milestone. Wall times recorded in each CURRICULUM_CHANGELOG entry were measured on the scratch copy (6.6s, 7.9s, 10.1s, 10.6s, 13.2s, 14.6s, 14.3s, 15.0s, 15.9s); re-measure at real commit time and correct the number if it differs. 

**CC-M-001-002** (CHANGELOG.md) - implements CI-M-001-002

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -15,6 +15,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   checked, and says so when every lesson is complete.
 - Checks that need a missing file now report the missing file instead of
   describing its contents.
+- `selftest.py` reports a checker crash as a harness error instead of an
+  expected exercise failure.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -18,1 +18,1 @@
 - `selftest.py` reports a checker crash as a harness error instead of an

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-001-003** (CURRICULUM_CHANGELOG.md) - implements CI-M-001-002

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -16,6 +16,14 @@ Entry template:
 - Re-evaluate: yes/no — when
 ```
 
+## 2026-09-29 — Selftest tells a checker crash from an expected failure
+- Observed problem: `Learner.check` treated any nonzero exit as "fail", so a regression that expects a failing check also passed when `check.py` crashed.
+- Evidence: adversarial review of 2026-09-28: a `check.py` that raises at import makes every expected-fail assertion pass. `python tools/selftest.py` wall time at this commit: 6.6s.
+- Hypothesis: Only exit codes 0 and 1 without a traceback on stderr mean pass or fail; everything else is the harness failing.
+- Change made: `Learner.check` raises on other exit codes or a traceback; added `Learner.line` (output line for one check id) and `fresh_course` (one fixture per regression) for the regressions that follow.
+- Expected improvement: a broken checker fails selftest loudly instead of looking like an exercise that has not been done yet.
+- Re-evaluate: no
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -25,1 +25,2 @@
 - Re-evaluate: no
+- Decisions: DL-002, DL-003 in tools/README.md.

```


### Milestone 2: F1 F2 conflict helper refuses unrelated work and fails fast

**Files**: tools/setup_conflict.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- refuse without mutation when any tracked file is modified or any path is staged
- untracked files do not block
- each git mutation is return-code checked and the first failure exits 1 with git stderr and state/recovery text
- success text prints only after verifying conflict-practice tip has the blue line and HEAD is main

**Acceptance Criteria**:

- staged unrelated file / staged deletion / partially staged edit each leave git status --porcelain and HEAD and branch list byte-identical and exit 1
- a pre-commit hook exiting 1 yields exit 1 and no Created branch text
- happy path lesson 06 walk still passes

**Tests**:

- selftest regressions helper_refuses_staged_work and helper_stops_on_git_failure

#### Code Intent

- **CI-M-002-001** `tools/setup_conflict.py::main / make_branch`: main(): after existing preflights, refuse when any line of git status --porcelain does not start with '??' (message: unrelated tracked or staged changes; list them; fix: commit or stash them yourself, then rerun). make_branch(): run each of switch -c, write, add, commit, switch main through a step helper that on nonzero return prints which step failed, git stderr, the branch you are on (git branch --show-current), and 'Nothing was undone; inspect with git status' then returns 1 immediately. After switch back, verify git show conflict-practice:workspace/favorites.md contains 'Favorite color: blue' and branch --show-current == main before printing the success lines. No reset/restore/unstage anywhere. Docstring 'Nothing else is touched' stays true. (refs: DL-004)
- **CI-M-002-002** `tools/selftest.py::helper_refuses_staged_work / helper_stops_on_git_failure`: helper_refuses_staged_work: in a fresh course with committed favorites.md, for each of (staged unrelated new file, staged deletion of hello.md, partially staged edit of profile.md) snapshot git status --porcelain, rev-parse HEAD, git branch --list, run setup_conflict.py, assert exit 1 and identical snapshots, then undo only the fixture's own change. helper_stops_on_git_failure: write .git/hooks/pre-commit that exits 1 (chmod +x), run helper, assert exit 1 and 'Created branch' not in stdout. Skip hook case on Windows (os.name == 'nt') with a printed note. (refs: DL-002, DL-004)

#### Code Changes

**CC-M-002-001** (tools/setup_conflict.py) - implements CI-M-002-001

**Code:**

```diff
diff --git a/tools/setup_conflict.py b/tools/setup_conflict.py
--- a/tools/setup_conflict.py
+++ b/tools/setup_conflict.py
@@ -35,6 +35,10 @@ def main():
         return refuse("workspace/favorites.md has uncommitted changes.", "Commit it first (step 2), then run this again.")
     if git("ls-files", "--error-unmatch", "workspace/favorites.md").returncode != 0:
         return refuse("workspace/favorites.md is not committed yet.", "Create it and commit it (steps 1–2).")
+    unrelated = [l for l in git("status", "--porcelain").stdout.splitlines() if not l.startswith("??")]
+    if unrelated:
+        return refuse("other tracked or staged changes would be swept into the new commit:\n    " + "\n    ".join(unrelated),
+                      "Commit or stash them yourself, then run this again.")
     with open(FAVES, encoding="utf-8") as fh:
         lines = fh.read().splitlines(keepends=True)
     idx = next((i for i, l in enumerate(lines) if "Favorite color" in l), None)
@@ -43,14 +47,40 @@ def main():
     return make_branch(lines, idx)
 
 
+def stopped(label, detail):
+    """Report a failed step and where it left the repository. Nothing is undone."""
+    print(f"Stopped: {label} failed.\n{detail.strip()}")
+    print(f"You are on branch {git('branch', '--show-current').stdout.strip()}. "
+          "Nothing was undone; inspect with git status.")
+    return 1
+
+
+def step(label, *args):
+    """Run one git command; return None on success, else report and return 1."""
+    result = git(*args)
+    return None if result.returncode == 0 else stopped(label, result.stderr)
+
+
+def write_favorites(lines):
+    try:
+        with open(FAVES, "w", encoding="utf-8") as fh:
+            fh.writelines(lines)
+    except OSError as err:
+        return stopped("writing workspace/favorites.md", str(err))
+
+
 def make_branch(lines, idx):
-    git("switch", "-c", BRANCH)
     lines[idx] = "- Favorite color: blue\n"
-    with open(FAVES, "w", encoding="utf-8") as fh:
-        fh.writelines(lines)
-    git("add", "workspace/favorites.md")
-    git("commit", "-m", "Change favorite color to blue")
-    git("switch", "main")
+    failure = (step("git switch -c", "switch", "-c", BRANCH)
+               or write_favorites(lines)
+               or step("git add", "add", "workspace/favorites.md")
+               or step("git commit", "commit", "-m", "Change favorite color to blue")
+               or step("git switch main", "switch", "main"))
+    if failure:
+        return failure
+    if ("Favorite color: blue" not in git("show", f"{BRANCH}:workspace/favorites.md").stdout
+            or git("branch", "--show-current").stdout.strip() != "main"):
+        return stopped("verifying the result", f"{BRANCH} lacks the blue line, or you are not on main.")
     print(f"Created branch {BRANCH} with one commit that sets the favorite color to blue.")
     print("You are back on main. favorites.md here is unchanged.")
     print("Next: edit the same 'Favorite color' line on main to a different colour, commit, then git merge conflict-practice.")

```

**Documentation:**

```diff
--- a/tools/setup_conflict.py
+++ b/tools/setup_conflict.py
@@ -38,2 +38,5 @@
         return refuse("workspace/favorites.md is not committed yet.", "Create it and commit it (steps 1–2).")
+    # A plain git commit takes the whole index, so any other staged or modified tracked
+    # file would be committed as part of this helper's commit. Untracked files are safe.
+    # (ref: DL-004)
     unrelated = [l for l in git("status", "--porcelain").stdout.splitlines() if not l.startswith("??")]
@@ -76,2 +76,5 @@
     lines[idx] = "- Favorite color: blue\n"
+    # Every git call is checked and the first failure stops the run with the repository
+    # left as-is: success is printed only after the branch tip is verified. Nothing is
+    # reset or restored, because learner work may be present. (ref: DL-004)
     failure = (step("git switch -c", "switch", "-c", BRANCH)

```


**CC-M-002-002** (tools/selftest.py) - implements CI-M-002-002

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -150,6 +150,63 @@
 
 [Back to notes](README.md)
 """
+
+
+FAVORITES = "# Favorites\n\n- Favorite color: green\n- Favorite food: bread\n- Favorite tool: git\n"
+
+
+def course_with_favorites(tmp, name):
+    l = fresh_course(tmp, name)
+    l.write("workspace/favorites.md", FAVORITES)
+    l.commit("Add favorites", "workspace/favorites.md")
+    return l
+
+
+def run_helper(l):
+    return subprocess.run([PY, "tools/setup_conflict.py"], cwd=l.root, capture_output=True, text=True)
+
+
+def helper_refuses_staged_work(tmp):
+    """setup_conflict.py commits with a plain git commit, which takes the whole
+    index; it must refuse rather than sweep in work it did not create."""
+    l = course_with_favorites(tmp, "helper-staged")
+    l.write("workspace/hello.md", "# Hello\n")
+    l.write("workspace/profile.md", "# Ada\n")
+    l.commit("Add hello and profile", "workspace/hello.md", "workspace/profile.md")
+
+    def refuses(why):
+        state = lambda: [l.git(*a).stdout for a in (("status", "--porcelain"), ("rev-parse", "HEAD"), ("branch", "--list"))]
+        before = state()
+        r = run_helper(l)
+        assert r.returncode == 1 and state() == before, f"helper did not refuse cleanly with {why}:\n{r.stdout}{r.stderr}"
+
+    l.write("workspace/other.md", "unrelated\n")
+    l.git("add", "workspace/other.md")
+    refuses("a staged unrelated file")
+    l.git("rm", "-q", "--cached", "workspace/other.md")
+    os.remove(os.path.join(l.root, "workspace/other.md"))
+    l.git("rm", "-q", "workspace/hello.md")
+    refuses("a staged deletion")
+    l.git("restore", "--staged", "--worktree", "workspace/hello.md")
+    l.append("workspace/profile.md", "one\n")
+    l.git("add", "workspace/profile.md")
+    l.append("workspace/profile.md", "two\n")
+    refuses("a partially staged edit")
+    print("  conflict helper: refuses staged and modified work, changing nothing")
+
+
+def helper_stops_on_git_failure(tmp):
+    """A failing git command must not be reported as success."""
+    if os.name == "nt":
+        print("  conflict helper failure test: skipped (needs a POSIX hook)")
+        return
+    l = course_with_favorites(tmp, "helper-hook")
+    hook = os.path.join(l.root, ".git", "hooks", "pre-commit")
+    l.write(".git/hooks/pre-commit", "#!/bin/sh\nexit 1\n")
+    os.chmod(hook, 0o755)
+    r = run_helper(l)
+    assert r.returncode == 1 and "Created branch" not in r.stdout, f"failed commit reported as success:\n{r.stdout}{r.stderr}"
+    print("  conflict helper: a failed git command stops it")
 
 
 def commits_before_first_check(l):
@@ -228,7 +285,7 @@
 def lesson_06(l):
     l.write("workspace/favorites.md", "# Favorites\n\n- Favorite color: green\n- Favorite food: bread\n- Favorite tool: git\n")
     l.commit("Add favorites", "workspace/favorites.md")
-    r = subprocess.run([PY, "tools/setup_conflict.py"], cwd=l.root, capture_output=True, text=True)
+    r = run_helper(l)
     assert r.returncode == 0, r.stdout + r.stderr
     l.edit("workspace/favorites.md", "green", "red")
     l.commit("Change favorite color to red", "workspace/favorites.md")
@@ -343,6 +400,9 @@
         lesson_07(l, tmp)
         lesson_08(l)
         lesson_09(l)
+        for regression in (helper_refuses_staged_work,
+                           helper_stops_on_git_failure):
+            regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr
         r = subprocess.run([PY, "tools/review.py"], cwd=l.root, capture_output=True, text=True)

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -168,2 +168,3 @@
 
+# Refusal must leave the index, HEAD and branches exactly as found. (ref: DL-004)
 def helper_refuses_staged_work(tmp):

```


**CC-M-002-003** (CHANGELOG.md) - implements CI-M-002-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -17,6 +17,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   describing its contents.
 - `selftest.py` reports a checker crash as a harness error instead of an
   expected exercise failure.
+- `setup_conflict.py` refuses to run while any tracked file is modified or
+  any change is staged, and stops at the first failing git command instead of
+  printing success.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -20,1 +20,1 @@
 - `setup_conflict.py` refuses to run while any tracked file is modified or

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-002-004** (CURRICULUM_CHANGELOG.md) - implements CI-M-002-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -24,6 +24,14 @@ Entry template:
 - Expected improvement: a broken checker fails selftest loudly instead of looking like an exercise that has not been done yet.
 - Re-evaluate: no
 
+## 2026-09-29 — Conflict helper no longer commits unrelated work or reports false success
+- Observed problem: `tools/setup_conflict.py` ran a plain `git commit`, which commits the whole index, so anything the learner had staged landed on `conflict-practice`; and it ignored git's exit codes, so a failed commit still printed "Created branch".
+- Evidence: adversarial review findings F1 and F2, reproduced by staging an unrelated file and by a pre-commit hook that exits 1. `python tools/selftest.py` wall time at this commit: 7.9s.
+- Hypothesis: Preflight has to look at the whole working tree, not just favorites.md, and every git call has to be checked; a helper that fails should report where it stopped and leave the repository as it is.
+- Change made: Whole-tree preflight (untracked files allowed), each git step return-code checked with the first failure reported, success printed only after the branch tip and current branch are verified. No reset or restore anywhere. Two selftest regressions.
+- Expected improvement: a learner with unrelated staged work is told to commit or stash it instead of losing it into the practice branch; a failed helper never reads as success.
+- Re-evaluate: no
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -33,1 +33,2 @@
 - Re-evaluate: no
+- Decisions: DL-004 in tools/README.md.

```


### Milestone 3: F3 lesson 06 accepts ours theirs and combined resolutions

**Files**: tools/check.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- merge_touching compares the two merge parents on the path
- 06.merge.commit passes for keep-main keep-branch and third-value resolutions
- 09.merge.branch keeps passing for the no-ff capstone merge

**Acceptance Criteria**:

- regression resolves the conflict three ways in three fixtures and 06.merge.commit is ok in each
- a fast-forward-only history still fails 06.merge.commit

**Tests**:

- selftest regression conflict_resolutions_all_pass

#### Code Intent

- **CI-M-003-001** `tools/check.py::merge_touching`: Add both_sides=False parameter. Default: learner merge commits whose first-parent diff on path is non-empty (used by 09.merge.branch). both_sides=True: git merge-base h^1 h^2 gives base; require git diff --name-only base h^1 -- path and base h^2 -- path both non-empty. 06.merge.commit calls it with both_sides=True. Docstring: any resolution of a real conflict counts; a merge only one side touched does not. (refs: DL-005)
- **CI-M-003-002** `tools/selftest.py::conflict_resolutions_all_pass`: Ff-only history fails 06.merge.commit. For resolution in (red, blue, purple): fresh course, commit favorites, run helper, change to red on main, git merge conflict-practice (expect conflict), write chosen file, commit, delete branch; 06.merge.commit is ok. Also a no-conflict --no-ff merge where only the side branch changed favorites.md (main changed another file) must leave 06.merge.commit failing. (refs: DL-002, DL-005)

#### Code Changes

**CC-M-003-001** (tools/check.py) - implements CI-M-003-001

**Code:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -74,11 +74,18 @@ def learner_commits(*paths, merges=None):
             if " " in line and not is_maintainer(line.split(" ", 1)[0])]
 
 
-def merge_touching(path):
-    """Merge commits (after the initial commit) whose result changes `path` relative to their first parent."""
+def merge_touching(path, both_sides=False):
+    """Learner merge commits that change `path` relative to their first parent.
+    With both_sides, only merges where each parent changed `path` since their
+    merge base: any resolution of a real conflict (ours, theirs, combined)
+    counts, and a merge that only one side touched does not."""
+    def touched(h):
+        if not both_sides:
+            return git("diff", "--name-only", f"{h}^1", h, "--", path)
+        base = git("merge-base", f"{h}^1", f"{h}^2")
+        return base and all(git("diff", "--name-only", base, f"{h}^{n}", "--", path) for n in (1, 2))
     hashes = git("log", "--format=%H", "--merges").splitlines()
-    return [h for h in hashes
-            if git("diff", "--name-only", f"{h}^1", h, "--", path) and not is_maintainer(h)]
+    return [h for h in hashes if touched(h) and not is_maintainer(h)]
 
 
 def read(relpath):
@@ -344,7 +351,7 @@ FAVES = "workspace/favorites.md"
 
 @check("06", "06.merge.commit", "merge-conflicts", "a merge commit touches favorites.md")
 def _():
-    if not merge_touching(FAVES):
+    if not merge_touching(FAVES, both_sides=True):
         return ("no merge commit involving favorites.md", "git log --oneline --graph -6",
                 "Complete the merge: resolve, git add, git commit (Exercise 6.1)")
 

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -80,2 +80,5 @@
             return git("diff", "--name-only", f"{h}^1", h, "--", path)
+        # A conflict exists only when both sides changed `path` since their merge base.
+        # Comparing h^1 with h would reject a resolution that keeps main's line, and
+        # comparing h^1 with h^2 would accept a conflict-free merge. (ref: DL-005)
         base = git("merge-base", f"{h}^1", f"{h}^2")

```


**CC-M-003-002** (tools/selftest.py) - implements CI-M-003-002

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -207,6 +207,41 @@
     r = run_helper(l)
     assert r.returncode == 1 and "Created branch" not in r.stdout, f"failed commit reported as success:\n{r.stdout}{r.stderr}"
     print("  conflict helper: a failed git command stops it")
+
+
+def conflict_resolutions_all_pass(tmp):
+    """Keeping main's line, the branch's line, or a third value all resolve the
+    conflict; the check must accept each, and reject a merge only one side changed."""
+    l = course_with_favorites(tmp, "resolve-ff")
+    l.git("switch", "-q", "-c", "side")
+    l.edit("workspace/favorites.md", "green", "blue")
+    l.commit("Change favorite color to blue", "workspace/favorites.md")
+    l.git("switch", "-q", "main")
+    l.git("merge", "-q", "--ff-only", "side")
+    out = l.check("06", "fail")
+    assert l.line(out, "06.merge.commit").split()[0] == "--", "a fast-forward wrongly counted as a conflict merge"
+    for colour in ("red", "blue", "purple"):
+        l = course_with_favorites(tmp, f"resolve-{colour}")
+        assert run_helper(l).returncode == 0
+        l.edit("workspace/favorites.md", "green", "red")
+        l.commit("Change favorite color to red", "workspace/favorites.md")
+        assert l.git("merge", "conflict-practice", ok=False).returncode != 0, "expected a conflict"
+        l.write("workspace/favorites.md", FAVORITES.replace("green", colour))
+        l.commit(f"Merge conflict-practice, choosing {colour}", "workspace/favorites.md")
+        l.git("branch", "-d", "conflict-practice")
+        out = l.check("06", "pass")
+        assert l.line(out, "06.merge.commit").split()[0] == "ok", f"resolution {colour} not accepted"
+    l = course_with_favorites(tmp, "resolve-one-sided")
+    l.git("switch", "-q", "-c", "side")
+    l.edit("workspace/favorites.md", "green", "blue")
+    l.commit("Change favorite color to blue", "workspace/favorites.md")
+    l.git("switch", "-q", "main")
+    l.write("workspace/other.md", "# Other\n")
+    l.commit("Add other", "workspace/other.md")
+    l.git("merge", "-q", "--no-ff", "--no-edit", "side")
+    out = l.check("06", "fail")
+    assert l.line(out, "06.merge.commit").split()[0] == "--", "a merge that only one side changed favorites.md wrongly counted as a conflict merge"
+    print("  conflict resolutions: ours, theirs and combined pass; one-sided merges do not")
 
 
 def commits_before_first_check(l):
@@ -401,7 +436,8 @@
         lesson_08(l)
         lesson_09(l)
         for regression in (helper_refuses_staged_work,
-                           helper_stops_on_git_failure):
+                           helper_stops_on_git_failure,
+                           conflict_resolutions_all_pass):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -211,2 +211,3 @@
 
+# Ours, theirs and combined resolutions pass; one-sided merges do not. (ref: DL-005)
 def conflict_resolutions_all_pass(tmp):

```


**CC-M-003-003** (CHANGELOG.md) - implements CI-M-003-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -20,6 +20,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - `setup_conflict.py` refuses to run while any tracked file is modified or
   any change is staged, and stops at the first failing git command instead of
   printing success.
+- `06.merge.commit` accepts a conflict resolved by keeping either side, or
+  by combining them, not only the resolutions that change the main line.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -23,1 +23,1 @@
 - `06.merge.commit` accepts a conflict resolved by keeping either side, or

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-003-004** (CURRICULUM_CHANGELOG.md) - implements CI-M-003-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -32,6 +32,14 @@ Entry template:
 - Expected improvement: a learner with unrelated staged work is told to commit or stash it instead of losing it into the practice branch; a failed helper never reads as success.
 - Re-evaluate: no
 
+## 2026-09-29 — Lesson 06 check accepts every valid conflict resolution
+- Observed problem: `merge_touching` compared a merge commit with its first parent, so a learner who resolved the conflict by keeping the line already on `main` produced a merge identical to `main` on that path and `06.merge.commit` failed.
+- Evidence: adversarial review finding F3: resolving with main's colour failed the check while purple passed. `python tools/selftest.py` wall time at this commit: 10.1s.
+- Hypothesis: A conflict needs both sides to have changed the file since their merge base, so requiring both parents to differ from the base accepts ours, theirs and combined resolutions and rejects a merge only one side touched.
+- Change made: `merge_touching(path, both_sides=True)` requires the path to differ from the merge base on both parents; 06.merge.commit uses it, the Lesson 09 check keeps the first-parent test. New selftest regression resolves the conflict three ways and requires 06.merge.commit to pass in each; a fast-forward and a no-conflict `--no-ff` merge still fail it.
+- Expected improvement: a correct resolution is never rejected for the value the learner chose.
+- Re-evaluate: no
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -41,1 +41,2 @@
 - Re-evaluate: no
+- Decisions: DL-005 in tools/README.md.

```


### Milestone 4: F8 lesson 04 scratch recovery reaches the checked state

**Files**: lessons/04-everyday-git/README.md, tools/check.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- first step: read .learning/progress.json; if current_lesson is 04, stop and queue this change (DL-013)
- Common Mistakes 4.3 tells a learner who committed scratch.md to run git rm --cached workspace/scratch.md then commit that removal and explains the file stays on disk
- the different-scratch-file suggestion is removed
- 04.scratch.untracked try text points at the same command

**Acceptance Criteria**:

- regression commits scratch.md then follows the lesson steps literally and 04.scratch.untracked is ok with the file contents unchanged
- validate_curriculum.py exits 0

**Tests**:

- selftest regression scratch_recovery_as_written

#### Code Intent

- **CI-M-004-001** `lessons/04-everyday-git/README.md::Exercise 4.3 Common Mistakes`: Replace the committing-by-reflex bullet: if you committed it, run git rm --cached workspace/scratch.md (removes it from Git's tracking, leaves the file on disk), then git commit -m "Stop tracking scratch file"; git status now lists it under Untracked files. Remove 'or simply create a different scratch file'. Recovery section unchanged. (refs: DL-006)
- **CI-M-004-002** `tools/check.py::04.scratch.untracked`: Try text for the tracked case: 'If staged: git restore --staged workspace/scratch.md. If committed: git rm --cached workspace/scratch.md, then commit (Common Mistakes 4.3)'. Rule unchanged. (refs: DL-006)
- **CI-M-004-003** `tools/selftest.py::scratch_recovery_as_written`: Fresh course; write scratch.md, git add, commit; run git rm --cached workspace/scratch.md and commit with a descriptive subject; assert 04.scratch.untracked line is ok and file content unchanged. (refs: DL-002, DL-006)

#### Code Changes

**CC-M-004-001** (lessons/04-everyday-git/README.md) - implements CI-M-004-001

**Code:**

```diff
diff --git a/lessons/04-everyday-git/README.md b/lessons/04-everyday-git/README.md
--- a/lessons/04-everyday-git/README.md
+++ b/lessons/04-everyday-git/README.md
@@ -319,10 +319,11 @@ python tools/check.py 04
 
 - Running `git restore workspace/scratch.md` (no `--staged`) on an
   untracked file: Git says it has no version to restore from. Harmless.
-- Committing it by reflex. If you did, `git log --oneline -1` will show it;
-  that is acceptable, but then delete the file and commit the deletion so the
-  check can see the intended end state is "untracked" — or simply create a
-  different scratch file.
+- Committing it by reflex. If you did, `git log --oneline -1` will show it.
+  Run `git rm --cached workspace/scratch.md`: that removes the file from
+  Git's tracking but leaves it on disk. Then commit with
+  `git commit -m "Stop tracking scratch file"`. `git status` now lists it
+  under *Untracked files*.
 
 ### Recovery
 

```

**Documentation:**

```diff
--- a/lessons/04-everyday-git/README.md
+++ b/lessons/04-everyday-git/README.md
@@ -326,1 +326,1 @@
 - Committing it by reflex. If you did, `git log --oneline -1` will show it.

```

> **Developer notes**: Apply changes in order within the milestone; diffs were generated from a sequential scratch copy and tools/selftest.py plus validate_curriculum.py passed after each milestone. DL-013 guard: before applying, read .learning/progress.json; if current_lesson is 04, stop and queue this milestone. doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-004-002** (tools/check.py) - implements CI-M-004-002

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -310,7 +310,7 @@ def _():
         return ("workspace/scratch.md not found", "ls workspace", "Create it (Exercise 4.3)")
     if tracked("workspace/scratch.md") or staged("workspace/scratch.md"):
         return ("scratch.md is staged or committed; it should be untracked", "git status",
-                "git restore --staged workspace/scratch.md (if staged). If committed, see Common Mistakes 4.3")
+                "If staged: git restore --staged workspace/scratch.md. If committed: git rm --cached workspace/scratch.md, then commit (Common Mistakes 4.3)")
 
 
 # ---------------------------------------------------------------- lesson 05

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -309,2 +309,5 @@
         return ("workspace/scratch.md not found", "ls workspace", "Create it (Exercise 4.3)")
+    # Recovery from a committed scratch file is git rm --cached: it untracks the file
+    # and keeps it on disk, so this state stays reachable without loosening the rule.
+    # (ref: DL-006)
     if tracked("workspace/scratch.md") or staged("workspace/scratch.md"):

```


**CC-M-004-003** (tools/selftest.py) - implements CI-M-004-003

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -244,6 +244,20 @@
     print("  conflict resolutions: ours, theirs and combined pass; one-sided merges do not")
 
 
+def scratch_recovery_as_written(tmp):
+    """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
+    by the steps the lesson gives, without losing the file."""
+    l = fresh_course(tmp, "scratch")
+    l.write("workspace/scratch.md", "scratch\n")
+    l.commit("Add scratch file", "workspace/scratch.md")
+    l.git("rm", "-q", "--cached", "workspace/scratch.md")
+    l.git("commit", "-q", "-m", "Stop tracking scratch file")
+    out = l.check("04", "fail")
+    assert l.line(out, "04.scratch.untracked").split()[0] == "ok", "recovery steps did not reach the checked state"
+    assert open(os.path.join(l.root, "workspace/scratch.md")).read() == "scratch\n", "recovery lost the file contents"
+    print("  scratch recovery: lesson 04 steps reach the checked state")
+
+
 def commits_before_first_check(l):
     """A learner who does a whole lesson and only then runs the checker must
     still have their commits recognised (found by hand-walking lesson 03)."""
@@ -437,7 +451,8 @@
         lesson_09(l)
         for regression in (helper_refuses_staged_work,
                            helper_stops_on_git_failure,
-                           conflict_resolutions_all_pass):
+                           conflict_resolutions_all_pass,
+                           scratch_recovery_as_written):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -246,2 +246,3 @@
 
+# Follows the lesson text literally, so text and check cannot drift apart. (ref: DL-006)
 def scratch_recovery_as_written(tmp):

```


**CC-M-004-004** (CHANGELOG.md) - implements CI-M-004-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -22,6 +22,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   printing success.
 - `06.merge.commit` accepts a conflict resolved by keeping either side, or
   by combining them, not only the resolutions that change the main line.
+- Lesson 04 Exercise 4.3 recovery for a committed `scratch.md` now ends in
+  the state `04.scratch.untracked` checks for.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -25,1 +25,1 @@
 - Lesson 04 Exercise 4.3 recovery for a committed `scratch.md` now ends in

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-004-005** (CURRICULUM_CHANGELOG.md) - implements CI-M-004-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -40,6 +40,14 @@ Entry template:
 - Expected improvement: a correct resolution is never rejected for the value the learner chose.
 - Re-evaluate: no
 
+## 2026-09-29 — Lesson 04.3: recovering a committed scratch file reaches the checked state
+- Observed problem: Common Mistakes 4.3 told a learner who committed `scratch.md` to delete the file and commit the deletion; that leaves the file missing, and `04.scratch.untracked` requires it to exist and be untracked, so the check could never pass by following the text.
+- Evidence: adversarial review finding F8: commit scratch.md, delete it and commit the deletion, and 04.scratch.untracked fails with "workspace/scratch.md not found". `python tools/selftest.py` wall time at this commit: 10.6s.
+- Hypothesis: The recovery advice was written against the desired end state (untracked) without walking the steps to see whether they reach it.
+- Change made: Common Mistakes 4.3 now says `git rm --cached workspace/scratch.md`, then commit; the different-scratch-file suggestion is removed; the check's Try text names the same command. The check rule is unchanged. New selftest regression follows the text literally.
+- Expected improvement: a learner who committed the file by reflex can get to green without losing it.
+- Re-evaluate: yes — when lesson 04 progress data exists
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -49,1 +49,2 @@
 - Re-evaluate: yes — when lesson 04 progress data exists
+- Decisions: DL-006 in tools/README.md.

```


### Milestone 5: F6 separate-commit checks require per-path commits

**Files**: lessons/03-git-foundations/README.md, lessons/04-everyday-git/README.md, tools/check.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- first step: read .learning/progress.json; if current_lesson is 03 or 04, stop and queue this change (DL-013)
- 03.commit.separate needs for each of hello/profile/notes a learner commit touching it and neither sibling
- 04.commits.two-more needs two learner commits touching profile.md without notes/README.md and two touching notes/README.md without profile.md
- messages name which path lacks its own commit
- Exercise 4.1 Recovery tells a learner who bundled profile and notes to make one further edit to each file and commit each separately
- Exercise 3.2 Recovery tells a learner who committed profile and notes together to make one further small edit to each and commit each separately, replacing the 'acceptable... move on' text

**Acceptance Criteria**:

- one bundled 03 commit plus an unrelated favorites commit plus an empty commit fails 03.commit.separate
- one combined 04 edit commit fails 04.commits.two-more
- prescribed walk passes
- bundled 4.1 commit followed by the new 4.1 Recovery steps literally passes 04.commits.two-more (lesson 04 has only Exercises 4.1-4.3; lesson 03's exclusive commits plus the recovery commits supply two per path)
- bundled 3.2 profile+notes commit followed by the new 3.2 Recovery steps literally passes 03.commit.separate

**Tests**:

- selftest regressions bundled_commit_rejected, combined_edit_rejected, bundled_41_recovery_as_written and bundled_32_recovery_as_written

#### Code Intent

- **CI-M-005-001** `tools/check.py::learner_commits / exclusive_commits / 03.commit.separate / 04.commits.two-more`: learner_commits gains a sibling exclusive_commits(path, *others) returning learner commit hashes touching path whose git show --name-only lists no file under any of others (reuse one log walk; keep learner_commits' public return of subjects). 03.commit.separate: for each of hello.md, profile.md, notes/ with the other two as others, require >=1; report the first path lacking its own commit. 04.commits.two-more: exclusive_commits(PROFILE, NOTES) >= 2 and exclusive_commits(NOTES, PROFILE) >= 2; report which falls short. (refs: DL-007)
- **CI-M-005-002** `tools/selftest.py::bundled_commit_rejected / combined_edit_rejected`: bundled: fresh course, write hello/profile/notes, commit all in one commit, commit favorites.md, git commit --allow-empty; assert 03.commit.separate line is '--'. combined: after a correct lesson 03, edit profile and notes and commit both together; assert 04.commits.two-more is '--'. (refs: DL-002, DL-007)
- **CI-M-005-003** `lessons/04-everyday-git/README.md::Exercise 4.1 Recovery`: Replace "Committed both together? Fine; do the next exercise's commits separately instead." with: Committed both together? Make one more small edit to each file and commit each on its own (two commits), so each file still ends up with commits of its own when you run the check. Staged-the-wrong-file sentence unchanged. (refs: DL-007)
- **CI-M-005-004** `tools/selftest.py::bundled_41_recovery_as_written`: Fresh course after a correct lesson 03; do 4.1 as one bundled profile+notes commit; follow the new 4.1 Recovery literally (one extra edit to each file, committed separately); run Exercises 4.2-4.3 as prescribed (they add no profile/notes commits); assert 04.commits.two-more line is ok. (refs: DL-002, DL-007)
- **CI-M-005-005** `lessons/03-git-foundations/README.md::Exercise 3.2 Recovery (Common Mistakes bullet)`: Replace "If you committed both together, that is acceptable. Note it in your reflection and move on; splitting commits is an advanced topic." with: If you committed both together, make one more small edit to profile.md and commit it on its own, then one more small edit inside notes/ and commit that on its own, so each has a commit of its own when you run the check. The staged-both-together bullet above stays unchanged. (refs: DL-007)
- **CI-M-005-006** `tools/selftest.py::bundled_32_recovery_as_written`: Fresh course; commit hello.md alone (3.1); commit profile.md and notes/ together in one commit; follow the new 3.2 Recovery literally (one extra edit to profile.md committed alone, one extra edit under notes/ committed alone); assert 03.commit.separate line is ok. (refs: DL-002, DL-007)

#### Code Changes

**CC-M-005-001** (tools/check.py) - implements CI-M-005-001

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -74,6 +74,14 @@ def learner_commits(*paths, merges=None):
             if " " in line and not is_maintainer(line.split(" ", 1)[0])]
 
 
+def exclusive_commits(path, *others):
+    """Hashes of the learner's commits that touch `path` and none of `others`:
+    one thing per commit, not just a count of commits."""
+    hashes = git("log", "--no-merges", "--format=%H", "--", path).splitlines()
+    return [h for h in hashes if not is_maintainer(h)
+            and not git("show", "--format=", "--name-only", h, "--", *others)]
+
+
 def merge_touching(path, both_sides=False):
     """Learner merge commits that change `path` relative to their first parent.
     With both_sides, only merges where each parent changed `path` since their
@@ -263,10 +271,11 @@ commit_touching("03", "03.commit.notes", "workspace/notes/", "the workspace/note
 
 @check("03", "03.commit.separate", "commit", "hello, profile, and notes were committed separately")
 def _():
-    subjects = learner_commits()
-    if len(subjects) < 3:
-        return (f"only {len(subjects)} commit(s) of yours so far; expected at least three",
-                "git log --oneline", "One commit per file/folder (Exercise 3.2)")
+    paths = ["workspace/hello.md", PROFILE, "workspace/notes"]
+    for path in paths:
+        if not exclusive_commits(path, *[p for p in paths if p != path]):
+            return (f"no commit of yours touches only {path}", "git log --oneline --stat",
+                    "One commit per file/folder (Exercise 3.2); if they were bundled, see Recovery in Exercise 3.2")
 
 
 @check("03", "03.clean", "working-tree", "working tree is clean (everything committed)")
@@ -291,10 +300,12 @@ def _():
 
 @check("04", "04.commits.two-more", "selective-staging", "two more commits exist after Lesson 03 (profile edit, notes edit)")
 def _():
-    if len(learner_commits(PROFILE)) < 2 or len(learner_commits(NOTES)) < 2:
-        return ("profile.md and notes/README.md should each have at least two commits by now",
-                f"git log --oneline -- {PROFILE}; git log --oneline -- {NOTES}",
-                "Exercise 4.1: edit both, then commit each separately")
+    for path, other in ((PROFILE, NOTES), (NOTES, PROFILE)):
+        n = len(exclusive_commits(path, other))
+        if n < 2:
+            return (f"{path} has {n} commit(s) of its own (touching it and not {other}); expected at least two",
+                    f"git log --oneline --stat -- {path}",
+                    "Exercise 4.1: edit both, then commit each separately (see Recovery in 4.1 if they were bundled)")
 
 
 @check("04", "04.restore.hello", "git-restore", "workspace/hello.md matches its committed version")

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -78,2 +78,4 @@
     one thing per commit, not just a count of commits."""
+    # A count of commits passes one bundled commit plus unrelated or empty ones.
+    # git log -- path already skips commits that do not touch path. (ref: DL-007)
     hashes = git("log", "--no-merges", "--format=%H", "--", path).splitlines()

```

> **Developer notes**: Apply changes in order within the milestone; diffs were generated from a sequential scratch copy and tools/selftest.py plus validate_curriculum.py passed after each milestone. DL-013 guard: before applying, read .learning/progress.json; if current_lesson is 03 or 04, stop and queue this milestone. Sub-steps a (check.py, selftest 002), b (lesson 04 README, selftest 004), c (lesson 03 README, selftest 006, changelogs) build on each other. 

**CC-M-005-002** (tools/selftest.py) - implements CI-M-005-002

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -244,6 +244,46 @@
     print("  conflict resolutions: ours, theirs and combined pass; one-sided merges do not")
 
 
+def course_after_lesson_03(tmp, name):
+    """A course where hello, profile and notes each have a commit of their own."""
+    l = fresh_course(tmp, name)
+    l.write("workspace/hello.md", "# Hello\n")
+    l.write("workspace/profile.md", PROFILE)
+    l.write("workspace/notes/README.md", NOTES)
+    l.write("workspace/notes/git-commands.md", GIT_COMMANDS)
+    l.commit("Add hello file", "workspace/hello.md")
+    l.commit("Add profile page", "workspace/profile.md")
+    l.commit("Add notes index and git command reference", "workspace/notes")
+    return l
+
+
+def bundled_commit_rejected(tmp):
+    """One commit holding hello, profile and notes, padded with unrelated and
+    empty commits, is not three separate commits."""
+    l = fresh_course(tmp, "bundled")
+    l.write("workspace/hello.md", "# Hello\n")
+    l.write("workspace/profile.md", PROFILE)
+    l.write("workspace/notes/README.md", NOTES)
+    l.commit("Add hello, profile and notes together", "workspace")
+    l.write("workspace/favorites.md", FAVORITES)
+    l.commit("Add favorites", "workspace/favorites.md")
+    l.git("commit", "-q", "--allow-empty", "-m", "Record an empty commit")
+    out = l.check("03", "fail")
+    assert l.line(out, "03.commit.separate").split()[0] == "--", "a bundled commit passed 03.commit.separate"
+    print("  bundled commit: rejected by 03.commit.separate")
+
+
+def combined_edit_rejected(tmp):
+    """Editing profile and notes in one commit is one commit, not two more each."""
+    l = course_after_lesson_03(tmp, "combined")
+    l.append("workspace/profile.md", "4. Merge conflicts\n")
+    l.append("workspace/notes/README.md", "- [ ] 04 Everyday Git\n")
+    l.commit("Update profile and notes together", "workspace")
+    out = l.check("04", "fail")
+    assert l.line(out, "04.commits.two-more").split()[0] == "--", "a combined edit passed 04.commits.two-more"
+    print("  combined edit: rejected by 04.commits.two-more")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -452,7 +492,9 @@
         for regression in (helper_refuses_staged_work,
                            helper_stops_on_git_failure,
                            conflict_resolutions_all_pass,
-                           scratch_recovery_as_written):
+                           scratch_recovery_as_written,
+                           bundled_commit_rejected,
+                           combined_edit_rejected):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -259,2 +259,3 @@
 
+# Padding with unrelated and empty commits must not satisfy a per-path check. (ref: DL-007)
 def bundled_commit_rejected(tmp):

```


**CC-M-005-003** (lessons/04-everyday-git/README.md) - implements CI-M-005-003

**Code:**

```diff
diff --git a/lessons/04-everyday-git/README.md b/lessons/04-everyday-git/README.md
--- a/lessons/04-everyday-git/README.md
+++ b/lessons/04-everyday-git/README.md
@@ -168,7 +168,9 @@ The `04.messages.*` checks read your last several commit subjects.
 ### Recovery
 
 Staged the wrong file? `git restore --staged <file>`. Committed both
-together? Fine; do the next exercise's commits separately instead.
+together? Make one more small edit to each file and commit each on its own
+(two commits), so each file still ends up with commits of its own when you
+run the check.
 
 ### Reflection
 

```

**Documentation:**

```diff
--- a/lessons/04-everyday-git/README.md
+++ b/lessons/04-everyday-git/README.md
@@ -172,1 +172,1 @@
 together? Make one more small edit to each file and commit each on its own

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-005-004** (tools/selftest.py) - implements CI-M-005-004

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -284,6 +284,25 @@
     print("  combined edit: rejected by 04.commits.two-more")
 
 
+def bundled_41_recovery_as_written(tmp):
+    """Lesson 04.1 Recovery: a learner who bundled profile and notes must be
+    able to reach 04.commits.two-more by the steps the lesson gives."""
+    l = course_after_lesson_03(tmp, "recover-41")
+    l.append("workspace/profile.md", "4. Merge conflicts\n")
+    l.append("workspace/notes/README.md", "- [ ] 04 Everyday Git\n")
+    l.commit("Update profile and notes together", "workspace")
+    l.append("workspace/profile.md", "5. Remotes again\n")
+    l.commit("Add a fifth item to the learning list", "workspace/profile.md")
+    l.append("workspace/notes/README.md", "- [ ] 05 Branches\n")
+    l.commit("Add branches to the progress checklist", "workspace/notes/README.md")
+    l.write("workspace/hello.md", "oops\n")
+    l.git("restore", "workspace/hello.md")
+    l.write("workspace/scratch.md", "scratch\n")
+    out = l.check("04", "pass")
+    assert l.line(out, "04.commits.two-more").split()[0] == "ok", "4.1 Recovery did not reach 04.commits.two-more"
+    print("  lesson 04.1 recovery: reaches 04.commits.two-more")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -494,7 +513,8 @@
                            conflict_resolutions_all_pass,
                            scratch_recovery_as_written,
                            bundled_commit_rejected,
-                           combined_edit_rejected):
+                           combined_edit_rejected,
+                           bundled_41_recovery_as_written):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -286,2 +286,3 @@
 
+# Follows the Recovery text literally to the checked state. (ref: DL-007)
 def bundled_41_recovery_as_written(tmp):

```


**CC-M-005-005** (lessons/03-git-foundations/README.md) - implements CI-M-005-005

**Code:**

```diff
diff --git a/lessons/03-git-foundations/README.md b/lessons/03-git-foundations/README.md
--- a/lessons/03-git-foundations/README.md
+++ b/lessons/03-git-foundations/README.md
@@ -339,8 +339,10 @@ python tools/check.py 03
 - If you accidentally staged both files together, `git restore --staged
   workspace/notes` unstages the folder (Lesson 04 explains this command);
   then commit the profile alone.
-- If you committed both together, that is acceptable. Note it in your
-  reflection and move on; splitting commits is an advanced topic.
+- If you committed both together, make one more small edit to `profile.md`
+  and commit it on its own, then one more small edit inside `notes/` and
+  commit that on its own, so each has a commit of its own when you run the
+  check.
 
 ### Reflection
 

```

**Documentation:**

```diff
--- a/lessons/03-git-foundations/README.md
+++ b/lessons/03-git-foundations/README.md
@@ -344,1 +344,1 @@
 - If you committed both together, make one more small edit to `profile.md`

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-005-006** (tools/selftest.py) - implements CI-M-005-006

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -303,6 +303,25 @@
     print("  lesson 04.1 recovery: reaches 04.commits.two-more")
 
 
+def bundled_32_recovery_as_written(tmp):
+    """Lesson 03.2 Recovery: a learner who bundled profile and notes must be
+    able to reach 03.commit.separate by the steps the lesson gives."""
+    l = fresh_course(tmp, "recover-32")
+    l.write("workspace/hello.md", "# Hello\n")
+    l.commit("Add hello file", "workspace/hello.md")
+    l.write("workspace/profile.md", PROFILE)
+    l.write("workspace/notes/README.md", NOTES)
+    l.write("workspace/notes/git-commands.md", GIT_COMMANDS)
+    l.commit("Add profile and notes together", "workspace")
+    l.append("workspace/profile.md", "4. Merge conflicts\n")
+    l.commit("Add merge conflicts to learning list", "workspace/profile.md")
+    l.append("workspace/notes/git-commands.md", "\nSee also the profile.\n")
+    l.commit("Add a see-also line to the command reference", "workspace/notes")
+    out = l.check("03", "pass")
+    assert l.line(out, "03.commit.separate").split()[0] == "ok", "3.2 Recovery did not reach 03.commit.separate"
+    print("  lesson 03.2 recovery: reaches 03.commit.separate")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -514,7 +533,8 @@
                            scratch_recovery_as_written,
                            bundled_commit_rejected,
                            combined_edit_rejected,
-                           bundled_41_recovery_as_written):
+                           bundled_41_recovery_as_written,
+                           bundled_32_recovery_as_written):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -305,2 +305,3 @@
 
+# Follows the Recovery text literally to the checked state. (ref: DL-007)
 def bundled_32_recovery_as_written(tmp):

```


**CC-M-005-007** (CHANGELOG.md) - implements CI-M-005-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -24,6 +24,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   by combining them, not only the resolutions that change the main line.
 - Lesson 04 Exercise 4.3 recovery for a committed `scratch.md` now ends in
   the state `04.scratch.untracked` checks for.
+- `03.commit.separate` and `04.commits.two-more` require commits that touch
+  only their own file or folder, not just enough commits overall. Recovery
+  text in Exercises 3.2 and 4.1 now tells a learner who bundled the files how
+  to reach the checked state.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -27,1 +27,1 @@
 - `03.commit.separate` and `04.commits.two-more` require commits that touch

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-005-008** (CURRICULUM_CHANGELOG.md) - implements CI-M-005-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -48,6 +48,14 @@ Entry template:
 - Expected improvement: a learner who committed the file by reflex can get to green without losing it.
 - Re-evaluate: yes — when lesson 04 progress data exists
 
+## 2026-09-29 — Separate-commit checks require a commit per file
+- Observed problem: `03.commit.separate` counted learner commits (three or more) and `04.commits.two-more` counted commits touching each file, so one bundled commit plus unrelated or empty commits passed, and one combined edit passed as two. The old Recovery text also said bundling was acceptable, which would have made the stricter check unpassable.
+- Evidence: adversarial review finding F6: one commit holding hello, profile and notes, then a favorites commit and an empty commit, passed `03.commit.separate`. Selftest now walks both Recovery texts literally. `python tools/selftest.py` wall time at this commit: 13.2s.
+- Hypothesis: The lessons promise "one commit per thing"; the check should look at what each commit touched, since history carries that evidence, and the recovery path must lead to a state the check accepts.
+- Change made: `exclusive_commits(path, *others)` in `tools/check.py`; lesson 03 needs a commit of its own for each of hello, profile and notes, lesson 04 needs two for profile.md and two for notes/README.md relative to each other. Exercise 3.2 and 4.1 Recovery now say to make one more small edit to each file and commit each alone. Four selftest regressions.
+- Expected improvement: a learner who bundled files is told exactly what to do instead of being told it is fine, and false green from padding commits is gone.
+- Re-evaluate: yes — when lesson 03 and 04 progress data exists
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -57,1 +57,2 @@
 - Re-evaluate: yes — when lesson 03 and 04 progress data exists
+- Decisions: DL-007 in tools/README.md.

```


### Milestone 6: F7 markdown checks ignore fenced and inline literals

**Files**: tools/check.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- a fence scanner splits text into prose and top-level fenced blocks honouring fence char and length
- inline code spans are blanked before emphasis/link/list/heading patterns
- 01 and 09 code-block rules test the extracted blocks (09 requires an info string)
- 01.profile.inline-code tests prose with inline spans intact
- tilde fences and unclosed fences follow CommonMark; indented code blocks are not treated as code (outside taught subset)

**Acceptance Criteria**:

- PROFILE fixture wrapped in a four-backtick text fence fails 01 (h1 h2 bold italic list link etc report missing)
- PROFILE containing a four-backtick fence that shows a three-backtick example still passes
- valid PROFILE and CAPSTONE fixtures pass
- unclosed tilde-fenced PROFILE fails 01.profile.h1

**Tests**:

- selftest regression fenced_profile_rejected and nested_example_fence_ok

#### Code Intent

- **CI-M-006-001** `tools/check.py::split_fences / prose / has_prose / profile_check / CAP_RULES / 09.readme.markdown`: split_fences(text) -> (prose, blocks): line scan; an opening line matching ^ {0,3}(`{3,}|~{3,})(.*) starts a block recording char and length and info string; a closing line is the same char with length >= opening and nothing else; unclosed block runs to end of text (CommonMark). Indented (4-space) code blocks are not detected: their lines stay in prose (outside the taught subset, DL-008). prose keeps non-block lines with blocks replaced by blank lines. blocks is a list of (info, body). strip_inline_code(prose) replaces backtick spans with spaces. profile_check gains a target selector: prose (default, inline code stripped), inline (prose with spans intact, used by 01.profile.inline-code), blocks (01.profile.code-block passes when any block exists). CAP_RULES code rule becomes a block test requiring a non-empty info string; other CAP rules run on stripped prose. Module docstring documents the supported subset (backtick/tilde fences, unclosed fence to EOF, no indented code blocks) and states rendered-preview verification stays the learner's job. (refs: DL-008)
- **CI-M-006-002** `tools/selftest.py::fenced_profile_rejected / nested_example_fence_ok`: fenced: fresh course, write ````text + newline + PROFILE + ```` to profile.md; assert check 01 fails and 01.profile.h1, 01.profile.bold, 01.profile.link lines are --. tilde: same with a ~~~ fence left unclosed; assert 01.profile.h1 is --. nested: PROFILE plus a section containing a four-backtick fence that shows a three-backtick example; assert check 01 passes. (refs: DL-002, DL-008)

#### Code Changes

**CC-M-006-001** (tools/check.py) - implements CI-M-006-001

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -7,6 +7,14 @@ Each check is a small function registered with the lesson it belongs to and
 the concept it tests. A check returns None when satisfied, or a
 (problem, look, try) triple: what is wrong, a command to inspect the state,
 and what to do about it. review.py imports CHECKS to map failures to concepts.
+
+The Markdown checks for lessons 01 and 09 read what a learner would see
+rendered: top-level fenced code blocks (backtick or tilde, closed by the same
+character at least as long; an unclosed fence runs to the end of the file, as
+in CommonMark) and inline code spans are set aside before headings, emphasis,
+links and lists are matched. Indented code blocks are outside the taught
+subset and are not detected. The checker cannot see a rendered preview;
+looking at one stays the learner's job.
 """
 import json
 import os
@@ -102,6 +110,45 @@ def has(pattern, text):
     return re.search(pattern, text, re.MULTILINE) is not None
 
 
+FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
+
+
+def split_fences(text):
+    """Split Markdown into (prose, blocks). blocks is a list of (info, body)
+    for the top-level fenced code blocks; prose is the text with every fence
+    and its contents blanked, so line structure is unchanged."""
+    prose, blocks, fence = [], [], None  # fence: (marker, info, body lines)
+    for line in text.split("\n"):
+        if fence is None:
+            m = FENCE.match(line)
+            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
+                fence = (m.group(1), m.group(2).strip(), [])
+                line = ""
+        else:
+            marker, info, body = fence
+            s = line.strip()
+            if len(line) - len(line.lstrip(" ")) <= 3 and len(s) >= len(marker) and set(s) == {marker[0]}:
+                blocks.append((info, "\n".join(body)))
+                fence = None
+            else:
+                body.append(line)
+            line = ""
+        prose.append(line)
+    if fence:
+        blocks.append((fence[1], "\n".join(fence[2])))
+    return "\n".join(prose), blocks
+
+
+def strip_inline_code(prose):
+    """Blank out backtick code spans so `**x**` is not read as bold."""
+    return re.sub(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", lambda m: " " * len(m.group()), prose)
+
+
+def has_prose(pattern, text):
+    """`pattern` matches Markdown outside fenced blocks and inline code."""
+    return has(pattern, strip_inline_code(split_fences(text)[0]))
+
+
 def broken_links(folder):
     """Relative links in every .md under folder whose target file does not exist."""
     broken = []
@@ -164,13 +211,22 @@ def _():
 PROFILE = "workspace/profile.md"
 
 
-def profile_check(cid, concept, desc, pattern, problem, tip):
+def profile_check(cid, concept, desc, pattern, problem, tip, target="prose"):
+    """target: 'prose' (outside fences and inline code), 'inline' (outside
+    fences, inline code kept) or 'blocks' (a fenced block exists; no pattern)."""
     @check("01", cid, concept, desc)
     def _():
         text = read(PROFILE)
         if text is None:
             return (f"{PROFILE} was not found", "ls workspace", "Create it (Exercise 1.1)")
-        if not has(pattern, text):
+        prose, blocks = split_fences(text)
+        if target == "blocks":
+            found = bool(blocks)
+        elif target == "inline":
+            found = has(pattern, prose)
+        else:
+            found = has_prose(pattern, text)
+        if not found:
             return (problem, f"cat {PROFILE}", tip)
 
 
@@ -183,13 +239,13 @@ profile_check("01.profile.bold", "emphasis", "has bold text", r"\*\*\S[^*]*\S\*\
 profile_check("01.profile.italic", "emphasis", "has italic text", r"(?<!\*)\*[^*\s][^*]*\*(?!\*)|(?<!_)_[^_\s][^_]*_(?!_)",
               "no *italic* text", "Wrap a word in single stars: *word*")
 profile_check("01.profile.inline-code", "inline-code", "has inline code", r"`[^`\n]+`",
-              "no `inline code`", "Wrap a command or program name in backticks")
+              "no `inline code`", "Wrap a command or program name in backticks", target="inline")
 profile_check("01.profile.list", "lists", "has a list", r"^\s*([-*+]|\d+\.) \S",
               "no list found", "Lines starting with '- ' or '1. '")
 profile_check("01.profile.nested", "lists", "has a nested list item", r"^\s*([-*+]|\d+\.) \S.*\n(\s*([-*+]|\d+\.) .*\n)*?\s{2,}([-*+]|\d+\.) \S",
               "no indented list item under another item", "Indent a '- ' line by two or more spaces below a list item")
-profile_check("01.profile.code-block", "code-blocks", "has a fenced code block", r"^```[\s\S]*?^```",
-              "no fenced code block (three backticks, content, three backticks)", "See Exercise 1.2")
+profile_check("01.profile.code-block", "code-blocks", "has a fenced code block", None,
+              "no fenced code block (three backticks, content, three backticks)", "See Exercise 1.2", target="blocks")
 profile_check("01.profile.link", "links", "has a link", r"(?<!!)\[[^\]]+\]\([^)\s]+\)",
               "no [text](url) link", "Add a link in the Links section (Exercise 1.3)")
 profile_check("01.profile.image", "images", "has an image with alt text", r"!\[[^\]]+\]\([^)\s]+\)",
@@ -471,7 +527,7 @@ CAP_RULES = [
     ("ordered", r"^\s*\d+\. \S", "an ordered list"),
     ("unordered", r"^\s*[-*+] (?!\[)\S", "an unordered list"),
     ("link", r"(?<!!)\[[^\]]+\]\([^)\s]+\)", "a link"),
-    ("code", r"^```[a-z]+\n[\s\S]*?^```", "a fenced code block with a language"),
+    ("code", None, "a fenced code block with a language"),  # tested on the extracted blocks
     ("table", r"^\|.*\|\s*\n\|?\s*:?-{3,}", "a table"),
     ("checklist", r"^\s*- \[[ x]\] \S", "a checklist"),
 ]
@@ -482,7 +538,9 @@ def _():
     text = read(f"{CAP}/README.md")
     if text is None:
         return (f"{CAP}/README.md not found", "ls workspace/capstone", "Create it on your capstone branch")
-    missing = [label for _, pat, label in CAP_RULES if not has(pat, text)]
+    blocks = split_fences(text)[1]
+    missing = [label for key, pat, label in CAP_RULES
+               if not (any(info for info, _ in blocks) if key == "code" else has_prose(pat, text))]
     if missing:
         return ("missing: " + ", ".join(missing), f"cat {CAP}/README.md", "See the Markdown outcomes list in Exercise 9.1")
 

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -112,4 +112,7 @@
     return re.search(pattern, text, re.MULTILINE) is not None
 
 
+# Opening fence: up to three spaces of indent, then three or more backticks or tildes.
+# Four-space indented code blocks are outside the taught subset and are not
+# detected; their text counts as prose (false red over false green). (ref: DL-008)
 FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
@@ -138,2 +138,4 @@
         prose.append(line)
+    # CommonMark runs an unclosed fence to the end of the document, so its content is
+    # code; treating it as prose would give false green for a forgotten closer. (ref: DL-008)
     if fence:

```


**CC-M-006-002** (tools/selftest.py) - implements CI-M-006-002

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -322,6 +322,27 @@
     print("  lesson 03.2 recovery: reaches 03.commit.separate")
 
 
+def fenced_profile_rejected(tmp):
+    """Markdown shown inside a code fence is not rendered Markdown."""
+    l = fresh_course(tmp, "fenced")
+    l.write("workspace/profile.md", "````text\n" + PROFILE + "````\n")
+    out = l.check("01", "fail")
+    for cid in ("01.profile.h1", "01.profile.bold", "01.profile.link"):
+        assert l.line(out, cid).split()[0] == "--", f"{cid} passed on fenced text"
+    l.write("workspace/profile.md", "~~~\n" + PROFILE)  # unclosed: runs to the end
+    out = l.check("01", "fail")
+    assert l.line(out, "01.profile.h1").split()[0] == "--", "an unclosed tilde fence was read as prose"
+    print("  fenced profile: rejected, unclosed fence included")
+
+
+def nested_example_fence_ok(tmp):
+    """A four-backtick fence that shows a three-backtick example is one block."""
+    l = fresh_course(tmp, "nested")
+    l.write("workspace/profile.md", PROFILE + "\n## Fence example\n\n````markdown\n```bash\ngit status\n```\n````\n")
+    l.check("01", "pass")
+    print("  nested example fence: profile still passes")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -534,7 +555,9 @@
                            bundled_commit_rejected,
                            combined_edit_rejected,
                            bundled_41_recovery_as_written,
-                           bundled_32_recovery_as_written):
+                           bundled_32_recovery_as_written,
+                           fenced_profile_rejected,
+                           nested_example_fence_ok):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -324,2 +324,3 @@
 
+# Fenced Markdown is not rendered Markdown; an unclosed fence runs to end of file. (ref: DL-008)
 def fenced_profile_rejected(tmp):

```


**CC-M-006-003** (CHANGELOG.md) - implements CI-M-006-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -28,6 +28,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   only their own file or folder, not just enough commits overall. Recovery
   text in Exercises 3.2 and 4.1 now tells a learner who bundled the files how
   to reach the checked state.
+- The Lesson 01 and Lesson 09 Markdown checks ignore fenced code blocks and
+  inline code spans, so Markdown shown as an example no longer counts as
+  Markdown used. Code-block rules test the fenced blocks themselves.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -31,1 +31,1 @@
 - The Lesson 01 and Lesson 09 Markdown checks ignore fenced code blocks and

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-006-004** (CURRICULUM_CHANGELOG.md) - implements CI-M-006-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -56,6 +56,14 @@ Entry template:
 - Expected improvement: a learner who bundled files is told exactly what to do instead of being told it is fine, and false green from padding commits is gone.
 - Re-evaluate: yes — when lesson 03 and 04 progress data exists
 
+## 2026-09-29 — Markdown checks stop counting text inside code fences
+- Observed problem: The lesson 01 and 09 checks ran regular expressions over the raw file, so a profile wrapped in a code fence (shown as text, rendering none of it) passed all thirteen checks, and `**x**` in backticks counted as bold.
+- Evidence: adversarial review finding F7: the PROFILE fixture wrapped in a four-backtick fence passed every 01 check. `python tools/selftest.py` wall time at this commit: 14.6s.
+- Hypothesis: Structure only counts if it renders; a small line scanner following the CommonMark fence rules is enough for the subset the lessons teach, without a parser dependency.
+- Change made: `split_fences` (backtick and tilde fences, closing fence at least as long, unclosed fence runs to end of file) and `strip_inline_code` in `tools/check.py`; code-block rules test the extracted blocks, and the Lesson 09 rule requires an info string. Indented code blocks are not detected (outside the taught subset). Three selftest cases: fenced, unclosed tilde, and a nested example fence.
+- Expected improvement: a learner cannot reach green by pasting the exercise inside a code block; rendered-preview checking remains the learner's job.
+- Re-evaluate: yes — when lesson 01 and 09 progress data exists
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -65,1 +65,2 @@
 - Re-evaluate: yes — when lesson 01 and 09 progress data exists
+- Decisions: DL-008 in tools/README.md.

```


### Milestone 7: F5 lesson 07 rejects unpushed local edits as proof of pull

**Files**: tools/check.py, lessons/07-remotes/README.md, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- first step: read .learning/progress.json; if current_lesson is 07, stop and queue this change (DL-013)
- 07.remote.pushed reports behind and diverged distinctly and passes when main contains origin/main
- 07.remote.pulled requires two learner reading-list commits reachable from origin/main and main containing origin/main
- lesson 07 Check Your Work states what the checker verifies and that clone provenance is learner-verified via git log

**Acceptance Criteria**:

- F5 repro (push baseline then two local reading-list commits and no pull) fails 07.remote.pulled
- clone/push/pull walk passes
- full walk through 09 then check all still passes 07

**Tests**:

- selftest regression local_edits_not_pull

#### Code Intent

- **CI-M-007-001** `tools/check.py::07.remote.pushed / 07.remote.pulled / learner_commits`: learner_commits accepts rev (default HEAD) passed to git log. pushed: no origin/main -> push hint; main ancestor of origin/main and unequal -> 'main is behind origin/main: git pull'; origin/main not ancestor of main -> 'main and origin/main have diverged: git pull, resolve, git push'; otherwise ok. pulled desc: 'origin/main carries a second reading-list commit and main contains it'; fail when origin/main is not an ancestor of main (git pull) or learner_commits('workspace/reading-list.md', rev='origin/main') has < 2 entries (message: the remote does not have a second reading-list commit yet; make it in ../learn-git-clone, push there, then git pull here). (refs: DL-009)
- **CI-M-007-002** `lessons/07-remotes/README.md::Exercise 7.1 Check Your Work`: Replace 'main and origin/main match, and that at least one commit arrived via the remote' with: the checker confirms origin exists, your main contains everything on origin/main, and the remote holds a second reading-list commit that your main also has. It cannot tell which folder made that commit; confirm that yourself with git log --format='%h %an %s' -- workspace/reading-list.md and the clone's git log. (refs: DL-009)
- **CI-M-007-003** `tools/selftest.py::local_edits_not_pull`: Fresh course through lesson 05 prerequisites (reading-list committed), bare remote, push; append two reading-list lines locally in two commits with no push; assert 07.remote.pulled line is '--'. Happy-path lesson_07 and the final check all remain unchanged and passing. (refs: DL-002, DL-009)

#### Code Changes

**CC-M-007-001** (tools/check.py) - implements CI-M-007-001

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -68,8 +68,14 @@ def curriculum_tip():
     return git("log", "-1", "--format=%H", "--", *CURRICULUM_PATHS)
 
 
-def learner_commits(*paths, merges=None):
-    """Subjects of the learner's own commits touching `paths`, newest first.
+def is_ancestor(older, newer):
+    return subprocess.run(["git", "merge-base", "--is-ancestor", older, newer],
+                          cwd=ROOT, capture_output=True).returncode == 0
+
+
+def learner_commits(*paths, merges=None, rev="HEAD"):
+    """Subjects of the learner's own commits touching `paths` reachable from
+    `rev`, newest first.
 
     A commit counts as the learner's when it touches these paths and does not
     touch the curriculum. That is a property of the commit itself, so it holds
@@ -77,7 +83,7 @@ def learner_commits(*paths, merges=None):
     curriculum updates pulled in later, or a course installed by cloning.
     """
     flag = {True: ["--merges"], False: ["--no-merges"], None: []}[merges]
-    out = git("log", "--format=%H %s", *flag, "--", *paths)
+    out = git("log", "--format=%H %s", *flag, rev, "--", *paths)
     return [line.split(" ", 1)[1] for line in out.splitlines()
             if " " in line and not is_maintainer(line.split(" ", 1)[0])]
 
@@ -441,21 +447,31 @@ def _():
                 "git remote add origin ../learn-git-remote.git (Exercise 7.1)")
 
 
+NOT_PUSHED = ("origin/main does not exist; nothing has been pushed", "git log --oneline --all -3",
+              "git push -u origin main")
+
+
 @check("07", "07.remote.pushed", "push", "main has been pushed and has not diverged from origin/main")
 def _():
     if not git("rev-parse", "--verify", "origin/main"):
-        return ("origin/main does not exist; nothing has been pushed", "git log --oneline --all -3",
-                "git push -u origin main")
-    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "main"], cwd=ROOT)
-    if ancestor.returncode != 0:
-        return ("origin/main has commits that main does not", "git status", "git pull, resolve if needed, then git push")
+        return NOT_PUSHED
+    if is_ancestor("main", "origin/main") and git("rev-parse", "main") != git("rev-parse", "origin/main"):
+        return ("main is behind origin/main", "git status", "git pull")
+    if not is_ancestor("origin/main", "main"):
+        return ("main and origin/main have diverged", "git log --oneline --graph --all -6",
+                "git pull, resolve if needed, then git push")
 
 
-@check("07", "07.remote.pulled", "pull", "reading-list.md was changed by a commit made in the clone")
+@check("07", "07.remote.pulled", "pull", "origin/main carries a second reading-list commit and main contains it")
 def _():
-    if len(learner_commits("workspace/reading-list.md")) < 2:
-        return ("reading-list.md has only its original commit", "git log --oneline -- workspace/reading-list.md",
-                "Commit a change in ../learn-git-clone, push there, then git pull here")
+    if not git("rev-parse", "--verify", "origin/main"):
+        return NOT_PUSHED
+    if not is_ancestor("origin/main", "main"):
+        return ("main does not contain everything on origin/main", "git status", "git pull")
+    if len(learner_commits("workspace/reading-list.md", rev="origin/main")) < 2:
+        return ("the remote does not have a second reading-list commit yet",
+                "git log --oneline origin/main -- workspace/reading-list.md",
+                "Make it in ../learn-git-clone, push there, then git pull here (Exercise 7.1)")
 
 
 # ---------------------------------------------------------------- lesson 08

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -470,2 +470,6 @@
         return ("main does not contain everything on origin/main", "git status", "git pull")
+    # Stateless on purpose: requiring main == origin/main would fail once lessons 08-09
+    # advance main. The second commit must be on origin/main, which rejects unpushed
+    # local edits. Which clone authored it is not provable from history, so lesson 07
+    # labels that step as self-verification. (ref: DL-009)
     if len(learner_commits("workspace/reading-list.md", rev="origin/main")) < 2:

```

> **Developer notes**: Apply changes in order within the milestone; diffs were generated from a sequential scratch copy and tools/selftest.py plus validate_curriculum.py passed after each milestone. DL-013 guard: before applying, read .learning/progress.json; if current_lesson is 07, stop and queue this milestone. 

**CC-M-007-002** (lessons/07-remotes/README.md) - implements CI-M-007-002

**Code:**

```diff
diff --git a/lessons/07-remotes/README.md b/lessons/07-remotes/README.md
--- a/lessons/07-remotes/README.md
+++ b/lessons/07-remotes/README.md
@@ -178,8 +178,11 @@ This changes a nickname only; nothing is downloaded or deleted.
 python tools/check.py 07
 ```
 
-The checker confirms `origin` exists, `main` and `origin/main` match, and
-that at least one commit arrived via the remote.
+The checker confirms `origin` exists, your `main` contains everything on
+`origin/main`, and the remote holds a second `reading-list.md` commit that
+your `main` also has. It cannot tell which folder made that commit; confirm
+that yourself with `git log --format='%h %an %s' -- workspace/reading-list.md`
+and the clone's `git log`.
 
 ### What You Should Notice
 

```

**Documentation:**

```diff
--- a/lessons/07-remotes/README.md
+++ b/lessons/07-remotes/README.md
@@ -183,1 +183,1 @@
 The checker confirms `origin` exists, your `main` contains everything on

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-007-003** (tools/selftest.py) - implements CI-M-007-003

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -343,6 +343,25 @@
     print("  nested example fence: profile still passes")
 
 
+def local_edits_not_pull(tmp):
+    """Two local reading-list commits are not a pull: the remote must have
+    the second commit and main must contain it."""
+    l = fresh_course(tmp, "local-edits")
+    l.write("workspace/reading-list.md", "# Reading list\n\n- Pro Git\n")
+    l.commit("Add reading list", "workspace/reading-list.md")
+    remote = os.path.join(tmp, "local-edits-remote.git")
+    l.git("init", "-q", "--bare", "-b", "main", remote)
+    l.git("remote", "add", "origin", remote)
+    l.git("push", "-q", "-u", "origin", "main")
+    l.append("workspace/reading-list.md", "- A novel\n")
+    l.commit("Add a novel to the reading list", "workspace/reading-list.md")
+    l.append("workspace/reading-list.md", "- A poem\n")
+    l.commit("Add a poem to the reading list", "workspace/reading-list.md")
+    out = l.check("07", "fail")
+    assert l.line(out, "07.remote.pulled").split()[0] == "--", "unpushed local edits passed 07.remote.pulled"
+    print("  local edits: not accepted as a pull")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -557,7 +576,8 @@
                            bundled_41_recovery_as_written,
                            bundled_32_recovery_as_written,
                            fenced_profile_rejected,
-                           nested_example_fence_ok):
+                           nested_example_fence_ok,
+                           local_edits_not_pull):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -345,2 +345,3 @@
 
+# The remote must carry the second commit; local edits alone are not a pull. (ref: DL-009)
 def local_edits_not_pull(tmp):

```


**CC-M-007-004** (CHANGELOG.md) - implements CI-M-007-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -31,6 +31,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - The Lesson 01 and Lesson 09 Markdown checks ignore fenced code blocks and
   inline code spans, so Markdown shown as an example no longer counts as
   Markdown used. Code-block rules test the fenced blocks themselves.
+- `07.remote.pulled` requires the second `reading-list.md` commit to be on
+  `origin/main` and contained in `main`; `07.remote.pushed` reports "behind"
+  and "diverged" separately. Lesson 07 Check Your Work says what the checker
+  can and cannot verify.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -34,1 +34,1 @@
 - `07.remote.pulled` requires the second `reading-list.md` commit to be on

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-007-005** (CURRICULUM_CHANGELOG.md) - implements CI-M-007-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -64,6 +64,14 @@ Entry template:
 - Expected improvement: a learner cannot reach green by pasting the exercise inside a code block; rendered-preview checking remains the learner's job.
 - Re-evaluate: yes — when lesson 01 and 09 progress data exists
 
+## 2026-09-29 — Lesson 07 no longer accepts unpushed local edits as a pull
+- Observed problem: `07.remote.pulled` counted reading-list commits on local `main`, so two local commits and no pull passed; `07.remote.pushed` passed whenever `main` was ahead of `origin/main` and gave one message for two different problems.
+- Evidence: adversarial review finding F5: push a baseline, make two local reading-list commits, never pull, and lesson 07 passed. `python tools/selftest.py` wall time at this commit: 14.3s.
+- Hypothesis: Which folder authored a commit cannot be proven from history, but whether the remote has the commit and whether main contains it can. The rest is learner self-verification and the lesson should say so.
+- Change made: `07.remote.pushed`: distinct behind and diverged messages. `07.remote.pulled`: origin/main must carry two learner reading-list commits and main must contain origin/main (stateless, so it survives lessons 08-09 advancing main). `learner_commits` takes a `rev`. Check Your Work states what is checked and points to `git log` for provenance. One selftest regression.
+- Expected improvement: a learner who never pulled is sent to the clone, and the lesson does not claim more than the checker verifies.
+- Re-evaluate: yes — when lesson 07 progress data exists
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -73,1 +73,2 @@
 - Re-evaluate: yes — when lesson 07 progress data exists
+- Decisions: DL-009 in tools/README.md.

```


### Milestone 8: F9 progress file is validated and written atomically

**Files**: tools/check.py, tools/review.py, tools/selftest.py, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- missing progress file yields the default record
- unreadable/invalid JSON/non-dict/lessons not a dict of dicts raises a ProgressError caught in main which prints path and reason and recovery and returns 2 without writing
- save writes progress.json.tmp in the same folder then os.replace
- review.load skips records failing the same shape test with a printed reason

**Acceptance Criteria**:

- invalid JSON in progress.json stays byte-identical after check.py 00 and exit is 2
- valid run leaves no .tmp file
- review.py on a folder with one bad-shape file reports it skipped and aggregates the rest

**Tests**:

- selftest regression malformed_progress_preserved

#### Code Intent

- **CI-M-008-001** `tools/check.py::load_progress / save_progress / main`: ProgressError(Exception). load_progress: FileNotFoundError -> default record; OSError or ValueError -> ProgressError(path, reason); decoded value must be a dict whose 'lessons' is a dict of dicts and 'current_lesson' a str, else ProgressError. save_progress: dump to PROGRESS + '.tmp' then os.replace(tmp, PROGRESS). main wraps load_progress: on ProgressError print 'Your progress file could not be read: <reason>. It has not been changed. Move it aside (e.g. rename to progress.broken.json) to start fresh, or fix the JSON.' and return 2. (refs: DL-010)
- **CI-M-008-002** `tools/review.py::load`: After json.load, apply the same shape test as check.load_progress (import a shared valid_progress(data) predicate from check.py rather than duplicating it); print 'skipping <path>: not a progress record' for failures. (refs: DL-010)
- **CI-M-008-003** `tools/selftest.py::malformed_progress_preserved`: Fresh course; write '{not json' to .learning/progress.json; run check.py 00 directly; assert returncode 2, file bytes unchanged, no progress.json.tmp. Then a valid run leaves no .tmp. review.py on a temp folder with one valid and one '[]' file exits 0 and prints 'skipping'. (refs: DL-002, DL-010)

#### Code Changes

**CC-M-008-001** (tools/check.py) - implements CI-M-008-001

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -615,19 +615,40 @@ def now():
     return datetime.now(timezone.utc).isoformat(timespec="seconds")
 
 
+class ProgressError(Exception):
+    """The progress file exists but cannot be trusted."""
+
+
+def valid_progress(data):
+    """True if `data` has the shape check.py and review.py rely on."""
+    return (isinstance(data, dict) and isinstance(data.get("current_lesson"), str)
+            and isinstance(data.get("lessons"), dict)
+            and all(isinstance(r, dict) for r in data["lessons"].values()))
+
+
 def load_progress():
+    """The saved record; a fresh one if there is no file. A file that is
+    there but unreadable raises ProgressError rather than being replaced."""
     try:
         with open(PROGRESS, encoding="utf-8") as fh:
-            return json.load(fh)
-    except (OSError, ValueError):
+            data = json.load(fh)
+    except FileNotFoundError:
         return {"version": 1, "current_lesson": "00", "lessons": {}}
+    except (OSError, ValueError) as err:
+        raise ProgressError(f"{PROGRESS}: {err}")
+    if not valid_progress(data):
+        raise ProgressError(f"{PROGRESS}: not a progress record")
+    return data
 
 
 def save_progress(data):
+    """Write beside the file, then swap it in, so a crash cannot leave half a file."""
     os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
-    with open(PROGRESS, "w", encoding="utf-8") as fh:
+    tmp = PROGRESS + ".tmp"
+    with open(tmp, "w", encoding="utf-8") as fh:
         json.dump(data, fh, indent=2)
         fh.write("\n")
+    os.replace(tmp, PROGRESS)
 
 
 def lesson_record(data, lesson):
@@ -712,7 +733,12 @@ def main(argv):
     if not git("rev-parse", "--show-toplevel"):
         print("This folder is not a Git repository. Run this from the course folder (see START_HERE.md).")
         return 2
-    data = load_progress()
+    try:
+        data = load_progress()
+    except ProgressError as err:
+        print(f"Your progress file could not be read: {err}. It has not been changed. "
+              "Move it aside (e.g. rename it to progress.broken.json) to start fresh, or fix the JSON.")
+        return 2
     if argv[:1] == ["hint"] and len(argv) == 2:
         lesson_record(data, argv[1].zfill(2))["hints_used"] += 1
         save_progress(data)

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -626,2 +626,4 @@
         return {"version": 1, "current_lesson": "00", "lessons": {}}
+    # Missing means first run. Anything else unreadable stops the run: replacing it with
+    # an empty record would erase the learner's history on the next save. (ref: DL-010)
     except (OSError, ValueError) as err:
@@ -640,2 +640,4 @@
         fh.write("\n")
+    # The temp file shares PROGRESS's directory because os.replace is atomic only within
+    # one filesystem. (ref: DL-010)
     os.replace(tmp, PROGRESS)

```


**CC-M-008-002** (tools/review.py) - implements CI-M-008-002

**Code:**

```diff
diff --git a/tools/review.py b/tools/review.py
--- a/tools/review.py
+++ b/tools/review.py
@@ -30,9 +30,14 @@ def load(target):
     for p in paths:
         try:
             with open(p, encoding="utf-8") as fh:
-                records.append(json.load(fh))
+                data = json.load(fh)
         except (OSError, ValueError) as err:
             print(f"skipping {p}: {err}")
+            continue
+        if checker.valid_progress(data):
+            records.append(data)
+        else:
+            print(f"skipping {p}: not a progress record")
     return records
 
 

```

**Documentation:**

```diff
--- a/tools/review.py
+++ b/tools/review.py
@@ -34,2 +34,4 @@
             continue
+        # Same shape rule as check.py, so a stray JSON file cannot crash aggregation.
+        # (ref: DL-010)
         if checker.valid_progress(data):

```


**CC-M-008-003** (tools/selftest.py) - implements CI-M-008-003

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -362,6 +362,28 @@
     print("  local edits: not accepted as a pull")
 
 
+def malformed_progress_preserved(tmp):
+    """An unreadable progress file is reported and left alone, not replaced by
+    an empty history; a normal save leaves no temp file behind."""
+    l = fresh_course(tmp, "progress")
+    bad = os.path.join(l.root, ".learning", "progress.json")
+    l.write(".learning/progress.json", "{not json")
+    r = subprocess.run([PY, "tools/check.py", "00"], cwd=l.root, capture_output=True, text=True)
+    assert r.returncode == 2 and "could not be read" in r.stdout, r.stdout + r.stderr
+    assert open(bad).read() == "{not json" and not os.path.exists(bad + ".tmp"), "bad progress file was touched"
+    os.remove(bad)
+    l.check("00", "fail")
+    assert os.path.exists(bad) and not os.path.exists(bad + ".tmp"), "a save left a temp file or no file"
+    folder = os.path.join(tmp, "progress-files")
+    os.makedirs(folder)
+    shutil.copy(bad, os.path.join(folder, "a.json"))
+    with open(os.path.join(folder, "b.json"), "w") as fh:
+        fh.write("[]")
+    r = subprocess.run([PY, "tools/review.py", folder], cwd=l.root, capture_output=True, text=True)
+    assert r.returncode == 0 and "skipping" in r.stdout and "b.json" in r.stdout, r.stdout + r.stderr
+    print("  progress file: malformed one preserved, review skips bad shapes")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -577,7 +599,8 @@
                            bundled_32_recovery_as_written,
                            fenced_profile_rejected,
                            nested_example_fence_ok,
-                           local_edits_not_pull):
+                           local_edits_not_pull,
+                           malformed_progress_preserved):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -364,2 +364,3 @@
 
+# An unreadable progress file is evidence to keep, not state to overwrite. (ref: DL-010)
 def malformed_progress_preserved(tmp):

```


**CC-M-008-004** (CHANGELOG.md) - implements CI-M-008-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -35,6 +35,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   `origin/main` and contained in `main`; `07.remote.pushed` reports "behind"
   and "diverged" separately. Lesson 07 Check Your Work says what the checker
   can and cannot verify.
+- `check.py` refuses to run on a progress file it cannot read (exit 2, file
+  untouched) instead of replacing it with an empty history, and saves
+  progress through a temporary file and `os.replace`. `review.py` skips
+  files that are not progress records and says which.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -38,1 +38,1 @@
 - `check.py` refuses to run on a progress file it cannot read (exit 2, file

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-008-005** (CURRICULUM_CHANGELOG.md) - implements CI-M-008-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -72,6 +72,14 @@ Entry template:
 - Expected improvement: a learner who never pulled is sent to the clone, and the lesson does not claim more than the checker verifies.
 - Re-evaluate: yes — when lesson 07 progress data exists
 
+## 2026-09-29 — Progress file is validated and written atomically
+- Observed problem: `load_progress` treated malformed JSON like a missing file, so the next save replaced a learner's history with an empty record; the write was not atomic.
+- Evidence: adversarial review finding F9: write invalid JSON to `.learning/progress.json`, run `check.py`, and it is replaced. `python tools/selftest.py` wall time at this commit: 15.0s.
+- Hypothesis: A missing file means "start fresh"; a file that exists but cannot be trusted means "stop and tell the learner", because the file is the only copy of their history.
+- Change made: `ProgressError` and a shared `valid_progress` predicate in `tools/check.py`; `main` prints the path, the reason and how to recover, and returns 2 without writing. `review.load` applies the same predicate. One selftest regression.
+- Expected improvement: a damaged progress file is never silently destroyed; review does not aggregate garbage.
+- Re-evaluate: no
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -81,1 +81,2 @@
 - Re-evaluate: no
+- Decisions: DL-010 in tools/README.md.

```


### Milestone 9: F4 curriculum metrics only claim what data supports

**Files**: tools/check.py, tools/review.py, tools/selftest.py, README.md, CURRICULUM_REVIEW.md, CHANGELOG.md, CURRICULUM_CHANGELOG.md

**Requirements**:

- check.py all evaluates every lesson and writes no progress
- a failing run on an already-completed lesson increments rechecks and leaves fails and failed_checks unchanged
- first completion stores fails_before_pass
- review.py removes trivial and abandoned signals and their table columns and SUGGESTIONS/classify entries
- hard to pass uses fails_before_pass and ignores records lacking it
- README says all checks every lesson without recording progress
- CURRICULUM_REVIEW.md signal table drops the timestamp-derived rows
- CURRICULUM_REVIEW.md scope extension is justified by DL-014

**Acceptance Criteria**:

- check.py all on untouched course leaves .learning/progress.json absent
- pass then three failing rechecks keeps fails_before_pass 0 and fails 0
- review.py --selfcheck passes
- review output contains no trivial or abandoned rows

**Tests**:

- selftest regression all_is_read_only and rechecks_do_not_rewrite_first_pass

#### Code Intent

- **CI-M-009-001** `tools/check.py::main / run_lesson / record_run`: main: when target == 'all' evaluate every lesson with recording off and skip save_progress; run_lesson takes record=True and skips record_run and recommend_drills when False. record_run: if rec['completed'] was set before this run and it fails, increment rec['rechecks'] (via .get) and do not touch fails/failed_checks; on first completion set rec['fails_before_pass'] = rec['fails']. (refs: DL-011)
- **CI-M-009-002** `tools/review.py::aggregate / _add_lesson / findings_for / render / SUGGESTIONS / classify_cause / selfcheck`: Drop 'abandoned' and 'trivial' from aggregate, _add_lesson, findings_for, render table, SUGGESTIONS ('trivial-pass', 'lesson-too-small' only if unreferenced after removal), classify_cause branches and selfcheck asserts. _add_lesson appends r['fails_before_pass'] + 1 to attempts_to_pass only when that key exists; seconds_between is deleted once unused. Rename table column 'Started' to 'Records' since presence is all it measures. (refs: DL-011)
- **CI-M-009-003** `README.md`: Line 'python tools/check.py all    # checks everything so far' reads '# checks every lesson; does not record progress'. (refs: DL-011)
- **CI-M-009-004** `CURRICULUM_REVIEW.md`: Remove the two timestamp-derived signal rows (abandoned; passed first attempt under a minute) and the trivial pass wording in the classification list and guidance; add one sentence that learning time and abandonment are not measured by the progress data. (refs: DL-011, DL-014)
- **CI-M-009-005** `tools/selftest.py::all_is_read_only / rechecks_do_not_rewrite_first_pass`: all: fresh course, run check.py all (expect fail), assert .learning/progress.json does not exist. rechecks: fresh course, pass lesson 00, then break hello.md and run check 00 three times; load progress.json and assert fails_before_pass == 0, fails == 0, rechecks == 3. The final happy-path check('all', 'pass') stays. (refs: DL-002, DL-011)

#### Code Changes

**CC-M-009-001** (tools/check.py) - implements CI-M-009-001

**Code:**

```diff
diff --git a/tools/check.py b/tools/check.py
--- a/tools/check.py
+++ b/tools/check.py
@@ -661,13 +661,17 @@ def record_run(data, lesson, failures):
     rec = lesson_record(data, lesson)
     rec["attempts"] += 1
     rec["last_run"] = now()
-    if failures:
+    if failures and rec["completed"]:
+        rec["rechecks"] = rec.get("rechecks", 0) + 1  # a failure after the first pass is not friction learning it
+    elif failures:
         rec["fails"] += 1
         for f in failures:
             rec["failed_checks"][f.id] = rec["failed_checks"].get(f.id, 0) + 1
     else:
         rec["passes"] += 1
-        rec["completed"] = rec["completed"] or now()
+        if not rec["completed"]:
+            rec["completed"] = now()
+            rec["fails_before_pass"] = rec["fails"]
     data["current_lesson"] = next((l for l in lesson_ids()
                                    if not data["lessons"].get(l, {}).get("completed")), "09")
 
@@ -696,8 +700,9 @@ def warn_protected():
         print("      Look: git diff <file>    Try: git restore <file> if you did not mean to edit it.\n")
 
 
-def run_lesson(lesson, data):
-    """Run one lesson's checks, print educational output, record progress. Returns failures."""
+def run_lesson(lesson, data, record=True):
+    """Run one lesson's checks and print educational output; with record=True
+    also update progress. Returns failures."""
     checks = [c for c in CHECKS if c.lesson == lesson]
     print(f"Lesson {lesson} — {lesson_title(lesson)}")
     failures, last_problem = [], None
@@ -716,8 +721,9 @@ def run_lesson(lesson, data):
         print(f"        Look: {look}")
         print(f"        Try:  {fix}")
     print(f"  {len(checks) - len(failures)} of {len(checks)} checks passed.")
-    record_run(data, lesson, failures)
-    recommend_drills(data, lesson, failures)
+    if record:
+        record_run(data, lesson, failures)
+        recommend_drills(data, lesson, failures)
     return failures
 
 
@@ -750,13 +756,15 @@ def main(argv):
         print(f"Unknown lesson {target!r}. Use 00–09, 'all', or nothing for the current lesson.")
         return 2
     warn_protected()
+    record = target != "all"  # 'all' is a read-only overview; only a lesson run is evidence for that lesson
     failed = 0
     for lesson in lessons:
-        failed += len(run_lesson(lesson, data))
+        failed += len(run_lesson(lesson, data, record))
         print()
-    save_progress(data)
+    if record:
+        save_progress(data)
     if failed == 0:
-        print(next_step(data, lessons[-1]))
+        print(next_step(data, lessons[-1]) if record else "All checks passed for every lesson. Nothing was recorded.")
     return 1 if failed else 0
 
 

```

**Documentation:**

```diff
--- a/tools/check.py
+++ b/tools/check.py
@@ -664,2 +664,5 @@
     rec["last_run"] = now()
+    # The first pass freezes fails_before_pass. Later failures only count as rechecks,
+    # so review.py measures friction of learning the lesson, not later regressions.
+    # (ref: DL-011)
     if failures and rec["completed"]:

```


**CC-M-009-002** (tools/review.py) - implements CI-M-009-002

**Code:**

```diff
diff --git a/tools/review.py b/tools/review.py
--- a/tools/review.py
+++ b/tools/review.py
@@ -11,7 +11,7 @@ import glob
 import json
 import os
 import sys
-from datetime import date, datetime
+from datetime import date
 
 ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 sys.path.insert(0, os.path.join(ROOT, "tools"))
@@ -41,26 +41,18 @@ def load(target):
     return records
 
 
-def seconds_between(a, b):
-    try:
-        return (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds()
-    except (TypeError, ValueError):
-        return None
-
-
 def aggregate(records):
-    """Per lesson: learners, completions, fails, hints, abandonments, trivial passes, failed check counts."""
-    agg = {l: {"started": 0, "completed": 0, "fails": 0, "hints": 0, "abandoned": 0,
-               "trivial": 0, "attempts_to_pass": [], "failed_checks": {}} for l in LESSONS}
+    """Per lesson: records, completions, fails, hints, attempts to first pass, failed check counts."""
+    agg = {l: {"started": 0, "completed": 0, "fails": 0, "hints": 0,
+               "attempts_to_pass": [], "failed_checks": {}} for l in LESSONS}
     for rec in records:
-        lessons = rec.get("lessons", {})
-        for lid, r in lessons.items():
+        for lid, r in rec.get("lessons", {}).items():
             if lid in agg:
-                _add_lesson(agg[lid], r, lid, lessons)
+                _add_lesson(agg[lid], r)
     return agg
 
 
-def _add_lesson(a, r, lid, all_lessons):
+def _add_lesson(a, r):
     a["started"] += 1
     a["fails"] += r.get("fails", 0)
     a["hints"] += r.get("hints_used", 0)
@@ -68,12 +60,8 @@ def _add_lesson(a, r, lid, all_lessons):
         a["failed_checks"][cid] = a["failed_checks"].get(cid, 0) + n
     if r.get("completed"):
         a["completed"] += 1
-        a["attempts_to_pass"].append(r.get("fails", 0) + 1)
-        elapsed = seconds_between(r.get("started"), r.get("completed", a))
-        if r.get("fails", 0) == 0 and elapsed is not None and elapsed < 60:
-            a["trivial"] += 1
-    elif any(l > lid for l in all_lessons):
-        a["abandoned"] += 1
+        if "fails_before_pass" in r:  # records without it are unknown, not guessed
+            a["attempts_to_pass"].append(r["fails_before_pass"] + 1)
 
 
 def findings_for(lid, a, prev):
@@ -82,14 +70,10 @@ def findings_for(lid, a, prev):
     mean_attempts = sum(a["attempts_to_pass"]) / len(a["attempts_to_pass"]) if a["attempts_to_pass"] else 0
     if mean_attempts >= 3:
         out.append(finding(lid, "high", "hard to pass", f"mean {mean_attempts:.1f} check runs before first pass", a))
-    if a["abandoned"]:
-        out.append(finding(lid, "high", "abandoned", f"{a['abandoned']} of {a['started']} moved on without passing", a))
     if a["hints"] / n >= 2:
         out.append(finding(lid, "medium", "hints needed", f"{a['hints']} hints across {a['started']} learner(s)", a))
     if prev is not None and a["fails"] >= 3 and a["fails"] >= 2 * max(prev["fails"], 1):
         out.append(finding(lid, "medium", "difficulty jump", f"{a['fails']} fails vs {prev['fails']} in the previous lesson", a))
-    if a["trivial"] and a["trivial"] == a["completed"]:
-        out.append(finding(lid, "low", "trivial pass", f"all {a['completed']} completion(s) passed first try in under a minute", a))
     out += concept_findings(lid, a, n)
     return out
 
@@ -125,7 +109,6 @@ SUGGESTIONS = {
     "concept-out-of-order": "Move the concept to an earlier lesson or add a reinforcement drill before it is needed.",
     "lesson-too-big": "Split into two exercises with a check after each.",
     "lesson-too-small": "Merge with a neighbour or add an optional challenge that demands understanding.",
-    "trivial-pass": "Add a check that requires a decision, not just a file's existence.",
     "unclassified": "Read the lesson as a beginner and decide which rubric category applies.",
 }
 
@@ -141,8 +124,6 @@ def classify_cause(f):
     always a human's, recorded in CURRICULUM_CHANGELOG.md.
     """
     signal, lesson, hints = f["signal"], f["lesson"], f["hints"]
-    if signal == "trivial pass":
-        return "trivial-pass"
     if signal == "hints needed":
         return "unclear-wording"
     if signal == "concept not landing":
@@ -155,10 +136,6 @@ def classify_cause(f):
     if signal == "difficulty jump":
         # A lesson doing many things is more likely oversized than misordered.
         return "lesson-too-big" if CHECK_COUNT.get(lesson, 0) >= BIG_LESSON else "concept-out-of-order"
-    if signal == "abandoned":
-        # Abandoned after asking for help reads as too much lesson at once;
-        # abandoned in silence could be anything, including life.
-        return "lesson-too-big" if hints else "unclassified"
     return "unclassified"
 
 
@@ -183,10 +160,10 @@ def render(findings, agg, sources):
         lines += [f"### Lesson {f['lesson']} — {f['signal']} ({f['severity']})", "",
                   f"- Evidence: {f['evidence']}", f"- Likely cause: {f['cause']}",
                   f"- Suggested change: {f['suggestion']}", ""]
-    lines += ["## Per-lesson signals", "", "| Lesson | Started | Completed | Fails | Hints | Abandoned | Trivial |",
-              "|--------|---------|-----------|-------|-------|-----------|---------|"]
+    lines += ["## Per-lesson signals", "", "| Lesson | Records | Completed | Fails | Hints |",
+              "|--------|---------|-----------|-------|-------|"]
     for lid, a in agg.items():
-        lines.append(f"| {lid} | {a['started']} | {a['completed']} | {a['fails']} | {a['hints']} | {a['abandoned']} | {a['trivial']} |")
+        lines.append(f"| {lid} | {a['started']} | {a['completed']} | {a['fails']} | {a['hints']} |")
     lines += ["", "Next: classify each finding, apply the smallest change, run validate_curriculum.py and selftest.py,",
               "then record it in CURRICULUM_CHANGELOG.md."]
     return "\n".join(lines) + "\n"
@@ -197,12 +174,9 @@ def selfcheck():
     def f(signal, lesson="03", hints=0, concept=None):
         return classify_cause({"signal": signal, "lesson": lesson, "hints": hints, "concept": concept})
 
-    assert f("trivial pass") == "trivial-pass"
     assert f("hints needed") == "unclear-wording"
     assert f("hard to pass", hints=0) == "check-too-strict"
     assert f("hard to pass", hints=4) == "unclear-wording"
-    assert f("abandoned", hints=3) == "lesson-too-big"
-    assert f("abandoned", hints=0) == "unclassified"
     # 'commit' is introduced in lesson 03, so failing there is a teaching problem...
     assert f("concept not landing", lesson="03", concept="commit") == "unclear-wording"
     # ...and failing in a later lesson means it never stuck.
@@ -212,8 +186,8 @@ def selfcheck():
     assert f("difficulty jump", lesson="00") == "concept-out-of-order"  # 2 checks
     assert f("something new") == "unclassified"
     assert set(SUGGESTIONS) >= {f(s, hints=h, concept=c)
-                                for s in ("trivial pass", "hints needed", "hard to pass",
-                                          "abandoned", "difficulty jump", "concept not landing")
+                                for s in ("hints needed", "hard to pass",
+                                          "difficulty jump", "concept not landing")
                                 for h in (0, 5) for c in (None, "commit")}, "a rule returned an unknown key"
     print("classify_cause: all rules behave as documented")
 

```

**Documentation:**

```diff
--- a/tools/review.py
+++ b/tools/review.py
@@ -52,4 +52,6 @@
     return agg
 
 
+# started/completed timestamps cannot measure learning time and a missing later record
+# cannot prove abandonment, so neither is reported. (ref: DL-011)
 def _add_lesson(a, r):

```

> **Developer notes**: Apply changes in order within the milestone; diffs were generated from a sequential scratch copy and tools/selftest.py plus validate_curriculum.py passed after each milestone. lesson-too-small is kept in SUGGESTIONS because CURRICULUM_REVIEW.md still lists it as a human classification; only trivial-pass was removed. 

**CC-M-009-003** (README.md) - implements CI-M-009-003

**Code:**

```diff
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -57,7 +57,7 @@ From the repository's top folder:
 ```text
 python tools/check.py        # checks the lesson you are currently on
 python tools/check.py 03     # checks lesson 03
-python tools/check.py all    # checks everything so far
+python tools/check.py all    # checks every lesson; does not record progress
 ```
 
 On some systems the command is `python3` instead of `python`.

```

**Documentation:**

```diff
--- a/README.md
+++ b/README.md
@@ -61,1 +61,1 @@
 python tools/check.py all    # checks every lesson; does not record progress

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-009-004** (CURRICULUM_REVIEW.md) - implements CI-M-009-004

**Code:**

```diff
diff --git a/CURRICULUM_REVIEW.md b/CURRICULUM_REVIEW.md
--- a/CURRICULUM_REVIEW.md
+++ b/CURRICULUM_REVIEW.md
@@ -15,13 +15,16 @@ check failed. Nothing about the person is stored.
 
 | Signal | Derived from | What it usually means |
 |--------|--------------|-----------------------|
-| High fail count before first pass | `attempts` at first pass | Instructions unclear, or check too strict |
+| High fail count before first pass | `fails_before_pass` | Instructions unclear, or check too strict |
 | Same check failing repeatedly | `failed_checks[id]` | The concept behind that check is not landing |
 | Hints requested | `hints_used` | Lesson text alone is insufficient |
-| Started, never completed, then a later lesson started | timestamps | Learner abandoned it; possible difficulty cliff or check bug |
-| Passed on first attempt in under a minute | timestamps | Possibly trivial; may not demonstrate understanding |
 | Fail spike in lesson N after clean N-1 | attempts across lessons | Difficulty jump or missing prerequisite |
 
+The progress data does not measure learning time or abandonment: its
+timestamps show when the checker ran, not how long anyone worked or whether
+they gave up. Read a check that everyone passes at once by reading the check,
+not from these numbers.
+
 Run it:
 
 ```text
@@ -67,7 +70,7 @@ Evaluate each lesson against these. Record findings as
 2. **Identify** — `python tools/review.py <folder>`. Read the findings.
 3. **Classify** — for each finding, decide the likely cause:
    unclear wording / missing prerequisite / check too strict / check buggy /
-   concept out of order / lesson too big / lesson too small / trivial pass.
+   concept out of order / lesson too big / lesson too small.
 4. **Propose** — write the smallest change that addresses the cause.
 5. **Apply** — edit the lesson and/or `tools/check.py`. Keep it to one
    concern.
@@ -80,7 +83,7 @@ Evaluate each lesson against these. Record findings as
 ## Guardrails
 
 - Never optimise for completion rate alone. A check that everyone passes
-  instantly is a finding ("trivial pass"), not a win.
+  instantly is a finding, not a win.
 - Never change the lesson a learner is currently on (`current_lesson` in
   their progress file) in a way that invalidates their in-progress work.
 - Changes are ordinary Git commits: reviewable, revertable.

```

**Documentation:**

```diff
--- a/CURRICULUM_REVIEW.md
+++ b/CURRICULUM_REVIEW.md
@@ -19,1 +19,1 @@
 | High fail count before first pass | `fails_before_pass` | Instructions unclear, or check too strict |

```

> **Developer notes**: (ref: DL-014) doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-009-005** (tools/selftest.py) - implements CI-M-009-005

**Code:**

```diff
diff --git a/tools/selftest.py b/tools/selftest.py
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -7,6 +7,7 @@
 each lesson's exercise the way the instructions say. After each lesson it
 asserts that check.py fails before the work is done and passes after.
 """
+import json
 import os
 import shutil
 import subprocess
@@ -384,6 +385,28 @@
     print("  progress file: malformed one preserved, review skips bad shapes")
 
 
+def all_is_read_only(tmp):
+    """check.py all is an overview: it must not write progress."""
+    l = fresh_course(tmp, "all-readonly")
+    l.check("all", "fail")
+    assert not os.path.exists(os.path.join(l.root, ".learning", "progress.json")), "'all' wrote progress"
+    print("  check all: writes no progress")
+
+
+def rechecks_do_not_rewrite_first_pass(tmp):
+    """Failing after the first pass is a recheck, not more friction learning the lesson."""
+    l = fresh_course(tmp, "rechecks")
+    l.write("workspace/hello.md", "# Hello\n")
+    l.check("00", "pass")
+    l.write("workspace/hello.md", "no heading\n")
+    for _ in range(3):
+        l.check("00", "fail")
+    with open(os.path.join(l.root, ".learning", "progress.json"), encoding="utf-8") as fh:
+        rec = json.load(fh)["lessons"]["00"]
+    assert (rec["fails_before_pass"], rec["fails"], rec["rechecks"]) == (0, 0, 3), rec
+    print("  rechecks: first pass stays frozen")
+
+
 def scratch_recovery_as_written(tmp):
     """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
     by the steps the lesson gives, without losing the file."""
@@ -600,7 +623,9 @@
                            fenced_profile_rejected,
                            nested_example_fence_ok,
                            local_edits_not_pull,
-                           malformed_progress_preserved):
+                           malformed_progress_preserved,
+                           all_is_read_only,
+                           rechecks_do_not_rewrite_first_pass):
             regression(tmp)
         r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
         assert r.returncode == 0, r.stdout + r.stderr

```

**Documentation:**

```diff
--- a/tools/selftest.py
+++ b/tools/selftest.py
@@ -387,2 +387,3 @@
 
+# 'all' is an overview; only a lesson run is evidence for that lesson. (ref: DL-011)
 def all_is_read_only(tmp):

```


**CC-M-009-006** (CHANGELOG.md) - implements CI-M-009-001

**Code:**

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -39,6 +39,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   untouched) instead of replacing it with an empty history, and saves
   progress through a temporary file and `os.replace`. `review.py` skips
   files that are not progress records and says which.
+- `check.py all` no longer records progress. A failing run after a lesson
+  is complete counts as a recheck and leaves `fails` and `failed_checks`
+  alone; the first completion stores `fails_before_pass`.
+- `review.py` no longer reports "abandoned" or "trivial pass", which were
+  derived from timestamps that only show when the checker ran. "Hard to pass"
+  uses `fails_before_pass` and ignores records that lack it.
 
 ### Added
 

```

**Documentation:**

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -42,1 +42,1 @@
 - `check.py all` no longer records progress. A failing run after a lesson

```

> **Developer notes**: doc_diff is intentionally context-only: the diff field is the complete documentation change for this markdown file; no further comment is added.

**CC-M-009-007** (CURRICULUM_CHANGELOG.md) - implements CI-M-009-001

**Code:**

```diff
diff --git a/CURRICULUM_CHANGELOG.md b/CURRICULUM_CHANGELOG.md
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -80,6 +80,14 @@ Entry template:
 - Expected improvement: a damaged progress file is never silently destroyed; review does not aggregate garbage.
 - Re-evaluate: no
 
+## 2026-09-29 — Curriculum metrics only claim what the data supports
+- Observed problem: `review.py` inferred abandonment from a later lesson having a record and triviality from a sub-minute gap between two check runs; neither is measured. `check.py all` recorded every lesson as started, and failures after a pass raised `fails`, so both distorted "hard to pass" and "difficulty jump".
+- Evidence: adversarial review finding F4: running `check.py all` on an untouched course created a record for every lesson; three failing rechecks after a pass changed `fails` from 0 to 3. `python tools/selftest.py` wall time at this commit: 15.9s.
+- Hypothesis: Deleting signals the data cannot support is smaller and more honest than a new schema version; additive keys read with `.get` keep existing files valid.
+- Change made: `check.py all` is read-only; `record_run` counts rechecks separately and freezes `fails_before_pass`; `review.py` drops the two signals, their table columns and classification branches, and renames the Started column to Records. README and CURRICULUM_REVIEW.md describe what is and is not measured (CURRICULUM_REVIEW.md is outside the original file list because its signal table documented the removed signals). Two selftest regressions.
+- Expected improvement: a maintainer is only pointed at lessons by evidence the tool actually has; a learner running `all` does not change their own record.
+- Re-evaluate: yes — when real progress files exist, to see whether "hard to pass" alone is enough
+
 ## 2026-09-28 — Three faults found by hand-walking lessons 04–09
 
 - Observed problem: (1) a learner who completed lesson 03 and only then ran

```

**Documentation:**

```diff
--- a/CURRICULUM_CHANGELOG.md
+++ b/CURRICULUM_CHANGELOG.md
@@ -89,1 +89,2 @@
 - Re-evaluate: yes — when real progress files exist, to see whether "hard to pass" alone is enough
+- Decisions: DL-011, DL-012 in tools/README.md.

```


## README Entries

### tools/README.md

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

## Execution Waves

- W-001: M-001
- W-002: M-002
- W-003: M-003
- W-004: M-004
- W-005: M-005
- W-006: M-006
- W-007: M-007
- W-008: M-008
- W-009: M-009
