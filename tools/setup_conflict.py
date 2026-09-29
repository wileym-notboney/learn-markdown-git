#!/usr/bin/env python3
# ABOUTME: Creates the controlled merge conflict for Lesson 06: a branch that edits one line of favorites.md.
# ABOUTME: Usage: python tools/setup_conflict.py. Refuses to run unless the repository is in the expected state.
"""Prepare the Lesson 06 conflict.

Creates branch conflict-practice from main, changes the "Favorite color"
line in workspace/favorites.md there, commits, and returns to main. The
learner then edits the same line on main and merges. Nothing else is touched.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAVES = os.path.join(ROOT, "workspace", "favorites.md")
BRANCH = "conflict-practice"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def refuse(why, fix):
    print(f"Not doing anything: {why}\n  {fix}")
    return 1


def main():
    if git("branch", "--show-current").stdout.strip() != "main":
        return refuse("you are not on main.", "git switch main, then run this again.")
    if git("branch", "--list", BRANCH).stdout.strip():
        return refuse(f"branch {BRANCH} already exists.",
                      f"If you want to start over: git branch -D {BRANCH}, then run this again.")
    if git("status", "--porcelain", "--", "workspace/favorites.md").stdout.strip():
        return refuse("workspace/favorites.md has uncommitted changes.", "Commit it first (step 2), then run this again.")
    if git("ls-files", "--error-unmatch", "workspace/favorites.md").returncode != 0:
        return refuse("workspace/favorites.md is not committed yet.", "Create it and commit it (steps 1–2).")
    # A plain git commit takes the whole index, so any other staged or modified tracked
    # file would be committed as part of this helper's commit. Untracked files are safe.
    # (ref: DL-004)
    unrelated = [l for l in git("status", "--porcelain").stdout.splitlines() if not l.startswith("??")]
    if unrelated:
        return refuse("other tracked or staged changes would be swept into the new commit:\n    " + "\n    ".join(unrelated),
                      "Commit or stash them yourself, then run this again.")
    with open(FAVES, encoding="utf-8") as fh:
        lines = fh.read().splitlines(keepends=True)
    idx = next((i for i, l in enumerate(lines) if "Favorite color" in l), None)
    if idx is None:
        return refuse("no line containing 'Favorite color' in favorites.md.", "Use the template from step 1.")
    return make_branch(lines, idx)


def stopped(label, detail):
    """Report a failed step and where it left the repository. Nothing is undone."""
    print(f"Stopped: {label} failed.\n{detail.strip()}")
    print(f"You are on branch {git('branch', '--show-current').stdout.strip()}. "
          "Nothing was undone; inspect with git status.")
    return 1


def step(label, *args):
    """Run one git command; return None on success, else report and return 1."""
    result = git(*args)
    if result.returncode == 0:
        return None
    return stopped(label, result.stderr.strip() or f"(no output from git; exit code {result.returncode})")


def write_favorites(lines):
    try:
        with open(FAVES, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
    except OSError as err:
        return stopped("writing workspace/favorites.md", str(err))


def make_branch(lines, idx):
    lines[idx] = "- Favorite color: blue\n"
    # Every git call is checked and the first failure stops the run with the repository
    # left as-is: success is printed only after the branch tip is verified. Nothing is
    # reset or restored, because learner work may be present. (ref: DL-004)
    failure = (step("git switch -c", "switch", "-c", BRANCH)
               or write_favorites(lines)
               or step("git add", "add", "workspace/favorites.md")
               or step("git commit", "commit", "-m", "Change favorite color to blue")
               or step("git switch main", "switch", "main"))
    if failure:
        return failure
    if ("Favorite color: blue" not in git("show", f"{BRANCH}:workspace/favorites.md").stdout
            or git("branch", "--show-current").stdout.strip() != "main"):
        return stopped("verifying the result", f"{BRANCH} lacks the blue line, or you are not on main.")
    print(f"Created branch {BRANCH} with one commit that sets the favorite color to blue.")
    print("You are back on main. favorites.md here is unchanged.")
    print("Next: edit the same 'Favorite color' line on main to a different colour, commit, then git merge conflict-practice.")


if __name__ == "__main__":
    sys.exit(main())
