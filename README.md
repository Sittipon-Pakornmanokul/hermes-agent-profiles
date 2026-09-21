# Hermes profiles and search patch

Bundle version: **0.1.0**. See [CHANGELOG.md](CHANGELOG.md) for release changes.

## Summary

Seven specialist profiles for Windows and macOS: orchestrator, coder, code-reviewer, research, mcp-ops, ux-ui and ux-ui-critic. Includes settings, role instructions, reusable workflows, selected skill instructions and an optional search patch. The default profile, credentials, memory, sessions, logs and task history are excluded.

Profiles are ordinary folders under `./profiles`. Import copies these files directly; no ZIP or tar archives are used. Native macOS execution has not been tested.

| Profile | Purpose |
| --- | --- |
| `orchestrator` | Handles small tasks directly; delegates substantial work and coordinates necessary review. |
| `coder` | Implements features, fixes bugs and runs relevant tests. |
| `code-reviewer` | Independently reviews code for correctness, security and regressions. |
| `research` | Investigates technical questions and compares options with cited evidence. |
| `mcp-ops` | Reads and updates connected business systems, then verifies authorized changes. |
| `ux-ui` | Designs user journeys, interfaces and prototypes for developer handoff. |
| `ux-ui-critic` | Independently reviews designs for usability, accessibility and user goals. |

## Install Hermes Agent

Start with a fresh, minimal Hermes setup. Configure your own model-provider credentials, then import these profiles before adding optional plugins, MCP servers, messaging integrations or custom instructions. This makes the shared setup easier to reproduce and troubleshoot; there is no need to restore old memory or sessions.

