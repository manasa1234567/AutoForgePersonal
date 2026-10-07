import asyncio
import unittest
from unittest.mock import AsyncMock

from app.agents.critic_agent import CriticResult
from app.models.schemas import BuildCreate, Blueprint, ProofResult
from app.repositories.build_repository import InMemoryBuildRepository
from app.services.orchestrator import Orchestrator


class ReviewRetry(unittest.IsolatedAsyncioTestCase):
    def fixture(self):
        store = Orchestrator(build_repository=InMemoryBuildRepository())
        build = store.create(BuildCreate(source_type='usecase', title='Example', source_text='Build app'))
        build.blueprint = Blueprint(application='Example', frontend='React', backend='FastAPI', data='None',
                                    storage='None', messaging='None', identity='None', deployment='ACA', security=[], reasoning=[])
        build.proof = ProofResult(artifacts={'app.py': 'original source'}, generator_mode='foundry-agent',
                                  critic_mode='foundry-review-evidence-invalid')
        build.status = 'Blocked'
        build.stage = 'Prove'
        build.progress = 72
        store._add_event(build, 'Approval', 'Approved artifacts', 'User', metadata={'gate': 'artifacts'})
        store._build_repository.save(build)
        return store, build

    async def test_retry_preserves_approved_source_and_runs_one_review_worker(self):
        store, build = self.fixture()
        store._complete_approval = AsyncMock()
        result = await store.retry_review(build.id)
        await store.retry_review(build.id)
        await asyncio.sleep(0)
        store._complete_approval.assert_awaited_once_with(build.id, 'artifacts')
        self.assertEqual(result.proof.artifacts, {'app.py': 'original source'})
        self.assertEqual(result.status, 'Running')
        self.assertEqual(result.audit[-1].stage, 'Retry')

    async def test_retry_rejects_unapproved_artifacts_and_unrelated_source_blockers(self):
        for reason in ('no_approval', 'static_error', 'wrong_stage'):
            store, build = self.fixture()
            if reason == 'no_approval': build.audit = []
            elif reason == 'static_error': build.proof.critic_mode = 'local-static-review'
            else: build.progress = 58
            store._build_repository.save(build)
            with self.assertRaises(ValueError):
                await store.retry_review(build.id)

    async def test_reviewer_failure_is_reported_precisely_without_coder_rewrites(self):
        store, build = self.fixture()
        store._agent_service.run_coder_agent = AsyncMock()
        store._agent_service.run_critic_agent = AsyncMock(return_value=CriticResult(
            summary='Review evidence invalid', findings=[], requirement_coverage=[], test_plan=[],
            checks={'artifact_paths': 'Passed', 'foundry_source_review': 'Failed: unsubstantiated review evidence',
                    'foundry_review_evidence_issues': 'Unknown artifact path: src/madeup.py'},
            runtime_status='Not run: review must be substantiated', mode='foundry-review-evidence-invalid'))
        await store._prove(build)
        store._agent_service.run_coder_agent.assert_not_awaited()
        saved = store.get(build.id)
        self.assertEqual(saved.status, 'Blocked')
        self.assertIn('Unknown artifact path', saved.error)
        self.assertIn('Retry source review', saved.error)
        self.assertNotIn('static safety', saved.error)
        self.assertEqual(saved.proof.artifacts, {'app.py': 'original source'})
