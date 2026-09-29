#!/usr/bin/env python3
# ABOUTME: Simulates a learner doing every lesson in a temporary copy and asserts the checker agrees.
# ABOUTME: Usage: python tools/selftest.py. Exit 0 means every lesson's checks pass when followed, and fail when not.
"""Prove the checker, do not just describe it.

Copies the course into a temp folder, makes the initial commit, then performs
each lesson's exercise the way the instructions say. After each lesson it
asserts that check.py fails before the work is done and passes after.
"""
import os
import shutil
import subprocess
import sys
import tempfile

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


class Learner:
    def __init__(self, root):
        self.root = root

    def git(self, *args, ok=True):
        r = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        if ok and r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr}")
        return r

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def append(self, rel, text):
        with open(os.path.join(self.root, rel), "a", encoding="utf-8") as fh:
            fh.write(text)

    def edit(self, rel, old, new):
        path = os.path.join(self.root, rel)
        text = open(path, encoding="utf-8").read()
        assert old in text, f"{old!r} not in {rel}"
        self.write(rel, text.replace(old, new))

    def commit(self, msg, *paths):
        self.git("add", *paths)
        self.git("commit", "-q", "-m", msg)

    def check(self, lesson, expect):
        r = subprocess.run([PY, "tools/check.py", lesson], cwd=self.root, capture_output=True, text=True)
        # check.py exits 1 for an unmet exercise and 2 for an operational error. Any other
        # status, or a traceback, is a harness fault: reading a crash as an expected fail
        # would let a regression pass on it. (ref: DL-003)
        if r.returncode not in (0, 1) or "Traceback" in r.stderr:
            raise RuntimeError(f"checker crashed on lesson {lesson}:\n{r.stdout}{r.stderr}")
        got = "pass" if r.returncode == 0 else "fail"
        if got != expect:
            raise AssertionError(f"lesson {lesson}: expected {expect}, got {got}\n{r.stdout}{r.stderr}")
        print(f"  lesson {lesson}: {expect} as expected")
        return r.stdout

    @staticmethod
    def line(out, cid):
        """The check.py output line for one check id; its first word is 'ok' or '--'."""
        return next(ln for ln in out.splitlines() if ln.split()[1:2] == [cid])


def setup(root):
    shutil.copytree(SRC, root, ignore=shutil.ignore_patterns(".git", ".learning", "docs", "__pycache__"))
    l = Learner(root)
    l.git("init", "-q")
    l.git("symbolic-ref", "HEAD", "refs/heads/main")
    l.git("config", "user.name", "Selftest")
    l.git("config", "user.email", "selftest@example.com")
    l.git("add", ".")
    l.git("commit", "-q", "-m", "Initial curriculum")
    l.append("lessons/00-orientation/README.md", "\n<!-- maintainer edit after release -->\n")
    l.commit("fix(lesson-00): maintainer edit that must not count as learner work", "lessons/00-orientation/README.md")
    return l


def fresh_course(tmp, name):
    """A new course in tmp/name, so a regression owns its fixture."""
    return setup(os.path.join(tmp, name))


PROFILE = """# Ada

## About

I am **learning** Markdown and *Git* together.

## Tools I use

I write in `vscode` and run `git` in the terminal.

## Things I want to learn

1. Branches
   - why they exist
   - how to merge
2. Tables
3. Remotes

## A command I know

```bash
git status
```

---

## Links

I keep notes in [my notes](https://example.com).

![A placeholder image](https://picsum.photos/200)

> Simplicity is prerequisite for reliability.

This sentence contains a literal asterisk: \\* like that.
"""

NOTES = """# My notes

Notes I am keeping while learning Markdown and Git.

## Git commands so far

See [Git commands](git-commands.md).

## Lesson progress

- [x] 00 Orientation
- [x] 01 Markdown basics
- [ ] 02 Practical Markdown
- [ ] 03 Git foundations

## Files

- [Git commands](git-commands.md)
- [My profile](../profile.md)
"""

GIT_COMMANDS = """# Git commands

| Command      | What it does                      | Changes anything? |
|--------------|-----------------------------------|-------------------|
| `git status` | shows what Git thinks is going on | no                |
| `pwd`        | shows the current folder          | no                |
| `ls`         | lists files                       | no                |

[Back to notes](README.md)
"""


FAVORITES = "# Favorites\n\n- Favorite color: green\n- Favorite food: bread\n- Favorite tool: git\n"


