# Agent 3: Coder Agent readiness

## Blueprint handoff

The Coder Agent receives the requirement set approved by the user and the final blueprint saved at the Architecture approval gate. Every blueprint choice is editable free-form text: application, UI, backend, identity, data, storage, messaging, deployment, and security controls. There is no provider or technology allowlist. Blueprint choices are binding: the exact user-entered values are included in the coder prompt and the agent is instructed not to substitute them. The Foundry model can generate for any stack it can handle; generation quality and stack-specific correctness still need Critic validation. The workspace shows generated artifacts returned by the agent.

## Foundry mode

Configure the GitHub Actions repository variable `FOUNDRY_CODER_MODEL` with the exact deployment name. For an Agent 3-only trial, set it to the existing `gpt-4.1-mini` deployment and leave the shared `FOUNDRY_MODEL` unset. The CD workflow passes this value to the backend; push the updated workflow to `main` and run CD again after adding the variable. Keep the Foundry project endpoint and managed identity settings from `AGENT1_READINESS.md` configured.

After requirements are approved and the Architecture Agent has produced a blueprint, review or edit the blueprint and select **Save and Approve Blueprint**. That approval invokes Agent 3. The output is limited to 12 relative-path text files and 100,000 combined characters. Unsafe paths and invalid outputs are rejected. A configured model failure stops the build visibly.

After generation, the build pauses at a human artifact-review gate. The user can download all generated text files as a ZIP, inspect a standalone static UI concept in a sandboxed preview, and request a revision in plain language before continuing to Critic review. Revisions are merged into the existing artifact set so files the model did not return remain in the project. The visual preview is a static mockup, not the running generated application; generated code is not executed by this review gate. AI revisions use the Coder deployment and add model usage. ZIP edits made outside the app are not synchronized back into the build.

This repository does not currently implement a Git merge or publish action. The artifact approval gate means “continue to Critic review”; a real merge still needs a separate Git integration, branch/PR review, and approval workflow. Generated code is not executed here; the current Critic and later stages still need isolated build/test/deploy implementations before generated artifacts can be considered validated or deployed.

## Before Azure access

The local path has small React and Angular preview templates. For other frontend choices it emits a scaffold note because offline rules cannot reliably generate arbitrary framework code. This is not full use-case implementation or semantic model code generation; it is labeled `local-scaffold` in the workspace. Arbitrary user-selected stacks require the configured Foundry Coder model.
