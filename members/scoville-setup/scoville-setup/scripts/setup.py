#!/usr/bin/env python3
"""Show, explicitly save or migrate one project's Scoville settings."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

from ask_settings import merge_config_layer, resolve_settings
from scoville_config import merge, read_config
from workflow_settings import load_config, needs_cleanup, validate_pair

ROOT = Path(__file__).resolve().parents[1]
# Schema-1 defaults at this fork's baseline, used only to interpret migration.
LEGACY_ROUTES = dict(ultra_low="low", low="medium", medium="high", high="xhigh", ultra_high="xhigh")
LEGACY_KEYS = {"schema_version", "execute", "review", "explore", "context_threshold_percent", "context", "manager", "pin_threads"}


def read_patch(required=True) -> dict:
    text = "" if sys.stdin.isatty() else sys.stdin.read()
    if not text.strip() and not required:
        return {}
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError("Supply a UTF-8 JSON object on stdin generated with a serializer; "
                         "use a workflow object with main, review and explore pairs for cleanup. "
                         f"Invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("stdin must contain a JSON object with ask and/or workflow settings")
    return value


def legacy_effective(value: dict) -> dict:
    unknown = set(value) - LEGACY_KEYS
    if unknown or ("schema_version" in value and
                   (type(value['schema_version']) is not int or value['schema_version'] != 1)):
        raise ValueError(f"workflow has unsupported legacy fields {sorted(unknown)} or schema_version; "
                         "resolve those fields explicitly before cleanup; no values were discarded")
    defaults = {route: {"model": "gpt-6.1-sol", "reasoning": effort}
                for route, effort in LEGACY_ROUTES.items()}
    result = {key: merge(defaults, value.get(key, {})) for key in ("execute", "review")}
    result['explore'] = merge(result['execute'], value.get('explore', {}))
    for section, table in result.items():
        if set(table) != set(LEGACY_ROUTES):
            raise ValueError(f"workflow.{section} must use the five legacy routes {', '.join(LEGACY_ROUTES)}; correct unknown routes before cleanup")
        for route, pair in table.items():
            validate_pair(pair, f"workflow.{section}.{route}")
    return result


def effective(project_root: Path) -> dict:
    current = read_config(project_root)
    workflow = current.get('workflow', {})
    values = (dict(schema_version=1, cleanup_required=True, **legacy_effective(workflow))
              if needs_cleanup(workflow) else load_config(ROOT / 'assets/workflow.toml', project_root))
    return {'ask': resolve_settings(ROOT / 'assets/ask.default.json', {'project_root': project_root}),
            'workflow': values}


def save_validated(project_root: Path, current: dict, proposed: dict, sections) -> dict:
    content = json.dumps(proposed, ensure_ascii=False, indent=2) + '\n'
    with tempfile.TemporaryDirectory(prefix='scoville-setup-') as temporary:
        candidate = Path(temporary)
        (candidate / '.scoville').mkdir()
        (candidate / '.scoville/config.json').write_bytes(content.encode('utf-8'))
        values = {}
        if 'workflow' in sections:
            values['workflow'] = load_config(ROOT / 'assets/workflow.toml', candidate)
        if 'ask' in sections:
            values['ask'] = resolve_settings(ROOT / 'assets/ask.default.json', {'project_root': candidate})
    if proposed == current:
        return {'saved': False, 'effective': values}
    path = project_root / '.scoville/config.json'
    path.parent.mkdir(exist_ok=True)
    staging = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.config-', suffix='.tmp', delete=False) as stream:
            staging = Path(stream.name)
            stream.write(content.encode('utf-8'))
        os.replace(staging, path)
    finally:
        if staging is not None and staging.exists():
            staging.unlink()
    return {'saved': True, 'effective': values}


def validate_setup_choices(value: dict, path: str = "patch") -> None:
    for key, item in value.items():
        field = f"{path}.{key}"
        if key in {"effort", "reasoning"} and item not in ("low", "medium", "high", "xhigh"):
            raise ValueError(
                f"{field}={type(item).__name__} is unsupported by Setup; choose low, medium, high or xhigh, "
                "or edit .scoville/config.json manually when another level is required"
            )
        if isinstance(item, dict):
            validate_setup_choices(item, field)
        elif isinstance(item, list):
            for index, entry in enumerate(item):
                if isinstance(entry, dict):
                    validate_setup_choices(entry, f"{field}[{index}]")


def apply(project_root: Path, patch: dict) -> dict:
    if not isinstance(patch, dict) or not patch or set(patch) - {'ask', 'workflow'}:
        raise ValueError("set requires a nonempty JSON object containing only ask and/or workflow")
    for key, value in patch.items():
        if not isinstance(value, dict):
            raise ValueError(f"patch.{key} must be a JSON object")
    validate_setup_choices(patch)
    current = read_config(project_root)
    if 'workflow' in patch:
        if needs_cleanup(current.get('workflow', {})):
            raise ValueError("saved workflow uses the old format; run cleanup before workflow set; no settings were saved")
        if set(patch['workflow']) - {'schema_version', 'main', 'review', 'explore'}:
            raise ValueError("patch.workflow accepts only schema_version=2, main, review and explore; use cleanup for old settings")
        if 'schema_version' in patch['workflow'] and (type(patch['workflow']['schema_version']) is not int
                                                     or patch['workflow']['schema_version'] != 2):
            raise ValueError('patch.workflow.schema_version must be integer 2 or omitted; set never writes the old format')
    if 'pin_threads' in patch.get('ask', {}):
        raise ValueError("patch.ask.pin_threads is obsolete; use ask.advisers or ask.presets")
    proposed = merge(current, patch)
    if 'workflow' in patch:
        proposed['workflow']['schema_version'] = 2
    if 'ask' in patch:
        proposed['ask'] = merge_config_layer(current.get('ask', {}), patch['ask'])
    return save_validated(project_root, current, proposed, patch.keys())


def cleanup(project_root: Path, patch: dict) -> dict:
    if set(patch) - {'workflow'} or not isinstance(patch.get('workflow', {}), dict):
        raise ValueError("cleanup accepts only a workflow object with explicit main, review and explore pairs")
    choices = patch.get('workflow', {})
    if set(choices) - {'main', 'review', 'explore'}:
        raise ValueError("cleanup workflow choices must be main, review and explore, each containing model and reasoning")
    for key, pair in choices.items():
        validate_pair(pair, 'workflow.' + key)
    current = read_config(project_root)
    old = current.get('workflow', {})
    if not needs_cleanup(old):
        if choices:
            return apply(project_root, {'workflow': choices})
        return {'saved': False, 'effective': {'workflow': load_config(ROOT / 'assets/workflow.toml', project_root)}}
    tables = legacy_effective(old)
    selected = dict(choices)
    missing = ['main'] if 'main' not in selected else []
    for section in ('review', 'explore'):
        candidates = {(pair['model'], pair['reasoning']) for pair in tables[section].values()}
        if section not in selected:
            if len(candidates) == 1:
                model, reasoning = next(iter(candidates))
                selected[section] = {'model': model, 'reasoning': reasoning}
            else:
                missing.append(section)
    if missing:
        raise ValueError(f"cleanup needs explicit pairs for workflow.{', workflow.'.join(missing)}; "
                         "main is never inferred from execute and different route pairs have no unique choice. "
                         "Run show, select the required complete pairs and rerun cleanup with serialized JSON on stdin; no settings were saved")
    proposed = dict(current, workflow=dict(schema_version=2, **selected))
    return save_validated(project_root, current, proposed, ('workflow',))


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='strict')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('show', 'set', 'cleanup'))
    parser.add_argument('--project-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.operation == 'show':
            result = {'saved': False, 'effective': effective(args.project_root)}
        elif args.operation == 'cleanup':
            result = cleanup(args.project_root, read_patch(required=False))
        else:
            result = apply(args.project_root, read_patch())
        print(json.dumps({'ok': True, 'file': str(args.project_root / '.scoville/config.json'), **result}, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(json.dumps({'ok': False, 'diagnostic': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
