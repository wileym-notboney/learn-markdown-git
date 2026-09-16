# Drill: Relative links

Five minutes, no Git needed.

The rule: a relative link is resolved from the folder containing the file
the link is written in. Your terminal's location is irrelevant.

For each row, write the link text you would put in the **from** file to
reach the **to** file, then check it by previewing and clicking.

| From | To | Link |
|------|----|------|
| `workspace/notes/README.md` | `workspace/notes/git-commands.md` | `git-commands.md` |
| `workspace/notes/README.md` | `workspace/profile.md` | `../profile.md` |
| `workspace/profile.md` | `workspace/notes/README.md` | ? |
| `workspace/notes/git-commands.md` | `examples/git-cheatsheet.md` | ? |
| `README.md` (top level) | `lessons/01-markdown-basics/README.md` | ? |

Answers: `notes/README.md`, `../../examples/git-cheatsheet.md`,
`lessons/01-markdown-basics/README.md`.

Test any link without previewing: from the folder containing the source
file, `ls <the link path>` should list the target.
