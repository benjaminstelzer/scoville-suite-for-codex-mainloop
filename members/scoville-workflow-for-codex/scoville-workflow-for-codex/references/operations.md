# Main-thread operations

Use Plan for records and [dispatch](operations-dispatch.md) for helper inputs.
The main thread owns implementation, required checks, records and commits.
Preserve scope, stops, independent Decisions and unrelated work. An authorized
correction stays on its affected original Step; optional ideas do not expand it.

{{ include: family.contract }}

## Start and continue

For a NEW run, before Plan writes, require Git and empty
`git status --porcelain --untracked-files=all`. A failed command or listed path
blocks that start. Never discard, stash, stage or commit earlier work to become
clean. Exception: if all listed paths are under `.scoville/temp` and it has no
`.gitignore`, create `.scoville/temp/.gitignore` containing `*` and check again.

An authorized continuation of the SAME started work reconciles actual Git
changes, results, processes and open reviews. It does not require committing
unreviewed work or repeating the new-run gate. Same paths alone do not prove
ownership; foreign or uncertain work needs clarification.

On activation or authorized resumption, verify the configured main pair with
the own active native session through dispatch. Repeat only after its required
pair changes, a visible host-model change or concrete loss of the binding.
Unknown or mismatching evidence stops Coding; planning and clarification remain
allowed. Retain the valid binding between unchanged Steps. Invisible model
changes cannot be promised detected. Setup does not change the host model.

Require the native spawn, wait, inspection and interruption operations actually
needed for the run; Explorer reuse also needs followup. Retain exact child
handles, launched pairs, assignments, complete finals and per-role counters.
Match results by sender and assignment, not titles or sidebar IDs. While a
child works, use native waits and keep the turn active. Timeout is not failure.
Use a scoped native listing only to resolve uncertain startup, state or a missing
result. A retained matching complete final needs no routine new inventory.
Optional agent types and close operations are used only if exposed; emulate
neither. After saving the complete final, close a finished Reviewer if supported.
Interruption alone proves neither termination nor a freed agent slot. Do not
raise thread limits automatically.

When the Plan is known, set this chat's title to `SC-WFL <Plan-ID>` with
set_thread_title and no threadId. Report rename errors. Keep the title through
pauses and compaction. Communicate changed positions briefly in the current
user's language. Plan owns record language; preserve quotes, technical literals
and required field names. Internal messages use only necessary labelled fields.

## Execute one Step

| Boundary | Required action |
| --- | --- |
| Work Item start | Select authorized Plan/item in order with dependencies met. Record HEAD in existing Evidence for closure. Save actual start/resume through Plan before coding; selection alone starts nothing. |
| Step start | Save the selected original Step in_progress. Use the main-task helper: it validates saved start and explicit old execute bindings. Do not rewrite the task or choose another model per Step. Retain its start HEAD in existing context. |
| Implementation | Perform only this Step and required checks. Preserve completed effects. Finish or safely stop owned write, test and restore processes before review. Read required sources completely; reuse unchanged passing checks. |
| Review decision | Establish completion, required checks and clear file, configuration and behavior effects. Use Git status/diff and actual observed effects. No change plus no open Step review needs no Step review; closure checks that Step. Do not invent a pass. |
| Changed Step | Give a fresh Reviewer the SAME original Step, needed check/effect evidence and relevant complete open review results. Review scope is its actual changes, dependencies and affected Acceptance; risk changes depth, not the review duty. |
| Correction | Retain unchanged objections and select the ONE affected original Step. Correct it, complete required checks and obtain a fresh review. Preserve relevant open findings and still-valid evidence. |
| Accepted change | After completion and required pass, record progress and commit reviewed versionable changes with Plan progress before advancing. Never stage foreign or unreviewed work. Failed or forbidden commit stops advancement. Confirm the resulting clean Git state; make no empty commit. |
| Unchanged Step | Record actual completion without a Step review or ritual commit. Ordinary Plan maintenance adds no review phase. |

Git HEAD is the Step review base; closure uses the Work Item start commit.
Before editing, read linked accepted Decisions completely unless their unchanged
complete text or valid original binding projection is retained. Restore this
binding after compaction; reread uncertain sources. Do not select or paraphrase
binding sections yourself.
If HEAD moved unexpectedly, reconcile actual commits and effects before treating
an empty diff as unchanged. A known accepted source baseline does not prove
behavior, ignored outputs or non-file effects. Keep necessary nonrepeatable
evidence available for closure through existing results or artifacts, referenced
in existing Evidence. No synthetic execution final, new per-Step report or
source archive is required.

