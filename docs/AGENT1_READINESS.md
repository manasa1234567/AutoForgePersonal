# Agent 1: Spec Agent readiness

## Available before Azure access

- The intake sends supported uploaded file bytes to the API; the API extracts text from OpenAPI YAML/JSON, selectable-text PDFs, DOCX, TXT, and Markdown.
- Pasted or uploaded OpenAPI contracts are validated locally. The offline analyzer lists operations, documented responses, server dependencies, authentication gaps, and clarification questions.
- Plain-language requirements still run in deterministic demo mode and remain clearly labelled as such.
- With Foundry configured, the Spec Agent turns a free-text use case into atomic functional requirements, acceptance criteria, assumptions, risks, and clarification questions. It does not generate code; the Architecture and Coder agents own those later stages.
- A configured model failure is surfaced to the user rather than silently returning deterministic demo output.
- The cloud path is wired to the Microsoft Agent Framework Foundry provider. It uses `DefaultAzureCredential` for local development and `ManagedIdentityCredential` when `AUTOFORGE_IDENTITY_MODE=managed_identity` is selected.
- Prompt Shields runs before the Spec Agent when configured. Cloud model analysis is stopped if Foundry is configured without the safety endpoint or the safety call fails.

## Required handover to activate the cloud path

1. From D1, set `FOUNDRY_PROJECT_ENDPOINT`, the Spec model deployment in `FOUNDRY_SPEC_MODEL`, and `AZURE_CONTENT_SAFETY_ENDPOINT`.
2. From D2 and D7, confirm the selected model, Agent Framework package, Prompt Shields endpoint, API version, and Python dependencies are enabled and approved.
3. From D4, assign the forge managed identity access to the Foundry project and Content Safety resource. The Day-0 handover must confirm the exact data-plane role for Content Safety.
4. Set `AUTOFORGE_IDENTITY_MODE=managed_identity`; set `AZURE_CLIENT_ID` only for a user-assigned identity.
5. From D5, confirm the worker subnet and proxy can reach the Foundry and Content Safety endpoints.

## Configure the deployed backend through CD

### Portal walkthrough for a first setup

The current Foundry home page already shows an existing project if its name appears in the top-left project selector. On that page:

1. Use the **Project endpoint** field and its copy icon. Do not use the adjacent API key. The expected project endpoint format is `https://<resource>.services.ai.azure.com/api/projects/<project>`.
2. Select **View deployments**. If a suitable text/chat model deployment already has status **Succeeded**, reuse it and record its deployment name. Do not create a second deployment yet.
3. If there is no suitable deployment, select **Discover** or **Explore models**, choose an available text/chat model, review its price and region, and deploy using a Standard/pay-per-token option. Avoid provisioned throughput for this initial trial. After deployment, verify it appears as **Succeeded** in View deployments and test it once in the Foundry playground. Use the exact deployment name in GitHub as `FOUNDRY_SPEC_MODEL`.

For Prompt Shields, create a separate **Azure AI Content Safety** resource in the Azure portal if one does not already exist:

1. In the Azure portal, select **Create a resource**, search for **Content Safety**, and select the Azure AI Content Safety resource. Select the personal subscription, a resource group, a supported region, and a supported pricing tier, then create it. Microsoft documents these resource-creation fields in the [Content Safety quickstart](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/quickstart-text).
2. Open the deployed resource and copy its endpoint from **Resource Management → Subscription Key and Endpoint** (the label may appear as **API Keys and Endpoints**). Copy only the endpoint; do not use or store its key for this app.
3. Assign the backend's user-assigned identity the **Cognitive Services User** role on this Content Safety resource. Prompt Shields uses the endpoint with Entra authentication; the application code sends the `2024-09-01` API version by default.

No extra repository code change is needed to create the Content Safety resource. The integration is already implemented in `backend/app/services/azure_adapters.py`; the endpoint, identity mode, and client ID are injected during CD from the GitHub variables below. Keep the displayed API key private. For an initial trial, use only synthetic requirements because the deployed application does not yet enforce company sign-in/VPN access.

The CD workflow can attach the provisioned user-assigned forge identity and configure the backend when the following GitHub Actions **repository variables** are set:

- `FOUNDRY_PROJECT_ENDPOINT`: the Foundry project endpoint from D1.
- `FOUNDRY_SPEC_MODEL`: the approved Spec model deployment name. For a low-cost first trial, a single deployment can instead be set as `FOUNDRY_MODEL`; the agent-specific value takes precedence.
- `AZURE_CONTENT_SAFETY_ENDPOINT`: the approved Prompt Shields Content Safety endpoint.
- `FOUNDRY_RUNTIME_IDENTITY_RESOURCE_ID`: full Azure resource ID of the user-assigned forge managed identity.
- `FOUNDRY_RUNTIME_CLIENT_ID`: client ID of that same user-assigned identity. This is an identifier, not a secret.
- `AZURE_PROMPT_SHIELDS_API_VERSION`: optional; defaults to `2024-09-01`.