def course_with_favorites(tmp, name):
    l = fresh_course(tmp, name)
    l.write("workspace/favorites.md", FAVORITES)
    l.commit("Add favorites", "workspace/favorites.md")
    return l


def run_helper(l):
    return subprocess.run([PY, "tools/setup_conflict.py"], cwd=l.root, capture_output=True, text=True)


# Refusal must leave the index, HEAD and branches exactly as found. (ref: DL-004)
def helper_refuses_staged_work(tmp):
    """setup_conflict.py commits with a plain git commit, which takes the whole
    index; it must refuse rather than sweep in work it did not create."""
    l = course_with_favorites(tmp, "helper-staged")
    l.write("workspace/hello.md", "# Hello\n")
    l.write("workspace/profile.md", "# Ada\n")
    l.commit("Add hello and profile", "workspace/hello.md", "workspace/profile.md")

    def refuses(why):
        state = lambda: [l.git(*a).stdout for a in (("status", "--porcelain"), ("rev-parse", "HEAD"), ("branch", "--list"))]
        before = state()
        r = run_helper(l)
        assert r.returncode == 1 and state() == before, f"helper did not refuse cleanly with {why}:\n{r.stdout}{r.stderr}"

    l.write("workspace/other.md", "unrelated\n")
    l.git("add", "workspace/other.md")
    refuses("a staged unrelated file")
    l.git("rm", "-q", "--cached", "workspace/other.md")
    os.remove(os.path.join(l.root, "workspace/other.md"))
    l.git("rm", "-q", "workspace/hello.md")
    refuses("a staged deletion")
    l.git("restore", "--staged", "--worktree", "workspace/hello.md")
    l.append("workspace/profile.md", "one\n")
    l.git("add", "workspace/profile.md")
    l.append("workspace/profile.md", "two\n")
    refuses("a partially staged edit")
    print("  conflict helper: refuses staged and modified work, changing nothing")


def helper_stops_on_git_failure(tmp):
    """A failing git command must not be reported as success."""
    if os.name == "nt":
        print("  conflict helper failure test: skipped (needs a POSIX hook)")
        return
    l = course_with_favorites(tmp, "helper-hook")
    hook = os.path.join(l.root, ".git", "hooks", "pre-commit")
    l.write(".git/hooks/pre-commit", "#!/bin/sh\nexit 1\n")
    os.chmod(hook, 0o755)
    r = run_helper(l)
    assert r.returncode == 1 and "Created branch" not in r.stdout, f"failed commit reported as success:\n{r.stdout}{r.stderr}"
    print("  conflict helper: a failed git command stops it")


# Ours, theirs and combined resolutions pass; one-sided merges do not. (ref: DL-005)
def conflict_resolutions_all_pass(tmp):
    """Keeping main's line, the branch's line, or a third value all resolve the
    conflict; the check must accept each, and reject a merge only one side changed."""
    l = course_with_favorites(tmp, "resolve-ff")
    l.git("switch", "-q", "-c", "side")
    l.edit("workspace/favorites.md", "green", "blue")
    l.commit("Change favorite color to blue", "workspace/favorites.md")
    l.git("switch", "-q", "main")
    l.git("merge", "-q", "--ff-only", "side")
    out = l.check("06", "fail")
    assert l.line(out, "06.merge.commit").split()[0] == "--", "a fast-forward wrongly counted as a conflict merge"
    for colour in ("red", "blue", "purple"):
        l = course_with_favorites(tmp, f"resolve-{colour}")
        assert run_helper(l).returncode == 0
        l.edit("workspace/favorites.md", "green", "red")
        l.commit("Change favorite color to red", "workspace/favorites.md")
        assert l.git("merge", "conflict-practice", ok=False).returncode != 0, "expected a conflict"
        l.write("workspace/favorites.md", FAVORITES.replace("green", colour))
        l.commit(f"Merge conflict-practice, choosing {colour}", "workspace/favorites.md")
        l.git("branch", "-d", "conflict-practice")
        out = l.check("06", "pass")
        assert l.line(out, "06.merge.commit").split()[0] == "ok", f"resolution {colour} not accepted"
    l = course_with_favorites(tmp, "resolve-one-sided")
    l.git("switch", "-q", "-c", "side")
    l.edit("workspace/favorites.md", "green", "blue")
    l.commit("Change favorite color to blue", "workspace/favorites.md")
    l.git("switch", "-q", "main")
    l.write("workspace/other.md", "# Other\n")
    l.commit("Add other", "workspace/other.md")
    l.git("merge", "-q", "--no-ff", "--no-edit", "side")
    out = l.check("06", "fail")
    assert l.line(out, "06.merge.commit").split()[0] == "--", "a merge that only one side changed favorites.md wrongly counted as a conflict merge"
    print("  conflict resolutions: ours, theirs and combined pass; one-sided merges do not")


