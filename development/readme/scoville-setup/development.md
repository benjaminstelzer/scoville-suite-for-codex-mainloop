## How it was developed

Setup reuses Ask and Workflow validation. Tests follow saved settings into
those consumers, because a successful save alone says little about the next run.

On 2026-10-29, actual gpt-6.1-sol / low recipients ran show, a requested
partial save and explicit schema-2 cleanup in isolated projects. The requested
pairs were saved, Ask and unrelated values were preserved, and Setup's effective
pairs matched the Workflow resolver. A read-only PowerShell check needed a
syntax correction. The save and cleanup were not repeated.

There was no separate byte checkpoint around the initial show. The absence of
writes during that call was therefore not independently verified. These cases
did not test migration during a running Workflow, installation, actual host-model
binding or adviser execution. No current Claude behavior test was run.