### Where each copied value goes

Do not paste these values into Python source files. Add them in GitHub: repository **Settings → Secrets and variables → Actions → Variables → New repository variable**. For each row, enter the left value as the variable **Name** and paste the copied Azure value as its **Value**.

| Copy this value from Azure | GitHub variable Name | Paste the value as |
|---|---|---|
| Foundry project home → **Project endpoint** (use the copy icon) | `FOUNDRY_PROJECT_ENDPOINT` | Value |
| Foundry Build → Models → Deployments → the deployed model's **Deployment name** | `FOUNDRY_SPEC_MODEL` | Value |
| Content Safety resource → **Subscription Key and Endpoint** → Endpoint | `AZURE_CONTENT_SAFETY_ENDPOINT` | Value |
| User-assigned managed identity → Overview → **Resource ID** | `FOUNDRY_RUNTIME_IDENTITY_RESOURCE_ID` | Value |
| User-assigned managed identity → Overview → **Client ID** | `FOUNDRY_RUNTIME_CLIENT_ID` | Value |

The Foundry project home may also show an **API key** beside the Project endpoint. Do not copy that key: this configuration uses managed identity. Keep `FOUNDRY_MODEL` empty for the Agent 1-only trial.

Once `FOUNDRY_PROJECT_ENDPOINT` is set, CD requires the deployment, Content Safety endpoint, and identity values, attaches the identity to `aegis-backend`, and injects the non-secret settings. It sets `AUTOFORGE_IDENTITY_MODE=managed_identity`. The deployment stops with an actionable message when those required values are missing. It does not store model API keys.

Before running CD, an Azure administrator must grant the **runtime forge identity** the Foundry User role on the Foundry resource and Cognitive Services User on the Content Safety resource. The GitHub Actions OIDC principal separately needs permission to update the backend Container App and attach this user-assigned identity (Managed Identity Operator on the identity). The workflow identity should not be granted permission to create arbitrary role assignments. Foundry role naming may appear as the former Azure AI User during Microsoft's rename rollout; see [Foundry RBAC](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry) and [Content Safety](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview).

After deployment, `GET /api/health` reports `mode`, `spec_agent`, `prompt_shields`, and `agent1_cloud_ready` without returning resource endpoints or identity IDs. A `demo`, `misconfigured`, or `agent1_cloud_ready: false` result means Agent 1 is not ready for cloud analysis. A `foundry` mode and `agent1_cloud_ready: true` confirm configuration only; the first real build is still required to verify endpoint access, role propagation, Prompt Shields, and model inference.

The normal flow remains automated through analysis, but the user must still approve the extracted requirements before the next agent runs. This is the human review gate, not a deployment configuration step.

These settings can be prepared now, but the cloud path cannot be authenticated or verified until the endpoint handover and role assignments arrive. Service Bus scheduling, persistent skill storage/search, the isolated code sandbox, image scanning, private deployment, smoke-test rollback, and Application Insights belong to later workflow agents and are not represented as completed by Agent 1.

## Local demo limit

Before model access is available, the local plain-language path splits submitted prose into source-grounded statements. It is useful for exercising intake and approval flow, but it is not semantic AI analysis and should not be treated as the automated end goal. To exercise the real Agent 1 path locally, configure the Foundry project endpoint and Spec deployment, authenticate with `az login`, and configure the approved Prompt Shields endpoint. In Azure, use the forge managed identity and the role assignments from the handover.

## Jira Cloud intake

The Jira intake accepts an issue key. Before running analysis, the backend resolves the key with the read-only Jira Cloud REST API and gives the issue summary, description, and issue type to Agent 1. Set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` in the backend environment. `JIRA_ACCEPTANCE_CRITERIA_FIELD` is optional because each Jira project may store acceptance criteria in a different custom field. The user represented by the token needs Browse Projects permission for the issue. Never put the API token in frontend configuration; store the production value in Key Vault and inject it into the backend runtime. Without Jira settings, analysis fails clearly rather than interpreting an issue key as the requirement.

For the initial Jira Cloud setup this uses Atlassian's documented email plus API token Basic authentication for REST API clients; Atlassian recommends OAuth 2.0 for a full multi-user app integration. Confirm the organization's approved authentication method and token policy before production rollout.