# Follows the lesson text literally, so text and check cannot drift apart. (ref: DL-006)
def course_after_lesson_03(tmp, name):
    """A course where hello, profile and notes each have a commit of their own."""
    l = fresh_course(tmp, name)
    l.write("workspace/hello.md", "# Hello\n")
    l.write("workspace/profile.md", PROFILE)
    l.write("workspace/notes/README.md", NOTES)
    l.write("workspace/notes/git-commands.md", GIT_COMMANDS)
    l.commit("Add hello file", "workspace/hello.md")
    l.commit("Add profile page", "workspace/profile.md")
    l.commit("Add notes index and git command reference", "workspace/notes")
    return l


# Padding with unrelated and empty commits must not satisfy a per-path check. (ref: DL-007)
def bundled_commit_rejected(tmp):
    """One commit holding hello, profile and notes, padded with unrelated and
    empty commits, is not three separate commits."""
    l = fresh_course(tmp, "bundled")
    l.write("workspace/hello.md", "# Hello\n")
    l.write("workspace/profile.md", PROFILE)
    l.write("workspace/notes/README.md", NOTES)
    l.commit("Add hello, profile and notes together", "workspace")
    l.write("workspace/favorites.md", FAVORITES)
    l.commit("Add favorites", "workspace/favorites.md")
    l.git("commit", "-q", "--allow-empty", "-m", "Record an empty commit")
    out = l.check("03", "fail")
    assert l.line(out, "03.commit.separate").split()[0] == "--", "a bundled commit passed 03.commit.separate"
    print("  bundled commit: rejected by 03.commit.separate")


def combined_edit_rejected(tmp):
    """Editing profile and notes in one commit is one commit, not two more each."""
    l = course_after_lesson_03(tmp, "combined")
    l.append("workspace/profile.md", "4. Merge conflicts\n")
    l.append("workspace/notes/README.md", "- [ ] 04 Everyday Git\n")
    l.commit("Update profile and notes together", "workspace")
    out = l.check("04", "fail")
    assert l.line(out, "04.commits.two-more").split()[0] == "--", "a combined edit passed 04.commits.two-more"
    print("  combined edit: rejected by 04.commits.two-more")


# Follows the Recovery text literally to the checked state. (ref: DL-007)
def bundled_41_recovery_as_written(tmp):
    """Lesson 04.1 Recovery: a learner who bundled profile and notes must be
    able to reach 04.commits.two-more by the steps the lesson gives."""
    l = course_after_lesson_03(tmp, "recover-41")
    l.append("workspace/profile.md", "4. Merge conflicts\n")
    l.append("workspace/notes/README.md", "- [ ] 04 Everyday Git\n")
    l.commit("Update profile and notes together", "workspace")
    l.append("workspace/profile.md", "5. Remotes again\n")
    l.commit("Add a fifth item to the learning list", "workspace/profile.md")
    l.append("workspace/notes/README.md", "- [ ] 05 Branches\n")
    l.commit("Add branches to the progress checklist", "workspace/notes/README.md")
    l.write("workspace/hello.md", "oops\n")
    l.git("restore", "workspace/hello.md")
    l.write("workspace/scratch.md", "scratch\n")
    out = l.check("04", "pass")
    assert l.line(out, "04.commits.two-more").split()[0] == "ok", "4.1 Recovery did not reach 04.commits.two-more"
    print("  lesson 04.1 recovery: reaches 04.commits.two-more")


