import unittest
import json
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from app.agents.critic_agent import CriticAgent
from app.models.schemas import CriticFinding


class CriticEvidence(unittest.TestCase):
    def test_invented_file_cannot_support_a_blocker(self):
        data = {'findings': [{'file': 'src/main.py', 'severity': 'Critical',
                             'issue': 'No validation may lead to injection', 'evidence': 'some invented source'}]}
        self.assertTrue(CriticAgent._review_evidence_issues(data, {'backend/app/main.py': 'app = None'}))

    def test_generic_security_claim_without_evidence_is_invalid(self):
        data = {'findings': [{'file': 'app.py', 'severity': 'Critical', 'issue': 'May lead to injection'}]}
        self.assertTrue(CriticAgent._review_evidence_issues(data, {'app.py': 'from fastapi import FastAPI\n'}))

    def test_matching_source_evidence_retains_real_critical_finding(self):
        source = 'os.system(request.query_params["command"])'
        data = {'findings': [{'file': 'app.py', 'severity': 'Critical', 'issue': 'User-controlled shell execution',
                             'recommendation': 'Remove shell execution', 'evidence': source}]}
        self.assertEqual(CriticAgent._review_evidence_issues(data, {'app.py': source}), [])
        findings = CriticAgent._normalize_findings(data['findings'], [])
        self.assertEqual(findings[0].severity, 'Critical')
        self.assertEqual(findings[0].evidence, source)

    def test_local_critical_findings_are_not_discarded(self):
        finding = CriticFinding(severity='Critical', file='app.py', issue='Proven local check', recommendation='Fix')
        self.assertEqual(CriticAgent._normalize_findings([], [finding]), [finding])

    def test_short_real_vulnerability_can_still_be_evidenced(self):
        source = 'eval(input())'
        data = {'findings': [{'severity': 'Critical', 'file': 'app.py', 'evidence': source}]}
        self.assertEqual(CriticAgent._review_evidence_issues(data, {'app.py': source}), [])

    def test_fences_relative_paths_and_uniform_indent_do_not_invalidate_real_source(self):
        source = 'def run():\n    if enabled:\n        os.system(command)\n'
        data = {'findings': [{'severity': 'Critical', 'file': '.\\app\\main.py',
                             'evidence': '```python\nif enabled:\n    os.system(command)\n```'}]}
        self.assertEqual(CriticAgent._review_evidence_issues(data, {'app/main.py': source}), [])
        self.assertEqual(data['findings'][0]['file'], 'app/main.py')
        self.assertIn('    if enabled:\n        os.system(command)', data['findings'][0]['evidence'])

    def test_normalization_does_not_change_string_literals_or_guard_indentation(self):
        source = 'if enabled:\n    query = "SELECT * FROM users"\n'
        self.assertIsNone(CriticAgent._matching_excerpt('query = "SELECT*FROM users"', source))
        self.assertIsNone(CriticAgent._matching_excerpt('if enabled:\nquery = "SELECT * FROM users"', source))

    def test_negative_coverage_claim_requires_actual_missing_check(self):
        data = {'findings': [{'severity': 'High', 'file': None, 'check': 'test_files', 'evidence': 'test_files: Missing'}]}
        self.assertEqual(CriticAgent._review_evidence_issues(data, {}, {'test_files': 'Missing'}), [])
        self.assertTrue(CriticAgent._review_evidence_issues(data, {}, {'test_files': 'Present'}))

    def test_invalid_or_empty_review_schema(self):
        self.assertTrue(CriticAgent._review_evidence_issues({}, {}))
        self.assertEqual(CriticAgent._review_evidence_issues({'findings': []}, {}), [])


class CriticEvidenceCorrection(unittest.IsolatedAsyncioTestCase):
    async def review(self, responses):
        self.agent = SimpleNamespace(run=AsyncMock(side_effect=[json.dumps(data) for data in responses]))
        framework = ModuleType('agent_framework')
        framework.Agent = Mock(return_value=self.agent)
        foundry = ModuleType('agent_framework.foundry')
        foundry.FoundryChatClient = Mock()
        identity = ModuleType('azure.identity')
        credential = Mock()
        identity.DefaultAzureCredential = Mock(return_value=credential)
        identity.ManagedIdentityCredential = Mock(return_value=credential)
        with patch.dict('sys.modules', {'agent_framework': framework, 'agent_framework.foundry': foundry,
                                      'azure.identity': identity}), \
             patch.dict('os.environ', {'FOUNDRY_PROJECT_ENDPOINT': 'https://example.test', 'FOUNDRY_CRITIC_MODEL': 'test'}):
            result = await CriticAgent()._review_with_foundry(title='Example',
                blueprint=SimpleNamespace(model_dump=lambda **kw: {}), requirements=[], acceptance_criteria=[],
                artifacts={'app.py': 'os.system(request.query_params["command"])'},
                local_findings=[], checks={'artifact_paths': 'Passed'}, skills=[])
        credential.close.assert_called_once()
        return result

    async def test_correction_retains_concrete_security_blocker(self):
        bad = {'findings': [{'severity': 'Critical', 'file': 'src/main.py', 'issue': 'No validation'}]}
        good = {'findings': [{'severity': 'Critical', 'file': 'app.py', 'issue': 'User-controlled shell execution',
                'recommendation': 'Remove shell execution', 'evidence': 'os.system(request.query_params["command"])'}]}
        result = await self.review([bad, good])
        self.assertEqual(self.agent.run.await_count, 2)
        self.assertEqual(result.findings[0].severity, 'Critical')
        self.assertEqual(result.findings[0].file, 'app.py')
        self.assertEqual(json.loads(self.agent.run.call_args_list[1].args[0])['availableArtifactPaths'], ['app.py'])

    async def test_repeated_unsupported_claim_stops_as_review_error(self):
        bad = {'findings': [{'severity': 'Critical', 'file': 'src/main.py', 'issue': 'No validation'}]}
        result = await self.review([bad, bad])
        self.assertEqual(self.agent.run.await_count, 2)
        self.assertEqual(result.checks['foundry_source_review'], 'Failed: unsubstantiated review evidence')
        self.assertFalse(result.findings)
