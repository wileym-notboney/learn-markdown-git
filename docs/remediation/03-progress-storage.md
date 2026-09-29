# Progress storage and migration

Read the [execution rules](../error-remediation-plan.md) and [progress record](progress.md) first. Load only the selected task and its listed inputs. Each task also permits its evidence entry in progress.md and required changelog entries. Paths below are relative to the repository root.

## Task 13 — Reject invalid progress without overwriting it

- **Depends on:** 12. **Coverage:** F9.
- **Read:** Review F9; tools/check.py: load_progress and main.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Validate the existing version-1 schema before use. Distinguish missing file from read error, malformed JSON, wrong types, and unsupported version. Missing initializes; other invalid input exits 2 with an explanation and leaves bytes untouched. Preserve compatible unknown fields.
- **Focused gate:** Test missing, valid, malformed, wrong-shape, negative/wrong-type counters, unsupported-version, and simulated permission errors. Only missing initializes. No invalid existing record is overwritten.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 14 — Write progress atomically

- **Depends on:** 13. **Coverage:** F9.
- **Read:** tools/check.py: save_progress; task 13 validation.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Validate first; write a uniquely named sibling temporary file, flush/fsync, close, then os.replace the target. Remove only this operation’s temporary file on failure. Document a single-writer boundary.
- **Focused gate:** Injected write, flush, and replace failures preserve the previous valid bytes and exit nonzero. Normal save round-trips supported data and leaves no owned temporary file. No concurrency-safety claim is made.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 15 — Validate review imports and report exclusions

- **Depends on:** 14. **Coverage:** F9.
- **Read:** Review F9; tools/review.py: load and main.
- **Edit scope:** tools/review.py; tools/selftest.py; CURRICULUM_REVIEW.md.
- **Change:** Reuse record validation. Identify rejected inputs. Mixed inputs may produce an explicitly partial report but return nonzero; all-invalid input produces no success report. Report the number accepted and rejected.
- **Focused gate:** Valid, invalid, and mixed folders give the specified results. Rejected data is never counted as zero failures or an extra learner.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 16 — Specify the version-2 progress contract

- **Depends on:** 15. **Coverage:** F4 design.
- **Read:** tools/check.py: lesson_record and record_run; tools/review.py: aggregate; Review F4.
- **Edit scope:** docs/remediation/progress-schema.md.
- **Change:** Write a compact field table and transition table before coding. Preserve legacy completion history; define separate assessment/recheck counters, immutable first-pass counts, remote assessment evidence, and unknown values. Decide defaults for uncompleted legacy records and partial historical evidence explicitly. Follow the behavior decisions in the main plan.
- **Focused gate:** Contract covers fresh failure/pass, completed recheck, preview, all, hint, version-1 complete/incomplete migration, remote checkpoint, and repeated migration. Every new field has type/default and every transition says which fields change. This is a document-only gate.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 17 — Implement the version-2 adapter and migration

- **Depends on:** 16. **Coverage:** F4 F9.
- **Read:** Task 16 contract; tasks 13–15 validation/storage.
- **Edit scope:** tools/check.py; tools/review.py; tools/selftest.py; docs/remediation/progress-schema.md only for a documented correction.
- **Change:** Add validation and in-memory adaptation for versions 1 and 2. Only a write-intent operation may persist migration. Before first replacement, preserve original bytes in an exclusive backup; if backup creation fails, leave original untouched and stop. Make repeated migration idempotent.
- **Focused gate:** Completion history is preserved; unknown historical metrics remain unknown. Read-only adaptation creates no files. Failed backup/replacement preserves original data; repeated writes do not overwrite the original backup. Both supported versions can be reviewed.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.
