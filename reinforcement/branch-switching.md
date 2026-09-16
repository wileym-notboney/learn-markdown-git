# Drill: Where am I?

Five minutes. Ends with one throwaway branch deleted.

1. `git branch --show-current`. Say the name out loud.
2. `git switch -c drill-branch`. Run `git branch`. Which has the `*`?
3. `git log --oneline -1`. Note the hash.
4. Add a line to `workspace/hello.md`. Do **not** commit. `git switch main`.
   Did Git let you? (Usually yes: the change came with you. `git status`
   shows it modified on `main`.)
5. `git switch drill-branch`. The change follows you again. Uncommitted
   changes belong to the working tree, not to a branch, until committed.
6. Commit the change on `drill-branch`. `git switch main`. `cat
   workspace/hello.md` — the line is gone from `main`'s view.
7. `git log --oneline --graph --all` — see `drill-branch` one commit ahead.
8. Clean up: `git branch -D drill-branch` (capital D because it is
   unmerged and you are deliberately throwing the commit away).

Habit: `git status` before every commit. Its first line is the branch.
