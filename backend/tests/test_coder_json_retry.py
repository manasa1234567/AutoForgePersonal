import json
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from app.agents.coder_agent import CoderAgent, CoderOutputError


class CoderJsonRetry(unittest.IsolatedAsyncioTestCase):
    async def generate(self, responses, retry=True, frontend="", previous=None, findings=None):
        agent = SimpleNamespace(run=AsyncMock(side_effect=responses))
        framework = ModuleType("agent_framework")
        framework.Agent = Mock(return_value=agent)
        foundry = ModuleType("agent_framework.foundry")
        foundry.FoundryChatClient = Mock()
        identity = ModuleType("azure.identity")
        credential = Mock()
        identity.DefaultAzureCredential = Mock(return_value=credential)
        identity.ManagedIdentityCredential = Mock(return_value=credential)
        self.agent = agent
        self.framework = framework
        self.credential = credential
        with patch.dict("sys.modules", {"agent_framework": framework,
                        "agent_framework.foundry": foundry, "azure.identity": identity}), \
                patch.dict("os.environ", {"FOUNDRY_PROJECT_ENDPOINT": "https://example.test", "FOUNDRY_MODEL": "test"}):
            return await CoderAgent()._generate_with_foundry(
                title="Example", blueprint=SimpleNamespace(frontend=frontend, model_dump=lambda **kw: {"frontend": frontend}),
                requirements=[], acceptance_criteria=[], skills=[], retry_packaging=retry,
                previous_artifacts=previous, repair_findings=findings)

    async def test_bad_json_gets_one_complete_regeneration(self):
        valid = json.dumps({"files": [{"path": "Dockerfile", "content": "FROM nginx\nEXPOSE 8080\n"}]})
        result = await self.generate(['{"files": [], bad}', valid])
        self.assertIn("Dockerfile", result.files)
        self.assertEqual(self.agent.run.await_count, 2)
        context = json.loads(self.agent.run.call_args_list[1].args[0])
        self.assertIn("Expecting property name", context["criticAndSandboxFindings"][0]["issue"])
        self.credential.close.assert_called_once()

    async def test_complete_source_gets_focused_configuration_completion(self):
        files = {
            "Dockerfile": "FROM python:3.11\nCOPY backend/pyproject.toml ./\nCOPY backend/ ./backend\nEXPOSE 8080\n",
            "backend/main.py": "from fastapi import FastAPI\napp = FastAPI()\n",
            "frontend/package.json": json.dumps({"scripts": {"build": "react-scripts build"},
                "dependencies": {"react": "18.2.0", "react-dom": "18.2.0", "react-scripts": "5.0.1"}}),
            "frontend/src/App.tsx": "export default function App() { return <h1>Application</h1>; }",
            "frontend/tsconfig.json": '{"compilerOptions":{"jsx":"react-jsx"}}',
        }
        manifest = json.loads(files["frontend/package.json"])
        manifest['devDependencies'] = {'typescript': '4.9.5', '@types/react': '^18.0.0', '@types/react-dom': '^18.0.0'}
        package_files = {'frontend/package.json': json.dumps(manifest),
            'backend/pyproject.toml': '[tool.poetry]\nname="service"\nversion="0.1.0"\npackage-mode=false\n'}
        def response(artifacts):
            return json.dumps({'files': [{'path': p, 'content': c} for p, c in artifacts.items()]})
        result = await self.generate([response(files), response(package_files)], frontend='React')
        self.assertEqual(self.agent.run.await_count, 2)
        self.assertEqual(self.framework.Agent.call_args_list[1].kwargs['name'], 'Packaging Agent')
        self.assertEqual(result.files['backend/main.py'], files['backend/main.py'])
        self.assertEqual(result.files['frontend/src/App.tsx'], files['frontend/src/App.tsx'])
        self.assertIn('backend/pyproject.toml', result.files)
        context = json.loads(self.agent.run.call_args_list[1].args[0])
        self.assertIn('TypeScript', context['packagingDiagnostics'])
        self.assertIn('backend/pyproject.toml', context['packagingDiagnostics'])

    def test_packaging_pass_cannot_replace_application_or_invent_locks(self):
        for path in ('src/main.py', 'frontend/src/App.tsx', 'poetry.lock', 'package-lock.json'):
            with self.assertRaisesRegex(ValueError, 'Packaging Agent attempted'):
                CoderAgent._merge_packaging_files({'files': [{'path': path, 'content': 'replacement'}]},
                                                {'src/main.py': 'original'})

    async def test_forge_resume_calls_packager_without_regenerating_source(self):
        previous = {'Dockerfile': 'FROM python:3.11\nCOPY backend/pyproject.toml ./\nEXPOSE 8080\n',
                    'frontend/src/App.jsx': 'export default () => <h1>Existing application</h1>;',
                    'backend/main.py': 'app = None\n'}
        reply = json.dumps({'files': [{'path': 'backend/pyproject.toml',
                            'content': '[tool.poetry]\nname="service"\nversion="0.1.0"\npackage-mode=false\n'}]})
        result = await self.generate([reply], frontend='React', previous=previous,
                                    findings=[{'kind': 'generation_packaging', 'issue': 'Missing manifest'}])
        self.assertEqual(self.agent.run.await_count, 1)
        self.assertEqual(result.files['frontend/src/App.jsx'], previous['frontend/src/App.jsx'])
        self.assertEqual(result.files['backend/main.py'], previous['backend/main.py'])
        self.assertEqual(self.framework.Agent.call_args_list[-1].kwargs['name'], 'Packaging Agent')

    def test_packaging_patch_preserves_all_source_and_artifact_bounds(self):
        previous = {'src/main.py': 'original', 'tests/test_main.py': 'test'}
        package_patch = {'files': [{'path': 'requirements.txt', 'content': 'fastapi'}]}
        result = CoderAgent._merge_packaging_files(package_patch, previous)
        self.assertEqual(result, {**previous, 'requirements.txt': 'fastapi'})
        with patch.object(CoderAgent, 'max_total_bytes', 10):
            with self.assertRaisesRegex(ValueError, 'total source size'):
                CoderAgent._merge_packaging_files(package_patch, previous)

    def test_partial_manifest_completion_keeps_application_dependencies_and_scripts(self):
        previous = {'frontend/package.json': json.dumps({'name': 'app', 'dependencies': {'react': '18.2.0', 'axios': '^1.0.0'},
                                                         'scripts': {'build': 'react-scripts build'}})}
        data = {'files': [{'path': 'frontend/package.json', 'content': json.dumps({'devDependencies': {'typescript': '4.9.5'}})}]}
        manifest = json.loads(CoderAgent._merge_packaging_files(data, previous)['frontend/package.json'])
        self.assertEqual(manifest['dependencies'], {'react': '18.2.0', 'axios': '^1.0.0'})
        self.assertEqual(manifest['scripts']['build'], 'react-scripts build')
        self.assertEqual(manifest['devDependencies']['typescript'], '4.9.5')

    async def test_repeated_bad_json_stops_after_two_calls(self):
        with self.assertRaises(CoderOutputError):
            await self.generate(['{"files": [], bad}'] * 2)
        self.assertEqual(self.agent.run.await_count, 2)
        self.credential.close.assert_called_once()

    async def test_deployment_loop_owns_its_retry_budget(self):
        with self.assertRaises(CoderOutputError):
            await self.generate(['{"files": [], bad}'], retry=False)
        self.assertEqual(self.agent.run.await_count, 1)

    async def test_missing_frontend_output_gets_two_packaging_repairs(self):
        files = {
            "Dockerfile": "FROM nginx\nCOPY frontend/build /site\nEXPOSE 8080\n",
            "frontend/package.json": '{"scripts":{"build":"react-scripts build"},"dependencies":{"react-scripts":"5.0.1"}}',
            "frontend/src/index.js": "console.log('application');",
        }
        initial = json.dumps({"files": [{"path": p, "content": c} for p, c in files.items()]})
        fixed = json.dumps({"files": [{"path": "Dockerfile", "content": (
            "FROM node:22 AS frontend-build\nWORKDIR /app/frontend\n"
            "COPY frontend/ ./\nRUN npm install && npm run build\n"
            "FROM nginx\nCOPY --from=frontend-build /app/frontend/build /site\nEXPOSE 8080\n"
        )}]})
        result = await self.generate([initial, initial, fixed])
        self.assertEqual(self.agent.run.await_count, 3)
        self.assertEqual(result.files["frontend/src/index.js"], files["frontend/src/index.js"])
        context = json.loads(self.agent.run.call_args_list[2].args[0])
        self.assertIn("frontend/build", context["criticAndSandboxFindings"][0]["issue"])
        self.assertIn("COPY --from", context["criticAndSandboxFindings"][0]["recommendation"])
        self.credential.close.assert_called_once()

    async def test_packaging_repairs_stop_and_preserve_candidate(self):
        invalid = json.dumps({"files": [{"path": "Dockerfile", "content":
                            "FROM nginx\nCOPY frontend/build /site\nEXPOSE 8080\n"}]})
        with self.assertRaises(CoderOutputError) as error:
            await self.generate([invalid] * 3)
        self.assertEqual(self.agent.run.await_count, 3)
        self.assertIn("frontend/build", str(error.exception))
        self.assertIn("Dockerfile", error.exception.files)
        self.assertEqual(len(error.exception.validation_history), 3)
        self.credential.close.assert_called_once()

    async def test_repairs_include_actual_inventory_and_prior_failures(self):
        def response(source):
            return json.dumps({"files": [
                {"path": "Dockerfile", "content": f"FROM python:3.11\nCOPY {source} /app\nEXPOSE 8080\n"},
                {"path": "backend/main.py", "content": "app = None\n"},
            ]})
        with self.assertRaises(CoderOutputError):
            await self.generate([response("frontend/build"), response("backend/app"), response("backend/app")])
        context = json.loads(self.agent.run.call_args_list[2].args[0])
        self.assertEqual(context["availableArtifactPaths"], ["Dockerfile", "backend/main.py"])
        self.assertIn("frontend/build", context["generationValidationHistory"][0]["issue"])
        self.assertIn("backend/app", context["generationValidationHistory"][1]["issue"])
