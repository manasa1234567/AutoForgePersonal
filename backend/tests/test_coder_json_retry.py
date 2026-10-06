import json
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from app.agents.coder_agent import CoderAgent, CoderOutputError


class CoderJsonRetry(unittest.IsolatedAsyncioTestCase):
    async def generate(self, responses, retry=True):
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
        self.credential = credential
        with patch.dict("sys.modules", {"agent_framework": framework,
                        "agent_framework.foundry": foundry, "azure.identity": identity}), \
                patch.dict("os.environ", {"FOUNDRY_PROJECT_ENDPOINT": "https://example.test", "FOUNDRY_MODEL": "test"}):
            return await CoderAgent()._generate_with_foundry(
                title="Example", blueprint=SimpleNamespace(model_dump=lambda **kw: {}),
                requirements=[], acceptance_criteria=[], skills=[], retry_packaging=retry)

    async def test_bad_json_gets_one_complete_regeneration(self):
        valid = json.dumps({"files": [{"path": "Dockerfile", "content": "FROM nginx\nEXPOSE 8080\n"}]})
        result = await self.generate(['{"files": [], bad}', valid])
        self.assertIn("Dockerfile", result.files)
        self.assertEqual(self.agent.run.await_count, 2)
        context = json.loads(self.agent.run.call_args_list[1].args[0])
        self.assertIn("Expecting property name", context["criticAndSandboxFindings"][0]["issue"])
        self.credential.close.assert_called_once()

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
        self.credential.close.assert_called_once()
