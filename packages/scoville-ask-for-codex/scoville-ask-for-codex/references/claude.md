# Claude CLI

Use only `ask.py` operation `claude` with the request returned by `prepare`.
It wraps the bundled Claude adapter, sends the question through stdin and uses
the explicit workspace, model, effort and budget. Claude must already be
available and authenticated. Opus 5.5 requires Claude Code 2.1.280 or newer and
Fable 5.2 requires 2.1.321 or newer; check `claude --version` and report an
older installation. Run `claude update`
only when the user has authorized installing or updating Claude Code in this
session. An Ask consultation alone does not authorize that global update.
After an authorized update, verify the version before retrying. A failed
native route is reported, not replaced by the CLI, because the user selected
the route.

## Contents

- Prepare and run
- Execution and result

## Prepare and run

Keep the UTF-8 question and generated request files in the workspace temporary
area outside the reviewed tree.

The helper preserves the literal question. Generate one request per selected
Claude adviser and pass it unchanged to execution:

```text
python "<ask-skill-directory>/scripts/ask.py" --project-root "<absolute-project-root>" --adviser claude --question-file "<temporary>/question.txt" --mode review --scope "<exact scope>" --reference "<consultation reference>" --output-file "<temporary>/claude-request.json"
```

Use the requested adviser ID and `--mode consultation` for advice. The helper
returns the saved file path and resolved settings. Preparation does not start
Claude. Set up complete capture under [output delivery](output-delivery.md)
before the first execution, because the call is paid and cannot be repeated
for its output, then execute the generated file unchanged:

```text
python "<ask-skill-directory>/scripts/ask.py" --input-file "<temporary>/claude-request.json"
```

Retain that request file with the answer and exact session ID. For an explicitly
requested follow-up, prepare a new question using the retained request:

```text
python "<ask-skill-directory>/scripts/ask.py" --resume-request "<temporary>/claude-request.json" --session-id "<exact retained session ID>" --question-file "<temporary>/followup.txt" --mode review --scope "<follow-up scope>" --reference "<new consultation reference>" --output-file "<temporary>/claude-followup.json"
```

Execute the new file with `--input-file`. Follow-ups keep the saved adviser,
workspace and settings even when defaults change. Use a separate file per
adviser and round. Continue only with the exact retained session ID; the most
recent session may be another consultation. If the result has
`continuation_available:false`, report that a fresh consultation is needed
instead of starting one. The session ID is the CLI continuation handle.

For a fresh request or follow-up, append only explicitly requested overrides to
the preparation command: `--model <id>`, `--effort max`, `--web-tools true`
(or `false`), `--timeout-seconds 3600` or `--max-budget-usd 10`. For example,
`--effort max --web-tools true` changes those two settings and retains the rest.
Overrides affect this request only; they do not change project configuration.
`--max-budget-usd 0` removes the helper's spend cap by omitting the CLI flag.
It does not mean free use or remove provider, account or timeout limits.

## Execution and result

The adapter allows Read, Grep and Glob and uses `dontAsk`. WebSearch and
WebFetch require an explicit `claude.web_tools: true` configuration or request
override. Read web-tools and timeout defaults from the imported settings in
[configuration.md](configuration.md).
Customizations are disabled by default. Local launch does not mean offline;
Claude and optional web tools communicate with their services. These tool
restrictions do not justify a claim of sandbox isolation.
The adviser cannot run shell commands or create delivery files. If a required
machine-data check needs code execution, supply checked results from the caller
or retain the resulting evidence gap.

A positive finite timeout_seconds on the request overrides its default for
that call.
Launch through the host's asynchronous shell facility and collect the running
process in bounded waits. A returned shell session is still running; keep
collecting it. If the host enforces a process-killing deadline, set it above
`timeout_seconds` with time for process-family cleanup. Killing Python first
prevents the adapter from completing its own cleanup and returning the result.
At the deadline the adapter terminates its process family and returns `ok:false` with
`code:claude_timeout`; it does not retry. Any unconfirmed cleanup is reported.
After timeout, retain any previously confirmed session ID and requested
settings, mark actual metadata unknown when unavailable, and do not claim the
interrupted turn was saved. Each consultation is a paid call, so after a
timeout or failure run it again, resume it, raise the budget or switch the
provider only on the user's request; a question about its status is not that
request.

Retain the JSON answer, permission denials, requested/reported settings and
exact session ID. Permission denials are evidence gaps even when an answer is
present. Missing session IDs mean continuation is unavailable, not success at
creating a resumable session. A process error, timeout, malformed JSON or empty
answer is a failed consultation; do not piece one together from logs, because
it would not be the adviser's answer.
The adapter attempts to retain raw stdout, stderr and original exit in a private
user-owned temporary directory before parsing. A storage failure preserves the
received answer and reports `raw_file_error`, with `raw_file: null` when no complete
copy exists; the answer stands, and the paid call is not repeated to repair
storage. On response failure, `raw_file`, `exit_code` and any parsed
`session_id` identify that record; inspect it in code rather than dumping it.
Timeout captures are partial. Requested settings are not runtime proof: reported model
and effort remain null until their actual producer schema is established.

After an uncertain process result, establish what happened from the retained
record before anything else; a second paid run needs the user's request.
Completion and retention follow the Skill's "Follow-up after completion" rules.

If authentication is missing or OAuth cannot refresh, report the error and ask
the user to run `claude auth login` in a separate terminal, complete browser
sign-in and verify with `claude auth status`. Leave unrelated running Claude
processes untouched and credential files unread and uncopied. Resume the requested check
after authentication succeeds.
