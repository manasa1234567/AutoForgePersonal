# Skill Registry readiness

## Implemented locally

- The 16 recipes in the supplied `Recipes.md` seed pack are copied to `backend/app/skills/seed_recipes.md` and loaded as typed recipe records with ID, owning agent, tags, trigger, inputs, steps, completion checks, pitfalls, output, version, status, and governance audit.
- Every seed starts as `draft`. The local review workflow is `draft -> pending_approval -> approved/rejected`; an approved recipe can be `deprecated`. Rejected and deprecated versions are retained and excluded from retrieval.
- `GET /api/skills` supports lifecycle status, agent, and text filters. `GET /api/skills/{id}` returns the recipe and governance events. `POST /api/skills/{id}/decision` changes lifecycle state and appends an audit event.
- Retrieval filters to approved recipes for the requested agent, applies a bounded lexical relevance ranking, and returns at most five matches. Zero-match recipes are not injected.
- In Azure persistence mode, recipe bodies are stored as immutable, content-addressed JSON blobs under `workspaces/skill-bodies/`; Cosmos stores lifecycle metadata and a body pointer. Legacy full-body Cosmos records remain readable and are backfilled without changing approval status.
- When `AUTOFORGE_SKILL_SEARCH_ENDPOINT` and `AUTOFORGE_SKILL_SEARCH_INDEX` are set, Azure AI Search performs keyword retrieval filtered by agent and approved status. Search results are rehydrated from Cosmos/Blob and checked against current approval/version. If Search is unset, empty, or unavailable, the approved-only lexical retriever remains the fallback.
- Model-backed Spec, Architecture, Coder, and Critic stages receive matching approved recipes as untrusted advisory context. Approved requirements, user blueprint choices, safety checks, and policy remain authoritative. The Coder response may report applied recipe IDs; the server validates those IDs against the retrieved set and records their versions in the build and timeline.
- The Skills UI lists and searches all seed recipes, exposes full recipe details and governance history, and supports submit, approve, reject, and deprecate actions.
- A Coder repair may return an optional stack-neutral skill candidate. Candidates are bounded and screened for secrets and unsafe control-bypass instructions, remain attached to the build during repair, and are persisted as drafts only after the repaired deployment passes its live smoke test. They are never auto-approved or injected into future prompts before human approval.

## Local limitations

- The local recipe repository and lifecycle state are in memory. Recipe decisions reset when the backend process restarts.
- There is no authenticated reviewer identity in the current API. Audit events explicitly identify local review as unauthenticated.
- Azure AI Search currently uses keyword/BM25 retrieval; vector/hybrid retrieval and a relevance evaluation suite are not enabled. The index must be provisioned before the endpoint is configured; the application identity is not expected to create the index.
- Offline deterministic agent paths do not consume recipe guidance. Only model-backed Spec, Architecture, Coder, and Critic calls receive retrieved recipes. Coder reports application only when its configured model returns an allowed recipe ID.
- Candidate generation depends on the Coder returning a reusable recipe during a repair; no independent before/after diff evaluator or usage-success metric currently ranks candidates. Security Reviewer recipes are contextual guidance for local static review; Deployer recipes are guidance for local deployment preflight. Neither recipe pack substitutes for Azure vulnerability scanning, image build/deploy, or other cloud execution evidence.

## Remaining Azure integration

1. Provision the `autoforge-skills` Azure AI Search index described in `AZURE_PERSISTENCE.md`, configure the Search endpoint/index variables, and grant Search Index Data Contributor to the backend managed identity.
2. Add Entra-authenticated reviewer identity and durable audit events. Require a distinct authorized reviewer for promotion where policy requires separation of duties.
3. Add the recipe evaluation set from the seed pack suggestions; measure relevance, unsafe/conflicting retrieval, and task quality before enabling Search retrieval in production.
4. Add candidate evaluation/usage-success metrics and Entra-authenticated reviewer identity. Integrate Deployer recipes with real deployment evidence before treating them as executed cloud controls.

The submitted recipes are guidance data, not executable tools or policy overrides. Prompt Shields, static checks, sandbox validation, approval gates, and the approved requirements remain independent controls.
