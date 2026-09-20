"""Import this directory's portable profiles into the main Hermes configuration."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil

import yaml
from profile_sync import ROLES, default_home, portable_file, checked_target, merge_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.cwd() / 'profiles')
    parser.add_argument('--hermes-home', type=Path)
    parser.add_argument('--profile', choices=ROLES, action='append')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--update', action='store_true', help='Update existing profiles with backups, retaining host-only settings and state')
    args = parser.parse_args()
    source = args.source.expanduser().resolve(strict=True)
    home = (args.hermes_home or default_home()).expanduser().absolute()
    destination = checked_target(home, 'profiles')
    if destination.resolve().is_relative_to(source) or source.is_relative_to(destination.resolve()):
        raise SystemExit('Import source and destination must be separate.')
    plans = []
    for role in dict.fromkeys(args.profile or ROLES):
        origin = checked_target(source, role)
        target = checked_target(destination, role)
        if target.exists() and not args.update:
            raise SystemExit(f'Profile already exists; use --update: {target}')
        if not (origin / 'config.yaml').is_file():
            raise SystemExit(f'Missing source config: {role}')
        entries = []
        for path in sorted(origin.rglob('*')):
            relative = path.relative_to(origin)
            checked_target(origin, relative)
            if not path.is_file() or not portable_file(relative):
                continue
            output = checked_target(target, relative)
            if output.exists() and not output.is_file():
                raise SystemExit(f'Destination is not a file: {output}')
            data = path.read_bytes()
            if relative.as_posix() in {'config.yaml', 'profile.yaml'}:
                incoming = yaml.safe_load(data) or {}
                current = yaml.safe_load(output.read_bytes()) or {} if output.is_file() else {}
                if not isinstance(incoming, dict) or not isinstance(current, dict):
                    raise SystemExit(f'Expected YAML mapping: {relative}')
                data = yaml.safe_dump(merge_settings(current, incoming), sort_keys=False, allow_unicode=True).encode('utf-8')
            entries.append((relative, data))
        marker = checked_target(target, '.profile-bundle.json')
        previous = json.loads(marker.read_text(encoding='utf-8')) if marker.is_file() else []
        if not isinstance(previous, list) or any(not isinstance(p, str) for p in previous):
            raise SystemExit(f'Invalid tracking file: {marker}')
        wanted = {r.as_posix() for r, _ in entries}
        stale = []
        for item in previous:
            old = checked_target(target, item)
            if portable_file(item) and item not in wanted and old.is_file():
                stale.append(old)
        plans.append((role, target, entries, stale))
    print('Source:', source)
    print('Hermes profiles:', destination)
    for role, target, entries, stale in plans:
        print(f'{role}: {len(entries)} files, {len(stale)} obsolete managed files -> {target}')
    if args.dry_run:
        print('Dry run; no files changed.')
        return
    backup = checked_target(home, 'backups/profile-import-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    for role, target, entries, stale in plans:
        target.mkdir(parents=True, exist_ok=args.update)
        marker = target / '.profile-bundle.json'
        changed = [target / r for r, data in entries if (target / r).is_file() and (target / r).read_bytes() != data]
        for old in changed + stale + ([marker] if marker.is_file() else []):
            saved = backup / role / old.relative_to(target)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, saved)
        for relative, data in entries:
            output = target / relative
            if output.is_file() and output.read_bytes() == data:
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + '.import-tmp')
            with temporary.open('xb') as stream:
                stream.write(data)
            os.replace(temporary, output)
        for old in stale:
            old.unlink()
        marker.write_text(json.dumps([r.as_posix() for r, _ in entries], indent=2), encoding='utf-8')
    if backup.exists():
        print('Previous files backed up to:', backup)
    print(f'Imported {len(plans)} profiles. Start fresh Hermes sessions to load instructions.')


if __name__ == '__main__':
    main()
