# Lesson 09 — Capstone

## Objectives

Demonstrate, without step-by-step instructions, that you can navigate a
repository, write Markdown, inspect state, stage, review diffs, commit with
good messages, branch, merge, recover from a mistake, and read history.

This lesson lists outcomes and how they are verified. How you get there is
up to you.

## Concepts

Nothing new. If you find yourself needing something not covered, check
whether it is really needed; the capstone is designed to be completed with
Lessons 00–08 only.

One reminder on recovery, since it is required below. Safe tools you have:

| Situation | Tool |
|-----------|------|
| Uncommitted edit you regret | `git diff <file>`, then `git restore <file>` |
| Staged the wrong thing | `git restore --staged <file>` |
| Wrong branch | `git switch` |
| Merge went wrong, not yet committed | `git merge --abort` |
| Committed something wrong | `git revert <hash>` — makes a *new* commit that undoes it; history stays intact |

`git revert` is the one command here you have not used. It is safe: it
adds a commit rather than removing one. `git revert HEAD` undoes the latest
commit that way.

---

## Exercise 9.1 — Capstone

### Goal

Produce `workspace/capstone/`, a documentation set for a project of your
choosing, built on a branch and merged, with one deliberate mistake made
and recovered.

### Why This Matters

This is the course's definition of done: you can do this on your own.

### Before You Start

Lesson 08 passed. On `main`, clean tree.

### Instructions

Outcomes to achieve. Verify each yourself before running the checker.

**Markdown**

- `workspace/capstone/README.md` uses: a heading hierarchy (`#`, `##`,
  `###`), bold, italic, an ordered list, an unordered list, a link, a fenced
  code block with a language, a table, and a checklist.
- At least one other Markdown file in `workspace/capstone/`, linked from
  the README with a relative link that resolves.

**Git**

- All capstone work happens on a branch (any sensible name) and is merged
  into `main` with a merge commit (`--no-ff`). The branch is deleted after.
- At least four commits touch `workspace/capstone/`. Each has a subject
  that says what it does.
- At some point you make a mistake on purpose and recover from it using one
  of the tools in the table above. Then write
  `workspace/capstone/RECOVERY.md` describing: what you did, what
  `git status` or `git diff` showed, which command you used to recover, and
  why that one. Mention the command in inline code. Commit that file.

**History**

- `git log --oneline --graph -12` shows the branch leaving and rejoining
  `main`. You can point at the merge commit and explain it.

### Check Your Work

```text
python tools/check.py 09
python tools/check.py all
```

Everything green means the course is complete.

### What You Should Notice

- How many commands did you have to look up? Compare with Lesson 05.
- Which of `status`, `diff`, `log` did you reach for first when unsure?
  That instinct is the real outcome of the course.

### Common Mistakes

- Doing the recovery step last and faking it. The point is to make the
  mistake *in the middle* of real work and notice that it was not scary.
- A README that has all the required syntax and says nothing. Write about
  something.

### Recovery

You know how. `git status` first. If genuinely stuck, `AI_TUTOR.md`
describes how an assistant should help without doing it for you.

### Reflection

- What would you tell someone starting Lesson 00 about what Git is *for*?
- What is one thing you would change about this course? Consider opening
  the file `CONTRIBUTING.md`.
