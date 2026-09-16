# Start Here

Welcome. Follow these steps in order.

## 1. Find the folder

This course is a folder on your computer. It contains this file. In your
terminal, move into that folder. If you are not sure how, Lesson 00 shows
you. Everything in this course assumes your terminal is **inside this
folder** unless a lesson says otherwise.

To confirm, run:

```text
git status
```

If you see a line beginning `On branch main`, you are in the right place.
If you see `fatal: not a git repository`, you are in the wrong folder.

## 2. Open Lesson 00

Read [lessons/00-orientation/README.md](lessons/00-orientation/README.md).
It explains what a terminal is, what this repository is, how the lessons
are structured, and how to check your work.

## 3. Work through the lessons in order

| Lesson | Topic |
|--------|-------|
| [00](lessons/00-orientation/README.md) | Orientation: terminal, repository, how the course works |
| [01](lessons/01-markdown-basics/README.md) | Markdown fundamentals |
| [02](lessons/02-practical-markdown/README.md) | Practical Markdown: tables, checklists, linking files |
| [03](lessons/03-git-foundations/README.md) | Git mental model and first commits |
| [04](lessons/04-everyday-git/README.md) | Everyday Git: messages, staging, restoring |
| [05](lessons/05-branches/README.md) | Branches |
| [06](lessons/06-merge-conflicts/README.md) | Merge conflicts |
| [07](lessons/07-remotes/README.md) | Remotes and GitHub |
| [08](lessons/08-real-workflow/README.md) | A real workflow |
| [09](lessons/09-capstone/README.md) | Capstone |

Each lesson ends with `python tools/check.py`. Green means move on.

## 4. Keep these three commands close

```text
git status    what is going on right now?
git diff      what exactly did I change?
git log       what happened before?
```

You will run these more than any other command. They never change anything.

## 5. If something goes wrong

Nothing in this course can damage your computer. Git makes it very hard to
lose committed work. Every lesson has a **Recovery** section. Lesson 00 has
a general one.
