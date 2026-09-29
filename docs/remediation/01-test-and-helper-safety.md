# Test infrastructure and helper safety

Read the [execution rules](../error-remediation-plan.md) and [progress record](progress.md) first. Load only the selected task and its listed inputs. Each task also permits its evidence entry in progress.md and required changelog entries. Paths below are relative to the repository root.

## Task 01 — Establish the baseline

- **Depends on:** none. **Coverage:** baseline.
- **Read:** Review execution rules; CONTRIBUTING.md; tools/selftest.py; current Git state.
- **Edit scope:** docs/remediation/progress.md.
- **Change:** Run the shared baseline gate. Record Python/Git versions, HEAD, pre-existing changes, and whether a progress file exists. Inspect only progress metadata needed to identify an active exercise.
- **Focused gate:** All baseline commands have recorded exit codes. Existing failures are identified before any implementation; this task changes no code.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 02 — Distinguish test failure from checker failure

- **Depends on:** 01. **Coverage:** tests.
- **Read:** tools/selftest.py: Learner.check.
- **Edit scope:** tools/selftest.py.
- **Change:** Require exit 0 for pass and exit 1 for an unmet lesson; reject tracebacks even if their exit code is 1. Add focused checks of this test helper using controlled subprocess results. Do not redesign checker error handling here.
- **Focused gate:** A result with exit 2 and a traceback with exit 1 both fail the test harness; a normal lesson failure with exit 1 is accepted. Existing walkthrough passes.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 03 — Isolate temporary course fixtures

- **Depends on:** 02. **Coverage:** tests.
- **Read:** tools/selftest.py: setup and subprocess calls.
- **Edit scope:** tools/selftest.py.
- **Change:** Copy an explicit list of curriculum inputs into temporary fixtures, create only required workspace placeholders, and isolate Git configuration using a subprocess environment. Keep hook/signing/identity overrides local to fixtures. Exclude learner and agent data.
- **Focused gate:** A source-only sentinel in workspace and a local agent-data sentinel are absent in the fixture. Tests work with deliberately conflicting parent Git configuration. Real user configuration is unchanged.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 04 — Add state snapshots for mutation tests

- **Depends on:** 03. **Coverage:** tests.
- **Read:** tools/selftest.py: Learner helpers.
- **Edit scope:** tools/selftest.py.
- **Change:** Add a fixture-only snapshot helper for HEAD, refs, semantic index entries, staged diff, and file bytes. Compare semantic state, not Git index file bytes.
- **Focused gate:** An unchanged fixture compares equal; changing each tracked state category is detected. Scratch/untracked fixture file changes are detected too.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 05 — Refuse unrelated tracked or staged work

- **Depends on:** 04. **Coverage:** F1.
- **Read:** Review F1; tools/setup_conflict.py: main; Lesson 06.
- **Edit scope:** tools/setup_conflict.py; tools/selftest.py; lessons/06-merge-conflicts/README.md.
- **Change:** Require a clean tracked working tree and index before setup. Allow unrelated untracked files. Before committing, require only favorites.md in the staged path set. Preserve current branch/template checks.
- **Focused gate:** Staged additions, modifications, deletions, partial staging, and unstaged tracked edits are refused without semantic state changes. An untracked scratch file survives successful setup unchanged.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 06 — Stop after a failed helper command

- **Depends on:** 05. **Coverage:** F2.
- **Read:** Review F2; tools/setup_conflict.py: git and make_branch.
- **Edit scope:** tools/setup_conflict.py; tools/selftest.py.
- **Change:** Check Git read and mutation return codes. Stop on the first failure, include useful stderr, and report actual state. Use standard-library mocks for individual failure paths plus a real rejecting pre-commit hook in a fixture.
- **Focused gate:** Failure at branch creation, add, commit, or return switch exits nonzero and prevents later mutations. A failed preflight query is not interpreted as empty successful output.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 07 — Verify helper success before announcing it

- **Depends on:** 06. **Coverage:** F1 F2.
- **Read:** tools/setup_conflict.py; tasks 05–06 tests.
- **Edit scope:** tools/setup_conflict.py; tools/selftest.py; lessons/06-merge-conflicts/README.md.
- **Change:** Verify exactly one expected practice commit, only favorites changed, return to original main commit, clean index, and original favorites contents on main. Print success only when these conditions hold. Keep partial state on failure and explain recovery.
- **Focused gate:** Normal setup satisfies every postcondition. A failed final switch reports the existing practice commit and actual branch, never success. All task 05–06 cases pass.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.
