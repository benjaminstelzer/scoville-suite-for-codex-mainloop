#!/usr/bin/env python3
"""Resolve a fixed child pair or verify the own active main-thread pair."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

from workflow_settings import EFFORTS, load_config

ROLE_KEYS = {"main": "main", "reviewer": "review", "explorer": "explore"}
NATIVE_ID = re.compile(r"[A-Za-z0-9._:-]{1,128}")
EVENT_KIND = re.compile(rb'"type"\s*:\s*"(turn_context|event_msg)"')


def resolve(config: dict, role: str) -> dict:
    if role not in ROLE_KEYS:
        raise ValueError(f"role={role!r}: use main, reviewer or explorer")
    pair = config[ROLE_KEYS[role]]
    return {"model": pair["model"], "thinking": pair["reasoning"]}


def native_record(line: bytes) -> dict:
    record = json.loads(line)
    if not isinstance(record, dict) or not isinstance(record.get('payload'), dict):
        raise ValueError('native session record must be an object with an object payload; obtain the current native session before coding')
    return record


def reverse_lines(stream):
    """Read the complete captured tail backwards; do not scan old task payloads."""
    remaining = os.fstat(stream.fileno()).st_size
    if not remaining:
        raise ValueError("native session is empty; wait for an active Codex turn")
    stream.seek(remaining - 1)
    if stream.read(1) != b"\n":
        raise ValueError("native session has an incomplete tail; retry after its current write finishes")
    fragments = []
    while remaining:
        count = min(remaining, 65536)
        remaining -= count
        stream.seek(remaining)
        parts = stream.read(count).split(b"\n")
        fragments.append(parts[-1])
        if len(parts) > 1:
            line = b"".join(reversed(fragments))
            if line:
                yield line
            yield from (line for line in reversed(parts[1:-1]) if line)
            fragments = [parts[0]]
    if fragments:
        line = b"".join(reversed(fragments))
        if line:
            yield line


def main_pair(session_path: Path | None = None, sessions_root: Path | None = None) -> dict:
    identity = os.environ.get("CODEX_THREAD_ID", "")
    if not NATIVE_ID.fullmatch(identity):
        raise ValueError("CODEX_THREAD_ID is missing or invalid; run this check inside the main Codex thread")
    root = sessions_root or Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
    if session_path is None:
        matches = list(root.rglob(f"*{identity}.jsonl"))
        if len(matches) != 1:
            raise ValueError(f"own native session for {identity} under {root} is missing or ambiguous ({len(matches)} matches); "
                             "supply --session-path for the own session")
        session_path = matches[0]
    path = session_path.resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("--session-path must be inside the native sessions directory")
    with path.open("rb") as stream:
        header = native_record(stream.readline())
        meta = header.get("payload", {})
        if (header.get("type") != "session_meta" or meta.get("id") != identity
                or not isinstance(meta.get("source"), str) or not meta["source"].strip()):
            raise ValueError("--session-path does not identify this main thread; use its own native session, not a child or parent")
        context = start = None
        terminated = False
        for line in reverse_lines(stream):
            if not EVENT_KIND.search(line):
                continue
            event = native_record(line)
            payload = event.get("payload", {})
            if event.get("type") == "turn_context" and context is None:
                context = event
            elif event.get("type") == "event_msg":
                kind = payload.get("type")
                if kind in {"task_complete", "task_failed", "task_aborted"}:
                    terminated = True
                if kind == "task_started":
                    start = event
                    break
    if not start or not context or terminated:
        raise ValueError("an active task_started and its turn_context are required; run in the active main turn")
    turn = start["payload"].get("turn_id")
    if (not isinstance(turn, str) or not turn.strip() or context["payload"].get("turn_id") != turn
            or type(start.get("ordinal")) is not int or type(context.get("ordinal")) is not int
            or context["ordinal"] <= start["ordinal"]):
        raise ValueError("native model evidence is not bound to the current active turn; refresh the own session proof")
    model, effort = context["payload"].get("model"), context["payload"].get("effort")
    if not isinstance(model, str) or not model.strip() or not isinstance(effort, str) or effort not in EFFORTS:
        raise ValueError("turn_context.model or effort is missing or unsupported; no technical model proof is available")
    return {"model": model, "thinking": effort, "thread_id": identity,
            "turn_id": turn, "session_path": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=tuple(ROLE_KEYS))
    parser.add_argument("--show-config", action="store_true")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--session-path", type=Path, help="own native session path for the main-pair check")
    args = parser.parse_args()
    if args.show_config and (args.role or args.session_path):
        parser.error("use --show-config alone, optionally with --project-root")
    if not args.show_config and not args.role:
        parser.error("supply --role main|reviewer|explorer, or --show-config")
    if args.session_path and args.role != "main":
        parser.error("--session-path is only for --role main")
    try:
        config = load_config(Path(__file__).resolve().parents[1] / "assets/workflow.toml", args.project_root)
        if args.show_config:
            result = {"config": config}
        else:
            result = resolve(config, args.role)
            if args.role == "main":
                actual = main_pair(args.session_path)
                if (actual["model"], actual["thinking"]) != (result["model"], result["thinking"]):
                    raise ValueError(f"main pair mismatch: expected {result['model']}/{result['thinking']}; "
                                     f"native active turn reports {actual['model']}/{actual['thinking']}. "
                                     "Select the configured pair in Codex, then recheck before coding")
                result.update(actual)
        print(json.dumps({"valid": True, **result}, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"valid": False, "diagnostic": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    raise SystemExit(main())
