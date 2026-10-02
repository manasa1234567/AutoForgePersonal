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

These settings can be prepared now, but the cloud path cannot be authenticated or verified until the endpoint handover and role assignments arrive. Service Bus scheduling, persistent skill storage/search, the isolated code sandbox, image scanning, private deployment, smoke-test rollback, and Application Insights belong to later workflow agents and are not represented as completed by Agent 1.

## Local demo limit

Before model access is available, the local plain-language path splits submitted prose into source-grounded statements. It is useful for exercising intake and approval flow, but it is not semantic AI analysis and should not be treated as the automated end goal. To exercise the real Agent 1 path locally, configure the Foundry project endpoint and Spec deployment, authenticate with `az login`, and configure the approved Prompt Shields endpoint. In Azure, use the forge managed identity and the role assignments from the handover.

## Jira Cloud intake

The Jira intake accepts an issue key. Before running analysis, the backend resolves the key with the read-only Jira Cloud REST API and gives the issue summary, description, and issue type to Agent 1. Set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` in the backend environment. `JIRA_ACCEPTANCE_CRITERIA_FIELD` is optional because each Jira project may store acceptance criteria in a different custom field. The user represented by the token needs Browse Projects permission for the issue. Never put the API token in frontend configuration; store the production value in Key Vault and inject it into the backend runtime. Without Jira settings, analysis fails clearly rather than interpreting an issue key as the requirement.

For the initial Jira Cloud setup this uses Atlassian's documented email plus API token Basic authentication for REST API clients; Atlassian recommends OAuth 2.0 for a full multi-user app integration. Confirm the organization's approved authentication method and token policy before production rollout.
