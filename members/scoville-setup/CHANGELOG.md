# Changelog

## 2026-11-20 - Python is required

The runtime helper rule now has the same wording as in every Skill of the suite: helpers need Python 3.11+, and without it, or after a helper error, the affected operation stops and reports the cause. Behavior does not change here; the general edition dropped its manual no-Python routes, so one wording now serves both editions.

## 2026-11-20 - Clearer structure

The sections that set the values come before the section that saves them. Upgrading a running project has its own heading.

## 2026-11-19 - One wording per rule

Sentences that repeated the generated reference list or another row are removed.

## 2026-11-19 - Show and set commands

The show and set commands now sit with their operations. Legacy migration follows in its own section.

## 2026-11-16 - Owner decisions on three open points

- A one-time choice stays in the request. Setup no longer points to a model choice kept in a Plan Step, because Workflow has none.

## 2026-11-15 - Rules that contradicted each other

- The precedence of saved Ask settings is stated once, in Scoville Ask's configuration reference; Setup's helper applies it with the new patch as the later layer.
- Shared rules: a reply uses the language of the request, while a record or file you edit keeps the language it is written in. Files saved with `--publish-full` are delivered output, so cleanup leaves them in place. A rule that holds only until something happens states that end in the rule.

## 2026-11-14 - Goodhart corrections

- One explicit request can authorize several steps of an upgrade.
- Shared rules: a final report after a small change no longer loads the writing reference, a test runner's console summary is not machine data, and a complete copy of a reference in context counts as read.

## 2026-11-12 - Concrete instructions and release command

- State each rule as a trigger, an action and a result the agent can check itself.
- Reword the shared writing, machine-data, shell and output-delivery rules the same way.

## 2026-11-10 - Leaner instructions and Plan validator fixes

- Link the shared writing, machine-data, shell, output-delivery and Python references directly from SKILL.md, each with its reading condition, instead of chained read-first rules.
- Shorten the shared rules: drop permission disclaimers that have no recorded incident and state scope and reason for the stop rules that remain.
- Reduce output delivery to when the checker is needed, its three calls and how to read a result. Every capture failure now names its next step in the helper's `instruction` field.
- State the reasons behind the migration and save rules.

## 2026-10-30 - Source reading and UTF-8 diagnostics

- Clarify direct source reading and producer-owned instruction-design loading while preserving report evaluation.
- Explain retained bytes, child status and unresolved text interpretation after invalid UTF-8.
- Remove redundant layout wording without changing activation or sibling requirements.

## 2026-10-30 - Capture and diagnostic follow-up

- Report Schema 2 cleanup requirements with the affected legacy fields and keep read-only diagnostics free of save-failure claims.
- Support complete command capture without a numeric token limit and retain primary failure diagnostics.

## 2026-10-30 - Shared criteria and focused helper fixes

- Preserve configuration modes, reject redirected writes and report invalid sections without partial success.
- Repair explicit mixed-format cleanup, retain valid inherited pairs and separate unrelated section reads.
- Add normal host interface metadata and describe the development cycle.

## 2026-10-29 - Actionable choices

- Name the rejected scalar choice and its field while withholding nested settings payloads; preserve existing files on failure.
- Inherit corrected capture, source/report and native delivery rules from their shared owners.

## 2026-10-29 - Follow-up corrections

- Restore the manual user route for supported special reasoning levels while keeping agent changes helper-based; load shared rules before data requests and disputed conclusions.

## 2026-10-29

- Load data, shell and output rules when needed while keeping configuration validation and save-error stops. Unsupported-choice errors name the field and supported levels, confirm that nothing was saved and no longer suggest manual configuration edits.
- Move the running-project migration procedure to Setup, including the reviewed safe boundary, evidence preservation, reload and separate authority for cleanup, commits and continuation.
- Separate technical requirements from observed gpt-6.1-sol / low results. Actual show, partial-save and cleanup cases preserved unrelated values and agreed with Workflow resolution. The initial show had no isolated byte checkpoint. Running-Workflow migration, installation, host-model binding and Claude behavior were not tested.

## 2026-10-28

- Clarify fixed-pair patches, explicit migration authority and one-time Ask resolution through Ask's own configuration reference; use the shared UTF-8 transport procedure and preserve save-error stops.
- Limit new Setup reasoning choices to low, medium, high and xhigh; preserve supported manual special values on unrelated saves and migration.

## 2026-10-27

- Save schema-2 fixed main, review and explore pairs; migrate old Workflow tables only through explicit cleanup.
- Resolve old Explorer fields with their effective inheritance; require main and ambiguous choices before an atomic complete save.
- Preserve Ask, foreign values and supported special reasoning; show stays read-only and repeated cleanup writes nothing.
