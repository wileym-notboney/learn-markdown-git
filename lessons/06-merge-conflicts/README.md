# Lesson 06 — Merge Conflicts

## Objectives

By the end of this lesson you can:

- explain why a conflict happens
- read conflict markers and identify which version is which
- choose a resolution, remove the markers, and complete the merge
- back out of a merge you are not ready for

## Concepts

### Why conflicts happen

Git merges by lines. When two branches change *different* lines of a file,
Git keeps both changes. When they change the *same* lines, Git cannot know
which is right, so it stops and hands the decision to you. That is a
conflict. It is not an error; it is a question.

### What a conflict looks like

`git merge` prints `CONFLICT (content): Merge conflict in <file>` and
`Automatic merge failed; fix conflicts and then commit the result.`
`git status` shows the file under *Unmerged paths* as `both modified`.

Inside the file, Git writes both versions between markers:

```text
<<<<<<< HEAD
- Favorite color: green
=======
- Favorite color: blue
>>>>>>> conflict-practice
```

- Between `<<<<<<< HEAD` and `=======`: the version on the branch you are
  on (usually `main`).
- Between `=======` and `>>>>>>> name`: the version from the branch being
  merged in.

Everything outside the markers merged fine and is left alone.

### Resolving

1. Open the file. Find every marker block (search for `<<<<<<<`).
2. Decide what the line should say: one side, the other, or something new.
3. Delete the three marker lines and the version you are not keeping.
4. Save. The file should look like an ordinary file with no `<<<<<<<`,
   `=======`, or `>>>>>>>` anywhere.
5. `git add <file>` — this is how you tell Git "resolved".
6. `git commit` — Git pre-fills a merge message; keep it. Using `-m` is
   fine too.

### Backing out

`git merge --abort` at any point before the final commit returns the
repository to exactly how it was before `git merge`. No work is lost. Use
it freely if you feel lost; you can retry the merge as many times as you
like.

### Seeing both sides without the markers

```text
git diff                    shows the conflicted regions
git show main:<file>        the file as it is on main   (read-only)
git show <branch>:<file>    the file as it is on the other branch
```

---

## Exercise 6.1 — Cause a conflict on purpose and resolve it

### Goal

Create `workspace/favorites.md`, let a helper script make a branch that
changes one line, change the same line yourself on `main`, merge, resolve.

### Why This Matters

Everyone hits a conflict eventually, usually at a bad moment. Meeting one
in a controlled setting, where the other branch was made by a script and
nothing is at stake, removes the fear.

### Before You Start

Lesson 05 passed, on `main`, clean working tree (scratch.md untracked is
fine).

### Instructions

1. Create `workspace/favorites.md` with exactly these lines. The helper
   script looks for the `Favorite color` line, so keep that text:

   ```markdown
   # Favorites

   - Favorite color: green
   - Favorite food: bread
   - Favorite tool: git
   ```

2. Commit it on `main` (you know how). Confirm with `git log --oneline -1`.

3. Run the helper. It creates a branch `conflict-practice`, changes the
   colour line on that branch, commits, and switches you back to `main`. It
   prints what it did. It touches nothing else.

   ```text
   python tools/setup_conflict.py
   ```

4. Look at what it made (read-only):

   ```text
   git log --oneline --graph --all
   git show conflict-practice:workspace/favorites.md
   ```

5. Now, on `main`, edit the **same** colour line to a different colour of
   your own choosing. Commit it.

6. Merge and read the message carefully:

   ```text
   git merge conflict-practice
   git status
   ```

   *Expected:* `CONFLICT (content)` and `both modified: workspace/favorites.md`.

7. Open `workspace/favorites.md`. Find the markers. Decide on the colour
   (either, or a third). Remove the markers and the rejected line. Save.
   The file should have exactly three list items again.

8. Tell Git it is resolved and finish the merge:

   ```text
   git add workspace/favorites.md
   git status
   git commit
   ```

   If an editor opens with a pre-written message, save and close it (in
   vim: `Esc`, `:wq`, Enter). Or use `git commit -m "Merge conflict-practice"`.

9. Confirm and clean up:

   ```text
   git log --oneline --graph -5
   git branch -d conflict-practice
   ```

### Check Your Work

```text
python tools/check.py 06
```

The checker looks for a merge commit touching `favorites.md`, confirms no
markers remain, and that the branch is gone.

### What You Should Notice

- Two of the three list lines merged without comment. Only the line both
  sides changed needed you.
- `git add` on a conflicted file means "I have resolved this". Nothing
  about the merge is final until the commit.
- The merge commit has two parents. `git log --graph` draws the join.

### Common Mistakes

- Committing with markers still in the file. Git allows it; the checker
  does not, and neither would a colleague. Search for `<<<<<<<` before
  `git add`.
- Editing a different line in step 5, so no conflict happens and the merge
  just works. Fine, but you missed the point: `git merge --abort` is not
  needed, just rerun the setup script after resetting the colour line to
  its original value and try again.
- Running `setup_conflict.py` before committing `favorites.md`. It refuses
  and says why.

### Recovery

- Lost in the middle? `git merge --abort`. Everything returns to before
  the merge. Re-read Concepts and try again from step 6.
- Ran the script twice? It refuses if the branch already exists. Delete it
  with `git branch -D conflict-practice` (capital D, because it is
  unmerged and you are deliberately discarding it), then rerun.
- Resolved wrongly and already committed? Fix the file, commit again with
  a message like "Fix favorites after merge". History with a correction in
  it is normal.

### Reflection

- What information did Git *not* have that you had, which made the decision
  yours?
- When would you keep both versions?
