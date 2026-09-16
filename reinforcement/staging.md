# Drill: Staging on purpose

Ten minutes. Ends with two small commits.

1. Edit two files: add a line to `workspace/hello.md` and a line to
   `workspace/profile.md`.
2. `git status` — both modified. `git diff` — both diffs.
3. Stage only `hello.md`. `git diff` now shows only the profile change;
   `git diff --staged` shows only the hello change. Confirm both.
4. Commit with a message naming the hello change.
5. `git status` — profile still modified. Stage it, commit with its own
   message.
6. `git log --oneline -2` — two commits, each about one thing.

Optional: make two separate edits in the *same* file, far apart. Run
`git add -p workspace/profile.md` and answer `y` to one hunk and `n` to
the other. `git diff --staged` shows only the one you said yes to.
