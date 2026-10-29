## How to use

Ask Setup to show or save this project's settings. For an old Workflow
configuration, explicitly request cleanup and supply the required main pair and
any ambiguous review/explore choices. All three valid pairs are saved together;
errors leave the file unchanged. Show never migrates.

For an explicitly authorized upgrade of a running project, let the old version
reach a reviewed, quiescent commit boundary, preferably Work Item closure.
Preserve needed closure evidence and commit a changed tracked Plan before
reload. If essential proof cannot be preserved, stay with the old version
within that Work Item. After reload, run explicitly authorized cleanup with
the chosen pairs. A tracked configuration change needs its own commit under
project checks before authorized continuation. The Skill's
migration instructions grant no upgrade, cleanup, commit or continuation
permission. Installation alone proves neither cleanup nor reload.
