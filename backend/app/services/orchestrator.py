from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4

from ..models.schemas import (
    AgentState,
    AuditEvent,
    BuildCreate,
    BuildState,
    BlueprintUpdate,
    DeploymentCallback,
    DeploymentPlan,
    ProofResult,
    SecurityReview,
    SkillRecipe,
    SkillUsage,
)
from .agent_service import AgentService
from .azure_adapters import AzureAdapters
from ..repositories.build_repository import (
    BuildRepository,
    build_repository_from_environment,
)
from .skill_registry import skill_registry
from .jira_client import JiraClient
from .job_dispatcher import BuildJobDispatcher, InProcessBuildJobDispatcher
from .source_documents import extract_source_documents
from .github_publisher import GitHubPublisher


class Orchestrator:
    """Coordinates the governed AutoForge workflow in demo mode."""

    def __init__(
        self,
        build_repository: BuildRepository | None = None,
        job_dispatcher: BuildJobDispatcher | None = None,
    ) -> None:
        self._build_repository = (
            build_repository or build_repository_from_environment()
        )
        self._azure = AzureAdapters()
        self._agent_service = AgentService()
        self._jira = JiraClient()
        self._job_dispatcher = (
            job_dispatcher
            or InProcessBuildJobDispatcher(self._run_until_gate)
        )
        self._approval_tasks: dict[str, asyncio.Task[None]] = {}

    @staticmethod
    def _time() -> str:
        return datetime.now(timezone.utc).strftime("%H:%M:%S")

    @staticmethod
    def _skill_query(build: BuildState) -> str:
        parts = [
            build.title,
            build.source_type,
            build.source_text,
        ]

        parts.extend(
            str(item.get("text", ""))
            for item in build.requirements
        )

        parts.extend(build.acceptance_criteria)

        if build.blueprint:
            parts.extend(
                [
                    build.blueprint.frontend,
                    build.blueprint.backend,
                    build.blueprint.data,
                    *build.blueprint.security,
                ]
            )

        return " ".join(part for part in parts if part)

    def _record_skill_retrieval(
        self,
        build: BuildState,
        recipes: list[SkillRecipe],
        agent: str,
    ) -> None:
        if not recipes:
            return

        build.skills_used.extend(
            SkillUsage(
                id=recipe.id,
                version=recipe.version,
                usage="retrieved",
            )
            for recipe in recipes
        )

        self._add_event(
            build,
            "Skills",
            f"Retrieved {len(recipes)} approved recipe(s) for {agent}",
            "Skill Registry",
            metadata={
                "agent": agent,
                "skills": [recipe.id for recipe in recipes],
            },
        )

    @staticmethod
    def _agents() -> list[AgentState]:
        return [
            AgentState(
                name="Spec Agent",
                role="Understand and refine requirements",
            ),
            AgentState(
                name="Architecture Agent",
                role="Design solution and technology stack",
            ),
            AgentState(
                name="Coder Agent",
                role="Generate code, tests and skills",
            ),
            AgentState(
                name="Critic Agent",
                role="Validate, test and self-heal",
            ),
            AgentState(
                name="Skill Agent",
                role="Manage, evolve and promote reusable skills",
            ),
            AgentState(
                name="Security Reviewer",
                role="Run security and policy checks",
            ),
            AgentState(
                name="Deployer Agent",
                role="Build, scan and deploy",
            ),
        ]

    def create(self, payload: BuildCreate) -> BuildState:
        extracted_documents = extract_source_documents(
            payload.file_contents
        )

        if payload.source_type == "openapi":
            if (
                len(extracted_documents) > 1
                or (
                    payload.source_text.strip()
                    and extracted_documents
                )
            ):
                raise ValueError(
                    "Provide one OpenAPI contract as pasted text "
                    "or one uploaded file"
                )

            if (
                extracted_documents
                and not extracted_documents[0][0]
                .lower()
                .endswith((".yaml", ".yml", ".json"))
            ):
                raise ValueError(
                    "OpenAPI source files must be YAML or JSON"
                )

            source_text = (
                extracted_documents[0][1]
                if extracted_documents
                else payload.source_text.strip()
            )

        else:
            sections = (
                [payload.source_text.strip()]
                if payload.source_text.strip()
                else []
            )

            sections.extend(
                f"Source document: {name}\n{text}"
                for name, text in extracted_documents
            )

            source_text = "\n\n".join(sections)

        if (
            payload.source_type == "upload"
            and not extracted_documents
        ):
            raise ValueError(
                "Select at least one engineering document to analyze"
            )

        if len(source_text) > 20_000:
            raise ValueError(
                "Combined input and extracted document text "
                "exceeds the 20,000 character limit"
            )

        build_id = str(uuid4())[:8]

        build = BuildState(
            id=build_id,
            title=payload.title,
            source_type=payload.source_type,
            source_text=source_text,
            files=payload.files
            or [name for name, _ in extracted_documents],
            agents=self._agents(),
        )

        self._add_event(
            build,
            "Intake",
            "Requirement submitted",
            "Orchestrator",
            metadata={
                "source_type": payload.source_type,
            },
        )

        self._build_repository.save(build)

        return build

    def list(self) -> list[BuildState]:
        """Return persisted builds newest first."""
        return self._build_repository.list()

    async def start(self, build_id: str) -> BuildState:
        build = self.get(build_id)

        if build.status not in {"Draft", "Refined"}:
            return build

        await self._job_dispatcher.enqueue(build_id)

        return build

    async def _run_until_gate(self, build_id: str) -> None:
        build = self.get(build_id)

        self._build_repository.save(build)

        try:
            await self._understand(build)

            build.approval_gate = "requirements"
            build.stage = "Understand"
            build.status = "Awaiting Approval"
            build.progress = 22

            self._build_repository.save(build)

        except Exception as exc:
            self._fail(build, str(exc))
            self._build_repository.save(build)

    async def _understand(self, build: BuildState) -> None:
        build.status = "Running"
        build.stage = "Understand"

        self._set_agent(
            build,
            "Spec Agent",
            "Running",
            "Extracting requirements and checking source",
        )

        self._add_event(
            build,
            "Understand",
            "Spec Agent started requirement extraction",
            "Spec Agent",
        )

        self._build_repository.save(build)

        if build.source_type == "jira":
            issue = await self._jira.get_issue(build.source_text)

            build.title = issue.summary[:160]

            source_parts = [
                f"Jira issue: {issue.key}",
            ]

            if issue.issue_type:
                source_parts.append(
                    f"Issue type: {issue.issue_type}"
                )

            source_parts.append(
                f"Summary: {issue.summary}"
            )

            if issue.description:
                source_parts.append(
                    f"Description:\n{issue.description}"
                )

            if issue.acceptance_criteria:
                source_parts.append(
                    "Acceptance criteria:\n"
                    f"{issue.acceptance_criteria}"
                )

            build.source_text = "\n\n".join(
                source_parts
            )[:20_000]

            self._add_event(
                build,
                "Intake",
                f"Jira issue {issue.key} retrieved for analysis",
                "Orchestrator",
                metadata={
                    "issue_key": issue.key,
                },
            )

        safety_result = await self._azure.content_safety_check(
            build.source_text
        )

        if bool(safety_result["blocked"]):
            raise RuntimeError(
                "Input blocked by AI safety policy: "
                f"{safety_result['reason']}"
            )

        recipes = skill_registry.retrieve(
            agent="Spec Agent",
            query=self._skill_query(build),
            limit=5,
        )

        result = await self._agent_service.run_spec_agent(
            title=build.title,
            source_type=build.source_type,
            source_text=build.source_text,
            skills=recipes,
        )

        if result.mode in {
            "foundry-agent",
            "azure-openai",
        }:
            self._record_skill_retrieval(
                build,
                recipes,
                "Spec Agent",
            )

        build.requirements = result.requirements
        build.requirement_summary = result.summary
        build.acceptance_criteria = result.acceptance_criteria
        build.dependencies = result.dependencies
        build.constraints = result.constraints
        build.ambiguities = result.ambiguities
        build.assumptions = result.assumptions
        build.risks = result.risks
        build.security_considerations = (
            result.security_considerations
        )
        build.clarification_questions = (
            result.clarification_questions
        )

        build.spec_confidence = result.confidence
        build.spec_readiness = result.readiness
        build.agent_mode = result.mode

        build.metrics.tokens += result.tokens
        build.metrics.tool_calls += 3

        self._set_agent(
            build,
            "Spec Agent",
            "Ready",
            f"{len(result.requirements)} requirements extracted",
        )

        self._add_event(
            build,
            "Understand",
            "Spec Agent completed requirement extraction",
            "Spec Agent",
            metadata={
                "count": len(result.requirements),
                "confidence": result.confidence,
                "mode": result.mode,
            },
        )

    async def _design(self, build: BuildState) -> None:
        self._set_agent(
            build,
            "Architecture Agent",
            "Running",
            "Creating solution blueprint",
        )

        self._build_repository.save(build)

        recipes = skill_registry.retrieve(
            agent="Architecture Agent",
            query=self._skill_query(build),
            limit=5,
        )

        result = await self._agent_service.run_architecture_agent(
            title=build.title,
            requirements=build.requirements,
            acceptance_criteria=build.acceptance_criteria,
            dependencies=build.dependencies,
            constraints=build.constraints,
            security_considerations=build.security_considerations,
            skills=recipes,
        )

        if result.mode == "foundry-agent":
            self._record_skill_retrieval(
                build,
                recipes,
                "Architecture Agent",
            )

        build.blueprint = result.blueprint
        build.metrics.tokens += result.tokens

        if result.mode == "foundry-agent":
            build.metrics.tool_calls += 1

        self._set_agent(
            build,
            "Architecture Agent",
            "Ready",
            "Blueprint ready for approval "
            f"({result.mode})",
        )

        self._add_event(
            build,
            "Design",
            "Architecture blueprint generated",
            "Architecture Agent",
            metadata={
                "mode": result.mode,
                "open_questions": len(
                    result.blueprint.open_questions
                ),
            },
        )

        self._build_repository.save(build)

    async def _forge(self, build: BuildState) -> None:
        self._set_agent(
            build,
            "Coder Agent",
            "Running",
            "Generating application, tests and reusable skill",
        )

        build.stage = "Forge"
        build.progress = 58

        self._build_repository.save(build)

        if build.blueprint is None:
            raise RuntimeError(
                "An approved architecture blueprint is required "
                "before code generation"
            )

        coder_recipes = skill_registry.retrieve(
            agent="Coder Agent",
            query=self._skill_query(build),
            limit=5,
        )

        result = await self._agent_service.run_coder_agent(
            title=build.title,
            blueprint=build.blueprint,
            requirements=build.requirements,
            acceptance_criteria=build.acceptance_criteria,
            skills=coder_recipes,
        )

        if result.mode == "foundry-agent":
            self._record_skill_retrieval(
                build,
                coder_recipes,
                "Coder Agent",
            )

        build.proof = ProofResult(
            files=list(result.files),
            artifacts=result.files,
            generator_mode=result.mode,
            integration="Not run",
        )

        build.skills_used.extend(result.skills_used)

        applied_skills = [
            skill
            for skill in result.skills_used
            if skill.usage == "applied"
        ]

        skipped_skills = [
            skill
            for skill in result.skills_used
            if skill.usage == "skipped"
        ]

        if applied_skills:
            self._add_event(
                build,
                "Skills",
                f"Coder Agent applied "
                f"{len(applied_skills)} approved skill recipe(s)",
                "Skill Agent",
                metadata={
                    "skills": [
                        skill.model_dump(by_alias=True)
                        for skill in applied_skills
                    ],
                },
            )

        if skipped_skills:
            self._add_event(
                build,
                "Skills",
                f"Coder Agent skipped "
                f"{len(skipped_skills)} retrieved recipe(s)",
                "Skill Agent",
                metadata={
                    "skills": [
                        skill.model_dump(by_alias=True)
                        for skill in skipped_skills
                    ],
                },
            )

        build.metrics.tokens += result.tokens

        if result.mode == "foundry-agent":
            build.metrics.tool_calls += 1

        self._set_agent(
            build,
            "Coder Agent",
            "Ready",
            f"Generated {len(result.files)} file(s) "
            f"({result.mode})",
        )

        self._add_event(
            build,
            "Forge",
            "Code artifacts generated from the approved blueprint",
            "Coder Agent",
            metadata={
                "files": len(build.proof.files),
                "mode": result.mode,
            },
        )

        build.stage = "Forge"
        build.status = "Awaiting Approval"
        build.approval_gate = "artifacts"
        build.progress = 66

        self._build_repository.save(build)

    async def _prove(self, build: BuildState) -> None:
        self._set_agent(
            build,
            "Critic Agent",
            "Running",
            "Reviewing generated artifacts without executing them",
        )

        build.stage = "Prove"
        build.progress = 72

        self._build_repository.save(build)

        if build.proof is None:
            raise RuntimeError(
                "Proof result is missing before critic execution"
            )

        if build.blueprint is None:
            raise RuntimeError(
                "The approved blueprint is missing before Critic review"
            )

        critic_recipes = skill_registry.retrieve(
            agent="Critic Agent",
            query=self._skill_query(build),
            limit=5,
        )

        result = await self._agent_service.run_critic_agent(
            title=build.title,
            blueprint=build.blueprint,
            requirements=build.requirements,
            acceptance_criteria=build.acceptance_criteria,
            artifacts=build.proof.artifacts,
            skills=critic_recipes,
        )

        if result.mode == "foundry-static-review":
            self._record_skill_retrieval(
                build,
                critic_recipes,
                "Critic Agent",
            )

        repair_limit = 2

        for attempt in range(1, repair_limit + 1):
            static_checks_failed = any(
                value == "Failed"
                for value in result.checks.values()
            )
            critical_findings = any(
                finding.severity == "Critical"
                for finding in result.findings
            )
            runtime_failed = result.runtime_status.lower().startswith("failed")
            if (
                not (
                    static_checks_failed
                    or critical_findings
                    or runtime_failed
                )
                or build.proof.generator_mode != "foundry-agent"
            ):
                break

            self._set_agent(
                build,
                "Coder Agent",
                "Running",
                f"Repair attempt {attempt} of "
                f"{repair_limit} from Critic findings",
            )

            repair_recipes = skill_registry.retrieve(
                agent="Coder Agent",
                query=self._skill_query(build),
                limit=5,
            )

            repaired = await self._agent_service.run_coder_agent(
                title=build.title,
                blueprint=build.blueprint,
                requirements=build.requirements,
                acceptance_criteria=build.acceptance_criteria,
                skills=repair_recipes,
                previous_artifacts=build.proof.artifacts,
                repair_findings=[
                    finding.model_dump(by_alias=True)
                    for finding in result.findings
                ],
            )

            if repaired.mode == "foundry-agent":
                self._record_skill_retrieval(
                    build,
                    repair_recipes,
                    "Coder Agent",
                )

            build.proof.files = list(repaired.files)
            build.proof.artifacts = repaired.files
            build.proof.code = repaired.files

            build.skills_used.extend(
                repaired.skills_used
            )

            applied_repair_skills = [
                skill
                for skill in repaired.skills_used
                if skill.usage == "applied"
            ]

            skipped_repair_skills = [
                skill
                for skill in repaired.skills_used
                if skill.usage == "skipped"
            ]

            if (
                applied_repair_skills
                or skipped_repair_skills
            ):
                self._add_event(
                    build,
                    "Skills",
                    f"Repair pass applied "
                    f"{len(applied_repair_skills)} recipe(s) "
                    f"and skipped "
                    f"{len(skipped_repair_skills)}",
                    "Skill Agent",
                    metadata={
                        "skills": [
                            skill.model_dump(
                                by_alias=True
                            )
                            for skill in repaired.skills_used
                        ],
                    },
                )

            build.metrics.tokens += repaired.tokens

            if repaired.mode == "foundry-agent":
                build.metrics.tool_calls += 1

            build.metrics.self_heal_iterations += 1

            self._set_agent(
                build,
                "Coder Agent",
                "Ready",
                f"Generated a revised artifact set "
                f"({repaired.mode})",
            )

            self._add_event(
                build,
                "Prove",
                f"Coder Agent revised artifacts after "
                f"validation findings (attempt {attempt} "
                f"of {repair_limit})",
                "Coder Agent",
                severity="warning",
                metadata={
                    "attempt": attempt,
                    "prior_findings": len(
                        result.findings
                    ),
                },
            )

            self._build_repository.save(build)

            critic_recipes = skill_registry.retrieve(
                agent="Critic Agent",
                query=self._skill_query(build),
                limit=5,
            )

            result = await self._agent_service.run_critic_agent(
                title=build.title,
                blueprint=build.blueprint,
                requirements=build.requirements,
                acceptance_criteria=build.acceptance_criteria,
                artifacts=build.proof.artifacts,
                skills=critic_recipes,
            )

            if result.mode == "foundry-static-review":
                self._record_skill_retrieval(
                    build,
                    critic_recipes,
                    "Critic Agent",
                )

        build.proof.critic_mode = result.mode
        build.proof.critic_summary = result.summary
        build.proof.critic_findings = result.findings
        build.proof.requirement_coverage = (
            result.requirement_coverage
        )
        build.proof.test_plan = result.test_plan
        build.proof.checks = result.checks
        build.proof.runtime_status = result.runtime_status
        build.proof.integration = result.runtime_status

        if result.mode.startswith(
            "foundry-static-review"
        ):
            build.metrics.tool_calls += 1

        critical_findings = any(
            finding.severity == "Critical"
            for finding in result.findings
        )

        runtime_pending = (
            not result.runtime_status
            .lower()
            .startswith("passed")
            or critical_findings
            or any(value == "Failed" for value in result.checks.values())
        )

        self._set_agent(
            build,
            "Critic Agent",
            "Blocked" if runtime_pending else "Ready",
            f"Review complete ({result.mode}); "
            f"{result.runtime_status}",
        )

        if runtime_pending:
            waiting_reason = (
                "Awaiting isolated runtime validation"
                if result.runtime_status
                .lower()
                .startswith("not run")
                else
                "Awaiting a passing build and test run"
            )

            self._set_agent(
                build,
                "Skill Agent",
                "Blocked",
                waiting_reason,
            )

        self._add_event(
            build,
            "Prove",
            (
                "Source review completed; runtime validation "
                "was not run"
                if result.runtime_status
                .lower()
                .startswith("not run")
                else
                "Source review and runtime validation completed: "
                f"{result.runtime_status}"
            ),
            "Critic Agent",
            severity=(
                "warning"
                if result.findings
                or "Not run" in result.runtime_status
                else "info"
            ),
            metadata={
                "mode": result.mode,
                "findings": len(result.findings),
                "runtime": result.runtime_status,
            },
        )

        if runtime_pending:
            build.approval_gate = None
            build.status = "Blocked"
            build.progress = 72

            failed_checks = [name for name, value in result.checks.items() if value == "Failed"]
            if failed_checks:
                details = " ".join(
                    f"{finding.file or 'Project'}: {finding.issue}"
                    for finding in result.findings[:3]
                )
                build.error = (
                    f"Validation checks failed ({', '.join(failed_checks)}). "
                    + (details or result.runtime_status)
                )
            elif (
                critical_findings
                and result.runtime_status
                .lower()
                .startswith("passed")
            ):
                build.error = (
                    "Critical source findings must be "
                    "resolved before this build can proceed."
                )

            elif (
                result.runtime_status
                .lower()
                .startswith("not run")
            ):
                build.error = result.runtime_status

            else:
                build.error = (
                    "Runtime validation did not pass. "
                    "Review the Critic findings before "
                    "requesting a corrected build."
                )

            self._build_repository.save(build)
            return

        if build.skill_proposal:
            build.approval_gate = "skill"
            build.status = "Awaiting Approval"
            build.progress = 78

            self._build_repository.save(build)
            return

        self._set_agent(
            build,
            "Skill Agent",
            "Ready",
            "No eligible reusable skill candidate "
            "was produced in this build",
        )

        self._add_event(
            build,
            "Skills",
            "No new reusable skill candidate was "
            "promoted by this build",
            "Skill Agent",
        )

        await self._security(build)

    # ============================================================
    # POC SECURITY / RELEASE GATE
    # ============================================================

    async def _security(self, build: BuildState) -> None:
        self._set_agent(
            build,
            "Security Reviewer",
            "Running",
            "Running POC security and policy checks",
        )

        build.stage = "Release"
        build.progress = 88

        self._build_repository.save(build)

        build_id = build.id
        review = await self.run_security_review(build_id)
        # run_security_review loads and persists its own BuildState snapshot.
        # Refresh here before saving the POC gate result, otherwise this older
        # object can overwrite the saved SecurityReview (especially with the
        # snapshot-based Azure repository) and make _deploy reject an approved
        # release because it sees security_review=None.
        build = self.get(build_id)

        repaired_for_security = False

        if (
            review.decision == "Block release"
            and build.proof is not None
            and build.proof.generator_mode == "foundry-agent"
        ):
            review, build, repaired_for_security = await self._repair_security_findings(
                build,
                review,
                repair_limit=2,
            )

        if repaired_for_security and review.decision != "Block release":
            # Security remediation changes the source after the previous
            # artifact approval. Require a fresh human approval before proof
            # and release continue with the corrected files.
            self._set_agent(
                build,
                "Security Reviewer",
                "Ready",
                "Security findings were remediated; updated artifacts need approval",
            )
            build.stage = "Prove"
            build.progress = 72
            build.approval_gate = "artifacts"
            build.status = "Awaiting Approval"
            build.error = None
            self._add_event(
                build,
                "Security",
                "Coder Agent remediated security findings. Review and approve the updated artifacts before validation continues.",
                "Security Reviewer",
                severity="warning",
                metadata={
                    "decision": review.decision,
                    "findings": len(review.findings),
                    "remediation_iterations": build.metrics.self_heal_iterations,
                },
            )
            self._build_repository.save(build)
            return

        # --------------------------------------------------------
        # POC RELEASE POLICY
        # --------------------------------------------------------
        #
        # For the POC we only block when the local Security
        # Reviewer reports a real release-blocking finding.
        #
        # The following enterprise integrations are intentionally
        # NOT required for the POC:
        #
        #   - Dependency CVE scanning
        #   - Container image vulnerability scanning
        #   - Azure Policy evaluation
        #   - Deployment verification
        #
        # These can be added later without changing the overall
        # agent workflow.
        # --------------------------------------------------------

        blocking = review.decision == "Block release"

        if blocking:
            self._set_agent(
                build,
                "Security Reviewer",
                "Blocked",
                "High or critical security findings "
                "require remediation",
            )

            build.approval_gate = None
            build.status = "Blocked"

            build.error = (
                "Release is blocked because high or critical "
                "security findings were detected."
            )

            build.progress = 88

            self._add_event(
                build,
                "Security",
                "POC security gate blocked the release",
                "Security Reviewer",
                severity="error",
                metadata={
                    "decision": review.decision,
                    "mode": review.mode,
                    "findings": len(review.findings),
                    "external_scans": review.external_scans,
                    "poc": True,
                },
            )

            self._build_repository.save(build)
            return

        # --------------------------------------------------------
        # POC SECURITY PASSED
        # --------------------------------------------------------

        self._set_agent(
            build,
            "Security Reviewer",
            "Ready",
            "POC security checks passed; enterprise "
            "release integrations are deferred",
        )

        self._add_event(
            build,
            "Security",
            "POC security gate passed; enterprise release "
            "integrations are deferred",
            "Security Reviewer",
            severity="info",
            metadata={
                "decision": review.decision,
                "mode": review.mode,
                "findings": len(review.findings),
                "external_scans": review.external_scans,
                "poc": True,
            },
        )

        # --------------------------------------------------------
        # Move to human release approval.
        # --------------------------------------------------------

        build.approval_gate = "release"
        build.status = "Awaiting Approval"
        build.progress = 93

        self._build_repository.save(build)

    async def _repair_security_findings(
        self,
        build: BuildState,
        review: SecurityReview,
        *,
        repair_limit: int,
    ) -> tuple[SecurityReview, BuildState, bool]:
        """Use bounded Coder repairs for generated-source security findings."""
        repaired_any = False
        remaining = repair_limit

        for attempt in range(1, remaining + 1):
            if review.decision != "Block release" or build.proof is None or build.blueprint is None:
                break

            self._set_agent(
                build,
                "Coder Agent",
                "Running",
                f"Repairing security findings (attempt {attempt} of {remaining})",
            )
            self._build_repository.save(build)

            coder_recipes = skill_registry.retrieve(
                agent="Coder Agent",
                query=self._skill_query(build),
                limit=5,
            )
            try:
                repaired = await self._agent_service.run_coder_agent(
                    title=build.title,
                    blueprint=build.blueprint,
                    requirements=build.requirements,
                    acceptance_criteria=build.acceptance_criteria,
                    skills=coder_recipes,
                    previous_artifacts=build.proof.artifacts,
                    repair_findings=[
                        finding.model_dump(by_alias=True)
                        for finding in review.findings
                    ],
                )
            except Exception as exc:
                self._set_agent(
                    build,
                    "Coder Agent",
                    "Failed",
                    f"Security remediation failed ({type(exc).__name__})",
                )
                self._add_event(
                    build,
                    "Security",
                    "Coder Agent could not produce a valid security remediation; release remains blocked.",
                    "Coder Agent",
                    severity="error",
                    metadata={"attempt": attempt, "error_type": type(exc).__name__},
                )
                self._build_repository.save(build)
                break
            if repaired.mode == "foundry-agent":
                self._record_skill_retrieval(build, coder_recipes, "Coder Agent")

            build.proof.artifacts = repaired.files
            build.proof.files = list(repaired.files)
            build.proof.code = repaired.files
            build.metrics.tokens += repaired.tokens
            build.metrics.tool_calls += int(repaired.mode == "foundry-agent")
            build.metrics.self_heal_iterations += 1
            build.skills_used.extend(repaired.skills_used)
            repaired_any = True
            self._set_agent(build, "Coder Agent", "Ready", "Generated corrected artifacts")

            self._add_event(
                build,
                "Security",
                f"Coder Agent produced security remediation attempt {attempt} of {remaining}",
                "Coder Agent",
                severity="warning",
                metadata={"findings": len(review.findings)},
            )
            self._build_repository.save(build)

            critic_recipes = skill_registry.retrieve(
                agent="Critic Agent",
                query=self._skill_query(build),
                limit=5,
            )
            critic = await self._agent_service.run_critic_agent(
                title=build.title,
                blueprint=build.blueprint,
                requirements=build.requirements,
                acceptance_criteria=build.acceptance_criteria,
                artifacts=build.proof.artifacts,
                skills=critic_recipes,
            )
            build.proof.critic_mode = critic.mode
            build.proof.critic_summary = critic.summary
            build.proof.critic_findings = critic.findings
            build.proof.requirement_coverage = critic.requirement_coverage
            build.proof.test_plan = critic.test_plan
            build.proof.checks = critic.checks
            build.proof.runtime_status = critic.runtime_status
            build.proof.integration = critic.runtime_status

            critic_blockers = (
                any(value == "Failed" for value in critic.checks.values())
                or any(item.severity == "Critical" for item in critic.findings)
                or not critic.runtime_status.lower().startswith("passed")
            )
            if critic_blockers:
                review.findings.extend(
                    item for item in critic.findings if item not in review.findings
                )
                review = review.model_copy(update={"decision": "Block release"})
                self._set_agent(
                    build,
                    "Critic Agent",
                    "Blocked",
                    "Remediated artifacts did not pass source and runtime validation",
                )
                self._build_repository.save(build)
                continue

            self._set_agent(build, "Critic Agent", "Ready", critic.runtime_status)
            # Security review reloads from durable storage, so persist the new
            # Critic result first instead of restoring the previous snapshot.
            self._build_repository.save(build)
            review = await self.run_security_review(build.id)
            build = self.get(build.id)

        return review, build, repaired_any

    async def run_security_review(
        self,
        build_id: str,
    ) -> SecurityReview:
        """Run the local Security Reviewer over generated source."""

        build = self.get(build_id)

        if (
            build.proof is None
            or not build.proof.artifacts
        ):
            raise ValueError(
                "Generate code artifacts before running "
                "the Security Reviewer"
            )

        self._set_agent(
            build,
            "Security Reviewer",
            "Running",
            "Inspecting generated artifacts without executing them",
        )

        self._build_repository.save(build)

        recipes = skill_registry.retrieve(
            agent="Security Reviewer",
            query=self._skill_query(build),
            limit=5,
        )

        review = await self._agent_service.run_security_reviewer(
            artifacts=build.proof.artifacts,
            skills=recipes,
            requirements=build.requirements,
            security_controls=(
                build.blueprint.security
                if build.blueprint
                else build.security_considerations
            ),
            blueprint_choices={
                "deployment": build.blueprint.deployment,
                "identity": build.blueprint.identity,
            }
            if build.blueprint
            else {},
        )

        build.security_review = review

        self._record_skill_retrieval(
            build,
            recipes,
            "Security Reviewer",
        )

        blockers = review.decision == "Block release"

        self._set_agent(
            build,
            "Security Reviewer",
            "Blocked" if blockers else "Ready",
            f"{review.mode}: "
            f"{len(review.findings)} finding(s); "
            f"external scans not required for POC",
        )

        self._add_event(
            build,
            "Security",
            review.summary,
            "Security Reviewer",
            severity="error" if blockers else "warning",
            metadata={
                "decision": review.decision,
                "mode": review.mode,
                "findings": len(review.findings),
                "external_scans": review.external_scans,
                "skills": [
                    item.id
                    for item in recipes
                ],
            },
        )

        self._build_repository.save(build)

        return review

    # ============================================================
    # RELEASE PUBLICATION
    # ============================================================

    def accept_deployment_callback(self, build_id: str, callback: DeploymentCallback) -> tuple[BuildState, bool]:
        from .deployment_repair import clean_diagnostics
        build = self.get(build_id)
        if build.feature_branch != callback.branch:
            raise ValueError("Deployment callback branch does not match this build.")
        if not build.deployment_commit:
            # Existing builds published before commit tracking retain the SHA
            # in their audit trail. Never adopt an arbitrary callback commit.
            for event in reversed(build.audit):
                commit = event.metadata.get("commit")
                if event.metadata.get("branch") == build.feature_branch and commit:
                    build.deployment_commit = commit
                    self._build_repository.save(build)
                    break
        if callback.commit_sha and build.deployment_commit and callback.commit_sha != build.deployment_commit:
            return build, False
        if build.deployment_status == "succeeded":
            return build, False
        if build.deployment_repairing and callback.phase != "repair_timeout":
            return build, False
        if build.deployment_commit and not callback.commit_sha:
            raise ValueError("This build requires commitSha in deployment callbacks; update the deployment workflow.")
        callback = callback.model_copy(update={
            "message": clean_diagnostics(callback.message),
            "diagnostics": clean_diagnostics(callback.diagnostics),
        })
        if callback.phase == "repair_timeout":
            build.deployment_repairing = False
        # Legacy workflows still report status, but cannot safely trigger repair
        # without an exact commit correlation and real diagnostics.
        can_repair = (
            callback.status == "failed" and callback.phase in {"packaging", "image_build", "startup"}
            and callback.diagnostics and callback.commit_sha and build.deployment_commit == callback.commit_sha
            and build.deployment_repair_attempts < 3
        )
        claim = callback.commit_sha + ("-" + callback.repair_request_id if callback.repair_request_id else "")
        if can_repair and self._build_repository.claim_deployment_repair(build_id, claim):
            build.deployment_failure_diagnostics = callback.diagnostics
            build.deployment_repair_review = {}
            build.deployment_repair_attempts += 1
            build.deployment_repairing = True
            build.deployment_status = "running"
            build.status = "Running"
            build.stage = "Release"
            build.error = None
            self._set_agent(build, "Coder Agent", "Running", f"Repairing actual deployment failure ({build.deployment_repair_attempts}/3)")
            self._add_event(build, "Deployment Repair", f"Container {callback.phase} failed; automatic repair {build.deployment_repair_attempts}/3 started", "Coder Agent", metadata={"commit": callback.commit_sha})
            self._build_repository.save(build)
            return build, True
        if can_repair:
            return self.get(build_id), False
        if callback.status == "failed" and build.deployment_repair_attempts >= 3:
            callback = callback.model_copy(update={"message": "Automatic repair limit reached (3). " + callback.message})
        return self.record_deployment(build_id, callback), False

    def record_deployment(self, build_id: str, callback: DeploymentCallback) -> BuildState:
        build = self.get(build_id)
        if build.feature_branch != callback.branch:
            raise ValueError("The deployment callback branch does not match the published build branch yet.")
        if callback.status == "succeeded":
            if not callback.url:
                raise ValueError("A successful deployment callback must include its application URL.")
            build.deployment_status = "succeeded"
            build.deployed_url = callback.url
            build.status = "Deployed"
            build.progress = 100
            build.error = None
            self._set_agent(build, "Deployer Agent", "Ready", "Application deployed and smoke test passed")
            self._add_event(
                build,
                "Deployment",
                "Generated application deployed to Azure Container Apps and passed its smoke test",
                "Deployer Agent",
                metadata={"url": callback.url, "branch": callback.branch},
            )
            if build.skill_proposal and build.skill_proposal.recipe:
                try:
                    candidate = SkillRecipe.model_validate(build.skill_proposal.recipe)
                    draft = skill_registry.save_repair_candidate(candidate, build_id=build.id)
                    build.skill_proposal.recipe = draft.model_dump(by_alias=True)
                    build.skill_proposal.name = draft.title
                    build.skill_proposal.version = draft.version
                    build.skill_proposal.status = "Pending Approval"
                    self._set_agent(build, "Skill Agent", "Ready", "Deployment-verified skill candidate saved as a draft")
                    self._add_event(
                        build,
                        "Skills",
                        f"Deployment-verified skill candidate saved as draft: {draft.title}",
                        "Skill Evolver",
                        severity="warning",
                        metadata={"skill_id": draft.id, "version": draft.version},
                    )
                except Exception as exc:
                    # Candidate storage must never invalidate a successful app deployment.
                    self._add_event(
                        build,
                        "Skills",
                        "Deployment succeeded, but its optional skill candidate could not be saved.",
                        "Skill Evolver",
                        severity="warning",
                        metadata={"error_type": type(exc).__name__},
                    )
        else:
            message = callback.message.strip()[:1000] or "Generated application deployment failed."
            build.deployment_status = "failed"
            build.status = "Failed"
            build.error = message
            build.deployment_repairing = False
            self._set_agent(build, "Deployer Agent", "Failed", message)
            self._add_event(
                build,
                "Deployment",
                message,
                "Deployer Agent",
                severity="error",
                metadata={"branch": callback.branch},
            )
        self._build_repository.save(build)
        return build

    async def _deploy(self, build: BuildState) -> None:
        build.stage = "Release"
        build.progress = 95

        self._set_agent(
            build,
            "Deployer Agent",
            "Running",
            "Publishing reviewed source to a new GitHub feature branch",
        )

        self._build_repository.save(build)

        if build.proof is None or not build.proof.artifacts:
            raise RuntimeError("Release stopped: no generated artifacts are available to publish.")
        if build.security_review is None or build.security_review.decision == "Block release":
            raise RuntimeError("Release stopped: the Security Reviewer has not approved these artifacts.")
        if not build.proof.runtime_status.lower().startswith("passed"):
            raise RuntimeError("Release stopped: isolated runtime validation must pass before publishing.")

        published = await GitHubPublisher().publish(build)
        build.feature_branch = published["branch"]
        build.feature_branch_url = published["branch_url"]
        build.repository_url = published["repository_url"]
        build.deployment_commit = published["commit_sha"]
        build.deployment_repair_attempts = 0
        build.deployment_repairing = False

        self._set_agent(build, "Deployer Agent", "Running", f"Deploying {build.feature_branch} to Azure Container Apps")
        self._add_event(
            build,
            "GitHub Publish",
            f"Reviewed source committed to {build.feature_branch}",
            "Deployer Agent",
            metadata={"branch": build.feature_branch, "branch_url": build.feature_branch_url, "commit": published["commit_sha"]},
        )

        # Feature-branch push triggers the generated-app deployment workflow.
        # It reports a verified URL through the authenticated callback endpoint.
        build.stage = "Release"
        build.approval_gate = None
        build.deployment_status = "running"
        build.progress = 96
        build.error = None
        build.status = "Running"
        self._add_event(
            build,
            "Deployment Started",
            "Source is published. Azure Container Apps is building and deploying the generated application.",
            "Deployer Agent",
            metadata={"branch": build.feature_branch},
        )

        self._build_repository.save(build)

    async def prepare_deployment(
        self,
        build_id: str,
    ) -> DeploymentPlan:
        build = self.get(build_id)
        self._set_agent(
            build,
            "Deployer Agent",
            "Running",
            "Checking Azure deployment prerequisites",
        )
        self._build_repository.save(build)
        plan = await self._agent_service.prepare_deployment(build)
        build.deployment_plan = plan
        status = "Ready" if plan.status == "ready" else "Blocked"
        self._set_agent(build, "Deployer Agent", status, plan.summary)
        self._add_event(
            build,
            "Deploy Preflight",
            plan.summary,
            "Deployer Agent",
            severity="info" if plan.status == "ready" else "warning",
            metadata={
                "target": plan.target,
                "image_tag": plan.image_tag,
                "blockers": plan.blockers,
                "files": len(plan.artifact_manifest),
            },
        )
        self._build_repository.save(build)
        return plan

    # ============================================================
    # HUMAN APPROVAL
    # ============================================================

    async def approve(
        self,
        build_id: str,
        gate: str,
    ) -> BuildState:
        build = self.get(build_id)

        if build.approval_gate != gate:
            raise ValueError(
                f"Approval gate '{gate}' is not active"
            )

        if (
            gate == "skill"
            and not build.skill_proposal
        ):
            raise ValueError(
                "There is no generated skill proposal "
                "pending approval for this build"
            )

        self._add_event(
            build,
            "Approval",
            f"Human approved {gate}",
            "User",
            metadata={
                "gate": gate,
            },
        )

        build.approval_gate = None
        build.status = "Running"

        owner, detail = {
            "requirements": (
                "Architecture Agent",
                "Designing the approved requirements",
            ),
            "blueprint": (
                "Coder Agent",
                "Generating the approved application",
            ),
            "artifacts": (
                "Critic Agent",
                "Reviewing generated artifacts",
            ),
            "skill": (
                "Security Reviewer",
                "Running security checks after skill approval",
            ),
            "release": (
                "Deployer Agent",
                "Processing the approved release",
            ),
        }[gate]

        self._set_agent(
            build,
            owner,
            "Running",
            detail,
        )

        self._build_repository.save(build)

        # Return persisted Running state immediately.
        # Agent calls can exceed HTTP gateway limits.
        task = asyncio.create_task(
            self._complete_approval(
                build_id,
                gate,
            )
        )

        self._approval_tasks[build_id] = task

        task.add_done_callback(
            lambda _task, key=build_id:
            self._approval_tasks.pop(key, None)
        )

        return build

    async def _complete_approval(
        self,
        build_id: str,
        gate: str,
    ) -> None:
        build = self.get(build_id)

        if gate == "requirements":
            try:
                await self._design(build)

            except Exception as exc:
                self._fail(build, str(exc))
                self._build_repository.save(build)
                return

            build.approval_gate = "blueprint"
            build.stage = "Design"
            build.status = "Awaiting Approval"
            build.progress = 38

        elif gate == "blueprint":
            try:
                await self._forge(build)

            except Exception as exc:
                self._fail(build, str(exc))
                self._build_repository.save(build)
                return

        elif gate == "artifacts":
            try:
                await self._prove(build)
                # _prove can enter _security(), which persists through its own
                # repository load. Keep that completed state instead of saving
                # this pre-review snapshot at the end of this task.
                build = self.get(build_id)

            except Exception as exc:
                self._fail(build, str(exc))
                self._build_repository.save(build)
                return

        elif gate == "skill":
            assert build.skill_proposal is not None

            build.skill_proposal.status = "Approved"

            self._set_agent(
                build,
                "Skill Agent",
                "Ready",
                "Skill version approved and promoted",
            )

            self._add_event(
                build,
                "Skills",
                f"{build.skill_proposal.name} "
                f"{build.skill_proposal.version} "
                "promoted after human approval",
                "Skill Agent",
            )

            try:
                await self._security(build)
                # _security refreshes and saves the build after its review.
                # Reload it before the common save below so the review result,
                # final status, and approval gate are not replaced by stale data.
                build = self.get(build_id)

            except Exception as exc:
                self._fail(build, str(exc))

        elif gate == "release":
            try:
                await self._deploy(build)

            except Exception as exc:
                self._fail(build, str(exc))

        self._build_repository.save(build)

    # ============================================================
    # BLUEPRINT
    # ============================================================

    def update_blueprint(
        self,
        build_id: str,
        payload: BlueprintUpdate,
    ) -> BuildState:
        build = self.get(build_id)

        if (
            build.approval_gate != "blueprint"
            or build.blueprint is None
        ):
            raise ValueError(
                "Blueprint edits are only allowed while "
                "the blueprint approval is pending"
            )

        fields = (
            "application",
            "frontend",
            "backend",
            "data",
            "storage",
            "messaging",
            "identity",
            "deployment",
            "security",
        )

        changed = [
            field
            for field in fields
            if getattr(
                build.blueprint,
                field,
            )
            != getattr(
                payload,
                field,
            )
        ]

        for field in fields:
            setattr(
                build.blueprint,
                field,
                getattr(payload, field),
            )

        if changed:
            self._add_event(
                build,
                "Design",
                "Human updated blueprint choices",
                "User",
                metadata={
                    "fields": changed,
                },
            )

        self._build_repository.save(build)

        return build

    # ============================================================
    # REFINE
    # ============================================================

    async def refine(
        self,
        build_id: str,
        text: str,
    ) -> BuildState:
        build = self.get(build_id)

        build.source_text = (
            f"{build.source_text}\n"
            f"Clarification: {text}"
        )

        build.status = "Refined"
        build.approval_gate = None

        self._add_event(
            build,
            "Refine",
            "Human clarification added",
            "User",
        )

        self._build_repository.save(build)

        return await self.start(build_id)

    # ============================================================
    # HELPERS
    # ============================================================

    def get(self, build_id: str) -> BuildState:
        return self._build_repository.get(build_id)

    @staticmethod
    def _set_agent(
        build: BuildState,
        name: str,
        status: str,
        detail: str,
    ) -> None:
        for agent in build.agents:
            if agent.name == name:
                agent.status = status  # type: ignore[assignment]
                agent.detail = detail
                agent.last_action = detail
                return

    def _add_event(
        self,
        build: BuildState,
        stage: str,
        message: str,
        agent: str | None = None,
        severity: str = "info",
        metadata: dict[str, object] | None = None,
    ) -> None:
        build.audit.append(
            AuditEvent(
                time=self._time(),
                stage=stage,
                message=message,
                agent=agent,
                severity=severity,
                metadata=metadata or {},
            )
        )

    def _fail(
        self,
        build: BuildState,
        message: str,
    ) -> None:
        build.status = "Failed"
        build.stage = "Error"
        build.error = message

        for agent in build.agents:
            if agent.status == "Running":
                agent.status = "Failed"
                agent.detail = message
                agent.last_action = message

        self._add_event(
            build,
            "Error",
            message,
            "Orchestrator",
            severity="error",
        )

    @staticmethod
    def _slug(value: str) -> str:
        import re

        return (
            re.sub(
                r"[^a-z0-9]+",
                "-",
                value.lower(),
            ).strip("-")
            or "autoforge"
        )
