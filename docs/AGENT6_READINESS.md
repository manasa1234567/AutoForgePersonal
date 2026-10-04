# Agent 6: generated application deployment

## Release flow

After the human approves release, AutoForge publishes reviewed files to a new `feature/<use-case-slug>-<8-character-build-id>` branch under `generated/<use-case-slug>-<build-id>/`. The resulting feature-branch push starts `.github/workflows/deploy-generated-app.yml`.

The workflow builds and pushes an image to ACR, creates or updates a per-build Azure Container App in `aegis-env` / `aegis-rg`, enables external HTTPS ingress, smoke-checks the app, and sends an authenticated callback to the backend. The callback updates the build to `Deployed`, stores the live URL, and adds an audit event. A deployment error marks the build `Failed` and is recorded in the timeline. The build page polls while deployment is running and displays **Open deployed application** after success.

Supported project layouts are a root `Dockerfile`, a Node package with a build or start script, or a static project containing `index.html`. A project containing common backend manifests must provide a root `Dockerfile`; the workflow fails rather than silently deploying only its frontend. This workflow does not run dependency vulnerability scans or Azure Policy checks, and it does not implement automatic cleanup of per-build apps.

## GitHub Actions setup

The `production` GitHub Environment must contain these secrets and allow deployment from feature branches:

- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` for the existing OIDC federated credential.
- `AUTOFORGE_DEPLOYMENT_CALLBACK_TOKEN`, a long random value shared with the backend through the Container App secret reference.

The existing environment/repository Actions variables must include `ACA_ENVIRONMENT_NAME=aegis-env`, `ACA_RESOURCE_GROUP=aegis-rg`, `ACR_NAME=aegisacr20500`, and `FOUNDRY_RUNTIME_IDENTITY_RESOURCE_ID` set to the full resource ID of `aegis-forge-mi`.

The OIDC principal used by Actions needs permission to push images to ACR and create/update Container Apps in `aegis-rg`. The user-assigned identity used by the generated Container Apps needs the **AcrPull** role on the registry. The existing backend identity also needs permission to access the callback route; the callback token is passed as a Container App secret by `CD - Azure`.

After this workflow is merged to the repository's default branch and `CD - Azure` succeeds, newly published feature branches deploy automatically. To deploy an existing feature branch, run **Deploy generated app to Azure Container Apps** manually and enter its branch name.

## Operational and security limits

Generated apps use public HTTPS ingress so the returned URL can be opened directly. They scale to zero and are limited to one replica, but each build creates a separate Container App and image; remove apps/images that are no longer needed to control resource use. Treat generated applications as publicly accessible unless authentication is part of the generated app itself.

The deployment callback requires `Authorization: Bearer <AUTOFORGE_DEPLOYMENT_CALLBACK_TOKEN>`, verifies successful URLs use HTTPS, and rejects callbacks whose feature branch does not match the build. Do not log or commit the callback token.

The workflow implementation has been added to the repository. Actual Azure deployment still depends on the GitHub Environment, OIDC, ACR, managed identity role assignments, and a successful `CD - Azure` run. The first end-to-end success is confirmed only when the workflow completes and the build page shows the deployed URL.
