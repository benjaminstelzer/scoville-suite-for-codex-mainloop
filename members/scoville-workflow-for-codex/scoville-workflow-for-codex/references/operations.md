# Main-thread operations

{{ include: helper.policy }}

Use Scoville Plan for records and [dispatch](operations-dispatch.md) for
helper commands. The main thread implements, runs required checks, writes
records and commits. Keep the authorized scope, the user's stops, independent
Decisions and unrelated work. An authorized correction changes only its
affected original Step; add no optional ideas or hypothetical hardening.

## Contents

- Start and continue
- Execute one Step
- Close the Work Item
- Questions, results and missing evidence
- Stop, compaction and failure

## Start and continue

Before a new run's first Plan write:

1. Run `git status --porcelain --untracked-files=all`.
2. If it fails or lists a path, do not start. Earlier work is not this run's
   to dispose of: do not discard, stash, stage or commit it to clean the tree.
3. Exception: all listed paths are under `.scoville/temp`, which has no
   `.gitignore`. Create `.scoville/temp/.gitignore` containing `*` and check
   again.

An authorized resumption of the same started work reconciles what actually
exists: Git changes, results, processes and open reviews. It need neither
repeat the new-run gate nor commit unreviewed work first. Same paths alone do
not show that a change is this run's; clarify foreign or uncertain work before
touching it.

On activation and on authorized resumption, run dispatch's `--role main` check
of this session's actual model and effort against the configured main pair.
Repeat it only when that pair changed, the host visibly changed the model or
the verified result is lost. Between unchanged Steps keep the verified
result. On an unknown or mismatching result, do not implement until it is resolved; planning and clarification continue. Do not
promise to detect a model change the host does not show.

Native child operations:

- Require those this run actually needs: spawn, wait, inspect, interrupt, and
  followup for Explorer reuse.
- Keep each child's exact handle, launched pair, assignment and complete
  final, and a counter per role.
- Match results by sender and assignment, not title or sidebar ID.
- While a child works, use native waits and keep the turn active. A timeout is
  not a failure.
- List agents, narrowly scoped, only to resolve uncertain startup or state or
  a missing result, not when you hold the matching complete final.
- Use agent types and close operations only if exposed; emulate neither. Close
  a finished Reviewer, if supported, after saving its complete final.
- An interrupt alone proves neither termination nor a free agent slot.
- Raising thread limits is the user's decision.

When the Plan is known, set this chat's title to `SC-WFL <Plan-ID>` with
set_thread_title and no threadId. Report rename errors. Keep the title through
pauses and compaction. Report position changes briefly in the user's current
language. Records use the language Plan prescribes; keep quotes, technical
literals and required field names exact. Messages between main thread and children carry only the labelled fields they need.

## Execute one Step

| Boundary | Required action |
| --- | --- |
| Work Item start | Select the authorized Plan and Work Item in order, dependencies met. Record HEAD in existing Evidence for closure. Before coding, save the actual start or resume through Plan; selecting starts nothing. |
| Step start | Save the selected original Step as in_progress. Run the main-task helper; it checks the saved start and an existing `[execute: ...]` annotation. Use its task unchanged; choose no other model per Step. Keep the Step's start HEAD in context. |
| Implementation | Apply [Code quality](code-quality.md) when choosing the implementation; its complete unchanged text in context counts as read. Do only this Step and its required checks. Preserve completed effects. Before review, finish or safely stop your write, test and restore processes. Read required sources completely. Reuse unchanged passing checks. |
| Review decision | Answer the diagram's change question from `git status`, `git diff` and the observed file, configuration and behavior effects. Closure checks unchanged Steps. Record no review pass that no Reviewer returned. |
| Changed Step | Give the review helper the same original Step, the needed check and effect evidence and each relevant complete open review result. When the Work Item has only this Step, say so in that evidence; the Reviewer then checks the full Acceptance. The helper adds the independent review rules: full diff, dependencies, consumers and Acceptance. |
| Correction | Select the one affected original Step. Resolve each finding: correct it, narrow a statement the evidence does not support, or refute it with evidence. Complete required checks. Obtain a fresh review; it focuses on the correction, its effects and open findings within the full original scope. Reuse still-valid evidence. |
| Repeated finding without new evidence or changed conditions | Continue only with a supported next diagnosis or correction. Otherwise keep the Step open, report the unresolved finding and record an actual external prerequisite in Work Item blockers. Ask the user only for a missing decision. |
| Accepted change | After completion and the required pass, record progress and commit reviewed versionable changes with Plan progress before advancing. Stage only this Step's reviewed work and its Plan progress, never foreign or unreviewed changes, because the commit records what the review accepted. A failed or forbidden commit holds advancement until resolved. Afterwards check with `git status` that none of this Step's work is left uncommitted; foreign changes stay untouched. Make no empty commit. |

