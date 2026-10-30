#!/usr/bin/env python3
"""Claude CLI command and response adapter; settings belong to config.default.json."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

READ_ONLY_TOOLS = "Read,Grep,Glob"


def configure_standard_streams() -> None:
    input_reconfigure = getattr(sys.stdin, "reconfigure", None)
    if callable(input_reconfigure):
        input_reconfigure(encoding="utf-8-sig", errors="strict")

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def resolve_claude_command() -> list[str]:
    executable = shutil.which("claude")
    if executable is None:
        raise RuntimeError("Claude Code CLI was not found on PATH")

    path = Path(executable)
    if path.suffix.lower() == ".ps1":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell is None:
            raise RuntimeError("Claude resolves to a PowerShell script, but no PowerShell executable was found")
        return [powershell, "-NoProfile", "-File", str(path)]

    return [str(path)]


def parse_claude_result(raw_output: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise ValueError(f"Claude returned invalid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("Claude returned JSON that is not an object")
    return payload


def claude_error_details(payload: dict[str, Any]) -> str | None:
    subtype = payload.get("subtype")
    has_error_subtype = isinstance(subtype, str) and subtype.startswith("error")
    if payload.get("is_error") is not True and not has_error_subtype:
        return None

    errors = payload.get("errors")
    if isinstance(errors, list):
        messages = [message for message in errors if isinstance(message, str)]
        if messages:
            return "; ".join(messages)

    for key in ("result", "terminal_reason", "subtype"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return "Claude reported an unspecified error"


def session_mode(args) -> str:
    if args.resume:
        return "resume"
    if args.session_persistence_default:
        return "persistent"
    return "fresh"


def build_command(args, claude_command: list[str]) -> list[str]:
    allowed_tools = READ_ONLY_TOOLS + (",WebSearch,WebFetch" if args.web_tools else "")
    command = [
        *claude_command,
        "-p",
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--output-format",
        "json",
        "--permission-mode",
        "dontAsk",
        "--tools",
        allowed_tools,
        "--allowed-tools",
        allowed_tools,
    ]

    if args.max_budget_usd != 0:
        command.extend(["--max-budget-usd", str(args.max_budget_usd)])

    mode = session_mode(args)
    if mode == "fresh":
        command.append("--no-session-persistence")
    elif mode == "resume":
        command.extend(["--resume", args.resume])

    if not args.customizations_enabled:
        command.append("--safe-mode")

    return command


class ClaudeTimeout(RuntimeError):
    """The consultation exceeded its deadline; no retry is implied."""


def temporary_root(workspace_root=None) -> Path:
    """Use an exclusive user-owned directory, never a shared .scoville path."""
    base = Path(tempfile.gettempdir()).resolve()
    if workspace_root is not None and base.is_relative_to(workspace_root.resolve()):
        raise ValueError('automatic assignment storage is inside the reviewed workspace; select a system temporary directory outside it')
    return Path(tempfile.mkdtemp(prefix='scoville-ask-', dir=base))


def retain_response(result) -> str | None:
    """Keep original streams locally before any response interpretation."""
    from check_text_size import PublicationError, publish_full
    stdout = result.stdout.encode('utf-8') if isinstance(result.stdout, str) else result.stdout or b''
    stderr = result.stderr.encode('utf-8') if isinstance(result.stderr, str) else result.stderr or b''
    data = f'exit={result.returncode} stdout_bytes={len(stdout)} stderr_bytes={len(stderr)}\n'.encode('ascii') + b'stdout:\n' + stdout + b'\nstderr:\n' + stderr
    try:
        return publish_full(temporary_root(), data, '.bin')
    except PublicationError as error:
        result.raw_file_error = error.reason
        return error.recovery_file  # Complete own capture, not a publication pass.
    except (OSError, ValueError) as error:
        result.raw_file_error = f'{type(error).__name__}:{getattr(error, "errno", None)}'
        return None


def run_command(command: list[str], cwd: Path, prompt: str, timeout: float):
    """Own one CLI process family and stop it when its deadline expires."""
    with subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          start_new_session=sys.platform != "win32",
                          creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0) as process:
        try:
            stdout, stderr = process.communicate(prompt.encode('utf-8'), timeout=timeout)
        except subprocess.TimeoutExpired as timeout_error:
            cleanup_error = None
            try:
                if sys.platform == "win32":
                    stopped = subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True, text=True, timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    if stopped.returncode:
                        cleanup_error = stopped.stderr.strip() or stopped.stdout.strip()
                else:
                    os.killpg(process.pid, signal.SIGKILL)
            except (OSError, subprocess.TimeoutExpired) as error:
                cleanup_error = str(error)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
            detail = f"Claude exceeded timeout_seconds={timeout:g}; no retry was started."
            if cleanup_error:
                detail += f" Process-family cleanup could not be confirmed: {cleanup_error}"
            failure = ClaudeTimeout(detail)
            failure.exit_code = process.returncode
            failure.capture_complete = False
            raw = subprocess.CompletedProcess(command, process.returncode, timeout_error.stdout, timeout_error.stderr)
            failure.raw_file = retain_response(raw)
            failure.raw_file_error = getattr(raw, 'raw_file_error', None)
            raise failure from None
    raw = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    raw_file = retain_response(raw)
    try:
        result = subprocess.CompletedProcess(command, process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))
    except UnicodeError as error:
        failure = RuntimeError('Claude response is not UTF-8; inspect raw_file locally; no retry was started.')
        failure.exit_code, failure.raw_file = process.returncode, raw_file
        failure.raw_file_error = getattr(raw, 'raw_file_error', None)
        failure.capture_complete = True
        raise failure from error
    result.raw_file = raw_file
    result.raw_file_error = getattr(raw, 'raw_file_error', None)
    return result
