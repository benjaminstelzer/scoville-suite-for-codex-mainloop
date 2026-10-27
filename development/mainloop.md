# Mainloop development target

- Source fork: `scoville-suite` at `418ed4694a5615f9d46617d0a0da0e55e87a4cd7`; original history retained.
- Runtime uses the main thread for implementation, read-only Explorer and fresh
  Reviewer roles. Development Plans and their live-run evidence remain private.
- Target: `codex`, suite `scoville-suite-for-codex-mainloop`. The existing generic
  builder resolves this manifest; there is no separate build implementation.
- The manifest selects the separate GitHub distribution. A source checkout or
  build does not establish publication, installation or project migration.
- The local build shim replaces only the variant's Runtime-CI Python test asset.
  Existing package, matrix and proof logic remains in the shared builder;
  preparation and verification use the same local test bytes. Shared is unchanged.

From this repository, use the existing commands:

```text
python development/build_suite.py --check-sources
python development/build_suite.py --write-readmes
python development/build_suite.py --check-readmes
python development/check_all.py
```

After implementation, acceptance and delivery authorization, a suite build uses
the same entrypoint with `--profile codex --layout suite` and an output below
the workspace's `skills/temp/release/mainloop/`. Existing release targets
and global installations stay separate. Follow the README's opt-in migration
instructions rather than automatically upgrading running projects.

## Verified native contract (2026-10-27)

- Official host configuration and subagents:
  <https://learn.chatgpt.com/docs/config-file/config-reference> and
  <https://learn.chatgpt.com/docs/agent-configuration/subagents>.
- This host exposes spawn, messages, followup, wait, list and interrupt. Its
  current spawn schema exposes model and reasoning, but no native type selector
  or close operation. Documentation alone does not prove tool availability.
- The own local rollout is bound by `CODEX_THREAD_ID` and its `session_meta.id`.
  Its active `task_started.turn_id` matches the following `turn_context.turn_id`;
  `turn_context.model` and `effort` contain the harness's current selected pair.
  An own live read established these fields and active-turn ordering. This proves
  the reported harness pair, not a billing/backend model identity.
- Add the main-pair check to the existing `resolve_model_pair.py`. Reuse session
  identity binding, not token/window measurement. The Workflow's operations
  reference owns its triggers, failures and invisible-change limit.
- A tested minimum Codex version remains unproved. The rollout's historical
  header version and the separately installed CLI version are not a minimum.
