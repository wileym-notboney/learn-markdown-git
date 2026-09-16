#!/usr/bin/env python3
# ABOUTME: Structural tests for the curriculum: lesson layout, exercise sections, links, and concept ordering.
# ABOUTME: Usage: python tools/validate_curriculum.py. Exit 0 when the curriculum is internally consistent.
"""Treat the curriculum like software and test it.

Checks: lesson folders are numbered contiguously and match curriculum.json;
every lesson has Objectives, Concepts, and at least one exercise; every
exercise has all nine sections in order; relative links resolve; every
lesson's `requires` was introduced earlier; prose does not mention a
concept before the lesson that introduces it (except in an explicit
"Lesson NN" pointer); every lesson has at least one check in check.py.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check as checker  # noqa: E402

SECTIONS = ["Goal", "Why This Matters", "Before You Start", "Instructions", "Check Your Work",
            "What You Should Notice", "Common Mistakes", "Recovery", "Reflection"]
problems = []


def problem(where, what):
    problems.append(f"{where}: {what}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def prose_lines(text):
    """Paragraphs outside fenced code blocks, joined to one line each, with inline code removed."""
    paragraphs, current, fenced = [], [], False
    for line in text.splitlines() + [""]:
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.strip():
            current.append(line.strip())
        elif current:
            paragraphs.append(re.sub(r"`[^`]*`", "", " ".join(current)))
            current = []
    return paragraphs


def check_layout(lessons):
    dirs = sorted(d for d in os.listdir(os.path.join(ROOT, "lessons")) if not d.startswith("."))
    expected = [l["dir"] for l in lessons]
    if dirs != expected:
        problem("lessons/", f"folders {dirs} do not match curriculum.json {expected}")
    for i, l in enumerate(lessons):
        if l["id"] != f"{i:02d}":
            problem("curriculum.json", f"lesson ids not contiguous at {l['id']}")


def check_lesson_structure(lesson, text):
    where = f"lessons/{lesson['dir']}/README.md"
    for heading in ("## Objectives", "## Concepts"):
        if heading not in text:
            problem(where, f"missing '{heading}'")
    exercises = re.split(r"^## (?:Optional )?(?:Exercise|Challenge) ", text, flags=re.M)[1:]
    if not exercises:
        problem(where, "no '## Exercise' sections")
    for ex in exercises:
        name = ex.splitlines()[0]
        found = re.findall(r"^### (.+)$", ex, flags=re.M)
        if found != SECTIONS:
            problem(where, f"exercise '{name}' sections are {found}, expected {SECTIONS}")


def check_links(path, text):
    for target in re.findall(r"\]\(([^)\s]+)\)", "\n".join(prose_lines(text))):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#")[0]
        if clean and not os.path.exists(os.path.join(os.path.dirname(path), clean)):
            problem(os.path.relpath(path, ROOT), f"broken link {target}")


def check_prerequisites(lessons):
    introduced = set()
    for l in lessons:
        for req in l["requires"]:
            if req not in introduced:
                problem(f"lesson {l['id']}", f"requires '{req}' which no earlier lesson introduces")
        introduced |= set(l["introduces"])


def check_concept_order(lessons, keywords):
    """Flag prose that mentions a concept before its lesson, unless the line points to a later lesson."""
    intro_at = {c: l["id"] for l in lessons for c in l["introduces"]}
    for l in lessons:
        if l.get("overview"):
            continue
        text = read(os.path.join(ROOT, "lessons", l["dir"], "README.md"))
        for n, line in enumerate(prose_lines(text), 1):
            _scan_line(l, n, line.lower(), keywords, intro_at)


def _scan_line(lesson, n, line, keywords, intro_at):
    if re.search(r"lesson \d\d|later|advanced topic|not yet|do not run|should not run", line):
        return
    for concept, words in keywords.items():
        if intro_at.get(concept, "00") <= lesson["id"]:
            continue
        for w in words:
            if re.search(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", line):
                problem(f"lesson {lesson['id']} paragraph {n}", f"mentions '{w}' ({concept}, introduced in {intro_at[concept]}) without a pointer")


def check_checks_exist(lessons):
    covered = {c.lesson for c in checker.CHECKS}
    for l in lessons:
        if l["id"] not in covered:
            problem(f"lesson {l['id']}", "has no checks in tools/check.py")
    for c in checker.CHECKS:
        if c.lesson not in [l["id"] for l in lessons]:
            problem("check.py", f"{c.id} belongs to unknown lesson {c.lesson}")


def main():
    data = json.load(open(os.path.join(ROOT, "tools", "curriculum.json"), encoding="utf-8"))
    lessons = data["lessons"]
    check_layout(lessons)
    check_prerequisites(lessons)
    check_concept_order(lessons, data["concept_keywords"])
    check_checks_exist(lessons)
    for l in lessons:
        path = os.path.join(ROOT, "lessons", l["dir"], "README.md")
        if not os.path.isfile(path):
            problem(path, "missing")
            continue
        text = read(path)
        check_lesson_structure(l, text)
        check_links(path, text)
    for name in ("README.md", "START_HERE.md", "GLOSSARY.md", "AI_TUTOR.md", "CLAUDE.md", "CONTRIBUTING.md",
                 "CURRICULUM_REVIEW.md", "reinforcement/README.md"):
        check_links(os.path.join(ROOT, name), read(os.path.join(ROOT, name)))
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(problems)} problem(s) found across {len(lessons)} lessons and {len(checker.CHECKS)} checks.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
