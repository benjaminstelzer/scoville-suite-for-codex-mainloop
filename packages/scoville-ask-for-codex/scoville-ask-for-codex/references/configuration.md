# Settings and helper inputs

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.

| Condition | Required route |
| --- | --- |
| Python and every named helper are available | Use the bundled helper. |
| Missing Python, script, dependency or helper error | Stop the affected operation; do not substitute manual execution. |

Helpers: `scripts/ask.py`, `scripts/build_adviser_prompt.py`.

Resolve locally with one complete command:

```text
python "<ask-skill-directory>/scripts/ask.py" --project-root "<absolute-project-root>"
```

Add `--adviser <configured-id>`, repeated as needed, to select only those
advisers. With one selected adviser, `--model <id>` and `--effort <level>`
override its settings without saving. For other overrides, pass a UTF-8 JSON
request written by a helper or a serializer; hand-written JSON breaks on
quoting:

```text
python "<ask-skill-directory>/scripts/ask.py" --input-file "<request.json>"
```

The request object contains:

- `operation=resolve` to select the operation.
- `project_root` for the selected project.
- Optional `overrides` for unsaved settings.

The JSON response's `config.advisers` entries supply these settings directly:

- `id` identifies the adviser.
- `route` selects its transport.
- `model` supplies the `spawn_agent` model.
- `effort` supplies the `spawn_agent` reasoning_effort.

These are technical settings, not a dispatch prompt. Questions to advisers
and their answers stay plain text. On a nonzero exit or ok:false, stop the
operation and report its diagnostic. JSON requests through stdin remain
supported, including Ask Claude.

ask_settings.py, scoville_config.py and ask_claude.py are imported modules, not
separate commands. Use the bundled ask.py from this installed package.

Legacy ask.pin_threads booleans remain readable and are preserved when other
settings change, but have no effect. Native advisers are subagents without
sidebar chats. Use Scoville Setup for agent-driven configuration changes.
Users can edit `.scoville/config.json` manually for supported special reasoning levels.
After such an edit, validate read-only with
`python -X utf8 "<ask-skill-directory>/scripts/ask.py" --project-root "<absolute-project-root>"`.
On a nonzero exit or `ok:false` the edit is not validated. This command never
migrates it.

Settings are in `.scoville/config.json` of the selected project root. Its
`ask` section overrides this Skill's defaults; a missing file or field uses
the default. Reading never creates a file and never searches parent
directories.

- Objects merge by field.
- `advisers` replaces the entire list, so an explicit selection contains only
  the named presets.
- Name advisers as strings such as `["astra"]`, or as objects with `id`
  and per-call overrides. A matching ID inherits its configured preset.
- A custom ID needs `route` (`native` or `claude-cli`), exact `model` and
  `effort`; `name` is optional.
- One adviser and several use the same structure.

Take current defaults from the actual config; do not infer model or effort
from a Skill name.

Shipped settings, generated from their canonical file:

```json
{
  "schema_version": 1,
  "advisers": ["astra"],
  "presets": {
    "astra": {"route": "native", "model": "gpt-6-astra", "effort": "high"},
    "sol": {"route": "native", "model": "gpt-6.1-sol", "effort": "high"},
    "claude": {"route": "claude-cli", "model": "claude-opus-5-5", "effort": "high"},
    "fable": {"route": "claude-cli", "model": "claude-fable-5-2", "effort": "medium"}
  },
  "claude": {
    "max_budget_usd": 10,
    "session_persistence": true,
    "customizations": false,
    "timeout_seconds": 3600,
    "web_tools": false
  }
}
```

Save only changed values, for example:
`{"ask":{"claude":{"timeout_seconds":1800}}}`.
Request overrides use the fields inside `ask`.

Pass the selected project's absolute root as `project_root`. Without it,
`resolve` uses `cwd`, and without both the process working directory. It
rejects `project_config` with migration guidance. Do not change settings
during a run. Show the resolved settings when the user asks about
configuration.

`claude.max_budget_usd` accepts a finite amount of 0 or more. A positive
amount sets the CLI spend cap. Zero removes this helper's spend limit by
omitting the CLI flag; use is not free, and provider, account and timeout
limits remain. Request overrides do not save project settings.

The Claude-only `prepare` request contains:

- `mode=review|consultation` to select the kind of advice.
- `question` for the actual request.
- `scope` for its boundary.
- `reference` for the consultation reference.
- `cwd` for an existing absolute working directory.
- `overrides` selecting only Claude advisers.

The response returns `entries[].request` for `operation=claude`. Use the helper commands
in [Claude operation](claude.md) for fresh requests and follow-ups.
