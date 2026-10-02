# API Contract — Demo Mode

Base URL: `http://127.0.0.1:8000`

## Health

`GET /api/health`

## Create build

`POST /api/builds`

```json
{
  "source_type": "usecase",
  "title": "Customer Onboarding Enhancement",
  "source_text": "Build a secure customer onboarding service...",
  "files": ["requirements.docx", "api-spec.yaml"],
  "file_contents": [
    { "name": "api-spec.yaml", "content_base64": "<base64-encoded file bytes>" }
  ]
}
```

`file_contents` is optional and limited to 10 files / 15 MB combined. Supported formats are OpenAPI YAML/JSON, text, Markdown, PDF with selectable text, and DOCX. For `source_type: "openapi"`, provide exactly one YAML/JSON file or one pasted contract. Extracted source text is capped at 20,000 characters before analysis.

## Start build

`POST /api/builds/{buildId}/start`

Starts the asynchronous orchestration workflow.

## Get build

`GET /api/builds/{buildId}`

The Angular UI polls this endpoint every second in demo mode.

## Approve gate

`POST /api/builds/{buildId}/approve`

```json
{ "gate": "requirements" }
```

Allowed gates: `requirements`, `blueprint`, `skill`, `release`.

## Update the proposed blueprint

`PUT /api/builds/{buildId}/blueprint` is available while the blueprint approval gate is pending. It accepts the editable application, frontend, backend, data, storage, messaging, identity, deployment, and security choices. The update is saved to the build and recorded in the audit trail. Blueprint approval then passes the saved choices to the Coder Agent.

`POST /api/builds/{buildId}/security-review` runs the local Security Reviewer over generated artifacts without executing them and returns the updated build, including findings, check statuses, and scans that were not run. It requires generated artifacts (otherwise HTTP 409). This static review does not replace dependency CVE, image, Azure policy, runtime, or deployment validation; the release gate stays closed while those integrations are unavailable. See `AGENT5_READINESS.md`.

`POST /api/builds/{buildId}/deployment-preflight` asks the Deployer Agent to prepare a local-only deployment plan. The response includes configuration and gate checks, blockers, and a SHA-256 manifest of generated artifacts. It never builds or deploys an image. See `AGENT6_READINESS.md`.

## Refine

`POST /api/builds/{buildId}/refine`

```json
{ "text": "Add explicit authentication and retry requirements." }
```

## Events

`GET /api/builds/{buildId}/events`

Returns the audit trail for the build.

## Skill Registry

`GET /api/skills` returns the imported recipe catalog. Optional query parameters are `status`, `agent`, and `q`. Supported lifecycle statuses are `draft`, `pending_approval`, `approved`, `rejected`, and `deprecated`.

`GET /api/skills/{recipeId}` returns a recipe and its governance audit.

`POST /api/skills/{recipeId}/decision` advances one lifecycle decision:

```json
{ "decision": "submit", "reason": "Ready for engineering review" }
```

Allowed decisions are `submit` (draft to pending approval), `approve` (pending approval to approved), `reject` (pending approval to rejected), and `deprecate` (approved to deprecated). Only approved recipes are eligible for agent retrieval. These local decisions are process-memory only and the API has no Entra reviewer identity yet; production must persist decisions and derive the reviewer from authenticated identity.
