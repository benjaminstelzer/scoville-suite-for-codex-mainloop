"""Project overrides reach actual model consumers; legacy role settings are inert."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from test_contract import PACKAGE
sys.path.insert(0, str(PACKAGE / "scripts"))
from resolve_model_pair import load_config, resolve


class ProjectConfigTests(unittest.TestCase):
    def test_explorer_pair_is_independent_of_main_and_has_fieldwise_defaults(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = load_config(defaults, root)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            saved = {'workflow': {'main': {'model': 'main-custom'}, 'explore': {'reasoning': 'medium'}}}
            path.write_text(json.dumps(saved), encoding='utf-8')
            config = load_config(defaults, root)
            self.assertEqual(baseline['explore']['model'], resolve(config, 'explorer')['model'])
            self.assertEqual('medium', resolve(config, 'explorer')['thinking'])
            self.assertEqual('main-custom', resolve(config, 'main')['model'])
            self.assertEqual(saved, json.loads(path.read_text()))

    def test_partial_file_overrides_do_not_search_parent_or_rewrite_values(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = load_config(defaults, root)
            self.assertFalse((root / '.scoville').exists())
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            saved = {'workflow': {'main': {'model': 'custom-model'}}}
            path.write_text(json.dumps(saved), encoding='utf-8')
            config = load_config(defaults, root)
            self.assertEqual('custom-model', config['main']['model'])
            self.assertEqual(baseline['main']['reasoning'], config['main']['reasoning'])
            self.assertEqual(baseline['review'], config['review'])
            child = root / 'child'
            child.mkdir()
            self.assertEqual(baseline, load_config(defaults, child))
            saved['workflow']['main']['model'] = 'next-run'
            path.write_text(json.dumps(saved), encoding='utf-8')
            self.assertEqual('next-run', load_config(defaults, root)['main']['model'])
            self.assertEqual(saved, json.loads(path.read_text()))

    def test_invalid_values_fail_in_the_consuming_operation(self):
        defaults = PACKAGE / "assets/workflow.toml"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".scoville").mkdir()
            path = root / ".scoville/config.json"
            for value in (None, [], {"execute": {"low": {"reasoning": False}}}):
                path.write_text(json.dumps({"workflow": value}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_config(defaults, root)
    def test_invalid_pair_does_not_echo_private_value(self):
        import subprocess
        marker = 'TEST_PRIVATE_VALUE_NOT_FOR_DIAGNOSTICS'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            path.write_text(json.dumps({'workflow': {'review': {'api_key': marker}}}), encoding='utf-8')
            cmd = [sys.executable, str(PACKAGE / 'scripts/resolve_model_pair.py'), '--role', 'reviewer', '--project-root', str(root)]
            failed = subprocess.run(cmd, text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(1, failed.returncode)
            self.assertNotIn(marker, failed.stdout + failed.stderr)
            self.assertIn('workflow.review', failed.stdout)
            path.write_text('{}', encoding='utf-8')
            self.assertEqual(0, subprocess.run(cmd, capture_output=True).returncode)


    def test_legacy_fields_require_cleanup_without_rewriting_project(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            for value in (None, [], False, {'worker_percent': 'broken', 'secret': 'not-read'}):
                saved = {'workflow': {'manager': value, 'context': value, 'pin_threads': value}, 'other': {'keep': True}}
                path.write_text(json.dumps(saved), encoding='utf-8')
                before = path.read_bytes()
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'cleanup'):
                    load_config(defaults, root)
                self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
