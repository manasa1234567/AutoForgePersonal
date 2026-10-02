# Agent 2: Architecture Agent readiness

## What it does

After a person approves Agent 1's requirements, the Architecture Agent receives the approved requirements, acceptance criteria, dependencies, constraints, and security considerations. It proposes an application blueprint, explains why components are included, records assumptions, and lists unresolved architecture decisions for human review.

The Architecture Agent does not write application code. The Coder Agent owns code generation after the blueprint is approved.

## Foundry mode

Configure the shared `FOUNDRY_PROJECT_ENDPOINT`, the architecture deployment as the GitHub Actions repository variable `FOUNDRY_ARCHITECTURE_MODEL`, and the approved managed identity/authentication settings described in `AGENT1_READINESS.md`. The CD workflow passes this variable to the backend. If `FOUNDRY_ARCHITECTURE_MODEL` is empty, the agent can use the shared `FOUNDRY_MODEL`. The model call starts when the user approves the requirements. A configured model failure fails the build visibly; the workflow does not substitute a local blueprint.

The Foundry instruction requires the agent to honor user technology and hosting constraints, tie selected components to approved requirements, and call out assumptions or open questions instead of silently inventing facts.

## Before Azure access

The local rules path produces a provisional, requirement-sensitive outline and is labeled `local-rules`. It detects common needs such as persisted records, file handling, notifications, and identity, but cannot semantically reason over arbitrary use cases like the Foundry model. It intentionally leaves provider, framework, and deployment choices open when the approved input does not provide enough context. Review the questions and assumptions before approving the blueprint.
