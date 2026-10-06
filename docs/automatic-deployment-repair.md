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
   If automatic repair previously stopped on that commit, tick **retry_repair**.
   This allows a new, deduplicated request but does not reset the three-attempt budget.
   Do not use **Re-run jobs** on an old run: it retains the old workflow revision.

## Flow

Before deployment, initial Forge generation validates the generated Dockerfile.
Invalid packaging gets up to two Coder repair calls with the latest candidate
files and validation diagnostics. Malformed JSON gets one regeneration. These
calls are separate from the deployment repair budget described below. Missing
frontend `build` or `dist` output must be built inside a named Docker stage and
copied from that stage, rather than copied from nonexistent project files.
Validation still blocks invalid candidates after the retry limit. Existing
builds stopped at this stage must restart Forge after the updated backend is
deployed; rerunning a deployment workflow cannot fix a build with no published
artifacts.

Packaging repair requests include the exact available artifact paths and the
accumulated validation history. A fix must resolve earlier defects as well as
the latest one. Exhausted generation failures retain their path-validated
candidate files and validation history in `generationFailure`, separately from
approved proof artifacts. The error audit event records the failed stage and
attempt count; the UI keeps that stage selected instead of resetting to
Understand and displays the persisted failure once.

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

Each build permits at most three Coder repair attempts, including candidates
rejected before publication. Critic or Security blockers are returned to Coder
with the latest candidate files, until those reviews pass or the budget is used.
The original installation/build log is saved in `deploymentFailureDiagnostics`;
the latest candidate's checks/findings/blockers are in `deploymentRepairReview`.
Rejected candidates do not replace the approved/published artifacts.
An unchanged response, exhausted budget, model failure, permission failure, or
timeout stops with concrete blockers rather than a truncated general review summary.
The overall worker deadline is 30 minutes; the workflow polling window includes
time for those bounded reviews. Successful repairs finish polling immediately.
Failed worker tasks are not blindly repeated. GitHub polls the backend;
if a worker restarts, the polling timeout reports failure rather than leaving
the build running forever. Azure mode stores repair claims in the existing
workspace Blob container; local mode remains process-local.

Only an image that passed the actual build and local startup check is pushed
and deployed. Its tag includes the source commit so a repair cannot accidentally
reuse an older image. Azure smoke-test success is still required before recording
the live URL. The failed attempt stays red in Actions; the dispatched retry is
a separate run.

## Limits

Generated npm projects resolve their lockfiles from the approved package.json
using npm in an isolated Node 22 packaging container. Model-authored checksums
and incomplete dependency trees are replaced with package-manager output;
lifecycle scripts are disabled during resolution. Peer dependency errors still
fail, and package download integrity checks remain enabled. Declared dependency
ranges may select newer versions when a build is repeated. The resolved locks
are saved as GitHub Actions artifacts for 14 days; they are build-context files,
not an automatic commit to the reviewed feature branch. Other package managers
retain their own lockfiles. The generated Dockerfile must use a compatible Node
runtime and still passes the normal image build and startup checks.

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
