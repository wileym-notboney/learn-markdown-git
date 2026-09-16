# Lesson 00 — Orientation

## Objectives

By the end of this lesson you can:

- open a terminal and move it into this course's folder
- explain in one sentence each what Markdown, Git, and GitHub are
- tell a folder apart from a repository
- create a file from the terminal
- run the checker and read what it says
- know where to look when something goes wrong

Nothing in this lesson can break anything.

## How to read the lessons

Each lesson has a **Concepts** part (read it) and one or more **Exercises**
(do them). Exercises always have the same sections, so you know where to
look:

| Section | Purpose |
|---------|---------|
| Goal | what you are trying to do |
| Why This Matters | where this shows up in real work |
| Before You Start | what your repository should look like first |
| Instructions | the steps |
| Check Your Work | how to confirm you did it |
| What You Should Notice | the idea the exercise is really about |
| Common Mistakes | things that go wrong for most people |
| Recovery | how to get back to a good state |
| Reflection | one or two questions to think about |

Formatting conventions used everywhere:

- Commands you type appear in a block like this, one per line, without a
  `$` or `>` prompt in front:

  ```text
  git status
  ```

- Example output appears in a block labelled *Expected output*. Yours may
  differ slightly (dates, names); the shape is what matters.
- File names look like `workspace/hello.md`. Folders end in `/`.
- Markdown syntax you should type into a file is shown in a `markdown` block.

Early lessons give exact commands. Later lessons give goals and hints. That
is deliberate: the aim is for you to stop needing this course.

## Concepts

### Plain text

A plain-text file contains only characters: letters, numbers, punctuation,
line breaks. No fonts, no colours, no hidden formatting. `.txt` files are
plain text. So are `.md` files, and so is program source code.

Plain text matters because tools can read it, compare it, and search it
without needing the program that made it. Word documents are not plain text.

### Markdown

Markdown is plain text with a few symbols that mean "make this a heading",
"make this bold", "this is a list". A file like:

```markdown
# Shopping

- milk
- **eggs**
```

can be *rendered* into a heading, a list, and a bold word. It stays readable
even when it is not rendered. That is the point: write once, read anywhere.
GitHub, note apps, chat tools, and documentation sites all speak Markdown.
Lessons 01 and 02 teach it.

### Folders, files, paths

A **folder** (also called a **directory** — same thing) contains files and
other folders. A **path** is the address of a file:
`lessons/00-orientation/README.md` means "the file `README.md`, inside the
folder `00-orientation`, inside the folder `lessons`".

Paths that start from where you are now are *relative*. Paths that start
from the root of the disk (`/Users/...` or `C:\Users\...`) are *absolute*.
This course uses relative paths from the top of the course folder.

### The terminal

A terminal is a program where you type a command, press Enter, and read
what comes back. It always has a **working directory**: the folder it is
"in". Commands act on files relative to that folder, which is why the first
thing to check when a command fails is *where am I?*

| Task | macOS / Linux | Windows PowerShell |
|------|---------------|--------------------|
| Where am I? | `pwd` | `pwd` |
| List files here | `ls` | `ls` (or `dir`) |
| Move into a folder | `cd foldername` | `cd foldername` |
| Move up one folder | `cd ..` | `cd ..` |
| Show a file's contents | `cat file.md` | `type file.md` |

Git commands are identical on every platform. When a non-Git command differs,
lessons show both.

### Git

Git is a program that takes snapshots of a folder. Each snapshot is called a
**commit**. You decide when to take one and you write a short note saying
what changed. Later you can see every snapshot, compare any two, go back to
one, or work on two versions side by side.

Git solves the problem of `essay-final-v2-REAL-final.docx`. Lesson 03 builds
the mental model properly. For now: Git remembers versions so you do not
have to.

### Repository vs folder

A **repository** is a folder that Git is watching. What makes it a repository
is a hidden subfolder named `.git` where Git keeps all the snapshots. Delete
`.git` and you have an ordinary folder again with only the latest files.

This course folder is already a repository. You will not need to create one
until Lesson 07.

### GitHub

GitHub is a website that stores copies of Git repositories and adds things
like discussion, review, and web-based editing. Git works without GitHub.
GitHub is optional in this course; Lesson 07 covers it and provides a way to
practise without an account.

### How exercises are checked

`tools/check.py` is a small Python program. It reads your files and your Git
history and reports what it finds. It never edits anything. It also records
what you have passed in `.learning/progress.json` so it knows which lesson
you are on. That file stays on your computer.

### Getting unstuck

1. `git status` — tells you what Git thinks is going on. Safe to run any time.
2. The lesson's **Common Mistakes** and **Recovery** sections.
3. `python tools/check.py` — says what it expected and what to look at.
4. An AI assistant that has read `AI_TUTOR.md`, or a person. When asking for
   help, paste the exact command you ran and the exact output.

---

