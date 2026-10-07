# Shared platform checkout and reviewer failures

Build `e8ce4088` originally failed because the packaging-tools checkout selected
`master`, while the deployed platform and resolver scripts are on `main`.
The workflow log explicitly records `ref: master`; Docker then reports that
`.autoforge-platform/scripts/resolve-generated-npm-locks.cjs` does not exist.
Application code changes cannot repair a missing platform tool.

The generated deployment workflow now selects
`AUTOFORGE_GITHUB_BASE_BRANCH`, falling back to `main`, for platform tools.
It validates the tool files inside the logged packaging step, after callback
configuration is available, so failures are reported to the build record.
The callback recognizes missing platform tooling and does not claim or spend
an application-repair attempt.

Critic output is separately checked against the actual candidate inventory.
File findings must name submitted artifacts. High/Critical findings must quote
matching source evidence. Unsupported output gets one evidence-correction
request. If still unsupported, publication stops as a reviewer failure;
Coder is not asked to rewrite application code to satisfy an ungrounded claim.
Local deterministic findings and grounded Critical findings remain blockers.
Candidate artifact paths are retained in rejected repair reports.

The previous build report named paths absent from published artifacts. Its
rejected candidate was not retained, so that alone cannot establish that the
model invented those paths. New validation uses the candidate itself rather
than inferring its contents from the last published version.

These are shared platform changes. They do not modify any generated use case.
Existing exhausted repair budgets are not reset by updating the platform.
