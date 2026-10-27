from pathlib import Path
import hashlib
import html
import importlib.util
import json
import os
import subprocess
import shutil
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
# Exercise the actual package, including bundled shared helpers and defaults.
SUITE_ROOT = ROOT.parents[1]
_build_spec = importlib.util.spec_from_file_location("workflow_test_build", SUITE_ROOT / "development/build_suite.py")
_builder = importlib.util.module_from_spec(_build_spec)
_build_spec.loader.exec_module(_builder)
_test_package = tempfile.TemporaryDirectory(prefix="workflow-tests-", ignore_cleanup_errors=True)
PACKAGE = Path(_test_package.name) / "scoville-workflow-for-codex"
_config = _builder.load(SUITE_ROOT, 'codex')
_member = next(m for m in _config['members'] if m['name'] == PACKAGE.name)
for _package_member in (_member, *(m for m in _config['members'] if m['name'] in {'scoville-code', 'scoville-plan'})):
    for _name, _data in _builder.payload(SUITE_ROOT, _package_member, _config).items():
        _target = Path(_test_package.name) / _name
        _target.parent.mkdir(parents=True, exist_ok=True)
        _target.write_bytes(_data)
MODEL_RESOLVER = PACKAGE / "scripts/resolve_model_pair.py"
SELECTOR = SUITE_ROOT / "members/scoville-plan/scoville-plan/scripts/select_context.py"
sys.path.insert(0, str(PACKAGE / "scripts"))
import resolve_model_pair as model_resolver
import build_dispatch_prompt as prompt_builder


def copy_started_profile(root, step=1):
    shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
    plan = root / 'docs/plans/0001-validate-profile.md'
    text = plan.read_text(encoding='utf-8')
    for number, action in ((1, 'Read the canonical files.'), (2, 'Check the local record shapes.')):
        status = 'in_progress' if number == step else 'done' if number < step else 'todo'
        text = text.replace(f'{number}. {action}', f'{number}. [status: {status}] {action}')
    plan.write_text(text, encoding='utf-8', newline='\n')

