# Agent 6: Deployer Agent readiness

## Implemented locally

The Deployer Agent now has a local preflight exposed from the Prove workspace as **Prepare Deployment Plan** and through `POST /api/builds/{buildId}/deployment-preflight`. It creates a source manifest with relative paths, UTF-8 byte sizes, and SHA-256 hashes; checks artifact bounds; records Critic runtime validation and Security Reviewer results; reports missing external scans; and verifies the Azure target configuration and managed-identity mode. The plan requires a separate human approval before deployment.

The Settings page now shows a deployment setup checklist for the agreed GitHub repository (`manasa1234567/AutoForgePersonal`) and Azure Container Apps target. `GET /api/integrations/deployment-status` reports whether server-side settings exist without returning their values. The UI includes steps to find an ACA environment and create a least-privilege GitHub App. This is diagnostic/setup guidance only; it does not create cloud resources or publish code.

The user confirmed the existing preview environment is `aegis-env` in resource group `aegis-rg` (Central India), under subscription `38dff143-17bc-4230-b3a9-133d5af58186`. The backend example now records the confirmed environment and resource-group names; keep subscription and credentials in deployment configuration rather than committing them as application defaults.

The Azure CD workflow now passes the confirmed ACA environment/resource group, subscription ID, ACR login server, and repository owner/name to the backend as runtime configuration. `AUTOFORGE_DEPLOYMENT_ENABLED` is deliberately kept `false`.

On release approval, the backend can use a GitHub App installation token to create a commit and a new `feature/<use-case-slug>-<build-id>` branch without writing to the base branch. Generated files are placed under `generated/<use-case-slug>-<build-id>/` to avoid overwriting the AutoForge platform source. The UI shows the branch link. Publishing is opt-in with `AUTOFORGE_GITHUB_PUBLISH_ENABLED=true`; the private key is stored as a Container App secret by CD. The GitHub App needs Contents read/write on the target repository. Pull request permission is not used.

The public workspace currently has no user authentication. Do not enable GitHub publishing on an internet-accessible deployment until release approvals are authenticated; otherwise an unauthenticated caller could ask the backend to create branches in the configured repository.

Preflight never builds or runs generated code and never contacts Azure. It saves a structured report and an audit event. Missing prerequisites are listed as blockers. `AzureAdapters.deploy()` now fails closed instead of returning a made-up Container App URL, and the orchestrator does not mark a build deployed or smoke-tested without a real adapter result.

## Local configuration

The backend `.env.example` lists the infrastructure values used by preflight:

- `AUTOFORGE_DEPLOYMENT_ENABLED` defaults to `false` and remains only a safety gate.
- `AUTOFORGE_GITHUB_PUBLISH_ENABLED` defaults to `false`; enable only after release approval is protected by application authentication.
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `ACR_LOGIN_SERVER`
- `ACA_ENVIRONMENT_NAME`
- `ACA_RESOURCE_GROUP`
- `AUTOFORGE_IDENTITY_MODE=managed_identity` for the Azure worker.
- `AUTOFORGE_GITHUB_OWNER`
- `AUTOFORGE_GITHUB_REPOSITORY`
- `AUTOFORGE_GITHUB_BASE_BRANCH` (optional; otherwise the repository default branch is read, never written)
- `AUTOFORGE_GITHUB_APP_ID`
- `AUTOFORGE_GITHUB_INSTALLATION_ID`
- `AUTOFORGE_GITHUB_APP_PRIVATE_KEY_BASE64` (secret; preferably supplied from Key Vault)

Filling these values does not enable deployment. The Azure deployment adapter is intentionally not implemented until the provisioned subscription, identities, security scanners, and target environment can be integrated and reviewed.

To try the local Deployer Agent, start the app, create a build, and proceed until generated artifacts appear in Prove. Run the Security Reviewer, then click **Prepare Deployment Plan**. The UI shows gate statuses, blockers, target, candidate image tag, and artifact hashes. Local preflight is expected to be blocked before Azure setup.

## Azure work remaining

The generated application pipeline still needs a build strategy for supported project types, an idempotent image build in ACR, vulnerability scanning and policy enforcement, isolated per-build Container Apps deployment, a deployment callback/status poll, smoke tests, and rollback on failed verification. Persist operation IDs and outputs for retries, handle timeouts without claiming success, and audit every state change. Do not run shell commands derived from generated artifacts inside the backend. No generated app deployment, URL, image scan, smoke test, or rollback has been verified in Azure.

**Readiness:** GitHub feature-branch publishing is implemented but opt-in and requires GitHub App credentials. It has not been exercised against GitHub. Azure generated-app image build, deploy, smoke test, and rollback remain pending; the UI must not show a live URL until these steps return verified evidence. Agent 6 is not production deployment-ready.
