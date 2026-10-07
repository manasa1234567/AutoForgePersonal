import asyncio
from io import BytesIO
import json
import unittest
from unittest.mock import AsyncMock, Mock
import zipfile
from types import SimpleNamespace, ModuleType
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.schemas import BuildState, ProofResult
from app.repositories.build_repository import InMemoryBuildRepository
from app.repositories.azure_repositories import AzureBuildRepository
from app.services.ui_preview import (OfflinePreviewAgent, PreviewError, PreviewService,
                                    preview_artifacts, preview_digest, validate_preview, wrap_preview)
from app.services.preview_archive import preview_zip

BODY = '''<!doctype html><html><head><style>body{font-family:system-ui;background:#edf5ff}button{padding:12px}</style></head><body><h1>Tasks</h1><button id="add">Add task</button><output id="count">0</output><script>var count=0;document.getElementById('add').onclick=function(){count++;document.getElementById('count').textContent=String(count);};</script></body></html>'''


def fixture():
    return BuildState(id='example', title='Example <script>', source_type='usecase', source_text='Build tasks', files=[],
                      proof=ProofResult(artifacts={'frontend/index.html': BODY, 'backend/main.py': 'app = None',
                                                  'tests/test_app.py': 'def test_app(): pass'}))


class PreviewValidation(unittest.TestCase):
    def test_standalone_script_is_valid_and_title_is_escaped(self):
        self.assertEqual(validate_preview(BODY), BODY)
        result = wrap_preview('Example <script>', BODY)
        self.assertIn('Example &lt;script&gt;', result)
        self.assertIn('sandbox="allow-scripts allow-downloads"', result)
        self.assertNotIn('allow-same-origin', result)
        self.assertIn('connect-src &#x27;none&#x27;', result)
        self.assertIn('Sample data only', result)

    def test_external_modules_and_invalid_javascript_are_rejected(self):
        for body in (
            '<html><body><script src="https://cdn.example/react.js"></script></body></html>',
            '<html><body><script type="module">import x from "./x.js"</script></body></html>',
            '<html><body><iframe src="https://example.test"></iframe></body></html>',
            '<html><body><script>var = broken;</script></body></html>',
            '<html><body><script>fetch("/api/data");</script></body></html>',
        ):
            with self.assertRaises(PreviewError):
                validate_preview(body)

    def test_digest_invalidates_on_source_change(self):
        build = fixture()
        old = preview_digest(build, build.proof.artifacts)
        new = preview_digest(build, {**build.proof.artifacts, 'frontend/style.css': 'body{color:red}'})
        self.assertNotEqual(old, new)

    def test_rejected_candidate_is_exportable_without_claiming_proof(self):
        build = fixture()
        build.generation_failure = {'artifacts': build.proof.artifacts}
        build.proof = None
        self.assertIn('frontend/index.html', preview_artifacts(build))

    def test_blob_preview_addition_keeps_deployment_claim_boolean_contract(self):
        repository = AzureBuildRepository.__new__(AzureBuildRepository)
        repository._snapshots = Mock()
        self.assertTrue(repository.claim_deployment_repair('example', 'commit'))
        error = RuntimeError('exists')
        error.status_code = 409
        repository._snapshots.upload_blob.side_effect = error
        self.assertFalse(repository.claim_deployment_repair('example', 'commit'))


