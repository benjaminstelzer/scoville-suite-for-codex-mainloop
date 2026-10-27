# Mainloop source project

This is the separate `scoville-suite-for-codex-mainloop` development repository.
PLAN-0055 tracks the implemented architecture and remaining native acceptance.

- Author `suite.json`, `members/` and `development/readme/` here.
- The original `../scoville-suite`, `../shared`, existing public distributions
  and installed Skills are read-only for this project. Never push to upstream.
- Reuse the existing builder through `development/build_suite.py` and the sibling
  Shared tools. Do not create another builder. `development/shared/` is a generated
  upstream snapshot, not an authoring source. For variant-specific shared runtime
  changes, use project-owned member files through this manifest. The Workflow
  `native_task_arguments.py` is owned here and adapted to the new roles.
- `codex` is the default profile and its suite identity is this project's name.
  `general` remains for inherited regression coverage, not publication.
- Build staging for this variant is `skills/temp/release/mainloop/` under the
  workspace's single release tree. Never overwrite existing Codex, general,
  standalone, public or global installation targets. A future publication or
  installation must use an explicitly selected separate target.
- Generate README previews from their fragments. Keep required diagrams.
- Choose checks from changed behavior. Require new runtime Actions only when
  packaged Python or its Python CI tests change. Before a canonical source
  commit, run `python development/check_all.py` and require exit 0.
- Public delivery needs Changelogs and artifact checks. Do not create releases
  or tags. Project creation alone authorizes no publication or manager migration.

Build entrypoints and provenance: `development/mainloop.md`.
