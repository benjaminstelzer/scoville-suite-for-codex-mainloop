"""Packaged route and saved-position integration; native dispatch is tested live."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

from test_contract import PACKAGE, SUITE_ROOT, copy_started_profile


class SimplifiedHelpersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        copy_started_profile(self.root)
        self.plan = self.root / 'docs/plans/0001-validate-profile.md'
        self.original = self.plan.read_text(encoding='utf-8')
        self.scope = self.root / 'scope.txt'
        self.scope.write_text('Auftrag erhalten: Text prüfen.', encoding='utf-8')
        self.result = self.root / 'result.txt'
        self.result.write_text('completed: original effects retained', encoding='utf-8')
        self.config = self.root / '.scoville/config.json'
        self.config.parent.mkdir()
        self.config.write_text(json.dumps({'workflow': {
            'schema_version': 2, 'main': {'model': 'gpt-6.1-sol', 'reasoning': 'high'},
            'review': {'model': 'gpt-6.1-sol', 'reasoning': 'xhigh'},
            'explore': {'model': 'gpt-6-luna', 'reasoning': 'medium'}}}), encoding='utf-8')

    def cli(self, name, *args, error=None):
        result = subprocess.run([sys.executable, '-B', str(PACKAGE / 'scripts' / name), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8')
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            self.assertIn(error, result.stderr)
            return
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def dispatch(self, *args, role='reviewer', error=None):
        if '--assignment-file' not in args:
            args = (*args, '--assignment-file', self.root / f'assignment-{uuid.uuid4().hex}.txt')
        return self.cli('build_dispatch_prompt.py', '--communication-language', 'German', '--project-root', self.root,
                        '--unit', 'W-001/step-1', '--role', role, '--format', 'create',
                        '--project-name', 'test',
                        '--agent-number', '1', *args, error=error)

    def test_fixed_pairs_follow_config_and_explorer_reuse_keeps_pair(self):
        actual = self.dispatch('--supplemental-context', self.scope, role='explorer')
        self.assertEqual(('gpt-6-luna', 'medium'), (actual['model'], actual['reasoning_effort']))
        reviewed = self.dispatch('--supplemental-context', self.result)
        self.assertEqual(('gpt-6.1-sol', 'xhigh'), (reviewed['model'], reviewed['reasoning_effort']))
        self.dispatch('--route', 'medium', error='unrecognized arguments')
        self.dispatch('--model', 'gpt-6-astra', '--thinking', 'high', error='fixed')
        self.dispatch('--agent-id', '/root/reviewer1', '--model', 'gpt-6.1-sol', '--thinking', 'xhigh', error='fresh')
        self.dispatch('--agent-id', '/root/explorer1', '--model', 'gpt-6.1-sol', '--thinking', 'high',
                      '--supplemental-context', self.scope, role='explorer', error='fixed')

    def test_assignment_delivery_tools_reach_actual_complete_file_consumer(self):
        payload = self.root / 'complete Grüße 中文.txt'
        payload.write_text('completed: full result\nRequired final fact: Grüße 中文.\n', encoding='utf-8')
        cases = [
            ('explorer', ['--supplemental-context', self.scope]),
            ('reviewer', ['--supplemental-context', self.result]),
            ('reviewer', ['--reviewer-result', self.result]),
        ]
        for role, extra in cases:
            with self.subTest(role=role, extra=extra):
                assignment = self.root / f'delivery-{uuid.uuid4().hex}.txt'
                carrier = self.dispatch(*extra, '--assignment-file', assignment, role=role)
                self.assertIn(str(assignment), carrier['message'])
                fields = dict(line.split(': ', 1) for line in assignment.read_text(encoding='utf-8').splitlines()
                              if line.startswith(('text_size_checker: ', 'python: ')))
                self.assertEqual(fields['python'], sys.executable)
                self.assertEqual(Path(fields['text_size_checker']), (PACKAGE / 'scripts/check_text_size.py').resolve())
                consumed = subprocess.run([fields['python'], fields['text_size_checker'], '--file', str(payload),
                                           '--publish-full', '--project-root', str(self.root)],
                                          capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(consumed.returncode, 0, consumed.stderr)
                metadata = json.loads(consumed.stdout)
                received = Path(metadata['full_file']).read_bytes()
                self.assertEqual(received, payload.read_bytes())
                self.assertNotIn('sha256', metadata)
                self.assertEqual(metadata['status'], 'complete_file')
                self.assertNotIn('tool_output_limit_tokens', metadata)

    def test_old_replacement_protocol_cannot_publish(self):
        self.dispatch('--replacement-of', '/root/prior', error='unrecognized arguments')

    def test_missing_delivery_checker_prevents_assignment_then_restoration_succeeds(self):
        suite = Path(self.temp.name) / 'copied suite'
        copy = suite / PACKAGE.name
        shutil.copytree(PACKAGE, copy)
        shutil.copytree(PACKAGE.parent / 'scoville-code', suite / 'scoville-code')
        checker = copy / 'scripts/check_text_size.py'
        original = checker.read_bytes()
        checker.unlink()
        assignment = self.root / 'restored-checker-assignment.txt'
        command = [sys.executable, '-B', str(copy / 'scripts/build_dispatch_prompt.py'),
                   '--communication-language', 'German', '--project-root', str(self.root), '--unit', 'W-001/step-1', '--role', 'reviewer',
                   '--format', 'create', '--project-name', 'test',
                   '--agent-number', '1', '--assignment-file', str(assignment)]
        failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(failed.stdout, '')
        self.assertIn(str(checker.resolve()), failed.stderr)
        self.assertIn('restore', failed.stderr)
        self.assertFalse(assignment.exists())
        checker.write_bytes(original)
        corrected = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        self.assertIn(str(assignment), json.loads(corrected.stdout)['message'])
        self.assertIn(str(checker.resolve()), assignment.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
