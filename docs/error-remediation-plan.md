# Provider-neutral incremental remediation plan

Status: proposed; no implementation has started. This replaces the previous 11 broad increments with 30 bounded tasks for a mid-tier coding model. It addresses F1–F9 in the [adversarial review](adversarial-review-2026-09-28.md), originally reviewed at `c9c0161`.

The plan requires repository file access, Python, Git, and a way to run commands. It requires no provider-specific tools, memory service, plugins, subagents, or paid APIs. A chat-only model can produce patches and test instructions, but an executor must run the gates before a task can be marked passed. Provider neutrality is a design property; execution across different models has not been benchmarked.

## Start or resume

1. Read this file and [progress.md](remediation/progress.md).
2. Inspect `git status --short` and `git log --oneline -5`; preserve pre-existing edits. Read local repository instructions and `CONTRIBUTING.md`.
3. Select the first unfinished task. Read only that task's section, listed source files/functions, and relevant F-number from the review. Paths in task cards are repository-relative.
4. Verify predecessor evidence against the current checkout. A missing or changed prerequisite needs revalidation, not trust in a previous model's summary.
5. Execute one task, pass its gates, and append evidence. With authorization to continue, proceed sequentially to the next task; otherwise hand off the recorded state. Small tasks do not require repeated permission questions.

Each task has one main behavior to change. If it needs unrelated production-file changes or a new architecture decision, record the reason and split the task before expanding scope. Follow the dependency order below; parallel execution is unnecessary.

## Task index

| Order | Open this packet only when working in this range | Outcome |
|---|---|---|
| 01–07 | [Test and helper safety](remediation/01-test-and-helper-safety.md) | Reliable tests; safe conflict setup; truthful Git error handling |
| 08–12 | [Lesson correctness](remediation/02-lesson-correctness.md) | Valid conflict choices, working recovery, separate-commit checks |
| 13–17 | [Progress storage](remediation/03-progress-storage.md) | Validated records, atomic writes, explicit schema and migration |
| 18–24 | [Assessment and remotes](remediation/04-assessment-and-remotes.md) | Honest metrics and cached remote-state checks |
| 25–30 | [Markdown and final evidence](remediation/05-markdown-and-release.md) | Region-aware Markdown checks and complete regression evidence |

Finding coverage: F1 → 05/07; F2 → 06/07; F3 → 08/09; F4 → 16–22; F5 → 23/24; F6 → 11/12; F7 → 25–28; F8 → 10; F9 → 13–17. Tasks 29–30 verify and document all findings.

## Shared task procedure

1. Inspect the specified code and existing tests before editing.
2. For an error fix, reproduce the defect in a temporary fixture. Record the failing assertion on the old behavior, then implement the smallest fix. For new infrastructure, demonstrate its own positive and negative cases instead of inventing an old defect.
3. Run the focused tests listed in the task. Add focused regressions to the existing self-test suite so later models run them automatically. Keep setup fixtures and assertions explicit; prefer small functions over a new test framework.
4. Run the shared gate below, review the intended diff and learner-state preservation, and update the progress record. Curriculum changes require both changelogs, as specified by `CONTRIBUTING.md`.
5. Mark passed only after observed success. A patch, plausible explanation, or simulated command output is not execution evidence.

Use one coherent change per task. Commits are optional unless the user requests them; task progress can refer to reviewed uncommitted files. Do not commit, publish, or push merely to advance the checklist.

## Shared validation gate

Run from the repository root with the verified Python interpreter. The examples use `python3`; use `python` where appropriate and record which interpreter ran.

```text
python3 tools/validate_curriculum.py
python3 tools/selftest.py
python3 tools/review.py --selfcheck
git diff --check
```

All must exit 0 after every implementation task. Record exit codes; a traceback is a failure even if a test expected nonzero output. Inspect newly created files separately because ordinary `git diff` omits untracked files. Document-only tasks validate content, links, and consistency; they need no learner simulation unless they change executable lesson instructions.

If a baseline gate already fails, record and isolate that failure before claiming any subsequent gate passes. If an interpreter/platform is unavailable, label that coverage unverified. Local completion can be reported separately from an unpassed compatibility gate.

