import unittest
import asyncio
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import httpx

from app.services.azure_adapters import AzureAdapters


def response(status=200, attack=False, headers=None):
    return httpx.Response(status, headers=headers, request=httpx.Request('POST', 'https://example.test/shield'),
        json={'userPromptAnalysis': {'attackDetected': False},
              'documentsAnalysis': [{'attackDetected': attack}]})


class PromptShieldsRetry(unittest.IsolatedAsyncioTestCase):
    async def check(self, responses, text='engineering request', input_kind='document'):
        credential = SimpleNamespace(get_token=AsyncMock(return_value=SimpleNamespace(token='test')),
                                     close=AsyncMock())
        identity = ModuleType('azure.identity.aio')
        identity.DefaultAzureCredential = Mock(return_value=credential)
        identity.ManagedIdentityCredential = Mock(return_value=credential)
        client = AsyncMock()
        client.post.side_effect = responses
        client.__aenter__.return_value = client
        self.client = client
        self.credential = credential
        with patch.dict('sys.modules', {'azure.identity.aio': identity}), \
             patch('app.services.azure_adapters.httpx.AsyncClient', return_value=client), \
             patch('app.services.azure_adapters.asyncio.sleep', new_callable=AsyncMock) as sleep:
            self.sleep = sleep
            return await AzureAdapters()._prompt_shields_check('https://example.test', text, input_kind=input_kind)

    async def test_direct_input_is_analyzed_as_user_prompt(self):
        await self.check([response()], 'Build a task list', input_kind='user_prompt')
        payload = self.client.post.call_args.kwargs['json']
        self.assertEqual(payload, {'userPrompt': 'Build a task list', 'documents': []})

    async def test_document_input_retains_indirect_attack_detection(self):
        result = await self.check([response(attack=True)], 'External source', input_kind='document')
        self.assertTrue(result['blocked'])
        self.assertEqual(self.client.post.call_args.kwargs['json']['documents'], ['External source'])

    async def test_empty_analysis_is_never_accepted(self):
        reply = httpx.Response(200, request=httpx.Request('POST', 'https://example.test'), json={})
        with self.assertRaisesRegex(RuntimeError, 'RuntimeError'):
            await self.check([reply])

    async def test_missing_document_analysis_is_never_accepted(self):
        reply = httpx.Response(200, request=httpx.Request('POST', 'https://example.test'),
                              json={'userPromptAnalysis': {'attackDetected': False}})
        with self.assertRaises(RuntimeError):
            await self.check([reply], input_kind='document')

    async def test_timeout_error_includes_mode_attempts_and_correlation_id(self):
        with self.assertRaisesRegex(RuntimeError, 'request ID request-123, 3 attempt.*mode user_prompt'):
            await self.check([response(408, headers={'apim-request-id': 'request-123'}) for _ in range(3)],
                             input_kind='user_prompt')

    async def test_408_retries_same_input_then_accepts(self):
        result = await self.check([response(408), response()])
        self.assertFalse(result['blocked'])
        self.assertEqual(self.client.post.await_count, 2)
        self.assertEqual(self.client.post.call_args_list[0], self.client.post.call_args_list[1])
        self.credential.close.assert_awaited_once()

    async def test_attack_after_transient_failure_still_blocks(self):
        result = await self.check([response(503), response(attack=True)])
        self.assertTrue(result['blocked'])

    async def test_exhausted_408_stops_analysis(self):
        with self.assertRaisesRegex(RuntimeError, 'HTTP 408'):
            await self.check([response(408)] * 3)
        self.assertEqual(self.client.post.await_count, 3)
        self.assertEqual(self.sleep.await_count, 2)
        self.credential.close.assert_awaited_once()

    async def test_auth_and_input_errors_are_not_retried(self):
        for status in (400, 401, 403, 404):
            with self.assertRaisesRegex(RuntimeError, f'HTTP {status}'):
                await self.check([response(status)])
            self.assertEqual(self.client.post.await_count, 1)
            self.sleep.assert_not_awaited()

    async def test_network_timeout_retries(self):
        result = await self.check([httpx.ReadTimeout('timeout'), response()])
        self.assertFalse(result['blocked'])

    async def test_later_chunk_failure_never_accepts_partial_scan(self):
        with self.assertRaisesRegex(RuntimeError, 'HTTP 408'):
            await self.check([response(), response(408), response(408), response(408)], 'x' * 10000)
        self.assertEqual(self.client.post.await_count, 4)

    async def test_rate_limit_delay_is_bounded(self):
        await self.check([response(429, headers={'Retry-After': '120'}), response()])
        self.sleep.assert_awaited_once_with(10.0)


class SafetyInputRouting(unittest.TestCase):
    def test_direct_requests_and_external_documents_use_distinct_detectors(self):
        from app.models.schemas import BuildCreate
        from app.repositories.build_repository import InMemoryBuildRepository
        from app.services.orchestrator import Orchestrator
        async def scenario():
            for source_type, files, expected in (
                ('usecase', [], 'user_prompt'), ('requirement', [], 'user_prompt'),
                ('usecase', ['requirements.pdf'], 'document'), ('openapi', [], 'document'),
            ):
                store = Orchestrator(build_repository=InMemoryBuildRepository())
                build = store.create(BuildCreate(source_type=source_type, title='Routing test',
                                                source_text='Build an application', files=files))
                store._azure.content_safety_check = AsyncMock(side_effect=RuntimeError('probe'))
                with self.assertRaisesRegex(RuntimeError, 'probe'):
                    await store._understand(build)
                store._azure.content_safety_check.assert_awaited_once_with(build.source_text, input_kind=expected)
        asyncio.run(scenario())
