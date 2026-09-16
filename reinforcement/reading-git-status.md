# Drill: Reading `git status`

Five minutes. Nothing here is committed unless you choose to.

1. Run `git status`. Write down (on paper or in your head) which of the
   three sections appear: *Changes to be committed*, *Changes not staged
   for commit*, *Untracked files*.
2. Create `workspace/drill.md` with one line. Run `git status`. Which
   section is it in? Why?
3. `git add workspace/drill.md`. Run `git status`. Which section now?
4. Edit the file: add a second line. Run `git status`. The same file appears
   in **two** sections. Explain to yourself why that is possible.
5. `git restore --staged workspace/drill.md`. Which section is it in now?
   Is your second line still in the file? (`cat` it.)
6. Delete `workspace/drill.md`. Run `git status`. Clean.

Rule to remember: each section answers a different question. Staged = "in
the next commit". Not staged = "changed since the last snapshot but not
chosen". Untracked = "Git has no snapshot of this at all".
