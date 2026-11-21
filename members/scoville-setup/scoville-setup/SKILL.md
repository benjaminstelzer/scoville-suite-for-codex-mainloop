---
name: scoville-setup
description: Show, change or explicitly migrate the selected project's Scoville Ask and Workflow settings. Use for fixed main-thread, reviewer and explorer model pairs and Claude limits. Excludes running workflows, installations, updates and monitoring.
compatibility: "Codex Suite with Python 3.11+, bundled configuration helpers and filesystem access to the selected project. Configuration changes are local; this Skill starts no host tasks."
---

# Scoville Setup

{{ include: family.contract }}

Manage `.scoville/config.json` in the selected project's absolute root. Saved
values override defaults per field. There is no personal layer and no
parent-directory search.

Setup only reads and writes this configuration. Starting advisers or Workflow,
installing or updating Skills and publishing packages each need their own
request. A one-time choice stays in the request; Workflow has no model
choice per Step.
Change saved settings between runs, following the safe
[upgrade route](#upgrade-a-running-project) when a running project needs
migration.

## Choose the operation

| Operation | Behavior |
| --- | --- |
| show | Reads only; creates no file. Shows effective fixed pairs, or resolves old routes with cleanup_required. Reports invalid sections together under ok:false, without partial effective success. |
| set | Accepts explicitly requested changes and applies the schema's derived changes. Old Workflow settings need cleanup before a Workflow save. An Ask-only save leaves Workflow unchanged. |
| cleanup | Migrates old Workflow settings to schema 2, only when explicitly authorized. Ask and foreign values stay unchanged. An unchanged valid configuration returns saved: false. |

For a one-time Ask override, use the read-only resolve route in Scoville Ask
for Codex's `references/configuration.md` and report the resolved values.
This route saves nothing and starts no adviser.

## Ask

Before an Ask save, read the saved settings and precedence in Scoville Ask
for Codex's `references/configuration.md`; the helper applies that precedence
with the patch as the later layer. [Defaults](assets/ask.default.json)
provide the shipped values. An explicitly supplied `advisers` list replaces
the current list and keeps its own inline precedence.

## Workflow pairs and migration

Schema 2 has fixed `main`, `review` and `explore` pairs, each with `model` and
`reasoning`. With set, send only requested fields, such as
`workflow.review.reasoning`. With cleanup, send both fields for each pair you
explicitly supply. Defaults come
from [Workflow](assets/workflow.toml), the one place that lists their values.
The host controls the actual main-thread model; saving the `main` pair neither
changes nor verifies it.

| Observed Workflow settings | Action before saving |
| --- | --- |
| Current schema, no cleanup required | Use `set` for requested changes. The helper supplies the schema marker. |
| Schema 2 with known legacy fields | With cleanup, keep existing pairs unless the user changes them. Use the helper's validated effective defaults where applicable. |
| Schema 1 routes | With cleanup, obtain an explicit `main` pair, which cannot be inferred from execute routes. Keep the single effective pair for `review` and `explore` when each is unambiguous. Obtain missing choices when routes differ. `explore` inherits from effective execute routes field by field. |
| Invalid settings or unsupported fields | Report the diagnostic and resolve the affected inputs before saving. |

The cleanup command only rewrites
`.scoville/config.json` and leaves Plans and `.codex` settings alone.

### Upgrade a running project

To upgrade a running project, the upgrade, the cleanup, the migration commits
and the continuation each need the user's explicit authorization; one request
can cover several, and the steps below grant none:

1. Let the old version reach a reviewed, quiescent commit boundary, preferably
   Work Item closure.
2. Preserve the old closure evidence still needed. If essential proof exists
   only in volatile host state, finish the Work Item on the old version before
   switching.
3. Commit a changed tracked Plan.
4. Switch versions through the separately authorized update, then reload the
   target version and run its authorized Setup cleanup with the chosen pairs.
5. Before the authorized continuation, commit a tracked configuration change
   separately under project checks. Untracked configuration needs no commit.

An installed new version proves neither cleanup, host-model change nor reload.

{{ include: helper.policy }}

## Prepare and run the selected command

```text
python "<setup-skill-directory>/scripts/setup.py" show --project-root "<project-root>"
python "<setup-skill-directory>/scripts/setup.py" set --project-root "<project-root>"
python "<setup-skill-directory>/scripts/setup.py" cleanup --project-root "<project-root>"
```

Set and cleanup read UTF-8 JSON from stdin. Arrange capture of the original
machine result and exit status before saving.

- Generate the JSON patch with a serializer so quoting preserves the values.
- Use `ask`, `workflow` or both for set, and only `workflow` for cleanup.
- Include only the requested changes, with the values the user gave. If
  capturing with the bundled checker, follow the stdin route in
  [Output delivery](references/output-delivery.md) so the same execution
  receives the serialized patch and yields the retained result.
- Set offers low, medium, high and xhigh. Existing special levels survive
  unrelated saves and migration.

The helper validates changed sections before saving. An invalid value does not
authorize a partial save. The user can edit `.scoville/config.json` manually
for supported special reasoning levels; agent-driven changes use the helpers
above.

## Verify the result

Use the helper's status and `saved` flag, the requested stored fields and
their resolved effective values. Compare resolved adviser objects by their
IDs and fields. `set` returns effective values for the patched sections.
`saved: false` means this execution wrote nothing, which may mean the requested
configuration was already in place. Report mismatches with their diagnostics.
Saving fewer, other or wider values needs the user.

If a save's result is unclear, recover its captured output and read the
requested stored fields at the selected project root. Verify their effective
values with `show`. If an unrelated section prevents the combined result, use
Ask's read-only resolve or Workflow's `resolve_model_pair.py --show-config`,
with `--project-root` set to the selected project. Report the original `saved` flag as unknown if its
output is unavailable. Resolve the local failure before continuing the same
requested save for a missing or different stored value.

{{ include: rules.references }}
