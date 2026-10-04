# Agent 4: Critic Agent readiness

## Implemented locally

The Critic Agent reviews the Coder Agent's returned artifacts before the workflow can continue. Its deterministic checks inspect relative artifact paths, the shared 128-file, 30,000 UTF-8-byte-per-file, and 100,000 UTF-8-byte-total bounds, Python syntax (using Python's parser without executing files), JSON syntax, YAML syntax when PyYAML is installed, credential-like literals, and whether test files are present. It reports findings, a requirement coverage review, and a test plan based on both acceptance criteria and requirements. If `FOUNDRY_PROJECT_ENDPOINT` is configured, it can also request a source-level review from the Foundry deployment named by `FOUNDRY_CRITIC_MODEL`, `FOUNDRY_MODEL`, or, as a single-deployment fallback, `FOUNDRY_CODER_MODEL`. The CD workflow forwards these variables to the backend. Configure the endpoint and identity as described in `AGENT1_READINESS.md`.

The workspace labels these as static checks and explicitly reports runtime validation as not run. It does not claim that a requirement is satisfied just because a matching word appears in source. Without runtime validation, the workflow enters `Blocked` at Prove and cannot proceed to Skill, Security, or Deploy. No fabricated test score or self-heal pass is presented.

## Container Apps Job sandbox integration

The backend supports two explicitly selected runtime modes. `container_job` uploads a per-run contract to Blob Storage, reads the existing Container Apps Job template, overrides only the configured runner container image and run-specific environment, starts the Job, then polls for the matching result blob. `dynamic_sessions` retains the previous custom session-pool adapter. The critic keeps static path, size, syntax, and credential checks ahead of either runtime. Sandbox infrastructure errors are recorded as validation failures and do not trigger code-generation self-heal attempts.

The current Azure setup uses the Container Apps Job path (`AUTOFORGE_SANDBOX_MODE=container_job`). The backend needs `Container Apps Jobs Operator` permission scoped to the named Job (or a custom role restricted to read/start). The backend identity and the Job's runner identity each need `Storage Blob Data Contributor` on the `sandbox-runs` container: the backend writes the contract and reads the result; the runner reads the contract and writes the result. The runner client ID must belong to a user-assigned identity attached to the Job. The `AUTOFORGE_SANDBOX_JOB_CONTAINER` value must match the Job's actual main container name.

The repository's `sandbox-runner/` image is the custom-session HTTP runner. Container Job mode uses the separately configured `AUTOFORGE_SANDBOX_IMAGE` (`afregistry5usl4p.azurecr.io/autoforge-runner:2.0` in the current deployment settings). Verify that this image implements the Blob contract with `contract.json` and `result.json`; CD does not replace the Job image unless that variable is changed.

GitHub Actions must pass the sandbox Job, resource group, image, runner client ID, storage account/container, and API version to the backend. The workflow validates required settings when sandbox execution is enabled. Repository variable changes do not affect an already running backend until CD deploys. Keep Dynamic Sessions settings in place if you may switch back; Container Job mode does not use the session pool endpoint.

## Readiness

**Status: Container Apps Job adapter and runtime-mode wiring are implemented locally. End-to-end execution still depends on the existing runner image contract, Job container name and managed identity, Blob container and role assignments, backend Job-start permission, and a successful deployment. No live Job validation has been performed here.**