# Follows the Recovery text literally to the checked state. (ref: DL-007)
def bundled_32_recovery_as_written(tmp):
    """Lesson 03.2 Recovery: a learner who bundled profile and notes must be
    able to reach 03.commit.separate by the steps the lesson gives."""
    l = fresh_course(tmp, "recover-32")
    l.write("workspace/hello.md", "# Hello\n")
    l.commit("Add hello file", "workspace/hello.md")
    l.write("workspace/profile.md", PROFILE)
    l.write("workspace/notes/README.md", NOTES)
    l.write("workspace/notes/git-commands.md", GIT_COMMANDS)
    l.commit("Add profile and notes together", "workspace")
    l.append("workspace/profile.md", "4. Merge conflicts\n")
    l.commit("Add merge conflicts to learning list", "workspace/profile.md")
    l.append("workspace/notes/git-commands.md", "\nSee also the profile.\n")
    l.commit("Add a see-also line to the command reference", "workspace/notes")
    out = l.check("03", "pass")
    assert l.line(out, "03.commit.separate").split()[0] == "ok", "3.2 Recovery did not reach 03.commit.separate"
    print("  lesson 03.2 recovery: reaches 03.commit.separate")


def fenced_profile_rejected(tmp):
    """Markdown shown inside a code fence is not rendered Markdown."""
    l = fresh_course(tmp, "fenced")
    l.write("workspace/profile.md", "````text\n" + PROFILE + "````\n")
    out = l.check("01", "fail")
    for cid in ("01.profile.h1", "01.profile.bold", "01.profile.link"):
        assert l.line(out, cid).split()[0] == "--", f"{cid} passed on fenced text"
    l.write("workspace/profile.md", "~~~\n" + PROFILE)  # unclosed: runs to the end
    out = l.check("01", "fail")
    assert l.line(out, "01.profile.h1").split()[0] == "--", "an unclosed tilde fence was read as prose"
    print("  fenced profile: rejected, unclosed fence included")


def nested_example_fence_ok(tmp):
    """A four-backtick fence that shows a three-backtick example is one block."""
    l = fresh_course(tmp, "nested")
    l.write("workspace/profile.md", PROFILE + "\n## Fence example\n\n````markdown\n```bash\ngit status\n```\n````\n")
    l.check("01", "pass")
    print("  nested example fence: profile still passes")


# The remote must carry the second commit; local edits alone are not a pull. (ref: DL-009)
def local_edits_not_pull(tmp):
    """Two local reading-list commits are not a pull: the remote must have
    the second commit and main must contain it."""
    l = fresh_course(tmp, "local-edits")
    l.write("workspace/reading-list.md", "# Reading list\n\n- Pro Git\n")
    l.commit("Add reading list", "workspace/reading-list.md")
    remote = os.path.join(tmp, "local-edits-remote.git")
    l.git("init", "-q", "--bare", "-b", "main", remote)
    l.git("remote", "add", "origin", remote)
    l.git("push", "-q", "-u", "origin", "main")
    l.append("workspace/reading-list.md", "- A novel\n")
    l.commit("Add a novel to the reading list", "workspace/reading-list.md")
    l.append("workspace/reading-list.md", "- A poem\n")
    l.commit("Add a poem to the reading list", "workspace/reading-list.md")
    out = l.check("07", "fail")
    assert l.line(out, "07.remote.pulled").split()[0] == "--", "unpushed local edits passed 07.remote.pulled"
    print("  local edits: not accepted as a pull")


def scratch_recovery_as_written(tmp):
    """Lesson 04 Common Mistakes: a committed scratch file must be recoverable
    by the steps the lesson gives, without losing the file."""
    l = fresh_course(tmp, "scratch")
    l.write("workspace/scratch.md", "scratch\n")
    l.commit("Add scratch file", "workspace/scratch.md")
    l.git("rm", "-q", "--cached", "workspace/scratch.md")
    l.git("commit", "-q", "-m", "Stop tracking scratch file")
    out = l.check("04", "fail")
    assert l.line(out, "04.scratch.untracked").split()[0] == "ok", "recovery steps did not reach the checked state"
    assert open(os.path.join(l.root, "workspace/scratch.md")).read() == "scratch\n", "recovery lost the file contents"
    print("  scratch recovery: lesson 04 steps reach the checked state")


def commits_before_first_check(l):
    """A learner who does a whole lesson and only then runs the checker must
    still have their commits recognised (found by hand-walking lesson 03)."""
    l.write("workspace/hello.md", "# Hello\n\nThis is my first Markdown file.\n")
    l.commit("Add hello file", "workspace/hello.md")
    out = l.check("03", "fail")
    assert "03.commit.hello" not in [ln.split()[1] for ln in out.splitlines() if ln.strip().startswith("--")], \
        "a commit made before the first check run was not counted as the learner's"
    print("  commits made before the first check run: counted")


