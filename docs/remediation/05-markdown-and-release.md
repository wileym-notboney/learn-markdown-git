# Markdown validation and final evidence

Read the [execution rules](../error-remediation-plan.md) and [progress record](progress.md) first. Load only the selected task and its listed inputs. Each task also permits its evidence entry in progress.md and required changelog entries. Paths below are relative to the repository root.

## Task 25 — Add a bounded Markdown fence scanner

- **Depends on:** 24. **Coverage:** F7.
- **Read:** Review F7; tools/check.py Markdown predicates; tools/validate_curriculum.py: prose_lines.
- **Edit scope:** tools/check.py or tools/markdown_subset.py; tools/selftest.py.
- **Change:** Implement one scanner for supported fenced blocks: backtick/tilde character, opening length, valid closing fence, and unclosed remainder. Expose prose and code-block regions. Do not integrate it everywhere yet or build a complete Markdown parser.
- **Focused gate:** Three/four-backtick fences, tildes, shorter nested example fences, and unclosed fences have explicit region assertions. Existing checks still pass unchanged.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 26 — Apply region-aware structural checks

- **Depends on:** 25. **Coverage:** F7.
- **Read:** Task 25 scanner; Lesson 01 and capstone predicates.
- **Edit scope:** tools/check.py; tools/selftest.py.
- **Change:** Run heading/list/quote/rule/table/checklist predicates on prose regions. Check fenced-code requirements using code regions. Keep link/emphasis integration for task 27.
- **Focused gate:** Whole-profile outer fence fails structural requirements; original profile/capstone pass. Unclosed code cannot leak apparent headings into prose.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 27 — Handle inline literals, emphasis, and links

- **Depends on:** 26. **Coverage:** F7.
- **Read:** Task 25 scanner; profile/CAP_RULES/_broken_in; taught examples.
- **Edit scope:** tools/check.py; tools/markdown_subset.py if created; tools/selftest.py; lessons/01-markdown-basics/README.md; lessons/09-capstone/README.md.
- **Change:** Mask inline-code regions and escaped markup for prose checks while separately detecting inline-code requirements. Accept single-character bold and taught underscore variants. Ignore link-like text in code when checking links. Document limits and retain manual preview.
- **Focused gate:** Literal/escaped emphasis and links cannot satisfy formatting checks; valid taught variants do. A nonexistent path inside a code example does not trigger a broken-link error. All original fixtures pass.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 28 — Integrate scanner with curriculum validation

- **Depends on:** 27. **Coverage:** F7.
- **Read:** tools/validate_curriculum.py: prose_lines and check_links; task 25 scanner.
- **Edit scope:** tools/validate_curriculum.py; tools/selftest.py; tools/markdown_subset.py if needed.
- **Change:** Reuse the bounded scanner where it corrects the validator’s fence handling; retain required section/concept checks. Avoid a validator rewrite.
- **Focused gate:** Four-backtick examples containing three-backtick examples are not treated as prose. Real broken prose links remain detectable. Structural validation still reports every lesson and check.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 29 — Run end-to-end and compatibility gates

- **Depends on:** 28. **Coverage:** release.
- **Read:** All completed task evidence; original review F1–F9; README prerequisites.
- **Edit scope:** tools/selftest.py only for missing integration coverage; docs/remediation/results.md.
- **Change:** Run initialized and clone-based fixtures; fresh, late-checking, resumed, and migrated learners. Repeat all nine reproductions against fixed code. Run supported minimum/current Python and available OS checks; record unavailable combinations explicitly.
- **Focused gate:** Every F1–F9 case has actual expected/observed results. Ordinary walkthroughs pass; no learner state changes. Missing environment coverage is labeled unverified and cannot be reported as a passed gate.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.

## Task 30 — Close the review with recorded evidence

- **Depends on:** 29. **Coverage:** release.
- **Read:** Task 29 results; changed lessons; both changelogs; original review.
- **Edit scope:** docs/remediation/results.md; docs/remediation/progress.md; docs/adversarial-review-2026-09-28.md; both changelogs if missing entries.
- **Change:** Map each finding to its passing regression, implementation reference, and remaining limitations. Audit changed claims against tests, distinguishing machine evidence from manual reflection. Preserve the original findings as historical evidence and append remediation status.
- **Focused gate:** All F1–F9 mappings are complete, standard gate passes, and final diff contains only intended changes. Report fixed-local versus platform-unverified accurately. Do not claim deployment or publication.
- **Done:** focused gate and applicable shared gate pass; evidence and next task are recorded. Stop here unless the user authorized continued execution.
