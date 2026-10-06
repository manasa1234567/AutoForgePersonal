# Buildathon Requirement Mapping

| Requirement | Demo implementation | Azure target |
|---|---|---|
| 3+ AI agents | 7 specialized agents + orchestrator | Foundry Hosted Agent + Agent Framework |
| 4+ APIs | Build create/start/get/approve/refine/events | FastAPI behind internal Container Apps |
| RAG / Knowledge Base | 16 governed seed recipes, local approval lifecycle, approved-only retrieval into model-backed agents | Cosmos DB governance metadata + immutable Blob bodies + optional pre-provisioned Azure AI Search keyword index; lexical fallback |
| Structured dataset | Requirements, blueprint, proof, metrics | Cosmos DB |
| Agent orchestration | `Orchestrator` | Microsoft Agent Framework |
| HITL | Requirements, blueprint, skill and release gates | Foundry tool approval / app approval flow |
| Simulated action | Deploy + smoke verification | GitHub Actions / ACR / Container Apps |
| Audit trail | `AuditEvent` | Application Insights + Log Analytics |
| Error handling | API errors + safety failure + orchestrator failure | Azure Monitor |
| AgentOps | tokens, tool calls, success rate, self-heal count | App Insights / Workbooks |
| AI guardrails | demo prompt-injection marker check | Content Safety / Prompt Shields |
| Private deployment | represented in release result | VNet + private endpoints + internal ingress |
