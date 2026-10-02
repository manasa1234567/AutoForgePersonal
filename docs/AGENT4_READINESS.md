# Agent 4: Critic Agent readiness

## Implemented locally

The Critic Agent reviews the Coder Agent's returned artifacts before the workflow can continue. Its deterministic checks inspect relative artifact paths, the 12-file and 30,000-character-per-file/100,000-character-total bounds, Python syntax (using Python's parser without executing files), JSON syntax, YAML syntax when PyYAML is installed, credential-like literals, and whether test files are present. It reports findings, a requirement coverage review, and a test plan based on both acceptance criteria and requirements. If `FOUNDRY_PROJECT_ENDPOINT` is configured, it can also request a source-level review from the Foundry deployment named by `FOUNDRY_CRITIC_MODEL` (or shared `FOUNDRY_MODEL`). Configure the endpoint and identity as described in `AGENT1_READINESS.md`.

The workspace labels these as static checks and explicitly reports runtime validation as not run. It does not claim that a requirement is satisfied just because a matching word appears in source. Without runtime validation, the workflow enters `Blocked` at Prove and cannot proceed to Skill, Security, or Deploy. No fabricated test score or self-heal pass is presented.

## Sandbox adapter implemented; runner and Azure remain pending

The backend now includes a disabled-by-default Azure Container Apps Dynamic Sessions client for a **custom container session pool**. It requests an Entra token for `https://dynamicsessions.io/.default`, calls the configured pool management endpoint over HTTPS, assigns a fresh per-run session identifier, limits requests to 5 to 600 seconds, caps response bodies at 1 MB, and validates a versioned JSON result before treating runtime checks as passed. Static safety failures prevent artifact submission. A non-passing or malformed result cannot reach skill promotion; critical findings block the gate.

The application side is ready to configure with:

- `AUTOFORGE_SANDBOX_ENABLED=true` to opt in. It defaults to `false`.
- `AUTOFORGE_SANDBOX_ENDPOINT` set to the provisioned custom session pool's `poolManagementEndpoint`.
- `AUTOFORGE_SANDBOX_ROUTE` set to a POST route served by the custom container; default `/autoforge/validate`.
- `AUTOFORGE_SANDBOX_TIMEOUT_SECONDS` from 5 to 600; default `120`.
- The existing approved identity settings, with `Azure ContainerApps Session Executor` on the session pool. Managed identity uses `AUTOFORGE_IDENTITY_MODE=managed_identity` and the configured `AZURE_CLIENT_ID` when applicable.

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

Check statuses are `passed`, `failed`, or `skipped`; overall status must be `passed` or `failed`. A passing response must include at least one passed check and no failed check. Findings use severity `Critical`, `High`, `Medium`, or `Low`, with `file`, `issue`, and `recommendation` fields. The runner itself must safely materialize only normalized relative files, impose CPU/memory/process limits, honor the time limit, capture bounded logs, clean up temporary files, and enforce the approved no-internet policy. It must choose build/test procedures from trusted runner policy and project metadata; never interpret requirement text or generated files as shell commands. Support for arbitrary runtimes depends on what this custom image and its policy actually provide.

This repo does **not** yet contain that custom session container/runner or its deployment configuration. Since no Azure pool or identity is available, the adapter has not been connected to a live session and no generated application has been built or tested there. Do not enable the adapter until the pool endpoint and compatible runner contract are provisioned and reviewed. A bounded fix-and-retest loop is implemented for up to two attempts, but it activates only when the sandbox reports a real failed check and the Foundry Coder is configured. The Coder receives the prior generated files and Critic findings, then the Critic and sandbox run again. The loop cannot be exercised until Azure and the custom runner are available; after two failed attempts the build stays blocked for review.

The Security Reviewer now has a separate local static-review implementation; it does not provide dependency CVE, image, Azure policy, runtime, or deployment evidence. See `AGENT5_READINESS.md`. Skill Registry persistence, image scanning, deployment, and rollback still require their own production integrations before a passing sandbox result should be interpreted as production approval.

Microsoft's documentation says custom containers provide the runtime and HTTP server, the pool management endpoint forwards custom paths to the container, and requests require Entra authentication plus the Session Executor role. Code-interpreter execution APIs are a separate pool type; this adapter targets custom containers for application builds. See [custom container sessions](https://learn.microsoft.com/en-us/azure/container-apps/sessions-custom-container), [session usage and authentication](https://learn.microsoft.com/en-us/azure/container-apps/sessions-usage), and [Dynamic Sessions overview](https://learn.microsoft.com/azure/container-apps/sessions).

## Readiness

**Status: static review and bounded repair-loop code implemented; ACA custom-session client and response contract implemented but disabled; custom runner and live runtime validation remain pending.** Agent 4 is not end-to-end verified or deployment-ready.
