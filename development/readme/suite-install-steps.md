Ask your agent host:

```text
Install and enable the complete suite for all my projects from the packages/ directory of {{ include: suite.repository }}.
Preserve personal settings and unrelated Skills. Ask before overwriting conflicting customizations.
Report the installed location and whether the host discovers every member.
```

If your host can't install from GitHub, download the repository and copy each
`packages/<name>/<name>/` directory into the host's Skills location. Don't mix
standalone and suite copies of the same Skill. Longer runs can hit Codex's
agent limit - see [Workflow](members/scoville-workflow-for-codex/README.md#limitations).

### Upgrading

Replace the installed copies with the complete packages of the suite you
chose. Your project settings and unrelated Skills stay.

Coming from an earlier Codex suite: finish and commit the current Work Item
first. Then install Mainloop, reload and ask Setup to show the project's
settings. If it reports old Workflow settings, ask it for a cleanup and name
the main model and reasoning level. Commit the changed settings file if it is
tracked.
