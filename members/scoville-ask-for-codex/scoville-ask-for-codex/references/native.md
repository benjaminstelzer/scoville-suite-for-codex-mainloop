# Native Ask agents

Use direct collaboration tools in the calling Ask chat.

## Spawn and collect

Put the question, raw evidence and explicit limits in a UTF-8 file outside the
reviewed working tree, using the workspace temporary area or system temporary
directory. Use the entrypoint's independent framing and build one assignment
per selected adviser:

```text
python "<ask-skill-directory>/scripts/build_adviser_prompt.py" --question-file "<question.txt>" --mode review --scope "<exact scope>" --reference "<consultation reference>" --workspace-root "<absolute-project-root>" --adviser-id <resolved-id> --format spawn --task-name <unique_name> --model <resolved-model> --effort <resolved-effort>
```

Use a unique task name with lowercase letters, digits and underscores, such as
`ask_sol_1`. Use `--mode consultation` for advice. Parse complete successful stdout as JSON
and pass it unchanged to `collaboration.spawn_agent`. The object supplies
`message`, `task_name`, `fork_turns="none"`, `model` and `reasoning_effort`.
A helper error or incomplete output stops dispatch. Correct its named input;
never repair the generated prompt. The host decides model/effort availability.

Retain adviser ID, requested settings, reference, scope and generated task name,
then the returned exact native handle and canonical task path. The host
identifies the final's sender; no startup callback is required.

Do not infer free capacity from an assumed limit or idle-agent count. Unknown
capacity permits an actual spawn attempt, not a claim that all advisers fit.
| Spawn result | Action |
| --- | --- |
| Capacity refusal | Retain the diagnostic and running advisers; mark undispatched ones pending. |
| Rejected spawn | Retain the failure. |
| Ambiguous result | Use `collaboration.list_agents` with the narrowest known canonical `path_prefix` that can resolve the retained task name and handle. Broaden only for that uncertainty; if unresolved, report the adviser unresolved with partial results. |

Never retry automatically, substitute an unmatched agent, change settings or
create replacement advisers or Codex chats. Completion provides no capacity
proof; do not wake advisers for cleanup or assume a `close_agent` tool exists.

## Collect and follow up

1. Use `collaboration.wait_agent` for bounded mailbox waits. Consume actual
   messages and finals; a wait summary or returned handle is not an answer.
2. Require the exact adviser's native final and completion. Match its host
   sender to the retained handle and its answer to the latest question,
   adviser identity, reference and scope. Resolve a repeated label from the
   retained assignment; clarify a different reference or scope. An earlier
   same-handle final cannot answer a later follow-up.
3. Read complete-file answers entirely before acceptance or use; metadata is
   insufficient. Retain complete answers once without listing those advisers
   again. Questions, substantive `send_message`, failures and incomplete finals
   remain partial or unresolved, never completed reviews.

| Collection state | Action |
| --- | --- |
| Timeout | Only the wait ended. Continue collecting active advisers; keep completed answers and failures visible. |
| Missing or incomplete final | Retain exact pending handle; do not accept partial messages as the final. |
| Tool failure, user interruption or missing fact requiring the user | Collection may end with exact pending handles. |

After a complete native final, retain the handle without routine acknowledgements,
closure messages or keepalives; its turn has ended. Necessary follow-ups use
the targeted route below, not queued `send_message`.
If a necessary follow-up targets an agent whose state is unclear, check once with
`collaboration.list_agents`, `path_prefix` set to its retained canonical task
path. A completion race remains possible; add no polling loop.

For a necessary clarification or authorized follow-up, use
`collaboration.followup_task` with the retained agent ID or canonical task name.
It resumes an idle agent and also delivers to an active one. Clarifications
preserve reference and scope. A new follow-up question supplies a new reference
and explicit scope. Retain the intended message before sending; reconcile an
uncertain result instead of resending blindly. Keep each adviser independent.

Follow the entrypoint's follow-up settings policy; this tool cannot override
model or effort. Never replace an unavailable handle silently.
