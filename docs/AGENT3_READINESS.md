# Agent 3: Coder Agent readiness

## Blueprint handoff

The Coder Agent receives the requirement set approved by the user and the final blueprint saved at the Architecture approval gate. Every blueprint choice is editable free-form text: application, UI, backend, identity, data, storage, messaging, deployment, and security controls. There is no provider or technology allowlist. Blueprint choices are binding: the exact user-entered values are included in the coder prompt and the agent is instructed not to substitute them. The Foundry model can generate for any stack it can handle; generation quality and stack-specific correctness still need Critic validation. The workspace shows generated artifacts returned by the agent.

## Foundry mode

Configure `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_CODER_MODEL`, or use the shared `FOUNDRY_MODEL`, with the approved identity setup documented in `AGENT1_READINESS.md`. The output is limited to 12 relative-path text files and 100,000 combined characters. Unsafe paths and invalid outputs are rejected. A configured model failure stops the build visibly.

Generated code is presented for review; this step does not execute model-generated files. The current Critic and later stages still have demo behavior and must be replaced with isolated build/test/deploy implementations before generated artifacts can be considered validated or deployed.

## Before Azure access

The local path has small React and Angular preview templates. For other frontend choices it emits a scaffold note because offline rules cannot reliably generate arbitrary framework code. This is not full use-case implementation or semantic model code generation; it is labeled `local-scaffold` in the workspace. Arbitrary user-selected stacks require the configured Foundry Coder model.
