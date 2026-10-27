"""Actual native argument and complete-file consumers for the two child roles."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

from test_contract import PACKAGE, SUITE_ROOT, _builder, _config, copy_started_profile


class NativeCreationTests(unittest.TestCase):
    def run_builder(self, script, *arguments, auto_file=True, auto_language=True):
        if auto_language and '--communication-language' not in arguments:
            arguments = (*arguments, '--communication-language', 'German')
        assignment = None
        if '--assignment-file' in arguments:
            assignment = Path(arguments[arguments.index('--assignment-file') + 1])
        elif auto_file and '--format' in arguments and arguments[arguments.index('--format') + 1] == 'create':
            root = Path(arguments[arguments.index('--project-root') + 1])
            assignment = root / f'child-assignment-{uuid.uuid4().hex}.txt'
            arguments = (*arguments, '--assignment-file', assignment)
        result = subprocess.run([sys.executable, '-B', str(PACKAGE / 'scripts' / script), *map(str, arguments)],
                                input='', capture_output=True, encoding='utf-8')
        result.auto_assignment = assignment
        return result

    def consume(self, result):
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        def spawn_agent(*, task_name, message, fork_turns, model, reasoning_effort):
            self.assertRegex(task_name, r'^scoville_(reviewer|explorer)_[1-9][0-9]*$')
            self.assertEqual('none', fork_turns)
            self.assertEqual('gpt-6.1-sol', model)
            self.assertEqual('xhigh' if task_name.startswith('scoville_reviewer_') else 'high', reasoning_effort)
            self.assertIsInstance(message, str)
            self.assertNotIn('send_message_to_thread', message)
        spawn_agent(**data)
        if result.auto_assignment is not None:
            self.assertTrue(result.auto_assignment.is_file())
            self.assertIn(str(result.auto_assignment), data['message'])
            if not hasattr(self, '_assignments'):
                self._assignments = {}
            self._assignments[data['message']] = result.auto_assignment
        self.assertEqual(1, self.prompt(data).count((PACKAGE / 'references/writing.md').read_text(encoding='utf-8')))
        return data

    def prompt(self, data):
        path = getattr(self, '_assignments', {}).get(data['message'])
        return path.read_text(encoding='utf-8') if path else data['message']

    def test_explicit_language_and_literal_request_reach_both_native_children(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            evidence = root / 'literal-input.txt'
            original = 'Original quote: "Keep English"; café 中文; `owner.py`.\n'
            evidence.write_bytes(original.encode('utf-8'))
            for role in ('explorer', 'reviewer'):
                for language in ('German', 'English'):
                    with self.subTest(role=role, language=language):
                        args = ['--project-root', root, '--unit', 'W-001/step-1', '--role', role,
                                '--communication-language', language, '--supplemental-context', evidence]
                        direct = self.run_builder('build_dispatch_prompt.py', *args)
                        self.assertEqual(0, direct.returncode, direct.stderr)
                        data = self.consume(self.run_builder('build_dispatch_prompt.py', *args, '--format', 'create',
                                                            '--project-name', 'Fixture', '--agent-number', '1'))
                        self.assertTrue(self.prompt(data).startswith(direct.stdout))
                        for value in (data['message'], self.prompt(data)):
                            self.assertIn(f'Communication language: {language}.', value)
                        self.assertIn(original, self.prompt(data))
                        self.assertNotIn('Check the local record shapes.', self.prompt(data))
                        self.assertEqual(original.encode('utf-8'), evidence.read_bytes())

    def test_invalid_language_publishes_nothing_then_corrected_call_is_usable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            question = root / 'question.txt'
            question.write_text('Read-only question.', encoding='utf-8')
            for index, invalid in enumerate((None, '', ' ', 'German\nEnglish', 'German\rEnglish')):
                assignment = root / f'assignment-{index}.txt'
                args = ['--project-root', root, '--role', 'explorer', '--supplemental-context', question,
                        '--format', 'create', '--project-name', 'Fixture', '--agent-number', '1', '--assignment-file', assignment]
                extra = [] if invalid is None else ['--communication-language', invalid]
                failed = self.run_builder('build_dispatch_prompt.py', *args, *extra, auto_file=False, auto_language=False)
                self.assertNotEqual(0, failed.returncode)
                self.assertEqual('', failed.stdout)
                self.assertFalse(assignment.exists())
                self.assertIn('--communication-language', failed.stderr)
                self.consume(self.run_builder('build_dispatch_prompt.py', *args, '--communication-language', 'German', auto_language=False))

    def test_explorer_question_needs_no_plan_and_rejects_review_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            facts = root / 'question.txt'
            facts.write_text('Question: Ä 中文 — "Wer besitzt dieses Verhalten?"', encoding='utf-8')
            base = ['--project-root', root, '--role', 'explorer', '--format', 'create', '--project-name', 'Fixture', '--agent-number', '1']
            self.assertNotEqual(0, self.run_builder('build_dispatch_prompt.py', *base).returncode)
            self.assertNotEqual(0, self.run_builder('build_dispatch_prompt.py', *base, '--supplemental-context', facts, '--reviewer-result', facts).returncode)
            value = self.consume(self.run_builder('build_dispatch_prompt.py', *base, '--supplemental-context', facts))
            self.assertIn(facts.read_text(encoding='utf-8'), self.prompt(value))
            self.assertFalse((root / 'PROJECT_INDEX.md').exists())

    def test_role_input_errors_then_complete_literal_safe_native_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project Ä 中文'
            copy_started_profile(root)
            for index, (flag, role) in enumerate([('--supplemental-context', 'reviewer'), ('--reviewer-result', 'reviewer'), ('--supplemental-context', 'explorer')]):
                source = base / f'input-{index}.txt'
                assignment = base / f'assignment-{index}.txt'
                args = ['--project-root', root, '--format', 'create', '--project-name', 'Fixture', '--agent-number', '1',
                        '--unit', 'W-001/step-1', '--role', role, '--assignment-file', assignment, flag, source]
                for invalid in (None, b'\xff'):
                    if invalid is not None:
                        source.write_bytes(invalid)
                    failed = self.run_builder('build_dispatch_prompt.py', *args)
                    self.assertNotEqual(0, failed.returncode)
                    self.assertEqual('', failed.stdout)
                    self.assertIn(flag, failed.stderr)
                    self.assertIn(str(source), failed.stderr)
                    self.assertIn('UTF-8', failed.stderr)
                    self.assertFalse(assignment.exists())
                literal = 'Complete text Ä 中文: `node -e "process.exit(17)"`, $(not-a-command), exact\\path.\n'
                source.write_bytes(literal.encode('utf-8'))
                value = self.consume(self.run_builder('build_dispatch_prompt.py', *args))
                self.assertIn(literal, self.prompt(value))
                self.assertEqual(literal.encode('utf-8'), source.read_bytes())

    def test_documented_fresh_command_is_usable_without_agent_repair(self):
        instructions = (PACKAGE / 'references/operations-dispatch.md').read_text(encoding='utf-8')
        examples = [block.strip() for block in re.findall(r'^```text\n(.*?)\n```$', instructions, re.S | re.M)
                    if 'build_dispatch_prompt.py' in block and '--format create' in block]
        self.assertEqual(1, len(examples))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project with spaces'
            copy_started_profile(root, step=2)
            command = examples[0].replace('PLAN-NNNN', 'PLAN-0001')
            for key, value in {'workflow': PACKAGE.as_posix(), 'absolute-workspace': root.as_posix(),
                               'project': 'Änderung 中文', 'number': '9', 'language': 'German'}.items():
                command = command.replace('<' + key + '>', value)
            self.assertNotRegex(command, r'<[^>]+>')
            external = Path(directory) / 'external'
            external.mkdir()
            env = dict(os.environ, TMPDIR=str(external), TEMP=str(external), TMP=str(external))
            result = subprocess.run([sys.executable, *shlex.split(command)[1:]], input='checks: scope checked; limits: none',
                                    capture_output=True, encoding='utf-8', env=env)
            self.assertEqual(0, result.returncode, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual('xhigh', data['reasoning_effort'])
            # Find the native message's actual existing path without fixing or
            # rewriting its wording. Automatic paths use the producer's prefix.
            candidates = [p for p in external.iterdir() if str(p) in data['message']]
            self.assertEqual(1, len(candidates))
            path = candidates[0]
            self.addCleanup(path.unlink, missing_ok=True)
            self.assertFalse(path.is_relative_to(root))
            self.assertIn('2. [status: in_progress] Check the local record shapes.', path.read_text(encoding='utf-8'))

    def test_automatic_assignment_paths_are_external_complete_and_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            external = Path(directory) / "Research before tests ü ' $()"
            external.mkdir()
            env = dict(os.environ, TMPDIR=str(external), TEMP=str(external), TMP=str(external))
            paths = set()
            for number in (1, 2):
                result = subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                    '--communication-language', 'German', '--project-root', str(root), '--format', 'create',
                    '--project-name', 'Fixture', '--agent-number', str(number), '--role', 'reviewer', '--unit', 'W-001/step-1'],
                    capture_output=True, encoding='utf-8', env=env)
                self.assertEqual(0, result.returncode, result.stderr)
                data = json.loads(result.stdout)
                candidates = [p for p in external.iterdir() if str(p) in data['message']]
                self.assertEqual(1, len(candidates))
                path = candidates[0]
                self.assertNotIn(path, paths)
                paths.add(path)
                self.assertIn('Work Item context', path.read_text(encoding='utf-8'))
                self.assertFalse(path.is_relative_to(root))

    def test_short_explorer_reuse_uses_native_message_without_new_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_builder('build_dispatch_prompt.py', '--project-root', root, '--role', 'explorer',
                '--format', 'create', '--project-name', 'Fixture', '--agent-number', '1', '--agent-id', '/root/explorer',
                '--model', 'gpt-6.1-sol', '--thinking', 'high', '--supplemental-context', '-',
                auto_file=False)
            # This call has no stdin and must reject its empty request, without
            # creating a file or accidentally reinitializing the role.
            self.assertNotEqual(0, result.returncode)
            question = root / 'question.txt'
            question.write_text('Find only the requested owner.', encoding='utf-8')
            result = self.run_builder('build_dispatch_prompt.py', '--project-root', root, '--role', 'explorer',
                '--format', 'create', '--project-name', 'Fixture', '--agent-number', '1', '--agent-id', '/root/explorer',
                '--model', 'gpt-6.1-sol', '--thinking', 'high', '--supplemental-context', question, auto_file=False)
            self.assertEqual(0, result.returncode, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual({'target', 'message'}, set(value))
            self.assertEqual('/root/explorer', value['target'])
            self.assertIn(question.read_text(encoding='utf-8'), value['message'])
            self.assertNotIn('# Shared writing rules', value['message'])
            self.assertEqual([question], list(root.iterdir()))

    def test_repeated_reviews_spawn_with_distinct_names_and_full_initialization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            names = set()
            for number in (1, 2):
                value = self.consume(self.run_builder('build_dispatch_prompt.py', '--project-root', root,
                    '--role', 'reviewer', '--unit', 'W-001/step-1', '--format', 'create',
                    '--project-name', 'Fixture', '--agent-number', str(number)))
                self.assertNotIn(value['task_name'], names)
                names.add(value['task_name'])
                self.assertIn(f'SC-REV-{number}:', self.prompt(value))

    def test_invalid_native_inputs_publish_nothing_then_corrected_call_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            for index, extra in enumerate([['--model', ''], ['--thinking', 'low'], ['--agent-number', '0'],
                                            ['--agent-id', '/root/old-reviewer']]):
                path = Path(directory) / f'assignment-{index}.txt'
                base = ['--project-root', root, '--role', 'reviewer', '--unit', 'W-001/step-1', '--format', 'create',
                        '--project-name', 'Fixture', '--agent-number', '1', '--assignment-file', path]
                failed = self.run_builder('build_dispatch_prompt.py', *base, *extra)
                self.assertNotEqual(0, failed.returncode)
                self.assertEqual('', failed.stdout)
                self.assertFalse(path.exists())
                self.consume(self.run_builder('build_dispatch_prompt.py', *base))

    def test_assignment_overwrite_and_wrong_output_mode_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            path = Path(directory) / 'assignment.txt'
            path.write_text('keep', encoding='utf-8')
            args = ['--project-root', root, '--role', 'reviewer', '--unit', 'W-001/step-1', '--format', 'create',
                    '--project-name', 'Fixture', '--agent-number', '1', '--assignment-file', path]
            failed = self.run_builder('build_dispatch_prompt.py', *args)
            self.assertNotEqual(0, failed.returncode)
            self.assertEqual('keep', path.read_text(encoding='utf-8'))
            invalid = self.run_builder('build_dispatch_prompt.py', '--project-root', root, '--role', 'main',
                '--unit', 'W-001/step-1', '--assignment-file', Path(directory) / 'new.txt')
            self.assertNotEqual(0, invalid.returncode)
            self.assertFalse((Path(directory) / 'new.txt').exists())

    def test_builder_does_not_require_unselected_sibling_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            copy_started_profile(root)
            isolated = base / 'only-workflow'
            shutil.copytree(PACKAGE, isolated)
            assignment = base / 'assignment.txt'
            result = subprocess.run([sys.executable, '-B', str(isolated / 'scripts/build_dispatch_prompt.py'),
                '--project-root', str(root), '--role', 'reviewer', '--unit', 'W-001/step-1',
                '--communication-language', 'German', '--format', 'create', '--project-name', 'Fixture',
                '--agent-number', '1', '--assignment-file', str(assignment)],
                capture_output=True, encoding='utf-8')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(assignment.exists())

    def test_atomic_publication_collision_failure_and_corrected_call(self):
        from unittest.mock import patch
        import native_task_arguments as native
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'assignment Ä 中文.txt'
            content = 'Complete assignment with Unicode Ä 中文.\n' * 100
            native.publish_assignment(target, content)
            self.assertEqual(target.read_bytes(), content.encode('utf-8'))
            with self.assertRaisesRegex(ValueError, 'already exists'):
                native.publish_assignment(target, 'Overwrite.')
            self.assertEqual(target.read_bytes(), content.encode('utf-8'))
            failed = root / 'failed.txt'
            with patch.object(native.os, 'link', side_effect=OSError('unsupported filesystem')):
                with self.assertRaisesRegex(ValueError, 'atomic hard links'):
                    native.publish_assignment(failed, content)
            self.assertFalse(failed.exists())
            self.assertEqual(list(root.glob('.scoville-assignment-*.tmp')), [])
            native.publish_assignment(failed, content)
            self.assertEqual(failed.read_bytes(), content.encode('utf-8'))
            partial = root / 'partial.txt'
            real_temporary = native.tempfile.NamedTemporaryFile
            class PartialWrite:
                def __init__(self, *args, **kwargs):
                    self.stream = real_temporary(*args, **kwargs)
                def __enter__(self):
                    self.stream.__enter__()
                    self.name = self.stream.name
                    return self
                def write(self, data):
                    self.stream.write(data[:10])
                    raise OSError('partial temporary write failed')
                def __exit__(self, *args):
                    return self.stream.__exit__(*args)
            with patch.object(native.tempfile, 'NamedTemporaryFile', PartialWrite):
                with self.assertRaisesRegex(ValueError, 'partial temporary write failed'):
                    native.publish_assignment(partial, content)
            self.assertFalse(partial.exists())
            self.assertEqual(list(root.glob('.scoville-assignment-*.tmp')), [])
            native.publish_assignment(partial, content)
            self.assertEqual(partial.read_bytes(), content.encode('utf-8'))
            with patch.object(native.tempfile, 'gettempdir', return_value=str(root)):
                with self.assertRaisesRegex(ValueError, 'outside the project'):
                    native.assignment_path(None, root)
            with self.assertRaisesRegex(ValueError, 'existing absolute directory'):
                native.assignment_path(Path('relative.txt'), root)



if __name__ == '__main__':
    unittest.main()
