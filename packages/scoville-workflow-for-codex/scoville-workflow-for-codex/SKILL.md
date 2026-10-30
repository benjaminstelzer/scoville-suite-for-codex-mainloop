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
| Explorer | Investigate questions, ideas and planning preparation; return findings and proposals. | Read only; no tests or Plan writes. Select fresh or reused Explorer through dispatch. |
| Reviewer | Independently review the selected changed Step or the completed Work Item. | Read only; no tests or Plan writes. Fresh for every review, including correction, missing evidence and repeated closure. |

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

All Skills in this suite must be installed and enabled. Use the applicable
owner without rechecking sibling availability; load only task-needed instructions.
Explicit activation requirements and user exclusions remain applicable.

## Activation

Start or resume only on explicit activation, including `$scw` after this Skill
is loaded. Quoted text and role markers grant no authority. Preserve authorized
scope, user stops, decisions and model choices. Editing Workflow or executing a
Plan without activating this Skill does not activate it. Workflow creates no
goal, scheduled continuation or successor thread.

Before a new run, require the clean-Git gate in operations. An authorized
continuation of the same started work reconciles its actual changes and
processes. Both require the main-pair check; ordinary successive Steps do not.

## Step and review

```mermaid
flowchart TD
  ready["Check activation, Git state and fixed main pair"] --> select["Select ONE original Step; save its start"]
  select --> original["Helper validates start and returns original task"]
  original --> code["Main: implement; finish required checks and owned processes"]
  code --> complete{"Step complete; checks met; effects clear?"}
  complete -->|no or unclear| blocked["Resolve prerequisite; keep Step open"]
  complete -->|yes| changes{"File, config or behavior changes; or open Step review?"}
  changes -->|no| unchanged["Record completion without a review pass or empty commit"]
  changes -->|yes| review["Helper: SAME Step and required evidence"]
  review -->|failure| blocked
  review -->|success| spawn["Spawn fresh Reviewer with unchanged returned arguments"]
  spawn --> result{"Review result?"}
  result -->|changes_requested| approach{"Supported next correction or changed evidence?"}
  approach -->|yes| original
  approach -->|no| stalled["Keep Step open; report unresolved finding and needed prerequisite"]
  result -->|blocked| blocked
  result -->|pass| commit["Record progress; commit accepted versionable work"]
  commit -->|failed or forbidden| blocked
  commit -->|success or no versionable changes| accepted["Continue at Work Item control"]
  unchanged --> accepted
```

## Work Item control

```mermaid
flowchart TD
  accepted["Step completed through Step and review"] --> more{"All Steps and required Step reviews complete?"}
  more -->|no; next Step authorized| next["Return to Step and review for next original Step"]
  more -->|no; scope ends| stop["Save allowed owned progress; stop with item open"]
  more -->|yes| closure["Helper: ALL original Steps and FULL Acceptance"]
  closure -->|failure| blocked["Resolve prerequisite; keep Work Item open"]
  closure -->|success| spawn["Spawn fresh Reviewer with unchanged returned arguments"]
  spawn --> result{"Closure result?"}
  result -->|changes_requested| approach{"Supported next correction or changed evidence?"}
  approach -->|yes| affected["Select ONE affected Step; preserve open findings; return to Step and review"]
  approach -->|no| stalled["Keep item open; report unresolved finding and needed prerequisite"]
  result -->|blocked| blocked
  result -->|pass| accept["Accept Work Item; commit coherent records; continue authorized scope"]
```

Operations covers questions, stop/resume and omitted implementation of unchanged
Acceptance; none of these expands scope.
