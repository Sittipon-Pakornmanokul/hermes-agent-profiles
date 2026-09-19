---
name: orchestrating-implementation-review-loop
description: Use when a worker profile implements code you must verify.
---

# Orchestrating an implementation + review loop

Delegate implementation to a worker profile, then verify it yourself and with an independent reviewer, then run bounded repair rounds.

## Handoff per round
- One handoff file per round (never a chain of chat messages): goal, absolute repo path, no-VCS/base notes, spec file pointers, file ownership, exact acceptance checks, non-goals, expected report path.
- Include environment facts the worker cannot discover: prepared venv, how to run tests, host quirks (MSYS paths, native-tool path form for python/git/rg).
- Workers do not inherit the conversation; repeat shared context in every handoff.
- Launch: `hermes -p <profile> chat -q 'Read the handoff at <abs path> and execute it.'` from the repo dir, with `background=true` + `notify=true`.
- Await via completion notification or `process_manage wait` — never shell `sleep` loops.

## Verify before you believe
- Never relay a worker's summary as fact: rerun the suite, run the CLI end-to-end yourself, inspect artifacts (records, logs, workspace bytes).
- For pipelines with a decision/execution binding, check chain of custody programmatically: every execution references a persisted decision, hashes match, no unmatched intents.
- Spawn a fresh round for leftovers instead of editing worker code yourself; keep one writer per file.

## Independent review handoff
- Give the reviewer acceptance criteria, artifact paths, the worker's report (labelled a claim) and your own verified evidence; state "read-only, report only, no fixes".
- Require per-criterion verdicts, findings with `file:line` + reproduction + severity + retest criterion, and guard-removal mutation spot-checks in a scratch copy outside the project.
- Ask for coverage limits: what could not be tested on this host.

## Load-bearing tests
- A test that still passes with its guard neutralised is a defect even when the guard works: rewrite so only that guard can reject (put the trigger input where no other validation fires first).
- Verify the fix with your own mutant copy: copy the tree, neutralise the exact guard line, assert the test now fails, restore.
- Prefer a targeted mutant check over another full review round when the change is test/doc-only.

## Bounded repair rounds
- Fix only findings inside the approved batch; leave accepted items documented with rationale, not re-engineered.
- Re-review only the touched guards, then re-run the full suite plus the end-to-end run.
- Report real numbers from real runs and state what remains unverified.
