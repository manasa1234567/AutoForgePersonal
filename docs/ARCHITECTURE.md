# AutoForge Architecture

## Target flow

```text
Company user on VPN
  -> Entra-protected Forge UI + API (private Azure Container Apps)
  -> Service Bus work item
  -> Forge worker on Azure Container Apps (default)
       or optional Microsoft Foundry Hosted Agent
  -> Microsoft Agent Framework agents
  -> Microsoft Foundry model deployments
  -> Cosmos DB + Blob Storage + Azure AI Search (Skill Registry)
  -> Container Apps Dynamic Sessions (isolated build and test sandbox, no internet egress)
  -> human release approval
  -> worker builds in ACR, vulnerability scan, deploys private Container App,
     runs smoke test, and rolls back on failure
  -> Application Insights, Log Analytics, Workbooks
```

The forge workload uses a managed identity for Foundry, Storage, Cosmos DB, Search, Key Vault, Service Bus, Dynamic Sessions, ACR, and deployment operations. Secrets belong in Key Vault. No GitHub token is required for image build, scan, or deployment in this design.

## Agent responsibilities

1. **Spec Agent** reads source requirements and API contracts, extracts implementation-ready requirements, flags ambiguity, and waits for human approval.
2. **Architecture Agent** proposes a solution blueprint and waits for approval.
3. **Coder Agent** produces code, tests, and candidate reusable skills inside the isolated workflow.
4. **Critic Agent** runs tests, identifies failures, and verifies fixes.
5. **Skill Agent** stores approved recipes in the Skill Registry (Cosmos DB / Blob Storage, discoverable through Azure AI Search).
6. **Security Reviewer** checks application and supply-chain risks.
7. **Deployer Agent** performs the approved build, scan, deployment, smoke test, and rollback path.

## Local implementation status

The Spec Agent runs without Azure credentials using a clearly labelled deterministic path. It parses pasted OpenAPI JSON and YAML locally and accepts extracted text from uploaded source documents. When `FOUNDRY_PROJECT_ENDPOINT` and a model deployment are configured, it runs as a code-first Microsoft Agent Framework agent. Local development uses `DefaultAzureCredential`; Azure Container Apps uses managed identity when `AUTOFORGE_IDENTITY_MODE=managed_identity`.

The API now has opt-in Cosmos DB and Blob Storage repositories for build snapshots and governed skill recipes; set `AUTOFORGE_PERSISTENCE=azure` to use them. The in-process job dispatcher is still not durable, and the Azure AI Search standards index, Service Bus worker, Entra/VPN boundary, dynamic sandbox, image pipeline, private deployment, monitoring, and rollback remain separate production integrations.

The seed recipe pack is imported from `backend/app/skills/seed_recipes.md`. Recipe lifecycle decisions are audited in process memory in local mode and persisted in Cosmos DB in Azure mode; recipe bodies are stored in Blob Storage. When a pre-provisioned index is configured, Azure AI Search retrieves recipes filtered by owning agent and approved status; every result is revalidated against Cosmos/Blob. If Search is unset or unavailable, approved-only lexical retrieval remains the fallback. Model-backed Spec, Architecture, Coder, Critic, and Security Reviewer workflows can receive relevant recipes as untrusted advisory context. Build snapshots remain in Blob Storage. The Security Reviewer still performs bounded local static review and reports cloud scans as not run; see `AGENT5_READINESS.md`. Automatic skill evolution from proven repairs, Entra-authenticated reviewer identity, relevance evaluation, and Deployer skill execution remain pending integrations.

## Governance checkpoints

1. Content safety before requirement processing.
2. Human approval after requirement understanding.
3. Human approval after architecture design.
4. Human approval before reusable skill promotion.
5. Security gates before deployment.
6. Human approval before deployment.
7. Audit event for every critical transition.
