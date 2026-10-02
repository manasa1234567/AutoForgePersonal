from __future__ import annotations

from typing import Any

from ..agents.architecture_agent import ArchitectureAgent, ArchitectureResult
from ..agents.coder_agent import CoderAgent, CoderResult
from ..agents.critic_agent import CriticAgent, CriticResult
from ..agents.spec_agent import SpecAgent, SpecAgentResult
from ..models.schemas import Blueprint


class AgentService:
    """Application boundary for executable AutoForge agents."""

    def __init__(self) -> None:
        self.spec_agent = SpecAgent()
        self.architecture_agent = ArchitectureAgent()
        self.coder_agent = CoderAgent()
        self.critic_agent = CriticAgent()

    async def run_spec_agent(self, *, title: str, source_type: str, source_text: str) -> SpecAgentResult:
        return await self.spec_agent.analyze(
            title=title,
            source_type=source_type,
            source_text=source_text,
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
    ) -> ArchitectureResult:
        return await self.architecture_agent.design(
            title=title,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            dependencies=dependencies,
            constraints=constraints,
            security_considerations=security_considerations,
        )

    async def run_coder_agent(
        self,
        *,
        title: str,
        blueprint: Blueprint,
        requirements: list[dict[str, Any]],
        acceptance_criteria: list[str],
        previous_artifacts: dict[str, str] | None = None,
        repair_findings: list[dict[str, Any]] | None = None,
    ) -> CoderResult:
        return await self.coder_agent.generate(
            title=title,
            blueprint=blueprint,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
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
    ) -> CriticResult:
        return await self.critic_agent.review(
            title=title,
            blueprint=blueprint,
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            artifacts=artifacts,
        )
