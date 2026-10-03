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

The existing `FOUNDRY_RUNTIME_IDENTITY_RESOURCE_ID` and `FOUNDRY_RUNTIME_CLIENT_ID` values select the backend's user-assigned managed identity. That identity needs Cosmos DB Built-in Data Contributor at the `autoforge` database scope, and Storage Blob Data Contributor on the `specs` and `workspaces` containers. The `skills` container uses the same Cosmos role.

## What is persisted

- Cosmos DB stores a compact current-build pointer in `jobs` and governed skill recipes in `skills`.
- Blob Storage stores immutable full build-state snapshots in `workspaces/{buildId}/snapshots/`. These include normalized agent results, generated source files, approval state, metrics, and the complete audit timeline.
- Blob Storage stores the extracted intake record in `specs/{buildId}/intake.json`.
- Each build save creates a new snapshot. No automatic snapshot retention or deletion is configured.

The Cosmos adapter reads each container's declared simple partition key and writes the build or skill ID to it. The key is therefore compatible with paths such as `/jobId`, `/skillId`, or `/id`.

## Limitations and next integration

This does not persist provider-internal raw token streams; it persists the structured agent results returned to AutoForge. Search index creation and company-standard ingestion/retrieval are separate: the `standards` and `standards_usage` Cosmos containers exist, but the Search service currently has no index. The backend's Search Index Data Contributor assignment can read/write documents after an index is provisioned, but cannot create the index. Do not claim that standards retrieval is active until its source corpus and index are configured.

If Azure persistence is enabled, backend startup checks the configured Cosmos containers and Blob containers. A resource, permission, or configuration failure is surfaced at startup rather than silently falling back to volatile storage.
