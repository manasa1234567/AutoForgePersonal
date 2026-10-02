# Agent 5: Security Reviewer readiness

## Implemented locally

The Security Reviewer now runs against the generated source artifacts without executing them. It checks normalized relative paths, embedded credential/private-key patterns, dangerous dynamic execution and deserialization patterns, insecure TLS/CORS/debug settings, and whether supported dependency manifests are present. It emits file-level findings, check statuses, an audit event, its local review mode, and an explicit list of scans that were not performed.

High or critical source findings block release. A clean local source review is **not** release approval: the workflow remains blocked while dependency vulnerability scanning, container image scanning, Azure policy/deployment checks, and the Azure deployment adapter are unavailable. The old hard-coded passing release scorecard has been removed. Generated source is never executed by this reviewer.

The reviewer is wired into the orchestrator's Release stage and can also be tried locally from the **Prove** screen with **Run Local Security Review** as soon as the Coder has produced artifacts. The equivalent API is `POST /api/builds/{buildId}/security-review`; it returns the updated build. Calls before code artifacts exist return HTTP 409.

## Skill Registry use

The Security Reviewer retrieves only human-approved `Security Reviewer` recipes matching the build. The imported `SKL-SEC-001` recipe is draft by default; use **Skills** to submit and approve it before it is made available to this agent. Recipe instructions are advisory and cannot override the approved requirements, blueprint, or security controls. Local checks run even when no security recipe has been approved.

## Local setup

No Azure endpoint, key, or scanner setting is required for the deterministic local checks. Start the backend and frontend using the repository's local setup, create a build, and proceed until the Prove stage displays generated artifacts. Click **Run Local Security Review** and inspect the checks, findings, and unperformed scans on that page. To inspect the backend contract, use the FastAPI docs at `/docs` and call `POST /api/builds/{buildId}/security-review`.

## Azure work remaining

The local reviewer does not establish package CVE status, build an image, scan an image, verify deployed identity/network policy, or execute application tests. Before release approval is enabled in Azure, integrate and capture actual results from the approved dependency scanner and vulnerability database, ACR image build and Defender for Containers scan, deployment-policy checks, and the private Container Apps deployment/smoke-test path. Persist reports and audit events through the configured Azure stores and ensure failures/timeouts block release. Assign only the workload identity permissions required by those approved integrations; do not treat a local static pass as evidence for Azure controls.

**Readiness:** local artifact review, API, audit, UI, and fail-closed release integration implemented. Vulnerability, image, Azure policy, and deployment checks still require the provisioned Azure environment. This agent is not a production release approval by itself.
