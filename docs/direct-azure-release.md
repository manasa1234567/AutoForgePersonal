# Direct Azure release

The Release gate has two explicit paths:

- **Approve and deploy via GitHub** keeps the existing process: publish the
  reviewed project under `generated/` on its feature branch, then let the
  GitHub Actions workflow build and deploy it.
- **Approve and deploy to Azure** sends the reviewed project directly from the
  backend to Azure Container Registry Tasks. ACR resolves generated npm locks
  with lifecycle scripts disabled, builds the staged Dockerfile, pushes the
  image, and the backend creates an isolated `af-<build-id>` Azure Container
  App. The backend returns the app URL only after the URL passes its HTTP
  smoke check. This path does not publish a GitHub feature branch.

Both paths require human approval at Release and use the same approved source,
security review, and runtime validation. The offline `preview.html` remains in
the downloaded ZIP; the on-page Preview UI and its API viewer endpoints are
removed.

## Backend settings

Set these values on the AegisAI backend Container App:

```text
AUTOFORGE_DEPLOYMENT_ENABLED=true
AUTOFORGE_AZURE_DIRECT_DEPLOYMENT_ENABLED=true
AUTOFORGE_IDENTITY_MODE=managed_identity
AZURE_SUBSCRIPTION_ID=<subscription GUID>
AZURE_CLIENT_ID=<backend managed identity client ID>
ACA_RESOURCE_GROUP=<generated apps resource group>
ACA_ENVIRONMENT_NAME=<Container Apps environment name>
ACR_LOGIN_SERVER=<registry>.azurecr.io
ACR_NAME=<registry name>
ACR_RESOURCE_GROUP=<resource group containing the registry>
ACA_REGISTRY_IDENTITY=<user-assigned identity resource ID used to pull images>
```

`ACR_RESOURCE_GROUP` defaults to the `AZURE_RG` GitHub Actions variable; set it
explicitly when the registry is in another resource group. The Aegis deployment workflow copies the registry name,
registry identity, and direct deployment feature flag from repository Actions
variables into the backend app. Enable the feature flag as a repository Actions
variable named `AUTOFORGE_AZURE_DIRECT_DEPLOYMENT_ENABLED` only after granting
the permissions below.

## Managed identity permissions

The backend managed identity needs:

- **Container Registry Tasks Contributor** on the ACR resource, to upload a
  build context and run the remote image build.
- **Container Apps Contributor** on the target resource group, to create and
  update the per-build app and join the configured environment.
- **Managed Identity Operator** on the user-assigned identity named by
  `ACA_REGISTRY_IDENTITY`, so the backend can attach it to generated apps.

That image-pull identity also needs **AcrPull** on the registry. The backend
identity must be the identity selected by `AZURE_CLIENT_ID` in managed-identity
mode. These assignments are not verified by a configuration-only readiness
check; Azure will report an authorization error if a role is missing.

Each direct deployment creates or updates the app named `af-<8-character
build-id>` in the configured Container Apps environment. Check its app logs if
the ACR build or post-deployment smoke check fails. No successful deployment
URL is recorded until the smoke check passes.
