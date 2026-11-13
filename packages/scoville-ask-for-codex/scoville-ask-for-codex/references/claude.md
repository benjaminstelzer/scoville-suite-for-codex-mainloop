# Claude CLI

Run a Claude adviser only through `ask.py` operation `claude`, with the
request `prepare` returned. It wraps the bundled Claude adapter, sends the
question through stdin and uses the explicit workspace, model, effort and
budget.

Claude must already be available and authenticated. Opus 5.5 requires Claude
Code 2.1.280 or newer and Fable 5.2 requires 2.1.321 or newer. Check
`claude --version` and report an older installation. Run `claude update` only
when the user authorized installing or updating Claude Code in this session;
an Ask consultation alone does not authorize that global update. After an
authorized update, verify the version before retrying.

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

Use the requested adviser ID, and `--mode consultation` for advice. The helper
returns the saved file path and resolved settings; it does not start Claude.
Before the first execution, set up complete capture under
[output delivery](output-delivery.md): the call is paid and cannot be repeated
for its output. Then execute the generated file unchanged:

```text
python "<ask-skill-directory>/scripts/ask.py" --input-file "<temporary>/claude-request.json"
```

Retain that request file with the answer and exact session ID. For an explicitly
requested follow-up, prepare a new question using the retained request:

```text
python "<ask-skill-directory>/scripts/ask.py" --resume-request "<temporary>/claude-request.json" --session-id "<exact retained session ID>" --question-file "<temporary>/followup.txt" --mode review --scope "<follow-up scope>" --reference "<new consultation reference>" --output-file "<temporary>/claude-followup.json"
```

Execute the new file with `--input-file`. A follow-up keeps the saved adviser,
workspace and settings even when defaults changed. Use a separate file per
adviser and round. If the result has `continuation_available:false`, report
that a fresh consultation is needed; do not start one.

For a fresh request or follow-up, append only explicitly requested overrides to
the preparation command: `--model <id>`, `--effort max`, `--web-tools true`
(or `false`), `--timeout-seconds 3600` or `--max-budget-usd 10`. For example,
`--effort max --web-tools true` changes those two settings and retains the rest.
Overrides affect this request only; they do not change project configuration.

## Execution and result

The adapter allows Read, Grep and Glob and uses `dontAsk`. WebSearch and
WebFetch need an explicit `claude.web_tools: true` in the configuration or as
a request override. Read web-tools and timeout defaults from the shipped
settings in [configuration.md](configuration.md). Customizations are disabled
by default. A local launch is not offline: Claude and enabled web tools
communicate with their services. Do not call these tool restrictions sandbox
isolation. The adviser cannot run shell commands or create delivery files. If
a required machine-data check needs code execution, supply the checked result
yourself or keep the evidence gap.

Launch and wait:

- A positive finite timeout_seconds on the request overrides its default for
  that call.
- If the host kills processes at a deadline, set that deadline above
  `timeout_seconds` plus time for process-family cleanup. Killing Python
  first keeps the adapter from cleaning up and returning the result.
- Launch through the host's asynchronous shell facility and collect the
  running process in bounded waits. A returned shell session is still
  running; keep collecting it.

At `timeout_seconds` the adapter terminates its process family and returns
`ok:false` with `code:claude_timeout`. It does not retry and reports cleanup
it could not confirm. After a timeout, retain a previously confirmed session
ID and the requested settings, mark unavailable actual metadata unknown and do
not claim the interrupted turn was saved.

Each consultation is a paid call. After a timeout or failure, run it again,
resume it, raise the budget or switch the provider only on the user's request;
a question about its status is not that request. After an uncertain process
result, first establish what happened from the retained record; the same rule
then applies.

| Result | Meaning and action |
| --- | --- |
| Answer | The adviser's result. Retain the JSON answer, permission denials, requested and reported settings and the exact session ID, whichever of them the result contains, also when no answer arrived. |
| Permission denials | Evidence gaps, even when an answer is present. |
| No session ID | Continuation is unavailable; no resumable session was created. |
| Process error, timeout, malformed JSON or empty answer | A failed consultation. Do not piece an answer together from logs; it would not be the adviser's. |
| `raw_file_error` | Storing the raw copy failed; `raw_file: null` means no complete copy exists. The received answer stands. Do not repeat the paid call to repair storage. |

Before parsing, the adapter tries to retain raw stdout, stderr and the
original exit in a private user-owned temporary directory. On response
failure, `raw_file`, `exit_code` and any parsed `session_id` identify that
record; inspect it in code and do not dump it. Timeout captures are partial.
Requested settings are not runtime proof: reported model and effort remain
null until their actual producer schema is established.

Completion and retention follow the Skill's "Follow-up after completion" rules.

If authentication is missing or OAuth cannot refresh, report the error. Ask
the user to run `claude auth login` in a separate terminal, complete the
browser sign-in and verify with `claude auth status`. Leave unrelated running
Claude processes untouched; do not read or copy credential files. Resume the
requested check after authentication succeeds.
