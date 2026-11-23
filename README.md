# Scoville Suite for Codex Mainloop

Scoville keeps planning, implementation and checks in your current Codex chat.
Workflow takes the Plan through its original Steps, read-only Explorers
investigate questions and fresh Reviewers check the work. Ask brings in
independent advice, Handoff prepares a continuation and Setup manages project
settings.

Scoville is the scale for chili heat. These Skills aim for sharper work and
less diluted context. Adding more instructions is easy. Keeping the useful
ones is the point.

This edition is for Codex desktop. For Claude Code and other Agent Skills
hosts there is [Scoville Suite](https://github.com/benjaminstelzer/scoville-suite),
without Workflow, Ask and Setup.

| Skill | What it does |
| --- | --- |
| [Workflow](members/scoville-workflow-for-codex/README.md) | Takes a Plan through implementation and independent review in your current chat. |
| [Code](members/scoville-code/README.md) | Keeps implementation, debugging and review tied to the result you asked for. |
| [Plan](members/scoville-plan/README.md) | Keeps goals, decisions and progress in the repository so longer work survives the next conversation. |
| [UI](members/scoville-ui/README.md) | Builds and audits interfaces with the project's framework and design system. |
| [Handoff](members/scoville-handoff/README.md) | Transfers the work state, not the whole conversation. |
| [Ask](members/scoville-ask-for-codex/README.md) | Gets independent advice from the advisers you choose. |
| [Setup](members/scoville-setup/README.md) | Shows and saves the project's Scoville settings. |
| [Project Context Cleanup](members/scoville-project-context-cleanup/README.md) | Adds and revises project rules without losing what made them useful. |
| [Skillwriter](members/scoville-skillwriter/README.md) | Writes and reviews Skills and reusable prompts for current frontier models. |

## Install

Needs Codex desktop with native agents. Claude consultations also need a
signed-in Claude Code CLI. The bundled helpers need Python 3.11+ - without it,
the affected step stops and says so.

Use `gpt-6.2-sol` at medium reasoning effort or higher. Below that, steps get
skipped more often.

Ask your agent host:

```text
Install and enable the complete suite for all my projects from the packages/ directory of https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop.
Preserve personal settings and unrelated Skills. Ask before overwriting conflicting customizations.
Report the installed location and whether the host discovers every member.
```

If your host can't install from GitHub, download the repository and copy each
`packages/<name>/<name>/` directory into the host's Skills location. Don't mix
standalone and suite copies of the same Skill. Longer runs can hit Codex's
agent limit - see [Workflow](members/scoville-workflow-for-codex/README.md#limitations).

### Upgrading

Replace the installed copies with the complete packages of the suite you
chose. Your project settings and unrelated Skills stay.

Coming from an earlier Codex suite: finish and commit the current Work Item
first. Then install Mainloop, reload and ask Setup to show the project's
settings. If it reports old Workflow settings, ask it for a cleanup and name
the main model and reasoning level. Commit the changed settings file if it is
tracked.

## Configuration

Scoville Setup shows and saves model choices and Workflow settings in
`.scoville/config.json`. Missing values use the bundled defaults. The
[Workflow](members/scoville-workflow-for-codex/README.md#configuration) and
[Ask](members/scoville-ask-for-codex/README.md#configuration) READMEs explain
them.

## Background

Scoville grew from a frustrating pattern in real software projects: an agent
could follow plenty of rules and still lose the goal between planning,
implementation and review. Every idea is tested and then used in real
workflows on large projects, and what those show goes into the next revision.
The [development notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/docs/README.md)
tell the longer story.

## Developer links

Sources, tests and notes for every Skill live in this repository. The
[build guide](development/shared/build/fragments.md) covers builds and checks.

- **scoville-code**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-code) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-code/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-code/development/README.md)
- **scoville-plan**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-plan) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-plan/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-plan/development/README.md)
- **scoville-ui**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-ui) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/development/tests/test_build_suite.py) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-ui/development/README.md)
- **scoville-handoff**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-handoff) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-handoff/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-handoff/development/README.md)
- **scoville-workflow-for-codex**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-workflow-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-workflow-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-workflow-for-codex/development/README.md)
- **scoville-ask-for-codex**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-ask-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-ask-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-ask-for-codex/development/README.md)
- **scoville-setup**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-setup) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-setup/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-setup/development/README.md)
- **scoville-project-context-cleanup**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-project-context-cleanup) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/development/tests/test_build_suite.py) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-project-context-cleanup/development/README.md)
- **scoville-skillwriter**: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/members/scoville-skillwriter) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/development/tests/test_build_suite.py) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/members/scoville-skillwriter/development/README.md)

## License

The bundled Skills use the MIT license. Each package includes its `LICENSE` file.

