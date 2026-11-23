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
