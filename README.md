# Hermes profiles and search patch

## Summary

Seven specialist profiles for Windows and macOS: orchestrator, coder, code-reviewer, research, mcp-ops, ux-ui and ux-ui-critic. Includes settings, role instructions, reusable workflows, selected skill instructions and an optional search patch. The default profile, credentials, memory, sessions, logs and task history are excluded.

Profiles are ordinary folders under `./profiles`. Import copies these files directly; no ZIP or tar archives are used. Native macOS execution has not been tested.

| Profile | Purpose |
| --- | --- |
| `orchestrator` | Plans scoped tasks, delegates work and coordinates verification. |
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

Install Hermes, clone this repository and open a terminal in the repository directory. Use Python 3.10 or newer.

Windows:

```powershell
py -3 .\import_profiles.py --dry-run
py -3 .\import_profiles.py
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

Repeat `--profile` to select several roles. Existing profiles are never overwritten. The script checks for conflicts before copying. If a copy is interrupted, inspect the partially created profile before retrying.

Configure your own provider keys and privacy/routing settings through Hermes. Set up needed MCP connections and missing skill dependencies separately.

Start a fresh session with the orchestrator profile (Windows or macOS):

```bash
hermes -p orchestrator chat
```

The profile flag is `-p` (or `--profile`), not `-u`: use the command above instead of `hermes -u orchestrator`.

Workflow templates are inside each profile under `workflows/lean-execution`. `${HERMES_HOME}` in instructions means the active profile directory. Shell/backend settings use the recipient's installation defaults. Models and reasoning are preserved; adjust unavailable models through Hermes.

Exported iteration limits are 60 for orchestrator/coder, 45 for ux-ui, and 30 for code-reviewer/research/mcp-ops/ux-ui-critic. These cap tool-calling iterations, not elapsed time or cost. Re-export applies these defaults; adjust `agent.max_turns` after export/import if needed. Models and reasoning are never changed by the workflow defaults. Small documentation and non-behavioral edits can stay with the orchestrator; substantive code still gets independent review.

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

For a custom installation, use `-Source`, `-Repo` and `-Python` on Windows, or `--source`, `--repo` and `--python` on macOS. Re-export refreshes files managed by the export manifest and preserves `.git` and unrelated files. Unmanaged file conflicts stop the export. Share the folder through Git.

## Optional search patch

Profile import does not apply or require the patch. Follow `patch/README.md` to check, apply and verify it separately. The original bug is Windows-specific; macOS compatibility is not native-tested. Do not force the patch onto an unsupported Hermes version.
