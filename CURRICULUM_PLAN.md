# Curriculum Plan: Early-Course Improvements (Preliminary Outline)

**Status:** Draft outline. Step A (Option 1, reorder Lesson 00) is
implemented on this branch; B and C are not started. Decisions so far, from
the maintainer: assume the learner has basic terminal knowledge and can look
up the rest; reorder first; AI-agent trial runs are being considered before
human testing (see "Trial testing" below).
**Origin:** An outside review of the curriculum raised seven concerns. This
plan covers three of them, in this order:

| Order | Concern | One-line summary |
|-------|---------|------------------|
| 1 | **A. Lesson 00 is too heavy** | Too much reading before the learner does anything |
| 2 | **B. The checker measures completion, not understanding** | Reflection answers are never captured; checks can be passed without understanding |
| 3 | **C. Retrieval practice is thin** | Reinforcement drills only appear after a failure; nothing is revisited on a schedule |

**Why this order:** A is self-contained and changes one lesson. B changes the
exercise template used by every lesson, so it should come after A (we will
only be reworking Lesson 00 once). C builds on B: a good retrieval drill can
reuse the explain-back mechanism.

**Not covered here:** the other four review concerns (no real-learner data,
solo-only conflicts and remotes, small accuracy fixes such as the Lesson 03
"four commands" table that lists five, and the number of top-level
documents). The first of those, getting real learners through the course,
should still happen and is the only way to check that any of this helped.

---

## Ground rules (from `CLAUDE.md`)

Every step below must respect these. They are restated because they shape
the plan.

- One lesson concern per commit; commit style `type(scope): description`.
- Before committing: `python tools/validate_curriculum.py` and
  `python tools/selftest.py` both pass.
- Every curriculum change gets a `CURRICULUM_CHANGELOG.md` entry (observed
  problem, evidence, hypothesis, change, expected improvement, re-evaluate)
  and `CHANGELOG.md` is staged in the same commit.
- Do not change an exercise a learner is currently completing. Queue the
  change or make it additive.
- Python standard library only. No new dependencies.
- Never touch learner-owned files (`workspace/`, `GLOSSARY.md`, `.learning/`).
- Automated proposals become commits only after a human reads the diff.

---

## A. Split or restructure Lesson 00

### A.1 What the evidence says (measured)

- `lessons/00-orientation/README.md` is the longest lesson (about 1,870
  words).
- **972 words come before Exercise 0.1**, the first thing the learner
  actually does. 653 of those are the Concepts section.
- Concepts covers seven topics at once: plain text, Markdown, paths, the
  terminal, Git, repository vs folder, and GitHub. It also explains how
  exercises are checked and how to get unstuck.
- The lesson also introduces the exercise template (nine sections) and its
  formatting conventions before any exercise exists to apply them to.
- Correction to the original review: `START_HERE.md` step 1 already asks the
  learner to run `git status`, so a first small action does exist. But it
  appears before the terminal has been explained, so it only helps a
  learner who already knows how to open a terminal and `cd`.
- Not yet verified: whether anyone actually stalls in Lesson 00. There is
  no learner data in this repo (no `.learning/` folder). The restructure is
  a hypothesis from reading, not from observed drop-off.

### A.2 Goal

The learner does something real (opens a terminal, confirms the folder,
makes a file) within the first few minutes. Each concept appears just before
the learner needs it, not all up front.

**Success criteria:**

- [ ] Concepts needed before the first action are under about 300 words.
- [ ] Each remaining concept sits next to the exercise that uses it.
- [ ] The exercise template table and formatting conventions are reachable
      but no longer block the first action.
- [ ] A learner who has never used a terminal can complete the first
      exercise from the text alone (tested with a real person; see A.6).

### A.3 Options

