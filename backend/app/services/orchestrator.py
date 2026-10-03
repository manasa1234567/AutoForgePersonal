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
    DeploymentPlan,
    ProofResult,
    SecurityReview,
    SkillRecipe,
    SkillUsage,
)
from .agent_service import AgentService
from .azure_adapters import AzureAdapters
from ..repositories.build_repository import BuildRepository, build_repository_from_environment
from .skill_registry import skill_registry
from .jira_client import JiraClient
from .job_dispatcher import BuildJobDispatcher, InProcessBuildJobDispatcher
from .source_documents import extract_source_documents


class Orchestrator:
    """Coordinates the governed AutoForge workflow in demo mode."""

    def __init__(
        self,
        build_repository: BuildRepository | None = None,
        job_dispatcher: BuildJobDispatcher | None = None,
    ) -> None:
        self._build_repository = build_repository or build_repository_from_environment()
        self._azure = AzureAdapters()
        self._agent_service = AgentService()
        self._jira = JiraClient()
        self._job_dispatcher = job_dispatcher or InProcessBuildJobDispatcher(self._run_until_gate)
        self._approval_tasks: dict[str, asyncio.Task[None]] = {}

    @staticmethod
    def _time() -> str:
        return datetime.now(timezone.utc).strftime("%H:%M:%S")

    @staticmethod
    def _skill_query(build: BuildState) -> str:
        parts = [build.title, build.source_type, build.source_text]
        parts.extend(str(item.get("text", "")) for item in build.requirements)
        parts.extend(build.acceptance_criteria)
        if build.blueprint:
            parts.extend([
                build.blueprint.frontend,
                build.blueprint.backend,
                build.blueprint.data,
                *build.blueprint.security,
            ])
        return " ".join(part for part in parts if part)

    def _record_skill_retrieval(self, build: BuildState, recipes: list[SkillRecipe], agent: str) -> None:
        if not recipes:
            return
        build.skills_used.extend(
            SkillUsage(id=recipe.id, version=recipe.version, usage="retrieved") for recipe in recipes
        )
        self._add_event(
            build,
            "Skills",
            f"Retrieved {len(recipes)} approved recipe(s) for {agent}",
            "Skill Registry",
            metadata={"agent": agent, "skills": [recipe.id for recipe in recipes]},
        )

    @staticmethod
    def _agents() -> list[AgentState]:
        return [
            AgentState(name="Spec Agent", role="Understand and refine requirements"),
            AgentState(name="Architecture Agent", role="Design solution and technology stack"),
            AgentState(name="Coder Agent", role="Generate code, tests and skills"),
            AgentState(name="Critic Agent", role="Validate, test and self-heal"),
            AgentState(name="Skill Agent", role="Manage, evolve and promote reusable skills"),
            AgentState(name="Security Reviewer", role="Run security and policy checks"),
            AgentState(name="Deployer Agent", role="Build, scan and deploy"),
        ]

    def create(self, payload: BuildCreate) -> BuildState:
        extracted_documents = extract_source_documents(payload.file_contents)
        if payload.source_type == "openapi":
            if len(extracted_documents) > 1 or (payload.source_text.strip() and extracted_documents):
                raise ValueError("Provide one OpenAPI contract as pasted text or one uploaded file")
            if extracted_documents and not extracted_documents[0][0].lower().endswith((".yaml", ".yml", ".json")):
                raise ValueError("OpenAPI source files must be YAML or JSON")
            source_text = extracted_documents[0][1] if extracted_documents else payload.source_text.strip()
        else:
            sections = [payload.source_text.strip()] if payload.source_text.strip() else []
            sections.extend(f"Source document: {name}\n{text}" for name, text in extracted_documents)
            source_text = "\n\n".join(sections)

        if payload.source_type == "upload" and not extracted_documents:
            raise ValueError("Select at least one engineering document to analyze")
        if len(source_text) > 20_000:
            raise ValueError("Combined input and extracted document text exceeds the 20,000 character limit")

        build_id = str(uuid4())[:8]
        build = BuildState(
            id=build_id,
            title=payload.title,
            source_type=payload.source_type,
            source_text=source_text,
            files=payload.files or [name for name, _ in extracted_documents],
            agents=self._agents(),
        )
        self._add_event(build, "Intake", "Requirement submitted", "Orchestrator", metadata={"source_type": payload.source_type})
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
        except Exception as exc:  # pragma: no cover - demo failure path
            self._fail(build, str(exc))
            self._build_repository.save(build)

    async def _understand(self, build: BuildState) -> None:
        build.status = "Running"
        build.stage = "Understand"
        self._set_agent(build, "Spec Agent", "Running", "Extracting requirements and checking source")
        self._add_event(build, "Understand", "Spec Agent started requirement extraction", "Spec Agent")
        self._build_repository.save(build)

        if build.source_type == "jira":
            issue = await self._jira.get_issue(build.source_text)
            build.title = issue.summary[:160]
            source_parts = [f"Jira issue: {issue.key}"]
            if issue.issue_type:
                source_parts.append(f"Issue type: {issue.issue_type}")
            source_parts.append(f"Summary: {issue.summary}")
            if issue.description:
                source_parts.append(f"Description:\n{issue.description}")
            if issue.acceptance_criteria:
                source_parts.append(f"Acceptance criteria:\n{issue.acceptance_criteria}")
            build.source_text = "\n\n".join(source_parts)[:20_000]
            self._add_event(
                build,
                "Intake",
                f"Jira issue {issue.key} retrieved for analysis",
                "Orchestrator",
                metadata={"issue_key": issue.key},
            )

        safety_result = await self._azure.content_safety_check(build.source_text)
        if bool(safety_result["blocked"]):
            raise RuntimeError(f"Input blocked by AI safety policy: {safety_result['reason']}")

        recipes = skill_registry.retrieve(agent="Spec Agent", query=self._skill_query(build), limit=5)
        result = await self._agent_service.run_spec_agent(
            title=build.title,
            source_type=build.source_type,
            source_text=build.source_text,
            skills=recipes,
        )
        if result.mode in {"foundry-agent", "azure-openai"}:
            self._record_skill_retrieval(build, recipes, "Spec Agent")
        build.requirements = result.requirements
        build.requirement_summary = result.summary
        build.acceptance_criteria = result.acceptance_criteria
        build.dependencies = result.dependencies
        build.constraints = result.constraints
        build.ambiguities = result.ambiguities
        build.assumptions = result.assumptions
        build.risks = result.risks
        build.security_considerations = result.security_considerations
        build.clarification_questions = result.clarification_questions
        build.spec_confidence = result.confidence
        build.spec_readiness = result.readiness
        build.agent_mode = result.mode
        build.metrics.tokens += result.tokens
        build.metrics.tool_calls += 3
        self._set_agent(build, "Spec Agent", "Ready", f"{len(result.requirements)} requirements extracted")
        self._add_event(
            build,
            "Understand",
            "Spec Agent completed requirement extraction",
            "Spec Agent",
            metadata={"count": len(result.requirements), "confidence": result.confidence, "mode": result.mode},
        )

    async def _design(self, build: BuildState) -> None:
        self._set_agent(build, "Architecture Agent", "Running", "Creating solution blueprint")
        self._build_repository.save(build)
        recipes = skill_registry.retrieve(agent="Architecture Agent", query=self._skill_query(build), limit=5)
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
            self._record_skill_retrieval(build, recipes, "Architecture Agent")
        build.blueprint = result.blueprint
        build.metrics.tokens += result.tokens
        if result.mode == "foundry-agent":
            build.metrics.tool_calls += 1
        self._set_agent(build, "Architecture Agent", "Ready", f"Blueprint ready for approval ({result.mode})")
        self._add_event(
            build,
            "Design",
            "Architecture blueprint generated",
            "Architecture Agent",
            metadata={"mode": result.mode, "open_questions": len(result.blueprint.open_questions)},
        )
        self._build_repository.save(build)

    async def _forge(self, build: BuildState) -> None:
        self._set_agent(build, "Coder Agent", "Running", "Generating application, tests and reusable skill")
        build.stage = "Forge"
        build.progress = 58
        self._build_repository.save(build)
        if build.blueprint is None:
            raise RuntimeError("An approved architecture blueprint is required before code generation")
        coder_recipes = skill_registry.retrieve(agent="Coder Agent", query=self._skill_query(build), limit=5)
        result = await self._agent_service.run_coder_agent(
            title=build.title,
            blueprint=build.blueprint,
            requirements=build.requirements,
            acceptance_criteria=build.acceptance_criteria,
            skills=coder_recipes,
        )
        if result.mode == "foundry-agent":
            self._record_skill_retrieval(build, coder_recipes, "Coder Agent")
        build.proof = ProofResult(
            files=list(result.files),
            artifacts=result.files,
            generator_mode=result.mode,
            integration="Not run",
        )
        build.skills_used.extend(result.skills_used)
        applied_skills = [skill for skill in result.skills_used if skill.usage == "applied"]
        skipped_skills = [skill for skill in result.skills_used if skill.usage == "skipped"]
        if applied_skills:
            self._add_event(
                build,
                "Skills",
                f"Coder Agent applied {len(applied_skills)} approved skill recipe(s)",
                "Skill Agent",
                metadata={"skills": [skill.model_dump(by_alias=True) for skill in applied_skills]},
            )
        if skipped_skills:
            self._add_event(
                build,
                "Skills",
                f"Coder Agent skipped {len(skipped_skills)} retrieved recipe(s)",
                "Skill Agent",
                metadata={"skills": [skill.model_dump(by_alias=True) for skill in skipped_skills]},
            )
        build.metrics.tokens += result.tokens
        if result.mode == "foundry-agent":
            build.metrics.tool_calls += 1
        self._set_agent(build, "Coder Agent", "Ready", f"Generated {len(result.files)} file(s) ({result.mode})")
        self._add_event(
            build,
            "Forge",
            "Code artifacts generated from the approved blueprint",
            "Coder Agent",
            metadata={"files": len(build.proof.files), "mode": result.mode},
        )
        build.stage = "Forge"
        build.status = "Awaiting Approval"
        build.approval_gate = "artifacts"
        build.progress = 66
        self._build_repository.save(build)

    async def _prove(self, build: BuildState) -> None:
        self._set_agent(build, "Critic Agent", "Running", "Reviewing generated artifacts without executing them")
        build.stage = "Prove"
        build.progress = 72
        self._build_repository.save(build)

        if build.proof is None:
            raise RuntimeError("Proof result is missing before critic execution")
        if build.blueprint is None:
            raise RuntimeError("The approved blueprint is missing before Critic review")
        critic_recipes = skill_registry.retrieve(agent="Critic Agent", query=self._skill_query(build), limit=5)
        result = await self._agent_service.run_critic_agent(
            title=build.title,
            blueprint=build.blueprint,
            requirements=build.requirements,
            acceptance_criteria=build.acceptance_criteria,
            artifacts=build.proof.artifacts,
            skills=critic_recipes,
        )
        if result.mode == "foundry-static-review":
            self._record_skill_retrieval(build, critic_recipes, "Critic Agent")
        repair_limit = 2
        for attempt in range(1, repair_limit + 1):
            if (
                not result.runtime_status.lower().startswith("failed")
                or not result.mode.startswith("foundry-static-review")
                or build.proof.generator_mode != "foundry-agent"
                or os.getenv("AUTOFORGE_SANDBOX_ENABLED", "false").lower() != "true"
            ):
                break
            self._set_agent(build, "Coder Agent", "Running", f"Repair attempt {attempt} of {repair_limit} from Critic findings")
            repair_recipes = skill_registry.retrieve(agent="Coder Agent", query=self._skill_query(build), limit=5)
            repaired = await self._agent_service.run_coder_agent(
                title=build.title,
                blueprint=build.blueprint,
                requirements=build.requirements,
                acceptance_criteria=build.acceptance_criteria,
                skills=repair_recipes,
                previous_artifacts=build.proof.artifacts,
                repair_findings=[finding.model_dump(by_alias=True) for finding in result.findings],
            )
            if repaired.mode == "foundry-agent":
                self._record_skill_retrieval(build, repair_recipes, "Coder Agent")
            build.proof.files = list(repaired.files)
            build.proof.artifacts = repaired.files
            build.proof.code = repaired.files
            build.skills_used.extend(repaired.skills_used)
            applied_repair_skills = [skill for skill in repaired.skills_used if skill.usage == "applied"]
            skipped_repair_skills = [skill for skill in repaired.skills_used if skill.usage == "skipped"]
            if applied_repair_skills or skipped_repair_skills:
                self._add_event(
                    build,
                    "Skills",
                    f"Repair pass applied {len(applied_repair_skills)} recipe(s) and skipped {len(skipped_repair_skills)}",
                    "Skill Agent",
                    metadata={"skills": [skill.model_dump(by_alias=True) for skill in repaired.skills_used]},
                )
            build.metrics.tokens += repaired.tokens
            if repaired.mode == "foundry-agent":
                build.metrics.tool_calls += 1
            build.metrics.self_heal_iterations += 1
            self._set_agent(build, "Coder Agent", "Ready", f"Generated a revised artifact set ({repaired.mode})")
            self._add_event(
                build,
                "Prove",
                f"Coder Agent revised artifacts after sandbox failure (attempt {attempt} of {repair_limit})",
                "Coder Agent",
                severity="warning",
                metadata={"attempt": attempt, "prior_findings": len(result.findings)},
            )
            self._build_repository.save(build)
            critic_recipes = skill_registry.retrieve(agent="Critic Agent", query=self._skill_query(build), limit=5)
            result = await self._agent_service.run_critic_agent(
                title=build.title,
                blueprint=build.blueprint,
                requirements=build.requirements,
                acceptance_criteria=build.acceptance_criteria,
                artifacts=build.proof.artifacts,
                skills=critic_recipes,
            )
            if result.mode == "foundry-static-review":
                self._record_skill_retrieval(build, critic_recipes, "Critic Agent")
        build.proof.critic_mode = result.mode
        build.proof.critic_summary = result.summary
        build.proof.critic_findings = result.findings
        build.proof.requirement_coverage = result.requirement_coverage
        build.proof.test_plan = result.test_plan
        build.proof.checks = result.checks
        build.proof.runtime_status = result.runtime_status
        build.proof.integration = result.runtime_status
        if result.mode.startswith("foundry-static-review"):
            build.metrics.tool_calls += 1
        critical_findings = any(finding.severity == "Critical" for finding in result.findings)
        runtime_pending = not result.runtime_status.lower().startswith("passed") or critical_findings
        self._set_agent(
            build,
            "Critic Agent",
            "Blocked" if runtime_pending else "Ready",
            f"Review complete ({result.mode}); {result.runtime_status}",
        )
        if runtime_pending:
            waiting_reason = "Awaiting isolated runtime validation" if result.runtime_status.lower().startswith("not run") else "Awaiting a passing build and test run"
            self._set_agent(build, "Skill Agent", "Blocked", waiting_reason)
        self._add_event(
            build,
            "Prove",
            "Source review completed; runtime validation was not run"
            if result.runtime_status.lower().startswith("not run")
            else f"Source review and runtime validation completed: {result.runtime_status}",
            "Critic Agent",
            severity="warning" if result.findings or "Not run" in result.runtime_status else "info",
            metadata={"mode": result.mode, "findings": len(result.findings), "runtime": result.runtime_status},
        )
        if runtime_pending:
            build.approval_gate = None
            build.status = "Blocked"
            build.progress = 72
            if critical_findings and result.runtime_status.lower().startswith("passed"):
                build.error = "Critical source findings must be resolved before this build can proceed."
            elif result.runtime_status.lower().startswith("not run"):
                build.error = "Runtime validation is blocked until the isolated Azure Container Apps sandbox is configured and enabled."
            else:
                build.error = "Runtime validation did not pass. Review the Critic findings before requesting a corrected build."
            self._build_repository.save(build)
            return

        if build.skill_proposal:
            build.approval_gate = "skill"
            build.status = "Awaiting Approval"
            build.progress = 78
            self._build_repository.save(build)
            return

        self._set_agent(build, "Skill Agent", "Ready", "No eligible reusable skill candidate was produced in this build")
        self._add_event(build, "Skills", "No new reusable skill candidate was promoted by this build", "Skill Agent")
        await self._security(build)

    async def _security(self, build: BuildState) -> None:
        self._set_agent(build, "Security Reviewer", "Running", "Running security and policy checks")
        build.stage = "Release"
        build.progress = 88
        self._build_repository.save(build)
        review = await self.run_security_review(build.id)
        blocking = review.decision == "Block release"
        pending = [name for name, state in review.external_scans.items() if state.startswith("Not run")]
        detail = "High or critical source findings require remediation" if blocking else "Local source review complete"
        if pending:
            detail += "; cloud release checks remain unavailable"
        self._set_agent(build, "Security Reviewer", "Blocked" if blocking or pending else "Ready", detail)
        if blocking or pending:
            build.approval_gate = None
            build.status = "Blocked"
            build.error = (
                "Release is blocked until high or critical source findings are resolved."
                if blocking else
                "Local source review is complete, but dependency CVE, image, Azure policy, and deployment checks "
                "are not configured. Release approval and deployment remain blocked until those integrations are ready."
            )
            build.progress = 88
        else:
            # This branch is reserved for when all release integrations report evidence.
            build.approval_gate = "release"
            build.status = "Awaiting Approval"
            build.progress = 93
        self._build_repository.save(build)

    async def run_security_review(self, build_id: str) -> SecurityReview:
        """Run the local Security Reviewer over generated source without executing it."""
        build = self.get(build_id)
        if build.proof is None or not build.proof.artifacts:
            raise ValueError("Generate code artifacts before running the Security Reviewer")
        self._set_agent(build, "Security Reviewer", "Running", "Inspecting generated artifacts without executing them")
        self._build_repository.save(build)
        recipes = skill_registry.retrieve(agent="Security Reviewer", query=self._skill_query(build), limit=5)
        review = await self._agent_service.run_security_reviewer(
            artifacts=build.proof.artifacts,
            skills=recipes,
            requirements=build.requirements,
            security_controls=build.blueprint.security if build.blueprint else build.security_considerations,
            blueprint_choices={
                "deployment": build.blueprint.deployment,
                "identity": build.blueprint.identity,
            } if build.blueprint else {},
        )
        build.security_review = review
        self._record_skill_retrieval(build, recipes, "Security Reviewer")
        blockers = review.decision == "Block release"
        self._set_agent(
            build,
            "Security Reviewer",
            "Blocked" if blockers else "Ready",
            f"{review.mode}: {len(review.findings)} finding(s); external scans not run locally",
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
                "skills": [item.id for item in recipes],
            },
        )
        self._build_repository.save(build)
        return review

    async def _deploy(self, build: BuildState) -> None:
        plan = await self.prepare_deployment(build.id)
        build.approval_gate = None
        if plan.status != "ready":
            build.status = "Blocked"
            build.stage = "Release"
            build.error = "Deployment was blocked by the Deployer Agent preflight. Review the blockers before retrying."
            self._set_agent(build, "Deployer Agent", "Blocked", plan.summary)
            self._add_event(
                build,
                "Deploy",
                "Deployment was not started because preflight checks are incomplete",
                "Deployer Agent",
                severity="warning",
                metadata={"blockers": plan.blockers},
            )
            self._build_repository.save(build)
            return
        # This code path remains disabled until a reviewed Azure deployment adapter is installed.
        build.status = "Blocked"
        build.stage = "Release"
        build.error = "The Azure deployment adapter is not implemented; no deployment was started."
        self._set_agent(build, "Deployer Agent", "Blocked", build.error)
        self._add_event(build, "Deploy", build.error, "Deployer Agent", severity="warning")
        self._build_repository.save(build)

    async def prepare_deployment(self, build_id: str) -> DeploymentPlan:
        """Run a local deployment preflight and save its artifact manifest; never deploy."""
        build = self.get(build_id)
        self._set_agent(build, "Deployer Agent", "Running", "Preparing deployment manifest and checking gates")
        self._build_repository.save(build)
        plan = await self._agent_service.prepare_deployment(build)
        build.deployment_plan = plan
        self._set_agent(
            build,
            "Deployer Agent",
            "Blocked" if plan.status == "blocked" else "Waiting",
            plan.summary,
        )
        self._add_event(
            build,
            "Deploy Preflight",
            plan.summary,
            "Deployer Agent",
            severity="warning" if plan.status == "blocked" else "info",
            metadata={"target": plan.target, "blockers": plan.blockers, "files": len(plan.artifact_manifest)},
        )
        self._build_repository.save(build)
        return plan

    async def approve(self, build_id: str, gate: str) -> BuildState:
        build = self.get(build_id)
        if build.approval_gate != gate:
            raise ValueError(f"Approval gate '{gate}' is not active")
        if gate == "skill" and not build.skill_proposal:
            raise ValueError("There is no generated skill proposal pending approval for this build")

        self._add_event(build, "Approval", f"Human approved {gate}", "User", metadata={"gate": gate})
        build.approval_gate = None
        build.status = "Running"
        owner, detail = {
            "requirements": ("Architecture Agent", "Designing the approved requirements"),
            "blueprint": ("Coder Agent", "Generating the approved application"),
            "artifacts": ("Critic Agent", "Reviewing generated artifacts"),
            "skill": ("Security Reviewer", "Running security checks after skill approval"),
            "release": ("Deployer Agent", "Processing the approved release"),
        }[gate]
        self._set_agent(build, owner, "Running", detail)
        self._build_repository.save(build)

        # Return the persisted Running state immediately. Agent calls can exceed
        # HTTP gateway limits, so their completion must not hold the approval request open.
        task = asyncio.create_task(self._complete_approval(build_id, gate))
        self._approval_tasks[build_id] = task
        task.add_done_callback(lambda _task, key=build_id: self._approval_tasks.pop(key, None))
        return build

    async def _complete_approval(self, build_id: str, gate: str) -> None:
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
            except Exception as exc:
                self._fail(build, str(exc))
                self._build_repository.save(build)
                return
        elif gate == "skill":
            assert build.skill_proposal is not None
            build.skill_proposal.status = "Approved"
            self._set_agent(build, "Skill Agent", "Ready", "Skill version approved and promoted")
            self._add_event(build, "Skills", f"{build.skill_proposal.name} {build.skill_proposal.version} promoted after human approval", "Skill Agent")
            try:
                await self._security(build)
            except Exception as exc:
                self._fail(build, str(exc))
        elif gate == "release":
            try:
                await self._deploy(build)
            except Exception as exc:
                self._fail(build, str(exc))
        self._build_repository.save(build)

    def update_blueprint(self, build_id: str, payload: BlueprintUpdate) -> BuildState:
        build = self.get(build_id)
        if build.approval_gate != "blueprint" or build.blueprint is None:
            raise ValueError("Blueprint edits are only allowed while the blueprint approval is pending")

        fields = ("application", "frontend", "backend", "data", "storage", "messaging", "identity", "deployment", "security")
        changed = [field for field in fields if getattr(build.blueprint, field) != getattr(payload, field)]
        for field in fields:
            setattr(build.blueprint, field, getattr(payload, field))
        if changed:
            self._add_event(
                build,
                "Design",
                "Human updated blueprint choices",
                "User",
                metadata={"fields": changed},
            )
        self._build_repository.save(build)
        return build

    async def refine(self, build_id: str, text: str) -> BuildState:
        build = self.get(build_id)
        build.source_text = f"{build.source_text}\nClarification: {text}"
        build.status = "Refined"
        build.approval_gate = None
        self._add_event(build, "Refine", "Human clarification added", "User")
        self._build_repository.save(build)
        return await self.start(build_id)

    def get(self, build_id: str) -> BuildState:
        return self._build_repository.get(build_id)

    @staticmethod
    def _set_agent(build: BuildState, name: str, status: str, detail: str) -> None:
        for agent in build.agents:
            if agent.name == name:
                agent.status = status  # type: ignore[assignment]
                agent.detail = detail
                agent.last_action = detail
                return

    def _add_event(self, build: BuildState, stage: str, message: str, agent: str | None = None, severity: str = "info", metadata: dict[str, object] | None = None) -> None:
        build.audit.append(AuditEvent(time=self._time(), stage=stage, message=message, agent=agent, severity=severity, metadata=metadata or {}))

    def _fail(self, build: BuildState, message: str) -> None:
        build.status = "Failed"
        build.stage = "Error"
        build.error = message
        for agent in build.agents:
            if agent.status == "Running":
                agent.status = "Failed"
                agent.detail = message
                agent.last_action = message
        self._add_event(build, "Error", message, "Orchestrator", severity="error")

    @staticmethod
    def _slug(value: str) -> str:
        import re
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "autoforge"
