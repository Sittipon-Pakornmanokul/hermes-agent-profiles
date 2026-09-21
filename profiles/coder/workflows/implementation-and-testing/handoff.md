# Bounded handoff — fill applicable fields only
- Task ID / role / decision or goal:
- Repository or source root (absolute); branch/worktree/base commit if applicable:
- Relevant instructions, files, original evidence and freshness/version (for fixes: available failing line, traceback and repro path; distinguish verified observations from hypotheses, without requiring duplicate investigation):
- Owned files/targets; non-goals; user changes to preserve:
- Acceptance criteria and required checks:
- Original user request and exact authorization; authorized side effects / privacy boundaries (task authorization never bypasses a runtime human-approval gate):
- Out-of-scope findings needing human approval (report only; do not implement or delegate fixes):
- Call/time budget and delivery reserve — advisory checkpoint by default; label a cap HARD only when the launcher enforces it; distinguish work time from human-approval wait time:
- Checkpoints / draft deadline / delivery reserve:
- Stop or escalate when (acceptance met; two attempts without new evidence; scope change; human approval required):
- Report, full-log and per-run receipt paths (ask for raw evidence — diff hunk + test summary lines — not narrative reports):
- Prior findings for repair, if any:
Read the role supplement; include only relevant context, not entire histories. A budget expiry means partial/blocked, never accepted. No secrets in handoffs.

Unattended workers must report APPROVAL REQUIRED with the exact action, target and reason. The orchestrator asks the human and waits; neither worker nor orchestrator may approve on their behalf or bypass the blocked action. Optional improvements stay deferred until explicitly authorized.
- Check evidence: command, result, log path, tested revision/file hashes; what invalidates it:
- Continuation only: unfinished checklist; completed checks still valid; safe next milestone boundary:
