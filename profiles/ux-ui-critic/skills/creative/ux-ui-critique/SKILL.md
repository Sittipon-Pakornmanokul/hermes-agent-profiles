---
name: ux-ui-critique
description: Use when independently validating UX/UI journeys and designs.
---
# Evidence-backed UX/UI critique

## Inputs
Original brief, user/task goals, artifact paths or authorized local prototype URL, target devices, constraints, acceptance criteria and report directory. If missing, state assumptions and limits rather than inventing research. Read requirements before the designer's defense of their choices.

## Checks
- Journey: entry point, orientation, next step, task completion, feedback, exits, backtracking and resumption.
- Information architecture: understandable labels, grouping, hierarchy, discovery and consistency.
- Friction and trust: unnecessary forms/decisions, premature signup, surprise costs, misleading choices, destructive actions and informed consent. Fewer clicks is not always better.
- Recovery: invalid input, network failure, empty results, unavailable options, duplicate submission, preserving user input and retry/cancel paths.
- Accessibility: keyboard order and operation, focus visibility/restoration, semantic controls, form labels/errors, contrast, zoom/reflow, touch targets and reduced motion. Report tested WCAG criteria and limits; automated checks do not prove conformance.
- Responsive behavior: examine actual mobile and desktop layouts, content priority and overflow.

## Evidence collection
Inspect files and use available browser tools to walk scoped interactions. Record viewport, screen/URL, actions, expected/actual outcomes and screenshot paths. Do not perform destructive actions or change real records without explicit authorization. Browser-exec screenshots can be inspected directly; legacy browser_vision names may not exist. Do not publish local artifacts to get a preview.
For static documents, label conclusions as specification review; do not claim keyboard/interaction tests. Calculate contrast with tools rather than guessing.

## Findings and verdict
Each finding: ID, severity (critical/high/medium/low), affected user task, location, evidence, expected behavior, proposed change, confidence and retest criterion. Separate observed failure, missing requirement, testable hypothesis and preference. Avoid duplicate findings and cosmetic preference disguised as a usability defect.
Verdict: not ready for task-blocking critical/high issues; insufficient evidence where essential coverage is absent; otherwise ready with caveats or revisions. Explain unresolved risks in plain language. No arbitrary quality scores or unsubstantiated optimized-UX claims.
Include coverage, untested areas and representative-user test tasks. Let users attempt tasks without coaching; record completion, wrong turns, errors and comprehension. Synthetic role-play is not user research. For production propose task success, abandonment, error and support metrics, with no invented baselines.
Return findings to the orchestrator; designer makes revisions. Re-review against stable finding IDs and report resolved, unresolved and new issues. Preserve design files unchanged.
