## How it works

- Showing the settings changes nothing and creates no file.
- It saves a change only when you ask and leaves unrelated settings alone.
  An invalid value is rejected before anything is written.
- Settings live in `.scoville/config.json` in the project: advisers and
  Claude limits for Ask, and the three model and reasoning pairs for Workflow.
  Setup sets the reasoning levels low, medium, high and xhigh.
- It changes settings between runs. It doesn't start Workflow, agents or
  tests, and it can't change the model your chat runs on.
