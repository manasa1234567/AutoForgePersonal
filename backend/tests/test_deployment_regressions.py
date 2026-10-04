import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.coder_agent import CoderAgent, CoderResult
from app.agents.critic_agent import CriticAgent, CriticResult
from app.agents.deployment_contract import missing_copy_sources
from app.models.schemas import Blueprint, BuildCreate, CriticFinding, ProofResult, SecurityReview
from app.repositories.build_repository import InMemoryBuildRepository
from app.services.orchestrator import Orchestrator


class SnapshotRepository(InMemoryBuildRepository):
    def save(self, build):
        super().save(build.model_copy(deep=True))

    def get(self, build_id):
        return super().get(build_id).model_copy(deep=True)


def blueprint():
    return Blueprint(application="Hello", frontend="React", backend="FastAPI",
                     data="None", storage="None", messaging="None", identity="None",
                     deployment="Container Apps", security=[], reasoning=[])


class DeploymentRegressions(unittest.TestCase):
    def test_multistage_copy_can_relocate_uvicorn_module(self):
        artifacts = {
            "Dockerfile": '''FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend
COPY backend/ ./
RUN pip install -r requirements.txt
FROM python:3.11-slim
WORKDIR /app
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app/backend/ .
RUN pip install uvicorn fastapi
EXPOSE 8080
CMD ["uvicorn", "main:app", "--app-dir", "./", "--port", "8080"]
''',
            "backend/main.py": "app = None\n",
            "backend/requirements.txt": "fastapi\nuvicorn\n",
        }
        findings, checks = CriticAgent()._local_checks(artifacts)
        self.assertEqual(checks["deployment_contract"], "Passed", findings)

    def test_virtualenv_copy_is_not_assumed_to_lose_dependencies(self):
        artifacts = {
            "Dockerfile": "FROM python:3.11-slim\nCOPY --from=deps /opt/venv /opt/venv\nEXPOSE 8080\n",
            "requirements.txt": "fastapi\n",
        }
        _, checks = CriticAgent()._local_checks(artifacts)
        self.assertEqual(checks["deployment_contract"], "Passed")

    def test_real_source_and_packaging_errors_still_block(self):
        findings, checks = CriticAgent()._local_checks({
            "Dockerfile": "FROM python:3.11-slim\nEXPOSE 8000\n",
            "main.py": "def broken(:\n",
        })
        self.assertEqual(checks["deployment_contract"], "Failed")
        self.assertEqual(checks["python_syntax"], "Failed")
        self.assertTrue(findings)

    def test_missing_explicit_manifest_is_caught_before_docker_build(self):
        artifacts = {"Dockerfile": "FROM node:22\nCOPY frontend/package.json frontend/package-lock.json* ./\nEXPOSE 8080\n"}
        self.assertEqual(missing_copy_sources(artifacts), ["frontend/package.json"])
        with self.assertRaisesRegex(ValueError, "frontend/package.json"):
            CoderAgent._validate_deployment_contract(artifacts)
        findings, checks = CriticAgent()._local_checks(artifacts)
        self.assertEqual(checks["deployment_contract"], "Failed")
        self.assertIn("frontend/package.json", findings[0].issue)

    def test_json_copy_flags_directories_and_dynamic_paths(self):
        artifacts = {
            "Dockerfile": '''FROM example
COPY --chown=1000:1000 ["frontend/package.json", "/app/package.json"]
COPY frontend/ /app/
COPY . .
COPY ${SOURCE} /app/
COPY --from=builder /generated /app/
EXPOSE 8080
''',
            "frontend/package.json": "{}",
        }
        self.assertEqual(missing_copy_sources(artifacts), [])

    def test_partial_repair_preserves_manifest_and_updates_changed_file(self):
        previous = {"frontend/package.json": "{}", "backend/main.py": "old = True"}
        result = CoderAgent._merge_repair_files(
            {"files": [{"path": "backend/main.py", "content": "new = True"}]}, previous
        )
        self.assertEqual(result, {"frontend/package.json": "{}", "backend/main.py": "new = True"})

    def test_merged_repairs_still_obey_total_size_limit(self):
        with patch.object(CoderAgent, "max_total_bytes", 10):
            with self.assertRaisesRegex(ValueError, "total source size"):
                CoderAgent._merge_repair_files(
                    {"files": [{"path": "b.txt", "content": "123456"}]}, {"a.txt": "123456"}
                )

    def test_static_failure_banner_reports_finding_not_sandbox_configuration(self):
        async def scenario():
            store = Orchestrator(build_repository=SnapshotRepository())
            build = store.create(BuildCreate(source_type="usecase", title="Hello", source_text="Hello page"))
            build.blueprint = blueprint()
            build.proof = ProofResult(artifacts={"Dockerfile": "FROM node:22"}, generator_mode="local-scaffold")
            finding = CriticFinding(severity="Critical", file="Dockerfile", issue="Missing frontend/package.json", recommendation="Include manifest")
            store._agent_service.run_critic_agent = AsyncMock(return_value=CriticResult(
                summary="Static failure", findings=[finding], requirement_coverage=[], test_plan=[],
                checks={"deployment_contract": "Failed"},
                runtime_status="Not run: static safety checks must pass before sandbox execution", mode="local-static-review"
            ))
            await store._prove(build)
            saved = store.get(build.id)
            self.assertEqual(saved.status, "Blocked")
            self.assertIn("frontend/package.json", saved.error)
            self.assertNotIn("configured and enabled", saved.error)
        asyncio.run(scenario())

    def test_security_review_reload_keeps_repaired_critic_result(self):
        async def scenario():
            store = Orchestrator(build_repository=SnapshotRepository())
            build = store.create(BuildCreate(source_type="usecase", title="Hello", source_text="Hello page"))
            build.blueprint = blueprint()
            build.proof = ProofResult(artifacts={"app.py": "old = True"}, generator_mode="foundry-agent", runtime_status="Old result")
            store._build_repository.save(build)
            store._agent_service.run_coder_agent = AsyncMock(return_value=CoderResult(files={"app.py": "fixed = True"}, mode="foundry-agent"))
            store._agent_service.run_critic_agent = AsyncMock(return_value=CriticResult(
                summary="Repaired", findings=[], requirement_coverage=[], test_plan=[],
                checks={"deployment_contract": "Passed"}, runtime_status="Passed: repaired", mode="local-static-review"
            ))
            async def reload_review(build_id):
                saved = store.get(build_id)
                self.assertEqual(saved.proof.runtime_status, "Passed: repaired")
                self.assertEqual(saved.proof.artifacts, {"app.py": "fixed = True"})
                return SecurityReview(decision="No high or critical findings", summary="Passed")
            store.run_security_review = reload_review
            review, saved, repaired = await store._repair_security_findings(
                build, SecurityReview(decision="Block release", summary="Needs repair"), repair_limit=2
            )
            self.assertTrue(repaired)
            self.assertEqual(review.decision, "No high or critical findings")
            self.assertEqual(saved.proof.runtime_status, "Passed: repaired")
        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
