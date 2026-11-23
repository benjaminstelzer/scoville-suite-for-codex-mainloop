# Scoville Ask for Codex

Scoville Ask gets independent advice from the advisers you choose and returns
it to your current task. Use it for a patch review, a second opinion or a
comparison of approaches. Each adviser gets the question and relevant evidence
with fresh context.

Scoville measures chili heat. Ask adds a little heat to your assumptions.
Unanimous agreement is pleasant, but finding the missed problem is more useful.

## How it works

- It asks the advisers you configured: native Codex agents, or Claude through
  the Claude CLI.
- Each adviser gets the same question, scope and evidence, independently and
  with fresh context.
- Reviews come back separately and stay attached to their adviser. For a
  general question Ask can combine the answers.
- Missing answers and failed starts are shown next to the results. Ask doesn't
  quietly pick a different adviser.
- Advisers assess. They change nothing and run no tests. For native agents
  that is an instruction - Codex doesn't enforce it. Claude gets Read, Grep
  and Glob, and web access only if you ask for it or set `claude.web_tools`.
- For a code review, advisers use Scoville Code and Scoville UI where these
  are installed beside Ask.

## What it costs

Each adviser adds model usage, waiting and one agent. Use extra opinions for
decisions worth checking. You still have to weigh the disagreements.

## How to use

```text
Use scoville-ask-for-codex to review this patch with SOL.
```

```text
Ask Fable and Claude independently how they would approach this problem, then return and compare their answers here.
```

Ask handles the consultation and necessary clarifications without asking you
to approve each exchange. Request a follow-up when you need one - native
agents keep their context, and Claude resumes its saved session.

## Install

Needs Codex desktop, online, with native agents and Python 3.11+.

Use `gpt-6.2-sol` at medium reasoning effort or higher. Below that, steps get
skipped more often.

It comes with the suite. Install every Skill from
[the suite's packages](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/tree/main/packages) - partial
installations aren't supported.

### Claude consultations

1. Install [Claude Code](https://code.claude.com/docs/en/setup) if needed and open a terminal.
2. Run `claude --version`. Opus 5.5 needs **2.1.280 or newer**, the `fable` preset (Fable 5.2) **2.1.321 or newer**. For an older version, run `claude update`.
3. Run `claude auth login` and complete sign-in in your browser.
4. Run `claude auth status` to check that you are signed in.

If Ask later reports an expired session, repeat steps 3 and 4.

## Configuration

The defaults are in `config.default.json` next to the installed `SKILL.md`.
Project choices go under `ask` in `.scoville/config.json` at the project root,
and anything missing falls back to the defaults. Scoville Setup shows and saves
them. What you name in a request applies to that call only.

This example selects SOL and Fable by default and changes only SOL's effort:

```json
{
  "ask": {
    "advisers": ["sol", "fable"],
    "presets": {"sol": {"effort": "medium"}}
  }
}
```

Project settings override the defaults one field at a time. The adviser list
is the exception: it replaces the default list completely. The `sol` preset
uses `gpt-6.2-sol` at `high`. For an adviser of your own, add an ID, route,
exact model and effort under `advisers`. The `claude` block caps each Claude
call: 10 USD, one hour, no web tools.

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

## Background

Early consultations made collecting answers and asking follow-up questions
more complicated than the question warranted.

The [full instructions](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/packages/scoville-ask-for-codex/scoville-ask-for-codex/SKILL.md) are what the agent reads.
Sources: [Codex Skills](https://learn.chatgpt.com/docs/build-skills) and the
[Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
