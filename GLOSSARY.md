# Glossary

Plain-language definitions. Terms link to the lesson that introduces them.
You are welcome to add terms here; Lesson 08 asks you to.

| Term | Meaning | Lesson |
|------|---------|--------|
| **terminal** | A program where you type commands instead of clicking. Also called shell, console, or command line. | [00](lessons/00-orientation/README.md) |
| **directory** | A folder. The two words mean the same thing. | 00 |
| **working directory** | The folder your terminal is "in" right now. Commands act relative to it. | 00 |
| **path** | The address of a file or folder, like `workspace/profile.md`. | 00 |
| **plain text** | A file containing only characters, no hidden formatting. Markdown is plain text. | 00 |
| **Markdown** | A way of writing plain text with light symbols (`#`, `*`, `-`) so it can be turned into formatted documents. | [01](lessons/01-markdown-basics/README.md) |
| **render** | Turn Markdown into its formatted appearance (what GitHub or a preview pane shows). | 01 |
| **relative link** | A link whose address is measured from the current file, like `../README.md`. | [02](lessons/02-practical-markdown/README.md) |
| **Git** | A program that records snapshots of a folder over time and lets you compare, branch, and restore them. | [03](lessons/03-git-foundations/README.md) |
| **repository (repo)** | A folder that Git is tracking. The tracking data lives in a hidden `.git` subfolder. | 03 |
| **working tree** | The actual files in your repository folder, as they are right now. | 03 |
| **tracked / untracked** | Tracked files are ones Git already knows about. Untracked files are new to Git. | 03 |
| **staging area (index)** | The set of changes you have chosen to include in the next commit. | 03 |
| **stage** | Add a change to the staging area (`git add`). | 03 |
| **commit** | A saved snapshot of the staged changes, with a message, author, and time. Also the verb. | 03 |
| **history** | The chain of all commits so far. | 03 |
| **HEAD** | Git's name for "the commit you are currently on". | 03 |
| **diff** | The exact lines that differ between two versions. | 03 |
| **commit message** | A short description saved with a commit explaining what it does. | [04](lessons/04-everyday-git/README.md) |
| **restore** | Put a file back to the way it was in a commit or the staging area. | 04 |
| **branch** | A named line of development. Lets you work on something without disturbing `main`. | [05](lessons/05-branches/README.md) |
| **main** | The default branch. The version of the project that is considered current. | 05 |
| **switch** | Move your working tree to a different branch. | 05 |
| **merge** | Combine the commits from one branch into another. | 05 |
| **merge commit** | A commit with two parents, created when merging. | 05 |
| **merge conflict** | Git could not combine two changes to the same lines automatically and asks you to decide. | [06](lessons/06-merge-conflicts/README.md) |
| **conflict markers** | The `<<<<<<<`, `=======`, `>>>>>>>` lines Git writes into a conflicted file. | 06 |
| **remote** | A copy of the repository somewhere else (another folder, a server, GitHub). | [07](lessons/07-remotes/README.md) |
| **origin** | The conventional name for the main remote. Just a nickname for an address. | 07 |
| **clone** | Make a full local copy of a remote repository. | 07 |
| **push / pull / fetch** | Send commits to a remote / bring commits from a remote in and merge them / bring them in without merging. | 07 |
| **GitHub** | A website that hosts Git repositories and adds collaboration features like pull requests. | 07 |
| **pull request (PR)** | A GitHub request to merge one branch into another, with discussion and review. | 07 |
| **.gitignore** | A file listing paths Git should not track. | 04 |
