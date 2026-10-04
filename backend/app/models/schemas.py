from __future__ import annotations

import base64
import binascii
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)


class SourceFileContent(ApiModel):
    name: str = Field(min_length=1, max_length=180)
    content_base64: str = Field(min_length=1, max_length=20_000_000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean = value.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not clean or "." not in clean:
            raise ValueError("Uploaded source files must have a supported file extension")
        extension = "." + clean.rsplit(".", 1)[-1].lower()
        if extension not in {".yaml", ".yml", ".json", ".pdf", ".docx", ".txt", ".md"}:
            raise ValueError(f"Unsupported engineering document type: {extension}")
        return clean

    @field_validator("content_base64")
    @classmethod
    def validate_base64_content(cls, value: str) -> str:
        try:
            base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Uploaded document content is not valid base64") from exc
        return value

SourceType = Literal["jira", "openapi", "architecture", "upload", "usecase", "requirement"]
ApprovalGate = Literal["requirements", "blueprint", "artifacts", "skill", "release"]
SpecReadiness = Literal["READY", "NEEDS_CLARIFICATION"]
SkillStatus = Literal["draft", "pending_approval", "approved", "deprecated", "rejected"]


class BuildCreate(ApiModel):
    source_type: SourceType
    title: str = Field(min_length=3, max_length=160)
    source_text: str = Field(default="", max_length=20_000)
    files: list[str] = Field(default_factory=list, max_length=20)
    file_contents: list[SourceFileContent] = Field(default_factory=list, max_length=10)

    @field_validator("file_contents")
    @classmethod
    def validate_file_content_size(cls, files: list[SourceFileContent]) -> list[SourceFileContent]:
        total_bytes = sum(len(base64.b64decode(item.content_base64)) for item in files)
        if total_bytes > 15_000_000:
            raise ValueError("Uploaded documents exceed the 15 MB combined limit")
        return files


class SpecAgentRequest(ApiModel):
    title: str = Field(min_length=3, max_length=160)
    source_type: SourceType
    source_text: str = Field(default="", max_length=20_000)


class ApprovalRequest(ApiModel):
    gate: ApprovalGate


class RefineRequest(ApiModel):
    text: str = Field(min_length=3, max_length=5_000)


class AgentState(ApiModel):
    name: str
    role: str
    status: Literal["Ready", "Running", "Waiting", "Blocked", "Failed"] = "Ready"
    detail: str = ""
    last_action: str = ""
    tokens: int = 0


class AuditEvent(ApiModel):
    time: str
    stage: str
    message: str
    agent: str | None = None
    severity: Literal["info", "warning", "error"] = "info"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Blueprint(ApiModel):
    application: str
    frontend: str
    backend: str
    data: str
    storage: str
    messaging: str
    identity: str
    deployment: str
    security: list[str]
    reasoning: list[str]
    mode: str = "local-rules"
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class BlueprintUpdate(ApiModel):
    application: str = Field(min_length=1, max_length=160)
    frontend: str = Field(min_length=1, max_length=240)
    backend: str = Field(min_length=1, max_length=240)
    data: str = Field(min_length=1, max_length=240)
    storage: str = Field(min_length=1, max_length=240)
    messaging: str = Field(min_length=1, max_length=240)
    identity: str = Field(min_length=1, max_length=240)
    deployment: str = Field(min_length=1, max_length=240)
    security: list[str] = Field(default_factory=list, max_length=20)

    @field_validator(
        "application", "frontend", "backend", "data", "storage", "messaging", "identity", "deployment"
    )
    @classmethod
    def require_nonblank_choice(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Blueprint choices cannot be blank")
        return value

    @field_validator("security")
    @classmethod
    def clean_security_controls(cls, values: list[str]) -> list[str]:
        return [value.strip()[:300] for value in values if value.strip()][:20]


class ProofFailure(ApiModel):
    failed_test: str
    expected: str
    received: str


class ProofIteration(ApiModel):
    iteration: int
    action: str
    status: Literal["Detected", "Patched", "Passed"]


class CriticFinding(ApiModel):
    severity: Literal["Critical", "High", "Medium", "Low"]
    file: str | None = None
    issue: str
    recommendation: str


class ProofResult(ApiModel):
    code_quality: int = 0
    spec_fidelity: int = 0
    failure_injected: bool = False
    failure: ProofFailure | None = None
    iterations: list[ProofIteration] = Field(default_factory=list)
    integration: str = "Not started"
    code: dict[str, str] = Field(default_factory=dict)
    files: list[str] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    generator_mode: str = ""
    critic_mode: str = ""
    critic_summary: str = ""
    critic_findings: list[CriticFinding] = Field(default_factory=list)
    requirement_coverage: list[str] = Field(default_factory=list)
    test_plan: list[str] = Field(default_factory=list)
    runtime_status: str = "Not run"
    checks: dict[str, str] = Field(default_factory=dict)


class SkillProposal(ApiModel):
    name: str
    version: str
    reason: str
    status: Literal["Pending Approval", "Approved"] = "Pending Approval"


class SkillRecipe(ApiModel):
    id: str
    agent: str
    title: str
    tags: list[str] = Field(default_factory=list)
    use_when: str = ""
    inputs: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    done_when: str = ""
    pitfalls: list[str] = Field(default_factory=list)
    output: str = ""
    version: str = "0.1"
    status: SkillStatus = "draft"
    audit: list[AuditEvent] = Field(default_factory=list)


class SkillApprovalRequest(ApiModel):
    decision: Literal["submit", "approve", "reject", "deprecate"]
    reason: str = Field(default="", max_length=1000)


class SkillUsage(ApiModel):
    id: str
    version: str
    usage: Literal["retrieved", "applied", "skipped"] = "retrieved"
    reason: str = ""


class ReleaseResult(ApiModel):
    spec_fidelity: int
    unit_tests: str
    contract_tests: str
    security_scan: str
    dependency_scan: str
    container_image_scan: str
    self_healing_iterations: int
    target: str
    private_network: bool
    public_ingress: bool
    deployment_url: str | None = None


class SecurityReview(ApiModel):
    mode: str = "local-static"
    decision: Literal["No high or critical findings", "Block release"]
    summary: str
    checks: dict[str, str] = Field(default_factory=dict)
    findings: list[CriticFinding] = Field(default_factory=list)
    scanned_files: int = 0
    skills_used: list[SkillUsage] = Field(default_factory=list)
    external_scans: dict[str, str] = Field(default_factory=dict)


class DeploymentPlan(ApiModel):
    status: Literal["ready", "blocked"]
    summary: str
    target: str
    image_tag: str
    human_approval_required: bool = True
    checks: dict[str, str] = Field(default_factory=dict)
    blockers: list[str] = Field(default_factory=list)
    artifact_manifest: list[dict[str, Any]] = Field(default_factory=list)


class BuildMetrics(ApiModel):
    tokens: int = 0
    tool_calls: int = 0
    build_seconds: int = 0
    self_heal_iterations: int = 0
    success_rate: int = 0


class BuildState(ApiModel):

    id: str
    title: str
    source_type: SourceType
    source_text: str
    files: list[str]
    stage: Literal["Draft", "Understand", "Design", "Forge", "Prove", "Release", "Replay", "Error"] = "Draft"
    progress: int = 0
    status: Literal["Draft", "Running", "Awaiting Approval", "Refined", "Deployed", "Blocked", "Failed", "Completed"] = "Draft"

    requirements: list[dict[str, Any]] = Field(default_factory=list)
    requirement_summary: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    security_considerations: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)

    spec_confidence: float = 0.0
    spec_readiness: SpecReadiness = "READY"
    agent_mode: str = ""

    blueprint: Blueprint | None = None
    proof: ProofResult | None = None
    release: ReleaseResult | None = None
    security_review: SecurityReview | None = None
    deployment_plan: DeploymentPlan | None = None
    feature_branch: str | None = None
    feature_branch_url: str | None = None
    repository_url: str | None = None
    deployed_url: str | None = None
    skill_proposal: SkillProposal | None = None
    skills_used: list[SkillUsage] = Field(default_factory=list)
    agents: list[AgentState] = Field(default_factory=list)
    audit: list[AuditEvent] = Field(default_factory=list)
    metrics: BuildMetrics = Field(default_factory=BuildMetrics)
    approval_gate: ApprovalGate | None = None
    error: str | None = None
