# Assessment measurements and remotes

Read the [execution rules](../error-remediation-plan.md) and [progress record](progress.md) first. Load only the selected task and its listed inputs. Each task also permits its evidence entry in progress.md and required changelog entries. Paths below are relative to the repository root.

## Task 18 — Add a read-only preview mode

- **Depends on:** 17. **Coverage:** F4.
- **Read:** Task 16 contract; tools/check.py: main and run_lesson.
- **Edit scope:** tools/check.py; tools/selftest.py; README.md.
- **Change:** Implement check.py --preview NN. Separate evaluation/output from progress mutation sufficiently to preview without writes or migration. Preserve normal NN behavior until task 20.
- **Focused gate:** Preview returns 0 or 1 according to requirements, leaves existing progress bytes unchanged, and creates neither progress nor backup when absent. Invalid arguments exit 2.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 19 — Make all a diagnostic sweep

- **Depends on:** 18. **Coverage:** F4.
- **Read:** tools/check.py: all handling; task 18 preview path.
- **Edit scope:** tools/check.py; tools/selftest.py; README.md; lessons/09-capstone/README.md.
- **Change:** Route all through read-only evaluation of all ten lessons. Adjust wording: it reports current checks, not recorded lesson completion. Individual assessments record completion.
- **Focused gate:** Running all on untouched lessons makes no progress records. Running it on completed lessons does not change attempts, failures, timestamps, or migration backups.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 20 — Record immutable first-pass metrics

- **Depends on:** 19. **Coverage:** F4.
- **Read:** Task 16 transition table; tools/check.py: record_run.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Implement assessment versus completed-lesson recheck transitions exactly as contracted. Persist first-pass counters at first success and never recompute them from later failures. Use unknown for legacy history where required.
- **Focused gate:** Fresh pass then three failed rechecks retains first-pass attempts=1. Failed assessments then pass store correct frozen counts. Completion history remains intact after recheck failure; output still reports the present failure.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 21 — Remove unsupported review conclusions

- **Depends on:** 20. **Coverage:** F4.
- **Read:** Review F4; tools/review.py aggregation/classification/selfcheck; task 16 contract.
- **Edit scope:** tools/review.py; tools/selftest.py; CURRICULUM_REVIEW.md.
- **Change:** Remove duration-based triviality and inferred abandonment. Use supported first-pass assessment metrics only, excluding previews/rechecks and unknown legacy values. Report sample size/unknown counts. Keep cause labels explicitly hypothetical; update --selfcheck.
- **Focused gate:** First checker use after completed work has no learning-time claim. Diagnostic sweep has no abandonment claim. Rechecks cannot inflate first-pass difficulty; unknown data cannot silently become zero or one.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 22 — Update prescribed partial-check commands

- **Depends on:** 21. **Coverage:** F4.
- **Read:** Lessons 00–04 and all lesson Check Your Work sections; AI_TUTOR.md; README.md.
- **Edit scope:** lessons/*/README.md; AI_TUTOR.md; README.md; tools/selftest.py.
- **Change:** Change demonstration and unfinished-exercise checks to --preview NN. Keep completed-lesson checks as assessments. Explain all as read-only and ensure tutor guidance records hints without treating previews as attempts.
- **Focused gate:** A literal walkthrough of prescribed previews leaves assessment counters unchanged; normal end-of-lesson assessment records completion. Validator accepts all lesson structures.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 23 — Classify cached remote state accurately

- **Depends on:** 22. **Coverage:** F5.
- **Read:** Review F5; tools/check.py: Lesson 07; tools/selftest.py: lesson_07.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Add a pure/read-only classification for missing, equal, ahead, behind, and diverged main versus cached origin/main. Compare refs and ancestry; do not contact remotes. Operational Git errors must be distinguishable from missing refs.
- **Focused gate:** Temporary local fixtures cover every state. Equal alone meets fresh synchronization. A baseline push followed by local edits is ahead, not synchronized.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 24 — Use initial remote evidence during later checks

- **Depends on:** 23. **Coverage:** F5.
- **Read:** Task 16 remote evidence contract; tasks 19–20 and 23; Lesson 07.
- **Edit scope:** tools/check.py; tools/selftest.py; lessons/07-remotes/README.md; README.md.
- **Change:** On a successful initial assessment, store equal-ref commit evidence. Later checks may recognize historical completion plus legitimate descendants on main; report current cached state separately. A checkpoint no longer reachable from main is stale. Legacy completion without evidence stays unknown; preview/all cannot create evidence. Remove commit-count claims that prove clone/pull provenance; require manual verification of those actions.
- **Focused gate:** Fresh local-only workflow fails synchronization. After valid Lesson 07 then Lessons 08–09 without pushes, all succeeds without claiming current sync. Unreachable checkpoint is flagged; legacy state is not certified. Offline tests perform no remote operations.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.
