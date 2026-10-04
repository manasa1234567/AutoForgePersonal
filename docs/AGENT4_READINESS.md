# Agent 4: Critic Agent readiness

## Implemented locally

The Critic Agent reviews the Coder Agent's returned artifacts before the workflow can continue. Its deterministic checks inspect relative artifact paths, the shared 128-file, 30,000 UTF-8-byte-per-file, and 100,000 UTF-8-byte-total bounds, Python syntax (using Python's parser without executing files), JSON syntax, YAML syntax when PyYAML is installed, credential-like literals, and whether test files are present. It reports findings, a requirement coverage review, and a test plan based on both acceptance criteria and requirements. If `FOUNDRY_PROJECT_ENDPOINT` is configured, it can also request a source-level review from the Foundry deployment named by `FOUNDRY_CRITIC_MODEL`, `FOUNDRY_MODEL`, or, as a single-deployment fallback, `FOUNDRY_CODER_MODEL`. The CD workflow forwards these variables to the backend. Configure the endpoint and identity as described in `AGENT1_READINESS.md`.

The workspace labels these as static checks and explicitly reports runtime validation as not run. It does not claim that a requirement is satisfied just because a matching word appears in source. Without runtime validation, the workflow enters `Blocked` at Prove and cannot proceed to Skill, Security, or Deploy. No fabricated test score or self-heal pass is presented.

## Sandbox adapter and initial runner implemented; Azure pool remains pending

The backend now includes a disabled-by-default Azure Container Apps Dynamic Sessions client for a **custom container session pool**. It requests an Entra token for `https://dynamicsessions.io/.default`, calls the configured pool management endpoint over HTTPS, assigns a fresh per-run session identifier, limits requests to 5 to 600 seconds, caps response bodies at 1 MB, and validates a versioned JSON result before treating runtime checks as passed. Static safety failures prevent artifact submission. A non-passing or malformed result cannot reach skill promotion; critical findings block the gate.

The repository includes an initial custom-container runner in `sandbox-runner/`.
The CD workflow builds and pushes it as
`<ACR_NAME>.azurecr.io/autoforge-sandbox-runner:<commit-sha>`. It serves port
8080. Its initial policy supports Python syntax/pytest, Node `build`/`test`
scripts from `package.json`, and JSON parsing. It does not install project
dependencies. With pool egress disabled, missing dependencies fail checks;
Java/Spring, Go, and Rust are unsupported. See `sandbox-runner/README.md` before
enabling it.

The application side is ready to configure with:

- `AUTOFORGE_SANDBOX_ENABLED=true` to opt in. It defaults to `false`.
- `AUTOFORGE_SANDBOX_ENDPOINT` set to the provisioned custom session pool's `poolManagementEndpoint`.
- `AUTOFORGE_SANDBOX_ROUTE` set to a POST route served by the custom container; default `/autoforge/validate`.
- `AUTOFORGE_SANDBOX_TIMEOUT_SECONDS` from 5 to 600; default `120`.
- The existing approved identity settings, with `Azure ContainerApps Session Executor` on the session pool. Managed identity uses `AUTOFORGE_IDENTITY_MODE=managed_identity` and the configured `AZURE_CLIENT_ID` when applicable.

For Azure Container Apps deployments, the CD workflow forwards these four sandbox settings into the backend container. GitHub Actions repository variables alone do not update the running container. The workflow rejects `AUTOFORGE_SANDBOX_ENABLED=true` when the endpoint is missing. Keep the flag `false` until the runner image, compatible session pool, and role assignment are deployed.

### Required custom-container runner contract

The session container still needs to implement the configured route. ACA forwards requests to the custom container and provisions a session based on the `identifier` query parameter. The runner receives JSON with `contractVersion: "1"`, title, approved blueprint, approved requirements, acceptance criteria, generated artifacts (relative path to text content), and the backend's timeout limit. It must return JSON with:

```json
{
  "contractVersion": "1",
  "status": "passed",
  "summary": "Build and checks completed",
  "checks": [{"name": "build", "status": "passed", "detail": "..."}],
  "findings": []
}
```

Check statuses are `passed`, `failed`, or `skipped`; overall status must be `passed` or `failed`. A passing response must include at least one passed check and no failed check. Findings use severity `Critical`, `High`, `Medium`, or `Low`, with `file`, `issue`, and `recommendation` fields. The HTTP parent validates normalized relative files, enforces request/artifact/output limits, creates and deletes a per-request temporary workspace, and passes no environment credentials to child processes. The parent runs as root only to drop generated Python tests and Node scripts to an unprivileged UID; child processes receive CPU, address-space, process-count, file-size, descriptor, and wall-clock limits. Keep session egress disabled and give the session pool only a dedicated, pull-only ACR identity. Never interpolate requirement text into commands. Arbitrary runtimes and dependency installation are unsupported by the initial image.

The runner image and CD publishing step now exist, but no live Azure pool has been confirmed and no generated application has run there. Do not enable the adapter until the image is present in ACR, the pool uses that image on port 8080 with egress disabled, and the backend identity has the Session Executor role. A bounded fix-and-retest loop is implemented for up to two attempts, but activates only when the sandbox reports a real failed check and the Foundry Coder is configured. Projects needing unavailable dependencies or runtimes fail under this initial runner policy.

The Security Reviewer now has a separate local static-review implementation; it does not provide dependency CVE, image, Azure policy, runtime, or deployment evidence. See `AGENT5_READINESS.md`. Skill Registry persistence, image scanning, deployment, and rollback still require their own production integrations before a passing sandbox result should be interpreted as production approval.

Microsoft's documentation says custom containers provide the runtime and HTTP server, the pool management endpoint forwards custom paths to the container, and requests require Entra authentication plus the Session Executor role. Code-interpreter execution APIs are a separate pool type; this adapter targets custom containers for application builds. See [custom container sessions](https://learn.microsoft.com/en-us/azure/container-apps/sessions-custom-container), [session usage and authentication](https://learn.microsoft.com/en-us/azure/container-apps/sessions-usage), and [Dynamic Sessions overview](https://learn.microsoft.com/azure/container-apps/sessions).

## Readiness

**Status: static review, bounded repair-loop code, ACA custom-session client, and initial runner image implemented; Azure pool provisioning and live runtime validation remain pending.** Agent 4 is not end-to-end verified or deployment-ready.

