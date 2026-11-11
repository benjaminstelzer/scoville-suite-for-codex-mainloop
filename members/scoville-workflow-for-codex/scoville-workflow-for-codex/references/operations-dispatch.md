# Original tasks and native dispatch

`--unit W-001/step-2` selects one original Step for main or Step review.
`--unit W-001` selects Reviewer closure. `--plan PLAN-NNNN` selects the canonical
Plan (default: active). Explorer may include it or omit both flags for an
independent question.

`--plan-root <directory>` reads records from that project instead of
`--project-root`; it does not change the working workspace or configured pairs.
`--selector <path>` replaces unit selection with a compatible Plan selector.
Decision identity and binding projection still use the bundled Plan library;
this option does not replace that library or its format contract. Keep the
custom selector's own required sibling libraries with it.
`--max-output-bytes <bytes>` forwards a success-payload budget to the selector;
an insufficient budget returns a diagnostic and corrected call, not partial context.

## Contents

- Fixed pairs
- Original main task
- Child selection
- Build and deliver child assignments

## Fixed pairs

```text
python "<workflow>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace>"
python "<workflow>/scripts/resolve_model_pair.py" --role main --project-root "<workspace>"
```

The first command resolves schema-2 settings without writing. The second checks
the own active native model and effort against main. It binds CODEX_THREAD_ID,
session_meta, task_started and turn_context; configuration, self-report and user
confirmation alone are not that proof. Retain its session_path for later required
checks through `--session-path`. A missing or mismatching proof stops coding.
The main-thread triggers and invisible-change limit are in operations; query
only on those triggers, not per Step. The host pair is changed in Codex; Setup only stores
the configured pair.

Use fixed main, review and explore pairs. Routes select no models.
The dispatcher compares existing execute annotations against main,
including partial annotations. A match needs no stop; a mismatch or unknown
fulfilment needs a user choice before coding, not a per-Step model change.
Old Workflow forms require explicit Setup cleanup; reading never migrates them.

## Original main task

Save start/resume through Plan, then use the helper before the first edit:

```text
python "<workflow>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace>" --plan PLAN-NNNN --unit W-001/step-2 --role main --communication-language "<language>"
```

The helper returns the original Step to main and validates the saved active Plan,
current item and in_progress Step. It creates no child or rule reload and reuses
the verified main pair without another native query.
Main output lists Decision identities, not bodies. Before editing, read each linked
accepted source completely unless its unchanged full text or valid original binding
projection is already retained. After compaction, restore that binding first
and reread uncertain sources. Do not compose a shortened projection yourself,
because it could drop a condition.

## Child selection

```mermaid
flowchart TD
  role{"Role?"}
  role -->|Reviewer| fresh["Select fresh Reviewer; fixed pair and next number"]
  role -->|Explorer| exists{"This thread's Explorer for SAME investigation or follow-up?"}
  exists -->|none or independent request| create["Select fresh Explorer; fixed pair"]
  exists -->|yes| idle{"Matching complete final confirms idle?"}
  idle -->|running or uncertain| wait["Wait or resolve the native state; dispatch nothing"]
  idle -->|yes| same{"Pair and loaded rules unchanged?"}
  same -->|yes| reuse["Select followup to retained handle and pair"]
  same -->|no| create
  create --> number["Use next Explorer number; preserve needed prior findings"]
  fresh --> build["Helper builds assignment and native arguments"]
  reuse --> build
  number --> build
  build --> valid{"Exit zero and complete successful output?"}
  valid -->|no| stop["Stop dispatch; resolve helper failure"]
  valid -->|yes| call["Call native tool with returned arguments unchanged"]
```

Confirmed failure follows operations before fresh work. No context measurement,
threshold or replacement protocol is part of dispatch. Use native type selection
only if it is exposed and compatible with the fixed pair, without emulating it
or installing custom agent files. Operations owns native waits, complete finals
and closing.

## Build and deliver child assignments

Supplemental context that you write for an assignment or review input follows
[agent instruction design](instruction-design.md). Keep original Plan text and
complete native finals unchanged, and include the checks, effects, attribution
and limits the selected role needs. The helper supplies the role and result
contracts, so add no authoring instructions to its message.

```text
python "<workflow>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace>" --plan PLAN-NNNN --unit W-001/step-2 --role reviewer --communication-language "<language>" --format create --project-name "<project>" --agent-number <number> --supplemental-context -
```

Send needed checks, effects, attribution and limits through stdin with
`--supplemental-context -`, or pass an existing UTF-8 file's path, not literal text.
`--reviewer-result` carries
the relevant complete native review final unchanged, including a closure finding
when correcting one Step. Only one input may use stdin. Pass finals and Plan
text as they are; a composed replacement or rewrite would give the Reviewer
your reading instead of the source.

The helper derives Plan identity, Goal, Non-goals, Work Item fields, Instructions,
selected original Step and linked Decision sources. Fresh children receive full
accepted Decisions or their valid unchanged binding-section projection under
Plan's Decision format. The main thread selects IDs, not sections or paraphrases.
Step assignments exclude other Step bodies, accumulated Evidence and Work Item
Next action. Closure includes the full original Work Item and Acceptance.
The helper's fixed scope sentence prevents Goal and Decisions granting role rights.

Fresh children receive complete role, writing, shell and result rules once;
Reviewers also receive the code-review policy. Embedded rules satisfy their
required reads. Codex supplies project instructions; add no AGENTS.md loader.
Explorer reuse sends the new task, current binding context, complete necessary
inputs and communication language, with Decision identities instead of retained
bodies. Read new, changed or uncertain Decisions completely; omitted nonbinding
background is no reread reason. Retained unchanged rules and Skills stay loaded;
load newly relevant sources and specialized references as needed.

For Explorer, use `--role explorer --supplemental-context "<request.txt>"` or stdin.
Preserve the user's exact request and requested response format with investigation
constraints.
For reuse, add `--agent-id`, its retained `--model` and `--thinking`
and the same agent number. If that pair conflicts with new settings, create a
fresh Explorer rather than silently changing followup's model.

Pass the user's current or explicitly chosen language with `--communication-language`;
Plan language and locale do not select it. Call the native direct tool with the
helper's arguments unchanged: fresh spawn or Explorer followup. Settings fix fresh
pairs; manual flags cannot bypass them. Number agents per role across items and
compaction; reuse keeps the number.

Assignments up to 8 KiB UTF-8 go directly into native messages. Larger assignments
use a new external system temporary file; `--assignment-file` can choose a new
absolute readable path. Keep it through the assignment. Children read it completely
before work using their chosen method. `--format prompt` returns text only.

Prepare complete UTF-8 files with literal-safe writes before dependent calls.
Require exit zero and complete successful output. A missing input, inaccessible
assignment file, capacity refusal or helper failure stops that operation:
correct the named cause before running it again, and respawn after a capacity
refusal only when a slot is actually free. Where a publication or spawn may
already have taken effect, establish its actual state before another attempt.
Never duplicate a dispatch, truncate or fabricate a result or substitute a
sidebar chat. Internal selection budgets can be corrected explicitly; binding
user or host caps need their owner's decision.

Match complete native results to retained handles and assignments. Partial messages
and metadata are not results. Read complete externalized results under shared
delivery rules. Read-only children may prepare only necessary oversized results;
they run no project tests, write no Plan records and create no other agents.
