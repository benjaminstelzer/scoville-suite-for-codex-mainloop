## How it was developed

Early consultations made collecting answers and asking follow-up questions
more complicated than the question warranted. Native adviser handles and
saved Claude sessions gave each conversation a clear continuation path.
Missing answers still have to remain visible: a partial panel is not a consensus.

### Current validation

Current native review and consultation cases used `gpt-6.1-sol / low`. Advisers
returned independent findings and respected the read-only scope. Local helper
tests also checked prompt delivery and Claude request/resume handling with a
CLI double. No current Claude provider behavior test was run.

These are targeted cases, not a general success rate or proof of faster model
execution. Encrypted native message records prevented an independent
byte-for-byte comparison of transmitted assignments.
