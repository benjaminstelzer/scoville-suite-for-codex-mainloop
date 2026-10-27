"""Use the actual Plan selector, validator, package and native argument producer."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]


class MainloopDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.package.cleanup)
        spec = importlib.util.spec_from_file_location('mainloop_dispatch_builder', ROOT / 'development/build_suite.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        config = builder.load(ROOT)
        member = next(m for m in config['members'] if m['name'] == 'scoville-workflow-for-codex')
        for relative, data in builder.payload(ROOT, member, config).items():
            path = Path(cls.package.name) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        cls.helper = Path(cls.package.name) / member['name'] / 'scripts/build_dispatch_prompt.py'

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / 'project'
        self.project.mkdir()
        (self.project / 'docs/plans').mkdir(parents=True)
        (self.project / 'docs/decisions').mkdir()
        (self.project / 'PROJECT_INDEX.md').write_text('---\nformat_version: 1\nactive_plan: PLAN-9001\n---\n', encoding='utf-8')
        self.plan = self.project / 'docs/plans/9001-mainloop.md'
        self.write_plan()

    def write_plan(self, annotation='', state='in_progress'):
        self.plan.write_text(f'''---
format_version: 1
id: PLAN-9001
status: active
created: 2026-10-27
updated: 2026-10-27
current_item: W-001
---

# Controlled dispatch fixture

## Goal

Perform the two requested bounded changes.

## Non-goals

- No network or unrelated edits.

## Work items

### W-001 Bounded fixture changes

Status: in_progress
Depends on: []
Blocked by: []
Decisions: []
Outcome: The fixture implements its requested behavior.
Acceptance: Both bounded changes work; unrelated content remains preserved.
Instructions: []
Steps:
1. [status: {state}] {annotation}Change only alpha.txt and check the requested result.
2. [status: todo] NEXT_STEP_MUST_NOT_APPEAR: change beta.txt and check that result.
Evidence: []
''', encoding='utf-8')

    def run_dispatch(self, role, *flags, request=''):
        return subprocess.run([sys.executable, '-B', str(self.helper), '--role', role,
                               '--project-root', str(self.project), '--communication-language', 'German', *flags],
                              input=request, capture_output=True, encoding='utf-8')

    def create(self, role, *flags, request='checks: targeted check passed; scope: the selected change'):
        path = self.base / 'assignment.txt'
        result = self.run_dispatch(role, '--format', 'create', '--project-name', 'Fixture',
                                   '--agent-number', '1', '--assignment-file', str(path), *flags,
                                   '--supplemental-context', '-', request=request)
        return result, path

    def test_main_receives_exactly_one_original_step_without_spawn_or_role_reload(self):
        result = self.run_dispatch('main', '--unit', 'W-001/step-1')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Change only alpha.txt and check the requested result.', result.stdout)
        self.assertNotIn('NEXT_STEP_MUST_NOT_APPEAR', result.stdout)
        self.assertNotIn('# Shared writing rules', result.stdout)
        self.assertFalse((self.base / 'assignment.txt').exists())

    def test_main_needs_saved_start_and_cannot_be_spawned(self):
        self.write_plan(state='todo')
        result = self.run_dispatch('main', '--unit', 'W-001/step-1')
        self.assertNotEqual(0, result.returncode)
        self.write_plan()
        result, path = self.create('main', '--unit', 'W-001/step-1')
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(path.exists())

    def test_matching_partial_and_complete_execution_annotations_allow_main(self):
        for value in ['[execute: model=gpt-6.1-sol] ', '[execute: reasoning=high] ',
                      '[execute: model=gpt-6.1-sol; reasoning=high] ']:
            with self.subTest(value=value):
                self.write_plan(value)
                result = self.run_dispatch('main', '--unit', 'W-001/step-1')
                self.assertEqual(0, result.returncode, result.stderr)

    def test_conflicting_execution_annotation_needs_user_choice(self):
        self.write_plan('[execute: reasoning=xhigh] ')
        result = self.run_dispatch('main', '--unit', 'W-001/step-1')
        self.assertNotEqual(0, result.returncode)
        self.assertIn('reasoning=xhigh', result.stderr)
        self.assertIn('reasoning=high', result.stderr)

    def test_step_reviewer_is_fresh_and_uses_only_selected_step_and_supplied_evidence(self):
        result, path = self.create('reviewer', '--unit', 'W-001/step-1')
        self.assertEqual(0, result.returncode, result.stderr)
        arguments = json.loads(result.stdout)
        self.assertEqual(('gpt-6.1-sol', 'xhigh', 'none'),
                         (arguments['model'], arguments['reasoning_effort'], arguments['fork_turns']))
        assignment = path.read_text(encoding='utf-8')
        self.assertIn('Change only alpha.txt and check the requested result.', assignment)
        self.assertNotIn('NEXT_STEP_MUST_NOT_APPEAR', assignment)
        self.assertIn('checks: targeted check passed', assignment)
        self.assertIn('# Code review quality', assignment)
        self.assertNotIn('check_agent_context.py', assignment)

    def test_closure_contains_all_original_steps_and_full_acceptance(self):
        result, path = self.create('reviewer', '--unit', 'W-001')
        self.assertEqual(0, result.returncode, result.stderr)
        assignment = path.read_text(encoding='utf-8')
        self.assertIn('Closure review', assignment)
        self.assertIn('NEXT_STEP_MUST_NOT_APPEAR', assignment)
        self.assertIn('Both bounded changes work; unrelated content remains preserved.', assignment)

    def test_reviewer_reuse_rejected_before_assignment_publication(self):
        result, path = self.create('reviewer', '--unit', 'W-001/step-1', '--agent-id', 'existing-reviewer')
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(path.exists())

    def test_missing_fresh_dependencies_block_then_restored_call_succeeds(self):
        package = self.helper.parents[1]
        for relative in ('references/code-review.md', 'references/output-delivery.md',
                         'scripts/check_text_size.py'):
            with self.subTest(relative=relative):
                dependency = package / relative
                content = dependency.read_bytes()
                dependency.unlink()
                try:
                    result, path = self.create('reviewer', '--unit', 'W-001/step-1')
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn(str(dependency), result.stderr)
                    self.assertFalse(path.exists())
                finally:
                    dependency.write_bytes(content)
        result, path = self.create('reviewer', '--unit', 'W-001/step-1')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(path.exists())

    def test_explorer_reuse_has_only_new_question_and_retains_its_pair(self):
        result = self.run_dispatch('explorer', '--format', 'create', '--project-name', 'Fixture',
                                   '--agent-number', '1', '--agent-id', 'existing-explorer',
                                   '--model', 'gpt-6.1-sol', '--thinking', 'high',
                                   '--supplemental-context', '-', request='Find the owner of alpha.txt without changes.')
        self.assertEqual(0, result.returncode, result.stderr)
        arguments = json.loads(result.stdout)
        self.assertEqual('existing-explorer', arguments['target'])
        self.assertIn('Find the owner', arguments['message'])
        self.assertNotIn('# Shared writing rules', arguments['message'])

    def test_changed_explorer_pair_cannot_reuse_old_agent(self):
        (self.project / '.scoville').mkdir()
        (self.project / '.scoville/config.json').write_text(
            json.dumps({'workflow': {'explore': {'reasoning': 'xhigh'}}}), encoding='utf-8')
        result = self.run_dispatch('explorer', '--format', 'create', '--project-name', 'Fixture',
                                   '--agent-number', '1', '--agent-id', 'existing-explorer',
                                   '--model', 'gpt-6.1-sol', '--thinking', 'high',
                                   '--supplemental-context', '-', request='Find the owner.')
        self.assertNotEqual(0, result.returncode)
        self.assertIn('xhigh', result.stderr)


if __name__ == '__main__':
    unittest.main()
