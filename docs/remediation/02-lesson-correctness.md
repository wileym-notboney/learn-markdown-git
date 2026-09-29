# Lesson correctness

Read the [execution rules](../error-remediation-plan.md) and [progress record](progress.md) first. Load only the selected task and its listed inputs. Each task also permits its evidence entry in progress.md and required changelog entries. Paths below are relative to the repository root.

## Task 08 — Accept all permitted conflict choices

- **Depends on:** 07. **Coverage:** F3.
- **Read:** Review F3; tools/check.py: merge_touching and Lesson 06 checks.
- **Edit scope:** tools/check.py; tools/selftest.py; lessons/06-merge-conflicts/README.md.
- **Change:** Implement a Lesson 06-specific merge predicate if needed to avoid changing capstone behavior. Search merges reachable from main; inspect both parents and favorites path history rather than only result versus first parent.
- **Focused gate:** Ours, theirs, and third-color resolutions pass. An unrelated merge and a relevant merge confined to an unmerged side branch fail. Existing capstone still passes.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 09 — Detect incomplete merges through Git

- **Depends on:** 08. **Coverage:** F3.
- **Read:** tools/check.py: 06.merge.finished; Lesson 06.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Use Git to locate/detect MERGE_HEAD instead of joining ROOT/.git/MERGE_HEAD. Preserve branch cleanup and marker requirements.
- **Focused gate:** Unfinished merges fail in a regular checkout and a linked worktree. Committed conflict markers fail. Completed allowed resolutions still pass.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 10 — Repair scratch recovery instructions

- **Depends on:** 09. **Coverage:** F8.
- **Read:** Review F8; Lesson 04 Common Mistakes and Recovery; scratch checker.
- **Edit scope:** lessons/04-everyday-git/README.md; tools/selftest.py; tools/check.py only if feedback needs correction.
- **Change:** Document git rm --cached workspace/scratch.md, inspect the staged removal, then commit with an otherwise clean index. Explain that contents stay on disk; do not stage the path again. If Git refuses, inspect rather than force. Remove the different-filename suggestion.
- **Focused gate:** Following the exact written recovery from committed scratch preserves bytes and passes the scratch check. A different path fails. Ordinary restore --staged behavior still passes.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 11 — Verify Lesson 03 separate commits

- **Depends on:** 10. **Coverage:** F6.
- **Read:** Review F6; tools/check.py: learner_commits and 03.commit.separate; Lesson 03.
- **Edit scope:** tools/check.py; tools/selftest.py; lessons/03-git-foundations/README.md.
- **Change:** Inspect relevant commit IDs and changed path groups: hello, profile, notes. Require distinct non-merge commits that each change one required group without another required group. Ignore empty/unrelated commits. Allow separate meaningful follow-up edits as recovery from a bundled start; keep current maintainer exclusions.
- **Focused gate:** Bundled files plus unrelated/empty commits fails. The prescribed workflow and documented additive follow-up recovery pass without rewriting old commits. Pre-check commits count.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 12 — Verify Lesson 04 separate edits

- **Depends on:** 11. **Coverage:** F6.
- **Read:** Review F6; tools/check.py: 04.commits.two-more; Lesson 04.
- **Edit scope:** tools/check.py; tools/selftest.py; lessons/04-everyday-git/README.md.
- **Change:** Require separate non-merge modification commits for profile and notes index after their creation; a shared commit cannot satisfy both. Reuse task 11 metadata only where helpful. Document additive separate edits for recovery.
- **Focused gate:** A single combined edit fails. Two separate edits pass. A bundled mistake followed by separate meaningful edits passes; unrelated/empty commits cannot substitute.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.
