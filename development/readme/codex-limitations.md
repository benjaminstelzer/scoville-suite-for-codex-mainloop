## Limitations

Codex keeps the agent threads of earlier assignments, so longer Workflow runs
and Ask consultations can hit its agent limit. I recommend raising it to 256
in `~/.codex/config.toml`. Add the section if it's missing:

```toml
[agents]
max_concurrent_threads_per_session = 256
```

The [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
describes the setting. If a start still fails, the affected operation stops,
reports it and keeps its progress for the next run.
