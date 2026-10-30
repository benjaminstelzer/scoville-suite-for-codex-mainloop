# Scoville Setup

Setup shows the Scoville settings your project actually uses and saves the
changes you request. Models, reasoning levels and Workflow settings stay in
one project file, with defaults filling the gaps.

Scoville measures chili heat. Setup lets you choose the seasoning instead of
discovering it halfway through the meal.

## How it works

1. Resolve this project's settings with consumer defaults.
2. Validate only the requested changed section.
3. Save a valid change atomically; preserve unrelated settings.

Cleanup is the sole old-Workflow migration operation. It resolves effective
legacy pairs, asks for ambiguous choices and validates the whole candidate
before one save. It creates no agents or Plan changes.

## What it enforces

- Saves settings only when you ask and leaves unrelated values alone.
- Rejects invalid values before writing.
- Changes configuration between runs, or at an explicitly authorized safe
  migration boundary. It doesn't start or supervise a workflow.

## What it costs

- Viewing or changing settings takes an agent interaction. Saved project settings spare you from repeating the same choices in later runs.

## How it was developed

Setup grew from the need to keep Ask and Workflow settings consistent without
editing configuration by hand. The important distinction was between saving a
setting and having the next operation use it as intended.

Changes are tested through the Skills that consume those settings and examined
in real project workflows. Configuration and migration problems feed back into
Setup, followed by another round of testing and use.

## Compatibility

Requires the Codex Suite, Python 3.11+, the bundled configuration helpers and
filesystem access to the selected project. Configuration changes are local.

## Install

Setup comes with the Codex Suite and isn't available on its own.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/packages).
Partial installations aren't supported: every member has to be installed and
enabled.

## Configuration

Settings are owned by the selected project's `.scoville/config.json`. Ask selects
advisers and Claude limits. Workflow schema 2 has fixed main, review and explore
model/reasoning pairs. The host owns the actual main model; Setup only saves its
required pair. Show is read-only and includes defaults.

Explicit cleanup converts old route tables after main and ambiguous pairs are
chosen. It removes obsolete Workflow fields only after complete validation,
preserving Ask, unrelated fields and valid special reasoning levels. A repeated
cleanup changes nothing. Workflow set against the old form requests cleanup
without writing; an Ask-only save preserves the old Workflow form unchanged.

## Limitations

Set offers low, medium, high and xhigh. Unrelated saves and migration preserve
valid special levels; execution still depends on actual model support. Setup neither changes the host model nor
starts agents, tests or Workflow. Cleanup changes no Plan or Codex settings.

Native advisers, Reviewers and Explorers have no sidebar chats. Legacy
ask.pin_threads remains readable and preserved but has no effect; new pin changes
are rejected. Claude CLI sessions also have no sidebar entry.

## How to use

Ask Setup to show or save this project's settings. For an old Workflow
configuration, explicitly request cleanup and supply the required main pair and
any ambiguous review/explore choices. All three valid pairs are saved together;
errors leave the file unchanged. Show never migrates.

For an explicitly authorized upgrade of a running project, let the old version
reach a reviewed, quiescent commit boundary, preferably Work Item closure.
Preserve needed closure evidence and commit a changed tracked Plan before
reload. If essential proof cannot be preserved, stay with the old version
within that Work Item. After reload, run explicitly authorized cleanup with
the chosen pairs. A tracked configuration change needs its own commit under
project checks before authorized continuation. The Skill's
migration instructions grant no upgrade, cleanup, commit or continuation
permission. Installation alone proves neither cleanup nor reload.

## Sources

- Ask and Workflow configuration files define the defaults and supported values.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop).

## License

MIT. See [LICENSE](LICENSE).