class NativeWorkflowContractTests(unittest.TestCase):
    def test_configuration_mode_and_model_mode_are_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            base = [sys.executable, str(MODEL_RESOLVER), '--project-root', directory]
            for extra in ([], ['--show-config', '--role', 'reviewer']):
                failed = subprocess.run(base + extra, text=True, encoding='utf-8', capture_output=True)
                self.assertNotEqual(0, failed.returncode)
                self.assertIn('usage:', failed.stderr)
                self.assertIn('--show-config', failed.stderr)
            corrected = subprocess.run(base + ['--show-config'], text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(0, corrected.returncode, corrected.stderr)
            self.assertEqual({'schema_version', 'main', 'review', 'explore'}, set(json.loads(corrected.stdout)['config']))

    def test_model_resolver_rejects_malformed_user_config(self):
        source = (PACKAGE / 'assets/workflow.toml').read_text(encoding='utf-8')
        for old, new, field in [('schema_version = 2', 'schema_version = true', 'schema_version'),
                                ('reasoning = "xhigh"', 'reasoning = []', 'workflow.review'),
                                ('reasoning = "xhigh"', 'reasoning = { bad = true }', 'workflow.review')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                self.assertIn(old, source)
                value = source.replace(old, new, 1)
                target = Path(directory) / 'workflow.toml'
                target.write_text(value, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, field):
                    model_resolver.load_config(target, Path(directory))

    def test_fixed_pairs_have_no_model_route_or_one_call_override(self):
        config = model_resolver.load_config(PACKAGE / 'assets/workflow.toml', PACKAGE)
        self.assertEqual({'schema_version', 'main', 'review', 'explore'}, set(config))
        for role, key in [('main', 'main'), ('reviewer', 'review'), ('explorer', 'explore')]:
            self.assertEqual({'model': config[key]['model'], 'thinking': config[key]['reasoning']},
                             model_resolver.resolve(config, role))
        with self.assertRaises(ValueError):
            model_resolver.resolve(config, 'executor')

    def test_explicit_plan_reasoning_stays_original_for_all_supported_levels(self):
        fixture_spec = importlib.util.spec_from_file_location('reasoning_fixture', SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        for level in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'):
            with self.subTest(level=level), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'docs/plans').mkdir(parents=True)
                (root / 'docs/decisions').mkdir()
                (root / 'PROJECT_INDEX.md').write_text('---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n', encoding='utf-8')
                annotation = '[execute: reasoning=' + level + ']'
                (root / 'docs/plans/0001-test.md').write_text(fixture.plan().replace('1. Inspect the producer.', '1. ' + annotation + ' Inspect the producer.'), encoding='utf-8')
                (root / 'docs/decisions/0001-test.md').write_text(fixture.DECISION, encoding='utf-8')
                context = prompt_builder.select_unit(SELECTOR, root, 'W-003/step-1')
                prompt = prompt_builder.build_prompt('main', root, context, {}, 'German')
                self.assertIn(annotation, context['work_item']['source_text'])
                self.assertIn(annotation, prompt)


    def test_fixed_reviewer_needs_no_route_and_rejects_old_route_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(MODEL_RESOLVER), '--project-root', directory, '--role', 'reviewer']
            result = subprocess.run(command, text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(json.loads(result.stdout)['valid'])
            rejected = subprocess.run(command + ['--route', 'medium'], capture_output=True)
            self.assertNotEqual(0, rejected.returncode)

    def test_actual_selector_source_and_crlf_survive_dispatch(self):
        fixture_spec = importlib.util.spec_from_file_location('plan_fixture',
            SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        for ending in ('\n', '\r\n'):
            with self.subTest(ending=repr(ending)), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / 'Änderung 中文'
                (root / 'docs/plans').mkdir(parents=True)
                (root / 'docs/decisions').mkdir()
                files = {'PROJECT_INDEX.md': '---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n',
                         'docs/plans/0001-test.md': fixture.plan(10).replace(
                             'Evidence: [old executor attempt, old reviewer attempt]',
                             'Evidence: Prüfung mit Komma, Ergebnis erhalten.'),
                         'docs/decisions/0001-test.md': fixture.DECISION}
                for name, content in files.items():
                    (root / name).write_bytes(content.replace('\n', ending).encode('utf-8'))
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                for unit in ('W-003/step-1', 'W-003/step-2'):
                    context = prompt_builder.select_unit(SELECTOR, root, unit)
                    completed = subprocess.run([sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                        '--unit', unit, '--role', 'reviewer', '--communication-language', 'German', '--project-root', str(root),
                        ],
                        input='{}', text=True, encoding='utf-8', capture_output=True,
                        env={**os.environ, 'PYTHONIOENCODING': 'cp1252'})
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    prompt = completed.stdout
                    embedded = prompt.split('## Work Item context\n', 1)[1].split('On user stop,', 1)[0]
                    item = context['work_item']
                    if '/' not in unit:
                        self.assertEqual(embedded.rstrip() + '\n', item['context_text'])
                        self.assertEqual(prompt.count(item['context_text'].rstrip()), 1)
                    else:
                        self.assertIn('Steps:\n' + item['source_text'], embedded)
                        for step in prompt_builder.select_unit(SELECTOR, root, 'W-003')['work_item']['steps']:
                            if step not in item['steps']:
                                self.assertNotIn(step, embedded)
                        self.assertNotIn('Evidence:', embedded)
                        self.assertNotIn('Next action:', embedded)
                    self.assertIn('## Assigned unit\n' + unit, prompt)
                    self.assertFalse(prompt.startswith('{'))
                    for decision in context['decisions']:
                        self.assertIn(decision.replace('\r\n', '\n'), prompt)
                    self.assertIn(context['work_item']['acceptance'], prompt)
                    self.assertIn(context['work_item']['outcome'], prompt)
                    self.assertEqual(context['work_item']['unit'], unit)
                    self.assertTrue(context['work_item']['source_text'])
                for unit in ('W-003/step-1..2', 'W-003/step-0', 'W-999', 'W-003/step-4'):
                    with self.assertRaises(ValueError):
                        prompt_builder.select_unit(SELECTOR, root, unit)
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_dispatch_budget_failure_and_corrected_assignment_with_bundled_selector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            outcome = 'é' * 20_000 + ' END-OF-REQUIRED-CONTEXT'
            plan = root / 'docs/plans/0001-validate-profile.md'
            plan.write_text(plan.read_text(encoding='utf-8').replace('W-001', 'W-003').replace(
                'Outcome: The local record shapes are valid.', 'Outcome: ' + outcome), encoding='utf-8')
            assignment = root / 'assignment.md'
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            command = [sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                       '--communication-language', 'German', '--project-root', str(root), '--unit', 'W-003/step-1', '--role', 'reviewer',
                       '--format', 'create', '--project-name', 'Budget test',
                       '--agent-number', '1', '--assignment-file', str(assignment)]
            for extra, code in (([], 'OUTPUT_BUDGET_EXCEEDED'),
                                (['--max-output-bytes', '512'], 'OUTPUT_BUDGET_EXCEEDED'),
                                (['--max-output-bytes', '0'], 'OUTPUT_BUDGET_INVALID')):
                failed = subprocess.run(command + extra, text=True, encoding='utf-8', capture_output=True)
                self.assertEqual(failed.returncode, 1, failed.stderr)
                self.assertEqual(failed.stdout, '')
                diagnostic = json.JSONDecoder().raw_decode(failed.stderr.split('ERROR: Plan selection failed: ', 1)[1])[0]['diagnostics'][0]
                self.assertEqual(diagnostic['code'], code)
                if code == 'OUTPUT_BUDGET_EXCEEDED':
                    required = diagnostic['observed']['required_bytes']
                    self.assertGreater(required, 65_536)
                    self.assertIn(f'--max-output-bytes {required}', diagnostic['message'])
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            corrected = subprocess.run(command + ['--max-output-bytes', str(required)],
                                       text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            arguments = json.loads(corrected.stdout)
            self.assertEqual(set(arguments), {'message', 'task_name', 'fork_turns', 'model', 'reasoning_effort'})
            self.assertEqual(arguments['fork_turns'], 'none')
            self.assertIn(str(assignment), arguments['message'])
            self.assertIn('PLAN-0001/W-003/step-1', arguments['message'])
            # Consume the generated file as directed by the native message.
            prompt = assignment.read_text(encoding='utf-8')
            self.assertIn(outcome, prompt)
            self.assertIn('## Assigned unit\nW-003/step-1', prompt)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*')
                                      if p.is_file() and p != assignment})

    def test_normal_messages_pass_unchanged_to_review_and_correction(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'}, 'work_item': {'unit': 'W-001/step-1', 'source_text': '1. Work', 'header':'### W-001 Work', 'status':'Status: in_progress', 'depends_on':'Depends on: []', 'blocked_by':'Blocked by: []', 'decisions':'Decisions: []', 'outcome':'Outcome: Work', 'acceptance':'Acceptance: Work'}}
        for role, field, text in [
            ('reviewer', 'supplemental_context', 'Completed. Import checks passed. No rollback proof yet.'),
            ('main', 'reviewer_result', 'Changes requested. src/import.py: rollback leaves partial writes. Fix the transaction.')]:
            prompt = prompt_builder.build_prompt(role, PACKAGE, context,
                {field: text}, 'German')
            self.assertIn(text, prompt)
            self.assertNotIn('SCOVILLE_RESULT_V1', prompt)
            self.assertNotIn('code_changed=', prompt)
        with self.assertRaises(ValueError):
            prompt_builder.build_prompt('reviewer', PACKAGE, context, {'supplemental_context': ''}, 'German')

    def test_obsolete_transfer_inputs_are_rejected(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'},
                   'work_item': {'unit': 'W-001/step-1', 'source_text': '1. Work', 'header':'### W-001 Work', 'status':'Status: in_progress', 'depends_on':'Depends on: []', 'blocked_by':'Blocked by: []', 'decisions':'Decisions: []', 'outcome':'Outcome: Work', 'acceptance':'Acceptance: Work'}}
        for obsolete in ('context_handoff', 'predecessor_agent_id'):
            with self.subTest(obsolete=obsolete), self.assertRaises(ValueError):
                prompt_builder.build_prompt('main', PACKAGE, context, {obsolete: 'old'}, 'German')

    def test_failed_child_remaining_work_uses_ordinary_assignment(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'},
                   'work_item': {'unit': 'W-001/step-2', 'source_text': '2. Work\n',
                     'header': '### W-001 Work', 'status': 'Status: in_progress',
                     'depends_on': 'Depends on: []', 'blocked_by': 'Blocked by: []',
                     'decisions': 'Decisions: []', 'outcome': 'Outcome: B works.',
                     'acceptance': 'Acceptance: B checked.'}}
        facts = 'Prior writer confirmed stopped. A and its checks passed. Only B remains; no release.'
        prompt = prompt_builder.build_prompt('main', PACKAGE, context,
                                             {}, 'German')
        self.assertIn('2. Work', prompt)
        continued = prompt_builder.build_prompt('main', PACKAGE, context, {'supplemental_context': facts}, 'German')
        self.assertIn(facts, continued)
        self.assertIn('2. Work', continued)
        self.assertIn('## Work Item context', prompt)
        for forbidden in ('HANDOFF_ACCEPTED', 'TAKEOVER_COMPLETE', 'rollover_pending', 'check_context_checkpoint'):
            self.assertNotIn(forbidden, prompt)


if __name__ == '__main__':
    unittest.main()
