"""The same variant test asset must bind preparation and runtime verification."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('mainloop_asset_builder', ROOT / 'development/build_suite.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class MainloopRuntimeAssets(unittest.TestCase):
    def test_prepare_and_each_loader_use_the_local_test_without_changing_other_assets(self):
        expected = (ROOT / 'development/runtime-tests/test_runtime_helpers.py').read_bytes()
        original = builder._shared_runtime_ci().assets()
        current = builder.runtime_ci().assets()
        self.assertEqual(set(original), set(current))
        self.assertEqual(expected, current['tests/test_runtime_helpers.py'])
        self.assertEqual(original[builder.runtime_ci().WORKFLOW], current[builder.runtime_ci().WORKFLOW])
        self.assertEqual(current, builder.runtime_ci().assets())
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'candidate'
            builder.runtime_ci().prepare(builder._module, ROOT, destination)
            meta = json.loads((destination / 'runtime-input.json').read_text(encoding='utf-8'))
            self.assertEqual(hashlib.sha256(expected).hexdigest(), meta['test_assets']['tests/test_runtime_helpers.py'])
            self.assertEqual(expected, (destination / 'tests/test_runtime_helpers.py').read_bytes())

    def test_verify_rejects_changed_local_test_bytes_before_package_proof(self):
        module = builder.runtime_ci()
        run = {'status': 'completed', 'conclusion': 'success', 'path': module.WORKFLOW,
               'run_attempt': 1, 'head_sha': 'tested-commit'}
        jobs = [{'name': f'runtime ({system}, {python})', 'conclusion': 'success'}
                for system in module.SYSTEMS for python in module.PYTHONS]
        def api(route):
            if route.endswith('/jobs?per_page=100'):
                return {'total_count': len(jobs), 'jobs': jobs}
            if '/actions/runs/' in route:
                return run
            return {'private': True}
        metadata = {'schema_version': 2, 'variants': {},
                    'test_assets': {'tests/test_runtime_helpers.py': hashlib.sha256(b'old test').hexdigest()}}
        with patch.object(module, 'api', side_effect=api), patch.object(module, 'remote_file',
                return_value=json.dumps(metadata).encode()):
            with self.assertRaisesRegex(ValueError, 'tests changed: test asset inventory'):
                module.verify(builder._module, ROOT,
                    f'https://github.com/{module.REPOSITORY}/actions/runs/123', builder.load(ROOT))


if __name__ == '__main__':
    unittest.main()
