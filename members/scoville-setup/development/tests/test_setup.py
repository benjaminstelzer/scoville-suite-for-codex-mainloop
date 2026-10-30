"""Exercise shipped Setup, legacy config migration and real route consumers."""
import importlib.util
import json
import os
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('setup_builder', ROOT / 'development/build_suite.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SetupTests(unittest.TestCase):
    def test_save_preserves_existing_mode_and_foreign_fields(self):
        self.save({'other': {'keep': True}})
        self.path.chmod(0o640)
        before = stat.S_IMODE(self.path.stat().st_mode)
        status, saved = self.run_setup('set', {'workflow': {'main': {'reasoning': 'medium'}}})
        self.assertEqual(status, 0, saved)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), before)
        self.assertEqual(json.loads(self.path.read_text())['other'], {'keep': True})

    def test_file_link_save_is_refused_without_replacing_link_or_target(self):
        outside = self.base / 'outside.json'
        outside.write_text('{"other":{"keep":true}}', encoding='utf-8')
        self.path.parent.mkdir()
        try:
            self.path.symlink_to(outside)
        except OSError as error:
            self.skipTest(f'symlinks unavailable: {error}')
        before = outside.read_bytes()
        status, failed = self.run_setup('set', {'workflow': {'main': {'reasoning': 'medium'}}})
        self.assertEqual(status, 1)
        self.assertIn('redirected path', failed['diagnostic'])
        self.assertTrue(self.path.is_symlink())
        self.assertEqual(outside.read_bytes(), before)
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ['config.json'])

    def test_directory_link_save_is_refused_without_writing_into_target(self):
        outside = self.base / 'outside-directory'
        outside.mkdir()
        (outside / 'config.json').write_text('{}', encoding='utf-8')
        try:
            self.path.parent.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f'symlinks unavailable: {error}')
        status, failed = self.run_setup('set', {'workflow': {'main': {'reasoning': 'medium'}}})
        self.assertEqual(status, 1)
        self.assertIn('redirected path', failed['diagnostic'])
        self.assertTrue(self.path.parent.is_symlink())
        self.assertEqual((outside / 'config.json').read_text(), '{}')
        self.assertEqual([p.name for p in outside.iterdir()], ['config.json'])

    def test_readonly_mode_is_preserved_and_failed_save_leaves_no_staging_file(self):
        self.save({'other': True})
        self.path.chmod(stat.S_IRUSR)
        before = self.path.read_bytes()
        mode = stat.S_IMODE(self.path.stat().st_mode)
        try:
            status, result = self.run_setup('set', {'workflow': {'main': {'reasoning': 'medium'}}})
            if os.name == 'nt':
                self.assertEqual(status, 1, result)
                self.assertEqual(self.path.read_bytes(), before)
            else:
                self.assertEqual(status, 0, result)
            self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), mode)
            self.assertEqual([p.name for p in self.path.parent.iterdir()], ['config.json'])
        finally:
            self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_cleanup_checks_explicit_choices_but_preserves_inherited_special_pairs(self):
        routes = {key: {'model': 'gpt-6.1-sol', 'reasoning': 'max'}
                  for key in ('ultra_low', 'low', 'medium', 'high', 'ultra_high')}
        self.save({'workflow': {'schema_version': 1, 'review': routes, 'explore': routes}, 'other': 7})
        before = self.path.read_bytes()
        status, failed = self.run_setup('cleanup', {'workflow': {'main': {'model': 'gpt-6.1-sol', 'reasoning': 'max'}}})
        self.assertEqual(status, 1)
        self.assertEqual(self.path.read_bytes(), before)
        status, saved = self.run_setup('cleanup', {'workflow': {'main': {'model': 'gpt-6.1-sol', 'reasoning': 'high'}}})
        self.assertEqual(status, 0, saved)
        actual = json.loads(self.path.read_text())
        self.assertEqual(actual['workflow']['review']['reasoning'], 'max')
        self.assertEqual(actual['workflow']['explore']['reasoning'], 'max')
        self.assertEqual(actual['other'], 7)

    def test_cleanup_schema_two_removes_known_legacy_fields_without_reinterpreting_pairs(self):
        pairs = {key: {'model': 'gpt-6.1-sol', 'reasoning': level}
                 for key, level in (('main', 'high'), ('review', 'max'), ('explore', 'low'))}
        self.save({'workflow': {'schema_version': 2, **pairs, 'context_threshold_percent': 50}, 'ask': {}, 'other': True})
        status, saved = self.run_setup('cleanup', {})
        self.assertEqual(status, 0, saved)
        self.assertEqual(json.loads(self.path.read_text()), {'workflow': {'schema_version': 2, **pairs}, 'ask': {}, 'other': True})
        self.save({'workflow': {'schema_version': 2, **pairs, 'context': {}, 'unknown': 7}})
        before = self.path.read_bytes()
        status, failed = self.run_setup('cleanup', {})
        self.assertEqual(status, 1)
        self.assertIn('unknown', failed['diagnostic'])
        self.assertEqual(self.path.read_bytes(), before)

    def test_show_reports_both_invalid_sections_without_partial_effective_payload(self):
        self.save({'ask': None, 'workflow': False})
        before = self.path.read_bytes()
        status, failed = self.run_setup('show')
        self.assertEqual(status, 1)
        self.assertFalse(failed['ok'])
        self.assertEqual(set(failed['diagnostics']), {'ask', 'workflow'})
        self.assertNotIn('effective', failed)
        self.assertEqual(self.path.read_bytes(), before)

    def test_bad_ask_type_does_not_block_workflow_config_or_main_config_boundary(self):
        self.save({'ask': None, 'workflow': {'schema_version': 2}})
        command = [sys.executable, str(self.workflow / 'resolve_model_pair.py'), '--project-root', str(self.project)]
        result = subprocess.run([*command, '--show-config'], capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(json.loads(result.stdout)['valid'])
        env = {key: value for key, value in os.environ.items() if key != 'CODEX_THREAD_ID'}
        result = subprocess.run([*command, '--role', 'main'], env=env, capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn('CODEX_THREAD_ID', json.loads(result.stdout)['diagnostic'])
        self.assertNotIn('$.ask', result.stdout)
        self.path.write_text('{', encoding='utf-8')
        result = subprocess.run([*command, '--show-config'], capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn('invalid JSON', result.stdout)

    def test_failed_candidate_diagnostic_names_actual_project_config(self):
        status, failed = self.run_setup('set', {'ask': {'presets': {'astra': {'model': 'bad model'}}}})
        self.assertEqual(status, 1)
        self.assertIn(str(self.path), failed['diagnostic'])
        self.assertNotIn('scoville-setup-', failed['diagnostic'])
        self.assertFalse(self.path.exists())

    def test_workflow_model_rejects_all_whitespace_and_metadata_is_packaged(self):
        self.assertTrue((self.helper.parents[1] / 'agents/openai.yaml').is_file())
        for model in ('bad model', 'bad\tmodel', 'bad\nmodel'):
            status, failed = self.run_setup('set', {'workflow': {'main': {'model': model}}})
            self.assertEqual(status, 1)
            self.assertIn('without whitespace', failed['diagnostic'])
            self.assertFalse(self.path.exists())

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        config = builder.load(ROOT, 'codex', 'suite')
        for name in ('scoville-setup', 'scoville-ask-for-codex', 'scoville-workflow-for-codex'):
            member = next(m for m in config['members'] if m['name'] == name)
            for relative, data in builder.payload(ROOT, member, config).items():
                target = self.base / name / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        self.project = self.base / 'Projekt Ä 中文'
        self.project.mkdir()
        self.path = self.project / '.scoville/config.json'
        self.helper = self.base / 'scoville-setup/scoville-setup/scripts/setup.py'
        self.workflow = self.base / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts'

    def save(self, value):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(value, ensure_ascii=False) + '\n', encoding='utf-8')

    def run_setup(self, operation, patch=None, raw=None):
        result = subprocess.run([sys.executable, '-B', str(self.helper), operation,
                                 '--project-root', str(self.project)],
                                input=raw if raw is not None else json.dumps(patch, ensure_ascii=False).encode('utf-8'),
                                capture_output=True)
        return result.returncode, json.loads(result.stdout.decode('utf-8'))

    def test_show_diagnoses_legacy_fields_without_writing(self):
        status, shown = self.run_setup('show')
        self.assertEqual(0, status)
        self.assertFalse(self.path.parent.exists())
        self.save({'workflow': {'context': {'worker_percent': 'obsolete'}, 'manager': {'model': False}, 'pin_threads': 'obsolete'}, 'unrelated': {'keep': 'Ä 中文'}})
        before = self.path.read_bytes()
        status, shown = self.run_setup('show')
        self.assertEqual(0, status)
        self.assertTrue(shown['effective']['workflow']['cleanup_required'])
        self.assertFalse(shown['saved'])
        self.assertEqual(before, self.path.read_bytes())

    def test_authorized_fixed_save_preserves_ask_and_foreign_values(self):
        before = {'workflow': {'main': {'reasoning': 'high'}}, 'ask': {'pin_threads': True, 'claude': {'timeout_seconds': 2400}}, 'other_tool': {'keep': [1, 2, 'Ä 中文']}}
        self.save(before)
        status, saved = self.run_setup('set', {'workflow': {'review': {'reasoning': 'medium'}}})
        self.assertEqual(0, status, saved)
        after = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(before['ask'], after['ask'])
        self.assertEqual(before['other_tool'], after['other_tool'])
        self.assertEqual({'reasoning': 'medium'}, after['workflow']['review'])
        resolved = subprocess.run([sys.executable, '-B', str(self.workflow / 'resolve_model_pair.py'), '--project-root', str(self.project), '--role', 'reviewer'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, resolved.returncode, resolved.stderr)
        self.assertEqual('medium', json.loads(resolved.stdout)['thinking'])
        ask = self.base / 'scoville-ask-for-codex/scoville-ask-for-codex/scripts/ask.py'
        request = {'operation': 'resolve', 'project_root': str(self.project), 'overrides': {'advisers': ['fable']}}
        resolved = subprocess.run([sys.executable, '-B', str(ask)], input=json.dumps(request), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, resolved.returncode, resolved.stderr)
        self.assertTrue(json.loads(resolved.stdout)['config']['pin_threads'])

    def test_rejected_patches_preserve_every_saved_byte(self):
        self.save({'workflow': {'context': {'worker_percent': 60}}, 'other': {'keep': True}})
        before = self.path.read_bytes()
        invalid = [ {'workflow': {key: {}}} for key in ('context', 'manager', 'pin_threads') ]
        invalid += [{'workflow': {'context_threshold_percent': value}} for value in (True, False, 0, 101, 50.0, '50', {})]
        invalid += [{'ask': {'claude': {'max_budget_usd': value}}}
                    for value in (-1, True, False, None, '0', float('nan'), float('inf'), -float('inf'))]
        invalid += [{'workflow': {'unknown': {}}}, {'ask': {'pin_threads': False}},
                    {'ask': {'claude': {'timeout_seconds': 0}}},
                    {'workflow': {'execute': {'low': {'reasoning': 'bad'}}}},
                    {'workflow': {'execute': {'low': {'model': False}}}}]
        for patch in invalid:
            with self.subTest(patch=patch):
                status, failed = self.run_setup('set', patch)
                self.assertNotEqual(status, 0)
                self.assertFalse(failed['ok'])
                self.assertTrue(failed['diagnostic'])
                self.assertEqual(self.path.read_bytes(), before)
        for raw in (b'', b'{\n"workflow":', b'\xff'):
            status, failed = self.run_setup('set', raw=raw)
            self.assertNotEqual(status, 0)
            self.assertFalse(failed['ok'])
            self.assertEqual(self.path.read_bytes(), before)
        choices = {key: {'model': 'gpt-6.1-sol', 'reasoning': 'high'} for key in ('main', 'review', 'explore')}
        status, saved = self.run_setup('cleanup', {'workflow': choices})
        self.assertEqual(status, 0, saved)
        self.assertNotIn('context', json.loads(self.path.read_text())['workflow'])

    def test_regular_choices_can_be_saved_for_workflow_and_ask(self):
        for level in ('low', 'medium', 'high', 'xhigh'):
            with self.subTest(level=level):
                status, saved = self.run_setup('set', {
                    'workflow': {'main': {'reasoning': level}},
                    'ask': {'presets': {'astra': {'effort': level}}}})
                self.assertEqual(0, status, saved)
                self.assertEqual(level, saved['effective']['workflow']['main']['reasoning'])
                self.assertEqual(level, saved['effective']['ask']['presets']['astra']['effort'])

    def test_new_special_choices_are_rejected_without_writing(self):
        self.save({'workflow': {'main': {'reasoning': 'high'}}, 'other': {'keep': True}})
        before = self.path.read_bytes()
        for level in ('none', 'minimal', 'max', 'ultra'):
            for patch in ({'workflow': {'main': {'reasoning': level}}},
                          {'ask': {'presets': {'astra': {'effort': level}}}}):
                with self.subTest(patch=patch):
                    status, failed = self.run_setup('set', patch)
                    self.assertEqual(1, status)
                    self.assertFalse(failed['ok'])
                    field = ('patch.workflow.main.reasoning' if 'workflow' in patch
                             else 'patch.ask.presets.astra.effort')
                    self.assertIn(field, failed['diagnostic'])
                    self.assertIn(repr(level), failed['diagnostic'])
                    self.assertIn('low, medium, high or xhigh', failed['diagnostic'])
                    self.assertIn('no settings were saved', failed['diagnostic'])
                    self.assertIn('the user can edit .scoville/config.json manually', failed['diagnostic'])
                    self.assertEqual(before, self.path.read_bytes())
        for value in ({'secret': 'private-token-not-for-display'}, ['private-token-not-for-display']):
            status, failed = self.run_setup('set', {'workflow': {'main': {'reasoning': value}}})
            self.assertEqual(status, 1)
            self.assertIn('patch.workflow.main.reasoning', failed['diagnostic'])
            self.assertNotIn('private-token-not-for-display', failed['diagnostic'])
            self.assertEqual(before, self.path.read_bytes())
        status, saved = self.run_setup('set', {
            'workflow': {'main': {'reasoning': 'medium'}},
            'ask': {'presets': {'astra': {'effort': 'medium'}}}})
        self.assertEqual(0, status, saved)
        self.assertTrue(saved['saved'])
        self.assertEqual('medium', saved['effective']['workflow']['main']['reasoning'])
        self.assertEqual('medium', saved['effective']['ask']['presets']['astra']['effort'])
        self.assertEqual({'keep': True}, json.loads(self.path.read_text())['other'])

    def test_supported_special_levels_survive_unrelated_save(self):
        for level in ('none', 'minimal', 'max', 'ultra'):
            with self.subTest(level=level):
                self.save({'workflow': {'main': {'reasoning': level}},
                           'ask': {'presets': {'astra': {'effort': level}}}})
                status, saved = self.run_setup('set', {'ask': {'claude': {'timeout_seconds': 2400}}})
                self.assertEqual(0, status, saved)
                self.assertEqual(level, json.loads(self.path.read_text())['workflow']['main']['reasoning'])
                self.assertEqual(level, saved['effective']['ask']['presets']['astra']['effort'])

    def test_unknown_saved_workflow_key_does_not_become_ignored(self):
        self.save({'workflow': {'unknown': True}})
        before = self.path.read_bytes()
        status, failed = self.run_setup('show')
        self.assertNotEqual(status, 0)
        self.assertFalse(failed['ok'])
        self.assertEqual(self.path.read_bytes(), before)

    def test_explorer_override_is_saved_without_materializing_default_fields(self):
        self.save({'workflow': {'main': {'model': 'main-only-model'}}})
        status, saved = self.run_setup('set', {'workflow': {'explore': {'reasoning': 'medium'}}})
        self.assertEqual(0, status, saved)
        self.assertEqual({'reasoning': 'medium'}, json.loads(self.path.read_text())['workflow']['explore'])
        self.assertEqual('gpt-6.1-sol', saved['effective']['workflow']['explore']['model'])
        resolved = subprocess.run([sys.executable, '-B', str(self.workflow / 'resolve_model_pair.py'), '--project-root', str(self.project), '--role', 'explorer'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, resolved.returncode, resolved.stderr)
        self.assertEqual('medium', json.loads(resolved.stdout)['thinking'])


    def test_zero_claude_budget_is_saved_shown_and_resolved_by_ask(self):
        self.save({'other': {'keep': 'Ä 中文'}})
        status, saved = self.run_setup('set', {'ask': {'claude': {'max_budget_usd': 0}}})
        self.assertEqual(status, 0, saved)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8')),
                         {'other': {'keep': 'Ä 中文'}, 'ask': {'claude': {'max_budget_usd': 0}}})
        before = self.path.read_bytes()
        status, shown = self.run_setup('show')
        self.assertEqual(status, 0, shown)
        self.assertEqual(shown['effective']['ask']['claude']['max_budget_usd'], 0)
        self.assertEqual(self.path.read_bytes(), before)
        helper = self.base / 'scoville-ask-for-codex/scoville-ask-for-codex/scripts/ask.py'
        resolved = subprocess.run([sys.executable, str(helper), '--project-root', str(self.project)],
                                  capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(resolved.returncode, 0, resolved.stdout + resolved.stderr)
        self.assertEqual(json.loads(resolved.stdout)['config']['claude']['max_budget_usd'], 0)

    def test_setup_is_codex_suite_only(self):
        for profile, layout, expected in [('codex', 'suite', True), ('codex', 'standalone', False),
                                          ('general', 'suite', False)]:
            config = builder.load(ROOT, profile, layout)
            self.assertEqual(any(m['name'] == 'scoville-setup' for m in config['members']), expected)


if __name__ == '__main__':
    unittest.main()
