# Lesson 07 — Remotes and GitHub

## Objectives

By the end of this lesson you can:

- explain what a remote is and what `origin` means
- push your commits to a remote and pull commits from it
- explain the difference between `fetch` and `pull`
- describe what GitHub adds on top of Git, and what a pull request is

**You do not need a GitHub account for the core exercise.** You will use a
second folder on your own computer as the remote. Everything works the same
way; only the address differs. A GitHub version is provided as an optional
exercise, clearly marked.

## Concepts

### Local and remote

Everything so far lived in one folder: your **local** repository. A
**remote** is another copy of the same repository somewhere else — another
folder, another computer, a server, GitHub. Git can send commits to it
(**push**) and bring commits from it (**fetch**, **pull**).

Remotes exist for backup and for collaboration. A remote on GitHub is also
a remote in the plain Git sense; nothing about GitHub is required to
understand this lesson.

### `origin`

A remote has an address (a folder path or a URL) and a nickname. The
conventional nickname for the main remote is `origin`. It is only a name;
`git remote -v` shows what it points to.

### Bare repositories

A remote that nobody edits directly does not need a working tree — just
the `.git` data. That is a **bare** repository. GitHub stores your
repository this way. You will create one in a folder next to this course
to act as your practice server.

### The commands

| Command | Does | Changes anything? |
|---------|------|-------------------|
| `git remote -v` | lists remotes | no |
| `git remote add origin <address>` | registers a remote | config only |
| `git push -u origin main` | sends `main`'s commits to origin; `-u` remembers the pairing | remote only |
| `git push` | sends new commits to the remembered remote | remote only |
| `git fetch` | downloads new commits from the remote without touching your files | local metadata only |
| `git pull` | `fetch` then merge the remote's branch into yours | your branch and files |
| `git clone <address>` | makes a new local copy of a remote | creates a folder |

`git pull` can produce a merge conflict, exactly like Lesson 06, when both
sides changed the same lines. Resolution is identical.

### Remote branches

