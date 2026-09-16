# Lesson 03 — Git Foundations

## Objectives

By the end of this lesson you can:

- explain the working tree, the staging area, and history, and how a change
  moves between them
- read `git status` and say which of those three places each file is in
- read a `git diff`
- make a commit with a message
- read `git log`

You will commit the three files you wrote in Lessons 00–02. They become the
first entries in your learning history.

## Concepts

### The problem Git solves

You edit a file. Later you want to know what you changed, or get back the
old version, or try something without ruining what works. Copying files
around (`notes-old.md`, `notes-v2.md`) sort of works and quickly becomes
chaos. Git replaces the copies with **snapshots** you can name, compare, and
return to.

### Three places

Every file in a repository is in some combination of three places:

```text
 working tree            staging area              history
 (your actual files)     (what goes in the         (commits: saved
                          next snapshot)            snapshots)

  edit a file  ──git add──▶  staged  ──git commit──▶  committed
```

- **Working tree**: the files as they are on disk right now. Your editor
  edits these.
- **Staging area** (also called the *index*): a holding area where you
  collect the changes you want in the next snapshot. `git add` puts a
  change here. Staging exists so you can commit *some* of your edits and
  not others.
- **History**: the chain of commits. `git commit` takes everything in the
  staging area and saves it as a new commit with a message.

A **commit** is a snapshot of the whole project plus a message, an author,
a timestamp, and a link to the previous commit. Commits are permanent in
the sense that you can always get back to one; nothing in this course
deletes them.

### Tracked and untracked

A file Git has committed at least once is **tracked**: Git compares it to
the last snapshot and reports changes. A file Git has never committed is
**untracked**: Git sees it exists and otherwise ignores it. Your three
`workspace/` files are untracked right now.

### HEAD

`HEAD` is Git's name for "the commit you are standing on", normally the
latest commit in your history. "Changes since HEAD" means "changes
since the last snapshot".

### Reading `git status`

`git status` groups files by where they are:

```text
On branch main
Changes to be committed:            ← staged; will go in the next commit
        new file:   workspace/hello.md

Changes not staged for commit:      ← tracked, edited, not yet staged
        modified:   README.md

Untracked files:                    ← Git has never committed these
        workspace/profile.md
```

Ask three questions, in order: What is staged? What is changed but not
staged? What is untracked? The answers tell you what `git commit` would
and would not include.

### Reading `git diff`

`git diff` shows exactly which lines changed, file by file:

```text
--- a/workspace/hello.md          ← the old version
+++ b/workspace/hello.md          ← the new version
@@ -1,3 +1,4 @@                   ← where in the file (line numbers)
 # Hello
                                   ← unchanged lines have a space in front
-This is my first Markdown file.  ← removed line
+This is my first Markdown file!  ← added line
+I edited it.
```

`git diff` alone shows working tree vs staging area (what you have not
staged yet). `git diff --staged` shows staging area vs HEAD (what you are
about to commit). Both are read-only.

### Reading `git log`

`git log` lists commits, newest first. `git log --oneline` compresses each
to one line: a short id (a *hash*, like `3f2a9c1`) and the message. The
hash is how Git names a commit; you rarely type it.

### The four commands

| Command | Where it acts | Changes anything? |
|---------|---------------|-------------------|
| `git status` | reports | no |
| `git diff` | reports | no |
| `git add <file>` | working tree → staging area | yes, staging only |
| `git commit -m "message"` | staging area → history | yes, creates a commit |
| `git log` | reports | no |

### Your name on commits

Every commit records an author. If Git has no name configured it will
refuse to commit and tell you what to run. Set it once (any name and email
you like; nothing is sent anywhere):

