#!/usr/bin/env python3
# ABOUTME: Checks a learner's progress through the lessons by reading files and Git history.
# ABOUTME: Usage: python tools/check.py [NN | all | hint NN]. Read-only apart from .learning/progress.json.
"""Educational checker for the Markdown + Git course.

Each check is a small function registered with the lesson it belongs to and
the concept it tests. A check returns None when satisfied, or a
(problem, look, try) triple: what is wrong, a command to inspect the state,
and what to do about it. review.py imports CHECKS to map failures to concepts.

The Markdown checks for lessons 01 and 09 read what a learner would see
rendered: top-level fenced code blocks (backtick or tilde, closed by the same
character at least as long; an unclosed fence runs to the end of the file, as
in CommonMark) and inline code spans are set aside before headings, emphasis,
links and lists are matched. Indented code blocks are outside the taught
subset and are not detected. The checker cannot see a rendered preview;
looking at one stays the learner's job.
"""
import json
import os
import re
import subprocess
import sys
from collections import namedtuple
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS = os.path.join(ROOT, ".learning", "progress.json")
CURRICULUM = os.path.join(ROOT, "tools", "curriculum.json")
PROTECTED = ["lessons", "tools", "reinforcement", "examples", "README.md",
             "START_HERE.md", "AI_TUTOR.md", "CLAUDE.md"]
LAZY_SUBJECTS = {"update", "updates", "fix", "fixes", "stuff", "changes", "change",
                 "wip", "asdf", "test", "commit", "edit", "edits", "done", "misc"}

Check = namedtuple("Check", "lesson id concept desc fn")
CHECKS = []


def check(lesson, cid, concept, desc):
    """Register a check function under a lesson id and the concept it tests."""
    def register(fn):
        CHECKS.append(Check(lesson, cid, concept, desc, fn))
        return fn
    return register


# ---------------------------------------------------------------- helpers

def git(*args):
    """Run git in the course folder; return stdout, or '' if git failed."""
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


CURRICULUM_PATHS = ["lessons", "tools", "reinforcement", "examples"]


def is_maintainer(commit):
    """True if a commit changes curriculum files. Per CLAUDE.md only maintainers
    touch those, so this separates course history from the learner's own work
    without depending on when the learner first ran this checker."""
    return bool(git("show", "--format=", "--name-only", commit, "--", *CURRICULUM_PATHS))


def curriculum_tip():
    """The newest commit that changed the curriculum: the reference for
    'has a course file been edited by accident?'."""
    return git("log", "-1", "--format=%H", "--", *CURRICULUM_PATHS)


def is_ancestor(older, newer):
    return subprocess.run(["git", "merge-base", "--is-ancestor", older, newer],
                          cwd=ROOT, capture_output=True).returncode == 0


def learner_commits(*paths, merges=None, rev="HEAD"):
    """Subjects of the learner's own commits touching `paths` reachable from
    `rev`, newest first.

    A commit counts as the learner's when it touches these paths and does not
    touch the curriculum. That is a property of the commit itself, so it holds
    however the history was built: commits made before the first check run,
    curriculum updates pulled in later, or a course installed by cloning.
    """
    flag = {True: ["--merges"], False: ["--no-merges"], None: []}[merges]
    out = git("log", "--format=%H %s", *flag, rev, "--", *paths)
    return [line.split(" ", 1)[1] for line in out.splitlines()
            if " " in line and not is_maintainer(line.split(" ", 1)[0])]


def exclusive_commits(path, *others):
    """Hashes of the learner's commits that touch `path` and none of `others`:
    one thing per commit, not just a count of commits."""
    # A count of commits passes one bundled commit plus unrelated or empty ones.
    # git log -- path already skips commits that do not touch path. (ref: DL-007)
    hashes = git("log", "--no-merges", "--format=%H", "--", path).splitlines()
    return [h for h in hashes if not is_maintainer(h)
            and not git("show", "--format=", "--name-only", h, "--", *others)]


