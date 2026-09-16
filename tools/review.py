#!/usr/bin/env python3
# ABOUTME: Turns learner progress data into curriculum findings (evidence, severity, likely cause, suggestion).
# ABOUTME: Usage: python tools/review.py [progress.json | folder-of-json]. Writes docs/review-<date>.md.
"""Self-review for the curriculum.

Reads one or many .learning/progress.json files (no personal data in them),
aggregates friction signals per lesson, and prints findings. Every finding
carries the evidence it rests on so a maintainer can disagree with it.
"""
import glob
import json
import os
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check as checker  # noqa: E402

CONCEPT_OF = {c.id: c.concept for c in checker.CHECKS}
LESSONS = [l["id"] for l in checker.curriculum()["lessons"]]


def load(target):
    paths = glob.glob(os.path.join(target, "*.json")) if os.path.isdir(target) else [target]
    records = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                records.append(json.load(fh))
        except (OSError, ValueError) as err:
            print(f"skipping {p}: {err}")
    return records


def seconds_between(a, b):
    try:
        return (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds()
    except (TypeError, ValueError):
        return None


def aggregate(records):
    """Per lesson: learners, completions, fails, hints, abandonments, trivial passes, failed check counts."""
    agg = {l: {"started": 0, "completed": 0, "fails": 0, "hints": 0, "abandoned": 0,
               "trivial": 0, "attempts_to_pass": [], "failed_checks": {}} for l in LESSONS}
    for rec in records:
        lessons = rec.get("lessons", {})
        for lid, r in lessons.items():
            if lid in agg:
                _add_lesson(agg[lid], r, lid, lessons)
    return agg


def _add_lesson(a, r, lid, all_lessons):
    a["started"] += 1
    a["fails"] += r.get("fails", 0)
    a["hints"] += r.get("hints_used", 0)
    for cid, n in r.get("failed_checks", {}).items():
        a["failed_checks"][cid] = a["failed_checks"].get(cid, 0) + n
    if r.get("completed"):
        a["completed"] += 1
        a["attempts_to_pass"].append(r.get("fails", 0) + 1)
        elapsed = seconds_between(r.get("started"), r.get("completed"))
        if r.get("fails", 0) == 0 and elapsed is not None and elapsed < 60:
            a["trivial"] += 1
    elif any(l > lid for l in all_lessons):
        a["abandoned"] += 1


def findings_for(lid, a, prev):
    out = []
    n = max(a["started"], 1)
    mean_attempts = sum(a["attempts_to_pass"]) / len(a["attempts_to_pass"]) if a["attempts_to_pass"] else 0
    if mean_attempts >= 3:
        out.append(finding(lid, "high", "hard to pass", f"mean {mean_attempts:.1f} check runs before first pass"))
    if a["abandoned"]:
        out.append(finding(lid, "high", "abandoned", f"{a['abandoned']} of {a['started']} moved on without passing"))
    if a["hints"] / n >= 2:
        out.append(finding(lid, "medium", "hints needed", f"{a['hints']} hints across {a['started']} learner(s)"))
    if prev is not None and a["fails"] >= 3 and a["fails"] >= 2 * max(prev["fails"], 1):
        out.append(finding(lid, "medium", "difficulty jump", f"{a['fails']} fails vs {prev['fails']} in the previous lesson"))
    if a["trivial"] and a["trivial"] == a["completed"]:
        out.append(finding(lid, "low", "trivial pass", f"all {a['completed']} completion(s) passed first try in under a minute"))
    for cid, count in a["failed_checks"].items():
        if count / n >= 3:
            out.append(finding(lid, "medium", "concept not landing",
                               f"{cid} failed {count} time(s); concept '{CONCEPT_OF.get(cid, '?')}'"))
    return out


def finding(lid, severity, signal, evidence):
    f = {"lesson": lid, "severity": severity, "signal": signal, "evidence": evidence}
    f["cause"] = classify_cause(f)
    f["suggestion"] = SUGGESTIONS.get(f["cause"], "Review the lesson against the rubric in CURRICULUM_REVIEW.md.")
    return f


SUGGESTIONS = {
    "unclear-wording": "Rewrite the exercise step the failing check maps to; add an expected-output block.",
    "missing-prerequisite": "Check curriculum.json requires; add a Concepts paragraph or a pointer to the earlier lesson.",
    "check-too-strict": "Loosen the regex or accept more variants in tools/check.py; extend selftest.py.",
    "check-buggy": "Reproduce in selftest.py, fix tools/check.py.",
    "concept-out-of-order": "Move the concept to an earlier lesson or add a reinforcement drill before it is needed.",
    "lesson-too-big": "Split into two exercises with a check after each.",
    "lesson-too-small": "Merge with a neighbour or add an optional challenge that demands understanding.",
    "trivial-pass": "Add a check that requires a decision, not just a file's existence.",
    "unclassified": "Read the lesson as a beginner and decide which rubric category applies.",
}


def classify_cause(f):
    """Map a finding (lesson, severity, signal, evidence) to one of the SUGGESTIONS keys.

    This is the judgement step of the optimisation loop: the same signal can
    have different causes (a 'hard to pass' lesson may be badly worded, or its
    check may be too strict). Returning 'unclassified' is always acceptable;
    a wrong classification is worse than none.
    """
    # TODO(human): implement the classification heuristics.
    return "unclassified"


def render(findings, agg, sources):
    lines = [f"# Curriculum review — {date.today().isoformat()}", "",
             f"Sources: {sources} progress file(s). Generated by `tools/review.py`.", "",
             "## Findings", ""]
    if not findings:
        lines.append("No findings. Either the data is thin or the lessons are holding up; check the table below.")
    for f in sorted(findings, key=lambda x: ("high", "medium", "low").index(x["severity"])):
        lines += [f"### Lesson {f['lesson']} — {f['signal']} ({f['severity']})", "",
                  f"- Evidence: {f['evidence']}", f"- Likely cause: {f['cause']}",
                  f"- Suggested change: {f['suggestion']}", ""]
    lines += ["## Per-lesson signals", "", "| Lesson | Started | Completed | Fails | Hints | Abandoned | Trivial |",
              "|--------|---------|-----------|-------|-------|-----------|---------|"]
    for lid, a in agg.items():
        lines.append(f"| {lid} | {a['started']} | {a['completed']} | {a['fails']} | {a['hints']} | {a['abandoned']} | {a['trivial']} |")
    lines += ["", "Next: classify each finding, apply the smallest change, run validate_curriculum.py and selftest.py,",
              "then record it in CURRICULUM_CHANGELOG.md."]
    return "\n".join(lines) + "\n"


def main(argv):
    target = argv[0] if argv else checker.PROGRESS
    records = load(target)
    if not records:
        print(f"No progress data found at {target}. Run tools/check.py first, or point at a folder of progress files.")
        return 1
    agg = aggregate(records)
    findings, prev = [], None
    for lid in LESSONS:
        findings += findings_for(lid, agg[lid], prev)
        prev = agg[lid]
    report = render(findings, agg, len(records))
    out = os.path.join(ROOT, "docs", f"review-{date.today().isoformat()}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    print(f"Written to {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
