# Skill Registry readiness

## Implemented locally

- The 16 recipes in the supplied `Recipes.md` seed pack are copied to `backend/app/skills/seed_recipes.md` and loaded as typed recipe records with ID, owning agent, tags, trigger, inputs, steps, completion checks, pitfalls, output, version, status, and governance audit.
- Every seed starts as `draft`. The local review workflow is `draft -> pending_approval -> approved/rejected`; an approved recipe can be `deprecated`. Rejected and deprecated versions are retained and excluded from retrieval.
- `GET /api/skills` supports lifecycle status, agent, and text filters. `GET /api/skills/{id}` returns the recipe and governance events. `POST /api/skills/{id}/decision` changes lifecycle state and appends an audit event.
- Retrieval filters to approved recipes for the requested agent, applies a bounded lexical relevance ranking, and returns at most five matches. Zero-match recipes are not injected.
- Model-backed Spec, Architecture, Coder, and Critic stages receive matching approved recipes as untrusted advisory context. Approved requirements, user blueprint choices, safety checks, and policy remain authoritative. The Coder response may report applied recipe IDs; the server validates those IDs against the retrieved set and records their versions in the build and timeline.
- The Skills UI lists and searches all seed recipes, exposes full recipe details and governance history, and supports submit, approve, reject, and deprecate actions.

## Local limitations

- The local recipe repository and lifecycle state are in memory. Recipe decisions reset when the backend process restarts.
- There is no authenticated reviewer identity in the current API. Audit events explicitly identify local review as unauthenticated.
- The lexical retriever is a development adapter, not Azure AI Search. Recipe bodies are loaded from the checked-in Markdown seed, not Blob Storage; metadata is not stored in Cosmos DB.
- Offline deterministic agent paths do not consume recipe guidance. Only model-backed Spec, Architecture, Coder, and Critic calls receive retrieved recipes. Coder reports application only when its configured model returns an allowed recipe ID.
- Skill evolution from successful repairs is not enabled: the current Critic does not yet emit reusable before/after diffs with the evidence required by `SKL-EVOL-001`. Security Reviewer recipes are contextual guidance for local static review; Deployer recipes are guidance for local deployment preflight. Neither recipe pack substitutes for Azure vulnerability scanning, image build/deploy, or other cloud execution evidence.

## Azure integration required

1. Implement a Cosmos DB metadata repository and Blob Storage body store behind `SkillRepository`, including version-preserving writes and transactional status changes.
2. Create/update Azure AI Search documents for approved versions; filter by agent and status, rank by query, and hydrate recipe bodies from Blob Storage.
3. Add Entra-authenticated reviewer identity and durable audit events. Require a distinct authorized reviewer for promotion where policy requires separation of duties.
4. Add the recipe evaluation set from the seed pack suggestions; measure relevance, unsafe/conflicting retrieval, and task quality before enabling automatic retrieval in production.
5. Implement the Evolver, and integrate the Azure-dependent Security Reviewer and Deployer controls before treating their recipes as executed cloud controls.

The submitted recipes are guidance data, not executable tools or policy overrides. Prompt Shields, static checks, sandbox validation, approval gates, and the approved requirements remain independent controls.
