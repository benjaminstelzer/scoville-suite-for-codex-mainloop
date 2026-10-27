## How it works

1. Resolve this project's settings with consumer defaults.
2. Validate only the requested changed section.
3. Save a valid change atomically; preserve unrelated settings.

Cleanup is the sole old-Workflow migration operation. It resolves effective
legacy pairs, asks for ambiguous choices and validates the whole candidate
before one save. It creates no agents or Plan changes.
