"""Keep the compact new-file route within the existing attribution boundary."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from test_contract import PACKAGE, SELECTOR, copy_started_profile, prompt_builder


class CompactNewFileTests(unittest.TestCase):
    def test_same_step_and_complete_report_survive_new_file_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            context = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            report = 'status: done\nchanges: created.py adds the requested helper; dist/ holds generated copies\nchecks: generator exited 0; expected outputs created in this run\nproblems: none\nlimits: none\n'
            new_file = 'NEW_FILE_CONTENT_READ_SEPARATELY = True\n'
            (root / 'created.py').write_text(new_file, encoding='utf-8')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            execution = prompt_builder.build_prompt('main', root, context, {}, 'German')
            review = prompt_builder.build_prompt('reviewer', root, context, {'supplemental_context': report}, 'German')
            self.assertIn('## supplemental_context\n' + report, review)
            self.assertIn('1. [status: in_progress] Read the canonical files.', review)
            self.assertNotIn('Check the local record shapes.', review)
            self.assertNotIn(new_file, execution)
            self.assertNotIn(new_file, review)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_main_retains_rules_explorer_reuses_and_reviews_are_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            context = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            inputs = {'supplemental_context': 'checks: observed; limits: none'}
            main = prompt_builder.build_prompt('main', root, context, inputs, 'German')
            fresh = prompt_builder.build_prompt('explorer', root, {}, inputs, 'German')
            reuse = prompt_builder.build_prompt('explorer', root, {}, inputs, 'German', reuse=True)
            review = prompt_builder.build_prompt('reviewer', root, context, inputs, 'German')
            for filename in ('writing.md', 'shell-commands.md'):
                rules = (PACKAGE / 'references' / filename).read_text(encoding='utf-8')
                self.assertNotIn(rules, main)
                self.assertNotIn(rules, reuse)
                self.assertEqual(1, fresh.count(rules))
                self.assertEqual(1, review.count(rules))
            quality = (PACKAGE / 'references/code-review.md').read_text(encoding='utf-8')
            self.assertEqual(1, review.count(quality))
            self.assertNotIn(quality, main + reuse + fresh)
            for text in (main, fresh, reuse, review):
                self.assertIn(inputs['supplemental_context'], text)
                if text != main:
                    self.assertIn('Communication language: German.', text)
            with self.assertRaises(ValueError):
                prompt_builder.build_prompt('reviewer', root, context, inputs, 'German', reuse=True)

    def test_missing_quality_blocks_review_but_not_main_or_explorer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            context = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            inputs = {'supplemental_context': 'checks: observed; limits: none'}
            copy = Path(directory) / 'package'
            shutil.copytree(PACKAGE, copy)
            policy = copy / 'references/code-review.md'
            original = policy.read_bytes()
            policy.unlink()
            with mock.patch.object(prompt_builder, '__file__', str(copy / 'scripts/build_dispatch_prompt.py')):
                with self.assertRaisesRegex(ValueError, 'bundled dependency missing.*code-review.md'):
                    prompt_builder.build_prompt('reviewer', root, context, inputs, 'German')
                prompt_builder.build_prompt('explorer', root, {}, inputs, 'German', reuse=True)
                prompt_builder.build_prompt('main', root, context, {}, 'German')
                policy.write_bytes(original)
                corrected = prompt_builder.build_prompt('reviewer', root, context, inputs, 'German')
                self.assertEqual(1, corrected.count(original.decode('utf-8')))


if __name__ == '__main__':
    unittest.main()
