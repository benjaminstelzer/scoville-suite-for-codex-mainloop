# Native Ask agents

## Spawn and collect

Put the question, raw evidence and explicit limits in a UTF-8 file outside the
reviewed working tree, in the workspace temporary area or system temporary
directory. Frame it as SKILL.md's "Ask and collect" requires. Build one
assignment per selected adviser:

```text
python "<ask-skill-directory>/scripts/build_adviser_prompt.py" --question-file "<question.txt>" --mode review --scope "<exact scope>" --reference "<consultation reference>" --workspace-root "<absolute-project-root>" --adviser-id <resolved-id> --format spawn --task-name <unique_name> --model <resolved-model> --effort <resolved-effort>
```

1. Use a unique task name of lowercase letters, digits and underscores, such
   as `ask_sol_1`, and `--mode consultation` for advice.
2. Parse complete successful stdout as JSON and pass it unchanged to
   `collaboration.spawn_agent`. The object supplies `message`, `task_name`,
   `fork_turns="none"`, `model` and `reasoning_effort`.
3. On a helper error or incomplete output, correct the named input and run the
   helper again before dispatch. Do not repair the prompt by hand; it would no
   longer be what the helper validated.
4. Retain adviser ID, requested settings, reference, scope and generated task
   name, then the returned exact native handle and canonical task path.

The host decides model and effort availability. An assignment above 8 KiB
UTF-8 uses the existing complete-file route in system temporary storage
outside the reviewed tree; forward the generated message unchanged, and the
adviser reads the whole assignment before work. The host identifies the
final's sender; require no startup callback.

Only an actual spawn attempt shows free capacity, not an assumed limit or a
count of idle agents. With unknown capacity you may attempt the spawn; do not claim that all advisers fit.

| Spawn result | Action |
| --- | --- |
| Capacity refusal | Retain the diagnostic and running advisers; mark undispatched ones pending. |
| Rejected spawn | Retain the failure. |
| Ambiguous result | Use `collaboration.list_agents` with the narrowest known canonical `path_prefix` that can resolve the retained task name and handle. Broaden only for that uncertainty; if unresolved, report the adviser unresolved with partial results. |

After a refused, rejected or ambiguous spawn, or a failed collection, a
further attempt needs the user's go-ahead. Without it, do not respawn,
substitute an unmatched agent, change settings or create replacement advisers
or Codex chats: each would occupy more host capacity and deliver advisers the
user did not select. A finished adviser proves no free capacity. Leave it as
it is; do not wake it for cleanup or assume a `close_agent` tool exists.

## Collect and follow up

1. Use `collaboration.wait_agent` for bounded mailbox waits. Read the actual
   messages and finals; a wait summary or returned handle is not an answer.
2. Accept only the exact adviser's native final after its completion. Its host
   sender must match the retained handle, its answer the latest question,
   adviser identity, reference and scope. Resolve a repeated label from the
   retained assignment; clarify a different reference or scope. An earlier
   same-handle final cannot answer a later follow-up.
3. Read complete-file answers entirely before acceptance or use; metadata is
   not enough. Retain complete answers once; do not list those advisers again.
   A question, a substantive `send_message`, a failure or an incomplete final
   stays partial or unresolved, never a completed review.

| Collection state | Action |
| --- | --- |
| Timeout | Only the wait ended. Continue collecting active advisers; keep completed answers and failures visible. |
| Missing or incomplete final | Retain exact pending handle; do not accept partial messages as the final. |
| Tool failure, user interruption or missing fact requiring the user | Collection may end with exact pending handles. |

After a complete native final the adviser's turn has ended. Retain the handle;
send no routine acknowledgement, closure message or keepalive.

For a necessary clarification or authorized follow-up, use
`collaboration.followup_task` with the retained agent ID or canonical task
name, not a queued `send_message`. It resumes an idle agent and also delivers
to an active one.

- If the target agent's state is unclear, check once with
  `collaboration.list_agents`, `path_prefix` set to its retained canonical
  task path. A completion race remains possible; add no polling loop.
- A clarification keeps reference and scope. A new follow-up question gets a
  new reference and explicit scope.
- Retain the intended message before sending. After an uncertain result, find
  out whether it arrived before resending.
- Keep each adviser independent.
- Settings follow SKILL.md's "Follow-up after completion"; this tool cannot
  override model or effort.
