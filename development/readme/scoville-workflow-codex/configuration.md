## Configuration

| Setting | Default model | Reasoning |
| --- | --- | --- |
| `workflow.main` | gpt-6.2-sol | high |
| `workflow.review` | gpt-6.2-sol | xhigh |
| `workflow.explore` | gpt-6.2-sol | high |

Change them with Scoville Setup between runs. It saves them in
`.scoville/config.json`. Before coding, Workflow checks that your chat
actually runs the main model and reasoning level. Setup can't switch that for
you - you change the chat's model in Codex.
