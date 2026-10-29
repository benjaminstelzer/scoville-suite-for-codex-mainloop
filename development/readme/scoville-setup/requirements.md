## What it enforces

- Saves settings only when you ask and leaves unrelated values alone.
- Rejects invalid values before writing.
- Changes configuration between runs, or at an explicitly authorized safe
  migration boundary. It doesn't start or supervise a workflow.
