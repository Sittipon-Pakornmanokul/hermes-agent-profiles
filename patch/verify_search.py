"""Portable offline real-tool probe. Run with Hermes' Python; no model/API calls."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--trace', action='store_true')
args = parser.parse_args()
ROOT = args.repo.expanduser().resolve(strict=True)
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

with tempfile.TemporaryDirectory(prefix='hermes-search-check-') as temp:
    os.environ['HERMES_HOME'] = str(Path(temp) / 'home')
    from tools.environments.local import LocalEnvironment
    from tools.file_operations import ShellFileOperations
    from tools import file_tools
    from tools.registry import registry

    folder = Path(temp) / 'source with spaces'
    folder.mkdir()
    source = folder / 'sample.py'
    source.write_text("call(value)\na.b\naXb\nC:\\temp\\file\nquote's.value\nABC.VALUE\n", encoding='utf-8')
    ops = ShellFileOperations(LocalEnvironment(cwd=str(folder)))
    if args.trace:
        execute = ops.env.execute
        def traced(command, **kwargs):
            print('COMMAND', repr(command))
            result = execute(command, **kwargs)
            print('OUTPUT', repr(result.get('output')))
            return result
        ops.env.execute = traced
        from tools.file_operations_search import _quote_search_pattern
        arg = _quote_search_pattern(r'C:\\temp\\file')
        print('FIXTURE', repr(source.read_text()))
        command = "printf '%s' " + arg
        print('RAW BASH', repr(ops.env._run_bash(command).communicate()[0]))
        print('ENV BASH', repr(ops.env.execute(command).get('output')))
    assert ops._resolve_command('rg'), 'ripgrep unavailable'
    from tools import file_operations_search
    import shlex
    if hasattr(file_operations_search, '_quote_search_pattern'):
        for value in [r'call\(', r'a\.b', r'C:\\temp\\file', "quote's.value", '', '\\', '\\\\', "\\'", '$(ignored);*', 'line\nnext']:
            assert shlex.split(file_operations_search._quote_search_pattern(value)) == [value], repr(value)
    failures = []
    cases = [(r'call\(', [1]), (r'a\.b', [2]),
             (r'C:\\temp\\file', [4]), (r"quote's\.value", [5])]
    with patch.object(file_tools, '_get_file_ops', return_value=ops):
        for engine in ['rg', 'grep']:
            original_has = ops._has_command
            with patch.object(ops, '_has_command', side_effect=lambda name: False if engine == 'grep' and name == 'rg' else original_has(name)):
                for pattern, expected in cases:
                    result = json.loads(registry.dispatch('search_files', {
                        'pattern': pattern, 'path': str(source), 'file_glob': '*.py'
                    }, task_id='search-regression'))
                    lines = [m['line'] for m in result.get('matches', [])]
                    passed = lines == expected and not result.get('error')
                    print(json.dumps({'engine': engine, 'pattern': pattern, 'pass': passed, 'result': result}))
                    if not passed:
                        failures.append((engine, pattern))
        hint = ops._zero_match_probe(r'abc\.value', str(source), '*.py')
        print(json.dumps({'zero_match_hint': hint}))
        if not hint or 'case' not in hint.lower():
            failures.append(('probe', 'case-insensitive'))
        result = json.loads(registry.dispatch('search_files', {
            'pattern': '*.py', 'target': 'files', 'path': str(folder)
        }, task_id='search-regression'))
        assert result.get('files') and not result.get('error'), result
    print(f'FAILED: {len(failures)} checks' if failures else 'PASS: all search checks')
    sys.exit(bool(failures))
