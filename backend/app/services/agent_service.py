from __future__ import annotations

from typing import Any

from ..agents.architecture_agent import ArchitectureAgent, ArchitectureResult
from ..agents.coder_agent import CoderAgent, CoderResult
from ..agents.critic_agent import CriticAgent, CriticResult
from ..agents.spec_agent import SpecAgent, SpecAgentResult
from ..agents.security_reviewer import SecurityReviewer
from ..agents.deployer_agent import DeployerAgent
from ..models.schemas import Blueprint, DeploymentPlan, SecurityReview, SkillRecipe, BuildState


class AgentService:
    """Application boundary for executable AutoForge agents."""

    def __init__(self) -> None:
        self.spec_agent = SpecAgent()
        self.architecture_agent = ArchitectureAgent()
        self.coder_agent = CoderAgent()
        self.critic_agent = CriticAgent()
        self.security_reviewer = SecurityReviewer()
        self.deployer_agent = DeployerAgent()

    async def run_spec_agent(
        self,
        *,
        title: str,
        source_type: str,
        source_text: str,
        skills: list[SkillRecipe] | None = None,
    ) -> SpecAgentResult:
        return await self.spec_agent.analyze(
            title=title,
            source_type=source_type,
            source_text=source_text,
            skills=skills,
        )

    async def run_architecture_agent(
        self,
        *,
        title: str,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        dependencies: list[str],
        constraints: list[str],
        security_considerations: list[str],
        skills: list[SkillRecipe] | None = None,
    ) -> ArchitectureResult:
        return await self.architecture_agent.design(
            title=title,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            dependencies=dependencies,
            constraints=constraints,
            security_considerations=security_considerations,
            skills=skills,
        )

    async def run_coder_agent(
        self,
        *,
        title: str,
        blueprint: Blueprint,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        skills: list[SkillRecipe] | None = None,
        previous_artifacts: dict[str, str] | None = None,
        repair_findings: list[dict[str, Any]] | None = None,
    ) -> CoderResult:
        return await self.coder_agent.generate(
            title=title,
            blueprint=blueprint,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            skills=skills,
            previous_artifacts=previous_artifacts,
            repair_findings=repair_findings,
        )

    async def run_critic_agent(
        self,
        *,
        title: str,
        blueprint: Blueprint,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        artifacts: dict[str, str],
        skills: list[SkillRecipe] | None = None,
    ) -> CriticResult:
        return await self.critic_agent.review(
            title=title,
            blueprint=blueprint,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            artifacts=artifacts,
            skills=skills,
        )

    async def run_security_reviewer(
        self,
        *,
        artifacts: dict[str, str],
        skills: list[SkillRecipe] | None = None,
        requirements: list[dict[str, Any]] | None = None,
        security_controls: list[str] | None = None,
        blueprint_choices: dict[str, str] | None = None,
    ) -> SecurityReview:
        return await self.security_reviewer.review(
            artifacts=artifacts,
            skills=skills,
            requirements=requirements,
            security_controls=security_controls,
            blueprint_choices=blueprint_choices,
        )

    async def prepare_deployment(self, build: BuildState) -> DeploymentPlan:
        return await self.deployer_agent.prepare(build)
