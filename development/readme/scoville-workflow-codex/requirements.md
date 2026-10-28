## What it enforces

- **Runtime:** Codex desktop, Python 3.11+, Git and the required native spawn,
  wait, inspection and interruption tools. Explorer reuse needs followup.
- **Start:** A new run requires a clean Git workspace. Authorized continuation
  reconciles its own started work; it never absorbs foreign changes.
- **Ownership:** Main plans, codes, checks and commits. Explorer and Reviewer
  remain read-only. Changed Steps receive independent review; every Work Item
  receives closure over all original Steps and full Acceptance.
- **Boundaries:** Commit accepted versionable Step changes and Plan before
  advancing. No intermediate, empty or foreign-change commit. Keep review quiet.
- **Children:** Every review is fresh, including corrections, evidence followups
  and closure. Explorer reuse retains rules and pair within the same investigation;
  independent requests get fresh Explorers, even in the same project or file.
- **Continuity:** Preserve actual effects, open reviews and stop position through
  compaction in the same chat. No automatic successor or capacity changes.

No minimum Codex version has been independently established. Optional native
type selection and close are not required. Use them only when exposed and
compatible. Agent capacity depends on the host's configured limit.

Workflow activation authorizes accepted-Step commits subject to user and project
restrictions. See [operations](https://github.com/benjaminstelzer/scoville-suite-for-codex-mainloop/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md).