After a fetch, Git keeps a read-only bookmark called `origin/main`: "where
`main` was on the remote the last time I looked". `git log --oneline
--all` shows it next to your own `main`. If `origin/main` is ahead, you
need to pull; if your `main` is ahead, you need to push. `git status`
tells you which ("Your branch is ahead of 'origin/main' by 1 commit").

### GitHub, and pull requests

GitHub hosts bare repositories and adds a website around them: browsing
files, rendering Markdown, issues, and **pull requests**. A pull request
(PR) is "please merge my branch into yours", with the diff shown, a place
to discuss, and a button to merge. It is a GitHub feature, not a Git
command; under the hood it is a branch and a merge. The workflow: push a
branch → open a PR → someone reviews → merge on GitHub → `git pull` locally.

---

## Exercise 7.1 — A remote on your own machine

### Goal

Create a bare repository next to the course folder, register it as
`origin`, push, then clone it into a third folder, commit there, push, and
pull the commit back here.

### Why This Matters

Push, pull, and clone are the whole remote vocabulary. Doing it with two
folders on one machine shows there is nothing magic about a server.

### Before You Start

Lesson 06 passed; on `main`; clean working tree. Your terminal is in the
course folder. Note the *parent* folder's name (`cd ..` then `pwd` shows
it; `cd` back into the course folder afterwards).

Run `git remote -v`. If it already lists `origin` — it will if you got this
course by cloning it — rename that one out of the way so the exercise can
use the conventional name:

```text
git remote rename origin course-source
```

This changes a nickname only; nothing is downloaded or deleted.

### Instructions

1. Create the bare repository in the parent folder. The `..` means "one
   folder up". Forward slashes work on Windows too. `-b main` tells the new
   repository that its default branch is called `main`, matching yours.

   ```text
   git init --bare -b main ../learn-git-remote.git
   ```

   *Expected:* `Initialized empty Git repository in .../learn-git-remote.git/`.
   A new folder appeared next to the course folder. Do not open it in an
   editor; it has no normal files.

2. Register it as `origin` and check:

   ```text
   git remote add origin ../learn-git-remote.git
   git remote -v
   ```

3. Push `main` and remember the pairing:

   ```text
   git push -u origin main
   ```

   *Expected:* a few lines of progress, then
   `branch 'main' set up to track 'origin/main'`.

4. `git status` — first line should now say your branch is up to date with
   `origin/main`. `git log --oneline -1` shows `origin/main` next to `HEAD`.

5. Clone the remote into a third folder, pretending to be a second
   computer:

   ```text
   git clone ../learn-git-remote.git ../learn-git-clone
   ```

6. Move into the clone, make a commit, push it, come back:

   ```text
   cd ../learn-git-clone
   ```

   Add one line to `workspace/reading-list.md`, commit it, then
   `git push`. Then return: `cd` back to the course folder (the one whose
   `lessons/` you have been reading). Confirm with `pwd`.

7. Back in the course folder, ask the remote what is new without changing
   any files:

   ```text
   git fetch
   git status
   ```

   *Expected:* "Your branch is behind 'origin/main' by 1 commit".
   `cat workspace/reading-list.md` does not have the new line yet.

8. Bring it in:

   ```text
   git pull
   ```

   *Expected:* `Fast-forward` and the file now has the line.

### Check Your Work

```text
python tools/check.py 07
```

The checker confirms `origin` exists, your `main` contains everything on
`origin/main`, and the remote holds a second `reading-list.md` commit that
your `main` also has. It cannot tell which folder made that commit; confirm
that yourself with `git log --format='%h %an %s' -- workspace/reading-list.md`
and the clone's `git log`.

### What You Should Notice

- `git fetch` changed what `git status` said but not a single file.
  `git pull` changed files. That is the difference.
- The clone had *everything*: all commits, the whole history. A clone is a
  full copy, not a download of the latest files.
- Push and pull are symmetric. The "server" is just a repository that
  nobody edits directly.

### Common Mistakes

- Running the clone or push from inside the wrong folder. `pwd` first.
- `git push` before `git remote add`: "no configured push destination".
- Forgetting `-u` the first time; later `git push` asks for a destination.
  Just run `git push -u origin main` once.
- Windows: if `../learn-git-remote.git` fails, try the full path.
- Clone prints `warning: remote HEAD refers to nonexistent ref` and the
  clone folder is empty: the bare repository was created without `-b main`.
  Delete the clone folder and run `git clone -b main ../learn-git-remote.git
  ../learn-git-clone` instead.

### Recovery

- Wrong remote address? `git remote remove origin` and add it again.
- Messed up the clone folder? Delete `../learn-git-clone` and clone again;
  it is a copy.
- Pull produced a conflict? Lesson 06 applies: resolve, `git add`,
  `git commit`; or `git merge --abort`.

### Reflection

- Which is the "real" repository: this folder, the bare one, or the clone?
- What would happen if you edited the same line in the clone and here
  before pulling?

---

## Optional Exercise 7.2 — The same thing on GitHub (requires an account)

### Goal

Push this repository to GitHub, make a change on a branch, and merge it via
a pull request.

### Why This Matters

GitHub is where most shared repositories live. Seeing your commits rendered
on a website connects the abstract history to something tangible.

### Before You Start

A GitHub account, and SSH or HTTPS access set up per GitHub's own
documentation (this course does not cover authentication; it changes too
often). Exercise 7.1 done. **Skip this exercise freely; nothing later
depends on it.**

### Instructions

1. On GitHub, create a new **empty** repository (no README, no licence).
   Copy the address it shows.

2. Replace the local remote with the GitHub one:

   ```text
   git remote set-url origin <the address>
   git push -u origin main
   ```

3. Open the repository page. Browse to `workspace/profile.md`; it renders.
   Click a commit in the history view; the diff is the same one `git log
   -p` shows.

4. Create a branch, change something in `workspace/notes/`, commit, then
   `git push -u origin <branch>`. GitHub will show a banner offering to open
   a pull request. Open it, read the diff, merge it with the button.

5. Locally: `git switch main`, `git pull`. Your merge arrived.
   `git branch -d <branch>`.

### Check Your Work

`git remote -v` shows GitHub; `git log --oneline -3` shows the merge.
The checker does not require this exercise.

### What You Should Notice

The PR merge is a merge commit Git made on GitHub's copy. `git pull`
treated it like any other commit.

### Common Mistakes

Creating the GitHub repository with a README: the first push is refused
because the histories differ. Create it empty.

### Recovery

If push is refused for authentication reasons, that is GitHub setup, not
Git: follow GitHub's docs, or `git remote set-url origin
../learn-git-remote.git` to go back to the local remote.

### Reflection

- What did GitHub do that Git alone did not?
