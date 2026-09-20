"""Shared portable-file and destination rules for Hermes profile transfers."""
import os
from pathlib import Path

ROLES = ('orchestrator', 'coder', 'code-reviewer', 'research', 'mcp-ops', 'ux-ui', 'ux-ui-critic')
WORKFLOW_NAMES = {'orchestrator': ('task-orchestration', 'Task Orchestration'), 'coder': ('implementation-and-testing', 'Implementation and Testing'), 'code-reviewer': ('independent-code-review', 'Independent Code Review'), 'research': ('evidence-and-decision-research', 'Evidence and Decision Research'), 'mcp-ops': ('verified-service-operations', 'Verified Service Operations'), 'ux-ui': ('ux-design-and-handoff', 'UX Design and Handoff'), 'ux-ui-critic': ('ux-accessibility-review', 'UX and Accessibility Review')}

EXCLUDED = {'runs', 'memory', 'memories', 'sessions', 'logs', 'cache', 'reports', '__pycache__'}


def default_home():
    try:
        from hermes_constants import get_default_hermes_root
        return Path(get_default_hermes_root())
    except ImportError:
        native = (Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'hermes'
                  if os.name == 'nt' else Path.home() / '.hermes')
        value = os.environ.get('HERMES_HOME', '').strip()
        if not value:
            return native
        home = Path(os.path.expandvars(value)).expanduser()
        if home.resolve().is_relative_to(native.resolve()):
            return native
        return home.parent.parent if home.parent.name == 'profiles' else home


def workflow_file(relative):
    """Templates only: workflow history and arbitrary reports are never portable."""
    relative = Path(relative)
    if set(p.lower() for p in relative.parts) & EXCLUDED:
        return False
    return (relative.name in {'README.md', 'workflow.md', 'handoff.md', 'measurement.md'}
            or (relative.parent.name == 'roles' and relative.suffix == '.md')
            or relative.name.endswith(('-template.json', '-template.yaml', '-template.md')))


def portable_file(relative):
    relative = Path(relative)
    if set(p.lower() for p in relative.parts) & EXCLUDED:
        return False
    if relative.as_posix() in {'config.yaml', 'SOUL.md', 'profile.yaml'}:
        return True
    if relative.parts[0] == 'skills':
        return relative.suffix == '.md'
    return relative.parts[0] == 'workflows' and workflow_file(Path(*relative.parts[1:]))


def checked_target(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Unsafe relative path: {relative}')
    target = root / relative
    for path in (target, *target.parents):
        if path == root.parent:
            break
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ValueError(f'Refusing linked target: {relative}')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Target outside destination: {relative}')
    return target


def merge_settings(current, incoming):
    """Overlay portable settings, retaining host-only keys omitted by export."""
    if isinstance(current, dict) and isinstance(incoming, dict):
        result = dict(current)
        for key, value in incoming.items():
            result[key] = merge_settings(result.get(key), value)
        return result
    return incoming
