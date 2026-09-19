"""Copy specialist profiles from the current directory into Hermes. No archives."""
import argparse
import os
from pathlib import Path
import shutil

ROLES = ('orchestrator', 'coder', 'code-reviewer', 'research', 'mcp-ops', 'ux-ui', 'ux-ui-critic')


def default_home():
    # When run with Hermes' interpreter, prefer the host's own root resolution.
    try:
        from hermes_constants import get_default_hermes_root
    except ImportError:
        if os.name == 'nt':
            return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'hermes'
        return Path.home() / '.hermes'
    return Path(get_default_hermes_root())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.cwd() / 'profiles', help='Profile folders (default: ./profiles)')
    parser.add_argument('--hermes-home', type=Path, help='Destination Hermes root; profiles are copied into its profiles subfolder')
    parser.add_argument('--profile', choices=ROLES, action='append', help='Copy just this role; repeat to select several')
    parser.add_argument('--dry-run', action='store_true', help='Show copies without writing')
    args = parser.parse_args()
    source = args.source.expanduser().resolve(strict=True)
    home = (args.hermes_home or default_home()).expanduser().resolve()
    destination = home / 'profiles'
    roles = list(dict.fromkeys(args.profile or ROLES))
    if destination.resolve() == source or destination.resolve().is_relative_to(source):
        raise SystemExit('Import destination must be outside the source profile folders.')
    if destination.is_symlink() or destination.resolve() != destination:
        raise SystemExit('Refusing a linked destination profiles directory.')
    copies = []
    for role in roles:
        origin = source / role
        target = destination / role
        if target.exists() or target.is_symlink():
            raise SystemExit(f'Profile already exists; nothing copied: {target}')
        if origin.is_symlink() or not (origin / 'config.yaml').is_file():
            raise SystemExit(f'Missing or linked source profile: {role}')
        entries = []
        for path in sorted(origin.rglob('*')):
            if path.is_symlink() or not path.resolve().is_relative_to(origin.resolve()):
                raise SystemExit(f'Refusing linked source content in {role}')
            if not path.is_file():
                continue
            relative = path.relative_to(origin)
            # Only exported configuration/instructions; never import runtime state or credentials.
            allowed = relative.as_posix() in {'config.yaml', 'SOUL.md', 'profile.yaml'}
            allowed |= relative.parts[0] in {'skills', 'workflows'} and path.suffix == '.md' and not set(relative.parts) & {'runs', 'memory', 'sessions', 'logs', 'cache'}
            if allowed:
                entries.append((path, relative))
        copies.append((role, target, entries))
    print('Source:', source)
    print('Hermes profiles:', destination)
    for role, target, entries in copies:
        print(f'{role}: {len(entries)} files -> {target}')
    if args.dry_run:
        print('Dry run; no files changed.')
        return
    destination.mkdir(parents=True, exist_ok=True)
    for role, target, entries in copies:
        target.mkdir()  # Fails rather than merging if another process created the profile.
        for path, relative in entries:
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            with path.open('rb') as src, output.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    print(f'Copied {len(copies)} profiles. Configure your own credentials and start fresh Hermes sessions.')


if __name__ == '__main__':
    main()
