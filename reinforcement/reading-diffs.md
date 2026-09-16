# Drill: Reading a diff

Five minutes, no commits.

1. Open `workspace/profile.md`. Change one word in a paragraph, delete one
   list item, and add one new line at the end. Save.
2. `git diff workspace/profile.md`.
3. Find, in the output:
   - the `---`/`+++` header naming the old and new file
   - an `@@ -a,b +c,d @@` line: old file starts at line *a*, new at *c*
   - the changed word: it appears as a `-` line and a `+` line, because
     Git thinks in whole lines
   - the deleted item: a `-` line with no `+` partner
   - the new line: a `+` line with no `-` partner
   - context lines with a leading space: unchanged, shown for orientation
4. `git restore workspace/profile.md` to discard the experiment (you have
   just read exactly what you are discarding, which is the habit).

Rule: `-` is what the old version had, `+` is what the new version has.
A changed line is always one of each.
