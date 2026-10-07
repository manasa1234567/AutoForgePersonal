import asyncio
import unittest
from unittest.mock import AsyncMock

from app.agents.coder_agent import CoderResult
from app.models.schemas import BuildCreate, Blueprint, ProofResult
from app.repositories.build_repository import InMemoryBuildRepository
from app.services.orchestrator import Orchestrator


class ForgeResume(unittest.IsolatedAsyncioTestCase):
    def fixture(self):
        store = Orchestrator(build_repository=InMemoryBuildRepository())
        build = store.create(BuildCreate(source_type='usecase', title='Example', source_text='Build an app'))
        build.blueprint = Blueprint(application='Example', frontend='React', backend='FastAPI', data='None',
                                    storage='None', messaging='None', identity='None', deployment='ACA', security=[], reasoning=[])
        build.status = 'Failed'
        build.progress = 58
        build.stage = 'Error'
        build.generation_failure = {'artifacts': {'app.py': 'original'}, 'issue': 'Missing manifest'}
        store._add_event(build, 'Approval', 'Human approved blueprint', 'User', metadata={'gate': 'blueprint'})
        store._build_repository.save(build)
        return store, build

    async def test_retry_reuses_approved_build_and_does_not_duplicate_worker(self):
        store, build = self.fixture()
        store._complete_approval = AsyncMock()
        result = await store.retry_forge(build.id)
        await store.retry_forge(build.id)
        await asyncio.sleep(0)
        store._complete_approval.assert_awaited_once_with(build.id, 'blueprint')
        self.assertEqual(result.id, build.id)
        self.assertEqual(result.status, 'Running')
        self.assertEqual(result.audit[-1].stage, 'Retry')

    async def test_approved_blueprint_and_unapproved_candidate_remain_separate(self):
        store, build = self.fixture()
        store._agent_service.run_coder_agent = AsyncMock(return_value=CoderResult(
            files={'app.py': 'original', 'requirements.txt': 'fastapi'}, mode='foundry-agent'))
        await store._forge(build)
        call = store._agent_service.run_coder_agent.call_args.kwargs
        self.assertEqual(call['previous_artifacts'], {'app.py': 'original'})
        self.assertEqual(call['repair_findings'][0]['issue'], 'Missing manifest')
        self.assertEqual(build.generation_failure, {})
        self.assertEqual(build.proof.artifacts['app.py'], 'original')
        self.assertEqual(build.approval_gate, 'artifacts')

    async def test_retry_requires_original_blueprint_approval_and_saved_candidate(self):
        for defect in ('unapproved', 'no_candidate', 'already_proved', 'later_stage'):
            store, build = self.fixture()
            if defect == 'unapproved': build.audit = []
            elif defect == 'no_candidate': build.generation_failure = {}
            elif defect == 'already_proved': build.proof = ProofResult()
            else: build.progress = 96
            store._build_repository.save(build)
            with self.assertRaises(ValueError):
                await store.retry_forge(build.id)
