# AutoForge ACA sandbox runner

This image serves `POST /autoforge/validate` on port 8080 and implements the
version 1 response contract consumed by the backend.

## Initial check policy

- Python files: syntax parsing; supplied test files run with `pytest`.
- Node projects: parse `package.json`; execute its declared `build` and `test`
  scripts when present.
- JSON files: syntax parsing.
- Java/Spring, Go, and Rust manifests: explicitly fail as unsupported.

The runner does not install dependencies or access package registries. Keep ACA
session egress disabled. Python dependencies beyond those baked into this image
and Node dependencies absent from the generated project will cause their checks
to fail. Unsupported runtimes fail rather than producing a false pass. This
initial image therefore needs a compatible generated project and offline
dependencies to pass runtime validation.

Generated Python tests and Node scripts execute as untrusted code in an
unprivileged child process inside the per-request ACA session. The HTTP parent
runs as root only so it can drop each child to the `execuser` UID. The child has
CPU, address-space, process-count, file-size, descriptor, and wall-clock limits.
The runner caps request, artifact, and captured-output sizes, rejects unsafe
paths, deletes the temporary workspace, and passes no cloud credentials to the
child. ACA session isolation and `EgressDisabled` are the outer security
boundary. Do not expose this runner outside the authenticated session-pool
management endpoint. Attach only a dedicated managed identity with ACR pull
permission to the pool; do not attach the backend identity, which has access to
application data services.

## Image

```sh
docker build -t autoforge-sandbox-runner:local ./sandbox-runner
```

The Azure CD workflow publishes
`<ACR_NAME>.azurecr.io/autoforge-sandbox-runner:<commit-sha>` alongside the
frontend and backend images. Configure the session pool with that exact image
tag and target port `8080`.
