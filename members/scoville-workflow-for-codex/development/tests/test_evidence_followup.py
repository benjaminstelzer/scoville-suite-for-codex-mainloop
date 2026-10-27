"""Preserve complete results and unresolved review in packaged follow-ups."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, copy_started_profile


class EvidenceFollowupTests(unittest.TestCase):
    def test_blocked_evidence_and_normal_correction_use_unchanged_role_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            copy_started_profile(root)
            original_step = '1. [status: in_progress] Read the canonical files.'
            blockers = (
                'status: blocked\nblocker: Required runtime check result is missing.\nlimits: Change remains unreviewed.\n',
                'status: changes_requested\nfindings: owner.py returns a string; return a number. Step 1.\n',
            )
            final = ('status: done\nchanges: owner.py applies the requested discount\n'
                     'checks: unchanged previous check passed\nproblems: none\nlimits: none\n')
            for index, review in enumerate(blockers):
                review_file = Path(folder) / f'review-{index}.txt'
                final_file = Path(folder) / f'executor-{index}.txt'
                review_file.write_text(review, encoding='utf-8')
                final_file.write_text(final, encoding='utf-8')
                for role in ('main', 'reviewer'):
                    assignment = Path(folder) / f'assignment-{index}-{role}.txt'
                    command = [sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                               '--project-root', str(root), '--unit', 'W-001/step-1', '--role', role,
                               '--communication-language', 'German', '--reviewer-result', str(review_file)]
                    if role == 'reviewer':
                        command += ['--format', 'create', '--project-name', 'fixture', '--agent-number', '1', '--assignment-file', str(assignment)]
                    if role == 'reviewer':
                        command += ['--supplemental-context', str(final_file)]
                    elif index == 0:
                        command += ['--supplemental-context', str(final_file)]
                    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if role == 'reviewer':
                        self.assertIn(str(assignment), json.loads(result.stdout)['message'])
                        prompt = assignment.read_text(encoding='utf-8')
                    else:
                        prompt = result.stdout
                    self.assertIn(original_step, prompt)
                    self.assertNotIn('Check the local record shapes.', prompt)
                    self.assertIn('## reviewer_result\n' + review, prompt)
                    if role == 'reviewer' or index == 0:
                        self.assertIn('## supplemental_context\n' + final, prompt)
                    self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
                    self.assertEqual(review_file.read_text(encoding='utf-8'), review)
                    self.assertEqual(final_file.read_text(encoding='utf-8'), final)

    def test_prior_evidence_alone_is_preserved_and_empty_inputs_block_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            copy_started_profile(root)
            result_file = Path(folder) / 'result.txt'
            review_file = Path(folder) / 'review.txt'
            result_file.write_text('status: done\nchanges: owner.py\n', encoding='utf-8')
            review_file.write_text('status: blocked\nblocker: Required runtime check result is missing.\n', encoding='utf-8')
            common = [sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                      '--project-root', str(root), '--unit', 'W-001/step-1', '--role', 'reviewer',
                      '--communication-language', 'German', '--format', 'create', '--project-name', 'fixture',
                      '--agent-number', '1', '--supplemental-context', str(result_file)]
            assignment = Path(folder) / 'continued.txt'
            prior = ('status: blocked\nchanges: owner.py returns the calculated price as text\n'
                     'checks: required lint still pending\nlimits: none\n')
            result_file.write_text(prior, encoding='utf-8')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = subprocess.run(common + ['--assignment-file', str(assignment)],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = assignment.read_text(encoding='utf-8')
            self.assertIn('## supplemental_context\n' + prior, prompt)
            self.assertNotIn('## reviewer_result', prompt)
            self.assertIn('1. [status: in_progress] Read the canonical files.', prompt)
            self.assertNotIn('Check the local record shapes.', prompt)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.assertEqual(result_file.read_text(encoding='utf-8'), prior)
            for number, (previous, review) in enumerate((('', None), (' ', 'status: blocked'),
                                                       ('status: done', ''))):
                assignment = Path(folder) / f'invalid-{number}.txt'
                result_file.write_text(previous, encoding='utf-8')
                extra = []
                if review is not None:
                    review_file.write_text(review, encoding='utf-8')
                    extra += ['--reviewer-result', str(review_file)]
                result = subprocess.run(common + extra + ['--assignment-file', str(assignment)],
                                        capture_output=True, text=True, encoding='utf-8')
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                error = next(line for line in result.stderr.splitlines() if line.startswith('ERROR: '))
                self.assertTrue('--supplemental-context' in error or '--reviewer-result' in error)
                self.assertFalse(assignment.exists())



if __name__ == '__main__':
    unittest.main()
