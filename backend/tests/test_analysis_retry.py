import unittest
from unittest.mock import AsyncMock

from app.models.schemas import BuildCreate
from app.repositories.build_repository import InMemoryBuildRepository
from app.services.orchestrator import Orchestrator


class AnalysisRetry(unittest.IsolatedAsyncioTestCase):
    def fixture(self, error='Azure Prompt Shields check failed (HTTP 408); analysis stopped'):
        dispatcher = AsyncMock()
        store = Orchestrator(build_repository=InMemoryBuildRepository(), job_dispatcher=dispatcher)
        build = store.create(BuildCreate(source_type='usecase', title='Example', source_text='Build an app'))
        build.status = 'Failed'
        build.stage = 'Error'
        build.error = error
        store._build_repository.save(build)
        return store, dispatcher, build

    async def test_transient_failure_retries_existing_build_once(self):
        store, dispatcher, original = self.fixture()
        result = await store.start(original.id)
        await store.start(original.id)
        dispatcher.enqueue.assert_awaited_once_with(original.id)
        self.assertEqual(result.status, 'Running')
        self.assertIsNone(result.error)
        self.assertEqual(result.source_text, original.source_text)
        self.assertEqual(result.audit[-1].stage, 'Retry')
        # The worker still runs the required safety check, not just the model.
        store._azure.content_safety_check = AsyncMock(side_effect=RuntimeError('safety unavailable'))
        await store._run_until_gate(original.id)
        store._azure.content_safety_check.assert_awaited_once()
        self.assertEqual(store.get(original.id).status, 'Failed')

    async def test_auth_attack_and_later_failures_are_not_restarted(self):
        for error, progress in (
            ('Azure Prompt Shields check failed (HTTP 401); analysis stopped', 0),
            ('Azure Prompt Shields detected a prompt injection attempt', 0),
            ('Azure Prompt Shields check failed (HTTP 408); analysis stopped', 58),
        ):
            store, dispatcher, build = self.fixture(error)
            build.progress = progress
            store._build_repository.save(build)
            await store.start(build.id)
            dispatcher.enqueue.assert_not_awaited()

    async def test_queue_failure_does_not_leave_build_running(self):
        store, dispatcher, build = self.fixture()
        dispatcher.enqueue.side_effect = RuntimeError('queue unavailable')
        with self.assertRaisesRegex(RuntimeError, 'queue unavailable'):
            await store.start(build.id)
        self.assertEqual(store.get(build.id).status, 'Failed')

    async def test_initial_start_is_also_deduplicated(self):
        store, dispatcher, build = self.fixture()
        build.status = 'Draft'
        store._build_repository.save(build)
        await store.start(build.id)
        await store.start(build.id)
        dispatcher.enqueue.assert_awaited_once()