| Option | What changes | Cost | Risk |
|--------|--------------|------|------|
| **1. Reorder inside Lesson 00** ("do, then read") | Move Exercise 0.1 ahead of most Concepts; give each concept a short just-in-time intro | Low: one file; lesson id `00` is unchanged | Lesson stays long on paper; may not fix the feeling of weight |
| **2. Split into two lessons** | New "First Steps" (terminal, folder, `git status`, `hello.md`) and "How This Course Works" (plain text, Markdown, Git, GitHub, checker) | High: see A.4 | Renumbering or sub-ids touch tooling, links, and progress files |
| **3. Hybrid** | Do Option 1 first; only split if learner evidence says it is still too heavy | Low now, deferred cost | Delays the split you asked for |

**Recommendation:** Option 3. Option 1 is reversible and cheap, and it tests
the hypothesis. The split (Option 2) is expensive enough that it should be
justified by evidence. **This is a decision for you** (see A.7).

### A.4 What a true split would touch (verified by reading the code)

The tooling assumes two-digit lesson ids `00`–`09`:

- `tools/curriculum.json`: lesson ids, `introduces`, `requires`, and the
  `overview` flag (Lesson 00 is exempt from the concept-order scan).
- `tools/validate_curriculum.py`: compares ids as strings
  (`intro_at.get(concept, "00") <= lesson["id"]`) and treats `lesson \d\d`
  as a pointer to a later lesson. An id such as `00b` would sort correctly
  as text but would not match `\d\d`.
- `check_layout` in `tools/validate_curriculum.py` also requires ids to be
  contiguous (`00`, `01`, ... with no gaps), so a sub-id such as `00b` would
  fail validation until that rule changes.
- `tools/check.py`: registers checks per lesson id; the existing
  `00.hello.exists` and `00.hello.heading` checks belong to Exercise 0.1; the
  progress file starts at `current_lesson: "00"`; it uses `zfill(2)`; and its
  error text says "Use 00–09".
- `tools/selftest.py`: has `lesson_00_02` and expects every lesson to fail
  before the work and pass after.
- `tools/review.py`: has a classification rule keyed to lesson `00`.
- Links to Lesson 00 in `START_HERE.md`, `README.md`, `GLOSSARY.md` (the
  "terminal" row), and `lessons/01-markdown-basics/README.md`.
- Renumbering every later lesson would also invalidate existing learners'
  `.learning/progress.json` files.

If we split, the lowest-risk id scheme is probably to keep `00` as the first
half and add the second half under a new id, rather than renumbering 01–09.
That needs tooling changes (the `\d\d` and `zfill(2)` assumptions) and is a
decision to confirm first.

### A.5 Proposed content map (applies to Option 1 and to the split)

| Part | Content | Approx. words |
|------|---------|---------------|
| Opening | Two or three sentences: what you will do first; nothing here can break anything | ~60 |
| Just-in-time: terminal and working directory | What a terminal is, `pwd` / `ls` / `cd` table | ~150 |
| **Exercise 0.1 (revised)** | Find the folder, run `git status`, create `workspace/hello.md` | existing |
| Just-in-time: what you just saw | Plain text, Markdown, untracked file, repository vs folder (explained against the output the learner just produced) | ~200 |
| How the course works | The exercise template table and formatting conventions | existing, moved |
| Git and GitHub in one paragraph each | Kept short; the full mental model arrives in Lesson 03 | ~120 |
| Exercise 0.2 (Read the checker) | Existing, with the "how checking works" and "getting unstuck" text moved next to it | existing |

All existing exercise content, checks, and the `workspace/hello.md` outcome
stay the same, so `00.hello.exists` and `00.hello.heading` keep working.

### A.6 Steps

