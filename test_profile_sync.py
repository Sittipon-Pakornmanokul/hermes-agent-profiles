import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml
from profile_sync import ROLES, checked_target, default_home, workflow_file

ROOT = Path(__file__).resolve().parent


class ProfileTransfers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'main'
        self.bundle = self.root / 'bundle'
        self.destination = self.root / 'recipient'
        self.repo = self.root / 'repo'
        (self.repo / 'agent').mkdir(parents=True)
        (self.repo / 'agent/__init__.py').write_text('')
        (self.repo / 'agent/redact.py').write_text('def redact_sensitive_text(text, force=False):\n    return text\n')
        for role in ROLES:
            home = self.source / 'profiles' / role
            workflow = home / 'workflows/lean-execution'
            workflow.mkdir(parents=True)
            (home / 'config.yaml').write_text('model:\n  default: test-model\nagent:\n  max_turns: 73\n  reasoning_effort: low\napi_key: private\n')
            (home / 'SOUL.md').write_text(f'{role} current instructions; keep this exactly.\n')
            (workflow / 'workflow.md').write_text(f'{role} unique workflow\n')
            (workflow / 'task-template.json').write_text('{"task_id": null}\n')
            (workflow / 'runs').mkdir()
            (workflow / 'runs/README.md').write_text('private history')
            (workflow / 'ledger.json').write_text('{"private": true}')

    def command(self, script, *args, success=True):
        result = subprocess.run([sys.executable, str(ROOT / script), *map(str, args)], capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def export(self, success=True):
        return self.command('export_profiles.py', '--source', self.source, '--dest', self.bundle, '--repo', self.repo, success=success)

    def test_export_preserves_roles_settings_and_excludes_history(self):
        self.export()
        for role in ROLES:
            profile = self.bundle / 'profiles' / role
            self.assertEqual((profile / 'workflows/lean-execution/workflow.md').read_text(), f'{role} unique workflow\n')
            self.assertTrue((profile / 'workflows/lean-execution/task-template.json').exists())
            self.assertFalse((profile / 'workflows/lean-execution/runs').exists())
            self.assertFalse((profile / 'workflows/lean-execution/ledger.json').exists())
            config = yaml.safe_load((profile / 'config.yaml').read_text())
            self.assertEqual(config['agent'], {'max_turns': 73, 'reasoning_effort': 'low'})
            self.assertNotIn('api_key', config)
        manifest = json.loads((self.bundle / 'MANIFEST.json').read_text())
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((self.bundle / name).read_bytes()).hexdigest(), digest)

    def test_import_roundtrip_update_backup_and_dry_run(self):
        self.export()
        args = ['--source', self.bundle / 'profiles', '--hermes-home', self.destination]
        self.command('import_profiles.py', *args, '--dry-run')
        self.assertFalse(self.destination.exists())
        self.command('import_profiles.py', *args)
        target = self.destination / 'profiles/coder'
        self.command('import_profiles.py', *args, success=False)
        config = yaml.safe_load((target / 'config.yaml').read_text())
        config['mcp_servers'] = {'local': {'command': 'private-local-command'}}
        config['model']['api_key'] = 'keep-private-key'
        (target / 'config.yaml').write_text(yaml.safe_dump(config))
        (target / '.env').write_text('PRIVATE=stay-here')
        (target / 'workflows/lean-execution/local-notes.md').write_text('keep')
        (self.bundle / 'profiles/coder/workflows/lean-execution/workflow.md').write_text('changed coder flow')
        (self.bundle / 'profiles/coder/workflows/lean-execution/task-template.json').unlink()
        self.command('import_profiles.py', *args, '--update', '--dry-run')
        self.assertEqual((target / 'workflows/lean-execution/workflow.md').read_text(), 'coder unique workflow\n')
        self.command('import_profiles.py', *args, '--update')
        merged = yaml.safe_load((target / 'config.yaml').read_text())
        self.assertEqual(merged['mcp_servers'], config['mcp_servers'])
        self.assertEqual(merged['model']['api_key'], 'keep-private-key')
        self.assertEqual((target / '.env').read_text(), 'PRIVATE=stay-here')
        self.assertEqual((target / 'workflows/lean-execution/workflow.md').read_text(), 'changed coder flow')
        self.assertFalse((target / 'workflows/lean-execution/task-template.json').exists())
        self.assertTrue((target / 'workflows/lean-execution/local-notes.md').exists())
        self.assertTrue(list((self.destination / 'backups').rglob('task-template.json')))

    def test_export_stale_cleanup_protects_local_changes(self):
        self.export()
        relative = 'profiles/coder/workflows/lean-execution/workflow.md'
        (self.source / relative).unlink()
        (self.bundle / relative).write_text('local edits')
        self.export(success=False)
        self.assertEqual((self.bundle / relative).read_text(), 'local edits')
        (self.bundle / relative).write_bytes(b'coder unique workflow\n')
        self.export()
        self.assertFalse((self.bundle / relative).exists())

    def test_manifest_traversal_rejected_before_write(self):
        self.export()
        manifest_path = self.bundle / 'MANIFEST.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files']['profiles/../../outside.md'] = 'bad'
        manifest_path.write_text(json.dumps(manifest))
        self.export(success=False)

    def test_custom_active_profile_home(self):
        custom = self.root / 'custom'
        with patch.dict(os.environ, {'HERMES_HOME': str(custom / 'profiles/coder')}):
            self.assertEqual(default_home(), custom)

    def test_template_filter_and_target_guard(self):
        self.assertTrue(workflow_file('lean-execution/task-template.json'))
        self.assertFalse(workflow_file('lean-execution/runs/README.md'))
        self.assertFalse(workflow_file('lean-execution/ledger.json'))
        with self.assertRaises(ValueError):
            checked_target(self.root, '../outside')


if __name__ == '__main__':
    unittest.main()
