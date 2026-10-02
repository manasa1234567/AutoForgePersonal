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

The remaining agents and Azure resources are still demo adapters in this repository. The worker queue, Entra/VPN boundary, persistent stores, dynamic sandbox, image pipeline, private deployment, monitoring, and rollback require the Day-0 environment and D1-D7 identity/network approvals before cloud execution can be completed.

The seed recipe pack is imported into a local `SkillRepository` from `backend/app/skills/seed_recipes.md`. Recipe lifecycle decisions are audited in process memory; lexical retrieval returns only approved recipes, and the model-backed Spec, Architecture, Coder, and Critic agents receive relevant recipes as untrusted advisory context. The Coder Agent can report which retrieved recipe IDs it applied, and build audit state records retrieval/application. The local store is not Cosmos DB, recipe bodies are not in Blob Storage, and retrieval is not Azure AI Search. The evolver, security-review, and deployer recipes remain catalogued guidance until those workflow components have real implementations.

## Governance checkpoints

1. Content safety before requirement processing.
2. Human approval after requirement understanding.
3. Human approval after architecture design.
4. Human approval before reusable skill promotion.
5. Security gates before deployment.
6. Human approval before deployment.
7. Audit event for every critical transition.
