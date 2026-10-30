"""Exercise deadline configuration and the actual owned process family."""
import ctypes
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from test_ask_behavior import ask, prepare_request, ADVISERS


class ClaudeTimeoutTests(unittest.TestCase):
    def test_paid_answer_survives_raw_storage_failures_without_retry(self):
        import check_text_size
        cases = ((check_text_size, 'publish_full', PermissionError('denied')),
                 (check_text_size, 'publish_full', OSError('full disk')),
                 (check_text_size, 'publish_full', ValueError('redirected storage')),
                 (ask.ask_claude.tempfile, 'mkdtemp', PermissionError('private directory denied')))
        for owner, operation, failure in cases:
            with self.subTest(operation=operation, failure=type(failure).__name__), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                marker = root / 'once.txt'
                code = 'import sys;from pathlib import Path;sys.stdin.read();p=Path(sys.argv[1]);p.write_text(p.read_text()+"x" if p.exists() else "x");print(\'{"type":"result","is_error":false,"result":"PAID ANSWER","session_id":"s-1"}\')'
                request = {**self.request(), 'cwd': str(root)}
                with mock.patch.object(ask.ask_claude, 'resolve_claude_command', return_value=[sys.executable, '-c', code, str(marker)]), mock.patch.object(owner, operation, side_effect=failure) as publish:
                    result = ask.claude(request)
                self.assertEqual(result['answer'], 'PAID ANSWER')
                self.assertEqual(result['session_id'], 's-1')
                self.assertIsNone(result['raw_file'])
                self.assertIn(type(failure).__name__, result['raw_file_error'])
                self.assertEqual(marker.read_text(), 'x')
                publish.assert_called_once()

    def test_private_storage_avoids_shared_scoville_collision(self):
        import os
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').write_text('another user owns this path')
            with mock.patch.object(ask.ask_claude.tempfile, 'gettempdir', return_value=str(root)):
                result = ask.ask_claude.run_command([sys.executable, '-c', 'import sys;sys.stdin.read();print("ANSWER")'], root, 'question', 5)
            self.assertEqual(result.stdout.strip(), 'ANSWER')
            raw = Path(result.raw_file)
            self.assertIn(b'ANSWER', raw.read_bytes())
            self.assertTrue(raw.is_relative_to(root))
            self.assertNotEqual(raw.parents[2], root)
            if os.name != 'nt':
                self.assertEqual(raw.parents[2].stat().st_mode & 0o777, 0o700)

    def test_raw_invalid_utf8_is_saved_before_decoding_without_rerun(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / 'once.txt'
            code = 'import sys;from pathlib import Path;p=Path(sys.argv[1]);p.write_text(p.read_text()+"x" if p.exists() else "x");sys.stdout.buffer.write(b"\\xff");sys.stderr.buffer.write(b"private detail");sys.exit(7)'
            with self.assertRaises(RuntimeError) as caught:
                ask.ask_claude.run_command([sys.executable, '-c', code, str(marker)], root, 'literal café\n', 5)
            failure = caught.exception
            self.assertEqual(failure.exit_code, 7)
            self.assertTrue(failure.capture_complete)
            self.assertEqual(Path(failure.raw_file).read_bytes(),
                             b'exit=7 stdout_bytes=1 stderr_bytes=14\nstdout:\n\xff\nstderr:\nprivate detail')
            self.assertEqual(marker.read_text(), 'x')
            self.assertNotIn('private detail', str(failure))

    def request(self):
        return ask.prepare(prepare_request([ADVISERS[1]]))["entries"][0]["request"]

    def test_default_override_and_invalid_deadlines(self):
        request = self.request()
        result = subprocess.CompletedProcess([], 0, '{"result":"ok"}', '')
        with mock.patch.object(ask.ask_claude, 'resolve_claude_command', return_value=['fake']), mock.patch.object(ask.ask_claude, 'run_command', return_value=result) as run:
            ask.claude(request)
            self.assertEqual(run.call_args.args[3], 3600)
            ask.claude({**request, 'timeout_seconds': 7200})
            self.assertEqual(run.call_args.args[3], 7200)
            for value in (None, True, 0, -1, '60', float('inf'), float('nan')):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    ask.claude({**request, 'timeout_seconds': value})
        configured = ask.resolve({'overrides': {'advisers': ['fable'], 'claude': {'timeout_seconds': 5400}}})
        self.assertEqual(configured['config']['claude']['timeout_seconds'], 5400)

    def test_timeout_has_stable_error_code(self):
        request = {**self.request(), 'operation': 'claude'}
        with mock.patch.object(sys, 'stdin', io.StringIO(json.dumps(request))), mock.patch.object(sys, 'stdout', io.StringIO()) as output, mock.patch.object(ask.ask_claude, 'resolve_claude_command', return_value=['fake']), mock.patch.object(ask.ask_claude, 'run_command', side_effect=ask.ask_claude.ClaudeTimeout('deadline')) as run:
            self.assertEqual(ask.main(), 1)
            self.assertEqual(json.loads(output.getvalue()), {'ok': False, 'error': 'deadline', 'code': 'claude_timeout'})
            run.assert_called_once()

    @unittest.skipUnless(sys.platform == 'win32', 'Windows process-family integration')
    def test_wrapper_and_child_stop_but_control_survives(self):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        def alive(pid):
            handle = kernel.OpenProcess(0x100000, False, pid)
            if not handle:
                return False
            try:
                return kernel.WaitForSingleObject(handle, 0) == 258
            finally:
                kernel.CloseHandle(handle)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / 'wrapper.py'
            script.write_text("import os, subprocess, sys, time, json\nfrom pathlib import Path\nchild=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\nPath('pids.json').write_text(json.dumps([os.getpid(),child.pid]))\ntime.sleep(60)\n", encoding='utf-8')
            control = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                with self.assertRaises(ask.ask_claude.ClaudeTimeout) as caught:
                    ask.ask_claude.run_command([sys.executable, str(script)], root, 'question', 2)
                self.assertNotIn('could not be confirmed', str(caught.exception))
                pids = json.loads((root / 'pids.json').read_text())
                self.assertEqual(len(pids), 2)
                for pid in pids:
                    self.assertFalse(alive(pid), f'owned process {pid} survived')
                self.assertIsNone(control.poll())
            finally:
                control.kill()
                control.wait()

if __name__ == '__main__':
    unittest.main()
