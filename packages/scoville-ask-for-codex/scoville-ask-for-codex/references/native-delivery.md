# Native agent delivery

Finish the complete answer, then choose its permitted delivery route before
you send anything:

1. Besides the answer, include only consultation_reference and material
   evidence limits; the caller already holds your scope, adviser ID and
   settings.
2. Deliver through the native final. If a known size limit applies, use the
   in-memory check under [Output delivery](output-delivery.md#the-three-calls)
   before writing any file.
3. If required content still exceeds the declared or explicitly selected
   limit, or an applicable outer tool-output limit, use the shared
   complete-file route. Return the same fields with the path in place of the
   answer. The caller has a standing instruction to read the whole file, so
   this delivery needs no additional reading instruction.
4. If permissions or host tools prevent that route, follow the shared writing
   rules' delivery limit and also name the content left undelivered; do not
   claim completeness.
5. Stop after the native final; do not wait for an acknowledgement. The caller
   may resume you for a necessary follow-up.

As a native Codex Ask adviser you may locate Python and run the named checker
for capture and size checks, also outside the workspace. Create temporary
files under the project's `.scoville/temp` only to deliver an oversized
answer. Your read-only role and the host's tool restrictions still apply.
Ask Claude has neither permission.

If a material fact is missing, return the concrete question; do not guess. The
caller resumes you with the answer. In a follow-up, answer under the same
reference and within the same scope unless the caller supplies a new
reference or changed scope.
