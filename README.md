# Learn Markdown and Git by Editing This Repository

This repository is a course. You learn Markdown by editing Markdown files
inside it, and you learn Git by saving those edits with Git. By the end,
your Git history is a record of everything you learned.

**New here? Open [START_HERE.md](START_HERE.md).**

## Who this is for

People with little or no experience with terminals, Git, GitHub, or
Markdown. Nothing is assumed beyond being able to install software and
open a folder.

## What you will learn

- Write Markdown: headings, lists, links, images, code, tables, checklists.
- Understand what Git is actually doing when you commit, branch, and merge.
- Use `git status`, `git diff`, and `git log` to answer "what is going on?"
  instead of memorizing workflows.
- Recover from ordinary mistakes without fear.
- Work with a remote repository (GitHub or a local stand-in).
- Finish a small, realistic documentation project on your own.

## Prerequisites

- Git installed (`git --version` prints a version).
- Python 3.8 or newer (`python --version` or `python3 --version`).
- A plain-text editor. [VS Code](https://code.visualstudio.com/) is a good
  free choice and previews Markdown.
- A terminal: Terminal on macOS, any terminal on Linux, PowerShell or
  Git Bash on Windows.

Lesson 00 walks through checking each of these.

## How long it takes

Ten lessons. Most people spend somewhere between a few evenings and a couple
of weeks, depending on how much they practise. There is no timer; the
curriculum is finished when you can do the capstone.

## How the learning system works

| Piece | What it does |
|-------|--------------|
| `lessons/` | One folder per lesson. Read the `README.md` inside. **Do not edit these.** |
| `workspace/` | Your files. Every exercise creates or edits something here. |
| `python tools/check.py` | Checks your work and explains what is missing and how to look into it. |
| `.learning/progress.json` | Local, private record of which lessons you have started, passed, and struggled with. No personal data. |
| `reinforcement/` | Short optional drills the checker recommends when you keep hitting the same problem. |
| `tools/review.py` | Reads your progress data and reports where the *curriculum* (not you) seems to be causing friction. |

## Checking your work

From the repository's top folder:

```text
python tools/check.py        # checks the lesson you are currently on
python tools/check.py 03     # checks lesson 03
python tools/check.py all    # checks everything so far
```

On some systems the command is `python3` instead of `python`.

The checker never edits your files. It reads them, reads your Git history,
and tells you what it found.

## When you are stuck

1. Run `git status`. Read it slowly. It usually tells you what is happening.
2. Read the lesson's **Common Mistakes** and **Recovery** sections.
3. Run the checker. It says what it expected and what to look at.
4. Ask an AI assistant. If you use Claude Code, it reads
   [AI_TUTOR.md](AI_TUTOR.md) and will help without doing the exercise for you.

## How the curriculum reviews itself

The course keeps notes on its own weaknesses. `tools/review.py` turns
progress data into findings; [CURRICULUM_REVIEW.md](CURRICULUM_REVIEW.md)
holds the rubric and process; [CURRICULUM_CHANGELOG.md](CURRICULUM_CHANGELOG.md)
records every change made to a lesson and why. See
[CONTRIBUTING.md](CONTRIBUTING.md) if you want to improve a lesson.

## Layout

```text
START_HERE.md            the first thing to read
GLOSSARY.md              plain-language definitions of every term used
lessons/00-orientation   ... through lessons/09-capstone
workspace/               your files (created as you go)
reinforcement/           short optional drills
examples/                reference documents and a cheat sheet
tools/                   check.py, validate_curriculum.py, review.py
.learning/               your local progress (not committed)
```
