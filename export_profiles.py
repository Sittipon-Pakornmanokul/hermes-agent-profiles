"""Export a deliberately limited, sanitized Hermes profile bundle. Never copies state."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

import yaml
from profile_sync import default_home, workflow_file, checked_target, portable_file

ROLES = ('orchestrator', 'coder', 'code-reviewer', 'research', 'mcp-ops', 'ux-ui', 'ux-ui-critic')
# These sections contain portable behavior/settings; machine integrations stay out.
SECTIONS = {'model', 'agent', 'auxiliary', 'provider_routing', 'approvals', 'delegation',
            'tool_loop_guardrails', 'compression', 'prompt_caching', 'display', 'web',
            'streaming', 'code_execution', 'smart_model_routing', 'skills', 'curator',
            'platform_toolsets', '_config_version', 'session_reset', 'telemetry'}
PRIVATE_KEY = re.compile(r'(api.?key|password|secret|credential|authorization|access_token|refresh_token|auth_token|headers|^env$|^cwd$|^path$|directory|volumes|mounts|account|login|personalities)', re.I)
PUBLIC_ENDPOINTS = {'https://openrouter.ai/api/v1', 'https://api.openai.com/v1', 'https://api.anthropic.com'}
SKILLS = (
    'autonomous-ai-agents/hermes-agent',
    'autonomous-ai-agents/orchestrating-implementation-review-loop',
    'autonomous-ai-agents/role-profile-model-selection',
    'research/research-and-rag', 'research/grounded-citations',
    'creative/ux-ui-critique', 'creative/design-md',
    'software-development/codebase-inspection',
    'software-development/requesting-code-review',
    'software-development/systematic-debugging',
    'software-development/test-driven-development', 'devops/sdlc-review',
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source_home = default_home()
    parser.add_argument('--source', type=Path, default=source_home)
    parser.add_argument('--dest', type=Path, default=Path.cwd(), help='Export into this directory (default: current working directory)')
    parser.add_argument('--repo', type=Path, help='Hermes source checkout if not SOURCE/hermes-agent')
    args = parser.parse_args()
    source = args.source.expanduser().resolve(strict=True)
    dest = args.dest.expanduser().resolve()
    repo = (args.repo or source / 'hermes-agent').expanduser().resolve(strict=True)
    if dest == source or dest.is_relative_to(source) or source.is_relative_to(dest):
        raise SystemExit('Export destination must be separate from the Hermes home.')
    previous_manifest = dest / 'MANIFEST.json'
    managed = set()
    if previous_manifest.is_file():
        previous = json.loads(previous_manifest.read_text(encoding='utf-8'))
        if previous.get('portable_settings_only') is not True or not isinstance(previous.get('files'), dict):
            raise SystemExit('Destination contains an unrecognized manifest; not overwritten.')
        managed = set(previous['files']) | {'MANIFEST.json'}
    sys.path.insert(0, str(repo))
    from agent.redact import redact_sensitive_text
    from dotenv import dotenv_values

    homes = [(role, source / 'profiles' / role) for role in ROLES]
    # Load secret values only for exact-match removal. Never copy/print their files or values.
    secret_values = set()
    for home in [source] + [home for _, home in homes]:
        envfile = home / '.env'
        if envfile.is_file():
            for key, value in dotenv_values(envfile).items():
                if value and len(value) >= 8 and re.search(r'KEY|TOKEN|SECRET|PASSWORD|AUTH', key, re.I):
                    secret_values.add(value)

    def clean_text(text):
        for value in sorted(secret_values, key=len, reverse=True):
            text = text.replace(value, '[REDACTED]')
        text = redact_sensitive_text(text, force=True)
        # Instructions refer to the recipient's active profile, never the exporter's home.
        text = re.sub(r'/Users/[^/\s]+/\.hermes', '${HERMES_HOME}', text)
        text = re.sub(r'[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/]AppData[\\/]Local[\\/]hermes', '${HERMES_HOME}', text, flags=re.I)
        text = re.sub(r'\$\{HERMES_HOME\}[^\s`\"\)]+', lambda m: m.group().replace('\\', '/'), text)
        text = re.sub(r'[A-Za-z]:[\\/]Users[\\/][^\\/\s]+', '<USER_HOME>', text, flags=re.I)
        text = re.sub(r'/Users/[^/\s]+', '<USER_HOME>', text)
        text = re.sub(r'(?i)\b[A-Z]:[\\/]workspace[\\/][^\s`\"\)]+', '<PROJECT_PATH>', text)
        text = re.sub(r'(?i)https?://[^\s/]+\.(?:atlassian\.net|ngrok[^/\s]*)[^\s`\"]*', '<BUSINESS_SERVICE_URL>', text)
        return text

    def scrub(value):
        if isinstance(value, dict):
            out = {}
            for key, item in value.items():
                if PRIVATE_KEY.search(str(key)):
                    continue
                if str(key) in ('base_url', 'url', 'endpoint') and item not in PUBLIC_ENDPOINTS:
                    continue
                out[key] = scrub(item)
            return out
        if isinstance(value, list):
            return [scrub(item) for item in value]
        if isinstance(value, str):
            return clean_text(value)
        return value

    asset_root = Path(__file__).resolve().parent
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Only sanitized material is staged; no full profile clone is ever made.
    with tempfile.TemporaryDirectory(prefix='hermes-share-', dir=dest.parent) as staging:
        stage = Path(staging)
        def write(relative, text):
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(clean_text(text), encoding='utf-8', newline='\n')

        for name, home in homes:
            checked_target(source, home.relative_to(source))
            config_path = checked_target(home, 'config.yaml')
            if not config_path.is_file():
                raise SystemExit(f'Missing config for {name}; no completed export produced.')
            config = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
            shared = scrub({k: v for k, v in config.items() if k in SECTIONS})
            # Retain timing preferences, but do not export source-specific shells or containers.
            if isinstance(config.get('terminal'), dict):
                shared['terminal'] = {k: v for k, v in config['terminal'].items() if k in {'timeout', 'lifetime_seconds'}}
            relative = Path('profiles') / name
            write(relative / 'config.yaml', yaml.safe_dump(shared, sort_keys=False, allow_unicode=True))
            soul = checked_target(home, 'SOUL.md')
            if soul.is_file():
                write(relative / 'SOUL.md', soul.read_text(encoding='utf-8'))
            metadata = checked_target(home, 'profile.yaml')
            if metadata.is_file():
                meta = yaml.safe_load(metadata.read_text(encoding='utf-8')) or {}
                write(relative / 'profile.yaml', yaml.safe_dump(scrub({k:meta[k] for k in ('description', 'description_auto') if k in meta}), sort_keys=False))
            workflow = checked_target(home, 'workflows')
            for template in sorted(workflow.rglob('*')):
                workflow_relative = template.relative_to(workflow)
                checked_target(workflow, workflow_relative)
                if template.is_file() and workflow_file(workflow_relative):
                    write(relative / 'workflows' / workflow_relative, template.read_text(encoding='utf-8'))
            skill_root = home / 'skills'
            for skill in SKILLS:
                root = checked_target(skill_root, skill)
                if not (root / 'SKILL.md').is_file():
                    continue
                for path in root.rglob('*'):
                    if not path.is_file() or path.is_symlink() or path.suffix.lower() != '.md':
                        continue
                    if not path.resolve().is_relative_to(root.resolve()):
                        continue
                    if any(part.lower() in {'runs', 'logs', 'memory', 'sessions', 'cache', 'reports'} for part in path.relative_to(root).parts):
                        continue
                    write(relative / 'skills' / skill / path.relative_to(root), path.read_text(encoding='utf-8'))

        for filename in ('export_profiles.py', 'workflow_defaults.py', 'profile_sync.py', 'update_profile_workflows.py', 'import_profiles.py', 'Import-Profiles.ps1', 'Export-Profiles.ps1', 'export-profiles.sh', 'README.md', 'VERSION', 'CHANGELOG.md', '.gitattributes'):
            (stage / filename).write_text((asset_root / filename).read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
        (stage / 'export-profiles.sh').chmod(0o755)
        for filename in ('apply_patch.py', 'verify_search.py', 'search-patterns.patch', 'README.md'):
            target = stage / 'patch' / filename
            target.parent.mkdir(exist_ok=True)
            target.write_text((asset_root / 'patch' / filename).read_text(encoding='utf-8'), encoding='utf-8', newline='\n')

        # Check every plain-text file before publishing the export.
        files = sorted(p for p in stage.rglob('*') if p.is_file())
        for path in files:
            content = path.read_text(encoding='utf-8')
            if any(value in content for value in secret_values):
                raise SystemExit('Known credential detected; export aborted without a published bundle.')
            if re.search(r'\bsk-(?:or-v1-)?[A-Za-z0-9_-]{20,}', content) or re.search(r'(?m)^-----BEGIN [A-Z ]*PRIVATE KEY-----$', content):
                raise SystemExit(f'Credential-shaped content detected in {path.relative_to(stage)}; export aborted.')
            if path.suffix == '.yaml':
                yaml.safe_load(content)
        manifest = {
            'bundle_version':(asset_root / 'VERSION').read_text(encoding='utf-8').strip(),
            'created_utc':datetime.now(timezone.utc).isoformat(),
            'profile_count':len(ROLES), 'portable_settings_only':True,
            'profile_targets':['Windows', 'macOS'], 'native_macos_tested':False,
            'excluded':['.env', 'auth/OAuth files', 'memory', 'sessions', 'databases', 'logs', 'caches', 'workflow runs/reports', 'MCP server connections', 'gateway routes', 'plugin state/code', 'machine paths/mounts', 'command allowlists'],
            'notes':['Only allowlisted skill Markdown instructions are included; install missing skill dependencies separately.', 'Each profile exports its own workflow templates; runtime history is excluded.', 'Terminal backend/shell/container settings omitted for portability; models and reasoning preserved.'],
            'files':{str(p.relative_to(stage)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        }
        write('MANIFEST.json', json.dumps(manifest, indent=2))
        # Refresh only managed export files; preserve .git and unrelated repository files.
        output_files = sorted(p for p in stage.rglob('*') if p.is_file())
        for item in output_files:
            relative = item.relative_to(stage)
            target = checked_target(dest, relative)
            if target.is_symlink() or not target.resolve().is_relative_to(dest):
                raise SystemExit(f'Refusing linked/outside export target: {relative}')
            if target.exists():
                if not target.is_file():
                    raise SystemExit(f'Export file collides with a directory: {relative}')
                if relative.as_posix() not in managed and target.read_bytes() != item.read_bytes():
                    raise SystemExit(f'Unmanaged file would be overwritten: {relative}')
        wanted = {p.relative_to(stage).as_posix() for p in output_files}
        stale = []
        for item in managed - wanted:
            if not item.startswith('profiles/'):
                continue
            old = checked_target(dest, item)
            parts = Path(item).parts
            if len(parts) < 3 or parts[1] not in ROLES or not portable_file(Path(*parts[2:])):
                raise SystemExit(f'Invalid managed profile path: {item}')
            if old.is_file():
                # Do not silently discard edits to files removed from the source.
                expected = previous['files'].get(item)
                if hashlib.sha256(old.read_bytes()).hexdigest() != expected:
                    raise SystemExit(f'Obsolete managed file has local edits: {item}')
                stale.append(old)
        dest.mkdir(exist_ok=True)
        for item in output_files:
            target = dest / item.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(item, target)
        for old in stale:
            old.unlink()
    print(f'Exported {len(ROLES)} sanitized profile templates to {dest}')
    print('Ready to share through Git. No memory, sessions, credentials or run history included.')


if __name__ == '__main__':
    main()
