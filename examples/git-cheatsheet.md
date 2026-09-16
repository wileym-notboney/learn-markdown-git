# Git Cheat Sheet

Commands used in this course, grouped by what they do to your repository.

## Report only (always safe)

| Command | Shows |
|---------|-------|
| `git status` | where every changed file is: staged, modified, untracked |
| `git diff` | unstaged changes, line by line |
| `git diff --staged` | what the next commit will contain |
| `git log --oneline` | history, one line per commit |
| `git log --oneline --graph --all` | history with branch shape |
| `git log -p -1` | last commit with its diff |
| `git log -- <file>` | commits that touched a file |
| `git show <hash>` | one commit with its diff |
| `git branch` | branches; `*` marks current |
| `git branch --show-current` | current branch name |
| `git remote -v` | remotes and their addresses |
| `git show <branch>:<file>` | a file as it is on another branch |

## Move changes forward (recoverable)

| Command | Does |
|---------|------|
| `git add <file>` | stage a file |
| `git add -p <file>` | stage parts of a file interactively |
| `git commit -m "msg"` | save staged changes as a commit |
| `git switch <branch>` | move to a branch |
| `git switch -c <name>` | create a branch and move to it |
| `git merge <branch>` | bring a branch's commits into the current one |
| `git merge --no-ff <branch>` | same, always creating a merge commit |
| `git branch -d <name>` | delete a merged branch (refuses if unmerged) |
| `git revert <hash>` | new commit that undoes an old one |
| `git push` / `git pull` / `git fetch` | send / bring and merge / bring only |

## Discard (read the diff first)

| Command | Loses |
|---------|-------|
| `git restore <file>` | uncommitted edits to that file |
| `git restore --staged <file>` | nothing — only unstages |
| `git merge --abort` | nothing — returns to before the merge |

## Not used in this course

`git checkout`, `git reset --hard`, `git clean`, `git rebase`,
`git push --force`. Each has a use; each can discard work. Learn them when
you need them, one at a time, with `git status` before and after.
