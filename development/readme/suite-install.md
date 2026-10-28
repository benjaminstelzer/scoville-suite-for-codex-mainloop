## Install the suite

Install the complete suite in your agent host to use it across projects.
Workflow starts in a saved Codex project.

### New installation

Use this request in your agent host:

```text
Install and enable the complete suite for all my projects from the packages/ directory of {{ include: suite.repository }}.
Preserve personal settings and unrelated Skills. Ask before overwriting conflicting customizations.
Report the installed location and whether the host discovers every member.
```

Do not mix standalone and suite copies of the same Skill. If your host cannot
install from GitHub, download the repository and copy each
`packages/<name>/<name>/` Skill directory into the host's Skills location.
The repository root and development sources are not installable Skills.

### Upgrade or migrate an existing installation

Choose the target suite explicitly. Preserve project settings and personal
customizations, then replace duplicate installed copies with the target suite's
complete packages. Remove only superseded Skills you have selected for removal.
An upgrade is not permission to erase settings or unrelated Skills.

When moving from an earlier Codex suite, first reach a reviewed,
quiet commit boundary, preferably Work Item closure. Retain required acceptance
evidence and commit a changed tracked Plan before reloading. If essential proof
cannot be retained, finish that Work Item before switching.

Install the complete Mainloop suite from this repository, reload it, then ask
Setup to show the existing project settings. If cleanup is required, explicitly
request migration and choose the complete main pair and any ambiguous role
pairs. Cleanup preserves Ask and unrelated settings. Commit a tracked settings
change under the project's checks before authorized continuation. An ignored
configuration needs no commit. Installation alone proves neither configuration
migration, reload nor the active host model.
