# Remediation progress

Implementation has not started. This file is the portable execution record; chat history is not required. Update it after each task. Task numbers are sequential; resume at the first unfinished task after verifying its predecessor’s evidence against the checkout.

| Task | Scope | Status | Evidence entry |
|---|---|---|---|
| 01 | Establish the baseline | pending | — |
| 02 | Distinguish test failure from checker failure | pending | — |
| 03 | Isolate temporary course fixtures | pending | — |
| 04 | Add state snapshots for mutation tests | pending | — |
| 05 | Refuse unrelated tracked or staged work | pending | — |
| 06 | Stop after a failed helper command | pending | — |
| 07 | Verify helper success before announcing it | pending | — |
| 08 | Accept all permitted conflict choices | pending | — |
| 09 | Detect incomplete merges through Git | pending | — |
| 10 | Repair scratch recovery instructions | pending | — |
| 11 | Verify Lesson 03 separate commits | pending | — |
| 12 | Verify Lesson 04 separate edits | pending | — |
| 13 | Reject invalid progress without overwriting it | pending | — |
| 14 | Write progress atomically | pending | — |
| 15 | Validate review imports and report exclusions | pending | — |
| 16 | Specify the version-2 progress contract | pending | — |
| 17 | Implement the version-2 adapter and migration | pending | — |
| 18 | Add a read-only preview mode | pending | — |
| 19 | Make all a diagnostic sweep | pending | — |
| 20 | Record immutable first-pass metrics | pending | — |
| 21 | Remove unsupported review conclusions | pending | — |
| 22 | Update prescribed partial-check commands | pending | — |
| 23 | Classify cached remote state accurately | pending | — |
| 24 | Use initial remote evidence during later checks | pending | — |
| 25 | Add a bounded Markdown fence scanner | pending | — |
| 26 | Apply region-aware structural checks | pending | — |
| 27 | Handle inline literals, emphasis, and links | pending | — |
| 28 | Integrate scanner with curriculum validation | pending | — |
| 29 | Run end-to-end and compatibility gates | pending | — |
| 30 | Close the review with recorded evidence | pending | — |

## Evidence entry template

Append one entry per task; replace placeholders with observed facts. Allowed status: pending, running, passed, blocked. “Passed” requires the applicable gates; missing runtime/tool access means blocked or explicitly limited validation, not passed coverage.

```text
Task:
Status:
Starting HEAD and pre-existing changes:
Changed files:
Reproduction before fix: command/case, expected failure, actual result
Focused gate: command/case, expected result, actual result and exit code
Shared gate: commands and exit codes (or document-only reason)
Learner-state preservation: what was compared and result
Implementation reference: commit if created, otherwise current uncommitted files
Limits or unresolved issue:
Next task and exact inputs to read:
```

Keep errors concise and redact credentials or personal learner content. If work stops mid-task, record the partial changes, last failing assertion, and next diagnostic action. Existing unrelated changes stay identified throughout.