def merge_touching(path, both_sides=False):
    """Learner merge commits that change `path` relative to their first parent.
    With both_sides, only merges where each parent changed `path` since their
    merge base: any resolution of a real conflict (ours, theirs, combined)
    counts, and a merge that only one side touched does not."""
    def touched(h):
        if not both_sides:
            return git("diff", "--name-only", f"{h}^1", h, "--", path)
        # A conflict exists only when both sides changed `path` since their merge base.
        # Comparing h^1 with h would reject a resolution that keeps main's line, and
        # comparing h^1 with h^2 would accept a conflict-free merge. (ref: DL-005)
        base = git("merge-base", f"{h}^1", f"{h}^2")
        return base and all(git("diff", "--name-only", base, f"{h}^{n}", "--", path) for n in (1, 2))
    hashes = git("log", "--format=%H", "--merges").splitlines()
    return [h for h in hashes if touched(h) and not is_maintainer(h)]


def read(relpath):
    path = os.path.join(ROOT, relpath)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def has(pattern, text):
    return re.search(pattern, text, re.MULTILINE) is not None


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def split_fences(text):
    """Split Markdown into (prose, blocks). blocks is a list of (info, body)
    for the top-level fenced code blocks; prose is the text with every fence
    and its contents blanked, so line structure is unchanged."""
    prose, blocks, fence = [], [], None  # fence: (marker, info, body lines)
    for line in text.split("\n"):
        if fence is None:
            m = FENCE.match(line)
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = (m.group(1), m.group(2).strip(), [])
                line = ""
        else:
            marker, info, body = fence
            s = line.strip()
            if len(line) - len(line.lstrip(" ")) <= 3 and len(s) >= len(marker) and set(s) == {marker[0]}:
                blocks.append((info, "\n".join(body)))
                fence = None
            else:
                body.append(line)
            line = ""
        prose.append(line)
    if fence:
        blocks.append((fence[1], "\n".join(fence[2])))
    return "\n".join(prose), blocks


