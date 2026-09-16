# Lesson 05 — Branches

## Objectives

By the end of this lesson you can:

- say why branches exist
- create a branch, switch to it, and see which one you are on
- commit on a branch and watch `main` stay unchanged
- merge a branch into `main` and delete it

From here on, instructions include fewer exact commands and more "you know
how to do this". If you do not, the Concepts section and your notes have
the answer.

## Concepts

### The problem

You want to try something — restructure your notes, draft a new page — but
you are not sure it will be good, and you want `main` to stay usable in the
meantime. Copying the folder is the old answer. Branches are Git's.

### Mental model

History is a chain of commits. A **branch** is a name that points at one
commit — the tip of a line of work. When you commit while on a branch, the
branch moves forward to the new commit. Other branches do not move.

```text
                  ┌── D ── E      reading-list
A ── B ── C ──────┘
                  main
```

Here `main` still points at `C`. The branch `reading-list` has two extra
commits. Files in your working tree change when you *switch* branches,
because Git swaps them to match the branch's tip.

**`main`** is just the branch everyone agrees is "the real one". There is
nothing special about it otherwise.

### Switching

`git switch <branch>` moves you onto a branch and updates the working tree
to match. `git switch -c <name>` creates a new branch from where you are
and switches to it in one step.

Switching with uncommitted changes: Git carries the edits across if they do
not clash with the target branch, and refuses (with a clear message) if they
would. Refusing is the safe outcome; commit or restore first.

### Knowing where you are

```text
git branch                  lists branches; * marks the current one
git branch --show-current   prints just the current branch name
git status                  first line: "On branch ..."
```

Most branch confusion is "I thought I was on main". Check before you
commit.

### Merging

`git merge <branch>` brings the commits from `<branch>` into the branch you
are currently on. Sequence: switch to the branch that should *receive* the
work (usually `main`), then merge the branch that *has* the work.

Two things can happen:

- **Fast-forward**: `main` has not moved since the branch was created, so
  Git just slides the `main` label forward. No new commit.
- **Merge commit**: both branches have new commits. Git creates a commit
  with two parents that joins them. If both changed the same lines, Git
  stops and asks you — that is Lesson 06.

### Deleting a merged branch

Once merged, the branch name has done its job. `git branch -d <name>`
removes the name. The commits stay; they are part of `main` now. Git
refuses `-d` on an unmerged branch, which protects you.

### Seeing the shape

```text
git log --oneline --graph --all
```

Draws the branch structure with text. Read-only; use it constantly in this
lesson.

---

## Exercise 5.1 — Draft a page on a branch, then merge it

### Goal

Create a branch `reading-list`, add `workspace/reading-list.md` on it,
confirm `main` does not have the file, merge, and delete the branch.

### Why This Matters

This is the shape of nearly all real Git work: branch, commit, merge,
delete. Everything later is a variation.

### Before You Start

Lesson 04 passed. `git status` clean apart from the untracked
`workspace/scratch.md` (that is expected).

### Instructions

1. Confirm you are on `main` and note the latest commit:

   ```text
   git branch --show-current
   git log --oneline -1
   ```

2. Create and switch to a new branch:

   ```text
   git switch -c reading-list
   ```

   *Expected:* `Switched to a new branch 'reading-list'`.

3. Create `workspace/reading-list.md`: a heading and a list of at least
   three things you want to read (books, articles, docs). Use a link for at
   least one.

4. Stage and commit it on this branch, with a good message. You know how.

5. Add it to the file index in `workspace/notes/README.md` and commit that
   too. Two commits on the branch now.

6. Look at the shape:

   ```text
   git log --oneline --graph --all
   ```

   *Expected:* your two commits above, with `(HEAD -> reading-list)` on the
   top one and `(main)` two commits down.

7. Switch back to `main` and look in `workspace/`:

   ```text
   git switch main
   ls workspace
   ```

   *Expected:* no `reading-list.md`. It exists only on the branch. Open
   `workspace/notes/README.md`; the index line is gone too. Nothing is lost:
   `git switch reading-list` would bring it all back.

8. Merge the branch into `main`:

   ```text
   git merge reading-list
   ```

   *Expected:* `Fast-forward` and a list of files changed. `ls workspace`
   now shows the file.

9. Delete the finished branch and view the result:

   ```text
   git branch -d reading-list
   git log --oneline --graph
   ```

### Check Your Work

```text
python tools/check.py 05
```

### What You Should Notice

- Switching changed your files on disk. That surprises everyone once.
- The merge was a fast-forward because `main` had not moved. The history is
  a straight line; you cannot tell a branch was ever used. Lesson 08 shows
  how to keep the branch visible when that matters.
- Deleting the branch removed a *name*, not commits.

### Common Mistakes

- Committing on `main` by accident because the switch was forgotten. Check
  `git status`'s first line before committing. If it happened: not a
  disaster; the exercise's end state is the same.
- `git merge` while still on `reading-list`: "Already up to date". You
  merged the branch into itself. Switch to `main` first.
- `git branch -d` before merging: Git refuses. Good.

### Recovery

- Wrong branch? `git switch main` or `git switch reading-list`. Uncommitted
  edits come along or Git tells you they cannot.
- Deleted a branch you had not merged? `git branch -d` refuses, so this
  cannot happen with `-d`. (`-D` forces it; do not.)
- Confused about the state? `git log --oneline --graph --all` and
  `git status`. Read both before acting.

### Reflection

- Why did `main` not get the new file until you merged?
- If you had made a commit on `main` between steps 7 and 8, what would the
  merge have looked like?

---

## Optional Challenge 5.2 — Two branches at once

### Goal

Create two branches from `main`, make a different commit on each, merge
both, and read the graph.

### Why This Matters

Real projects have several branches in flight. Seeing the graph fork and
rejoin makes the model stick.

### Before You Start

Exercise 5.1 passed. Optional.

### Instructions

Create `idea-a` and `idea-b` from `main`. On each, add a different line to
`workspace/reading-list.md` (different lines, not the same one). Merge `idea-a`
into `main`, then `idea-b`. The second merge is not a fast-forward — read
what Git says. Delete both branches.

### Check Your Work

`git log --oneline --graph` should show a diamond. The checker does not
require this exercise.

### What You Should Notice

Git merged two edits to the same file automatically because they touched
different lines.

### Common Mistakes

Editing the same line on both: you get a conflict. That is Lesson 06;
`git merge --abort` backs out if you want to wait.

### Recovery

`git merge --abort` during a conflicted merge returns to the pre-merge
state.

### Reflection

- What would have to be true for Git to be unable to merge automatically?
