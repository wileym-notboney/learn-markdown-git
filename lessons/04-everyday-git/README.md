# Lesson 04 — Everyday Git

## Objectives

By the end of this lesson you can:

- write a commit message someone else will thank you for
- stage some files and not others on purpose
- look at what a past commit changed
- throw away an edit you regret, safely
- unstage something you staged by accident
- tell the difference between commands that report, commands that move
  changes, and commands that discard changes

## Concepts

### Commit messages

A message has a short **subject** line and, optionally, a blank line and a
longer body. Conventions that make history readable:

- Subject under about 50 characters, 72 at most.
- Imperative mood: "Add table", "Fix broken link", not "Added" or "Fixes".
  Read it as "this commit will … *Add table*".
- Say what and why, not how. The diff already shows how.
- Capitalise the first word, no full stop at the end.

Bad: `update`, `stuff`, `fixed it`, `asdf`.
Good: `Add reading list to notes`, `Fix relative link to profile`.

The checker looks at your recent messages and flags the obviously lazy
ones. Not to be strict — because in a month, `update` tells you nothing.

### Staging is a choice

`git add` takes a *path*. Give it one file and only that file is staged.
That is how you turn "I edited five things this afternoon" into three
tidy commits. Habit: `git status` → `git add` the files that belong
together → `git diff --staged` → `git commit`.

Edited two unrelated things in the *same* file? `git add -p <file>` walks
through each change and asks `y`/`n`. Try it once; it is optional.

### Inspecting history

| Command | Shows |
|---------|-------|
| `git log --oneline` | one line per commit |
| `git log -3` | the last three commits in full |
| `git log -p -1` | the last commit with its diff |
| `git log -- <file>` | only commits that touched that file |
| `git show <hash>` | one specific commit with its diff |

All read-only.

### Three kinds of commands

| Kind | Examples | Risk |
|------|----------|------|
| Report | `status`, `diff`, `log`, `show` | none |
| Move changes forward | `add`, `commit` | none; everything is recoverable |
| Discard changes | `restore` | **loses uncommitted edits** |

Git only becomes dangerous when a command *discards*. This lesson
introduces exactly one such command, `git restore`, because you need it.
It is explained before you run it.

### `git restore`

`git restore <file>` replaces the working-tree version of a file with the
version in the staging area (or, if nothing is staged, the version in
HEAD). Any *uncommitted* edits to that file are gone and cannot be
recovered. Committed versions are untouched.

`git restore --staged <file>` does something different and harmless: it
moves a file out of the staging area without changing its contents. Use it
when you `git add`ed the wrong thing.

Before any `git restore` without `--staged`: run `git diff <file>` and
confirm the changes shown are the ones you want to lose.

### Commands you will see mentioned elsewhere, and should not run yet

- `git checkout` — the old command that did both switching and restoring.
  Ambiguous; this course uses `git switch` and `git restore` instead.
- `git reset --hard` — discards all uncommitted changes to every file and
  can move history. Never needed in this course.
- `git clean` — deletes untracked files. Never needed here.

If a tutorial or an assistant suggests one of these, ask what it is for
and whether `restore` or `switch` would do.

### `.gitignore`

Some files should never be committed: editor backups, secrets, your local
progress file. A file named `.gitignore` at the top of the repository lists
patterns Git should not track. Open this repository's `.gitignore` to see
why `.learning/` never appears in `git status`.

---

## Exercise 4.1 — Two edits, two commits

### Goal

Edit `workspace/profile.md` and `workspace/notes/README.md`, then commit
each change separately with a good message.

### Why This Matters

Editing more than one thing before committing is normal. Sorting the edits
into sensible commits afterwards is the everyday skill.

### Before You Start

Lesson 03 passed; `git status` reports a clean working tree.

### Instructions

1. In `workspace/profile.md`, add one line to the "Things I want to learn"
   list.

2. In `workspace/notes/README.md`, tick the Lesson 03 checkbox
   (`[ ]` → `[x]`) and add Lesson 04.

3. Look at the combined state:

   ```text
   git status
   git diff
   ```

   Both files are *modified* and the diff shows both changes.

4. Stage and commit only the profile change. Choose your own message; make
   it say what changed.

   ```text
   git add workspace/profile.md
   git diff --staged
   git commit -m "..."
   ```

5. `git status` — the notes change is still unstaged. Stage and commit it
   with its own message.

6. `git log --oneline -3` to see both.

