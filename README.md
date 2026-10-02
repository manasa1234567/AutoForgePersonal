# AegisAI AutoForge — Buildathon Reference Implementation

A clean Angular 19 + FastAPI reference implementation for the **AutoForge on Azure** buildathon use case.

> **Important:** this repository starts in **Mock Mode**. It demonstrates the complete user journey and agent orchestration without requiring Azure credentials. Azure integration points are isolated behind adapters so the team can replace them incrementally with Microsoft Foundry, Azure OpenAI, AI Search, Content Safety, Dynamic Sessions, Cosmos DB, Service Bus, ACR and the governed deployment pipeline.

## 1. What the user does

The user clicks **Start Forge** and can provide engineering intent through:

- Jira / work item
- OpenAPI or other specification
- Architecture document
- Uploaded engineering documents
- Use case
- Plain-language requirement

The flow is:

```text
START FORGE
    ↓
UNDERSTAND — Spec Agent
    ↓ human approval
DESIGN — Architecture Agent
    ↓ human approval
FORGE — Coder Agent
    ↓
PROVE — Critic Agent + Self-Healing
    ↓ human approval for evolved skill
RELEASE — Security Reviewer + Deployer Agent
    ↓ human approval
DEPLOY + VERIFY
    ↓
RUN REPLAY / AUDIT / AGENTOPS
```

## 2. Prerequisites

- Node.js 20+ (Node 22 recommended)
- npm 10+
- Python 3.12+
- Git

## 3. Run locally

### Terminal 1 — backend

From the **repository root**:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn app.main:app --reload --app-dir backend
```

Backend: `http://127.0.0.1:8000`

Health check: `http://127.0.0.1:8000/api/health`

### Terminal 2 — frontend

From the **repository root**:

```powershell
npm install
npm start
```

Frontend: `http://localhost:4200`

You can also run:

```powershell
npm run build
```

The root `package.json` is intentional: **you can run `npm install` from the repository root**. The earlier version did not have this and caused the `ENOENT package.json` error when npm was executed in the wrong directory.

## 4. Angular coding standards used

The frontend is intentionally structured as production-style Angular rather than putting a large HTML template inside `.ts` files.

- Standalone components
- External `.html` templates
- External `.scss` styles
- `ChangeDetectionStrategy.OnPush`
- `strict: true` TypeScript
- Strict Angular template checking
- Lazy-loaded route components
- Typed API/domain models
- Reactive Forms
- `inject()` instead of constructor injection where appropriate
- `takeUntilDestroyed()` for polling lifecycle management
- No `any` in application domain/API models
- Feature-based folder structure
- API access isolated in `core/api.service.ts`
- Domain interfaces isolated in `shared/models`

## 5. Backend standards used

- FastAPI routers separated from orchestration
- Pydantic domain/request models
- Type hints throughout
- Central orchestrator service
- Azure integration boundary in `azure_adapters.py`
- Explicit error handling in API routes
- Mock safety gate demonstrating prompt-injection handling
- Audit events for critical operations

## 6. Where to understand the code

Start here:

1. `frontend/src/app/features/home/home.component.ts` — Start Forge input
2. `frontend/src/app/features/home/home.component.html` — intake UX
3. `frontend/src/app/core/api.service.ts` — frontend/backend boundary
4. `backend/app/routers/builds.py` — REST API
5. `backend/app/services/orchestrator.py` — agent workflow
6. `backend/app/services/azure_adapters.py` — future Azure integration boundary
7. `frontend/src/app/features/build/build.component.ts` — build journey state
8. `frontend/src/app/features/build/build.component.html` — Understand → Design → Forge → Prove → Release UX

## 7. Azure mapping

| Demo component | Azure target |
|---|---|
| Forge worker + agents | Azure Container Apps worker using Microsoft Agent Framework; Foundry Hosted Agent is an optional hosting mode |
| Model calls | Microsoft Foundry model deployments |
| Skill/knowledge retrieval | Azure AI Search + Cosmos DB |
| Prompt safety | Azure AI Content Safety / Prompt Shields |
| Generated-code sandbox | Container Apps Dynamic Sessions, egress disabled |
| Forge API/UI | Azure Container Apps internal environment |
| Files/artifacts | Azure Blob Storage |
| Async job queue | Azure Service Bus |
| Skill/job metadata | Cosmos DB for NoSQL |
| Secrets | Key Vault |
| Identity | Microsoft Entra ID + managed identities |
| Container image | Azure Container Registry |
| Vulnerability gate | Microsoft Defender for Containers |
| Private network | VNet + Private Endpoints + Private DNS |
| Observability | Application Insights + Log Analytics + Workbooks |
| Worker build/deploy | Managed identity builds in ACR, requests Defender scanning, and deploys the approved private Container App; no GitHub token is required |

## 8. What is deliberately simulated

The current version does **not** claim to deploy code to Azure. The following are simulated so the team can understand and demo the orchestration first:

- Requirement extraction
- Architecture generation
- Code generation result
- Critic failure
- Self-healing iteration
- Skill promotion
- Dependency/image security scans and Azure release gate (local source review is implemented; see `docs/AGENT5_READINESS.md`)
- Container deployment
- Smoke-test verification
- AgentOps metrics

Replace these one at a time with real Azure calls after the Azure environment is approved.

## 9. Buildathon demo story

Use a requirement such as:

> Build a secure customer onboarding service with KYC verification, document upload, validation and notifications.

Then demonstrate:

1. Choose **Use Case** and click **Start Forge**.
2. Spec Agent extracts six requirements.
3. Human approves the requirements.
4. Architecture Agent creates the blueprint.
5. Human approves the blueprint.
6. Coder Agent generates the application and proposes a reusable skill.
7. Critic Agent deliberately discovers a contract failure.
8. Self-healing patches the failure and reruns tests.
9. Human approves promotion of the proven skill.
10. Security Reviewer runs the release gates.
11. Human approves deployment.
12. Deployer verifies the internal deployment.
13. Run Replay shows audit events, tokens, tool calls and self-healing iterations.

This makes the differentiator visible: **the system does not only generate code; it understands, proves, recovers, learns a reusable skill, and requires governed human approval before release.**

## UX baseline (v5)
The frontend is organized around an AI Engineering Workspace rather than a dashboard. Home is an entry point only. Start Forge opens a multi-source intake (Jira, OpenAPI/specification, architecture document, engineering documents, use case, or plain requirement). A Build then follows UNDERSTAND → DESIGN → FORGE → PROVE → RELEASE, with Agent Constellation and an auditable Build Timeline visible throughout the workspace.

## First executable agent: Spec Agent

The first end-to-end automation agent is now implemented as the **Spec Agent**.

Flow:

1. User selects Jira, OpenAPI, Architecture, Documents, Use Case or Requirement.
2. Angular calls `POST /api/builds`.
3. Angular starts the build with `POST /api/builds/{id}/start`.
4. The FastAPI orchestrator invokes `SpecAgent`.
5. The Spec Agent checks the input through the safety adapter, extracts structured requirements, acceptance criteria, dependencies and risks, and records confidence/token metrics.
6. The Build Workspace polls the build and shows the real agent result.
7. A human approves the requirements before the workflow continues to the Architecture Agent.

### Microsoft Foundry mode (Agent Framework)

The Spec Agent uses the Microsoft Agent Framework Foundry provider when these settings are present:

- `FOUNDRY_PROJECT_ENDPOINT` — project endpoint from the Azure handover table
- `FOUNDRY_SPEC_MODEL` — Spec Agent deployment name (or shared `FOUNDRY_MODEL`)
- `AZURE_CONTENT_SAFETY_ENDPOINT` — Content Safety resource endpoint for Prompt Shields
- `AUTOFORGE_IDENTITY_MODE=managed_identity` in Azure Container Apps
- `AZURE_CLIENT_ID` only when the forge uses a user-assigned managed identity

Local development uses `DefaultAzureCredential` (for example, `az login`). Azure should explicitly select managed identity. If Foundry is configured but the model call or authentication fails, the build fails visibly instead of claiming a deterministic result is real model analysis.

When `AZURE_CONTENT_SAFETY_ENDPOINT` is configured, Prompt Shields runs before the Spec Agent and blocks detected prompt injection. It also fails closed if the configured service is unavailable. The marker-based check is available only in local demo mode; configuring Foundry without the safety endpoint stops analysis.

Without Azure settings, the Spec Agent remains runnable locally. OpenAPI JSON and YAML are parsed into explicit operation requirements, documented response criteria, security questions, and contract constraints. Plain-language input uses the deterministic fallback, which is clearly labeled `deterministic-demo` and asks for unresolved information. Invalid OpenAPI input is returned as `NEEDS_CLARIFICATION` with a validation question.

The earlier `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` path remains available for local compatibility; use Foundry project settings for the target architecture and managed-identity deployment.

## Second executable agent: Architecture Agent

After the user approves Agent 1's requirements, Agent 2 proposes a requirement-grounded blueprint and surfaces assumptions and open architecture decisions. With Azure configured, it calls the Microsoft Agent Framework Foundry deployment selected by `FOUNDRY_ARCHITECTURE_MODEL` (or shared `FOUNDRY_MODEL`). Before Azure access, a clearly labeled `local-rules` path creates a provisional outline; it does not claim model-level reasoning. See [Agent 2 readiness](docs/AGENT2_READINESS.md).

The blueprint fields are editable before approval. The saved choices, including a framework change such as Angular to React, are passed into Agent 3. With Azure configured, the Coder Agent uses `FOUNDRY_CODER_MODEL` (or shared `FOUNDRY_MODEL`) to produce source artifacts. Before Azure access it only provides a clearly labeled local scaffold preview. See [Agent 3 readiness](docs/AGENT3_READINESS.md).

### Run on Windows

Install Python dependencies once:

```powershell
python -m pip install -r backend/requirements.txt
```

Then use the PowerShell launcher:

```powershell
.\scripts\start-demo.ps1
```

Or run the two processes separately:

```powershell
npm run start:backend
npm start
```

The Angular proxy sends `/api` calls to `http://127.0.0.1:8000`.

## Agent readiness

- Agent 4 readiness: `docs/AGENT4_READINESS.md` (static review, disabled ACA session adapter, and bounded repair loop implemented; live runner validation pending)

## Workspace navigation

- `Home` shows recent builds from the API; `New Build` opens the intake form; `Builds` lists and reopens builds.
- `Agents` shows workflow roles and their latest recorded build state; `Skills` imports the 16 seed recipes and supports submission, approval, rejection, deprecation, and approved-only retrieval; `Knowledge` indexes source documents and text submitted with current-session builds; `Run History` shows their audit events.
- `Settings` saves a workspace label in the current browser and documents server-side integration configuration. It does not store credentials or report connection health.
- The recipe catalog is served from `/api/skills`, with state held by a local in-memory repository. Approved recipes are supplied as advisory context to model-backed Spec, Architecture, Coder, and Critic agents; Coder skill application is included in build records and audit events. Recipe decisions and builds clear when the backend restarts. Durable Azure persistence, Service Bus, Cosmos DB, Blob Storage, AI Search, Entra reviewer identity, and live integration status still require their Azure adapters and APIs.