Use the existing supplemental-context transport for check results, effects,
attribution and limits. Inspect generated content only when the original Step,
Acceptance, project contract or a concrete defect requires it. Current successful
generation plus observed expected outputs normally suffices. Missing required
proof stops dependent work; do not rerun successful or nonrepeatable effects
merely to reconstruct it.

## Close the Work Item

After all Steps and required Step reviews complete, create a fresh Reviewer for
the whole original Work Item: every original Step, full Acceptance and necessary
current source/effect evidence. This is closure, not an unrelated general audit.
Supply retained proof and relevant complete open reviews; old review coverage
is evidence, not a current pass.

A finding keeps the same item open. Select one affected Step and use its
correction loop. If no Step covers an omitted implementation of an already
binding unchanged criterion, append one bounded Step through Plan and run the
normal loop. Changed scope, Acceptance, contradictions or unclear intent need
the user. Preserve original Steps, order and completed effects.

Mark the Work Item done only after Acceptance and closure pass. Validate and
commit the coherent records under repository checks. Retain this thread's
Explorers and counters; no Reviewer is reused. Continue only the authorized scope.

## Questions, results and missing evidence

Send questions, ideas, changes and planning preparation to the read-only
Explorer with the complete request and necessary context. It returns facts,
proposals, scope and open choices. The main thread writes the Plan and answers
the user. Reuse its Explorer for the same investigation or a follow-up building
on its findings. A separate question independent of that investigation gets a
fresh Explorer, even in this thread; the same project or file alone is not enough.
Use retained assignments and handles, not new topic IDs or a registry.
Stop invalidated implementation before exploring a proposed change.
Known progress and stop/resume handling need no exploration.

| Child result | Meaning |
| --- | --- |
| done | Assigned exploration finished; not acceptance. |
| pass | Assigned review completed without open defects or required proof gaps. |
| changes_requested | Actual defect with location, effect, correction and affected Step, or none. |
| blocked | An actual prerequisite or required decision is missing. |

Capture each relevant native final completely and unchanged through a permitted
literal-safe write before supplying it to another assignment. A brief Plan
summary is not its substitute. The main thread handles review evidence gaps
itself: recover existing proof or complete missing authorized checks, retain
both original changes and relevant open review result, then create a fresh
Reviewer for the SAME scope. Missing proof is not permission to repeat an
unchanged successful check, nonrepeatable effect or broaden work. Name unavailable
proof and stop that dependent work.

## Stop, compaction and failure

On user stop, start no new work. Safely finish or stop the currently started
write/test/restore operation and interrupt running children by exact handle.
Establish actual termination and process state; an interrupt's previous status
alone proves no termination. Save and validate the observed Plan position,
unfinished checks, effects and open reviews. Resume only when authorized.

After compaction, recover this same main thread's actual Plan, Git, processes,
results and effects before continuing. Do not redo completed work to rebuild
history. A confirmed failed child can be replaced only after its termination
and retained work are understood. Give the new role the remaining original
scope, valid evidence and open findings. Uncertain startup or result forbids a
duplicate dispatch. A completed blocked result is not a failed agent.

When upgrading a running project to this variant, the old version first reaches
a reviewed, quiescent commit boundary, preferably Work Item closure. Preserve
needed old closure evidence before reload. If essential proof is only volatile,
save it once in a unique ignored `.scoville/temp/workflow-migration-<Plan>-<WorkItem>-<Nr>.txt`
and reference it in existing Evidence; commit a changed tracked Plan before
reload. No archive or per-Step report is introduced. If essential proof cannot
be preserved, do not switch within the Work Item. Then reload, explicitly run
Setup cleanup with chosen pairs, and separately commit a tracked configuration
change under project checks before authorized continuation. Untracked config
needs no commit. Installation proves neither cleanup, host-model change nor reload.

Before leaving, commit pending owned records only if no unreviewed implementation
remains; otherwise report the paths. Completion requires requested Acceptance,
required Step reviews, closure, coherent Plan closure and quiescent processes
and children. Report actual outcome and limits in the user's language. A pause
or blocker is not completion and creates no automatic successor.
