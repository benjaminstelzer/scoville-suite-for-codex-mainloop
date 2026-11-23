# Scoville Setup

Setup shows the Scoville settings your project actually uses and saves the
changes you request. Models, reasoning levels and Workflow settings stay in
one project file, with defaults filling the gaps.

Scoville measures chili heat. Setup lets you choose the seasoning instead of
discovering it halfway through the meal.

## How it works

- Showing the settings changes nothing and creates no file.
- It saves a change only when you ask and leaves unrelated settings alone.
  An invalid value is rejected before anything is written.
- Settings live in `.scoville/config.json` in the project: advisers and
  Claude limits for Ask, and the three model and reasoning pairs for Workflow.
  Setup sets the reasoning levels low, medium, high and xhigh.
- It changes settings between runs. It doesn't start Workflow, agents or
  tests, and it can't change the model your chat runs on.

## How to use

```text
Use Scoville Setup to show this project's settings.
```

```text
Use Scoville Setup to set the Workflow review reasoning to high.
```

A configuration from an earlier Codex suite needs one explicit cleanup: ask
Setup for it and name the main model and reasoning level. It asks about
anything ambiguous and keeps Ask and unrelated settings.

## Install

Setup comes with [Scoville Suite for Codex Mainloop](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop)
and isn't available on its own. Install every Skill from
[the suite's packages](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/packages) - partial
installations aren't supported. It needs Python 3.11+.

## Background

Setup grew from the need to keep Ask and Workflow settings consistent without
editing configuration by hand. The important distinction was between saving a
setting and having the next operation actually use it. The
[full instructions](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/packages/scoville-setup/scoville-setup/SKILL.md) are what the agent reads.

## Developer links

[Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-setup) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-setup/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-setup/development/README.md)

## License

MIT. See [LICENSE](LICENSE).