def next_step_moves_forward(l):
    """Passing a lesson must point at the next one, not back to lesson 00."""
    out = l.check("00", "pass")
    assert "01-markdown-basics" in out, f"next step did not point forward:\n{out}"
    print("  next-step line: points forward")


def protected_files(l):
    out = l.check("00", "fail")
    assert "course files differ" not in out, "maintainer commit wrongly flagged as learner edit"
    l.append("lessons/01-markdown-basics/README.md", "accidental edit\n")
    out = l.check("00", "fail")
    assert "course files differ" in out and "01-markdown-basics" in out, "learner edit to a lesson not flagged"
    l.git("restore", "lessons/01-markdown-basics/README.md")
    print("  protected-file warning: works")


def lesson_00_02(l):
    l.check("01", "fail")
    l.write("workspace/profile.md", PROFILE)
    l.check("01", "pass")
    l.check("02", "fail")
    l.write("workspace/notes/README.md", NOTES)
    l.write("workspace/notes/git-commands.md", GIT_COMMANDS)
    l.check("02", "pass")


def lesson_03(l):
    l.check("03", "fail")  # hello.md is already committed by the earlier regression check
    l.commit("Add profile page", "workspace/profile.md")
    l.commit("Add notes index and git command reference", "workspace/notes")
    l.check("03", "pass")


def lesson_04(l):
    l.append("workspace/profile.md", "4. Merge conflicts\n")
    l.edit("workspace/notes/README.md", "- [ ] 03 Git foundations", "- [x] 03 Git foundations\n- [ ] 04 Everyday Git")
    l.commit("Add merge conflicts to learning list", "workspace/profile.md")
    l.commit("Tick lesson 03 in progress checklist", "workspace/notes/README.md")
    l.write("workspace/hello.md", "oops\n")
    l.check("04", "fail")
    l.git("restore", "workspace/hello.md")
    l.write("workspace/scratch.md", "scratch\n")
    l.git("add", "workspace/scratch.md")
    l.check("04", "fail")
    l.git("restore", "--staged", "workspace/scratch.md")
    l.check("04", "pass")


def lesson_05(l):
    l.git("switch", "-q", "-c", "reading-list")
    l.write("workspace/reading-list.md", "# Reading list\n\n- [Pro Git](https://git-scm.com/book)\n- CommonMark spec\n- A novel\n")
    l.commit("Add reading list", "workspace/reading-list.md")
    l.append("workspace/notes/README.md", "- [Reading list](../reading-list.md)\n")
    l.commit("Link reading list from notes index", "workspace/notes/README.md")
    l.git("switch", "-q", "main")
    l.check("05", "fail")
    l.git("merge", "-q", "reading-list")
    l.git("branch", "-d", "reading-list")
    l.check("05", "pass")


def lesson_06(l):
    l.write("workspace/favorites.md", "# Favorites\n\n- Favorite color: green\n- Favorite food: bread\n- Favorite tool: git\n")
    l.commit("Add favorites", "workspace/favorites.md")
    r = run_helper(l)
    assert r.returncode == 0, r.stdout + r.stderr
    l.edit("workspace/favorites.md", "green", "red")
    l.commit("Change favorite color to red", "workspace/favorites.md")
    merge = l.git("merge", "conflict-practice", ok=False)
    assert merge.returncode != 0 and "CONFLICT" in merge.stdout, "expected a conflict"
    l.check("06", "fail")
    l.write("workspace/favorites.md", "# Favorites\n\n- Favorite color: purple\n- Favorite food: bread\n- Favorite tool: git\n")
    l.commit("Merge conflict-practice, choosing purple", "workspace/favorites.md")
    l.git("branch", "-d", "conflict-practice")
    l.check("06", "pass")


def lesson_07(l, tmp):
    remote = os.path.join(tmp, "learn-git-remote.git")
    clone = os.path.join(tmp, "learn-git-clone")
    l.git("init", "-q", "--bare", "-b", "main", remote)
    l.git("remote", "add", "origin", remote)
    l.check("07", "fail")
    l.git("push", "-q", "-u", "origin", "main")
    l.git("clone", "-q", remote, clone)
    c = Learner(clone)
    c.git("config", "user.name", "Clone")
    c.git("config", "user.email", "clone@example.com")
    c.append("workspace/reading-list.md", "- Added from the clone\n")
    c.commit("Add a book from the clone", "workspace/reading-list.md")
    c.git("push", "-q")
    l.git("fetch", "-q")
    l.git("pull", "-q")
    l.check("07", "pass")


