import unittest

from app.agents.deployer_agent import DeployerAgent
from app.models.schemas import BuildState, ProofResult


class ReleaseValidationEvidence(unittest.IsolatedAsyncioTestCase):
    async def plan(self, runtime):
        build = BuildState(id='example', title='Example', source_type='usecase', source_text='Example', files=[],
                           proof=ProofResult(artifacts={'Dockerfile': 'FROM example\nEXPOSE 8080\n'},
                                             runtime_status=runtime))
        return await DeployerAgent().prepare(build)

    async def test_source_checks_are_not_presented_as_runtime_execution(self):
        plan = await self.plan('Passed: Sandbox source checks passed. Application compilation and test execution were not performed.')
        self.assertIn('isolated_source_validation', plan.checks)
        self.assertNotIn('isolated_runtime_validation', plan.checks)
        self.assertTrue(plan.checks['image_build_and_startup'].startswith('Pending:'))

    async def test_actual_runtime_evidence_retains_its_label(self):
        plan = await self.plan('Passed: image compiled and HTTP startup verified')
        self.assertIn('isolated_runtime_validation', plan.checks)

    async def test_failed_validation_remains_a_blocker(self):
        plan = await self.plan('Failed: image compilation')
        self.assertTrue(any('validation has not passed' in issue for issue in plan.blockers))