### Check Your Work

```text
python tools/check.py 04
```

The `04.messages.*` checks read your last several commit subjects.

### What You Should Notice

- `git diff` (unstaged) and `git diff --staged` show different things after
  step 4. Together they always add up to "everything changed since HEAD".
- Nothing forced you to commit separately. Git leaves that judgement to you.

### Common Mistakes

- `git add .` here would stage both and squash two ideas into one commit.
- A subject like "changes". Say which change.

### Recovery

Staged the wrong file? `git restore --staged <file>`. Committed both
together? Fine; do the next exercise's commits separately instead.

### Reflection

- Which of your two messages would be more useful in six months? Why?

---

## Exercise 4.2 — Make a mistake and throw it away

### Goal

Damage `workspace/hello.md`, see the damage in a diff, and restore the
committed version.

### Why This Matters

This is the core promise of Git: committed work is safe, so experiments are
cheap. You should feel this once, on purpose, before it happens by accident.

### Before You Start

Exercise 4.1 done; working tree clean.

### Instructions

1. Open `workspace/hello.md`. Delete everything in it. Type `oops`. Save.

2. See what you did:

   ```text
   git status
   git diff workspace/hello.md
   ```

   *Expected:* every original line with `-`, one `+oops` line.

3. Decide: you want the committed version back. Confirm the diff shows
   only things you are happy to lose (it does — you just wrote `oops`).

4. Restore it. **This discards the uncommitted edit to that one file.**

   ```text
   git restore workspace/hello.md
   ```

5. Confirm:

   ```text
   git status
   cat workspace/hello.md
   ```

   *Expected:* clean working tree; the original contents are back.

### Check Your Work

```text
python tools/check.py 04
```

The checker confirms `hello.md` matches its committed version.

### What You Should Notice

- The edit did not exist anywhere but the working tree. That is why
  `restore` could remove it without a trace, and why uncommitted work is the
  only kind Git can lose.
- `git diff` before `git restore` is the safety step. Make it a habit.

### Common Mistakes

- Running `git restore .` (a dot): restores *every* modified file. Correct
  when intended; costly when not. Name the file.
- Expecting `restore` to bring back an *untracked* file you deleted. It
  cannot; Git never had a copy. Only committed versions can be restored.

### Recovery

If you restored the wrong file and lost an edit you wanted: it is gone.
Re-make the edit. This is the one lesson where recovery is "type it again",
which is exactly why the lesson exists.

### Reflection

- What would `git restore workspace/profile.md` have done at step 4? Would
  it have been harmful?

---

## Exercise 4.3 — Stage by accident, unstage on purpose

### Goal

Create a scratch file, accidentally stage it, unstage it, and leave it
untracked.

### Why This Matters

`git add .` and editor Git buttons stage things you did not mean to.
Knowing `restore --staged` means you never have to commit junk.

### Before You Start

Exercise 4.2 done; working tree clean.

### Instructions

1. Create `workspace/scratch.md` with a line of anything.

2. Stage it as if by accident:

   ```text
   git add workspace/scratch.md
   git status
   ```

   It is under *Changes to be committed*.

3. You did not mean to. Take it back out of the staging area. This does not
   touch the file's contents:

   ```text
   git restore --staged workspace/scratch.md
   git status
   ```

   *Expected:* `scratch.md` is back under *Untracked files*. The file is
   still on disk with your line in it — check with `cat`.

4. Leave it there. Do not commit it and do not delete it. The checker wants
   to find it existing, untracked, and unstaged.

### Check Your Work

```text
python tools/check.py 04
```

### What You Should Notice

- `restore --staged` and `restore` share a name and do very different
  things. The `--staged` form is always safe.
- An untracked file that sits there forever is a small smell. In real
  projects you either commit it or add it to `.gitignore`. Here it stays as
  evidence.

### Common Mistakes

- Running `git restore workspace/scratch.md` (no `--staged`) on an
  untracked file: Git says it has no version to restore from. Harmless.
- Committing it by reflex. If you did, `git log --oneline -1` will show it;
  that is acceptable, but then delete the file and commit the deletion so the
  check can see the intended end state is "untracked" — or simply create a
  different scratch file.

### Recovery

`git status` tells you which section the file is in. Move it with
`git add` or `git restore --staged` until it is under *Untracked files*.

### Reflection

- In one sentence each: what does `git add` do, and what does
  `git restore --staged` do?