## Fixed behavior decisions

These decisions keep later models from redesigning the course independently. Task 16 supplies field names and transition details, not a new product direction.

- **CLI:** `check.py NN` assesses an unfinished lesson; on a completed lesson it records a recheck. `check.py --preview NN` and `check.py all` evaluate without writing progress, backups, or migrations. `all` evaluates all ten lessons. No-argument mode keeps selecting the earliest unfinished lesson. Invalid usage and handled operational errors return 2; unmet exercise requirements return 1; successful evaluation returns 0.
- **History:** preserve existing completion records. A failing recheck reports the current defect but does not erase historical completion. First-pass counters freeze at first assessment success; legacy values that cannot be reconstructed remain unknown.
- **Metrics:** previews and rechecks do not drive assessment-difficulty findings. Remove inferred learning duration and abandonment; existing timestamps and lesson-record presence cannot establish either.
- **Storage:** validate before use/write. Preserve invalid input. Migrate only on write intent, with an exclusive original-data backup and atomic replacement. Read-only commands can adapt valid old data in memory. Single-writer integrity is in scope; concurrent writers are not certified.
- **Remotes:** assess initial equality against cached `origin/main`, never by contacting a server. Save the verified equal-ref commit on successful assessment. Later descendants may preserve historical completion while showing current cached state separately. Missing/stale evidence remains unknown. Actual clone/pull actions require manual learner verification.
- **Recovery:** use additive commits and content-preserving instructions. Existing learner history is not rewritten to satisfy a checker.
- **Markdown:** support the taught syntax subset using the standard library. Distinguish prose from fenced/inline literals; retain rendered-preview verification. Full CommonMark compliance is outside this change.

## Learner protection and scope

Actual learner-owned `workspace/`, `GLOSSARY.md`, and `.learning/` remain untouched by implementation and tests. Exercise mutations occur only in temporary fixtures. Inspect current progress read-only when deciding whether a lesson change would invalidate active work; prefer additive changes or defer activation in that case.

Preserve unrelated working-tree changes. Never run reset, rebase, amend, force-push, or delete learner branches to make tests pass. Failure recovery reports the partial state; it does not silently restore or unstage user work. Tests keep Git hooks and configuration local to their fixtures.

Keep standard-library-only tooling. Runtime optimization, extra frameworks, baseline-provenance redesign, unrelated lesson expansion, and external service integration are deferred. Fix correctness before measuring whether repeated Git queries need optimization.

## When a gate fails

Stop promotion of the current task; continue diagnosing it within scope. Read the exact error, identify whether it is implementation, fixture, environment, or an existing failure, then rerun the focused case after a justified change. After two attempts with the same unexplained failure, record what each attempt ruled out and the next diagnostic experiment before trying again. Do not repeat a command without new evidence or a change relevant to its failure.

If progress requires missing access or a product decision outside this contract, mark blocked with the specific missing input and hand off. Ordinary implementation choices within the task do not need approval. Preserve the last error, partial diff, and next action in progress.md so another model can resume.

For rollback, revert only the focused implementation change when authorized; preserve learner history. After migration, retain both migrated data and backup. Do not run an old writer against a new schema or automatically restore a stale backup; fix forward or provide an explicitly compatible export.

## Portable execution prompt

Copy this into any coding assistant with this repository available:

```text
Execute the next unfinished task in docs/error-remediation-plan.md.
Read that file, docs/remediation/progress.md, repository instructions,
and only the selected task's inputs. Preserve existing user changes.
Implement just that task, reproduce the relevant failure, and run its
focused and shared validation gates. Record actual evidence and the next
task in progress.md. Do not claim tests ran unless you executed them.
Stop after this task unless I have authorized continued execution.
If blocked, record partial state and the precise missing input.
```

## Completion

The errors are fixed only when each F1–F9 has a passing regression plus a compatible normal workflow, migration evidence preserves original records, and task 30 links the evidence. State runtime/platform limits explicitly. This planning update does not itself fix any repository error.