Download and run the Windows or macOS installer from the [official Hermes website](https://hermes-agent.nousresearch.com/). It installs both the desktop app and the `hermes` command. The macOS installer supports Apple Silicon.

For a command-line-only setup, follow the [official installation instructions](https://hermes-agent.nousresearch.com/docs/getting-started/installation), or run:

Windows PowerShell:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

macOS:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Reopen your terminal after installation and check that `hermes --help` works.

These profiles use OpenRouter for models and Exa for web search/extraction. Set up your own OpenRouter credentials and required account privacy policy (the profiles require ZDR). For web tasks, configure your own `EXA_API_KEY` in the active profile's private `.env`, or select and configure another supported search/extraction backend through Hermes. An OpenRouter key alone does not configure Exa. Never commit `.env` files. MCP profiles also need your own connections; service-specific skills are optional.

## Import profiles

Install Hermes, clone this repository and open a terminal in the repository directory. Use Python 3.10 or newer with PyYAML (already included in the Hermes interpreter).

Windows:

```powershell
.\Import-Profiles.ps1 -DryRun
.\Import-Profiles.ps1
```

macOS:

```bash
python3 ./import_profiles.py --dry-run
python3 ./import_profiles.py
```

The source defaults to `./profiles` in your current directory. The destination is Hermes' profile storage, normally `%LOCALAPPDATA%/hermes/profiles` on Windows or `$HOME/.hermes/profiles` on macOS. When available, the script uses Hermes' own root resolver. For a custom installation, pass `--hermes-home "/path/to/hermes-home"`; check the displayed destination with `--dry-run` first.

To import only the coder profile from the current directory:

Windows:

```powershell
py -3 .\import_profiles.py --profile coder
```

macOS:

```bash
python3 ./import_profiles.py --profile coder
```

Repeat `--profile` to select several roles. Existing profiles require `--update` (Windows: `.\Import-Profiles.ps1 -Update -DryRun`, then `.\Import-Profiles.ps1 -Update`). The Windows launcher finds Hermes' Python automatically; use `-Python` for a custom interpreter. Preview with `python import_profiles.py --update --dry-run`, then apply with `python import_profiles.py --update`. Changed files are backed up under the destination Hermes home's `backups/profile-import-*` directory. Portable YAML settings overlay the destination's settings, retaining host-only keys omitted by export, such as connections and local shell configuration. Credentials and runtime data are not imported. Previously imported portable files removed from the bundle are removed on the next update; untracked files are preserved. The script checks all selected profiles before writing. A copy interruption is not a transaction rollback; inspect the printed destination and backup before retrying.

Configure your own provider keys and privacy/routing settings through Hermes. Set up needed MCP connections and missing skill dependencies separately.

Start a fresh session with the orchestrator profile (Windows or macOS):

```bash
hermes -p orchestrator chat
```

The profile flag is `-p` (or `--profile`), not `-u`: use the command above instead of `hermes -u orchestrator`.

Workflow templates are inside each profile under its named `workflows/<workflow-name>` folder (see below). `${HERMES_HOME}` in instructions means the active profile directory. Shell/backend settings use the recipient's installation defaults. Models and reasoning are preserved; adjust unavailable models through Hermes.

Each profile has its own `workflows/<workflow-name>/workflow.md`, linked from its SOUL.md. Workflows cover role-specific execution, handoffs, acceptance and decision-layer boundaries. They do not enable a decision engine. Models, reasoning and iteration limits come from the installed profile and are preserved during export; export no longer rewrites instructions or applies workflow defaults. For a deliberate workflow refresh, run `python update_profile_workflows.py --hermes-home /path/to/hermes-home`; it backs up changed workflow and SOUL files without changing config.yaml.

If a non-interactive worker needs approval, let it exit and open the same profile interactively in the project directory with `hermes -p coder --resume SESSION_ID`, using its actual profile and session ID. The human answers any approval prompt there. If no ID is available, run `hermes -p coder chat` and supply its handoff and partial results. Do not run concurrent writers or repeatedly restart a blocked worker. Manual approvals remain enabled.

## Export profiles

Run from the directory where you want the exported files.

Windows:

```powershell
.\Export-Profiles.ps1
```

macOS:

```bash
bash ./export-profiles.sh
```

Both write directly into the current directory. If the scripts are elsewhere, invoke their paths without changing directory. Use `-Destination` on Windows or `--dest` on macOS only to override the destination.

Export requires the source installation's Hermes Python and all seven specialist profiles. The Windows launcher detects `venv/Scripts/python.exe` or `.venv/Scripts/python.exe`. The macOS launcher detects `.venv/bin/python` or `venv/bin/python` under the Hermes source checkout.

For a custom installation, use `-Source`, `-Repo` and `-Python` on Windows, or `--source`, `--repo` and `--python` on macOS. Re-export reads each matching installed profile and its own workflow templates, then refreshes files managed by the export manifest and preserves `.git` and unrelated files. Obsolete manifest-managed profile files are removed only if they still match their previous checksum; local edits to obsolete files stop export. Workflows include Markdown instructions and empty JSON/YAML templates; runs, receipts, ledgers and reports are excluded. Import direction is this directory to Hermes; export direction is Hermes to this directory. Both Python commands honor Hermes root resolution, including a custom HERMES_HOME and active-profile homes. Unmanaged file conflicts stop the export. Share the folder through Git.

## Optional search patch

Profile import does not apply or require the patch. Follow `patch/README.md` to check, apply and verify it separately. The original bug is Windows-specific; macOS compatibility is not native-tested. Do not force the patch onto an unsupported Hermes version.

## Workflow names


| Profile | Workflow | Folder |
| --- | --- | --- |
| `orchestrator` | Task Orchestration | `task-orchestration` |
| `coder` | Implementation and Testing | `implementation-and-testing` |
| `code-reviewer` | Independent Code Review | `independent-code-review` |
| `research` | Evidence and Decision Research | `evidence-and-decision-research` |
| `mcp-ops` | Verified Service Operations | `verified-service-operations` |
| `ux-ui` | UX Design and Handoff | `ux-design-and-handoff` |
| `ux-ui-critic` | UX and Accessibility Review | `ux-accessibility-review` |

Historical run artifacts retain their original locations. Imports and exports carry each profile's named templates and current SOUL references.

## Token efficiency

All seven roles have tailored rules for concise tool output, evidence freshness and focused verification. Start fresh workers after accepted milestones; preserve unresolved debugging context. Continuations carry unfinished work and still-valid checks, not full history. Keep required independent reviews and business read-back. Start new sessions to load changed instructions. Token savings have not been benchmarked.

## Versioning

`VERSION` identifies this bundle, not Hermes or its models. Use MAJOR.MINOR.PATCH: major for incompatible changes, minor for compatible features, patch for fixes/documentation. Update VERSION, README.md and CHANGELOG.md together. Exports include the bundle version and checksums in MANIFEST.json. Preview profile updates with --update --dry-run before applying them; retain your own credentials and review model/reasoning changes before import.

## Focused execution

Small, clear tasks run directly without a mandatory coder/reviewer round. Substantial or specialist
work is delegated; consequential changes and explicit project requirements retain independent review.
Tests target the change first, with required broader checks once the implementation is stable.
Handoffs use a short prompt unless a durable file is needed. Kanban, measurement ledgers and repeated
status reports are not prerequisites. Workers use completion notifications or waits of at most
60 seconds, with no fixed sleep loops. Models, reasoning and runtime approval settings are unchanged.
Start a new profile session after applying instructions; do not expect an existing session to reload
its system prompt. These are instruction improvements, not measured speed guarantees.
