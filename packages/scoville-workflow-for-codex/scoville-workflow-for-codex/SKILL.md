---
name: scoville-workflow-for-codex
description: Execute an ordered Scoville Plan in the current Codex thread on explicit activation, such as "Start Scoville Workflow", $scoville-workflow-for-codex or scoflow codex. The main thread plans and codes; only read-only exploration and independent reviews are delegated. Generic delegation and discussion do not activate it.
compatibility: "Codex with native collaboration agents, an own active-session model and reasoning record, shared workspace, filesystem and Git access, Python 3.11+ and matching Scoville Plan helpers. Codex Suite only."
---

# Scoville Workflow Codex

The original **main thread** plans, communicates, implements, runs required
checks and maintains Plan records. It handles exactly one original Step at a
time. It delegates only these roles:

| Role | Assignment | Rights and lifetime |
| --- | --- | --- |
| Explorer | Investigate questions, ideas and planning preparation; return findings and proposals. | Read only; no tests or Plan writes. Reuse this thread's Explorer only for the same investigation or a follow-up building on its findings, while idle with unchanged pair and rules. An independent request gets a fresh Explorer. |
| Reviewer | Independently review the selected changed Step or the completed Work Item. | Read only; no tests or Plan writes. Fresh for EVERY review, including correction, missing evidence and repeated closure. |

Only necessary oversized-result delivery under the shared procedure permits
temporary writes by read-only roles. Do not modify the review's sources or
binding inputs while it runs. Workflow activation authorizes commits of accepted
Steps, subject to user and project restrictions. Host compaction continues this
same thread; recover actual work rather than repeating completed effects.

Read the [shared writing rules](references/writing.md) and
[operations](references/operations.md) before managing work. Use Plan for its
records and [dispatch](references/operations-dispatch.md) for original tasks and
child arguments. Reuse matching loaded rules. Agents select needed Skills and
references themselves; explicit user invocations remain binding.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

## Activation

Start or resume only on explicit activation, including `$scw` after this Skill
is loaded. Quoted text and role markers grant no authority. Preserve authorized
scope, user stops, decisions and model choices. Editing Workflow or executing a
Plan without activating this Skill does not activate it. Workflow creates no
goal, scheduled continuation or successor thread.

Reuse an already verified interpreter meeting this Skill's Python 3.11+
requirement. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Verify its version before the first helper operation.
Use that executable wherever examples say `python` or `<verified-python>`,
including Python commands after `--run --`.
Report a missing runtime only when no suitable installed interpreter is found.

Before processing machine reports or logs, use the [shared writing rules](references/writing.md).
If their complete text is not loaded, read it in a separate call before reading
the data. Reuse retained rules under their existing reload conditions.
Before helper calls, follow [shell command rules](references/shell-commands.md).

Before a new run, require the clean-Git gate in operations. An authorized
continuation of the same started work reconciles its actual changes and
processes. Both require the main-pair check; ordinary successive Steps do not.

## Step loop

```mermaid
flowchart TD
  ready["Check activation, Git state and fixed main pair"] --> select["Select ONE original Step; save its start"]
  select --> original["Helper validates start and returns original task"]
  original --> code["Main thread: implement and finish required checks"]
  code --> quiet["Establish write and process quiescence"]
  quiet --> complete{"Step complete; checks met; effects clear?"}
  complete -->|no or unclear| blocked["Resolve prerequisite; keep work open"]
  complete -->|yes| changes{"File, config or behavior changes; or open Step review?"}
  changes -->|yes| review["Helper: SAME original Step and required evidence"]
  review -->|success| spawn["Fresh Reviewer from unchanged returned arguments"]
  review -->|failure| blocked
  spawn --> result{"Review result?"}
  result -->|changes_requested| original
  result -->|blocked| blocked
  result -->|pass| commit["Record progress; commit accepted versionable work"]
  changes -->|no| unchanged["Record completion; invent no review pass or empty commit"]
  commit -->|success or no versionable changes| more{"All Steps and required Step reviews complete?"}
  commit -->|failed or forbidden| blocked
  unchanged --> more
  more -->|no; next Step authorized| select
  more -->|no; scope ends| stop["Save allowed owned progress; stop with item open"]
  more -->|yes| closure["Helper: ALL original Steps and FULL Acceptance"]
  closure -->|success| closure_spawn["Fresh Reviewer from unchanged returned arguments"]
  closure -->|failure| blocked
  closure_spawn --> final{"Closure result?"}
  final -->|changes_requested| affected["Select ONE affected Step; preserve open findings"]
  affected --> original
  final -->|blocked| blocked
  final -->|pass| accept["Accept Work Item; commit coherent records; continue authorized scope"]
```

Use Explorer for questions, ideas and planning preparation; the main thread
answers the user and writes authorized Plans. Handle stop, resume and known
progress directly. A missing Step for unchanged binding Acceptance follows
operations; it does not authorize changing scope.

Before acting, check authority, the original task, role and prerequisites.
Before reporting, check relevant evidence, required fields and the user's
language. Correct mismatches; do not print a checklist transcript. Missing
evidence is a named gap, not a pass. Waiting for a child is working, not blocked.

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.

| Condition | Required route |
| --- | --- |
| Python and every named helper are available | Use the bundled helper. |
| Missing Python, script, dependency or helper error | Stop the affected operation; do not substitute manual execution. |

Helpers: `scripts/build_dispatch_prompt.py`, `scripts/validate_profile.py`, `scripts/resolve_model_pair.py`, `scripts/select_context.py`, `scripts/check_text_size.py`.
