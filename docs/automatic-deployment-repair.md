# Automatic deployment repair

This change repairs generated projects using real Docker build/startup diagnostics.
It is independent of the prompt and framework. It does not patch a particular form,
force npm installation, or bypass security review.

## Enable it

1. Commit and push these backend and workflow changes together to `main` (or your
   repository's configured default branch).
2. Wait for **CD - Azure** to deploy the updated AutoForge backend successfully.
3. Keep the existing production callback secret and GitHub App configuration.
  The GitHub App needs its existing Contents write permission so a repair commit
  can advance the feature branch. No Actions write permission or new Azure
  resource is required.
4. New generated builds use the loop automatically after release approval.
5. To retry an existing failed build without generating again: open GitHub
   **Actions → Deploy generated app to Azure Container Apps → Run workflow**.
   Select `main` for **Use workflow from** and enter the existing feature branch
   in the **branch** input. This uses the current workflow with that branch's code.
   Do not use **Re-run jobs** on an old run: it retains the old workflow revision.

## Flow

The workflow builds the generated root Dockerfile, starts that image locally,
and checks its HTTP root. If packaging, compilation, dependency installation,
or startup fails, it sends bounded, redacted diagnostics and the exact commit
to the authenticated backend callback.

The backend records a durable claim per failed commit, then runs Coder with the
existing files, approved blueprint and error report. Changed files must pass
Critic and Security review. The publisher advances the same feature branch
without force-pushing or overwriting a newer commit. Its push triggers the next
deployment workflow run through the normal feature-branch path. Repair commits
do not use `[skip ci]`, so no separate Actions dispatch is required.

Each build permits at most three repair commits. An unchanged response, failed
review, model failure, permission failure, or timeout stops with an explicit
error. Failed worker tasks are not blindly repeated. GitHub polls the backend;
if a worker restarts, the polling timeout reports failure rather than leaving
the build running forever. Azure mode stores repair claims in the existing
workspace Blob container; local mode remains process-local.

Only an image that passed the actual build and local startup check is pushed
and deployed. Its tag includes the source commit so a repair cannot accidentally
reuse an older image. Azure smoke-test success is still required before recording
the live URL. The failed attempt stays red in Actions; the dispatched retry is
a separate run.

## Limits

- Azure authentication, registry push permissions, Azure provisioning and cloud
  smoke-test failures are reported rather than sent to Coder as source repairs.
- A successful HTTP root check does not prove every feature or database operation
  works. Required external services must still be configured for the application.
- Legacy builds need a published commit in their audit trail to correlate repair.
  A manually advanced branch is never silently overwritten.
- Automatic repair preserves the approved stack/scope and re-runs reviewers;
  it cannot guarantee that arbitrary generated code will succeed within three tries.
- This local change has not been deployed. End-to-end GitHub/Azure validation
  requires the updated backend and workflow to be live together.
