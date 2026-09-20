"""Apply the reviewed Hermes search fix to a matching checkout. Standard library only."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re

BEFORE = '2daf46cf147cbb38323859204004913d4c1ccafa26df20876de584311478c3dc'
AFTER = 'e265c4f99a99f7cd34a0d905d6b6f21ae525bfab5e87e55f2614bae013514abb'


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def transform(text, patch_text):
    lines = text.splitlines(keepends=True)
    output, position = [], 0
    hunks = patch_text.splitlines(keepends=True)
    i = 0
    while i < len(hunks):
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', hunks[i])
        if not match:
            i += 1
            continue
        start = int(match.group(1)) - 1
        if start < position:
            raise ValueError('Overlapping patch hunks')
        output.extend(lines[position:start])
        position = start
        i += 1
        while i < len(hunks) and not hunks[i].startswith('@@'):
            item = hunks[i]
            if item.startswith((' ', '-')):
                if position >= len(lines) or lines[position] != item[1:]:
                    raise ValueError('Patch context mismatch; no changes written')
                if item[0] == ' ':
                    output.append(lines[position])
                position += 1
            elif item.startswith('+'):
                output.append(item[1:])
            else:
                raise ValueError('Unexpected patch line')
            i += 1
    output.extend(lines[position:])
    result = ''.join(output)
    if digest(result) != AFTER:
        raise ValueError('Unexpected patched hash; no changes written')
    compile(result, 'file_operations_search.py', 'exec')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='Installed Hermes source checkout')
    parser.add_argument('--check', action='store_true', help='Check applicability without writing')
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve(strict=True)
    source = repo / 'tools/file_operations_search.py'
    if source.is_symlink() or not source.resolve().is_relative_to(repo):
        raise SystemExit('Refusing a linked source outside the requested checkout')
    raw = source.read_bytes()
    text = raw.decode('utf-8').replace('\r\n', '\n')
    if digest(text) == AFTER:
        print('Already patched; no changes.')
        return
    if digest(text) != BEFORE:
        raise SystemExit('Unsupported or locally changed Hermes source. Do not force this patch; review the diff against this version.')
    result = transform(text, Path(__file__).with_name('search-patterns.patch').read_text(encoding='utf-8'))
    if args.check:
        print('Patch applies to this source version. No files changed.')
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = source.with_name(source.name + '.backup-' + stamp)
    with backup.open('xb') as stream:
        stream.write(raw)
    if source.read_bytes() != raw:
        raise SystemExit('Source changed during preparation; not overwritten.')
    newline = '\r\n' if b'\r\n' in raw else '\n'
    source.write_bytes(result.replace('\n', newline).encode('utf-8'))
    print('Applied. Backup:', backup)
    print('Restart Hermes at a safe stopping point to load the fix.')


if __name__ == '__main__':
    main()
