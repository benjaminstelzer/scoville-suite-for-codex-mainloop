## Configuration

Schema 2 has three fixed model and reasoning pairs:

| Setting | Default model | Reasoning |
| --- | --- | --- |
| workflow.main | gpt-6.1-sol | high |
| workflow.review | gpt-6.1-sol | xhigh |
| workflow.explore | gpt-6.1-sol | high |

Use Setup to show or save project overrides in `.scoville/config.json`.
The main pair must match its own active native session before coding. Recheck
on activation, authorized resumption, a changed required pair, visible host-model
change or concrete loss of binding; not on every Step. Setup cannot change the
host model. Invisible host changes cannot be guaranteed detected.

Old route tables and context settings require explicit Setup cleanup. It asks
for main and any ambiguous role pair, preserves Ask and unrelated values, and
saves only a complete valid migration. Reads never migrate or create settings.
There are no per-Step model routes or context thresholds. Existing execute
annotations are retained and compared with main; conflicts require a decision.
See the [dispatch rules](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations-dispatch.md).
