# 7-Minute Demo Script

## 0:00 — Problem

"Developers spend time translating requirements into architecture, code, tests, fixes and deployment steps. AutoForge turns that workflow into a governed agent journey."

## 0:30 — Start Forge

Choose **Use Case** rather than Jira to show that Jira is not a mandatory dependency. Enter the customer onboarding requirement and optionally add documents.

## 1:15 — Understand

Show extracted requirements and the source files. Explain that the Spec Agent converts engineering intent into testable requirements. Click **Approve & Continue**.

## 2:00 — Design

Show the blueprint and reasoning. Explain that the Architecture Agent selects the solution using enterprise constraints. Approve it.

## 2:45 — Forge

Show the generated project structure and reusable skill proposal. Explain that the Coder Agent creates application code and tests.

## 3:30 — Prove

Show the synthetic contract failure. The Critic Agent identifies the root cause, applies a fix and reruns tests. This is the strongest autonomous behavior in the demo.

## 4:30 — Skill Registry

Open **Skills** and show the imported seed recipes. Submit one draft for review, approve it, and explain that only approved recipes for the active agent can be retrieved. In local mode the registry is in memory with lexical retrieval. Azure mode stores governance in Cosmos DB and recipe bodies in Blob Storage; when the IT-provisioned skill index is configured, Azure AI Search performs keyword retrieval, with lexical fallback if Search is unavailable. After a repaired app successfully deploys, an optional generalized skill candidate appears as a draft for human review; it is not automatically approved.

## 5:00 — Release

Show security, dependency and container checks. Explain the private Azure Container Apps target and human deployment approval.

## 5:45 — Deploy and verify

Approve deployment. Show the smoke-test verification.

## 6:15 — Run Replay

Show audit timeline, token consumption, tool calls, self-healing count and success rate.

## Closing

"The differentiator is not code generation alone. AutoForge creates a governed feedback loop: understand → design → build → prove → recover → learn → secure → deploy, with human control at the critical gates."