## Exercise 0.1 — Find the folder, make a file

### Goal

Move your terminal into the course folder, confirm Git sees it, and create
your first file using the terminal.

### Why This Matters

Every command in this course assumes your terminal is inside the course
folder. Most "it doesn't work" problems in the first week are "wrong folder".

### Before You Start

- Git and Python are installed. Check with `git --version` and
  `python --version` (or `python3 --version`). Each should print a version
  number. If not, install them and come back.
- You know where you saved this course folder (for example in your
  Documents folder).

### Instructions

1. Open a terminal.

2. Move into the course folder. Type `cd ` (with a space) and then the path
   to the folder. Tip: on most systems you can type `cd `, then drag the
   folder from your file browser into the terminal window to paste its path.
   Press Enter.

3. Confirm where you are:

   ```text
   pwd
   ```

   *Expected output:* a path ending in the course folder's name. This
   command only prints; it changes nothing.

4. Confirm Git sees this folder as a repository:

   ```text
   git status
   ```

   *Expected output (roughly):*

   ```text
   On branch main
   nothing to commit, working tree clean
   ```

   If you see `fatal: not a git repository`, you are in the wrong folder.
   Use `cd` to fix it. This command only reads; it changes nothing.

5. Look at what is here:

   ```text
   ls
   ```

   You should see `README.md`, `lessons`, `workspace`, `tools`, and more.

6. Create a file named `hello.md` inside the `workspace` folder. Open your
   editor, create a new file, type exactly this, and save it as
   `workspace/hello.md`:

   ```markdown
   # Hello

   This is my first Markdown file.
   ```

   Using VS Code? From the terminal, `code workspace/hello.md` opens (and
   creates) it directly.

7. Confirm the file exists and has what you typed:

   ```text
   cat workspace/hello.md
   ```

   (Windows PowerShell: `type workspace/hello.md`.)

8. Ask Git what it thinks now:

   ```text
   git status
   ```

   *Expected output:* the phrase `Untracked files:` followed by
   `workspace/hello.md`. Git noticed a new file it has never seen. That is
   all it does for now; you have not asked it to remember the file. Lesson 03
   covers that.

### Check Your Work

```text
python tools/check.py 00
```

Use `python3` if `python` is not found. It will say the file was found and
has a heading, or tell you which part is missing.

### What You Should Notice

- `git status` is safe. Run it whenever you are unsure. It reports; it does
  not act.
- Git notices new files immediately but does nothing with them until told.
- The checker reads your real files. It is not looking for the "right
  answer" in some hidden place; it is looking at `workspace/hello.md`.

### Common Mistakes

- Saving the file in the wrong folder (often the course's top folder, or
  your home folder). `ls workspace` should list `hello.md`.
- Saving as `hello.md.txt`. Some editors add `.txt`. Check the exact name.
- Typing `#Hello` without a space. Markdown needs `# Hello`.

### Recovery

Nothing here can go wrong in a way that matters. If the file is in the wrong
place, move it or create it again in `workspace/`. If your terminal is in the
wrong folder, `cd` to the right one. If you closed the terminal, open a new
one and `cd` back; nothing is lost.

### Reflection

- What is the difference between what `pwd` tells you and what `ls` tells you?
- Git said the file was "untracked". What do you think "tracked" will mean?

---

## Exercise 0.2 — Read the checker

### Goal

Understand what the checker's output means before you rely on it.

### Why This Matters

Automated feedback is only useful if you can read it. You will run this
tool after every lesson.

### Before You Start

Exercise 0.1 passed.

### Instructions

1. Run the checker for a lesson you have not done:

   ```text
   python tools/check.py 01
   ```

   It changes nothing except its own progress file.

2. Read the output. Each line has a status, an identifier like
   `01.profile.exists`, and a sentence. Failing lines are followed by
   **Look** (a command to run to see the state yourself) and **Try** (what
   to do about it).

3. Run it without a lesson number:

   ```text
   python tools/check.py
   ```

   It checks the lesson it believes you are on — the earliest one not yet
   fully passed. Right now that is lesson 01.

### Check Your Work

Nothing to pass. If both commands ran and printed lines, you are done.

### What You Should Notice

The checker tells you *what to inspect*, not just pass/fail. Its "Look"
commands are usually `ls`, `cat`, `git status`, `git diff`, or `git log` —
the same tools you will use to answer questions yourself.

### Common Mistakes

- `python: command not found` — try `python3`. On Windows, the Microsoft
  Store may open; install Python from python.org instead and re-open the
  terminal.
- Running from inside `lessons/` or `workspace/`. The checker expects the
  course's top folder. `cd ..` until `ls` shows `tools`.

### Recovery

The checker cannot damage anything. If it prints a Python error, note the
last line and ask for help; that is a course bug, not your mistake.

### Reflection

- If the checker said a file was missing but you can see it in your editor,
  what would you check first?
