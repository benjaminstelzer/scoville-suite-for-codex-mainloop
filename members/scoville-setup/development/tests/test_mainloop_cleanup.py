"""Exercise shipped Setup migration and its actual Workflow consumer."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
PAIRS = {'main': {'model': 'gpt-6.1-sol', 'reasoning': 'high'},
         'review': {'model': 'gpt-6.1-sol', 'reasoning': 'xhigh'},
         'explore': {'model': 'gpt-6.1-sol', 'reasoning': 'high'}}
ROUTES = ('ultra_low', 'low', 'medium', 'high', 'ultra_high')


class MainloopCleanupTests(unittest.TestCase):
    def test_show_schema2_legacy_fields_names_cleanup_without_writing(self):
        self.save({'workflow': dict(schema_version=2, **PAIRS, pin_threads=True)})
        original = self.path.read_bytes()
        status, result = self.run_setup('show')
        self.assertEqual(status, 0, result)
        workflow = result['effective']['workflow']
        self.assertTrue(workflow['cleanup_required'])
        self.assertEqual(workflow['legacy_fields'], ['pin_threads'])
        self.assertEqual(workflow['main'], PAIRS['main'])
        self.assertEqual(self.path.read_bytes(), original)
        status, result = self.run_setup('cleanup')
        self.assertEqual(status, 0, result)
        self.assertNotIn('pin_threads', json.loads(self.path.read_text())['workflow'])
        self.save({'workflow': []})
        status, result = self.run_setup('show')
        self.assertEqual(status, 1)
        self.assertNotIn('no settings were saved', json.dumps(result))

    @classmethod
    def setUpClass(cls):
        cls.package = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.package.cleanup)
        spec = importlib.util.spec_from_file_location('mainloop_setup_builder', ROOT / 'development/build_suite.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        config = builder.load(ROOT, 'codex')
        for name in ('scoville-setup', 'scoville-workflow-for-codex'):
            member = next(m for m in config['members'] if m['name'] == name)
            for relative, data in builder.payload(ROOT, member, config).items():
                path = Path(cls.package.name) / name / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        cls.helper = Path(cls.package.name) / 'scoville-setup/scoville-setup/scripts/setup.py'
        cls.resolver = Path(cls.package.name) / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/resolve_model_pair.py'

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / 'Projekt Ä 中文'
        self.project.mkdir()
        self.path = self.project / '.scoville/config.json'

    def save(self, value):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_bytes((json.dumps(value, ensure_ascii=False) + '\n').encode('utf-8'))

    def run_setup(self, operation, value=None):
        result = subprocess.run([sys.executable, '-B', str(self.helper), operation,
                                 '--project-root', str(self.project)],
                                input='' if value is None else json.dumps(value, ensure_ascii=False),
                                capture_output=True, encoding='utf-8')
        return result.returncode, json.loads(result.stdout)

    def resolve(self, role):
        result = subprocess.run([sys.executable, '-B', str(self.resolver), '--role', role,
                                 '--project-root', str(self.project)], capture_output=True, encoding='utf-8')
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_show_new_defaults_without_creating_configuration(self):
        status, result = self.run_setup('show')
        self.assertEqual(0, status)
        self.assertFalse(result['saved'])
        self.assertEqual(dict(schema_version=2, **PAIRS), result['effective']['workflow'])
        self.assertFalse(self.path.parent.exists())

    def test_show_legacy_resolves_but_never_migrates(self):
        self.save({'workflow': {'schema_version': 1, 'context_threshold_percent': 50}})
        before = self.path.read_bytes()
        status, result = self.run_setup('show')
        self.assertEqual(0, status)
        self.assertTrue(result['effective']['workflow']['cleanup_required'])
        self.assertFalse(result['saved'])
        self.assertEqual(before, self.path.read_bytes())

    def test_workflow_set_requires_cleanup_and_has_no_side_effect(self):
        self.save({'workflow': {'execute': {'low': {'model': 'existing'}}}})
        before = self.path.read_bytes()
        status, result = self.run_setup('set', {'workflow': {'review': PAIRS['review']}})
        self.assertEqual(1, status)
        self.assertIn('cleanup', result['diagnostic'].lower())
        self.assertEqual(before, self.path.read_bytes())

    def test_ask_only_save_does_not_validate_or_rewrite_legacy_workflow_values(self):
        old = {'schema_version': 1, 'context': {'worker_percent': 'old'},
               'execute': {'invalid-route': None}}
        other = {'keep': [1, 2, 'Ä 中文']}
        self.save({'workflow': old, 'other_tool': other})
        status, result = self.run_setup('set', {'ask': {'claude': {'max_budget_usd': 0}}})
        self.assertEqual(0, status, result)
        saved = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(old, saved['workflow'])
        self.assertEqual(other, saved['other_tool'])
        self.assertNotIn('workflow', result['effective'])

    def test_ambiguous_routes_need_choices_then_actual_consumer_uses_them(self):
        self.save({'workflow': {'schema_version': 1}, 'other': 'keep'})
        before = self.path.read_bytes()
        status, result = self.run_setup('cleanup')
        self.assertEqual(1, status)
        for section in ('main', 'review', 'explore'):
            self.assertIn('workflow.' + section, result['diagnostic'])
        self.assertEqual(before, self.path.read_bytes())
        status, result = self.run_setup('cleanup', {'workflow': PAIRS})
        self.assertEqual(0, status, result)
        self.assertTrue(result['saved'])
        saved = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(dict(schema_version=2, **PAIRS), saved['workflow'])
        self.assertEqual('keep', saved['other'])
        self.assertEqual('xhigh', self.resolve('reviewer')['thinking'])
        self.assertEqual('high', self.resolve('explorer')['thinking'])

    def test_fieldwise_explorer_inheritance_and_special_efforts_survive(self):
        old = {'schema_version': 1,
               'execute': {route: {'model': 'execute-model', 'reasoning': 'max'} for route in ROUTES},
               'review': {route: {'model': 'review-model', 'reasoning': 'ultra'} for route in ROUTES},
               'explore': {route: {'model': 'explore-model'} for route in ROUTES},
               'context_threshold_percent': 20, 'manager': {'old': True}}
        ask = {'presets': {'sol': {'effort': 'max'}}}
        self.save({'workflow': old, 'ask': ask})
        status, result = self.run_setup('cleanup', {'workflow': {'main': PAIRS['main']}})
        self.assertEqual(0, status, result)
        saved = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual({'model': 'review-model', 'reasoning': 'ultra'}, saved['workflow']['review'])
        self.assertEqual({'model': 'explore-model', 'reasoning': 'max'}, saved['workflow']['explore'])
        self.assertEqual(ask, saved['ask'])
        self.assertEqual('max', self.resolve('explorer')['thinking'])

    def test_second_cleanup_has_no_write(self):
        self.save({'workflow': {'schema_version': 1}})
        self.assertEqual(0, self.run_setup('cleanup', {'workflow': PAIRS})[0])
        before, metadata = self.path.read_bytes(), self.path.stat()
        status, result = self.run_setup('cleanup')
        self.assertEqual(0, status)
        self.assertFalse(result['saved'])
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(metadata.st_mtime_ns, self.path.stat().st_mtime_ns)

    def test_invalid_choices_cannot_partially_migrate(self):
        self.save({'workflow': {'schema_version': 1}, 'other': 'preserve'})
        before = self.path.read_bytes()
        choices = dict(PAIRS, main={'model': 'gpt-6.1-sol'})
        status, result = self.run_setup('cleanup', {'workflow': choices})
        self.assertEqual(1, status)
        self.assertIn('workflow.main', result['diagnostic'])
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(0, self.run_setup('cleanup', {'workflow': PAIRS})[0])

    def test_workflow_save_does_not_validate_unrelated_ask_semantics(self):
        ask = {'claude': {'timeout_seconds': 'invalid-but-unchanged'}}
        self.save({'ask': ask})
        status, result = self.run_setup('set', {'workflow': {'review': {'reasoning': 'high'}}})
        self.assertEqual(0, status, result)
        self.assertEqual(ask, json.loads(self.path.read_text(encoding='utf-8'))['ask'])
        self.assertEqual('high', self.resolve('reviewer')['thinking'])

    def test_unknown_legacy_values_are_not_discarded(self):
        self.save({'workflow': {'schema_version': 1, 'foreign_flag': 'preserve'}})
        before = self.path.read_bytes()
        status, result = self.run_setup('cleanup', {'workflow': PAIRS})
        self.assertEqual(1, status)
        self.assertIn('foreign_flag', result['diagnostic'])
        self.assertEqual(before, self.path.read_bytes())


if __name__ == '__main__':
    unittest.main()
