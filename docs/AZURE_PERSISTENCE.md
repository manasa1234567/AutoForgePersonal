# Azure persistence setup

The backend can use the existing Cosmos DB and Blob Storage resources for durable build and skill state. Local development remains in-memory unless `AUTOFORGE_PERSISTENCE=azure` is set.

## GitHub Actions variables

Add these repository or `production` environment variables before enabling Azure persistence:

| Name | Value |
| --- | --- |
| `AUTOFORGE_PERSISTENCE` | `azure` |
| `AUTOFORGE_COSMOS_ENDPOINT` | `https://af-cosmos-5usl4p.documents.azure.com:443/` |
| `AUTOFORGE_COSMOS_DATABASE` | `autoforge` |
| `AUTOFORGE_COSMOS_JOBS_CONTAINER` | `jobs` |
| `AUTOFORGE_COSMOS_SKILLS_CONTAINER` | `skills` |
| `AUTOFORGE_BLOB_ACCOUNT_URL` | `https://afstorage5usl4p.blob.core.windows.net` |
| `AUTOFORGE_BLOB_SPECS_CONTAINER` | `specs` |
| `AUTOFORGE_BLOB_WORKSPACES_CONTAINER` | `workspaces` |
| `AUTOFORGE_SKILL_SEARCH_ENDPOINT` | Optional Azure AI Search endpoint |
| `AUTOFORGE_SKILL_SEARCH_INDEX` | `autoforge-skills` |

The existing `FOUNDRY_RUNTIME_IDENTITY_RESOURCE_ID` and `FOUNDRY_RUNTIME_CLIENT_ID` values select the backend's user-assigned managed identity. That identity needs Cosmos DB Built-in Data Contributor at the `autoforge` database scope, and Storage Blob Data Contributor on the `specs` and `workspaces` containers. The `skills` container uses the same Cosmos role.

When Search is enabled, grant the same identity **Search Index Data Contributor** on the Search service. The application does not create indexes; Azure IT must provision the index before setting the endpoint. Search is optional, and approved-only lexical retrieval remains active if Search is unset or unavailable.

## What is persisted

- Cosmos DB stores a compact current-build pointer in `jobs` and governed skill recipes in `skills`.
- Blob Storage stores immutable full build-state snapshots in `workspaces/{buildId}/snapshots/`. These include normalized agent results, generated source files, approval state, metrics, and the complete audit timeline.
- Blob Storage stores the extracted intake record in `specs/{buildId}/intake.json`.
- Each build save creates a new snapshot. No automatic snapshot retention or deletion is configured.
- Skill bodies are stored at `workspaces/skill-bodies/{skillId}/{version}/{sha256}.json`. Cosmos stores recipe lifecycle metadata, audit events, and the body pointer. Existing full-body Cosmos records are read compatibly and backfilled at startup.

## Azure AI Search skills index

Pre-provision the configured skill index with these fields:

| Field | Type | Attributes |
| --- | --- | --- |
| `id` | Edm.String | key |
| `skillId` | Edm.String | filterable |
| `version` | Edm.String | filterable |
| `agent` | Edm.String | filterable |
| `status` | Edm.String | filterable |
| `title` | Edm.String | searchable |
| `useWhen` | Edm.String | searchable |
| `tags` | Collection(Edm.String) | searchable, filterable |
| `searchText` | Edm.String | searchable |

Search documents contain retrieval text and governance metadata, not executable tools. The backend filters by agent and approved status, then reloads the recipe from Cosmos/Blob and rechecks its status/version before injecting it into an agent prompt.

The Cosmos adapter reads each container's declared simple partition key and writes the build or skill ID to it. The key is therefore compatible with paths such as `/jobId`, `/skillId`, or `/id`.

## Limitations and next integration

This does not persist provider-internal raw token streams; it persists the structured agent results returned to AutoForge. Company-standard ingestion/retrieval remains separate: the `standards` and `standards_usage` Cosmos containers exist, but the skill index contains governed recipe retrieval only. Search cannot create its own index; provision the schema above before enabling Search.

If Azure persistence is enabled, backend startup checks the configured Cosmos containers and Blob containers. A resource, permission, or configuration failure is surfaced at startup rather than silently falling back to volatile storage.
