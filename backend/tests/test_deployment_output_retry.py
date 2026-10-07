import json
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock, patch

from app.agents.coder_agent import CoderAgent, CoderOutputError, CoderResult
from app.agents.deployment_contract import dependency_manifest_issues
from app.services.deployment_repair import repair_deployment


class DependencyChecks(unittest.TestCase):
    def test_cra_existing_tsx_without_typescript_setup_is_rejected(self):
        files = {
            "Dockerfile": "FROM node:22\nCOPY frontend/ /app/\nEXPOSE 8080\n",
            "frontend/package.json": json.dumps({"scripts": {"build": "react-scripts build"},
                "dependencies": {"react-scripts": "5.0.1", "react": "18.2.0"}}),
            "frontend/src/index.tsx": "import App from './App';",
            "frontend/src/App.tsx": "export default function App() { return null; }",
        }
        with self.assertRaisesRegex(ValueError, "tsconfig.json") as error:
            CoderAgent._validate_deployment_contract(files)
        self.assertIn("@types/react-dom", str(error.exception))
        # Shared Critic uses the same packaging checks, before publication.
        from app.agents.critic_agent import CriticAgent
        findings, checks = CriticAgent()._local_checks(files)
        self.assertEqual(checks["deployment_contract"], "Failed")
        self.assertTrue(any("tsconfig.json" in finding.issue for finding in findings))

    def test_cra_typed_setup_and_other_toolchains_are_supported(self):
        for build_tool in ("react-scripts", "vite", "next"):
            files = {"frontend/package.json": json.dumps({
                "scripts": {"build": build_tool + " build"},
                "devDependencies": {"react-scripts": "5.0.1", "typescript": "4.9.5",
                    "@types/react": "18.2.0", "@types/react-dom": "18.2.0"}}),
                "frontend/src/App.tsx": "export default () => null;"}
            if build_tool == "react-scripts":
                files["frontend/tsconfig.json"] = '{"compilerOptions":{"jsx":"react-jsx"}}'
            self.assertEqual(dependency_manifest_issues(files), [])

    def test_cra_javascript_and_type_declarations_do_not_require_ts_setup(self):
        files = {"package.json": json.dumps({"scripts": {"build": "react-scripts build"},
                    "dependencies": {"react-scripts": "5.0.1"}}),
                 "src/App.jsx": "export default () => null;", "src/react-app-env.d.ts": "types"}
        self.assertEqual(dependency_manifest_issues(files), [])

    def test_cra_build_tool_missing_with_lockfile_is_rejected(self):
        files = {
            "Dockerfile": "FROM node:22\nCOPY frontend/ /app/\nEXPOSE 8080\n",
            "frontend/package.json": json.dumps({
                "scripts": {"build": "react-scripts build"},
                "devDependencies": {"typescript": "5.1.6"}}),
            "frontend/package-lock.json": '{"lockfileVersion":3,"packages":{}}',
        }
        with self.assertRaisesRegex(ValueError, "neither dependencies nor devDependencies") as error:
            CoderAgent._validate_deployment_contract(files)
        self.assertIn("4.9.5", str(error.exception))
        self.assertEqual(files["frontend/package-lock.json"], '{"lockfileVersion":3,"packages":{}}')

    def test_cra_conflict_is_rejected_before_publication(self):
        files = {
            "Dockerfile": "FROM node:22\nCOPY frontend/ /app/\nEXPOSE 8080\n",
            "frontend/package.json": json.dumps({"devDependencies": {
                "react-scripts": "5.0.1", "typescript": "^5.1.6"}}),
        }
        with self.assertRaisesRegex(ValueError, "TypeScript"):
            CoderAgent._validate_deployment_contract(files)

    def test_compatible_and_other_toolchains_unchanged(self):
        for dependencies in (
            {"react-scripts": "5.0.1", "typescript": "4.9.5"},
            {"vite": "5.0.0", "typescript": "^5.1.6"},
        ):
            files = {"package.json": json.dumps({"devDependencies": dependencies})}
            before = dict(files)
            self.assertEqual(dependency_manifest_issues(files), [])
            self.assertEqual(files, before)


