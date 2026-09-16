# Lesson 02 — Practical Markdown

## Objectives

By the end of this lesson you can:

- write a table and a checklist
- organise notes across several files
- link between files in the same repository with relative paths
- structure a README so a stranger can use it

You will build a small notes folder, `workspace/notes/`, that you will keep
adding to for the rest of the course.

## Concepts

### Tables

```markdown
| Command      | Changes anything? |
|--------------|-------------------|
| `git status` | no                |
| `git add`    | yes (staging)     |
```

The second line, with dashes, is required; it separates the header row from
the body. Columns do not have to line up in the raw text, but lining them up
helps humans. Add colons to align: `|:---|` left, `|:---:|` centre,
`|---:|` right.

Tables are for data with consistent columns. If cells need paragraphs or
lists, use headings instead.

### Checklists

```markdown
- [ ] not done
- [x] done
```

A space or an `x` between the brackets. On GitHub these become clickable
checkboxes. In a notes file they are a lightweight to-do list.

### Organising documentation

One long file is hard to navigate; one file per topic with an index is
easier. A common shape:

```text
notes/
  README.md          index: what is here and where to start
  git-commands.md    one topic
  markdown-tips.md   another topic
```

`README.md` is special: GitHub and many tools display it automatically when
you open a folder. Put the map in it.

### Relative links between files

To link from one file to another in the same repository, use a path
relative to the *file you are writing in*, not the folder your terminal is
in.

```markdown
[Git commands](git-commands.md)         same folder
[my profile](../profile.md)            one folder up
[cheat sheet](../../examples/markdown-cheatsheet.md)   two up, then down
```

`..` means "the parent folder". These links work on GitHub, in VS Code
preview, and in most Markdown tools, and they keep working if the whole
repository is moved or copied. Full URLs to a GitHub page break the moment
the repository moves.

You can also link to a heading inside a file: `[Tables](#tables)` links to
a heading named "Tables" in the same file. Lowercase, spaces become dashes.

### What a good README has

1. A title and one sentence saying what this is.
2. Who it is for.
3. How to start (the first three things to do).
4. Where things are.
5. Where to get help.

See [examples/good-readme.md](../../examples/good-readme.md) for a short
model.

### Writing readable technical notes

- One idea per paragraph. Short paragraphs.
- Put the command in a code block and the *why* in the sentence before it.
- Say what the reader should see afterwards.
- Prefer a table when comparing; prefer a list when ordering.
- Use inline code for anything typed exactly: commands, file names, keys.

---

## Exercise 2.1 — A notes index with a table and a checklist

### Goal

Create `workspace/notes/README.md` containing a table of Git commands you
have met and a checklist of lessons.

### Why This Matters

You will spend the rest of the course adding to these notes. Writing your
own reference is the fastest way to stop needing someone else's.

### Before You Start

Lesson 01 passed. The folder `workspace/notes/` exists (it is empty apart
from a placeholder file; that is fine).

### Instructions

1. Create `workspace/notes/README.md`:

   ```markdown
   # My notes

   Notes I am keeping while learning Markdown and Git.

   ## Git commands so far

   | Command      | What it does                        | Changes anything? |
   |--------------|-------------------------------------|-------------------|
   | `git status` | shows what Git thinks is going on   | no                |
   | `pwd`        | shows the folder my terminal is in  | no                |

   ## Lesson progress

   - [x] 00 Orientation
   - [x] 01 Markdown basics
   - [ ] 02 Practical Markdown
   - [ ] 03 Git foundations
   ```

2. Add at least one more row to the table (`ls` or `cat` are good
   candidates) and at least one more lesson to the checklist.

3. Preview it. The table should render as a grid; the checklist should show
   boxes.

### Check Your Work

```text
python tools/check.py 02
```

### What You Should Notice

- The dashes row is what makes it a table. Without it you get a paragraph
  full of pipes.
- A checklist is just a list whose items start with `[ ]` or `[x]`.

### Common Mistakes

- Missing the `|---|---|` separator row.
- A different number of cells in one row. Renderers cope, but the result
  looks wrong.
- `[]` with nothing inside: needs a space, `[ ]`.

### Recovery

The file is untracked; edit freely.

### Reflection

- Which of the commands in your table would you be nervous to run on
  someone else's computer? Why or why not?

---

## Exercise 2.2 — Link between files

### Goal

Create a second notes file and link it from the index; link from the index
back up to your profile.

### Why This Matters

Documentation that links to itself is navigable. Relative links are how
every real repository does it.

### Before You Start

Exercise 2.1 done.

### Instructions

1. Create `workspace/notes/git-commands.md`. Move the Git commands table
   from `README.md` into it, under a `# Git commands` heading. Leave a
   one-line description in `README.md` where the table was.

2. In `workspace/notes/README.md`, add a section:

   ```markdown
   ## Files

   - [Git commands](git-commands.md)
   - [My profile](../profile.md)
   ```

3. In `workspace/notes/git-commands.md`, add a line at the bottom linking
   back: `[Back to notes](README.md)`.

4. Preview `README.md` and click the links. Each should open the right
   file. If a link does nothing or opens an error, the path is wrong.

### Check Your Work

```text
python tools/check.py 02
```

The checker follows every relative link in `workspace/notes/` and reports
any that point at a file that does not exist.

### What You Should Notice

- `../profile.md` works from `notes/README.md` because `..` steps out of
  `notes/`. The same link written in `workspace/profile.md` would be wrong.
- Links are checked relative to the file, never relative to your terminal.

### Common Mistakes

- Linking to `workspace/profile.md` from inside `workspace/notes/`. That
  path would look for `workspace/notes/workspace/profile.md`.
- Case: `Profile.md` and `profile.md` are different files on Linux and on
  GitHub, even if your Mac or Windows machine forgives it.
- Spaces in file names. Avoid them; use dashes.

### Recovery

Both files are untracked. Fix paths and re-run the checker.

### Reflection

- Why would a relative link survive moving the repository when an absolute
  URL would not?

---

## Optional Challenge 2.3 — Anchor links

### Goal

Add a small table of contents to `workspace/notes/README.md` using
heading anchors like `[Files](#files)`.

### Why This Matters

Long documents need in-page navigation.

### Before You Start

Exercise 2.2 done. This is optional; the checker does not require it.

### Instructions

Add a `## Contents` section near the top with a list of links to each
heading in the file. Anchors are the heading text in lowercase with spaces
replaced by dashes and punctuation removed.

### Check Your Work

Preview and click. That is the only check.

### What You Should Notice

Anchors are generated from heading text, so renaming a heading breaks links
to it.

### Common Mistakes

Capital letters or spaces in the anchor.

### Recovery

Untracked file; edit freely.

### Reflection

- What would you have to do if you renamed a heading that other files link to?