Updating Plan records alone needs no review.

A Step review compares against Git HEAD; closure against the Work Item's start
commit. If HEAD moved unexpectedly, find the commits and effects that moved it
before treating an empty diff as unchanged. An accepted source baseline
proves nothing about behavior, ignored outputs or non-file effects.

Pass check results, effects, attribution and limits to a child through
`--supplemental-context`. Inspect generated content only when the original
Step, Acceptance, a project rule or a concrete defect requires it; normally
current successful generation plus observed expected outputs suffices.

Missing required proof holds the work that depends on it. Recover it from
existing results or run the authorized check that has not passed yet. Do not
repeat an unchanged successful check or a nonrepeatable action, and do not
widen the work. Name proof that stays unavailable. Keep nonrepeatable evidence
that closure needs as the existing result or artifact, referenced in existing
Evidence; no synthetic execution final, new per-Step report or source archive is required.

## Close the Work Item

When the Work Item has exactly one Step and its passing Step review checked
the full Acceptance, that review is the closure review; dispatch no second
Reviewer. Every other Work Item gets the diagram's closure review: give the
helper the needed current source and effect evidence, retained proof and each
relevant complete open review. An earlier review, Step or closure, is
evidence, not a current pass. Closure stays within the original Work Item.

| Closure finding; the item stays open | Action |
| --- | --- |
| Affects an existing Step | Select that one Step; use its correction loop. |
| An unchanged, already binding criterion lacks implementation and no Step covers it | Append one bounded Step through Plan; run the normal loop. |
| Changed scope or Acceptance, a contradiction or unclear intent | Ask the user. |

Keep original Steps, order and completed effects. After Acceptance and closure
pass, validate and commit the records as one consistent state under repository
checks. Keep this thread's Explorers and counters.

## Questions, results and missing evidence

Send a question, idea, proposed change or planning preparation that needs
investigation to an Explorer selected through dispatch, with the complete
request and needed context.
The same project or file alone does not make independent questions one
investigation. Find the Explorer through retained assignments and handles, not
topic IDs or a registry. From its findings and proposals the main thread
answers the user and writes authorized Plans. Stop implementation that a
proposed change invalidates before exploring it. Known progress, stop or
resume and a question you can answer from what you already hold need no
Explorer; do your Step's own reading yourself.

| Child result | Meaning |
| --- | --- |
| done | Assigned exploration finished; not acceptance. |
| pass | Assigned review completed without open defects or required proof gaps. |
| changes_requested | Actual defect with location, effect, correction and affected Step, or none. |
| blocked | An actual prerequisite or required decision is missing. |

Before passing a relevant native final to another assignment, save it
complete and unchanged with a permitted literal-safe write, as a new file in
the system temporary directory outside the project; a file in the project
would show up as an unattributed change in the next review. A brief Plan
summary does not replace it.

The main thread closes a review's evidence gap itself:

1. Apply the missing-proof rules in "Execute one Step".
2. Keep the original changes and the relevant open review result.
3. Create a fresh Reviewer for the same scope.

## Stop, compaction and failure

When the user stops the run:

1. Start no new work.
2. Finish or safely stop the running write, test or restore operation, and
   interrupt running children by exact handle. Then establish their actual
   termination and the process state; the status an interrupt returns proves
   no termination.
3. Save and validate the observed Plan position, unfinished checks, effects
   and open reviews.
4. Resume only when authorized.

After compaction, read this same thread's actual Plan, Git, processes, results
and effects before continuing. Do not redo completed work to rebuild history.

Replace a child only when its failure is confirmed, it has ended and you know
what it left behind. Give the new child the remaining original scope, valid
evidence and open findings. While a child's startup or result is uncertain,
resolve its state before dispatching again; a duplicate would do the same
work twice. A child that completed with `blocked` did not fail.

Only for an explicitly authorized upgrade or migration, use Scoville Setup's
"Workflow pairs and migration" section before switching a running project.

Before ending, commit this run's pending records only if no unreviewed implementation
remains; otherwise report the paths. The run is complete only when the
requested Acceptance is met, every required Step review and closure passed,
the Plan is closed consistently and no process or child still runs. Report the
actual outcome and limits in the user's language. A pause or blocker is not
completion and creates no automatic successor.
