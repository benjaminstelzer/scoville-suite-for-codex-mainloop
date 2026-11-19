---
name: scoville-ask-for-codex
description: Ask one or more configured advisers for independent advice or reviews from Codex, through fresh Codex subagents or Claude CLI. Use when the user requests an Ask consultation, a second opinion, or a review by specified advisers. Ordinary questions to the current assistant do not trigger a consultation.
compatibility: "Codex desktop online, Python 3.11+ and filesystem access. Native advisers require collaboration agent tools. Claude advisers require authenticated Claude Code CLI; Opus 5.5 requires CLI 2.1.280+, Fable 5.2 requires 2.1.321+."
---

# Scoville Ask for Codex

Ask collects independent answers in the calling task. In a review, each
adviser assesses the same evidence. In a consultation, you synthesize the
independent answers. Advisers only inspect; they change nothing, run no tests
and do not delegate. Later changes are the caller's.

The helpers give advisers the shared writing rules and keep the user's literal
question unchanged. For an adviser question or follow-up you compose, apply
[agent instruction design](references/instruction-design.md).

## Choose the consultation

All Skills in this suite are installed and enabled together. Use the
Skill that owns a concern without checking its availability, and load only the
instructions the task needs.
Do not use a Skill that needs explicit activation before it is activated, or
one the user excluded.

For a one-time settings lookup or override, use
[configuration](references/configuration.md) to resolve the settings read-only
and report them. It starts no adviser. For a request to save settings, use
the configuration reference's route for this package. Continue below when
the request calls for independent advice or review.

Infer `review` or `consultation` from the actual question; an explicit mode
wins. “Could this patch lose data?” is a review even without “for review”. If
you cannot tell which outcome the user wants, ask before dispatch. Do not ask about a mode, advisers or permission the request already establishes.

Resolve settings with `scripts/ask.py`:

| Priority | Settings source |
| --- | --- |
| 1 | Unsaved request overrides. |
| 2 | Selected project's `.scoville/config.json`, `ask` section. |
| 3 | [config.default.json](config.default.json). |

| Adviser selection | Presets |
| --- | --- |
| Explicitly named | Exactly those presets, even if absent from the default list. |
| None named | Default adviser list; it is not an allowlist. |

Use exactly the requested routes, models and efforts. Identify results by
adviser ID; a display name is not an agent handle. Resolve selected
presets in one call and report each adviser's settings. Read
[configuration and helper inputs](references/configuration.md) for settings
resolution, migration or the first helper call.

The actual host validates the requested model and effort when native
spawn_agent runs. Report a rejection; substitute no other model or route.

An explicit Ask request authorizes the full consultation: create the needed
adviser subagents, exchange the necessary questions and answers and return the
results, without separate approval for agents or messages and without
authorization fields. Respect explicit user limits and host requirements.
Native Ask uses direct collaboration tools in the calling chat.

## Ask and collect

Apply style rules only to the framing you write. Keep the user's literal
questions, quotations and technical data unchanged, except for authorized
edits and required secret redaction.

Prepare a self-contained question:

- Include scope, requirements and raw evidence, with paths and the
  working-tree scope when relevant.
- From a fresh consultation exclude your verdict and intermediate reasoning,
  previous adviser answers, unrelated history and secrets.

When review evidence can change during collection, bind the assignment to the
applicable revision or identifiable source state. If the evidence drifts,
attribute each finding to the state it actually covers and report any review
still missing for the requested state.

Read [native operation](references/native.md) or
[Claude operation](references/claude.md) for each selected route.

1. Report invalid settings and hold the affected dispatch. Independently
   dispatch each selected adviser with fresh context and the resolved settings
   within host capacity and process limits. A native adviser may write a
   temporary file only for an oversized answer under [native delivery](references/native-delivery.md).
   Native spawning adds no write barrier. Claude has its own tool restrictions
   and opt-in web access.
2. Collect by exact adviser and current assignment. Keep waiting for running
   agents or processes. An answer that only asks for clarification remains
   open. Use the retained native handle for necessary clarification. A further
   Claude call follows the Claude reference's authorization rules.
3. Accept a complete answer to the current question. Report partial answers,
   failures and pending handles with their reasons when collection cannot
   complete. A failed adviser stays in the report without substitution.

| Mode | Do |
| --- | --- |
| consultation | Synthesize agreement, differences and useful conclusions; invent no consensus. |
| review | Keep findings apart from untested concerns; verify findings before authorized fixes. |

Neither mode requires a second exchange round.

Apply [Evidence-based conclusions](references/writing.md#evidence-based-conclusions)
to exchanges with advisers. Present claims and evidence neutrally, also when
you ask whether an adviser accepts or objects, and do not press for agreement.
An unexplained concession does not resolve a finding. Consensus does not
replace a required review acceptance.

Retain requested and actually reported model and effort separately; unreported
values are unknown.

## Follow-up after completion

Retain the answer, evidence, settings and the exact native handle or Claude
session ID. Resume only for an explicitly requested follow-up, on the original
route with that exact ID; the most recent session may belong to another
consultation.

| Route | Follow-up settings |
| --- | --- |
| Native | Unchanged. A requested change needs a fresh adviser: explain that choice and obtain it unless already authorized. |
| Claude | Unchanged unless explicitly overridden. |

A completed review stays available: do not ask about keeping it open and do
not close it when the user changes topic. Claude print mode exits after its
answer; a retained ID is saved history, not a running agent.

## Shared references

Read one when its condition holds. A complete, unchanged copy in context
counts as read, including one embedded in your assignment. Fetch incomplete
or changed passages, and reload when requested.

- [Writing](references/writing.md): a plan, decision, instruction, review, handoff or a report the user asked for as the result; a disputed conclusion.
- [Machine data](references/machine-data.md): a structured report, log file or saved state you must evaluate, such as JUnit XML or coverage data; a test runner's console summary is not one.
- [Shell commands](references/shell-commands.md): composed text or scripts passed through a shell; quoting, PowerShell encoding, exact bytes or several exit statuses matter.
- [Output delivery](references/output-delivery.md): before a command whose output may exceed the display limit or is needed as evidence and cannot be reproduced; text that must fit a known limit; delivery as a file.
- [Python discovery](references/python-discovery.md): a bundled helper or other Python you run, no interpreter verified this session.
- [Instruction design](references/instruction-design.md): a reusable instruction, Skill rule or prompt template.