```text
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

## Exercise 3.1 — Watch a change move through the three places

### Goal

Stage and commit `workspace/hello.md`, running `git status` between every
step so you see the file move.

### Why This Matters

Most Git confusion is not knowing *where* a change currently is. Watching
one file travel the whole path once fixes that.

### Before You Start

- `git status` shows `workspace/hello.md`, `workspace/profile.md`, and
  `workspace/notes/` under *Untracked files*.
- Your name and email are configured (see Concepts).

### Instructions

1. Look at the starting state. Read-only:

   ```text
   git status
   ```

   `hello.md` is under *Untracked files*.

2. Stage it. This changes the staging area only:

   ```text
   git add workspace/hello.md
   git status
   ```

   *Expected:* `hello.md` moved to *Changes to be committed* as
   `new file:`. The other two are still untracked.

3. See what you are about to commit. Read-only:

   ```text
   git diff --staged
   ```

   *Expected:* the whole file shown with `+` in front of every line, because
   compared with history (where it does not exist yet) every line is new.

4. Commit it. This creates a permanent snapshot:

   ```text
   git commit -m "Add hello file"
   ```

   *Expected output (roughly):*

   ```text
   [main a1b2c3d] Add hello file
    1 file changed, 3 insertions(+)
    create mode 100644 workspace/hello.md
   ```

   The letters and numbers after `main` are the commit's short hash; yours
   will differ.

5. Look again:

   ```text
   git status
   git log --oneline
   ```

   *Expected:* `hello.md` no longer appears in status at all (it is
   tracked and unchanged). `git log --oneline` shows your commit at the
   top, above the course's own initial commit.

### Check Your Work

```text
python tools/check.py 03
```

The `03.commit.hello` check should pass; the others belong to 3.2.

### What You Should Notice

- After committing, a file "disappears" from `git status`. That is good
  news: it matches the last snapshot.
- `git diff --staged` before `git commit` is how you avoid committing
  something you did not mean to.
- The commit message is part of the snapshot. It is the only human-readable
  clue about what the commit is for.

### Common Mistakes

- `git commit` without `-m`. Git opens an editor for the message. If it is
  an unfamiliar editor and you are stuck: press `Esc`, type `:q!`, press
  Enter. That cancels; nothing is committed. Then try again with `-m`.
- `git add hello.md` from the top folder: "did not match any files". The
  path is `workspace/hello.md`.
- Committing with the wrong name because config was skipped. Not harmful;
  set it and carry on.

### Recovery

- Staged something you did not mean to? `git restore --staged <file>` moves
  it back out of the staging area (Lesson 04 covers this properly). The
  file's contents are untouched.
- Committed with a typo in the message? Leave it. History with a typo is
  fine; rewriting history is a later topic.

### Reflection

- After `git add`, you edit the file again. Is the new edit in the staging
  area? (Try it: edit, `git status`, see both sections appear.)

---

## Exercise 3.2 — Commit the rest, one thing per commit

### Goal

Commit `workspace/profile.md` and the `workspace/notes/` folder as two
separate commits, then read the history.

### Why This Matters

A commit should be one logical change so that history reads like a list of
things that happened. "Add profile" and "Add notes index" are two things.

### Before You Start

Exercise 3.1 done: `git log --oneline` shows "Add hello file".

### Instructions

1. Stage only the profile:

   ```text
   git add workspace/profile.md
   git status
   ```

   Confirm: profile under *to be committed*; notes still untracked.

2. Commit it with a message that says what it adds:

   ```text
   git commit -m "Add profile page"
   ```

3. Stage the whole notes folder (adding a folder adds every file in it):

   ```text
   git add workspace/notes
   git status
   ```

4. Commit:

   ```text
   git commit -m "Add notes index and git command reference"
   ```

5. Read the history:

   ```text
   git log --oneline
   ```

   *Expected:* your three commits, newest first, then the course's initial
   commit.

6. Look at one commit in detail (read-only; `-1` means "just the latest",
   `-p` means "show the diff"):

   ```text
   git log -1 -p
   ```

   If the output is longer than the screen, press the space bar to page
   and `q` to quit.

### Check Your Work

```text
python tools/check.py 03
```

### What You Should Notice

- `git status` now says `nothing to commit, working tree clean`. Every file
  matches the last snapshot. This is the state you want to see at the end of
  a lesson.
- History is a list of *why*, not just *what*. Compare your three messages
  with what `git log -p` shows.

### Common Mistakes

- `git add .` stages everything, including things you did not intend.
  It is fine when you have checked `git status` first and everything listed
  belongs together. Prefer naming files while learning.
- Trying to commit with nothing staged: "nothing to commit". Stage first.

### Recovery

- If you accidentally staged both files together, `git restore --staged
  workspace/notes` unstages the folder (Lesson 04 explains this command);
  then commit the profile alone.
- If you committed both together, that is acceptable. Note it in your
  reflection and move on; splitting commits is an advanced topic.

### Reflection

- If you delete `workspace/hello.md` now, is it gone? Where else does it
  exist? (Do not delete it yet; Lesson 04 does this deliberately.)
