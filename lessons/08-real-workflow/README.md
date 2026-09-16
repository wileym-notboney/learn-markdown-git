# Lesson 08 — A Real Workflow

## Objectives

Do a small documentation project the way it is done in practice: on a
branch, in several logical commits, merged with a visible merge commit,
then inspected. This lesson gives goals and hints, not commands. If you
need a command, your notes in `workspace/notes/git-commands.md` should have
it; if they do not, that is a sign to add it.

## Concepts

### `--no-ff`

In Lesson 05 the merge fast-forwarded and left no trace that a branch
existed. Sometimes you want the branch visible in history — "these four
commits were one piece of work". `git merge --no-ff <branch>` forces a
merge commit even when a fast-forward was possible. Many teams use this
for every feature branch. Look at the difference with
`git log --oneline --graph` afterwards.

### Logical commits

One commit per idea. "Add install instructions" and "Add changelog" are two
commits even if you wrote them in the same sitting. Reviewers read commits
one at a time; a commit that does three things is three times as hard to
review. Use `git add <file>` (or `git add -p`) to split.

### Maintaining the repository you learn from

You have been told not to edit curriculum files. `GLOSSARY.md` is the
exception: it belongs to everyone using this course, and adding a term you
had to look up is a real contribution. This lesson asks you to.

---

## Exercise 8.1 — Document a small project on a branch

### Goal

On a branch named `docs-improvements`, create a documentation set for a
small project (real or invented) in `workspace/project/`, in at least
three commits; add one term to `GLOSSARY.md`; merge with `--no-ff`;
delete the branch; read the graph.

### Why This Matters

This is the loop you will run for every piece of work for the rest of your
Git life. The only new thing is that nobody is telling you the commands.

### Before You Start

Lesson 07 passed. On `main`, clean tree. (The optional GitHub exercise
does not matter here.)

### Instructions

1. Create the branch and switch to it.

2. Create `workspace/project/README.md` for a small project: a tool, a
   recipe collection, a game, anything. Follow the README shape from
   Lesson 02 (what it is, who it is for, how to start, where things are).
   Commit.

3. Create `workspace/project/INSTALL.md` (or `SETUP.md`, or `USAGE.md` —
   something a user would need). Include a fenced code block. Link to it
   from the README with a relative link. Commit.

4. Create `workspace/project/CHANGELOG.md` with a heading and one entry
   describing today's work. Link it from the README. Commit.

5. Add one row to the table in `GLOSSARY.md` (top of the course folder)
   for a term you had to look up or think about. Commit with a message that
   says which term.

6. Check the branch: `git log --oneline main..docs-improvements` lists only
   the commits on the branch (read-only; `main..X` means "on X but not on
   main"). At least four.

7. Switch to `main`, merge with `--no-ff`, delete the branch.

8. Read `git log --oneline --graph -8`. The branch should be visible as a
   loop that leaves `main` and rejoins at a merge commit.

### Check Your Work

```text
python tools/check.py 08
```

Checks: at least two Markdown files in `workspace/project/`, links between
them resolve, at least three commits touched that folder, `GLOSSARY.md`
gained a row, a merge commit mentions `docs-improvements`, the branch is
gone, and recent messages are decent.

### What You Should Notice

- Hints you needed: were they Markdown or Git? Add the answers to your
  notes so the capstone needs fewer.
- Compare this merge's graph with Lesson 05's. Same operation, different
  record.

### Common Mistakes

- Committing everything in one go at the end. The checker counts commits
  touching the folder; more importantly, you lose the habit.
- Forgetting to switch back to `main` before merging.
- Editing `GLOSSARY.md` on `main` instead of the branch. Works, but the
  point is that all the work travels together.

### Recovery

- Merged without `--no-ff` and got a fast-forward? Nothing is lost; the
  commits are all on `main`. To get the merge commit the checker looks for:
  create `docs-improvements` again from `main`, add one more small commit
  on it (a line in `CHANGELOG.md` noting what happened), switch to `main`,
  merge with `--no-ff`, delete the branch.
- On the wrong branch with uncommitted work? Commit it where you are, or
  `git switch` (Git will carry the changes if it safely can).

### Reflection

- Which commands did you look up? Which did you not need to?
- When would you *not* want `--no-ff`?