1. **Check state first:** `git status`, `git log --oneline -5`. Confirm no
   learner is mid-Lesson-00 in this clone (there is no `.learning/` here, so
   none locally; other learners' clones are their own).
2. **Draft** the reordered Lesson 00 (Option 1) in one commit, touching only
   `lessons/00-orientation/README.md`.
3. **Update `tools/curriculum.json`** only if `introduces` changes (it should
   not for Option 1).
4. **Validate:** `python tools/validate_curriculum.py`, then
   `python tools/selftest.py`. Both must pass.
5. **Record:** add the `CURRICULUM_CHANGELOG.md` entry and stage
   `CHANGELOG.md`.
6. **Test with a person:** hand the revised lesson to one or two people who
   have never used a terminal. Watch without helping. Note where they pause.
   This is the real test of the hypothesis.
7. **Decide on the split** using what step 6 shows. If yes, write a
   separate follow-up plan for the id scheme and tooling changes in A.4.

### A.7 Open questions (need your decision)

- [x] Option 1 first, then split only if needed. **Decided:** reorder first.
- [ ] If we split: new id scheme (keep `00`, add a second id) versus
      renumbering 01–09? Renumbering breaks existing progress files.
- [ ] Should `START_HERE.md` step 1 (`git status` before any explanation)
      move into Lesson 00, or stay as a smoke test?
- [ ] Is there a real beginner available for the step 6 test? (Open. AI
      agent trials may come first; see below.)

---

## B. Check understanding, not just completion

### B.1 What the evidence says

- The checker verifies that files and commits exist. It does not capture
  Reflection answers; those questions ("Try it: edit, `git status`, see…")
  are prompts with nowhere to be answered.
- `CURRICULUM_REVIEW.md` already says a check everyone passes instantly is a
  "trivial pass" finding. The capstone's `RECOVERY.md` check only requires
  that a command appear in inline code, which a learner can satisfy without
  understanding why that command was right.
- `CLAUDE.md` says to optimise for understanding and independence, but the
  signals in `.learning/progress.json` (attempts, passes, fails, hints) all
  measure completion effort.

### B.2 Goal

Learners put key ideas in their own words at a few well-chosen points, and a
human or the AI tutor can read those words. The checker stays a
completeness tool; understanding is reviewed by a person.

### B.3 Design questions to settle before building

- **Where does the explanation live?** A learner-owned file (for example
  `workspace/reflections.md`) fits the protected/learner-owned split in
  `CLAUDE.md`. It is committed in the learner's own history, so it doubles as
  commit practice.
- **Who reads it?** The AI tutor per `AI_TUTOR.md` (hint ladder stays in
  force), or a person. Automated grading of free text is not proposed:
  `CURRICULUM_REVIEW.md` says automated tooling proposes and a human decides.
- **What does the checker do?** At most: confirm an entry exists and is not
  trivially short, with wording that makes clear this checks effort, not
  correctness. Anything stronger would be guessing.
- **How many prompts?** A few per course, at high-value moments. Candidates
  to evaluate: end of Lesson 03 (three places), Lesson 05 (what a branch is),
  Lesson 06 (what a conflict is), Lesson 09 (already has `RECOVERY.md`).

### B.4 Steps

1. Read the Reflection sections across all ten lessons and list which
   questions test understanding versus which are curiosity prompts.
2. Pick the three to four highest-value prompts (see B.3).
3. Add an explain-back section to those lessons additively (new section at
   the end, no change to existing steps) so no active learner is disrupted.
4. Add a matching optional check or a progress note; update `selftest.py`
   so the new behaviour is exercised.
5. Update `AI_TUTOR.md` with how the tutor should read and respond to an
   explain-back entry, within the hint ladder.
6. Validate, record in `CURRICULUM_CHANGELOG.md`, stage `CHANGELOG.md`.

### B.5 Open questions

- [ ] Is `workspace/reflections.md` the right home, or one file per lesson?
- [ ] Should the checker only confirm presence, or not touch it at all?
- [ ] Where should the tightening of the capstone `RECOVERY.md` check
      (for example, requiring the command and a reason) fit in?

---

## C. Add spaced retrieval practice

### C.1 What the evidence says

- `reinforcement/` holds five short drills (about 120 to 160 words each)
  covering `git status`, staging, diffs, links, and branch switching.
- They are offered only by `check.py` after a check fails repeatedly
  (`tools/curriculum.json` maps concepts to drills; the checker prints "This
  keeps failing. A short drill may help").
- Nothing prompts a learner to revisit an earlier concept unprompted later in
  the course. Memory research favours recall that is spaced out and
  attempted without looking.

### C.2 Goal

At planned points the learner recalls earlier material without notes, then
checks themselves against the lesson. Reactive drills stay; scheduled ones
are added.

### C.3 Design questions

- **What is the unit?** A short "from memory" block (three to five
  questions or tiny tasks) at the start of selected later lessons, covering
  concepts from two or more lessons back.
- **How do we avoid new tooling?** Prefer plain-Markdown content over new
  Python. If the checker is involved, keep it to reading prior state.
- **Which concepts?** Use the dependency map in `tools/curriculum.json`;
  start with the concepts the existing drills already target (status,
  staging, diffs, branches) since those are the highest-failure candidates.
- **Reuse B.** Where possible, a retrieval prompt is answered in the same
  `workspace/reflections.md` mechanism from B, so there is one new habit, not
  two.

### C.4 Steps

1. List where each concept in `curriculum.json` is introduced and where it is
   next used; flag gaps longer than two lessons.
2. Draft retrieval blocks for the three to five biggest gaps.
3. Add them at the top of the relevant later lessons as an additive section.
4. Update `reinforcement/README.md` to explain scheduled versus reactive
   drills.
5. Validate (including the concept-order scan in `validate_curriculum.py`, which
   flags prose that mentions a concept before its lesson without a pointer),
   record, and commit.

### C.5 Open questions

- [ ] How many retrieval prompts are enough without becoming a chore?
- [ ] Should answers be saved, shown only, or checked for presence?

---

## Cross-cutting: how we will know any of this worked

Nothing in A, B, or C can be judged from the repo alone. The review loop in
`CURRICULUM_REVIEW.md` already defines what to compare (attempts before first
pass, hints requested, abandonment) but has only run on simulated data.

- [ ] Run each change past at least one real beginner before treating it as
      done.
- [ ] Collect `.learning/progress.json` files from those runs and use
      `python tools/review.py` on them.
- [ ] Re-evaluate A after the first real-learner test; do not start B until
      A's outcome is recorded.

## Suggested sequence (each bullet = one commit unless noted)

1. `docs(plan)`: add this outline (this file).
2. `fix(lesson-00)`: restructure Lesson 00 (Option 1), plus changelog entries.
3. Real-learner test of Lesson 00; record the outcome.
4. Decision on whether to split; if yes, a separate plan.
5. B: explain-back prompts (additive), one lesson concern per commit.
6. C: scheduled retrieval blocks (additive), one lesson concern per commit.

## Trial testing before a human (under consideration)

The maintainer is considering AI agents trial-running the curriculum before
a human does. Assessment, to be confirmed by trying it:

- **Likely useful for:** mechanical faults (a command that errors, an
  expected output that no longer matches, a broken link, a check that fails
  on correct work, ambiguous step order). The earlier hand-walk of lessons
  04 to 09 found three such faults that the self-test could not reach.
- **Likely not useful for:** confusion, motivation, and whether a concept
  sticks. An agent already knows Git, cannot un-know it, and does not get
  bored or lost the way a beginner does. A clean agent run is not evidence
  that a beginner will understand.
- **If done:** use a fresh clone per run, tell the agent to follow only the
  written lesson text (no outside knowledge of Git, and to report every point
  where it had to guess), give it a persona with limited terminal skill, and
  keep its own report as the data. Treat findings as proposals; a human reads
  them before any change is committed, per `CLAUDE.md`.
- **Still needed:** at least one real beginner, since agent runs do not
  replace that.
