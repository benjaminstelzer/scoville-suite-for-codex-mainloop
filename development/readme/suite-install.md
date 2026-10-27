## Install the suite

Install the suite once in your agent host and it's available in all your
projects. Workflow starts directly in a saved Codex project.

### New installation

Use this request in your agent host:

```text
Install and enable the complete suite for all my projects directly from {{ include: suite.repository }}.
```

Don't mix standalone and suite copies of the same Skill.

If your host can't install directly from GitHub, download this repository and
copy all the package directories inside it to the host's Skills folder. You
end up with the same complete suite and the same requirements.

### Opt-in migration from the original Codex suite

This is a separate variant, not an in-place upgrade. Do not mix their packages
or switch an active old implementation. First reach a reviewed, quiet commit
boundary, preferably Work Item closure, and preserve required old closure proof
in existing artifacts. If essential evidence cannot be retained, finish the Work
Item before switching. Commit a changed tracked Plan before reload.

Only after explicitly selecting this variant's separate installation target:
reload it, request Setup cleanup with complete chosen pairs, and commit a tracked
configuration change under project checks before authorized continuation. An
ignored configuration needs no commit. Installation proves neither migration,
host-model selection nor reload. Keep the original suite available separately.
