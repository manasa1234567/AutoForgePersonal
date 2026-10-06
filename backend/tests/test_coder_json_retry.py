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