class OutputRetry(unittest.IsolatedAsyncioTestCase):
    async def test_unchanged_repair_keeps_original_failure_and_does_not_publish(self):
        build, store, callback = self.fixture()
        callback.diagnostics = "Module not found: Can't resolve './App' in '/app/frontend/src'"
        store._agent_service.run_coder_agent.return_value = CoderResult(
            files=dict(build.proof.artifacts), mode="foundry-agent")
        with patch("app.services.deployment_repair.GitHubPublisher.publish", new_callable=AsyncMock) as publish:
            await repair_deployment(store, build.id, callback)
        publish.assert_not_awaited()
        store._agent_service.run_critic_agent.assert_not_awaited()
        self.assertIn("Can't resolve './App'", build.error)
        self.assertTrue(build.deployment_repair_review["blockers"])
        self.assertEqual(build.proof.artifacts, {"app.py": "original"})
        self.assertEqual(store._agent_service.run_coder_agent.await_count, 3)

    async def test_unchanged_candidate_can_be_corrected_within_shared_budget(self):
        build, store, callback = self.fixture()
        store._agent_service.run_coder_agent.side_effect = [
            CoderResult(files={"app.py": "original"}, mode="foundry-agent"),
            CoderResult(files={"app.py": "corrected"}, mode="foundry-agent"),
        ]
        with patch("app.services.deployment_repair.GitHubPublisher.publish", new_callable=AsyncMock,
                   return_value={"commit_sha": "b" * 40}) as publish:
            await repair_deployment(store, build.id, callback)
        publish.assert_awaited_once()
        self.assertEqual(build.deployment_repair_attempts, 2)
        context = store._agent_service.run_coder_agent.call_args_list[1].kwargs
        self.assertTrue(any('unchanged files' in finding['issue'] for finding in context['repair_findings']))
        self.assertIn('ERESOLVE', context['repair_findings'][0]['issue'])

    def fixture(self):
        build = NS(id="example", title="Example", blueprint=NS(security=[], deployment="ACA", identity="OIDC"),
                   requirements=[], acceptance_criteria=[], proof=NS(artifacts={"app.py": "original"}),
                   deployment_repairing=True, deployment_commit="a" * 40, deployment_repair_attempts=1,
                   metrics=NS(tokens=0, tool_calls=0, self_heal_iterations=0))
        critic = NS(findings=[], checks={"syntax": "Passed"}, runtime_status="Passed", mode="review", summary="Reviewed")
        service = NS(run_coder_agent=AsyncMock(), run_critic_agent=AsyncMock(return_value=critic),
                     run_security_reviewer=AsyncMock(return_value=NS(findings=[], decision="Pass")))
        store = NS(get=Mock(return_value=build), _agent_service=service,
                   _set_agent=Mock(), _add_event=Mock(), _build_repository=NS(save=Mock()))
        callback = NS(commit_sha="a" * 40, phase="image_build", diagnostics="npm ERESOLVE")
        return build, store, callback

    async def test_invalid_packaging_retried_with_candidate_and_original_error(self):
        build, store, callback = self.fixture()
        store._agent_service.run_coder_agent.side_effect = [
            CoderOutputError("Missing frontend/yarn.lock", {"app.py": "candidate"}),
            CoderResult(files={"app.py": "corrected"}, mode="foundry-agent"),
        ]
        with patch("app.services.deployment_repair.GitHubPublisher.publish", new_callable=AsyncMock,
                   return_value={"commit_sha": "b" * 40}) as publish:
            await repair_deployment(store, build.id, callback)
            publish.assert_awaited_once()
        second = store._agent_service.run_coder_agent.call_args_list[1].kwargs
        self.assertEqual(second["previous_artifacts"]["app.py"], "candidate")
        self.assertIn("ERESOLVE", second["repair_findings"][0]["issue"])
        self.assertIn("yarn.lock", second["repair_findings"][-1]["issue"])
        self.assertEqual(build.deployment_repair_attempts, 2)
        self.assertEqual(build.proof.artifacts["app.py"], "corrected")
        self.assertEqual(build.deployment_status, "running")

    async def test_invalid_output_stops_at_budget_without_publishing(self):
        build, store, callback = self.fixture()
        store._agent_service.run_coder_agent.side_effect = CoderOutputError("Missing yarn.lock")
        with patch("app.services.deployment_repair.GitHubPublisher.publish", new_callable=AsyncMock) as publish:
            await repair_deployment(store, build.id, callback)
            publish.assert_not_awaited()
        self.assertEqual(store._agent_service.run_coder_agent.await_count, 3)
        self.assertEqual(build.deployment_repair_attempts, 3)
        self.assertEqual(build.deployment_status, "failed")
        self.assertFalse(build.deployment_repairing)
        self.assertEqual(build.proof.artifacts, {"app.py": "original"})
        self.assertTrue(any(call.args[1:3] == ("Deployer Agent", "Failed")
                            for call in store._set_agent.call_args_list))

    async def test_transport_errors_are_not_retried_as_source_errors(self):
        build, store, callback = self.fixture()
        store._agent_service.run_coder_agent.side_effect = RuntimeError("Foundry unavailable")
        await repair_deployment(store, build.id, callback)
        self.assertEqual(store._agent_service.run_coder_agent.await_count, 1)
        self.assertEqual(build.deployment_status, "failed")

    async def test_critic_then_packaging_rejection_preserves_both_findings(self):
        build, store, callback = self.fixture()
        finding = NS(severity="Critical", model_dump=lambda: {
            "severity": "Critical", "file": "app.py", "issue": "Mock authentication", "recommendation": "Validate identity"})
        passed = store._agent_service.run_critic_agent.return_value
        rejected = NS(findings=[finding], checks={}, runtime_status="Passed")
        store._agent_service.run_critic_agent.side_effect = [rejected, passed]
        store._agent_service.run_coder_agent.side_effect = [
            CoderResult(files={"app.py": "first"}, mode="foundry-agent"),
            CoderOutputError("Missing yarn.lock", {"app.py": "second"}),
            CoderResult(files={"app.py": "third"}, mode="foundry-agent"),
        ]
        with patch("app.services.deployment_repair.GitHubPublisher.publish", new_callable=AsyncMock,
                   return_value={"commit_sha": "b" * 40}):
            await repair_deployment(store, build.id, callback)
        third = store._agent_service.run_coder_agent.call_args_list[2].kwargs
        issues = " ".join(item["issue"] for item in third["repair_findings"])
        for detail in ("ERESOLVE", "Mock authentication", "yarn.lock"):
            self.assertIn(detail, issues)
        self.assertEqual(third["previous_artifacts"]["app.py"], "second")
        self.assertEqual(build.deployment_repair_attempts, 3)
        self.assertEqual(build.deployment_status, "running")
