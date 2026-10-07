# Focused packaging and Forge resume

Build `e3492044` returned backend source in its first two attempts, then added
frontend source while still omitting the backend Poetry manifest and CRA
TypeScript build dependencies. The shared validator rejected these real
defects. Broad full-application retries did not complete the configuration.

Generation now permits one separate Packaging Agent call once the approved
frontend's source is present. It receives the approved stack, complete source
inventory and validation history. Its output is restricted to dependency/build
configuration. Application source, tests and model-authored lockfiles cannot be
changed by this pass. npm manifest updates retain existing dependency and script
entries. The merged files still pass normal source-size, path, startup and
packaging validation; failures are returned to the bounded coding repair loop.

There are at most three coding responses and one focused packaging response in
an initial generation run. Deployment repair retains its existing shared
three-attempt budget and disables this additional packaging call.

Failed Forge builds with saved candidate files and a previously approved
blueprint can use Retry code generation, or POST `/api/builds/{id}/retry-forge`.
The same build, requirements, blueprint and candidate are reused. Complete
saved frontend source goes directly to packaging completion before any broad
code regeneration is considered. Successful output returns to the artifacts
approval gate; Prove, Security and Release approvals are not bypassed.

This is shared platform behavior, not a manual modification of a generated
use case. Deploy the platform update before using the new retry control.
Passing platform tests does not prove a generated application's Docker build,
startup or Azure smoke test; those validations remain mandatory.
