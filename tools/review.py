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
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check as checker  # noqa: E402

CONCEPT_OF = {c.id: c.concept for c in checker.CHECKS}
LESSONS = [l["id"] for l in checker.curriculum()["lessons"]]
CHECK_COUNT = {l: sum(1 for c in checker.CHECKS if c.lesson == l) for l in LESSONS}
INTRODUCED_IN = {c: l["id"] for l in checker.curriculum()["lessons"] for c in l["introduces"]}
BIG_LESSON = 6  # a lesson with this many checks is doing enough to be worth splitting


def load(target):
    paths = glob.glob(os.path.join(target, "*.json")) if os.path.isdir(target) else [target]
    records = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as err:
            print(f"skipping {p}: {err}")
            continue
        # Same shape rule as check.py, so a stray JSON file cannot crash aggregation.
        # (ref: DL-010)
        if checker.valid_progress(data):
            records.append(data)
        else:
            print(f"skipping {p}: not a progress record")
    return records


def aggregate(records):
    """Per lesson: records, completions, fails, hints, attempts to first pass, failed check counts."""
    agg = {l: {"started": 0, "completed": 0, "fails": 0, "hints": 0,
               "attempts_to_pass": [], "failed_checks": {}} for l in LESSONS}
    for rec in records:
        for lid, r in rec.get("lessons", {}).items():
            if lid in agg:
                _add_lesson(agg[lid], r)
    return agg


# started/completed timestamps cannot measure learning time and a missing later record
# cannot prove abandonment, so neither is reported. (ref: DL-011)
def _add_lesson(a, r):
    a["started"] += 1
    a["fails"] += r.get("fails", 0)
    a["hints"] += r.get("hints_used", 0)
    for cid, n in r.get("failed_checks", {}).items():
        a["failed_checks"][cid] = a["failed_checks"].get(cid, 0) + n
    if r.get("completed"):
        a["completed"] += 1
        if "fails_before_pass" in r:  # records without it are unknown, not guessed
            a["attempts_to_pass"].append(r["fails_before_pass"] + 1)


def findings_for(lid, a, prev):
    out = []
    n = max(a["started"], 1)
    mean_attempts = sum(a["attempts_to_pass"]) / len(a["attempts_to_pass"]) if a["attempts_to_pass"] else 0
    if mean_attempts >= 3:
        out.append(finding(lid, "high", "hard to pass", f"mean {mean_attempts:.1f} check runs before first pass", a))
    if a["hints"] / n >= 2:
        out.append(finding(lid, "medium", "hints needed", f"{a['hints']} hints across {a['started']} learner(s)", a))
    if prev is not None and a["fails"] >= 3 and a["fails"] >= 2 * max(prev["fails"], 1):
        out.append(finding(lid, "medium", "difficulty jump", f"{a['fails']} fails vs {prev['fails']} in the previous lesson", a))
    out += concept_findings(lid, a, n)
    return out


def concept_findings(lid, a, n):
    """One finding per struggling concept, not per check: several checks often
    test the same idea, and three copies of one diagnosis hides the others."""
    by_concept = {}
    for cid, count in a["failed_checks"].items():
        if count / n >= 3:
            by_concept.setdefault(CONCEPT_OF.get(cid), []).append((cid, count))
    out = []
    for concept, checks in by_concept.items():
        ids = ", ".join(f"{cid} x{count}" for cid, count in sorted(checks))
        out.append(finding(lid, "medium", "concept not landing",
                           f"concept '{concept}' — failing checks: {ids}", a, concept=concept))
    return out


def finding(lid, severity, signal, evidence, agg=None, concept=None):
    f = {"lesson": lid, "severity": severity, "signal": signal, "evidence": evidence,
         "hints": (agg or {}).get("hints", 0), "concept": concept}
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
    "unclassified": "Read the lesson as a beginner and decide which rubric category applies.",
}


def classify_cause(f):
    """Map a finding to one of the SUGGESTIONS keys.

    The judgement step of the optimisation loop: one signal can have several
    causes, so each rule leans on a second piece of evidence to tell them
    apart. Every rule that cannot find that second piece returns
    "unclassified" — a wrong diagnosis sends a maintainer to rewrite the
    wrong lesson, which is worse than no diagnosis at all. The final call is
    always a human's, recorded in CURRICULUM_CHANGELOG.md.
    """
    signal, lesson, hints = f["signal"], f["lesson"], f["hints"]
    if signal == "hints needed":
        return "unclear-wording"
    if signal == "concept not landing":
        return _concept_cause(f["concept"], lesson)
    if signal == "hard to pass":
        # Hints mean the learner knew they were stuck and the text did not
        # rescue them. No hints means they believed they were done, so
        # suspect the check before the prose.
        return "unclear-wording" if hints else "check-too-strict"
    if signal == "difficulty jump":
        # A lesson doing many things is more likely oversized than misordered.
        return "lesson-too-big" if CHECK_COUNT.get(lesson, 0) >= BIG_LESSON else "concept-out-of-order"
    return "unclassified"


def _concept_cause(concept, lesson):
    """A concept failing in the lesson that teaches it is a teaching problem;
    failing later means the earlier lesson did not make it stick."""
    introduced = INTRODUCED_IN.get(concept)
    if introduced is None:
        return "unclassified"
    if introduced == lesson:
        return "unclear-wording"
    return "missing-prerequisite"


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
    lines += ["## Per-lesson signals", "", "| Lesson | Records | Completed | Fails | Hints |",
              "|--------|---------|-----------|-------|-------|"]
    for lid, a in agg.items():
        lines.append(f"| {lid} | {a['started']} | {a['completed']} | {a['fails']} | {a['hints']} |")
    lines += ["", "Next: classify each finding, apply the smallest change, run validate_curriculum.py and selftest.py,",
              "then record it in CURRICULUM_CHANGELOG.md."]
    return "\n".join(lines) + "\n"


def selfcheck():
    """assert-based check of the classification rules; run with --selfcheck."""
    def f(signal, lesson="03", hints=0, concept=None):
        return classify_cause({"signal": signal, "lesson": lesson, "hints": hints, "concept": concept})

    assert f("hints needed") == "unclear-wording"
    assert f("hard to pass", hints=0) == "check-too-strict"
    assert f("hard to pass", hints=4) == "unclear-wording"
    # 'commit' is introduced in lesson 03, so failing there is a teaching problem...
    assert f("concept not landing", lesson="03", concept="commit") == "unclear-wording"
    # ...and failing in a later lesson means it never stuck.
    assert f("concept not landing", lesson="08", concept="commit") == "missing-prerequisite"
    assert f("concept not landing", concept="not-a-concept") == "unclassified"
    assert f("difficulty jump", lesson="01") == "lesson-too-big"        # 13 checks
    assert f("difficulty jump", lesson="00") == "concept-out-of-order"  # 2 checks
    assert f("something new") == "unclassified"
    assert set(SUGGESTIONS) >= {f(s, hints=h, concept=c)
                                for s in ("hints needed", "hard to pass",
                                          "difficulty jump", "concept not landing")
                                for h in (0, 5) for c in (None, "commit")}, "a rule returned an unknown key"
    print("classify_cause: all rules behave as documented")


def main(argv):
    if argv[:1] == ["--selfcheck"]:
        selfcheck()
        return 0
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