def strip_inline_code(prose):
    """Blank out backtick code spans so `**x**` is not read as bold."""
    return re.sub(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", lambda m: " " * len(m.group()), prose)


def has_prose(pattern, text):
    """`pattern` matches Markdown outside fenced blocks and inline code."""
    return has(pattern, strip_inline_code(split_fences(text)[0]))


def broken_links(folder):
    """Relative links in every .md under folder whose target file does not exist."""
    broken = []
    for dirpath, _, files in os.walk(os.path.join(ROOT, folder)):
        for name in files:
            if name.endswith(".md"):
                path = os.path.join(dirpath, name)
                broken += _broken_in(path)
    return broken


def _broken_in(path):
    text = read(os.path.relpath(path, ROOT)) or ""
    found = []
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#")[0]
        if clean and not os.path.exists(os.path.join(os.path.dirname(path), clean)):
            found.append(f"{os.path.relpath(path, ROOT)} -> {target}")
    return found


def tracked(relpath):
    return git("ls-files", "--error-unmatch", relpath) != ""


def staged(relpath):
    return relpath in git("diff", "--name-only", "--cached").splitlines()


def lazy_subjects(subjects):
    bad = []
    for s in subjects:
        words = s.strip().lower()
        if len(s) > 72 or words in LAZY_SUBJECTS or len(words) < 6 or not s[:1].isupper():
            bad.append(s)
    return bad


# ---------------------------------------------------------------- lesson 00

@check("00", "00.hello.exists", "terminal", "workspace/hello.md exists")
def _():
    if read("workspace/hello.md") is None:
        return ("workspace/hello.md was not found", "ls workspace",
                "Create the file in your editor and save it inside the workspace folder (Exercise 0.1)")


@check("00", "00.hello.heading", "headings", "workspace/hello.md starts with a level-1 heading")
def _():
    text = read("workspace/hello.md") or ""
    if not has(r"^# \S", text):
        return ("No line starting with '# ' (hash, space, text) found", "cat workspace/hello.md",
                "The first line should be '# Hello' with a space after the #")


# ---------------------------------------------------------------- lesson 01

PROFILE = "workspace/profile.md"


def profile_check(cid, concept, desc, pattern, problem, tip, target="prose"):
    """target: 'prose' (outside fences and inline code), 'inline' (outside
    fences, inline code kept) or 'blocks' (a fenced block exists; no pattern)."""
    @check("01", cid, concept, desc)
    def _():
        text = read(PROFILE)
        if text is None:
            return (f"{PROFILE} was not found", "ls workspace", "Create it (Exercise 1.1)")
        prose, blocks = split_fences(text)
        if target == "blocks":
            found = bool(blocks)
        elif target == "inline":
            found = has(pattern, prose)
        else:
            found = has_prose(pattern, text)
        if not found:
            return (problem, f"cat {PROFILE}", tip)


profile_check("01.profile.h1", "headings", "has a level-1 heading", r"^# \S",
              "no '# ' heading", "Start the file with '# Your name'")
profile_check("01.profile.h2", "headings", "has at least two level-2 headings", r"^## \S[\s\S]*^## \S",
              "fewer than two '## ' headings", "Add '## About' and '## Tools I use'")
profile_check("01.profile.bold", "emphasis", "has bold text", r"\*\*\S[^*]*\S\*\*|__\S[^_]*\S__",
              "no **bold** text", "Wrap a word in double stars with no spaces inside: **word**")
profile_check("01.profile.italic", "emphasis", "has italic text", r"(?<!\*)\*[^*\s][^*]*\*(?!\*)|(?<!_)_[^_\s][^_]*_(?!_)",
              "no *italic* text", "Wrap a word in single stars: *word*")
profile_check("01.profile.inline-code", "inline-code", "has inline code", r"`[^`\n]+`",
              "no `inline code`", "Wrap a command or program name in backticks", target="inline")
profile_check("01.profile.list", "lists", "has a list", r"^\s*([-*+]|\d+\.) \S",
              "no list found", "Lines starting with '- ' or '1. '")
profile_check("01.profile.nested", "lists", "has a nested list item", r"^\s*([-*+]|\d+\.) \S.*\n(\s*([-*+]|\d+\.) .*\n)*?\s{2,}([-*+]|\d+\.) \S",
              "no indented list item under another item", "Indent a '- ' line by two or more spaces below a list item")
profile_check("01.profile.code-block", "code-blocks", "has a fenced code block", None,
              "no fenced code block (three backticks, content, three backticks)", "See Exercise 1.2", target="blocks")
profile_check("01.profile.link", "links", "has a link", r"(?<!!)\[[^\]]+\]\([^)\s]+\)",
              "no [text](url) link", "Add a link in the Links section (Exercise 1.3)")
profile_check("01.profile.image", "images", "has an image with alt text", r"!\[[^\]]+\]\([^)\s]+\)",
              "no ![alt](url) image with non-empty alt text", "Images need text inside the square brackets")
profile_check("01.profile.blockquote", "blockquotes", "has a blockquote", r"^> \S",
              "no line starting with '> '", "Add a quote line beginning with '> '")
profile_check("01.profile.hr", "horizontal-rules", "has a horizontal rule", r"^(---|\*\*\*|___)\s*$",
              "no '---' on a line by itself", "Add a line containing only --- with blank lines around it")
profile_check("01.profile.escape", "escaping", "has an escaped character", r"\\[*#`_]",
              "no backslash-escaped symbol", r"Write \* to show a literal asterisk")


# ---------------------------------------------------------------- lesson 02

NOTES = "workspace/notes/README.md"


@check("02", "02.notes.exists", "readme-structure", "workspace/notes/README.md exists with a title")
def _():
    text = read(NOTES)
    if text is None or not has(r"^# \S", text):
        return (f"{NOTES} missing or has no '# ' title", "ls workspace/notes", "Create it (Exercise 2.1)")


@check("02", "02.notes.table", "tables", "a table with a separator row exists in the notes")
def _():
    texts = [read(NOTES) or "", read("workspace/notes/git-commands.md") or ""]
    if not any(has(r"^\|.*\|\s*\n\|?\s*:?-{3,}", t) for t in texts):
        return ("no table found (needs a header row and a |---|---| row under it)",
                f"cat {NOTES}", "See Tables in Lesson 02 Concepts")


@check("02", "02.notes.checklist", "checklists", "a checklist exists in the notes index")
def _():
    if not has(r"^\s*- \[[ x]\] \S", read(NOTES) or ""):
        return ("no '- [ ]' or '- [x]' items", f"cat {NOTES}", "Add the lesson progress checklist")


@check("02", "02.notes.second-file", "relative-links", "workspace/notes/git-commands.md exists and is linked from the index")
def _():
    if read("workspace/notes/git-commands.md") is None:
        return ("workspace/notes/git-commands.md not found", "ls workspace/notes", "Create it (Exercise 2.2)")
    if "git-commands.md" not in (read(NOTES) or ""):
        return ("index does not link to git-commands.md", f"cat {NOTES}", "Add [Git commands](git-commands.md)")


@check("02", "02.notes.link-up", "relative-links", "the index links up to ../profile.md")
def _():
    if "../profile.md" not in (read(NOTES) or ""):
        return ("no link to ../profile.md in the index", f"cat {NOTES}",
                "From inside notes/, the profile is one folder up: [My profile](../profile.md)")


@check("02", "02.notes.links-resolve", "relative-links", "every relative link under workspace/notes points at a real file")
def _():
    bad = broken_links("workspace/notes")
    if bad:
        return ("broken links: " + "; ".join(bad), "ls workspace workspace/notes",
                "Paths are relative to the file the link is in, not to your terminal")


# ---------------------------------------------------------------- lesson 03

def commit_touching(lesson, cid, path, what):
    @check(lesson, cid, "commit", f"a commit adds {what}")
    def _():
        if not tracked(path if not path.endswith("/") else path + "README.md"):
            return (f"{what} is not tracked by Git yet", "git status",
                    f"git add {path.rstrip('/')} then git commit -m \"...\"")
        if not learner_commits(path):
            return (f"no commit of yours touches {what}", f"git log --oneline -- {path}",
                    "Stage it and commit it")


commit_touching("03", "03.commit.hello", "workspace/hello.md", "workspace/hello.md")
commit_touching("03", "03.commit.profile", "workspace/profile.md", "workspace/profile.md")
commit_touching("03", "03.commit.notes", "workspace/notes/", "the workspace/notes folder")


@check("03", "03.commit.separate", "commit", "hello, profile, and notes were committed separately")
def _():
    paths = ["workspace/hello.md", PROFILE, "workspace/notes"]
    for path in paths:
        if not exclusive_commits(path, *[p for p in paths if p != path]):
            return (f"no commit of yours touches only {path}", "git log --oneline --stat",
                    "One commit per file/folder (Exercise 3.2); if they were bundled, see Recovery in Exercise 3.2")


@check("03", "03.clean", "working-tree", "working tree is clean (everything committed)")
def _():
    dirty = [l for l in git("status", "--porcelain", "--", "workspace").splitlines()
             if not l.startswith("??")]
    if dirty:
        return ("some tracked files in workspace/ are modified or staged but not committed",
                "git status", "Commit them, or git restore them if the change was accidental")


# ---------------------------------------------------------------- lesson 04

@check("04", "04.messages.quality", "commit-messages", "recent commit subjects are descriptive")
def _():
    recent = [s for s in learner_commits()[:6] if not s.startswith("Revert")]
    bad = lazy_subjects(recent)
    if bad:
        return ("these subjects are too short, too long, lowercase, or say nothing: " + "; ".join(repr(b) for b in bad),
                "git log --oneline -6", "Imperative, capitalised, under 72 characters, says what changed")


@check("04", "04.commits.two-more", "selective-staging", "two more commits exist after Lesson 03 (profile edit, notes edit)")
def _():
    for path, other in ((PROFILE, NOTES), (NOTES, PROFILE)):
        n = len(exclusive_commits(path, other))
        if n < 2:
            return (f"{path} has {n} commit(s) of its own (touching it and not {other}); expected at least two",
                    f"git log --oneline --stat -- {path}",
                    "Exercise 4.1: edit both, then commit each separately (see Recovery in 4.1 if they were bundled)")


@check("04", "04.restore.hello", "git-restore", "workspace/hello.md matches its committed version")
def _():
    if git("diff", "--name-only", "--", "workspace/hello.md") or staged("workspace/hello.md"):
        return ("hello.md differs from the last commit", "git diff workspace/hello.md",
                "Exercise 4.2 ends with git restore workspace/hello.md")


@check("04", "04.scratch.untracked", "unstaging", "workspace/scratch.md exists, is untracked, and is not staged")
def _():
    if read("workspace/scratch.md") is None:
        return ("workspace/scratch.md not found", "ls workspace", "Create it (Exercise 4.3)")
    # Recovery from a committed scratch file is git rm --cached: it untracks the file
    # and keeps it on disk, so this state stays reachable without loosening the rule.
    # (ref: DL-006)
    if tracked("workspace/scratch.md") or staged("workspace/scratch.md"):
        return ("scratch.md is staged or committed; it should be untracked", "git status",
                "If staged: git restore --staged workspace/scratch.md. If committed: git rm --cached workspace/scratch.md, then commit (Common Mistakes 4.3)")


# ---------------------------------------------------------------- lesson 05

@check("05", "05.reading-list.merged", "git-merge", "workspace/reading-list.md is on main")
def _():
    if git("branch", "--show-current") != "main":
        return ("you are not on main", "git branch --show-current", "git switch main")
    if not tracked("workspace/reading-list.md"):
        return ("reading-list.md is not on main", "git log --oneline --graph --all",
                "Commit it on the branch, then on main run git merge reading-list")


@check("05", "05.reading-list.indexed", "relative-links", "the notes index links to reading-list.md")
def _():
    if "reading-list.md" not in (read(NOTES) or ""):
        return ("notes/README.md does not mention reading-list.md", f"cat {NOTES}",
                "Add it to the Files list (step 5) and commit")


@check("05", "05.branch.deleted", "branch-delete", "the reading-list branch was deleted after merging")
def _():
    if git("branch", "--list", "reading-list"):
        return ("branch reading-list still exists", "git branch",
                "After merging: git branch -d reading-list")


# ---------------------------------------------------------------- lesson 06

FAVES = "workspace/favorites.md"


@check("06", "06.merge.commit", "merge-conflicts", "a merge commit touches favorites.md")
def _():
    if not merge_touching(FAVES, both_sides=True):
        return ("no merge commit involving favorites.md", "git log --oneline --graph -6",
                "Complete the merge: resolve, git add, git commit (Exercise 6.1)")


@check("06", "06.merge.no-markers", "conflict-markers", "favorites.md has no conflict markers")
def _():
    if has(r"^(<<<<<<<|=======|>>>>>>>)", read(FAVES) or ""):
        return ("conflict markers remain in favorites.md", f"cat {FAVES}",
                "Remove the <<<<<<< ======= >>>>>>> lines and the rejected version, then commit")


@check("06", "06.merge.finished", "merge-abort", "no merge is in progress and the practice branch is gone")
def _():
    if os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD")):
        return ("a merge is still in progress", "git status", "git add the file and git commit, or git merge --abort")
    if git("branch", "--list", "conflict-practice"):
        return ("branch conflict-practice still exists", "git branch", "git branch -d conflict-practice")


# ---------------------------------------------------------------- lesson 07

@check("07", "07.remote.origin", "remotes", "a remote named origin exists")
def _():
    if "origin" not in git("remote").splitlines():
        return ("no remote called origin", "git remote -v",
                "git remote add origin ../learn-git-remote.git (Exercise 7.1)")


NOT_PUSHED = ("origin/main does not exist; nothing has been pushed", "git log --oneline --all -3",
              "git push -u origin main")


@check("07", "07.remote.pushed", "push", "main has been pushed and has not diverged from origin/main")
def _():
    if not git("rev-parse", "--verify", "origin/main"):
        return NOT_PUSHED
    if is_ancestor("main", "origin/main") and git("rev-parse", "main") != git("rev-parse", "origin/main"):
        return ("main is behind origin/main", "git status", "git pull")
    if not is_ancestor("origin/main", "main"):
        return ("main and origin/main have diverged", "git log --oneline --graph --all -6",
                "git pull, resolve if needed, then git push")


@check("07", "07.remote.pulled", "pull", "origin/main carries a second reading-list commit and main contains it")
def _():
    if not git("rev-parse", "--verify", "origin/main"):
        return NOT_PUSHED
    if not is_ancestor("origin/main", "main"):
        return ("main does not contain everything on origin/main", "git status", "git pull")
    # Stateless on purpose: requiring main == origin/main would fail once lessons 08-09
    # advance main. The second commit must be on origin/main, which rejects unpushed
    # local edits. Which clone authored it is not provable from history, so lesson 07
    # labels that step as self-verification. (ref: DL-009)
    if len(learner_commits("workspace/reading-list.md", rev="origin/main")) < 2:
        return ("the remote does not have a second reading-list commit yet",
                "git log --oneline origin/main -- workspace/reading-list.md",
                "Make it in ../learn-git-clone, push there, then git pull here (Exercise 7.1)")


# ---------------------------------------------------------------- lesson 08

PROJECT = "workspace/project"


@check("08", "08.project.files", "readme-structure", "workspace/project/ has a README and at least one other Markdown file")
def _():
    if read(f"{PROJECT}/README.md") is None:
        return (f"{PROJECT}/README.md not found", "ls workspace/project", "Create it on the docs-improvements branch")
    others = [f for f in os.listdir(os.path.join(ROOT, PROJECT)) if f.endswith(".md") and f != "README.md"]
    if not others:
        return ("only README.md in workspace/project/", "ls workspace/project", "Add INSTALL.md and CHANGELOG.md")


@check("08", "08.project.links", "relative-links", "links inside workspace/project/ resolve")
def _():
    readme = read(f"{PROJECT}/README.md")
    if readme is None:
        return (f"{PROJECT}/README.md not found, so its links cannot be checked", "ls workspace/project",
                "Create the README first")
    bad = broken_links(PROJECT)
    if bad:
        return ("broken links: " + "; ".join(bad), "ls workspace/project", "Relative to the linking file")
    if not re.search(r"\]\((?!http)[^)]+\.md\)", readme):
        return ("README.md does not link to another file", f"cat {PROJECT}/README.md", "Link INSTALL.md and CHANGELOG.md")


@check("08", "08.project.commits", "logical-commits", "at least three commits touch workspace/project/")
def _():
    n = len(learner_commits(PROJECT))
    if n < 3:
        return (f"only {n} commit(s) touch workspace/project", f"git log --oneline -- {PROJECT}",
                "One commit per file is the habit being practised")


@check("08", "08.glossary.term", "logical-commits", "GLOSSARY.md gained a term")
def _():
    if not learner_commits("GLOSSARY.md"):
        return ("GLOSSARY.md is unchanged since the course started", "git log --oneline -- GLOSSARY.md",
                "Add one table row and commit it on the branch")


@check("08", "08.merge.no-ff", "no-ff", "docs-improvements was merged with a merge commit")
def _():
    if not any("docs-improvements" in s for s in learner_commits(merges=True)):
        return ("no merge commit mentioning docs-improvements", "git log --oneline --graph -8",
                "On main: git merge --no-ff docs-improvements")
    if git("branch", "--list", "docs-improvements"):
        return ("branch docs-improvements still exists", "git branch", "git branch -d docs-improvements")


@check("08", "08.messages.quality", "commit-messages", "recent commit subjects are descriptive")
def _():
    bad = lazy_subjects([s for s in learner_commits(PROJECT) if not s.startswith("Merge")])
    if bad:
        return ("weak subjects: " + "; ".join(repr(b) for b in bad), f"git log --oneline -- {PROJECT}",
                "Say what each commit does")


# ---------------------------------------------------------------- lesson 09

CAP = "workspace/capstone"
CAP_RULES = [
    ("h1-h3", r"^# \S[\s\S]*^## \S[\s\S]*^### \S", "heading hierarchy #, ##, ###"),
    ("bold", r"\*\*\S[^*]*\S\*\*", "bold"),
    ("italic", r"(?<!\*)\*[^*\s][^*]*\*(?!\*)", "italic"),
    ("ordered", r"^\s*\d+\. \S", "an ordered list"),
    ("unordered", r"^\s*[-*+] (?!\[)\S", "an unordered list"),
    ("link", r"(?<!!)\[[^\]]+\]\([^)\s]+\)", "a link"),
    ("code", None, "a fenced code block with a language"),  # tested on the extracted blocks
    ("table", r"^\|.*\|\s*\n\|?\s*:?-{3,}", "a table"),
    ("checklist", r"^\s*- \[[ x]\] \S", "a checklist"),
]


@check("09", "09.readme.markdown", "readme-structure", "capstone README uses every required Markdown structure")
def _():
    text = read(f"{CAP}/README.md")
    if text is None:
        return (f"{CAP}/README.md not found", "ls workspace/capstone", "Create it on your capstone branch")
    blocks = split_fences(text)[1]
    missing = [label for key, pat, label in CAP_RULES
               if not (any(info for info, _ in blocks) if key == "code" else has_prose(pat, text))]
    if missing:
        return ("missing: " + ", ".join(missing), f"cat {CAP}/README.md", "See the Markdown outcomes list in Exercise 9.1")


@check("09", "09.readme.links", "relative-links", "capstone README links to another capstone file that exists")
def _():
    readme = read(f"{CAP}/README.md")
    if readme is None:
        return (f"{CAP}/README.md not found, so its links cannot be checked", f"ls {CAP}",
                "Create the README first")
    bad = broken_links(CAP)
    if bad:
        return ("broken links: " + "; ".join(bad), f"ls {CAP}", "Fix the relative paths")
    if not re.search(r"\]\((?!http)[^)]+\.md\)", readme):
        return ("README does not link to another .md file", f"cat {CAP}/README.md", "Add a second file and link it")


@check("09", "09.recovery.documented", "git-restore", "RECOVERY.md describes a recovery and names the command used")
def _():
    text = read(f"{CAP}/RECOVERY.md")
    if text is None:
        return (f"{CAP}/RECOVERY.md not found", f"ls {CAP}", "Make a mistake, recover, write it up")
    if not re.search(r"`git (restore|revert|merge --abort|switch)[^`]*`", text):
        return ("RECOVERY.md does not mention a recovery command in inline code", f"cat {CAP}/RECOVERY.md",
                "Name the command, e.g. `git restore workspace/capstone/README.md`")


@check("09", "09.commits.count", "logical-commits", "at least four commits touch workspace/capstone/")
def _():
    n = len(learner_commits(CAP))
    if n < 4:
        return (f"only {n} commit(s) touch {CAP}", f"git log --oneline -- {CAP}", "Commit in logical units")


@check("09", "09.merge.branch", "git-merge", "capstone work was merged with a merge commit and the branch removed")
def _():
    if not merge_touching(CAP):
        return ("no merge commit touches workspace/capstone", "git log --oneline --graph -12",
                "Work on a branch, then on main: git merge --no-ff <branch>")
    unmerged = git("branch", "--no-merged", "main")
    if unmerged:
        return ("unmerged branches remain: " + unmerged.replace("\n", ", "), "git branch --no-merged main",
                "Merge or delete them")


@check("09", "09.messages.quality", "commit-messages", "capstone commit subjects are descriptive")
def _():
    bad = lazy_subjects([s for s in learner_commits(CAP) if not s.startswith(("Merge", "Revert"))])
    if bad:
        return ("weak subjects: " + "; ".join(repr(b) for b in bad), f"git log --oneline -- {CAP}", "Say what each commit does")


# ---------------------------------------------------------------- progress

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_progress():
    try:
        with open(PROGRESS, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"version": 1, "current_lesson": "00", "lessons": {}}


def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
    with open(PROGRESS, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def lesson_record(data, lesson):
    return data["lessons"].setdefault(lesson, {
        "started": now(), "completed": None, "attempts": 0, "passes": 0,
        "fails": 0, "hints_used": 0, "failed_checks": {}, "last_run": None})


def record_run(data, lesson, failures):
    rec = lesson_record(data, lesson)
    rec["attempts"] += 1
    rec["last_run"] = now()
    if failures:
        rec["fails"] += 1
        for f in failures:
            rec["failed_checks"][f.id] = rec["failed_checks"].get(f.id, 0) + 1
    else:
        rec["passes"] += 1
        rec["completed"] = rec["completed"] or now()
    data["current_lesson"] = next((l for l in lesson_ids()
                                   if not data["lessons"].get(l, {}).get("completed")), "09")


# ---------------------------------------------------------------- running

def curriculum():
    with open(CURRICULUM, encoding="utf-8") as fh:
        return json.load(fh)


def lesson_ids():
    return [l["id"] for l in curriculum()["lessons"]]


def lesson_title(lesson):
    return next(l["title"] for l in curriculum()["lessons"] if l["id"] == lesson)


def warn_protected():
    changed = git("diff", "--name-only", curriculum_tip(), "--", *PROTECTED).splitlines()
    if changed:
        print("Note: these course files differ from the original. That is usually an accident:")
        for c in changed:
            print(f"      {c}")
        print("      Look: git diff <file>    Try: git restore <file> if you did not mean to edit it.\n")


def run_lesson(lesson, data):
    """Run one lesson's checks, print educational output, record progress. Returns failures."""
    checks = [c for c in CHECKS if c.lesson == lesson]
    print(f"Lesson {lesson} — {lesson_title(lesson)}")
    failures, last_problem = [], None
    for c in checks:
        result = c.fn()
        if result is None:
            print(f"  ok    {c.id:<26} {c.desc}")
            continue
        failures.append(c)
        problem, look, fix = result
        if problem == last_problem:
            print(f"  --    {c.id:<26} (same problem as above)")
            continue
        last_problem = problem
        print(f"  --    {c.id:<26} {problem}")
        print(f"        Look: {look}")
        print(f"        Try:  {fix}")
    print(f"  {len(checks) - len(failures)} of {len(checks)} checks passed.")
    record_run(data, lesson, failures)
    recommend_drills(data, lesson, failures)
    return failures


def recommend_drills(data, lesson, failures):
    drills = curriculum()["reinforcement"]
    counts = data["lessons"][lesson]["failed_checks"]
    suggested = {drills[f.concept] for f in failures if f.concept in drills and counts.get(f.id, 0) >= 3}
    for d in sorted(suggested):
        print(f"  This keeps failing. A short drill may help: {d}")


def main(argv):
    if not git("rev-parse", "--show-toplevel"):
        print("This folder is not a Git repository. Run this from the course folder (see START_HERE.md).")
        return 2
    data = load_progress()
    if argv[:1] == ["hint"] and len(argv) == 2:
        lesson_record(data, argv[1].zfill(2))["hints_used"] += 1
        save_progress(data)
        print(f"Recorded a hint for lesson {argv[1].zfill(2)}.")
        return 0
    target = argv[0] if argv else data["current_lesson"]
    lessons = lesson_ids() if target == "all" else [target.zfill(2)]
    if any(l not in lesson_ids() for l in lessons):
        print(f"Unknown lesson {target!r}. Use 00–09, 'all', or nothing for the current lesson.")
        return 2
    warn_protected()
    failed = 0
    for lesson in lessons:
        failed += len(run_lesson(lesson, data))
        print()
    save_progress(data)
    if failed == 0:
        print(next_step(data, lessons[-1]))
    return 1 if failed else 0


def next_step(data, just_checked):
    """What to tell a learner who just passed. Points forward from the lesson
    they actually ran, not back to the earliest one they have never checked."""
    done = {l for l in lesson_ids() if data["lessons"].get(l, {}).get("completed")}
    remaining = [l for l in lesson_ids() if l not in done]
    if not remaining:
        return "All checks passed — every lesson is complete. Nothing left but to use it."
    ahead = [l for l in remaining if l > just_checked]
    nxt = ahead[0] if ahead else remaining[0]
    folder = next(l["dir"] for l in curriculum()["lessons"] if l["id"] == nxt)
    revisit = "" if ahead else "  (Lessons you have not checked yet: " + ", ".join(remaining) + ")"
    return f"All checks passed. Next: lessons/{folder}/README.md{revisit}"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
