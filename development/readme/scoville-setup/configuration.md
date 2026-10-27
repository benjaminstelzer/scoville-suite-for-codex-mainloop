## Configuration

Settings are owned by the selected project's `.scoville/config.json`. Ask selects
advisers and Claude limits. Workflow schema 2 has fixed main, review and explore
model/reasoning pairs. The host owns the actual main model; Setup only saves its
required pair. Show is read-only and includes defaults.

Explicit cleanup converts old route tables after main and ambiguous pairs are
chosen. It removes obsolete Workflow fields only after complete validation,
preserving Ask, unrelated fields and valid special reasoning levels. A repeated
cleanup changes nothing. Workflow set against the old form requests cleanup
without writing; an Ask-only save preserves the old Workflow form unchanged.
