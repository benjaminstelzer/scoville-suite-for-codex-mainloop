## Configuration

The defaults are in `config.default.json` next to the installed `SKILL.md`.
Project choices go under `ask` in `.scoville/config.json` at the project root,
and anything missing falls back to the defaults. Scoville Setup shows and saves
them. What you name in a request applies to that call only.

This example selects SOL and Fable by default and changes only SOL's effort:

```json
{
  "ask": {
    "advisers": ["sol", "fable"],
    "presets": {"sol": {"effort": "medium"}}
  }
}
```

Project settings override the defaults one field at a time. The adviser list
is the exception: it replaces the default list completely. The `sol` preset
uses `gpt-6.2-sol` at `high`. For an adviser of your own, add an ID, route,
exact model and effort under `advisers`. The `claude` block caps each Claude
call: 10 USD, one hour, no web tools.