class PreviewExport(unittest.IsolatedAsyncioTestCase):
    async def test_framework_preview_validates_and_corrects_model_output_once(self):
        agent = SimpleNamespace(run=AsyncMock(side_effect=[
            json.dumps({'html': '<html><body><script src="/bundle.js"></script></body></html>'}),
            json.dumps({'html': BODY}),
        ]))
        framework = ModuleType('agent_framework')
        framework.Agent = Mock(return_value=agent)
        foundry = ModuleType('agent_framework.foundry')
        foundry.FoundryChatClient = Mock()
        identity = ModuleType('azure.identity')
        credential = Mock()
        identity.DefaultAzureCredential = Mock(return_value=credential)
        identity.ManagedIdentityCredential = Mock(return_value=credential)
        build = fixture()
        artifacts = {**build.proof.artifacts, 'frontend/src/App.tsx': 'export default () => null;'}
        with patch.dict('sys.modules', {'agent_framework': framework, 'agent_framework.foundry': foundry,
                                      'azure.identity': identity}), \
             patch.dict('os.environ', {'FOUNDRY_PROJECT_ENDPOINT': 'https://example.test', 'FOUNDRY_CODER_MODEL': 'test'}):
            result = await OfflinePreviewAgent().generate(build, artifacts)
        self.assertEqual(agent.run.await_count, 2)
        self.assertIn('Add task', result)
        context = json.loads(agent.run.call_args_list[1].args[0])
        self.assertIn('previewValidationIssue', context)
        credential.close.assert_called_once()

    async def test_angular_entry_shell_is_not_presented_as_a_working_static_ui(self):
        build = fixture()
        artifacts = {'frontend/index.html': '<html><body><app-root></app-root></body></html>',
                     'frontend/package.json': '{"dependencies":{"@angular/core":"20.0.0"}}'}
        with patch.dict('os.environ', {'FOUNDRY_PROJECT_ENDPOINT': '', 'FOUNDRY_CODER_MODEL': ''}):
            with self.assertRaises(PreviewError):
                await OfflinePreviewAgent().generate(build, artifacts)

    async def test_static_ui_and_zip_work_without_model_and_preserve_every_source_file(self):
        build = fixture()
        repository = InMemoryBuildRepository()
        repository.save(build)
        service = PreviewService(repository)
        before = build.model_dump()
        body = await service.html(build, build.proof.artifacts)
        self.assertIn('Add task', body)
        chunks = [chunk async for chunk in preview_zip(build, build.proof.artifacts, service, heartbeat=.01)]
        with zipfile.ZipFile(BytesIO(b''.join(chunks))) as archive:
            self.assertIsNone(archive.testzip())
            for path, content in build.proof.artifacts.items():
                self.assertEqual(archive.read(path).decode(), content)
            self.assertIn('preview.html', archive.namelist())
            self.assertIn('PREVIEW_README.md', archive.namelist())
            self.assertIn('Add task', archive.read('preview.html').decode())
        self.assertEqual(build.model_dump(), before)
        self.assertEqual((await service.status(build, build.proof.artifacts))['status'], 'ready')

    async def test_model_failure_does_not_break_zip_or_change_build(self):
        build = fixture()
        agent = Mock()
        agent.generate = AsyncMock(side_effect=PreviewError('Model unavailable'))
        service = PreviewService(InMemoryBuildRepository(), agent)
        chunks = [chunk async for chunk in preview_zip(build, build.proof.artifacts, service, heartbeat=.01)]
        with zipfile.ZipFile(BytesIO(b''.join(chunks))) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn('Preview unavailable', archive.read('preview.html').decode())
            self.assertEqual(archive.read('backend/main.py').decode(), 'app = None')

    async def test_cached_preview_avoids_regeneration_and_source_change_gets_new_preview(self):
        build = fixture()
        agent = Mock()
        agent.generate = AsyncMock(return_value=wrap_preview(build.title, BODY))
        service = PreviewService(InMemoryBuildRepository(), agent)
        await service.html(build, build.proof.artifacts)
        await service.html(build, build.proof.artifacts)
        self.assertEqual(agent.generate.await_count, 1)
        await service.html(build, {**build.proof.artifacts, 'extra.txt': 'new snapshot'})
        self.assertEqual(agent.generate.await_count, 2)

    async def test_archive_heartbeats_are_valid_zip_data_and_name_collision_is_preserved(self):
        build = fixture()
        files = {**build.proof.artifacts, 'Preview.html': 'original preview', '../escape.txt': 'unsafe'}
        class SlowPreview:
            async def html(self, *args):
                await asyncio.sleep(.04)
                return wrap_preview('Example', BODY)
        chunks = [chunk async for chunk in preview_zip(build, files, SlowPreview(), heartbeat=.005)]
        with zipfile.ZipFile(BytesIO(b''.join(chunks))) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read('Preview.html').decode(), 'original preview')
            self.assertIn('preview-1.html', archive.namelist())
            self.assertNotIn('../escape.txt', archive.namelist())
            self.assertTrue(archive.read('preview-1.html').startswith(b'\n'))


class PreviewRoutes(unittest.TestCase):
    def test_open_preview_status_and_zip_routes_share_cached_content(self):
        from app.routers import builds
        build = fixture()
        repository = InMemoryBuildRepository()
        repository.save(build)
        service = PreviewService(repository)
        repository.save_preview(build.id, preview_digest(build, build.proof.artifacts),
                                {'status': 'ready', 'html': wrap_preview(build.title, BODY)})
        app = FastAPI()
        app.include_router(builds.router)
        with patch.object(builds, 'store', SimpleNamespace(get=repository.get)), \
             patch.object(builds, 'previews', service), TestClient(app) as client:
            page = client.get('/api/builds/example/preview')
            self.assertEqual(page.status_code, 200)
            self.assertIn('Preparing UI preview', page.text)
            self.assertIn("connect-src 'self'", page.headers['content-security-policy'])
            self.assertEqual(client.get('/api/builds/example/preview/status').json(), {'status': 'ready'})
            body = client.get('/api/builds/example/preview/content')
            self.assertEqual(body.status_code, 200)
            self.assertIn("connect-src 'none'", body.headers['content-security-policy'])
            result = client.get('/api/builds/example/artifacts.zip')
            self.assertEqual(result.status_code, 200)
            with zipfile.ZipFile(BytesIO(result.content)) as archive:
                self.assertEqual(archive.read('preview.html').decode(), body.text)
            self.assertEqual(client.get('/api/builds/missing/preview').status_code, 404)
