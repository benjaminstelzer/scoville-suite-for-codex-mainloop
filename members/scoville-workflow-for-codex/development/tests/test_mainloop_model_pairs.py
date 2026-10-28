"""Fixed model defaults and real resolver inputs, independent of old dispatch."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]


class FixedPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.package.cleanup)
        spec = importlib.util.spec_from_file_location('mainloop_test_builder', ROOT / 'development/build_suite.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        config = builder.load(ROOT, 'codex')
        member = next(m for m in config['members'] if m['name'] == 'scoville-workflow-for-codex')
        for relative, content in builder.payload(ROOT, member, config).items():
            path = Path(cls.package.name) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        cls.member = Path(cls.package.name) / member['name']
        scripts = str(cls.member / 'scripts')
        sys.path.insert(0, scripts)
        cls.addClassCleanup(sys.path.remove, scripts)
        spec = importlib.util.spec_from_file_location('mainloop_pairs', cls.member / 'scripts/resolve_model_pair.py')
        cls.pairs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.pairs)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sessions = self.root / 'sessions'
        self.sessions.mkdir()
        self.session = self.sessions / 'rollout-main-1.jsonl'
        self.environment = patch.dict(os.environ, CODEX_THREAD_ID='main-1', CODEX_HOME=str(self.root))
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def write_session(self, *, identity='main-1', source='vscode', context=None, terminal=None):
        values = [
            {'type': 'session_meta', 'payload': {'id': identity, 'source': source}},
            {'type': 'event_msg', 'payload': {'type': 'task_started', 'turn_id': 'turn-2'}},
            {'type': 'turn_context', 'payload': context if context is not None else
             {'turn_id': 'turn-2', 'model': 'gpt-6.1-sol', 'effort': 'high'}},
        ]
        if terminal:
            values.append({'type': 'event_msg', 'payload': {'type': terminal, 'turn_id': 'turn-2'}})
        self.session.write_text(''.join(json.dumps(dict(ordinal=i, **value)) + '\n'
                                        for i, value in enumerate(values)), encoding='utf-8')

    def invoke(self, *args):
        return subprocess.run([sys.executable, '-B', str(self.member / 'scripts/resolve_model_pair.py'),
                               '--project-root', str(self.root), *args],
                              text=True, capture_output=True, encoding='utf-8')

    def save(self, workflow):
        path = self.root / '.scoville/config.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({'workflow': workflow}), encoding='utf-8')

    def test_user_selected_defaults_reach_native_child_arguments(self):
        for role, effort in [('reviewer', 'xhigh'), ('explorer', 'high')]:
            with self.subTest(role=role):
                result = self.invoke('--role', role)
                self.assertEqual(0, result.returncode, result.stderr)
                value = json.loads(result.stdout)
                self.assertTrue(value['valid'])
                self.assertEqual(('gpt-6.1-sol', effort), (value['model'], value['thinking']))
                self.assertNotIn('route', value)

    def test_active_own_native_pair_matches(self):
        self.write_session()
        result = self.invoke('--role', 'main', '--session-path', str(self.session))
        self.assertEqual(0, result.returncode, result.stderr)
        value = json.loads(result.stdout)
        self.assertTrue(value['valid'])
        self.assertEqual(('main-1', 'turn-2'), (value['thread_id'], value['turn_id']))

    def test_mismatch_rejects_then_correct_host_evidence_passes(self):
        self.write_session(context={'turn_id': 'turn-2', 'model': 'gpt-6.1-sol', 'effort': 'xhigh'})
        result = self.invoke('--role', 'main')
        self.assertEqual(1, result.returncode)
        diagnostic = json.loads(result.stdout)['diagnostic']
        self.assertIn('gpt-6.1-sol/high', diagnostic)
        self.assertIn('gpt-6.1-sol/xhigh', diagnostic)
        self.write_session()
        self.assertEqual(0, self.invoke('--role', 'main').returncode)

    def test_own_main_identity_and_current_turn_are_required(self):
        for override in [
            {'identity': 'other-1'},
            {'source': {'subagent': {'thread_spawn': {'parent_thread_id': 'parent-1'}}}},
            {'context': {'turn_id': 'old-turn', 'model': 'gpt-6.1-sol', 'effort': 'high'}},
            {'context': {'turn_id': 'turn-2', 'model': 'gpt-6.1-sol'}},
            {'terminal': 'task_complete'}, {'terminal': 'task_failed'}, {'terminal': 'task_aborted'},
        ]:
            with self.subTest(override=override):
                self.write_session(**override)
                result = self.invoke('--role', 'main', '--session-path', str(self.session))
                self.assertEqual(1, result.returncode)
                self.assertFalse(json.loads(result.stdout)['valid'])

    def test_native_proof_failures_do_not_fall_back_to_an_older_valid_pair(self):
        for tail in (b'{"type":"turn_context"', b'{"type":"turn_context","payload":invalid}\n'):
            with self.subTest(tail=tail):
                self.write_session()
                with self.session.open('ab') as stream:
                    stream.write(tail)
                failed = self.invoke('--role', 'main')
                self.assertEqual(1, failed.returncode)
                self.assertFalse(json.loads(failed.stdout)['valid'])
        self.write_session()
        duplicate = self.sessions / 'duplicate-main-1.jsonl'
        duplicate.write_bytes(self.session.read_bytes())
        self.assertEqual(1, self.invoke('--role', 'main').returncode)
        # The retained explicit identity disambiguates discovery without weakening its checks.
        self.assertEqual(0, self.invoke('--role', 'main', '--session-path', str(self.session)).returncode)
        duplicate.unlink()
        with patch.dict(os.environ, CODEX_THREAD_ID=''):
            self.assertEqual(1, self.invoke('--role', 'main').returncode)
        self.assertEqual(0, self.invoke('--role', 'main').returncode)

    def test_reverse_reader_preserves_large_records_without_repeating_bytes(self):
        self.write_session()
        with self.session.open('ab') as stream:
            stream.write((json.dumps({'ordinal': 3, 'type': 'response_item',
                                      'payload': 'x' * 431000}) + '\n').encode())
        with self.session.open('rb') as stream:
            actual = list(self.pairs.reverse_lines(stream))
        expected = [line for line in reversed(self.session.read_bytes().split(b'\n')) if line]
        self.assertEqual(len(expected), len(actual))
        self.assertTrue(all(left == right for left, right in zip(expected, actual)),
                        'Reverse reading changed complete record bytes at a chunk boundary')
        self.assertEqual('high', self.pairs.main_pair(self.session)['thinking'])

    def test_legacy_workflow_needs_explicit_cleanup_without_write(self):
        for value in [{'schema_version': 1}, {'execute': {}},
                      {'review': {'low': {'model': 'old', 'reasoning': 'high'}}},
                      {'context_threshold_percent': 50}]:
            with self.subTest(value=value):
                self.save(value)
                before = (self.root / '.scoville/config.json').read_bytes()
                result = self.invoke('--role', 'reviewer')
                self.assertEqual(1, result.returncode)
                self.assertIn('cleanup', json.loads(result.stdout)['diagnostic'].lower())
                self.assertEqual(before, (self.root / '.scoville/config.json').read_bytes())

    def test_fixed_overrides_preserve_supported_special_efforts(self):
        self.save({'schema_version': 2, 'review': {'reasoning': 'ultra'}})
        result = self.invoke('--role', 'reviewer')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('ultra', json.loads(result.stdout)['thinking'])
        self.assertEqual('high', json.loads(self.invoke('--role', 'explorer').stdout)['thinking'])

    def test_removed_executor_and_route_cannot_silently_select_a_pair(self):
        for args in [('--role', 'executor'), ('--role', 'reviewer', '--route', 'high')]:
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertNotEqual(0, result.returncode)
                self.assertTrue(result.stderr)


if __name__ == '__main__':
    unittest.main()