def lesson_08(l):
    out = l.check("08", "fail")
    assert "cannot be checked" in out, "missing README was not reported as missing"
    l.git("switch", "-q", "-c", "docs-improvements")
    l.write("workspace/project/README.md", "# Pantry\n\nA list of what is in the kitchen.\n\n## Files\n\n- [Install](INSTALL.md)\n- [Changelog](CHANGELOG.md)\n")
    l.commit("Add pantry project README", "workspace/project/README.md")
    l.write("workspace/project/INSTALL.md", "# Install\n\n```bash\ncp pantry.md ~/\n```\n")
    l.commit("Add install instructions", "workspace/project/INSTALL.md")
    l.write("workspace/project/CHANGELOG.md", "# Changelog\n\n## Today\n\n- Started the pantry docs.\n")
    l.commit("Add changelog", "workspace/project/CHANGELOG.md")
    l.append("GLOSSARY.md", "| **fast-forward** | A merge where the branch label simply moves ahead; no merge commit. | 05 |\n")
    l.commit("Add fast-forward to glossary", "GLOSSARY.md")
    l.git("switch", "-q", "main")
    l.check("08", "fail")
    l.git("merge", "-q", "--no-ff", "--no-edit", "docs-improvements")
    l.git("branch", "-d", "docs-improvements")
    l.check("08", "pass")


CAPSTONE = """# Trail Log

A **journal** of *hikes*.

## Getting started

1. Clone the repository
2. Open `log.md`

### Details

- Boots
- Water

| Trail | Km |
|-------|----|
| Ridge | 12 |

```bash
git log --oneline
```

- [ ] Add photos
- [x] Write first entry

See the [log](log.md) and [RECOVERY](RECOVERY.md).
"""


def lesson_09(l):
    l.git("switch", "-q", "-c", "capstone")
    l.write("workspace/capstone/README.md", CAPSTONE)
    l.commit("Add trail log README", "workspace/capstone/README.md")
    l.write("workspace/capstone/log.md", "# Log\n\n- Ridge trail, sunny.\n")
    l.commit("Add first log entry", "workspace/capstone/log.md")
    l.write("workspace/capstone/log.md", "garbage\n")
    l.git("restore", "workspace/capstone/log.md")
    l.write("workspace/capstone/RECOVERY.md", "# Recovery\n\nI overwrote log.md. `git diff` showed every line removed, so I ran `git restore workspace/capstone/log.md`.\n")
    l.commit("Document recovering log.md with git restore", "workspace/capstone/RECOVERY.md")
    l.append("workspace/capstone/log.md", "- River loop, rain.\n")
    l.commit("Add second log entry", "workspace/capstone/log.md")
    l.git("switch", "-q", "main")
    l.check("09", "fail")
    l.git("merge", "-q", "--no-ff", "--no-edit", "capstone")
    l.git("branch", "-d", "capstone")
    l.check("09", "pass")
    l.check("all", "pass")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        print("Simulating a learner in a temporary copy...")
        l = setup(os.path.join(tmp, "course"))
        protected_files(l)
        commits_before_first_check(l)
        next_step_moves_forward(l)
        lesson_00_02(l)
        lesson_03(l)
        lesson_04(l)
        lesson_05(l)
        lesson_06(l)
        lesson_07(l, tmp)
        lesson_08(l)
        lesson_09(l)
        for regression in (helper_refuses_staged_work,
                           helper_stops_on_git_failure,
                           conflict_resolutions_all_pass,
                           scratch_recovery_as_written,
                           bundled_commit_rejected,
                           combined_edit_rejected,
                           bundled_41_recovery_as_written,
                           bundled_32_recovery_as_written,
                           fenced_profile_rejected,
                           nested_example_fence_ok,
                           local_edits_not_pull):
            regression(tmp)
        r = subprocess.run([PY, "tools/review.py", "--selfcheck"], cwd=l.root, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        r = subprocess.run([PY, "tools/review.py"], cwd=l.root, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "unclassified" not in r.stdout or "Likely cause" in r.stdout
        print("  review.py and its classification self-check ran on the simulated data")
    print("Selftest passed: every lesson fails before the work and passes after.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
